# -*- coding: gb18030 -*-
"""
�����NPC�Ի� 14:11 2010-1-14 by ����
"""

from Function import Function
from bwdebug import *
import csstatus
import csdefine
import csconst
import BigWorld
import sys

class FuncTongSign( Function ):
	"""
	�����NPC�Ի�
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._talkType = int( section.readString( "param1" ) )	# ��Ҫ�ϴ�(1)���Ǹ���(2)����ȡ��(3)ͼ��
		
	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		if player.iskitbagsLocked():	# ����������by����
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			player.endGossip( talkEntity )
			return
		if self._talkType == 1:
			self.submitTongSign( player )
		elif self._talkType == 2:
			self.changeTongSign( player )
		elif self._talkType == 3:
			self.cancleTongSign( player )
		elif self._talkType == 4:
			self.useSubmitTongSign( player )
		else:
			ERROR_MSG( "self._talkType error, no this talk type %i"%( self._talkType ) )
		player.sendGossipComplete( talkEntity.id )
		Function.do( self, player, talkEntity )
		player.endGossip( talkEntity )

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
		
	def submitTongSign( self, player ):
		"""
		�ϴ����ͼ��
		"""
		if not player.checkDutyRights( csdefine.TONG_RIGHT_SIGN ):	# Ȩ�޼��
			player.statusMessage( csstatus.TONG_ME_NOT_IS_CHIEF )
			return
		if player.tong_level < csconst.USER_TONG_SIGN_REQ_TONG_LEVEL:
			player.statusMessage( csstatus.TONG_SIGN_NOT_THAT_LEVEL )
			return
		player.client.tongSignTalkResult( 1 )
		
	def changeTongSign( self, player ):
		"""
		���������
		"""
		if not player.checkDutyRights( csdefine.TONG_RIGHT_SIGN ):	# Ȩ�޼��
			player.statusMessage( csstatus.TONG_ME_NOT_IS_CHIEF )
			return
		player.client.tongSignTalkResult( 2 )
		
	def cancleTongSign( self, player ):
		"""
		ȡ�������
		"""
		if not player.checkDutyRights( csdefine.TONG_RIGHT_SIGN ):	# Ȩ�޼��
			player.statusMessage( csstatus.TONG_ME_NOT_IS_CHIEF )
			return
		player.client.tongSignTalkResult( 3 )
		
	def useSubmitTongSign( self, player ):
		"""
		ʹ���ϴ����
		"""
		if not player.checkDutyRights( csdefine.TONG_RIGHT_SIGN ):	# Ȩ�޼��
			player.statusMessage( csstatus.TONG_ME_NOT_IS_CHIEF )
			return
		player.tong_getSelfTongEntity().changeTongSing( False, 0, "sub", player )