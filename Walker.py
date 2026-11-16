import numpy as np
from matplotlib import pyplot
from shapely.geometry import LineString, Point, Polygon
import random

import Ray as myray
import Polygon as mypolygon

"""
The jump algorithm. Can readily alter the way @ang or @length is determined.
"""
def jump(xOld, yOld, ang, length):
    v_new = np.array([xOld + np.cos(ang) * length, yOld + np.sin(ang) * length])
    v_new /= np.linalg.norm(v_new)
    return v_new[0], v_new[1]
    #return xOld + np.cos(ang) * length, yOld + np.sin(ang) * length


"""
@(x,y) is a point in @poly and @ang is some random test direction. 
If @(x,y,ang) intersects @poly at a distance @dtc from @(x,y) and 
this distance is greater than @stepLength, we can be sure that the 
new point is a valid one and that the segment is indeed contained within the polygon
"""
def segmentInPolygon(poly, x, y, ang, stepLength):
    r = myray.Ray(x, y, ang)
    poly.solution = [None, None, 0, -1] # Flush solution
    null = poly.whichIntersected(r) # sets the solution
    dtc = np.sqrt(np.sum(np.square(r.p - [poly.solution[0], poly.solution[1]])))
    return dtc > stepLength

def Collide(polygon,ray):
    polygon.solution = [None, None, 0, -1]
    edgeID = polygon.whichIntersected(ray)
    return edgeID, polygon.solution[0], polygon.solution[1] 

"""
If the walker experiences a collision, the available directions for its next nSteps
are determined by the inward normal taken at the collision point. CCW ordering is assumed.
"""
def getAngleFromEdge(polygon, edgeID):
    angleToNormal = np.arctan2(polygon.inwardNormal[edgeID][1], polygon.inwardNormal[edgeID][0])
    return np.random.uniform(angleToNormal - np.pi / 2., angleToNormal + np.pi / 2.)
    #ntheta = angleToNormal
    #proposal = 0
    #print(f"{ntheta*180/np.pi}")
    #if np.cos(ntheta) > 0. and np.sin(ntheta) > 0.:
    #    proposal = np.random.uniform(ntheta - np.pi/2., ntheta)
    #elif np.cos(ntheta) > 0. and np.sin(ntheta) < 0.:
    #    proposal = np.random.uniform(ntheta, 0.)
    #elif np.cos(ntheta) < 0. and np.sin(ntheta) > 0.:
    #    proposal = np.random.uniform(ntheta, ntheta + np.pi/2.)
    #elif np.cos(ntheta) < 0. and np.sin(ntheta) < 0.:
    #    proposal = np.random.uniform(ntheta, ntheta + np.pi/2.)
    #else:
    #    print("ERROR")
    #return proposal

def sample_component_magnitude(v0=1, alpha=100):
    # alpha > 0
    u = random.random()  # in [0,1)
    return v0 * (u ** (1.0/alpha))

#def soft_bounce_velocity(v0, alpha, normal):
#def getAngleFromEdge(polygon, edgeID):
#    angleToNormal = np.arctan2(polygon.inwardNormal[edgeID][1], polygon.inwardNormal[edgeID][0])
#    # normal: 2D numpy array, unit vector pointing OUT of the wall (i.e. into domain)
#    # returns new velocity vector (numpy array)
#    # build tangent (rotate normal by +90 degrees)
#    normal = polygon.inwardNormal[edgeID]
#    n = np.array(normal, dtype=float)
#    t = np.array([-n[1], n[0]])
#
#    # sample magnitudes
#    v0 = 1.
#    alpha = 20
#    mag_t = sample_component_magnitude(v0, alpha)
#    mag_n = sample_component_magnitude(v0, alpha)
#
#    # sign for tangential component: ± equally likely
#    sign_t = 1.0 if random.random() < 0.5 else -1.0
#    v_t = sign_t * mag_t
#    #v_t = mag_t
#
#    # ensure normal component points away from the wall (dot with normal > 0)
#    # i.e., normal basis component should be positive
#    v_n = mag_n  # choose positive
#
#    # combine in local frame then to global
#    v_new = v_t * t + v_n * n
#    return np.arctan2(v_new[1], v_new[0])

# Example usage inside collision handler:
# assume pos, vel known, and wall_normal computed (unit)
# new_vel = soft_bounce_velocity(v0=1.0, alpha=0.8, normal=wall_normal)



def getAngle(polygon, hadCollision, edgeID):
    if hadCollision:
        return getAngleFromEdge(polygon, edgeID)
    else:
        return np.random.uniform(-np.pi/2., 3*np.pi/2.)

def getRandomICInPolygon(mypolygon, poly):
    # Bounding box coordinates
    sw_x,sw_y = np.min(mypolygon.x),np.min(mypolygon.y)
    ne_x,ne_y = np.max(mypolygon.x),np.max(mypolygon.y)
    while True:
        xTest = np.random.uniform(sw_x, ne_x)
        yTest = np.random.uniform(sw_y, ne_y)
        testPoint = Point(xTest, yTest)
        if poly.contains(testPoint):
            break
    return xTest, yTest, np.random.uniform(-np.pi/2., 3*np.pi/2.)

def isClose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def getDistanceToJump(hadCollision, stepSize, currentTotalTime):
    if hadCollision:
        return stepSize - (currentTotalTime % stepSize) 
    else:
        return stepSize

"""
To add dissolution-precipitation, should only need the current contour of the discretised polygon.
Whenever there is a collision, just check if the position is within one of those blocks 
"""

def getWalkerTrajectory(mypolygon, stepSize, T):

    # This is a shapely.geometry polygon. Its only use to is check for point-in-polygon
    poly = Polygon(list(zip(mypolygon.x,mypolygon.y)))

    # Random point in the interior of @mypolgon 
    x0,y0,a0 = getRandomICInPolygon(mypolygon, poly)
    x,y,a = np.array([x0]),np.array([y0]),np.array([a0])

    # Loop variables
    cid, cellID,edges,pbc_indices = 0,[0],[5],np.array([0])
    trajectoryLength, lastJumpLength = 0., 0.
    freePathLengths = np.array([0.])
    i = 1
    hadCollision = False
    edgeID = -1
    while trajectoryLength < T:

        # Determine distance to jump
        cumulTime = np.cumsum(freePathLengths)
        distanceToJump = getDistanceToJump(hadCollision, stepSize, cumulTime[-1])
        if distanceToJump + cumulTime[-1] > T+stepSize/2.:
            break

        # Jump to a new position
        xNew, yNew = jump(x[i-1], y[i-1], a[i-1], distanceToJump)
       
        # Handle collisions
        if not poly.contains(Point(xNew, yNew)): # Not in poly => a collision occurred
            edgeID,xNew,yNew = Collide(mypolygon, myray.Ray(x[i-1], y[i-1], a[i-1]))
            hadCollision = True 
        else:                                    # Point in polygon 
            # New point is in polygon and segment formed from prev. point is also in poly. 
            if segmentInPolygon(mypolygon, x[i-1], y[i-1], a[i-1], distanceToJump):
                hadCollision = False 
            else: # Segment crosses a corner after having a regular collision => collision occurred 
                edgeID,xNew,yNew = Collide(mypolygon, myray.Ray(x[i-1], y[i-1], a[i-1]))
                hadCollision = True 

        # Handle periodic boundary conditions
        if hadCollision:
            if edgeID == mypolygon.exitID[1]: #LHS PB
                xNew, angle, cid = 1., a[i-1], -1.
                pbc_indices = np.append(pbc_indices, 1)  
            elif edgeID == mypolygon.exitID[0]: #RHS PB
                xNew, angle, cid = 0., a[i-1], 1.
                pbc_indices = np.append(pbc_indices, 1)  
            else:
                angle = getAngleFromEdge(mypolygon, edgeID)
                cid = 0
                pbc_indices = np.append(pbc_indices, 0)  
        else:
            angle = np.random.uniform(-np.pi/2., 3*np.pi/2.)
            cid = 0
            pbc_indices = np.append(pbc_indices, 0)  

        # Update trajectory data. TODO: Create a trajectory class
        a = np.append(a,angle)
        x = np.append(x,xNew)
        y = np.append(y,yNew)
        cellID.append(cellID[i-1] + cid)
        edges.append(edgeID)
        #mypolygon.solution = [None, None, 0, -1] # Flush solution
        
        lastJumpLength = np.linalg.norm(np.array([x[i]+cellID[i], y[i]]) - np.array([x[i-1]+cellID[i-1], y[i-1]]))
        trajectoryLength = trajectoryLength + lastJumpLength
        freePathLengths = np.append(freePathLengths, lastJumpLength)

        i = i + 1
        #if (i % 10 == 0):
        #    print(f"Iterate {i} completed.")
    return x,y,a,cellID,edges,pbc_indices
