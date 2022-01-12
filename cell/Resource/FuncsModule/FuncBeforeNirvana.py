# -*- coding:gb18030 -*-
# 10 ��������ǰ�����䡱 by mushuang


from Function import Function
import csstatus
import csdefine
from bwdebug import *
import Const
import BigWorld

REQUIRED_LEVEL = 10
SPACE_COPY_NAME = "fu_ben_qian_shi"
ENTER_POINT = ( 15.625, -5.093, 0.583 )	#modify by wuxo 2011-12-2
ENTER_DIRECTION = ( 11.76, 59.584, -1.014 ) #modify by wuxo 2011-12-13

class FuncBeforeNirvana( Function ):
	"""
	װ�����Է���
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		# param1: Ϊ���븱��ʱ��Ҫչ���Ļ���ID
		self.scrollID = section[ "param1" ].asInt

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
		if talkEntity is None:
			ERROR_MSG( "player( %s ) talk entity is None." % player.getName() )
			return
		playerEntity.endGossip( talkEntity )
		
		# �����ؽ�������
		
		# �ȼ�
		if playerEntity.getLevel() < REQUIRED_LEVEL :
			playerEntity.statusMessage( csstatus.BEFORE_NIRVANA_LEVEL_TOO_LOW )
			return
		
		playerEntity.setTemp( "ScrollIDOnEnter", self.scrollID )
		
		# ��������ͨ����׼�����
		playerEntity.gotoSpace( SPACE_COPY_NAME, ENTER_POINT, ENTER_DIRECTION )
		