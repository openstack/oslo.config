====================
 Option Deprecation
====================

If you want to rename some options, move them to another group or remove
completely, you may change their declarations using `deprecated_name`,
`deprecated_group`  and `deprecated_for_removal` parameters to the :class:`Opt`
constructor:

.. code-block:: python

    from oslo_config import cfg

    conf = cfg.ConfigOpts()

    opt_1 = cfg.StrOpt('opt_1', default='foo', deprecated_name='opt1')
    opt_2 = cfg.StrOpt('opt_2', default='spam', deprecated_group='DEFAULT')
    opt_3 = cfg.BoolOpt('opt_3', default=False, deprecated_for_removal=True)

    conf.register_opt(opt_1, group='group_1')
    conf.register_opt(opt_2, group='group_2')
    conf.register_opt(opt_3)

    conf(['--config-file', 'config.conf'])

    assert conf.group_1.opt_1 == 'bar'
    assert conf.group_2.opt_2 == 'eggs'
    assert conf.opt_3

Assuming that the file config.conf has the following content:

.. code-block:: ini

    [group_1]
    opt1 = bar

    [DEFAULT]
    opt_2 = eggs
    opt_3 = True

the script will succeed, but will log three respective warnings about the
given deprecated options.

There are also `deprecated_reason` and `deprecated_since` parameters for
specifying some additional information about a deprecation.

All the mentioned parameters can be mixed together in any combinations.
