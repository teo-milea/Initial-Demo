import bpy
from mathutils import *
import math
import socket
import threading
import queue
from time import sleep

running = True
Q = queue.Queue()

class Server:
    def __init__(self, host="", port=10002):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#        self.socket.setblocking(False)
        self.socket.bind((host,port))
        print(self.socket.getsockname())
        
    def receive(self):
        global running
        while running:
            try:
                data, addr = self.socket.recvfrom(1024)
                print('Am primit')
                print(data)
                Q.put(data.decode())
            except socket.error:
                print(socket.error)
                continue
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        
    def execute(self):
        self.thread = threading.Thread(target=self.receive)
        self.thread.start()
                         
class Transformer():
    
    def _execute(self):
        rover = bpy.data.objects["Cube"]
        angle = math.radians(0.5)
        
        x_pos_rot = Euler((angle, 0, 0))
        y_pos_rot = Euler((0, angle, 0))
        z_pos_rot = Euler((0, 0, angle))
        
        x_neg_rot = Euler((-angle, 0, 0))
        y_neg_rot = Euler((0, -angle, 0))
        z_neg_rot = Euler((0, 0, -angle))
        
        scale_factor = 1.01
        
        global running
        while running:
            command = Q.get()
            print(command)
            if command == "X_UP":
                rover.rotation_euler.rotate(x_pos_rot)
            if command == "X_DOWN":
                rover.rotation_euler.rotate(x_neg_rot)
            if command == "Y_LEFT":
                rover.rotation_euler.rotate(y_neg_rot)
            if command == "Y_RIGHT":
                rover.rotation_euler.rotate(y_pos_rot)
            if command == "Z_FRONT":
                rover.rotation_euler.rotate(z_pos_rot)
            if command == "Z_BACK":
                rover.rotation_euler.rotate(z_neg_rot)
            if command == "S_UP":
                rover.scale *= scale_factor
            if command == "S_DOWN":
                rover.scale /= scale_factor
            if command == "SHUTDOWN":
                running = False

    def execute(self):
        self.thread = threading.Thread(target=self._execute)
        self.thread.start()


def register():
    bpy.types.Scene.watcher_running = bpy.props.BoolProperty(default=False)
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    del bpy.types.Scene.watcher_running
    for cls in classes:
        bpy.utils.unregister_class(cls) 
        
if __name__ == '__main__':
    server = Server()
    server.execute()
    trans = Transformer()
    trans.execute()
    
#    server.thread.join()
#    trans.thread.join()
    
#    print("FINISH SCRIPT")
