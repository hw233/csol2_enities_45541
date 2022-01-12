# -*- coding: gb18030 -*-

import BigWorld
import csdefine
from bwdebug import *
from Monster import Monster
from QuestBox import QuestBox
import event.EventCenter as ECenter

class MonsterCityWarBase( Monster, QuestBox ):
	"""
	���ս�ݵ�
	"""
	def __init__( self ):
		Monster.__init__( self )
		QuestBox.__init__( self )
		if not self.hasFlag( csdefine.ENTITY_FLAG_QUEST_BOX ):
			self.__canSelect = True
			self.setSelectable( True )

	def refurbishTaskStatus(self):
		"""
		����cell�����Լ�������Ŀ��״̬
		"""
		if self.hasFlag( csdefine.ENTITY_FLAG_QUEST_BOX ):
			self.cell.taskStatus()

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache�������
		"""
		if self.hasFlag( csdefine.ENTITY_FLAG_QUEST_BOX ):
			QuestBox.onCacheCompleted( self )
		else:
			Monster.onCacheCompleted( self )

	def onTaskStatus( self, state ):
		"""
		define method
		"""
		if self.hasFlag( csdefine.ENTITY_FLAG_QUEST_BOX ):
			QuestBox.onTaskStatus( self, state )

	def onTargetFocus( self ):
		"""
		����ƶ����ݵ���
		"""
		if self.hasFlag( csdefine.ENTITY_FLAG_QUEST_BOX ):
			QuestBox.onTargetFocus( self )
		else:
			Monster.onTargetFocus( self )

	def onTargetBlur( self ):
		"""
		���Ӿݵ��ƿ�
		"""
		if self.hasFlag( csdefine.ENTITY_FLAG_QUEST_BOX ):
			QuestBox.onTargetBlur( self )
		else:
			Monster.onTargetBlur( self )

	def set_flags( self, old ):
		"""
		"""
		if self.hasFlag( csdefine.ENTITY_FLAG_QUEST_BOX ):
			QuestBox.set_flags( self, old )
		else:
			Monster.set_flags( self, old )

	def onLoseTarget( self ) :
		"""
		"""
		if self.hasFlag( csdefine.ENTITY_FLAG_QUEST_BOX ):
			QuestBox.onLoseTarget( self )
		else:
			Monster.onLoseTarget( self )

	def queryRelation( self, entity ):
		"""
		��ϵ�ж�
		"""
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		if self.isUseCombatCamp and entity.isUseCombatCamp:
			return Monster.queryRelation( self, entity )
		
		if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			entiyBelong = entity.getCityWarTongBelong( entity.tong_dbID )
			if entity.cityWarFinalBelong == self.belong:
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE

		return csdefine.RELATION_NEUTRALLY

	def abandonBoxQuestItems( self ):
		pass
		
	def set_belong( self, oldValue ):
		ECenter.fireEvent( "EVT_ON_BELONG_CHANGED", self )
		
	def set_energy( self, oldValue ):
		ECenter.fireEvent( "EVT_ON_MONSTER_ENERGY_CHANGED",self )
		
	def set_baseType( self, oldValue ):
		pass