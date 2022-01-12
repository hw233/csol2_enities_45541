# -*- coding:gb18030 -*-

import Love3
from bwdebug import *
from FishingJoyTimer import FishingJoyTimer

SEND_FISH_TICK_TIME	 = 0.1 # ����ø��ͻ��˷�һ���������
SEND_FISH_AMOUNT	 = 10  # ÿ�η��������������

class Fisher( FishingJoyTimer ):
	def __init__( self, playerName, baseMailbox, room ):
		FishingJoyTimer.__init__( self )
		self.playerName = playerName
		self.baseMailbox = baseMailbox
		self.room = room
		self.bulletType = 1
		self.moneyLoss = 0		# �����Ϸ�����
		self.silverLoss = 0		# ���Ԫ�����
		self.id = baseMailbox.id
		
		self.magnification = 1	# �ڵ����ı���
		self.usingItem = False	# �Ƿ��ڲ�����Ʒʹ����
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
		�����Ǯ��ġ�����
		"""
		self.moneyLoss += loss - earnings
		if earnings > 0:
			self.baseMailbox.cell.fish_gainMoney( earnings )
		
	def addSilverEarnings( self, earnings, loss ):
		"""
		����Ԫ����ġ�����
		"""
		self.silverLoss += loss - earnings
		if earnings > 0:
			self.baseMailbox.fish_gainSilver( earnings )
			
	def fishBorn( self, fishes ):
		"""
		���������һ��������ƣ�ֻҪ�б����������ݣ���ô����һ��timer��ÿSEND_FISH_TICK_TIME����ͻ��˸���һ��һ�����������ݡ�
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
		�������ݸ��ͻ���
		"""
		self.timerID = None
		fishDatas = []
		# �ҵ� SEND_FISH_AMOUNT ֻ����һ�𷢸��ͻ���
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
		����һ���㣬���˵Ļ������Ʒ
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
		