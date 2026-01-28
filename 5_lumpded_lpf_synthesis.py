import os
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from IPython.core import getipython
 
from keysight.ads import de
from keysight.ads.de import db_uu as db
from keysight.edatoolbox import ads
import keysight.ads.dataset as dataset
 
 
ripple_db = 0.1  # Passband ripple
fc = 800e6  # Passband corner freq in Hz
fs = 1500e6  # Stopband freq in Hz
R0 = 50  # Reference Impedance for Filter
La = 40  # Required attenuation at fs in dB
 
workspace_path = "C:/ADS_Python_Tutorials/tutorial5_wrk"
cell_name = "python_filter_schematic"
library_name = "tutorial5_lib"
 
 
# Chebyshev LPF Designer
def lpf_design_by_Atten(ripple_db, fc, fs, R0, La):
    ep = 10 ** (ripple_db / 10) - 1
    pi = np.pi
    wc = 2 * pi * fc  # angular passband freq
    ws = 2 * pi * fs  # angular stopband freq
 
    N = round(np.sqrt(np.arccosh((10 ** (La) - 1) / ep)) / np.arccosh(ws / wc)) - 1
 
    Atten = 0 - 10 * np.log10(1 + ep * np.cosh((N * np.arccosh(ws / wc))) ** 2)
    Atten = round(Atten, 2)
 
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
    return L, C, N, Atten, gk
 
 
# Design a low pass filter using the required attenuation method
L, C, N, La, gk = lpf_design_by_Atten(ripple_db, fc, fs, R0, La)
 
print("\ng-values=", gk)
print("Filter Design with Required Attenuation Method")
print("Computed Filter Order =", N)
print("Computed Rejection(dB) @ fs=", La)
print("L(nH) =", L)
print("C(pF) =", C)
 
 
def create_and_open_an_empty_workspace(workspace_path: str):
    # Ensure there isn't already a workspace open
    if de.workspace_is_open():
        de.close_workspace()
 
    # Cannot create a workspace if the directory already exists
    # Cannot create a workspace if the directory already exists
    if os.path.exists(workspace_path):
        raise RuntimeError(f"Workspace directory already exists: {workspace_path}")
 
    # Create the workspace
    workspace = de.create_workspace(workspace_path)
    # Open the workspace
    workspace.open()
    # Return the open workspace and close when it finished
    return workspace
 
 
def create_a_library_and_add_it_to_the_workspace(workspace: de.Workspace):
    # assert workspace.path is not None
    # Libraries can only be added to an open workspace
    assert workspace.is_open
    # We'll create a library in the directory of the workspace
    library_path = workspace.path / library_name
    # Create the library
    de.create_new_library(library_name, library_path)
    # And add it to the workspace (update lib.defs)
    workspace.add_library(library_name, library_path, de.LibraryMode.SHARED)
    lib = workspace.open_library(library_name, library_path, de.LibraryMode.SHARED)
    lib.setup_schematic_tech()
    return lib
 
 
ws = create_and_open_an_empty_workspace(workspace_path)
# Create and add library to the empty workspace using the pointer to the workspace
lib = create_a_library_and_add_it_to_the_workspace(ws)
 
 
def create_schematic(library: de.Library):
    design = db.create_schematic(f"{library_name}:{cell_name}:schematic")
 
    v = design.add_instance(
        ("ads_datacmps", "VAR", "symbol"), (3.5, -2.75), name="VAR1", angle=-90
    )
    assert v.is_var_instance
    for i in range(len(L)):
        ind = design.add_instance("ads_rflib:L:symbol", (i * 2, 0))
        ind.parameters["L"].value = f"L{i + 1} nH"
        ind.update_item_annotation()
        v.vars[f"L{i + 1}"] = f"{L[i]}"
        design.add_wire([(i * 2 + 1, 0), (i * 2 + 2, 0)])
 
    for i in range(len(C)):
        cap = design.add_instance("ads_rflib:C:symbol", (i * 2 + 1.5, -1), angle=-90)
        cap.parameters["C"].value = f"C{i + 1} pF"
        cap.update_item_annotation()
        v.vars[f"C{i + 1}"] = f"{C[i]}"
        design.add_wire([(i * 2 + 1.5, 0), (i * 2 + 1.5, -1)])
        design.add_instance("ads_rflib:GROUND:symbol", (i * 2 + 1.5, -2), angle=-90)
    del v.vars["X"]
 
    design.add_instance("ads_simulation:TermG:symbol", (-1, -1), angle=-90)
    design.add_wire([(-1, -1), (-1, 0), (0, 0)])
 
    design.add_instance("ads_simulation:TermG:symbol", (len(L) * 2 + 1, -1), angle=-90)
    design.add_wire([(len(L) * 2, 0), (len(L) * 2 + 1, 0.0)])
    design.add_wire([(len(L) * 2 + 1, 0), (len(L) * 2 + 1, -1.0)])
 
    sp = design.add_instance("ads_simulation:S_Param:symbol", (2, 2))
    sp.parameters["Start"].value = "0.01 GHz"
    sp.parameters["Stop"].value = f"{(fs * 2) / 1e9} GHz"
    sp.parameters["Step"].value = "0.01 GHz"
    sp.update_item_annotation()
    design.save_design()
    return design
 
 
# Create schematic with the lib object/pointer
design = create_schematic(lib)
 
netlist = design.generate_netlist()
simulator = ads.CircuitSimulator()
target_output_dir = os.path.join(workspace_path, "data")
simulator.run_netlist(netlist, output_dir=target_output_dir)
 
##### Data Processing & Plot #####
 
ipython = getipython.get_ipython()
output_data = dataset.open(
    Path(os.path.join(target_output_dir, f"{cell_name}" + ".ds"))
)
 
# Convert SP1.SP datablock to the pandas dataframe
mydata = output_data["SP1.SP"].to_dataframe().reset_index()
 
# Extract data and convert S21 & S11 to dB
freq = mydata["freq"] / 1e6
S21 = 20 * np.log10(abs(mydata["S[2,1]"]))
S11 = 20 * np.log10(abs(mydata["S[1,1]"]))
 
# Plot results using inline plot from matplotlib
ipython.run_line_magic("matplotlib", "inline")
_, ax = plt.subplots()
ax.set_title("Synthesized Filter Response")
plt.xlabel("Frequency (MHz)")
plt.ylabel("S21 and S11 (dB)")
plt.grid(True)
plt.plot(freq, S21)
plt.plot(freq, S11)