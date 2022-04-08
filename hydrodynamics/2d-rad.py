import numpy as np
import matplotlib.pyplot as plt
import scipy


# Setting grids
xmin = 0.0
xmax = 1.0

ng = 2 # ghost cells
nx = 100 # number of cells
dx = dy = (xmax - xmin)/nx
dz = 1.

rho = np.zeros([nx+2*ng,nx+2*ng],dtype=np.float64)
P = np.zeros([nx+2*ng,nx+2*ng],dtype=np.float64)
e = np.zeros([nx+2*ng,nx+2*ng],dtype=np.float64)

v = np.zeros([nx+2*ng,nx+2*ng],dtype=np.float64)
f_rho = np.zeros([nx+2*ng,nx+2*ng],dtype=np.float64)
f_e = np.zeros([nx+2*ng,nx+2*ng],dtype=np.float64)

# MAKE IT CLASS

# then, the lowest cell is [2*ng]
# the highest cell is [2*(ng+nx-1)]

# even indice: cell edge
# odd indice: cell center

#def fill_center(grid): IT SHOULD BE CHANGED SINCE I CHANGED THE SCHEME
#    # x-direction
#    for j in range(0,2*(max-1),2):
#        grid[j+1,:] = 0.5*(grid[j,:]+grid[j+2,:])
#    # y-direction
#    for k in range(0,2*(max-1),2):
#        grid[:,k+1] = 0.5*(grid[:,k]+grid[:,k+2])

def fill_ICs(type="shock"):
    center = int(nx/2+ng)
    left = center - 10
    right = center + 10
    if type == "shock": # 1+1d shock tube
        rho[left:right,left:right] = 1.0
        P[left:right,left:right] = 1.0
    else:
        print("unknown type")


# energy and velocity
# updated by the source terms
# in the edge (even index)
# no gravitational force
def update_velocity():
# not complete,  put loops
    u_temp[j,k] = u[j,k] - 2*dt*(P[j+1,k]-P[j-1,k])/(dx*(rho[j,k]-rho[j-1,k])
    w_temp[j,k] = w[j,k] - 2*dt*(P[j,k+1]-P[j,k-1])/(dy*(rho[j,k]-rho[j,k-1])



def update_energy():
    e_temp_p[j,k] = e[j,k] - dt*P[j,k]*((u[j+1,k]-u[j,k])/dx + (w[j,k+1]-w[j,k])/dy)

    P_temp_p[j,k] = e_temp_p[j,k]/(gamma-1.)

    P_temp_half[j,k] = 0.5*(P[j,k] + P_temp_p[j,k])

    e_temp[j,k] = e[j,k] - dt*P_temp_half[j,k]*((u[j+1,k]-u[j,k])/dx + (w[j,k+1]-w[j,k])/dy)

def apply_artificial_viscosity():

    def Qx(u):
        if u[j+1,k]-u[j,k] < 0.:
            return q**2.*rho[j,k]*(u[j+1,k]-u[j,k])**2.
        else:
            return 0.

    def Qy(u):
        if w[j,k+1]-w[j,k] < 0.:
            return q**2.*rho[j,k]*(w[j,k+1]-w[j,k])**2.
        else:
            return 0.

    u_temp[j,k] = u[j,k] - 2*dt*(Qx[j+1,k]-Qx[j-1,k])/(dx*(rho[j,k]-rho[j-1,k])
    w_temp[j,k] = w[j,k] - 2*dt*(Qy[j,k+1]-Qy[j,k-1])/(dy*(rho[j,k]-rho[j,k-1])

    e_temp[j,k] = e[j,k] - dt*Qx[j,k]*(u[j+1,k]-u[j,k])/dx + Qy[j,k]*(w[j,k+1]-w[j,k])/dy

def fill_ICs(type="shock"):

    if type == "shock":
        rho[nx/2+ng,nx/2+ng] = 1.0
        P[nx/2+ng,nx/2+ng] = 1.0
    else:
        print("unknown type")




# Advection part

def solve_advection():

    Ax = dy*dz # Ax[j,k]
    Ay = dx*dz # Ay[j,k]

    dv = dx*dy*dz

    f_rho_x[j,k] = u[j,k]*avg_rho*Ax
    f_rho_y[j,k] = w[j,k]*avg_rho*Ay

    rho_temp[j,k] = rho[j,k] - dt/dv * (f_rho_x[j+1,k]-f_rho_x[j,k])
    rho[j,k] = rho_temp[j,k] - dt/dv * (f_rho_y[j,k+1]-f_rho_y[j,k])

    f_e_x[j,k] = avg_e*f_rho_x[j,k]
    f_e_y[j,k] = avg_e*f_rho_y[j,k]

    e_temp[j,k] = e[j,k] - dt/dv * (f_e_x[j+1,k]-f_e_x[j,k])
    e[j,k] = e_temp[j,k] - dt/dv * (f_e_y[j,k+1]-f_e_y[j,k])

    f_u_x[j,k] = avg_ux*0.5*(f_rho_x[j-1,k]+f_rho_x[j,k])
    f_u_y[j,k] = avg_uy*0.5*(f_rho_y[j-1,k]+f_rho_y[j,k])

    f_w_x[j,k] = avg_wx*0.5*(f_rho_x[j,k-1]+f_rho_x[j,k])
    f_w_y[j,k] = avg_wy*0.5*(f_rho_y[j,k-1]+f_rho_y[j,k])

    mom_den_u_temp[j,k] = rho[j,k]*u[j,k] - dt/dv*(f_u_x[j+1,k]-f_u_x[j,k])
    mom_den_u[j,k] = mom_den_u_temp[j,k] - dt/dv*(f_u_y[j,k+1]-f_u_y[j,k])

    mom_den_w_temp[j,k] = rho[j,k]*w[j,k] - dt/dv*(f_w_x[j+1,k]-f_w_x[j,k])
    mom_den_w[j,k] = mom_den_w_temp[j,k] - dt/dv*(f_w_y[j,k+1]-f_w_y[j,k])

    u[j,k] = mom_den_u[j,k]/rho[j,k]
    w[j,k] = mom_den_w[j,k]/rho[j,k]

def apply_BCs():
    if method == "reflecting":
        dd
    elif method == "inflow":
        dd
    elif method == "outflow":
        dd
    elif method == "periodic":
        dd

def timestep():
    du?
    dw?
    q?
    C0 = 0.5
    dt_1 = dx/(cs+np.abs(u)) #1/cs*np.min(dx,dy)
    dt_2 = dy/(cs+np.abs(w)) #dx/np.abs(u)
    dt_3 = dx/(4.q*q*np.abs(du)) #dy/np.abs(w)
    dt_4 = dy/(4.q*q*np.abs(dw)) #np.min(dx/(4.q*q*np.abs(du)),dy/(4.q*q*np.abs(dw)))

    dt = C0*np.min(dt_1,dt_2,dt_3,dt_4)
    # dt = C0*np.max(dt_1**(-2.0)+dt_2**(-2.0)+dt_3**(-2.0)+dt_4**(-2.0))**(-0.5)
    return dt
