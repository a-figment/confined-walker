import sys
import math
import string
import random
import hashlib
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib import pyplot
from shapely.geometry import LineString, Point, Polygon
from scipy.optimize import curve_fit

# MY CLASSES
import Cells as cell_select
import Plots as myplots
import Walker as walker

###### MSD CALCULATIONS FOR VARYING APERTURE ######
def MSDvAperture(M=10, apertures=math.pi/2, fact=1., times=[0]):
    
    slopes = []
    for i in range(len(apertures)):
        pc = cell_select.getParallelChannel(alpha=apertures[i], d=0, factor=fact, show=False)
        msd = getEnsembleAverage(M, pc, stepSize, nSteps*stepSize, times)
        slope, msd_fit = getMSDFit(times[4:len(times)], msd[4:len(times)])
        slopes.append(slope)

        fig, ax = plt.subplots()
        ax.set_title('MSD fits')
        ax.set_xlabel('x')
        ax.set_ylabel('MSD')
        ax.set_yscale('log')
        ax.set_xscale('log')
        ax.plot(times, msd, marker='o')
        ax.plot(times[4:len(times)], np.exp(msd_fit), color='black', linewidth=0.5)
        plt.show()
        print(slope)

    return slopes

def getPointsAtTimeT(x, y, T):
   # Compute the cumulative distances along the polyline
   segment_lengths = np.sqrt(np.diff(x)**2 + np.diff(y)**2)
   cumulative_lengths = np.insert(np.cumsum(segment_lengths), 0, 0)
   
   # Initialize the output arrays
   xp = np.zeros(len(T))
   yp = np.zeros(len(T))
   # For each length in T, find the corresponding point on the polyline
   for i, t in enumerate(T):
        # Find the segment that contains the point
        idx = np.searchsorted(cumulative_lengths, t) - 1
        # Linear interpolation between the two points of the segment
        t0, t1 = cumulative_lengths[idx], cumulative_lengths[idx + 1]
        alpha = (t - t0) / (t1 - t0)
        xp[i] = (1 - alpha) * x[idx] + alpha * x[idx + 1]
        yp[i] = (1 - alpha) * y[idx] + alpha * y[idx + 1]
   return xp, yp

"""
Generates @M trajectories and computes the ensemble average of x-position
TODO: Consider a running average computation
"""
def getEnsembleAverage(M, polygon, stepSize, T, interpolatingTimes):
    xs = []
    for i in range(M):
        x,y,_,cellID,_,_ = walker.getWalkerTrajectory(polygon, stepSize, T)
        X = x+np.array(cellID)
        xp, _ = getPointsAtTimeT(X,y,interpolatingTimes)
        xs.append(xp)
    mat = np.array(xs)
    return np.mean(mat**2, axis=0)

def linear_func(x, a, b):
    return a * x + b

def getMSDFit(t, x):
    # Perform linear fit on the log-log data
    popt, pcov = curve_fit(linear_func, np.log(t), np.log(x))
    # Extract the fit parameters (slope and intercept)
    slope, intercept = popt
    # Calculate the fitted MSD on a log-log scale
    fitted_msd = linear_func(np.log(t), slope, intercept)
    return slope, fitted_msd


# Polygon
#pc = cell_select.getRectangularChannel(width=0.1, dx=0.5, show=False)

pc = cell_select.getParallelChannel(alpha=math.pi/2., d=1, factor=1, show=False)

# Star billiard
#pc = cell_select.getStar([0., 0.], 5., 2.5, 25, show=False)


# Walker parameters
nSteps = 100
stepSize = 0.01

start_time = time.time()
x,y,a,cellID,edges,pbc_indices = walker.getWalkerTrajectory(pc, stepSize, nSteps * stepSize)
print("--- Run time: %s seconds ---" % (time.time() - start_time))
X = x + np.array(cellID)
Y = y
# This removes points recorded on the PBC
X = X[pbc_indices == 0]
Y = Y[pbc_indices == 0]
print("Total time = " + str(round(np.sum(np.sqrt((np.diff(X))**2 + np.diff(Y)**2)),4)) + ", target time = " + str(stepSize*nSteps))
myplots.PlotSampleTrajectory(pc, X, Y, xlimits=[-4,4])
plt.plot(range(len(X)), X, color='black')
plt.show()

n_walkers = 1000
times = [10, 100, 1000]
stepSize = 1
nSteps = max(times)
displacements = {t: [] for t in times}

for _ in range(n_walkers):
    x, y, a, cellID, edges, pbc_indices = walker.getWalkerTrajectory(pc, stepSize, nSteps * stepSize)
    X = x + np.array(cellID)
    Y = y
    # This removes points recorded on the PBC
    X = X[pbc_indices == 0]
    Y = Y[pbc_indices == 0]
    print("Total time = " + str(round(np.sum(np.sqrt((np.diff(X))**2 + np.diff(Y)**2)),4)) + ", target time = " + str(stepSize*nSteps))
    for t in times:
        dx = X[t] - X[0]
        displacements[t].append(dx)

#print(displacements)
# build normalized distributions P(x,t)
bins = np.linspace(-20, 50, 200)
for t in times:
    hist, edges = np.histogram(displacements[t], bins=bins, density=True)
    centers = 0.5 * (edges[:-1] + edges[1:])
    plt.step(centers, hist, where='mid', label=f"t={t}")

plt.xlabel("Displacement x")
plt.ylabel("P(x,t)")
plt.legend()
plt.show()


num_bins = 200
#data_min = np.min(displacements)
#data_max = np.max(displacements)
#bins = np.logspace(np.log(data_min), np.log(data_max), num_bins)
bins = np.logspace(np.log(1), np.log(100), num_bins)
bin_centers = np.sqrt(bins[:-1] * bins[1:])  # geometric mean of edge

# Plot histogram curves for each column
for t in times:
    ti = t
    counts, _ = np.histogram(displacements[t], bins=bins, density=True)  # probability density
    mask = (counts > 0) & np.isfinite(counts)
    plt.step(bin_centers[mask], counts[mask], label=f"t={t}")

plt.xscale("log")
plt.yscale("log")
plt.xlabel("Value")
plt.ylabel("Probability density")
plt.title("Time-varying probability distributions (histogram curves)")
plt.xlim([1, np.max(times)])
plt.legend()
plt.show()


#apertures = np.linspace(math.pi/5, 4*math.pi/5., 5)
#print(apertures)
##print("Simulating angles alpha = {:.3f}".format(apertures))
##times = np.array([1.,10.,100.,500.,1000.,2000.,4000.,6000.,8000.,10000.])
#times = np.array([1.,10.,50.,100.,200.,300.,400.,500.,600.,700.,800.,900.,1000.])
#slopes = MSDvAperture(M=1000, apertures=apertures, fact=0.75, times=times)
#
#plt.title('MSD scaling vs. aperture angle')
#plt.xlabel('\u03B1')
#
#n = 7  # For example, starting with π/7
#denominators_first_half = np.arange(n, 1, -1)  # Sequence from n to 2
#tick_positions_first_half = np.pi / denominators_first_half
#numerators_second_half = np.arange(2, n + 1)  # Sequence from 2 to n
#denominators_second_half = numerators_second_half + 1  # Corresponding denominators
#tick_positions_second_half = numerators_second_half * np.pi / denominators_second_half
#tick_positions = np.concatenate((tick_positions_first_half, tick_positions_second_half))
#tick_labels_first_half = [r'$\frac{{\pi}}{{{}}}$'.format(d) for d in denominators_first_half]
#tick_labels_second_half = [r'$\frac{{{}\pi}}{{{}}}$'.format(num, denom) for num, denom in zip(numerators_second_half, denominators_second_half)]
#tick_labels = tick_labels_first_half + tick_labels_second_half
#
#plt.xticks(tick_positions,tick_labels)
#plt.ylabel('MSD scaling')
#plt.grid()
#plt.plot(apertures, slopes)
#plt.show()


###### COMPARING MSD SCALINGS FOR DIFFERENT STEP LENGTHS ######
#M = 1000
#stepsizes = np.linspace(0.5, 100, 5)
#slopes = []
#for i in range(len(stepsizes)):
#    print(i)
#    means = getEnsembleAverage(M, pc, nSteps, stepsizes[i], T)
#    time = range(50, len(means))
#    slope, msd_fit = getMSDFit(time, means[time])
#    slopes.append(slope)
#    
#    #fig, ax = plt.subplots()
#    #ax.set_title('MSD for walker in rectangular channel')
#    #ax.set_xlabel('x')
#    #ax.set_ylabel('MSD')
#    #ax.set_yscale('log')
#    #ax.set_xscale('log')
#    #ax.plot(range(nSteps), means)
#    #ax.plot(time, np.exp(msd_fit), color='black', linewidth=0.5)
#    #ax.legend(['L = 10W', 'L = W', 'L = W/10'])
#    #plt.show()
#
## Plot slopes as a function of step size
#fig, ax = plt.subplots()
#ax.set_title('MSD vs. step size')
#ax.set_xlabel('L')
#ax.set_ylabel('MSD slope')
#ax.plot(stepsizes, slopes)
#plt.show()
###############################################################


