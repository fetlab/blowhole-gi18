import os
import sys

import wx 

import mmapi
from mmRemote import *
import mm

#feedback text
statusText = None

#size in x of the target object
#size_x=51.863*1.0
size_x=129.66

#list of selected area
selected_area=list()

#list of hole sizes
hole_sizes=[6,8,10,12,14,16,18,20]
used_sizes=list()

def setStatusText(txt):
	""" Updates the text in the status bar """
	global statusText
	statusText.SetLabel(txt)
	
def createGUI():
	""" Creates window for us to work with """
	#Creates app instance for GUI
	app = wx.App()
		
	#Creates Window
	window = wx.Frame(None, size=(400,200), style= wx.STAY_ON_TOP | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)

	#Creates button, adds it to the window and binds the function to the button
	addButton = wx.Button(window,id=2, label="Add Position", pos=(8, 10), size=(200, 20))
	window.Bind(wx.EVT_BUTTON, addPosition, addButton)

	#Creates button, adds it to the window and binds the function to the button
	runButton = wx.Button(window,id=-1, label="Blow Holes!", pos=(8, 35), size=(200, 20))
	window.Bind(wx.EVT_BUTTON, scriptButton, runButton)

	#Creates the status text bar
	global statusText
	statusText = wx.StaticText(window,-1, "Select an area in MeshMixer then click Add Position", pos=(8, 80), size=(384, 20))

	window.SetTitle("Blow Holes Editor")#Sets the title of the window
	window.Centre()#Centers it in the middle of the screen
	window.Show(True)#Should be true or the window won't show up
	app.MainLoop()#

def addPosition(event):
	""" Function that is called when "Add Position" is pressed """
	# check that we have a selection
	cur_groups = mm.list_selected_groups(remote)
	if len(cur_groups) == 0:
		setStatusText("Error! Please select an area")
	else:
		centroid = mm.get_face_selection_centroid(remote)
		sel_ctr = centroid
		(bFound, Frame) = mm.find_nearest(remote, sel_ctr)
		selected_area.append(Frame)
		mm.clear_face_selection(remote)
		setStatusText("Position Added")

def scriptButton(theEvent):
	""" Called when our "Blow Hole" button is pressed """
	print(len(selected_area))
	setStatusText("Computing")
	for area in selected_area:
		drill_holes(area,pipe_filename,[1,0.5,1],0,0)
		drill_holes(area,hole_filename,[12,12,12],5,1)
		#drill_holes(area,sphere_filename,[1,1,1],-0.5,1)
	setStatusText("Finished")

class State():
    def __init__(self,input_val):
		self.children = list()
		self.parent = None
		self.object_id = input_val
		self.possible_size = hole_sizes

def DFS_Compute_Model(root_id):
	root=State(root_id)
	
	
	
	#copy model
	mm.select_objects(remote, obj_list[0])
	mm.begin_tool(remote, "duplicate")
	mm.accept_tool(remote)
	
def TestIntersection(id1,id2):
	cmd_TI=mmapi.StoredCommands()
	key_TI=cmd_TI.AppendQueryCommand_TestIntersection(id1,id2)
	remote.runCommand(cmd_TI)
	return cmd_TI.GetQueryResult_TestIntersection(key_TI)

# 1 move_dy is 1mm
def drill_holes(selFrame,filenames,scale_size,move_dy,flag_set_dy):
	new_objs = mm.append_objects_from_file(remote, filenames);
	mm.select_objects(remote, new_objs)

	mm.begin_tool(remote, "transform")
	mm.set_toolparam(remote, "scale",scale_size)
	#mm.set_toolparam(remote, "translation", [0,0,0])
	mm.accept_tool(remote)
	
	(min,max) = mm.get_selected_bounding_box(remote)

	mm.begin_tool(remote, "transform")
	cur_origin = mm.get_toolparam(remote, "origin")
	dy = flag_set_dy*(-((cur_origin[1] - min[1])+move_dy*2/size_x))
	rotation = mm.make_matrix_from_axes(selFrame.x, mm.negv3(selFrame.z), selFrame.y )
	mm.set_toolparam(remote, "rotation", rotation )

	translate = mm.subv3( selFrame.origin, cur_origin )
	translate = mm.addv3( translate, mm.mulv3s( selFrame.z, dy ) )
	mm.set_toolparam(remote, "translation", translate )
	mm.accept_tool(remote)

	#mm.begin_tool(remote, "duplicate")
	#mm.accept_tool(remote)

	mm.select_objects(remote, [obj_list[0], new_objs[0]] )

	mm.begin_tool(remote, "difference")
	mm.accept_tool(remote)
	return

# main
examples_dir = os.getcwd()
pipe_filename = os.path.join( examples_dir, "pipe.obj" )
hole_filename = os.path.join( examples_dir, "hole.obj" )
sphere_filename=os.path.join( examples_dir, "sphere_16.stl" )



# initialize connection
remote = mmRemote()
remote.connect()

#print(mm.list_objects(remote))
#print(TestIntersection(16,18))

# assumption: we have object we want to modify selected
obj_list = mm.list_selected_objects(remote)

#GUI
createGUI()

#done!
#remote.shutdown()



