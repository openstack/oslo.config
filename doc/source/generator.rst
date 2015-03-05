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

Defining Option Discovery Entry Points
--------------------------------------

The ``--namespace`` option specifies an entry point name registered under the
'oslo.config.opts' entry point namespace. For example, in oslo.messaging's
setup.cfg we have::

  [entry_points]
  oslo.config.opts =
      oslo.messaging = oslo.messaging.opts:list_opts

The callable referenced by the entry point should take no arguments and return
a list of (group_name, [opt_1, opt_2]) tuples. For example::

  opts = [
      cfg.StrOpt('foo'),
      cfg.StrOpt('bar'),
  ]

  cfg.CONF.register_opts(opts, group='blaa')

  def list_opts():
      return [('blaa', opts)]

You might choose to return a copy of the options so that the return value can't
be modified for nefarious purposes, though this is not strictly necessary::

  def list_opts():
      return [('blaa', copy.deepcopy(opts))]

The module holding the entry point *must* be importable, even if the
dependencies of that module are not installed. For example, driver
modules that define options but have optional dependencies on
third-party modules must still be importable if those modules are not
installed. To accomplish this, the optional dependency can either be
imported using :func:`oslo.utils.importutils.try_import` or the option
definitions can be placed in a file that does not try to import the
optional dependency.

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
