
ip = "166.111.80.127"
port = 10024
import socket 
s = socket.socket()   
host = socket.gethostname() # 获取本地主机名

try:
    s.connect((ip, port))
    print('connection established!')
    s.close()

except Exception as err:
    print('connection failed.')