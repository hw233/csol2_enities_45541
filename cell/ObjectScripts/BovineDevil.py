# -*- coding: gb18030 -*-
#
# BovineDevil�� 2009-05-27 SongPeifang
#

from WXMonster import WXMonster
import cschannel_msgs
import ShareTexts as ST


class BovineDevil( WXMonster ):
	"""
	ţħ���ű��ļ�
	"""
	def __init__( self ):
		"""
		"""
		WXMonster.__init__( self )
		self.bornNPC = False
		#self.callMonsterID	= "20712014"
		#self.fightingText	= cschannel_msgs.NIU_MO_WANG_VOICE_5
		#self.freeText		= cschannel_msgs.NIU_MO_WANG_VOICE_6
		#self.fightOption	= cschannel_msgs.NIU_MO_WANG_VOICE_1
		#self.leaveOption	= cschannel_msgs.NIU_MO_WANG_VOICE_2
		#self.fightSay		= cschannel_msgs.NIU_MO_WANG_VOICE_3
		#self.dieSay			= cschannel_msgs.NIU_MO_WANG_VOICE_4
		
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
		NPCObject.gossipWith( self, selfEntity, playerEntity, dlgKey )
		
	def getSpawnPos( self, selfEntity ):
		return selfEntity.position
	