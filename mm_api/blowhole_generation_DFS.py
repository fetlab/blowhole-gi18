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
size_x=129.66*1.0
#size_x=79.681*1.0

#list of selected area
selected_area=list()

#list of hole sizes
hole_sizes=[6,8,10,12,14,16,18,20]



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
	cur_groups = mm.list_selected_groups(remote)
	if len(cur_groups) == 0:
		setStatusText("Error! Please select an area")
	else:
		centroid = mm.get_face_selection_centroid(remote)
		(bFound, Frame) = mm.find_nearest(remote, centroid)
		selected_area.append(Frame)
		mm.clear_face_selection(remote)
		setStatusText("Position Added")

#hole_sizes=[6,50,8,10,60]
def scriptButton(theEvent):	
	print("!!!!!!!!!function blow hole!!!!!!!!!!!!")
	flag_done=0
	root=State(mm.list_selected_objects(remote)[0])
	cur_state=root
	possible_size=root.possible_size
	remain_area=list(selected_area)
	used_sizes=list()
	print("area:"+str(len(remain_area))+","+str(remain_area))
	while (len(possible_size) and len(remain_area)):
		print("###in while loop###")
		print("1: cur "+str(cur_state.object))
		mm.select_objects(remote, [cur_state.object])
		mm.begin_tool(remote, "duplicate")
		mm.accept_tool(remote)
		copy_object=mm.list_selected_objects(remote)[0]
		print("2:"+str(copy_object))
		cur_frame=remain_area.pop()
		cur_state.frame=cur_frame
		print(["3:",cur_frame])
		flag_done=0
		print("4: used "+str(used_sizes))
		print("4: possi "+str(possible_size))
		print("4: cur_possi "+str(cur_state.possible_size))
		for size in possible_size:
			if not TestFit(copy_object,cur_frame,[size,size,size],5):
				cur_state.possible_size.remove(size)
			else:
				print("5 select:"+str(size))
				print("5: "+str(TestFit(copy_object,cur_frame,[size,size,size],5)))
				print("6:"+str(cur_state.possible_size))
				flag_done=1
				cur_state.possible_size.remove(size)
				print("6:"+str(cur_state.possible_size))
				cur_state.used_size=size
				used_sizes.append(size)
				print("7:"+str(used_sizes))
				create_ring(copy_object,cur_frame,[8,2,8])
				drill_holes(copy_object,cur_frame,pipe_filename,[1,0.5,1],0,0)
				drill_holes(copy_object,cur_frame,hole_filename,[size,size,size],5,1)
				new_state=State(copy_object)
				print("9: new "+str(new_state.object))
				new_state.parent=cur_state
				new_state.possible_size=list(set(hole_sizes) - set(used_sizes))
				print("10:"+str(new_state.possible_size))
				cur_state=new_state
				possible_size=cur_state.possible_size
				print("11:"+str(possible_size))
				break
		if not cur_state.parent:
			possible_size=list()
			break
		if flag_done==0:
			print("12: failed")
			new_state=cur_state.parent
			print("13: "+str(cur_state.frame))
			remain_area.append(cur_state.frame)
			used_sizes.append(new_state.used_size)
			print("15: "+str(possible_size))
			possible_size=cur_state.possible_size
	if not len(remain_area):
		print("done area:"+str(len(remain_area)))
		setStatusText("Success!")
		#selected_area=[]
	else:
		setStatusText("Unable to assign the holes")
		#selected_area=[]


class State():
    def __init__(self,in_object):
		self.children = list()
		self.parent = None
		self.object = in_object
		self.frame = None
		self.possible_size = list(hole_sizes)
		self.used_size=None

	
def TestIntersection(id1,id2):
	cmd_TI=mmapi.StoredCommands()
	key_TI=cmd_TI.AppendQueryCommand_TestIntersection(id1,id2)
	remote.runCommand(cmd_TI)
	return cmd_TI.GetQueryResult_TestIntersection(key_TI)

def delete_select_objects():
	cmd_D = mmapi.StoredCommands()
	cmd_D.AppendSceneCommand_DeleteSelectedObjects();
	remote.runCommand(cmd_D)

def TestFit(tar_object, selFrame, scale_size, move_dy):
	new_objs = mm.append_objects_from_file(remote, hole_filename);
	mm.select_objects(remote, new_objs)

	mm.begin_tool(remote, "transform")
	mm.set_toolparam(remote, "scale",scale_size)
	#mm.set_toolparam(remote, "translation", [0,0,0])
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
	
	mm.select_objects(remote, [tar_object, new_objs[0]])
	result=TestIntersection(tar_object, new_objs[0])
	mm.select_objects(remote, [new_objs[0]])
	delete_select_objects()
	mm.select_objects(remote, [tar_object])
	return not result

# 1 move_dy is 1mm
def drill_holes(tar_object,selFrame,filenames,scale_size,move_dy,flag_set_dy):
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

	mm.select_objects(remote, [tar_object, new_objs[0]] )

	mm.begin_tool(remote, "difference")
	mm.accept_tool(remote)
	return

def create_ring(tar_object,selFrame,scale_size):
	new_objs = mm.append_objects_from_file(remote, ring_name);
	mm.select_objects(remote, new_objs)

	mm.begin_tool(remote, "transform")
	mm.set_toolparam(remote, "scale",scale_size)
	mm.accept_tool(remote)
	
	(min,max) = mm.get_selected_bounding_box(remote)

	mm.begin_tool(remote, "transform")
	cur_origin = mm.get_toolparam(remote, "origin")
	rotation = mm.make_matrix_from_axes(selFrame.x, mm.negv3(selFrame.z), selFrame.y )
	mm.set_toolparam(remote, "rotation", rotation )

	translate = mm.subv3( selFrame.origin, cur_origin )
	mm.set_toolparam(remote, "translation", translate )
	mm.accept_tool(remote)

	mm.select_objects(remote, [tar_object, new_objs[0]] )

	mm.begin_tool(remote, "combine")
	mm.accept_tool(remote)
	return
# main
examples_dir = os.getcwd()
pipe_filename = os.path.join( examples_dir, "pipe.obj" )
hole_filename = os.path.join( examples_dir, "hole.obj" )
ring_name=os.path.join( examples_dir, "ring.obj" )


# initialize connection
remote = mmRemote()
remote.connect()

#print(mm.list_objects(remote))
#print(TestIntersection(16,18))

# assumption: we have object we want to modify selected
obj_list = mm.list_selected_objects(remote)
print(obj_list)

#GUI
createGUI()

#done!
#remote.shutdown()



