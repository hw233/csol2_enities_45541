# -*- coding:gb18030 -*-

import BigWorld
import Define
from bwdebug import *
from gbref import rds
from event import EventCenter as ECenter
from fishing.FishingStatus import FishingStatus

class Fisher:
	def __init__( self ):
		self.fishing_index = -1
		self.addFisherCBID = 0
		self.fishers = set()

		self.fishesBornCache = []
		self.fisherBulletCache = {}
		self.fisherEnterCache = {}

		self.fishingJoyMoney = 0
		self.fishingJoySilver = 0
		self.magnification = 1

	def fish_fishBorn( self, fishDict ):
		"""
		Define method.
		�µ�������ˡ�

		@param fishDict : like as[ {"number":int,"type":int,"spawnTime":float, "path":[ (int, int ), ... ]}, \
									... ]
		"""
		if self.isFishingStatus():
			self.onFishesBorn(fishDict)
		else:
			self.fishesBornCache.append(fishDict)

	def onFishesBorn(self, fishDict):
		"""
		ˢ��
		"""
		for fishData in fishDict:
			uid = fishData["number"]
			style = fishData["type"]
			bornTime = fishData["spawnTime"]
			path = fishData["path"]
			ECenter.fireEvent("EVT_FISHING_ON_ADD_FISH", uid, style, bornTime, path)

	def fish_fishBeenCaught( self, fisherID, bulletNumber, fishNumbers ):
		"""
		Define method.
		һЩ�㱻����

		@param fisherID : ���OBJECT_ID
		@param number : ��ı��
		"""
		DEBUG_MSG( fisherID, bulletNumber, fishNumbers )
		for number in fishNumbers:
			ECenter.fireEvent("EVT_FISHING_ON_FISH_CAUGHT", fisherID, number, bulletNumber )

	def fish_fisherChangeBulletType( self, fisherID, bulletType ):
		"""
		Define method.
		ĳ����Ҹı����ڵ�����
		"""
		DEBUG_MSG( fisherID, bulletType )
		if fisherID not in self.fishers or not self.isFishingStatus():
			self.fisherBulletCache[fisherID] = bulletType
		else:
			ECenter.fireEvent("EVT_FISHING_ON_CANNONBALL_LEVEL_CHANGED_FROM_SERVER", fisherID, bulletType)

	def otherFisherHit( self, fisherID, bulletNumber, position ):
		"""
		Define method.
		ĳ�������ĳһ�㷢�����ڵ�
		"""
		DEBUG_MSG( fisherID, bulletNumber, position )
		ECenter.fireEvent("EVT_FISHING_ON_FISHER_FIRE", fisherID, bulletNumber, position)

	def setFishingJoyMoney( self, value ):
		"""
		Define method.
		�����Ǯ�ı���
		"""
		DEBUG_MSG( "oldValue( %i ) -> newValue( %i )." % ( self.fishingJoyMoney, value ) )
		self.fishingJoyMoney = value
		ECenter.fireEvent("EVT_FISHING_ON_FISHER_BUY_BULLET", self.id)

	def setFishingJoySilver( self, value ):
		"""
		Define method.
		������Ԫ��ֵ�ı���
		"""
		DEBUG_MSG( "oldValue( %i ) -> newValue( %i )." % ( self.fishingJoySilver, value ) )
		self.fishingJoySilver = value
		ECenter.fireEvent("EVT_FISHING_ON_FISHER_BUY_BULLET", self.id)

	def fish_pickFishItem( self, itemType, fishNumber ):
		"""
		Define method.
		����˲�����Ʒ

		@param itemType:INT16, ����Ĳ�����Ʒ����
		@param fishNumber:INT32, ������Ʒ������
		"""
		DEBUG_MSG( "pick fish( %i ) item( %i )." % ( fishNumber, itemType ) )
		ECenter.fireEvent("EVT_FISHING_ON_GAIN_MULTIPLE_CARD", self.id, itemType, fishNumber)

	def fish_useItemSuccess( self, itemType ):
		"""
		Define method.
		ʹ�ò�����Ʒ�ɹ�
		"""
		DEBUG_MSG( "use fish item( %i )." % ( itemType ) )
		ECenter.fireEvent("EVT_FISHING_ON_USE_MULTIPLE_CARD", self.id, itemType)

	def fishing_payMoneyCheck(self, value):
		""""""
		return self.fishingJoyMoney >= value

	def fishing_paySilverCheck(self, value):
		""""""
		return self.fishingJoySilver >= value

	def fishing_payMoney(self, value):
		""""""
		self.fishingJoyMoney -= value

	def fishing_paySilver(self, value):
		""""""
		self.fishingJoySilver -= value

	def fish_enterSpace( self, playerID, index ):
		"""
		Define method.
		ĳ����ҽ��벶�㳡��ĳ������̨
		"""
		DEBUG_MSG( playerID, index )
		self.fishers.add(playerID)

		if BigWorld.player().id == playerID:
			self.fishing_index = index
			self.detectToEnterFishing()
			# �򿪿���������
			if index == 0 or index == 3:
				ECenter.fireEvent("EVT_ON_ENTER_FISHING", "LEFT_STYLE")
			else:
				ECenter.fireEvent("EVT_ON_ENTER_FISHING", "RIGHT_STYLE")
		elif not self.isFishingStatus():
			self.fisherEnterCache[playerID] = index
			self.otherFisherEnterDetect()
		else:
			self.onOtherFisherEnter(playerID, index)

	def onOtherFisherEnter(self, fisherID, index):
		""""""
		ECenter.fireEvent("EVT_FISHING_ON_ADD_FISHER", fisherID, index)
		bulletType = self.fisherBulletCache.get(fisherID)
		if bulletType is not None:
			ECenter.fireEvent("EVT_FISHING_ON_CANNONBALL_LEVEL_CHANGED_FROM_SERVER", fisherID, bulletType)
			del self.fisherBulletCache[fisherID]

	def fish_leaveSpace( self, playerID ):
		"""
		Define method.
		ĳ������뿪���㳡
		"""
		DEBUG_MSG( playerID )
		if BigWorld.player().id == playerID:
			self.fishing_index = -1
			self.leaveFishing()
			self.fishers.clear()
			self.fisherEnterCache.clear()
			self.fisherBulletCache.clear()
			self.fishesBornCache = []
		else:
			if playerID in self.fisherBulletCache:
				del self.fisherBulletCache[playerID]

			if playerID in self.fisherEnterCache:
				del self.fisherEnterCache[playerID]

			self.fishers.remove(playerID)

			ECenter.fireEvent("EVT_FISHING_ON_REMOVE_FISHER", playerID)

	def isFishingStatus(self):
		"""�Ƿ����ڲ���֮��"""
		return rds.statusMgr.isInSubStatus(Define.GST_IN_WORLD, FishingStatus)

	def detectToEnterFishing(self):
		"""���״̬�����벶��"""
		if self.fishing_index == -1:
			return

		if self.isFishingStatus():
			return

		if rds.statusMgr.isInWorld():
			self.enterFishing()
			self.applyFishingCache()
		else:
			BigWorld.callback(1.0, self.detectToEnterFishing)

	def otherFisherEnterDetect(self):
		"""���״̬����������Ҽ��벶��"""
		if self.addFisherCBID:
			BigWorld.cancelCallback(self.addFisherCBID)
			self.addFisherCBID = 0

		if len(self.fisherEnterCache) == 0:
			return

		if self.isFishingStatus():
			fisherID, index = self.fisherEnterCache.popitem()
			self.onOtherFisherEnter(fisherID, index)

		self.addFisherCBID = BigWorld.callback(1.0, self.otherFisherEnterDetect)

	def applyFishingCache(self):
		"""Ӧ�û��������"""
		if not self.isFishingStatus():
			return

		cacheNonempty = False

		if len(self.fishesBornCache):
			cacheNonempty = True
			self.onFishesBorn(self.fishesBornCache.pop(0))

		if len(self.fisherEnterCache):
			cacheNonempty = True
			fisherID, index = self.fisherEnterCache.popitem()
			self.onOtherFisherEnter(fisherID, index)
		elif len(self.fisherBulletCache):
			cacheNonempty = True
			fisherID = self.fisherBulletCache.keys()[0]
			if fisherID in self.fishers:
				bulletType = self.fisherBulletCache.pop(fisherID)
				ECenter.fireEvent("EVT_FISHING_ON_CANNONBALL_LEVEL_CHANGED_FROM_SERVER", fisherID, bulletType)
			else:
				INFO_MSG("Fisher %i changed bullet level to %i, but it's not in this client yet!")

		if cacheNonempty:
			BigWorld.callback(0.5, self.applyFishingCache)

	def enterFishing( self ):
		"""���벶��"""
		rds.statusMgr.setToSubStatus( Define.GST_IN_WORLD, FishingStatus() )
		ECenter.fireEvent("EVT_FISHING_ON_ADD_FISHER", self.id, self.fishing_index)

	def leaveFishing( self ):
		"""�˳�����"""
		rds.statusMgr.leaveSubStatus( Define.GST_IN_WORLD, FishingStatus )

	def fish_setMagnification( self, magnification ):
		"""
		Define method
		���㱶�ʸı���
		"""
		DEBUG_MSG( "maginification change:old( %i ) -> new( %i )." % ( self.magnification, magnification ) )
		self.magnification = magnification
		ECenter.fireEvent("EVT_FISHING_ON_MAGNIFICATION_CHANGED", self.id, magnification)
