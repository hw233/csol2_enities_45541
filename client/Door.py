# -*- coding: gb18030 -*-

"""
��
"""

from NPCObject import NPCObject
from gbref import rds
import csstatus
import BigWorld
import Const
import Math
import utils
import Define
from Function import Functor

class Door( NPCObject ):
	"""
	Door
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		NPCObject.__init__( self )

		self.selectable = False		# ����ѡ��

	def createModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		template method.
		����ģ�ͣ���̬ģ�ͣ��޷�ͨ����
		�̳� NPCObject.createModel
		"""
		rds.npcModel.createDynamicModelBG( self.modelNumber,  Functor( self.__onModelLoad, event ) )
	
	def __onModelLoad( self, event, pyModel ):
		if not self.inWorld : return  # ����Ѳ�����Ұ�����
		if pyModel:
			self.addModel( pyModel )
			pyModel.scale = ( self.modelScale, self.modelScale, self.modelScale )
			pyModel.position = self.position
			pyModel.yaw = self.yaw
		else:
			ERROR_MSG( "entity %s loaded model %s fault." % ( self.className, self.modelNumber ) )

		if self.isOpen:
			rds.actionMgr.playAction( pyModel, Const.DOOR_FENG_JIAN_SHEN_GONG_END )
		else:
			self.openCollide()
		
	def fadeInModel( self ):
		"""
		����ģ��
		"""
		rds.effectMgr.fadeInModel( self.getModel() )

	def open( self ):
		"""
		�ͻ��˲��ſ��ű���
		"""
		if len( self.models ) == 0: return
		pyModel = self.models[0]
		rds.actionMgr.playActions( pyModel, [Const.DOOR_FENG_JIAN_SHEN_GONG_STAR, Const.DOOR_FENG_JIAN_SHEN_GONG_END] )

	def close( self ):
		"""
		�ͻ��˲��Ź��ű���
		"""
		if len( self.models ) == 0: return
		pyModel = self.models[0]
		rds.actionMgr.playActions( pyModel, [Const.DOOR_FENG_JIAN_SHEN_GONG_OVER, Const.DOOR_FENG_JIAN_SHEN_GONG_DEF] )

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
		pyStaticModel = rds.npcModel.createStaticModel( Const.STATIC_MODEL_MODELNUM, matrix, True )
		pyStaticModel.visible = False
		self.setModel( pyStaticModel )

	def closeCollide( self ):
		"""
		�ر���ײ
		"""
		self.setModel( None )

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
		NPCObject.onCacheCompleted( self )
		if self.useRectangle:
			width, height, long = self.volume
			self.transportTrapID = self.addBoxTrapExt( self.pitch, self.yaw, self.roll, width, height, long, self.onTransport )
		else:
			self.transportTrapID = self.addTrapExt(self.radius, self.onTransport )

	def onModelChange( self, oldModel, newModel ):
		"""
		ģ�͸ı�֪ͨ
		"""
		pass

	def onTransport( self, entitiesInTrap ):
		if not self.isOpen:
			if self.className == "10111397" :
				BigWorld.player().statusMessage( csstatus.SHMZ_ROLE_MEET_DOOR )
