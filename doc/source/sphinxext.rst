====================
 Sphinx Integration
====================

The ``oslo_config.sphinxext`` module defines a custom domain for
documenting configuration options. The domain includes a directive and
two roles.

.. rst:directive:: show-options

   Given a namespace, show all of the options exported from that
   namespace.

   ::

       .. show-options:: oslo.config

.. rst:role:: option

   Link to an option.

   ::

     :oslo.config:option:`config_file`
     :oslo.config:option:`DEFAULT.config_file`

.. rst:role:: group

   Link to an option group.

   ::

     :oslo.config:group:`DEFAULT`
