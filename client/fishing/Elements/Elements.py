# -*- coding:gb18030 -*-

import BigWorld
import weakref
import keys
from gbref import rds
from bwdebug import WARNING_MSG
from ..utils import util

class BaseElement:

	def __init__( self, entityType, spaceID, position, direction, modelNumber, modelScale, elementType ):
		state = {"modelNumber":modelNumber, "modelScale":modelScale, "className":elementType}
		self._id = BigWorld.createEntity(entityType, spaceID, 0, position, direction, state)
		#self._ent = weakref.proxy( BigWorld.entities[self._id] )			# �´�����entity�������ϴ�entities�б���
		self._ent = None
		self._fadingCBID = 0
		self._isDestroyed = False

	def __del__(self):
		""""""
		#print "--->>> %s(%i) is released ..." % (self.__class__.__name__, self._id)
		pass

	def _entityReady( self, entity ):
		"""���entity�Ƿ��Ѿ�׼��������entity�������ˣ�
		��ģ�ͻ���һ��������"""
		return entity and entity.model != None

	def _initEntity( self, entity ):
		"""��ʼ��entity"""
		assert self._ent is None
		self._ent = weakref.proxy( entity )
		self._ent.script = weakref.proxy(self)

	def _cancelFadingCallback(self):
		"""ȡ��ģ�ͽ����ص�"""
		BigWorld.cancelCallback(self._fadingCBID)
		self._fadingCBID = 0

	@property
	def id( self ):
		return self._id

	def destroy( self ):
		"""��������"""
		BigWorld.destroyEntity( self._id )
		self._cancelFadingCallback()
		self._isDestroyed = True

	def isDestroyed( self ):
		"""�Ƿ��Ѿ�����"""
		return self._isDestroyed

	def ready( self ):
		"""�Ƿ��Ѿ�����"""
		return self._ent != None

	def playAction( self, actionName, callback=None ):
		"""���Ŷ���"""
		rds.actionMgr.playAction(self._ent.model, actionName, 0.0, callback)

	def fadeIn(self, duration=0.5, callback=None):
		"""ģ�ͽ���"""
		rds.effectMgr.fadeInModel(self._ent.model, duration)
		if callback:
			self._cancelFadingCallback()
			self._fadingCBID = BigWorld.callback(duration, callback)

	def fadeOut(self, duration=2.0, callback=None):
		"""ģ�ͽ���"""
		rds.effectMgr.fadeOutModel(self._ent.model, duration)
		if callback:
			self._cancelFadingCallback()
			self._fadingCBID = BigWorld.callback(duration, callback)

	def setVisible( self, visible ):
		"""�����Ƿ�ɼ�"""
		self._ent.model.visible = visible

	def setDirection( self, yaw ):
		"""���÷���"""
		self._ent.model.yaw = yaw

	def turnToPosition( self, position ):
		"""ת��ָ��λ��"""
		yaw = (position - self._ent.position).yaw
		self.setDirection( yaw )

	def flatToPosition(self, position):
		"""ʹģ�͵�ͷ����y����ָ��position"""
		util.flatToPos(self._ent.model, position)

	def position( self ):
		"""��ȡ��ǰλ��"""
		return self._ent.position

	def onTick( self, dt ):
		"""Every fishing tick"""
		if not self.ready():
			entity = BigWorld.entities.get( self._id )
			if self._entityReady( entity ):
				self._initEntity( entity )


class MovableElement( BaseElement ):

	def __init__( self, entityType, spaceID, position, direction, modelNumber, modelScale, elementType, speed, path = () ):
		BaseElement.__init__(self, entityType, spaceID, position, direction, modelNumber, modelScale, elementType)
		self._path = tuple(path)
		self._speed = speed
		self._autoMove = True
		self._travelIndex = -1							# -1��ʾ��û��ʼ�ߣ���������Ӧ��·����������߹��ĵ�

	def _initEntity( self, entity ):
		"""��ʼ��entity"""
		BaseElement._initEntity(self, entity)
		am = BigWorld.ActionMatcher(entity)
		am.turnModelToEntity = True
		entity.model.motors = (am,)
		entity.model.scale = (entity.modelScale,)*3
		entity.physics = keys.SIMPLE_PHYSICS
		entity.physics.collide = False
		entity.physics.fall = False

	def _onMoveOver( self, success ):
		if success:
			self._travelIndex += 1
			if not self.travelFinished():
				nextPos = self._path[self._travelIndex + 1]
				self.moveTo( nextPos, self._onMoveOver )
			else:
				self._onTravelFinished()
		else:
			self._onTravelFailed()
			WARNING_MSG("%s %i move fail. May be time out or blocked." % (self.__class__.__name__, self._id))

	def _onTravelFinished(self):
		"""·������ʱ����"""
		self.stopMoving()

	def _onTravelFailed(self):
		"""�ƶ��ж�"""
		self.stopMoving()

	def speed(self):
		"""�ƶ��ٶ�"""
		return self._speed

	def destroy( self ):
		"""��������"""
		BaseElement.destroy(self)
		self._path = ()
		self._travelIndex = -1

	def setPath( self, path ):
		"""�����н�·��"""
		self._path = tuple(path)

	def setAutoMove( self, auto ):
		"""�����Ƿ�����ƶ�"""
		self._autoMove = auto

	def travelFinished( self ):
		"""����·���Ѿ�����"""
		return self._travelIndex >= (len(self._path) - 1)

	def isLastTravel( self ):
		"""�Ƿ��ߵ������һ��"""
		return self._travelIndex == (len(self._path) - 2)

	def updateSpeed(self, speed):
		"""�����ƶ��ٶȣ�����"""
		self._speed = speed
		if self.moving():
			v = self._ent.physics.velocity
			v.normalise()
			self.updateVelocity(v * self._speed)

	def updateVelocity( self, velocity ):
		"""�����ƶ��ٶȣ�ʸ��"""
		self._ent.physics.velocity = velocity

	def moveTo( self, position, callback = None ):
		"""�ƶ���ָ��λ��"""
		travel = position - self._ent.position
		if travel.length < 0.05:
			if callback:
				callback(True)
			return
		direction = travel.yaw
		timeout = travel.length / self._speed * 3
		travel.normalise()
		physics = self._ent.physics
		physics.velocity = travel * self._speed
		physics.setSeekCallBackFn( None )
		physics.seek(tuple(position) + (direction,), timeout, 1000, callback, True)

	def stopMoving( self ):
		"""ֹͣ�ζ�"""
		physics = self._ent.physics
		physics.velocity = (0, 0, 0)
		physics.setSeekCallBackFn( None )
		physics.seek(None, 0, 0, None)

	def moving( self ):
		"""�Ƿ������ƶ�"""
		return self.ready() and self._ent.physics.seeking

	def resetMoving( self ):
		"""�����ƶ�"""
		self.stopMoving()
		self._travelIndex = -1

	def onTick( self, dt ):
		"""Every fishing tick"""
		BaseElement.onTick(self, dt)

		if not self.ready() or self.isDestroyed():
			return

		if self._autoMove and not self.moving() and not self.travelFinished():
			position = self._path[self._travelIndex + 1]
			self.moveTo(position, self._onMoveOver)