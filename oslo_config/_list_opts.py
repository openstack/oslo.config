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

from oslo_config import cfg

import stevedore


def list_opts():
    default_config_files = [
        '~/.project/project.conf',
        '~/project.conf',
        '/etc/project/project.conf',
        '/etc/project.conf',
    ]
    default_config_dirs = [
        '~/.project/project.conf.d/',
        '~/project.conf.d/',
        '/etc/project/project.conf.d/',
        '/etc/project.conf.d/',
    ]
    options = [(None, cfg.ConfigOpts._list_options_for_discovery(
        default_config_files,
        default_config_dirs,
    ))]

    ext_mgr = stevedore.ExtensionManager(
        "oslo.config.driver",
        invoke_on_load=True)

    for driver in ext_mgr.names():
        options.append(('sample_%s_source' % driver,
                       ext_mgr[driver].obj.list_options_for_discovery()))

    return options
