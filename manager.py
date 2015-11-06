from multiprocessing import Pool
from time import sleep, time
from os import remove
from os.path import getsize as GetFileSize

from worker import Worker
from functions import ParseURL, FormatByte

cacheName="pending_urls.cache"
cacheThreshold=500000

def Boss(queueRd, queueWr, processCount=5, taskSize=30, tasksPerChild=20):
	pendingUrls=[]
	queuedTasks=[]
	foundUrls={}
	pool=Pool(processes=processCount, maxtasksperchild=tasksPerChild)

	useTOR=False
	cachedPending=False
	while True:

		cmd=CheckQueue(queueRd, pendingUrls)
		if cmd=="STOP":
			try:
				remove(cacheName)
			except:
				pass
			pool.terminate()
			return 0
		elif cmd=="TOR":
			useTOR=not useTOR
		elif cmd=="INFO":
			if cachedPending==False:
				cacheSize=0
			else:
				try:
					cacheSize=GetFileSize(cacheName)
				except:
					cacheSize=0
			queueWr.put([len(queuedTasks), len(pendingUrls), cacheSize])
		elif "DUMP" in cmd:
			DumpURLs(foundUrls, cmd[5:])

		if len(pendingUrls)>cacheThreshold:
			if cachedPending==True:
				mode="a"
			else:
				mode="w"
			CachePendingURLs(pendingUrls, cacheName, mode)
			pendingUrls=[]
			cachedPending=True
			

		if len(queuedTasks)<processCount**2:
			if cachedPending==True:
				pendingUrls+=ReadPendingCache(cacheName)
				cachedPending=False
			preparedTasks=CreateTasks(pendingUrls, taskSize)
			while preparedTasks:
				queuedTasks.append(pool.apply_async(Worker, (preparedTasks.pop(0), useTOR,)))
			pendingUrls=[]

		i=0
		while queuedTasks:
			if i>=len(queuedTasks):
				break
			if queuedTasks[i].ready():
				r=queuedTasks.pop(i)
			else:
				i+=1
				continue
			try:
				urls, worktime, bytesRead, errors, httpCodes, usedTOR=r.get()
			except Exception as ex:
				queueWr.put(ex)
				continue

			newUrls=AddURLs(foundUrls, urls)
			pendingUrls+=newUrls
			queueWr.put([worktime, bytesRead, errors, httpCodes, usedTOR, len(newUrls)])

		sleep(1)

def CheckQueue(queue, pendingUrls):
	while not queue.empty():
		cmd=queue.get()
		if cmd[0]=="!":
			return cmd[1:]
		else:
			pendingUrls.append(cmd)
	return "PROCEED"

def CreateTasks(pendingUrls, taskSize=30):
	taskDict={}
	while pendingUrls:
		t=pendingUrls.pop()
		if t[0] in taskDict:
			taskDict[t[0]].append(t[1])
		else:
			taskDict[t[0]]=[t[1]]
	tasks=[]

	while len(taskDict)>0:
		currSize=0
		task=[]
		while currSize<taskSize and len(taskDict)>0:
			domain, paths=taskDict.popitem()
			task.append((domain, paths))
			currSize+=len(paths)
		tasks.append(task)
	return tasks
	
def AddURLs(foundUrls, urls):
	newUrls=[]
	for host, path in urls:
		if host[:4]=="www.":
			host=host[4:]

		if host in foundUrls:
			if not path in foundUrls[host]:
				foundUrls[host].append(path)
				newUrls.append([host, path])
		else:
			foundUrls.update({host:[path]})
			newUrls.append([host, path])
	return newUrls
	
def DumpURLs(foundUrls, filename):
	f=open(filename, "w")
	for host in foundUrls:
		for path in foundUrls[host]:
			f.write("%s%s\n" % (host, path))
	f.close()

def CachePendingURLs(pendingUrls, filename, mode):
	f=open(filename, mode)
	for host, path in pendingUrls:
		f.write(host+" "+path+"\n")
	f.close()

def ReadPendingCache(filename):
	f=open(filename, "r")
	cache=[]
	line=f.readline()
	while len(line)>1:
		cache.append(tuple(line.split(" ")))
		line=f.readline()
	f.close()
	remove(filename)
	return cache
