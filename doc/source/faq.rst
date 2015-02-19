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
