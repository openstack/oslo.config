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

.. versionadded:: 1.4
"""

import collections
import logging
import operator
import sys
import textwrap

import pkg_resources
import six

from oslo_config._i18n import _LW
from oslo_config import cfg
import stevedore.named  # noqa

LOG = logging.getLogger(__name__)
UPPER_CASE_GROUP_NAMES = ['DEFAULT']

_generator_opts = [
    cfg.StrOpt(
        'output-file',
        help='Path of the file to write to. Defaults to stdout.'),
    cfg.IntOpt(
        'wrap-width',
        default=70,
        help='The maximum length of help lines.'),
    cfg.MultiStrOpt(
        'namespace',
        required=True,
        help='Option namespace under "oslo.config.opts" in which to query '
        'for options.'),
    cfg.BoolOpt(
        'minimal',
        default=False,
        help='Generate a minimal required configuration.'),
    cfg.BoolOpt(
        'summarize',
        default=False,
        help='Only output summaries of help text to config files. Retain '
        'longer help text for Sphinx documents.'),
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
        elif (isinstance(opt, (cfg.StrOpt, cfg.IPOpt,
                               cfg.HostnameOpt, cfg.HostAddressOpt,
                               cfg.URIOpt))):
            default_str = opt.default
        elif isinstance(opt, cfg.BoolOpt):
            default_str = str(opt.default).lower()
        elif isinstance(opt, (cfg.IntOpt, cfg.FloatOpt,
                              cfg.PortOpt)):
            default_str = str(opt.default)
        elif isinstance(opt, (cfg.ListOpt, cfg._ConfigFileOpt,
                              cfg._ConfigDirOpt)):
            default_str = ','.join(opt.default)
        elif isinstance(opt, cfg.DictOpt):
            sorted_items = sorted(opt.default.items(),
                                  key=operator.itemgetter(0))
            default_str = ','.join(['%s:%s' % i for i in sorted_items])
        else:
            LOG.warning(_LW('Unknown option type: %s'), repr(opt))
            default_str = str(opt.default)
        defaults = [default_str]

    results = []
    for default_str in defaults:
        if default_str.strip() != default_str:
            default_str = '"%s"' % default_str
        results.append(default_str)
    return results


_TYPE_NAMES = {
    str: 'string value',
    int: 'integer value',
    float: 'floating point value',
}


def _format_type_name(opt_type):
    """Format the type name to use in describing an option"""
    try:
        return opt_type.type_name
    except AttributeError:  # nosec
        pass

    try:
        return _TYPE_NAMES[opt_type]
    except KeyError:  # nosec
        pass

    return 'unknown value'


class _OptFormatter(object):

    """Format configuration option descriptions to a file."""

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

    def format_group(self, group_or_groupname):
        """Format the description of a group header to the output file

        :param group_or_groupname: a cfg.OptGroup instance or a name of group
        :returns: a formatted group description string
        """
        if isinstance(group_or_groupname, cfg.OptGroup):
            group = group_or_groupname
            lines = ['[%s]\n' % group.name]
            if group.help:
                lines += self._format_help(group.help)
        else:
            groupname = group_or_groupname
            lines = ['[%s]\n' % groupname]
        self.writelines(lines)

    def format(self, opt, group_name, minimal=False, summarize=False):
        """Format a description of an option to the output file.

        :param opt: a cfg.Opt instance
        :param group_name: name of the group to which the opt is assigned
        :param minimal: enable option by default, marking it as required
        :param summarize: output a summarized description of the opt
        :returns: a formatted opt description string
        """
        if not opt.help:
            LOG.warning(_LW('"%s" is missing a help string'), opt.dest)

        opt_type = _format_type_name(opt.type)
        opt_prefix = ''
        if (opt.deprecated_for_removal and
                not opt.help.startswith('DEPRECATED')):
            opt_prefix = 'DEPRECATED: '

        if opt.help:
            # an empty line signifies a new paragraph. We only want the
            # summary line
            if summarize:
                _split = opt.help.split('\n\n')
                opt_help = _split[0].rstrip(':').rstrip('.')
                if len(_split) > 1:
                    opt_help += '. For more information, refer to the '
                    opt_help += 'documentation.'
            else:
                opt_help = opt.help

            help_text = u'%s%s (%s)' % (opt_prefix,
                                        opt_help,
                                        opt_type)
        else:
            help_text = u'(%s)' % opt_type
        lines = self._format_help(help_text)

        if getattr(opt.type, 'min', None) is not None:
            lines.append('# Minimum value: %d\n' % opt.type.min)

        if getattr(opt.type, 'max', None) is not None:
            lines.append('# Maximum value: %d\n' % opt.type.max)

        if getattr(opt.type, 'choices', None):
            choices_text = ', '.join([self._get_choice_text(choice)
                                      for choice in opt.type.choices])
            lines.append('# Allowed values: %s\n' % choices_text)

        try:
            if opt.mutable:
                lines.append(
                    '# Note: This option can be changed without restarting.\n'
                )
        except AttributeError as err:
            # NOTE(dhellmann): keystoneauth defines its own Opt class,
            # and neutron (at least) returns instances of those
            # classes instead of oslo_config Opt instances. The new
            # mutable attribute is the first property where the API
            # isn't supported in the external class, so we can use
            # this failure to emit a warning. See
            # https://bugs.launchpad.net/keystoneauth/+bug/1548433 for
            # more details.
            import warnings
            if not isinstance(opt, cfg.Opt):
                warnings.warn(
                    'Incompatible option class for %s (%r): %s' %
                    (opt.dest, opt.__class__, err),
                )
            else:
                warnings.warn('Failed to fully format sample for %s: %s' %
                              (opt.dest, err))

        for d in opt.deprecated_opts:
            lines.append('# Deprecated group/name - [%s]/%s\n' %
                         (d.group or group_name, d.name or opt.dest))

        if opt.deprecated_for_removal:
            if opt.deprecated_since:
                lines.append(
                    '# This option is deprecated for removal since %s.\n' % (
                        opt.deprecated_since))
            else:
                lines.append(
                    '# This option is deprecated for removal.\n')
            lines.append(
                '# Its value may be silently ignored in the future.\n')
            if opt.deprecated_reason:
                lines.extend(
                    self._format_help('Reason: ' + opt.deprecated_reason))

        if opt.advanced:
            lines.append(
                '# Advanced Option: intended for advanced users and not used\n'
                '# by the majority of users, and might have a significant\n'
                '# effect on stability and/or performance.\n'
            )

        if hasattr(opt.type, 'format_defaults'):
            defaults = opt.type.format_defaults(opt.default,
                                                opt.sample_default)
        else:
            LOG.debug(
                "The type for option %(name)s which is %(type)s is not a "
                "subclass of types.ConfigType and doesn't provide a "
                "'format_defaults' method. A default formatter is not "
                "available so the best-effort formatter will be used.",
                {'type': opt.type, 'name': opt.name})
            defaults = _format_defaults(opt)
        for default_str in defaults:
            if default_str:
                default_str = ' ' + default_str
            if minimal:
                lines.append('%s =%s\n' % (opt.dest, default_str))
            else:
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


def _cleanup_opts(read_opts):
    """Cleanup duplicate options in namespace groups

    Return a structure which removes duplicate options from a namespace group.
    NOTE:(rbradfor) This does not remove duplicated options from repeating
    groups in different namespaces:

    :param read_opts: a list (namespace, [(group, [opt_1, opt_2])]) tuples
    :returns: a list of (namespace, [(group, [opt_1, opt_2])]) tuples
    """

    # OrderedDict is used specifically in the three levels to maintain the
    # source order of namespace/group/opt values
    clean = collections.OrderedDict()
    for namespace, listing in read_opts:
        if namespace not in clean:
            clean[namespace] = collections.OrderedDict()
        for group, opts in listing:
            # NOTE: Normalize group names to lowe-case except those defined in
            # UPPER_CASE_GROUP_NAMES
            if group:
                group_name = getattr(group, 'name', str(group))
                if group_name.upper() in UPPER_CASE_GROUP_NAMES:
                    normalized_gn = group_name.upper()
                else:
                    normalized_gn = group_name.lower()
                if normalized_gn != group_name:
                    LOG.warning('normalizing group name %r to %r', group_name,
                                normalized_gn)
                    if hasattr(group, 'name'):
                        group.name = normalized_gn
                    else:
                        group = normalized_gn

            if group not in clean[namespace]:
                clean[namespace][group] = collections.OrderedDict()
            for opt in opts:
                clean[namespace][group][opt.dest] = opt

    # recreate the list of (namespace, [(group, [opt_1, opt_2])]) tuples
    # from the cleaned structure.
    cleaned_opts = [
        (namespace, [(g, list(clean[namespace][g].values()))
                     for g in clean[namespace]])
        for namespace in clean
    ]

    return cleaned_opts


def _get_raw_opts_loaders(namespaces):
    """List the options available via the given namespaces.

    :param namespaces: a list of namespaces registered under 'oslo.config.opts'
    :returns: a list of (namespace, [(group, [opt_1, opt_2])]) tuples
    """
    mgr = stevedore.named.NamedExtensionManager(
        'oslo.config.opts',
        names=namespaces,
        on_load_failure_callback=on_load_failure_callback,
        invoke_on_load=False)
    return [(e.name, e.plugin) for e in mgr]


def _get_opt_default_updaters(namespaces):
    mgr = stevedore.named.NamedExtensionManager(
        'oslo.config.opts.defaults',
        names=namespaces,
        warn_on_missing_entrypoint=False,
        on_load_failure_callback=on_load_failure_callback,
        invoke_on_load=False)
    return [ep.plugin for ep in mgr]


def _update_defaults(namespaces):
    "Let application hooks update defaults inside libraries."
    for update in _get_opt_default_updaters(namespaces):
        update()


def _list_opts(namespaces):
    """List the options available via the given namespaces.

    Duplicate options from a namespace are removed.

    :param namespaces: a list of namespaces registered under 'oslo.config.opts'
    :returns: a list of (namespace, [(group, [opt_1, opt_2])]) tuples
    """
    # Load the functions to get the options.
    loaders = _get_raw_opts_loaders(namespaces)
    # Update defaults, which might change global settings in library
    # modules.
    _update_defaults(namespaces)
    # Ask for the option definitions. At this point any global default
    # changes made by the updaters should be in effect.
    opts = [
        (namespace, loader())
        for namespace, loader in loaders
    ]
    return _cleanup_opts(opts)


def on_load_failure_callback(*args, **kwargs):
    raise


def _output_opts(f, group, group_data, minimal=False, summarize=False):
    f.format_group(group_data['object'] or group)
    for (namespace, opts) in sorted(group_data['namespaces'],
                                    key=operator.itemgetter(0)):
        f.write('\n#\n# From %s\n#\n' % namespace)
        for opt in sorted(opts, key=operator.attrgetter('advanced')):
            try:
                if minimal and not opt.required:
                    pass
                else:
                    f.write('\n')
                    f.format(opt, group, minimal, summarize)
            except Exception as err:
                f.write('# Warning: Failed to format sample for %s\n' %
                        (opt.dest,))
                f.write('# %s\n' % (err,))


def _get_groups(conf_ns):
    """Invert a list of groups by namespace into a dict by group name.

    :param conf_ns: a list of (namespace, [(<group>, [opt_1, opt_2])]) tuples,
                    such as returned by _list_opts.
    :returns: {<group_name>, {'object': <group_object>,
                              'namespaces': [(<namespace>, <opts>)]}}

    <group> may be a string or a group object.
    <group_name> is always a string.
    <group_object> will only be set if <group> was a group object in at least
    one namespace.

    Keying by group_name avoids adding duplicate group names in case a group is
    added as both an OptGroup and as a str, but still makes the additional
    OptGroup data available to the output code when possible.
    """
    groups = {'DEFAULT': {'object': None, 'namespaces': []}}
    for namespace, listing in conf_ns:
        for group, opts in listing:
            if not opts:
                continue
            group = group if group else 'DEFAULT'
            is_optgroup = hasattr(group, 'name')
            group_name = group.name if is_optgroup else group
            if group_name not in groups:
                groups[group_name] = {'object': None, 'namespaces': []}
            if is_optgroup:
                groups[group_name]['object'] = group
            groups[group_name]['namespaces'].append((namespace, opts))
    return groups


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

    groups = _get_groups(_list_opts(conf.namespace))

    # Output the "DEFAULT" section as the very first section
    _output_opts(formatter, 'DEFAULT', groups.pop('DEFAULT'), conf.minimal,
                 conf.summarize)

    # output all other config sections with groups in alphabetical order
    for group, group_data in sorted(groups.items()):
        formatter.write('\n\n')
        _output_opts(formatter, group, group_data, conf.minimal,
                     conf.summarize)


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
