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
   cfgfilter
   helpers
   fixture
   parser
   exceptions
   namespaces
   styleguide
   generator
   contributing

Release Notes
=============

1.4.0.0a2
---------

Dependency changes:

* netaddr (0.7.6) is required.
* stevedore (0.14) is required.

New features/APIs:

* A new oslo-config-generator_ utility for generating sample
  configuration files.
* A ConfigFilter_ wrapper class to allow controlling the visibilty of
  private configuration options.
* 1284684_: Add new cfg.IPOpt type.

Bugfixes:

* Add CLI option support to config fixture.

Cleanups:

* Replaced 'e.g.' with 'for example'.
* Fix confusing logic in _Namespace._get_cli_value().
* Changes imports order to pass H305, enables check.

Docs:

* Fix typos some method parameter docs.

.. _oslo-config-generator: http://docs.openstack.org/developer/oslo.config/generator.html
.. _ConfigFilter: http://docs.openstack.org/developer/oslo.config/cfgfilter.html
.. _1284684: https://code.launchpad.net/bugs/1284684

Thanks to Christian Berendt, David Stanek, Jakub Libosvar, liu-sheng
Mark McLoughlin and Petr Blaho for their contributions to this release.

1.4.0.0a1
---------

Dependency changes:

* Newer six (1.7.0, previously 1.5.2)
* Newer hacking (0.9.1, previously 0.8.0)
* Newer versions of oslo.sphinx 1.2.x are supported.

New features/APIs:

* New `test fixture`_ for configuration options.

Bug fixes:

* Add warning about interpolating values from groups
* 1284969_: Reject option names prefixed with '_'
* 1284969_: Avoid using too generic names in _Namespace.
* 1283960_: Fix deprecated_opts for cli options
* 1329478_: Fix an issue with validating max integer values.

Cleanups:

* 1321274_: Log string format arguments changed to function parameters.
* 1331449_: Remove print statement from types.Dict

Python 3:

* Fix test_version on Python 3.4

Tests:

* 1279973_: Add test case for hyphenated option names.
* Add more tests for positional CLI opts.
* Import run_cross_tests.sh from oslo-incubator.
* Move py33 env before py2x

Docs:

* Add section titles and fix markup of docstring.
* Add a doc sample for how to use the required field
* Fix docstring for _Namespace._get_cli_value

.. _test fixture: http://docs.openstack.org/developer/oslo.config/generator.html
.. _1279973: https://code.launchpad.net/bugs/1279973
.. _1283960: https://code.launchpad.net/bugs/1283960
.. _1284969: https://code.launchpad.net/bugs/1284969
.. _1321274: https://code.launchpad.net/bugs/1321274
.. _1329478: https://code.launchpad.net/bugs/1329478
.. _1331449: https://code.launchpad.net/bugs/1331449

Thanks to Ben Nemec, Christian Berendt, Cyril Roelandt,
Davanum Srinivas, David Stanek, Doug Hellmann, Mark McLoughlin,
Matthew Treinish, Radomir Dopieralski and YAMAMOTO Takashi for their
contributions to this release.

1.3.0
-----

Dependency changes:

* Newer six (1.5.2, previously unspecified version)
* Newer hacking  (0.8.0, previously 0.5.6)
* oslotest (unspecified) and mock (1.0) are now required
* Newer testtools (0.9.34, was 0.9.32), testrepository (0.0.18)
  and python-subunit (0.0.18)
* sphinx 1.2 or later is not supported
* oslo.sphinx has been renamed to oslosphinx

New features/APIs:

* Support for `custom option types`_.
* 1262148_: Added support of operator '==' to cfg.Opt.
* Add the ability to validate default options value.

Bugfixes:

* 1282250_: Do substitution on overrides and defaults too.
* 1255354_: Throw exception if --config-dir doesn't exist.
* 1259729_: Fix for parsing error with Dollar Sign ($) in values.
* 1244674_: Fix to make ConfigOpts no longer obscure IOErrors

Python 3:

* Support building wheels (PEP-427).

Docs:

* Fix docstring of parsing order.
* 1277168_: Switch over to oslosphinx.
* Add Style Guide for help of config options

Tests:

* Convert to oslo.test.

Cleanups:

* Include the 'meta' trove classifiers for python versions.
* Follow style guide for help strings.
* Add py33 trove classifier.
* Fix a whitespace in a comment.
* 1229324_: Remove extraneous vim configuration comments.
* 1257295_: Fix some misspellings.
* 1262424_: Remove copyright from empty files.
* Fix spelling errors in docstrings and comments.
* Utilizes assertIsNone and assertIsNotNone.
* Replace assertEquals with assertEqual.

.. _`custom option types`: http://docs.openstack.org/developer/oslo.config/types.html
.. _1229324: https://code.launchpad.net/bugs/1229324
.. _1244674: https://code.launchpad.net/bugs/1244674
.. _1255354: https://code.launchpad.net/bugs/1255354
.. _1257295: https://code.launchpad.net/bugs/1257295
.. _1259729: https://code.launchpad.net/bugs/1259729
.. _1262148: https://code.launchpad.net/bugs/1262148
.. _1262424: https://code.launchpad.net/bugs/1262424
.. _1277168: https://code.launchpad.net/bugs/1277168
.. _1282250: https://code.launchpad.net/bugs/1282250

Thanks to Alex Gaynor, Andreas Jaeger, Ben Nemec, Davanum Srinivas,
Dirk Mueller, Doug Hellmann, Eric Guo, Jay S. Bryant, Jonathan LaCour,
Julien Danjou, Lars Butler, Lianhao Lu, llg8212, Maxim Kulkin, Sascha
Peilicke, Shane Wang, skudriashev, YAMAMOTO Takashi and Zhongyue Luo
for their contributions to this release.

1.2.1
-----

bf70519 Fix subparsers add_parser() regression
3d59667 Expand DeprecatedOpt documentation

Thanks to Ian Wienand and Mark McLoughlin for their contributions to
this relase.

1.2.0
-----

* 1223667_: Fix DictOpt to split only the first colon
* 1228995_: Disallow duplicate keys in DictOpt
* Explicit version removed from setup.cfg
* Dependency version updates

.. _1223667: https://bugs.launchpad.net/oslo/+bug/1223667
.. _1228995: https://bugs.launchpad.net/oslo/+bug/1228995

Thanks to Julien Danjou, Mark McLoughlin and Zhongyue Luo for their
contributions to this release.

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
.. _docs.openstack.org: http://docs.openstack.org/developer/oslo.config/

Thanks to Davanum Srinivas, Doug Hellmann, Flavio Percoco, Julien
Danjou, Luis A. Garcia, Mark McLoughlin, Sergey Lukjanov and Zhongyue
Luo for their contributions to this release.

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

Thanks to Chuck Short, Davanum Srinivas, Dirk Mueller, Fengqian.Gao,
Mark McLoughlin, Monty Taylor, Sergey Lukjanov and Zhongyue Luo for
their contributions to this release.

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

Thanks to Chuck Short, Davanum Srinivas, Dirk Mueller, James E. Blair,
Mark McLoughlin, Monty Taylor, Steven Deaton and Zhongyue Luo for
their contributions to this release.

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

