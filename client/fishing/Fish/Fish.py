# -*- coding:gb18030 -*-

from Time import Time
from bwdebug import *
from ..Elements.Elements import MovableElement
from ..FishingDataMgr import FishingDataMgr
from ..utils import effect
import Math

BIG_FISH = 1
SMALL_FISH = 2
LARGE_FISH = 3
LITTLE_FISH = 4
FISH_5 = 5
FISH_6 = 6
FISH_7 = 7
FISH_8 = 8
FISH_9 = 9
FISH_10 = 10
FISH_11 = 11
FISH_12 = 12

FISH_STYLE = {
	BIG_FISH : {"model":"gw0362_2", "scale":10.0, "speed":3},
	SMALL_FISH : {"model":"gw0362_2", "scale":8.0, "speed":4},
	LARGE_FISH : {"model":"gw0362_2", "scale":13.0, "speed":1.5},
	LITTLE_FISH : {"model":"gw0362_2", "scale":5.0, "speed":6},
	}

class Fish( MovableElement ):

	def __init__( self, uid, style, spaceID, bornTime, direction, path ):
		fishData = FishingDataMgr.instance().getFishDataByStyle(style)
		roll, pitch, yaw = direction

		bornPos, yaw_direction, travelIndex = self.findArrival(bornTime, fishData["speed"], path)
		direction = (roll, pitch, yaw_direction.yaw)

		MovableElement.__init__(self, "NPCObject", spaceID, bornPos, direction,
			fishData["model"], fishData["scale"], "fish", fishData["speed"], path)
		self._travelIndex = travelIndex
		self._uid = uid
		self._style = style
		self._bornTime = bornTime
		self._dead = False

	@property
	def uid( self ):
		"""获取uid"""
		return self._uid

	@property
	def style( self ):
		"""获取uid"""
		return self._style

	def _initEntity( self, entity ):
		"""初始化entity"""
		# The fish died before ready!
		if self.isDead(): return

		MovableElement._initEntity(self, entity)
		setattr(entity, "uid", self._uid)

		fishData = FishingDataMgr.instance().getFishDataByStyle(self._style)
		eid = fishData.get("moveEffect")

		if eid:
			effect.applyEffect(entity.model, eid)

	def _onMoveOver( self, success ):
		MovableElement._onMoveOver(self, success)
		#print "----->>> Fish %i move over, success %s" % (self.id, success)

	def _onCaughtPlayOver(self):
		"""被抓住动作播放结束回调"""
		self.destroy()

	def isDead(self):
		"""是否已经死亡"""
		return self._dead

	def timeout(self):
		"""是否已经超时"""
		if len(self._path) <= 1:
			return False

		elapse = Time.time() - self._bornTime
		travel = 0
		origin = self._path[0]
		for goal in self._path[1:]:
			travel += origin.distTo(goal)
			origin = goal

		# 如果过去的时间超出了根据实际路程和速度计算的时间的3倍，就算超时
		return elapse > (travel / self._speed * 3)

	@staticmethod
	def findArrival(bornTime, speed, path):
		"""根据服务器提供的出生时间来计算实际所在的位置
		@param bornTime: 出生时间
		@param path: 行进路径
		@param speed: 行进速度
		@return: 起始位置，路径索引
		@rtype: position, float
		"""
		arrival = Math.Vector3(0, 0, 0)
		direction = Math.Vector3(0, 0, 0)
		travelIndex = -1

		if len(path) == 0:
			return arrival, direction, travelIndex

		elapse = Time.time() - bornTime
		if elapse <= 0:
			if len(path) >= 2:
				direction = path[1] - path[0]
			return path[0], direction, travelIndex

		travel = elapse * speed
		origin = path[0]
		goal = origin
		distance = 0
		travelIndex = 0

		for goal in path[1:]:
			distance += goal.distTo(origin)
			if distance > travel:
				break
			else:
				origin = goal
				travelIndex += 1
		# 所有距离加起来都达不到根据时间算得的路程
		# 说明鱼已经走完了全程
		else:
			travel = distance

		direction = origin - goal
		direction.normalise()
		arrival = goal + direction * (distance - travel)

		return arrival, -direction, travelIndex

	def adjustPosition( self ):
		"""根据服务器提供的出生时间来计算实际所在的位置，
		目的是保持鱼的位置跟其他客户端玩家的一样"""
		arrival = self.findArrival(self._bornTime, self._speed, self._path)
		self.stopMoving()
		self._travelIndex = arrival[2]
		self.teleport(arrival[0], self._ent.yaw)

	def teleport(self, position, yaw):
		"""将鱼传送到指定位置"""
		self._ent.model.position = arrival
		self._ent.restartFilterMoving()
		self._ent.setFilterLastPosition(position)
		self._ent.restartFilterMoving()
		self._ent.setFilterYaw(yaw)
		self._ent.restartFilterMoving()

	def onCaught( self, battery ):
		"""鱼被抓住"""
		DEBUG_MSG("Fish %i is caught by %i" % (self._uid, battery.controller().id))
		assert self._dead == False

		self._dead = True
		if self.isDestroyed(): return

		self.setAutoMove(False)
		if self.ready():
			self.stopMoving()
			self.fadeOut(2.0, self._onCaughtPlayOver)
			battery.onFishCaught(self)
		else:
			self.destroy()

	def onTick( self, dt ):
		"""Every fishing tick"""
		MovableElement.onTick(self, dt)

		if not self.ready() or self.isDestroyed():
			return

		# For Test currently
		if self.travelFinished() or self.timeout():
			self.destroy()


def test():
	import Math
	speed = 1
	bornTime = Time.time()
	pos1 = Math.Vector3((0, 0, 0))
	pos2 = Math.Vector3((5, 0, 0))
	pos3 = Math.Vector3((10, 0, 0))
	pos4 = Math.Vector3((13, 0, 0))
	path = (pos1, pos2, pos3, pos4)
	assert (Fish.findArrival(bornTime, speed, path) == (Math.Vector3((0, 0, 0)), 0))
	assert (Fish.findArrival(bornTime - 1, speed, path) == (Math.Vector3((1, 0, 0)), 0))
	assert (Fish.findArrival(bornTime - 2, speed, path) == (Math.Vector3((2, 0, 0)), 0))
	assert (Fish.findArrival(bornTime - 5, speed, path) == (Math.Vector3((5, 0, 0)), 1))
	assert (Fish.findArrival(bornTime - 6, speed, path) == (Math.Vector3((6, 0, 0)), 1))
	assert (Fish.findArrival(bornTime - 9, speed, path) == (Math.Vector3((9, 0, 0)), 1))
	assert (Fish.findArrival(bornTime - 11, speed, path) == (Math.Vector3((11, 0, 0)), 2))
	assert (Fish.findArrival(bornTime - 12, speed, path) == (Math.Vector3((12, 0, 0)), 2))
	assert (Fish.findArrival(bornTime - 13, speed, path) == (Math.Vector3((13, 0, 0)), 3))
	assert (Fish.findArrival(bornTime - 14, speed, path) == (Math.Vector3((13, 0, 0)), 3))
	print "test is ok!"
