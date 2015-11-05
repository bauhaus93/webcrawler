from urlparse import urlparse

def ParseURL(url):
	p=urlparse(url)
	return p.hostname, p.path
	
def FormatByte(byte):
    letters=[(0x400, "ki"), (0x100000, "Mi"), (0x40000000, "Gi")]
    for pair in reversed(letters):
        if byte>=pair[0]:
            return "%.2f %sB" % (float(byte)/pair[0], pair[1])
    return "%d B" % byte
    
def FormatByteSpeed(byte):
	return FormatByte(byte)+"/s"

def FormatTime(time):

	if time<60:
		return "%.2fs" % time
	if time<60*60:
		return "%dm %ds" % (time/60, time%60)
	h=time/3600
	m=(time%3600)/60
	#not correct: seconds (seem to be minutes)
	s=m%60
	return "%dh %dm %ds" % (h, m ,s)
