from time import sleep
import os

from crawler import Crawler
import functions

if __name__=="__main__":
	c=Crawler()
	c.Start(3)
	#c.ToggleTOR()
	#c.EnableTasksToFile("tasks.txt")

	c.AddURLs(["//orf.at"])

	i=0
	while True:
		c.Update()
		c.Print()
		sleep(1)
		os.system("cls")
		i+=1
		if i>10:
			break
		#if (i%60)==0:
		#c.DumpURLs("dump.txt")

	c.Join("lolo.save")
