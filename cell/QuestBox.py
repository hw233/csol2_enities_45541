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
		@param srcEntityID: �����ߵ�ID
		@type  srcEntityID: OBJECT_ID

		�������ӽ��뵽ĳ��ҵ���Ұ������������������������������ҵĹ�ϵ
		"""
		try:
			playerEntity = BigWorld.entities.get( srcEntityID )
		except KeyError:
			INFO_MSG( "entity %i not exist in world" % srcEntityID )
			return

		if playerEntity.isReal():
			self.getScript().taskStatus( self, playerEntity )
		else:
			playerEntity.taskStatusForward( self )	#���ǵ����Ӻ���ҿ��ܲ���һ��cell��

	def onIncreaseQuestTaskState( self, srcEntityID ):
		"""
		define method.   (ֻ��cell�ϱ�����)
		֪ͨ������������ĳ������λ���ϵ�����Ŀ���Ѿ������
		@param srcEntityID: �����ߵ�ID
		@type  srcEntityID: OBJECT_ID
		@param index: Ҫ�趨��ɵ�����Ŀ�������λ��
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
			playerEntity.onIncreaseQuestTaskStateForward( self )	#���ǵ����Ӻ���ҿ��ܲ���һ��cell��

	def onCorpseDelayTimer( self, controllerID, userData ):
		"""
		MONSTER_CORPSE_DELAY_TIMER_CBID��callback������
		"""
		self.getScript().corpseDelay( self )

	def onReceiveSpell( self, caster, spell ):
		"""
		��������Ļص�����ĳЩ���⼼�ܵ���

		@param spell: ����ʵ��
		"""
	
		self.getScript().onReceiveSpell( self, caster, spell )

	def onRedivious( self, controllerID, userData ):
		"""
		ƥ��ECBExtend.QUEST_BOX_REDIVIOUS_TIMER_CBID
		"""
		self.removeFlag( 0 )	# ����ר�ã����ܻ���FLAG_*��ͻ�������û������ԭ��Ӧ��û������
		self.removeFlag( 1 )	# ����ڲ����صĳ��������Ϊ��ʹ�ͻ����ܵõ�����
		self.removeTemp( "quest_box_destroyed" )
		self.removeTemp( "questMonsterCount" )	# ˢ�º��ֵҪ���
		
	def entityDead( self ):
		"""
		Define method.
		QuestBox�ٻ������Ĺ��������ˣ�֪ͨ���ｫ����-1
		ֱ���������ˢ���µ�QuestBox�������ˢ������ָ�ڿͻ�����ʾ��
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
		ʰȡս��Ʒ
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
		if isPicked:															#��Ʒ��ʰȡ
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
