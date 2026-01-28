import os
import shutil
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
 
import keysight.ads.de as de
from keysight.ads.de import db_uu
from keysight.ads.de.db_uu import Transaction
from keysight.ads.de import PointF
from keysight.edatoolbox import ads
import keysight.ads.dataset as dataset
 
warnings.simplefilter("ignore", DeprecationWarning)
 
wrk_name = "Python_Tutorial7_wrk"
lib = "Python_Tutorial7_lib"
path = "C:/ADS_Python_Tutorials"
cell = "Demo_PDK_Schematic"
ads_install_dir = "C:/Program Files/Keysight/ADS2025_Update2"
 
wrk_path = os.path.join(path, wrk_name)
lib_path = os.path.join(wrk_path, lib)
 
pdk_loc="examples/DesignKit/DemoKit_Non_Linear/DemoKit_Non_Linear_v2.0/DemoKit_Non_Linear"
 
pdk_tech_loc="examples/DesignKit/DemoKit_Non_Linear/DemoKit_Non_Linear_v2.0/DemoKit_Non_Linear_tech"
pdk_path = os.path.join(ads_install_dir, pdk_loc)
pdk_tech_path = os.path.join(ads_install_dir, pdk_tech_loc)
 
 
def create_workspace(wrk_path, lib, lib_path) -> de.Library:
    # Check if the workspace exists and delete it if it does
    if os.path.exists(wrk_path):
        shutil.rmtree(wrk_path)
 
    # Create the workspace
    de.create_workspace(wrk_path)
    # Open the workspace
    wrk_space = de.open_workspace(wrk_path)
 
    # Create the library
    library = de.create_new_library(lib, lib_path)
 
    wrk_space.add_library(lib, lib_path, mode=de.LibraryMode.SHARED)
 
    wrk_space.add_library("DemoKit_Non_Linear", pdk_path, mode=de.LibraryMode.READ_ONLY)
    wrk_space.add_library(
        "DemoKit_Non_Linear_tech", pdk_tech_path, mode=de.LibraryMode.READ_ONLY
    )
    open_pdk_lib = wrk_space.open_library(
        "DemoKit_Non_Linear", pdk_path, mode=de.LibraryMode.READ_ONLY
    )
 
    # Create schematic and layout technology
 
    library.setup_schematic_tech()
    library.create_layout_tech_from_pdk(open_pdk_lib, copy_tech=False)
 
    return library
 
wrk_lib = create_workspace(wrk_path, lib, lib_path)
 
def create_dciv_schematic(library, cell):
    # Create a schematic cell
    dst_design = db_uu.create_schematic(f"{library.name}:{cell}:schematic")
    dst_design = db_uu.open_design(f"{library.name}:{cell}:schematic")
 
    # Place Demo Include instance for MMIC DemoKit PDK to the schematic
    inst = dst_design.add_instance(
        "DemoKit_Non_Linear:DEMO_NETLIST_INCLUDE",
        name="DEMO_NETLIST_INCLUDE",
        origin=(-6.875, -1.875),
    )
    inst.parameters["NonLinearDemoKit_thermal"].value = "1"
    inst.update_item_annotation()
 
    with Transaction(dst_design) as transaction:
        inst = dst_design.add_instance(
            "DemoKit_Non_Linear:demo_fet2", name="M1", origin=(1.875, 0.0)
        )
        inst.parameters["model"].value = "model21"
        inst.parameters["nf"].value = "4"
        inst.invoke_item_parameter_changed_callback(["nf"])
        inst.update_item_annotation()
 
        inst = dst_design.add_instance(
            "ads_simulation:DC", name="DC1", origin=(0.25, -1.875)
        )
        inst.parameters["SweepVar"].value = '"VDS"'
        inst.parameters["Start"].value = "0"
        inst.parameters["Stop"].value = "5"
        inst.parameters["Step"].value = "0.1"
        inst.parameters["Sort"].value = "LINEAR START STEP "
        inst.update_item_annotation()
 
        inst = dst_design.add_instance(
            "ads_simulation:DisplayTemplate", name="disptemp1", origin=(-0.25, -4.375)
        )
        inst.orient = db_uu.Orientation.R90
        inst.parameters["TemplateName"].repeats[0].value = '"FET_curve_tracer"'
        inst.update_item_annotation()
 
        inst = dst_design.add_instance(
            "ads_simulation:ParamSweep", name="Sweep1", origin=(-3.25, -1.875)
        )
        inst.parameters["SweepVar"].value = '"VGS"'
        inst.parameters["SimInstanceName"].repeats[0].value = '"DC1"'
        inst.parameters["Start"].value = "-2.4"
        inst.parameters["Stop"].value = "0"
        inst.parameters["Step"].value = "0.2"
        inst.update_item_annotation()
 
        inst = dst_design.add_var_instance(name="VAR1", origin=(-4.375, -0.625))
        inst.orient = db_uu.Orientation.R90
        inst.vars.update({"VDS ": "0 V", "VGS ": "0 V"})
        del inst.vars["X"]  # Remove the 'X' variable from VAR1 block
        inst.update_item_annotation()
 
        inst = dst_design.add_instance(
            "ads_rflib:GROUND", name="G1", origin=(1.0, -1.375)
        )
        inst.orient = db_uu.Orientation.R270
        inst.update_item_annotation()
 
        inst = dst_design.add_instance(
            "ads_rflib:GROUND", name="G2", origin=(2.375, -0.5)
        )
        inst.orient = db_uu.Orientation.R270
        inst.update_item_annotation()
 
        inst = dst_design.add_instance(
            "ads_rflib:GROUND", name="G3", origin=(2.625, -0.5)
        )
        inst.orient = db_uu.Orientation.R270
        inst.update_item_annotation()
 
        inst = dst_design.add_instance(
            "ads_rflib:I_Probe", name="IDS", origin=(-0.125, 0.625)
        )
        inst.parameters["SaveCurrent"].value = "yes"
        inst.parameters["Layer"].value = '"cond:drawing"'
        inst.invoke_item_parameter_changed_callback(["Layer"])
        inst.update_item_annotation()
 
        inst = dst_design.add_instance(
            "ads_sources:V_DC", name="SRC2", origin=(-0.5, -0.375)
        )
        inst.orient = db_uu.Orientation.R270
        inst.parameters["Vdc"].value = "VGS"
        inst.parameters["SaveCurrent"].value = "1"
        inst.update_item_annotation()
 
        inst = dst_design.add_instance(
            "ads_sources:V_DC", name="SRC1", origin=(-2.5, 0.625)
        )
        inst.orient = db_uu.Orientation.R270
        inst.parameters["Vdc"].value = "VDS"
        inst.parameters["SaveCurrent"].value = "1"
        inst.update_item_annotation()
         
        dst_design.add_wire([(-2.5,0.625),(-0.125,0.625)])
        dst_design.add_wire([(0.125,0.625),(2.375,0.625),(2.375,0.5)])
        dst_design.add_wire([(1,-1.375),(-0.5,-1.375)])
        dst_design.add_wire([(-0.5,-1.375),(-2.5,-1.375),(-2.5,-0.375)])
        dst_design.add_wire([(-0.5,-0.375),(-0.5,0),(1.875,0)])
        transaction.commit()
 
        dst_design.save_design()
 
create_dciv_schematic(wrk_lib, cell)
 
def create_netlist_run_simulation(lib_name, cell_name, view_name) -> None:
    # Open the schematic design
    circuit = db_uu.open_design(f"{lib_name}:{cell_name}:{view_name}")
    print(f"Opening the schematic design: {circuit}")
    netlist = circuit.generate_netlist()
    print("Netlist generated successfully.")
    simulator = ads.CircuitSimulator()
    output_dir = os.path.join(wrk_path, "data")
    # run the netlist, this will block output
    simulator.run_netlist(netlist, output_dir=output_dir)
    print("Simulation completed successfully.")
    return output_dir
 
dataset_dir = create_netlist_run_simulation(lib, cell, "schematic")
 
def plot_dciv_data(output_dir, cell_name):
     
    data = dataset.open(os.path.join(output_dir, cell_name + ".ds"))
 
    #Inspect available data blocks in the dataset
    for datablock in data.find_varblocks_with_var_name("IDS.i"):
        dciv=datablock.name
 
    # Create a line plot
    df = data[dciv].to_dataframe().reset_index()
     
    # Convert IDS.i from A to mA
    df["IDS.i"] = df["IDS.i"] * 1000  # Scale current to mA
    warnings.simplefilter(action="ignore", category=FutureWarning)
    warnings.simplefilter(action="ignore", category=DeprecationWarning)
 
    # Format the VGS column to 4 decimal places
    df["VGS"] = df["VGS"].map(lambda x: f"{x:.2f}")
 
    # Plot DC IV characteristics
    plt.figure(figsize=(10, 6))
    sns.lineplot(
        data=df,
        x="VDS",  # Replace with the actual column name for VDS in your dataframe
        y="IDS.i",  # Replace with the actual column name for IDS.i in your dataframe
        hue="VGS",  # Replace with the actual column name for VGS in your dataframe
        palette="tab10",
    )
    plt.ylabel("Drain Current - Ids (mA)")
    plt.xlabel("Drain Voltage - Vds (V)")
    plt.title("DC-IV Characteristics")
    # Move the legend to the right side of the plot
    plt.legend(
        title="VGS (V)", bbox_to_anchor=(1.05, 1), loc="upper left", borderaxespad=0.0
    )
 
    plt.grid(True)
    plt.tight_layout()  # Adjust the layout to make it tight
    plt.show()
 
plot_dciv_data(dataset_dir, cell)