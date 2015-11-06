import wx

from crawler import Crawler
from taskdata import TaskData
from ui_grid import GridTasks, GridInfo

class CrawlerFrame(wx.Frame):

	def __init__(self, parent):
		wx.Frame.__init__(self, parent, title="webcrawler", size=(850, 600))
		
		self.statusbar=self.CreateStatusBar()

		self.gridInfo=GridInfo(self, Crawler.GetInfoNames())
		self.gridTasks=GridTasks(self, TaskData.GetFieldNames())

		self.inputStatic=wx.StaticText(self, label="Command", style=wx.ALIGN_CENTRE_HORIZONTAL)
		self.textInput=wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
		self.textInput.Bind(wx.EVT_TEXT_ENTER, self.CmdEnter)

		self.sizerHoriz=wx.BoxSizer(wx.HORIZONTAL)
		self.sizerHoriz.Add(self.gridInfo, 1, wx.EXPAND|wx.ALL)
		self.sizerHoriz.Add(self.gridTasks, 1, wx.EXPAND|wx.ALL)

		self.sizerVert=wx.BoxSizer(wx.VERTICAL)
		self.sizerVert.Add(self.sizerHoriz, 5)
		
		sH=wx.BoxSizer(wx.HORIZONTAL)
		sH.Add(self.inputStatic, flag=wx.ALL, border=5)
		sH.Add(self.textInput, 1, flag=wx.ALL | wx.ALIGN_LEFT, border=3)
		self.sizerVert.Add(sH, 0, wx.EXPAND)

		self.SetAutoLayout(True)
		self.SetSizer(self.sizerVert)
		self.Layout()
		self.Show(True)
		
		self.StartCrawler()


	def StartCrawler(self):
		self.crawler=Crawler()
		self.crawler.Start(5)
		self.crawler.AddURLs(["//www.orf.at"])
		self.timer=wx.Timer(self, 666)
		self.Bind(wx.EVT_TIMER, self.OnTimer)
		self.Bind(wx.EVT_CLOSE, self.StopCrawler)
		self.timer.Start(1000)
		self.statusbar.SetStatusText("Active")

	def StopCrawler(self, event):
		self.crawler.Stop()
		self.Destroy()

	def OnTimer(self, event):
		evtId=event.GetId()
		if evtId==666:
			self.crawler.Update()
			self.gridInfo.Update(self.crawler.GetInfoValues())
			self.gridTasks.AddTasks(self.crawler.GetTasks())

	def CmdEnter(self, event):
		cmd=self.textInput.GetValue()

		if cmd=="exit":
			self.StopCrawler(event)
		elif cmd=="tor":
			self.crawler.ToggleTOR()

		self.textInput.Clear()


if __name__=="__main__":
	app=wx.App(False)
	f=CrawlerFrame(None)
	f.Show(True)
	app.MainLoop()
