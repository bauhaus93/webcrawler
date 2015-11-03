import wx

class Progress(wx.Panel):

	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		self.bar=wx.Gauge(self, wx.ID_ANY, range=100)
		self.bar.Pulse()

		self.text=wx.StaticText(self, style=wx.ALIGN_RIGHT)
		self.text.SetLabel("0/0")
		
		self.sizer=wx.BoxSizer(wx.HORIZONTAL)
		self.sizer.Add(self.text, 1, wx.EXPAND | wx.RIGHT, 10)
		self.sizer.Add(self.bar, 6, wx.EXPAND)
		
		self.SetAutoLayout(True)
		self.SetSizer(self.sizer)
		self.Layout()

	def Update(self, info):
		curr=int(info["cycle tasks done"])
		max=int(info["cycle tasks total"])
		self.bar.SetValue(curr)
		self.bar.SetRange(max)
		self.text.SetLabel("%d/%d" % (curr, max))
		self.Layout()
