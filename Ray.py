import math
import numpy as np

class Ray: 
    def __init__(self, xFoot, yFoot, orientation):
        self.p = np.array([xFoot, yFoot])
        self.theta = orientation 
        self.vect = np.array([math.cos(orientation), math.sin(orientation)])
    def draw(self,ax,s):
        ax.plot([self.p[0], self.p[0] + s*math.cos(self.theta)], 
              [self.p[1], self.p[1] + s*math.sin(self.theta)], color='blue')
        ax.plot(self.p[0], self.p[1], 'ro', markersize=2)
