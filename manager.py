from multiprocessing import Pool
from time import sleep, time

from worker import Worker
from functions import ParseURL, FormatByte

def Boss(queueRd, queueWr, processCount=5, taskSize=30, tasksPerChild=20):
	pendingUrls=[]
	queuedTasks=[]
	foundUrls={}
	pool=Pool(processes=processCount, maxtasksperchild=tasksPerChild)

	while True:
		print "queued tasks:", len(queuedTasks)
		print "pending urls:", len(pendingUrls)

		cmd=CheckQueue(queueRd, pendingUrls)
		print cmd
		if cmd=="STOP":
			return 0

		if len(queuedTasks)<processCount**2:
			preparedTasks=CreateTasks(pendingUrls, taskSize)
			while preparedTasks:
				queuedTasks.append(pool.apply_async(Worker, (preparedTasks.pop(0),)))
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
				urls, worktime, bytesRead, errors, invalidMeta, httpCodes=r.get(timeout=60)
				queueWr.put([worktime, bytesRead, errors, invalidMeta, httpCodes])
			except Exception as ex:
				queueWr.put("TaskError: "+str(ex))
				continue

			newUrls=AddURLs(foundUrls, urls)
			pendingUrls+=newUrls

		sleep(1)

def CheckQueue(queue, pendingUrls):
	while not queue.empty():
		cmd=queue.get()
		if cmd[0]=="!":
			cmd=cmd[1:]
			if cmd=="STOP":
				return "STOP"
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
	f=open("fUrls.txt", "a")
	for host, path in urls:
		if host[:4]=="www.":
			host=host[4:]

		if host in foundUrls:
			if not path in foundUrls[host]:
				foundUrls[host].append(path)
				newUrls.append([host, path])
				f.write(host+path+"\n")
		else:
			foundUrls.update({host:[path]})
			newUrls.append([host, path])
			f.write(host+path+"\n")
	f.close()
	return newUrls