from time import sleep
import os

from crawler import Crawler
import functions

if __name__=="__main__":
	c=Crawler()
	c.Start()
	#c.UseTOR()
	#c.EnableTasksToFile("tasks.txt")

	c.AddURLs(["//orf.at"])

	i=0
	while True:
		c.Update()
		c.Print()
		sleep(1)
		os.system("cls")
		#i+=1
		#if (i%60)==0:
		#	c.DumpURLs("dump.txt")

	c.Stop()
