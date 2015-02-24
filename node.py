from Tkinter import *

from basics import *

NODE_RADIUS = 5
NODE_COLOR = "green"
NODE_PENDING_COLOR = "purple"
CONNECTION_COLOR = "yellow"

class NodeError(Exception):
    pass

class Node:
    def __init__(self, location):
        self.location = location
        self.connections = []
        self.packetBuffer = []
        self.isPendingAction = False

    def addPacketToBuffer(self, packet):
        self.packetBuffer.append(packet)

    def setPendingAction(self):
        self.isPendingAction = True

    def clearPendingAction(self):
        self.isPendingAction = False

    def connectTo(self, destNode):
        self.clearPendingAction()

        if destNode is self:
            raise NodeError("Tried to connect a node to itself")

        for connection in self.connections:
            if connection.destNode is destNode:
                raise NodeError("Tried to connect to a node that already has a connection")

        self.connections.append(Connection(self, destNode))

    def disconnectFrom(self, destNode):
        for connection in self.connections:
            if connection.destNode is destNode:
                self.connections.remove(connection)
                return

        raise NodeError("Tried to disconnect from a node that doesn't have a connection")

    def update(self):
        for connection in self.connections:
            connection.update()

    def draw(self, canvas):
        for connection in self.connections:
            connection.draw(canvas)

        nodeColor = NODE_COLOR
        if self.isPendingAction:
            nodeColor = NODE_PENDING_COLOR

        canvas.create_rectangle(self.location.x - NODE_RADIUS, self.location.y - NODE_RADIUS,
                                self.location.x + NODE_RADIUS, self.location.y + NODE_RADIUS, outline=nodeColor)

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

class Packet:
    def __init__(self, sourceNode, destNode, message):
        self.sourceNode = sourceNode
        self.destNode = destNode
        self.message = message
