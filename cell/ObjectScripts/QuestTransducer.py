# -*- coding: gb18030 -*-
#
# $Id: QuestTransducer.py,v 1.8 2008-05-19 07:26:36 phw Exp $

"""
"""

import BigWorld
from bwdebug import *
from NPCObject import NPCObject
import csdefine

# 全局的属性初始化对应表
g_propsMap = (
				( "visible",					lambda section, key: section[key].asInt ),			# 是否可见
				( "radius",						lambda section, key: section[key].asFloat ),		# 触发半径
			)

START_QUEST = [20101032, 20101039, 20101046, 20101053, 20101060, 20101061, 20101062, 20101063]

class QuestTransducer( NPCObject ):
	"""
	任务传感器。
	用于玩家接近出生点时自动给玩家新手任务。
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

	def remoteEnterTrap( self, selfEntityID, entityID, range, userData ):
		"""
		一个用于中转onEnterTrapExt()消息的函数，此方法会被远程调用（详见onEnterTrapExt()）。
		"""
		selfEntity = BigWorld.entities.get( selfEntityID )
		entity = BigWorld.entities.get( entityID )
		if selfEntity is None or entity is None:
			ERROR_MSG( "remote call fail. selfEntityID = %i(%s), entityID = %i(%s)." % (
					selfEntityID, ("found", "not found")[selfEntity is None], 
					entityID,     ("found", "not found")[entity is None] ) )
			return
		self.onEnterTrapExt( selfEntity, entity, range, userData )

	def onEnterTrapExt( self, selfEntity, entity, range, userData ):
		"""
		This method is associated with the Entity.addProximity method.
		It is called when an entity enters a proximity trap of this entity.

		@param selfEntity:	全局实例自身的entity实例
		@param entity:		The entity that has entered.
		@param range:		The range of the trigger.
		@param userData:	The user data that was passed to Entity.addProximity.
		"""
		if entity.__class__.__name__ != "Role":
			return
		if not entity.isReal():
			INFO_MSG( "Dest entity(%i/%s) not a real entity, I will foreward the call." % ( entity.id, entity.getName() ) )
			# 远程脚本调用
			# 之所以不调用相同onEnterTrapExt()接口，是为了避免onEnterTrapExt()复杂化。
			# 因为如果使用同一个onEnterTrapExt()接口，将需要判断传进来的entity参数是一个entity还是mailbox。
			entity.forwardScriptCall( self.className, "remoteEnterTrap", ( selfEntity.id, entity.id, range, userData ) )
			return
		for questID in self._questFinishList:
			q = self.getQuest( questID )
			if q.query( entity ) == csdefine.QUEST_STATE_FINISH:
				q.complete( entity, 0 )

		for questID in self._questStartList:
			q = self.getQuest( questID )
			if q.query( entity ) == csdefine.QUEST_STATE_NOT_HAVE:
				q.accept( entity )
#				if questID in START_QUEST :	# 接受到第一个新手任务时打开任务界面
#					entity.delayCall( 1, "showQuestLog", questID )

	def gossipWith( self, selfEntity, playerEntity, dlgKey ):
		"""
		与玩家对话；未声明(不能声明)的方法，因此重载此方法的上层如果需要访问自己的私有属性请自己判断self.isReal()。

		@param   selfEntity: 与自己对应的Entity实例，传这个参数是为了方便以后的扩充
		@type    selfEntity: Entity
		@param playerEntity: 说话的玩家
		@type  playerEntity: Entity
		@param       dlgKey: 对话关键字
		@type        dlgKey: str
		@return: 无
		"""
		# 当前啥都不做，重载它是为了禁止底层的调用
		return # the end

# end of QuestTransducer.py
