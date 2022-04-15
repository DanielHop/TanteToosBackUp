from network_socket import NetworkSocket
import time
import pyodbc


class Controller():
    def __init__(self, name, ip, port=17494):
        self.ip = ip
        self.port = int(port)
        self.ns = NetworkSocket()
        self.connected = 0
        # self.connected = self.ns.connect_socket(self.ip, self.port, "password")
        # print(self.connected)
        self.name = name

    def connect(self):
        self.ns = NetworkSocket()
        self.connected = self.ns.connect_socket(self.ip, self.port, "")

    def relay_on(self, relay):
        if self.connected == 0:
            print("Not connected")
            return -1

        command = "\x20"
        command += chr(relay)
        command += "\x00"

        self.ns.write(command)
        return(self.ns.read(1))

    def relay_off(self, relay):
        if self.connected == 0:
            print("Not connected")
            return -1

        command = "\x21"
        command += chr(relay)
        command += "\x00"

        self.ns.write(command)
        return(self.ns.read(1))

    def open(self, relay):
        self.connect()
        self.relay_on(relay)
        time.sleep(0.5)
        self.relay_off(relay)
        self.close()

    def close(self):
        self.ns.close_socket()
        return 1


def find_controller(name, c_lockers, c_ports):
    for i in range(0, len(c_lockers)):
        index = None
        try:
            index = c_lockers[i].index(name)
        except:
            continue

        if(index is not None):
            return(i, index, c_ports[i][index])
    return(-1, -1, -1)


cmd = r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=.\simple.accdb;'
conn = pyodbc.connect(cmd)
cursor = conn.cursor()

# Get all controllers
sql = "select ID, ip_address, names from devices where type_id = 1 and active = 1"
cursor.execute(sql)
controller_data = cursor.fetchall()

n = len(controller_data)
# controllers = [None]*n
c_lockers = [None]*n
c_ports = [None]*n
controllers = [None]*n

for i in range(0, len(controller_data)):
    c = controller_data[i]
    ip = c[1]
    name = c[2]
    controllers[i] = Controller(name, ip)

    sql = "select names, port_number FROM devices"
    sql += " where parent_id =" + str(c[0])
    # print(sql)
    cursor.execute(sql)
    lockers = cursor.fetchall()

    l_names = [x[0] for x in lockers if x[1] is not None]
    l_port = [x[1] for x in lockers if x[1] is not None]

    c_lockers[i] = l_names
    c_ports[i] = l_port

lock = ""
while lock != "exit":
    lock = input("Kluisje om te openen: ")

    c_index, n_index, port = find_controller(lock, c_lockers, c_ports)

    if(c_index != -1):
        controller = controllers[c_index]
        name = controller.name
        ip = controller.ip
        print("Openen controller " + str(name) + " op poortje " + str(port) + " en ip: " + str(ip))
        controller.open(port)
    else:
        print("Kluisje niet gevonden in actieve controllers")

[c.close() for c in controllers]
