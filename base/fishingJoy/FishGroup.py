# -*- coding:gb18030 -*-

class FishGroup:
	"""
	鱼群。只做简单的计数维护。
	"""
	def __init__( self, number, fishSpecies, memberCount ):
		self.number = number
		self.memberCount = memberCount
		self.fishSpecies = fishSpecies
		self.fishes = {}
		
	def addFish( self, fish ):
		self.memberCount += 1
		self.fishes[fish.getNumber()] = fish
		
	def getFishes( self ):
		return self.fishes
		
	def fishDie( self, number ):
		self.memberCount -= 1
		if self.isEmpty():
			self.fishSpecies.fishGroupDie( self.number )
			
	def isEmpty( self ):
		return self.memberCount == 0
		