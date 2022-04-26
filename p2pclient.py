"""
Appending to log: every time you have to add a log entry, create a new dictionary and append it to self.log. The dictionary formats for diff. cases are given below
Registraion: (R)
{
    "time": <time>,
    "text": "Client ID <client_id> registered"
}
Unregister: (U)
{
    "time": <time>,
    "text": "Unregistered"
}
Fetch content: (Q)
{
    "time": <time>,
    "text": "Obtained <content_id> from <IP>#<Port>
}
Purge: (P)
{
    "time": <time>,
    "text": "Removed <content_id>"
}
Obtain list of clients known to a client: (O)
{
    "time": <time>,
    "text": "Client <client_id>: <<client_id>, <IP>, <Port>>, <<client_id>, <IP>, <Port>>, ..., <<client_id>, <IP>, <Port>>"
}
Obtain list of content with a client: (M)
{
    "time": <time>,
    "text": "Client <client_id>: <content_id>, <content_id>, ..., <content_id>"
}
Obtain list of clients from Bootstrapper: (L)
{
    "time": <time>,
    "text": "Bootstrapper: <<client_id>, <IP>, <Port>>, <<client_id>, <IP>, <Port>>, ..., <<client_id>, <IP>, <Port>>"
}
"""
import pickle
import random
import socket
import time
import json
import threading


class p2pclient:
    def __init__(self, client_id, content, actions):
        
        ##############################################################################
        # TODO: Initialize the class variables with the arguments coming             #
        #       into the constructor                                                 #
        ##############################################################################

        self.client_id = client_id
        self.content = content
        self.actions = actions  # this list of actions that the client needs to execute

        
        self.content_originator_list = []  # None for now, it will be built eventually
        #[{content_id:<>, client_id:<>, ip:<>, port:<>}]

        ##################################################################################
        # TODO:  You know that in a P2P architecture, each client acts as a client       #
        #        and the server. Now we need to setup the server socket of this client   #
        #        Initialize the the self.socket object on a random port, bind to the port#
        ##################################################################################
        random.seed(int(client_id))
        self.randport = random.randint(9000, 9999)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('127.0.0.1', self.randport))
        
        self.time = 0
        self.log = []
        ##############################################################################
        # TODO:  Register with the bootstrapper by calling the 'register' function   #
        #        Make sure you communicate to the B.S the serverport that this client#
        #        is running on to the bootstrapper.                                  #
        ##############################################################################

        self.register()
        ##############################################################################
        # TODO:  You can set status variable based on the status of the client:      #
        #        Registered: if registered to bootstrapper                           #
        #        Unregistered: unregistred from bootstrapper                         #
        ##############################################################################
        self.status = None

        # 'log' variable is used to record the series of events that happen on the client
        # Empty list for now, update as we take actions

        # Timing variables:
        ###############################################################################################
        # TODO: B.S dictates time. Updating this variable when BS sends a time increment signal       #                               #
        ###############################################################################################
        self.time = 0
        self.start_listening()



    def start_listening(self):
        ##############################################################################
        # TODO:  This function will make the client start listening on the randomly  #
        #        chosen server port.                                                 #
        ##############################################################################
        self.socket.listen(40) 

        while True:
            (clientsocket, address) = self.socket.accept()
            th = threading.Thread(target = self.client_thread, args=(clientsocket,))

            th.start()
            

    def client_thread(self, client_sock):
        ##############################################################################
        # TODO:  This function should handle the incoming connection requests from   #
        #        other clients.                                                      #
        ##############################################################################
        message = client_sock.recv(4096).decode('utf-8')

        action = message.split(',')
        if action[0] == 'O':
            data=pickle.dumps(self.return_list_of_known_clients())
            client_sock.send(data)
        elif action[0] == 'M':
            data=pickle.dumps(self.return_content_list())
            client_sock.send(data)
        elif action[0] == 'S':

            self.start()
        elif action[0] == "content":
            for content in self.content:
                if content == action[1]:
                    client_sock.send("found".encode('utf-8'))
                    return
            for col in self.content_originator_list:
                if col['content_id'] == action[1]:
                    response = str(col['port'])+","+str(col['client_id'])
                    client_sock.send(response.encode('utf-8'))
                    return
            client_sock.send("none".encode('utf-8'))



    def register(self, ip='127.0.0.1', port=8888):
        ##############################################################################
        # TODO:  Register with the bootstrapper.                                     #
        #        Append an entry to self.log that registration is successful         #
        ##############################################################################
        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        time.sleep(1)
        temp_sock.connect((ip,port))
        msg = 'R,' + str(self.client_id) + "," + str(self.randport) 
        temp_sock.send(msg.encode())

        text = "Client ID " + str(self.client_id)+ " registered"
        dict = {"time": self.time, "text": text}
        self.log.append(dict)
        temp_sock.close()
        path = "client_"+str(self.client_id)+".json"
        with open(path, 'w') as json_file:
            json.dump(self.log, json_file)


    def deregister(self, ip='127.0.0.1', port=8888):
        ##############################################################################
        # TODO:  Deregister/re-register with the bootstrapper                        #
        #        Append an entry to self.log that deregistration is successful       #
        ##############################################################################
        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        time.sleep(1)
        temp_sock.connect((ip,port))
        msg = 'U,' + str(self.client_id) 
        temp_sock.send(msg.encode())
        text = "Unregistered"
        dict = {"time": self.time, "text": text}
        self.log.append(dict)
        self.status = "Unregistered"
        path = "client_"+str(self.client_id)+".json"
        with open(path, 'w') as json_file:
            json.dump(self.log, json_file)
        

    def start(self): 
        ##############################################################################
        # TODO:  When the Bootstrapper sends a start signal, the client starts       #
        #        executing its actions. Once this is call it starts reading the      #
        #        items in self.actions and start performing them  sequentially,      #
        #        at the time they have been scheduled for, and as timed              #
        #        by B.S.                                                             #
        ##############################################################################
        
        self.time += 1
        print('time at client '+ str(self.client_id) + 'is ' + str(self.time))
        action = list(filter(lambda item: int(item['time']) == self.time, self.actions))
        if not action:
            temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_sock.connect(('127.0.0.1',8888))
            msg = 'Completed'
            temp_sock.send(msg.encode('utf-8'))
            temp_sock.close()
            return
        else:
            action = action[0]
        code = action["code"]
        if(code == "R"):
            self.register()
        elif(code == "L"):
            self.query_bootstrapper_all_clients('s')
            temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_sock.connect(('127.0.0.1',8888))
            msg = 'Completed'
            temp_sock.send(msg.encode('utf-8'))
            temp_sock.close()
        elif(code == "U"):
            self.deregister()
        elif(code == "Q"):
            content_id = action["content_id"]
            self.request_content(content_id)
            temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_sock.connect(('127.0.0.1',8888))
            msg = 'Completed'
            temp_sock.send(msg.encode('utf-8'))
            temp_sock.close()
        elif(code == "P"):
            content_id = action["content_id"]
            self.purge_content(content_id)
            temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_sock.connect(('127.0.0.1',8888))
            msg = 'Completed'
            temp_sock.send(msg.encode('utf-8'))
            temp_sock.close()
        elif(code == "O"):
            self.query_client_for_known_client('s',int(target_id))
            temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_sock.connect(('127.0.0.1',8888))
            msg = 'Completed'
            temp_sock.send(msg.encode('utf-8'))
            temp_sock.close()
        elif(code == "M"):
            target_id = action['client_id']     
            self.query_client_for_content_list(int(target_id))
            temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_sock.connect(('127.0.0.1',8888))
            msg = 'Completed'
            temp_sock.send(msg.encode('utf-8'))
            temp_sock.close()

        #add sending complete message

    #TODO: clarify on logging
    def query_bootstrapper_all_clients(self, code): 
        ##############################################################################
        # TODO:  Use the connection to ask the bootstrapper for the list of clients  #
        #        registered clients.                                                 #
        #        Append an entry to self.log                                         #
        ##############################################################################
        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        temp_sock.connect(('127.0.0.1',8888))
        msg = 'L'
        clients_text = ''
        temp_sock.send(msg.encode('utf-8'))
        list = temp_sock.recv(4096)
        
        list = pickle.loads(list)

        temp_sock.close()
        #"text": "Bootstrapper: <<client_id>, <IP>, <Port>>, <<client_id>, <IP>, <Port>>, ..., <<client_id>, <IP>, <Port>>"
        if code == 's':
            for client in list:
                    client_id, ip, port, status = client['client_id'], '127.0.0.1', client['port'], client['status']
                    if(status == "Registered"):
                        clients_text += f'<{client_id}, {ip}, {port}>, '

            self.log.append({"time": self.time, "text" : "Bootstrapper: " + clients_text[: len(clients_text)-2] })
            path = "client_"+str(self.client_id)+".json"
            with open(path, 'w') as json_file:
                json.dump(self.log, json_file)
        
        return list

    #TODO: clarify on logging
    def query_client_for_known_client(self,code, client_id): 
        client_list = None
        ##############################################################################
        # TODO:  Connect to the client and get the list of clients it knows          #
        #        Append an entry to self.log                                         #
        ##############################################################################
        #get client port 
        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        temp_sock.connect(('127.0.0.1',8888))
        msg = 'port,' + str(client_id)
        temp_sock.send(msg.encode('utf-8'))
        port = temp_sock.recv(4096).decode('utf-8')
        temp_sock.close()

        #connect to client
        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        temp_sock.connect(('127.0.0.1',int(port)))
        msg = 'O'
        temp_sock.send(msg.encode('utf-8'))
        client_list = temp_sock.recv(4096)
        client_list = pickle.loads(client_list)
        temp_sock.close()
        #"text": "Client <client_id>: <<client_id>, <IP>, <Port>>, <<client_id>, <IP>, <Port>>, ..., <<client_id>, <IP>, <Port>>"
        clients_text = ""
        if code == 's':
            for client in client_list:
                    client_id, ip, port = client['client_id'], '127.0.0.1', client['port']
                    clients_text += f'<{client_id}, {ip}, {port}>, '

            self.log.append({"time": self.time, "text" : "Client "+str(client_id)+": " + clients_text[: len(clients_text)-2] })
            path = "client_"+str(self.client_id)+".json"
            with open(path, 'w') as json_file:
                json.dump(self.log, json_file)

        return client_list

    def return_list_of_known_clients(self):
        ##############################################################################
        # TODO:  Return the list of clients known to you                             #
        ##############################################################################
        return self.content_originator_list

    def query_client_for_content_list(self, client_id): 
        content_list = None
        ##############################################################################
        # TODO:  Connect to the client and get the list of content it has            #
        #        Append an entry to self.log                                         #
        ##############################################################################
        #get client port 
        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        temp_sock.connect(('127.0.0.1',8888))
        msg = 'port,' + str(client_id)
        temp_sock.send(msg.encode('utf-8'))
        port = temp_sock.recv(4096).decode('utf-8')
        temp_sock.close()

        #connect to client
        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        temp_sock.connect(('127.0.0.1',int(port)))
        msg = 'M'
        temp_sock.send(msg.encode('utf-8'))
        content_list = temp_sock.recv(4096)
        content_list = pickle.loads(content_list)
        temp_sock.close()
        contents_text = ""
        #"text": "Client <client_id>: <content_id>, <content_id>, ..., <content_id>"
        for content in content_list:
                contents_text += content+", "

        self.log.append({"time": self.time, "text" : "Client "+str(client_id)+": " + contents_text[: len(contents_text)-2] })
        path = "client_"+str(self.client_id)+".json"
        with open(path, 'w') as json_file:
            json.dump(self.log, json_file)
        return content_list


    def return_content_list(self):
        ##############################################################################
        # TODO:  Return the content list that you have (self.content)                #
        ##############################################################################
        return self.content

    def request_content(self, content_id):
        #####################################################################################################
        # TODO:  Your task is to obtain the content and append it to the                                    #
        #        self.content list.                                                                         #
        #####################################################################################################
        #[{content_id:<>, client_id:<>, ip:<>, port:<>}]
        found = False

        for content in self.content_originator_list:
            if content_id == content['content_id']:
                client_id = content['client_id']
                port = int(content['port'])
                temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                temp_sock.connect(('127.0.0.1',port))
                msg = 'content,' + content_id #Add to client thread
                temp_sock.send(msg.encode('utf-8'))
                response = temp_sock.recv(4096).decode('utf-8')
                temp_sock.close()
                if(response == "found"):
                    found = True
                break
        if(not found):
            clients_list = self.query_bootstrapper_all_clients('n')
            for client in clients_list:
                if(not found):
                    port = int(client['port'])
                    client_id = client['client_id']
                    temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    temp_sock.connect(('127.0.0.1',port))
                    msg = 'content,' + content_id #Add to client thread
                    temp_sock.send(msg.encode('utf-8'))
                    response = temp_sock.recv(4096).decode('utf-8')
                    temp_sock.close()
                    if(response == "none"):
                        continue
                    elif(response == "found"):
                        found = True
                        print("found!!!", port)
                    else:
                        while True:
                            response = response.split(',')
                            print(response)
                            port = int(response[0].strip())
                            client_id = response[1]
                            temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            temp_sock.connect(('127.0.0.1',port))
                            msg = 'content,' + content_id #Add to client thread
                            temp_sock.send(msg.encode('utf-8'))
                            response = temp_sock.recv(4096).decode('utf-8')
                            temp_sock.close()
                            if response == "found" or response == "none":
                                break
                        if response == "found" : 
                            found = True
            if not found:
                big_list = []
                for client in clients_list:
                    list = self.query_client_for_known_client('n',int(client['client_id']))
                    big_list.extend(list) 
                    big_list = [dict(t) for t in {tuple(d.items()) for d in big_list}]
                for client in big_list:
                    if(not found):
                        port = int(client['port'])
                        client_id = client['client_id']
                        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        temp_sock.connect(('127.0.0.1',port))
                        msg = 'content,' + content_id #Add to client thread
                        temp_sock.send(msg.encode('utf-8'))
                        response = temp_sock.recv(4096).decode('utf-8')
                        temp_sock.close()
                        if(response == "found"):
                            found = True
                    # Fetch content: (Q)
                    # {
                    #     "time": <time>,
                    #     "text": "Obtained <content_id> from <IP>#<Port>
                    # }
        if found: #log
            print(client_id, port)
            self.content.append(content_id)
            dict = {'content_id' : content_id, 'client_id': client_id, 'ip': '127.0.0.1', 'port': port}
            self.content_originator_list.append(dict)
            append = {
            "time": self.time,
            "text": "Obtained "+content_id+" from "+ '127.0.0.1#'+str(port)
            }
            print(append)
            self.log.append(append)
            path = "client_"+str(self.client_id)+".json"
            with open(path, 'w') as json_file:
                json.dump(self.log, json_file)

            


    def purge_content(self, content_id):
        #####################################################################################################
        # TODO:  Delete the content from your content list                                                  #
        #        Append an entry to self.log that content is purged                                         #
        #####################################################################################################
        self.content.remove(content_id)
        append = {
        "time": self.time,
        "text": f"Removed {content_id}"
        }
        self.log.append(append)
        path = "client_"+str(self.client_id)+".json"
        with open(path, 'w') as json_file:
            json.dump(self.log, json_file)
