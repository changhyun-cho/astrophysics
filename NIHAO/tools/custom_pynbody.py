import os
import os.path
import math

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import distinctipy

import pynbody
import pynbody.units as un
import pynbody.array as pa
import pynbody.filt as f

N = 64
pynbody.config["centering-scheme"] = "ssc"
pynbody.config["number_of_threads"] = N
os.environ["OMP_NUM_THREADS"] = str(N)

# generate 10 visually distinct colours
colors = distinctipy.get_colors(20)


class analyzeNIHAO:
    # obtain and save some physical parameters from the NIHAO snapshots

    def __init__(self, f):  # , outdir import pandas as pd
        self.f = f
        # self.outdir = outdir
        self.dir = str(self.f[:-14])
        self.m_sim = str(self.f[-14:-6])
        self.n_file = int(int(self.f[-5:]) / 16)
        self.dt = [
            ("t", float),
            ("z", float),
            ("sfh", float),
            ("sfhtime", float),
            ("sftlen", float),
            ("n_gas_bh", float),
            ("mvir", float),
            ("rvir", float),
            ("m_bh", float),
            ("m_bhc", float),
            ("m_dm", float),
            ("m_s", float),
            ("m_g", float),
            ("m_g_hot", float),
            ("m_g_cold", float),
            ("mdot", float),
            ("mdotedd", float),
            ("n_s", float),
            ("n_g", float),
            ("n_bh", float),
            ("n_dm", float),
            ("mdotbondi", float),
            ("rho", float),
            ("r_bondi", float),
            ("cs", float),
            ("h_smooth", float),
            ("half_m_r", float),
        ]
        self.df = pd.DataFrame(np.zeros(self.n_file, dtype=self.dt))
        # can be used for many halos in the future!

    def loadPynbody(self, file):
        self.s = pynbody.load(self.file)
        self.s.physical_units()
        self.h = self.s.halos()

    def find_sfh(self, h, t_beg, t_end, bins=64):
        starf = pynbody.filt.HighPass("tform", "0 Gyr")
        stars = h[1].star[starf]
        binnorm = 1e-9 * bins / (t_end - t_beg)
        tforms = stars["tform"].in_units("Gyr")
        # try:
        weight = stars["massform"].in_units("Msol") * binnorm
        # except:
        #    weight = stars["mass"].in_units("Msol") * binnorm
        sfh, sfhbines = np.histogram(
            tforms, range=(t_beg, t_end), weights=weight, bins=bins
        )
        sfhtimes = 0.5 * (sfhbines[1:] + sfhbines[:-1])
        return sfh, sfhtimes

    def center_avd(self, sim):
        pynbody.analysis.halo.center(sim, vel=False)
        cen_size = "1 kpc"
        fr = pynbody.filt.Sphere(cen_size)
        if len(sim.s[fr]) < 5 and len(sim.d[fr]) < 5 and len(sim.g[fr]) < 5:
            cen_size = self.h_smooth(sim.d, N=5)
            if len(sim.s) >= 5:
                cen_size = np.min([cen_size, self.h_smooth(sim.s, N=5)])
            if len(sim.g) >= 5:
                cen_size = np.min([cen_size, self.h_smooth(sim.g, N=5)])
        pynbody.analysis.halo.vel_center(sim, cen_size=cen_size)

    def half_mass_r(self, sim, cen=True, cylindrical=False):

        if cen:
            self.center_avd(sim)

        half_mass = sim["mass"].sum() * 0.5

        if cylindrical:
            coord = "rxy"
        else:
            coord = "r"

        X = sorted(zip(sim[coord], sim["mass"]), key=lambda pair: pair[0])
        mass = 0.0

        for k in range(len(X)):
            mass += X[k][1]
            if mass >= half_mass:
                break

        return pa.SimArray(X[k][0], sim[coord].units)

    def h_smooth(self, sim, pos=(0, 0, 0), N=50):
        if len(sim) < N or N == 0:
            return pa.SimArray(np.nan, "Mpc")
        r = pa.SimArray(
            np.sort(np.linalg.norm(sim["pos"] - pos, axis=1)), sim["pos"].units
        )
        if len(sim) == N:
            return pa.SimArray(r[N - 1], r.units)
        return pa.SimArray(0.5 * (r[N] + r[N - 1]), r.units)

    def kernel(self, x):
        if x <= 0:
            w = (21 / 16.0) * (1 - 0.0454684)
        else:
            u = np.sqrt(x * 0.25)
            w = 1 - u
            w = w * w
            w = w * w
            w = (21 / 16.0) * w * (1 + 4 * u)
        return w

    def kernel2(self, x):
        u = np.sqrt(x * 0.25)
        w = 1 - u
        w = w * w
        w = w * w
        w = (21 / 16.0) * w * (1 + 4 * u)
        return w

    def mdotbondi(self, sim, bh, N=50, alpha=100, aDot=0):
        # if (len(self.bh)==0): return np.nan, np.nan, np.nan, np.nan, np.nan
        # self.aDot *= 100*un.a*un.km/(un.s*un.Mpc)

        pos2 = [bh["pos"][0][0], bh["pos"][0][1], bh["pos"][0][2]]
        vel2 = [bh["vel"][0][0], bh["vel"][0][1], bh["vel"][0][2]]
        sim["pos"] -= pos2
        sim["vel"] -= vel2

        mass = bh[0]["mass"]

        hs = self.h_smooth(sim.g, bh["pos"][0])
        hhs = hs / 2
        filt_smooth = f.LowPass("r", hs)
        gas = sim.g[filt_smooth]

        r2 = gas["r"] * gas["r"] / (hhs * hhs)
        w = self.kernel2(r2)
        v2 = gas["v2"]

        # v2 = ((gas['vel']-aDot*gas['pos'])*(gas['vel']-aDot*gas['pos'])).sum(axis=1)
        vels2 = v2 + gas["cs"] * gas["cs"]
        ssum = np.sum(w * gas["mass"] / (vels2 * np.sqrt(vels2)))
        mdot = (
            4.0
            * math.pi
            * alpha
            * un.G
            * un.G
            * mass
            * mass
            * ssum
            / (math.pi * hhs * hhs * hhs)
        )

        rho = np.sum(w * gas["mass"]) / (math.pi * hhs * hhs * hhs)
        cs = np.sum(w * gas["cs"]) / sum(w)
        r_bondi = 2 * mass * un.G / (cs * cs)

        sim["pos"] += pos2
        sim["vel"] += vel2

        return (
            mdot.in_units("Msol yr**-1"),
            rho.in_units("Msol kpc**-3"),
            r_bondi.in_units("kpc"),
            cs.in_units("km s**-1"),
            hs.in_units("kpc"),
        )

    def generateData(self):

        self.bhf = pynbody.filt.LowPass("tform", "0 Gyr")
        self.starf = pynbody.filt.HighPass("tform", "0 Gyr")
        self.fifmyrf = pynbody.filt.LowPass("age", "15 Myr")
        self.hot = pynbody.filt.HighPass("temp", 2e4)
        self.cold = pynbody.filt.LowPass("temp", 2e4)

        self.tau_s = 4.5e8  # Salpeter timescale (year)
        self.eps_r = 0.1  # accretion (radiative) efficiency

        for i in range(self.n_file):
            self.file = self.dir + self.m_sim + "." + "{:05d}".format((i + 1) * 16)
            # print("Reading "+self.file)
            self.loadPynbody(self.file)

            try:
                pynbody.analysis.halo.center(self.h[1], mode="hyb")
            except Exception:
                print("Error at " + self.file + ": Could not center!")

            self.df["t"][i] = self.s.properties["time"].in_units("Gyr")
            self.df["z"][i] = self.s.properties["z"]

            try:
                self.df["rvir"][i] = self.h[1]["r"].in_units("kpc").max()
                self.r20f = pynbody.filt.Sphere(0.2 * self.df["rvir"][i])
                self.df["mvir"][i] = np.sum(self.h[1]["mass"].in_units("Msol"))

                self.df["m_g"][i] = np.sum(self.h[1].gas["mass"].in_units("Msol"))
                self.df["m_g_cold"][i] = np.sum(
                    self.h[1].gas[self.cold]["mass"].in_units("Msol")
                )
                self.df["m_g_hot"][i] = np.sum(
                    self.h[1].gas[self.hot]["mass"].in_units("Msol")
                )
                self.df["m_s"][i] = np.sum(self.h[1].star["mass"].in_units("Msol"))
                self.df["m_dm"][i] = np.sum(self.h[1].d["mass"].in_units("Msol"))

                self.df["n_g"][i] = len(self.h[1].gas)
                self.df["n_s"][i] = len(self.h[1].star)
                self.df["n_dm"][i] = len(self.h[1].d)

                try:
                    self.bhs = self.h[1].star[self.bhf]
                    self.i_bh = self.bhs["mass"].argmax()
                    self.df["m_bhc"][i] = self.bhs[self.i_bh]["mass"].in_units("Msol")
                    self.df["n_bh"][i] = len(self.bhs)
                    self.df["m_bh"][i] = np.sum(self.bhs["mass"].in_units("Msol"))
                    self.df["sftlen"][i] = self.bhs[self.i_bh]["eps"]  # kpcbhs[i_bh]
                    self.df["n_gas_bh"][i] = len(
                        self.h[1].g[self.cold][
                            pynbody.filt.Sphere(5 * self.df["sftlen"][i])
                        ]
                    )
                except Exception:
                    print(
                        "Warning from " + self.file + ": No black holes generated yet!"
                    )

                if len(self.bhs) != 0:
                    (
                        self.df["mdotbondi"][i],
                        self.df["rho"][i],
                        self.df["r_bondi"][i],
                        self.df["cs"][i],
                        self.df["h_smooth"][i],
                    ) = self.mdotbondi(self.h[1], self.bhs[self.i_bh], N=50, alpha=70)

                if len(self.h[1].star) != 0:
                    self.df["half_m_r"][i] = self.half_mass_r(
                        self.h[1].star, cen=False, cylindrical=True
                    )

            except Exception:
                print("Error at " + self.file + ": Could not find the central halo!")

        self.t_beg = self.df["t"][0]
        self.t_end = self.df["t"][self.n_file - 1]
        self.bins = self.n_file
        self.df["sfh"], self.df["sfhtime"] = self.find_sfh(
            self.h, self.t_beg, self.t_end, self.bins
        )

        for i in range(0, self.n_file - 1):
            self.df["mdot"][i] = (
                1.0e-9
                * (self.df["m_bhc"][i + 1] - self.df["m_bhc"][i])
                / (self.df["t"][i + 1] - self.df["t"][i])
            )
            self.df["mdotedd"][i] = (
                0.5
                * (self.df["m_bhc"][i + 1] + self.df["m_bhc"][i])
                / (self.eps_r * self.tau_s)
            )

        print("Analysis complete.")

    def readData(self):
        if os.path.isfile(
            self.dir + self.m_sim + ".csv"
        ):  # self.dir+self.m_sim+'.csv' #self.outdir+self.m_sim+'.csv'
            print("Data file found! I will read it.")
            self.df = pd.read_csv(
                self.dir + self.m_sim + ".csv"
            )  # self.dir+self.m_sim+'.csv' #self.outdir+self.m_sim+'.csv'
        else:
            print("Since there is no data file, I will read the snapshots.")
            self.generateData()

    def saveData(self):
        self.df.to_csv(
            self.dir + self.m_sim + ".csv",
            index=False
            # self.dir+self.m_sim+'.csv',index=False
            ##self.outdir+self.m_sim+'.csv',index=False
        )

        print(
            "Saving data at " + self.dir + self.m_sim + ".csv"
        )  # self.dir+self.m_sim+'.csv' #self.outdir+self.m_sim+'.csv'


def visual_nihao(*args):

    # Black hole mass vs. Stellar mass relation
    i = 0
    for data in args:
        plt.step(data[0]["m_s"], data[0]["m_bh"], color=colors[i], label=data[1])
        i += 1
    plt.xlabel(r"$M_{*}$ [$M_{\odot}$]", fontsize=15)  #'Redshift (z)'
    plt.ylabel(r"$M_{BH}$ [$M_{\odot}$]", fontsize=15)
    # plt.xlim(1.0e9,1.0e11)
    # plt.ylim(1.0e6,1.0e9)
    plt.xscale("log")
    plt.yscale("log")
    plt.legend(fontsize=15)
    plt.show()

    # Black hole mass evolution
    i = 0
    for data in args:
        plt.step(data[0]["t"], data[0]["m_bh"], color=colors[i], label=data[1])
        i += 1
    plt.xlabel("time [Gyr]", fontsize=15)  #'Redshift (z)'
    plt.ylabel(r"$M_{BH}$ [$M_{\odot}$]", fontsize=15)
    # plt.xlim(4,14)
    plt.yscale("log")
    plt.legend(fontsize=15)
    plt.show()

    # Stellar mass evolution
    i = 0
    for data in args:
        plt.step(data[0]["t"], data[0]["m_s"], color=colors[i], label=data[1])
        i += 1
    plt.xlabel("time [Gyr]", fontsize=15)  #'Redshift (z)'
    plt.ylabel(r"$M_{*}$ [$M_{\odot}$]", fontsize=15)
    # plt.xlim(4,14)
    plt.yscale("log")
    plt.legend(fontsize=15)
    plt.show()

    # Gas mass evolution
    i = 0
    for data in args:
        plt.step(data[0]["t"], data[0]["m_g"], color=colors[i], label=data[1])
        i += 1
    plt.xlabel("time [Gyr]", fontsize=15)  #'Redshift (z)'
    plt.ylabel(r"$M_{gas}$ [$M_{\odot}$]", fontsize=15)
    # plt.xlim(4,14)
    plt.yscale("log")
    plt.legend(fontsize=15)
    plt.show()

    # Gas mass evolution (Cold)
    i = 0
    for data in args:
        plt.step(data[0]["t"], data[0]["m_g_cold"], color=colors[i], label=data[1])
        i += 1
    plt.xlabel("time [Gyr]", fontsize=15)  #'Redshift (z)'
    plt.ylabel(r"$M_{gas, cold}$ [$M_{\odot}$]", fontsize=15)
    # plt.xlim(4,14)
    plt.yscale("log")
    plt.legend(fontsize=15)
    plt.show()

    # Gas mass evolution (Hot)
    i = 0
    for data in args:
        plt.step(data[0]["t"], data[0]["m_g_hot"], color=colors[i], label=data[1])
        i += 1
    plt.xlabel("time [Gyr]", fontsize=15)  #'Redshift (z)'
    plt.ylabel(r"$M_{gas, hot}$ [$M_{\odot}$]", fontsize=15)
    # plt.xlim(4,14)
    plt.yscale("log")
    plt.legend(fontsize=15)
    plt.show()

    # Star formation history
    i = 0
    for data in args:
        plt.step(data[0]["t"], data[0]["sfh"], color=colors[i], label=data[1])
        i += 1
    plt.xlabel("time [Gyr]", fontsize=15)  #'Redshift (z)'
    plt.ylabel(r"SFR [$M_{\odot}/yr$]", fontsize=15)
    plt.yscale("log")
    plt.legend(fontsize=15)
    plt.show()

    # Accretion rate history
    i = 0
    for data in args:
        plt.plot(data[0]["t"], data[0]["mdot"], color=colors[i], label=data[1])
        i += 1
    plt.xlabel("time [Gyr]", fontsize=15)  #'Redshift (z)'
    plt.ylabel(r"$\dot{M}$ [$M_{\odot}/yr$]", fontsize=15)
    plt.yscale("log")
    plt.legend(fontsize=15)
    plt.show()

    # Eddington ratio history
    i = 0
    for data in args:
        plt.plot(
            data[0]["t"],
            data[0]["mdot"] / data[0]["mdotedd"],
            color=colors[i],
            label=data[1],
        )
        i += 1
    plt.xlabel("time [Gyr]", fontsize=15)  #'Redshift (z)'
    plt.ylabel(r"$\dot{m}$ [$M_{\odot}/yr$]", fontsize=15)
    plt.yscale("log")
    plt.legend(fontsize=15)
    plt.axhline(y=0.05, color="purple", linestyle="-")
    plt.show()

    # Softening length
    i = 0
    for data in args:
        plt.step(data[0]["t"], data[0]["sftlen"], color=colors[i], label=data[1])
        i += 1
    plt.xlabel("time [Gyr]", fontsize=15)  #'Redshift (z)'
    plt.ylabel(r"$h_{sft}$ [$kpc$]", fontsize=15)
    plt.yscale("log")
    plt.legend(fontsize=15)
    plt.show()

    # Number of gas particles
    i = 0
    for data in args:
        plt.step(data[0]["t"], data[0]["n_g"], color=colors[i], label=data[1])
        i += 1
    plt.xlabel("time [Gyr]", fontsize=15)  #'Redshift (z)'
    plt.ylabel(r"$n_{gas}$", fontsize=15)
    plt.yscale("log")
    plt.legend(fontsize=15)
    plt.show()

    # Number of star particles
    i = 0
    for data in args:
        plt.step(data[0]["t"], data[0]["n_s"], color=colors[i], label=data[1])
        i += 1
    plt.xlabel("time [Gyr]", fontsize=15)  #'Redshift (z)'
    plt.ylabel(r"$n_{*}$", fontsize=15)
    plt.yscale("log")
    plt.legend(fontsize=15)
    plt.show()


def distNIHAO(*args):
    def getPARTICLES(halo):
        s = pynbody.load(halo)
        s.physical_units()  # convert all units to something reasonable (kpc, Msol, etc)
        h = s.halos()  # load the halos
        try:
            pynbody.analysis.halo.center(h[1], mode="hyb", vel=True)
            pynbody.analysis.angmom.faceon(h[1])
            r_size = "5 kpc"
        except Exception:
            print(
                "Error: Cannot face-on! Might be an elliptical galaxy. Will center it."
            )
            pynbody.analysis.halo.center(h[1], mode="hyb", vel=True)
            r_size = "10 kpc"
        h_g = h[1].gas
        h_s = h[1].star
        h_d = h[1].dm
        return (h[1], h_d, h_s, h_g, r_size)

    def get_vel(halo, r_size):
        r_within = f.Sphere(r_size)
        particle = halo[r_within]
        vel = np.sqrt(
            particle["vx"] * particle["vx"]
            + particle["vy"] * particle["vy"]
            + particle["vz"] * particle["vz"]
        )
        return vel

    # Figure settings
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    i = 0
    for data in args:
        halo, halo_d, halo_s, halo_g, r_size = getPARTICLES(data[0])
        # Particle mass
        mass = halo_g["mass"]
        axs[0, 0].hist(
            mass,
            bins=np.logspace(5, 7, 100),
            density=True,
            color=colors[i],
            alpha=0.5,
            label=data[1],
        )

        # Number density
        rho = halo_g["rho"].in_units("g cm**-3") / 1.67262192e-24
        axs[1, 0].hist(
            rho,
            bins=np.logspace(-6, 2, 100),
            density=True,
            color=colors[i],
            alpha=0.5,
            label=data[1],
        )

        # Temperature
        temp = halo_g["temp"]
        axs[0, 1].hist(
            temp,
            bins=np.logspace(2, 8, 100),
            log=True,
            density=True,
            color=colors[i],
            alpha=0.5,
            label=data[1],
        )

        # Velocity
        vel = get_vel(halo_g, r_size)
        axs[1, 1].hist(
            vel,
            bins=np.logspace(1.5, 3.5, 100),
            density=True,
            color=colors[i],
            alpha=0.5,
            label=data[1],
        )
        i += 1

    axs[0, 0].set(xlabel=r"mass [$M_{\odot}$]", ylabel="frequency")
    axs[0, 0].set_xscale("log")
    axs[0, 0].set_yscale("log")
    axs[0, 0].legend()  # fontsize=15

    axs[1, 0].set(xlabel=r"number density [cm$^{-3}$]", ylabel="frequency")
    axs[1, 0].set_xscale("log")
    axs[1, 0].set_yscale("log")
    axs[1, 0].axvline(x=10, color="b", label=r"10 H atoms cm$^{-3}$")
    axs[1, 0].legend()

    axs[0, 1].set(xlabel=r"temperature [K]", ylabel="frequency")
    axs[0, 1].set_xscale("log")
    axs[0, 1].legend()

    axs[1, 1].set(xlabel=r"gas velocity [km s$^{-1}$]", ylabel="frequency")
    axs[1, 1].set_xscale("log")
    axs[1, 1].set_yscale("log")
    axs[1, 1].legend()
    plt.show()

    # Profiles
    fig, axs = plt.subplots(3, 4, figsize=(15, 15))
    i = 0
    for data in args:
        halo, halo_d, halo_s, halo_g, r_size = getPARTICLES(data[0])
        r_size = 20.0
        r_within = f.Sphere(r_size)

        # create profiles object (by default this is a 3D profile)
        p_t = pynbody.analysis.profile.Profile(
            halo[r_within], rmin=0.01, rmax=r_size, ndim=3, type="log"
        )
        p_d = pynbody.analysis.profile.Profile(
            halo_d[r_within], rmin=0.01, rmax=r_size, ndim=3, type="log"
        )
        p_s = pynbody.analysis.profile.Profile(
            halo_s[r_within], rmin=0.01, rmax=r_size, ndim=3, type="log"
        )
        p_g = pynbody.analysis.profile.Profile(
            halo_g[r_within], rmin=0.01, rmax=r_size, ndim=3, type="log"
        )

        profile = (p_t, p_d, p_s, p_g)
        p_type = ("Total", "DM", "Star", "Gas")

        # circular velocities
        for k in range(4):
            axs[0, k].plot(
                profile[k]["rbins"].in_units("kpc"),
                profile[k]["v_circ"].in_units("km s^-1"),
                color=colors[i],
                label=data[1] + " " + p_type[k],
            )

        # velocity dispersions
        for k in range(4):
            axs[1, k].plot(
                profile[k]["rbins"].in_units("pc"),
                profile[k]["vr_disp"].in_units("km s^-1"),
                color=colors[i],
                label=data[1] + " " + p_type[k],
            )

        # 3D densities
        for k in range(4):
            axs[2, k].plot(
                profile[k]["rbins"].in_units("pc"),
                profile[k]["density"].in_units("Msol pc^-3"),
                color=colors[i],
                label=data[1] + " " + p_type[k],
            )
        i += 1

    axs[0, 0].set_ylabel(r"$v_{circ}$ [km s$^{-1}$]")
    axs[1, 0].set_ylabel(r"$\sigma_{0}$ [km s$^{-1}$]")
    axs[2, 0].set_ylabel(r"$\rho$ [M$_{\odot}$ pc$^{-3}$]")
    for j in range(4):
        axs[0, j].set_xlabel("R [kpc]")
        axs[0, j].set_xlim([1, r_size])
        axs[0, j].legend()
        # axs[1, j].set_ylim(bottom=1)
        for k in range(2):
            axs[k + 1, j].set_xlim(left=100)
            axs[k + 1, j].set_xlabel("R [pc]")
            axs[k + 1, j].set_xscale("log")
            axs[k + 1, j].set_yscale("log")
            axs[k + 1, j].legend()
    plt.show()
