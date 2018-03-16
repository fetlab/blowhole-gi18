"""
FETLab
"""

import wx #library used for GUI Stuff

statusText = None#This is a global for the textbox for the model

def scriptButton(theEvent):
	""" Called when our "Blow Hole" button is pressed """
	setStatusText("Blowing Holes in Model")


def addModel(event):
	""" Function that is called when "Add Model" is pressed """
	setStatusText("Adding model")

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
	addButton = wx.Button(window,id=2, label="Add Model", pos=(8, 10), size=(200, 20))
	window.Bind(wx.EVT_BUTTON, addModel, addButton)

	#Creates button, adds it to the window and binds the function to the button
	runButton = wx.Button(window,id=-1, label="Blow Holes!", pos=(8, 35), size=(200, 20))
	window.Bind(wx.EVT_BUTTON, scriptButton, runButton)

	#Creates the status text bar
	global statusText
	statusText = wx.StaticText(window,-1, "[initial Text goes here]", pos=(8, 80), size=(384, 20))

	window.SetTitle("[Title here]")#Sets the title of the window
	window.Centre()#Centers it in the middle of the screen
	window.Show(True)#Should be true or the window won't show up
	app.MainLoop()#


createGUI()