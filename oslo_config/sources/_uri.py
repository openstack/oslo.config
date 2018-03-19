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

import requests
import tempfile

from oslo_config import cfg
from oslo_config import sources


class URIConfigurationSourceDriver(sources.ConfigurationSourceDriver):
    """A configuration source driver for remote files served through http[s].

    Required options:
      - uri: URI containing the file location.

    Non-required options:
      - ca_path: The path to a CA_BUNDLE file or directory with
                 certificates of trusted CAs.

      - client_cert: Client side certificate, as a single file path
                     containing either the certificate only or the
                     private key and the certificate.

      - client_key: Client side private key, in case client_cert is
                    specified but does not includes the private key.
    """

    def open_source_from_opt_group(self, conf, group_name):
        group = cfg.OptGroup(group_name)

        conf.register_opt(cfg.URIOpt("uri",
                                     schemes=["http", "https"],
                                     required=True),
                          group)

        conf.register_opt(cfg.StrOpt("ca_path"), group)
        conf.register_opt(cfg.StrOpt("client_cert"), group)
        conf.register_opt(cfg.StrOpt("client_key"), group)

        return URIConfigurationSource(
            conf[group_name].uri,
            conf[group_name].ca_path,
            conf[group_name].client_cert,
            conf[group_name].client_key)


class URIConfigurationSource(sources.ConfigurationSource):
    """A configuration source for remote files served through http[s].

    :uri: The Uniform Resource Identifier of the configuration to be
          retrieved.

    :ca_path: The path to a CA_BUNDLE file or directory with
              certificates of trusted CAs.

    :client_cert: Client side certificate, as a single file path
                  containing either the certificate only or the
                  private key and the certificate.

    :client_key: Client side private key, in case client_cert is
                 specified but does not includes the private key.
    """

    def __init__(self, uri, ca_path=None, client_cert=None, client_key=None):
        self._uri = uri
        self._namespace = cfg._Namespace(cfg.ConfigOpts())

        data = self._fetch_uri(uri, ca_path, client_cert, client_key)

        with tempfile.NamedTemporaryFile() as tmpfile:
            tmpfile.write(data.encode("utf-8"))
            tmpfile.flush()

            cfg.ConfigParser._parse_file(tmpfile.name, self._namespace)

    def _fetch_uri(self, uri, ca_path, client_cert, client_key):
        verify = ca_path if ca_path else True
        cert = (client_cert, client_key) if client_cert and client_key else \
            client_cert

        with requests.get(uri, verify=verify, cert=cert) as response:
            response.raise_for_status()  # raises only in case of HTTPError

            return response.text

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
        try:
            return self._namespace._get_value(
                [(group_name, option_name)],
                multi=opt.multi)
        except KeyError:
            return (sources._NoValue, None)
