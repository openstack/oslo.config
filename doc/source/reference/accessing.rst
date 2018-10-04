======================================
 Accessing Option Values In Your Code
======================================

Option values in the default group are referenced as attributes/properties on
the config manager; groups are also attributes on the config manager, with
attributes for each of the options associated with the group:

.. code-block:: python

    server.start(app, conf.bind_port, conf.bind_host, conf)

    self.connection = kombu.connection.BrokerConnection(
        hostname=conf.rabbit.host,
        port=conf.rabbit.port,
        ...)
