# -*- coding:gb18030 -*-

import Math
import BigWorld
from bwdebug import *

from FishGroup import FishGroup
import Scene

from Fish import SingleFish
from Fish import GroupFish

class FishSpecies:
	def __init__( self, fishData, room ):
		self.fishes = {}				# 当前房间此类型的鱼列表
		self.room = room
		
		self.index = fishData.getIndex()
		self.baseAmount = fishData.getBaseAmount()
		self.type = fishData.getType()
		
	def onFisherEnter( self, newFisher ):
		"""
		新渔夫进入
		"""
		fishes = []
		for i in xrange( self.baseAmount ):
			path = Scene.createFishPath()
			fish = self.createFish( path )
			self.fishes[fish.getNumber()] = fish
			fishes.append( fish )
		if fishes:
			self.room.fishBornBatch( fishes )
		DEBUG_MSG( "create new Fish for player.", newFisher.getName(), fishes )
		
	def isExceed( self ):
		return len( self.fishes ) > self.baseAmount * self.room.getFisherCount()
		
	def fishDie( self, number ):
		DEBUG_MSG( "fish die...%i." % number )
		# 在鱼死亡时检查，如果鱼数量超出了额定数量，那么销毁
		if self.isExceed():
			self.destroyFish( number )
		else:
			self.fishes[number].rebornStart()
			
	def swimAway( self, number ):
		DEBUG_MSG( "swimAway...%i." % number )
		self.room.swimAway( number )
		self.fishDie( number )
		
	def fishReborn( self, number ):
		if self.isExceed():
			self.destroyFish( number )
			return
		path = Scene.createFishPath()
		fish = self.fishes.pop( number )
		newNumber = self.room.newNumber()
		fish.reborn( newNumber, path )
		self.fishes[newNumber] = fish
		self.room.fishBorn( fish )
		DEBUG_MSG( "fishReborn...%i." % number )
		
	def createFish( self, path ):
		"""
		@param path : list of vector2.
		"""
		fish = SingleFish( self.index, self.room.newNumber(), self.type, self, path )
		return fish
		
	def destroyFish( self, number ):
		fish = self.fishes.pop( number )
		fish.destroy()
		
	def destroy( self ):
		for number, fish in self.fishes.items():
			self.fishes.pop( number ).destroy()
		self.room = None
		
class GroupFishSpecies( FishSpecies ):
	def __init__( self, fishData, room  ):
		FishSpecies.__init__( self, fishData, room )
		self.memberAmount = fishData.getMemberAmount()
		self.baseGroupAmount = self.baseAmount / self.memberAmount
		
	def onFisherEnter( self, fisher ):
		for i in xrange( self.baseGroupAmount ):
			path = Scene.createFishPath()
			number = self.room.newNumber()
			self.fishes[number] = GroupFish( self.index, number, self.type, self, path )
		DEBUG_MSG( "create new Fish for player.", fisher.getName(), self.fishes )
		
	def isExceed( self ):
		return len( self.fishes ) > self.room.getFisherCount() * self.baseGroupAmount
		
	def fishReborn( self, number ):
		if self.isExceed():
			self.destroyFish( number )
			return
		path = Scene.createFishPath()
		fish = self.fishes.pop( number )
		newNumber = self.room.newNumber()
		fish.reborn( newNumber, path )
		self.fishes[newNumber] = fish
		
	def swimAway( self, number ):
		fishGroup = self.fishes[number]
		for fish in fishGroup.getAliveFishes():
			self.room.swimAway( fish.getNumber() )
		self.fishDie( number )
		