from functions import FormatTime, FormatByte

class TaskData:

	def __init__(self, msg):
		self.worktime=msg.pop(0)
		self.byteRead=msg.pop(0)
		self.errors=msg.pop(0)
		self.httpCode=msg.pop(0)
		self.usedTOR=msg.pop(0)
		self.urlsFound=msg.pop(0)
	
	def GetSize(self):
		size=self.errors
		for i in range(5):
			size+=self.httpCode(i)
			
	def GetWorkTime(self):
		return self.worktime
		
	def GetByteRead(self):
		return self.byteRead
	
	def GetErrors(self):
		return self.errors

	def GetHTTP(self):
		return self.httpCode
		
	def UsedTOR(self):
		return self.usedTOR
		
	def GetURLsFound(self):
		return self.urlsFound
		
	def __str__(self):
		out="%8s | %11s | " % (FormatTime(self.worktime), FormatByte(self.byteRead))
		for i in range(5):
			out+="%3d | " % self.httpCode[i]
		out+="%3d | %10d | %8s" % (self.errors, self.urlsFound, self.usedTOR)
		return out
