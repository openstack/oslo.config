#
# Copyright 2013 Mirantis, Inc.
# Copyright 2013 OpenStack Foundation
# All Rights Reserved.
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

from oslotest import base

from oslo_config import cfg
from oslo_config import fixture as config

conf = cfg.CONF


class ConfigTestCase(base.BaseTestCase):
    def setUp(self):
        super(ConfigTestCase, self).setUp()
        self.config_fixture = self.useFixture(config.Config(conf))
        self.config = self.config_fixture.config
        self.config_fixture.register_opt(cfg.StrOpt(
            'testing_option', default='initial_value'))

    def test_overridden_value(self):
        self.assertEqual(conf.get('testing_option'), 'initial_value')
        self.config(testing_option='changed_value')
        self.assertEqual(conf.get('testing_option'),
                         self.config_fixture.conf.get('testing_option'))

    def test_cleanup(self):
        self.config(testing_option='changed_value')
        self.assertEqual(self.config_fixture.conf.get('testing_option'),
                         'changed_value')
        self.config_fixture.conf.reset()
        self.assertEqual(conf.get('testing_option'), 'initial_value')

    def test_register_option(self):
        opt = cfg.StrOpt('new_test_opt', default='initial_value')
        self.config_fixture.register_opt(opt)
        self.assertEqual(conf.get('new_test_opt'),
                         opt.default)

    def test_register_options(self):
        opt1 = cfg.StrOpt('first_test_opt', default='initial_value_1')
        opt2 = cfg.StrOpt('second_test_opt', default='initial_value_2')
        self.config_fixture.register_opts([opt1, opt2])
        self.assertEqual(conf.get('first_test_opt'), opt1.default)
        self.assertEqual(conf.get('second_test_opt'), opt2.default)

    def test_cleanup_unregister_option(self):
        opt = cfg.StrOpt('new_test_opt', default='initial_value')
        self.config_fixture.register_opt(opt)
        self.assertEqual(conf.get('new_test_opt'),
                         opt.default)
        self.config_fixture.cleanUp()
        self.assertRaises(cfg.NoSuchOptError, conf.get, 'new_test_opt')

    def test_register_cli_option(self):
        opt = cfg.StrOpt('new_test_opt', default='initial_value')
        self.config_fixture.register_cli_opt(opt)
        self.assertEqual(conf.get('new_test_opt'),
                         opt.default)

    def test_register_cli_options(self):
        opt1 = cfg.StrOpt('first_test_opt', default='initial_value_1')
        opt2 = cfg.StrOpt('second_test_opt', default='initial_value_2')
        self.config_fixture.register_cli_opts([opt1, opt2])
        self.assertEqual(conf.get('first_test_opt'), opt1.default)
        self.assertEqual(conf.get('second_test_opt'), opt2.default)

    def test_cleanup_unregister_cli_option(self):
        opt = cfg.StrOpt('new_test_opt', default='initial_value')
        self.config_fixture.register_cli_opt(opt)
        self.assertEqual(conf.get('new_test_opt'),
                         opt.default)
        self.config_fixture.cleanUp()
        self.assertRaises(cfg.NoSuchOptError, conf.get, 'new_test_opt')

    def test_load_raw_values(self):
        self.config_fixture.load_raw_values(first_test_opt='loaded_value_1',
                                            second_test_opt='loaded_value_2')

        # Must not be registered.
        self.assertRaises(cfg.NoSuchOptError, conf.get, 'first_test_opt')
        self.assertRaises(cfg.NoSuchOptError, conf.get, 'second_test_opt')

        opt1 = cfg.StrOpt('first_test_opt', default='initial_value_1')
        opt2 = cfg.StrOpt('second_test_opt', default='initial_value_2')

        self.config_fixture.register_opt(opt1)
        self.config_fixture.register_opt(opt2)

        self.assertEqual(conf.first_test_opt, 'loaded_value_1')
        self.assertEqual(conf.second_test_opt, 'loaded_value_2')

        # Cleanup.
        self.config_fixture.cleanUp()

        # Must no longer be registered.
        self.assertRaises(cfg.NoSuchOptError, conf.get, 'first_test_opt')
        self.assertRaises(cfg.NoSuchOptError, conf.get, 'second_test_opt')

        # Even when registered, must be default.
        self.config_fixture.register_opt(opt1)
        self.config_fixture.register_opt(opt2)
        self.assertEqual(conf.first_test_opt, 'initial_value_1')
        self.assertEqual(conf.second_test_opt, 'initial_value_2')

    def test_assert_default_files_cleanup(self):
        """Assert that using the fixture forces a clean list."""
        self.assertNotIn('default_config_files', conf)

        config_files = ['./test_fixture.conf']
        self.config_fixture.set_config_files(config_files)

        self.assertEqual(conf.default_config_files, config_files)
        self.config_fixture.cleanUp()

        self.assertNotIn('default_config_files', conf)

    def test_load_custom_files(self):
        self.assertNotIn('default_config_files', conf)
        config_files = ['./oslo_config/tests/test_fixture.conf']
        self.config_fixture.set_config_files(config_files)

        opt1 = cfg.StrOpt('first_test_opt', default='initial_value_1')
        opt2 = cfg.StrOpt('second_test_opt', default='initial_value_2')

        self.config_fixture.register_opt(opt1)
        self.config_fixture.register_opt(opt2)

        self.assertEqual('loaded_value_1', conf.get('first_test_opt'))
        self.assertEqual('loaded_value_2', conf.get('second_test_opt'))
