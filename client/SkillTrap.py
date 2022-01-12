# -*- coding: gb18030 -*-

# 2008-11-26 gjx&lq
from Function import Functor

import BigWorld
from bwdebug import *
from NPCObject import NPCObject
from interface.CombatUnit import CombatUnit
from gbref import rds
import csdefine
import Define


class SkillTrap( NPCObject, CombatUnit ):
	"""
	技能陷阱
	"""
	def __init__( self ):
		NPCObject.__init__( self )
		CombatUnit.__init__( self )

		self.selectable = False		# 不能选中
		self.entityList = []
		self.visibleRules = [ csdefine.VISIBLE_RULE_BY_PLANEID, csdefine.VISIBLE_RULE_BY_FLAG, csdefine.VISIBLE_RULE_BY_FLASH ,\
		csdefine.VISIBLE_RULE_BY_SHOW_SELF]
	
	def onCacheCompleted( self ):
		NPCObject.onCacheCompleted( self )
		CombatUnit.onCacheCompleted( self )
		if hasattr( self, "radius" ) and self.radius > 0.0:
			self.trapID = self.addTrapExt(self.radius, self.onTransport )

	def filterCreator( self ):
		"""
		template method.
		创建entity的filter模块
		"""
		return BigWorld.DumbFilter()

	def enterWorld( self ) :
		"""
		it will be called, when character enter world
		"""
		#  初始化模型相关
 		NPCObject.enterWorld( self )

	def leaveWorld( self ):
		"""
		it will be called, when the entity leaves the world
		"""
		NPCObject.leaveWorld( self )
		self.entityList = []
		try:
			self.delTrap( self.trapID )
		except:
			pass

	def createModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		template method.
		创建模型
		继承 NPCObject.createModel
		"""
		# 因为一些摆摊限制也用到这个entity.且该entity是不可见的,所以应该屏蔽此种entity的模型
		if len( self.modelNumber ) == 0: return
		# 模型可以绑定相应的光效
		rds.npcModel.createDynamicModelBG( self.modelNumber,  Functor( self.__onModelLoad, event ) )
		self.filter = BigWorld.AvatarFilter()

	def __onModelLoad( self, event, pyModel ):
		if not self.inWorld : return  # 如果已不在视野则过滤
		if pyModel is None:
			return
		self.setModel( pyModel, event )
		am = BigWorld.ActionMatcher( self )    #设置模型am
		self.model.motors = ( am, )
		self.model.scale = ( self.modelScale, self.modelScale, self.modelScale )

	def set_modelScale( self, oldScale ):
		"""
		这里重载了NPCObject的set_modelScale方法，将缩放模型倍率的速度改为0，即瞬时变大。
		"""
		model = self.getModel()
		if model is None: return
		rds.effectMgr.scaleModel( model, ( self.modelScale, self.modelScale, self.modelScale ), 0 )

	def onTransport( self, entitiesInTrap ):
		"""
		进出陷阱回调
		"""
		for entity in entitiesInTrap:
			if entity in self.entityList:
				continue
			else:
				self.cell.onEnterTrap( entity.id )

		for entity in self.entityList:
			if entity in entitiesInTrap:
				continue
			else:
				self.cell.onLeaveTrap( entity.id )

		self.entityList = list( entitiesInTrap )
