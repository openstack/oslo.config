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
    ERROR:root:foo/bar not found
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
    ERROR:root:foo/bar not found
    INFO:root:Ignoring missing option "project_domain_name" from group "keystone_authtoken" because the group is known to have incomplete sample config data and thus cannot be validated properly.
    INFO:root:Ignoring missing option "project_name" from group "keystone_authtoken" because the group is known to have incomplete sample config data and thus cannot be validated properly.
    INFO:root:Ignoring missing option "user_domain_name" from group "keystone_authtoken" because the group is known to have incomplete sample config data and thus cannot be validated properly.
    INFO:root:Ignoring missing option "password" from group "keystone_authtoken" because the group is known to have incomplete sample config data and thus cannot be validated properly.
    INFO:root:Ignoring missing option "username" from group "keystone_authtoken" because the group is known to have incomplete sample config data and thus cannot be validated properly.
    INFO:root:Ignoring missing option "auth_url" from group "keystone_authtoken" because the group is known to have incomplete sample config data and thus cannot be validated properly.

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
