import wx

import functions

infoItems=[	("active time", functions.FormatTime),
			("active workers", None),
		 	("active tasks", None),
			("tasks done", None),
			("pending urls", None),
			("unique urls found", None),
			("bytes read", functions.FormatByte),
			("processing speed", functions.FormatByteSpeed),
			("current processing speed", functions.FormatByteSpeed),
			("work time", functions.FormatTime),
			("errors", None),
			("invalid data", None),
			("http 1xx", None),
			("http 2xx", None),
			("http 3xx", None),
			("http 4xx", None),
			("http 5xx",None)]

class InfoPanel(wx.Panel):

	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		self.sizer=wx.GridSizer(rows=len(infoItems), cols=2)
		
		self.text={}
		for key, f in infoItems:
			self.text[key+"_TITLE"]=wx.StaticText(self, label=key+":")
			self.text[key]=wx.StaticText(self)

			self.text[key].SetMaxSize((-1, 20))
			self.text[key+"_TITLE"].SetMaxSize((-1, 20))
			self.sizer.Add(self.text[key+"_TITLE"], 1, wx.EXPAND)
			self.sizer.Add(self.text[key], 1, wx.EXPAND)

		self.sizer.SetVGap(1)

		self.SetAutoLayout(True)
		self.SetSizer(self.sizer)
		self.Layout()
		
	def Update(self, info):
		for key, f in infoItems:
			if f:
				val=f(info[key])
			else:
				val=str(info[key])
			if self.text[key].GetLabel()!=val:
				self.text[key].SetLabel(val)
		self.Layout()
		

