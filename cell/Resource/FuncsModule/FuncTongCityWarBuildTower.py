# -*- coding: gb18030 -*-
#
# $Id: FuncQueryFamilyNPC.py,v 1.2 2008-07-19 03:53:07 kebiao Exp $

"""
"""
from Function import Function
import BigWorld
import csconst

class FuncTongCityWarBuildTower( Function ):
	"""
	������ս ����һ����¥
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		# ���춫��¥ ���ϱ� ��������Ϊ 1,2,3,4
		self._whoisTower = section.readInt( "param1" ) - 1

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		if player.tong_dbID in BigWorld.globalData[ "CityWarRightTongDBID" ]:
			tongMailbox = player.tong_getTongEntity( player.tong_dbID )
			if tongMailbox:
				player.getCurrentSpaceBase().cell.buildTower( player.id, self._whoisTower, tongMailbox )
				#tongMailbox.buildCityWarTower( player.databaseID, self._whoisTower, player.getCurrentSpaceBase() )
				
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
		return player.tong_dbID in BigWorld.globalData[ "CityWarRightTongDBID" ]


#
# $Log: not supported by cvs2svn $
# Revision 1.1  2008/07/18 06:23:15  kebiao
# no message
#
# Revision 1.4  2008/06/09 01:22:12  fangpengjun
# no message
#
# Revision 1.3  2008/06/05 07:54:14  fangpengjun
# no message
#
# Revision 1.2  2008/06/05 02:03:14  kebiao
# no message
#
#
