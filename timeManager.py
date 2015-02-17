import time

TARGET_FRAME_TIME_MS = 20
RUNNING_AVERAGE_MAX_SAMPLES = 10

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
        self.startTimer("frame")

    def stopFrameTimer(self):
        elapsedTime = self.stopTimer("frame")
        millisecondsElapsed = int(round(elapsedTime))
        millisToNextFrame = max(0, TARGET_FRAME_TIME_MS - millisecondsElapsed)

        return millisToNextFrame

class Timer:
    def __init__(self, name):
        self.name = name
        self.samples = []
        self.startTime = -1

    def start(self):
        self.startTime = time.time()

    def stop(self):
        if(self.startTime < 0):
            raise RuntimeError("stop() called before start() on timer " + self.name)

        elapsedTime = time.time() - self.startTime
        self.startTime = -1

        self.samples.append(elapsedTime)
        if len(self.samples) > RUNNING_AVERAGE_MAX_SAMPLES:
            self.samples.pop()

        return elapsedTime

    def runningAverage(self):
        totalTime = 0

        for sample in self.samples:
            totalTime += sample

        return (totalTime / len(self.samples))
