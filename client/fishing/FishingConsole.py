# -*- coding:gb18030 -*-

import Math
import BigWorld
from bwdebug import *
from FishingGround import FishingGround
from FishingCamera import FishingCamera
from FishingDefine import FISHING_GROUND_VIEW_SIZE
from FishingDefine import FISHING_GROUND_ACTUAL_SIZE
from FishingDefine import FISHING_GROUND_CENTER_POS
from FishingDefine import FISHING_CAMERA_UP_SIGHT_YPR
from FishingDefine import FISHING_CAMERA_DOWN_SIGHT_YPR
from FishingDefine import FISHING_CAMERA_HEIGHT
from FishingDefine import FISH_DATA_PATH
from FishingDefine import CANNONBALL_DATA_PATH
from FishingDefine import MULTIPLE_CARD_DATA_PATH
from FishingDefine import EFFECT_DATA_PATH
from FishingDataMgr import FishingDataMgr
from event import EventCenter as ECenter

CLIENT_DEBUG = False

class FishingConsole:

	def __init__( self ):
		self._fishpond = None
		self._camera = None
		self._fishers = {}							# 渔夫

		self._triggers = {}
		self._triggers["EVT_FISHING_ON_ADD_FISH"] = self.addFish
		self._triggers["EVT_FISHING_ON_ADD_FISHER"] = self.addFisher
		self._triggers["EVT_FISHING_ON_REMOVE_FISHER"] = self.removeFisher
		self._triggers["EVT_FISHING_ON_FISHER_FIRE"] = self.onFisherFire
		self._triggers["EVT_FISHING_ON_FISHER_TURN_CANNON"] = self.onFisherTurnCannon
		self._triggers["EVT_FISHING_ON_CANNONBALL_LEVEL_CHANGED_FROM_SERVER"] = self.onFisherSwitchCannonballLevel
		self._triggers["EVT_FISHING_ON_PLAYER_CHANGE_CANNONBALL_LEVEL"] = self.onPlayerSwitchCannonballLevel
		self._triggers["EVT_FISHING_ON_FISH_CAUGHT"] = self.onFishCaught
		self._triggers["EVT_FISHING_ON_GAIN_MULTIPLE_CARD"] = self.onFisherGainMultipleCard
		self._triggers["EVT_FISHING_ON_USE_MULTIPLE_CARD"] = self.onFisherUseMultipleCard
		self._triggers["EVT_FISHING_ON_MAGNIFICATION_CHANGED"] = self.onFisherMagnificationChanged
		self._triggers["EVT_FISHING_ON_CANNONBALL_EXPLODED"] = self.onCannonballExploded
		self._triggers["EVT_FISHING_ON_FISHER_BUY_BULLET"] = self.onFisherBuyBullet
		self._triggers["EVT_FISHING_ON_PLAYER_CHANGE_AUTO_BUY"] = self.onPlayerChangeAutoBuy
		self._triggers["EVT_FISHING_ON_PLAYER_BUYING_BULLET"] = self.onPlayerBuyingBullet

		for evt in self._triggers:
			ECenter.registerEvent(evt, self)

	def init( self ):
		FishingDataMgr.instance().loadFishData(FISH_DATA_PATH)
		FishingDataMgr.instance().loadCannonballData(CANNONBALL_DATA_PATH)
		FishingDataMgr.instance().loadMultipleCardData(MULTIPLE_CARD_DATA_PATH)
		FishingDataMgr.instance().loadEffectData(EFFECT_DATA_PATH)

		self._fishpond = FishingGround( BigWorld.player().spaceID )
		self._fishpond.init(FISHING_GROUND_VIEW_SIZE, FISHING_GROUND_CENTER_POS,
							FISHING_GROUND_ACTUAL_SIZE, FISHING_GROUND_CENTER_POS,
							)

		center = self._fishpond.viewCenter()
		target = Math.Matrix()
		target.setTranslate(center)
		self._camera = FishingCamera()
		self._camera.init(target, FISHING_CAMERA_DOWN_SIGHT_YPR, FISHING_CAMERA_HEIGHT)
		self._camera.use()

		# For Test
		#self.addFisher(BigWorld.player().id, 1)
		#self.addFisher(2, 1)
		#self.addFisher(3, 2)
		#self.addFisher(4, 3)
		if CLIENT_DEBUG:
			self._fishpond.setAutoAddFish( True )
			self._fishpond.testEnterAtLater()

	def release( self ):
		""""""
		for evt in self._triggers:
			ECenter.unregisterEvent(evt, self)
		self._triggers.clear()

		self._fishers.clear()
		self._fishpond.clear()
		self._camera.recoverToPreviousCamera()

		# 关闭控制面板界面
		ECenter.fireEvent("EVT_ON_LEAVE_FISHING")

	def onClientOwnerEnterFishing(self, fisherID, batteryNumber):
		""""""
		fisher = SelfClientFisher(fisherID)
		self._fishers[fisherID] = fisher
		self._fishpond.onFisherEnter(fisher, batteryNumber)

		# 调节摄像机，保证玩家所在的炮台在游戏屏幕下方
		if batteryNumber == 2 or batteryNumber == 3:
			self._camera.setYPR(FISHING_CAMERA_UP_SIGHT_YPR)
		else:
			self._camera.setYPR(FISHING_CAMERA_DOWN_SIGHT_YPR)

	def addFisher( self, fisherID, batteryNumber ):
		""""""
		if fisherID == BigWorld.player().id:
			self.onClientOwnerEnterFishing(fisherID, batteryNumber)
		else:
			fisher = OtherClientFisher(fisherID)
			self._fishers[fisherID] = fisher
			self._fishpond.onFisherEnter(fisher, batteryNumber)

	def removeFisher( self, fisherID ):
		""""""
		self._fishpond.onFisherLeave( fisherID )

	def addFish( self, uid, style, bornTime, path ):
		"""fish"""
		self._fishpond.addFish(uid, style, bornTime, path)

	def removeFish( self, uid ):
		"""fish"""
		self._fishpond.removeFish(uid)

	def onFisherFire( self, fisherID, cannonballNumber, destination ):
		""""""
		self._fishpond.onFisherFire(fisherID, cannonballNumber, destination)

	def onFishCaught( self, fisherID, fishUid, cannonballNumber ):
		""""""
		print "------>>> on fish caught", fisherID, fishUid, cannonballNumber
		self._fishpond.onFishCaught(fisherID, fishUid, cannonballNumber)

	def onFisherTurnCannon(self, fisherID, yaw):
		""""""
		self._fishpond.onFisherTurnCannon(fisherID, yaw)

	def onFisherSwitchCannonballLevel(self, fisherID, level):
		""""""
		self._fishpond.onFisherSwitchCannonballLevel(fisherID, level)

	def onPlayerSwitchCannonballLevel(self, level):
		""""""
		player_id = BigWorld.player().id
		self._fishpond.onFisherSwitchCannonballLevel(player_id, level)
		self._fishers[player_id].switchCannonballLevel(level)

	def onPlayerChangeAutoBuy(self, auto):
		""""""
		player_id = BigWorld.player().id
		self._fishpond.onFisherChangedAutoBuyBullet(player_id, auto)
		self._fishers[player_id].setBulletAutoBuy(auto)

	def onPlayerBuyingBullet(self, level, amount):
		""""""
		fisher = self._fishers[BigWorld.player().id]
		price = FishingDataMgr.instance().getCannonballPriceByLevel(level)
		price.sell(fisher, amount)

	def onFisherGainMultipleCard(self, fisherID, type, fishUid):
		""""""
		self._fishpond.onFisherGainMultipleCard(fisherID, type, fishUid)
		self._fishers[fisherID].gainMultipleCard(type)

	def onFisherUseMultipleCard(self, fisherID, type):
		""""""
		self._fishers[fisherID].onMultipleCardUsed(type)

	def onFisherMagnificationChanged(self, fisherID, magnification):
		""""""
		self._fishpond.onFisherMagnificationChanged(fisherID, magnification)
		self._fishers[fisherID].setMagnification(magnification)

	def onCannonballExploded( self, fisherID, uid ):
		""""""
		self._fishpond.onCannonballExploded(fisherID, uid)

	def onFisherBuyBullet(self, fisherID):
		""""""
		self._fishpond.onFisherBuyBullet(fisherID)

	def handleKeyEvent( self, down, key, mods ) :
		"""处理按键消息"""
		return self._fishpond.handleKeyEvent(down, key, mods)

	def onTick( self, dt ):
		""""""
		self._fishpond.onTick(dt)

	def onEvent( self, evtMacro, *args ):
		""""""
		self._triggers[evtMacro](*args)


class FisherBase:

	def __init__( self, id ):
		self._id = id
		self._magnification = 1

	@property
	def id( self ):
		return self._id

	def isClientOwner(self):
		return False

	def turnCannon(self, destination):
		""""""
		pass

	def fire(self, cannonballLevel, destination):
		"""
		return: fire result
		rtype: bool
		"""
		return True

	def magnification(self):
		"""
		return: magnification
		rtype: int
		"""
		return self._magnification

	def setMagnification(self, value):
		"""
		"""
		self._magnification = value


class OtherClientFisher(FisherBase):

	def isClientOwner(self):
		return False

	def turnCannon(self, yaw):
		""""""
		#print "-->>> Other client fisher %i turn cannon to yaw %s" % (self.id, yaw)
		pass

	def fire( self, cannonballLevel, destination ):
		""""""
		print "-->>> Other client fisher %i fisher fire cannonball of level %i" % (self.id, cannonballLevel)
		return True


class SelfClientFisher(FisherBase):

	def __init__( self, id ):
		FisherBase. __init__(self, id)

	def isClientOwner(self):
		return True

	def turnCannon(self, yaw):
		""""""
		#print "-->>> Self client turn cannon to yaw", yaw
		BigWorld.dcursor().yaw = yaw

	def switchCannonballLevel(self, cannonballLevel):
		""""""
		BigWorld.player().base.fish_changeBullet(cannonballLevel)

	def setBulletAutoBuy(self, auto):
		""""""
		print "----->>> Fisher %i change auto buy to %s" % (self._id, auto)

	def fire( self, cannonballLevel, destination ):
		""""""
		#BigWorld.player().fishingFire(cannonballLevel, destination)
		price = FishingDataMgr.instance().getCannonballPriceByLevel(cannonballLevel)
		if price.deduct(self):
			BigWorld.player().base.fish_hit(destination)
			return True
		else:
			WARNING_MSG("Self client fisher fire(level: %i) fail! No more money..." % cannonballLevel)
			return False

	def checkForFire(self, cannonballLevel):
		""""""
		price = FishingDataMgr.instance().getCannonballPriceByLevel(cannonballLevel)
		return price.checkForPay(self)

	def payCoinCheck(self, value):
		""""""
		return self.fishingCoin() >= value

	def payIngotCheck(self, value):
		""""""
		return self.fishingIngot() >= value

	def payCoin(self, value):
		""""""
		if self.payCoinCheck(value):
			#return BigWorld.player().fishing_payMoney(value)
			BigWorld.player().fishingJoyMoney -= value
			return True
		else:
			return False

	def payIngot(self, value):
		""""""
		if self.payIngotCheck(value):
			#return BigWorld.player().fishing_paySilver(value)
			BigWorld.player().fishingJoySilver -= value
			return True
		else:
			return False

	def fishingCoin(self):
		""""""
		return BigWorld.player().fishingJoyMoney

	def fishingIngot(self):
		""""""
		return BigWorld.player().fishingJoySilver

	def magnification(self):
		""""""
		return BigWorld.player().magnification

	def catchFishes( self, cannonballNumber, cannonballLevel, fishesUid ):
		""""""
		player = BigWorld.entities.get(self._id)
		if player:
			DEBUG_MSG("-->>> Self client fisher catches %i fishes with cannanball %s level %i" % (len(fishesUid), cannonballNumber, cannonballLevel))
			player.base.fish_hitFish(cannonballNumber, fishesUid)
			# For test begin
			if CLIENT_DEBUG:
				for fishUid in fishesUid:
					ECenter.fireEvent("EVT_FISHING_ON_FISH_CAUGHT", self._id, fishUid, cannonballNumber)
			# For test end

	def gainMultipleCard(self, type):
		""""""
		pass

	def onMultipleCardUsed(self, type):
		""""""
		pass

	def buyCoinBullet(self, money):
		""""""
		BigWorld.player().cell.fish_buyBulletRequest(money)

	def buyIngotBullet(self, money):
		""""""
		BigWorld.player().base.fish_buyBulletRequest(money)