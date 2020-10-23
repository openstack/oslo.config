=====================
oslo-config-validator
=====================

`oslo-config-validator` is a utility for verifying that the entries in a
config file are correct. It will report an error for any options found that
are not defined by the service, and a warning for any deprecated options found.

.. versionadded:: 6.5.0

Usage
-----

There are two primary ways to use the config validator. It can use the sample
config generator configuration file found in each service to determine the list
of available options, or it can consume a machine-readable sample config that
provides the same information.

Sample Config Generator Configuration
-------------------------------------

.. note:: When using this method, all dependencies of the service must be
          installed in the environment where the validator is run.

There are two parameters that must be passed to the validator in this case:
``--config-file`` and ``--input-file``.  ``--config-file`` should point at the
location of the sample config generator configuration file, while
``--input-file`` should point at the location of the configuration file to be
validated.

Here's an example of using the validator on Nova as installed by Devstack (with
the option [foo]/bar added to demonstrate a failure)::

    $ oslo-config-validator --config-file /opt/stack/nova/etc/nova/nova-config-generator.conf --input-file /etc/nova/nova.conf
    ERROR:root:foo/bar is not part of the sample config
    INFO:root:Ignoring missing option "project_domain_name" from group "keystone_authtoken" because the group is known to have incomplete sample config data and thus cannot be validated properly.
    INFO:root:Ignoring missing option "project_name" from group "keystone_authtoken" because the group is known to have incomplete sample config data and thus cannot be validated properly.
    INFO:root:Ignoring missing option "user_domain_name" from group "keystone_authtoken" because the group is known to have incomplete sample config data and thus cannot be validated properly.
    INFO:root:Ignoring missing option "password" from group "keystone_authtoken" because the group is known to have incomplete sample config data and thus cannot be validated properly.
    INFO:root:Ignoring missing option "username" from group "keystone_authtoken" because the group is known to have incomplete sample config data and thus cannot be validated properly.
    INFO:root:Ignoring missing option "auth_url" from group "keystone_authtoken" because the group is known to have incomplete sample config data and thus cannot be validated properly.

Machine-Readable Sample Config
------------------------------

.. note:: For most accurate results, the machine-readable sample config should
          be generated from the same version of the code as is running on
          the system whose config file is being validated.

In this case, a machine-readable sample config must first be generated, as
described in :doc:`generator`.

This file is then passed to the validator with ``--opt-data``, along with the
config file to validated in ``--input-file`` as above.

Here's an example of using the validator on Nova as installed by Devstack, with
a sample config file ``config-data.yaml`` created by the config generator (with
the option [foo]/bar added to demonstrate a failure)::

    $ oslo-config-validator --opt-data config-data.yaml --input-file /etc/nova/nova.conf
    ERROR:root:foo/bar is not part of the sample config
    INFO:root:Ignoring missing option "project_domain_name" from group "keystone_authtoken" because the group is known to have incomplete sample config data and thus cannot be validated properly.
    INFO:root:Ignoring missing option "project_name" from group "keystone_authtoken" because the group is known to have incomplete sample config data and thus cannot be validated properly.
    INFO:root:Ignoring missing option "user_domain_name" from group "keystone_authtoken" because the group is known to have incomplete sample config data and thus cannot be validated properly.
    INFO:root:Ignoring missing option "password" from group "keystone_authtoken" because the group is known to have incomplete sample config data and thus cannot be validated properly.
    INFO:root:Ignoring missing option "username" from group "keystone_authtoken" because the group is known to have incomplete sample config data and thus cannot be validated properly.
    INFO:root:Ignoring missing option "auth_url" from group "keystone_authtoken" because the group is known to have incomplete sample config data and thus cannot be validated properly.

Comparing configuration with the default configuration
------------------------------------------------------

.. note:: For most accurate results, the validation should be done using the
          same version of the code as the system whose config file is being
          validated.

Comparing the default configuration with the current configuration can help
operators with troubleshooting issues. Since the generator config is not always
available in production environment, we can pass the ``--namespace`` arguments.
In addition to the ``--namespace``, we need to pass a ``--input-file`` as well
as the ``--check-defaults``.

Some options are ignored by default but this behavior can be overridden with
the ``--exclude-options`` list argument.

Here's an example of using the validator on Nova::

    $ oslo-config-validator --input-file /etc/nova/nova.conf \
                            --check-defaults \
                            --namespace nova.conf \
                            --namespace oslo.log \
                            --namespace oslo.messaging \
                            --namespace oslo.policy \
                            --namespace oslo.privsep \
                            --namespace oslo.service.periodic_task \
                            --namespace oslo.service.service \
                            --namespace oslo.db \
                            --namespace oslo.db.concurrency \
                            --namespace oslo.middleware \
                            --namespace oslo.concurrency \
                            --namespace keystonemiddleware.auth_token \
                            --namespace osprofiler
    INFO:keyring.backend:Loading Gnome
    INFO:keyring.backend:Loading Google
    INFO:keyring.backend:Loading Windows (alt)
    INFO:keyring.backend:Loading file
    INFO:keyring.backend:Loading keyczar
    INFO:keyring.backend:Loading multi
    INFO:keyring.backend:Loading pyfs
    WARNING:root:DEFAULT/compute_driver sample value is empty but input-file has libvirt.LibvirtDriver
    WARNING:root:DEFAULT/allow_resize_to_same_host sample value is empty but input-file has True
    WARNING:root:DEFAULT/default_ephemeral_format sample value is empty but input-file has ext4
    WARNING:root:DEFAULT/pointer_model sample value ['usbtablet'] is not in ['ps2mouse']
    WARNING:root:DEFAULT/instances_path sample value ['$state_path/instances'] is not in ['/opt/stack/data/nova/instances']
    WARNING:root:DEFAULT/shutdown_timeout sample value ['60'] is not in ['0']
    INFO:root:DEFAULT/my_ip Ignoring option because it is part of the excluded patterns. This can be changed with the --exclude-options argument.
    WARNING:root:DEFAULT/state_path sample value ['$pybasedir'] is not in ['/opt/stack/data/nova']
    INFO:root:DEFAULT/osapi_compute_listen Ignoring option because it is part of the excluded patterns. This can be changed with the --exclude-options argument.
    WARNING:root:DEFAULT/osapi_compute_workers sample value is empty but input-file has 2
    WARNING:root:DEFAULT/metadata_workers sample value is empty but input-file has 2
    WARNING:root:DEFAULT/graceful_shutdown_timeout sample value ['60'] is not in ['5']
    INFO:root:DEFAULT/transport_url Ignoring option because it is part of the excluded patterns. This can be changed with the --exclude-options argument.
    WARNING:root:DEFAULT/debug sample value is empty but input-file has True
    WARNING:root:DEFAULT/logging_context_format_string sample value ['%(asctime)s.%(msecs)03d %(process)d %(levelname)s %(name)s [%(request_id)s %(user_identity)s] %(instance)s%(message)s'] is not in ['%(color)s%(levelname)s %(name)s [\x1b[01;36m%(global_request_id)s %(request_id)s \x1b[00;36m%(project_name)s %(user_name)s%(color)s] \x1b[01;35m%(instance)s%(color)s%(message)s\x1b[00m']
    WARNING:root:DEFAULT/logging_default_format_string sample value ['%(asctime)s.%(msecs)03d %(process)d %(levelname)s %(name)s [-] %(instance)s%(message)s'] is not in ['%(color)s%(levelname)s %(name)s [\x1b[00;36m-%(color)s] \x1b[01;35m%(instance)s%(color)s%(message)s\x1b[00m']
    WARNING:root:DEFAULT/logging_debug_format_suffix sample value ['%(funcName)s %(pathname)s:%(lineno)d'] is not in ['\x1b[00;33m{{(pid=%(process)d) %(funcName)s %(pathname)s:%(lineno)d}}\x1b[00m']
    WARNING:root:DEFAULT/logging_exception_prefix sample value ['%(asctime)s.%(msecs)03d %(process)d ERROR %(name)s %(instance)s'] is not in ['ERROR %(name)s \x1b[01;35m%(instance)s\x1b[00m']
    WARNING:root:Group api from the sample config is not defined in input-file
    WARNING:root:cache/backend sample value ['dogpile.cache.null'] is not in ['dogpile.cache.memcached']
    WARNING:root:cache/enabled sample value is empty but input-file has True
    WARNING:root:cinder/os_region_name sample value is empty but input-file has RegionOne
    WARNING:root:cinder/auth_type sample value is empty but input-file has password
    INFO:root:cinder/auth_url Ignoring option because it is part of the excluded patterns. This can be changed with the --exclude-options argument.
    WARNING:root:cinder/project_name sample value is empty but input-file has service
    WARNING:root:cinder/project_domain_name sample value is empty but input-file has Default
    INFO:root:cinder/username Ignoring option because it is part of the excluded patterns. This can be changed with the --exclude-options argument.
    WARNING:root:cinder/user_domain_name sample value is empty but input-file has Default
    INFO:root:cinder/password Ignoring option because it is part of the excluded patterns. This can be changed with the --exclude-options argument.
    WARNING:root:Group compute from the sample config is not defined in input-file
    WARNING:root:conductor/workers sample value is empty but input-file has 2
    WARNING:root:Group console from the sample config is not defined in input-file
    WARNING:root:Group consoleauth from the sample config is not defined in input-file
    WARNING:root:Group cyborg from the sample config is not defined in input-file
    INFO:root:api_database/connection Ignoring option because it is part of the excluded patterns. This can be changed with the --exclude-options argument.
    WARNING:root:Group devices from the sample config is not defined in input-file
    WARNING:root:Group ephemeral_storage_encryption from the sample config is not defined in input-file
    WARNING:root:Group glance from the sample config is not defined in input-file
    WARNING:root:Group guestfs from the sample config is not defined in input-file
    WARNING:root:Group hyperv from the sample config is not defined in input-file
    WARNING:root:Group image_cache from the sample config is not defined in input-file
    WARNING:root:Group ironic from the sample config is not defined in input-file
    WARNING:root:key_manager/fixed_key sample value is empty but input-file has bae3516cc1c0eb18b05440eba8012a4a880a2ee04d584a9c1579445e675b12defdc716ec
    WARNING:root:key_manager/backend sample value ['barbican'] is not in ['nova.keymgr.conf_key_mgr.ConfKeyManager']
    WARNING:root:Group barbican from the sample config is not defined in input-file
    WARNING:root:Group vault from the sample config is not defined in input-file
    WARNING:root:Group keystone from the sample config is not defined in input-file
    INFO:root:libvirt/live_migration_uri Ignoring option because it is part of the excluded patterns. This can be changed with the --exclude-options argument.
    WARNING:root:libvirt/cpu_mode sample value is empty but input-file has none
    WARNING:root:Group mks from the sample config is not defined in input-file
    WARNING:root:neutron/default_floating_pool sample value ['nova'] is not in ['public']
    WARNING:root:neutron/service_metadata_proxy sample value is empty but input-file has True
    WARNING:root:neutron/auth_type sample value is empty but input-file has password
    INFO:root:neutron/auth_url Ignoring option because it is part of the excluded patterns. This can be changed with the --exclude-options argument.
    WARNING:root:neutron/project_name sample value is empty but input-file has service
    WARNING:root:neutron/project_domain_name sample value is empty but input-file has Default
    INFO:root:neutron/username Ignoring option because it is part of the excluded patterns. This can be changed with the --exclude-options argument.
    WARNING:root:neutron/user_domain_name sample value is empty but input-file has Default
    INFO:root:neutron/password Ignoring option because it is part of the excluded patterns. This can be changed with the --exclude-options argument.
    WARNING:root:neutron/region_name sample value is empty but input-file has RegionOne
    WARNING:root:Group pci from the sample config is not defined in input-file
    WARNING:root:placement/auth_type sample value is empty but input-file has password
    INFO:root:placement/auth_url Ignoring option because it is part of the excluded patterns. This can be changed with the --exclude-options argument.
    WARNING:root:placement/project_name sample value is empty but input-file has service
    WARNING:root:placement/project_domain_name sample value is empty but input-file has Default
    INFO:root:placement/username Ignoring option because it is part of the excluded patterns. This can be changed with the --exclude-options argument.
    WARNING:root:placement/user_domain_name sample value is empty but input-file has Default
    INFO:root:placement/password Ignoring option because it is part of the excluded patterns. This can be changed with the --exclude-options argument.
    WARNING:root:placement/region_name sample value is empty but input-file has RegionOne
    WARNING:root:Group powervm from the sample config is not defined in input-file
    WARNING:root:Group quota from the sample config is not defined in input-file
    WARNING:root:Group rdp from the sample config is not defined in input-file
    WARNING:root:Group remote_debug from the sample config is not defined in input-file
    WARNING:root:scheduler/workers sample value is empty but input-file has 2
    WARNING:root:filter_scheduler/track_instance_changes sample value ['True'] is not in ['False']
    WARNING:root:filter_scheduler/enabled_filters sample value ['AvailabilityZoneFilter', 'ComputeFilter', 'ComputeCapabilitiesFilter', 'ImagePropertiesFilter', 'ServerGroupAntiAffinityFilter', 'ServerGroupAffinityFilter'] is not in ['AvailabilityZoneFilter,ComputeFilter,ComputeCapabilitiesFilter,ImagePropertiesFilter,ServerGroupAntiAffinityFilter,ServerGroupAffinityFilter,SameHostFilter,DifferentHostFilter']
    WARNING:root:Group metrics from the sample config is not defined in input-file
    WARNING:root:Group serial_console from the sample config is not defined in input-file
    WARNING:root:Group service_user from the sample config is not defined in input-file
    WARNING:root:Group spice from the sample config is not defined in input-file
    WARNING:root:upgrade_levels/compute sample value is empty but input-file has auto
    WARNING:root:Group vendordata_dynamic_auth from the sample config is not defined in input-file
    WARNING:root:Group vmware from the sample config is not defined in input-file
    WARNING:root:Group vnc from the sample config is not defined in input-file
    WARNING:root:Group workarounds from the sample config is not defined in input-file
    WARNING:root:wsgi/api_paste_config sample value ['api-paste.ini'] is not in ['/etc/nova/api-paste.ini']
    WARNING:root:Group zvm from the sample config is not defined in input-file
    WARNING:root:oslo_concurrency/lock_path sample value is empty but input-file has /opt/stack/data/nova
    WARNING:root:Group oslo_middleware from the sample config is not defined in input-file
    WARNING:root:Group cors from the sample config is not defined in input-file
    WARNING:root:Group healthcheck from the sample config is not defined in input-file
    WARNING:root:Group oslo_messaging_amqp from the sample config is not defined in input-file
    WARNING:root:oslo_messaging_notifications/driver sample value is empty but input-file has messagingv2
    INFO:root:oslo_messaging_notifications/transport_url Ignoring option because it is part of the excluded patterns. This can be changed with the --exclude-options argument.
    WARNING:root:Group oslo_messaging_rabbit from the sample config is not defined in input-file
    WARNING:root:Group oslo_messaging_kafka from the sample config is not defined in input-file
    WARNING:root:Group oslo_policy from the sample config is not defined in input-file
    WARNING:root:Group privsep from the sample config is not defined in input-file
    WARNING:root:Group profiler from the sample config is not defined in input-file
    INFO:root:database/connection Ignoring option because it is part of the excluded patterns. This can be changed with the --exclude-options argument.
    WARNING:root:keystone_authtoken/interface sample value ['internal'] is not in ['public']
    WARNING:root:keystone_authtoken/cafile sample value is empty but input-file has /opt/stack/data/ca-bundle.pem
    WARNING:root:keystone_authtoken/memcached_servers sample value is empty but input-file has localhost:11211
    WARNING:root:keystone_authtoken/auth_type sample value is empty but input-file has password
    ERROR:root:neutron/auth_strategy is not part of the sample config
    INFO:root:Ignoring missing option "project_domain_name" from group "keystone_authtoken" because the group is known to have incomplete sample config data and thus cannot be validated properly.
    INFO:root:Ignoring missing option "project_name" from group "keystone_authtoken" because the group is known to have incomplete sample config data and thus cannot be validated properly.
    INFO:root:Ignoring missing option "user_domain_name" from group "keystone_authtoken" because the group is known to have incomplete sample config data and thus cannot be validated properly.
    INFO:root:Ignoring missing option "password" from group "keystone_authtoken" because the group is known to have incomplete sample config data and thus cannot be validated properly.
    INFO:root:Ignoring missing option "username" from group "keystone_authtoken" because the group is known to have incomplete sample config data and thus cannot be validated properly.
    INFO:root:Ignoring missing option "auth_url" from group "keystone_authtoken" because the group is known to have incomplete sample config data and thus cannot be validated properly

Handling Dynamic Groups
-----------------------

Some services register group names dynamically at runtime based on other
configuration. This is problematic for the validator because these groups won't
be present in the sample config data. The ``--exclude-group`` option for the
validator can be used to ignore such groups and allow the other options in a
config file to be validated normally.

.. note:: The ``keystone_authtoken`` group is always ignored because of the
          unusual way the options from that library are generated. The sample
          configuration data is known to be incomplete as a result.
