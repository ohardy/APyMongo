class ReadPreference:
    """An enum that defines the read preferences supported by PyMongo.

    +----------------------+--------------------------------------------------+
    |    Connection type   |                 Read Preference                  |
    +======================+================+================+================+
    |                      |`PRIMARY`       |`SECONDARY`     |`SECONDARY_ONLY`|
    +----------------------+----------------+----------------+----------------+
    |Connection to a single|Queries are     |Queries are     |Same as         |
    |host.                 |allowed if the  |allowed if the  |`SECONDARY`     |
    |                      |connection is to|connection is to|                |
    |                      |the replica set |the replica set |                |
    |                      |primary.        |primary or a    |                |
    |                      |                |secondary.      |                |
    +----------------------+----------------+----------------+----------------+
    |Connection to a       |Queries are sent|Queries are     |Same as         |
    |mongos.               |to the primary  |distributed     |`SECONDARY`     |
    |                      |of a shard.     |among shard     |                |
    |                      |                |secondaries.    |                |
    |                      |                |Queries are sent|                |
    |                      |                |to the primary  |                |
    |                      |                |if no           |                |
    |                      |                |secondaries are |                |
    |                      |                |available.      |                |
    |                      |                |                |                |
    +----------------------+----------------+----------------+----------------+
    |ReplicaSetConnection  |Queries are sent|Queries are     |Queries are     |
    |                      |to the primary  |distributed     |never sent to   |
    |                      |of the replica  |among replica   |the replica set |
    |                      |set.            |set secondaries.|primary. An     |
    |                      |                |Queries are sent|exception is    |
    |                      |                |to the primary  |raised if no    |
    |                      |                |if no           |secondary is    |
    |                      |                |secondaries are |available.      |
    |                      |                |available.      |                |
    |                      |                |                |                |
    +----------------------+----------------+----------------+----------------+
    """

    PRIMARY = 0
    SECONDARY = 1
    SECONDARY_ONLY = 2
