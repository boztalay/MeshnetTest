from Tkinter import *

from basics import *
from node import *
import timeManager

# Some ugly constants to control some behavior

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
BORDER_MARGIN = 5

TARGET_FRAME_TIME = 20

# Keeping track of an ugly global state

STATE_IDLE = 0
STATE_PLACING = 1
STATE_MOVING = 2
state = STATE_IDLE

# Some ugly globals

nodes = []
timeMgr = timeManager.TimeManager()

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

    timeMgr.startTimer("update")
    for node in nodes:
        node.update()
    timeMgr.stopTimer("update")

    timeMgr.startTimer("draw")
    canvas.delete("all")
    canvas.create_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill="black")
    for node in nodes:
        node.draw(canvas)
    timeMgr.stopTimer("draw")

    # Continue the loop by starting another timer
    millisToNextFrame = timeMgr.stopFrameTimer()
    master.after(millisToNextFrame, updateAndDrawAll)

# Handling mouse input

def mouseClicked(event):
    global state

    clickPoint = Point(event.x, event.y)
    clampPointToBounds(clickPoint, WINDOW_WIDTH, WINDOW_HEIGHT, BORDER_MARGIN)

    if state is STATE_IDLE:
        newNode = Node(clickPoint)
        nodes.append(newNode)

# Clearing the screen and quitting

def clear(event):
    global nodes

    if state is STATE_IDLE:
        del(nodes[:])

def quit(event):
    master.quit()

# Bind some I/O

master.bind("<Button-1>", mouseClicked)
master.bind("c", clear)
master.bind("q", quit)

# Start rendering things

master.after(timeManager.TARGET_FRAME_TIME_MS, updateAndDrawAll)
mainloop()
