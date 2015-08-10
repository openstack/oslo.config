# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
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

import os

from oslo_config import generator


def generate_sample(app):

    def info(msg):
        app.info('[%s] %s' % (__name__, msg))

    if not app.config.config_generator_config_file:
        app.warn("No config_generator_config_file is specified, "
                 "skipping sample config generation")
        return

    # If we are given a file that isn't an absolute path, look for it
    # in the source directory if it doesn't exist.
    candidates = [
        app.config.config_generator_config_file,
        os.path.join(
            app.srcdir,
            app.config.config_generator_config_file,
        ),
    ]
    for c in candidates:
        if os.path.isfile(c):
            info('reading config generator instructions from %s' % c)
            config_path = c
            break
    else:
        raise ValueError(
            "Could not find config_generator_config_file %r" %
            app.config.config_generator_config_file)

    if app.config.sample_config_basename:
        out_file = os.path.join(
            app.srcdir, app.config.sample_config_basename) + '.conf.sample'
        if not os.path.isdir(os.path.dirname(os.path.abspath(out_file))):
            os.mkdir(os.path.dirname(os.path.abspath(out_file)))
    else:
        file_name = 'sample.config'
        out_file = os.path.join(app.srcdir, file_name)

    info('writing sample configuration to %s' % out_file)
    generator.main(args=['--config-file', config_path,
                         '--output-file', out_file])


def setup(app):
    app.add_config_value('config_generator_config_file', None, 'env')
    app.add_config_value('sample_config_basename', None, 'env')
    app.connect('builder-inited', generate_sample)
