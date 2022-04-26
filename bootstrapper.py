from p2pbootstrapper import p2pbootstrapper
import time
import threading
import socket

if __name__ == "__main__":
    ##############################################################################
    # This performs the following tasks:                                   #
    # 1) Instantiate the bootstrapper                                            #
    # 2) Wait for 10 sec so that all clients come up and register                #
    # 4) Call bootst.start() which inturn calls the start of all clients         #
    ##############################################################################
    bootst = p2pbootstrapper() # '127.0.0.1', 8888
    thread = threading.Thread(target=bootst.start_listening)
    thread.start()
    time.sleep(20)
    



   