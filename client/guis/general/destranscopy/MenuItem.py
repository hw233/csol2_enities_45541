# -*- coding: gb18030 -*-
# ��������Ҽ��˵�

from guis import *
from LabelGather import labelGather
from guis.controls.ContextMenu import DefMenuItem
from config.client.msgboxtexts import Datas as mbmsgs
import csdefine

class QuitTeamMItem( DefMenuItem ):
	"""
	�˳������Ӳ˵�
	"""
	def __init__( self, text = "�˳�����" ) :
		DefMenuItem.__init__( self, text )

	def check( self, matedbid, player ):
		return matedbid == player.databaseID

	def do( self, matedbid, player ):
		"""
		�뿪����
		"""
		player.leaveTeam()

class KickMateMItem( DefMenuItem ):
	"""
	���������Ӳ˵�
	"""
	def __init__( self, text = "�߳�����" ) :
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
	��ɢ�����Ӳ˵�
	"""
	def __init__( self, text = "��ɢ����" ) :
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