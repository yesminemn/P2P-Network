import imp
from p2pclient import p2pclient
import json
import argparse
import threading

if __name__ == "__main__":
    
    client_id = None
    content = None
    actions = None
    
    ##############################################################################
    # This performs the following tasks:                                         #  
    # 1) Instantiate the client                                                  #
    # 2) Client picks its serveport,bind to it (randomly picked)                 #
    # 3) Register with bootstrapper                                              #
    # 4) Start listening on the port picked                                      #
    # 5) Start executing its actions                                             #
    ##############################################################################

    #########################################################################################
    # TODO:  Read the client_id, content and actions from <file>.json, which can be obtained#
    #        from command line arguments. and feed it into the constructor of               #
    #        the p2pclient below                                                            #
    #########################################################################################
    parser = argparse.ArgumentParser(description='Client arguments')
    parser.add_argument('-file', '--file') 
    options = parser.parse_args()
    path = options.file
    
    f = open(path)
    data = json.load(f)
    client_id = data['client_id']
    content = data['content']
    actions = data['actions']
    print('calling const in client.py')

    client = p2pclient(client_id=client_id, content=content, actions=actions)
    # t = threading.Thread(target=client.start_listening, args=[])
    # t.start()

    
    

    ##############################################################################
    # the bootstrapper will call the start() on this client, which will make     #
    # this client start taking its actions.                                      #
    ##############################################################################