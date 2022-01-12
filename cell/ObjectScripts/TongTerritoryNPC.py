# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
NPC����
"""

import BigWorld
from bwdebug import *
import csdefine
import csstatus
from NPC import NPC

TONG_TREASURY_MGR = "10111132"				#������Ա

class TongTerritoryNPC( NPC ):
	"""
	������NPC����
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		NPC.__init__( self )

	def gossipWith( self, selfEntity, playerEntity, dlgKey ):
		"""
		����ҶԻ���δ����(��������)�ķ�����������ش˷������ϲ������Ҫ�����Լ���˽���������Լ��ж�self.isReal()��

		@param   selfEntity: ���Լ���Ӧ��Entityʵ���������������Ϊ�˷����Ժ������
		@type    selfEntity: Entity
		@param playerEntity: ˵�������
		@type  playerEntity: Entity
		@param       dlgKey: �Ի��ؼ���
		@type        dlgKey: str
		@return: ��
		"""
		if selfEntity.ownTongDBID > 0 and selfEntity.ownTongDBID != playerEntity.tong_dbID:
			playerEntity.statusMessage( csstatus.TONG_NPC_IS_TARGET_TONG_NPC )
			return
		elif selfEntity.locked:
			playerEntity.statusMessage( csstatus.TONG_NPC_LOCKED )
			return			
		NPC.gossipWith( self, selfEntity, playerEntity, dlgKey )

	def questStatus( self, selfEntity, playerEntity ):
		"""
		��ѯһ����Ϸ�������������������ҵ�״̬��״̬��ͨ���ص����ظ�client���Ӧ��GameObject��

		@param   selfEntity: ���Լ���Ӧ��Entityʵ���������������Ϊ�˷����Ժ������
		@type    selfEntity: Entity
		@param playerEntity: ���
		@type  playerEntity: Entity
		@return: ��
		"""

		level,signID = self.getQuestStateLevel( playerEntity )
		if selfEntity.className == TONG_TREASURY_MGR and level > 500:
			signID = 101
		playerEntity.clientEntity( selfEntity.id ).onQuestStatus( signID )
	
# NPC.py
