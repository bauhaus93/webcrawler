from multiprocessing import Process, Queue

from time import sleep, time

from functions import FormatByte, FormatTime, ParseURL
import worker
import manager

class Crawler:

	def __init__(self):
		self.Init()

	def Start(self, processCount=5):
		self.bossQueueWr=Queue()
		self.bossQueueRd=Queue()
		self.boss=Process(target=manager.Boss, args=(self.bossQueueWr, self.bossQueueRd))
		self.boss.start()
		self.processCount=processCount
		self.startTime=time()

	def Init(self):
		self.tasksFinished=0
		self.totalWork=0
		self.totalRead=0
		self.errors=0
		self.httpCode=[0]*5
		self.taskExceptions=0
		self.urlsFound=0

	def Stop(self):
		self.bossQueueWr.put("!STOP")

	def AddURLs(self, urls):
		for url in urls:
			self.bossQueueWr.put(ParseURL(url))
			
	def Update(self):
		while not self.bossQueueRd.empty():
			msg=self.bossQueueRd.get()
			if isinstance(msg, list):
				self.tasksFinished+=1
				self.totalWork+=msg.pop(0)
				self.totalRead+=msg.pop(0)
				self.errors+=msg.pop(0)
				http=msg.pop(0)
				self.httpCode=map(lambda a, b: a+b, self.httpCode, http)
				self.urlsFound+=msg.pop(0)
			elif isinstance(Exception):
				self.taskExceptions+=1
	
	def Print(self):
		print "time active:\t\t%s" % FormatTime(time()-self.startTime)
		print "total worktime:\t\t%s" % FormatTime(self.totalWork)
		print "tasks finished:\t\t%d" % self.tasksFinished
		print "byte read:\t\t%s" % FormatByte(self.totalRead)
		print "urls found:\t\t%d" % self.urlsFound
		for i in range(5):
			print "http %dxx:\t\t%d" % (i+1, self.httpCode[i])
		print "errors:\t\t\t%d" % self.errors
		print "task exceptions:\t%d" % self.taskExceptions

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




