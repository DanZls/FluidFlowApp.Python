import numpy as np
from math import sqrt, ceil
from numba import jit


#Calculates euclidean distance (2-dimensional) for point, presented as an array of coordinates
def dist(point):
    return sqrt((point**2).sum())

#Increases density of points on a boundary by adding new points into gaps greater than delta
def add_points(points0, delta):
    points = np.empty([0,2])
    for i in range(len(points0)-1):
        a = points0[i]
        b = points0[i+1]
        uvec = (b-a)/dist(b-a)
        ins_vec = np.array([a+uvec*delta*i for i in range(1, ceil(dist(b-a)/delta))])
        points = np.append(points, [a], axis=0)
        if len(ins_vec)>0:
            points = np.append(points, ins_vec, axis=0)
    points = np.append(points, [points0[-1]], axis=0)
    return points

#Generates array of collocation points for a given array of points
def add_col_points(points):
    col_points = np.empty([0,2])
    for i in range(len(points)-1):
        col_points = np.append(col_points, [(points[i+1]+points[i])/2], axis=0)
    return col_points

#Calculates orthogonal to boundary normales in collocation points
def add_norm_points(col_points):
    col_points = np.append(col_points, [col_points[0]], axis=0)
    norm_points = np.empty([0,2])
    for i in range(len(col_points)-1):
        x0, y0 = col_points[i]
        x1, y1 = col_points[i+1]
        n_x = -(y1-y0)/sqrt((x1-x0)**2+(y1-y0)**2)
        n_y = (x1-x0)/sqrt((x1-x0)**2+(y1-y0)**2)
        norm_points = np.append(norm_points, [[n_x, n_y]], axis=0)
    return norm_points

#Decreases density of points on a boundary by removing points with gaps less than delta
def del_points(x, delta):
    x_new = x[0:1,:]
    for i in range(1, len(x)-1):
        if dist(x[i]-x[i-1])>=delta:
            x_new = np.vstack([x_new, x[i:i+1, :]])
    x_new = np.vstack([x_new, x[len(x)-1:len(x), :]])
    return x_new

#Calculates non-zero distance between points (x, y) and (x0, y0)
@jit(nopython=True)
def R(x, x0, y, y0, delta=0.001):
    length = sqrt((x-x0)**2+(y-y0)**2)
    if length>delta:
        return length
    else:
        return delta

#Calculates velocity vector for points x, x0
def V(x, x0):
    x, y = x
    x0, y0 = x0
    return np.array([y0-y, x-x0])/(2*np.pi*R(x,x0,y,y0)**2)

#Calculates left side of the system of linear equations (in matrix form)
def CalculateMatrix_A(points, col_points, norm_points):
    x = col_points
    x0 = points
    n = norm_points
    A = np.array([[np.dot(V(x[k],x0[j]), n[k]) for j in range(len(x0))] for k in range(len(x))])
    A = np.append(A, [[1 for j in range(len(x0))]], axis=0)
    return A

#Calculates right side of the system of linear equations (in matrix form)
def CalculateVector_b(norm_points, V_inf, Gamma0):
    n = norm_points
    b = np.array([-np.dot(V_inf, n[k]) for k in range(len(n))])
    b = np.append(b, [Gamma0])
    return b

#Calculates field coefficients by solving the system of linear equations
def CalculateFieldCoefficients(A, b):
    # return np.array([np.linalg.solve(A, b)]).T
    return np.array(np.dot(np.linalg.pinv(A), b)).T

#Calculates velocity vector for each point in array x
def CalculateFieldVelocity(x, x0, Gamma, V_inf):
    v_n = V_inf + np.array([[Gamma[j]*V(x[k],x0[j]) for j in range(len(x0))] for k in range(len(x))]).sum(axis=1)
    return v_n

# CalculateFieldVelocity with numba.jit acceleration
@jit(nopython=True)
def CalculateFieldVelocityWithJit(X, X0, Gamma, V_inf):
    V = np.empty(shape=(len(X), 2))
    for k in range(len(X)):
        vxk = 0
        vyk = 0
        for j in range(len(X0)):
            x = X[k][0]
            y = X[k][1]
            x0 = X0[j][0]
            y0 = X0[j][1]
            g = Gamma[j]
            vx = (y0-y)/(2*np.pi*R(x,x0,y,y0)**2)
            vy = (x-x0)/(2*np.pi*R(x,x0,y,y0)**2)
            vxk += g * vx
            vyk += g * vy
        V[k][0] = vxk
        V[k][1] = vyk
    v_n = V + V_inf
    return v_n

# CalculateFieldVelocity with Nvidia CUDA acceleration (disabled for GKE)
# def CalculateFieldVelocityWithCuda(dynArray, vorArray, gammaArray, V_inf):
#     import cupy as cp
#     dynIter = range(len(dynArray))
#     vorIter = range(len(vorArray))
#     g = cp.array([gammaArray[j] for j in vorIter for k in dynIter])
#     x = cp.array([dynArray[k][0] for j in vorIter for k in dynIter])
#     y = cp.array([dynArray[k][1] for j in vorIter for k in dynIter])
#     x0 = cp.array([vorArray[j][0] for j in vorIter for k in dynIter])
#     y0 = cp.array([vorArray[j][1] for j in vorIter for k in dynIter])

#     r = cp.maximum(cp.sqrt(cp.power(cp.subtract(x, x0), 2) + cp.power(cp.subtract(y, y0), 2)), 0.001)

#     vx = cp.divide(cp.subtract(y0, y), cp.multiply(cp.power(r, 2), 2*cp.pi))
#     vy = cp.divide(cp.subtract(x, x0), cp.multiply(cp.power(r, 2), 2*cp.pi))

#     vnx = cp.multiply(g, vx)
#     vny = cp.multiply(g, vy)

#     vn = np.add(np.array([[vnx.get(), vny.get()]]), V_inf)
    
#     return vn