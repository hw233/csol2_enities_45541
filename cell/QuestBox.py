# -*- coding: gb18030 -*-
#
# $Id: QuestBox.py,v 1.6 2008-01-08 06:25:59 yangkai Exp $

from NPCObject import NPCObject
from interface.CombatUnit import CombatUnit
import BigWorld
import csdefine
import ECBExtend
from bwdebug import *
import csstatus
import Const

class QuestBox( NPCObject, CombatUnit ) :
	"""
	"""

	def __init__( self ) :
		NPCObject.__init__( self )
		CombatUnit.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_QUEST_BOX )

	def taskStatus( self, srcEntityID ):
		"""
		Exposed method.
		@param srcEntityID: 调用者的ID
		@type  srcEntityID: OBJECT_ID

		任务箱子进入到某玩家的视野，任务箱子向服务器乞求它于这个玩家的关系
		"""
		try:
			playerEntity = BigWorld.entities.get( srcEntityID )
		except KeyError:
			INFO_MSG( "entity %i not exist in world" % srcEntityID )
			return

		if playerEntity.isReal():
			self.getScript().taskStatus( self, playerEntity )
		else:
			playerEntity.taskStatusForward( self )	#考虑到箱子和玩家可能不在一个cell中

	def onIncreaseQuestTaskState( self, srcEntityID ):
		"""
		define method.   (只在cell上被调用)
		通知该任务箱子中某个索引位置上的任务目标已经完成了
		@param srcEntityID: 调用者的ID
		@type  srcEntityID: OBJECT_ID
		@param index: 要设定完成的任务目标的索引位置
		@type  index: INT16
		"""
		try:
			playerEntity = BigWorld.entities[srcEntityID]
		except KeyError:
			INFO_MSG( "entity %i not exist in world" % srcEntityID )
			return

		if playerEntity.isReal():
			self.getScript().onIncreaseQuestTaskState( self, playerEntity )
		else:
			playerEntity.onIncreaseQuestTaskStateForward( self )	#考虑到箱子和玩家可能不在一个cell中

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
		self.removeTemp( "questMonsterCount" )	# 刷新后此值要清除
		
	def entityDead( self ):
		"""
		Define method.
		QuestBox召唤出来的怪物死亡了，通知这里将数量-1
		直到都死光才刷出新的QuestBox（这里的刷出就是指在客户端显示）
		"""
		self.setTemp( "gossipingID", 0 )
		self.getScript().entityDead( self )


	def onItemsArrived( self, target, itemList ):
		"""
		define method
		"""
		id = self.queryTemp("gossipingID",0) 
		if id != 0 and BigWorld.entities.has_key( id ):
			target.client.onStatusMessage( csstatus.QUEST_BOX_CANT_OPERATE, "" )
			return
		self.setTemp( "gossipingID", target.id )
		self.itemBox = []
		for iItem in itemList:
			self.itemBox.append( {'order' :len( self.itemBox ), 'item' : iItem })
		
		target.clientEntity( self.id ).receiveQuestItems( self.itemBox )

		if len( self.itemBox ) == 0:
			self.onReceiveSpell( target, None )
			target.client.onStatusMessage( csstatus.QUEST_BOX_NOT_USEFUL_FOR_YOU, "" )

	def pickQuestItem( self, srcEntityID, index ):
		"""
		Exposed method
		拾取战利品
		"""
		
		player = BigWorld.entities.get( srcEntityID, None )
		if player is None:
			return
		
		if len( self.itemBox ) != 0:
			tempItem = None
			for i in self.itemBox:
				if i['order'] == index:
					tempItem = i['item']
			
			if tempItem is None:
				ERROR_MSG( "index: %i does has quest Item" % index )
				print  "--->>>>", self.itemBox
				target.client.onStatusMessage( csstatus.QUEST_BOX_NOT_EXIST, "" )
				return
			player.requestAddQuestItem( self.id, index, tempItem )
	
	
	def receiveQuestItemPickedCB( self, playerID, index, isPicked ):
		"""
		define method
		"""
		if isPicked:															#物品被拾取
			BigWorld.entities[playerID].clientEntity( self.id ).onBoxQuestItemRemove( index )
			for i in self.itemBox:
				if i['order'] == index:
					self.itemBox.remove( i )
					break
		else:
			BigWorld.entities[playerID].client.onStatusMessage( csstatus.QUEST_BOX_BAG_FULL, "" )
		
		
		if len( self.itemBox ) == 0:
			self.onReceiveSpell( BigWorld.entities[playerID], None )
			self.setTemp( "gossiping", False )

	def abandonBoxQuestItems( self, srcEntityID ):
		"""
		Exposed method
		"""
		self.setTemp( "gossipingID", 0 )
		self.itemBox = []
	
	def onWitnessed( self, isWitnessed ):
		"""
		see also Python Cell API::Entity::onWitnessed()
		@param isWitnessed: A boolean indicating whether or not the entity is now witnessed;
		@type  isWitnessed: bool
		"""
		if self.hasFlag( csdefine.ENTITY_FLAG_MODEL_COLLIDE ):
			self.spellTarget( Const.ENTITY_CREATE_TRIGGER_SKILL_ID , self.id )
	
# QuestBox.py
