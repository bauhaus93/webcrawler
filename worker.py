import requests
from time import sleep, time
from io import BufferedReader
import re
import logging

from functions import ParseURL

def Worker(task):
	bytesRead=0
	httpCodes=[0, 0, 0, 0, 0]
	urlList=[]
	start=time()
	errors=0
	invalidMeta=0
	tooBig=0
	#logging.basicConfig(level=logging.INFO)
	
	session=requests.Session()

	for t in task:
		urls=[]
		host=t[0]
		for path in t[1]:
			url="http://"+host+path
			try:
				r=session.get(url, timeout=3.0, stream=True, allow_redirects=True)
			except:
				errors+=1
				break

			httpCodes[(r.status_code/100)-1]+=1
			if r.status_code!=200:
				continue
			if "Content-Type" in r.headers:
				if not "text" in r.headers["Content-Type"]:
					invalidMeta+1
					continue
			else:
				invalidMeta+=1
				continue
			if "Content-Length" in r.headers:
				if int(r.headers["Content-Length"])>10*1024*1024:
					invalidMeta+=1
					continue
			else:
				invalidMeta+=1
				continue
			try:
				size, urls=ReadResponse(r , t[0])
			except:
				continue
			bytesRead+=size
			urlList.extend(urls)

	return urlList, time()-start, bytesRead, errors, invalidMeta, httpCodes

def ReadResponse(response, domain):
	size=0
	urls=[]
	for chunk in response.iter_content(chunk_size=512*1024):
		if not chunk:
			continue
		for m in re.findall("href=\"[a-z0-9.:/]+\"", chunk, re.IGNORECASE):
			d, path=ParseURL(m[6:-1])
			if d==None:
				d=domain
			if len(path)>0:
				if path[0]!="/":
					path="/"+path
			else:
				path="/"
			urls.append((d, path))
		size+=len(chunk)
	return size, urls
