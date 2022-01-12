# -*- coding: gb18030 -*-
#


"""
"""
from Function import Function
import csdefine
import BigWorld
import time
import csstatus
import csconst

ENTERN_MENBER_DISTANCE = 5

class FuncEnterProtectTong( Function ):
	"""
	���뱣�����ɸ���
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self.spaceName = section["param1"].asString
		self.protectType = section["param2"].asInt

	def do( self, player, talkEntity = None ):
		"""
		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		if player.level < csconst.PK_PROTECT_LEVEL:
			player.statusMessage( csstatus.ROLE_LEVEL_LOWER_PK_ALOW_LEVEL )
			player.endGossip( talkEntity )
			return

		if not player.isInTeam():
			#���û�����
			player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
			return

		if not player.isTeamCaptain():
			player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
			return

		pList = player.getAllMemberInRange( ENTERN_MENBER_DISTANCE )
		count = len( pList )

		if not player.getTeamCount() >= 3 :
			player.statusMessage( csstatus.PROTECT_TONG_TEAM_INVALID )
			return

		if count != player.getTeamCount():
			player.statusMessage( csstatus.PROTECT_TONG_TEAM_FULL_INVALID )
			return
		talkEntity.onProtectTongOver()
		tongDBID = BigWorld.globalData[ "AS_ProtectTong" ][0]
		for p in pList:
			p.setTemp( "ProtectTongData", ( tongDBID, tuple( p.position ), ( 0, 0, 0 ) ) )
			p.setTemp( "enterSpaceID", p.teamMailbox.id )
			p.gotoSpace( self.spaceName, ( 0, 0, 0 ), ( 0, 0, 0 ) )

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
		try:
			protectTongData = BigWorld.globalData[ "AS_ProtectTong" ]
		except KeyError:
			protectTongData = None
		return protectTongData is not None and protectTongData[2] == self.protectType
		#return BigWorld.globalData.has_key( "AS_ProtectTong" )

