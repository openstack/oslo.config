----------------------------------------------
Choosing group names for configuration options
----------------------------------------------

Applications should use a meaningful name without a prefix. For Oslo
libraries, when naming groups for configuration options using the
name of the library itself instead of a descriptive name to help avoid
collisions. If the library name is namespaced then use '_' as a separator
in the group name.

For example, the ``oslo.log`` library should use ``oslo_log`` as the
group name.
