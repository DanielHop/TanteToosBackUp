import pyodbc

cmd = r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=.\simple.accdb;'
conn = pyodbc.connect(cmd)
cursor = conn.cursor()

sql = ''
with open('setup_db.sql') as f:
    sql = f.read()


with open('setup_db.sql') as file:
    sql = file.readlines()
    command = sql[0][:-1]
    sql = [command + data[:-2] + ";" for data in sql[1:]]

for s in sql:
    cursor.execute(s)
    cursor.commit()
