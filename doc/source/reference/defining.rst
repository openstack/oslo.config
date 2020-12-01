==================
 Defining Options
==================

Configuration options may be set on the command line, in the
:mod:`environment <oslo_config.sources._environment>`, or in config files.
Options are processed in that order.

The schema for each option is defined using the
:class:`Opt` class or its sub-classes, for example:

.. code-block:: python

    from oslo_config import cfg
    from oslo_config import types

    PortType = types.Integer(1, 65535)

    common_opts = [
        cfg.StrOpt('bind_host',
                   default='0.0.0.0',
                   help='IP address to listen on.'),
        cfg.Opt('bind_port',
                type=PortType,
                default=9292,
                help='Port number to listen on.')
    ]

Option Types
------------

Options can have arbitrary types via the `type` parameter to the :class:`Opt`
constructor. The `type` parameter is a callable object that takes a string and
either returns a value of that particular type or raises :class:`ValueError` if
the value can not be converted.

For convenience, there are predefined option subclasses in
:mod:`oslo_config.cfg` that set the option `type` as in the following table:

======================================  ======
Type                                    Option
======================================  ======
:class:`oslo_config.types.String`       :class:`oslo_config.cfg.StrOpt`
:class:`oslo_config.types.String`       :class:`oslo_config.cfg.SubCommandOpt`
:class:`oslo_config.types.Boolean`      :class:`oslo_config.cfg.BoolOpt`
:class:`oslo_config.types.Integer`      :class:`oslo_config.cfg.IntOpt`
:class:`oslo_config.types.Float`        :class:`oslo_config.cfg.FloatOpt`
:class:`oslo_config.types.Port`         :class:`oslo_config.cfg.PortOpt`
:class:`oslo_config.types.List`         :class:`oslo_config.cfg.ListOpt`
:class:`oslo_config.types.Dict`         :class:`oslo_config.cfg.DictOpt`
:class:`oslo_config.types.IPAddress`    :class:`oslo_config.cfg.IPOpt`
:class:`oslo_config.types.Hostname`     :class:`oslo_config.cfg.HostnameOpt`
:class:`oslo_config.types.HostAddress`  :class:`oslo_config.cfg.HostAddressOpt`
:class:`oslo_config.types.URI`          :class:`oslo_config.cfg.URIOpt`
======================================  ======

For :class:`oslo_config.cfg.MultiOpt` the `item_type` parameter defines
the type of the values. For convenience, :class:`oslo_config.cfg.MultiStrOpt`
is :class:`~oslo_config.cfg.MultiOpt` with the `item_type` parameter set to
:class:`oslo_config.types.MultiString`.

The following example defines options using the convenience classes:

.. code-block:: python

    enabled_apis_opt = cfg.ListOpt('enabled_apis',
                                   default=['ec2', 'osapi_compute'],
                                   help='List of APIs to enable by default.')

    DEFAULT_EXTENSIONS = [
        'nova.api.openstack.compute.contrib.standard_extensions'
    ]
    osapi_compute_extension_opt = cfg.MultiStrOpt('osapi_compute_extension',
                                                  default=DEFAULT_EXTENSIONS)

Registering Options
-------------------

Option schemas are registered with the config manager at runtime, but before
the option is referenced:

.. code-block:: python

    class ExtensionManager:

        enabled_apis_opt = cfg.ListOpt(...)

        def __init__(self, conf):
            self.conf = conf
            self.conf.register_opt(enabled_apis_opt)
            ...

        def _load_extensions(self):
            for ext_factory in self.conf.osapi_compute_extension:
                ....

A common usage pattern is for each option schema to be defined in the module or
class which uses the option:

.. code-block:: python

    opts = ...

    def add_common_opts(conf):
        conf.register_opts(opts)

    def get_bind_host(conf):
        return conf.bind_host

    def get_bind_port(conf):
        return conf.bind_port

An option may optionally be made available via the command line. Such options
must be registered with the config manager before the command line is parsed
(for the purposes of --help and CLI arg validation).

Note that options registered for CLI use do not need to be registered again for
use from other config sources, such as files. CLI options can be read from
either the CLI or from the other enabled config sources.

.. code-block:: python

    cli_opts = [
        cfg.BoolOpt('verbose',
                    short='v',
                    default=False,
                    help='Print more verbose output.'),
        cfg.BoolOpt('debug',
                    short='d',
                    default=False,
                    help='Print debugging output.'),
    ]

    def add_common_opts(conf):
        conf.register_cli_opts(cli_opts)

Option Groups
-------------

Options can be registered as belonging to a group:

.. code-block:: python

    rabbit_group = cfg.OptGroup(name='rabbit',
                                title='RabbitMQ options')

    rabbit_host_opt = cfg.StrOpt('host',
                                 default='localhost',
                                 help='IP/hostname to listen on.'),
    rabbit_port_opt = cfg.PortOpt('port',
                                  default=5672,
                                  help='Port number to listen on.')

    def register_rabbit_opts(conf):
        conf.register_group(rabbit_group)
        # options can be registered under a group in either of these ways:
        conf.register_opt(rabbit_host_opt, group=rabbit_group)
        conf.register_opt(rabbit_port_opt, group='rabbit')

If no group attributes are required other than the group name, the group
need not be explicitly registered for example:

.. code-block:: python

    def register_rabbit_opts(conf):
        # The group will automatically be created, equivalent calling:
        #   conf.register_group(OptGroup(name='rabbit'))
        conf.register_opt(rabbit_port_opt, group='rabbit')

If no group is specified, options belong to the 'DEFAULT' section of config
files:

.. code-block:: text

    glance-api.conf:
      [DEFAULT]
      bind_port = 9292
      ...

      [rabbit]
      host = localhost
      port = 5672
      use_ssl = False
      userid = guest
      password = guest
      virtual_host = /

Command-line options in a group are automatically prefixed with the
group name:

.. code-block:: console

    --rabbit-host localhost --rabbit-port 9999

Dynamic Groups
--------------

Groups can be registered dynamically by application code. This
introduces a challenge for the sample generator, discovery mechanisms,
and validation tools, since they do not know in advance the names of
all of the groups. The ``dynamic_group_owner`` parameter to the
constructor specifies the full name of an option registered in another
group that controls repeated instances of a dynamic group. This option
is usually a MultiStrOpt.

For example, Cinder supports multiple storage backend devices and
services. To configure Cinder to communicate with multiple backends,
the ``enabled_backends`` option is set to the list of names of
backends. Each backend group includes the options for communicating
with that device or service.

Driver Groups
-------------

Groups can have dynamic sets of options, usually based on a driver
that has unique requirements. This works at runtime because the code
registers options before it uses them, but it introduces a challenge
for the sample generator, discovery mechanisms, and validation tools
because they do not know in advance the correct options for a group.

To address this issue, the driver option for a group can be named
using the ``driver_option`` parameter.  Each driver option should
define its own discovery entry point namespace to return the set of
options for that driver, named using the prefix
``"oslo.config.opts."`` followed by the driver option name.

In the Cinder case described above, a ``volume_backend_name`` option
is part of the static definition of the group, so ``driver_option``
should be set to ``"volume_backend_name"``. And plugins should be
registered under ``"oslo.config.opts.volume_backend_name"`` using the
same names as the main plugin registered with
``"oslo.config.opts"``. The drivers residing within the Cinder code
base have an entry point named ``"cinder"`` registered.

Special Handling Instructions
-----------------------------

Options may be declared as required so that an error is raised if the user
does not supply a value for the option:

.. code-block:: python

    opts = [
        cfg.StrOpt('service_name', required=True),
        cfg.StrOpt('image_id', required=True),
        ...
    ]

Options may be declared as secret so that their values are not leaked into
log files:

.. code-block:: python

     opts = [
        cfg.StrOpt('s3_store_access_key', secret=True),
        cfg.StrOpt('s3_store_secret_key', secret=True),
        ...
     ]

Dictionary Options
------------------

If you need end users to specify a dictionary of key/value pairs, then you can
use the DictOpt:

.. code-block:: python

    opts = [
        cfg.DictOpt('foo',
                    default={})
    ]

The end users can then specify the option foo in their configuration file
as shown below:

.. code-block:: ini

    [DEFAULT]
    foo = k1:v1,k2:v2

Advanced Option
---------------

Use if you need to label an option as advanced in sample files, indicating the
option is not normally used by the majority of users and might have a
significant effect on stability and/or performance:

.. code-block:: python

    from oslo_config import cfg

    opts = [
        cfg.StrOpt('option1', default='default_value',
                    advanced=True, help='This is help '
                    'text.'),
        cfg.PortOpt('option2', default='default_value',
                     help='This is help text.'),
    ]

    CONF = cfg.CONF
    CONF.register_opts(opts)

This will result in the option being pushed to the bottom of the
namespace and labeled as advanced in the sample files, with a notation
about possible effects:

.. code-block:: ini

    [DEFAULT]
    ...
    # This is help text. (string value)
    # option2 = default_value
    ...
    <pushed to bottom of section>
    ...
    # This is help text. (string value)
    # Advanced Option: intended for advanced users and not used
    # by the majority of users, and might have a significant
    # effect on stability and/or performance.
    # option1 = default_value
