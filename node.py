from Tkinter import *

from basics import *

NODE_RADIUS = 5
NODE_COLOR = "green"
CONNECTION_COLOR = "yellow"

class Node:
    def __init__(self, location):
        self.location = location
        self.connections = []
        self.packetBuffer = []

    def addPacketToBuffer(self, packet):
        self.packetBuffer.append(packet)

    def connectTo(self, destNode):
        for connection in self.connections:
            if connection.destNode is destNode:
                raise RuntimeError("Tried to connect to a node that already has a connection")

        self.connections.append(Connection(self, destNode))

    def disconnectFrom(self, destNode):
        for connection in self.connections:
            if connection.destNode is destNode:
                self.connections.remove(connection)
                return

        raise RuntimeError("Tried to disconnect from a node that doesn't have a connection")

    def update(self):
        pass

    def draw(self, canvas):
        canvas.create_rectangle(self.location.x - NODE_RADIUS, self.location.y - NODE_RADIUS,
                                self.location.x + NODE_RADIUS, self.location.y + NODE_RADIUS, outline = NODE_COLOR)

class Connection:
    def __init__(self, sourceNode, destNode):
        self.sourceNode = sourceNode
        self.destNode = destNode

    def sendPacket(self, packet):
        self.destNode.addPacketToBuffer(packet)

    def update(self):
        pass

    def draw(self, canvas):
        canvas.create_line(self.sourceNode.location.x, self.sourceNode.location.y,
                           self.destNode.location.x, self.destNode.location.y, fill = CONNECTION_COLOR)
