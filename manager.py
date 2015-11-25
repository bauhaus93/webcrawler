from multiprocessing import Pool
from time import sleep, time
from os import remove
from os.path import getsize as GetFileSize

from worker import Worker
from functions import ParseURL, FormatByte

def Main(queueRd, queueWr, processCount=5, taskSize=30, tasksPerChild=20):
	m=Manager(queueRd, queueWr, processCount, taskSize, tasksPerChild)

	while not m.Quit():
		m.Loop()
		sleep(1)

class Cache:

	def __init__(self, path="pending_urls.cache"):
		self.path=path

	def __del__(self):
		try:
			remove(self.path)
		except:
			pass

	def GetSize(self):
		try:
			size=GetFileSize(self.path)
		except:
			size=0
		return size

	def Put(self, urls):
		f=open(self.path, "a")
		for host, path in urls:
			f.write(host+" "+path+"\n")
		f.close()

	def Get(self):
		try:
			f=open(self.path, "r")
		except:
			return []
		cache=[]
		line=f.readline()
		while len(line)>1:
			cache.append(tuple(line[:-1].split(" "))) # -1 cuz \n
			line=f.readline()
		f.close()
		remove(self.path)
		cache.sort()
		return cache

class Manager:

	def __init__(self, queueRd, queueWr, processCount=5, taskSize=30, tasksPerChild=20):
		self.queueRd=queueRd
		self.queueWr=queueWr
		self.processCount=processCount
		self.taskSize=taskSize
		self.tasksPerChild=tasksPerChild

		self.pendingUrls=[]
		self.queuedTasks=[]
		self.foundUrls={}
		self.pool=Pool(processes=processCount, maxtasksperchild=tasksPerChild)

		self.useTOR=False
		self.cachePending=Cache()
		self.cacheThreshold=500000

		self.quit=False
		self.finish=False
		

	def Loop(self):
		self.ReadMsgQueue()
		self.HandleCaching()
		self.HandleTaskQueueSize()
		self.HandleTaskQueue()

	def Shutdown(self):
		del self.cachePending
		self.pool.terminate()
		self.quit=True

	def Quit(self):
		return self.quit

	def ReadMsgQueue(self):
		while not self.queueRd.empty():
			cmd=self.queueRd.get()
			if cmd[0]!="!":
				self.pendingUrls.append(cmd)
				self.pendingUrls.sort()
			else:
				cmd=cmd[1:]
				if cmd=="STOP":
					self.Shutdown()
				elif cmd=="FINISH":
					self.finish=True
				elif cmd=="TOR":
					self.ToggleTOR()
				elif cmd=="INFO":
					self.PutInfo()
				elif "SAVE" in cmd:
					self.Save(cmd[5:])
				elif "LOAD" in cmd:
					self.Load(cmd[5:])
				elif "DUMP" in cmd:
					self.DumpURLs(cmd[5:])

	def PutInfo(self):
		self.queueWr.put([len(self.queuedTasks), len(self.pendingUrls), self.cachePending.GetSize()])

	def ToggleTOR(self):
		self.useTOR=not self.useTOR

	def DumpURLs(self, filename):
		f=open(filename, "w")
		for host in self.foundUrls:
			for path in self.foundUrls[host]:
				f.write("%s%s\n" % (host, path))
		f.close()
		
	def HandleCaching(self):
		if len(self.pendingUrls)>self.cacheThreshold:
			self.cachePending.Put(self.pendingUrls)
			self.pendingUrls=[]

	def HandleTaskQueueSize(self):
		if self.finish:
			return
		if len(self.queuedTasks)<self.processCount:
			takeCount=2*self.processCount*self.taskSize
			
			if len(self.pendingUrls)<takeCount:
				self.pendingUrls.extend(self.cachePending.Get())
				
			takeCount=min(takeCount, len(self.pendingUrls))
			preparedTasks=self.CreateTasks(takeCount)
			
			while preparedTasks:
				self.queuedTasks.append(self.pool.apply_async(Worker, (preparedTasks.pop(0), self.useTOR,)))

	def HandleTaskQueue(self):
		i=0
		while self.queuedTasks:
			if i>=len(self.queuedTasks):
				break
				
			if self.queuedTasks[i].ready():
				r=self.queuedTasks.pop(i)
			else:
				i+=1
				continue
				
			try:
				urls, worktime, bytesRead, errors, httpCodes, usedTOR=r.get()
			except Exception as ex:
				self.queueWr.put(ex)
				continue

			newCount=self.AddFoundURLs(urls)
			self.queueWr.put([worktime, bytesRead, httpCodes, errors, newCount, usedTOR])

	def CreateTasks(self, takeCount):
		taskDict={}
		count=0
		while count < takeCount and self.pendingUrls:
			t=self.pendingUrls.pop()
			if t[0] in taskDict:
				taskDict[t[0]].append(t[1])
			else:
				taskDict[t[0]]=[t[1]]
			count+=1
		tasks=[]

		while len(taskDict)>0:
			currSize=0
			task=[]
			while currSize<self.taskSize and len(taskDict)>0:
				domain, paths=taskDict.popitem()
				task.append((domain, paths))
				currSize+=len(paths)
			tasks.append(task)
		return tasks

	def AddFoundURLs(self, urls):
		newCount=0
		for host, path in urls:
			if host[:4]=="www.":
				host=host[4:]

			if host in self.foundUrls:
				if not path in self.foundUrls[host]:
					self.foundUrls[host].append(path)
					self.pendingUrls.append([host, path])
					newCount+=1
			else:
				self.foundUrls.update({host:[path]})
				self.pendingUrls.append([host, path])
				newCount+=1
		return newCount

	def Save(self, path):
		f=open(path, "a")
		self.pendingUrls.extend(self.cachePending.Get())
		f.write("PENDING_URLS\n")
		for url in self.pendingUrls:
			f.write(url[0]+" "+url[1]+"\n")
		f.write("FOUND_URLS\n")
		for host in self.foundUrls:
			for path in self.foundUrls[host]:
				f.write(host+" "+path+"\n")

	def Load(self, path):
		with open(path, "r") as f:
			state=0
			for line in f:
				line=line[:-1]
				if state==0 and line=="PENDING_URLS":
					state=1
					continue
				elif state==1 and line=="FOUND_URLS":
					state=2
					continue

				if state==1:
					self.pendingUrls.append(tuple(line.split(" ")))
				elif state==2:
					self.AddFoundURLs([tuple(line.split(" "))])
		

