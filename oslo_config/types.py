# Copyright 2013 Mirantis, Inc.
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

"""Type conversion and validation classes for configuration options.

Use these classes as values for the `type` argument to
:class:`oslo_config.cfg.Opt` and its subclasses.

.. versionadded:: 1.3
"""
import operator
import re
import warnings

import abc
import netaddr
import six


class ConfigType(object):
    def __init__(self, type_name='unknown type'):
        self.type_name = type_name

    NONE_DEFAULT = '<None>'

    def format_defaults(self, default, sample_default=None):
        """Return a list of formatted default values.

        """
        if sample_default is not None:
            default_str = sample_default
        elif default is None:
            default_str = self.NONE_DEFAULT
        else:
            default_str = self._formatter(default)
        return [default_str]

    def quote_trailing_and_leading_space(self, str_val):
        if not isinstance(str_val, six.string_types):
            warnings.warn('converting \'%s\' to a string' % str_val)
            str_val = six.text_type(str_val)
        if str_val.strip() != str_val:
            return '"%s"' % str_val
        return str_val

    @abc.abstractmethod
    def _formatter(self, value):
        pass


class String(ConfigType):

    """String type.

    String values do not get transformed and are returned as str objects.

    :param choices: Optional sequence of valid values. Mutually
                    exclusive with 'regex'.
    :param quotes: If True and string is enclosed with single or double
                   quotes, will strip those quotes. Will signal error if
                   string have quote at the beginning and no quote at
                   the end. Turned off by default. Useful if used with
                   container types like List.
    :param regex: Optional regular expression (string or compiled
                  regex) that the value must match on an unanchored
                  search. Mutually exclusive with 'choices'.
    :param ignore_case:  If True case differences (uppercase vs. lowercase)
                         between 'choices' or 'regex' will be ignored;
                         defaults to False.
    :param max_length:  Optional integer. If a positive value is specified,
                        a maximum length of an option value must be less than
                        or equal to this parameter. Otherwise no length check
                        will be done.
    :param type_name: Type name to be used in the sample config file.

    .. versionchanged:: 2.1
       Added *regex* parameter.

    .. versionchanged:: 2.5
       Added *ignore_case* parameter.

    .. versionchanged:: 2.7
       Added *max_length* parameter.
       Added *type_name* parameter.
    """

    def __init__(self, choices=None, quotes=False, regex=None,
                 ignore_case=False, max_length=None,
                 type_name='string value'):
        super(String, self).__init__(type_name=type_name)
        if choices and regex:
            raise ValueError("'choices' and 'regex' cannot both be specified")

        self.ignore_case = ignore_case
        self.quotes = quotes
        self.max_length = max_length or 0

        self.choices = choices
        self.lower_case_choices = None
        if self.choices is not None and self.ignore_case:
            self.lower_case_choices = [c.lower() for c in choices]

        self.regex = regex
        if self.regex is not None:
            re_flags = re.IGNORECASE if self.ignore_case else 0

            # Check if regex is a string or an already compiled regex
            if isinstance(regex, six.string_types):
                self.regex = re.compile(regex, re_flags)
            else:
                self.regex = re.compile(regex.pattern, re_flags | regex.flags)

    def __call__(self, value):
        value = str(value)
        if self.quotes and value:
            if value[0] in "\"'":
                if value[-1] != value[0]:
                    raise ValueError('Non-closed quote: %s' % value)
                value = value[1:-1]

        if self.max_length > 0 and len(value) > self.max_length:
            raise ValueError("Value '%s' exceeds maximum length %d" %
                             (value, self.max_length))

        if self.regex and not self.regex.search(value):
            raise ValueError("Value %r doesn't match regex %r" %
                             (value, self.regex.pattern))

        if self.choices is None:
            return value

        # Check for case insensitive
        processed_value, choices = ((value.lower(), self.lower_case_choices)
                                    if self.ignore_case else
                                    (value, self.choices))
        if processed_value in choices:
            return value

        raise ValueError(
            'Valid values are [%s], but found %s' % (
                ', '.join([str(v) for v in self.choices]),
                repr(value)))

    def __repr__(self):
        details = []
        if self.choices:
            details.append("choices=%r" % self.choices)
        if self.regex:
            details.append("regex=%r" % self.regex.pattern)
        if details:
            return "String(%s)" % ",".join(details)
        return 'String'

    def __eq__(self, other):
        return (
            (self.__class__ == other.__class__) and
            (set(self.choices) == set(other.choices) if
             self.choices and other.choices else
             self.choices == other.choices) and
            (self.quotes == other.quotes) and
            (self.regex == other.regex)
        )

    def _formatter(self, value):
        return self.quote_trailing_and_leading_space(value)


class MultiString(String):
    """Multi-valued string."""

    def __init__(self, type_name='multi valued'):
        super(MultiString, self).__init__(type_name=type_name)

    NONE_DEFAULT = ['']

    def format_defaults(self, default, sample_default=None):
        """Return a list of formatted default values.

        """
        if sample_default is not None:
            default_list = self._formatter(sample_default)
        elif not default:
            default_list = self.NONE_DEFAULT
        else:
            default_list = self._formatter(default)
        return default_list

    def _formatter(self, value):
        return [self.quote_trailing_and_leading_space(v) for v in value]


class Boolean(ConfigType):

    """Boolean type.

    Values are case insensitive and can be set using
    1/0, yes/no, true/false or on/off.

    :param type_name: Type name to be used in the sample config file.

    .. versionchanged:: 2.7

       Added *type_name* parameter.
    """
    TRUE_VALUES = ['true', '1', 'on', 'yes']
    FALSE_VALUES = ['false', '0', 'off', 'no']

    def __init__(self, type_name='boolean value'):
        super(Boolean, self).__init__(type_name=type_name)

    def __call__(self, value):
        if isinstance(value, bool):
            return value

        s = value.lower()
        if s in self.TRUE_VALUES:
            return True
        elif s in self.FALSE_VALUES:
            return False
        else:
            raise ValueError('Unexpected boolean value %r' % value)

    def __repr__(self):
        return 'Boolean'

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def _formatter(self, value):
        return str(value).lower()


class Integer(ConfigType):

    """Integer type.

    Converts value to an integer optionally doing range checking.
    If value is whitespace or empty string will return None.

    :param min: Optional check that value is greater than or equal to min.
                Mutually exclusive with 'choices'.
    :param max: Optional check that value is less than or equal to max.
                Mutually exclusive with 'choices'.
    :param type_name: Type name to be used in the sample config file.
    :param choices: Optional sequence of valid values. Mutually exclusive
                    with 'min/max'.

    .. versionchanged:: 2.4
       The class now honors zero for *min* and *max* parameters.

    .. versionchanged:: 2.7
       Added *type_name* parameter.

    .. versionchanged:: 3.2
       Added *choices* parameter.
    """

    def __init__(self, min=None, max=None, type_name='integer value',
                 choices=None):
        super(Integer, self).__init__(type_name=type_name)
        if choices is not None:
            if min is not None or max is not None:
                raise ValueError("'choices' and 'min/max' cannot both be "
                                 "specified")
        else:
            if min is not None and max is not None and max < min:
                raise ValueError('Max value is less than min value')
        self.min = min
        self.max = max
        self.choices = choices

    def __call__(self, value):
        if not isinstance(value, int):
            s = str(value).strip()
            if s == '':
                value = None
            else:
                value = int(value)

        if value is not None:
            if self.choices is not None:
                self._check_choices(value)
            else:
                self._check_range(value)

        return value

    def _check_choices(self, value):
        if value in self.choices:
            return
        else:
            raise ValueError('Valid values are %r, but found %d' % (
                             self.choices, value))

    def _check_range(self, value):
        if self.min is not None and value < self.min:
            raise ValueError('Should be greater than or equal to %d' %
                             self.min)
        if self.max is not None and value > self.max:
            raise ValueError('Should be less than or equal to %d' % self.max)

    def __repr__(self):
        props = []
        if self.choices is not None:
            props.append("choices=%r" % (self.choices,))
        else:
            if self.min is not None:
                props.append('min=%d' % self.min)
            if self.max is not None:
                props.append('max=%d' % self.max)

        if props:
            return 'Integer(%s)' % ', '.join(props)
        return 'Integer'

    def __eq__(self, other):
        return (
            (self.__class__ == other.__class__) and
            (self.min == other.min) and
            (self.max == other.max) and
            (set(self.choices) == set(other.choices) if
             self.choices and other.choices else
             self.choices == other.choices)
        )

    def _formatter(self, value):
        return str(value)


class Float(ConfigType):

    """Float type.

    :param type_name: Type name to be used in the sample config file.

    .. versionchanged:: 2.7

       Added *type_name* parameter.
    """

    def __init__(self, type_name='floating point value'):
        super(Float, self).__init__(type_name=type_name)

    def __call__(self, value):
        if isinstance(value, float):
            return value

        return float(value)

    def __repr__(self):
        return 'Float'

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def _formatter(self, value):
        return str(value)


class List(ConfigType):

    """List type.

    Represent values of other (item) type, separated by commas.
    The resulting value is a list containing those values.

    List doesn't know if item type can also contain commas. To workaround this
    it tries the following: if the next part fails item validation, it appends
    comma and next item until validation succeeds or there is no parts left.
    In the later case it will signal validation error.

    :param item_type: type of list items
    :param bounds: if True, value should be inside "[" and "]" pair
    :param type_name: Type name to be used in the sample config file.

    .. versionchanged:: 2.7

       Added *type_name* parameter.
    """

    def __init__(self, item_type=None, bounds=False, type_name='list value'):
        super(List, self).__init__(type_name=type_name)

        if item_type is None:
            item_type = String()

        if not callable(item_type):
            raise TypeError('item_type must be callable')
        self.item_type = item_type
        self.bounds = bounds

    def __call__(self, value):
        if isinstance(value, list):
            return value

        result = []
        s = value.strip()

        if self.bounds:
            if not s.startswith('['):
                raise ValueError('Value should start with "["')
            if not s.endswith(']'):
                raise ValueError('Value should end with "]"')
            s = s[1:-1]

        if s == '':
            return result

        values = s.split(',')
        while values:
            value = values.pop(0)
            while True:
                first_error = None
                try:
                    validated_value = self.item_type(value.strip())
                    break
                except ValueError as e:
                    if not first_error:
                        first_error = e
                    if len(values) == 0:
                        raise first_error

                value += ',' + values.pop(0)

            result.append(validated_value)

        return result

    def __repr__(self):
        return 'List of %s' % repr(self.item_type)

    def __eq__(self, other):
        return (
            (self.__class__ == other.__class__) and
            (self.item_type == other.item_type)
        )

    def _formatter(self, value):
        return ','.join(value)


class Dict(ConfigType):

    """Dictionary type.

    Dictionary type values are key:value pairs separated by commas.
    The resulting value is a dictionary of these key/value pairs.
    Type of dictionary key is always string, but dictionary value
    type can be customized.

    :param value_type: type of values in dictionary
    :param bounds: if True, value should be inside "{" and "}" pair
    :param type_name: Type name to be used in the sample config file.

    .. versionchanged:: 2.7

       Added *type_name* parameter.
    """

    def __init__(self, value_type=None, bounds=False, type_name='dict value'):
        super(Dict, self).__init__(type_name=type_name)

        if value_type is None:
            value_type = String()

        if not callable(value_type):
            raise TypeError('value_type must be callable')
        self.value_type = value_type
        self.bounds = bounds

    def __call__(self, value):
        if isinstance(value, dict):
            return value

        result = {}
        s = value.strip()

        if self.bounds:
            if not s.startswith('{'):
                raise ValueError('Value should start with "{"')
            if not s.endswith('}'):
                raise ValueError('Value should end with "}"')
            s = s[1:-1]

        if s == '':
            return result

        pairs = s.split(',')
        while pairs:
            pair = pairs.pop(0)

            while True:
                first_error = None
                try:
                    key_value = pair.split(':', 1)

                    if len(key_value) < 2:
                        raise ValueError('Value should be NAME:VALUE pairs '
                                         'separated by ","')

                    key, value = key_value
                    key = key.strip()
                    value = value.strip()

                    value = self.value_type(value)
                    break
                except ValueError as e:
                    if not first_error:
                        first_error = e
                    if not pairs:
                        raise first_error

                pair += ',' + pairs.pop(0)

            if key == '':
                raise ValueError('Key name should not be empty')

            if key in result:
                raise ValueError('Duplicate key %s' % key)

            result[key] = value

        return result

    def __repr__(self):
        return 'Dict of %s' % repr(self.value_type)

    def __eq__(self, other):
        return (
            (self.__class__ == other.__class__) and
            (self.value_type == other.value_type)
        )

    def _formatter(self, value):
        sorted_items = sorted(value.items(),
                              key=operator.itemgetter(0))
        return ','.join(['%s:%s' % i for i in sorted_items])


class IPAddress(ConfigType):

    """IP address type

    Represents either ipv4 or ipv6. Without specifying version parameter both
    versions are checked

    :param version: defines which version should be explicitly checked (4 or 6)
    :param type_name: Type name to be used in the sample config file.

    .. versionchanged:: 2.7

       Added *type_name* parameter.
    """

    def __init__(self, version=None, type_name='IP address value'):
        super(IPAddress, self).__init__(type_name=type_name)
        version_checkers = {
            None: self._check_both_versions,
            4: self._check_ipv4,
            6: self._check_ipv6
        }

        self.version_checker = version_checkers.get(version)
        if self.version_checker is None:
            raise TypeError("%s is not a valid IP version." % version)

    def __call__(self, value):
        value = str(value)
        if not value:
            raise ValueError("IP address cannot be an empty string")
        self.version_checker(value)
        return value

    def __repr__(self):
        return "IPAddress"

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def _check_ipv4(self, address):
        if not netaddr.valid_ipv4(address, netaddr.core.INET_PTON):
            raise ValueError("%s is not an IPv4 address" % address)

    def _check_ipv6(self, address):
        if not netaddr.valid_ipv6(address, netaddr.core.INET_PTON):
            raise ValueError("%s is not an IPv6 address" % address)

    def _check_both_versions(self, address):
        if not (netaddr.valid_ipv4(address, netaddr.core.INET_PTON) or
                netaddr.valid_ipv6(address, netaddr.core.INET_PTON)):
            raise ValueError("%s is not IPv4 or IPv6 address" % address)

    def _formatter(self, value):
        return value


class Hostname(ConfigType):
    """Hostname type.

    A hostname refers to a valid DNS or hostname. It must not be longer than
    253 characters, have a segment greater than 63 characters, nor start or
    end with a hyphen.

    :param type_name: Type name to be used in the sample config file.

    """

    def __init__(self, type_name='hostname value'):
        super(Hostname, self).__init__(type_name=type_name)

    def __call__(self, value):
        """Check hostname is valid.

        Ensures that each segment
        - Contains at least one character and a maximum of 63 characters
        - Consists only of allowed characters: letters (A-Z and a-z),
          digits (0-9), and hyphen (-)
        - Does not begin or end with a hyphen
        - maximum total length of 253 characters

        For more details , please see: http://tools.ietf.org/html/rfc1035
        """

        if len(value) == 0:
            raise ValueError("Cannot have an empty hostname")
        if len(value) > 253:
            raise ValueError("hostname is greater than 253 characters: %s"
                             % value)
        if value.endswith("."):
            value = value[:-1]
        allowed = re.compile("(?!-)[A-Z0-9-]{1,63}(?<!-)$", re.IGNORECASE)
        if any((not allowed.match(x)) for x in value.split(".")):
            raise ValueError("%s is an invalid hostname" % value)
        return value

    def __repr__(self):
        return 'Hostname'

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def _formatter(self, value):
        return value
