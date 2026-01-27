"""
This script is continuation of the 1st tutorial script (https://abhargava.wordpress.com/2025/05/14/ads-python-tutorials-2/), run that script before running following code segment as shown in the YouTube video.
"""
 
design = db.create_schematic("tutorial1_lib:python_schematic:schematic")
 
# Alternatively, you can use the library pointer
# design = db.create_schematic(f"{lib.name}:python_schematic:schematic")
 
# Insert a resistor & create a pointer
r = design.add_instance(("ads_rflib", "R", "symbol"), (0, 0))
r.parameters["R"].value = "100 Ohm"
r.update_item_annotation()
 
# Insert another resistor with 90deg rotation but no pointer
design.add_instance("ads_rflib:R:symbol", (2, 0), name="myR", angle=-90)
 
# Draw wire to connect both the resistors
design.add_wire([(1, 0), (2, 0)])
 
# Logic to create a pointer to a instance in the design and then update its value
myr = design.instances.get("myR")
myr.parameters["R"].value = "1000 Ohm"
myr.update_item_annotation()
 
# Function to iterate through all instanaces in the design, search for a specific
# component and then modify the value
for inst in design.instances:
    print(inst)
    if inst.name == "myR":
        inst.parameters["R"].value = "100 Ohm"
        inst.update_item_annotation()
        print("Instance value is updated")
 
# Iterate though instances and print model definition parameters for each of them
for inst in design.instances:
    print(inst.model_def.parameters)
 
 
# Create a LC ladder network with a for loop
num_inds = 5
num_caps = num_inds - 1
 
for i in range(num_inds):
    ind = design.add_instance("ads_rflib:L:symbol", (i * 2, -2))
    ind.parameters["L"].value = "70 nH"
    ind.update_item_annotation()
    design.add_wire([(i * 2 + 1, -2), (i * 2 + 2, -2)])
 
for i in range(num_caps):
    cap = design.add_instance("ads_rflib:C:symbol", (i * 2 + 1.5, -3), angle=-90)
    cap.parameters["C"].value = "30 pF"
    cap.update_item_annotation()
    design.add_wire([(i * 2 + 1.5, -2), (i * 2 + 1.5, -3)])
    design.add_instance("ads_rflib:GROUND:symbol", (i * 2 + 1.5, -4), angle=-90)
 
design.save_design()