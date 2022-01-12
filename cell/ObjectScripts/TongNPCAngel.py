# -*- coding: gb18030 -*-

from bwdebug import *
from NPC import NPC
import csstatus

class TongNPCAngel( NPC ):
	"""
	�������
	"""
	def __init__( self ):
		"""
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
		if selfEntity.ownTongDBID != playerEntity.tong_dbID:
			playerEntity.statusMessage( csstatus.TONG_NPC_IS_TARGET_TONG_NPC )
			return
		elif selfEntity.locked:
			playerEntity.statusMessage( csstatus.TONG_NPC_LOCKED )
			return			
		NPC.gossipWith( self, selfEntity, playerEntity, dlgKey )