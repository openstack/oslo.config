=============================
 Loading Configuration Files
=============================

The config manager has two CLI options defined by default, ``--config-file``
and ``--config-dir``:

.. code-block:: python

    class ConfigOpts(object):

        def __call__(self, ...):

            opts = [
                MultiStrOpt('config-file',
                        ...),
                StrOpt('config-dir',
                       ...),
            ]

            self.register_cli_opts(opts)

Option values are parsed from any supplied config files using
oslo_config.iniparser. If none are specified, a default set is used
for example glance-api.conf and glance-common.conf:

.. code-block:: text

    glance-api.conf:
      [DEFAULT]
      bind_port = 9292

    glance-common.conf:
      [DEFAULT]
      bind_host = 0.0.0.0

Lines in a configuration file should not start with whitespace. A
configuration file also supports comments, which must start with '#' or ';'.
Option values in config files and those on the command line are parsed
in order. The same option (includes deprecated option name and current
option name) can appear many times, in config files or on the command line.
Later values always override earlier ones.

The order of configuration files inside the same configuration directory is
defined by the alphabetic sorting order of their file names. Files in a
configuration directory are parsed after any individual configuration files,
so values that appear in both a configuration file and configuration directory
will use the value from the directory.

The parsing of CLI args and config files is initiated by invoking the config
manager for example:

.. code-block:: python

    conf = cfg.ConfigOpts()
    conf.register_opt(cfg.BoolOpt('verbose', ...))
    conf(sys.argv[1:])
    if conf.verbose:
        ...

Option Value Interpolation
--------------------------

Option values may reference other values using PEP 292 string substitution:

.. code-block:: python

    opts = [
        cfg.StrOpt('state_path',
                   default=os.path.join(os.path.dirname(__file__), '../'),
                   help='Top-level directory for maintaining nova state.'),
        cfg.StrOpt('sqlite_db',
                   default='nova.sqlite',
                   help='File name for SQLite.'),
        cfg.StrOpt('sql_connection',
                   default='sqlite:///$state_path/$sqlite_db',
                   help='Connection string for SQL database.'),
    ]

.. note::

  Interpolation can be avoided by using `$$`.

.. note::

  You can use `.` to delimit option from other groups, e.g.
  ${mygroup.myoption}.
