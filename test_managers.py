from multiprocessing import Process
from multiprocessing.managers import BaseManager
from time import sleep
from random import randint


class Rekt(object):

	def __init__(self, n):
		self.n=n


	def GetN(self):
		return self.n*self.n
	
	def SetN(self, n):
		self.n=n

	def HardcoreAlloc(self):
		self.data=[]
		print "DO"
		for i in range(100000):
			s=""
			for j in range(100):
				s+="LELELEL"
			self.data.append(s)
		print "DONE"
		
	def GetData(self):
		return self.data

	def Master(self, lel):
		for i in range(10):
			print lel.LEL()
			if i==5:
				self.HardcoreAlloc()
			sleep(1)
			
class Rofl(object):

        def LEL(self):
                return 666

class Manager(BaseManager):
	pass

Manager.register("Rekt", Rekt)
Manager.register("Rofl", Rofl)

if __name__=="__main__":
	m=Manager()
	m.start()
	r=m.Rekt(5)
	lel=m.Rofl()
	p=Process(target=r.Master, args=(lel,))
	p.start()
	p.join()
	print r.GetData()[:20]
	sleep(10)
