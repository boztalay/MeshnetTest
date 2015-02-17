from Tkinter import *

from basics import *

NODE_RADIUS = 5
NODE_COLOR = "green"

class Node:
    def __init__(self, location):
        self.connections = []
        self.location = location

    def update(self):
        pass

    def draw(self, canvas):
        canvas.create_rectangle(self.location.x - NODE_RADIUS, self.location.y - NODE_RADIUS,
                                self.location.x + NODE_RADIUS, self.location.y + NODE_RADIUS, outline = NODE_COLOR)
