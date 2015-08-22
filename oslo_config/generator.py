# Copyright 2012 SINA Corporation
# Copyright 2014 Cisco Systems, Inc.
# All Rights Reserved.
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

"""Sample configuration generator

Tool for generating a sample configuration file. See
../doc/source/generator.rst for details.

"""

import logging
import operator
import sys
import textwrap

import pkg_resources
import six

from oslo_config import cfg
import stevedore.named  # noqa

LOG = logging.getLogger(__name__)

_generator_opts = [
    cfg.StrOpt('output-file',
               help='Path of the file to write to. Defaults to stdout.'),
    cfg.IntOpt('wrap-width',
               default=70,
               help='The maximum length of help lines.'),
    cfg.MultiStrOpt('namespace',
                    help='Option namespace under "oslo.config.opts" in which '
                         'to query for options.'),
]


def register_cli_opts(conf):
    """Register the formatter's CLI options with a ConfigOpts instance.

    Note, this must be done before the ConfigOpts instance is called to parse
    the configuration.

    :param conf: a ConfigOpts instance
    :raises: DuplicateOptError, ArgsAlreadyParsedError
    """
    conf.register_cli_opts(_generator_opts)


def _format_defaults(opt):
    "Return a list of formatted default values."
    if isinstance(opt, cfg.MultiStrOpt):
        if opt.sample_default is not None:
            defaults = opt.sample_default
        elif not opt.default:
            defaults = ['']
        else:
            defaults = opt.default
    else:
        if opt.sample_default is not None:
            default_str = str(opt.sample_default)
        elif opt.default is None:
            default_str = '<None>'
        elif isinstance(opt, cfg.StrOpt):
            default_str = opt.default
        elif isinstance(opt, cfg.BoolOpt):
            default_str = str(opt.default).lower()
        elif (isinstance(opt, cfg.IntOpt) or
              isinstance(opt, cfg.FloatOpt)):
            default_str = str(opt.default)
        elif isinstance(opt, cfg.ListOpt):
            default_str = ','.join(opt.default)
        elif isinstance(opt, cfg.DictOpt):
            sorted_items = sorted(opt.default.items(),
                                  key=operator.itemgetter(0))
            default_str = ','.join(['%s:%s' % i for i in sorted_items])
        else:
            LOG.warning('Unknown option type: %s', repr(opt))
            default_str = str(opt.default)
        defaults = [default_str]

    results = []
    for default_str in defaults:
        if default_str.strip() != default_str:
            default_str = '"%s"' % default_str
        results.append(default_str)
    return results


class _OptFormatter(object):

    """Format configuration option descriptions to a file."""

    _TYPE_DESCRIPTIONS = {
        cfg.StrOpt: 'string value',
        cfg.BoolOpt: 'boolean value',
        cfg.IntOpt: 'integer value',
        cfg.FloatOpt: 'floating point value',
        cfg.ListOpt: 'list value',
        cfg.DictOpt: 'dict value',
        cfg.MultiStrOpt: 'multi valued',
    }

    def __init__(self, output_file=None, wrap_width=70):
        """Construct an OptFormatter object.

        :param output_file: a writeable file object
        :param wrap_width: The maximum length of help lines, 0 to not wrap
        """
        self.output_file = output_file or sys.stdout
        self.wrap_width = wrap_width

    def _format_help(self, help_text):
        """Format the help for a group or option to the output file.

        :param help_text: The text of the help string
        """
        if self.wrap_width is not None and self.wrap_width > 0:
            wrapped = ""
            for line in help_text.splitlines():
                text = "\n".join(textwrap.wrap(line, self.wrap_width,
                                               initial_indent='# ',
                                               subsequent_indent='# ',
                                               break_long_words=False,
                                               replace_whitespace=False))
                wrapped += "#" if text == "" else text
                wrapped += "\n"
            lines = [wrapped]
        else:
            lines = ['# ' + help_text + '\n']
        return lines

    def _get_choice_text(self, choice):
        if choice is None:
            return '<None>'
        elif choice == '':
            return "''"
        return six.text_type(choice)

    def format(self, opt):
        """Format a description of an option to the output file.

        :param opt: a cfg.Opt instance
        """
        if not opt.help:
            LOG.warning('"%s" is missing a help string', opt.dest)

        opt_type = self._TYPE_DESCRIPTIONS.get(type(opt), 'unknown type')

        if opt.help:
            help_text = u'%s (%s)' % (opt.help,
                                      opt_type)
        else:
            help_text = u'(%s)' % opt_type
        lines = self._format_help(help_text)

        if getattr(opt.type, 'min', None):
            lines.append('# Minimum value: %d\n' % opt.type.min)

        if getattr(opt.type, 'max', None):
            lines.append('# Maximum value: %d\n' % opt.type.max)

        if getattr(opt.type, 'choices', None):
            choices_text = ', '.join([self._get_choice_text(choice)
                                      for choice in opt.type.choices])
            lines.append('# Allowed values: %s\n' % choices_text)

        for d in opt.deprecated_opts:
            lines.append('# Deprecated group/name - [%s]/%s\n' %
                         (d.group or 'DEFAULT', d.name or opt.dest))

        if opt.deprecated_for_removal:
            lines.append(
                '# This option is deprecated for removal.\n'
                '# Its value may be silently ignored in the future.\n')

        defaults = _format_defaults(opt)
        for default_str in defaults:
            if default_str:
                default_str = ' ' + default_str
            lines.append('#%s =%s\n' % (opt.dest, default_str))

        self.writelines(lines)

    def write(self, s):
        """Write an arbitrary string to the output file.

        :param s: an arbitrary string
        """
        self.output_file.write(s)

    def writelines(self, l):
        """Write an arbitrary sequence of strings to the output file.

        :param l: a list of arbitrary strings
        """
        self.output_file.writelines(l)


def _list_opts(namespaces):
    """List the options available via the given namespaces.

    :param namespaces: a list of namespaces registered under 'oslo.config.opts'
    :returns: a list of (namespace, [(group, [opt_1, opt_2])]) tuples
    """
    mgr = stevedore.named.NamedExtensionManager(
        'oslo.config.opts',
        names=namespaces,
        on_load_failure_callback=on_load_failure_callback,
        invoke_on_load=True)
    return [(ep.name, ep.obj) for ep in mgr]


def on_load_failure_callback(*args, **kwargs):
    raise


def generate(conf):
    """Generate a sample config file.

    List all of the options available via the namespaces specified in the given
    configuration and write a description of them to the specified output file.

    :param conf: a ConfigOpts instance containing the generator's configuration
    """
    conf.register_opts(_generator_opts)

    output_file = (open(conf.output_file, 'w')
                   if conf.output_file else sys.stdout)

    formatter = _OptFormatter(output_file=output_file,
                              wrap_width=conf.wrap_width)

    groups = {'DEFAULT': []}
    for namespace, listing in _list_opts(conf.namespace):
        for group, opts in listing:
            if not opts:
                continue
            namespaces = groups.setdefault(group or 'DEFAULT', [])
            namespaces.append((namespace, opts))

    def _output_opts(f, group, namespaces):
        if isinstance(group, cfg.OptGroup):
            group_name = group.name
        else:
            group_name = group

        f.write('[%s]\n' % group_name)

        for (namespace, opts) in sorted(namespaces,
                                        key=operator.itemgetter(0)):
            f.write('\n#\n# From %s\n#\n' % namespace)
            for opt in opts:
                f.write('\n')
                f.format(opt)

    _output_opts(formatter, 'DEFAULT', groups.pop('DEFAULT'))
    for group, namespaces in sorted(groups.items(),
                                    key=operator.itemgetter(0)):
        formatter.write('\n\n')
        _output_opts(formatter, group, namespaces)


def main(args=None):
    """The main function of oslo-config-generator."""
    version = pkg_resources.get_distribution('oslo.config').version
    logging.basicConfig(level=logging.WARN)
    conf = cfg.ConfigOpts()
    register_cli_opts(conf)
    conf(args, version=version)
    generate(conf)


if __name__ == '__main__':
    main()
