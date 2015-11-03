import wx

from crawler import Crawler
from ui_grid import GridTasks, GridHostSites
from ui_progress import Progress
from ui_infopanel import InfoPanel

class CrawlerFrame(wx.Frame):

	def __init__(self, parent):
		wx.Frame.__init__(self, parent, title="webcrawler", size=(1024, 768))
		
		self.statusbar=self.CreateStatusBar()

		self.gridTasks=GridTasks(self)
		self.panelInfo=InfoPanel(self)
		self.gridHostSites=GridHostSites(self, self.FillHostSites)

		self.sizerHoriz=wx.BoxSizer(wx.HORIZONTAL)
		self.sizerHoriz.Add(self.gridTasks, 1, wx.EXPAND)
		self.sizerHoriz.Add(self.panelInfo, 1, wx.EXPAND)
		self.sizerHoriz.Add(self.gridHostSites, 1, wx.EXPAND)

		self.SetAutoLayout(True)
		self.SetSizer(self.sizerHoriz)
		self.Layout()
		self.Show(True)
		
		self.StartCrawler()

	def StartCrawler(self):
		self.crawler=Crawler()
		self.crawler.Start(3)
		self.crawler.AddURLs(["//www.orf.at"])
		self.timer=wx.Timer(self, 666)
		self.Bind(wx.EVT_TIMER, self.OnTimer)
		self.Bind(wx.EVT_CLOSE, self.StopCrawler)
		self.timer.Start(1000)
		self.statusbar.SetStatusText("Active")

	def StopCrawler(self, event):
		#self.timer.Stop()
		self.crawler.Stop()
		self.stopTimer=wx.Timer(self, 667)
		self.stopTimer.Start(1000)
		self.statusbar.SetStatusText("Stopping")

	def OnTimer(self, event):
		evtId=event.GetId()
		if evtId==666:
			info=self.crawler.GetInfo()
			self.panelInfo.Update(info)

			while self.crawler.FinishedTask():
				self.gridTasks.AddTask(self.crawler.PopFinishedTask())
			self.Layout()
		elif evtId==667:
			if not self.crawler.Active():
				self.Destroy()
				
	def FillHostSites(self, event):
		self.gridHostSites.Fill(self.crawler.GetSitesPerHost())



if __name__=="__main__":
	app=wx.App(False)
	f=CrawlerFrame(None)
	f.Show(True)
	app.MainLoop()