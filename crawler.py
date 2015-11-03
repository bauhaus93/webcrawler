from multiprocessing import Process

from time import sleep
from random import randint

from functions import FormatByte, FormatTime, ParseURL
import worker
import manager

class Crawler:

	def __init__(self):
		pass

	def Start(self, processCount=5):
		self.manager=manager.ManagerExt()
		self.manager.start()
		self.urlCache=self.manager.URLCache()
		self.master=self.manager.Master(self.urlCache, processCount)


		self.procMaster=Process(target=self.master.Loop)
		self.procMaster.start()


	def Stop(self):
		#self.procMaster.terminate()
		self.master.Stop()

	def Active(self):
		return self.master.Active()
		
	def AddURLs(self, urls):
		urlTup=[]
		for url in urls:
			urlTup.append(ParseURL(url))
		self.master.AddURLs(urlTup)

	def GetInfo(self):
		return self.master.GetInfo()
		
	def FinishedTask(self):
		return self.master.FinishedTask()
		
	def PopFinishedTask(self):
		return self.master.PopFinishedTask()
		
	def GetSitesPerHost(self):
		return self.master.GetSitesPerHost() 

#if __name__=="__main__":
#	c=Crawler()
#	c.Start()
#	c.AddURLs(["//orf.at"])
#	for i in range(10):
#		info=c.GetInfo()
#		for key in info:
#			print "%s:\t%d" % (key, info[key])
#		print "---------------------"
#		sleep(1)
#	c.Stop()
#	while c.Active():
#		sleep(1)
#	print "stopped!"




