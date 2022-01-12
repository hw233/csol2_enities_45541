# -*- coding: gb18030 -*-

# ------------------------------------------------
# from python
import time
# ------------------------------------------------
# from engine
import BigWorld
# ------------------------------------------------
# from common
import csdefine
import csstatus
import csconst
# ------------------------------------------------
# from locale_default
import cschannel_msgs
# ------------------------------------------------
# from cell
# ------------------------------------------------
# from current directory
from CopyTeamTemplate import CopyTeamTemplate

# ------------------------------------------------



SPACE_LAST_TIME = 3600 		#持续时间一小时

class CopyHunDun( CopyTeamTemplate ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		CopyTeamTemplate.__init__( self )

	def packedDomainData( self, player ):
		"""
		"""
		captain = BigWorld.entities.get( player.captainID )
		if captain:
			level = captain.level
		else:
			level = 0
		monsterID = 0
		if "HD_%i"%player.teamMailbox.id in BigWorld.cellAppData.keys():
			monsterID = BigWorld.cellAppData["HD_%i"%player.teamMailbox.id]

		data = {"copyLevel"			: 	level,
				"dbID" 				: 	player.databaseID,
				"teamID" 			: 	player.teamMailbox.id,
				"captainDBID"		:	player.getTeamCaptainDBID(),
				"spaceLabel"		:	BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_KEY ),
				"position"			:	player.position,
				"enterMonsterID"	:	monsterID,
				}
		return data

	def packedSpaceDataOnEnter( self, player ):
		"""
		"""
		dict = CopyTeamTemplate.packedSpaceDataOnEnter( self, player )
		dict["dbID" ] = player.databaseID
		
		return dict

	def shownDetails( self ):
		"""
		shownDetails 副本内容显示规则：
		[ 
			0: 剩余时间
			1: 剩余小怪
			2: 剩余小怪批次
			3: 剩余BOSS
			4: 蒙蒙数量
			5: 剩余魔纹虎数量
			6: 剩余真鬼影狮数量
		]
		"""
		# 显示剩余小怪，剩余BOSS。 
		return [ 1, 3 ]