#sample server bluetooth connection
from bluetooth import *
from time import sleep

import re
import sys
import threading 
import socket


class BtServer:
    
    port=3

    def __init__(self):
        self.address =""
        self.testnum =0
        
        self.recvd_list=[]
        self.liveData=[]
        self.sem_val = 0
        self.sem_plot = 0
        self.state = 0
        
        self.create_socket()
        
        #self.accept_conn()


    def create_socket(self):
        self.socket = BluetoothSocket( RFCOMM )
        self.socket.bind(("",BtServer.port))
        self.socket.listen(1)
        print("listenting on port "+str(BtServer.port))

    def accept_conn(self):
        print("Handling BT connection on thread")
        t1=threading.Thread(target=self.bt_handler)
        t1.start()
        
        t2=threading.Thread(target=self.liveData_thread)
        t2.start()
    def liveData_thread(self):
        
        self.liveData= [0]*2000
        
        index = 0
        value=""
        
        while(1):
            try:
                #if (index % 25 == 0):
                #    print("SEMAPHORE VALUE = " + str(self.sem_val))
                
                if (self.sem_val > 0):
        
                    self.sem_plot = 0
                    
                    for i in self.recvd_list[-self.sem_val]:
                        if(i!=","):
                            if(i!= ""):
                                value+=i
                        else:
                            self.liveData[index % 2000] = (int(value))
                            index += 1
                            value=""
                            
                    if(value!= ""):
                        self.liveData[index % 2000] = (int(value)) # Append the last value
                        index += 1
                        
                    value=""
                    
                    self.sem_val = self.sem_val - 1
                    
                    self.sem_plot = 1
                if (self.state==2):
                    break
                
            except ValueError as error:
                print ("Thread 2 exits")
                break

                    
    def bt_handler(self):
        
        self.state = 1; # Accept State
        
        self.client,self.address = self.socket.accept()
        print("Connected to ",self.address)
        recording=False
        
        # Start Receiving Data
        data = self.client.recv(1024)
        data = data.decode("utf-8")
        #print(data)
        valid = re.match("data: ([\d,]+)",data)
        self.recvd_list=[]
        
        #--------------------------------------------#
        while (1):

            #print ("received: %s" % (data))
            
            self.recvd_list.append(data)
            self.sem_val = self.sem_val + 1
            if (self.sem_val>10):
                    sleep(0.02)
            data = self.client.recv(1024)
            data = data.decode("utf-8")
            if ("runtime" in data):
                print ("received: %s" % (data))
                self.recvd_list.append(data)
                break
        #--------------------------------------------#
        
        # All recorded data is done sending. Now just need to receive final values
        # Runtime
        
        #print(data)

        #print(runtime)
        #self.recvd_list.append(runtime.group(1))
        
        # Sampling Frequency
        #freq = self.client.recv(1024) 
        #freq = freq.decode("utf-8")   
        #recvd_list.append(freq)

        # Parse comma-separated values and create an array of 
        # individual values
        parsed_list=self.parse_csv(self.recvd_list)
        
        #Write Values to a textfile
        txtFile=open("test0.txt","w")#+str(self.testnum)+".txt","w")
        self.testnum+=1
        for item in parsed_list:
            txtFile.write(item+"\n")
        txtFile.close()

        #print(freq)


        self.client.close()
        print("Data Transfer Complete")
        self.state = 2; # Complete State
        return 

    def parse_csv(self,arr):

        data_arr=[]
        value=""

        for line in arr:
            for i in line:
                if(i!=","):
                    value+=i
                else:
                    data_arr.append(value)
                    value=""
            data_arr.append(value)
            value=""
            
        data_arr[-1] = re.sub('runtime: ', '', data_arr[-1])
        return data_arr

if __name__ =="__main__":

    server=BtServer()

    server.accept_conn()

        
        
        



    
