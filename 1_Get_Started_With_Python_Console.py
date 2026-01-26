from keysight.ads import de
from keysight.ads.de import db_uu as db
import os

workspace_path = "C:/ADS_Python_Tutorials/tutorial_workspace"

# Create a new workspace
workspace = de.create_workspace(workspace_path)

# Open the workspace
workspace.open()

# Create a library in thr diretory of the workspace
library_name = "tutorial_lib"
library_path = workspace_path + "/" + library_name

# Create the library
de.create_new_library(library_name,library_path)

# Add it to the workspace(update lib.defs)
workspace.add_library(library_name,library_path,de.LibraryMode.SHARED)

lib = workspace.open_library(library_name,library_path,de.LibraryMode.SHARED)