# -*- coding:gb18030 -*-

import Math
import math
import gbref
import keys
import time
import BigWorld
from bwdebug import WARNING_MSG
from guis.ExtraEvents import LastKeyUpEvent
from ..Elements.Elements import BaseElement
from ..utils import effect
from ..utils.Event import Event
from ..FishingDefine import CANNON_FIRE_INTERVAL_MIN
from ..FishingDefine import CANNON_DECLARE_DIRECTION_CHANGED_DELTA

FIRE_EFFECT_ID = 5
NORMAL_CANNON = 1

CANNON_STYLE = {
	NORMAL_CANNON : {"modelNumber":"gw7236", "modelScale":1.0, "radius":1.0},
	}

class Cannon( BaseElement ):

	def __init__( self, style, spaceID, position, direction ):
		cannonData = CANNON_STYLE[style]
		BaseElement.__init__(self, "NPCObject", spaceID, position, direction,\
			cannonData["modelNumber"], cannonData["modelScale"], "cannon")
		self._style = style
		self._radius = cannonData["radius"]
		self._directionRange = (-math.pi, math.pi)
		self._active = True
		self._autoFire = False              # 是否自动发射，当鼠标左键一直按下不放时，就自动发射
		self._traceCursor = False
		self._lastFireTime = 0
		self._lastSyncYaw = 0
		self._bulletAmount = 0
		self._fireEvent = Event("Fire")
		self._turnEvent = Event("Turn")
		LastKeyUpEvent.attach(self._onKeyUpEvent)

	@property
	def fireEvent( self ):
		"""炮弹发射事件"""
		return self._fireEvent

	@property
	def turnEvent( self ):
		"""炮弹发射事件"""
		return self._turnEvent

	def _onKeyUpEvent(self, key, mods):
		"""按键提起事件"""
		self.handleKeyEvent(False, key, mods)

	def bulletEmpty(self):
		"""没子弹"""
		return self._bulletAmount <= 0

	def destroy( self ):
		"""销毁自身"""
		BaseElement.destroy(self)
		self._fireEvent.clear()

	def setDirection( self, yaw ):
		"""设置方向"""
		if yaw < 0:
			yaw += math.pi * 2

		if yaw < self._directionRange[0] or yaw > self._directionRange[1]:
			quadrant = math.floor( 2*yaw/math.pi )
			if quadrant == 1 or quadrant == 2:
				yaw = self._directionRange[1]
			else:
				yaw = self._directionRange[0]

		self._ent.model.yaw = yaw
		# 触发转向改变事件
		if math.fabs(self._lastSyncYaw - yaw) > CANNON_DECLARE_DIRECTION_CHANGED_DELTA:
			self._turnEvent.trigger(yaw)
			self._lastSyncYaw = yaw

	def turnToPosition( self, position ):
		"""转向指定位置"""
		BaseElement.turnToPosition(self, position)
		#self._turnEvent.trigger(position)

	def setDirectionRange( self, range ):
		"""设置转向范围"""
		self._directionRange = tuple( range )

	def setActive( self, active ):
		"""设置是否能开火"""
		self._active = active

	def fillBullet(self, amount):
		"""填装弹药"""
		self._bulletAmount = amount

	def canFire( self ):
		"""检查是否能开火"""
		return self._active and self.fireCooldown()

	def fireCooldown( self ):
		"""检查时间是否到达"""
		elapse = time.time() - self._lastFireTime
		return elapse >= CANNON_FIRE_INTERVAL_MIN

	def fire( self, destination ):
		"""往某个目标点开火"""
		if not self.ready() or self.isDestroyed():
			return
		self._lastFireTime = time.time()
		self._bulletAmount -= 1

		self.playAction("attack1")
		effect.applyEffect(self._ent.model, FIRE_EFFECT_ID)

		yaw = (destination - self._ent.position).yaw
		firePos = self.positionOnCircle( yaw )
		self._fireEvent.trigger(self._style, firePos, destination)

	def positionOnCircle( self, yaw ):
		"""根据朝向计算出圆周上的点"""
		radius = self._radius * self._ent.modelScale
		mx, my, mz = self._ent.position
		x = mx + math.sin( yaw ) * radius
		z = mz + math.cos( yaw ) * radius
		return Math.Vector3(x, my, z)

	def setTraceCursor( self, trace ):
		"""设置是否追踪鼠标"""
		self._traceCursor = trace

	def handleKeyEvent( self, down, key, mods ):
		"""按键事件通知"""
		if key == keys.KEY_LEFTMOUSE:
			if down:
				self._autoFire = True
				if self.canFire():
					cursorDropPoint = gbref.cursorFirstDropPoint()
					if cursorDropPoint:
						self.fire( cursorDropPoint )
			else:
				self._autoFire = False
			return True
		else:
			return False

	def onTick( self, dt ):
		"""Every fishing tick"""
		BaseElement.onTick(self, dt)

		if not self.ready() or self.isDestroyed():
			return

		cursorDropPoint = None
		# 转向鼠标
		if self._traceCursor:
			cursorDropPoint = gbref.cursorFirstDropPoint()
			if cursorDropPoint:
				cursorDropPoint.y = self.position().y
				self.turnToPosition( cursorDropPoint )
		# 连续发射
		if self._autoFire and self.canFire():
			cursorDropPoint = cursorDropPoint or gbref.cursorFirstDropPoint()
			if cursorDropPoint:
				cursorDropPoint.y = self.position().y
				self.fire( cursorDropPoint )
