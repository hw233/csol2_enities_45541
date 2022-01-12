# -*- coding: gb18030 -*-
#
# $Id: FuncContestFamilyNPC.py,v 1.3 2008-07-31 04:14:37 kebiao Exp $

"""
"""
from Function import Function
import BigWorld
import csstatus
import csdefine
import csconst

class FuncSelectTongShenShou( Function ):
	"""
	ѡ��������
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		pass

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
		
		if BigWorld.globalData.has_key( "TONG_ROB_WAR_START" ) and player.tong_dbID in BigWorld.globalData[ "TONG_ROB_WAR_START" ]:
			player.statusMessage( csstatus.TONG_SELECT_SHENSHOU_REVIVE_INVALID1 )
			return
				
		try:
			tongTerritory = BigWorld.entities.get( player.getCurrentSpaceBase().id )
			if tongTerritory.queryTemp("startCampaingnTime", 0):					# ħ����Ϯ��в������������
				player.statusMessage( csstatus.TONG_SELECT_SHENSHOU_REVIVE_INVALID2 )
				return 
		except:
			pass
		
		tongMailbox = player.tong_getTongEntity( player.tong_dbID )
		if tongMailbox:
			tongMailbox.onOpenShenShouSelectWindow( player.databaseID )

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


#
# $Log: not supported by cvs2svn $
#
