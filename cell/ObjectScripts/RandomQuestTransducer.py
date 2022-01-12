# -*- coding: gb18030 -*-

"""
"""

import BigWorld
from bwdebug import *
from NPCObject import NPCObject
import csdefine
from QuestTransducer import QuestTransducer
import random


class RandomQuestTransducer( QuestTransducer ):
	"""
	任务传感器。
	用于玩家接近出生点时自动给玩家任务。
	"""
	def __init__( self ):
		"""
		初始化
		"""
		QuestTransducer.__init__( self )

	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		根据给定的section，初始化（读取）entity属性。
		注：只有在createEntity()时需要把值自动对entity进行初始化时才有必要放到此函数初始化，
		也就是说，这里初始化的所有属性都必须是在相应的.def中声明过的。

		@param section: PyDataSection, 根据一定的格式存储了entity属性的section
		"""
		QuestTransducer.onLoadEntityProperties_( self, section )
		
		position = []
		positionSection = section["randomPosition"]
		if positionSection:
			positions = positionSection.readVector3s( "item" )
			for p in positions:
				position.append( p )
		self.setEntityProperty( "randomPosition", position )											# 随机位置
		
		self.setEntityProperty( "triggerInterval",		section.readInt( "triggerInterval") )			# 触发间隔
		self.setEntityProperty( "triggerRate",			section.readFloat( "triggerRate") )				# 触发几率
		
		self.questID = section.readInt( "questID" )														# 任务ID
		
	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		初始化自己的entity的数据
		"""
		# 重载啥事都不做只是禁用底层的处理
		pass

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
		quest = self.getQuest( self.questID )
		if quest and quest.query( entity ) == csdefine.QUEST_STATE_NOT_HAVE:
			entity.client.showQuestTrapTip( selfEntity.id )# 触发陷阱后弹出提示信息
			entity.setTemp("LeaveQuestTrapError",selfEntity.id) #增加临时标记 标记玩家离开陷进异常 
			
	def onTipClicked( self, entity ):
		"""
		玩家点击触发陷阱闪烁提示的处理
		@param entity:		The entity that has clicked the tip.
		"""
		quest = self.getQuest( self.questID )
		if quest and quest.query( entity ) == csdefine.QUEST_STATE_NOT_HAVE:
			quest.gossipDetail( entity, None )										# 弹出任务接取界面

	def onLeaveTrapExt( self, selfEntity, entity, range, userData ):
		"""
		玩家离开陷阱时的处理，如关闭提示信息
		@param selfEntity:	全局实例自身的entity实例
		@param entity:		The entity that has entered.
		@param range:		The range of the trigger.
		@param userData:	The user data that was passed to Entity.addProximity.
		"""
		if entity.__class__.__name__ != "Role":
			return
		if selfEntity.randomPosition :
			selfEntity.position = selfEntity.randomPosition[random.randint( 0, len( selfEntity.randomPosition ) -1 ) ]		# 改变陷阱的位置
		try:
			entity.client.hideQuestTrapTip( selfEntity.id )# 关闭提示信息
			entity.removeTemp("LeaveQuestTrapError")
		except:
			ERROR_MSG("Role has onleave RandomQuestTransducer error!")	
		

# end of RandomQuestTransducer.py
