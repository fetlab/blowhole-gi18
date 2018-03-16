import os
import sys
import pickle

import wx 
 
import mmapi
from mmRemote import *
import mm


#size_x=51.863*1.0
size_x=129.66*1.0
#size_x=79.681*1.0

selected_area=list()

hole_sizes=[6,8,10,12,14,16,18,20]
hole_sizes=hole_sizes[0:5]
hole_sizes.sort(reverse=True)
used_sizes=list()

function_call=dict()

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
	rotation = mm.make_matrix_from_axes(selFrame.x, mm.negv3(selFrame.z), selFrame.y )
	mm.set_toolparam(remote, "rotation", rotation )

	translate = mm.subv3( selFrame.origin, cur_origin )
	mm.set_toolparam(remote, "translation", translate )
	mm.accept_tool(remote)

	mm.select_objects(remote, [obj_list[0], new_objs[0]] )

	mm.begin_tool(remote, "combine")
	mm.accept_tool(remote)
	return


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
			print("3:")
			text = ask(message = 'What do you want to do here?')
			print("4:")
			function_call[size]=text
			pickle.dump( function_call, open( "function_dict.p", "wb" ) )
			setStatusText("Position added, now you can select another area")
		#selected_area.append(Frame)
		mm.clear_face_selection(remote)

class Mywin(wx.Frame): 
	def __init__(self, parent, title): 
		super(Mywin, self).__init__(parent, title = title,size = (300,100))
		self.InitUI() 
         
	def InitUI(self):    
		self.count = 0 
		pnl = wx.Panel(self)
		self.SetWindowStyle(wx.STAY_ON_TOP)
		vbox = wx.BoxSizer(wx.VERTICAL) 
		
		hbox1 = wx.BoxSizer(wx.HORIZONTAL) 
		hbox2 = wx.BoxSizer(wx.HORIZONTAL) 
		self.text = wx.TextCtrl(pnl, size = (390, 30),style = wx.TE_READONLY)
		self.text.SetValue("Select an area in MeshMixer then click Add Position")
		self.btn1 = wx.Button(pnl, label = "Add Position") 
		self.Bind(wx.EVT_BUTTON, self.OnClick, self.btn1) 
		
		hbox1.Add(self.text, proportion = 1, flag = wx.ALIGN_CENTRE) 
		hbox2.Add(self.btn1, proportion = 1, flag = wx.RIGHT, border = 10)
		
		vbox.Add((0, 20)) 
		vbox.Add(hbox2, proportion = 1, flag = wx.ALIGN_CENTRE) 
		vbox.Add((0, 10)) 
		vbox.Add(hbox1, flag = wx.ALIGN_CENTRE) 
		
		pnl.SetSizer(vbox) 
		#self.Centre() 
		self.Move((dis_size[0]-300,100))
		self.Show(True)
		
	def OnClick(self, e): 
		obj_list = mm.list_selected_objects(remote)
		mm.select_objects(remote, [obj_list[0]])
		cur_groups = mm.list_selected_groups(remote)
		if len(cur_groups) == 0:
			self.text.SetValue("Error! Please select an area")
		else:
			self.text.SetValue("Computing...")
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
			if flag_done==0:
				self.text.SetValue("Unable to create hole here, Please select another area")
			else:
				dlg = wx.TextEntryDialog(self,'What you want here', 'Text Entry Dialog','',wx.ICON_QUESTION | wx.OK | wx.CANCEL,(dis_size[0]-300,200))
				if dlg.ShowModal() == wx.ID_OK: 
					function_call[size]=str(dlg.GetValue())
					pickle.dump(function_call,open( "function_dict.p", "wb"))
					self.text.SetValue("updated:"+dlg.GetValue()) 
				dlg.Destroy() 

# main
examples_dir = os.getcwd()
pipe_filename = os.path.join( examples_dir, "pipe.obj" )
hole_filename = os.path.join( examples_dir, "hole.obj" )
ring_name=os.path.join( examples_dir, "ring.obj" )

remote = mmRemote()
remote.connect()

obj_list = mm.list_selected_objects(remote)

function_call=dict()              
ex = wx.App() 
dis_size=wx.GetDisplaySize()  
Mywin(None,'Blowhole Editor') 
ex.MainLoop()