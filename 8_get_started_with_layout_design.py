import os
import shutil
import keysight.ads.de as de
from keysight.ads.de import db_uu
from keysight.ads.de.db import LayerId
 
wrk_name = "Python_Tutorial8_wrk"
lib = "Python_Tutorial8_lib"
cell = "Demo_Layout"
path = r"C:\ADS_Python_Tutorials"
 
wrk_path = os.path.join(path, wrk_name)
lib_path = os.path.join(wrk_path, lib)
 
# Check if the workspace exists and delete it if it does
if os.path.exists(wrk_path):
    shutil.rmtree(wrk_path)
 
de.create_workspace(wrk_path)
wrk_space = de.open_workspace(wrk_path)
library = de.create_new_library(lib, lib_path)
wrk_space.add_library(lib, lib_path, mode=de.LibraryMode.SHARED)
 
# Create schematic and layout technology
library.setup_schematic_tech()
# Create layout technology with standard ADS layout layers
library.create_layout_tech_std_ads("millimeter", 10000, False)
 
# Create a layout cell
layout = db_uu.create_layout(f"{library.name}:{cell}:layout")
 
# Add some basic shapes on layer "cond:drawing"
cond = LayerId.create_layer_id_from_library(library, "cond", "drawing")
 
# Add some basic shapes
layout.add_rectangle(cond, (0, 0), (5, 1))
layout.add_circle(cond, (6, 0.5), 0.5)
layout.add_polygon(cond, [(8, 0), (10, 3), (13, 3), (15, 0), (13, -3), (10, -3)])
layout.add_path(cond, [(0, -5), (2, -5), (2, -2), (4, -2)], 0.3)
layout.add_trace(cond, [(4, -5), (6, -5), (6, -2), (8, -2)], 0.3)
 
# Save the layout
layout.save_design()