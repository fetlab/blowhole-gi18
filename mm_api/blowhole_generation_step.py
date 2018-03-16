import os
import sys
import pickle

import wx 

import mmapi
from mmRemote import *
import mm

#feedback text
statusText = None

#size in x of the target object
#size_x=51.863*1.0
size_x=129.66*1.0
#size_x=79.681*1.0

#list of selected area
selected_area=list()

#list of hole sizes
hole_sizes=[6,8,10,12,14]
hole_sizes.sort(reverse=True)
used_sizes=list()

function_call=dict()

def setStatusText(txt):
	""" Updates the text in the status bar """
	global statusText
	statusText.SetLabel(txt)

def ask(parent=None, message='', default_value=''):
    dlg = wx.TextEntryDialog(parent, message, defaultValue=default_value)
    dlg.ShowModal()
    result = dlg.GetValue()
    dlg.Destroy()
    return result	

def createGUI():
	""" Creates window for us to work with """
	#Creates app instance for GUI
	app = wx.App()
		
	#Creates Window
	window = wx.Frame(None,size=(400,200), style= wx.STAY_ON_TOP | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)

	#Creates button, adds it to the window and binds the function to the button
	addButton = wx.Button(window,id=2, label="Add Position", pos=(8, 10), size=(200, 20))
	window.Bind(wx.EVT_BUTTON, addPosition, addButton)

	#Creates button, adds it to the window and binds the function to the button
	#runButton = wx.Button(window,id=-1, label="Blow Holes!", pos=(8, 35), size=(200, 20))
	#window.Bind(wx.EVT_BUTTON, scriptButton, runButton)

	#Creates the status text bar
	global statusText
	statusText = wx.StaticText(window,-1, "Select an area in MeshMixer then click Add Position", pos=(8, 80), size=(384, 20))

	window.SetTitle("Blow Holes Editor")#Sets the title of the window
	#window.Centre()#Centers it in the middle of the screen
	window.Move((900,100))
	window.Show(True)#Should be true or the window won't show up
	app.MainLoop()

def addPosition(event):
	obj_list = mm.list_selected_objects(remote)
	mm.select_objects(remote, [obj_list[0]])
	# check that we have a selection
	cur_groups = mm.list_selected_groups(remote)
	if len(cur_groups) == 0:
		setStatusText("Error! Please select an area")
	else:
		print("1:")
		setStatusText("Computing...")
		centroid = mm.get_face_selection_centroid(remote)
		(bFound, Frame) = mm.find_nearest(remote, centroid)
		flag_done=0
		for size in hole_sizes:	
			if size in used_sizes:
				continue
			print("Test:"+str(size)+":"+str(TestFit(Frame,[size,size,size],5)))
			if TestFit(Frame,[size,size,size],5):
				print("Created size with"+str(size))
				used_sizes.append(size)
				create_ring(Frame,[8,2,8])
				drill_holes(Frame,pipe_filename,[1,0.5,1],0,0)
				drill_holes(Frame,hole_filename,[size,size,size],5,1)
				flag_done=1
				break
		print("2:"+str(flag_done))
		if flag_done==0:
			setStatusText("Unable to create hole here, Please select another area")
		else:
			#text = ask(message = 'What do you want to do here?')
			#function_call[size]=text
			#pickle.dump( function_call, open( "function_dict.p", "wb" ) )
			setStatusText("Position added, now you can select another area")
		#selected_area.append(Frame)
		mm.clear_face_selection(remote)
	
def TestIntersection(id1,id2):
	cmd_TI=mmapi.StoredCommands()
	key_TI=cmd_TI.AppendQueryCommand_TestIntersection(id1,id2)
	remote.runCommand(cmd_TI)
	return cmd_TI.GetQueryResult_TestIntersection(key_TI)

def TestFit(selFrame, scale_size, move_dy):
	new_objs = mm.append_objects_from_file(remote, hole_filename);
	mm.select_objects(remote, new_objs)

	mm.begin_tool(remote, "transform")
	mm.set_toolparam(remote, "scale",scale_size)
	mm.accept_tool(remote)
	
	(min,max) = mm.get_selected_bounding_box(remote)

	mm.begin_tool(remote, "transform")
	cur_origin = mm.get_toolparam(remote, "origin")
	dy =-((cur_origin[1] - min[1])+move_dy*2/size_x)
	rotation = mm.make_matrix_from_axes(selFrame.x, mm.negv3(selFrame.z), selFrame.y )
	mm.set_toolparam(remote, "rotation", rotation )

	translate = mm.subv3( selFrame.origin, cur_origin )
	translate = mm.addv3( translate, mm.mulv3s( selFrame.z, dy ) )
	mm.set_toolparam(remote, "translation", translate )
	mm.accept_tool(remote)
	
	mm.select_objects(remote, [obj_list[0], new_objs[0]])
	result=TestIntersection(obj_list[0],new_objs[0])
	mm.select_objects(remote, [new_objs[0]])
	cmd_D = mmapi.StoredCommands()
	cmd_D.AppendSceneCommand_DeleteSelectedObjects();
	remote.runCommand(cmd_D)
	mm.select_objects(remote, [obj_list[0]])
	return not result

# 1 move_dy is 1mm
def drill_holes(selFrame,filenames,scale_size,move_dy,flag_set_dy):
	new_objs = mm.append_objects_from_file(remote, filenames);
	mm.select_objects(remote, new_objs)

	mm.begin_tool(remote, "transform")
	mm.set_toolparam(remote, "scale",scale_size)
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

def create_ring(selFrame,scale_size):
	new_objs = mm.append_objects_from_file(remote, ring_name);
	mm.select_objects(remote, new_objs)

	mm.begin_tool(remote, "transform")
	mm.set_toolparam(remote, "scale",scale_size)
	mm.accept_tool(remote)
	
	(min,max) = mm.get_selected_bounding_box(remote)

	mm.begin_tool(remote, "transform")
	cur_origin = mm.get_toolparam(remote, "origin")
	#dy = flag_set_dy*(-((cur_origin[1] - min[1])+move_dy*2/size_x))
	rotation = mm.make_matrix_from_axes(selFrame.x, mm.negv3(selFrame.z), selFrame.y )
	mm.set_toolparam(remote, "rotation", rotation )

	translate = mm.subv3( selFrame.origin, cur_origin )
	#translate = mm.addv3( translate, mm.mulv3s( selFrame.z, dy ) )
	mm.set_toolparam(remote, "translation", translate )
	mm.accept_tool(remote)

	#mm.begin_tool(remote, "duplicate")
	#mm.accept_tool(remote)

	mm.select_objects(remote, [obj_list[0], new_objs[0]] )

	mm.begin_tool(remote, "combine")
	mm.accept_tool(remote)
	return

# main
examples_dir = os.getcwd()
pipe_filename = os.path.join( examples_dir, "pipe.obj" )
hole_filename = os.path.join( examples_dir, "hole.obj" )
#sphere_filename=os.path.join( examples_dir, "sphere_16.stl" )
ring_name=os.path.join( examples_dir, "ring.obj" )



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



