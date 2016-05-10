====================================
Sphinx Oslo Sample Config Generation
====================================

Included with oslo.config is a sphinx extension to generate a sample config
file at the beginning of each sphinx build. To activate the extension add
``oslo_config.sphinxconfiggen`` to the list of extensions in your sphinx
``conf.py``.

Then you just need to use the ``config_generator_config_file`` option to point
the config generator at the config file which tells it how to generate the
sample config. If one isn't specified or it doesn't point to a real file the
sample config file generation will be skipped.

Output File Name
----------------

By default the sphinx plugin will generate the sample config file and name the
file sample.config. However, if for whatever reason you'd like the name to be
more specific to the project name you can use the ``sample_config_basename``
config option to specify the project name. If it's set the output filename
will be that value with a .conf.sample extension. For example if you set that
to be nova the output filename will be nova.conf.sample. You can also put a
subdirectory off of the srcdir as part of this value.
