# Copyright 2011 GovData Project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Asynchronous Python driver for MongoDB."""

from apymongo.connection import Connection as APyMongo_Connection

from consts import ASCENDING
from consts import DESCENDING
from consts import GEO2D

"""Index specifier for a 2-dimensional `geospatial index`_.

.. versionadded:: 1.5.1

.. note:: Geo-spatial indexing requires server version **>= 1.3.3+**.

.. _geospatial index: http://www.mongodb.org/display/DOCS/Geospatial+Indexing
"""

GEOHAYSTACK = "geoHaystack"
"""Index specifier for a 2-dimensional `haystack index`_.

.. versionadded:: 2.1

.. note:: Geo-spatial indexing requires server version **>= 1.5.6+**.

.. _geospatial index: http://www.mongodb.org/display/DOCS/Geospatial+Haystack+Indexing
"""


OFF = 0
"""No database profiling."""
SLOW_ONLY = 1
"""Only profile slow operations."""
ALL = 2
"""Profile all operations."""

version_tuple = (2, 1, 1, 1, '+')

def get_version_string():
    if version_tuple[-1] == '+':
        return '.'.join(map(str, version_tuple[:-1])) + '+'
    return '.'.join(map(str, version_tuple))

version = get_version_string()
"""Current version of PyMongo."""

from apymongo.connection import Connection
# from apymongo.replica_set_connection import ReplicaSetConnection

def has_c():
    """Is the C extension installed?
    
    .. versionadded:: 1.5
    """
    try:
        from apymongoo import _cmessage
        return True
    except ImportError:
        return False