from Tkinter import *

from basics import *
from node import *
import timeManager

# Some ugly constants to control some behavior

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
BORDER_MARGIN = 5

TARGET_FRAME_TIME = 20
TARGET_UPDATE_INTERVAL = 500

CLICK_RADIUS = 9

# Keeping track of an ugly global state

STATE_IDLE = "Idle"
STATE_MOVING = "Moving"
STATE_CONNECTING_START = "Connecting start"
STATE_CONNECTING_FINISH = "Connecting finish"
STATE_PACKET_START = "Packet start"
STATE_PACKET_FINISH = "Packet finish"
state = STATE_IDLE

# Some ugly globals

timeMgr = timeManager.TimeManager()

nodes = []
nodeBeingMoved = None
newConnectionSourceNode = None
newPacketSourceNode = None
paused = False

# Set up the window and put a canvas in it

master = Tk()
master.resizable(width=False, height=False)
canvas = Canvas(master, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, highlightthickness=0)
canvas.pack()

# Updating the nodes and drawing each frame

def drawAll():
    global canvas
    global nodes
    global timeMgr

    timeMgr.startFrameTimer()

    # Draw
    timeMgr.startTimer("draw")

    canvas.delete("all")
    canvas.create_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill="black")

    for node in nodes:
        node.draw(canvas)

    drawInfo(canvas)

    timeMgr.stopTimer("draw")

    # Continue the loop by starting another timer
    millisToNextFrame = timeMgr.stopFrameTimer()
    master.after(millisToNextFrame, drawAll)

def drawInfo(canvas):
    global state
    global timeMgr
    global paused

    timeMgr.draw(canvas)
    canvas.create_text(WINDOW_WIDTH - BORDER_MARGIN, 2, text=state, anchor=NE, fill="white")

    if paused:
        pausedText = "Paused"
    else:
        pausedText = "Running"
    canvas.create_text(WINDOW_WIDTH - BORDER_MARGIN, 15, text=pausedText, anchor=NE, fill="white")

def updateAll():
    global nodes
    global paused

    timeMgr.startTimer("update")
    if not paused:
        updateNodesAndConnections()
    timeMgr.stopTimer("update")

    master.after(TARGET_UPDATE_INTERVAL, updateAll)

def updateNodesAndConnections():
    global nodes

    for node in nodes:
        node.update()

    for node in nodes:
        node.updateConnections()

def manualUpdate(event):
    global paused

    if paused:
        updateNodesAndConnections()

# Handling mouse input

def mouseClicked(event):
    global state
    global nodes

    clickPoint = Point(event.x, event.y)
    clampPointToBounds(clickPoint, WINDOW_WIDTH, WINDOW_HEIGHT, BORDER_MARGIN)
    nearbyNode = getNearbyNode(clickPoint)

    if state is STATE_IDLE:
        if nearbyNode is None:
            placeNewNode(clickPoint)
        else:
            startMovingNode(nearbyNode)
    elif state is STATE_MOVING:
        stopMovingNode()
    elif state is STATE_CONNECTING_START:
        if nearbyNode is not None:
            startConnection(nearbyNode)
    elif state is STATE_CONNECTING_FINISH:
        if nearbyNode is not None:
            finishConnection(nearbyNode)
    elif state is STATE_PACKET_START:
        if nearbyNode is not None:
            startPacket(nearbyNode)
    elif state is STATE_PACKET_FINISH:
        if nearbyNode is not None:
            finishPacket(nearbyNode)

def mouseMoved(event):
    global state
    global nodes

    mousePos = Point(event.x, event.y)
    clampPointToBounds(mousePos, WINDOW_WIDTH, WINDOW_HEIGHT, BORDER_MARGIN)

    if state is STATE_MOVING:
        nodeBeingMoved.location.setToPoint(mousePos)

# Placing new nodes

def placeNewNode(clickPoint):
    global nodes

    newNode = Node(clickPoint)
    nodes.append(newNode)

# Moving nodes

def startMovingNode(node):
    global state
    global nodeBeingMoved

    nodeBeingMoved = node
    state = STATE_MOVING

def stopMovingNode():
    global state
    global nodeBeingMoved

    nodeBeingMoved = None
    state = STATE_IDLE

# Connecting nodes

def toggleConnecting(event):
    global state
    global newConnectionSourceNode

    if state is STATE_IDLE:
        state = STATE_CONNECTING_START
    elif state is STATE_CONNECTING_START:
        state = STATE_IDLE
    elif state is STATE_CONNECTING_FINISH:
        state = STATE_IDLE
        newConnectionSourceNode.clearPendingAction()
        newConnectionSourceNode = None

def startConnection(sourceNode):
    global state
    global newConnectionSourceNode

    newConnectionSourceNode = sourceNode
    newConnectionSourceNode.setPendingAction()
    state = STATE_CONNECTING_FINISH

def finishConnection(destNode):
    global state
    global newConnectionSourceNode

    try:
        newConnectionSourceNode.connectTo(destNode)
        destNode.connectTo(newConnectionSourceNode)
    except NodeError:
        pass
    finally:
        newConnectionSourceNode = None
        state = STATE_IDLE

# Making and routing packets

def togglePacketRouting(event):
    global state
    global newPacketSourceNode

    if state is STATE_IDLE:
        state = STATE_PACKET_START
    elif state is STATE_PACKET_START:
        state = STATE_IDLE
    elif state is STATE_PACKET_FINISH:
        state = STATE_IDLE
        newConnectionSourceNode.clearPendingAction()
        newConnectionSourceNode = None

def startPacket(sourceNode):
    global state
    global newPacketSourceNode

    newPacketSourceNode = sourceNode
    newPacketSourceNode.setPendingAction()
    state = STATE_PACKET_FINISH

def finishPacket(destNode):
    global state
    global newPacketSourceNode

    packet = Packet(newPacketSourceNode, destNode, "Hello, world!")
    newPacketSourceNode.addPacketToBuffer(packet, None)
    newPacketSourceNode.clearPendingAction()

    newConnectionSourceNode = None
    state = STATE_IDLE

# A helper function to get a nearby node to move or add a connection to

def getNearbyNode(clickPoint):
    global nodes

    closestNode = None
    closestDistance = None

    for node in nodes:
        distance = node.location.distanceTo(clickPoint)
        if closestDistance is None or distance < closestDistance:
            closestNode = node
            closestDistance = distance

    if closestDistance is not None and closestDistance < CLICK_RADIUS:
        return closestNode
    else:
        return None

# Clearing the screen, quitting, pausing

def reset(event):
    global nodes

    if state is STATE_IDLE:
        del(nodes[:])

def togglePause(event):
    global paused

    paused = not paused

def quit(event):
    master.quit()

# Bind some I/O

master.bind("<Button-1>", mouseClicked)
master.bind("<Motion>", mouseMoved)
master.bind("z", togglePause)
master.bind("s", manualUpdate)
master.bind("c", toggleConnecting)
master.bind("p", togglePacketRouting)
master.bind("r", reset)
master.bind("q", quit)

# Start rendering things

drawAll()
updateAll()
mainloop()
