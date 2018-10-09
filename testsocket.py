import socket
import time

class Algo():
    def __init__(self):
        self.host = "192.168.21.21"
        self.port = 3053
        self.buffersize = 1024
        self.connected = False
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Socket established, connecting...')
        self.connect()

    def connect(self):
        while not self.connected:
            try:
                print('Connecting')
                self.client.connect((self.host, self.port))
                print('Connected.')
                self.connected = True
            except socket.error:
                time.sleep(2)
                
    def write(self,msg):
        sflag = False
        while not sflag:
            try:
                print('sending')
                self.client.sendall(msg.encode('utf-8'))
                print(msg)
                sflag = True
            except socket.error:
                print('send error occurred')
                self.connect()
                time.sleep(1)
                

    def read(self,fro=''):
        while True:
            try:
                print('reading')
##                while self.client.recv(self.buffersize) == None:            
                msg = self.client.recv(1024).decode('utf-8')
                print('READ DATA: ' + msg)
                
                if fro in msg:
                    msg = msg.split('|')[1].strip()
                    if ';' in msg:
                        return msg.split(';')
                    else:
                        return msg
                else:
                    return False
            except socket.error:
                self.connect()
                time.sleep(2)

        
        
