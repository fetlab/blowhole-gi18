import wx 
import pickle
 
function_call=dict()
class Mywin(wx.Frame): 
            
   def __init__(self, parent, title): 
      super(Mywin, self).__init__(parent, title = title,size = (300,200))  
         
      self.InitUI() 
         
   def InitUI(self):
      print(dis_size)
      self.count = 0 
      pnl = wx.Panel(self)
      self.SetWindowStyle(wx.STAY_ON_TOP)
      vbox = wx.BoxSizer(wx.VERTICAL) 
		
      hbox1 = wx.BoxSizer(wx.HORIZONTAL) 
      hbox2 = wx.BoxSizer(wx.HORIZONTAL) 
		
      self.text = wx.TextCtrl(pnl, size = (250, 25),style = wx.TE_READONLY) 
      self.btn1 = wx.Button(pnl, label = "Enter Text") 
      self.Bind(wx.EVT_BUTTON, self.OnClick, self.btn1) 
		
      hbox1.Add(self.text, proportion = 1, flag = wx.ALIGN_CENTRE) 
      hbox2.Add(self.btn1, proportion = 1, flag = wx.RIGHT, border = 10)
		
      vbox.Add((0, 30)) 
      vbox.Add(hbox1, flag = wx.ALIGN_CENTRE) 
      vbox.Add((0, 20)) 
      vbox.Add(hbox2, proportion = 1, flag = wx.ALIGN_CENTRE) 
		
      pnl.SetSizer(vbox) 
      #self.Centre()
      self.Move((dis_size[0]-300,100)) 
      self.Show(True)
		
   def OnClick(self, e): 
      dlg = wx.TextEntryDialog(self,'Enter Your Name', 'Text Entry Dialog','',wx.ICON_QUESTION | wx.OK | wx.CANCEL,(dis_size[0]-300,400))
      if dlg.ShowModal() == wx.ID_OK: 
         print(dlg.GetValue())
         function_call[1]=str(dlg.GetValue())
         pickle.dump( function_call, open( "test.p", "wb" ) )
         self.text.SetValue("Name entered:"+dlg.GetValue()) 
      dlg.Destroy() 
                                 
ex = wx.App() 
dis_size=wx.GetDisplaySize() 
Mywin(None,'TextEntry Demo') 
ex.MainLoop()