# -*- coding: gb18030 -*-
# ������� by ���� 12:07 2010-11-8


import BigWorld
from QuestDart import QuestDart
import csstatus
import csdefine

class QuestTongDart( QuestDart ):


	def accept( self, player ):
		"""
		virtual method.
		���������������ʧ�����򷵻�False��������ұ������˷Ų���������ߣ���

		@param     player: instance of Role Entity
		@type      player: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		QuestDart.accept( self, player )
		"""			CSOL-2118��������һ���ڰ���Ա�ܵĽ�ȡ����
		tongMB = player.tong_getSelfTongEntity()
		
		if tongMB is None:
			player.statusMessage( csstatus.TONG_DART_NOT_EXIST )
			return
		
		tongMB.queryDartCount( player.base, self.getID() )
		"""

	def onAccept( self, player, tasks ):
		"""
		virtual method.
		ִ������ʵ�ʴ���
		"""
		QuestDart.onAccept( self, player, tasks )
		
		#tongMB = player.tong_getSelfTongEntity()
		
		#tongMB.addDartCount()

	def checkRequirement( self, player ):
		"""
		virtual method.
		�ж���ҵ������Ƿ��㹻�ӵ�ǰ����
		@return: ����ﲻ���������Ҫ���򷵻�False��
		@rtype:  BOOL
		"""
		if player.tong_dbID == 0 or not player.tongDartQuestIsOpen:		# ����û�����ھͲ��ý�
			return False
		return QuestDart.checkRequirement( self, player )
