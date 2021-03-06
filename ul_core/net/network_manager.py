import socket
import select


class ConnectionClosed(Exception):
    def __init__(self, conn):
        self.conn = conn


class BufferTooLong(ConnectionClosed):
    pass


class Connection:
    def __init__(self, conn, addr):
        self.conn, self.addr = conn, addr
        self.buffer = b''

    def close(self):
        self.conn.close()


class NetworkManager:
    def __init__(self):
        self.ip = "127.0.0.1"
        self.port = 9099
        self.bufsize = 1024
        self.maxBufferLength = 10000

        # internet, tcp
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # SO_REUSEADDR will allow us to quickly restart the server if it dies
        # (useful for testing)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Use non blocking socket
        self.sock.setblocking(0)
        self.connections = []
        self.isClient = False

        self.verbose = False

    def startServer(self):
        self.sock.bind(("", self.port))
        self.sock.listen(2)

    def accept(self):
        """
        Accept connections. Does not block
        """
        readers, writers, errors = select.select([self.sock], [], [], 0)
        if len(readers) > 0:
            # Get connection
            conn = Connection(*self.sock.accept())
            self.connections.append(conn)
            self.onClientConnected(conn)  # Do callback

    def close(self):
        for conn in self.connections:
            conn.close()

    def connect(self, addr):
        self.sock.setblocking(1)
        self.sock.connect(addr)
        self.connections = [Connection(self.sock, addr)]
        self.isClient = True
        self.sock.setblocking(0)

    def send(self, target, data):
        packet = bytes(data) + b'\0'

        if self.verbose:
            print("Sent packet " + str(packet) + " to " + str(target))

        if self.isClient:
            self.sock.sendall(packet)
        else:
            tgt = next(x for x in self.connections if x.addr == target)
            tgt.conn.sendall(packet)

    def recv(self):
        readers, writers, errors = select.select(
            [c.conn for c in self.connections], [], [], 0)

        for conn in readers:
            c = next(x for x in self.connections if x.conn == conn)

            try:
                newData = c.conn.recv(self.bufsize)
            except (ConnectionResetError, TimeoutError):
                raise ConnectionClosed(c)

            if newData == b'':
                raise ConnectionClosed(c)

            c.buffer += newData

            if len(c.buffer) > self.maxBufferLength:
                c.close()
                raise BufferTooLong(c)

            data = c.buffer.split(b'\0')
            c.buffer = data[-1]
            data = data[:-1]

            tgt = next(x for x in self.connections if x.conn == conn)

            for d in data:
                self.onGotPacket(d, tgt.addr)

    def onClientConnected(self, conn):
        """
        Callback for when the client connects. Override this
        """
        print(conn)

    def onGotPacket(self, packet, addr):
        print(packet)
