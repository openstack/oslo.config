# Copyright 2014 Red Hat, Inc.
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

import sys

import fixtures
import mock
from oslotest import base
from six import moves
import tempfile
import testscenarios

from oslo_config import cfg
from oslo_config import fixture as config_fixture
from oslo_config import generator
from oslo_config import types

load_tests = testscenarios.load_tests_apply_scenarios


class GeneratorTestCase(base.BaseTestCase):

    groups = {
        'group1': cfg.OptGroup(name='group1',
                               help='Lorem ipsum dolor sit amet, consectetur '
                                    'adipisicing elit, sed do eiusmod tempor '
                                    'incididunt ut labore et dolore magna '
                                    'aliqua. Ut enim ad minim veniam, quis '
                                    'nostrud exercitation ullamco laboris '
                                    'nisi ut aliquip ex ea commodo '
                                    'consequat. Duis aute irure dolor in.'),
        'group2': cfg.OptGroup(name='group2', title='Group 2'),
        'foo': cfg.OptGroup(name='foo', title='Foo Title', help='foo help'),
    }

    opts = {
        'foo': cfg.StrOpt('foo', help='foo option'),
        'bar': cfg.StrOpt('bar', help='bar option'),
        'foo-bar': cfg.StrOpt('foo-bar', help='foobar'),
        'no_help': cfg.StrOpt('no_help'),
        'long_help': cfg.StrOpt('long_help',
                                help='Lorem ipsum dolor sit amet, consectetur '
                                     'adipisicing elit, sed do eiusmod tempor '
                                     'incididunt ut labore et dolore magna '
                                     'aliqua. Ut enim ad minim veniam, quis '
                                     'nostrud exercitation ullamco laboris '
                                     'nisi ut aliquip ex ea commodo '
                                     'consequat. Duis aute irure dolor in '
                                     'reprehenderit in voluptate velit esse '
                                     'cillum dolore eu fugiat nulla '
                                     'pariatur. Excepteur sint occaecat '
                                     'cupidatat non proident, sunt in culpa '
                                     'qui officia deserunt mollit anim id est '
                                     'laborum.'),
        'long_help_pre': cfg.StrOpt('long_help_pre',
                                    help='This is a very long help text which '
                                         'is preformatted with line breaks. '
                                         'It should break when it is too long '
                                         'but also keep the specified line '
                                         'breaks. This makes it possible to '
                                         'create lists with items:\n'
                                         '\n'
                                         '* item 1\n'
                                         '* item 2\n'
                                         '\n'
                                         'and should increase the '
                                         'readability.'),
        'choices_opt': cfg.StrOpt('choices_opt',
                                  default='a',
                                  choices=(None, '', 'a', 'b', 'c'),
                                  help='a string with choices'),
        'deprecated_opt': cfg.StrOpt('bar',
                                     deprecated_name='foobar',
                                     help='deprecated'),
        'deprecated_for_removal_opt': cfg.StrOpt(
            'bar', deprecated_for_removal=True, help='deprecated for removal'),
        'deprecated_reason_opt': cfg.BoolOpt(
            'turn_off_stove',
            default=False,
            deprecated_for_removal=True,
            deprecated_reason='This was supposed to work but it really, '
                              'really did not. Always buy house insurance.',
            help='DEPRECATED: Turn off stove'),
        'deprecated_group': cfg.StrOpt('bar',
                                       deprecated_group='group1',
                                       deprecated_name='foobar',
                                       help='deprecated'),
        # Unknown Opt default must be a string
        'unknown_type': cfg.Opt('unknown_opt',
                                default='123',
                                help='unknown',
                                type=types.String(type_name='unknown type')),
        'str_opt': cfg.StrOpt('str_opt',
                              default='foo bar',
                              help='a string'),
        'str_opt_sample_default': cfg.StrOpt('str_opt',
                                             default='fooishbar',
                                             help='a string'),
        'str_opt_with_space': cfg.StrOpt('str_opt',
                                         default='  foo bar  ',
                                         help='a string with spaces'),
        'bool_opt': cfg.BoolOpt('bool_opt',
                                default=False,
                                help='a boolean'),
        'int_opt': cfg.IntOpt('int_opt',
                              default=10,
                              min=1,
                              max=20,
                              help='an integer'),
        'int_opt_min_0': cfg.IntOpt('int_opt_min_0',
                                    default=10,
                                    min=0,
                                    max=20,
                                    help='an integer'),
        'int_opt_max_0': cfg.IntOpt('int_opt_max_0',
                                    default=-1,
                                    max=0,
                                    help='an integer'),
        'float_opt': cfg.FloatOpt('float_opt',
                                  default=0.1,
                                  help='a float'),
        'list_opt': cfg.ListOpt('list_opt',
                                default=['1', '2', '3'],
                                help='a list'),
        'dict_opt': cfg.DictOpt('dict_opt',
                                default={'1': 'yes', '2': 'no'},
                                help='a dict'),
        'ip_opt': cfg.IPOpt('ip_opt',
                            default='127.0.0.1',
                            help='an ip address'),
        'port_opt': cfg.PortOpt('port_opt',
                                default=80,
                                help='a port'),
        'hostname_opt': cfg.HostnameOpt('hostname_opt',
                                        default='compute01.nova.site1',
                                        help='a hostname'),
        'multi_opt': cfg.MultiStrOpt('multi_opt',
                                     default=['1', '2', '3'],
                                     help='multiple strings'),
        'multi_opt_none': cfg.MultiStrOpt('multi_opt_none',
                                          help='multiple strings'),
        'multi_opt_empty': cfg.MultiStrOpt('multi_opt_empty',
                                           default=[],
                                           help='multiple strings'),
        'multi_opt_sample_default': cfg.MultiStrOpt('multi_opt',
                                                    default=['1', '2', '3'],
                                                    sample_default=['5', '6'],
                                                    help='multiple strings'),
        'string_type_with_bad_default': cfg.Opt('string_type_with_bad_default',
                                                help='string with bad default',
                                                default=4096),
        'custom_type': cfg.Opt('custom_type',
                               help='custom help',
                               type=type('string')),
        'custom_type_name': cfg.Opt('custom_opt_type',
                                    type=types.Integer(type_name='port'
                                                       ' number'),
                                    default=5511,
                                    help='this is a port'),
    }

    content_scenarios = [
        ('empty',
         dict(opts=[], expected='''[DEFAULT]
''')),
        ('single_namespace',
         dict(opts=[('test', [(None, [opts['foo']])])],
              expected='''[DEFAULT]

#
# From test
#

# foo option (string value)
#foo = <None>
''')),
        ('multiple_namespaces',
         dict(opts=[('test', [(None, [opts['foo']])]),
                    ('other', [(None, [opts['bar']])])],
              expected='''[DEFAULT]

#
# From other
#

# bar option (string value)
#bar = <None>

#
# From test
#

# foo option (string value)
#foo = <None>
''')),
        ('group',
         dict(opts=[('test', [(groups['group1'], [opts['foo']])])],
              expected='''[DEFAULT]


[group1]
# Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do
# eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim
# ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
# aliquip ex ea commodo consequat. Duis aute irure dolor in.

#
# From test
#

# foo option (string value)
#foo = <None>
''')),
        ('empty_group',
         dict(opts=[('test', [(groups['group1'], [])])],
              expected='''[DEFAULT]
''')),
        ('multiple_groups',
         dict(opts=[('test', [(groups['group1'], [opts['foo']]),
                              (groups['group2'], [opts['bar']])])],
              expected='''[DEFAULT]


[group1]
# Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do
# eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim
# ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
# aliquip ex ea commodo consequat. Duis aute irure dolor in.

#
# From test
#

# foo option (string value)
#foo = <None>


[group2]

#
# From test
#

# bar option (string value)
#bar = <None>
''')),
        ('group_in_multiple_namespaces',
         dict(opts=[('test', [(groups['group1'], [opts['foo']])]),
                    ('other', [(groups['group1'], [opts['bar']])])],
              expected='''[DEFAULT]


[group1]
# Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do
# eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim
# ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
# aliquip ex ea commodo consequat. Duis aute irure dolor in.

#
# From other
#

# bar option (string value)
#bar = <None>

#
# From test
#

# foo option (string value)
#foo = <None>
''')),
        ('hyphenated_name',
         dict(opts=[('test', [(None, [opts['foo-bar']])])],
              expected='''[DEFAULT]

#
# From test
#

# foobar (string value)
#foo_bar = <None>
''')),
        ('no_help',
         dict(opts=[('test', [(None, [opts['no_help']])])],
              log_warning=('"%s" is missing a help string', 'no_help'),
              expected='''[DEFAULT]

#
# From test
#

# (string value)
#no_help = <None>
''')),
        ('long_help',
         dict(opts=[('test', [(None, [opts['long_help']])])],
              expected='''[DEFAULT]

#
# From test
#

# Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do
# eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim
# ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
# aliquip ex ea commodo consequat. Duis aute irure dolor in
# reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
# pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
# culpa qui officia deserunt mollit anim id est laborum. (string
# value)
#long_help = <None>
''')),
        ('long_help_wrap_at_40',
         dict(opts=[('test', [(None, [opts['long_help']])])],
              wrap_width=40,
              expected='''[DEFAULT]

#
# From test
#

# Lorem ipsum dolor sit amet,
# consectetur adipisicing elit, sed do
# eiusmod tempor incididunt ut labore et
# dolore magna aliqua. Ut enim ad minim
# veniam, quis nostrud exercitation
# ullamco laboris nisi ut aliquip ex ea
# commodo consequat. Duis aute irure
# dolor in reprehenderit in voluptate
# velit esse cillum dolore eu fugiat
# nulla pariatur. Excepteur sint
# occaecat cupidatat non proident, sunt
# in culpa qui officia deserunt mollit
# anim id est laborum. (string value)
#long_help = <None>
''')),
        ('long_help_no_wrapping',
         dict(opts=[('test', [(None, [opts['long_help']])])],
              wrap_width=0,
              expected='''[DEFAULT]

#
# From test
#

'''   # noqa
'# Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod '
'tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, '
'quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo '
'consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse '
'cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat '
'non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. '
'(string value)'
'''
#long_help = <None>
''')),
        ('long_help_with_preformatting',
         dict(opts=[('test', [(None, [opts['long_help_pre']])])],
              wrap_width=70,
              expected='''[DEFAULT]

#
# From test
#

# This is a very long help text which is preformatted with line
# breaks. It should break when it is too long but also keep the
# specified line breaks. This makes it possible to create lists with
# items:
#
# * item 1
# * item 2
#
# and should increase the readability. (string value)
#long_help_pre = <None>
''')),
        ('choices_opt',
         dict(opts=[('test', [(None, [opts['choices_opt']])])],
              expected='''[DEFAULT]

#
# From test
#

# a string with choices (string value)
# Allowed values: <None>, '', a, b, c
#choices_opt = a
''')),
        ('deprecated',
         dict(opts=[('test', [(groups['foo'], [opts['deprecated_opt']])])],
              expected='''[DEFAULT]


[foo]
# foo help

#
# From test
#

# deprecated (string value)
# Deprecated group/name - [DEFAULT]/foobar
#bar = <None>
''')),
        ('deprecated_for_removal',
         dict(opts=[('test', [(groups['foo'],
                              [opts['deprecated_for_removal_opt']])])],
              expected='''[DEFAULT]


[foo]
# foo help

#
# From test
#

# DEPRECATED: deprecated for removal (string value)
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
#bar = <None>
''')),
        ('deprecated_reason',
         dict(opts=[('test', [(groups['foo'],
                              [opts['deprecated_reason_opt']])])],
              expected='''[DEFAULT]


[foo]
# foo help

#
# From test
#

# DEPRECATED: Turn off stove (boolean value)
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
# Reason: This was supposed to work but it really, really did not.
# Always buy house insurance.
#turn_off_stove = false
''')),
        ('deprecated_group',
         dict(opts=[('test', [(groups['foo'], [opts['deprecated_group']])])],
              expected='''[DEFAULT]


[foo]
# foo help

#
# From test
#

# deprecated (string value)
# Deprecated group/name - [group1]/foobar
#bar = <None>
''')),
        ('unknown_type',
         dict(opts=[('test', [(None, [opts['unknown_type']])])],
              expected='''[DEFAULT]

#
# From test
#

# unknown (unknown type)
#unknown_opt = 123
''')),
        ('str_opt',
         dict(opts=[('test', [(None, [opts['str_opt']])])],
              expected='''[DEFAULT]

#
# From test
#

# a string (string value)
#str_opt = foo bar
''')),
        ('str_opt_with_space',
         dict(opts=[('test', [(None, [opts['str_opt_with_space']])])],
              expected='''[DEFAULT]

#
# From test
#

# a string with spaces (string value)
#str_opt = "  foo bar  "
''')),
        ('bool_opt',
         dict(opts=[('test', [(None, [opts['bool_opt']])])],
              expected='''[DEFAULT]

#
# From test
#

# a boolean (boolean value)
#bool_opt = false
''')),
        ('int_opt',
         dict(opts=[('test', [(None, [opts['int_opt']])])],
              expected='''[DEFAULT]

#
# From test
#

# an integer (integer value)
# Minimum value: 1
# Maximum value: 20
#int_opt = 10
''')),
        ('int_opt_min_0',
         dict(opts=[('test', [(None, [opts['int_opt_min_0']])])],
              expected='''[DEFAULT]

#
# From test
#

# an integer (integer value)
# Minimum value: 0
# Maximum value: 20
#int_opt_min_0 = 10
''')),
        ('int_opt_max_0',
         dict(opts=[('test', [(None, [opts['int_opt_max_0']])])],
              expected='''[DEFAULT]

#
# From test
#

# an integer (integer value)
# Maximum value: 0
#int_opt_max_0 = -1
''')),

        ('float_opt',
         dict(opts=[('test', [(None, [opts['float_opt']])])],
              expected='''[DEFAULT]

#
# From test
#

# a float (floating point value)
#float_opt = 0.1
''')),
        ('list_opt',
         dict(opts=[('test', [(None, [opts['list_opt']])])],
              expected='''[DEFAULT]

#
# From test
#

# a list (list value)
#list_opt = 1,2,3
''')),
        ('dict_opt',
         dict(opts=[('test', [(None, [opts['dict_opt']])])],
              expected='''[DEFAULT]

#
# From test
#

# a dict (dict value)
#dict_opt = 1:yes,2:no
''')),
        ('ip_opt',
         dict(opts=[('test', [(None, [opts['ip_opt']])])],
              expected='''[DEFAULT]

#
# From test
#

# an ip address (IP address value)
#ip_opt = 127.0.0.1
''')),
        ('port_opt',
         dict(opts=[('test', [(None, [opts['port_opt']])])],
              expected='''[DEFAULT]

#
# From test
#

# a port (port value)
# Minimum value: 0
# Maximum value: 65535
#port_opt = 80
''')),
        ('hostname_opt',
         dict(opts=[('test', [(None, [opts['hostname_opt']])])],
              expected='''[DEFAULT]

#
# From test
#

# a hostname (hostname value)
#hostname_opt = compute01.nova.site1
''')),
        ('multi_opt',
         dict(opts=[('test', [(None, [opts['multi_opt']])])],
              expected='''[DEFAULT]

#
# From test
#

# multiple strings (multi valued)
#multi_opt = 1
#multi_opt = 2
#multi_opt = 3
''')),
        ('multi_opt_none',
         dict(opts=[('test', [(None, [opts['multi_opt_none']])])],
              expected='''[DEFAULT]

#
# From test
#

# multiple strings (multi valued)
#multi_opt_none =
''')),
        ('multi_opt_empty',
         dict(opts=[('test', [(None, [opts['multi_opt_empty']])])],
              expected='''[DEFAULT]

#
# From test
#

# multiple strings (multi valued)
#multi_opt_empty =
''')),
        ('str_opt_sample_default',
         dict(opts=[('test', [(None, [opts['str_opt_sample_default']])])],
              expected='''[DEFAULT]

#
# From test
#

# a string (string value)
#str_opt = fooishbar
''')),
        ('multi_opt_sample_default',
         dict(opts=[('test', [(None, [opts['multi_opt_sample_default']])])],
              expected='''[DEFAULT]

#
# From test
#

# multiple strings (multi valued)
#multi_opt = 5
#multi_opt = 6
''')),
        ('custom_type_name',
         dict(opts=[('test', [(None, [opts['custom_type_name']])])],
              expected='''[DEFAULT]

#
# From test
#

# this is a port (port number)
#custom_opt_type = 5511
''')),
        ('custom_type',
         dict(opts=[('test', [(None, [opts['custom_type']])])],
              expected='''[DEFAULT]

#
# From test
#

# custom help (unknown value)
#custom_type = <None>
''')),
        ('string_type_with_bad_default',
         dict(opts=[('test', [(None,
                               [opts['string_type_with_bad_default']])])],
              expected='''[DEFAULT]

#
# From test
#

# string with bad default (string value)
#string_type_with_bad_default = 4096
''')),
         ('str_opt_str_group',
         dict(opts=[('test', [('foo',
                               [opts['str_opt']]),
                              (groups['foo'],
                               [opts['int_opt']])]),
                    ('foo', [('foo',
                               [opts['bool_opt']])])],
              expected='''[DEFAULT]


[foo]
# foo help

#
# From foo
#

# a boolean (boolean value)
#bool_opt = false

#
# From test
#

# a string (string value)
#str_opt = foo bar

#
# From test
#

# an integer (integer value)
# Minimum value: 1
# Maximum value: 20
#int_opt = 10
''')),
         ('opt_str_opt_group',
         dict(opts=[('test', [(groups['foo'],
                               [opts['int_opt']]),
                              ('foo',
                               [opts['str_opt']])]),
                    ('foo', [(groups['foo'],
                              [opts['bool_opt']])])],
              expected='''[DEFAULT]


[foo]
# foo help

#
# From foo
#

# a boolean (boolean value)
#bool_opt = false

#
# From test
#

# an integer (integer value)
# Minimum value: 1
# Maximum value: 20
#int_opt = 10

#
# From test
#

# a string (string value)
#str_opt = foo bar
''')),
    ]

    output_file_scenarios = [
        ('stdout',
         dict(stdout=True, output_file=None)),
        ('output_file',
         dict(output_file='sample.conf', stdout=False)),
    ]

    @classmethod
    def generate_scenarios(cls):
        cls.scenarios = testscenarios.multiply_scenarios(
            cls.content_scenarios,
            cls.output_file_scenarios)

    def setUp(self):
        super(GeneratorTestCase, self).setUp()

        self.conf = cfg.ConfigOpts()
        self.config_fixture = config_fixture.Config(self.conf)
        self.config = self.config_fixture.config
        self.useFixture(self.config_fixture)

        self.tempdir = self.useFixture(fixtures.TempDir())

    def _capture_stream(self, stream_name):
        self.useFixture(fixtures.MonkeyPatch("sys.%s" % stream_name,
                                             moves.StringIO()))
        return getattr(sys, stream_name)

    def _capture_stdout(self):
        return self._capture_stream('stdout')

    @mock.patch.object(generator, '_get_raw_opts_loaders')
    @mock.patch.object(generator, 'LOG')
    def test_generate(self, mock_log, raw_opts_loader):
        generator.register_cli_opts(self.conf)

        namespaces = [i[0] for i in self.opts]
        self.config(namespace=namespaces)

        for group in self.groups.values():
            self.conf.register_group(group)

        wrap_width = getattr(self, 'wrap_width', None)
        if wrap_width is not None:
            self.config(wrap_width=wrap_width)

        if self.stdout:
            stdout = self._capture_stdout()
        else:
            output_file = self.tempdir.join(self.output_file)
            self.config(output_file=output_file)

        # We have a static data structure matching what should be
        # returned by _list_opts() but we're mocking out a lower level
        # function that needs to return a namespace and a callable to
        # return options from that namespace. We have to pass opts to
        # the lambda to cache a reference to the name because the list
        # comprehension changes the thing pointed to by the name each
        # time through the loop.
        raw_opts_loader.return_value = [
            (ns, lambda opts=opts: opts)
            for ns, opts in self.opts
        ]

        generator.generate(self.conf)

        if self.stdout:
            self.assertEqual(self.expected, stdout.getvalue())
        else:
            with open(output_file, 'r') as f:
                actual = f.read()
            self.assertEqual(self.expected, actual)

        log_warning = getattr(self, 'log_warning', None)
        if log_warning is not None:
            mock_log.warning.assert_called_once_with(*log_warning)
        else:
            self.assertFalse(mock_log.warning.called)


class IgnoreDoublesTestCase(base.BaseTestCase):

    opts = [cfg.StrOpt('foo', help='foo option'),
            cfg.StrOpt('bar', help='bar option'),
            cfg.StrOpt('foo_bar', help='foobar'),
            cfg.StrOpt('str_opt', help='a string'),
            cfg.BoolOpt('bool_opt', help='a boolean'),
            cfg.IntOpt('int_opt', help='an integer')]

    def test_cleanup_opts_default(self):
        o = [("namespace1", [
              ("group1", self.opts)])]
        self.assertEqual(o, generator._cleanup_opts(o))

    def test_cleanup_opts_dup_opt(self):
        o = [("namespace1", [
              ("group1", self.opts + [self.opts[0]])])]
        e = [("namespace1", [
              ("group1", self.opts)])]
        self.assertEqual(e, generator._cleanup_opts(o))

    def test_cleanup_opts_dup_groups_opt(self):
        o = [("namespace1", [
              ("group1", self.opts + [self.opts[1]]),
              ("group2", self.opts),
              ("group3", self.opts + [self.opts[2]])])]
        e = [("namespace1", [
              ("group1", self.opts),
              ("group2", self.opts),
              ("group3", self.opts)])]
        self.assertEqual(e, generator._cleanup_opts(o))

    def test_cleanup_opts_dup_namespace_groups_opts(self):
        o = [("namespace1", [
              ("group1", self.opts + [self.opts[1]]),
              ("group2", self.opts)]),
             ("namespace2", [
              ("group1", self.opts + [self.opts[2]]),
              ("group2", self.opts)])]
        e = [("namespace1", [
              ("group1", self.opts),
              ("group2", self.opts)]),
             ("namespace2", [
              ("group1", self.opts),
              ("group2", self.opts)])]
        self.assertEqual(e, generator._cleanup_opts(o))

    @mock.patch.object(generator, '_get_raw_opts_loaders')
    def test_list_ignores_doubles(self, raw_opts_loaders):
        config_opts = [
            (None, [cfg.StrOpt('foo'), cfg.StrOpt('bar')]),
        ]

        # These are the very same config options, but read twice.
        # This is possible if one misconfigures the entry point for the
        # sample config generator.
        raw_opts_loaders.return_value = [
            ('namespace', lambda: config_opts),
            ('namespace', lambda: config_opts),
        ]

        slurped_opts = 0
        for _, listing in generator._list_opts(None):
            for _, opts in listing:
                slurped_opts += len(opts)
        self.assertEqual(2, slurped_opts)


class GeneratorAdditionalTestCase(base.BaseTestCase):

    opts = [cfg.StrOpt('foo', help='foo option', default='fred'),
            cfg.StrOpt('bar', help='bar option'),
            cfg.StrOpt('foo_bar', help='foobar'),
            cfg.StrOpt('str_opt', help='a string'),
            cfg.BoolOpt('bool_opt', help='a boolean'),
            cfg.IntOpt('int_opt', help='an integer')]

    def test_get_groups_empty_ns(self):
        groups = generator._get_groups([])
        self.assertEqual({'DEFAULT': {'object': None, 'namespaces': []}},
                         groups)

    def test_get_groups_single_ns(self):
        config = [("namespace1", [
                   ("beta", self.opts),
                   ("alpha", self.opts)])]
        groups = generator._get_groups(config)
        self.assertEqual(['DEFAULT', 'alpha', 'beta'], sorted(groups))

    def test_get_groups_multiple_ns(self):
        config = [("namespace1", [
                   ("beta", self.opts),
                   ("alpha", self.opts)]),
                  ("namespace2", [
                   ("gamma", self.opts),
                   ("alpha", self.opts)])]
        groups = generator._get_groups(config)
        self.assertEqual(['DEFAULT', 'alpha', 'beta', 'gamma'], sorted(groups))

    def test_output_opts_empty_default(self):

        config = [("namespace1", [
                   ("alpha", [])])]
        groups = generator._get_groups(config)

        fd, tmp_file = tempfile.mkstemp()
        with open(tmp_file, 'w+') as f:
            formatter = generator._OptFormatter(output_file=f)
            generator._output_opts(formatter, 'DEFAULT', groups.pop('DEFAULT'))
        expected = '''[DEFAULT]
'''
        with open(tmp_file, 'r') as f:
            actual = f.read()
        self.assertEqual(expected, actual)

    def test_output_opts_group(self):

        config = [("namespace1", [
                   ("alpha", [self.opts[0]])])]
        groups = generator._get_groups(config)

        fd, tmp_file = tempfile.mkstemp()
        with open(tmp_file, 'w+') as f:
            formatter = generator._OptFormatter(output_file=f)
            generator._output_opts(formatter, 'alpha', groups.pop('alpha'))
        expected = '''[alpha]

#
# From namespace1
#

# foo option (string value)
#foo = fred
'''
        with open(tmp_file, 'r') as f:
            actual = f.read()
        self.assertEqual(expected, actual)


class GeneratorMutableOptionTestCase(base.BaseTestCase):

    def test_include_message(self):
        out = moves.StringIO()
        opt = cfg.StrOpt('foo', help='foo option', mutable=True)
        gen = generator._OptFormatter(output_file=out)
        gen.format(opt)
        result = out.getvalue()
        self.assertIn(
            'This option can be changed without restarting.',
            result,
        )

    def test_do_not_include_message(self):
        out = moves.StringIO()
        opt = cfg.StrOpt('foo', help='foo option', mutable=False)
        gen = generator._OptFormatter(output_file=out)
        gen.format(opt)
        result = out.getvalue()
        self.assertNotIn(
            'This option can be changed without restarting.',
            result,
        )


class GeneratorRaiseErrorTestCase(base.BaseTestCase):

    def test_generator_raises_error(self):
        """Verifies that errors from extension manager are not suppressed."""
        class FakeException(Exception):
            pass

        class FakeEP(object):

            def __init__(self):
                self.name = 'callback_is_expected'
                self.require = self.resolve
                self.load = self.resolve

            def resolve(self, *args, **kwargs):
                raise FakeException()

        fake_ep = FakeEP()
        self.conf = cfg.ConfigOpts()
        self.conf.register_opts(generator._generator_opts)
        self.conf.set_default('namespace', fake_ep.name)
        fake_eps = mock.Mock(return_value=[fake_ep])
        with mock.patch('pkg_resources.iter_entry_points', fake_eps):
            self.assertRaises(FakeException, generator.generate, self.conf)

    def test_generator_call_with_no_arguments_raises_error(self):
        testargs = ['oslo-config-generator']
        with mock.patch('sys.argv', testargs):
            self.assertRaises(cfg.RequiredOptError, generator.main, [])


class ChangeDefaultsTestCase(base.BaseTestCase):

    @mock.patch.object(generator, '_get_opt_default_updaters')
    @mock.patch.object(generator, '_get_raw_opts_loaders')
    def test_no_modifiers_registered(self, raw_opts_loaders, get_updaters):
        orig_opt = cfg.StrOpt('foo', default='bar')
        raw_opts_loaders.return_value = [
            ('namespace', lambda: [(None, [orig_opt])]),
        ]
        get_updaters.return_value = []

        opts = generator._list_opts(['namespace'])
        # NOTE(dhellmann): Who designed this data structure?
        the_opt = opts[0][1][0][1][0]

        self.assertEqual('bar', the_opt.default)
        self.assertIs(orig_opt, the_opt)

    @mock.patch.object(generator, '_get_opt_default_updaters')
    @mock.patch.object(generator, '_get_raw_opts_loaders')
    def test_change_default(self, raw_opts_loaders, get_updaters):
        orig_opt = cfg.StrOpt('foo', default='bar')
        raw_opts_loaders.return_value = [
            ('namespace', lambda: [(None, [orig_opt])]),
        ]

        def updater():
            cfg.set_defaults([orig_opt], foo='blah')

        get_updaters.return_value = [updater]

        opts = generator._list_opts(['namespace'])
        # NOTE(dhellmann): Who designed this data structure?
        the_opt = opts[0][1][0][1][0]

        self.assertEqual('blah', the_opt.default)
        self.assertIs(orig_opt, the_opt)


GeneratorTestCase.generate_scenarios()
