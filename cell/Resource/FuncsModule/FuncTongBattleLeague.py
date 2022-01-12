# -*- coding: gb18030 -*-

import csdefine
import csstatus
from bwdebug import *

class FuncTongBattleLeague:
	"""
	���ս������
	"""
	def __init__( self, section ):
		self.camp = section.readInt( "param1")		# ��Ӫ

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		if not player.checkDutyRights( csdefine.TONG_RIGHT_LEAGUE_MAMAGE ):
			player.statusMessage( csstatus.TONG_BATTLE_LEAGUE_LIMIT )
			return
		
		BigWorld.globalData[ "TongManager"].reqOpenBattleLeaguesWindow( player, player.getCamp(), player.spaceType )

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
		return self.camp == player.getCamp()
