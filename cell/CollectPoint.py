# -*- coding: gb18030 -*-
#
# $Id: QuestBox.py,v 1.6 2008-01-08 06:25:59 yangkai Exp $

from NPCObject import NPCObject
import BigWorld
import csdefine
import ECBExtend
from bwdebug import *

class CollectPoint( NPCObject ) :
	"""
	"""

	def __init__( self ) :
		NPCObject.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_COLLECT_POINT )
	
	def onCorpseDelayTimer( self, controllerID, userData ):
		"""
		MONSTER_CORPSE_DELAY_TIMER_CBID的callback函数；
		"""
		self.getScript().corpseDelay( self )

	def onReceiveSpell( self, caster, spell ):
		"""
		法术到达的回调，由某些特殊技能调用

		@param spell: 技能实例
		"""
	
		self.getScript().onReceiveSpell( self, caster, spell )

	def onRedivious( self, controllerID, userData ):
		"""
		匹配ECBExtend.QUEST_BOX_REDIVIOUS_TIMER_CBID
		"""
		self.removeFlag( 0 )	# 箱子专用，可能会与FLAG_*冲突，但如果没有特殊原因，应该没有问题
		self.removeFlag( 1 )	# 针对于不隐藏的场景物件，为了使客户端能得到触发
		self.removeTemp( "quest_box_destroyed" )
		
	def collectStatus( self, srcEntityID ):
		"""
		Exposed method
		@param srcEntityID: 调用者的ID
		@type  srcEntityID: OBJECT_ID

		任务箱子进入到某玩家的视野，采集点向服务器申请状态
		"""
		try:
			playerEntity = BigWorld.entities[srcEntityID]
		except KeyError:
			INFO_MSG( "entity %i not exist in world" % srcEntityID )
			return
		self.getScript().collectStatus( self, playerEntity )
			
	def onPickUpItemByIndex( self, srcEntityID, index ):
		"""
		Exposed method
		@param srcEntityID: 调用者的ID
		@type  srcEntityID: OBJECT_ID
		@param index: 物品index
		@type  index: INT8
		
		拾取采集物品回调
		"""
		try:
			playerEntity = BigWorld.entities[srcEntityID]
		except KeyError:
			INFO_MSG( "entity %i not exist in world" % srcEntityID )
			return
		if playerEntity.isReal():
			self.getScript().onPickUpItemByIndex( self, playerEntity, index )
		else:
			playerEntity.pickUpStatusForward( self )	#考虑到箱子和玩家可能不在一个cell中

# CollectPoint.py
