import os
import socket
import sys
import time
import threading
import weakref
import tornado
import functools
from datetime import timedelta
import Queue

have_ssl = True
try:
    import ssl
except ImportError:
    have_ssl = False


# APyMongo does not use greenlet-aware connection pools by default, but it will
# attempt to do so if you pass use_greenlets=True to Connection or
# ReplicaSetConnection
have_greenlet = True
try:
    import greenlet
except ImportError:
    have_greenlet = False

NO_REQUEST    = None
NO_SOCKET_YET = -1

if sys.platform.startswith('java'):
    from select import cpython_compatible_select as select
else:
    from select import select
    
def _closed(sock):
    """Return True if we know socket has been closed, False otherwise.
    """
    try:
        rd, _, _ = select([sock], [], [], 0)
    # Any exception here is equally bad (select.error, ValueError, etc.).
    except:
        return True
    return len(rd) > 0
    
class ConnectionFailure(Exception):
    pass

class ConnectionStream(object):
    """docstring for ConnectionStream"""
    def __init__(self, pool, stream=None):
        super(ConnectionStream, self).__init__()
        self.poolref             = weakref.ref(pool)
        self.usage_count      = 0
        self.stream           = stream
        self.last_checkout    = 0
        self.closed           = False

    def cache(self):
        """docstring for cache"""
        self.poolref().return_stream(self)

    def use(self, callback):
        """docstring for get"""
        self.usage_count += 1
        self.poolref().use(self)
        # def scallback(stream):
        #             """docstring for scallback"""
        #             if isinstance(stream, tornado.iostream.IOStream):
        #                 self.stream = stream
        #                 callback(self)
        #             else:
        #                 raise Exception('stream is %s' % (type(tornado.iostream.IOStream), ))
        # 
        #         if self.stream is None:
        #             self.factory(None, scallback)
        #         else:
        callback(self)

    def __del__(self):
        if not self.closed:
            # This stream was given out, but not explicitly returned. Perhaps
            # the socket was assigned to a thread local for a request, but the
            # request wasn't ended before the thread died. Reclaim the socket
            # for the pool.
            pool = self.poolref and self.poolref()
            if pool:
                # Return a copy of self rather than self -- the Python docs
                # discourage postponing deletion by adding a reference to self.
                copy = ConnectionStream(pool, stream=self.stream)
                pool.return_stream(copy)
            else:
                # Close socket now rather than awaiting garbage collector
                self.close()

    def close(self):
        """docstring for close"""
        self.stream.close()
        self.closed = True

    def write(self, *args, **kwargs):
        """docstring for write"""
        self.stream.write(*args, **kwargs)
        # try:
        #             self.stream.write(*args, **kwargs)
        #         except IOError as e:
        #             print e
        #             self.close()
        #         except Exception as e:
        #             print e
        #             raise

    def read_bytes(self, *args, **kwargs):
        """docstring for read_bytes"""
        # try:
        self.stream.read_bytes(*args, **kwargs)
        # except Exception as e:
            # print e
            # self.close()
            
    def __eq__(self, other):
        return hasattr(other, 'stream') and self.stream == other.stream

    def __hash__(self):
        return hash(self.stream)
    

class ConnectionStreamPool(object):
    """Connection Pool to a single mongo instance.

    :Parameters:
      - `mincached` (optional): minimum connections to open on instantiation. 0 to open connections on first use
      - `maxcached` (optional): maximum inactive cached connections for this pool. 0 for unlimited
      - `maxconnections` (optional): maximum open connections for this pool. 0 for unlimited
      - `maxusage` (optional): number of requests allowed on a connection before it is closed. 0 for unlimited
      - `dbname`: mongo database name
      - `slave_okay` (optional): is it okay to connect directly to and perform queries on a slave instance
      - `**kwargs`: passed to `connection.Connection`

    """
    def __init__(self, pair, net_timeout, conn_timeout, use_ssl, io_loop, mincached=0, maxcached=0, maxusage=0, maxconnections=0):
        assert isinstance(maxconnections, int)
        self._maxconnections = maxconnections
        # self._condition      = Condition()
        # self._idle_cache     = []
        self.pair            = pair
        self._mincached      = maxcached
        self._maxcached      = maxcached
        self._maxusage       = maxusage
        self._maxconnections = maxconnections
        self._connections    = 0
        self.net_timeout = net_timeout
        self.conn_timeout = conn_timeout
        self.use_ssl = use_ssl
        self.lock = threading.Lock()
        self.lock1 = threading.Lock()
        self.lock2 = threading.Lock()
        self.lock3 = threading.Lock()
        self.lock4 = threading.Lock()
        self.io_loop = io_loop
        self.streams = set()
        self.waitings_callback = Queue.Queue()
        
    def reset(self):
        streams = None
        try:
            # Swapping variables is not atomic. We need to ensure no other
            # thread is modifying self.sockets, or replacing it, in this
            # critical section.
            self.lock.acquire()
            streams, self.streams = self.streams, set()
        finally:
            self.lock.release()

        for stream in streams: stream.close()
        
    def start_request(self):
        """docstring for start_request"""
        pass
    
    def _stream_close(self):
        """docstring for _socket_close"""
        pass
        
    def create_connection(self, pair, callback):
        """(Re-)connect to Mongo and return a new (connected) socket.

        Connect to the master if this is a paired connection.
        """
        # host, port = self.__host, self.__port
        
        # Don't try IPv6 if we don't support it.
        family = socket.AF_INET
        if socket.has_ipv6:
            family = socket.AF_UNSPEC
        
        if pair is not None:
            host, port = pair
        else:
            host, port = self.pair
            
        err = None
        stream = None
        for res in socket.getaddrinfo(host, port, family, socket.SOCK_STREAM):
            af, socktype, proto, dummy, sa = res
            sock = None
            try:
                # sock = socket.socket(af, socktype, proto)
                #                 sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                #                 sock.settimeout(self.conn_timeout or 20.0)
                #                 stream = tornado.iostream.IOStream(sock, self.io_loop)
                #                 stream.set_close_callback(self._socket_close)
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
                # sock = socket.socket(af, socktype, proto)
                print self.conn_timeout
                sock.settimeout(self.conn_timeout or 10.0)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                sock.setblocking(0)
                stream = tornado.iostream.IOStream(sock, self.io_loop)
                stream.set_close_callback(self._stream_close)
                break

            except socket.error, e:
                print e
                err = e
                if sock is not None:
                    sock.close()
        
        if stream is not None:
            def scallback():
                callback(ConnectionStream(self, stream))
            try:
                stream.connect((host, port), callback=scallback)
            except:
                callback(ConnectionFailure())
        else:
            callback(ConnectionFailure())
        
    def check_nb_cached(self):
        """docstring for check_nb_cached"""
        pass

    # def new_stream(self):
        # return ConnectionStream(self, self.create_connection)

    def stream(self, callback, pair=None):
        """ get a cached connection from the pool """
        if (self._maxconnections and self._connections >= self._maxconnections):
            #TODO: See if the pool can call waiting callbacks when pool free
            self.waitings_callback.put(callback)
            print 'too much, waiting : ', self.waitings_callback.qsize()
        else:
            # raise Exception("%d connections are already equal to the max: %d" % (self._connections, self._maxconnections))
        # connection limit not reached, get a dedicated connection
            try:
                # set.pop() isn't atomic in Jython, see
                # http://bugs.jython.org/issue1854
                self.lock1.acquire()
                stream = self.streams.pop()
            except:
                self.create_connection(pair, callback)
            else:
                self.io_loop.add_callback(functools.partial(self._check_closed, stream, pair, callback))
            finally:
                self.lock1.release()

            self._connections += 1

    def get_stream(self, callback):
        def mod_callback(stream):
            """docstring for callback"""
            if isinstance(stream, Exception):
                raise stream
            else:
                stream.use(callback)
                
        self.stream(mod_callback)
        
    def use(self, stream):
        """docstring for use"""
        try:
            self.streams.index(stream)
        except:
            pass
        else:
            self.streams.pop(index)
            
    def discard_stream(self, stream):
        """docstring for close_stream"""
        stream.close()
        try:
            self.streams.index(stream)
        except:
            pass
        else:
            self.streams.pop(index)

    def return_stream(self, strm):
        """Put a dedicated connection back into the idle cache."""
        if self._maxusage and strm.usage_count > self._maxusage:
            self._connections -=1
            logging.info('dropping connection %s uses past max usage %s' % (strm.usage_count, self._maxusage))
            strm.close()
            return
        self.lock3.acquire()
        if strm in self.streams:
            # called via socket close on a connection in the idle cache
            self.lock3.release()
            return
        try:
            if not self._maxcached or len(self.streams) < self._maxcached:
                if not self.waitings_callback.empty():
                    try:
                        # set.pop() isn't atomic in Jython, see
                        # http://bugs.jython.org/issue1854
                        # self.lock2.acquire()
                        callback = self.waitings_callback.get()
                        print 'waiting :', self.waitings_callback.qsize()
                    except:
                        # self.lock2.release()
                        self.streams.add(strm)
                        strm.last_checkout = time.time()
                    else:
                        # self.lock2.release()
                        print 'call callback : ', callback, ' with stream : ', strm
                        callback(strm)

                else:
                    # the idle cache is not full, so put it there
                    self.streams.add(strm)
                    strm.last_checkout = time.time()
            else: # if the idle cache is already full,
                logging.info('dropping connection. connection pool (%s) is full. maxcached %s' % (len(self.streams), self._maxcached))
                strm.close() # then close the connection
            # self.lock.notify()
        finally:
            self._connections -= 1
            self.lock3.release()

    def close(self):
        """Close all connections in the pool."""
        self._condition.acquire()
        try:
            while self.streams: # close all idle connections
                strm = self.streams.pop(0)
                try:
                    strm.close()
                except Exception:
                    pass
                self._connections -=1
            self._condition.notifyAll()
        finally:
            self._condition.release()
            
    def _check_closed(self, stream, pair, callback):
        """This side-effecty function checks if a socket has been closed by
        some external network error if it's been > 1 second since the last time
        we used it, and if so, attempts to create a new socket. If this
        connection attempt fails we reset the pool and reraise the error.

        Checking sockets lets us avoid seeing *some*
        :class:`~pymongo.errors.AutoReconnect` exceptions on server
        hiccups, etc. We only do this if it's been > 1 second since
        the last socket checkout, to keep performance reasonable - we
        can't avoid AutoReconnects completely anyway.
        """
        # self.discard_stream(stream)
        # self.create_connection(pair, callback)
        # raise Exception()
        if time.time() - stream.last_checkout > 1:
            if _closed(stream.stream.socket):
                # Ensure sock_info doesn't return itself to pool
                self.discard_stream(stream)
                self.create_connection(pair, callback)
                return
                # try:
                #                     self.create_connection(pair, callback)
                #                 except socket.error as e:
                #                     print e
                #                     self.reset()
                #                     raise
        # else:
        callback(stream)

    

class Request(object):
    """
    A context manager returned by Connection.start_request(), so you can do
    `with connection.start_request(): do_something()` in Python 2.5+.
    """
    def __init__(self, connection):
        self.connection = connection

    def end(self):
        self.connection.end_request()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end()
        # Returning False means, "Don't suppress exceptions if any were
        # thrown within the block"
        return False
