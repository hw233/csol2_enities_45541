# -*- coding: gb18030 -*-
#

import BigWorld
import csdefine
import csconst
import items
import ECBExtend
from QuestBox import QuestBox

class QuestBoxCampActivity( QuestBox ):
	"""
	��Ӫ����ӣ�ֻ����Ӫ����������ڵ�ͼ�������Ӳſ�ѡ��
	"""
	def taskStatus( self, selfEntity, playerEntity ):
		"""
		�ж���Һ����ӵ�����״̬
		
		playerEntity.clientEntity( selfEntity.id ).onTaskStatus�� state )
		state == True :  ��ʾ��������״̬�������������ӿ��Ա�ѡ��
		����: û��������״̬�����ܱ�ѡ��
		""" 
		# �����жϸ�entity�Ƿ�Ϊreal����������queryTemp()һ��Ĵ��뽫������ȷִ�С�
		if not selfEntity.isReal():
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( 0 )
			return
			
		if len( self.questData ) <= 0:
			if self.spellID <= 0:
				playerEntity.clientEntity( selfEntity.id ).onTaskStatus( 0 )
			else:
				playerEntity.clientEntity( selfEntity.id ).onTaskStatus( selfEntity.queryTemp( "quest_box_destroyed", 0 ) == 0 )
			return
			
		findQuest = False
		for id in self.questData.keys():
			quest = self.getQuest( id )
			if quest != None:
				findQuest = True
				break
		if not findQuest:
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( False )
			return

		if selfEntity.queryTemp( "quest_box_destroyed", 0 ) != 0:	# ������0��ʾ�Ѿ����������ˣ��ȴ�ɾ����
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( False )
			return
			
		# ֻ����Ӫ����������ڵ�ͼ�����ſ���ѡȡ����
		if not BigWorld.globalData.has_key( "CampActivityCondition" ):
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( False )
			return
		if playerEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) not in BigWorld.globalData["CampActivityCondition"][0]:
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( False )
			return

		indexTaskState = False
		for questID, taskIndex in self.questData.iteritems():
			if not playerEntity.taskIsCompleted( questID, taskIndex ):
				indexTaskState = True
				break
		playerEntity.clientEntity( selfEntity.id ).onTaskStatus( indexTaskState )