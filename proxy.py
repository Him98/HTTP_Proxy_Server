import os,sys
import pickle
import time
import datetime
import copy
import socket
import json
from thread import *
import threading

buffer_size = 4096
CACHE_DIR = './cache'
MAX_CACHE_SIZE = 3
file_name=""
cache = {}

if not os.path.isdir(CACHE_DIR):
    os.makedirs(CACHE_DIR)

for file in os.listdir(CACHE_DIR):
    os.remove(CACHE_DIR + "/" + file)

# The main function starts here
def start():
    try:

        # Establishing connection with client
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('',19999))
        s.listen(5)
    except Exception, e:
        print "unable to establish socket"
        print e
        sys.exit(2)

    while True:
        try:
            conn, addr = s.accept()
            data = conn.recv(buffer_size)
            newdata = data[:3]
            newdata = newdata + " " + data[26:]
            print newdata
            # Every new thread starts here
            new_thread = threading.Thread(target = conn_string, args = (conn, data, addr, newdata))
            new_thread.start()
            
        except KeyboardInterrupt:
            s.close()
            print "Server shutting down"

            sys.exit(1)

        except Exception,e:
            s.close()
            print "An error occured : ",e
            sys.exit(1)

    s.close()

# The function for parsing the data to the main server
def conn_string(conn, data, addr, newdata):
    try:
        #print "This is data1",data
        first_line  = data.split('\n')[0]
        break_url = first_line.split(' ')[1]
        http_pos = break_url.find("://")
        if(http_pos == -1):
            temp = break_url
        else:
            temp = break_url[(http_pos+3):]

        position_port = temp.find(":")
        #print temp,position_port

        webserver_position = temp.find("/")
        if(webserver_position == -1):
            webserver_position = len(temp)
        webserver = ""
        port = -1
        if(webserver_position == -1 or webserver_position < position_port):
            port = 80
            webserver = temp[:webserver_position]
        else:
            port = int((temp[(position_port+1):])[:webserver_position - position_port - 1])
            webserver = temp[:position_port]
        #print "THis is data2",data
            
        proxy_server(webserver, port, conn, addr, data, newdata)
    except Exception,e:         
        pass
    
    sys.exit(0)

# The proxy_server function establishes the connection with the main server and sends the request to it. 
def proxy_server(webserver,port, conn, addr, data, newdata):
    try : 
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((webserver,port))
        print "connection established"
        file_name = newdata.split()[1][1:]

        if(file_name not in os.listdir(CACHE_DIR)):

            print("done")
            number_of_files = len(os.listdir(CACHE_DIR))

            if(number_of_files == 3):
                file_to_remove = ""
                minimum = 100000000000
                for i in os.listdir(CACHE_DIR):
                    if(cache[i]<minimum):
                        minimum = cache[i]
                        file_to_remove = i
                os.remove(CACHE_DIR + "/" + file_to_remove)
            
            s.send(newdata)
            fp = open(CACHE_DIR+"/"+file_name,'w')
            cache[file_name] = time.time()
            flag = 0

            while True:
                reply = s.recv(buffer_size)
                if("no-cache" in reply):
                    flag = 1;
                if(len(reply)>0):
                    fp.write(reply)
                    conn.send(reply)
                else:
                    fp.close()
                    break
            if(flag == 1):
                os.remove(CACHE_DIR + "/" + file_name)

        else:
            cache_path = CACHE_DIR + "/" + file_name
            temp1 = newdata.splitlines()
            temp1.insert(2,"If-Modified-Since: %s" % (time.strftime('%a %b %d %H:%M:%S %Y', time.localtime(cache[file_name]))))
            #temp2 = "\r\n".join(temp1)
            temp2 = ""
            for i in temp1:
                temp2 += (i + "\r\n")
            #print "This is ",temp2
            s.send(temp2)
            reply = s.recv(buffer_size)
            #print "This is ",reply
            #cache[file_name] = time.strptime(time.ctime(os.path.getmtime(cache_path)), "%a %b %d %H:%M:%S %Y")
            status_code = reply.split(" ")[1]
            #print "This is ",status_code
            
            if(status_code == "304"):
                fi = open(cache_path,'rb')
                while True:
                    dta = fi.read(buffer_size)
                    if(len(dta) > 0):
                        conn.send(dta)
                    else:
                        fi.close()
                        break

            elif(status_code == "200"):
                fp = open(cache_path,'wb')
                cache[file_name] = time.time()
                j=0
                flag = 0
                while True:
                    if("no-cache" in reply):
                        flag = 1;
                    if(j!=0):
                        reply = s.recv(buffer_size)
                    if(len(reply) > 0):
                        fp.write(reply)
                        conn.send(reply)
                    else:
                        fp.close()
                        break
                    j=j+1
                if(flag == 1):
                    os.remove(CACHE_DIR + "/" + file_name)

        s.close()
        conn.close()
        sys.exit(1)

    except socket.error, (value, message):
        s.close()
        conn.close()
        sys.exit(1)

start()

