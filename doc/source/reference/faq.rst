============================
 Frequently Asked Questions
============================

Why does oslo.config have a CONF object? Global objects SUCK!
=============================================================

.. original source: https://wiki.openstack.org/wiki/Oslo#Why_does_oslo.config_have_a_CONF_object.3F_Global_object_SUCK.21

Indeed. Well, it's a long story and well documented in mailing list
archives if anyone cares to dig up some links.

Around the time of the Folsom Design Summit, an attempt was made to
remove our dependence on a global object like this. There was massive
debate and, in the end, the rough consensus was to stick with using
this approach.

Nova, through its use of the gflags library, used this approach from
`commit zero
<https://github.com/openstack/nova/blob/bf6e6e7/nova/flags.py#L27>`__. Some
OpenStack projects didn't initially use this approach, but most now
do. The idea is that having all projects use the same approach is more
important than the objections to the approach. Sharing code between
projects is great, but by also having projects use the same idioms for
stuff like this it makes it much easier for people to work on multiple
projects.

This debate will probably never completely go away, though. See `this
latest discussion in August, 2014
<http://lists.openstack.org/pipermail/openstack-dev/2014-August/044050.html>`__

Why are configuration options not part of a library's API?
==========================================================

Configuration options are a way for deployers to change the behavior
of OpenStack. Applications are not supposed to be aware of the
configuration options defined and used within libraries, because the
library API is supposed to work transparently no matter which backend
is configured.

Configuration options in libraries can be renamed, moved, and
deprecated just like configuration options in applications. However,
if applications are allowed to read or write the configuration options
directly, treating them as an API, the option cannot be renamed
without breaking the application. Instead, libraries should provide a
programmatic API (usually a :func:`set_defaults` function) for setting
the defaults for configuration options. For example, this function
from ``oslo.log`` lets the caller change the format string and default
logging levels:

::

    def set_defaults(logging_context_format_string=None,
                     default_log_levels=None):
        """Set default values for the configuration options used by oslo.log."""
        # Just in case the caller is not setting the
        # default_log_level. This is insurance because
        # we introduced the default_log_level parameter
        # later in a backwards in-compatible change
        if default_log_levels is not None:
            cfg.set_defaults(
                _options.log_opts,
                default_log_levels=default_log_levels)
        if logging_context_format_string is not None:
            cfg.set_defaults(
                _options.log_opts,
                logging_context_format_string=logging_context_format_string)

If the name of either option changes, the API of :func:`set_defaults`
can be updated to allow both names, and warn if the old one is
provided. Using a supported API like this is better than having an
application call :func:`set_default` on the configuration object
directly, such as:

::

    cfg.CONF.set_default('default_log_levels', default_log_levels)

This form will trigger an error if the logging options are moved out
of the default option group into their own section of the
configuration file. It will also fail if the ``default_log_levels``
option is not yet registered, or if it is renamed. All of those cases
can be protected against with a :func:`set_defaults` function in the
library that owns the options.

Similarly, code that does not *own* the configuration option
definition should not read the option value. An application should
never, for example, do something like:

::

    log_file = cfg.CONF.log_file

The type, name, and existence of the ``log_file`` configuration option
is subject to change. ``oslo.config`` makes it easy to communicate
that change to a deployer in a way that allows their old configuration
files to continue to work. It has no mechanism for doing that in
application code, however.
