import numpy as np
import os
import shutil
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=DeprecationWarning)
 
from keysight.ads.de import db_uu as db
import keysight.ads.de as de
from keysight.ads.de.experimental.text_maker import TextMaker
import keysight.ads.dataset as dataset
from keysight.edatoolbox import ads
 
# Filter Design Parameters - Set appropriate design specifications
ripple_db = 0.1  # Passband ripple in dB
fc = 2000e6  # Passband Cutoff Frequency
fs = 3500e6  # Stopband Cutoff Frequency
R0 = 50  # Characteristic Impedance
N = 7  # Order of the Filter, choose Odd order only
 
Er = 3.66  # Relative Permittivity of the Substrate
tanD = 0.0023  # Loss Tangent of the Substrate
H_mm = 0.508  # Height of the substrate in mm
Zhigh = 130  # High Impedance Line Characteristic Impedance
Zlow = 15  # Low Impedance Line Characteristic Impedance
Feed_Length = 2 # 50 Ohm feed line length at input and output
 
# ADS Workspace and Design Creation
wrk_name = "Demo_Python_Tutorial6_wrk"
lib = "Demo_Python_Tutorial6_lib"
cell = "cell_lpf"
HOME = "C:/ADS_Python_Tutorials/"
 
 
def lpf_design_by_N(ripple_db, fc, fs, R0, N):
    ep = 10 ** (ripple_db / 10) - 1
    pi = np.pi
    wc = 2 * pi * fc  # angular passband freq
    ws = 2 * pi * fs  # angular stopband freq
 
    La = 0 - 10 * np.log10(1 + ep * np.cosh((N * np.arccosh(ws / wc))) ** 2)
    La = round(La, 2)
 
    beta = np.log(1 / np.tanh(ripple_db / 17.37))
 
    gamma = np.sinh(beta / (2 * N))
 
    L = []
    C = []
    ak = []
    bk = []
    gk = []
 
    for k in range(1, N + 1):
        a1 = np.sin(((2 * k - 1) * pi) / (2 * N))
        ak.append(a1)
 
        b1 = gamma**2 + (np.sin(k * pi / N)) ** 2
        bk.append(b1)
 
    for k in range(1, N + 1):
        if k == 1:
            gk.append(round(2 * ak[k - 1] / gamma, 4))
        else:
            gk.append(round((4 * ak[k - 2] * ak[k - 1]) / (bk[k - 2] * gk[k - 2]), 4))
 
        if k % 2 != 0:
            L.append(round(((R0 * gk[k - 1] / wc) / 1e-9), 2))
        else:
            C.append(round((gk[k - 1] / (R0 * wc)) / 1e-12, 2))
 
    return L, C, N, La, gk
 
# Chebyshev Low Pass Filter Design function
L, C, N, La, gk = lpf_design_by_N(ripple_db, fc, fs, R0, N)
 
print(f"\nLumped/Discrete Implementation for {N}th order Chebyshev LPF design:")
print(f"L[1-{len(L)}] = {L} nH")
print(f"C[1-{len(C)}] = {C} pF")
print("Estimated Attenuation @", fs / 1e9, "GHz =", La, "dB")
 
# Compute Microstrip implementation values for LPF design
def microstrip_calc_fromZ0(Er, H_mm, Z0):
    Zeff = 40 - 2 * Er
 
    if Z0 > Zeff:
        # High Impedance calculation
        Heff = Z0 * np.sqrt(2 * (Er + 1)) / 119.9 + 1 / 2 * ((Er - 1) / (Er + 1)) * (
            np.log(np.pi / 2) + ((1 / Er) * np.log(4 / np.pi))
        )
        WH = 1 / (np.exp(Heff) / 8 - 1 / (4 * np.exp(Heff)))
        calc_w = WH * H_mm
    else:
        # Low Impedance calculation
        der = 59.95 * pow(np.pi, 2) / (Z0 * np.sqrt(Er))
        WH = (2 / np.pi) * ((der - 1) - np.log(2 * der - 1)) + (
            (Er - 1) / (np.pi * Er)
        ) * (np.log(der - 1) + 0.293 - (0.517 / Er))
        calc_w = WH * H_mm
 
    return calc_w
 
wlength = 3e11 / (fc * np.sqrt(Er))  # Wavelength in mm
beta = 2 * np.pi / wlength
 
Line_L = []
Line_C = []
 
for k in range(1, N + 1):
    if k % 2 != 0:
        Line_L.append(round(((R0 * gk[k - 1] / Zhigh) / beta), 2))
    else:
        Line_C.append(round((gk[k - 1] * Zlow / R0 / beta), 2))
 
w_ind = round(microstrip_calc_fromZ0(Er, H_mm, Zhigh), 2)
w_cap = round(microstrip_calc_fromZ0(Er, H_mm, Zlow), 2)
w50 = round(microstrip_calc_fromZ0(Er, H_mm, R0), 2)
 
print(f"\nMicrostrip Implementation for {N}th order Chebyshev LPF design:")
print("Inductive Line Lengths =", Line_L, "mm")
print("Width of Inductive Line =", round(w_ind, 2), "mm")
print("Capacitive Line Lenghts =", Line_C, "mm")
print("Width of Capacitive Line =", round(w_cap, 2), "mm")
print("Width of 50 Ohm Microstrip Line =", round(w50, 2), "mm \n")
 
 
def create_workspace_and_design_then_simulate_and_plot(
    wrk_name, lib, cell, HOME
) -> None:
    wrk_space_path = os.path.join(HOME, wrk_name)
 
    # ensure to start from a closed workspace
    if de.workspace_is_open():
        de.close_workspace()
 
    # delete the workspace if it exists
    if os.path.exists(wrk_space_path):
        shutil.rmtree(wrk_space_path)
 
    # create the workspace
    de.create_workspace(wrk_space_path)
    wrk_space = de.open_workspace(wrk_space_path)
    library = de.create_new_library(lib, os.path.join(wrk_space_path, lib))
    wrk_space.add_library(
        lib, os.path.join(wrk_space_path, lib), mode=de.LibraryMode.SHARED
    )
 
    library.setup_schematic_tech()
    library.create_layout_tech_std_ads("millimeter", 10000, False)
    design = db.create_schematic(lib + ":" + cell + ":" + "schematic")
 
    v1 = design.add_instance(
        ("ads_datacmps", "VAR", "symbol"), (3.0, -3.125), name="VAR1", angle=-90
    )
    v2 = design.add_instance(
        ("ads_datacmps", "VAR", "symbol"), (4.75, -3.125), name="VAR2", angle=-90
    )
    assert v1.is_var_instance
    assert v2.is_var_instance
 
    design.add_instance(
        ("ads_simulation", "Term", "symbol"),
        (-3, -1),
        name="Term1",
        angle=-90,
    )
    design.add_instance(("ads_rflib", "GROUND", "symbol"), (-3, -2), name="", angle=-90)
    design.add_wire([(-3.0, -1), (-3.0, 0.0)])
    design.add_wire([(-3.0, 0), (-1.5, 0.0)])
 
    # Add a 50Ohm line at the input
    lip = design.add_instance(
        ("ads_tlines", "MLIN", "symbol"), (-1.5, 0), name="IP_50", angle=0
    )
    lip.parameters["W"].value = "w50 mm"
    lip.parameters["L"].value = f"{Feed_Length} mm"
    design.add_wire([(-0.5, 0.0), (0.0, 0.0)])
 
    # Add 50Ohm line at the output
    lop = design.add_instance(
        ("ads_tlines", "MLIN", "symbol"),
        ((3 * N - 1) / 2 + 0.5, 0),
        name="OP_50",
        angle=0,
    )
    lop.parameters["W"].value = "w50 mm"
    lop.parameters["L"].value = f"{Feed_Length} mm"
    design.add_wire([((3 * N - 1) / 2 + 1.5, 0), ((3 * N + 1) / 2 + 2, 0.0)])
 
    for i in range(len(Line_L)):
        tlin_L = design.add_instance(
            ("ads_tlines", "MLIN", "symbol"),
            (3 + (i - 1) * 3, 0),
            name="TL_L" + str(i + 1),
            angle=0,
        )
        tlin_L.parameters["W"].value = "w_ind" + str(i + 1) + " mm"
        tlin_L.parameters["L"].value = "Line_L" + str(i + 1) + " mm"
        v1.vars["Line_L" + str(i + 1)] = str(Line_L[i])
        v1.vars["w_ind" + str(i + 1)] = str(w_ind)
        design.add_wire([(4 + (i - 1) * 3, 0.0), (4.5 + (i - 1) * 3, 0.0)])
    for i in range(len(Line_C)):
        tlin_C = design.add_instance(
            ("ads_tlines", "MLIN", "symbol"),
            (4.5 + (i - 1) * 3, 0),
            name="TL_C" + str(i + 1),
            angle=0,
        )
        design.add_wire([(5.5 + (i - 1) * 3, 0), (6.0 + (i - 1) * 3, 0.0)])
        tlin_C.parameters["W"].value = "w_cap" + str(i + 1) + " mm"
        tlin_C.parameters["L"].value = "Line_C" + str(i + 1) + " mm"
        v2.vars["Line_C" + str(i + 1)] = str(Line_C[i])
        v2.vars["w_cap" + str(i + 1)] = str(w_cap)
 
    del v1.vars["X"]
    del v2.vars["X"]
    v2.vars["w50"] = str(w50)
    v2.vars["Er"] = "3.66"
    design.add_instance(
        ("ads_simulation", "Term", "symbol"),
        ((3 * N + 1) / 2 + 2, -1),
        name="Term2",
        angle=-90,
    )
    design.add_instance(
        ("ads_rflib", "GROUND", "symbol"),
        ((3 * N + 1) / 2 + 2, -2),
        name="",
        angle=-90,
    )
 
    design.add_wire([((3 * N + 1) / 2 + 1, 0), ((3 * N + 1) / 2 + 2, 0.0)])
    design.add_wire([((3 * N + 1) / 2 + 2, 0), ((3 * N + 1) / 2 + 2, -1.0)])
 
    sp = design.add_instance(
        ("ads_simulation", "S_Param", "symbol"), (0, -3), name="SP1"
    )
    sp.parameters["Start"].value = "0.001 GHz"
    sp.parameters["Stop"].value = str(fs * 1.5 / 1e9) + " GHz"
    sp.parameters["Step"].value = str(fs / 1e9 / 400) + " GHz"
 
    inst = design.add_instance("ads_tlines:MSUB", name="MSub1", origin=(6.5, -3.5))
    inst.parameters["H"].value = str(H_mm) + " mm"
    inst.parameters["Er"].value = "Er"
    inst.parameters["Cond"].value = "5.8E7"
    inst.parameters["Hu"].value = "1e+33 mm"
    inst.parameters["T"].value = "0.017 mm"
    inst.parameters["TanD"].value = str(tanD)
    inst.parameters["Rough"].value = "0 mm"
    inst.parameters["DielectricLossModel"].value = "1"
    inst.parameters["RoughnessModel"].value = "2"
    inst.invoke_item_parameter_changed_callback(["H"])
    inst.update_item_annotation()
 
    # Place desired text on ADS Schematic
    layer_id = db.LayerId(231 if design.is_schematic is True else 1)
    # Create the text & Style
    text_maker = TextMaker(design)
    text_maker.height = 0.225
    text_maker.font_name = "Arial Bold Italic"
    text_maker.align = db.TextAlignment.UPPER_LEFT
    text_maker.orient = db.Orientation.R0
    origin = (0.0, 2.0)
    text_maker.add_text(
        layer_id, "Synthesized Filter Design using Python for ADS...!", origin
    )
    # text_maker.add_text(layer_id, "Expected Filter Characteristics:", (0.0,1.7))
    text_maker.add_text(layer_id, "Filter Order : " + str(N), (0.0, 1.4))
    # text_maker.add_text(layer_id, "Expected Rejection at "+str(fs/1e9)+" GHz : "+str(La2)+ " dB", (0.0,1.1))
     
     
    return design
 
design = create_workspace_and_design_then_simulate_and_plot(wrk_name, lib, cell, HOME)
design.save_design()
 
inst = design.add_instance("ads_simulation:ParamSweep", name="Sweep1",origin=(8.5,-3))
inst.parameters["SweepVar"].value = '"Er"'
inst.parameters["SimInstanceName"].repeats[0].value='"SP1"'
inst.parameters["Start"].value = '3'
inst.parameters["Stop"].value = '4'
inst.parameters["Step"].value = '0.1'
inst.parameters["Sort"].value = 'LINEAR START STEP '
inst.update_item_annotation()
design.save_design()
 
netlist = design.generate_netlist()
simulator = ads.CircuitSimulator()
output_dir = os.path.join(HOME, wrk_name, "data")
simulator.run_netlist(netlist, output_dir=output_dir)
 
data = dataset.open(os.path.join(output_dir, cell + ".ds"))
 
#Inspect available data blocks in the dataset
for datablock in data.find_varblocks_with_var_name("S[2,1]"):
    sp=datablock.name
 
# Create a line plot
df = data[sp].to_dataframe().reset_index() 
 
plt.figure(figsize=(8, 6))
df["freq"] = df["freq"] / 1e9
df["S[2,1]"] = 20 * np.log10(abs(df["S[2,1]"]))
df["S[1,1]"] = 20 * np.log10(abs(df["S[1,1]"]))
 
sns.lineplot(
data=df,
x="freq",  
y="S[2,1]",
hue="Er",  
palette="tab10",
legend=False
)
sns.lineplot(
data=df,
x="freq",  
y="S[1,1]",
hue="Er",  
palette="tab10",
legend=True
)
 
handles, labels = plt.gca().get_legend_handles_labels()
 
# Format the labels to one decimal place
formatted_labels = [f"{float(label):.1f}" for label in labels]
 
# Set the formatted labels back to the legend
 
plt.legend(handles, formatted_labels, loc='center left', bbox_to_anchor=(1, 0.5),title="Er")
plt.ylabel("S11 & S21 (dB)")
plt.xlabel("Frequency (GHz)")
plt.title("Filter Parameter Sweep")
plt.grid(True)
plt.tight_layout()  
plt.show()