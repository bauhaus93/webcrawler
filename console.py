from time import sleep

from crawler import Crawler
import functions


if __name__=="__main__":
	c=Crawler()
	c.Start()
	c.AddURLs(["//orf.at"])

	while True:
		c.Update()
		sleep(1)
	c.Stop()