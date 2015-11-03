from multiprocessing import Pool, TimeoutError
from multiprocessing.managers import BaseManager
from time import sleep, time

from worker import Worker
from functions import ParseURL, FormatByte

class ManagerExt(BaseManager):
	pass

class URLCache:

	def __init__(self):
		self.urls={}
		self.count=0

	def AddURL(self, host, path):
		urls=self.urls
		if host[:4]=="www.":
			host=host[4:]
                        
		if host in self.urls:
			if not path in self.urls[host]:
				urls[host].append(path)
				self.count+=1
				self.urls=urls
				return True
		else:
			urls[host]=[path]
			self.count+=1
			self.urls=urls
			return True
		return False
	
	def GetSize(self):
		return self.count
		
	def GetSitesPerHost(self):
		l=[]
		for host in self.urls:
			l.append((host, len(self.urls[host])))
		l.sort(cmp=lambda a, b: b[1]-a[1])
		return l

class Master:

	def __init__(self, urlCache, processCount=5, taskSize=30, tasksPerChild=20):
		self.processCount=processCount
		self.taskSize=taskSize
		self.pendingTasks=[]
		self.preparedTasks=[]
		self.foundUrls=urlCache
		self.pool=Pool(processes=processCount, maxtasksperchild=tasksPerChild)
		self.fileOut="url_%d.txt" % int(time())
		self.stop=False
		self.active=False
		
		self.tasksDone=0
		self.bytesRead=0
		self.activeTasks=0
		self.httpCodes=[0, 0, 0, 0, 0]
		self.errors=0
		self.invalidMeta=0
		self.worktime=0
		self.taskTimeouts=0
		self.bytesReadLastMinute=[]
		self.finishedTasks=[]
		
	def Loop(self):
		self.active=True
		self.startTime=time()
		while not self.ShouldStop():

			if not self.pendingTasks:
				sleep(1)
				continue

			self.PrepareTasks()
			results=[]
			for t in self.preparedTasks:
				results.append(self.pool.apply_async(Worker, (t,)))

			while results:
				self.activeTasks=len(results)
				if self.ShouldStop():
					break
				r=results.pop(0)
				try:
					urls, worktime, bytesRead, errors, invalidMeta, httpCodes=r.get(timeout=60)
					self.tasksDone+=1
					self.bytesRead+=bytesRead
					self.bytesReadLastMinute=self.bytesReadLastMinute+[(bytesRead, time())]
					self.httpCodes=map(lambda a, b: a+b, self.httpCodes, httpCodes)
					self.errors+=errors
					self.invalidMeta+=invalidMeta
					self.worktime+=worktime
					f=self.finishedTasks
					f.append((worktime, bytesRead, len(urls)))
					self.finishedTasks=f
				except TimeoutError:
					self.taskTimeouts+=1
					print "task timed out (+60s)"
					continue
				except Exception as ex:
					print "exception:", ex
					continue
				self.AddURLs(urls)

				if self.activeTasks<=self.processCount**2:
					self.PrepareTasks()
					for t in self.preparedTasks:
						results.append(self.pool.apply_async(Worker, (t,)))
		#self.pool.terminate()
		self.active=False

	def PrepareTasks(self):
		taskDict={}
		while self.pendingTasks:
			t=self.pendingTasks.pop()
			if t[0] in taskDict:
				taskDict[t[0]].append(t[1])
			else:
				taskDict[t[0]]=[t[1]]
		tasks=[]
		while len(taskDict)>0:
			taskSize=0
			task=[]
			while taskSize<self.taskSize and len(taskDict)>0:
				domain, paths=taskDict.popitem()
				task.append((domain, paths))
				taskSize+=len(paths)
			tasks.append(task)
		self.pendingTasks=[]
		self.preparedTasks=tasks
	
	def AddURLs(self, urls):
		f=open(self.fileOut, "a+")
		p=self.pendingTasks
		for host, path in urls:
			if self.foundUrls.AddURL(host, path):
				p.append((host, path))
				f.write(host+path+"\n")
		self.pendingTasks=p
		f.close()

	def ShouldStop(self):
		return self.stop

	def Stop(self):
		self.stop=True
		
	def Active(self):
		return self.active

	def FinishedTask(self):
		return len(self.finishedTasks)!=0

	def PopFinishedTask(self):
		if self.finishedTasks:
			t=self.finishedTasks[0]
			self.finishedTasks=self.finishedTasks[1:]
			return t
		return None
		
	def HandleBytesReadLastMinute(self):
		t=time()
		#print "#####################"
		#for bytes, ts in self.bytesReadLastMinute:
		#	print "%10s %.2f" % (FormatByte(bytes), t-ts)
		while self.bytesReadLastMinute:
			if t-self.bytesReadLastMinute[0][1]>60:
				self.bytesReadLastMinute=self.bytesReadLastMinute[1:]
			else:
				break
		
	def GetInfo(self):
		self.HandleBytesReadLastMinute()

		info={}
		info["active workers"]=self.processCount
		info["tasks done"]=self.tasksDone
		info["unique urls found"]=self.foundUrls.GetSize()
		info["bytes read"]=self.bytesRead
		info["active tasks"]=self.activeTasks
		info["pending urls"]=len(self.pendingTasks)
		for i in range(5):
			info["http %dxx" % (i+1)]=self.httpCodes[i]
		info["errors"]=self.errors
		info["invalid data"]=self.invalidMeta
		info["work time"]=self.worktime
		info["active time"]=time()-self.startTime
		info["processing speed"]=(self.bytesRead/(time()-self.startTime))
		if len(self.bytesReadLastMinute)!=0:
			bytes=0
			for read, ts in self.bytesReadLastMinute:
				bytes+=read
			interval=time()-self.bytesReadLastMinute[0][1]
			if interval==0:
				interval=1
			info["current processing speed"]=bytes/interval
		else:
			info["current processing speed"]=0
		return info
		
	def GetSitesPerHost(self):
		return self.foundUrls.GetSitesPerHost()

ManagerExt.register("Master", Master)
ManagerExt.register("URLCache", URLCache)
