# -*- coding: gb18030 -*-


import BigWorld
import NPC


class TiShouNPC( NPC.NPC ):
	"""
	"""	
	def __init__( self ):
		"""
		"""
		NPC.NPC.__init__( self )
		
		
	
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
		if dlgKey == "Talk":
			selfEntity.queryTSInfo( playerEntity.id )
		else:
			playerEntity.endGossip( selfEntity )