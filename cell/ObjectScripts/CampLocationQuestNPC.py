# -*- coding: gb18030 -*-

import random
import BigWorld
import csdefine
import csconst
from bwdebug import *

from NPC import NPC

RANDOM_AMOUNT = 5

class CampLocationQuestNPC( NPC ):
	"""
	��Ӫ�ճ����񷢲�NPC
	��Ӫ�ճ����������ƣ����ݵ�ǰ��Ӫ�ȷ��N����Ҫ�ճ���������������ճ����������M�����������������ҿɽӵ��ճ�����CSOL-1774
	"""
	def __init__( self ):
		NPC.__init__( self )
		self.hasFiltrated = False			# �Ƿ��������Ӫ�ճ�����
		self._questStartList_record = set()

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		��ʼ���Լ���entity������
		"""
		NPC.initEntity( self, selfEntity )
		BigWorld.globalData["CampMgr"].addDailyQuestNpcBases( selfEntity.base )
		
	def addStartQuest( self, questID ):
		"""
		virtual method.
		����һ�����񵽿�ʼ�б���
		"""
		self._questStartList.add( questID )
		self._questStartList_record.add( questID )
	
	def embedQuests( self, selfEntity, player ):
		"""
		Ƕ��ָ��������п�����ʾ������
		"""
		if not self.hasFiltrated:
			self.hasFiltrated = True
			self.filtrateDailyQuest( selfEntity )
		NPC.embedQuests( self, selfEntity, player )

	def questStatus( self, selfEntity, playerEntity ):
		"""
		��ѯһ����Ϸ�������������������ҵ�״̬��״̬��ͨ���ص����ظ�client���Ӧ��GameObject��

		@param   selfEntity: ���Լ���Ӧ��Entityʵ���������������Ϊ�˷����Ժ������
		@type    selfEntity: Entity
		@param playerEntity: ���
		@type  playerEntity: Entity
		@return: ��
		"""
		if not self.hasFiltrated:
			self.hasFiltrated = True
			self.filtrateDailyQuest( selfEntity )
		NPC.questStatus( self, selfEntity, playerEntity )
		
		
	def filtrateDailyQuest( self, selfEntity ):
		"""
		��Ӫ�ճ�����ˢ�£���Ҫ�ճ�����һ���ڿ�ʼ�����б��У������Ǳ�Ҫ�ճ���������������ӵ���ʼ�����б��У�����δ��������Ƴ���
		���ȷ��Ϊ��Ҫ�ճ������ж����õĽű�ΪQTRCampActivityCondition��requirement�����ͨ��˵���������뵱ǰ��Ӫ�������ƥ��,Ϊ��Ҫ����
		�����Ӫ�ճ�������붼��һ���������͵�requirement��
		"""
		self._questStartList = self._questStartList_record.copy()			# �Ȼָ�ԭʼ����
		removeQuests = []
		tempQuestList = []
		
		# ���û����Ӫ�����������Ӫ�ճ������NPC�Ŀ�ʼ�����б����Ƴ�
		if not BigWorld.globalData.has_key( "CampActivityCondition" ):
			for id in self._questStartList:
				quest = self.getQuest( id )
				if quest.getType() == csdefine.QUEST_TYPE_CAMP_DAILY:
					removeQuests.append( id )
			for i in removeQuests:
				self._questStartList.remove( i )
		
		# ����ˢ���ճ�����
		else:
			activitySpace = BigWorld.globalData["CampActivityCondition"][0]
			for id in self._questStartList:
				quest = self.getQuest( id )
				if quest.getType() == csdefine.QUEST_TYPE_CAMP_DAILY:		# ֻ���ճ�����Ҫ�����·������ж�
					passed = False
					for requirement in quest.requirements_:
						if requirement.__class__.__name__ == "QTRCampActivityCondition" and requirement.query( None ) and requirement._activityType != "":		# ��Ҫ�ճ����񣬲���
							passed = True
							break
						
						elif requirement.__class__.__name__ == "QTRCampActivityCondition" and requirement._spaceName in activitySpace: # �Ǳ�Ҫ�ճ����񣬵����ǿ�������ճ�����ͼƥ�䣬ֻ�ǻ���Ͳ�ƥ�䣩������
							tempQuestList.append( id )
							break
					
					if not passed:
						removeQuests.append( id )
			
			# ���Ƴ����зǱ�Ҫ�ճ�����
			for i in removeQuests:
				self._questStartList.remove( i )
				
			# �Դ����ճ�����������
			if len( tempQuestList ) >= RANDOM_AMOUNT:
				for i in random.sample( tempQuestList, RANDOM_AMOUNT ):
					self._questStartList.add( i )
			else:
				for i in tempQuestList:
					self._questStartList.add( i )
			
		for role in selfEntity.entitiesInRangeExt( csconst.ROLE_AOI_RADIUS, "Role", selfEntity.position ):
			self.questStatus( selfEntity, role )
		
		DEBUG_MSG( "Camp NPC refresh daily quest. className: %s" % selfEntity.className )
				