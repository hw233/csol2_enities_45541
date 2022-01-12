# -*- coding:gb18030 -*-

import BigWorld
import gbref
import keys
from bwdebug import *
from event import EventCenter as ECenter
from Cannon import Cannon, NORMAL_CANNON
from Cannonball import PassiveCannonball, ActiveCannonball
from ..utils import util
from ..utils.Event import Event
from ..Reward.Money import Money, Silver
from ..Reward.Card import Card
from ..FishingDataMgr import FishingDataMgr
from ..FishingDefine import AUTO_BUY_AMOUNT


# ��̨���ɿ����߲������ڷ����ڵ�
class Battery:

	def __init__( self, number, spaceID, position, directionRange ):
		"""
		@param number:			��̨�ı��
		@param spaceID:			��̨���ڿռ��ID
		@param position:		��̨��λ��
		@param directionRange:	���ڵĵĳ���Χ
		"""
		self._number = number
		self._spaceID = spaceID
		self._position = position						# ��̨��λ��
		self._drange = directionRange					# ���ڵĵĳ���Χ

		self._rewards = []                              # ���ڲ��ŵĽ�������

		self._cannon = None
		self._cannonballLevel = 1						# �ڵ��ȼ���Ĭ��1��
		self._controller = None
		self._cannonFireEvent = Event("CannonballFire")

	@property
	def cannonFireEvent( self ):
		"""�ڵ������¼�"""
		return self._cannonFireEvent

	@property
	def number( self ):
		"""��̨���"""
		return self._number

	def _buildCannon( self ):
		"""��������"""
		cannon = Cannon(NORMAL_CANNON, self._spaceID, self._position, (0,0,0))
		cannon.fireEvent.bind(self._onCannonFire)
		cannon.turnEvent.bind(self._onCannonTurn)
		cannon.setDirectionRange( self._drange )
		self._cannon = cannon

	def _destroyCannon( self ):
		"""���ٴ���"""
		if self._cannon:
			self._cannon.destroy()
			self._cannon = None

	def _fireCannonball( self, origin, destination ):
		"""�����ڵ�������"""
		pass

	def _onCannonFire( self, style, origin, destination ):
		"""���ڷ���"""
		self._fireCannonball(origin, destination)
		self._controller.fire(self._cannonballLevel, destination)

	def _onCannonTurn(self, yaw):
		"""����ת��"""
		self._controller.turnCannon(yaw)

	def onFishCaught(self, fish):
		"""�㱻����̨����"""
		rewardType = FishingDataMgr.instance().getRewardTypeByCannonballLevel(self._cannonballLevel)
		earning = FishingDataMgr.instance().getFishDataByStyle(fish.style)[rewardType]
		earning *= self._controller.magnification()         # ���ϱ���
		ECenter.fireEvent("EVT_ON_SHOW_FLOATING_TEXT", fish.id, "+%s" % earning)
		if rewardType == "coin":
			Reward = Money
		elif rewardType == "ingot":
			Reward = Silver
		else:
			ERROR_MSG("Unknow reward type: %s" % rewardType)
			return
		self._rewards.append(Reward(rewardType, self._spaceID, (0, 0, 0), (fish.position(), self._position)))

	def onControllerGainMultipleCard(self, type, origin):
		"""��ñ�����"""
		self._rewards.append(Card(type, self._spaceID, (0, 0, 0), (origin, self._position)))

	def fire( self, destination ):
		"""֪ͨ���ڷ���"""
		if self._cannon.ready() and not self._cannon.isDestroyed():
			self._cannon.fire( destination )

	def onControllerTurnCannon(self, yaw):
		"""ת������"""
		if self._cannon.ready() and not self._cannon.isDestroyed():
			self._cannon.setDirection(yaw)

	def destroy( self ):
		""""""
		self._controller = None
		self._destroyCannon()
		self._cannonFireEvent.clear()
		for reward in self._rewards:
			if not reward.isDestroyed():
				reward.destroy()
		self._rewards = []

	def onCannonballLevelChanged( self, level ):
		"""�л��ڵ��ȼ�"""
		self._cannonballLevel = level

	def controlledBy( self, controller ):
		"""����Ȩ����������"""
		if self.inUse():
			return
		self._controller = controller
		self._buildCannon()

	def controller( self ):
		""""""
		return self._controller

	def discard( self ):
		"""��������̨"""
		self._controller = None
		self._destroyCannon()

	def inUse( self ):
		""""""
		return self._controller != None

	def handleKeyEvent( self, down, key, mods ):
		"""�����¼�֪ͨ"""
		return False

	def onTick( self, dt ):
		""""""
		if not self.inUse():
			return

		self._cannon.onTick( dt )

		for reward in self._rewards[:]:
			if reward.isDestroyed():
				self._rewards.remove(reward)
			else:
				reward.onTick(dt)


class OtherClientBattery(Battery):

	def __init__( self, number, spaceID, position, directionRange ):
		"""
		@param number:			��̨�ı��
		@param spaceID:			��̨���ڿռ��ID
		@param position:		��̨��λ��
		@param directionRange:	���ڵĵĳ���Χ
		"""
		Battery.__init__(self, number, spaceID, position, directionRange)
		self._fireCannonballNumber = 0

	def _buildCannon( self ):
		"""��������"""
		Battery._buildCannon(self)
		# For test
		self._cannon.setActive(False)
		self._cannon.setTraceCursor(True)

	def _fireCannonball( self, origin, destination ):
		"""�����ڵ�������"""
		Battery._fireCannonball(self, origin, destination)
		uid = util.cannonballUid(self._controller.id, self._fireCannonballNumber)
		cannonball = PassiveCannonball(uid, self._cannonballLevel, self._spaceID, origin, destination)
		self._cannonFireEvent.trigger( cannonball )

	def onControllerFire(self, destination, cannonballNumber):
		"""����Ա����"""
		self._fireCannonballNumber = cannonballNumber
		self.fire(destination)

	def onTick( self, dt ):
		""""""
		Battery.onTick(self, dt)

		if not self.inUse():
			return

		if self._cannon.ready():
			controllerEntity = BigWorld.entities.get(self.controller().id)
			if controllerEntity is not None:
				# �������ʽ��ʵ��ͬ��������ҵ�ת����е���̫���ʣ�
				# ��Ϊ������ʽ��Ҫ��˿ͻ����ܿ���������ҡ�
				self.onControllerTurnCannon(controllerEntity.yaw)


class SelfClientBattery(Battery):

	def __init__( self, number, spaceID, position, directionRange ):
		"""
		@param number:			��̨�ı��
		@param spaceID:			��̨���ڿռ��ID
		@param position:		��̨��λ��
		@param directionRange:	���ڵĵĳ���Χ
		"""
		Battery.__init__(self, number, spaceID, position, directionRange)
		self._fireCounter = 0                           # �����¼
		self._autoBuyBullet = False

	def _buildCannon( self ):
		"""��������"""
		Battery._buildCannon(self)
		self._cannon.setActive(True)
		self._cannon.setTraceCursor(True)

	def _fireCannonball( self, origin, destination ):
		"""�����ڵ�������"""
		Battery._fireCannonball(self, origin, destination)
		self._fireCounter += 1
		uid = util.cannonballUid(self._controller.id, self._fireCounter)
		cannonball = ActiveCannonball(uid, self._cannonballLevel, self._spaceID, origin, destination)
		cannonball.explosionEvent.bind( self._onCannonballExploded )
		self._cannonFireEvent.trigger( cannonball )

	def _onCannonFire( self, style, origin, destination ):
		"""���ڷ���"""
		remain = 0
		if self._controller.fire(self._cannonballLevel, destination):
			self._fireCannonball(origin, destination)
			remain = self._bulletNumberOfController()
			ECenter.fireEvent("EVT_FISHING_ON_UPDATE_BULLET", remain)

		if remain == 0:
			if self._autoBuyBullet:
				price = FishingDataMgr.instance().getCannonballPriceByLevel(self._cannonballLevel)
				amount = min(self._maxBulletAmountToBuyInto(), AUTO_BUY_AMOUNT)
				price.sell(self._controller, amount)
			else:
				ECenter.fireEvent("EVT_FISHING_ON_BUY_BULLET")

	def _onCannonballExploded( self, cannonball, fishes ):
		"""ը����ը"""
		number = util.parseCannonballUid(cannonball.uid)[1]
		fishesUid = [f.uid for f in fishes]
		self._controller.catchFishes(number, cannonball.level, fishesUid)

	def _bulletNumberOfController(self):
		"""�����ӵ�����"""
		price = FishingDataMgr.instance().getCannonballPriceByLevel(self._cannonballLevel)
		return price.unitNumber(self._controller)

	def _maxBulletAmountToBuyInto(self):
		"""���ܹ�����ӵ�����"""
		price = FishingDataMgr.instance().getCannonballPriceByLevel(self._cannonballLevel)
		return price.maxSellTo(BigWorld.player())

	def updateCannonBullet(self):
		"""��������װ��ҩ"""
		amount = self._bulletNumberOfController()
		self._cannon.fillBullet(amount)
		ECenter.fireEvent("EVT_FISHING_ON_UPDATE_BULLET", amount)

	def controlledBy( self, controller ):
		"""����Ȩ����������"""
		Battery.controlledBy(self, controller)
		self.updateCannonBullet()

	def onCannonballLevelChanged( self, level ):
		"""�л��ڵ��ȼ�"""
		Battery.onCannonballLevelChanged(self, level)
		self.updateCannonBullet()

	def onControllerChangedAutoBuy(self, auto):
		"""�����Ƿ��Զ������ӵ�"""
		self._autoBuyBullet = auto

	def handleKeyEvent( self, down, key, mods ):
		"""�����¼�֪ͨ"""
		if self.inUse():
			return self._cannon.handleKeyEvent(down, key, mods)
		else:
			return False
