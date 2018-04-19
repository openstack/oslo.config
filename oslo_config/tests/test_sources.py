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

import tempfile

from oslo_config import cfg
from oslo_config import sources

from oslotest import base

_GROUP = "group"
_OPTIONS = "options"
_DEFAULT = "DEFAULT"

_extra_ini_opt_group = "extra_conf_from_ini"
_extra_conf_url = "https://oslo.config/extra.conf"

_conf_data = {
    _DEFAULT: {
        "config_sources": (cfg.StrOpt, _extra_ini_opt_group)
    },
    _extra_ini_opt_group: {
        "driver": (cfg.StrOpt, "ini"),
        "uri": (cfg.URIOpt, _extra_conf_url)
    }
}

_extra_conf_data = {
    _DEFAULT: {
        "foo": (cfg.StrOpt, "bar")
    },
    "test": {
        "opt_str": (cfg.StrOpt, "a nice string"),
        "opt_bool": (cfg.BoolOpt, True),
        "opt_int": (cfg.IntOpt, 42),
        "opt_float": (cfg.FloatOpt, 3.14),
        "opt_ip": (cfg.IPOpt, "127.0.0.1"),
        "opt_port": (cfg.PortOpt, 443),
        "opt_host": (cfg.HostnameOpt, "www.openstack.org"),
        "opt_uri": (cfg.URIOpt, "https://www.openstack.org"),
        "opt_multi": (cfg.MultiStrOpt, ["abc", "def", "ghi"])
    }
}


def register_opts(conf, opts):
    # 'g': group, 'o': option, and 't': type
    for g in opts.keys():
        for o, (t, _) in opts[g].items():
            try:
                conf.register_opt(t(o), g if g != "DEFAULT" else None)
            except cfg.DuplicateOptError:
                pass


def opts_to_ini(opts):
    result = ""

    # 'g': group, 'o': option, 't': type, and 'v': value
    for g in opts.keys():
        result += "[{}]\n".format(g)
        for o, (t, v) in opts[g].items():
            if t == cfg.MultiStrOpt:
                for i in v:
                    result += "{} = {}\n".format(o, i)
            else:
                result += "{} = {}\n".format(o, v)

    return result


def mocked_get(*args, **kwargs):
    class MockResponse(object):
        def __init__(self, text_data, status_code):
            self.text = text_data
            self.status_code = status_code

        def __enter__(self, *args, **kwargs):
            return self

        def __exit__(self, *args, **kwargs):
            pass

        def raise_for_status(self):
            if self.status_code != 200:
                raise

    if args[0] in _extra_conf_url:
        return MockResponse(opts_to_ini(_extra_conf_data), 200)

    return MockResponse(None, 404)


class INISourceTestCase(base.BaseTestCase):

    def setUp(self):
        super(INISourceTestCase, self).setUp()

        self.conf = cfg.ConfigOpts()

        with tempfile.NamedTemporaryFile() as tmp_file:
            tmp_file.write(opts_to_ini(_conf_data).encode("utf-8"))
            tmp_file.flush()

            self.conf(["--config-file", tmp_file.name])

    @base.mock.patch(
        "oslo_config.sources.ini.requests.get", side_effect=mocked_get)
    def test_configuration_source(self, mock_requests_get):
        driver = sources.ini.INIConfigurationSourceDriver()
        source = driver.open_source_from_opt_group(
            self.conf, _extra_ini_opt_group)

        # non-existing option
        self.assertIs(sources._NoValue,
                      source.get("DEFAULT", "bar", cfg.StrOpt("bar"))[0])

        # 'g': group, 'o': option, 't': type, and 'v': value
        for g in _extra_conf_data:
            for o, (t, v) in _extra_conf_data[g].items():
                self.assertEqual(str(v), str(source.get(g, o, t(o))[0]))
