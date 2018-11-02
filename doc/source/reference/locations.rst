==========================
 Option Setting Locations
==========================

.. currentmodule:: oslo_config.cfg

The :func:`~ConfigOpts.get_location` method of :class:`ConfigOpts` can
be used to determine where the value for an option was set, either by
the user or by the application code. The return value is a
:class:`LocationInfo` instance, which includes 2 fields: ``location``
and ``detail``.

The ``location`` value is a member of the :class:`Locations` enum,
which has 5 possible values. The ``detail`` value is a string
describing the location. Its value depends on the ``location``.

.. list-table::
   :header-rows: 1
   :widths: 15 15 35 35

   * - Value
     - ``is_user_controlled``
     - Description
     - ``detail``
   * - ``opt_default``
     - ``False``
     - The original default set when the option was defined.
     - The source file name where the option is defined.
   * - ``set_default``
     - ``False``
     - A default value set by the application as an override of the
       original default. This usually only applies to options defined
       in libraries.
     - The source file name where :func:`~ConfigOpts.set_default` or
       :func:`set_defaults` was called.
   * - ``set_override``
     - ``False``
     - A forced value set by the application.
     - The source file name where :func:`~ConfigOpts.set_override` was
       called.
   * - ``user``
     - ``True``
     - A value set by the user through a configuration backend such as
       a file.
     - The configuration file where the option is set.
   * - ``command_line``
     - ``True``
     - A value set by the user on the command line.
     - Empty string.
   * - ``environment``
     - ``True``
     - A value set by the user in the process environment.
     - The name of the environment variable.

Did a user set a configuration option?
======================================

Each :class:`Locations` enum value has a boolean property indicating
whether that type of location is managed by the user. This eliminates
the need for application code to track which types of locations are
user-controlled separately.

.. code-block:: python

   loc = CONF.get_location('normal_opt').location
   if loc.is_user_controlled:
      print('normal_opt was set by the user')
   else:
      print('normal_opt was set by the application')
