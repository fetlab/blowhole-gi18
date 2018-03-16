import os
import sys

import wx 
import pickle

import mmapi
from mmRemote import *
import mm

#feedback text
statusText = None

#size in x of the target object
#size_x=51.863*1.0
size_x=129.66*1.0
#size_x=79.681*1.0 #earth

#size_x=110.0*1.0 #cell
#size_x=119.69 #rushmore
#size_x=80.0*1.0 #elephant
#size_x=80.0*1.0 #earth

#list of selected area
selected_area=list()

class candidates():
	def __init__(self, tl, sr):
		self.tl=tl
		self.sr=sr
		self.key=str(tb)+'-'+str(sr)

sr_list=[4.6, 5.2, 6, 6.4, 7,   7.8, 8.8, 10.4, 13.6]
tl_list=[1.6, 1.8, 2, 2.2, 2.4, 2.6, 3,   3.6,  4.6]


#tl_list=[1.6, 2.4, 4.6]
#sr_list=[4.6, 7, 13.6]

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

class State():
    def __init__(self,in_object):
    	self.children = list()
    	self.parent = None
    	self.object = in_object
    	self.frame = None
    	self.possible_size = list(sr_list)
    	self.used_size=None

final_result=0
used_sizes=list()
def backtracking(node):
	global final_result
	global used_sizes
	global selected_area
	global action_dict
	global frame_dict
	print("start: "+str(node.object))
	if selected_area==[]:
		final_result=node.object
		print(str(node.object)+" return 1")
		return 1
	cur_frame=selected_area.pop()
	while len(node.possible_size):
		if final_result:
			print("result found")
			print(str(node.object)+" break")
			break
		print(str(node.object)+" possible: "+str(node.possible_size))
		size=node.possible_size[0]
		move_dy = tl_list[sr_list.index(size)]
		if not TestFit(node.object,cur_frame,[size,size,size],move_dy):
		#if size in [4.6,5.2,6]:
			print(str(node.object)+" removed "+str(size))
			node.possible_size.remove(size)
		else:
			print(str(node.object)+" picked "+str(size))
			node.possible_size.remove(size)
			action_dict[size]=frame_dict[cur_frame]
			mm.select_objects(remote, [node.object])
			mm.begin_tool(remote, "duplicate")
			mm.accept_tool(remote)
			copy_object=mm.list_selected_objects(remote)[0]
			drill_holes(copy_object,cur_frame,pipe_filename,[1,0.1*move_dy+0.3,1],0,0)
			drill_holes(copy_object,cur_frame,hole_filename,[size,size,size],move_dy-1,1)
			child=State(copy_object)
			child.used_size=size
			used_sizes.append(size)
			child.frame=cur_frame
			print("used size: "+str(used_sizes))
			child.possible_size=list(set(sr_list) - set(used_sizes))
			print(str(child.object)+" possible: "+str(child.possible_size))
			backtracking(child)
			break
			
	print(str(node.object)+" return -2")
	if node.used_size!=None:
		used_sizes.remove(node.used_size)
	if node.frame!=None:
		selected_area.append(cur_frame)
	return -2

class Mywin(wx.Frame): 
	def __init__(self, parent, title): 
		super(Mywin, self).__init__(parent, title = title,size = (400,100))
		self.InitUI()
	
	def OnCreate(self, e): 
		if len(sr_list)<len(selected_area):
			self.text.SetValue("Too many selected area")
			return
		root = State(mm.list_selected_objects(remote)[0])
		backtracking(root)
		print(final_result)
		if final_result:
			cur_groups = mm.list_objects(remote)
			cur_groups.remove(final_result)
			print cur_groups
			#for obj in cur_groups:
			#	mm.select_objects(remote, [obj])
			#	delete_select_objects()
			mm.select_objects(remote, [final_result])
			pickle.dump(action_dict,open( "action_dict.p", "wb"))
			self.text.SetValue("Success!")
		else:
			self.text.SetValue("Unable to assign holes")

	
	def OnAdd(self, e):
		global frame_dict
		cur_groups = mm.list_selected_groups(remote)
		if len(cur_groups) == 0:
			self.text.SetValue("Error! Please select an area")
		else:
			centroid = mm.get_face_selection_centroid(remote)
			(bFound, Frame) = mm.find_nearest(remote, centroid)
			create_ring(mm.list_selected_objects(remote)[0],Frame,[7,2,7])
			selected_area.append(Frame)
			mm.clear_face_selection(remote)
			dlg = wx.TextEntryDialog(self,'What you want here', 'Text Entry Dialog','',wx.ICON_QUESTION | wx.OK | wx.CANCEL,(dis_size[0]-400,300))
			if dlg.ShowModal() == wx.ID_OK: 
				frame_dict[Frame]=str(dlg.GetValue())
			dlg.Destroy()
			self.text.SetValue("Position Added")
	
	def InitUI(self):    
		self.count = 0 
		pnl = wx.Panel(self)
		self.SetWindowStyle(wx.STAY_ON_TOP)
		vbox = wx.BoxSizer(wx.VERTICAL) 
		
		hbox1 = wx.BoxSizer(wx.HORIZONTAL) 
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3 = wx.BoxSizer(wx.HORIZONTAL)  
		self.text = wx.TextCtrl(pnl, size = (390, 30),style = wx.TE_READONLY)
		self.text.SetValue("Select an area in MeshMixer then click Add Position")
		self.btn1 = wx.Button(pnl, label = "Add Position")
		self.Bind(wx.EVT_BUTTON, self.OnAdd, self.btn1)
		self.btn2 = wx.Button(pnl, label = "Blowhole")
		self.Bind(wx.EVT_BUTTON, self.OnCreate, self.btn2) 
		
		hbox1.Add(self.text, proportion = 1, flag = wx.ALIGN_CENTRE) 
		hbox2.Add(self.btn1, proportion = 1, flag = wx.RIGHT, border = 15)
		hbox3.Add(self.btn2, proportion = 1, flag = wx.RIGHT, border = 15)
		
		vbox.Add((0, 10)) 
		vbox.Add(hbox2, proportion = 1, flag = wx.ALIGN_CENTRE) 
		vbox.Add((0, 20))
		vbox.Add(hbox3, proportion = 1, flag = wx.ALIGN_CENTRE) 
		vbox.Add((0, 20)) 
		vbox.Add(hbox1, flag = wx.ALIGN_CENTRE) 
		
		pnl.SetSizer(vbox) 
		#self.Centre() 
		self.Move((dis_size[0]-400,100))
		self.Show(True)
		
# main
examples_dir = os.getcwd()
pipe_filename = os.path.join( examples_dir, "pipe.obj" )
hole_filename = os.path.join( examples_dir, "hole.obj" )
ring_name=os.path.join( examples_dir, "ring.obj" )

remote = mmRemote()
remote.connect()

action_dict=dict()
frame_dict=dict()

ex = wx.App() 
dis_size=wx.GetDisplaySize()  
Mywin(None,'Blowhole Editor') 
ex.MainLoop()

#done!
#remote.shutdown()




