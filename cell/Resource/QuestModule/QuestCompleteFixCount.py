# -*- coding: gb18030 -*-
#
# $Id: QuestFixedLoop.py,v 1.7 2008-08-07 08:56:36 zhangyuxing Exp $


"""
"""

from bwdebug import *
from Quest import Quest
import csdefine


class QuestCompleteFixCount( Quest ):
	"""
	ÿ��ֻ�����ָ������������
	"""
	def __init__( self ):
		Quest.__init__( self )
		self.repeatable_ = 1	# �����͵�����ǿ���������ظ��ӣ������û��������
		self._finish_count = 1	# ÿ������ܽӼ��Σ�Ĭ��Ϊ1��
		self._style = csdefine.QUEST_STYLE_FIXED_LOOP	#������ʽ


	def init( self, section ):
		"""
		virtual method.
		@param section: ���������ļ�section
		@type  section: pyDataSection
		"""
		Quest.init( self, section )
		self.repeatable_ = 1	# �����͵�����ǿ���������ظ��ӣ������û��������
		self._finish_count = section.readInt( "repeat_upper_limit" )

	def checkRequirement( self, player ):
		"""
		virtual method.
		�ж���ҵ������Ƿ��㹻�ӵ�ǰ����
		@return: ����ﲻ���������Ҫ���򷵻�False��
		@rtype:  BOOL
		"""
		lpLog = player.getLoopQuestLog( self.getID(), True )
		if not lpLog.checkStartTime():
			# �����������뵱ǰʱ�䲻��ͬһ�죬Ҳ�ͱ�ʾ��Ҫ��������״̬
			lpLog.reset()
		if lpLog.getDegree() >= self._finish_count:
			# ���������������࣬�������ٽ�
			return False
		return Quest.checkRequirement( self, player )


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
		return False

