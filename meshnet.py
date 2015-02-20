from Tkinter import *

from basics import *
from node import *
import timeManager

# Some ugly constants to control some behavior

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
BORDER_MARGIN = 5

TARGET_FRAME_TIME = 20

CLICK_RADIUS = 9

# Keeping track of an ugly global state

STATE_IDLE = 0
STATE_MOVING = 1
STATE_CONNECTING = 2
state = STATE_IDLE

# Some ugly globals

timeMgr = timeManager.TimeManager()

nodes = []
nodeBeingMoved = None

# Set up the window and put a canvas in it

master = Tk()
master.resizable(width=False, height=False)
canvas = Canvas(master, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, highlightthickness=0)
canvas.pack()

# Updating the nodes and drawing each frame

def updateAndDrawAll():
    global canvas
    global bezierCurves

    timeMgr.startFrameTimer()

    # Update
    timeMgr.startTimer("update")
    for node in nodes:
        node.update()
    timeMgr.stopTimer("update")

    # Draw
    timeMgr.startTimer("draw")
    canvas.delete("all")
    canvas.create_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill="black")

    for node in nodes:
        node.draw(canvas)

    timeMgr.draw(canvas)
    timeMgr.stopTimer("draw")

    # Continue the loop by starting another timer
    millisToNextFrame = timeMgr.stopFrameTimer()
    master.after(millisToNextFrame, updateAndDrawAll)

# Handling mouse input

def mouseClicked(event):
    global state
    global nodes

    clickPoint = Point(event.x, event.y)
    clampPointToBounds(clickPoint, WINDOW_WIDTH, WINDOW_HEIGHT, BORDER_MARGIN)

    if state is STATE_IDLE:
        nearbyNode = getNearbyNode(clickPoint)

        if nearbyNode is None:
            placeNewNode(clickPoint)
        else:
            startMovingNode(nearbyNode)
    elif state is STATE_MOVING:
        stopMovingNode()

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

# Clearing the screen and quitting

def clear(event):
    global nodes

    if state is STATE_IDLE:
        del(nodes[:])

def quit(event):
    master.quit()

# Bind some I/O

master.bind("<Button-1>", mouseClicked)
master.bind("<Motion>", mouseMoved)
master.bind("c", clear)
master.bind("q", quit)

# Start rendering things

updateAndDrawAll()
mainloop()
