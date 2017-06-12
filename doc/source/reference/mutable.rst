Enabling your project for mutable config
========================================

As of OpenStack Newton, config options can be marked as 'mutable'. This means
they can be reloaded (usually via SIGHUP) at runtime, without a service
restart. However, each project has to be enabled before this will work and some
care needs to be taken over how each option is used before it can safely be
marked mutable.

.. contents:: Table of Contents
   :local:


Calling mutate_config_files
---------------------------

Config mutation is triggered by ``ConfigOpts#mutate_config_files`` being
called. Services launched with oslo.service get a signal handler on SIGHUP but
by default that calls the older ``ConfigOpts#reload_config_files`` method. To
get the new behaviour, we have to pass ``restart_method='mutate'``. For
example::

    service.ProcessLauncher(CONF, restart_method='mutate')

An example patch is here: https://review.openstack.org/#/c/280851

Some projects may call ``reload_config_files`` directly, in this case just
change that call to ``mutate_config_files``. If there is no signal handler or
you want to trigger reload by a different method, maybe via a web UI or
watching a file, just ensure your trigger calls ``mutate_config_files``.



Making options mutable-safe
---------------------------

When options are mutated, they change in the ConfigOpts object but this will
not necessarily affect your service immediately. There are three main cases to
deal with:

* The option is checked every time
* The option is cached on the stack
* The option affects state


The option is checked every time
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This pattern is already safe. Example code::

    while True:
        progress_timeout = CONF.libvirt.live_migration_progress_timeout
        completion_timeout = int(
            CONF.libvirt.live_migration_completion_timeout * data_gb)
        if libvirt_migrate.should_abort(instance, now, progress_time,
                                        progress_timeout, completion_timeout):
            guest.abort_job()


The option is cached on the stack
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Just putting the option value in a local variable is enough to cache it. This
is tempting to do with loops. Example code::

    progress_timeout = CONF.libvirt.live_migration_progress_timeout
    completion_timeout = int(
        CONF.libvirt.live_migration_completion_timeout * data_gb)
    while True:
        if libvirt_migrate.should_abort(instance, now, progress_time,
                                        progress_timeout, completion_timeout):
            guest.abort_job()

The goal is to check the option exactly once every time it could have an
effect. Usually this is as simple as checking it every time, for example by
moving the locals into the loop. Example patch:
https://review.openstack.org/#/c/319203

Sometimes multiple computations have to be performed using the option values
and it's important that the result is consistent. In this case, it's necessary
to cache the option values in locals. Example patch:
https://review.openstack.org/#/c/319254


The option affects state
^^^^^^^^^^^^^^^^^^^^^^^^

An option value can also be cached, after a fashion, by state - either system
or external. For example, the 'debug' option of oslo.log is used to set the
default log level on startup. The option is not normally checked again, so if
it is mutated, the system state will not reflect the new value of the option.
In this case we have to use a *mutate hook*::

    def _mutate_hook(conf, fresh):
        if (None, 'debug') in fresh:
            if conf.debug:
                log_root.setLevel(logging.DEBUG)

    def register_options(conf):
        ... snip ...
        conf.register_mutate_hook(_mutate_hook)

Mutate hook functions will be passed two positional parameters, 'conf' and
'fresh'. 'conf' is a reference to the updated ConfigOpts object. 'fresh' looks
like::

    { (group, option_name): (old_value, new_value), ... }

for example::

    { (None, 'debug'): (False, True),
      ('libvirt', 'live_migration_progress_timeout'): (50, 75) }

Hooks may be called in any order.

Each project should register one hook, which does whatever is necessary to
apply all the new option values. This hook function could grow very large. For
good style, modularise the hook using secondary functions rather than accreting
a monolith or registering multiple hooks.

Example patch: https://review.openstack.org/#/c/254821/
