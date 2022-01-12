# -*- coding: gb18030 -*-
#

from interface.GameObject import GameObject
from gbref import rds
import csdefine
import BigWorld
import Const
import Define
from Function import Functor

class EnvironmentObject( GameObject ):
	"""
	"""
	def __init__( self ):
		"""
		初始化
		"""
		GameObject.__init__( self )
		self.setSelectable( False )


	def prerequisites( self ):
		"""
		This method is called before the entity enter the world
		"""
		prerep = []
		path = rds.npcModel.getModelSources( self.modelNumber )
		prerep.extend( path )
		hairPath = rds.npcModel.getHairPath( self.modelNumber )
		prerep.extend( [hairPath] )
		return prerep

	def filterCreator( self ):
		"""
		"""
		return BigWorld.DumbFilter()

	def enterWorld( self ) :
		"""
		"""
		self.createModel( Define.MODEL_LOAD_ENTER_WORLD )
		GameObject.enterWorld( self )

	def leaveWorld( self ):
		"""
		"""
		GameObject.leaveWorld( self )


	def set_modelNumber( self, oldModelNumber = 0 ):
		"""
		"""
		self.createModel()

	def createModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		"""
		rds.npcModel.createDynamicModelBG( self.modelNumber,  Functor( self.__onModelLoad, event ) )
	
	def __onModelLoad( self, event, pyModel ):
		if not self.inWorld : return  # 如果已不在视野则过滤
		self.setModel( pyModel, event )
		pyModel.motors = ()
		pyModel.scale = ( self.modelScale, self.modelScale, self.modelScale )
		rds.actionMgr.playAction( pyModel, Const.MODEL_ACTION_WJ_STAND )
		self.model.visible = self.visible

	def set_visible( self, value = False ):
		"""
		"""
		if self.model is not None:
			self.model.visible = self.visible