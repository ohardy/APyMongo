import struct

def _partition(source, sub):
    """Our own string partitioning method.

    Splits `source` on `sub`.
    """
    i = source.find(sub)
    if i == -1:
        return (source, None)
    return (source[:i], source[i + len(sub):])


def _str_to_node(string, default_port=27017):
    """Convert a string to a node tuple.

    "localhost:27017" -> ("localhost", 27017)
    """
    (host, port) = _partition(string, ":")
    if port:
        port = int(port)
    else:
        port = default_port
    return (host, port)


def _parse_uri(uri, default_port=27017):
    """MongoDB URI parser.
    """

    if uri.startswith("mongodb://"):
        uri = uri[len("mongodb://"):]
    elif "://" in uri:
        raise InvalidURI("Invalid uri scheme: %s" % _partition(uri, "://")[0])

    (hosts, namespace) = _partition(uri, "/")

    raw_options = None
    if namespace:
        (namespace, raw_options) = _partition(namespace, "?")
        if namespace.find(".") < 0:
            db = namespace
            collection = None
        else:
            (db, collection) = namespace.split(".", 1)
    else:
        db = None
        collection = None

    username = None
    password = None
    if "@" in hosts:
        (auth, hosts) = _partition(hosts, "@")

        if ":" not in auth:
            raise InvalidURI("auth must be specified as "
                             "'username:password@'")
        (username, password) = _partition(auth, ":")

    host_list = []
    for host in hosts.split(","):
        if not host:
            raise InvalidURI("empty host (or extra comma in host list)")
        host_list.append(_str_to_node(host, default_port))

    options = {}
    if raw_options:
        and_idx = raw_options.find("&")
        semi_idx = raw_options.find(";")
        if and_idx >= 0 and semi_idx >= 0:
            raise InvalidURI("Cannot mix & and ; for option separators.")
        elif and_idx >= 0:
            options = dict([kv.split("=") for kv in raw_options.split("&")])
        elif semi_idx >= 0:
            options = dict([kv.split("=") for kv in raw_options.split(";")])
        elif raw_options.find("="):
            options = dict([raw_options.split("=")])


    return (host_list, db, username, password, collection, options)


def receive_body_on_stream(operation, request_id, strm, callback, header):
    length = struct.unpack("<i", header[:4])[0]
    assert request_id == struct.unpack("<i", header[8:12])[0], \
        "ids don't match %r %r" % (request_id,
                                   struct.unpack("<i", header[8:12])[0])
    assert operation == struct.unpack("<i", header[12:])[0]

    strm.read_bytes(length - 16, callback)
