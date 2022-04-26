 
At end of each timestep, after all clients have completed their actions, log the registered clients in the format below
{
    "time": <time>,
    "text": "Clients registered: <<client_id>, <IP>, <Port>>, <<client_id>, <IP>, <Port>>, ..., <<client_id>, <IP>, <Port>>"
}

import socket
import threading
import json
import pickle
import time 


class p2pbootstrapper:
    def __init__(self, ip='127.0.0.1', port=8888):
        ##############################################################################
        # TODO:  Initialize the socket object and bind it to the IP and port         #
        ##############################################################################

        self.boots_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []  # None for now, will get updates as clients register
        for i in range(20):
            self.clients.append({'client_id': i+1, 'port': 0, 'status': "Unregistered"})

        # Append the log to this variable.
        self.log = []
        self.completed = 0

        # Timing variables:
        ###############################################################################################
        # TODO:  To track the time for all clients, self.time starts at 0, when all clients register  #
        #        self.MAX_CLIENTS is the number of clients we will be spinnign up.                    #
        ###############################################################################################
        self.time = 0
        self.MAX_CLIENTS = 20
        self.boots_socket.bind((ip, port))
        

    def start_listening(self):
        ##############################################################################
        # TODO:  This function will make the BS start listening on the port 8888     #
        ##############################################################################
        self.boots_socket.listen(40)
        while True:
            (clientsocket, address) = self.boots_socket.accept()
            th = threading.Thread(target = self.client_thread, args=(clientsocket,))
            th.start()
            
            

    def client_thread(self, client_sock):
        ##############################################################################
        # TODO:  This function should handle the incoming connection requests from   #
        #        clients. You are free to add more arguments to this function based  #
        #        on your need                                                        #
        ##############################################################################
        message = client_sock.recv(4096).decode('utf-8')
        action = message.split(',')
        if action[0] == 'R':
            self.register_client(int(action[1]), '127.0.0.1' ,int(action[2]))
            self.process_action_complete()
        elif action[0] == 'U':
            self.deregister_client(int(action[1]))
            self.process_action_complete()
        elif action[0] == 'L':
            data=pickle.dumps(self.return_clients())
            client_sock.send(data)
        elif action[0]=="port":
            for client in self.clients:
                if(client['client_id'] == int(action[1])):
                   port = str(client['port'])
                   client_sock.send(port.encode('utf-8'))
        elif action[0] == 'Completed':
            self.process_action_complete()
        
           
    def register_client(self, client_id, ip, port):  
        ########################################################################################
        # TODO:  Add client to self.clients, if already present, update status to 'registered  #
        ########################################################################################
        self.clients[client_id-1] = {'client_id': client_id, 'port': port, 'status': "Registered"}
        
            

    def deregister_client(self, client_id):
        ##############################################################################
        # TODO:  Update status of client to 'deregisterd'                            #
        ##############################################################################
        for client in self.clients:
            if(client["client_id"] == client_id):
                client["status"] = "Unregistered"


    def return_clients(self):
        ##############################################################################
        # TODO:  Return self.clients                                                 #
        ##############################################################################
        return self.clients

    def start(self):
        ##############################################################################
        # TODO:  Start timer for all clients so clients can start performing their   #
        #        actions                                                             #
        ##############################################################################
        if(self.time == 7):
            print("Good bye!")
            return
        self.time += 1
        print('time is: ' + str(self.time)) #printing
        for client in self.clients:
            
            temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_sock.connect(('localhost',int(client['port'])))
            msg = 'S'
            temp_sock.send(msg.encode())
            temp_sock.close()

    def process_action_complete(self):
        ##############################################################################
        # TODO:  Process the 'action complete' message from a client,update time if  #
        #        all clients are done, inform all clients about time increment       #
        ##############################################################################
        self.completed += 1 
        clients_text = ""
          
        print(self.completed ) #printing
        if (self.completed == self.MAX_CLIENTS ):
            path = 'bootstrapper.json'
            self.completed = 0
            for client in self.clients:
                client_id, ip, port, status = client['client_id'], '127.0.0.1', client['port'], client['status']
                if(status == "Registered"):
                    clients_text += f'<{client_id}, {ip}, {port}>, '
            self.log.append({"time": self.time, "text":"Clients registered: " + clients_text[: len(clients_text)-2] })
            print(f'appending in time {self.time}') # printing
            with open(path, 'w') as json_file:
                json.dump(self.log, json_file)
            
            
            self.start()


        


