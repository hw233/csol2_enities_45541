#-*- coding:gb18030 -*-
import BigWorld
import Love3
from fishingJoy.FishRoom import FishRoom
from fishingJoy.Fisher import Fisher
from fishingJoy.FishingJoyTimerProvider import FishingJoyTimerProvider
from bwdebug import *

class FishingJoyMgr( FishingJoyTimerProvider, BigWorld.Base ):
	"""
	全局的捕鱼管理器。
	
	1、捕鱼活动的开启与关闭；
	2、创建并维护捕鱼房间；
	3、timer功能提供者；
	4、维护参与捕鱼的玩家数据；
	5、玩家与捕鱼房间之间的通讯桥梁；
	"""
	def __init__( self ):
		FishingJoyTimerProvider.__init__( self )
		BigWorld.Base.__init__( self )
		self.fishRooms = {}
		self.isOpen = False
		self.fishers = {}				# 正在参与捕鱼的玩家
		BigWorld.globalData["FishingJoyMgr"] = self
		
	def start( self ):
		self.isOpen = True
	
	def close( self ):
		self.isOpen = False
		
	def isOpen( self ):
		return self.isOpen
		
	def canJoin( self, playerName ):
		"""
		验证此玩家是否可以参与捕鱼
		0、捕鱼活动是否开启
		1、捕鱼人数是否已达上限
		2、玩家是否已经在捕鱼中
		3、其他条件检测...
		"""
		if not self.isOpen():
			INFO_MSG( "fish has not open." )
			return False
		if self.fishers.has_key( playerName ):
			WARNNING_MSG( "player( %s ) request dumplicated." % playerName )
			return False
		return True
		
	def findFishingRoom( self, roomID ):
		if not self.fishRooms.has_key( roomID ):
			self.fishRooms[roomID] = FishRoom( self, roomID )
		return self.fishRooms[roomID]
		
	def enterRoom( self, playerName, playerBase, roomID ):
		"""
		Define method.
		玩家选定房间开始捕鱼，可以是进入捕鱼space。
		如果需要更丰富的表现则需要更多的玩家信息，例如全服通知“玩家×××成功捕获一条大白鲨”。
		
		@param roomID : SPACE_ID,如果一个space对应一个room，那么这是一个space id，这必须是一个可以唯一标识捕鱼房间的编号，此编号可以被玩家选择。
		"""
		if self.fishers.has_key( playerBase.id ):
			HACK_MSG( "player( %s ) had already been joined." % ( playerName ) )
			return
		
		fishRoom = self.findFishingRoom( roomID )
		fisher = Fisher( playerName, playerBase, fishRoom )
		self.fishers[playerBase.id] = fisher
		fishRoom.enter( fisher )
		
	def fisherHit( self, playerID, bulletNumber, positionTuple ):
		"""
		define mehtod.
		玩家向某个位置发送炮弹。需要通知其他玩家客户端。
		"""
		if not self.fishers.has_key( playerID ):
			HACK_MSG( "cant find player( %i )." % ( playerID ) )
			return
		fisher = self.fishers[playerID]
		fisher.getRoom().fisherHit( playerID, bulletNumber, positionTuple )
		
	def fisherHitFish( self, playerID, bulletNumber, bulletType, magnification, fishNumbers ):
		"""
		define mehtod.
		玩家网中了一些鱼。
		
		@param magnification : 此次击中的倍率
		@Param fishNumbers : array of int32
		"""
		if not self.fishers.has_key( playerID ):
			HACK_MSG( "cant find player( %i )." % ( playerID ) )
			return
			
		fisher = self.fishers[playerID]
		fisher.getRoom().hitFishes( fisher, bulletNumber, bulletType, magnification, fishNumbers )
		
	def leaveRoom( self, playerID ):
		"""
		Define method.
		玩家离开房间
		"""
		if not self.fishers.has_key( playerID ):
			HACK_MSG( "cant find player( %i )." % ( playerID ) )
			return
		fisher = self.fishers.pop( playerID )
		fishRoom = fisher.getRoom()
		fishRoom.leave( fisher )
		if fishRoom.isEmpty():
			self.fishRooms.pop( fishRoom.getID() ).destroy()
			
	def fisherChangeBullet( self, playerID, bulletType ):
		"""
		Define method.
		玩家改变所使用的炮弹类型
		"""
		if not self.fishers.has_key( playerID ):
			HACK_MSG( "cant find player( %i )." % ( playerID ) )
			return
		self.fishers[playerID].changeBullet( bulletType )
		
	def fisherUseItem( self, playerID ):
		"""
		Define method.
		玩家使用了物品
		"""
		if not self.fishers.has_key( playerID ):
			HACK_MSG( "cant find player( %i )." % ( playerID ) )
			return
		self.fishers[playerID].useItem()
		
	def fisherUseItemOver( self, playerID ):
		"""
		Define method.
		玩家使用了物品
		"""
		if not self.fishers.has_key( playerID ):
			HACK_MSG( "cant find player( %i )." % ( playerID ) )
			return
		self.fishers[playerID].useItemOver()
		
	def onTimer( self, timerID, useArg ):
		FishingJoyTimerProvider.onTimer( self, timerID, useArg )
		
		