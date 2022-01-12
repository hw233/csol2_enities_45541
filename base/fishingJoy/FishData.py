# -*- coding:gb18030 -*-

import BigWorld
import random
import Math
import math
import Scene


FORMATION = [ [( 0, 0 ), ( 2, 0 ), ( 4, 0 ), ( 6, 0 ), ( 8, 0 )],	\
					[( 0, 0 ), ( 2, -1 ), ( 2, 1 ), ( 4, -2 ), ( 4, 2 )]	\
					 ]

	
class FishData:
	"""
	<item>
		<type> 1 </type>
		<name> 小黄鱼 </name>
		<baseAmount> 10 	</baseAmount>
		<group> 5 </group>
		<value> 1 </value>
		<moveSpeed> 15 </moveSpeed>
		<supplyDelay> 0 </supplyDelay>
		<catchRate> 100 </catchRate>
		<randomMoveRate> 1 </randomMoveRate>
	</item>
	每一个房间的鱼会关联同类型的FishData
	"""
	length = 1024
	wide = 768
	def __init__( self, data ):
		self.index = data["index"]
		self.type = data["type"]
		self.moneyValue = data["moneyValue"]
		self.silverValue = data["silverValue"]
		self.moveSpeed = data["moveSpeed"]
		self.catchRate = data["catchRate"]
		self.memberAmount = data["memberAmount"]
		self.randomMoveRate = data["randomMoveRate"]
		self.supplyDelay = data["supplyDelay"]
		self.baseAmount = data["baseAmount"]			# 每一个玩家对应的数量。
		
	def getIndex( self ):
		return self.index
		
	def getType( self ):
		return self.type
		
	def getMoneyValue( self ):
		return self.moneyValue
		
	def getSilverValue( self ):
		return self.silverValue
		
	def getBaseAmount( self ):
		return self.baseAmount
		
	def getSupplyDelay( self ):
		return self.supplyDelay
		
	def getMoveSpeed( self ):
		return self.moveSpeed
		
	def getMemberAmount( self ):
		return self.memberAmount
		
	def getFormation( self ):
		return random.choice( FORMATION )

