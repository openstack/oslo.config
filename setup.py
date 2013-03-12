#!/usr/bin/python

# Copyright 2013 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import setuptools

from magic.openstack.common import setup

package = 'oslo.config'
version = '1.1.1'

requires = setup.parse_requirements()
depend_links = setup.parse_dependency_links()
tests_require = setup.parse_requirements(['tools/test-requires'])


setuptools.setup(
    name=package,
    version=setup.get_version(package, version),
    description='Oslo configuration API',
    long_description='The Oslo configuration API supports parsing command '
                     'line arguments and .ini style configuration files.',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: OpenStack',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6', ],
    author='OpenStack',
    author_email='openstack-dev@lists.openstack.org',
    url='http://www.openstack.org/',
    license='Apache Software License',
    packages=['oslo', 'oslo.config'],
    namespace_packages=['oslo'],
    cmdclass=setup.get_cmdclass(),
    install_requires=requires,
    tests_require=tests_require,
    dependency_links=depend_links,
)
