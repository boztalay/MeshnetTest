import time
from Tkinter import *

TARGET_FRAME_TIME_MS = 20
RUNNING_AVERAGE_MAX_SAMPLES = 25

FRAME_TIMER_NAME = "frame"
FPS_TIMER_NAME = "fps"

class TimeManager:
    def __init__(self):
        self.timers = {}

    def startTimer(self, timerName):
        if timerName in self.timers:
            timer = self.timers[timerName]
        else:
            timer = Timer(timerName)
            self.timers[timerName] = timer

        timer.start()

    def stopTimer(self, timerName):
        if timerName not in self.timers:
            raise RuntimeError("Tried to stop a timer that doesn't exist (" + timerName + ")")
        timer = self.timers[timerName]

        return timer.stop()

    def runningAverageOfTimer(self, timerName):
        if timerName not in self.timers:
            raise RuntimeError("Tried to get running average of a timer that doesn't exist (" + timerName + ")")
        timer = self.timers[timerName]

        return timer.runningAverage()

    def startFrameTimer(self):
        self.startTimer(FRAME_TIMER_NAME)

        if FPS_TIMER_NAME in self.timers:
            self.stopTimer(FPS_TIMER_NAME)
        self.startTimer(FPS_TIMER_NAME)

    def stopFrameTimer(self):
        elapsedTime = self.stopTimer(FRAME_TIMER_NAME)
        millisecondsElapsed = int(round(elapsedTime * 1000.0))
        millisToNextFrame = max(0, TARGET_FRAME_TIME_MS - millisecondsElapsed)

        return millisToNextFrame

    def draw(self, canvas):
        currentY = 2

        for timerName, timer in self.timers.iteritems():
            if timer.name not in [FRAME_TIMER_NAME, FPS_TIMER_NAME]:
                canvas.create_text(5, currentY, text=timerName + (":\t%.5fms" % (timer.runningAverage() * 1000)), anchor=NW, fill="white")
                currentY += 13

        if FPS_TIMER_NAME in self.timers:
            fpsAverage = self.runningAverageOfTimer(FPS_TIMER_NAME)
            if fpsAverage > 0:
                frameRate = 1.0 / fpsAverage
                canvas.create_text(5, currentY + 2, text=("FPS:\t%.5f" % frameRate), anchor=NW, fill="white")

class Timer:
    def __init__(self, name):
        self.name = name
        self.samples = []
        self.startTime = -1

    def start(self):
        self.startTime = time.time()

    def stop(self):
        if self.startTime < 0:
            raise RuntimeError("stop() called before start() on timer " + self.name)

        elapsedTime = time.time() - self.startTime
        self.startTime = -1

        self.samples.insert(0, elapsedTime)
        if len(self.samples) > RUNNING_AVERAGE_MAX_SAMPLES:
            self.samples.pop()

        return elapsedTime

    def runningAverage(self):
        if len(self.samples) == 0:
            return 0.0

        totalTime = 0.0

        for sample in self.samples:
            totalTime += sample

        return (totalTime / len(self.samples))
