import ibm_db

hostname="b1bc1829-6f45-4cd4-bef4-10cf081900bf.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud"
uid="ngw72704"
pwd="mzQy2ksb3Ff6i3Ex"
driver="(IBM DB2 ODBC DRIVER)"
db="bludb"
port="32304"
protocol="TCPIP"
cert="certificate.crt"


dsn=(
    "DATABASE={0};"
     "HOSTNAME={1};"
     "PORT={2};"
     "UID={3};"
     "SECURITY=SSL;"
     "SSLServerCertificate={4};"
     "PWD={5};"
     ).format(db,hostname,port,uid,cert,pwd)
print(dsn)
try:
    db2=ibm_db.connect(dsn,"","")
    print("connected to database")
except:
    print("unable to connect",ibm_db.conn_errormsg())
    

