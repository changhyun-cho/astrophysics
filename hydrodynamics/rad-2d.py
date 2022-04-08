import numpy as np
import matplotlib.pyplot as plt
import scipy


# Setting grids
phi = np.zeros([M+4,M+4],dtype=np.float64)

phi[:,0] = 0.0  # phi(0,y) = 0
phi[:,M] = 1.0  # phi(1,y) = 1
for i in range(M+1):
    phi[0,i] = i*1.0/M  # phi(x,1) = x
    phi[M,i] = i*1.0/M  # phi(x,0) = x




# Problem 2. Method of lines
# Author : Changhyun Cho
# ID # : 111742136

# 2nd-order accurate finite-volume implementation of linear advection with
# piecewise linear slope reconstruction
#
# We are solving a_t + u a_x = 0
#
# M. Zingale (2013-03-24)

import numpy as np
import matplotlib.pyplot as plt

class FVGrid(object):

    def __init__(self, nx, ng, xmin=0.0, xmax=1.0):

        self.xmin = xmin
        self.xmax = xmax
        self.ng = ng
        self.nx = nx

        # python is zero-based.  Make easy integers to know where the
        # real data lives
        self.ilo = ng
        self.ihi = ng+nx-1

        # physical coords -- cell-centered, left and right edges
        self.dx = (xmax - xmin)/(nx)
        self.x = xmin + (np.arange(nx+2*ng)-ng+0.5)*self.dx
        self.xl = xmin + (np.arange(nx+2*ng)-ng)*self.dx
        self.xr = xmin + (np.arange(nx+2*ng)-ng+1.0)*self.dx

        # storage for the solution
        self.a = np.zeros((nx+2*ng), dtype=np.float64)

    def period(self, u):
        """ return the period for advection with velocity u """
        return (self.xmax - self.xmin)/u

    def scratch_array(self):
        """ return a scratch array dimensioned for our grid """
        return np.zeros((self.nx+2*self.ng), dtype=np.float64)

    def fill_BCs(self):
        """ fill all single ghostcell with periodic boundary conditions """

        # left boundary
        for n in range(self.ng):
            self.a[self.ilo-1-n] = self.a[self.ihi-n]

        # right boundary
        for n in range(self.ng):
            self.a[self.ihi+1+n] = self.a[self.ilo+n]

    def init_cond(self, type="tophat"):

        if type == "tophat":
            self.a[np.logical_and(self.x >= 0.333, self.x <= 0.666)] = 1.0
        elif type == "gaussian":
            self.a[:] = 1.0 + np.exp(-60.0*(self.x - 0.5)**2.0)

        self.ainit = self.a.copy()

    def norm(self, e):
        """ return the norm of quantity e which lives on the grid """
        if not len(e) == (2*self.ng + self.nx):
            return None

        return np.sqrt(self.dx*np.sum(e[self.ilo:self.ihi+1]**2))



#-----------------------------------------------------------------------------
# advection-specific routines

def timestep(g, C, u):
    return C*g.dx/np.abs(u)


def states(g, dt, u, slope_type):
    """ compute the left and right interface states """

    # compute the piecewise linear slopes
    slope = g.scratch_array()
    adel = g.scratch_array()

    if slope_type == "godunov":

        # piecewise constant = 0 slopes
        slope[:] = 0.0

    elif slope_type == "centered":

        # unlimited centered difference slopes
        for i in range(g.ilo-1, g.ihi+2):
            adel[i] = 0.5*(g.a[i+1] - g.a[i-1])
            slope[i] = 0.5*(g.a[i+1] - g.a[i-1])/g.dx

    elif slope_type == "minmod":

        # minmod limited slope
        for i in range(g.ilo-1, g.ihi+2):
            slope[i] = minmod( (g.a[i] - g.a[i-1])/g.dx,
                               (g.a[i+1] - g.a[i])/g.dx )


    # loop over all the interfaces.  Here, i refers to the left
    # interface of the zone.  Note that thre are 1 more interfaces
    # than zones
    al = g.scratch_array()
    ar = g.scratch_array()

    for i in range(g.ilo, g.ihi+2):

        # left state on the current interface comes from zone i-1
        if slope_type == "minmod":

            #al[i] = g.a[i-1] + 0.5*g.dx*(1.0 - u*dt/g.dx)*slope[i-1]
            al[i] = g.a[i-1] + 0.5*g.dx*slope[i-1]

        else:
            al[i] = g.a[i-1] + 0.5*adel[i-1]

    return al

def update(g, dt, flux, slope_type):
    """ conservative update """

    def function(g, flux):
        func = g.scratch_array()

        for i in range(g.ilo, g.ihi+1):
            func[i] = (flux[i] - flux[i+1])/g.dx
        return func

    aori = g.scratch_array()
    aori[:] = g.a[:]

    func = function(g,flux)

    amid = g.scratch_array()
    amid[g.ilo:g.ihi+1] = aori[g.ilo:g.ihi+1] + 0.5*dt*func[g.ilo:g.ihi+1]


    # left boundary
    #for n in range(ng):
    #    amid[g.ilo-1-n] = amid[g.ihi-n]

    # right boundary
    #for n in range(ng):
    #    amid[g.ihi+1+n] = amid[g.ilo+n]

    g.a[:] = amid[:]
    g.fill_BCs()

    al = states(g, dt, u, slope_type)

    flux = u*al

    func = function(g,flux)

    anew = g.scratch_array()
    anew[g.ilo:g.ihi+1] = aori[g.ilo:g.ihi+1] + dt*func[g.ilo:g.ihi+1]

    return anew

def evolve(nx, C, u, num_periods, init_cond_name, slope_type="centered"):

    ng = 2

    # create the grid
    g = FVGrid(nx, ng)

    t = 0.0
    tmax = num_periods*g.period(u)

    # initialize the data
    g.init_cond(init_cond_name)


    # main evolution loop
    while t < tmax:

        # fill the boundary conditions
        g.fill_BCs()

        # get the timestep
        dt = timestep(g, C, u)

        if t + dt > tmax:
            dt = tmax - t

        # get the interface states
        al = states(g, dt, u, slope_type)

        # all interfaces
        flux = u*al

        # do the conservative update
        anew = update(g, dt, flux, slope_type)

        g.a[:] = anew[:]

        t += dt

    return g


def minmod(a, b):
    if abs(a) < abs(b) and a*b > 0.0:
        return a
    elif abs(b) < abs(a) and a*b > 0.0:
        return b
    else:
        return 0.0

def maxmod(a, b):
    if abs(a) > abs(b) and a*b > 0.0:
        return a
    elif abs(b) > abs(a) and a*b > 0.0:
        return b
    else:
        return 0.0


print('Problem 2. Method of lines')
print('Author : Changhyun Cho')
print(" ")


#-----------------------------------------------------------------------------
# tophat

u = 1.0
nx = 64
C = 0.5

for type in ["tophat", "gaussian"]:
    for method in ["centered", "minmod"]:
        g = evolve(nx, C, u, 1, type, method)

        plt.plot(g.x[g.ilo:g.ihi+1], g.a[g.ilo:g.ihi+1], color="C1")
        plt.plot(g.x[g.ilo:g.ihi+1], g.ainit[g.ilo:g.ihi+1], ls=":", color="C0")

        filename=type+"_"+method+".png"
        plt.savefig(filename)
        plt.clf()


#-----------------------------------------------------------------------------
# gaussian

#u = 1.0
#nx = 64
#C = 0.5

#g = evolve(nx, C, u, 1, "gaussian")

#plt.clf()

#plt.plot(g.x[g.ilo:g.ihi+1], g.a[g.ilo:g.ihi+1], color="C1")
#plt.plot(g.x[g.ilo:g.ihi+1], g.ainit[g.ilo:g.ihi+1], ls=":", color="C0")

#plt.savefig("fv-advect-gaussian.png")



#-----------------------------------------------------------------------------
# convergence test
for problem in ["tophat", "gaussian"]:
    N = [32, 64, 128, 256]
    u = 1.0
    C = 0.5

    err = []

    for nx in N:
        g = evolve(nx, C, u, 1, problem)

        err.append(g.norm(g.a - g.ainit))
        print(g.dx, nx, err[-1])

    plt.clf()

    N = np.array(N, dtype=np.float64)
    err = np.array(err)

    plt.scatter(N, err, color="C1")
    plt.plot(N, err[len(N)-1]*(N[len(N)-1]/N)**2, color="C0", label="2nd order convergence")

    ax = plt.gca()
    ax.set_xscale('log')
    ax.set_yscale('log')

    plt.xlabel("N")
    plt.ylabel("absolute error")

    plt.legend(frameon=False, fontsize="small")
    filename = "converge_"+problem+".png"
    plt.savefig(filename)
    plt.clf()
