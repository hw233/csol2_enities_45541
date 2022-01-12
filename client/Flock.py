# -*- coding: gb18030 -*-
import sys
import BigWorld
from keys import *
import random
from interface.GameObject import GameObject
from bwdebug import *
import csdefine
from math import sin, cos
from Function import Functor
from gbref import rds
import Const
import Define
import Math


STATE_FLYING = 0
STATE_LANDING = 1
STATE_TOO_FAR = 2


# ------------------------------------------------------------------------------
# Section: class Flock
# ------------------------------------------------------------------------------


class Flock( GameObject ):
	"""
	cell 创建：
	BigWorld.createEntity("Flock", spaceID, position, direction, {"serverControl":1} )

	client 创建：
	BigWorld.createEntity("Flock", spaceID, 0，  position, direction, {"serverControl":0} )

	"""
	def __init__( self ):

		GameObject.__init__( self )
		self.utype = csdefine.ENTITY_TYPE_MISC
		self.setSelectable( False )
		self.timerID = -1
		self.xorigin = self.position[0]
		self.yorigin = self.position[1]
		self.zorigin = self.position[2]
		self.action_1 = self.actionID + "_1"
		self.action_2 = self.actionID + "_2"
		self.action_3 = self.actionID + "_3"
		self.effectID = ""
		self.inLod = False
		self.isControlEntity = False

	def filterCreator( self ):
		"""
		template method.
		创建entity的filter模块
		"""
		boidsfilter = BigWorld.BoidsFilter()
		boidsfilter.approachRadius    = self.approachRadius
		boidsfilter.collisionFraction = self.collisionFraction
		boidsfilter.influenceRadius   = self.influenceRadius
		boidsfilter.speed             = self.speed
		boidsfilter.stopRadius        = self.stopRadius
		boidsfilter.pitchEnable		  = self.pitchEnable
		boidsfilter.rollEnable		  = self.rollEnable
		boidsfilter.modelScale		  = self.modelScale
		boidsfilter.heightClipMax     = self.heightClipMax
		boidsfilter.heightClipMin     = self.heightClipMin

		return boidsfilter

	def createModels( self ):
		for i in xrange( self.amount - len(self.models) ):
			try:
				model = BigWorld.Model( self.modelFile )		# "npc/crow/crow.model"
			except ValueError:
				EXCEHOOK_MSG( "open '%s' fault." % self.modelFile )
				return
			model.outsideOnly = 1
			self.addModel( model )
			rds.actionMgr.playAction( model, Const.MODEL_ACTION_WALK, time = -5 * random.random() )

		for boid in self.models:
			boid.visible = (self.state == STATE_FLYING )

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		if not self.inWorld:
			return

		self.createModels()
		GameObject.onCacheCompleted( self )

	def leaveWorld( self ):
		if self.timerID != -1:
			BigWorld.cancelCallback( self.timerID )
		self.models = []
		self.set_state( STATE_LANDING )

	def set_state( self, oldState ):
		if self.state == STATE_FLYING:
			for boid in self.models:
				boid.visible = 1

	def boidsLanded( self ):
		landedBoids = filter(lambda x, pos=self.position: x.position == pos, self.models)
		for boid in landedBoids:
			boid.visible = 0

	def onTimer( self ):
		"""
		只用于纯客户端entity的飞行表现
		"""
		if not self.inWorld: return
		if not self.inLod: return

		if self.state == STATE_FLYING:
			now = BigWorld.time()
			position = ( self.xorigin + self.radius * sin(0.24 * now), \
						self.yorigin, self.zorigin + self.radius * cos(0.27 * now) )
			self.physics.teleport( position )

			t = int( now )                             # 其他表现
			if t % self.triggerLoopTime == 0:
				for model in self.models:
					if model.hasAction( self.actionID ):
						functor1 = Functor( self._onloadTriggerEffect1, model )
						functor2 = Functor( self._onloadTriggerEffect2, model )
						rds.actionMgr.playActions( model, [self.action_1, self.action_2, self.action_3, Const.MODEL_ACTION_WALK], callbacks = [functor1, functor2] )

		self.timerID = BigWorld.callback( 1, self.onTimer )

	def playEffect( self, model ):
		"""
		播放光效
		@param		model		: 模型
		@type		model		: PyModel
		@return					: None
		"""
		effect = None
		if len( self.effectID ):
			effect = rds.skillEffect.createEffectByID( self.effectID, None, None, Define.TYPE_PARTICLE_NPC, Define.TYPE_PARTICLE_NPC )

		if effect is None: return
		m = Math.Matrix( model.node( self.hardPoint ) )
		pos = m.applyToOrigin()
		if pos == Math.Vector3(): return
		pos.y = self.waterHeight
		effect.setPosition( pos )
		effect.start()

	def _onloadTriggerEffect1( self, model ):
		"""
		回调函数
		@param		model		: 模型
		@type		model		: PyModel
		"""
		if not self.inWorld: return
		if not self.inLod: return

		self.playEffect( model )

	def _onloadTriggerEffect2( self, model ):
		"""
		回调函数
		@param		model		: 模型
		@type		model		: PyModel
		"""
		if not self.inWorld: return
		if not self.inLod: return

		self.playEffect( model )

	def onLeaveLod( self ):
		self.inLod = False
		self.physics = DUMMY_PHYSICS
		if self.timerID != 0:
			BigWorld.cancelCallback( self.timerID )
			self.timerID = 0
		for model in self.models:
			model.visible = False

	def onEnterLod( self ):
		self.inLod = True
		if not self.isControlEntity:
			BigWorld.controlEntity( self, True )
			self.isControlEntity = True
		self.physics = STANDARD_PHYSICS
		self.set_state( STATE_FLYING )
		self.onTimer()
		for model in self.models:
			model.visible = True

#Flock.py

