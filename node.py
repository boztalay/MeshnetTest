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
        self.connectionsTriedForDests = {}
        self.connectionsFailedForDests = {}
        self.isPendingAction = False

    def addPacketToBuffer(self, packet, sourceNode):
        # If this is the first time this node has gotten a packet for this destination,
        # this will ensure that the connection to the node that first send this node
        # a packet with this destination will be at the front of the list of connections
        # to try for it. This makes sure that 1) the packet isn't just sent back to that node
        # and 2) we can default to sending the packet back to it if all other connections
        # have been tried. If the packet is marked as hitting a dead end, we add that
        # connection to a list of failed connections for that destination.

        if packet.destNode not in self.connectionsTriedForDests:
            connectionsTriedForDest = []
            self.connectionsTriedForDests[packet.destNode] = connectionsTriedForDest
        else:
            connectionsTriedForDest = self.connectionsTriedForDests[packet.destNode]

        if packet.destNode not in self.connectionsFailedForDests:
            connectionsFailedForDest = []
            self.connectionsFailedForDests[packet.destNode] = connectionsFailedForDest
        else:
            connectionsFailedForDest = self.connectionsFailedForDests[packet.destNode]

        connectionPacketCameFrom = None
        for connection in self.connections:
            if connection.destNode is sourceNode:
                connectionPacketCameFrom = connection

        if connectionPacketCameFrom is not None:
            if connectionPacketCameFrom not in connectionsTriedForDest:
                connectionsTriedForDest.append(connectionPacketCameFrom)
            if packet.foundDeadEnd:
                packet.foundDeadEnd = False
                if connectionPacketCameFrom not in connectionsFailedForDest:
                    connectionsFailedForDest.append(connectionPacketCameFrom)

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

            sortedConnectionsForDest = sorted(self.connections, key=lambda connection: connection.destNode.distanceTo(packet.destNode))
            connectionsTriedForDest = self.connectionsTriedForDests[packet.destNode]
            connectionsFailedForDest = self.connectionsFailedForDests[packet.destNode]

            couldSend = False
            for connection in sortedConnectionsForDest:
                if connection not in connectionsFailedForDest:
                    if len(connectionsTriedForDest) == 0 or (len(connectionsTriedForDest) > 0 and connection is not connectionsTriedForDest[0]):
                        connection.sendPacket(packet)
                        connectionsTriedForDest.append(connection)
                        couldSend = True
                        break

            if not couldSend:
                if len(connectionsTriedForDest) > 0:
                    # No connections left to try, send it back to the node we got it from
                    # Index 0 will always be the first node that sent a packet with this destination
                    packet.foundDeadEnd = True
                    connectionsTriedForDest[0].sendPacket(packet)
                elif packet not in unsendablePackets:
                    unsendablePackets.append(packet)

        self.packetBuffer = unsendablePackets

    def updateConnections(self):
        for connection in self.connections:
            connection.update()

    def draw(self, canvas):
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
        print "Got a packet!"

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
        self.foundDeadEnd = False
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
