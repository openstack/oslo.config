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
import abc
import six


@six.add_metaclass(abc.ABCMeta)
class ConfigurationSourceDriver(object):
    """A config driver option for Oslo.config.

    Represents an oslo.config driver to allow store configuration data in
    other places, such as secret stores managed by a proper key management
    store solution.

    """

    @abc.abstractmethod
    def open_source_from_opt_group(self, conf, group_name):
        """Return an open option source.

        Use group_name to find the configuration settings for the new
        source then open the source and return it.

        If a source cannot be open, raise an appropriate exception.

        :param conf: The active configuration option handler from which
                     to seek configuration values.
        :type conf: ConfigOpts
        :param group_name: The configuration option group name where the
                           options for the source are stored.
        :type group_name: str
        :returns: an instance of a subclass of ConfigurationSource
        """


@six.add_metaclass(abc.ABCMeta)
class ConfigurationSource(object):
    """A configuration source option for oslo.config.

    A configuration source is able to fetch configuration values based on
    a (group, option) key from an external source that supports key-value
    mapping such as INI files, key-value stores, secret stores, and so on.

    """

    @abc.abstractmethod
    def get(self, group_name, option_name, opt):
        """Return the value of the option from the group.

        :param group_name: Name of the group.
        :type group_name: str
        :param option_name: Name of the option.
        :type option_name: str
        :param opt: The option definition.
        :type opt: Opt
        :returns: A tuple (value, location) where value is the option value
                  or oslo_config.sources._NoValue if the (group, option) is
                  not present in the source, and location is a LocationInfo.
        """
