# -*- coding: gb18030 -*-
#
# $Id $

"""
��������ģ�� spf
"""

from bwdebug import *
from Quest import *
from QuestDataType import QuestDataType
from QuestRandomRecordType import QuestRandomRecordType
from string import Template
from QuestFixedLoop import QuestFixedLoop
import QTReward
import QTTask
import time
import random
import csdefine
import csstatus
import csconst
import ECBExtend


class QuestRob( QuestFixedLoop ):
	def __init__( self ):
		QuestFixedLoop.__init__( self )
		self._finish_count = 1 #Ĭ��Ϊ1

	def init( self, section ):
		"""
		"""
		QuestFixedLoop.init( self, section )
		self._type = csdefine.QUEST_TYPE_ROB
		self._finish_count = section.readInt( "repeat_upper_limit" )

	def getFaction( self, player, tasks = None ):
		"""
		��ô������ھֵ�����
		"""
		factionID = -1
		if tasks is None:
			tasks = self.newTasks_( player )
		if tasks is None:
			ERROR_MSG( "Faction id should be set into tasks!" )
			return -1
		for task in tasks._tasks.itervalues():
			if task.getType() == csdefine.QUEST_OBJECTIVE_DART_KILL:
				factionID = int( task.str1 )
		if factionID == -1 or factionID == None:
			ERROR_MSG( "Faction id has not been initiate!" )
		if factionID == csconst.FACTION_CP:
			factionID = csconst.FACTION_XL
		elif factionID == csconst.FACTION_XL:
			factionID = csconst.FACTION_CP
		return factionID

	def onAccept( self, player, tasks ):
		"""
		virtual method.
		ִ������ʵ�ʴ���
		"""

		lpLog = player.getLoopQuestLog( self._id, True )
		if lpLog:
			lpLog.incrDegree()
		Quest.onAccept( self, player, tasks )

	def abandoned( self, player, flags ):
		"""
		virtual method.
		��������ֻ���ھ������������
		@param player: instance of Role Entity
		@type  player: Entity
		@return: None
		"""
		#Ϊ�˱��ڲ�����ע�͵�
		if  flags != csdefine.QUEST_REMOVE_FLAG_NPC_CHOOSE:
			player.statusMessage( csstatus.ROLE_QUEST_ROB_ABANDONED_FAILED )
			return False
		player.statusMessage( csstatus.ROLE_QUEST_ROB_ABANDONED )
		tasks = self.newTasks_( player )
		factionID = self.getFaction( player, tasks )
		player.client.updateTitlesDartRob( factionID )
		return QuestFixedLoop.abandoned( self, player, flags )

	def onRemoved( self, player ):
		"""
		������ȥʱ֪ͨ���ȥ��ͷ�����
		"""
		#player.removeFlag( csdefine.ROLE_FLAG_ROBBING )

		if player.hasFlag( csdefine.ROLE_FLAG_CP_ROBBING ):
			player.removeFlag( csdefine.ROLE_FLAG_CP_ROBBING )
		else:
			player.removeFlag( csdefine.ROLE_FLAG_XL_ROBBING )

		player.cancel( player.queryTemp( "robDart_timerID", 0 ) )
		player.removeTemp( "robDart_timerID" )
		player.remove( "RobEndTime" )


	def query( self, player ):
		"""
		��ѯ��Ҷ�ĳһ������Ľ���״̬��
		����ר�ŶԽ������񵥶�������Ϊ�����������������һ��
		�߻�Ҫ����������ɱ�ڳ��󣬼�ʱ�涨ʱ���ڲ�������Ҳ�����
		@return: ����ֵ������鿴common���QUEST_STATE_*
		@rtype:  UINT8
		"""
		questID = self.getID()
		if player.questIsCompleted( questID ):
			return csdefine.QUEST_STATE_COMPLETE						# ������������
		if player.has_quest( questID ):
			# �ѽ��˸�����
			if player.questTaskIsCompleted( questID ):
				return csdefine.QUEST_STATE_FINISH						# ����Ŀ�������
			elif self.isCompleted( player ):
				return csdefine.QUEST_STATE_FINISH
			else:
				return csdefine.QUEST_STATE_NOT_FINISH					# ����Ŀ��δ���
		else:
			# û�нӸ�����
			if self.checkRequirement( player ):
				return csdefine.QUEST_STATE_NOT_HAVE					# ���Խӵ���δ�Ӹ�����
			else:
				return csdefine.QUEST_STATE_NOT_ALLOW					# ���������Ӹ�����

	def sendQuestLog( self, player, questLog ):
		"""
		"""
		QuestFixedLoop.sendQuestLog( self, player, questLog )
		self.addPlayerRobFlag( player )

	def addPlayerRobFlag( self, player ):
		"""
		"""
		factionID = self.getFaction( player )
		player.client.updateTitlesDartRob( factionID )
		if not self.isFailed( player ):
			if factionID == csconst.FACTION_CP:
				player.addFlag( csdefine.ROLE_FLAG_CP_ROBBING )
			else:
				player.addFlag( csdefine.ROLE_FLAG_XL_ROBBING )
		t = player.query("RobEndTime", 0) - time.time()
		
		# ����������ߵ�ʱ����ܽ��ڵ�ʱ���Ѿ���ȥ�ˣ����ǽ��ڵ�flag�����������, ����ɾ����־�Ķ�ʱ������ʲôʱ��Ҫ������
		if t < 1:
			t = 1
			
		player.setTemp( "robDart_timerID", player.addTimer( t, 0, ECBExtend.REMOVE_ROB_FLAG ) )

	def isCompleted( self, player ):
		"""
		�Ƿ���ɽ�������,���ݲ߻���Ҫ��ֻҪ�ڹ涨ʱ���ھ�ɱ���ڳ��������
		��ɱ�ڳ���ʱ�涨ʱ���ڲ�������Ҳ������ʧ��
		"""
		for t in self.tasks_.itervalues():
			if t.getType() == csdefine.QUEST_OBJECTIVE_DART_KILL:
				index = t.index
				return player.questsTable[self.getID()]._tasks[index].isCompleted( player )
		return False

	def isFailed( self, player ):
		"""
		���������Ƿ��Ѿ�ʧ��
		"""
		failed = False
		for t in self.tasks_.itervalues():
			if t.getType() == csdefine.QUEST_OBJECTIVE_DART_KILL:
				# û��ʧ��
				if player.questsTable[self.getID()]._tasks[t.index].isCompleted( player ):
					return False
			elif t.getType() == csdefine.QUEST_OBJECTIVE_TIME:
				failed = not player.questsTable[self.getID()]._tasks[t.index].isCompleted( player )
		return failed