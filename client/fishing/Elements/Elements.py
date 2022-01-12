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
		#self._ent = weakref.proxy( BigWorld.entities[self._id] )			# 新创建的entity不能马上从entities列表获得
		self._ent = None
		self._fadingCBID = 0
		self._isDestroyed = False

	def __del__(self):
		""""""
		#print "--->>> %s(%i) is released ..." % (self.__class__.__name__, self._id)
		pass

	def _entityReady( self, entity ):
		"""检查entity是否已经准备就绪，entity创建好了，
		但模型还不一定创建好"""
		return entity and entity.model != None

	def _initEntity( self, entity ):
		"""初始化entity"""
		assert self._ent is None
		self._ent = weakref.proxy( entity )
		self._ent.script = weakref.proxy(self)

	def _cancelFadingCallback(self):
		"""取消模型渐隐回调"""
		BigWorld.cancelCallback(self._fadingCBID)
		self._fadingCBID = 0

	@property
	def id( self ):
		return self._id

	def destroy( self ):
		"""销毁自身"""
		BigWorld.destroyEntity( self._id )
		self._cancelFadingCallback()
		self._isDestroyed = True

	def isDestroyed( self ):
		"""是否已经销毁"""
		return self._isDestroyed

	def ready( self ):
		"""是否已经就绪"""
		return self._ent != None

	def playAction( self, actionName, callback=None ):
		"""播放动作"""
		rds.actionMgr.playAction(self._ent.model, actionName, 0.0, callback)

	def fadeIn(self, duration=0.5, callback=None):
		"""模型渐隐"""
		rds.effectMgr.fadeInModel(self._ent.model, duration)
		if callback:
			self._cancelFadingCallback()
			self._fadingCBID = BigWorld.callback(duration, callback)

	def fadeOut(self, duration=2.0, callback=None):
		"""模型渐隐"""
		rds.effectMgr.fadeOutModel(self._ent.model, duration)
		if callback:
			self._cancelFadingCallback()
			self._fadingCBID = BigWorld.callback(duration, callback)

	def setVisible( self, visible ):
		"""设置是否可见"""
		self._ent.model.visible = visible

	def setDirection( self, yaw ):
		"""设置方向"""
		self._ent.model.yaw = yaw

	def turnToPosition( self, position ):
		"""转向指定位置"""
		yaw = (position - self._ent.position).yaw
		self.setDirection( yaw )

	def flatToPosition(self, position):
		"""使模型的头顶（y方向）指向position"""
		util.flatToPos(self._ent.model, position)

	def position( self ):
		"""获取当前位置"""
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
		self._travelIndex = -1							# -1表示还没开始走，此索引对应的路径点是最后走过的点

	def _initEntity( self, entity ):
		"""初始化entity"""
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
		"""路程走完时调用"""
		self.stopMoving()

	def _onTravelFailed(self):
		"""移动中断"""
		self.stopMoving()

	def speed(self):
		"""移动速度"""
		return self._speed

	def destroy( self ):
		"""销毁自身"""
		BaseElement.destroy(self)
		self._path = ()
		self._travelIndex = -1

	def setPath( self, path ):
		"""设置行进路径"""
		self._path = tuple(path)

	def setAutoMove( self, auto ):
		"""设置是否可以移动"""
		self._autoMove = auto

	def travelFinished( self ):
		"""所有路程已经走完"""
		return self._travelIndex >= (len(self._path) - 1)

	def isLastTravel( self ):
		"""是否走到了最后一程"""
		return self._travelIndex == (len(self._path) - 2)

	def updateSpeed(self, speed):
		"""更新移动速度，标量"""
		self._speed = speed
		if self.moving():
			v = self._ent.physics.velocity
			v.normalise()
			self.updateVelocity(v * self._speed)

	def updateVelocity( self, velocity ):
		"""更新移动速度，矢量"""
		self._ent.physics.velocity = velocity

	def moveTo( self, position, callback = None ):
		"""移动到指定位置"""
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
		"""停止游动"""
		physics = self._ent.physics
		physics.velocity = (0, 0, 0)
		physics.setSeekCallBackFn( None )
		physics.seek(None, 0, 0, None)

	def moving( self ):
		"""是否正在移动"""
		return self.ready() and self._ent.physics.seeking

	def resetMoving( self ):
		"""重设移动"""
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