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

	def Start(self, processCount=5):
		self.bossQueueWr=Queue()
		self.bossQueueRd=Queue()
		self.boss=Process(target=manager.Boss, args=(self.bossQueueWr, self.bossQueueRd))
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

	def Stop(self):
		self.bossQueueWr.put("!STOP")

	def UseTOR(self):
		if not self.useTOR:
			s=socket(AF_INET, SOCK_STREAM)
			try:
				s.connect(("127.0.0.1", 9050))
				s.close()
			except:
				return
			self.useTOR=True
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
		while not self.bossQueueRd.empty():
			msg=self.bossQueueRd.get()
			if isinstance(msg, list):
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

	@staticmethod
	def GetInfoNames():
		return ("TOR used",
				"time active",
				"total worktime",
				"tasks finished",
				"byte read",
				"urls found",
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
		info["time active"]=FormatTime(time()-self.startTime)
		info["total worktime"]=FormatTime(self.totalWork)
		info["tasks finished"]=str(len(self.taskData))
		info["byte read"]=FormatByte(self.totalRead)
		info["urls found"]=str(self.urlsFound)
		for i in range(5):
			info["http %dxx" % (i+1)]=str(self.httpCode[i])
		info["errors"]=str(self.errors)
		info["task exceptions"]=str(self.taskExceptions)
		info["TOR used"]=str(self.useTOR)
		return info

