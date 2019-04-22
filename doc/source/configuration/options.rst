========================================
 Configuration Options from oslo.config
========================================

When loading values from the sources defined by the following options, the
precedence is as follows:

#. Command Line
#. Environment Variables
#. Config Files from ``--config-dir`` [1]_
#. Config Files from ``--config-file``
#. Pluggable Config Sources

If a value is specified in multiple locations, the location used will be the
one higher in the list. For example, if a value is specified both on the
command line and in an environment variable, the value from the command line
will be the one returned.

.. [1] Files in a config dir are parsed in alphabetical order. Later files
       take precedence over earlier ones.

.. show-options::

   oslo.config
