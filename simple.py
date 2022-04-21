from network_socket import NetworkSocket
import time
import pyodbc
from datetime import datetime, timedelta

DEVELOPER = False
DEF_PORT = 17494
PASSWORD_TIME = 300


class Controller():
    def __init__(self, name, ip, port=DEF_PORT):
        self.ip = ip
        self.port = int(port)
        self.ns = NetworkSocket()
        self.connected = 0
        self.name = name

    def __del__(self):
        self.close()

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
        i = self.relay_off(relay)
        self.close()
        return i

    def close(self):
        self.ns.close_socket()
        return 1


class Log():
    def __init__(self):
        date = datetime.now() - timedelta(hours=12)
        date = date.strftime("%Y-%m-%d")
        self.f = open(".\\Log\\log" + date + ".txt", "a+")
        line = "Log boek geopend op tijd "
        line += datetime.now().strftime("%H:%M:%S:")
        self.f.write(line + "\n")

    def __del__(self):
        line = "Log boek gesloten op tijd "
        line += datetime.now().strftime("%H:%M:%S:")
        self.f.write(line + "\n")
        self.f.close()

    def log_locker(self, locker, success):
        line = datetime.now().strftime("%H:%M:%S:") + " Openen locker "
        line += str(locker) + " return code " + str(success)
        self.f.write(line + "\n")

    def log_not_found(self, locker):
        line = datetime.now().strftime("%H:%M:%S:") + " Locker "
        line += str(locker) + " niet gevonden"
        self.f.write(line + "\n")


def find_controller(name, c_lockers, c_ports):
    for i in range(0, len(c_lockers)):
        index = None
        try:
            index = c_lockers[i].index(name)
        except Exception:
            continue

        if(index is not None):
            return(i, index, c_ports[i][index])

    return(-1, -1, -1)


def open_controller(c_index, locker, controllers):
    controller = controllers[c_index]
    name = controller.name
    ip = controller.ip
    time = datetime.now().strftime("%H:%M")
    if DEVELOPER:
        line = "Openen controller " + str(name) + " op poortje " + str(port)
        line += " en ip: " + str(ip)
        print(line)
    else:
        print(time + ": Openen kluisje " + str(locker))
    i = controller.open(port)
    return i


def enter_password():
    password = input("Voer wachtwoord in: ")
    while password != "1234":
        print("Incorrect wachtwoord")
        password = input("Voer wachtwoord in: ")
    print("Wachtwoord klopt!")


logger = Log()

cmd = r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=.\simple.accdb;'
conn = pyodbc.connect(cmd)
cursor = conn.cursor()

# Get all controllers
sql = "select ID, ip_address, names from devices where type_id = 1"
sql += " and active = 1"
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
last_time = datetime.now()
enter_password()
while lock != "exit":
    lock = input("Kluisje om te openen: ")
    diff = datetime.now() - last_time

    if diff.total_seconds() > PASSWORD_TIME:
        enter_password()

    c_index, n_index, port = find_controller(lock, c_lockers, c_ports)

    if(c_index != -1):
        success = open_controller(c_index, lock, controllers)
        logger.log_locker(lock, success)
    else:
        print("Kluisje niet gevonden")
        logger.log_not_found(lock)

    last_time = datetime.now()

# Timestamps
# Logboeks
# Pincode om te openen
