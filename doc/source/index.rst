oslo.config
===========

An OpenStack library for parsing configuration options from the command
line and configuration files.

Contents
--------

.. toctree::
   :maxdepth: 1

   api/autoindex

Release Notes
=============

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

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

