# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import shutil
import sys
import StringIO
import tempfile
import unittest

import stubout

from openstack.common.cfg import *


class ExceptionsTestCase(unittest.TestCase):

    def test_error(self):
        msg = str(Error('foobar'))
        self.assertEquals(msg, 'foobar')

    def test_args_already_parsed_error(self):
        msg = str(ArgsAlreadyParsedError('foobar'))
        self.assertEquals(msg, 'arguments already parsed: foobar')

    def test_no_such_opt_error(self):
        msg = str(NoSuchOptError('foo'))
        self.assertEquals(msg, 'no such option: foo')

    def test_no_such_opt_error_with_group(self):
        msg = str(NoSuchOptError('foo', OptGroup('bar')))
        self.assertEquals(msg, 'no such option in group bar: foo')

    def test_no_such_group_error(self):
        msg = str(NoSuchGroupError('bar'))
        self.assertEquals(msg, 'no such group: bar')

    def test_duplicate_opt_error(self):
        msg = str(DuplicateOptError('foo'))
        self.assertEquals(msg, 'duplicate option: foo')

    def test_required_opt_error(self):
        msg = str(RequiredOptError('foo'))
        self.assertEquals(msg, 'value required for option: foo')

    def test_required_opt_error_with_group(self):
        msg = str(RequiredOptError('foo', OptGroup('bar')))
        self.assertEquals(msg, 'value required for option: bar.foo')

    def test_template_substitution_error(self):
        msg = str(TemplateSubstitutionError('foobar'))
        self.assertEquals(msg, 'template substitution error: foobar')

    def test_config_files_not_found_error(self):
        msg = str(ConfigFilesNotFoundError(['foo', 'bar']))
        self.assertEquals(msg, 'Failed to read some config files: foo,bar')

    def test_config_file_parse_error(self):
        msg = str(ConfigFileParseError('foo', 'foobar'))
        self.assertEquals(msg, 'Failed to parse foo: foobar')


class BaseTestCase(unittest.TestCase):

    class TestConfigOpts(ConfigOpts):
        def __call__(self, args=None):
            return ConfigOpts.__call__(self,
                                       args=args,
                                       prog='test',
                                       version='1.0',
                                       usage='%(prog)s FOO BAR',
                                       default_config_files=[])

    def setUp(self):
        self.conf = self.TestConfigOpts()

        self.tempfiles = []
        self.tempdirs = []
        self.stubs = stubout.StubOutForTesting()

    def tearDown(self):
        self.remove_tempfiles()
        self.stubs.UnsetAll()

    def create_tempfiles(self, files, ext='.conf'):
        for (basename, contents) in files:
            if not os.path.isabs(basename):
                (fd, path) = tempfile.mkstemp(prefix=basename, suffix=ext)
            else:
                path = basename + ext
                fd = os.open(path, os.O_CREAT | os.O_WRONLY)
            self.tempfiles.append(path)
            try:
                os.write(fd, contents)
            finally:
                os.close(fd)
        return self.tempfiles[-len(files):]

    def remove_tempfiles(self):
        for p in self.tempfiles:
            os.remove(p)
        for d in self.tempdirs:
            shutil.rmtree(d, ignore_errors=True)


class UsageTestCase(BaseTestCase):

    def test_print_usage(self):
        f = StringIO.StringIO()
        self.conf([])
        self.conf.print_usage(file=f)
        self.assertTrue('usage: test FOO BAR' in f.getvalue())
        self.assertTrue('optional:' not in f.getvalue())


class HelpTestCase(BaseTestCase):

    def test_print_help(self):
        f = StringIO.StringIO()
        self.conf([])
        self.conf.print_help(file=f)
        self.assertTrue('usage: test FOO BAR' in f.getvalue())
        self.assertTrue('optional' in f.getvalue())
        self.assertTrue('-h, --help' in f.getvalue())


class FindConfigFilesTestCase(BaseTestCase):

    def test_find_config_files(self):
        config_files = [os.path.expanduser('~/.blaa/blaa.conf'),
                        '/etc/foo.conf']

        self.stubs.Set(sys, 'argv', ['foo'])
        self.stubs.Set(os.path, 'exists', lambda p: p in config_files)

        self.assertEquals(find_config_files(project='blaa'), config_files)

    def test_find_config_files_with_extension(self):
        config_files = ['/etc/foo.json']

        self.stubs.Set(sys, 'argv', ['foo'])
        self.stubs.Set(os.path, 'exists', lambda p: p in config_files)

        self.assertEquals(find_config_files(project='blaa'), [])
        self.assertEquals(find_config_files(project='blaa', extension='.json'),
                          config_files)


class CliOptsTestCase(BaseTestCase):

    def _do_cli_test(self, opt_class, default, cli_args, value):
        self.conf.register_cli_opt(opt_class('foo', default=default,
                                   deprecated_name='oldfoo'))

        self.conf(cli_args)

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, value)

    def test_str_default(self):
        self._do_cli_test(StrOpt, None, [], None)

    def test_str_arg(self):
        self._do_cli_test(StrOpt, None, ['--foo', 'bar'], 'bar')

    def test_str_arg_deprecated(self):
        self._do_cli_test(StrOpt, None, ['--oldfoo', 'bar'], 'bar')

    def test_bool_default(self):
        self._do_cli_test(BoolOpt, False, [], False)

    def test_bool_arg(self):
        self._do_cli_test(BoolOpt, None, ['--foo'], True)

    def test_bool_arg_deprecated(self):
        self._do_cli_test(BoolOpt, None, ['--oldfoo'], True)

    def test_bool_arg_inverse(self):
        self._do_cli_test(BoolOpt, None, ['--foo', '--nofoo'], False)

    def test_bool_arg_inverse_deprecated(self):
        self._do_cli_test(BoolOpt, None, ['--oldfoo', '--nooldfoo'], False)

    def test_int_default(self):
        self._do_cli_test(IntOpt, 10, [], 10)

    def test_int_arg(self):
        self._do_cli_test(IntOpt, None, ['--foo=20'], 20)

    def test_int_arg_deprecated(self):
        self._do_cli_test(IntOpt, None, ['--oldfoo=20'], 20)

    def test_float_default(self):
        self._do_cli_test(FloatOpt, 1.0, [], 1.0)

    def test_float_arg(self):
        self._do_cli_test(FloatOpt, None, ['--foo', '2.0'], 2.0)

    def test_float_arg_deprecated(self):
        self._do_cli_test(FloatOpt, None, ['--oldfoo', '2.0'], 2.0)

    def test_list_default(self):
        self._do_cli_test(ListOpt, ['bar'], [], ['bar'])

    def test_list_arg(self):
        self._do_cli_test(ListOpt, None,
                          ['--foo', 'blaa,bar'], ['blaa', 'bar'])

    def test_list_arg_with_spaces(self):
        self._do_cli_test(ListOpt, None,
                          ['--foo', 'blaa ,bar'], ['blaa', 'bar'])

    def test_list_arg_deprecated(self):
        self._do_cli_test(ListOpt, None,
                          ['--oldfoo', 'blaa,bar'], ['blaa', 'bar'])

    def test_multistr_default(self):
        self._do_cli_test(MultiStrOpt, ['bar'], [], ['bar'])

    def test_multistr_arg(self):
        self._do_cli_test(MultiStrOpt, None,
                          ['--foo', 'blaa', '--foo', 'bar'], ['blaa', 'bar'])

    def test_multistr_arg_deprecated(self):
        self._do_cli_test(MultiStrOpt, None,
                          ['--oldfoo', 'blaa', '--oldfoo', 'bar'],
                          ['blaa', 'bar'])

    def test_help(self):
        self.stubs.Set(sys, 'stdout', StringIO.StringIO())
        self.assertRaises(SystemExit, self.conf, ['--help'])
        self.assertTrue('FOO BAR' in sys.stdout.getvalue())
        self.assertTrue('--version' in sys.stdout.getvalue())
        self.assertTrue('--help' in sys.stdout.getvalue())
        self.assertTrue('--config-file' in sys.stdout.getvalue())

    def test_version(self):
        self.stubs.Set(sys, 'stderr', StringIO.StringIO())
        self.assertRaises(SystemExit, self.conf, ['--version'])
        self.assertTrue('1.0' in sys.stderr.getvalue())

    def test_config_file(self):
        paths = self.create_tempfiles([('1', '[DEFAULT]'),
                                       ('2', '[DEFAULT]')])

        self.conf(['--config-file', paths[0], '--config-file', paths[1]])

        self.assertEquals(self.conf.config_file, paths)


class PositionalTestCase(BaseTestCase):

    def _do_pos_test(self, opt_class, default, cli_args, value):
        self.conf.register_cli_opt(opt_class('foo',
                                             default=default,
                                             positional=True))

        self.conf(cli_args)

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, value)

    def test_positional_str_default(self):
        self._do_pos_test(StrOpt, None, [], None)

    def test_positional_str_arg(self):
        self._do_pos_test(StrOpt, None, ['bar'], 'bar')

    def test_positional_int_default(self):
        self._do_pos_test(IntOpt, 10, [], 10)

    def test_positional_int_arg(self):
        self._do_pos_test(IntOpt, None, ['20'], 20)

    def test_positional_float_default(self):
        self._do_pos_test(FloatOpt, 1.0, [], 1.0)

    def test_positional_float_arg(self):
        self._do_pos_test(FloatOpt, None, ['2.0'], 2.0)

    def test_positional_list_default(self):
        self._do_pos_test(ListOpt, ['bar'], [], ['bar'])

    def test_positional_list_arg(self):
        self._do_pos_test(ListOpt, None,
                          ['blaa,bar'], ['blaa', 'bar'])

    def test_positional_multistr_default(self):
        self._do_pos_test(MultiStrOpt, ['bar'], [], ['bar'])

    def test_positional_multistr_arg(self):
        self._do_pos_test(MultiStrOpt, None,
                          ['blaa', 'bar'], ['blaa', 'bar'])

    def test_positional_bool(self):
        self.assertRaises(ValueError, BoolOpt, 'foo', positional=True)

    def test_required_positional_opt(self):
        self.conf.register_cli_opt(StrOpt('foo',
                                          required=True,
                                          positional=True))

        self.conf(['bar'])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, 'bar')

    def test_missing_required_cli_opt(self):
        self.conf.register_cli_opt(StrOpt('foo',
                                          required=True,
                                          positional=True))
        self.assertRaises(RequiredOptError, self.conf, [])


class ConfigFileOptsTestCase(BaseTestCase):

    def _do_deprecated_test_use(self, opt_class, value, result):
        self.conf.register_opt(opt_class('newfoo', deprecated_name='oldfoo'))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'oldfoo = %s\n' % value)])

        self.conf(['--config-file', paths[0]])
        self.assertTrue(hasattr(self.conf, 'newfoo'))
        self.assertEquals(self.conf.newfoo, result)

    def _do_deprecated_test_ignore(self, opt_class, value, result):
        self.conf.register_opt(opt_class('newfoo', deprecated_name='oldfoo'))

        paths2 = self.create_tempfiles([('test',
                                         '[DEFAULT]\n'
                                         'newfoo = %s\n' % value)])

        self.conf(['--config-file', paths2[0]])
        self.assertTrue(hasattr(self.conf, 'newfoo'))
        self.assertEquals(self.conf.newfoo, result)

    def test_conf_file_str_default(self):
        self.conf.register_opt(StrOpt('foo', default='bar'))

        paths = self.create_tempfiles([('test', '[DEFAULT]\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, 'bar')

    def test_conf_file_str_value(self):
        self.conf.register_opt(StrOpt('foo'))

        paths = self.create_tempfiles([('test', '[DEFAULT]\n''foo = bar\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, 'bar')

    def test_conf_file_str_value_override(self):
        self.conf.register_cli_opt(StrOpt('foo'))

        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo = baar\n'),
                                       ('2',
                                        '[DEFAULT]\n'
                                        'foo = baaar\n')])

        self.conf(['--foo', 'bar',
                   '--config-file', paths[0],
                   '--config-file', paths[1]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, 'baaar')

    def test_conf_file_str_value_override_use_deprecated(self):
        """last option should always win, even if last uses deprecated"""
        self.conf.register_cli_opt(StrOpt('newfoo', deprecated_name='oldfoo'))

        paths = self.create_tempfiles([('0',
                                        '[DEFAULT]\n'
                                        'newfoo = middle\n'),
                                       ('1',
                                        '[DEFAULT]\n'
                                        'oldfoo = last\n')])

        self.conf(['--newfoo', 'first',
                   '--config-file', paths[0],
                   '--config-file', paths[1]])

        self.assertTrue(hasattr(self.conf, 'newfoo'))
        self.assertFalse(hasattr(self.conf, 'oldfoo'))
        self.assertEquals(self.conf.newfoo, 'last')

    def test_conf_file_str_use_deprecated(self):
        self._do_deprecated_test_use(StrOpt, 'value1', 'value1')

    def test_conf_file_str_ignore_deprecated(self):
        self._do_deprecated_test_ignore(StrOpt, 'value2', 'value2')

    def test_conf_file_bool_default(self):
        self.conf.register_opt(BoolOpt('foo', default=False))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, False)

    def test_conf_file_bool_value(self):
        self.conf.register_opt(BoolOpt('foo'))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = true\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, True)

    def test_conf_file_bool_value_override(self):
        self.conf.register_cli_opt(BoolOpt('foo'))

        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo = 0\n'),
                                       ('2',
                                        '[DEFAULT]\n'
                                        'foo = yes\n')])

        self.conf(['--foo',
                   '--config-file', paths[0],
                   '--config-file', paths[1]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, True)

    def test_conf_file_bool_use_deprecated(self):
        self._do_deprecated_test_use(BoolOpt, 'yes', True)

    def test_conf_file_bool_ignore_deprecated(self):
        self._do_deprecated_test_ignore(BoolOpt, 'no', False)

    def test_conf_file_int_default(self):
        self.conf.register_opt(IntOpt('foo', default=666))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, 666)

    def test_conf_file_int_value(self):
        self.conf.register_opt(IntOpt('foo'))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 666\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, 666)

    def test_conf_file_int_value_override(self):
        self.conf.register_cli_opt(IntOpt('foo'))

        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo = 66\n'),
                                       ('2',
                                        '[DEFAULT]\n'
                                        'foo = 666\n')])

        self.conf(['--foo', '6',
                   '--config-file', paths[0],
                   '--config-file', paths[1]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, 666)

    def test_conf_file_int_use_deprecated(self):
        self._do_deprecated_test_use(IntOpt, '66', 66)

    def test_conf_file_int_ignore_deprecated(self):
        self._do_deprecated_test_ignore(IntOpt, '64', 64)

    def test_conf_file_float_default(self):
        self.conf.register_opt(FloatOpt('foo', default=6.66))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, 6.66)

    def test_conf_file_float_value(self):
        self.conf.register_opt(FloatOpt('foo'))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 6.66\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, 6.66)

    def test_conf_file_float_value_override(self):
        self.conf.register_cli_opt(FloatOpt('foo'))

        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo = 6.6\n'),
                                       ('2',
                                        '[DEFAULT]\n'
                                        'foo = 6.66\n')])

        self.conf(['--foo', '6',
                   '--config-file', paths[0],
                   '--config-file', paths[1]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, 6.66)

    def test_conf_file_float_use_deprecated(self):
        self._do_deprecated_test_use(FloatOpt, '66.54', 66.54)

    def test_conf_file_float_ignore_deprecated(self):
        self._do_deprecated_test_ignore(FloatOpt, '64.54', 64.54)

    def test_conf_file_list_default(self):
        self.conf.register_opt(ListOpt('foo', default=['bar']))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, ['bar'])

    def test_conf_file_list_value(self):
        self.conf.register_opt(ListOpt('foo'))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = bar\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, ['bar'])

    def test_conf_file_list_value_override(self):
        self.conf.register_cli_opt(ListOpt('foo'))

        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo = bar,bar\n'),
                                       ('2',
                                        '[DEFAULT]\n'
                                        'foo = b,a,r\n')])

        self.conf(['--foo', 'bar',
                   '--config-file', paths[0],
                   '--config-file', paths[1]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, ['b', 'a', 'r'])

    def test_conf_file_list_use_deprecated(self):
        self._do_deprecated_test_use(ListOpt, 'a,b,c', ['a', 'b', 'c'])

    def test_conf_file_list_ignore_deprecated(self):
        self._do_deprecated_test_ignore(ListOpt, 'd,e,f', ['d', 'e', 'f'])

    def test_conf_file_list_spaces_use_deprecated(self):
        self._do_deprecated_test_use(ListOpt, 'a, b, c', ['a', 'b', 'c'])

    def test_conf_file_list_spaces_ignore_deprecated(self):
        self._do_deprecated_test_ignore(ListOpt, 'd, e, f', ['d', 'e', 'f'])

    def test_conf_file_multistr_default(self):
        self.conf.register_opt(MultiStrOpt('foo', default=['bar']))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, ['bar'])

    def test_conf_file_multistr_value(self):
        self.conf.register_opt(MultiStrOpt('foo'))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = bar\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, ['bar'])

    def test_conf_file_multistr_values_append_deprecated(self):
        self.conf.register_cli_opt(MultiStrOpt('foo',
                                   deprecated_name='oldfoo'))

        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo = bar1\n'),
                                       ('2',
                                        '[DEFAULT]\n'
                                        'oldfoo = bar2\n'
                                        'oldfoo = bar3\n')])

        self.conf(['--foo', 'bar0',
                   '--config-file', paths[0],
                   '--config-file', paths[1]])

        self.assertTrue(hasattr(self.conf, 'foo'))

        self.assertEquals(self.conf.foo, ['bar0', 'bar1', 'bar2', 'bar3'])

    def test_conf_file_multistr_values_append(self):
        self.conf.register_cli_opt(MultiStrOpt('foo'))

        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo = bar1\n'),
                                       ('2',
                                        '[DEFAULT]\n'
                                        'foo = bar2\n'
                                        'foo = bar3\n')])

        self.conf(['--foo', 'bar0',
                   '--config-file', paths[0],
                   '--config-file', paths[1]])

        self.assertTrue(hasattr(self.conf, 'foo'))

        self.assertEquals(self.conf.foo, ['bar0', 'bar1', 'bar2', 'bar3'])

    def test_conf_file_multistr_deprecated(self):
        self.conf.register_opt(MultiStrOpt('newfoo', deprecated_name='oldfoo'))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'oldfoo= bar1\n'
                                        'oldfoo = bar2\n')])

        self.conf(['--config-file', paths[0]])
        self.assertTrue(hasattr(self.conf, 'newfoo'))
        self.assertEquals(self.conf.newfoo, ['bar1', 'bar2'])

    def test_conf_file_multiple_opts(self):
        self.conf.register_opts([StrOpt('foo'), StrOpt('bar')])

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = bar\n'
                                        'bar = foo\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, 'bar')
        self.assertTrue(hasattr(self.conf, 'bar'))
        self.assertEquals(self.conf.bar, 'foo')

    def test_conf_file_raw_value(self):
        self.conf.register_opt(StrOpt('foo'))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = bar-%08x\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, 'bar-%08x')


class OptGroupsTestCase(BaseTestCase):

    def test_arg_group(self):
        blaa_group = OptGroup('blaa', 'blaa options')
        self.conf.register_group(blaa_group)
        self.conf.register_cli_opt(StrOpt('foo'), group=blaa_group)

        self.conf(['--blaa-foo', 'bar'])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEquals(self.conf.blaa.foo, 'bar')

    def test_autocreate_group(self):
        self.conf.register_cli_opt(StrOpt('foo'), group='blaa')

        self.conf(['--blaa-foo', 'bar'])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEquals(self.conf.blaa.foo, 'bar')

    def test_arg_group_by_name(self):
        self.conf.register_group(OptGroup('blaa'))
        self.conf.register_cli_opt(StrOpt('foo'), group='blaa')

        self.conf(['--blaa-foo', 'bar'])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEquals(self.conf.blaa.foo, 'bar')

    def test_arg_group_with_default(self):
        self.conf.register_group(OptGroup('blaa'))
        self.conf.register_cli_opt(StrOpt('foo', default='bar'), group='blaa')

        self.conf([])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEquals(self.conf.blaa.foo, 'bar')

    def test_arg_group_with_conf_and_group_opts(self):
        self.conf.register_cli_opt(StrOpt('conf'), group='blaa')
        self.conf.register_cli_opt(StrOpt('group'), group='blaa')

        self.conf(['--blaa-conf', 'foo', '--blaa-group', 'bar'])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'conf'))
        self.assertEquals(self.conf.blaa.conf, 'foo')
        self.assertTrue(hasattr(self.conf.blaa, 'group'))
        self.assertEquals(self.conf.blaa.group, 'bar')

    def test_arg_group_in_config_file(self):
        self.conf.register_group(OptGroup('blaa'))
        self.conf.register_opt(StrOpt('foo'), group='blaa')

        paths = self.create_tempfiles([('test',
                                        '[blaa]\n'
                                        'foo = bar\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEquals(self.conf.blaa.foo, 'bar')

    def test_arg_group_in_config_file_with_deprecated(self):
        self.conf.register_group(OptGroup('blaa'))
        self.conf.register_opt(StrOpt('foo', deprecated_name='oldfoo'),
                               group='blaa')

        paths = self.create_tempfiles([('test',
                                        '[blaa]\n'
                                        'oldfoo = bar\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEquals(self.conf.blaa.foo, 'bar')


class MappingInterfaceTestCase(BaseTestCase):

    def test_mapping_interface(self):
        self.conf.register_cli_opt(StrOpt('foo'))

        self.conf(['--foo', 'bar'])

        self.assertTrue('foo' in self.conf)
        self.assertTrue('config_file' in self.conf)
        self.assertEquals(len(self.conf), 3)
        self.assertEquals(self.conf['foo'], 'bar')
        self.assertEquals(self.conf.get('foo'), 'bar')
        self.assertTrue('bar' in self.conf.values())

    def test_mapping_interface_with_group(self):
        self.conf.register_group(OptGroup('blaa'))
        self.conf.register_cli_opt(StrOpt('foo'), group='blaa')

        self.conf(['--blaa-foo', 'bar'])

        self.assertTrue('blaa' in self.conf)
        self.assertTrue('foo' in self.conf['blaa'])
        self.assertEquals(len(self.conf['blaa']), 1)
        self.assertEquals(self.conf['blaa']['foo'], 'bar')
        self.assertEquals(self.conf['blaa'].get('foo'), 'bar')
        self.assertTrue('bar' in self.conf['blaa'].values())
        self.assertEquals(self.conf.blaa, self.conf['blaa'])


class ReRegisterOptTestCase(BaseTestCase):

    def test_conf_file_re_register_opt(self):
        opt = StrOpt('foo')
        self.assertTrue(self.conf.register_opt(opt))
        self.assertFalse(self.conf.register_opt(opt))

    def test_conf_file_re_register_opt_in_group(self):
        group = OptGroup('blaa')
        self.conf.register_group(group)
        self.conf.register_group(group)  # not an error
        opt = StrOpt('foo')
        self.assertTrue(self.conf.register_opt(opt, group=group))
        self.assertFalse(self.conf.register_opt(opt, group='blaa'))


class TemplateSubstitutionTestCase(BaseTestCase):

    def _prep_test_str_sub(self, foo_default=None, bar_default=None):
        self.conf.register_cli_opt(StrOpt('foo', default=foo_default))
        self.conf.register_cli_opt(StrOpt('bar', default=bar_default))

    def _assert_str_sub(self):
        self.assertTrue(hasattr(self.conf, 'bar'))
        self.assertEquals(self.conf.bar, 'blaa')

    def test_str_sub_default_from_default(self):
        self._prep_test_str_sub(foo_default='blaa', bar_default='$foo')

        self.conf([])

        self._assert_str_sub()

    def test_str_sub_default_from_default_recurse(self):
        self.conf.register_cli_opt(StrOpt('blaa', default='blaa'))
        self._prep_test_str_sub(foo_default='$blaa', bar_default='$foo')

        self.conf([])

        self._assert_str_sub()

    def test_str_sub_default_from_arg(self):
        self._prep_test_str_sub(bar_default='$foo')

        self.conf(['--foo', 'blaa'])

        self._assert_str_sub()

    def test_str_sub_default_from_config_file(self):
        self._prep_test_str_sub(bar_default='$foo')

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = blaa\n')])

        self.conf(['--config-file', paths[0]])

        self._assert_str_sub()

    def test_str_sub_arg_from_default(self):
        self._prep_test_str_sub(foo_default='blaa')

        self.conf(['--bar', '$foo'])

        self._assert_str_sub()

    def test_str_sub_arg_from_arg(self):
        self._prep_test_str_sub()

        self.conf(['--foo', 'blaa', '--bar', '$foo'])

        self._assert_str_sub()

    def test_str_sub_arg_from_config_file(self):
        self._prep_test_str_sub()

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = blaa\n')])

        self.conf(['--config-file', paths[0], '--bar=$foo'])

        self._assert_str_sub()

    def test_str_sub_config_file_from_default(self):
        self._prep_test_str_sub(foo_default='blaa')

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'bar = $foo\n')])

        self.conf(['--config-file', paths[0]])

        self._assert_str_sub()

    def test_str_sub_config_file_from_arg(self):
        self._prep_test_str_sub()

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'bar = $foo\n')])

        self.conf(['--config-file', paths[0], '--foo=blaa'])

        self._assert_str_sub()

    def test_str_sub_config_file_from_config_file(self):
        self._prep_test_str_sub()

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'bar = $foo\n'
                                        'foo = blaa\n')])

        self.conf(['--config-file', paths[0]])

        self._assert_str_sub()

    def test_str_sub_group_from_default(self):
        self.conf.register_cli_opt(StrOpt('foo', default='blaa'))
        self.conf.register_group(OptGroup('ba'))
        self.conf.register_cli_opt(StrOpt('r', default='$foo'), group='ba')

        self.conf([])

        self.assertTrue(hasattr(self.conf, 'ba'))
        self.assertTrue(hasattr(self.conf.ba, 'r'))
        self.assertEquals(self.conf.ba.r, 'blaa')

    def test_config_dir(self):
        snafu_group = OptGroup('snafu')
        self.conf.register_group(snafu_group)
        self.conf.register_cli_opt(StrOpt('foo'))
        self.conf.register_cli_opt(StrOpt('bell'), group=snafu_group)

        dir = tempfile.mkdtemp()
        self.tempdirs.append(dir)

        paths = self.create_tempfiles([(os.path.join(dir, '00-test'),
                                        '[DEFAULT]\n'
                                        'foo = bar-00\n'
                                        '[snafu]\n'
                                        'bell = whistle-00\n'),
                                       (os.path.join(dir, '02-test'),
                                        '[snafu]\n'
                                        'bell = whistle-02\n'
                                        '[DEFAULT]\n'
                                        'foo = bar-02\n'),
                                       (os.path.join(dir, '01-test'),
                                        '[DEFAULT]\n'
                                        'foo = bar-01\n')])

        self.conf(['--foo', 'bar',
                   '--config-dir', os.path.dirname(paths[0])])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, 'bar-02')
        self.assertTrue(hasattr(self.conf, 'snafu'))
        self.assertTrue(hasattr(self.conf.snafu, 'bell'))
        self.assertEquals(self.conf.snafu.bell, 'whistle-02')

    def test_config_dir_file_precedence(self):
        snafu_group = OptGroup('snafu')
        self.conf.register_group(snafu_group)
        self.conf.register_cli_opt(StrOpt('foo'))
        self.conf.register_cli_opt(StrOpt('bell'), group=snafu_group)

        dir = tempfile.mkdtemp()
        self.tempdirs.append(dir)

        paths = self.create_tempfiles([(os.path.join(dir, '00-test'),
                                        '[DEFAULT]\n'
                                        'foo = bar-00\n'),
                                       ('01-test',
                                        '[snafu]\n'
                                        'bell = whistle-01\n'
                                        '[DEFAULT]\n'
                                        'foo = bar-01\n'),
                                       ('03-test',
                                        '[snafu]\n'
                                        'bell = whistle-03\n'
                                        '[DEFAULT]\n'
                                        'foo = bar-03\n'),
                                       (os.path.join(dir, '02-test'),
                                        '[DEFAULT]\n'
                                        'foo = bar-02\n')])

        self.conf(['--foo', 'bar',
                   '--config-file', paths[1],
                   '--config-dir', os.path.dirname(paths[0]),
                   '--config-file', paths[2], ])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, 'bar-02')
        self.assertTrue(hasattr(self.conf, 'snafu'))
        self.assertTrue(hasattr(self.conf.snafu, 'bell'))
        self.assertEquals(self.conf.snafu.bell, 'whistle-03')


class ReparseTestCase(BaseTestCase):

    def test_reparse(self):
        self.conf.register_group(OptGroup('blaa'))
        self.conf.register_cli_opt(StrOpt('foo', default='r'), group='blaa')

        paths = self.create_tempfiles([('test',
                                        '[blaa]\n'
                                        'foo = b\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEquals(self.conf.blaa.foo, 'b')

        self.conf(['--blaa-foo', 'a'])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEquals(self.conf.blaa.foo, 'a')

        self.conf([])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEquals(self.conf.blaa.foo, 'r')


class OverridesTestCase(BaseTestCase):

    def test_default_none(self):
        self.conf.register_opt(StrOpt('foo', default='foo'))
        self.conf([])
        self.assertEquals(self.conf.foo, 'foo')
        self.conf.set_default('foo', None)
        self.assertEquals(self.conf.foo, None)
        self.conf.clear_default('foo')
        self.assertEquals(self.conf.foo, 'foo')

    def test_override_none(self):
        self.conf.register_opt(StrOpt('foo', default='foo'))
        self.conf([])
        self.assertEquals(self.conf.foo, 'foo')
        self.conf.set_override('foo', None)
        self.assertEquals(self.conf.foo, None)
        self.conf.clear_override('foo')
        self.assertEquals(self.conf.foo, 'foo')

    def test_no_default_override(self):
        self.conf.register_opt(StrOpt('foo'))
        self.conf([])
        self.assertEquals(self.conf.foo, None)
        self.conf.set_default('foo', 'bar')
        self.assertEquals(self.conf.foo, 'bar')
        self.conf.clear_default('foo')
        self.assertEquals(self.conf.foo, None)

    def test_default_override(self):
        self.conf.register_opt(StrOpt('foo', default='foo'))
        self.conf([])
        self.assertEquals(self.conf.foo, 'foo')
        self.conf.set_default('foo', 'bar')
        self.assertEquals(self.conf.foo, 'bar')
        self.conf.clear_default('foo')
        self.assertEquals(self.conf.foo, 'foo')

    def test_override(self):
        self.conf.register_opt(StrOpt('foo'))
        self.conf.set_override('foo', 'bar')
        self.conf([])
        self.assertEquals(self.conf.foo, 'bar')
        self.conf.clear_override('foo')
        self.assertEquals(self.conf.foo, None)

    def test_group_no_default_override(self):
        self.conf.register_group(OptGroup('blaa'))
        self.conf.register_opt(StrOpt('foo'), group='blaa')
        self.conf([])
        self.assertEquals(self.conf.blaa.foo, None)
        self.conf.set_default('foo', 'bar', group='blaa')
        self.assertEquals(self.conf.blaa.foo, 'bar')
        self.conf.clear_default('foo', group='blaa')
        self.assertEquals(self.conf.blaa.foo, None)

    def test_group_default_override(self):
        self.conf.register_group(OptGroup('blaa'))
        self.conf.register_opt(StrOpt('foo', default='foo'), group='blaa')
        self.conf([])
        self.assertEquals(self.conf.blaa.foo, 'foo')
        self.conf.set_default('foo', 'bar', group='blaa')
        self.assertEquals(self.conf.blaa.foo, 'bar')
        self.conf.clear_default('foo', group='blaa')
        self.assertEquals(self.conf.blaa.foo, 'foo')

    def test_group_override(self):
        self.conf.register_group(OptGroup('blaa'))
        self.conf.register_opt(StrOpt('foo'), group='blaa')
        self.assertEquals(self.conf.blaa.foo, None)
        self.conf.set_override('foo', 'bar', group='blaa')
        self.conf([])
        self.assertEquals(self.conf.blaa.foo, 'bar')
        self.conf.clear_override('foo', group='blaa')
        self.assertEquals(self.conf.blaa.foo, None)

    def test_cli_bool_default(self):
        self.conf.register_cli_opt(BoolOpt('foo'))
        self.conf.set_default('foo', True)
        self.assertTrue(self.conf.foo)
        self.conf([])
        self.assertTrue(self.conf.foo)
        self.conf.set_default('foo', False)
        self.assertFalse(self.conf.foo)
        self.conf.clear_default('foo')
        self.assertTrue(self.conf.foo is None)

    def test_cli_bool_override(self):
        self.conf.register_cli_opt(BoolOpt('foo'))
        self.conf.set_override('foo', True)
        self.assertTrue(self.conf.foo)
        self.conf([])
        self.assertTrue(self.conf.foo)
        self.conf.set_override('foo', False)
        self.assertFalse(self.conf.foo)
        self.conf.clear_override('foo')
        self.assertTrue(self.conf.foo is None)


class ResetAndClearTestCase(BaseTestCase):

    def test_clear(self):
        self.conf.register_cli_opt(StrOpt('foo'))
        self.conf.register_cli_opt(StrOpt('bar'), group='blaa')

        self.assertEquals(self.conf.foo, None)
        self.assertEquals(self.conf.blaa.bar, None)

        self.conf(['--foo', 'foo', '--blaa-bar', 'bar'])

        self.assertEquals(self.conf.foo, 'foo')
        self.assertEquals(self.conf.blaa.bar, 'bar')

        self.conf.clear()

        self.assertEquals(self.conf.foo, None)
        self.assertEquals(self.conf.blaa.bar, None)

    def test_reset_and_clear_with_defaults_and_overrides(self):
        self.conf.register_cli_opt(StrOpt('foo'))
        self.conf.register_cli_opt(StrOpt('bar'), group='blaa')

        self.conf.set_default('foo', 'foo')
        self.conf.set_override('bar', 'bar', group='blaa')

        self.conf(['--foo', 'foofoo'])

        self.assertEquals(self.conf.foo, 'foofoo')
        self.assertEquals(self.conf.blaa.bar, 'bar')

        self.conf.clear()

        self.assertEquals(self.conf.foo, 'foo')
        self.assertEquals(self.conf.blaa.bar, 'bar')

        self.conf.reset()

        self.assertEquals(self.conf.foo, None)
        self.assertEquals(self.conf.blaa.bar, None)


class UnregisterOptTestCase(BaseTestCase):

    def test_unregister_opt(self):
        opts = [StrOpt('foo'), StrOpt('bar')]

        self.conf.register_opts(opts)

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertTrue(hasattr(self.conf, 'bar'))

        self.conf.unregister_opt(opts[0])

        self.assertFalse(hasattr(self.conf, 'foo'))
        self.assertTrue(hasattr(self.conf, 'bar'))

        self.conf([])

        self.assertRaises(ArgsAlreadyParsedError,
                          self.conf.unregister_opt, opts[1])

        self.conf.clear()

        self.assertTrue(hasattr(self.conf, 'bar'))

        self.conf.unregister_opts(opts)

    def test_unregister_opt_from_group(self):
        opt = StrOpt('foo')

        self.conf.register_opt(opt, group='blaa')

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))

        self.conf.unregister_opt(opt, group='blaa')

        self.assertFalse(hasattr(self.conf.blaa, 'foo'))


class ImportOptTestCase(BaseTestCase):

    def test_import_opt(self):
        self.assertFalse(hasattr(CONF, 'blaa'))
        CONF.import_opt('blaa', 'tests.testmods.blaa_opt')
        self.assertTrue(hasattr(CONF, 'blaa'))

    def test_import_opt_in_group(self):
        self.assertFalse(hasattr(CONF, 'bar'))
        CONF.import_opt('foo', 'tests.testmods.bar_foo_opt', group='bar')
        self.assertTrue(hasattr(CONF, 'bar'))
        self.assertTrue(hasattr(CONF.bar, 'foo'))

    def test_import_opt_import_errror(self):
        self.assertRaises(ImportError, CONF.import_opt,
                          'blaa', 'tests.testmods.blaablaa_opt')

    def test_import_opt_no_such_opt(self):
        self.assertRaises(NoSuchOptError, CONF.import_opt,
                          'blaablaa', 'tests.testmods.blaa_opt')

    def test_import_opt_no_such_group(self):
        self.assertRaises(NoSuchGroupError, CONF.import_opt,
                          'blaa', 'tests.testmods.blaa_opt', group='blaa')


class RequiredOptsTestCase(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.conf.register_opt(StrOpt('boo', required=False))

    def test_required_opt(self):
        self.conf.register_opt(StrOpt('foo', required=True))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = bar')])

        self.conf(['--config-file', paths[0]])
        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, 'bar')

    def test_required_cli_opt(self):
        self.conf.register_cli_opt(StrOpt('foo', required=True))

        self.conf(['--foo', 'bar'])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, 'bar')

    def test_required_cli_opt_with_dash(self):
        self.conf.register_cli_opt(StrOpt('foo-bar', required=True))

        self.conf(['--foo-bar', 'baz'])

        self.assertTrue(hasattr(self.conf, 'foo_bar'))
        self.assertEquals(self.conf.foo_bar, 'baz')

    def test_missing_required_opt(self):
        self.conf.register_opt(StrOpt('foo', required=True))
        self.assertRaises(RequiredOptError, self.conf, [])

    def test_missing_required_cli_opt(self):
        self.conf.register_cli_opt(StrOpt('foo', required=True))
        self.assertRaises(RequiredOptError, self.conf, [])

    def test_required_group_opt(self):
        self.conf.register_group(OptGroup('blaa'))
        self.conf.register_opt(StrOpt('foo', required=True), group='blaa')

        paths = self.create_tempfiles([('test',
                                        '[blaa]\n'
                                        'foo = bar')])

        self.conf(['--config-file', paths[0]])
        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEquals(self.conf.blaa.foo, 'bar')

    def test_required_cli_group_opt(self):
        self.conf.register_group(OptGroup('blaa'))
        self.conf.register_cli_opt(StrOpt('foo', required=True), group='blaa')

        self.conf(['--blaa-foo', 'bar'])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEquals(self.conf.blaa.foo, 'bar')

    def test_missing_required_group_opt(self):
        self.conf.register_group(OptGroup('blaa'))
        self.conf.register_opt(StrOpt('foo', required=True), group='blaa')
        self.assertRaises(RequiredOptError, self.conf, [])

    def test_missing_required_cli_group_opt(self):
        self.conf.register_group(OptGroup('blaa'))
        self.conf.register_cli_opt(StrOpt('foo', required=True), group='blaa')
        self.assertRaises(RequiredOptError, self.conf, [])

    def test_required_opt_with_default(self):
        self.conf.register_cli_opt(StrOpt('foo', required=True))
        self.conf.set_default('foo', 'bar')

        self.conf([])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, 'bar')

    def test_required_opt_with_override(self):
        self.conf.register_cli_opt(StrOpt('foo', required=True))
        self.conf.set_override('foo', 'bar')

        self.conf([])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, 'bar')


class SadPathTestCase(BaseTestCase):

    def test_unknown_attr(self):
        self.conf([])
        self.assertFalse(hasattr(self.conf, 'foo'))
        self.assertRaises(NoSuchOptError, getattr, self.conf, 'foo')

    def test_unknown_attr_is_attr_error(self):
        self.conf([])
        self.assertFalse(hasattr(self.conf, 'foo'))
        self.assertRaises(AttributeError, getattr, self.conf, 'foo')

    def test_unknown_group_attr(self):
        self.conf.register_group(OptGroup('blaa'))

        self.conf([])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertFalse(hasattr(self.conf.blaa, 'foo'))
        self.assertRaises(NoSuchOptError, getattr, self.conf.blaa, 'foo')

    def test_ok_duplicate(self):
        opt = StrOpt('foo')
        self.conf.register_cli_opt(opt)
        opt2 = StrOpt('foo')
        self.conf.register_cli_opt(opt2)

        self.conf([])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, None)

    def test_error_duplicate(self):
        self.conf.register_cli_opt(StrOpt('foo', help='bar'))
        self.assertRaises(DuplicateOptError,
                          self.conf.register_cli_opt, StrOpt('foo'))

    def test_error_duplicate_with_different_dest(self):
        self.conf.register_cli_opt(StrOpt('foo', dest='f'))
        self.conf.register_cli_opt(StrOpt('foo'))
        self.assertRaises(DuplicateOptError, self.conf, [])

    def test_error_duplicate_short(self):
        self.conf.register_cli_opt(StrOpt('foo', short='f'))
        self.conf.register_cli_opt(StrOpt('bar', short='f'))
        self.assertRaises(DuplicateOptError, self.conf, [])

    def test_no_such_group(self):
        group = OptGroup('blaa')
        self.assertRaises(NoSuchGroupError, self.conf.register_cli_opt,
                          StrOpt('foo'), group=group)

    def test_already_parsed(self):
        self.conf([])

        self.assertRaises(ArgsAlreadyParsedError,
                          self.conf.register_cli_opt, StrOpt('foo'))

    def test_bad_cli_arg(self):
        self.conf.register_opt(BoolOpt('foo'))

        self.stubs.Set(sys, 'stderr', StringIO.StringIO())

        self.assertRaises(SystemExit, self.conf, ['--foo'])

        self.assertTrue('error' in sys.stderr.getvalue())
        self.assertTrue('--foo' in sys.stderr.getvalue())

    def _do_test_bad_cli_value(self, opt_class):
        self.conf.register_cli_opt(opt_class('foo'))

        self.stubs.Set(sys, 'stderr', StringIO.StringIO())

        self.assertRaises(SystemExit, self.conf, ['--foo', 'bar'])

        self.assertTrue('foo' in sys.stderr.getvalue())
        self.assertTrue('bar' in sys.stderr.getvalue())

    def test_bad_int_arg(self):
        self._do_test_bad_cli_value(IntOpt)

    def test_bad_float_arg(self):
        self._do_test_bad_cli_value(FloatOpt)

    def test_conf_file_not_found(self):
        paths = self.create_tempfiles([('test', '')])
        os.remove(paths[0])
        self.tempfiles.remove(paths[0])

        self.assertRaises(ConfigFilesNotFoundError,
                          self.conf, ['--config-file', paths[0]])

    def test_conf_file_broken(self):
        paths = self.create_tempfiles([('test', 'foo')])

        self.assertRaises(ConfigFileParseError,
                          self.conf, ['--config-file', paths[0]])

    def _do_test_conf_file_bad_value(self, opt_class):
        self.conf.register_opt(opt_class('foo'))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = bar\n')])

        self.conf(['--config-file', paths[0]])

        self.assertRaises(ConfigFileValueError, getattr, self.conf, 'foo')

    def test_conf_file_bad_bool(self):
        self._do_test_conf_file_bad_value(BoolOpt)

    def test_conf_file_bad_int(self):
        self._do_test_conf_file_bad_value(IntOpt)

    def test_conf_file_bad_float(self):
        self._do_test_conf_file_bad_value(FloatOpt)

    def test_str_sub_from_group(self):
        self.conf.register_group(OptGroup('f'))
        self.conf.register_cli_opt(StrOpt('oo', default='blaa'), group='f')
        self.conf.register_cli_opt(StrOpt('bar', default='$f.oo'))

        self.conf([])

        self.assertFalse(hasattr(self.conf, 'bar'))
        self.assertRaises(TemplateSubstitutionError, getattr, self.conf, 'bar')

    def test_set_default_unknown_attr(self):
        self.conf([])
        self.assertRaises(NoSuchOptError, self.conf.set_default, 'foo', 'bar')

    def test_set_default_unknown_group(self):
        self.conf([])
        self.assertRaises(NoSuchGroupError,
                          self.conf.set_default, 'foo', 'bar', group='blaa')

    def test_set_override_unknown_attr(self):
        self.conf([])
        self.assertRaises(NoSuchOptError, self.conf.set_override, 'foo', 'bar')

    def test_set_override_unknown_group(self):
        self.conf([])
        self.assertRaises(NoSuchGroupError,
                          self.conf.set_override, 'foo', 'bar', group='blaa')


class FindFileTestCase(BaseTestCase):

    def test_find_policy_file(self):
        policy_file = '/etc/policy.json'

        self.stubs.Set(os.path, 'exists', lambda p: p == policy_file)

        self.conf([])

        self.assertEquals(self.conf.find_file('foo.json'), None)
        self.assertEquals(self.conf.find_file('policy.json'), policy_file)

    def test_find_policy_file_with_config_file(self):
        dir = tempfile.mkdtemp()
        self.tempdirs.append(dir)

        paths = self.create_tempfiles([(os.path.join(dir, 'test.conf'),
                                        '[DEFAULT]'),
                                       (os.path.join(dir, 'policy.json'),
                                        '{}')],
                                      ext='')

        self.conf(['--config-file', paths[0]])

        self.assertEquals(self.conf.find_file('policy.json'), paths[1])

    def test_find_policy_file_with_config_dir(self):
        dir = tempfile.mkdtemp()
        self.tempdirs.append(dir)

        path = self.create_tempfiles([(os.path.join(dir, 'policy.json'),
                                       '{}')],
                                     ext='')[0]

        self.conf(['--config-dir', dir])

        self.assertEquals(self.conf.find_file('policy.json'), path)


class OptDumpingTestCase(BaseTestCase):

    class FakeLogger:

        def __init__(self, test_case, expected_lvl):
            self.test_case = test_case
            self.expected_lvl = expected_lvl
            self.logged = []

        def log(self, lvl, fmt, *args):
            self.test_case.assertEquals(lvl, self.expected_lvl)
            self.logged.append(fmt % args)

    def test_log_opt_values(self):
        self.conf.register_cli_opt(StrOpt('foo'))
        self.conf.register_cli_opt(StrOpt('passwd', secret=True))
        self.conf.register_group(OptGroup('blaa'))
        self.conf.register_cli_opt(StrOpt('bar'), 'blaa')
        self.conf.register_cli_opt(StrOpt('key', secret=True), 'blaa')

        self.conf(['--foo', 'this', '--blaa-bar', 'that',
                   '--blaa-key', 'admin', '--passwd', 'hush'])

        logger = self.FakeLogger(self, 666)

        self.conf.log_opt_values(logger, 666)

        self.assertEquals(logger.logged, [
                          "*" * 80,
                          "Configuration options gathered from:",
                          "command line args: ['--foo', 'this', '--blaa-bar', "
                          "'that', '--blaa-key', 'admin', '--passwd', 'hush']",
                          "config files: []",
                          "=" * 80,
                          "config_dir                     = None",
                          "config_file                    = []",
                          "foo                            = this",
                          "passwd                         = ****",
                          "blaa.bar                       = that",
                          "blaa.key                       = *****",
                          "*" * 80,
                          ])


class CommonOptsTestCase(BaseTestCase):

    def setUp(self):
        super(CommonOptsTestCase, self).setUp()
        self.conf = CommonConfigOpts()

    def test_print_help(self):
        f = StringIO.StringIO()
        self.conf([])
        self.conf.print_help(file=f)
        self.assertTrue('debug' in f.getvalue())
        self.assertTrue('verbose' in f.getvalue())
        self.assertTrue('log-config' in f.getvalue())
        self.assertTrue('log-format' in f.getvalue())

    def test_debug_verbose(self):
        self.conf(['--debug', '--verbose'])

        self.assertEquals(self.conf.debug, True)
        self.assertEquals(self.conf.verbose, True)

    def test_logging_opts(self):
        self.conf([])

        self.assertTrue(self.conf.log_config is None)
        self.assertTrue(self.conf.log_file is None)
        self.assertTrue(self.conf.log_dir is None)

        self.assertEquals(self.conf.log_format,
                          CommonConfigOpts.DEFAULT_LOG_FORMAT)
        self.assertEquals(self.conf.log_date_format,
                          CommonConfigOpts.DEFAULT_LOG_DATE_FORMAT)

        self.assertEquals(self.conf.use_syslog, False)

    def test_log_file(self):
        log_file = '/some/path/foo-bar.log'
        self.conf(['--log-file', log_file])
        self.assertEquals(self.conf.log_file, log_file)

    def test_logfile_deprecated(self):
        logfile = '/some/other/path/foo-bar.log'
        self.conf(['--logfile', logfile])
        self.assertEquals(self.conf.log_file, logfile)

    def test_log_dir(self):
        log_dir = '/some/path/'
        self.conf(['--log-dir', log_dir])
        self.assertEquals(self.conf.log_dir, log_dir)

    def test_logdir_deprecated(self):
        logdir = '/some/other/path/'
        self.conf(['--logdir', logdir])
        self.assertEquals(self.conf.log_dir, logdir)


class ConfigParserTestCase(unittest.TestCase):
    def test_no_section(self):
        with tempfile.NamedTemporaryFile() as tmpfile:
            tmpfile.write('foo = bar')
            tmpfile.flush()

            parser = ConfigParser(tmpfile.name, {})
            self.assertRaises(ParseError, parser.parse)


class TildeExpansionTestCase(BaseTestCase):

    def test_config_file_tilde(self):
        homedir = os.path.expanduser('~')
        tmpfile = tempfile.mktemp(dir=homedir, prefix='cfg-', suffix='.conf')
        tmpbase = os.path.basename(tmpfile)

        try:
            self.conf(['--config-file', os.path.join('~', tmpbase)])
        except ConfigFilesNotFoundError, cfnfe:
            print cfnfe
            self.assertTrue(homedir in str(cfnfe))

        self.stubs.Set(os.path, 'exists', lambda p: p == tmpfile)

        self.assertEquals(self.conf.find_file(tmpbase), tmpfile)

    def test_config_dir_tilde(self):
        homedir = os.path.expanduser('~')
        tmpdir = tempfile.mktemp(dir=homedir,
                                 prefix='cfg-',
                                 suffix='.d')
        tmpfile = os.path.join(tmpdir, 'foo.conf')
        tmpbase = os.path.basename(tmpfile)

        self.stubs.Set(glob, 'glob', lambda p: [tmpfile])

        try:
            print ['--config-dir', os.path.join('~', os.path.basename(tmpdir))]
            self.conf(['--config-dir',
                       os.path.join('~', os.path.basename(tmpdir))])
        except ConfigFilesNotFoundError, cfnfe:
            print cfnfe
            self.assertTrue(os.path.expanduser('~') in str(cfnfe))

        self.stubs.Set(os.path, 'exists', lambda p: p == tmpfile)

        self.assertEquals(self.conf.find_file(tmpbase), tmpfile)


class SubCommandTestCase(BaseTestCase):

    def test_sub_command(self):
        def add_parsers(subparsers):
            sub = subparsers.add_parser('a')
            sub.add_argument('bar', type=int)

        self.conf.register_cli_opt(SubCommandOpt('cmd', handler=add_parsers))
        self.assertTrue(hasattr(self.conf, 'cmd'))
        self.conf(['a', '10'])
        self.assertTrue(hasattr(self.conf.cmd, 'name'))
        self.assertTrue(hasattr(self.conf.cmd, 'bar'))
        self.assertEquals(self.conf.cmd.name, 'a')
        self.assertEquals(self.conf.cmd.bar, 10)

    def test_sub_command_with_dest(self):
        def add_parsers(subparsers):
            sub = subparsers.add_parser('a')

        self.conf.register_cli_opt(SubCommandOpt('cmd', dest='command',
                                                 handler=add_parsers))
        self.assertTrue(hasattr(self.conf, 'command'))
        self.conf(['a'])
        self.assertEquals(self.conf.command.name, 'a')

    def test_sub_command_with_group(self):
        def add_parsers(subparsers):
            sub = subparsers.add_parser('a')
            sub.add_argument('--bar', choices='XYZ')

        self.conf.register_cli_opt(SubCommandOpt('cmd', handler=add_parsers),
                                   group='blaa')
        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'cmd'))
        self.conf(['a', '--bar', 'Z'])
        self.assertTrue(hasattr(self.conf.blaa.cmd, 'name'))
        self.assertTrue(hasattr(self.conf.blaa.cmd, 'bar'))
        self.assertEquals(self.conf.blaa.cmd.name, 'a')
        self.assertEquals(self.conf.blaa.cmd.bar, 'Z')

    def test_sub_command_not_cli(self):
        self.conf.register_opt(SubCommandOpt('cmd'))
        self.conf([])

    def test_sub_command_resparse(self):
        def add_parsers(subparsers):
            sub = subparsers.add_parser('a')

        self.conf.register_cli_opt(SubCommandOpt('cmd',
                                                 handler=add_parsers))

        foo_opt = StrOpt('foo')
        self.conf.register_cli_opt(foo_opt)

        self.conf(['--foo=bar', 'a'])

        self.assertTrue(hasattr(self.conf.cmd, 'name'))
        self.assertEquals(self.conf.cmd.name, 'a')
        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEquals(self.conf.foo, 'bar')

        self.conf.clear()
        self.conf.unregister_opt(foo_opt)
        self.conf(['a'])

        self.assertTrue(hasattr(self.conf.cmd, 'name'))
        self.assertEquals(self.conf.cmd.name, 'a')
        self.assertFalse(hasattr(self.conf, 'foo'))

    def test_sub_command_no_handler(self):
        self.conf.register_cli_opt(SubCommandOpt('cmd'))
        self.stubs.Set(sys, 'stderr', StringIO.StringIO())
        self.assertRaises(SystemExit, self.conf, [])
        self.assertTrue('error' in sys.stderr.getvalue())

    def test_sub_command_with_help(self):
        def add_parsers(subparsers):
            sub = subparsers.add_parser('a')

        self.conf.register_cli_opt(SubCommandOpt('cmd',
                                                 title='foo foo',
                                                 description='bar bar',
                                                 help='blaa blaa',
                                                 handler=add_parsers))
        self.stubs.Set(sys, 'stdout', StringIO.StringIO())
        self.assertRaises(SystemExit, self.conf, ['--help'])
        self.assertTrue('foo foo' in sys.stdout.getvalue())
        self.assertTrue('bar bar' in sys.stdout.getvalue())
        self.assertTrue('blaa blaa' in sys.stdout.getvalue())

    def test_sub_command_errors(self):
        def add_parsers(subparsers):
            sub = subparsers.add_parser('a')
            sub.add_argument('--bar')

        self.conf.register_cli_opt(BoolOpt('bar'))
        self.conf.register_cli_opt(SubCommandOpt('cmd', handler=add_parsers))
        self.conf(['a'])
        self.assertRaises(DuplicateOptError, getattr, self.conf.cmd, 'bar')
        self.assertRaises(NoSuchOptError, getattr, self.conf.cmd, 'foo')

    def test_sub_command_multiple(self):
        self.conf.register_cli_opt(SubCommandOpt('cmd1'))
        self.conf.register_cli_opt(SubCommandOpt('cmd2'))
        self.stubs.Set(sys, 'stderr', StringIO.StringIO())
        self.assertRaises(SystemExit, self.conf, [])
        self.assertTrue('multiple' in sys.stderr.getvalue())


class SetDefaultsTestCase(BaseTestCase):

    def test_default_to_none(self):
        opts = [StrOpt('foo', default='foo')]
        self.conf.register_opts(opts)
        set_defaults(opts, foo=None)
        self.conf([])
        self.assertEquals(self.conf.foo, None)

    def test_default_from_none(self):
        opts = [StrOpt('foo')]
        self.conf.register_opts(opts)
        set_defaults(opts, foo='bar')
        self.conf([])
        self.assertEquals(self.conf.foo, 'bar')

    def test_change_default(self):
        opts = [StrOpt('foo', default='foo')]
        self.conf.register_opts(opts)
        set_defaults(opts, foo='bar')
        self.conf([])
        self.assertEquals(self.conf.foo, 'bar')

    def test_group_default_to_none(self):
        opts = [StrOpt('foo', default='foo')]
        self.conf.register_opts(opts, group='blaa')
        set_defaults(opts, foo=None)
        self.conf([])
        self.assertEquals(self.conf.blaa.foo, None)

    def test_group_default_from_none(self):
        opts = [StrOpt('foo')]
        self.conf.register_opts(opts, group='blaa')
        set_defaults(opts, foo='bar')
        self.conf([])
        self.assertEquals(self.conf.blaa.foo, 'bar')

    def test_group_change_default(self):
        opts = [StrOpt('foo', default='foo')]
        self.conf.register_opts(opts, group='blaa')
        set_defaults(opts, foo='bar')
        self.conf([])
        self.assertEquals(self.conf.blaa.foo, 'bar')
