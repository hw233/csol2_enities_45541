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
		self._autoFire = False              # �Ƿ��Զ����䣬��������һֱ���²���ʱ�����Զ�����
		self._traceCursor = False
		self._lastFireTime = 0
		self._lastSyncYaw = 0
		self._bulletAmount = 0
		self._fireEvent = Event("Fire")
		self._turnEvent = Event("Turn")
		LastKeyUpEvent.attach(self._onKeyUpEvent)

	@property
	def fireEvent( self ):
		"""�ڵ������¼�"""
		return self._fireEvent

	@property
	def turnEvent( self ):
		"""�ڵ������¼�"""
		return self._turnEvent

	def _onKeyUpEvent(self, key, mods):
		"""���������¼�"""
		self.handleKeyEvent(False, key, mods)

	def bulletEmpty(self):
		"""û�ӵ�"""
		return self._bulletAmount <= 0

	def destroy( self ):
		"""��������"""
		BaseElement.destroy(self)
		self._fireEvent.clear()

	def setDirection( self, yaw ):
		"""���÷���"""
		if yaw < 0:
			yaw += math.pi * 2

		if yaw < self._directionRange[0] or yaw > self._directionRange[1]:
			quadrant = math.floor( 2*yaw/math.pi )
			if quadrant == 1 or quadrant == 2:
				yaw = self._directionRange[1]
			else:
				yaw = self._directionRange[0]

		self._ent.model.yaw = yaw
		# ����ת��ı��¼�
		if math.fabs(self._lastSyncYaw - yaw) > CANNON_DECLARE_DIRECTION_CHANGED_DELTA:
			self._turnEvent.trigger(yaw)
			self._lastSyncYaw = yaw

	def turnToPosition( self, position ):
		"""ת��ָ��λ��"""
		BaseElement.turnToPosition(self, position)
		#self._turnEvent.trigger(position)

	def setDirectionRange( self, range ):
		"""����ת��Χ"""
		self._directionRange = tuple( range )

	def setActive( self, active ):
		"""�����Ƿ��ܿ���"""
		self._active = active

	def fillBullet(self, amount):
		"""��װ��ҩ"""
		self._bulletAmount = amount

	def canFire( self ):
		"""����Ƿ��ܿ���"""
		return self._active and self.fireCooldown()

	def fireCooldown( self ):
		"""���ʱ���Ƿ񵽴�"""
		elapse = time.time() - self._lastFireTime
		return elapse >= CANNON_FIRE_INTERVAL_MIN

	def fire( self, destination ):
		"""��ĳ��Ŀ��㿪��"""
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
		"""���ݳ�������Բ���ϵĵ�"""
		radius = self._radius * self._ent.modelScale
		mx, my, mz = self._ent.position
		x = mx + math.sin( yaw ) * radius
		z = mz + math.cos( yaw ) * radius
		return Math.Vector3(x, my, z)

	def setTraceCursor( self, trace ):
		"""�����Ƿ�׷�����"""
		self._traceCursor = trace

	def handleKeyEvent( self, down, key, mods ):
		"""�����¼�֪ͨ"""
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
		# ת�����
		if self._traceCursor:
			cursorDropPoint = gbref.cursorFirstDropPoint()
			if cursorDropPoint:
				cursorDropPoint.y = self.position().y
				self.turnToPosition( cursorDropPoint )
		# ��������
		if self._autoFire and self.canFire():
			cursorDropPoint = cursorDropPoint or gbref.cursorFirstDropPoint()
			if cursorDropPoint:
				cursorDropPoint.y = self.position().y
				self.fire( cursorDropPoint )
