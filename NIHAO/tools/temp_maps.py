# surface mass density and RGB images of galaxies
# The original code is from Tobias and Stefan

# load python packages and select plotting settings
import pynbody as pb
import numpy as np
import pynbody.filt as filt
import pynbody.plot.sph as sph
import seaborn as sns
import matplotlib.pyplot as plt
import os
import matplotlib.gridspec as gridspec
from pynbody.snapshot.tipsy import TipsySnap


lg = filt.LowPass("r", "400 kpc")

plt.switch_backend("agg")
#%matplotlib inline
#%config InlineBackend.figure_format='retina'
plt.rcParams["figure.figsize"] = (10, 10)

sns.set_style("ticks")
sns.set_context("talk", font_scale=2, rc={"lines.linewidth": 4})

plt.rc("axes", linewidth=3)
plt.rcParams["xtick.major.size"] = 10
plt.rcParams["xtick.major.width"] = 3
plt.rcParams["xtick.minor.size"] = 5
plt.rcParams["xtick.minor.width"] = 1.5
plt.rcParams["xtick.direction"] = "in"
plt.rcParams["ytick.major.size"] = 10
plt.rcParams["ytick.major.width"] = 3
plt.rcParams["ytick.minor.size"] = 5
plt.rcParams["ytick.minor.width"] = 1.5
plt.rcParams["ytick.direction"] = "in"


def get_surf_den(s, sim, bins, phys_size):

    m_min = s.d["mass"].min()
    idx = np.where(sim["mass"] <= m_min)[0]
    hist, xe, ye = np.histogram2d(
        sim[idx]["x"],
        sim[idx]["y"],
        bins=bins,
        range=((-phys_size, phys_size), (-phys_size, phys_size)),
        weights=sim["mass"][idx].in_units("Msol"),
    )
    norm = (
        4 * phys_size * phys_size * 1000000 / float(bins * bins)
    )  # factor 1000000 for conversion of kpc to pc
    surf_den = hist / norm

    return surf_den


def center(halo):
    return pb.analysis.halo.center(halo, mode="ssc", retcen=True)


# custom pynbody defs to estimate HI
@TipsySnap.derived_quantity
def HI_rahmati(sim):
    lamb = 315614.0 / sim["temp"]
    rhoh = sim["rho"].in_units("m_p cm^-3") * sim["hydrogen"]
    z = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
    # Haardt and Madau 2001, taken from table 2 of Rahmati 2013b
    UVB_array = pb.array.SimArray(
        [8.34e-14, 7.39e-13, 1.50e-12, 1.16e-12, 7.92e-13, 5.43e-13], "s^-1"
    )
    ssh_array = pb.array.SimArray(
        [1.1e-3, 5.1e-3, 8.7e-3, 7.4e-3, 5.8e-3, 4.5e-3], "cm^-3"
    )
    UVB = pb.array.SimArray(np.interp(sim.properties["z"], z, UVB_array), "s^-1")
    ssh = pb.array.SimArray(np.interp(sim.properties["z"], z, ssh_array), "cm^-3")
    Cooling = pb.array.SimArray(
        1.17e-10
        * (sim["temp"] ** 0.5 * np.exp(-157809 / sim["temp"]))
        / (1 + np.sqrt(sim["temp"] / 1e5)),
        "cm^3 s^-1",
    )
    Gammaphot = pb.array.SimArray(
        UVB
        * (
            0.98 * (1 + (rhoh / ssh) ** (1.64)) ** (-2.28)
            + 0.02 * (1 + (rhoh / ssh)) ** (-0.84)
        ),
        "s^-1",
    )
    # C = alpha_A as per Rahmati 2013b Appendix 2
    C = pb.array.SimArray(
        1.269e-13 * (lamb ** (1.503)) / (1 + (lamb / 0.522) ** (0.47)) ** (1.923),
        "cm^3 s^-1",
    )
    A = C + Cooling
    B = 2 * C + Gammaphot / rhoh + Cooling
    return (B - np.sqrt(B**2 - 4 * A * C)) / (2 * A)


# set up the figure grid for 5 plots (4 face-on, 1 edge-on) and 6 different sims
fig = plt.figure(figsize=(42, 60))
gs = gridspec.GridSpec(
    7, 5, width_ratios=[1, 1, 1, 1, 0.25], height_ratios=[0.1, 1, 1, 1, 1, 1, 1]
)
gs.update(hspace=0.025, wspace=0.025)

axes = []
for i, cell in enumerate(gs):
    axes.append(plt.subplot(cell))
    if i == 3:
        axes[-1].set_axis_off()
    if i == 4:
        axes[-1].set_axis_off()
    if i > 4:
        axes[-1].set_xticklabels([])
        axes[-1].set_yticklabels([])

path = "/data/sw4445/nihao2/n10/z2.0"
# path = '/data/sw4445/nihao2/n10/z3.6'
sims = [
    "g2.75e12/g2.75e12.00240",
    "g2.29e12/g2.29e12.00240",
    "g2.63e12/g2.63e12.00240",
    "g2.83e12/g2.83e12.00240",
    "g3.03e12/g3.03e12.00240",
    "g3.20e12/g3.20e12.00240",
]
# sims = ['g4.58e12/g4.58e12.00128']

pix = 500

for i, sim in enumerate(sims):

    i = (1 + i) * 5  # leave space for colorbars
    s = pb.load(os.path.join(path, sim))
    h = s.halos()
    s.physical_units()
    j = 2 if sim == "g2.91e12/g2.91e12.00240" else 1
    pb.analysis.angmom.faceon(h[j])

    # add circle for main halo
    cen = center(h[j])
    rvir = np.max(h[j]["r"].in_units("kpc"))
    circ = plt.Circle(
        (cen[0], cen[1]),
        radius=rvir,
        linestyle="dashed",
        linewidth=4,
        color="w",
        fill=False,
    )

    phys_size = 200
    lg = filt.BandPass("z", "-" + str(phys_size) + " kpc", str(phys_size) + " kpc")

    # dm projection far
    surf_den_dm = get_surf_den(s, s[lg].d, pix, phys_size)
    axes[i + 0].set_facecolor("black")
    c_dm_far = axes[i + 0].imshow(
        np.log10(surf_den_dm).T,
        origin="lower",
        interpolation="nearest",
        extent=(-phys_size, phys_size, -phys_size, phys_size),
        cmap="Greys_r",
        vmin=1.0,
        vmax=3.49,
    )
    axes[i + 0].add_artist(circ)

    # phys_size = phys_size/2.
    axes[i + 0].plot(
        np.array([0.9 * phys_size - 100, 0.9 * phys_size]),
        np.array([-0.9 * phys_size, -0.9 * phys_size]),
        linestyle="-",
        lw=2.0,
        color="white",
    )
    axes[i + 0].text(
        0.765,
        0.075,
        "100 kpc",
        fontsize=25,
        color="white",
        horizontalalignment="left",
        verticalalignment="center",
        transform=axes[i + 0].transAxes,
    )
    axes[i + 0].text(
        0.5,
        0.925,
        sim[0:8],
        fontsize=35,
        color="white",
        horizontalalignment="center",
        verticalalignment="center",
        transform=axes[i + 0].transAxes,
    )

    # star projection far
    surf_den_star = get_surf_den(s, s[lg].s, pix, phys_size)
    axes[i + 1].set_facecolor("black")
    c_star_far = axes[i + 1].imshow(
        np.log10(surf_den_star).T,
        origin="lower",
        interpolation="nearest",
        extent=(-phys_size, phys_size, -phys_size, phys_size),
        cmap="plasma",
        vmin=-3.49,
        vmax=2.49,
    )
    # redefine artist because of error reusing it.
    circ = plt.Circle(
        (cen[0], cen[1]),
        radius=rvir,
        linestyle="dashed",
        linewidth=4,
        color="w",
        fill=False,
    )
    axes[i + 1].add_artist(circ)

    # phys_size = phys_size/2.
    axes[i + 1].plot(
        np.array([0.9 * phys_size - 100, 0.9 * phys_size]),
        np.array([-0.9 * phys_size, -0.9 * phys_size]),
        linestyle="-",
        lw=2.0,
        color="white",
    )
    axes[i + 1].text(
        0.765,
        0.075,
        "100 kpc",
        fontsize=25,
        color="white",
        horizontalalignment="left",
        verticalalignment="center",
        transform=axes[i + 1].transAxes,
    )
    axes[i + 1].text(
        0.5,
        0.925,
        sim[0:8],
        fontsize=35,
        color="white",
        horizontalalignment="center",
        verticalalignment="center",
        transform=axes[i + 1].transAxes,
    )

    # gas projection close
    phys_size = 80
    lg = filt.BandPass("z", "-" + str(phys_size) + " kpc", str(phys_size) + " kpc")

    # calculate HI density
    s.g["hrm"] = pb.array.SimArray(
        s.g["rho"] * s.g["hydrogen"] * s.g["HI_rahmati"], "Msol kpc**-3"
    )
    # s.g['hrm'].set_units_like("Msol kpc**-3")

    surf_den_gas = sph.image(
        h[j].g,
        qty="hrm",
        units="Msol pc^-2",
        width=phys_size,
        cmap="viridis",
        show_cbar=False,
        noplot=True,
        ret_im=True,
    )
    axes[i + 2].set_facecolor("black")
    c_gas = axes[i + 2].imshow(
        np.log10(surf_den_gas).T,
        interpolation="nearest",
        extent=(-phys_size / 2.0, phys_size / 2.0, -phys_size / 2.0, phys_size / 2.0),
        cmap="viridis",
        vmin=-0.6,
        vmax=2.0,
    )

    phys_size = phys_size / 2.0
    axes[i + 2].plot(
        np.array([0.9 * phys_size - 25, 0.9 * phys_size]),
        np.array([-0.9 * phys_size, -0.9 * phys_size]),
        linestyle="-",
        lw=2.0,
        color="white",
    )
    axes[i + 2].text(
        0.775,
        0.075,
        "25 kpc",
        fontsize=25,
        color="white",
        horizontalalignment="left",
        verticalalignment="center",
        transform=axes[i + 2].transAxes,
    )
    axes[i + 2].text(
        0.5,
        0.925,
        sim[0:8],
        fontsize=35,
        color="white",
        horizontalalignment="center",
        verticalalignment="center",
        transform=axes[i + 2].transAxes,
    )

    # star projection close
    phys_size = 40
    # face-on image
    axes[i + 3].set_facecolor("black")
    face = pb.plot.stars.render(
        h[j], dynamic_range=3, ret_im=True, plot=False, width=str(phys_size) + " kpc"
    )
    axes[i + 3].imshow(
        face,
        extent=(-phys_size / 2.0, phys_size / 2.0, -phys_size / 2.0, phys_size / 2.0),
    )

    phys_size = phys_size / 2.0
    # phys_size = 2*phys_size
    axes[i + 3].plot(
        np.array([0.9 * phys_size - 15, 0.9 * phys_size]),
        np.array([-0.9 * phys_size, -0.9 * phys_size]),
        linestyle="-",
        lw=2.0,
        color="white",
    )
    axes[i + 3].text(
        0.775,
        0.075,
        "15 kpc",
        fontsize=25,
        color="white",
        horizontalalignment="left",
        verticalalignment="center",
        transform=axes[i + 3].transAxes,
    )
    axes[i + 3].text(
        0.5,
        0.925,
        sim[0:8],
        fontsize=35,
        color="white",
        horizontalalignment="center",
        verticalalignment="center",
        transform=axes[i + 3].transAxes,
    )

    # edge-on image
    phys_size = 40

    s.rotate_y(90)
    side = pb.plot.stars.render(
        h[j], dynamic_range=3, ret_im=True, plot=False, width=str(phys_size) + " kpc"
    )
    axes[i + 4].set_facecolor("black")
    axes[i + 4].imshow(
        side[:, int(3 * side.shape[0] / 8.0) : int(5 * side.shape[0] / 8.0)],
        extent=(-phys_size / 8.0, phys_size / 8.0, -phys_size / 2.0, phys_size / 2.0),
    )


cb = plt.colorbar(c_dm_far, cax=axes[0], orientation="horizontal")
cb.set_label(r"log$(\Sigma_{\rm DM}/M_{\rm\odot}\rm{pc}^{-2})$", labelpad=2)
cb.ax.xaxis.set_ticks_position("top")
cb.ax.xaxis.set_label_position("top")

cb1 = plt.colorbar(c_star_far, cax=axes[1], orientation="horizontal")
cb1.set_label(r"log$(\Sigma_{\rm star}/M_{\rm\odot}\rm{pc}^{-2})$", labelpad=2)
cb1.ax.xaxis.set_ticks_position("top")
cb1.ax.xaxis.set_label_position("top")

cb2 = plt.colorbar(c_gas, cax=axes[2], orientation="horizontal")
cb2.set_label(r"log$(\Sigma_{\rm HI}/M_{\rm\odot}\rm{pc}^{-2})$", labelpad=2)
cb2.ax.xaxis.set_ticks_position("top")
cb2.ax.xaxis.set_label_position("top")


plt.savefig(
    "/home/sw4445/nihao2/plots/maps/z2.0/surface_density.pdf", bbox_inches="tight"
)
