import wx
import wx.grid

import functions

class GridTasks(wx.grid.Grid):

	def __init__(self, parent, fields):
		wx.grid.Grid.__init__(self, parent)
		
		self.CreateGrid(0, len(fields))
		self.EnableEditing(False)

		for i in range(len(fields)):
			self.SetColLabelValue(i, fields[i])
		self.AutoSize()
		#self.Fit()
		

	def AddTasks(self, tasks):
		oldRows=self.GetNumberRows()
		tLen=len(tasks)
		if tLen-oldRows>0:
			self.AppendRows(tLen-oldRows)
			for i in range(oldRows, tLen):
				self.AddTask(i, tasks[i])
		
		
	def AddTask(self, row, task):
		fields=task.GetFieldValues()
		for i in range(len(fields)):
			self.SetCellValue(row, i, fields[i])

class GridInfo(wx.grid.Grid):

	def __init__(self, parent, fields):
		wx.grid.Grid.__init__(self, parent)
	
		self.CreateGrid(len(fields), 2)
		self.EnableEditing(False)

		self.SetRowLabelSize(0)
		self.SetColLabelValue(0, "Info")
		self.SetColLabelValue(1, "Value")
		

		for i in range(len(fields)):
			self.SetCellValue(i, 0, fields[i])

		self.AutoSize()
		#self.Fit()

	def Update(self, fields):
		for i in range(len(fields)):
			self.SetCellValue(i, 1, fields[i])
		self.AutoSizeColumns()
