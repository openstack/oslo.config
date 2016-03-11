=======================
 oslo-config-generator
=======================

oslo-config-generator is a utility for generating sample config files. For
example, to generate a sample config file for oslo.messaging you would run::

  $> oslo-config-generator --namespace oslo.messaging > oslo.messaging.conf

This generated sample lists all of the available options, along with their help
string, type, deprecated aliases and defaults.

To generate a sample config file for an application ``myapp`` that has
its own options and uses oslo.messaging, you can list both
namespaces::

  $> oslo-config-generator --namespace myapp --namespace oslo.messaging > myapp.conf

.. versionadded:: 1.4

Defining Option Discovery Entry Points
--------------------------------------

The ``--namespace`` option specifies an entry point name registered under the
'oslo.config.opts' entry point namespace. For example, in oslo.messaging's
setup.cfg we have::

  [entry_points]
  oslo.config.opts =
      oslo.messaging = oslo.messaging.opts:list_opts

The callable referenced by the entry point should take no arguments and return
a list of (``group``, [opt_1, opt_2]) tuples, where ``group`` is either a
group name as a string or an ``OptGroup`` object. Passing the ``OptGroup``
object allows the consumer of the ``list_opts`` method to access and publish
group help. An example, using both styles::

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

::

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
   used. Applications that have multple list_opts functions should use
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

::

   from oslo_log import log

   def update_opt_defaults():
       log.set_defaults(
           default_log_levels=log.get_default_log_levels() + ['noisy=WARN'],
       )

Generating Multiple Sample Configs
----------------------------------

A single codebase might have multiple programs, each of which use a subset of
the total set of options registered by the codebase. In that case, you can
register multiple entry points::

  [entry_points]
  oslo.config.opts =
      nova.common = nova.config:list_common_opts
      nova.api = nova.config:list_api_opts
      nova.compute = nova.config:list_compute_opts

and generate a config file specific to each program::

  $> oslo-config-generator --namespace oslo.messaging \
                           --namespace nova.common \
                           --namespace nova.api > nova-api.conf
  $> oslo-config-generator --namespace oslo.messaging \
                           --namespace nova.common \
                           --namespace nova.compute > nova-compute.conf

To make this more convenient, you can use config files to describe your config
files::

  $> cat > config-generator/api.conf <<EOF
  [DEFAULT]
  output_file = etc/nova/nova-api.conf
  namespace = oslo.messaging
  namespace = nova.common
  namespace = nova.api
  EOF
  $> cat > config-generator/compute.conf <<EOF
  [DEFAULT]
  output_file = etc/nova/nova-compute.conf
  namespace = oslo.messaging
  namespace = nova.common
  namespace = nova.compute
  EOF
  $> oslo-config-generator --config-file config-generator/api.conf
  $> oslo-config-generator --config-file config-generator/compute.conf

Sample Default Values
---------------------

The default runtime values of configuration options are not always the most
suitable values to include in sample config files - for example, rather than
including the IP address or hostname of the machine where the config file
was generated, you might want to include something like '10.0.0.1'. To
facilitate this, options can be supplied with a 'sample_default' attribute::

  cfg.StrOpt('base_dir'
             default=os.getcwd(),
             sample_default='/usr/lib/myapp')

API
---

.. currentmodule:: oslo_config.generator

.. autofunction:: main
.. autofunction:: generate
.. autofunction:: register_cli_opts
