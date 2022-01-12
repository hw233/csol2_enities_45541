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
		
	def collectStatus( self, srcEntityID ):
		"""
		Exposed method
		@param srcEntityID: �����ߵ�ID
		@type  srcEntityID: OBJECT_ID

		�������ӽ��뵽ĳ��ҵ���Ұ���ɼ��������������״̬
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
		@param srcEntityID: �����ߵ�ID
		@type  srcEntityID: OBJECT_ID
		@param index: ��Ʒindex
		@type  index: INT8
		
		ʰȡ�ɼ���Ʒ�ص�
		"""
		try:
			playerEntity = BigWorld.entities[srcEntityID]
		except KeyError:
			INFO_MSG( "entity %i not exist in world" % srcEntityID )
			return
		if playerEntity.isReal():
			self.getScript().onPickUpItemByIndex( self, playerEntity, index )
		else:
			playerEntity.pickUpStatusForward( self )	#���ǵ����Ӻ���ҿ��ܲ���һ��cell��

# CollectPoint.py
