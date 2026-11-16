
"""
Generates a random walk of @nSteps or length @T bounded/confined to @polygon.
RETURNS: 1D vectors of x and y positions, velocity angles, cell id's (for open billiards) 
and the edges touched
TODO: Allow custom automated selection of `nStep' runs or `T' runs
"""
def getWalkerTrajectory(polygon, stepSize, T):

    x,y,a = [0.],[np.random.uniform(0., 1.)],[0.] # CAREFUL WITH THE INITIAL Y-VALUE!
    #y = [np.random.uniform(0, polygon.y[3]-polygon.y[2])] # Channel initial conditions
    cellID = [0] 
    edges = [5] 
    pbc_indices = [0] # 0 -> not on PBC (ignored for the start position)

    # Loop variables
    i = 1
    hadCollision = False
    edgeID = -1
    cid = 0 # cell id
    trajectoryLength = 0
    lastJumpLength = 0
    #while i <= nSteps:
    while trajectoryLength < T:
        print("TL = " + str(trajectoryLength))
        # The walker jumps one step
        xNew, yNew, angle = None, None, None
        
        #   
        distanceToJump = stepSize - lastJumpLength 
        if distanceToJump < 0.:
            distanceToJump = stepSize

        print("DTJ = " + str(distanceToJump))
        if i == 1:
            #angle = np.random.uniform(-np.pi/2., np.pi/2.)
            angle = 0.0001
            xNew,yNew = jump(x[i-1], y[i-1], angle, distanceToJump)
            cid = 0 # check what happens if infinite horizon
        elif hadCollision:
            if edgeID == polygon.exitID[1]: #LHS PB
                x[i-1], angle, cid = 1., a[i-1], -1.
                xNew, yNew = jump(1., y[i-1], a[i-1], distanceToJump)
                pbc_indices.append(1)  
            elif edgeID == polygon.exitID[0]: #RHS PB
                x[i-1], angle, cid = 0., a[i-1], 1.
                xNew, yNew = jump(0., y[i-1], a[i-1], distanceToJump)
                pbc_indices.append(1)   
            else:
                angle = getAngleFromEdge(polygon, edgeID)
                xNew, yNew = jump(x[i-1], y[i-1], angle, distanceToJump)
                cid = 0
                pbc_indices.append(0)  
        else:
            angle = np.random.uniform(-np.pi/2., 3*np.pi/2.)
            xNew,yNew = jump(x[i-1], y[i-1], angle, distanceToJump)
            cid = 0
            pbc_indices.append(0)   
    
        #print(str(edgeID) + ', ' + str(x[i-1]) + ', ' + str(y[i-1]) + ', ' + str(a[i-1]*180/np.pi))
        # Trajectory data
        x.append(xNew)
        print("x new = " + str(xNew))
        y.append(yNew)
        a.append(angle)
        cellID.append(cellID[i-1] + cid)
        edges.append(edgeID)
    
        
        if not poly.contains(Point(x[i], y[i])): # Not in polygon => a collision occurred
            r = myray.Ray(x[i-1], y[i-1], angle) # This is the ray from the other PBC
            hadCollision = True 
            edgeID = polygon.whichIntersected(r)
            x[i],y[i] = polygon.solution[0], polygon.solution[1] # Current position is now a point on the boundary. This overwrite the above append
            #polygon.solution = [None, None, 0, -1]
        else: # Current walker position is in polygon but need to ensure no boundary crossings for non-convex domains
            while True: # If current walker position is not valid (e.g. crosses a corner), repeatedly propose new positions until valid
                if hadCollision: # If walker is jumping from an edge and 
                    if poly.contains(Point(xNew,yNew)) and segmentInPolygon(polygon, x[i-1], y[i-1], angle, distanceToJump):
                        break
                    angle = getAngleFromEdge(polygon, edgeID)
                    xNew,yNew = jump(x[i-1], y[i-1], angle, distanceToJump)
                else:
                    if poly.contains(Point(xNew,yNew)) and segmentInPolygon(polygon, x[i-1], y[i-1], angle, distanceToJump):
                        break
                    angle = np.random.uniform(-np.pi/2., 3*np.pi/2.)
                    xNew,yNew = jump(x[i-1], y[i-1], angle, distanceToJump)
                x[i],y[i],a[i] = xNew, yNew, angle
            hadCollision = False
    
        polygon.solution = [None, None, 0, -1] # Flush solution
        lastJumpLength = np.sqrt((x[i]-x[i-1])**2 + (y[i]-y[i-1])**2)
        trajectoryLength = trajectoryLength + lastJumpLength
        i = i + 1
    print(x)
    return x,y,a,cellID,edges,pbc_indices


"""
Generates a random walk of @nSteps or length @T bounded/confined to @polygon.
RETURNS: 1D vectors of x and y positions, velocity angles, cell id's (for open billiards) 
and the edges touched
TODO: Allow custom automated selection of `nStep' runs or `T' runs
"""
def getWalkerTrajectoryNEWER(mypolygon, poly, stepSize, T):

    x,y,a = [0.],[np.random.uniform(0., 1.)],[0.] # CAREFUL WITH THE INITIAL Y-VALUE!
    #y = [np.random.uniform(0, mypolygon.y[3]-mypolygon.y[2])] # Channel initial conditions
    cellID = [0] 
    edges = [5] 
    pbc_indices = [0] # 0 -> not on PBC (ignored for the start position)

    # Loop variables
    i = 1
    hadCollision = False
    edgeID = -1
    cid, trajectoryLength, lastJumpLength = 0, 0., 0.
    while trajectoryLength < T:
        #print("TL = " + str(trajectoryLength))
        xNew, yNew, angle = None, None, None

        #   
        distanceToJump = stepSize - lastJumpLength 
        if distanceToJump < 0.:
            distanceToJump = stepSize

        print("DTJ = " + str(distanceToJump))

        # Propose the new jump location
        if i == 1:
            angle = np.random.uniform(-np.pi/2., np.pi/2.)
            xNew,yNew = jump(x[i-1], y[i-1], angle, distanceToJump)
            cid = 0 # check what happens if infinite horizon
        elif hadCollision:
            if edgeID == mypolygon.exitID[1]: #LHS PB
                x[i-1], angle, cid = 1., a[i-1], -1.
                xNew, yNew = jump(1., y[i-1], a[i-1], distanceToJump)
                pbc_indices.append(1)  
            elif edgeID == mypolygon.exitID[0]: #RHS PB
                x[i-1], angle, cid = 0., a[i-1], 1.
                xNew, yNew = jump(0., y[i-1], a[i-1], distanceToJump)
                pbc_indices.append(1)   
            else:
                angle = getAngleFromEdge(mypolygon, edgeID)
                xNew, yNew = jump(x[i-1], y[i-1], angle, distanceToJump)
                cid = 0
                pbc_indices.append(0)  
        else:
            angle = np.random.uniform(-np.pi/2., 3*np.pi/2.)
            xNew,yNew = jump(x[i-1], y[i-1], angle, distanceToJump)
            cid = 0
            pbc_indices.append(0)   

        # Assume proposed jump is valid
        x.append(xNew)
        y.append(yNew)
        a.append(angle)
        cellID.append(cellID[i-1] + cid)
        edges.append(edgeID)
    
        # Replace proposed jumps for if out-of-bounds or if crossing a corner
        if not poly.contains(Point(x[i], y[i])): # Not in mypolygon => a collision occurred
            r = myray.Ray(x[i-1], y[i-1], angle) # This is the ray from the other PBC
            hadCollision = True 
            edgeID = mypolygon.whichIntersected(r)
            x[i],y[i] = mypolygon.solution[0], mypolygon.solution[1] # Overwrite current pos. to be a point on the boundary
            mypolygon.solution = [None, None, 0, -1]
        else: # Current walker position is in mypolygon but need to ensure no corner crossings 
            K = 0
            while True: # Repeatedly propose new positions until valid
                print('stuck, edgeid = ' + str(edgeID))
                print(str(xNew) + " " + str(yNew))
                if poly.contains(Point(xNew,yNew)) and segmentInPolygon(mypolygon, x[i-1], y[i-1], angle, distanceToJump):
                    break
                angle = getAngle(mypolygon, hadCollision, edgeID)
                xNew,yNew = jump(x[i-1], y[i-1], angle, distanceToJump)
                print("(" + str(x[i-1]) + ", " + str(y[i-1]) + ")--(" + str(xNew) + "," + str(yNew) + ")")
                x[i],y[i],a[i] = xNew, yNew, angle
                #K = K + 1
                #if K > 5:
                #    plt.axes().set_aspect(1)
                #    plt.plot(mypolygon.xcycle, mypolygon.ycycle, linewidth=1)
                #    plt.plot(x,y)
                #    plt.show()
            hadCollision = False
        mypolygon.solution = [None, None, 0, -1] # Flush solution
        lastJumpLength = np.sqrt((x[i]-x[i-1])**2 + (y[i]-y[i-1])**2)
        #lastJumpLength = np.linalg.norm([x[i], y[i]] - [x[i-1], y[i-1]])
        trajectoryLength = trajectoryLength + lastJumpLength
        i = i + 1
    return x,y,a,cellID,edges,pbc_indices

# LATEST
def getWalkerTrajectory(mypolygon, poly, stepSize, T):

    fig, ax = plt.subplots(figsize=(10,10))
    ax.set_aspect(1)
    ax.set_xlim([-1,2])
    mypolygon.drawExtended(ax,-1)
    mypolygon.drawExtended(ax,0)
    mypolygon.drawExtended(ax,1)
    # Random point in the interior of @mypolgon 
    x0,y0,a0 = getRandomICInPolygon(mypolygon, poly)
    x,y,a = [x0],[y0],[a0] 

    # Loop variables
    cid, cellID,edges,pbc_indices = 0,[0],[5],[0]
    trajectoryLength, lastJumpLength = 0., 0.
    i = 1
    hadCollision = False
    edgeID = -1
    while trajectoryLength < T:

        xNew, yNew, angle = None, None, None
        distanceToJump = stepSize - lastJumpLength 
        if distanceToJump < 0.:
            distanceToJump = stepSize
        print("DTJ = " + str(distanceToJump))

        # Propose the new jump location
        if hadCollision:
            if edgeID == mypolygon.exitID[1]: #LHS PB
                x[i-1], angle, cid = 1., a[i-1], -1.
                xNew, yNew = jump(1., y[i-1], a[i-1], distanceToJump)
                pbc_indices.append(1)  
            elif edgeID == mypolygon.exitID[0]: #RHS PB
                x[i-1], angle, cid = 0., a[i-1], 1.
                xNew, yNew = jump(0., y[i-1], a[i-1], distanceToJump)
                pbc_indices.append(1)   
            else:
                angle = getAngleFromEdge(mypolygon, edgeID)
                xNew, yNew = jump(x[i-1], y[i-1], angle, distanceToJump)
                cid = 0
                pbc_indices.append(0)  
        else:
            angle = np.random.uniform(-np.pi/2., 3*np.pi/2.)
            xNew,yNew = jump(x[i-1], y[i-1], angle, distanceToJump)
            cid = 0
            pbc_indices.append(0)   

        # Assume proposed jump is valid
        x.append(xNew)
        y.append(yNew)
        a.append(angle)
        cellID.append(cellID[i-1] + cid)
        edges.append(edgeID)
    
        # Replace proposed jumps for if out-of-bounds or if crossing a corner
        if not poly.contains(Point(x[i], y[i])): # Not in mypolygon => a collision occurred
            r = myray.Ray(x[i-1], y[i-1], angle) # This is the ray from the other PBC
            edgeID = mypolygon.whichIntersected(r)
            x[i],y[i] = mypolygon.solution[0], mypolygon.solution[1] # Overwrite current pos. to be a point on the boundary
            #a[i] = a[i-1]
            mypolygon.solution = [None, None, 0, -1]
            hadCollision = True 
        else: # Current walker position is in mypolygon but need to ensure no corner crossings 
            K = 0
            while True: # Repeatedly propose new positions until valid
                if hadCollision: # If walker is jumping from an edge and 
                    if poly.contains(Point(xNew,yNew)) and segmentInPolygon(mypolygon, x[i-1], y[i-1], angle, distanceToJump):
                        break
                    angle = getAngleFromEdge(mypolygon, edgeID)
                    if edges[i-1] == 5 or edges[i-1] == 2:
                        angle = a[i-1]
                        print('true')
                    xNew,yNew = jump(x[i-1], y[i-1], angle, distanceToJump)
                    print("(" + str(x[i-1]) + ", " + str(y[i-1]) + ")--(" + str(xNew) + "," + str(yNew) + ")")
                    if K > 5:
                        X = x[0:(len(x)-1)]+np.array(cellID)[1:len(cellID)]
                        Y = y[0:(len(y)-1)]
                        ax.plot(X, Y, marker='o', markersize=3)
                        cumul = 0
                        ax.plot([X[len(X)-1], xNew], [Y[len(Y)-1], yNew], color='red')
                        ax.scatter(xNew, yNew, color='red')
                        for i in range(len(X)-1):
                            ax.text(X[i],Y[i],str(i))
                            dist = np.sqrt((X[i]-X[i+1])**2 + (Y[i]-Y[i+1])**2)
                            cumul = cumul + dist
                            ax.text((X[i]+X[i+1])/2., (Y[i]+Y[i+1])/2., str(round(dist,3)) + ", " + str(round(cumul,3)), fontsize=9, color='blue')
                        plt.show()
                else:
                    if poly.contains(Point(xNew,yNew)) and segmentInPolygon(mypolygon, x[i-1], y[i-1], angle, distanceToJump):
                        break
                    angle = np.random.uniform(-np.pi/2., 3*np.pi/2.)
                    xNew,yNew = jump(x[i-1], y[i-1], angle, distanceToJump)
                    x[i],y[i],a[i] = xNew, yNew, angle
                K = K + 1
            hadCollision = False
            #x[i],y[i],a[i] = xNew, yNew, angle
        mypolygon.solution = [None, None, 0, -1] # Flush solution
        #lastJumpLength = np.sqrt((x[i]-x[i-1])**2 + (y[i]-y[i-1])**2)
        lastJumpLength = np.linalg.norm(np.array([x[i], y[i]]) - np.array([x[i-1], y[i-1]]))
        trajectoryLength = trajectoryLength + lastJumpLength
        i = i + 1
    return x,y,a,cellID,edges,pbc_indices

# This works for finite step lengths but not if the billiard is very small. If it is small, then we get stuck in an infinite loop
# due to the radius about certain points not being contained in the billiard.
def getWalkerTrajectory(mypolygon, poly, stepSize, T):

    # Random point in the interior of @mypolgon 
    x0,y0,a0 = getRandomICInPolygon(mypolygon, poly)
    x,y,a = [x0],[y0],[a0] 

    # Loop variables
    cid, cellID,edges,pbc_indices = 0,[0],[5],[0]
    trajectoryLength, lastJumpLength = 0., 0.
    i = 1
    hadCollision = False
    edgeID = -1
    while trajectoryLength < T:

        xNew, yNew, angle = None, None, None
        distanceToJump = stepSize - lastJumpLength 
        if distanceToJump < 0.:
            distanceToJump = stepSize
        print("DTJ = " + str(round(distanceToJump,3)))

        # Propose the new jump location
        if hadCollision:
            if edgeID == mypolygon.exitID[1]: #LHS PB
                x[i-1], angle, cid = 1., a[i-1], -1.
                xNew, yNew = jump(1., y[i-1], a[i-1], distanceToJump)
                pbc_indices.append(1)  
            elif edgeID == mypolygon.exitID[0]: #RHS PB
                x[i-1], angle, cid = 0., a[i-1], 1.
                xNew, yNew = jump(0., y[i-1], a[i-1], distanceToJump)
                pbc_indices.append(1)   
            else:
                angle = getAngleFromEdge(mypolygon, edgeID)
                xNew, yNew = jump(x[i-1], y[i-1], angle, distanceToJump)
                cid = 0
                pbc_indices.append(0)  
        else:
            angle = np.random.uniform(-np.pi/2., 3*np.pi/2.)
            xNew,yNew = jump(x[i-1], y[i-1], angle, distanceToJump)
            cid = 0
            pbc_indices.append(0)   

        # Assume proposed jump is valid
        x.append(xNew)
        y.append(yNew)
        a.append(angle)
        cellID.append(cellID[i-1] + cid)
        edges.append(edgeID)
    
        # Replace proposed jumps for if out-of-bounds or if crossing a corner
        if not poly.contains(Point(x[i], y[i])): # Not in mypolygon => a collision occurred
            mypolygon.solution = [None, None, 0, -1]
            r = myray.Ray(x[i-1], y[i-1], angle) # This is the ray from the other PBC
            edgeID = mypolygon.whichIntersected(r)
            x[i],y[i] = mypolygon.solution[0], mypolygon.solution[1] # Overwrite current pos. to be a point on the boundary
            hadCollision = True 
        else: # Current walker position is in mypolygon but need to ensure no corner crossings 
            B = False
            while True: # Repeatedly propose new positions until valid
                if hadCollision and (edgeID == mypolygon.exitID[0] or edgeID == mypolygon.exitID[1]): # If walker is jumping from an edge and 
                    if poly.contains(Point(xNew,yNew)) and segmentInPolygon(mypolygon, x[i-1], y[i-1], angle, distanceToJump):
                        break
                        print("A")
                    else:
                        mypolygon.solution = [None, None, 0, -1]
                        r = myray.Ray(x[i-1], y[i-1], angle) # This is the ray from the other PBC
                        edgeID = mypolygon.whichIntersected(r)
                        xNew,yNew,angle = mypolygon.solution[0],mypolygon.solution[1],angle # Overwrite current pos. to be a point on the boundary
                        hadCollision = True 
                        B = True
                        DEBUG_PLOT(i, mypolygon,x,y,angle,cellID,xNew,yNew,distanceToJump)
                        mypolygon.print()
                        print("this" + str(mypolygon.solution[0]))
                        print("({:.3f},{:.3f})--({:.3f},{:.3f})".format(x[i-1],y[i-1],x[i],y[i]))
                        print("B")
                        break
                elif hadCollision:
                    if poly.contains(Point(xNew,yNew)) and segmentInPolygon(mypolygon, x[i-1], y[i-1], angle, distanceToJump):
                        break
                    angle = getAngleFromEdge(mypolygon, edgeID)
                    xNew,yNew = jump(x[i-1], y[i-1], angle, distanceToJump)
                    print("C")
                else:
                    if poly.contains(Point(xNew,yNew)) and segmentInPolygon(mypolygon, x[i-1], y[i-1], angle, distanceToJump):
                        break
                    angle = np.random.uniform(-np.pi/2., 3*np.pi/2.)
                    xNew,yNew = jump(x[i-1], y[i-1], angle, distanceToJump)
                    print("D")
            if not B:
                hadCollision = False
            x[i],y[i],a[i] = xNew, yNew, angle
        mypolygon.solution = [None, None, 0, -1] # Flush solution
        print("this" + str(xNew))
        #lastJumpLength = np.sqrt((x[i]-x[i-1])**2 + (y[i]-y[i-1])**2)
        #print("(" + str(x[i-1]) + ", " + str(y[i-1]) + ")--(" + str(x[i]) + "," + str(y[i]) + ")")
        if x[i] is None:
            print("(" + str(x[i-1]) + ", " + str(y[i-1]) + ")--(" + str(x[i]) + "," + str(y[i]) + ")")
        print("({:.3f},{:.3f})--({:.3f},{:.3f})".format(x[i-1],y[i-1],x[i],y[i]))
        lastJumpLength = np.linalg.norm(np.array([x[i], y[i]]) - np.array([x[i-1], y[i-1]]))
        trajectoryLength = trajectoryLength + lastJumpLength
        i = i + 1
    return x,y,a,cellID,edges,pbc_indices

            #if hadCollision and not (edgeID == mypolygon.exitID[0] or edgeID == mypolygon.exitID[1]):
            #    if segmentInPolygon(mypolygon, x[i-1], y[i-1], a[i-1], distanceToJump):
            #        hadCollision = False 
            #        break
            #    else: # Segment crosses a corner after having a regular collision => collision occurred 
            #        mypolygon.solution = [None, None, 0, -1]
            #        r = myray.Ray(x[i-1], y[i-1], a[i-1]) # This is the ray from the other PBC
            #        edgeID = mypolygon.whichIntersected(r)
            #        xNew,yNew = mypolygon.solution[0], mypolygon.solution[1] # Overwrite current pos. to be a point on the boundary
            #        hadCollision = True 
            #        break
            #elif hadCollision and (edgeID == mypolygon.exitID[0] or edgeID == mypolygon.exitID[1]):
            #    if segmentInPolygon(mypolygon, x[i-1], y[i-1], a[i-1], distanceToJump):
            #        hadCollision = False 
            #        break
            #    else: # Segment crosses a corner after having a regular collision => collision occurred 
            #        mypolygon.solution = [None, None, 0, -1]
            #        r = myray.Ray(x[i-1], y[i-1], a[i-1]) # This is the ray from the other PBC
            #        edgeID = mypolygon.whichIntersected(r)
            #        xNew,yNew = mypolygon.solution[0], mypolygon.solution[1] # Overwrite current pos. to be a point on the boundary
            #        hadCollision = True 
            #        break
            #else: # (xNew,yNew) is in the polygon and we are coming from within the interior
            #    if segmentInPolygon(mypolygon, x[i-1], y[i-1], a[i-1], distanceToJump):
            #        hadCollision = False 
            #        break
            #    else: # Segment crosses a corner after having a regular collision => collision occurred 
            #        mypolygon.solution = [None, None, 0, -1]
            #        r = myray.Ray(x[i-1], y[i-1], a[i-1]) # This is the ray from the other PBC
            #        edgeID = mypolygon.whichIntersected(r)
            #        xNew,yNew = mypolygon.solution[0], mypolygon.solution[1] # Overwrite current pos. to be a point on the boundary
            #        hadCollision = True 
            #        break


