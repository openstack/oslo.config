==========================
 oslo.config Quick Start!
==========================

Are you brand new to oslo.config? This brief tutorial will get you started
understanding some of the fundamentals.

Prerequisites
-------------
* A plain text editor or Python-enabled IDE
* A Python interpreter
* A command shell from which the interpreter can be invoked
* The oslo_config library in your Python path.

Test Script
-----------
Put this in a file called ``oslocfgtest.py``.

.. code:: python

  # The sys module lets you get at the command line arguments.
  import sys

  # Load up the cfg module, which contains all the classes and methods
  # you'll need.
  from oslo_config import cfg

  # Define an option group
  grp = cfg.OptGroup('mygroup')

  # Define a couple of options
  opts = [cfg.StrOpt('option1'),
          cfg.IntOpt('option2', default=42)]

  # Register your config group
  cfg.CONF.register_group(grp)

  # Register your options within the config group
  cfg.CONF.register_opts(opts, group=grp)

  # Process command line arguments.  The arguments tell CONF where to
  # find your config file, which it loads and parses to populate itself.
  cfg.CONF(sys.argv[1:])

  # Now you can access the values from the config file as
  # CONF.<group>.<opt>
  print("The value of option1 is %s" % cfg.CONF.mygroup.option1)
  print("The value of option2 is %d" % cfg.CONF.mygroup.option2)

Conf File
---------
Put this in a file called ``oslocfgtest.conf`` in the same directory as
``oslocfgtest.py``.

.. code:: ini

  [mygroup]
  option1 = foo
  # Comment out option2 to test the default value
  # option2 = 123

Run It!
-------
From your command shell, in the same directory as your script and conf, invoke:

.. code:: shell

  python oslocfgtest.py --config-file oslocfgtest.conf

Revel in the output being exactly as expected.  If you've done everything
right, you should see:

.. code:: shell

  The value of option1 is foo
  The value of option2 is 42

Now go play with some more advanced option settings!
