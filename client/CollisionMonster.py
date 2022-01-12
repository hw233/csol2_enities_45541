# -*- coding: gb18030 -*-

"""
碰撞可调节类型的怪物
"""

from Monster import Monster
from interface.CombatUnit import CombatUnit
from gbref import rds
import csstatus
import BigWorld
import Const
import csdefine
import Math
import utils
import Define
import event.EventCenter as ECenter
from Function import Functor
import random

class CollisionMonster( Monster ):
	"""
	CollisionMonster
	"""

	def onModelChange( self, oldModel, newModel ):
		"""
		模型更换通知
		"""
		pass

	def createModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		template method.
		创建模型（静态模型，无法通过）
		继承 NPCObject.createModel
		"""
		rds.npcModel.createDynamicModelBG( self.modelNumber,  Functor( self.__onModelLoad, event ) )

	def __onModelLoad( self, event, model ):
		if not self.inWorld : return  # 如果已不在视野则过滤
		if model:
			self.setModel(None)
			self.addModel( model )
			model.scale = ( self.modelScale, self.modelScale, self.modelScale )
			model.position = self.position
			model.yaw = self.yaw
		else:
			ERROR_MSG( "entity %s loaded model %s fault." % ( self.className, self.modelNumber ) )

		if self.isOpen:
			rds.actionMgr.playAction( model, Const.COLLISION_MONSTER_END )
		else:
			self.openCollide()

	def fadeInModel( self ):
		"""
		渐入模型
		"""
		model = self.getModel()
		alpha = rds.npcModel.getModelAlpha( self.modelNumber )
		if alpha != 1:
			rds.effectMgr.setModelAlpha( model, alpha, 1.0 )
		else:
			rds.effectMgr.fadeInModel( model )

	def set_state( self, oldState = None ):
		CombatUnit.set_state( self, oldState )
		model = self.getModel()
		if self.state == csdefine.ENTITY_STATE_DEAD:
			self.onDieSound()	# 怪物死亡音效 jy
			self.onDie()
			for linkEffect in self.linkEffect:
				linkEffect.stop()
			self.linkEffect = []
		elif self.state == csdefine.ENTITY_STATE_FIGHT:
			print "%s %d fight." % ( self.getName(), self.id )
			self.onFightSound()	# 怪物进入战斗音效 jy
			rds.actionMgr.playAction( self.getModel(), Const.MODEL_ACTION_IDLE )
			ECenter.fireEvent( "EVT_ON_MONSTER_FIGHT_STATE_CHANGE", self )
		else:
			self.doDefaultStateAction()
		self.setArmCaps()

	def doDefaultStateAction( self ):
		"""
		播放普通状态下的动作表现
		"""
		rds.actionMgr.playAction( self.getModel(), Const.MODEL_ACTION_STAND )
		time = random.uniform( 6, 12 )
		if self.getModel() and self.getModel().hasAction( Const.MODEL_ACTION_RANDOM ):
			BigWorld.callback( time, self.playRandomAction )

	def playRandomAction( self ):
		"""
		播放随机动作
		"""
		rds.actionMgr.playActions( self.getModel(), [ Const.MODEL_ACTION_RANDOM, Const.MODEL_ACTION_STAND ], 0, [ self.doDefaultStateAction, None ] )

	def open( self ):
		"""
		客户端播放开门表现
		"""
		if len( self.models ) == 0: return
		pyModel = self.models[0]
		rds.actionMgr.playActions( pyModel, [Const.COLLISION_MONSTER_START, Const.COLLISION_MONSTER_END] )

	def close( self ):
		"""
		客户端播放关门表现
		"""
		if len( self.models ) == 0: return
		pyModel = self.models[0]
		rds.actionMgr.playActions( pyModel, [Const.COLLISION_MONSTER_OVER, Const.COLLISION_MONSTER_DEF] )

	def openCollide( self ):
		"""
		开启碰撞
		"""
		if len( self.models ) == 0: return
		model = self.models[0]
		x, y, z = utils.getModelSize( model )
		m = Math.Matrix()
		m.setScale( (x, y, z) )
		matrix = Math.Matrix( self.matrix )
		matrix.preMultiply( m )
		pyStaticModel = rds.npcModel.createStaticModel( Const.COllISION_MODEL_MODELNUM, matrix, True )
		pyStaticModel.visible = False
		self.setModel( pyStaticModel )

	def closeCollide( self ):
		"""
		关闭碰撞
		"""
		matrix = Math.Matrix( )
		matrix.setScale( ( 0, 0, 0 ) )
		pyStaticModel = rds.npcModel.createStaticModel( Const.COllISION_MODEL_MODELNUM, matrix, True )
		pyStaticModel.visible = False
		self.setModel( pyStaticModel )

	def set_isOpen( self, old ):
		"""
		开门/关门
		"""
		if self.isOpen:
			self.closeCollide()
			self.open()
		else:
			self.openCollide()
			self.close()

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		if not self.inWorld:
			return
		Monster.onCacheCompleted( self )
		if self.useRectangle:
			width, height, long = self.volume
			self.transportTrapID = self.addBoxTrapExt( self.pitch, self.yaw, self.roll, width, height, long, self.onTransport )
		else:
			self.transportTrapID = self.addTrapExt(self.radius, self.onTransport )

	def onTransport( self, entitiesInTrap ):
		"""
		预留下来以方便后续功能的扩展
		"""
		pass
		
	def onDie( self ):
		"""
		死亡回调
		"""
		Monster.onDie( self )
		self.closeCollide()

	def setArmCaps( self ):
		"""
		动作匹配caps
		"""
		pass
