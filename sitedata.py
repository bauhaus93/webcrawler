
class SiteData:

	def __init__(self, urlTup):
		self.host=urlTup[0]
		self.path=urlTup[1]

	def SetSource(self, urlTup):
		self.srcHost=urlTup[0]
		self.srcPath=urlTup[1]

	def SetSize(self, size):
		self.size=size


