from time import sleep
import os

from crawler import Crawler
import functions


if __name__=="__main__":
	c=Crawler()
	c.Start()
	c.UseTOR()
	c.AddURLs(["//orf.at"])

	while True:
		c.Update()
		c.Print()
		sleep(1)
		os.system("cls")

	c.Stop()