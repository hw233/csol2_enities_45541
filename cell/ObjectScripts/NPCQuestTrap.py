# -*- coding: gb18030 -*-
#
# $Id:

"""
"""
from bwdebug import *
from NPCObject import NPCObject
import csstatus

# 全局的属性初始化对应表
g_propsMap = (
				( "visible",					lambda section, key: section[key].asInt ),			# 是否可见
				( "radius",						lambda section, key: section[key].asFloat ),		# 触发半径
			)

class NPCQuestTrap( NPCObject ):
	"""
	任务触发器
	"""
	def __init__( self ):
		"""
		初始化
		"""
		NPCObject.__init__( self )

	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		根据给定的section，初始化（读取）entity属性。
		注：只有在createEntity()时需要把值自动对entity进行初始化时才有必要放到此函数初始化，
		也就是说，这里初始化的所有属性都必须是在相应的.def中声明过的。

		@param section: PyDataSection, 根据一定的格式存储了entity属性的section
		"""
		NPCObject.onLoadEntityProperties_( self, section )
		self.setEntityProperty( "visible",		section["visible"].asInt )			# 是否可见
		self.setEntityProperty( "radius",		section["radius"].asFloat )			# 触发半径

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		初始化自己的entity的数据
		"""
		# 重载啥事都不做只是禁用底层的处理
		pass

	def onEnterTrapExt( self, selfEntity , entity, range, userData ):
		"""
		This method is associated with the Entity.addProximity method.
		It is called when an entity enters a proximity trap of this entity.

		@param entity:		The entity that has entered.
		@param range:		The range of the trigger.
		@param userData:	The user data that was passed to Entity.addProximity.
		"""
		if entity.__class__.__name__ != "Role" or not entity.isReal():
			return

		#self.listUsableQuests( selfEntity, entity, "Talk", False )

	def onLeaveTrapExt( self, selfEntity , entity, range, userData ):
		"""
		This method is associated with the Entity.addProximity method.
		It is called when an entity leaves a proximity trap of this entity.

		@param entity:		The entity that has left.
		@param range:		The range of the trigger.
		@param userData:	The user data that was passed to Entity.addProximity.
		"""
		pass

	def gossipWith( self, selfEntity, player, dlgKey ):
		"""
		@param       dlgKey: 对话关键字
		@type        dlgKey: string
		@return: 无
		"""
		#self.castQuests( selfEntity, player, dlgKey )
		pass