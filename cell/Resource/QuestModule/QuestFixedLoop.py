# -*- coding: gb18030 -*-
#
# $Id: QuestFixedLoop.py,v 1.7 2008-08-07 08:56:36 zhangyuxing Exp $


"""
"""

from bwdebug import *
from Quest import Quest
import csdefine


class QuestFixedLoop( Quest ):
	"""
	ÿ��ֻ�����ָ������������
	"""
	def __init__( self ):
		Quest.__init__( self )
		self.repeatable_ = 1	# �����͵�����ǿ���������ظ��ӣ������û��������
		self._finish_count = 1	# ÿ������ܽӼ��Σ�Ĭ��Ϊ1��
		self._style = csdefine.QUEST_STYLE_FIXED_LOOP	#������ʽ
		self._type = csdefine.QUEST_TYPE_MERCHANT		#�̻�����(��ǰ�������͵����񣬶���Ϊ�̻������Ժ����޸��ڵ���)

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


	def onAccept( self, player, tasks ):
		"""
		virtual method.
		ִ������ʵ�ʴ���
		"""
		Quest.onAccept( self, player, tasks )
		lpLog = player.getLoopQuestLog( self.getID(), True )
		lpLog.incrDegree()	# �ɹ�������֮��͸�����ӵ�����������+1


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
			if lpLog.getDegree() == 0:
				lpLog.incrDegree()
		return False
		
	def getLevel( self, playerEntity = None ):
		"""
		��ȡ����ȼ�
		"""
		if playerEntity is None:
			return Quest.getLevel( self )
		return playerEntity.query( "recordQuestLevel_%i"%self.getID(), playerEntity.level )
		