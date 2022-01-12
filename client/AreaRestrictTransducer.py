# -*- coding: gb18030 -*-

# 2008-11-26 gjx&lq

import BigWorld
from bwdebug import *
from NPCObject import NPCObject
from interface.CombatUnit import CombatUnit
from gbref import rds
import csdefine
import Define
from Function import Functor


class AreaRestrictTransducer( NPCObject, CombatUnit ):
	"""
	区域限制触发器；
	作用：对进入或者离开该区域的玩家进行某些操作限制，如摆摊限制，PK限制
	"""
	def __init__( self ):
		NPCObject.__init__( self )
		CombatUnit.__init__( self )

		self.selectable = False		# 不能选中
		self.modelScale = 1.0
		self.visibleRules = [ csdefine.VISIBLE_RULE_BY_PLANEID, csdefine.VISIBLE_RULE_BY_FLAG, csdefine.VISIBLE_RULE_BY_FLASH ,\
		csdefine.VISIBLE_RULE_BY_SHOW_SELF]

	def enterWorld( self ) :
		"""
		it will be called, when character enter world
		"""
		#  初始化模型相关
 		NPCObject.enterWorld( self )

	def createModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		template method.
		创建模型
		继承 NPCObject.createModel
		"""
		# 因为一些摆摊限制也用到这个entity.且该entity是不可见的,所以应该屏蔽此种entity的模型
		if len( self.modelNumber ) == 0: return
		rds.npcModel.createDynamicModelBG( self.modelNumber, Functor( self.__onModelLoad, event ) )
		
	def __onModelLoad( self, event, model):
		"""
		模型加载完毕
		"""
		if model is None:
			return
		self.setModel( model, event )
		self.model.motors = ( )
		self.model.scale = ( self.modelScale, self.modelScale, self.modelScale )

	def set_modelScale( self, oldScale ):
		"""
		这里重载了NPCObject的set_modelScale方法，将缩放模型倍率的速度改为0，即瞬时变大。
		"""
		model = self.getModel()
		if model is None: return
		rds.effectMgr.scaleModel( model, ( self.modelScale, self.modelScale, self.modelScale ), 0 )
