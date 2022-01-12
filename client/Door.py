# -*- coding: gb18030 -*-

"""
门
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
		初始化
		"""
		NPCObject.__init__( self )

		self.selectable = False		# 不能选中

	def createModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		template method.
		创建模型（静态模型，无法通过）
		继承 NPCObject.createModel
		"""
		rds.npcModel.createDynamicModelBG( self.modelNumber,  Functor( self.__onModelLoad, event ) )
	
	def __onModelLoad( self, event, pyModel ):
		if not self.inWorld : return  # 如果已不在视野则过滤
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
		渐入模型
		"""
		rds.effectMgr.fadeInModel( self.getModel() )

	def open( self ):
		"""
		客户端播放开门表现
		"""
		if len( self.models ) == 0: return
		pyModel = self.models[0]
		rds.actionMgr.playActions( pyModel, [Const.DOOR_FENG_JIAN_SHEN_GONG_STAR, Const.DOOR_FENG_JIAN_SHEN_GONG_END] )

	def close( self ):
		"""
		客户端播放关门表现
		"""
		if len( self.models ) == 0: return
		pyModel = self.models[0]
		rds.actionMgr.playActions( pyModel, [Const.DOOR_FENG_JIAN_SHEN_GONG_OVER, Const.DOOR_FENG_JIAN_SHEN_GONG_DEF] )

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
		pyStaticModel = rds.npcModel.createStaticModel( Const.STATIC_MODEL_MODELNUM, matrix, True )
		pyStaticModel.visible = False
		self.setModel( pyStaticModel )

	def closeCollide( self ):
		"""
		关闭碰撞
		"""
		self.setModel( None )

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
		NPCObject.onCacheCompleted( self )
		if self.useRectangle:
			width, height, long = self.volume
			self.transportTrapID = self.addBoxTrapExt( self.pitch, self.yaw, self.roll, width, height, long, self.onTransport )
		else:
			self.transportTrapID = self.addTrapExt(self.radius, self.onTransport )

	def onModelChange( self, oldModel, newModel ):
		"""
		模型改变通知
		"""
		pass

	def onTransport( self, entitiesInTrap ):
		if not self.isOpen:
			if self.className == "10111397" :
				BigWorld.player().statusMessage( csstatus.SHMZ_ROLE_MEET_DOOR )
