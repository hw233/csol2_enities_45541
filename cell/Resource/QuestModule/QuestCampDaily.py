# -*- coding: gb18030 -*-
#


from bwdebug import *
from Quest import Quest
import BigWorld
import csdefine
import csconst

class QuestCampDaily( Quest ):
	"""
	��������ÿ��ֻ�����һ���ĸ�����������Ӫ�ճ�����
	"""
	def __init__( self ):
		Quest.__init__( self )
		self.repeatable_ = True
		self._type = csdefine.QUEST_TYPE_CAMP_DAILY

	def checkRequirement( self, player ):
		"""
		virtual method.
		�ж���ҵ������Ƿ��㹻�ӵ�ǰ����
		@return: ����ﲻ���������Ҫ���򷵻�False��
		@rtype:  BOOL
		"""
		# �ڵ�����Ӫ�ʱ���ڣ�ֻ�����һ�α�����
		activityTimeRecord = player.query( "CampDailyTimeRecord_%s" % self.getID(), None )
		if activityTimeRecord:
			if BigWorld.globalData.has_key( "CampActivityEndTime" ) and BigWorld.globalData["CampActivityEndTime"] == activityTimeRecord:
				return False
			else:
				player.remove( "CampDailyTimeRecord_%s" % self.getID() )
				
		# ͬ������һ��ֻ����ɹ̶�����
		count = len( player.findQuestByType( csdefine.QUEST_TYPE_CAMP_DAILY ) )
		for i in player.loopQuestLogs:
			quest = player.getQuest( i.getQuestID() )
			if i.checkStartTime() and quest.getType() == csdefine.QUEST_TYPE_CAMP_DAILY:
				count += i.getDegree()
		if count >= csconst.CAMP_DAILY_REPEAT_LIMIT:
			return False
		
		for requirement in self.requirements_:
			if requirement.__class__.__name__ == "QTRCampActivityCondition":		# �������͵����������ж�,���������NPC�ű������⴦��:CampLocationQuestNPC
				continue
			if not requirement.query( player ):
				return False
		return True
		
	def onAccept( self, player, tasks ):
		"""
		"""
		buff = player.findBuffsByBuffID( 22133 )
		if len( buff ) <= 0:
			player.systemCastSpell( csconst.CAMP_ACTIVITY_CHECK_SPELL_ID )			# ���һ�������Ӫ����������buff��Buff_22133
		Quest.onAccept( self, player, tasks )
		
	def complete( self, player, rewardIndex, codeStr = "" ):
		"""
		virtual method.
		������

		@param player: instance of Role Entity
		@type  player: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if Quest.complete( self, player, rewardIndex, codeStr ):
			lpLog = player.getLoopQuestLog( self.getID(), True )
			if not lpLog.checkStartTime():
				# �����������뵱ǰʱ�䲻��ͬһ�죬Ҳ�ͱ�ʾ��Ҫ��������״̬
				lpLog.reset()
			lpLog.incrDegree()
			if BigWorld.globalData.has_key( "CampActivityEndTime" ):
				player.set( "CampDailyTimeRecord_%s" % self.getID(), BigWorld.globalData["CampActivityEndTime"] )			# ��¼��Ӫ�����ʱ��
			return True
		return False
