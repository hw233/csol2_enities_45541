# -*- coding:gb18030 -*-

import Love3
from bwdebug import *
from FishingJoyTimer import FishingJoyTimer

SEND_FISH_TICK_TIME	 = 0.1 # 隔多久给客户端发一次鱼的数据
SEND_FISH_AMOUNT	 = 10  # 每次发多少条鱼的数据

class Fisher( FishingJoyTimer ):
	def __init__( self, playerName, baseMailbox, room ):
		FishingJoyTimer.__init__( self )
		self.playerName = playerName
		self.baseMailbox = baseMailbox
		self.room = room
		self.bulletType = 1
		self.moneyLoss = 0		# 玩家游戏币损耗
		self.silverLoss = 0		# 玩家元宝损耗
		self.id = baseMailbox.id
		
		self.magnification = 1	# 炮弹消耗倍率
		self.usingItem = False	# 是否在捕鱼物品使用中
		self.fishes = []
		self.timerID = None
		
	def getMoneyLoss( self ):
		return self.moneyLoss
		
	def getSilverLoss( self ):
		return self.silverLoss
		
	def resetMoneyLoss( self ):
		DEBUG_MSG( "fisher:", self.getName(), self.moneyLoss )
		self.moneyLoss = 0
		
	def resetSilverLoss( self ):
		DEBUG_MSG( "fisher:", self.getName(), self.silverLoss )
		self.silverLoss = 0
		
	def getID( self ):
		return self.id
		
	def getRoom( self ):
		return self.room
		
	def getMagnification( self ):
		return self.magnification
		
	def addMoneyEarnings( self, earnings, loss ):
		"""
		计算金钱损耗、收益
		"""
		self.moneyLoss += loss - earnings
		if earnings > 0:
			self.baseMailbox.cell.fish_gainMoney( earnings )
		
	def addSilverEarnings( self, earnings, loss ):
		"""
		计算元宝损耗、收益
		"""
		self.silverLoss += loss - earnings
		if earnings > 0:
			self.baseMailbox.fish_gainSilver( earnings )
			
	def fishBorn( self, fishes ):
		"""
		这里可以有一个缓冲机制，只要列表中有鱼数据，那么启动一个timer，每SEND_FISH_TICK_TIME秒给客户端更新一次一定量的鱼数据。
		"""
		if not fishes:
			return
			
		if self.timerID:
			self.fishes.extend( fishes )
			return
			
		self.baseMailbox.client.fish_fishBorn( [ fish.getDictFromObj() for fish in fishes[ 0:10 ] ] )
		leftFishes = fishes[ 10: ]
		if leftFishes:
			self.fishes.extend( leftFishes )
			self.timerID = self.addTimer( SEND_FISH_TICK_TIME, self.sendFishToClient )
	
	def sendFishToClient( self ):
		"""
		发鱼数据给客户端
		"""
		self.timerID = None
		fishDatas = []
		# 找到 SEND_FISH_AMOUNT 只活鱼一起发给客户端
		while True:
			fish = self.fishes.pop( 0 )
			if fish.isRunning():
				fishDatas.append( fish.getDictFromObj() )
			if len( fishDatas ) >= SEND_FISH_AMOUNT or len( self.fishes ) == 0:
				break
		self.baseMailbox.client.fish_fishBorn( fishDatas )
		if len( self.fishes ) != 0:
			self.timerID = self.addTimer( SEND_FISH_TICK_TIME, self.sendFishToClient )
	
	def getBulletType( self ):
		return self.bulletType
		
	def getName( self ):
		return self.playerName
		
	def changeBullet( self, bulletType ):
		self.bulletType = bulletType
		self.room.fisherChangeBullet( self.id, bulletType )
		
	def otherFisherChangeBulletType( self, fisherID, bulletType ):
		self.baseMailbox.client.fish_fisherChangeBulletType( fisherID, bulletType )
		
	def fishBeenCaught( self, killerID, bulletNumber, fishNumbers ):
		self.baseMailbox.client.fish_fishBeenCaught( killerID, bulletNumber, fishNumbers )
		
	def otherFisherHit( self, playerID, bulletNumber, position ):
		self.baseMailbox.client.otherFisherHit( playerID, bulletNumber, position )
		
	def pickItem( self, itemType, fishNumber ):
		"""
		捕获一条鱼，幸运的获得了物品
		"""
		self.baseMailbox.fish_pickItem( itemType, fishNumber )
		
	def useItem( self ):
		self.usingItem = True
		
	def isUsingItem( self ):
		return self.usingItem
		
	def useItemOver( self ):
		self.usingItem = False
		
	def leaveRoom( self ):
		self.timerID = None
		self.baseMailbox.fish_leaveRoom()
		