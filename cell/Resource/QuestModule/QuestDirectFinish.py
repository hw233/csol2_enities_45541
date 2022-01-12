# -*- coding: gb18030 -*-
#
# $Id: QuestDirectFinish.py,v 1.8 2008-08-14 06:14:09 zhangyuxing Exp $


"""
"""

import csdefine
import csstatus
from bwdebug import *
from Quest import Quest

class QuestDirectFinish( Quest ):
	"""
	һ������Ҫ�ӵ�����ģ��,����������ʾʱ��ʾ����Ȼ��δ�Ӹ�����,
	��ֻҪ�ﵽ�������������Ҵﵽ�˽������������,
	�������ʱ���ֵ��ǽ�����Ľ���,���ǽ�������棻

	��ģ����Ҫ����һЩ����Ʒ����Ʒ�������磺��Ȫˮ��ʳ�
	"""
	def __init__( self ):
		Quest.__init__( self )
		self._style = csdefine.QUEST_STYLE_DIRECT_FINISH	# ������ʽ

	def init( self, section ):
		"""
		virtual method.
		@param section: ���������ļ�section
		@type  section: pyDataSection
		"""
		Quest.init( self, section )

	def _query_tasks( self, player ):
		"""
		��ѯ����Ƿ��ɽ����������Ŀ�ꡣ
		@return: ����ֵ������鿴common���QUEST_STATE_*
		@rtype:  UINT8
		"""

		for i in self.tasks_:
			if not self.tasks_[i].isCompletedForNoStart( player ):
				return csdefine.QUEST_STATE_NOT_FINISH		# ����Ŀ��δ���
		return csdefine.QUEST_STATE_FINISH					# ����Ŀ�������


	def _get_tasksDetail( self, player ):
		"""
		"""
		return [ task.getDetail( player ) for task in self.tasks_.itervalues() ]


	def _complete_tasks( self, player ):
		"""
		"""
		for i in self.tasks_:
			self.tasks_[i].complete( player )


	def gossipDetail( self, playerEntity, issuer = None ):
		"""
		"""
		state = self._query_tasks( playerEntity )
		if state == csdefine.QUEST_STATE_NOT_FINISH:	# ����Ŀ��δ���
			playerEntity.sendQuestRewards( self._id, self.getRewardsDetail( playerEntity ) )
			playerEntity.sendObjectiveDetail( self._id, self._get_tasksDetail( playerEntity ) )
			self.gossipIncomplete( playerEntity, issuer )
		elif state == csdefine.QUEST_STATE_FINISH:		# ����Ŀ�������
			self.gossipPrecomplete( playerEntity, issuer )
		else:
			assert "UNKNOWN ERROR!!!"


	def gossipPrecomplete( self, playerEntity, issuer ):
		"""
		����Ŀ������ɶ԰�
		"""
		if issuer:	targetID = issuer.id
		else:		targetID = 0
		playerEntity.sendQuestRewards( self._id, self.getRewardsDetail( playerEntity ) )
		playerEntity.sendObjectiveDetail( self._id, self._get_tasksDetail( playerEntity ) )

		playerEntity.sendQuestSubmitBlank( self._id, self.getSubmitDetail( playerEntity ) )
		if len( self._msg_precomplete ):
			msg = self._msg_precomplete
		else:
			msg = self._msg_log_detail
		playerEntity.sendQuestPrecomplete( self._id, self._title, self._level, msg, targetID )


	def query( self, playerEntity ):
		"""
		"""
		tempState = Quest.query( self, playerEntity)

		if tempState == csdefine.QUEST_STATE_COMPLETE:
			return csdefine.QUEST_STATE_COMPLETE

		elif tempState == csdefine.QUEST_STATE_NOT_ALLOW:
			return csdefine.QUEST_STATE_NOT_ALLOW

		else:
			return csdefine.QUEST_STATE_DIRECT_FINISH


	def complete( self, player, rewardIndex, codeStr = "" ):
		"""
		virtual method.
		������

		@param player: instance of Role Entity
		@type  player: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		#player.setTemp( "questKitTote", kitTote )
		#player.setTemp( "questOrder", order )
		self.setDecodeTemp( player, codeStr )
		player.setTemp( "questTeam", True)

		if not self.query( player ) == csdefine.QUEST_STATE_DIRECT_FINISH:
			#player.removeTemp( "questKitTote" )
			#player.removeTemp( "questOrder" )
			self.removeDecodeTemp( player , codeStr)
			player.removeTemp( "questTeam" )
			return False

		if not self._isTasksCompleted( player):
			#player.removeTemp( "questKitTote" )
			#player.removeTemp( "questOrder" )
			self.removeDecodeTemp( player, codeStr )
			player.removeTemp( "questTeam" )
			return False

		player.setTemp( "RewardItemChoose" , rewardIndex )
		if not self.reward_( player, rewardIndex ):
			player.removeTemp( "RewardItemChoose" )
			#player.removeTemp( "questKitTote" )
			#player.removeTemp( "questOrder" )
			self.removeDecodeTemp( player, codeStr )
			player.removeTemp( "questTeam" )
			return False
		if not self.repeatable_:				# ֻ���治���ظ���ɵ�����
			player.recordQuestLog( self._id )	# ��¼������־

		# after complete
		for e in self.afterComplete_:
			e.do( player )

		self._complete_tasks( player )
		player.questFinishQuest( self._id )
		player.client.onQuestLogRemove( 0, False ) #��������֪ͨ�ͻ��˸�����ΧNPC

		player.removeTemp( "RewardItemChoose" )
		#player.removeTemp( "questKitTote" )
		#player.removeTemp( "questOrder" )
		self.removeDecodeTemp( player, codeStr )
		player.removeTemp( "questTeam" )
		player.statusMessage( csstatus.ROLE_QUEST_COMPLETE, self._title )

		return True


	def _isTasksCompleted( self, playerEntity ):
		"""
		"""
		tasks = self.newTasks_( playerEntity )
		return tasks.isCompletedForNoStart( playerEntity )



#
# $Log: not supported by cvs2svn $
# Revision 1.7  2008/08/07 08:56:20  zhangyuxing
# �޸������ύ �����Ĵ���ʹ���ַ�����Ϊ����Ŀ����Ҫ���ݣ�������Ŀ��
# ���н�����
#
# Revision 1.6  2008/07/31 09:23:49  zhangyuxing
# �޸�һ����������
#
# Revision 1.5  2008/07/28 01:10:42  zhangyuxing
# �����������֪ͨ
#
# Revision 1.4  2008/01/30 02:50:25  zhangyuxing
# ���ӣ���ֱ�ӿɽ��������������ıȽ϶����� ��������Ӧ��һЩ����
#
# Revision 1.3  2008/01/11 06:50:51  zhangyuxing
# ����������ʽ self._style
#
# Revision 1.2  2007/12/04 03:04:21  zhangyuxing
# �������Ŀ�� tasks_ ���ݴ洢��ʽ���б��Ϊ �ֵ�,������Ӧ�ķ��ʷ�ʽҲ��
# �ı�
#
# Revision 1.1  2007/11/02 03:57:27  phw
# no message
#
#