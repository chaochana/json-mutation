# JSON Mutator

import socket
from select import select
import sys
import logging
import json

class TcpTee:

    def __init__(self, source_port, destination):
        self.destination = destination

        self.teesock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.teesock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.teesock.bind(('127.0.0.1', source_port))
        self.teesock.listen(200)

        # Linked client/server sockets in both directions
        self.channel = {}

    def run(self):
        while 1:
            inputready, outputready, exceptready = select([self.teesock] + self.channel.keys(), [], [])
            for s in inputready:
                if s == self.teesock:
                    self.on_accept()
                    break

                data = s.recv(4096)
                if not data:
                    self.on_close(s)
                    break

                self.on_recv(s, data)

    def on_accept(self):
        clientsock, clientaddr = self.teesock.accept()
        serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            serversock.connect(self.destination)
        except Exception:
            logging.exception('Could not connect to server %s. Closing connection to client %s' % (self.destination, clientaddr))
            clientsock.close()
        else:
            logging.info("%r has connected", clientaddr)
            self.channel[clientsock] = serversock
            self.channel[serversock] = clientsock

    def on_close(self, sock):
        logging.info("%s has disconnected", s.getpeername())
        othersock = self.channel[sock]

        sock.close()
        othersock.close()

        del self.channel[sock]
        del self.channel[othersock]

    def on_recv(self, sock, data):
        print("================= ORIGINAL ===============")
        adata = str(data).split("\r\n\r\n")
        
        header = adata[0]
        print("HEADER: ",header)
        if len(adata) == 2:
            payload = adata[1]
            print("PAYLOAD: ",payload)
 
        newPayload = "{\"id\": 1}"

        print("================= MUTANT ===============")
        print(data.replace("json-server","json-client"))
        print("================================")
        # jdata = json.loads(data)
        # print(jdata)
        # data.replace("json-server","json-server-modify")
        if len(adata) == 2:
            print("OLD DATA: ", data)
            newData = header+"\r\n\r\n"+payload.replace("json","jsxn")
            print("NEW DATA: ", newData)
            self.channel[sock].send(newData)
        else:
            self.channel[sock].send(data)

    def dump(obj):
        for attr in dir(obj):
            if hasattr( obj, attr ):
                print( "obj.%s = %s" % (attr, getattr(obj, attr)))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("listen_port", help="The port this process will listen on.", type=int)
    parser.add_argument("server_host", help="The remote host to connect to.")
    parser.add_argument("server_port", help="The remote port to connect to.", type=int)
    args = parser.parse_args()

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    tee = TcpTee(int(args.listen_port), (args.server_host, int(args.server_port)))
    try:
        tee.run()
    except KeyboardInterrupt:
        logging.info("Ctrl C - Good Bye")
        sys.exit(1)