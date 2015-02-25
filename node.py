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
        self.connectionsTriedForPackets = {}
        self.isPendingAction = False

    def addPacketToBuffer(self, packet, sourceNode):
        # If this is the first time the node has seen the packet, this ensures that
        # the original sender's connection is at the front of the list of connections
        # that have already been tried, so it can be sent back if needed
        if packet not in self.connectionsTriedForPackets:
            connectionsTriedForPacket = []
            self.connectionsTriedForPackets[packet] = connectionsTriedForPacket
        else:
            connectionsTriedForPacket = self.connectionsTriedForPackets[packet]

        connectionPacketCameFrom = None
        for connection in self.connections:
            if connection.destNode is sourceNode:
                connectionPacketCameFrom = connection

        connectionsTriedForPacket.append(connectionPacketCameFrom)
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
        unsendablePackets = []

        for packet in self.packetBuffer:
            if packet.destNode is self:
                self.receivePacket(packet)
                continue

            sortedConnectionsForPacket = sorted(self.connections, key=lambda connection: connection.destNode.distanceTo(packet.destNode))
            connectionsTriedForPacket = self.connectionsTriedForPackets[packet]

            couldSend = False
            for connection in sortedConnectionsForPacket:
                if connection not in connectionsTriedForPacket:
                    connection.sendPacket(packet)
                    connectionsTriedForPacket.append(connection)
                    couldSend = True
                    break

            if not couldSend:
                if len(connectionsTriedForPacket) > 0:
                    connectionsTriedForPacket[0].sendPacket(packet) # Index 0 will always be the original sender of the packet to this node
                else:
                    unsendablePackets.append(packet)

        self.packetBuffer = unsendablePackets

    def updateConnections(self):
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

        if len(self.packetBuffer) > 0:
            innerColor = self.packetBuffer[0].makeColor()
            canvas.create_rectangle(self.location.x - (NODE_RADIUS - 2), self.location.y - (NODE_RADIUS - 2),
                                    self.location.x + (NODE_RADIUS - 2), self.location.y + (NODE_RADIUS - 2), fill=innerColor)

    def receivePacket(self, packet):
        pass

    def distanceTo(self, otherNode):
        return self.location.distanceTo(otherNode.location)

class Connection:
    def __init__(self, sourceNode, destNode):
        self.sourceNode = sourceNode
        self.destNode = destNode
        self.packetsToSend = []

    def sendPacket(self, packet):
        self.packetsToSend.append(packet)

    def update(self):
        while len(self.packetsToSend) > 0:
            self.destNode.addPacketToBuffer(self.packetsToSend.pop(), self.sourceNode)

    def draw(self, canvas):
        canvas.create_line(self.sourceNode.location.x, self.sourceNode.location.y,
                           self.destNode.location.x, self.destNode.location.y, fill = CONNECTION_COLOR)

class Packet:
    def __init__(self, sourceNode, destNode, message):
        self.sourceNode = sourceNode
        self.destNode = destNode
        self.message = message
        self.color = None

    def makeColor(self):
        if self.color is not None:
            return self.color

        color = self.sourceNode.location.x & 0x3f
        color = color << 6
        color |= self.sourceNode.location.y & 0x3f
        color = color << 6
        color |= self.destNode.location.x & 0x3f
        color = color << 6
        color |= self.destNode.location.y & 0x3f

        self.color = "#%0.6X" % color

        return self.color
