# -*- coding:gb18030 -*-

from Function import Function
import csstatus
import csdefine
from bwdebug import *
import Const
import BigWorld
import SkillTargetObjImpl

class FuncUnfoldScroll( Function ):
	"""
	10��������չ��ǽ�ϵĻ��������ʩ��
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		# param1 UINT32����ָ������һ����
		# param2 STRING����ָ��չ������ʱʩ���õļ���
		
		self.scrollID = section[ "param1" ].asInt
		self.spellID = section[ "param2" ].asInt
		
		assert self.spellID != 0
		

	def valid( self, playerEntity, talkEntity = None ):
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

	def do( self, playerEntity, talkEntity = None ):
		"""
		ִ��һ������

		@param playerEntity: ���
		@type  playerEntity: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		playerEntity.endGossip( talkEntity )
		
		
		if talkEntity is None:
			ERROR_MSG( "player( %s ) talk entity is None." % playerEntity.getName() )
			return		
		
		# �����ʩ�����Ա�����������м���ض������Ƿ����
		playerEntity.spellTarget( self.spellID, playerEntity.id )
		
		playerEntity.client.unfoldScroll( talkEntity.id, self.scrollID )