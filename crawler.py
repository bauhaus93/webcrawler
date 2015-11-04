from multiprocessing import Process, Queue

from time import sleep
from random import randint

from functions import FormatByte, FormatTime, ParseURL
import worker
import manager

class Crawler:

	def __init__(self):
		pass

	def Start(self, processCount=5):
		self.bossQueueWr=Queue()
		self.bossQueueRd=Queue()
		self.boss=Process(target=manager.Boss, args=(self.bossQueueWr, self.bossQueueRd))
		self.boss.start()

	def Stop(self):
		self.bossQueueWr.put("!STOP")

	def AddURLs(self, urls):
		for url in urls:
			self.bossQueueWr.put(ParseURL(url))
			
	def Update(self):
		while self.bossQueueRd:
			print self.bossQueueRd.get()

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




