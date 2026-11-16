import math
import numpy as np
import matplotlib.pyplot as plt
import time


def PlotExtendedChannel(pc, xlimits=[-2,2], isExtended=True, showSegmentLengths=False):

    fig, ax = plt.subplots()
    ax.set_aspect(1)
    ax.set_title('Confined walker')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_xlim(xlimits)
    pc.drawExtended(ax,[-3,-2,-1,0,1,2,3], labels=False)
    return ax
    #plt.show()

def PlotSampleTrajectory(pc, X,Y, xlimits=[-2,2], isExtended=True, showSegmentLengths=False):

    #print("edges = " + str(edges))
    #print("cids  = " + str(cellID))
    #print("PBCSI = " + str(pbc_indices))
    #print("x     = " + str(X))
    
    x_diameter = np.max(pc.x) - np.min(pc.x)
    #print([x*x_diameter for x in cls])
    fig, ax = plt.subplots()
    ax.set_aspect(1)
    ax.set_title('Confined walker')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_xlim(xlimits)
    if isExtended:
        cls = [-3,-2,-1,0,1,2,3]
        pc.drawExtended(ax,[x*x_diameter for x in cls], labels=False)
    else:
        pc.draw(ax, 'black')

    if len(X) > 100:
        X = X[0:100]
        Y = Y[0:100]

    ax.scatter(X, Y, s=10, marker='o', color='red')
    ax.plot(X, Y, color='green')
    ax.scatter(X, Y, s=10, marker='o', color='red')
    if showSegmentLengths:
        cumul = 0
        for i in range(len(X)-1):
            dist = np.sqrt((X[i]-X[i+1])**2 + (Y[i]-Y[i+1])**2)
            cumul = cumul + dist
            ax.text(X[i],Y[i],str(i))
            ax.text((X[i]+X[i+1])/2., (Y[i]+Y[i+1])/2., str(round(dist,3)) + ", " + str(round(cumul,3)), fontsize=8, color='blue')
        for i in range(len(X)):
            ax.text(X[i],Y[i],str(i), fontsize=6)
    #return ax
    plt.show()
    plt.savefig('sample.png', dpi=100)


