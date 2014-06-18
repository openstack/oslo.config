oslo.config
===========

An OpenStack library for parsing configuration options from the command
line and configuration files.

Contents
========

.. toctree::
   :maxdepth: 2

   cfg
   opts
   types
   configopts
   helpers
   parser
   exceptions
   styleguide
   generator

Release Notes
=============

1.2.0
-----

* 1223667_: Fix DictOpt to split only the first colon
* 1228995_: Disallow duplicate keys in DictOpt
* Explicit version removed from setup.cfg
* Dependency version updates

.. _1223667: https://bugs.launchpad.net/oslo/+bug/1223667
.. _1228995: https://bugs.launchpad.net/oslo/+bug/1228995

1.2.0a4
-------

* Add auto-create support for OptGroup instances (see review 41865_)
* Publish full API docs to docs.openstack.org_
* Finished Python 3 support
* 1196601_: Raise an exception if print_help() is called before __call__
* Fix DeprecatedOpt equality test
* Use oslo.sphinx

.. _41865: https://review.openstack.org/41865
.. _1196601: https://bugs.launchpad.net/oslo/+bug/1196601
.. _docs.openstack.org:  http://docs.openstack.org/developer/oslo.config/

1.2.0a3
-------

* 1176817_: Fix the priority of CLI args vs config file values
* 1123043_: New 'choices' param to StrOpt constructor
* cfg-reload-config-files_: Add new ConfigOpts.reload_config_files() method
* 1194742_: Fix regression which meant we weren't registering our namespace package
* 1185959_: Make --help output order alphabetical
* More progress on python3 support
* Fix obscure cache clearing race condition
* Move from tools/pip-requires to requirements.txt
* Include missing .testr.conf in dist tarball

.. _1176817: https://bugs.launchpad.net/oslo/+bug/1176817
.. _1123043: https://bugs.launchpad.net/oslo/+bug/1123043
.. _cfg-reload-config-files: https://blueprints.launchpad.net/oslo/+spec/cfg-reload-config-files
.. _1194742: https://bugs.launchpad.net/oslo/+bug/1194742
.. _1185959: https://bugs.launchpad.net/oslo/+bug/1185959

1.2.0a2
-------

* Fix MultiConfigParser API breakage in 1.2.0a1

1.2.0a1
-------

* Solid progress has been made adding Python 3 support.
* cfg-lowercase-groups_: uppercase section names in config files are now normalized to lowercase.
* Support has been added for dictionary style options with the ``DictOpt`` class.
* Multiple deprecated option names per option are now supported via the ``deprecated_opts`` argument.
* The package build process now uses pbr_.
* The package tests are now run using testr_.
* The package coding style checks are now performed using hacking_.

.. _cfg-lowercase-groups: https://blueprints.launchpad.net/oslo/+spec/cfg-lowercase-groups
.. _pbr: http://docs.openstack.org/developer/pbr/
.. _testr: https://wiki.openstack.org/wiki/Testr
.. _hacking: https://pypi.python.org/pypi/hacking

1.1.1
-----

* 1160922_: Fix set_defaults() to handle multiple arguments
* 1175096_: Fix the title argument to ``OptGroup``

.. _1160922: https://bugs.launchpad.net/oslo/+bug/1160922
.. _1175096: https://bugs.launchpad.net/oslo/+bug/1175096

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

