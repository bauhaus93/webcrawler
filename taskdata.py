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
			size+=self.GetHTTP()[i]
			
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

	@staticmethod
	def GetFieldNames():
		return ("work time", "byte read", "http 1xx", "http 2xx", "http 3xx", "http 4xx", "http5xx", "errors", "urls found", "TOR used")

	def GetFieldValues(self):
		return (FormatTime(self.worktime),
				FormatByte(self.byteRead),
				str(self.httpCode[0]),
				str(self.httpCode[1]),
				str(self.httpCode[2]),
				str(self.httpCode[3]),
				str(self.httpCode[4]),
				str(self.errors),
				str(self.urlsFound),
				str(self.usedTOR))
		
	def __str__(self):
		out="%8s | %11s | " % (FormatTime(self.worktime), FormatByte(self.byteRead))
		for i in range(5):
			out+="%3d | " % self.httpCode[i]
		out+="%3d | %10d | %8s" % (self.errors, self.urlsFound, self.usedTOR)
		return out

	def Save(self, f):
		f.write(str(self.GetWorkTime())+" ")
		f.write(str(self.GetByteRead())+" ")
		f.write(str(self.GetErrors())+" ")
		for i in range(5):
			f.write(str(self.GetHTTP()[i])+" ")
		f.write(str(self.UsedTOR())+" ")
		f.write(str(self.GetURLsFound())+"\n")
