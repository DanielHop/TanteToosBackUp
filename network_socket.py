import socket


class NetworkSocket():

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def connect_socket(self, ip, port, password):
        print("connecting...")
        # Try to connect
        self.connected = 0
        try:
            self.sock.connect((ip, port))
        except Exception as e:
            print(type(ip), type(port))
            print(e)
            self.sock.close()
            return 0

        # check for correct module
        self.write("\x10")
        d = []
        d = self.read(3)
        if d[0] != 21 and d[0] != 19:
            print("Wrong module type found")
            self.sock.close()
            return 0

        # Check to see if password is enabled
        self.write("\x7a")
        d = []
        d = self.read(1)
        if d[0] == 0:
            print("p")                     # Password is enabled
            passwordString = '\x79' + password      # Put together password command and send it
            self.write(passwordString)
            d = self.read(1)
            if d[0] != 1:                      # The password was wrong
                print("Wrong password")
                self.sock.close()
                return 0
        return 1

    def write(self, mesg):
        try:
            self.sock.sendall(mesg.encode())
        except Exception as e:
            print(e)
            print("Error writing message")

    def read(self, readnum):
        chunks = []
        bytes_recd = 0
        while bytes_recd < readnum:
            chunk = self.sock.recv(min(readnum - bytes_recd, 2048))
            if chunk == '':
                print("Error reading message")
                raise RuntimeError("socket connection broken")
            chunks.extend(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return chunks

    def close_socket(self):
        try:
            self.sock.close()
            self.connected = False
        except Exception as e:
            print(e)
        print("Disconnected")
