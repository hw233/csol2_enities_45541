# -*- coding: gb18030 -*-
#
# �����������
#

"""
"""

from bwdebug import *
from QuestFixedLoop import QuestFixedLoop
import csdefine

MERCHANT_TITLE	= 23		#���̳ƺ�

class QuestMerchant( QuestFixedLoop ):
	"""
	�����������
	"""
	def __init__( self ):
		QuestFixedLoop.__init__( self )
		self._type =  csdefine.QUEST_TYPE_RUN_MERCHANT

	def accept( self, player ):
		"""
		virtual method.
		���������������ʧ�����򷵻�False��������ұ������˷Ų���������ߣ���

		@param     player: instance of Role Entity
		@type      player: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		
		tongMB = player.tong_getSelfTongEntity()
		# ������������������
		lpLog = player.getLoopQuestLog( self.getID(), True )
		count = lpLog.getDegree()

		tongMB.queryMerchantCount( player.base, self.getID(), count )

	def onRemoved( self, player ):
		"""
		"""
		player.removeMerchantQuestFlag()
		#player.removeTitle( MERCHANT_TITLE )

	def checkRequirement( self, player ):
		"""
		virtual method.
		�ж���ҵ������Ƿ��㹻�ӵ�ǰ����
		@return: ����ﲻ���������Ҫ���򷵻�False��
		@rtype:  BOOL
		"""
		return QuestFixedLoop.checkRequirement( self, player ) and not player.isInMerchantQuest()

	def sendQuestLog( self, player, questLog ):
		"""
		"""
		player.showMerchantQuestFlag()
		QuestFixedLoop.sendQuestLog( self, player, questLog )
	

