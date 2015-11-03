import curses
from time import sleep

from crawler import Crawler
import functions

infoItems=[	("active time", functions.FormatTime),
			("active workers", None),
		 	("active tasks", None),
			("tasks done", None),
			("pending urls", None),
			("unique urls found", None),
			("bytes read", functions.FormatByte),
			("processing speed", functions.FormatByteSpeed),
			("current processing speed", functions.FormatByteSpeed),
			("work time", functions.FormatTime),
			("errors", None),
			("invalid data", None),
			("http 1xx", None),
			("http 2xx", None),
			("http 3xx", None),
			("http 4xx", None),
			("http 5xx",None)]



if __name__=="__main__":
	c=Crawler()
	c.Start()



	c.Stop()
	while c.Active():
		sleep(1)
