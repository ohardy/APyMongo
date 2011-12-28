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

OFF = 0
"""No database profiling."""
SLOW_ONLY = 1
"""Only profile slow operations."""
ALL = 2
"""Profile all operations."""

# Remember to change in setup.py as well!
version = "0.0.1"
"""Current version of PyMongo."""

Connection = APyMongo_Connection
"""Alias for :class:`apymongo.connection.Connection`."""


def has_c():
    """Is the C extension installed?
    
    .. versionadded:: 1.5
    """
    try:
        from pymongo import _cmessage
        return True
    except ImportError:
        return False