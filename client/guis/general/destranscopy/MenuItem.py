# -*- coding: gb18030 -*-
# 副本组队右键菜单

from guis import *
from LabelGather import labelGather
from guis.controls.ContextMenu import DefMenuItem
from config.client.msgboxtexts import Datas as mbmsgs
import csdefine

class QuitTeamMItem( DefMenuItem ):
	"""
	退出队伍子菜单
	"""
	def __init__( self, text = "退出队伍" ) :
		DefMenuItem.__init__( self, text )

	def check( self, matedbid, player ):
		return matedbid == player.databaseID

	def do( self, matedbid, player ):
		"""
		离开队伍
		"""
		player.leaveTeam()

class KickMateMItem( DefMenuItem ):
	"""
	队伍踢人子菜单
	"""
	def __init__( self, text = "踢出队伍" ) :
		DefMenuItem.__init__( self, text )

	def check( self, matedbid, player ):
		isCaptain = player.isCaptain()
		return isCaptain and matedbid != player.databaseID

	def do( self, matedbid, player ):
		member = getTeamMateByDBID( matedbid )
		if member:
			player.teamDisemploy( member.objectID )

class DisbTeamMItem( DefMenuItem ) :
	"""
	解散队伍子菜单
	"""
	def __init__( self, text = "解散队伍" ) :
		DefMenuItem.__init__( self, text )

	def check( self, matedbid, player ):
		isCaptain = player.isCaptain()
		return isCaptain and matedbid == player.databaseID

	def do( self, matedbid, player ):
		player.disbandTeam()
		
def getTeamMateByDBID( dbid ):
	player = BigWorld.player()
	for member in player.teamMember.values():
		if member.DBID == dbid:
			return member