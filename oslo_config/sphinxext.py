# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from docutils import nodes
from docutils.parsers import rst
from docutils.statemachine import ViewList
from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain
from sphinx.domains import ObjType
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode
from sphinx.util.nodes import nested_parse_with_titles

from oslo_config import cfg
from oslo_config import generator

import six


def _list_table(add, headers, data, title='', columns=None):
    """Build a list-table directive.

    :param add: Function to add one row to output.
    :param headers: List of header values.
    :param data: Iterable of row data, yielding lists or tuples with rows.
    """
    add('.. list-table:: %s' % title)
    add('   :header-rows: 1')
    if columns:
        add('   :widths: %s' % (','.join(str(c) for c in columns)))
    add('')
    add('   - * %s' % headers[0])
    for h in headers[1:]:
        add('     * %s' % h)
    for row in data:
        add('   - * %s' % row[0])
        for r in row[1:]:
            add('     * %s' % r)
    add('')


def _indent(text, n=2):
    padding = ' ' * n
    return '\n'.join(padding + l for l in text.splitlines())


def _make_anchor_target(group_name, option_name):
    # We need to ensure this is unique across entire documentation
    # http://www.sphinx-doc.org/en/stable/markup/inline.html#ref-role
    target = '%s.%s' % (cfg._normalize_group_name(group_name),
                        option_name.lower())
    return target


class ShowOptionsDirective(rst.Directive):

    # option_spec = {}

    has_content = True

    _TYPE_DESCRIPTIONS = {
        cfg.StrOpt: 'string',
        cfg.BoolOpt: 'boolean',
        cfg.IntOpt: 'integer',
        cfg.FloatOpt: 'floating point',
        cfg.ListOpt: 'list',
        cfg.DictOpt: 'dict',
        cfg.MultiStrOpt: 'multi-valued',
        cfg._ConfigFileOpt: 'list of filenames',
        cfg._ConfigDirOpt: 'list of directory names',
    }

    def run(self):
        env = self.state.document.settings.env
        app = env.app

        namespace = ' '.join(self.content)

        opts = generator._list_opts([namespace])

        result = ViewList()
        source_name = '<' + __name__ + '>'

        def _add(text):
            "Append some text to the output result view to be parsed."
            result.append(text, source_name)

        def _add_indented(text):
            """Append some text, indented by a couple of spaces.

            Indent everything under the option name,
            to format it as a definition list.
            """
            _add(_indent(text))

        by_section = {}

        for ignore, opt_list in opts:
            for group_name, opts in opt_list:
                by_section.setdefault(group_name, []).extend(opts)

        for group_name, opt_list in sorted(by_section.items()):
            group_name = group_name or 'DEFAULT'
            app.info('[oslo.config] %s %s' % (namespace, group_name))

            _add('.. oslo.config:group:: %s' % group_name)
            _add('')

            for opt in opt_list:
                opt_type = self._TYPE_DESCRIPTIONS.get(type(opt),
                                                       'unknown type')
                _add('.. oslo.config:option:: %s' % opt.dest)
                _add('')
                _add_indented(':Type: %s' % opt_type)
                for default in generator._format_defaults(opt):
                    if default:
                        default = '``' + default + '``'
                    _add_indented(':Default: %s' % default)
                if getattr(opt.type, 'min', None):
                    _add_indented(':Minimum Value: %s' % opt.type.min)
                if getattr(opt.type, 'max', None):
                    _add_indented(':Maximum Value: %s' % opt.type.max)
                if getattr(opt.type, 'choices', None):
                    choices_text = ', '.join([self._get_choice_text(choice)
                                              for choice in opt.type.choices])
                    _add_indented(':Valid Values: %s' % choices_text)
                _add('')

                try:
                    help_text = opt.help % {'default': 'the value above'}
                except (TypeError, KeyError):
                    # There is no mention of the default in the help string,
                    # or the string had some unknown key
                    help_text = opt.help
                _add_indented(help_text)
                _add('')

                if opt.deprecated_opts:
                    _list_table(
                        _add_indented,
                        ['Group', 'Name'],
                        ((d.group or 'DEFAULT',
                          d.name or opt.dest or 'UNSET')
                         for d in opt.deprecated_opts),
                        title='Deprecated Variations',
                    )
                if opt.deprecated_for_removal:
                    _add_indented('.. warning::')
                    _add_indented('   This option is deprecated for removal.')
                    _add_indented('   Its value may be silently ignored ')
                    _add_indented('   in the future.')
                    if opt.deprecated_reason:
                        _add_indented('   Reason: ' + opt.deprecated_reason)
                    _add('')

                _add('')

        node = nodes.section()
        node.document = self.state.document
        nested_parse_with_titles(self.state, result, node)

        return node.children

    def _get_choice_text(self, choice):
        if choice is None:
            return '<None>'
        elif choice == '':
            return "''"
        return six.text_type(choice)


class ConfigGroupXRefRole(XRefRole):
    "Handles :oslo.config:group: roles pointing to configuration groups."

    def __init__(self):
        super(ConfigGroupXRefRole, self).__init__(
            warn_dangling=True,
        )

    def process_link(self, env, refnode, has_explicit_title, title, target):
        # The anchor for the group link is the group name.
        return target, target


class ConfigOptXRefRole(XRefRole):
    "Handles :oslo.config:option: roles pointing to configuration options."

    def __init__(self):
        super(ConfigOptXRefRole, self).__init__(
            warn_dangling=True,
        )

    def process_link(self, env, refnode, has_explicit_title, title, target):
        if not has_explicit_title:
            title = target
        if '.' in target:
            group, opt_name = target.split('.')
        else:
            group = 'DEFAULT'
            opt_name = target
        anchor = _make_anchor_target(group, opt_name)
        return title, anchor


class ConfigGroup(ObjectDescription):
    "Description of a configuration group (.. group)."

    def handle_signature(self, sig, signode):
        """Transform a group description into RST nodes."""
        group_name = sig
        signode += addnodes.desc_name(
            group_name,
            'Option Group: %s' % group_name,
        )
        signode['allnames'] = [group_name]
        return group_name

    def add_target_and_index(self, firstname, sig, signode):
        cached_groups = self.env.domaindata['oslo.config']['groups']
        # Store the current group for use later in option directives
        self.env.temp_data['oslo.config:group'] = sig
        # Store the location where this group is being defined
        # for use when resolving cross-references later.
        # FIXME: This should take the source namespace into account, too
        cached_groups[sig] = self.env.docname
        # Compute the normalized target and set the node to have that
        # as an id
        target_name = cfg._normalize_group_name(sig)
        signode['ids'].append(target_name)
        self.state.document.note_explicit_target(signode)


class ConfigOption(ObjectDescription):
    "Description of a configuration option (.. option)."

    def handle_signature(self, sig, signode):
        """Transform an option description into RST nodes."""
        optname = sig
        # Insert a node into the output showing the option name
        signode += addnodes.desc_name(optname, optname)
        signode['allnames'] = [optname]
        return optname

    def add_target_and_index(self, firstname, sig, signode):
        cached_options = self.env.domaindata['oslo.config']['options']
        # Look up the current group name from the processing context
        currgroup = self.env.temp_data.get('oslo.config:group')
        # Compute the normalized target name for the option and give
        # that to the node as an id
        target_name = _make_anchor_target(currgroup, sig)
        signode['ids'].append(target_name)
        self.state.document.note_explicit_target(signode)
        # Store the location of the option definition for later use in
        # resolving cross-references
        # FIXME: This should take the source namespace into account, too
        cached_options[target_name] = self.env.docname


class ConfigDomain(Domain):
    """oslo.config domain."""
    name = 'oslo.config'
    label = 'oslo.config'
    object_types = {
        'configoption': ObjType('configuration option', 'option'),
    }
    directives = {
        'group': ConfigGroup,
        'option': ConfigOption,
    }
    roles = {
        'option': ConfigOptXRefRole(),
        'group': ConfigGroupXRefRole(),
    }
    initial_data = {
        'options': {},
        'groups': {},
    }

    def resolve_xref(self, env, fromdocname, builder,
                     typ, target, node, contnode):
        if typ == 'option':
            group_name, option_name = target.split('.', 1)
            return make_refnode(
                builder,
                fromdocname,
                env.domaindata['oslo.config']['options'][target],
                target,
                contnode,
                option_name,
            )
        if typ == 'group':
            return make_refnode(
                builder,
                fromdocname,
                env.domaindata['oslo.config']['groups'][target],
                target,
                contnode,
                target,
            )
        return None


def setup(app):
    app.add_directive('show-options', ShowOptionsDirective)
    app.add_domain(ConfigDomain)
