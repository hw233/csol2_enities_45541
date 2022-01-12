# -*- coding: gb18030 -*-

import BigWorld
import csstatus
import csconst
import csdefine
from bwdebug import *
from Function import Function

ENTERN_DESTINY_TRANS_MENBER_DISTANCE = 30.0

class FuncEnterDestinyTrans( Function ):
	"""
	�����ֻظ���
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		self.reqLevel = section.readInt( "param1" )
		
	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��
		"""
		if player.isState( csdefine.ENTITY_STATE_DEAD ):	# �������Ѿ����������ܿ���
			return False
		return True
		
	def do( self, player, talkEntity = None ):
		"""
		���������ֻظ���
		"""
		player.endGossip( talkEntity )
		
		if self.reqLevel > player.level:
			#��ҵȼ�����
			player.statusMessage( csstatus.DESTINY_TRANS_LEVEL_NOT_ENOUGH,  player.getName() )
			return

		if not player.isInTeam():
			#���û�����
			player.statusMessage( csstatus.DESTINY_TRANS_NEED_TEAM )
			return

class FuncEnterDestinyTransCommon( FuncEnterDestinyTrans ):
	"""
	�����ֻظ�������ͨģʽ
	"""
	def __init__( self, section ):
		FuncEnterDestinyTrans.__init__( self, section )
		self.type = csconst.DESTINY_TRANS_COPY_COMMON
	
	def do( self, player, talkEntity = None ):
		FuncEnterDestinyTrans.do( self, player, talkEntity )
		BigWorld.globalData[ "SpaceDestinyTransMgr" ].roleRequreEnter( player.base, player.databaseID, player.getTeamMailbox().id, self.reqLevel )

