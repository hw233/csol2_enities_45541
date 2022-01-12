# -*- coding: gb18030 -*-

import BigWorld
from Function import Function
import csdefine

class FuncPlaySound( Function ):
	"""
	����ָ��·������
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.param1 = section.readString( 'param1' )	# ��Ƶ�ļ�·��
		self.priority = csdefine.GOSSIP_PLAY_VOICE_PRIORITY_OPTION

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.client.playSound( self.param1, 2, 0, self.priority )	# Ĭ�ϲ���2D����

	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True
		
class FuncPlaySoundFromGender( Function ):
	"""
	�����Ա𲥷�ָ��·������
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.param1 = section.readString( 'param1' )	# ��Ƶ�ļ�·�������ԣ�
		self.param2 = section.readString( 'param2' )	# ��Ƶ�ļ�·����Ů�ԣ�
		self.priority = csdefine.GOSSIP_PLAY_VOICE_PRIORITY_OPTION

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		if player.getGender() == csdefine.GENDER_MALE:
			player.client.playSound( self.param1, 2, 0, self.priority )	# Ĭ�ϲ���2D����
		elif player.getGender() == csdefine.GENDER_FEMALE:
			player.client.playSound( self.param2, 2, 0, self.priority )	# Ĭ�ϲ���2D����

	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True