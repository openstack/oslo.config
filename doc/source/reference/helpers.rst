----------------
Helper Functions
----------------

Showing detailed locations for configuration settings
-----------------------------------------------------

``oslo.config`` can track the location in application and library code
where an option is defined, defaults are set, or values are
overridden. This feature is disabled by default because it is
expensive and incurs a significant performance penalty, but it can be
useful for developers tracing down issues with configuration option
definitions.

To turn on detailed location tracking, set the environment variable
``OSLO_CONFIG_SHOW_CODE_LOCATIONS`` to any non-empty value (for
example, ``"1"`` or ``"yes, please"``) before starting the
application, test suite, or script. Then use
:func:`ConfigOpts.get_location` to access the location data for the
option.
