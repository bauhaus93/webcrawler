from multiprocessing import Process, Queue
from socket import socket, AF_INET, SOCK_STREAM

from time import sleep, time

from functions import FormatByte, FormatTime, ParseURL
from taskdata import TaskData
import worker
import manager

class Crawler:

	def __init__(self):
		self.Init()

	def Start(self, processCount=10):
		self.bossQueueWr=Queue()
		self.bossQueueRd=Queue()
		self.boss=Process(target=manager.Main, args=(self.bossQueueWr, self.bossQueueRd))
		self.boss.start()
		self.processCount=processCount
		self.startTime=time()

	def Init(self):
		self.useTOR=False
		self.totalWork=0
		self.totalRead=0
		self.errors=0
		self.httpCode=[0]*5
		self.taskExceptions=0
		self.urlsFound=0
		self.tasksToFile=False
		self.taskData=[]
		self.queuedTasks=0
		self.pendingUrls=0
		self.cacheSize=0
		self.timeOffset=0

	def Stop(self):
		self.bossQueueWr.put("!STOP")

	def Finish(self):
		self.bossQueueWr.put("!FINISH")

	def Save(self, filename):
		f=open(filename, "w")
		f.write("GENERAL_DATA\n")
		f.write(str(self.useTOR)+"\n")
		f.write(str(self.timeOffset+time()-self.startTime)+"\n")
		f.write(str(self.taskExceptions)+"\n")
		f.write("TASK_DATA\n")
		for task in self.taskData:
			task.Save(f)
		f.close()
		self.bossQueueWr.put("!SAVE "+filename)

	def Load(self, filename):
		self.Init()
		
		f=open(filename, "r")
		
		if f.readline()[:-1]!="GENERAL_DATA":
			print "Format Error"
		if f.readline()[:-1]=="True":
			self.useTOR=True
		self.timeOffset=float(f.readline())
		self.taskExceptions=int(f.readline())
		if f.readline()[:-1]!="TASK_DATA":
			print "Format Error"
		for line in f.readline():
			line=line[:-1]
			
			

		f.close()
		self.bossQueueWr.put("!LOAD "+filename)

	def Join(self, savefile=None):
		self.Finish()
		while self.HasQueuedTasks():
			sleep(1)
		if savefile:
			self.Save(savefile)
		self.Stop()

	def ToggleTOR(self):
		self.useTOR=not self.useTOR
		if self.useTOR:
			s=socket(AF_INET, SOCK_STREAM)
			try:
				s.connect(("127.0.0.1", 9050))
				s.close()
			except:
				self.useTOR=False
				return
		self.bossQueueWr.put("!TOR")
		
	def DumpURLs(self, filename):
		self.bossQueueWr.put("!DUMP %s" % filename)
	
	def EnableTasksToFile(self, filename):
		self.tasksToFile=True
		self.filename=filename
		f=open(self.filename, "w")
		f.write("worktime |")
		f.write("   byte read |")
		for i in range(1, 6):
			f.write(" %d00 |" % i)
		f.write(" err |")
		f.write(" urls found |")
		f.write(" TOR used")
		f.write("\n"+"-"*82)
		f.close()

	def AddURLs(self, urls):
		for url in urls:
			self.bossQueueWr.put(ParseURL(url))
			
	def Update(self):
		if self.tasksToFile:
			f=open(self.filename, "a")
		self.bossQueueWr.put("!INFO")
		while not self.bossQueueRd.empty():
			msg=self.bossQueueRd.get()
			if isinstance(msg, list):
				if len(msg)==3:
					self.queuedTasks=msg.pop(0)
					self.pendingUrls=msg.pop(0)
					self.cacheSize=msg.pop(0)
				else:
					task=TaskData(msg)
					self.totalWork+=task.GetWorkTime()
					self.totalRead+=task.GetByteRead()
					self.errors+=task.GetErrors()
					http=task.GetHTTP()
					self.httpCode=map(lambda a, b: a+b, self.httpCode, http)
					self.urlsFound+=task.GetURLsFound()
					self.taskData.append(task)
					if self.tasksToFile:
						f.write("\n"+str(task))
			elif isinstance(msg, Exception):
				self.taskExceptions+=1
		if self.tasksToFile:
			f.close()

	def GetTasks(self):
		return self.taskData

	def HasQueuedTasks(self):
		self.Update()
		print self.queuedTasks
		return self.queuedTasks!=0



	@staticmethod
	def GetInfoNames():
		return ("TOR used",
				"workers",
				"time active",
				"total worktime",
				"tasks finished",
				"queued tasks",
				"byte read",
				"urls found",
				"pending urls",
				"cache size", 
				"http 1xx",
				"http 2xx",
				"http 3xx",
				"http 4xx",
				"http 5xx",
				"errors",
				"task exceptions")

	def GetInfoValues(self):
		info=[]
		data=self.GetInfo()
		for name in Crawler.GetInfoNames():
			info.append(data[name])
		return info
	
	def Print(self):
		items=Crawler.GetInfoNames()
		maxLen=reduce(lambda a, b: max(a, b), map(lambda s: len(s), items))
		maxLen+=2
		info=self.GetInfo()
		for i in items:
			out=i+":"
			out+=" "*(maxLen-len(i))
			out+=info[i]
			print out

	def GetInfo(self):
		info={}
		info["time active"]=FormatTime(self.timeOffset+time()-self.startTime)
		info["total worktime"]=FormatTime(self.totalWork)
		info["tasks finished"]=str(len(self.taskData))
		info["byte read"]=FormatByte(self.totalRead)
		info["urls found"]=str(self.urlsFound)
		for i in range(5):
			info["http %dxx" % (i+1)]=str(self.httpCode[i])
		info["errors"]=str(self.errors)
		info["task exceptions"]=str(self.taskExceptions)
		info["TOR used"]=str(self.useTOR)
		info["queued tasks"]=str(self.queuedTasks)
		info["pending urls"]=str(self.pendingUrls)
		info["workers"]=str(self.processCount)
		if self.cacheSize==0:
			info["cache size"]="inactive"
		else:
			info["cache size"]=FormatByte(self.cacheSize)
		return info

