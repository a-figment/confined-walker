import math
import numpy as np
import matplotlib.pyplot as plt
#from matplotlib import pyplot
#import unicodedata as ud 
import Polygon as polygon

# This file implements a few different elementary cells. Each function must return a polygon.ClosedPolygon object.

# --------------- RECTANGULAR CHANNEL -----------------------
# Parallel channels have an upper and lower internal angle 0<@alpha<=\pi
# and are separated by a fixed vertical width @d. The total horizontal 
# span of the cell is 1 unit and the height of scatterers are 
# @factor Multiply @d by dy = dx * 1/math.tan(alpha/2.) 
# @show Draw the selected cell and show to user.
def getRectangularChannel(width, dx=1/2., show=False):
    #alpha = math.pi/3. # HERE
    # Note CCW ordering 
    #x = np.array([0., dx, 2.*dx, 2.*dx, dx, 0.])
    #y = np.array([0., 0, 0., d, d, d])
    y = np.array([0., 0., width, width])
    x = np.array([-dx, dx, dx, -dx])
    ids = np.array(['0','R','1','L']) 
    exitIDs = np.array([1, 3])
    #exitIDs = np.array([8, 8])
    Cell = polygon.ClosedPolygon(x, y, ids, exitIDs, 0.)

    print("Generated rectangular channel with W = " + str(width) + 
          " and \u03B4x = " + '{0:.5g}'.format(dx))
    if show:
        fig, ax = plt.subplots()
        ax.set_aspect(1)
        Cell.draw(ax)
        plt.show()
    return Cell

# --------------- PARALLEL CHANNEL -----------------------
# Parallel channels have an upper and lower internal angle 0<@alpha<=\pi
# and are separated by a fixed vertical width @d. The total horizontal 
# span of the cell is 1 unit and the height of scatterers are 
# @factor Multiply @d by dy = dx * 1/math.tan(alpha/2.) 
# @show Draw the selected cell and show to user.
def getParallelChannel(alpha, d, factor=1., dx=1/2., show=False):
    #alpha = math.pi/3. # HERE
    dy = dx * 1./math.tan(alpha/2.)
    d = factor * dy
    # Note CCW ordering 
    x = np.array([0., dx, 2.*dx, 2.*dx, dx, 0.])
    y = np.array([0., dy, 0., d, d+dy, d])
    ids = np.array(['0','1','R','3','4','L']) 
    exitIDs = np.array([2, 5])
    #exitIDs = np.array([10, 10])
    Cell = polygon.ClosedPolygon(x, y, ids, exitIDs, 0.)

    print("Generated parallel channel with \u03B1 = " + '{0:.5g}'.format(alpha) + 
          ", d = " + '{0:.5g}'.format(d) + 
          " and \u03B4y = " + '{0:.5g}'.format(dy))
    if show:
        fig, ax = plt.subplots()
        ax.set_aspect(1)
        Cell.draw(ax)
        plt.show()
    return Cell

def getStar(center, r_out, r_inner, num_points, show=False):
    angle = np.pi / num_points
    points = []
    x,y = [], []
    for i in range(2 * num_points):
        r = r_out if i % 2 == 0 else r_inner
        theta = i * angle
        x.append(center[0] + r * np.cos(theta))
        y.append(center[1] + r * np.sin(theta))
    exitIDs = np.array([None, None])
    ids = np.array([str(i) for i in range(1, 2*num_points + 1)])
    print(ids)
    Cell = polygon.ClosedPolygon(x,y,ids,exitIDs,0.)
    if show:
        fig, ax = plt.subplots()
        ax.set_aspect(1)
        Cell.draw(ax)
        plt.show()
    return Cell

# --------------- EPSILON BOTTOM CHANNEL -----------------------
# Non-parallel channel with fixed upper internal angle and lower internal angle @epsilon+@alpha
# and are separated by a fixed vertical width @d.  
# @show Draw the selected cell and show to user.
def getEpsilonBottomChannel(alpha, d, epsilon=0., dx=1/2., show=False):
    #alpha = math.pi/3. # HERE
    dy_upper = dx * 1/math.tan(alpha/2.)
    dy_lower = dx * 1/math.tan((alpha+epsilon)/2.)
    # Note CCW ordering 
    x = np.array([0., dx, 2.*dx, 2.*dx, dx, 0.])
    y = np.array([0., dy_lower, 0., d, d+dy_upper, d])
    ids = np.array(['0','1','R','3','4','L']) 
    exitIDs = np.array([2, 5])
    Cell = polygon.ClosedPolygon(x, y, ids, exitIDs, 0)

    print("Generated epsilon-bottom parallel channel with \u03B1 = " + '{0:.5g}'.format(alpha) + 
          ", d = " + '{0:.5g}'.format(d) + 
          " and \u03B5 = " + '{0:.5g}'.format(epsilon))
    fig, ax = plt.subplots()
    if show:
        ax.set_aspect(1)
        Cell.draw(ax)
        plt.show()
    return Cell


## --------------- FLAT BOTTOM CHANNEL -----------------------
#alpha = math.pi/2. # HERE
#dx = 1/2.
#dy = dx * 1/math.tan(alpha/2.)
#d = dy
#print("Chosen parameters: alpha = " + str(alpha) + ", d = " + str(d) + ", dy = " + str(dy))
## Note CCW ordering 
#x = np.array([0., dx, 2.*dx, 2.*dx, dx, 0.])
#y = np.array([0., 0., 0., d, d+dy, d])
#ids = np.array(['0','1','2','3','4','5']) 
#Cell = polygon.ClosedPolygon(x, y, ids, np.array([2, 5]), 0)
# --------------------------------------------------------

# ------ NON PARALLEL CHANNEL (Sanders, 2006) ------
#dx = 1.
#h1 = [0.3, 0.4, 0.5, 0.61, 0.71]
#hid = 4
#d = h1[hid]
#h2 = 0.77
#h3 = 0.45
#x = np.array([0., dx, 2.*dx, 2.*dx, dx, 0.])
#y = np.array([0., h3, 0., d, d + h2, d])
#ids = np.array(['0','1','2','3','4','5']) 
#Cell = polygon.ClosedPolygon(x, y, ids, np.array([2, 5]), 0)
# --------------------------------------------------

# -------------- RANDOM VERTICES CHANNEL --------------
#d = 1/4.
#x = np.array([0., np.random.uniform(0.,1.), 1., 1., np.random.uniform(0.,1.), 0.])
#y = np.array([0., np.random.uniform(0.2,1/2.), 0., d, d+np.random.uniform(0.4,1/2.), d])
#x = np.array([0., 0.6, 1., 1., 0.41, 0.])
#y = np.array([0., 0.32, 0., d, d+0.44, d])
#ids = np.array(['0','1','2','3','4','5']) 
#Cell = ClosedPolygon(x, y, ids, np.array([2, 5]), 0)
# --------------------------------------------------

