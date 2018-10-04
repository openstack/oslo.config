===================
 Global ConfigOpts
===================

This module also contains a global instance of the ConfigOpts class
in order to support a common usage pattern in OpenStack:

.. code-block:: python

    from oslo_config import cfg

    opts = [
        cfg.StrOpt('bind_host', default='0.0.0.0'),
        cfg.PortOpt('bind_port', default=9292),
    ]

    CONF = cfg.CONF
    CONF.register_opts(opts)

    def start(server, app):
        server.start(app, CONF.bind_port, CONF.bind_host)
