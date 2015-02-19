import math

# A quick class to store points

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def setToPoint(self, otherPoint):
        self.x = otherPoint.x
        self.y = otherPoint.y

    def distanceTo(self, otherPoint):
        return math.sqrt(pow(self.x - otherPoint.x, 2) + pow(self.y - otherPoint.y, 2))

# Helper function to keep the given point within the given bounds

def clampPointToBounds(point, boundX, boundY, margin):
    if point.x < 0 + margin:
        point.x = 0 + margin
    elif point.x > boundX - margin:
        point.x = boundX - margin

    if point.y < 0 + margin:
        point.y = 0 + margin
    elif point.y > boundY - margin:
        point.y = boundY - margin

# Ugh floating point

def areFloatsEqual(float1, float2):
    if float1 > (float2 - 0.001) and float1 < (float2 + 0.001):
        return True
    else:
        return False
