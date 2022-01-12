# -*- coding: gb18030 -*-
# ��������Ҽ��˵�

from guis import *
from LabelGather import labelGather
from guis.controls.ContextMenu import DefMenuItem
from config.client.msgboxtexts import Datas as mbmsgs
import csdefine

class EnterCopyMItem( DefMenuItem ):
	"""
	���븱���Ӳ˵�
	"""
	def __init__( self, text = labelGather.getText( "copyteam:TeamMenus", "entercopy" ) ) :
		DefMenuItem.__init__( self, text )

	def check( self, player ):
		insideMatchedCopy = player.insideMatchedCopy
		matchedCopy = player.labelOfMatchedCopy
		return ( not insideMatchedCopy ) and matchedCopy

	def do( self, player):
		"""
		��������
		"""
		player.shuttleMatchedCopy( True )

class QuitCopyMItem( DefMenuItem ):
	"""
	�뿪�����Ӳ˵�
	"""
	def __init__( self, text = labelGather.getText( "copyteam:TeamMenus", "quitcopy" ) ) :
		DefMenuItem.__init__( self, text )

	def check( self, player ):
		insideMatchedCopy = player.insideMatchedCopy
		matchedCopy = player.labelOfMatchedCopy
		return insideMatchedCopy and matchedCopy

	def do( self, player ):
		player.shuttleMatchedCopy( False )

class SuppleMItem( DefMenuItem ) :
	"""
	��������Ӳ˵�
	"""
	def __init__( self, text = labelGather.getText( "copyteam:TeamMenus", "suppmember" ) ) :
		DefMenuItem.__init__( self, text )

	def check( self, player ):
		isTeamFull = player.isTeamFull()
		matchedCopy = player.labelOfMatchedCopy
		isCaptain = player.isCaptain()
		return ( not isTeamFull ) and matchedCopy and isCaptain

	def do( self, player ):
		ECenter.fireEvent( "EVT_ON_TOGGLE_TEAMCOPY_SYSTEM_WND", True )

class CopyTeamMItem( DefMenuItem ) :
	"""
	��������Ӳ˵�
	"""
	def __init__( self, text = labelGather.getText( "copyteam:TeamMenus", "copyTeam" ) ) :
		DefMenuItem.__init__( self, text )

	def check( self, player ):
		matchedCopy = player.labelOfMatchedCopy
		return  matchedCopy != ""

	def do( self, player ):
		ECenter.fireEvent( "EVT_ON_TOGGLE_TEAMCOPY_SYSTEM_WND" )