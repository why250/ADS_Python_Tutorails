from keysight.ads import de
from keysight.ads.de import db_uu as db
import os

workspace_path = "C:/ADS_Python_Tutorials/tutorial1_wrk"

def create_and_open_empty_workspace(workspace_path : str):
    #Ensure there isn't already a workspace open
    if de.workspace_is_open():
        de.close_workspace()
    
    # Cannot create a workspace if one already exists at the path
    if os.path.exists(workspace_path):
        raise Exception(f"Workspace already exists at {workspace_path}. Please delete it or choose a different path.")
    
    # Create a new workspace
    workspace = de.create_workspace(workspace_path)
    # Open the workspace
    workspace.open()
    # Return the open workspce and close when it finished
    return workspace

def create_a_library_and_add_it_to_the_workspace(workspace : de.Workspace, library_name : str):
    # Assert workspace.path is not None
    # Library can only be added to an open workspace
    assert workspace.is_open

    # Create a library in the directory of the workspace
    library_path = os.path.join(workspace.path, library_name)
    
    # Create the library
    de.create_new_library(library_name, library_path)
    
    # Add it to the workspace (update lib.defs)
    workspace.add_library(library_name, library_path, de.LibraryMode.SHARED)
    
    # Open and return the library
    lib = workspace.open_library(library_name, library_path, de.LibraryMode.SHARED)
    return lib

# Create and open an empty workspace
workspace = create_and_open_empty_workspace(workspace_path)
# Create a library and add it to the workspace
library_name = "tutorial1_lib"
lib = create_a_library_and_add_it_to_the_workspace(workspace, library_name)