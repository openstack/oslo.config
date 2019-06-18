=======================
 oslo-config-generator
=======================

`oslo-config-generator` is a utility for generating sample config files in a
variety of formats. Sample config files list all of the available options,
along with their help string, type, deprecated aliases and defaults.  These
sample files can be used as config files for `oslo.config` itself (``ini``) or
by configuration management tools (``json``, ``yaml``).

.. versionadded:: 1.4.0

.. versionchanged:: 4.3.0

   The :option:`oslo-config-generator --format` parameter was added, which
   allows outputting in additional formats.

Usage
-----

.. program:: oslo-config-generator

.. code-block:: shell

   oslo-config-generator
      --namespace <namespace> [--namespace <namespace> ...]
      [--output-file <output-file>]
      [--wrap-width <wrap-width>]
      [--format <format>]
      [--minimal]
      [--summarize]

.. option:: --namespace <namespace>

   Option namespace under ``oslo.config.opts`` in which to query for options.

.. option:: --output-file <output-file>

   Path of the file to write to.

   :Default: stdout

.. option:: --wrap-width <wrap-width>

   The maximum length of help lines.

   :Default: 70

.. option:: --format <format>

   Desired format for the output. ``ini`` is the only format that can be used
   directly with `oslo.config`. ``json`` and ``yaml`` are intended for
   third-party tools that want to write config files based on the sample config
   data. For more information, refer to :ref:`machine-readable-configs`.

   :Choices: ini, json, yaml

.. option:: --minimal

   Generate a minimal required configuration.

.. option:: --summarize

   Only output summaries of help text to config files. Retain longer help text
   for Sphinx documents.

For example, to generate a sample config file for `oslo.messaging` you would
run:

.. code-block:: shell

   $ oslo-config-generator --namespace oslo.messaging > oslo.messaging.conf

To generate a sample config file for an application ``myapp`` that has its own
options and uses `oslo.messaging`, you would list both namespaces:

.. code-block:: shell

   $ oslo-config-generator --namespace myapp \
       --namespace oslo.messaging > myapp.conf

To generate a sample config file for `oslo.messaging` in `JSON` format, you
would run:

.. code-block:: shell

   $ oslo-config-generator --namespace oslo.messaging \
       --format json > oslo.messaging.conf

Defining Option Discovery Entry Points
--------------------------------------

The :option:`oslo-config-generator --namespace` option specifies an entry point
name registered under the ``oslo.config.opts`` entry point namespace. For
example, in the `oslo.messaging` ``setup.cfg`` we have:

.. code-block:: ini

  [entry_points]
  oslo.config.opts =
      oslo.messaging = oslo.messaging.opts:list_opts

The callable referenced by the entry point should take no arguments and return
a list of ``(group, [opt_1, opt_2])`` tuples, where ``group`` is either a group
name as a string or an ``OptGroup`` object. Passing the ``OptGroup`` object
allows the consumer of the ``list_opts`` method to access and publish group
help. An example, using both styles:

.. code-block:: python

   from oslo_config import cfg

   opts1 = [
       cfg.StrOpt('foo'),
       cfg.StrOpt('bar'),
   ]

   opts2 = [
       cfg.StrOpt('baz'),
   ]

   baz_group = cfg.OptGroup(name='baz_group'
                            title='Baz group options',
                            help='Baz group help text')
   cfg.CONF.register_group(baz_group)

   cfg.CONF.register_opts(opts1, group='blaa')
   cfg.CONF.register_opts(opts2, group=baz_group)

   def list_opts():
       # Allows the generation of the help text for
       # the baz_group OptGroup object. No help
       # text is generated for the 'blaa' group.
       return [('blaa', opts1), (baz_group, opts2)]

.. note::

   You should return the original options, not a copy, because the
   default update hooks depend on the original option object being
   returned.

The module holding the entry point *must* be importable, even if the
dependencies of that module are not installed. For example, driver
modules that define options but have optional dependencies on
third-party modules must still be importable if those modules are not
installed. To accomplish this, the optional dependency can either be
imported using :func:`oslo.utils.importutils.try_import` or the option
definitions can be placed in a file that does not try to import the
optional dependency.

Modifying Defaults from Other Namespaces
----------------------------------------

Occasionally applications need to override the defaults for options
defined in libraries. At runtime this is done using an API within the
library. Since the config generator cannot guarantee the order in
which namespaces will be imported, we can't ensure that application
code can change the option defaults before the generator loads the
options from a library. Instead, a separate optional processing hook
is provided for applications to register a function to update default
values after *all* options are loaded.

The hooks are registered in a separate entry point namespace
(``oslo.config.opts.defaults``), using the same entry point name as
**the application's** ``list_opts()`` function.

.. code-block:: ini

   [entry_points]
   oslo.config.opts.defaults =
       keystone = keystone.common.config:update_opt_defaults

.. warning::

   Never, under any circumstances, register an entry point using a
   name owned by another project. Doing so causes unexpected interplay
   between projects within the config generator and will result in
   failure to generate the configuration file or invalid values
   showing in the sample.

   In this case, the name of the entry point for the default override
   function *must* match the name of one of the entry points defining
   options for the application in order to be detected and
   used. Applications that have multiple list_opts functions should use
   one that is present in the inputs for the config generator where
   the changed defaults need to appear. For example, if an application
   defines ``foo.api`` to list the API-related options, and needs to
   override the defaults in the ``oslo.middleware.cors`` library, the
   application should register ``foo.api`` under
   ``oslo.config.opts.defaults`` and point to a function within the
   application code space that changes the defaults for
   ``oslo.middleware.cors``.

The update function should take no arguments. It should invoke the
public :func:`set_defaults` functions in any libraries for which it
has option defaults to override, just as the application does during
its normal startup process.

.. code-block:: python

   from oslo_log import log

   def update_opt_defaults():
       log.set_defaults(
           default_log_levels=log.get_default_log_levels() + ['noisy=WARN'],
       )

.. _machine-readable-configs:

Generating Machine Readable Configs
-----------------------------------

All deployment tools have to solve a similar problem: how to generate the
config files for each service at deployment time. To help with this problem,
`oslo-config-generator` can generate machine-readable sample config files that
output the same data as the INI files used by `oslo.config` itself, but in a
YAML or JSON format that can be more easily consumed by deployment tools.

.. important::

   The YAML and JSON-formatted files generated by `oslo-config-generator`
   cannot be used by `oslo.config` itself - they are only for use by other
   tools.

For example, some YAML-formatted output might look like so:

.. code-block:: yaml

   generator_options:
     config_dir: []
     config_file: []
     format_: yaml
     minimal: false
     namespace:
     - keystone
     output_file: null
     summarize: false
     wrap_width: 70
   options:
     DEFAULT:
       help: ''
       opts:
       - advanced: false
         choices: []
         default: null
         deprecated_for_removal: false
         deprecated_opts: []
         deprecated_reason: null
         deprecated_since: null
         dest: admin_token
         help: Using this feature is *NOT* recommended. Instead, use the `keystone-manage
           bootstrap` command. The value of this option is treated as a "shared secret"
           that can be used to bootstrap Keystone through the API. This "token" does
           not represent a user (it has no identity), and carries no explicit authorization
           (it effectively bypasses most authorization checks). If set to `None`, the
           value is ignored and the `admin_token` middleware is effectively disabled.
           However, to completely disable `admin_token` in production (highly recommended,
           as it presents a security risk), remove `AdminTokenAuthMiddleware` (the `admin_token_auth`
           filter) from your paste application pipelines (for example, in `keystone-paste.ini`).
         max: null
         metavar: null
         min: null
         mutable: false
         name: admin_token
         namespace: keystone
         positional: false
         required: false
         sample_default: null
         secret: true
         short: null
         type: string value
       - ...
     ...
   deprecated_options:
     DEFAULT:
     - name: bind_host
       replacement_group: eventlet_server
       replacement_name: public_bind_host

where the top-level keys are:

``generator_options``

  The options passed to the :program:`oslo-config-generator` tool itself

``options``

  All options registered in the provided namespace(s). These are grouped under
  the ``OptGroup`` they are assigned to which defaults to ``DEFAULT`` if unset.

  For information on the various attributes of each option, refer to
  :class:`oslo_config.cfg.Opt` and its subclasses.

``deprecated_options``

  All **deprecated** options registered in the provided namespace(s). Like
  ``options``, these options are grouped by ``OptGroup``.

Generating Multiple Sample Configs
----------------------------------

A single codebase might have multiple programs, each of which use a subset of
the total set of options registered by the codebase. In that case, you can
register multiple entry points:

.. code-block:: ini

  [entry_points]
  oslo.config.opts =
      nova.common = nova.config:list_common_opts
      nova.api = nova.config:list_api_opts
      nova.compute = nova.config:list_compute_opts

and generate a config file specific to each program:

.. code-block:: shell

   $ oslo-config-generator --namespace oslo.messaging \
                           --namespace nova.common \
                           --namespace nova.api > nova-api.conf
   $ oslo-config-generator --namespace oslo.messaging \
                           --namespace nova.common \
                           --namespace nova.compute > nova-compute.conf

To make this more convenient, you can use config files to describe your config
files:

.. code-block:: shell

   $ cat > config-generator/api.conf <<EOF
   [DEFAULT]
   output_file = etc/nova/nova-api.conf
   namespace = oslo.messaging
   namespace = nova.common
   namespace = nova.api
   EOF
   $ cat > config-generator/compute.conf <<EOF
   [DEFAULT]
   output_file = etc/nova/nova-compute.conf
   namespace = oslo.messaging
   namespace = nova.common
   namespace = nova.compute
   EOF
   $ oslo-config-generator --config-file config-generator/api.conf
   $ oslo-config-generator --config-file config-generator/compute.conf

Sample Default Values
---------------------

The default runtime values of configuration options are not always the most
suitable values to include in sample config files - for example, rather than
including the IP address or hostname of the machine where the config file
was generated, you might want to include something like ``10.0.0.1``. To
facilitate this, options can be supplied with a ``sample_default`` attribute:

.. code-block:: python

   cfg.StrOpt('base_dir'
              default=os.getcwd(),
              sample_default='/usr/lib/myapp')
