import os
import os.path

import numpy as np
import pandas as pd
from scipy import interpolate
from scipy.interpolate import InterpolatedUnivariateSpline

import matplotlib
import matplotlib.pyplot as plt
import distinctipy


import pynbody
import pynbody.filt as f
import pynbody.plot.sph as sph
from pynbody.plot.stars import moster, behroozi

N = 128
# pynbody.config["centering-scheme"] = "ssc"
pynbody.config["number_of_threads"] = N
os.environ["OMP_NUM_THREADS"] = str(N)

# generate 20 visually distinct colours
colors = distinctipy.get_colors(20)

# Set universal font properties
matplotlib.rcParams[
    "font.family"
] = "serif"  # Font family (e.g., 'serif', 'sans-serif', 'monospace')
matplotlib.rcParams["text.usetex"] = True
dpi = 500


class analyzeHELLO:
    # obtain and save some physical parameters from the hello snapshots

    def __init__(self, f):
        self.f = f
        # self.outdir = outdir
        self.dir = str(self.f[:-14])
        self.m_sim = str(self.f[-14:-6])
        self.n_file = int(int(self.f[-5:]) / 16)
        self.dt = [
            "t",
            "z",
            "sfh",
            "sfhtime",
            "sftlen",
            "n_g_1",
            "n_g_2",
            "n_g_3",
            "rho_gas",
            "mvir",
            "rvir",
            "r_half_m",
            "m_bh",
            "m_bhc",
            "m_dm",
            "m_s",
            "m_g",
            "m_g_hot",
            "m_g_cold",
            "m_g_HI",
            "m_g_HeI",
            "mdot",
            "mdotedd",
            "n_s",
            "n_g",
            # "v_disp_hm",
            # "v_disp_595",
            "n_bh",
            "n_dm",
            "lum_u",
            "lum_b",
            "lum_v",
            "lum_r",
            "lum_i",
            "mag_u",
            "mag_b",
            "mag_v",
            "mag_r",
            "mag_i",
        ]
        # Initialize DataFrame with zeros for each column
        self.df = pd.DataFrame({column: np.zeros(self.n_file) for column in self.dt})
        # can be used for many halos in the future!

    def loadPynbody(self, file):
        self.s = pynbody.load(self.file)
        self.s.physical_units()
        self.h = self.s.halos()

    def find_sfh(self, h, t_beg, t_end, bins):
        starf = pynbody.filt.HighPass("tform", "0 Gyr")
        stars = h[1].star[starf]
        binnorm = 1e-9 * bins / (t_end - t_beg)
        tforms = stars["tform"].in_units("Gyr")
        weight = stars["massform"].in_units("Msol") * binnorm
        sfh, sfhbines = np.histogram(
            tforms, range=(t_beg, t_end), weights=weight, bins=bins
        )
        sfhtimes = 0.5 * (sfhbines[1:] + sfhbines[:-1])
        return sfh, sfhtimes

    def get_r_half(self, halo):

        # Calculate total stellar mass and find the maximum radius
        m_tot = np.sum(halo.s["mass"].in_units("Msol"))
        r_max = halo.s["r"].in_units("kpc").max()

        N = 200
        r_list = np.logspace(np.log10(0.5), np.log10(r_max), N)
        m_list = np.zeros(N)

        # Calculate the cumulative mass fraction within each radius
        for i, r in enumerate(r_list):
            sphere = pynbody.filt.Sphere(f"{r} kpc")
            m_list[i] = np.sum(halo.s[sphere]["mass"].in_units("Msol"))

        # Normalize the mass list to get the fraction of total mass
        m_list /= m_tot

        # Interpolation to find the half-mass radius
        interp_func = interpolate.interp1d(
            m_list, r_list, kind="linear", bounds_error=False, fill_value="extrapolate"
        )
        r_half_mass = interp_func(0.5)

        return r_half_mass

    def get_sigma(self, rbins, v_disp, r, k=1):

        rbins = np.asarray(rbins)
        v_disp = np.asarray(v_disp)

        # Create an interpolation function
        interp_func = InterpolatedUnivariateSpline(rbins, v_disp, k=k)

        # Perform interpolation
        sigma = interp_func(r)

        return sigma

    def get_norm_sig(self, rbins, v_disp, r_norm, r_ap):

        # Convert input arrays to float for consistency
        rbins = np.asarray(rbins, dtype=float)
        v_disp = np.asarray(v_disp, dtype=float)
        r_ap = float(r_ap)

        # Calculate the normalization velocity dispersion at r_norm
        sigma_norm = self.get_sigma(rbins, v_disp, r_norm)

        # Constants for the scaling law
        alpha = -0.065
        beta = -0.013

        # Calculate the log ratio of the aperture to the normalization radius
        log_ratio = np.log10(r_ap / r_norm)

        sigma_ap = sigma_norm * 10 ** (alpha * log_ratio + beta * log_ratio**2)

        return sigma_ap

    def generateData(self):

        self.bhf = pynbody.filt.LowPass("tform", "0 Gyr")
        self.starf = pynbody.filt.HighPass("tform", "0 Gyr")
        self.fifmyrf = pynbody.filt.LowPass("age", "15 Myr")
        self.hot = pynbody.filt.HighPass("temp", 2e4)
        self.cold = pynbody.filt.LowPass("temp", 2e4)
        self.one = pynbody.filt.Sphere("1 kpc")
        self.two = pynbody.filt.Sphere("2 kpc")
        self.three = pynbody.filt.Sphere("3 kpc")

        self.tau_s = 4.5e8  # Salpeter timescale (year)
        self.eps_r = 0.1  # accretion (radiative) efficiency

        for i in range(self.n_file):
            self.file = os.path.join(self.dir, f"{self.m_sim}.{(i + 1) * 16:05d}")
            # print("Reading "+self.file)
            try:
                self.loadPynbody(self.file)
            except Exception:
                print("No file found! Skipping...")

            try:
                pynbody.analysis.halo.center(self.h[1])
            except Exception:
                print(f"Error at {self.file}: Could not center!")

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
                self.df["m_g_HI"][i] = np.sum(
                    self.h[1].gas["mass"].in_units("Msol") * self.h[1].gas["HI"]
                )
                self.df["m_g_HeI"][i] = np.sum(
                    self.h[1].gas["mass"].in_units("Msol") * self.h[1].gas["HeI"]
                )
                self.df["m_s"][i] = np.sum(self.h[1].star["mass"].in_units("Msol"))
                self.df["m_dm"][i] = np.sum(self.h[1].d["mass"].in_units("Msol"))
                self.df["n_g"][i] = len(self.h[1].gas)
                self.df["n_s"][i] = len(self.h[1].star)
                self.df["n_dm"][i] = len(self.h[1].d)
                self.df["n_g_1"][i] = len(self.h[1].g[self.one])
                self.df["n_g_2"][i] = len(self.h[1].g[self.two])
                self.df["n_g_3"][i] = len(self.h[1].g[self.three])
                self.df["rho_gas"][i] = (
                    1.0e-9
                    * np.sum(self.h[1].g[self.one]["mass"].in_units("Msol"))
                    / ((4.0 / 3.0) * np.pi)
                )
                self.df["lum_u"][i] = float(
                    pynbody.analysis.luminosity.halo_lum(self.h[1].s, band="u")
                )
                self.df["lum_b"][i] = float(
                    pynbody.analysis.luminosity.halo_lum(self.h[1].s, band="b")
                )
                self.df["lum_v"][i] = float(
                    pynbody.analysis.luminosity.halo_lum(self.h[1].s, band="v")
                )
                self.df["lum_r"][i] = float(
                    pynbody.analysis.luminosity.halo_lum(self.h[1].s, band="r")
                )
                self.df["lum_i"][i] = float(
                    pynbody.analysis.luminosity.halo_lum(self.h[1].s, band="i")
                )
                self.df["mag_u"][i] = float(
                    pynbody.analysis.luminosity.halo_mag(self.h[1].s, band="u")
                )
                self.df["mag_b"][i] = float(
                    pynbody.analysis.luminosity.halo_mag(self.h[1].s, band="b")
                )
                self.df["mag_v"][i] = float(
                    pynbody.analysis.luminosity.halo_mag(self.h[1].s, band="v")
                )
                self.df["mag_r"][i] = float(
                    pynbody.analysis.luminosity.halo_mag(self.h[1].s, band="r")
                )
                self.df["mag_i"][i] = float(
                    pynbody.analysis.luminosity.halo_mag(self.h[1].s, band="i")
                )

                try:
                    self.bhs = self.h[1].star[self.bhf]
                    self.i_bh = self.bhs["mass"].argmax()
                    self.df["m_bhc"][i] = self.bhs[self.i_bh]["mass"].in_units("Msol")
                    self.df["n_bh"][i] = len(self.bhs)
                    self.df["m_bh"][i] = np.sum(self.bhs["mass"].in_units("Msol"))
                    self.df["sftlen"][i] = self.bhs[self.i_bh]["eps"]  # kpcbhs[i_bh]

                except Exception:
                    print(f"Warning from {self.file}: No black holes generated yet!")

            except Exception:
                print(f"Error at {self.file}: Could not find the central halo!")

        self.t_beg = self.df["t"][0]
        self.t_end = self.df["t"][i]
        self.bins = i + 1
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

        print("Analysis completed.")

    def readData(self):
        self.outfile = self.dir + self.m_sim + ".csv"
        if os.path.isfile(self.outfile):
            # self.dir+self.m_sim+'.csv' #self.outdir+self.m_sim+'.csv'
            print("Data file found! I will read it.")
            self.df = pd.read_csv(self.outfile)
            # self.dir+self.m_sim+'.csv' #self.outdir+self.m_sim+'.csv'
        else:
            print("Since there is no data file, I will read the snapshots.")
            self.generateData()

    def saveData(self, outdir=None):

        # If outdir is provided, use it; otherwise, use self.dir
        self.target_dir = outdir if outdir else self.dir

        # Construct the full file path
        self.file_path = os.path.join(self.target_dir, self.m_sim + ".csv")

        # Save the DataFrame to the specified file path
        self.df.to_csv(self.file_path, index=False)

        print(f"Saving data at {self.file_path}")


def visual_hello(*args):

    fig, axs = plt.subplots(6, 2, figsize=(10, 20), dpi=dpi)

    # Moster realtion
    # Generate log-spaced mass array
    halomasses = np.logspace(9, 13.5, 40)

    # Calculate stellar masses and errors using Moster and Behroozi relations
    y_stellar_moster, errors_moster = moster(halomasses, 0)
    y_stellar_behroozi, errors_behroozi = behroozi(
        halomasses, 0, alpha=-1.412, Kravtsov=False
    )

    # Plotting shaded areas for errors
    axs[4, 0].fill_between(
        halomasses,
        y_stellar_moster / errors_moster,
        y2=y_stellar_moster * errors_moster,
        color="skyblue",
        alpha=0.6,
        label="Moster+ (2013)",
    )
    axs[4, 0].fill_between(
        halomasses,
        y_stellar_behroozi / errors_behroozi,
        y2=y_stellar_behroozi * errors_behroozi,
        color="coral",
        alpha=0.6,
        label="Behroozi+ (2013)",
    )

    # BH mass-stellar mass relation
    m_s_rel = np.logspace(7.5, 11.5, 100)
    m_bh_rel = 0.49e9 * (m_s_rel / 1.0e11) ** 1.17
    dex = 0.28

    axs[5, 1].plot(
        m_s_rel, m_bh_rel, label="Kormendy \& Ho (2013)", color="gray", linewidth=1
    )
    axs[5, 1].fill_between(
        m_s_rel, m_bh_rel * (1.0 - dex), m_bh_rel * (1.0 + dex), color="gray", alpha=0.3
    )

    i = 0
    for data in args:
        axs[0, 0].step(
            data[0]["t"], data[0]["m_bh"], color=colors[i], alpha=0.6, label=data[1]
        )
        axs[0, 1].step(
            data[0]["t"], data[0]["m_s"], color=colors[i], alpha=0.6, label=data[1]
        )
        axs[1, 0].step(
            data[0]["t"], data[0]["m_g"], color=colors[i], alpha=0.6, label=data[1]
        )
        axs[1, 1].step(
            data[0]["t"], data[0]["m_g_cold"], color=colors[i], alpha=0.6, label=data[1]
        )
        axs[2, 0].step(
            data[0]["t"], data[0]["m_g_hot"], color=colors[i], alpha=0.6, label=data[1]
        )
        axs[2, 1].step(
            data[0]["t"], data[0]["sfh"], color=colors[i], alpha=0.6, label=data[1]
        )
        axs[3, 0].plot(
            data[0]["t"], data[0]["mdot"], color=colors[i], alpha=0.6, label=data[1]
        )
        axs[3, 1].step(
            data[0]["t"],
            data[0]["n_g_1"],
            color=colors[i],
            alpha=0.6,
            label=f"{data[1]}, 1 kpc",
        )
        axs[3, 1].step(
            data[0]["t"],
            data[0]["n_g_2"],
            linestyle="--",
            color=colors[i],
            alpha=0.6,
            label=f"{data[1]}, 2 kpc",
        )
        axs[4, 0].scatter(
            data[0]["mvir"],
            data[0]["m_s"],
            color=colors[i],
            label=data[1],
            s=15,
            alpha=0.6,
        )
        axs[4, 1].step(
            data[0]["t"], data[0]["rho_gas"], color=colors[i], alpha=0.6, label=data[1]
        )
        axs[5, 0].plot(
            data[0]["m_s"], data[0]["sfh"], color=colors[i], alpha=0.6, label=data[1]
        )
        axs[5, 1].plot(
            data[0]["m_s"], data[0]["m_bh"], color=colors[i], alpha=0.6, label=data[1]
        )
        i += 1

    axs[0, 0].set_xlabel(
        "time [Gyr]",
    )  #'Redshift (z)'
    axs[0, 0].set_ylabel(
        r"$M_{BH}$ [$M_{\odot}$]",
    )
    # axs[0, 0].xlim(4,14)
    axs[0, 0].set_yscale("log")
    axs[0, 0].legend()

    axs[0, 1].set_xlabel(
        "time [Gyr]",
    )  #'Redshift (z)'
    axs[0, 1].set_ylabel(
        r"$M_{*}$ [$M_{\odot}$]",
    )
    axs[0, 1].set_ylim(bottom=1.0e7)
    axs[0, 1].set_yscale("log")
    axs[0, 1].legend()

    axs[1, 0].set_xlabel(
        "time [Gyr]",
    )  #'Redshift (z)'
    axs[1, 0].set_ylabel(
        r"$M_{gas}$ [$M_{\odot}$]",
    )
    # axs[1, 0].xlim(4,14)
    axs[1, 0].set_yscale("log")
    axs[1, 0].legend()

    axs[1, 1].set_xlabel(
        "time [Gyr]",
    )  #'Redshift (z)'
    axs[1, 1].set_ylabel(
        r"$M_{gas, cold}$ [$M_{\odot}$]",
    )
    # axs[1, 1].xlim(4,14)
    axs[1, 1].set_yscale("log")
    axs[1, 1].legend()

    axs[2, 0].set_xlabel(
        "time [Gyr]",
    )  #'Redshift (z)'
    axs[2, 0].set_ylabel(
        r"$M_{gas, hot}$ [$M_{\odot}$]",
    )
    # axs[2, 0].xlim(4,14)
    axs[2, 0].set_yscale("log")
    axs[2, 0].legend()

    axs[2, 1].set_xlabel(
        "time [Gyr]",
    )  #'Redshift (z)'
    axs[2, 1].set_ylabel(
        r"SFR [$M_{\odot}$ yr$^{-1}$]",
    )
    axs[2, 1].set_yscale("log")
    axs[2, 1].legend()

    axs[3, 0].set_xlabel(
        "time [Gyr]",
    )  #'Redshift (z)'
    axs[3, 0].set_ylabel(
        r"$\dot{M}$ [$M_{\odot}$ yr$^{-1}$]",
    )
    axs[3, 0].set_yscale("log")
    axs[3, 0].legend()

    axs[3, 1].set_xlabel(
        "time [Gyr]",
    )  #'Redshift (z)'
    axs[3, 1].set_ylabel(
        r"$n_{gas}<r$ kpc",
    )
    axs[3, 1].set_yscale("log")
    axs[3, 1].legend()

    axs[4, 0].set_xlabel(
        r"$M_{Vir}$ [$M_{\odot}$]",
    )
    axs[4, 0].set_ylabel(r"$M_{*}$ [$M_{\odot}$]")
    axs[4, 0].set_xscale("log")
    axs[4, 0].set_yscale("log")
    axs[4, 0].set_xlim(1.0e9, 1.0e13)
    axs[4, 0].legend()

    axs[4, 1].set_xlabel(
        "time [Gyr]",
    )
    axs[4, 1].set_ylabel(
        r"$\rho_{gas}$ [$M_{\odot}$ pc$^{-3}$]",
    )
    axs[4, 1].set_yscale("log")
    axs[4, 1].legend()

    axs[5, 0].set_xlabel(
        r"$M_{*}$ [$M_{\odot}$]",
    )
    axs[5, 0].set_ylabel(
        r"SFR [$M_{\odot}$ yr$^{-1}$]",
    )
    axs[5, 0].set_xscale("log")
    axs[5, 0].set_yscale("log")
    axs[5, 0].legend()

    axs[5, 1].set_xlabel(
        r"$M_{*}$ [$M_{\odot}$]",
    )  #'Redshift (z)'
    axs[5, 1].set_ylabel(
        r"$M_{BH}$ [$M_{\odot}$]",
    )
    axs[5, 1].set_xlim(left=1.0e8)
    axs[5, 1].set_ylim(bottom=1.0e5)
    axs[5, 1].set_xscale("log")
    axs[5, 1].set_yscale("log")
    axs[5, 1].legend()
    plt.show()


def dist_hello(*args):
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
    fig, axs = plt.subplots(2, 2, figsize=(15, 10), dpi=dpi)
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
    axs[0, 0].legend()  #

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
    fig, axs = plt.subplots(3, 4, figsize=(15, 15), dpi=dpi)
    i = 0
    for data in args:
        halo, halo_d, halo_s, halo_g, r_size = getPARTICLES(data[0])
        r_within = f.Sphere(r_size)
        r_size = "20.0 kpc"

        # create profiles object (by default this is a 3D profile)
        p_t = pynbody.analysis.profile.Profile(
            halo[r_within],
            rmin="0.1 kpc",
            rmax=r_size,
            ndim=3,
            type="log",
        )
        p_d = pynbody.analysis.profile.Profile(
            halo_d[r_within],
            rmin="0.1 kpc",
            rmax=r_size,
            ndim=3,
            type="log",
        )
        p_s = pynbody.analysis.profile.Profile(
            halo_s[r_within],
            rmin="0.1 kpc",
            rmax=r_size,
            ndim=3,
            type="log",
        )
        p_g = pynbody.analysis.profile.Profile(
            halo_g[r_within],
            rmin="0.1 kpc",
            rmax=r_size,
            ndim=3,
            type="log",
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
        axs[0, j].set_xlim(left=1)
        axs[0, j].legend()
        for k in range(2):
            axs[k + 1, j].set_xlim(left=100)
            axs[k + 1, j].set_xlabel("R [pc]")
            axs[k + 1, j].set_xscale("log")
            axs[k + 1, j].set_yscale("log")
            axs[k + 1, j].legend()
    plt.show()


def map_hello(*args):
    # See these links
    # https://pynbody.github.io/pynbody/tutorials/pictures.html
    # https://pynbody.github.io/pynbody/tutorials/halos.html
    # https://pynbody.github.io/pynbody/tutorials/hmf.html

    for data in args:
        fig, axs = plt.subplots(3, 2, figsize=(15, 10))
        fig.suptitle(data[1])

        s = pynbody.load(data[0])
        s.physical_units()  # convert all units to something reasonable (kpc, Msol, etc)
        h = s.halos()  # load the halos
        pynbody.analysis.halo.center(h[1], mode="hyb", vel=True)

        # face on, use this function
        pynbody.analysis.angmom.faceon(h[1], cen=(0, 0, 0))
        pynbody.plot.stars.render(h[1].s, width="5 kpc", axes=axs[0, 0])
        pynbody.plot.image(
            h[1].g,
            qty="rho",
            units="g cm^-3",
            width="5 kpc",
            cmap="Greys",
            subplot=axs[0, 1],
            threaded=False,
        )  # 1,0
        # axs[0, 0].pynbody.plot.image(h[1].g, qty="temp", width="5 kpc") #1,1
        sph.image(
            h[1].g,
            qty="temp",
            width=5,
            cmap="YlOrRd",
            denoise=True,
            approximate_fast=False,
            ax=axs[0, 2],
        )

        # edge on, or use other things
        pynbody.analysis.angmom.sideon(h[1], cen=(0, 0, 0))
        pynbody.plot.stars.render(h[1].s, width="5 kpc", axes=axs[1, 0])
        pynbody.plot.image(
            h[1].g,
            qty="rho",
            units="g cm^-3",
            width="5 kpc",
            cmap="Greys",
            subplot=axs[1, 1],
            threaded=False,
        )  # 2,0
        # pynbody.plot.image(h[1].g, qty="temp", width="5 kpc") #2,1
        sph.image(
            h[1].g,
            qty="temp",
            width=5,
            cmap="YlOrRd",
            denoise=True,
            approximate_fast=False,
            ax=axs[1, 2],
        )
        # s.rotate_x(90)
        # s.rotate_x(-90)
        plt.show()


def plot_m_sigma(*args):
    # For now, first value is BH mass, second sigma, and label
    # but later, it should be merged to the basic data frame
    def get_m(v_disp):  # Equation (3) from Sahu et al. (2019)
        m = 6.1 * np.log10(v_disp / 200.0) + 8.27
        return 10.0**m

    sigma = np.logspace(1.4, 2.8, 100)
    m_bh = get_m(sigma)

    plt.plot(np.log10(sigma), np.log10(m_bh), label=r"m-$\sigma$")
    for data in args:
        plt.scatter(np.log10(data[0]), np.log10(data[1]), label=data[2])
    plt.show()
