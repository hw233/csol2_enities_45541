# -*- coding: gb18030 -*-
#

import BigWorld
from Quest import Quest
import csdefine
import csconst

class QuestCampActivity( Quest ):
	"""
	��Ӫ���������
	"""
	def __init__( self ):
		Quest.__init__( self )
		self.repeatable_ = True
		self._type = csdefine.QUEST_TYPE_CAMP_ACTIVITY
		
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
				
		return Quest.checkRequirement( self, player )
				
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
			if BigWorld.globalData.has_key( "CampActivityEndTime" ):
				player.set( "CampDailyTimeRecord_%s" % self.getID(), BigWorld.globalData["CampActivityEndTime"] )			# ��¼��Ӫ�����ʱ��
			return True
		return False
		