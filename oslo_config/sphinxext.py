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
            _add(group_name)
            _add('=' * len(group_name))
            _add('')

            for opt in opt_list:
                opt_type = self._TYPE_DESCRIPTIONS.get(type(opt),
                                                       'unknown type')
                _add('``%s``' % opt.dest)
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

                _add_indented(opt.help)
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
                    _add_indented('.. warning:')
                    _add_indented('   This option is deprecated for removal.')
                    _add_indented('   Its value may be silently ignored ')
                    _add_indented('   in the future.')
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


def setup(app):
    app.add_directive('show-options', ShowOptionsDirective)
