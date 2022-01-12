# -*- coding: gb18030 -*-

"""
��ײ�ɵ������͵Ĺ���
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
		ģ�͸���֪ͨ
		"""
		pass

	def createModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		template method.
		����ģ�ͣ���̬ģ�ͣ��޷�ͨ����
		�̳� NPCObject.createModel
		"""
		rds.npcModel.createDynamicModelBG( self.modelNumber,  Functor( self.__onModelLoad, event ) )

	def __onModelLoad( self, event, model ):
		if not self.inWorld : return  # ����Ѳ�����Ұ�����
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
		����ģ��
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
			self.onDieSound()	# ����������Ч jy
			self.onDie()
			for linkEffect in self.linkEffect:
				linkEffect.stop()
			self.linkEffect = []
		elif self.state == csdefine.ENTITY_STATE_FIGHT:
			print "%s %d fight." % ( self.getName(), self.id )
			self.onFightSound()	# �������ս����Ч jy
			rds.actionMgr.playAction( self.getModel(), Const.MODEL_ACTION_IDLE )
			ECenter.fireEvent( "EVT_ON_MONSTER_FIGHT_STATE_CHANGE", self )
		else:
			self.doDefaultStateAction()
		self.setArmCaps()

	def doDefaultStateAction( self ):
		"""
		������ͨ״̬�µĶ�������
		"""
		rds.actionMgr.playAction( self.getModel(), Const.MODEL_ACTION_STAND )
		time = random.uniform( 6, 12 )
		if self.getModel() and self.getModel().hasAction( Const.MODEL_ACTION_RANDOM ):
			BigWorld.callback( time, self.playRandomAction )

	def playRandomAction( self ):
		"""
		�����������
		"""
		rds.actionMgr.playActions( self.getModel(), [ Const.MODEL_ACTION_RANDOM, Const.MODEL_ACTION_STAND ], 0, [ self.doDefaultStateAction, None ] )

	def open( self ):
		"""
		�ͻ��˲��ſ��ű���
		"""
		if len( self.models ) == 0: return
		pyModel = self.models[0]
		rds.actionMgr.playActions( pyModel, [Const.COLLISION_MONSTER_START, Const.COLLISION_MONSTER_END] )

	def close( self ):
		"""
		�ͻ��˲��Ź��ű���
		"""
		if len( self.models ) == 0: return
		pyModel = self.models[0]
		rds.actionMgr.playActions( pyModel, [Const.COLLISION_MONSTER_OVER, Const.COLLISION_MONSTER_DEF] )

	def openCollide( self ):
		"""
		������ײ
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
		�ر���ײ
		"""
		matrix = Math.Matrix( )
		matrix.setScale( ( 0, 0, 0 ) )
		pyStaticModel = rds.npcModel.createStaticModel( Const.COllISION_MODEL_MODELNUM, matrix, True )
		pyStaticModel.visible = False
		self.setModel( pyStaticModel )

	def set_isOpen( self, old ):
		"""
		����/����
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
		EntityCache�������
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
		Ԥ�������Է���������ܵ���չ
		"""
		pass
		
	def onDie( self ):
		"""
		�����ص�
		"""
		Monster.onDie( self )
		self.closeCollide()

	def setArmCaps( self ):
		"""
		����ƥ��caps
		"""
		pass
