======================
 Command Line Options
======================

Positional Command Line Arguments
---------------------------------

Positional command line arguments are supported via a 'positional' Opt
constructor argument:

.. code-block:: console

    >>> conf = cfg.ConfigOpts()
    >>> conf.register_cli_opt(cfg.MultiStrOpt('bar', positional=True))
    True
    >>> conf(['a', 'b'])
    >>> conf.bar
    ['a', 'b']

Sub-Parsers
-----------

It is also possible to use argparse "sub-parsers" to parse additional
command line arguments using the SubCommandOpt class:

.. code-block:: console

    >>> def add_parsers(subparsers):
    ...     list_action = subparsers.add_parser('list')
    ...     list_action.add_argument('id')
    ...
    >>> conf = cfg.ConfigOpts()
    >>> conf.register_cli_opt(cfg.SubCommandOpt('action', handler=add_parsers))
    True
    >>> conf(args=['list', '10'])
    >>> conf.action.name, conf.action.id
    ('list', '10')
