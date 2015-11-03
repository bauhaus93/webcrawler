import wx
import wx.grid

import functions

class GridTasks(wx.grid.Grid):

	def __init__(self, parent):
		wx.grid.Grid.__init__(self, parent)
		
		self.CreateGrid(0, 3)
		self.EnableEditing(False)

		self.SetMinSize((355, -1))
		self.SetMaxSize((335, -1))
		self.SetColSize(0, 85)
		self.SetColSize(1, 75)
		self.SetColSize(2, 75)

		self.SetColLabelValue(0, "time")
		self.SetColLabelValue(1, "size")
		self.SetColLabelValue(2, "urls")

		self.filled=False
		
	def AddTask(self, task):
		self.AppendRows(1)
		rows=self.GetNumberRows()
		formats=(functions.FormatTime, functions.FormatByte, lambda t: str(t))
		f=lambda n: formats[n](task[n])
		for i in range(3):
			self.SetCellValue(rows-1, i, f(i))

class GridHostSites(wx.Panel):
	
	def __init__(self, parent, callback):
		wx.Panel.__init__(self, parent)
		
		self.SetMinSize((300, -1))
		self.SetMaxSize((300, -1))
		
		self.grid=wx.grid.Grid(self)
		self.grid.CreateGrid(0, 2)
		self.grid.SetColLabelValue(0, "host")
		self.grid.SetColLabelValue(1, "urls")
		self.grid.EnableEditing(False)
		
		self.buttonFill=wx.Button(self, label="Fill")
		self.buttonFill.SetMinSize((100, 20))
		self.buttonFill.SetMaxSize((100, 20))
		
		self.buttonFlush=wx.Button(self, label="Flush")
		self.buttonFlush.SetMinSize((100, 20))
		self.buttonFlush.SetMaxSize((100, 20))

		self.sizer=wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.grid, 1, wx.EXPAND)
		self.sizer.Add(self.buttonFill, 0, wx.EXPAND)
		self.sizer.Add(self.buttonFlush, 0, wx.EXPAND)
		
		self.Bind(wx.EVT_BUTTON, callback, self.buttonFill)
		self.Bind(wx.EVT_BUTTON, self.Flush, self.buttonFlush)

		self.SetAutoLayout(True)
		self.SetSizer(self.sizer)
		self.Layout()

	def Fill(self, hosts):

		self.grid.ClearGrid()
		rows=self.grid.GetNumberRows()
		if rows>len(hosts):
			self.grid.DeleteRows(numRows=rows-len(hosts))
		else:
			self.grid.AppendRows(len(hosts)-rows)
		row=0
		for host, count in hosts:
			self.grid.SetCellValue(row, 0, host)
			self.grid.SetCellValue(row, 1, str(count))
			row+=1

	def Flush(self, event):
		self.grid.ClearGrid()
		self.grid.DeleteRows(0, self.grid.GetNumberRows())

