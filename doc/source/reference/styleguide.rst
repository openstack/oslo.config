----------------------------
Style Guide for Help Strings
----------------------------

This document provides style guidance for writing the required help
strings for configuration options using the ``oslo.config`` code.

The help strings are parsed from the code to appear in sample
configuration files, such as ``etc/cinder/cinder.conf`` in the
cinder repository. They are also displayed in the `OpenStack
Configuration Reference
<https://docs.openstack.org/oslo.config/latest/reference/index.html>`_.

Examples::

    cfg.StrOpt('bind_host',
               default='0.0.0.0',
               help='IP address to listen on.'),
    cfg.PortOpt('bind_port',
                default=9292,
                help='Port number to listen on.')


Style Guide
-----------

1. Use sentence-style capitalization for help strings: Capitalize or
   uppercase the first character (see the examples above).

2. Only use single spaces, no double spaces.

3. Properly capitalize words. If in doubt check the `OpenStack Glossary <https://docs.openstack.org/oslo.config/latest/reference/styleguide.html#style-guide>`_.

4. End each segment with a period and write complete sentences if
   possible. Examples::

     cfg.StrOpt('osapi_volume_base_URL',
                default=None,
                help='Base URL that appears in links to the OpenStack '
                     'Block Storage API.')


     cfg.StrOpt('host',
                default=socket.gethostname(),
                help='Name of this node. This can be an opaque identifier. '
                     'It is not necessarily a host name, FQDN, or IP address.')

5. Use valid service names and API names. Valid service names include
   nova, cinder, swift, glance, heat, neutron, trove, ceilometer,
   horizon, keystone, and marconi.

   Valid API names include Compute API, Image Service API, Identity
   Service API, Object Storage API, Block Storage API, Database API,
   and Networking API.

Format
------

1. For multi-line strings, remember that strings are concatenated
   directly and thus spaces need to be inserted normally.

   This document recommends to add the space at the end of a line and
   not at the beginning. Example::

     cfg.BoolOpt('glance_api_ssl_compression',
                 default=False,
                 help='Enables or disables negotiation of SSL layer '
                      'compression. In some cases disabling compression '
                      'can improve data throughput, such as when high '
                      'network bandwidth is available and you use '
                      'compressed image formats like qcow2.')

2. It is possible to preformat the multi-line strings to increase readability.
   Line break characters ``\n`` will be kept as they are used in the help text.
   Example::

     cfg.IntOpt('sync_power_state_interval',
                default=600,
                help='Interval to sync power states between the database and '
                     'the hypervisor.\n'
                     '\n'
                     '-1: disables the sync \n'
                     ' 0: run at the default rate.\n'
                     '>0: the interval in seconds')
