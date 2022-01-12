# -*- coding:gb18030 -*-

import random

class FishDropBox:
	def __init__( self ):
		self.totalRate = 0
		self.dropDatas = None
		
	def init( self, totalRate, dropDatas ):
		self.totalRate = totalRate
		self.dropDatas = dropDatas
		self.dropDatas.sort( key = lambda d:d["rate"] )
		
	def dropItem( self ):
		"""
		掉落物品
		
		@return 
		"""
		assert self.dropDatas is not None
		randomRate = random.randint( 0, self.totalRate )
		for data in self.dropDatas:
			if randomRate <= data["rate"]:
				return data["itemType"]
		return -1