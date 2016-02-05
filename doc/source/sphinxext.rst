====================
 Sphinx Integration
====================

The ``oslo_config.sphinxext`` module defines a custom domain for
documenting configuration options. The domain includes a directive and
two roles.

.. rst:directive:: show-options

   Given a list of namespaces, show all of the options exported from
   them.

   ::

       .. show-options::

          oslo.config
          oslo.log

   To show each namespace separately, add the ``split-namespaces``
   flag.

   ::

       .. show-options::
          :split-namespaces:

          oslo.config
          oslo.log

.. rst:role:: option

   Link to an option.

   ::

     #. :oslo.config:option:`config_file`
     #. :oslo.config:option:`DEFAULT.config_file`

   #. :oslo.config:option:`config_file`
   #. :oslo.config:option:`DEFAULT.config_file`

.. rst:role:: group

   Link to an option group.

   ::

     :oslo.config:group:`DEFAULT`

   :oslo.config:group:`DEFAULT`
