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

To generate multiple files, set ``config_generator_config_file`` to a
list of tuples containing the input filename and the base name for the
output file.

The output value can be ``None``, in which case the name is taken from
the input value.

The input name can be an full path or a value relative to the
documentation source directory.

For example::

  config_generator_config_file = [
      ('../../etc/glance-api.conf', 'api'),
      ('../../etc/glance-cache.conf', 'cache'),
      ('../../etc/glance-glare.conf', None),
      ('../../etc/glance-registry.conf', None),
      ('../../etc/glance-scrubber.conf', None),
  ]

Produces the output files ``api.conf.sample``, ``cache.conf.sample``,
``glance-glare.conf.sample``, ``glance-registry.conf.sample``, and
``glance-scrubber.conf.sample``.

Output File Name
----------------

By default the sphinx plugin will generate the sample config file and
name the file ``sample.config``. However, if for whatever reason you'd
like the name to be more specific to the project name you can use the
``sample_config_basename`` config option to specify the project
name. If it's set the output filename will be that value with a
``.conf.sample`` extension. For example if you set the value to
"``nova``" the output filename will be "``nova.conf.sample``". You can
also include a subdirectory off of the documentation source directory
as part of this value.
