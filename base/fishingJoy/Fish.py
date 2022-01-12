# -*- coding:gb18030 -*-

import time
import Love3
from bwdebug import *
from FishingJoyTimer import FishingJoyTimer
import copy

class Fish:
	def __init__( self, index, number, fishType, parent,  path ):
		self.parent = parent
		self.index = index
		self.number = number
		self.type = fishType
		self.spawnTime = time.time()
		self.enable = True
		self.path = path
		self.moneyValue = Love3.g_fishingJoyLoader.getFishMoneyValue( self.index )
		self.silverValue = Love3.g_fishingJoyLoader.getFishSilverValue( self.index )
	
	def getIndex( self ):
		return self.index
	
	def getNumber( self ):
		return self.number
		
	def getMoneyValue( self ):
		return self.moneyValue
		
	def getSilverValue( self ):
		return self.silverValue
		
	def getType( self ):
		return self.type
		
	def isRunning( self ):
		return self.enable
		
	def die( self, fisher ):
		self.enable = False
		self.parent.fishDie( self.number )
		if fisher.isUsingItem():	# ʹ����Ʒʱ�޷������Ʒ
			return
		dropItemType = Love3.g_fishingJoyLoader.dropItem()
		DEBUG_MSG( "fish( %i ) dropItemType:(%i)" % ( self.getNumber(), dropItemType ) )
		if dropItemType != -1:
			fisher.pickItem( dropItemType, self.number )
			
	def reborn( self, number, path ):
		self.number = number
		self.path = path
		self.spawnTime = time.time()
		self.enable = True
		DEBUG_MSG( "new born.number( %i )." % number )
		
	def destroy( self ):
		self.parent = None
		
	def getDictFromObj( self ):
		"""
		����һ��python dict���ݣ��Ա㷢�͸��ͻ���
		"""
		return {"number":self.number, \
				"type":self.type, \
				"spawnTime":self.spawnTime, \
				"path":[ p.tuple() for p in self.path ], \
				 }
				
class SingleFish( Fish, FishingJoyTimer ):
	def __init__( self, index, number, fishType, parent,  path ):
		Fish.__init__( self, index, number, fishType, parent,  path )
		FishingJoyTimer.__init__( self )
		
		self.moveSpeed = Love3.g_fishingJoyLoader.getFishMoveSpeed( self.index )
		self.supplyDelay = Love3.g_fishingJoyLoader.getFishBornDelay( self.index )
		self.timerID = self.addTimer( self.calcDisposeTime(), self.swimAwayCB )
		DEBUG_MSG( "fish( %i ) born.life time( %f ) in timer( %i )" % ( self.number, self.calcDisposeTime(), self.timerID ) )
		
	def die( self, fisher ):
		self.cancel( self.timerID )
		self.timerID = -1
		Fish.die( self, fisher )
		
	def rebornStart( self ):
		"""
		���ⲿ֪ͨ����
		"""
		self.timerID = self.addTimer( self.supplyDelay, self.rebornCB )
		DEBUG_MSG( "fish( %i ) reborn.maybe delay( %i ) in timer( %i )" % ( self.number, self.supplyDelay, self.timerID ) )
		

	def reborn( self, number, path ):
		Fish.reborn( self, number, path )
		self.timerID = self.addTimer( self.calcDisposeTime(), self.swimAwayCB )
		DEBUG_MSG( "fish( %i ) reborn.life time( %i ) in timer( %i )" % ( self.number, self.calcDisposeTime(), self.timerID ) )
		
	def calcDisposeTime( self ):
		"""
		@rtype : float
		"""
		prePoint = self.path[0]
		length = 0
		for point in self.path[1:]:
			length += ( point - prePoint ).length
			prePoint = point
		return length / self.moveSpeed + 0.01			# ��������0.01�롣
		
	def destroy( self ):
		if self.timerID:
			self.cancel( self.timerID )
		FishingJoyTimer.destroy( self )
		Fish.destroy( self )
		
	# --------------------------------------------------------------------------------
	# callback
	# --------------------------------------------------------------------------------
	def swimAwayCB( self ):
		DEBUG_MSG( "fish number( %i )." % self.number )
		self.timerID = -1
		self.enable = False
		self.parent.swimAway( self.number )
		
	def rebornCB( self ):
		self.timerID = -1
		self.parent.fishReborn( self.number )	# ���ϲ�����Ƿ�����
		
class GroupFish( SingleFish ):
	def __init__( self, index, number, fishType, parent, path ):
		SingleFish.__init__( self, index, number, fishType, parent,  path )
		self.memberAmount = Love3.g_fishingJoyLoader.getFishMemberAmount( self.index )
		self.room = self.parent.room
		self.deadFishList = []
		self.fishes = []
		self.createMember()
		
	def getFishes( self ):
		return self.fishes
		
	def getAliveFishes( self ):
		return [fish for fish in self.fishes if fish.getNumber() not in self.deadFishList]
		
	def newNumber( self ):
		"""
		Ӧ����ʱ��ؿ��Ի��Ψһ�±�ŵģ����ҷ�װ������ʵ���ʱ���ٸġ�
		"""
		return self.room.newNumber()
		
	def createMember( self ):
		formation = Love3.g_fishingJoyLoader.getFishFormation( self.index )
		for i in xrange( self.memberAmount ):
			path = []
			for point in self.path:
				point = copy.copy( point )
				point += formation[i]
				path.append( point )
			fish = self.createFish( path )
			self.fishes.append( fish )
		self.room.fishBornBatch( self.fishes )		# ֱ��ע�ᵽroom
		
	def createFish( self, path ):
		"""
		@param path : list of vector2.
		"""
		number = self.room.newNumber()
		fish = Fish( self.index, number, self.type, self, path )
		return fish
		
	def destroy( self ):
		SingleFish.destroy( self )
		self.room = None
		
	def fishDie( self, number ):
		self.deadFishList.append( number )
		if len( self.deadFishList ) == self.memberAmount:		# ��Ⱥ������
			self.cancel( self.timerID )
			self.timerID = -1
			self.parent.fishDie( self.number )
			
	def reborn( self, number, templePath ):
		DEBUG_MSG( "groupFish( %i )" % number )
		SingleFish.reborn( self, number, templePath )
		self.deadFishList = []
		formation = Love3.g_fishingJoyLoader.getFishFormation( self.index )
		for i in xrange( self.memberAmount ):
			path = []
			for point in self.path:
				point = copy.copy( point )
				point += formation[i]
				path.append( point )
			newNumber = self.newNumber()
			self.fishes[i].reborn( newNumber, path )
		self.room.fishBornBatch( self.fishes )		# ֱ��ע�ᵽroom�����fish����ʱ��Ϊ0������̽���die����������room���Ҳ���fish���쳣����ʱ�趨��fish����С����ʱ��Ϊ0.01�롣
		
	def swimAwayCB( self ):
		DEBUG_MSG( "fish number( %i )." % self.number )
		SingleFish.swimAwayCB( self )
		