# -*- coding:gb18030 -*-

import time
import random
import Math
import math
import BigWorld
from Time import Time
from bwdebug import *
from Fish.Fish import Fish
from Fish.Fish import BIG_FISH, SMALL_FISH, LARGE_FISH, LITTLE_FISH
from Fish.Fish import FISH_5, FISH_6, FISH_7, FISH_8, FISH_9, FISH_10, FISH_11, FISH_12
from Cannon.Battery import OtherClientBattery, SelfClientBattery
from utils import util


# �泡�����������ǣ�
# ���Ͻ���ԭ�㣨0,0��λ�ã����1��
# ���Ͻ�λ���ǣ�width��0�������2��
# ���½�λ���ǣ�0��height)�����3��
# ���½�λ���ǣ�width��height�������4��
# ��ͼ��
#     ��3 (0, height)       4 (width, height)
#     ������������������������
#     ��                    ��
#     ��        �泡        ��
#     ��                    ��
# �����੤�������������������ة�������������
#     ��1 (0, 0)            2 (width, 0)
#
# �ĸ���̨�ֲ����ĸ���

guid = 0
def uid():
	global guid
	guid += 1
	return guid


class FishingGround:

	def __init__( self, spaceID ):
		self._spaceID = spaceID

		self._viewArea = WorldArea()				# �泡��������
		self._actualArea = WorldArea()				# �泡ʵ������

		self._fishs = []							# �泡�����
		self._cannonballs = []						# �泡����ڵ�
		self._batteries = {}						# ��̨ {fisherID : battery,}

		self._batteriesData = {}					# ��̨������

		# For Test
		self._autoAddFish = False
		self._autoAddInterval = 1.0
		self._lastAddFish = 0

	def init( self, viewSize, viewCenter, actualSize, actualCenter ):
		"""��ʼ���泡
		@param viewSize:	�泡�������ߴ磬tuple
		@param viewPos:		�泡������������λ�ö�Ӧ���������꣬Vector3
		@param actualSize:	�泡ʵ�ʳߴ磬tuple
		@param centerPos:	�泡ʵ����������λ�ö�Ӧ���������꣬Vector3
		"""
		self._viewArea.update(viewSize, viewCenter, "CM")
		self._actualArea.update(actualSize, actualCenter, "CM")

		left = 0; top = 0
		right, bottom = self._viewArea.size()
		edgeOffset = 2
		self._batteriesData[0] = ((left + edgeOffset, top + edgeOffset),(0, math.pi/2))		# 1����̨λ���Լ�ת��Ƕ�����
		self._batteriesData[1] = ((right - edgeOffset, top + edgeOffset),(math.pi*1.5, math.pi*2))		# 2����̨λ���Լ�ת��Ƕ�����
		self._batteriesData[2] = ((left + edgeOffset, bottom - edgeOffset),(math.pi/2, math.pi))	# 3����̨λ���Լ�ת��Ƕ�����
		self._batteriesData[3] = ((right - edgeOffset, bottom - edgeOffset),(math.pi, math.pi*1.5))	# 4����̨λ���Լ�ת��Ƕ�����

	def positionToBatteryNumber(self, position):
		"""����ʵ��λ���ҵ�������̨�ı��"""
		for number, (vpos, drange) in self._batteriesData.iteritems():
			apos = self.virtualPosToViewPos(vpos)
			if position.distTo(apos) < 1:
				return number
		return None

	def layout( self ):
		"""�����泡 For Test"""
		self.init((32.0, 24.0), (2.853615, 0.0, 52.0),
				  (40.0, 26.0), (2.853615, 0.0, 52.0))

	def testEnterAtLater(self):
		"""������;���� For Test"""
		delayBornTimeSample = [1, 2, 3, 4, 5, 6, 7, 8, 9]
		server_time = Time.time()
		for i in xrange(10):
			style, path = self.generateRandomFishData()
			delay = random.sample(delayBornTimeSample, 1)[0]
			self.addFish(uid(), style, server_time - delay, path)

	def generateRandomFishData(self):
		"""������;����"""
		style = random.sample((BIG_FISH, SMALL_FISH, LARGE_FISH, LITTLE_FISH,
			FISH_5, FISH_6, FISH_7, FISH_8, FISH_9, FISH_10, FISH_11, FISH_12), 1)[0]

		size = self._actualArea.size()
		lpos = (0, random.randint(0, size[1]))
		mpos = (random.randint(0, size[0]), random.randint(0, size[1]))
		rpos = (size[0], random.randint(0, size[1]))

		leftStart = random.randint(0, 1)
		if leftStart:
			path = (lpos, mpos, rpos)
		else:
			path = (rpos, mpos, lpos)

		return style, path

	def autoAddFish( self ):
		"""�Զ����泡�����һ���� For Test"""
		style, path = self.generateRandomFishData()
		self.addFish(uid(), style, Time.time(), path)

	def setAutoAddFish( self, auto ):
		"""�����Ƿ��Զ����泡����� For Test"""
		self._autoAddFish = auto

	def clear( self ):
		"""����泡"""
		for fish in self._fishs:
			if not fish.isDestroyed():
				fish.destroy()

		for cannonball in self._cannonballs:
			if not cannonball.isDestroyed():
				cannonball.destroy()

		for battery in self._batteries.itervalues():
			battery.destroy()

		self._fishs = []
		self._cannonballs = []
		self._batteries.clear()

	def viewCenter(self):
		"""��ȡ�泡���������ĵ㣬���������λ"""
		return self._viewArea.center()

	def center( self ):
		"""��ȡ�泡ʵ���������ĵ㣬���������λ"""
		return self._actualArea.center()

	def mapToGameWorld( self, viewCenter, actualCenter ):
		"""
		ӳ�䵽��ʵ����Ϸ����
		@param viewCenter		: �泡�Ŀ�����������λ��
		@param actualCenter		: �泡��ʵ����������λ��
		"""
		self._viewArea.relocate(viewCenter, "CM")
		self._actualArea.relocate(actualCenter, "CM")

	def outsideArea( self, position ):
		"""�Ƿ���ʵ������֮��"""
		return self._actualArea.outside(position)

	def outsideViewArea(self, position):
		"""�Ƿ��ڿ�������֮��"""
		return self._viewArea.outside(position)

	def getBatteryByFisherID(self, fisherID):
		"""�������ID���Ҷ�Ӧ����̨"""
		return self._batteries.get(fisherID)

	def onFisherEnter( self, fisher, batteryNumber ):
		"""����볡
		@param fisher:			���instance
		@param batteryNumber:	��̨�ı��
		@param active:			�Ƿ��������������̨
		"""
		point, drange = self._batteriesData[batteryNumber]
		location = self.virtualPosToViewPos( point )

		if fisher.isClientOwner():
			battery = SelfClientBattery(batteryNumber, self._spaceID, location, drange)
		else:
			battery = OtherClientBattery(batteryNumber, self._spaceID, location, drange)

		battery.controlledBy( fisher )
		battery.cannonFireEvent.bind( self._onCannonFire )
		self._batteries[fisher.id] = battery

	def onFisherLeave( self, fisherID ):
		"""����뿪"""
		battery = self._batteries.get(fisherID)
		if battery is not None:
			battery.destroy()
			del self._batteries[fisherID]

	def onFisherFire( self, fisherID, cannonballNumber, destination ):
		"""������ڵ�"""
		battery = self._batteries.get(fisherID)
		if battery is not None:
			battery.onControllerFire(destination, cannonballNumber)

	def addCannonball( self, cannonball ):
		"""����һ���ڵ�"""
		self._cannonballs.append( cannonball )

	def removeCannonball( self, uid ):
		"""�Ƴ�һ���ڵ�"""
		pass

	def onCannonballExploded(self, fisherID, cannonballNumber):
		"""�ڵ���ը"""
		uid = util.cannonballUid(fisherID, cannonballNumber)
		for cannonball in self._cannonballs:
			if cannonball.uid == uid:
				cannonball.explode()
				break
		else:
			DEBUG_MSG("Can't find cannonball by uid %s" % uid)

	def onFisherBuyBullet(self, fisherID):
		"""�����˵�ҩ"""
		battery = self._batteries.get(fisherID)
		if battery is not None:
			battery.updateCannonBullet()

	def addFish( self, uid, style, bornTime, path ):
		"""���泡�������"""
		path = [self.virtualPosToActualPos(p) for p in path]
		fish = Fish(uid, style, self._spaceID, bornTime, (0,0,0), path)
		self._fishs.append(fish)

	def removeFish( self, uid ):
		pass

	def onFishCaught(self, fisherID, fishUid, cannonballNumber):
		""""""
		self.onCannonballExploded(fisherID, cannonballNumber)
		for fish in self._fishs:
			if fish.uid == fishUid:
				fish.onCaught(self._batteries.get(fisherID))
				break
		else:
			WARNING_MSG("Fish %i cought by fisher %i was lose." % (fishUid, fisherID))

	def onFisherGainMultipleCard(self, fisherID, type, fishUid):
		""""""
		battery = self._batteries.get(fisherID)
		if battery is not None:
			for fish in self._fishs:
				if fish.uid == fishUid:
					origin = fish.position()
					break
			else:
				origin = self.center()
			battery.onControllerGainMultipleCard(type, origin)

	def onFisherTurnCannon(self, fisherID, yaw):
		""""""
		battery = self._batteries.get(fisherID)
		if battery is not None:
			battery.onControllerTurnCannon(yaw)

	def onFisherSwitchCannonballLevel(self, fisherID, level):
		""""""
		battery = self._batteries.get(fisherID)
		if battery is not None:
			battery.onCannonballLevelChanged(level)
		else:
			WARNING_MSG("Can't find battery on fisher %i changed cannonball level to %i" % (fisherID, level))

	def onFisherChangedAutoBuyBullet(self, fisherID, auto):
		""""""
		battery = self._batteries.get(fisherID)
		if battery is not None:
			battery.onControllerChangedAutoBuy(auto)

	def onFisherMagnificationChanged(self, fisherID, magnification):
		""""""
		battery = self._batteries.get(fisherID)
		if battery is not None:
			battery.updateCannonBullet()

	def virtualPosToActualPos( self, point ):
		"""���������꣨�����泡ʵ�ʳߴ磬ԭ����(0, 0)��ת��Ϊ�泡ʵ�����������"""
		return self._actualArea.fromOrigin(point)

	def virtualPosToViewPos( self, point ):
		"""���������꣨�����泡���ӳߴ磬ԭ����(0, 0)��ת��Ϊ�泡�������������"""
		return self._viewArea.fromOrigin(point)

	def onTick( self, dt ):
		"""on global tick."""
		for fish in self._fishs[:]:
			if fish.isDestroyed():
				self._fishs.remove(fish)
			else:
				fish.onTick(dt)

		for cannonball in self._cannonballs[:]:
			if cannonball.isDestroyed():
				self._cannonballs.remove(cannonball)
			elif cannonball.ready() and self.outsideViewArea(cannonball.position()):
				cannonball.explode()
			else:
				cannonball.onTick(dt)

		for battery in self._batteries.itervalues():
			battery.onTick(dt)

		# For Test
		if self._autoAddFish:
			now = time.time()
			elapse = now - self._lastAddFish
			if elapse >= self._autoAddInterval:
				self.autoAddFish()
				self._lastAddFish = now

	def handleKeyEvent( self, down, key, mods ):
		"""��������Ϣ"""
		handled = False
		for battery in self._batteries.itervalues():
			handled = battery.handleKeyEvent(down, key, mods) or handled
		return handled

	def _onCannonFire( self, cannonball ):
		"""�ڵ�����֪ͨ"""
		self.addCannonball( cannonball )


class WorldArea:

	def __init__(self, size=(0, 0), position=(0, 0, 0), anchor="CM"):
		"""anchor should be one of LT, CM, RD, which mean:
		LT: position is a left top position of area
		CM: position is a center middle position of area
		RD: position is a right down position of area"""
		self._lt = Math.Vector3()
		self._rd = Math.Vector3()
		self.update(size, position, anchor)

	def size(self):
		return (self._rd.x - self._lt.x, self._rd.z - self._lt.z)

	def center(self):
		w, h = self.size()
		return (self._lt.x + w/2, self._lt.y, self._lt.z + h/2)

	def resize(self, size, anchor="CM"):
		""""""
		w, h = size

		if anchor == "LT":
			x, y, z = self._lt
			self._rd.set(x + w, y, z + h)
		elif anchor == "CM":
			x, y, z = self.center()
			self._lt.set(x - w/2.0, y, z - h/2.0)
			self._rd.set(x + w/2.0, y, z + h/2.0)
		elif anchor == "RD":
			x, y, z = self._rd
			self._lt.set(x - w, y, z - h)
		else:
			assert 0, "anchor should be one of LT, CM, RD"

	def relocate(self, position, anchor="CM"):
		""""""
		self.update(self.size(), position, anchor)

	def update(self, size, position, anchor="CM"):
		""""""
		w, h = size
		x, y, z = position

		if anchor == "LT":
			self._lt.set(x, y, z)
			self._rd.set(x + w, y, z + h)
		elif anchor == "CM":
			self._lt.set(x - w/2.0, y, z - h/2.0)
			self._rd.set(x + w/2.0, y, z + h/2.0)
		elif anchor == "RD":
			self._lt.set(x - w, y, z - h)
			self._rd.set(x, y, z)
		else:
			assert 0, "anchor should be one of LT, CM, RD"

	def outside(self, position):
		""""""
		x, y, z = position
		lt, rd = self._lt, self._rd
		return x < lt.x or x > rd.x or z < lt.z or z > rd.z

	def fromOrigin(self, point):
		""""""
		lt = self._lt
		x = lt.x + point[0]
		z = lt.z + point[1]
		return Math.Vector3( x, lt.y, z )


def testWorldArea():
	area = WorldArea((20, 60), (0,0,0), "LT")

	assert area.size() == (20.0, 60.0), "size = %s, %s" % area.size()
	assert(area.center() == (10.0, 0, 30.0), "center = %s, %s, %s" % area.center())

	assert(area.outside((-1, 0, 0)))
	assert(area.outside((10, 0, 70)))
	assert(area.outside((0, 0, 70)))

	assert(not area.outside((0, 0, 0)))
	assert(not area.outside((20, 0, 20)))
	assert(not area.outside((20, 100, 20)))
	assert(not area.outside((20, 0, 60)))
	assert(not area.outside((20, 10, 60)))
	assert(not area.outside((0, 10, 40)))

	area.resize((10, 10), "LT")

	assert(area.size() == (10.0, 10.0))
	assert(area.center() == (5.0, 0, 5.0))

	assert(area.outside((-1, 0, 0)))
	assert(area.outside((10, 0, 70)))
	assert(area.outside((0, 0, 70)))
	assert(area.outside((20, 0, 20)))
	assert(area.outside((20, 0, 10)))

	assert(not area.outside((0, 0, 10)))
	assert(not area.outside((10, 0, 10)))
	assert(not area.outside((10, 0, 0)))
	assert(not area.outside((0, 0, 0)))

	area.relocate((10, 10, 10), "LT")

	assert(area.size() == (10.0, 10.0))
	assert(area.center() == (15.0, 10, 15.0))

	assert(area.outside((0, 0, 10)))
	assert(area.outside((10, 0, 0)))
	assert(area.outside((0, 0, 0)))
	assert(area.outside((30, 0, 20)))

	assert(not area.outside((10, 0, 10)))
	assert(not area.outside((20, 0, 10)))
	assert(not area.outside((20, 0, 20)))

	area.relocate((10, 10, 10), "CM")

	assert(area.size() == (10.0, 10.0))
	assert(area.center() == (10.0, 10, 10.0))

	assert(area.outside((0, 0, 0)))
	assert(area.outside((0, 0, 15)))
	assert(area.outside((16, 0, 15)))

	assert(not area.outside((5, 0, 5)))
	assert(not area.outside((10, 0, 10)))
	assert(not area.outside((15, 0, 15)))
	assert(not area.outside((8, 0, 8)))

	print "test OK!"
