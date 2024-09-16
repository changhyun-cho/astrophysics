import pynbody
import os


def get_info(f):
    global dir_data, m_gal, n_file

    # extract mass and file numbers
    dir_data = str(f[:-14])
    m_gal = str(f[-14:-6])
    n_file = int(int(f[-5:]) / 16)


def run_AHF(file):

    get_info(file)

    print(dir_data)
    os.chdir(dir_data)
    for i in range(n_file):
        fname = dir_data + m_gal + "." + "{:05d}".format(int((i + 1) * 16))
        print(fname)
        s = pynbody.load(fname)
        s.halos()


if __name__ == "__main__":

    # last_file = str(sys.argv[1])
    # run_AHF(last_file)

    files = (
        "/data/cc6881/new_fb_test/parameter_test/g2.71e12_0.1_0.005/g2.71e12.01024",
        "/data/cc6881/new_fb_test/parameter_test/g2.71e12_0.1_0.001/g2.71e12.01024",
        "/data/cc6881/new_fb_test/parameter_test/g2.71e12_0.05_0.001/g2.71e12.01024",
        "/data/cc6881/new_fb_test/parameter_test/g2.71e12_0.05_0.005/g2.71e12.01024",
        "/data/cc6881/new_fb_test/parameter_test/g1.05e13_0.05_0.01/g1.05e13.01024",
        "/data/cc6881/new_fb_test/parameter_test/g1.05e13_0.05_0.05/g1.05e13.01024",
        "/data/cc6881/new_fb_test/parameter_test/g1.05e13_0.1_0.01/g1.05e13.01024",
        "/data/cc6881/new_fb_test/parameter_test/g1.05e13_0.1_0.05/g1.05e13.01024",
        "/data/cc6881/new_fb_test/parameter_test/g3.89e13_0.05_0.01/g3.89e13.01024",
        "/data/cc6881/new_fb_test/parameter_test/g3.89e13_0.05_0.05/g3.89e13.01024",
        "/data/cc6881/new_fb_test/parameter_test/g3.89e13_0.1_0.01/g3.89e13.01024",
        "/data/cc6881/new_fb_test/parameter_test/g3.89e13_0.1_0.05/g3.89e13.01024",
        # "/data/cc6881/output_NIHAO/agn/g2.71e12.01024",
        "/data/cc6881/new_fb_test/bondi/g2.71e12/g2.71e12.01024",
        "/data/cc6881/new_fb_test/alpha/g2.71e12/g2.71e12.01024",
        "/data/cc6881/new_fb_test/alpha/g2.71e12_scaled_alpha/g2.71e12.01024",
        # "/data/cc6881/output_NIHAO/agn/g8.26e11.01024",
        "/data/cc6881/new_fb_test/bondi/g8.26e11/g8.26e11.01024",
        "/data/cc6881/new_fb_test/alpha/g8.26e11/g8.26e11.01024",
        "/data/cc6881/new_fb_test/alpha/g8.26e11_scaled_alpha/g8.26e11.01024",
        # "/data/cc6881/output_NIHAO/agn/g1.55e12.01024",
        "/data/cc6881/new_fb_test/bondi/g1.55e12/g1.55e12.01024",
        "/data/cc6881/new_fb_test/alpha/g1.55e12/g1.55e12.01024",
        "/data/cc6881/new_fb_test/alpha/g1.55e12_scaled_alpha/g1.55e12.01024",
        "/data/cc6881/new_fb_test/bondi/g4.99e09/g4.99e09.01024",
        "/data/cc6881/new_fb_test/alpha/g4.99e09/g4.99e09.01024",
        "/data/cc6881/new_fb_test/alpha/g4.99e09_scaled_alpha/g4.99e09.01024",
        "/data/cc6881/new_fb_test/bondi/g7.12e10/g7.12e10.01024",
        "/data/cc6881/new_fb_test/alpha/g7.12e10/g7.12e10.01024",
        "/data/cc6881/new_fb_test/alpha/g7.12e10_scaled_alpha/g7.12e10.01024",
        "/data/cc6881/new_fb_test/bondi/g3.89e13/g3.89e13.01024",
        "/data/cc6881/new_fb_test/alpha/g3.89e13/g3.89e13.01024",
        "/data/cc6881/new_fb_test/alpha/g3.89e13_scaled_alpha/g3.89e13.01024",
        "/data/cc6881/new_fb_test/parameter_test/g2.71e12_0.05_0.01/g2.71e12.01024",
        "/data/cc6881/new_fb_test/parameter_test/g2.71e12_0.05_0.05/g2.71e12.01024",
        "/data/cc6881/new_fb_test/parameter_test/g2.71e12_0.05_0.02/g2.71e12.01024",
        "/data/cc6881/new_fb_test/parameter_test/g2.71e12_0.05_0.1/g2.71e12.01024",
        "/data/cc6881/new_fb_test/parameter_test/g2.71e12_0.05_0.2/g2.71e12.01024",
        "/data/cc6881/new_fb_test/parameter_test/g2.71e12_0.1_0.1/g2.71e12.01024",
        "/data/cc6881/new_fb_test/parameter_test/g2.71e12_0.1_0.05/g2.71e12.01024",
        "/data/cc6881/new_fb_test/parameter_test/g2.71e12_0.1_0.02/g2.71e12.01024",
        "/data/cc6881/new_fb_test/parameter_test/g2.71e12_0.1_0.01/g2.71e12.01024",
        "/data/cc6881/new_fb_test/parameter_test/g2.71e12_0.1_0.1/g2.71e12.01024",
        "/data/cc6881/new_fb_test/parameter_test/g2.71e12_0.1_0.2/g2.71e12.01024",
        # "/data/cc6881/new_fb_test/bondi/g2.71e12_big_seed/g2.71e12.01024",
        # "/data/cc6881/new_fb_test/alpha/g2.71e12_big_seed/g2.71e12.01024",
        # "/data/cc6881/new_fb_test/kinetic_test/g2.71e12/g2.71e12.01024",
        # "/data/cc6881/new_fb_test/kinetic_test/g2.71e12_erf/g2.71e12.01024",
        # "/data/cc6881/new_fb_test/kinetic_test/g2.71e12_obs_0.3/g2.71e12.01024",
        # "/data/cc6881/new_fb_test/10_thermal/alpha/g2.71e12.01024",
        # "/data/cc6881/new_fb_test/10_thermal/bondi/g2.71e12.01024",
        # "/data/cc6881/new_fb_test/BHseed_test/g2.71e12_alpha_2fb/g2.71e12.01024",
        # "/data/cc6881/new_fb_test/BHseed_test/g2.71e12_bondi_2fb/g2.71e12.01024",
        # "/data/cc6881/new_fb_test/BHseed_test/g2.71e12_twoFB_normal/g2.71e12.01024",
        # "/data/cc6881/new_fb_test/BHseed_test/g2.71e12_twoFB_alpha/g2.71e12.01024",
    )

    #        '/data/cc6881/gasfix_nihao1/g6.86e12/g6.86e12.01024',
    #             '/data/cc6881/movies/g7.08e11/g7.08e11.01024',
    #             '/data/cc6881/gasfix_nihao1/g8.94e12/g8.94e12.01024',
    #             '/data/cc6881/gasfix_nihao1/g2.02e13/g2.02e13.01024',
    #             '/data/cc6881/new_fb_test/torque_test/g2.71e12.01024',
    #             '/data/cc6881/movies/g1.12e12/g1.12e12.01024',
    #             '/data/cc6881/gasfix_nihao1/g2.11e13/g2.11e13.01024',
    #             '/data/cc6881/gasfix_nihao1/g2.20e13/g2.20e13.01024',
    #             '/data/cc6881/new_fb_test/alpha_test/g2.37e12.01024',
    #             '/data/cc6881/movies/g2.83e10/g2.83e10.01024')

    for file in files:
        try:
            run_AHF(file)
        except Exception:
            print("Next!")
    # run_AHF(file)

# python3 run_AHF.py <LAST CHECKPOINT>
