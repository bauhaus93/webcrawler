from time import sleep
import os
import signal

from crawler import Crawler
import functions

quit=False
def SigInt(signal, frame):
	print "QUIT!"
	global quit
	quit=True


if __name__=="__main__":
	c=Crawler("lolo.save")
	c.Start(5)
	c.ToggleTOR()
	c.EnableTasksToFile("tasks.txt")

	c.AddURLs(["//orf.at"])

	i=0
	signal.signal(signal.SIGINT, SigInt)
	while not quit:
		c.Update()
		c.Print()
		sleep(1)
		os.system("cls")
		i+=1
		if i==60:
			c.DumpURLs("dump.txt")
			i=0

	c.Join("lolo.save")
