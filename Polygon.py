import math
import numpy as np

# ClosedPolygon acts on externally provided @Ray object. 
class ClosedPolygon: 
    def __init__(self, x, y, ids, exitID, ttcPrevious):
        self.x = x
        self.y = y
        # Wrap coords on themselves
        self.xcycle = np.append(self.x, self.x[0])
        self.ycycle = np.append(self.y, self.y[0])
        # Must be set before overriding vertices if CW
        self.isCW = self.isClockwise()
        self.inwardNormal = self.getInwardNormals()
        #self.edgeSlope,self.edgeIntercept = self.getEdgeAsLine()

        nv = len(x)+1
        self.mp = np.array([(self.xcycle[range(0, nv-1)] + self.xcycle[range(1,nv)])/2., 
                             (self.ycycle[range(0, nv-1)] + self.ycycle[range(1,nv)])/2.])
        self.ids = ids 
        # Halts when ray passes through this ID
        self.exitID = exitID
        # Ray initially on cell entrance
        self.currID = len(x)-1
        self.solution = [None,None,ttcPrevious,-1]

    def draw(self, ax, col='black'):
        ax.plot(self.xcycle, self.ycycle, color=col)
        ax.scatter(self.solution[0], self.solution[1], color=col, s=40)
        #for i in range(len(self.x)):
        #    ax.text(self.mp[0,i], self.mp[1,i], self.ids[i], color='red', size=10)
    #def drawExtended(self, ax, xshift=0, col='black'):
    #    ax.plot(self.xcycle+xshift, self.ycycle, color=col)
    #    ax.scatter(self.solution[0], self.solution[1], color=col, s=40)
    #    for i in range(len(self.x)):
    #        ax.text(self.mp[0,i], self.mp[1,i], self.ids[i], color='red', size=10)

    def drawExtended(self, ax, xshift=[0], labels=True, col='black'):
        if np.min(self.exitID) > 0:
            for xs in xshift:
                ax.plot(self.x[0:(self.exitID[0]+1)]+xs, self.y[0:(self.exitID[0]+1)], color=col)
                ax.plot(self.xcycle[(self.exitID[0]+1):(self.exitID[1]+1)]+xs, self.y[(self.exitID[0]+1):(self.exitID[1]+1)], color=col)
                # Draw the periodic boundary
                ax.plot([self.x[self.exitID[0]]+xs, self.x[self.exitID[0]+1]+xs], 
                        [self.y[self.exitID[0]], self.y[self.exitID[0]+1]], 
                        linestyle='dashed', color='gray', alpha=0.3)
                ax.plot([self.x[self.exitID[1]]+xs, self.xcycle[self.exitID[1]+1]+xs], 
                        [self.y[self.exitID[1]], self.ycycle[self.exitID[1]+1]], 
                        linestyle='dashed', color='gray', alpha=0.3)
        else:
            print("ERROR: Exit ID of 0 not implemented.")
        if labels:
            for i in range(len(self.x)):
                ax.text(self.mp[0,i], self.mp[1,i], self.ids[i], color='red', size=10)

    def print(self):
        print("Intersection point: (" + str(round(self.solution[0],3)) + "," + str(round(self.solution[1],3)) + ")." + ". Previous ttc = " + str(round(self.solution[2],3)) + ". ID = " + str(round(self.solution[3],3)) + ".")
        #print("Intersection point: ({:.3f},{:.3f}). Previous ttc = {:.3f}. ID = {:}".format(self.solution))

    # CW or CCW polygonal vertices
    def isClockwise(self):
        edgeSum = 0.
        for i in range(len(self.x)): 
            edgeSum += (self.xcycle[i+1] - self.xcycle[i])*(self.ycycle[i+1] + self.ycycle[i])
        return edgeSum > 0.

    def getInwardNormals(self):
        iN = np.empty([len(self.x), 2])
        if self.isClockwise():
            self.xcycle = self.xcycle[::-1]
            self.ycycle = self.ycycle[::-1]
        for i in range(len(self.x)):
            iN[i] = np.array([-(self.ycycle[i+1] - self.ycycle[i]), self.xcycle[i+1] - self.xcycle[i]]) 
            iN[i] = iN[i] / np.sqrt(iN[i].dot(iN[i]))
        return iN

    # Returns the segment that @ray passes through AND 
    # sets the 'solution' (collision coordinates and distance to collision)
    def whichIntersected(self, ray):
        ttc = math.inf
        ttc_previous = self.solution[2]
        for i in range(len(self.x)):
            v1 = np.dot(ray.vect, self.inwardNormal[i])
            if (v1 > 0.):
                continue 
            A = np.array([self.xcycle[i],   self.ycycle[i]])
            B = np.array([self.xcycle[i+1], self.ycycle[i+1]])
            v2 = np.dot(A - ray.p, self.inwardNormal[i])
            if (v2 > 0.):
                continue
            ttc_current = v2 / v1
            cp = ray.p + ttc_current * ray.vect
            midpt = (A + B) / 2.
            dtc = np.sqrt(np.sum(np.square(cp - midpt)))
            half_length = np.sqrt(np.sum(np.square(A - midpt)))
            if (dtc > half_length):
                continue
            # Smallest collision point that is greater than the previous
            if (ttc_current < ttc and ttc_current > ttc_previous):
                ttc = ttc_current
                self.currID = i 
                self.solution = [cp[0], cp[1], ttc, self.currID]
        return self.currID


