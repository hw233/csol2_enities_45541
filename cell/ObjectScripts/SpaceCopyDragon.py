# -*- coding: gb18030 -*-

from SpaceCopyTeamTemplate import SpaceCopyTeamTemplate
import cschannel_msgs
import ShareTexts as ST
from CopyContent import NEXT_CONTENT
from CopyContent import CopyContent
from CopyContent import CCKickPlayersProcess
from CopyContent import CCWait
from CopyContent import CCEndWait
import BigWorld
import csconst
import time
import csdefine
import ECBExtend

LITTLE_MONSTER_TYPE = 0
BOSS_MONSTER_TYPE = 1

MONSTER_LEVEL     =  40   #小怪等级

class CCSpawnLittleDragon( CopyContent ):
	"""
	#刷新小暴龙
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanLittleDragon"
		self.val = 60

	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.base.spawnMonsters( {"monsterType":  LITTLE_MONSTER_TYPE, "copyLevel": spaceEntity.params["copyLevel"] } )

	def onConditionChange( self, spaceEntity, params ):
		"""
		"""
		CopyContent.onConditionChange( self, spaceEntity, params )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, 60 - spaceEntity.queryTemp( self.key, 0 )  )


class CCSpawnBigDragon( CopyContent ):
	"""
	#刷新大暴龙
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanBigDragon"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.BCT_TIANJIANGQISHOU_BOSS_NOTIFY, [] )
		spaceEntity.base.spawnMonsters( {"monsterType":  BOSS_MONSTER_TYPE, "copyLevel": spaceEntity.params["copyLevel"] + 3 } )

	def onConditionChange( self, spaceEntity, params ):
		"""
		"""
		CopyContent.onConditionChange( self, spaceEntity, params )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 0 )
		self.createDoor( spaceEntity )

		self.destroyEnterMonster( spaceEntity )


	def createDoor( self, spaceEntity ):
		"""
		创建Door
		"""
		doordict = {"name" : cschannel_msgs.TIAN_JIANG_QI_SHOU_INFO_1}
		doordict["radius"] = 2.0
		doordict["destSpace"] = spaceEntity.params["spaceLabel"]
		doordict["destPosition"] = spaceEntity.params["position"]
		doordict["destDirection"] = ( 0, 0, 0 )
		doordict["modelNumber"] = "gw7123"
		doordict["modelScale"] = 25
		BigWorld.createEntity( "SpaceDoor", spaceEntity.spaceID, (-32.783,2.996,106.986), (0, 0, 0), doordict )

	def destroyEnterMonster( self, spaceEntity ):
		"""
		销毁进入的NPC
		"""
		for key in BigWorld.globalData.keys():
			if type(key) == type("cellApp_") and "cellApp_" in key:
				BigWorld.executeRemoteScript( "BigWorld.cellAppData['%s'].entityFunc( %i, '%s' )"%( key + "_actions", spaceEntity.params["enterMonsterID"], "destroy" ), BigWorld.globalData[key] )



class SpaceCopyDragon( SpaceCopyTeamTemplate ):
	"""
	大头暴龙活动
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopyTeamTemplate.__init__( self )
		self.isSpaceCalcPkValue = True
		self.isSpaceDesideDrop = True

	def initContent( self ):
		"""
		"""
		self.contents.append( CCWait() )
		self.contents.append( CCSpawnLittleDragon())
		self.contents.append( CCSpawnBigDragon() )
		self.contents.append( CCEndWait() )
		self.contents.append( CCKickPlayersProcess() )

	def packedDomainData( self, player ):
		"""
		"""
		captain = BigWorld.entities.get( player.captainID )
		if captain:
			level = captain.level
		else:
			level = 0
		monsterID = 0
		if "TJQS_%i"%player.teamMailbox.id in BigWorld.cellAppData.keys():
			monsterID = BigWorld.cellAppData["TJQS_%i"%player.teamMailbox.id]

		data = {"copyLevel" 		: 	level,
				"dbID" 				: 	player.databaseID,
				"teamID"			:	player.teamMailbox.id,
				"captainDBID"		:	player.getTeamCaptainDBID(),
				"spaceLabel"		:	BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_KEY ),
				"position"			:	player.position,
				"enterMonsterID"	:	monsterID,
				"spaceKey"			:	player.teamMailbox.id,
				}
		return data


	def onStartContent( self, selfEntity, baseMailbox, params ):
		"""
		"""
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEVEL, 		"" )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_COPY_TITLE, cschannel_msgs.TIAN_JIANG_QI_SHOU_INFO_2 )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, time.time() )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, -1 )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, 60 )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 1 )
		SpaceCopyTeamTemplate.onStartContent( self, selfEntity, baseMailbox, params )

	def onEnter( self, selfEntity, baseMailbox, params ):
		"""
		"""
		SpaceCopyTeamTemplate.onEnter( self, selfEntity, baseMailbox, params )

		baseMailbox.cell.checkTeamInCopySpace( selfEntity.base )

	def packedSpaceDataOnEnter( self, player ):
		"""
		"""
		packeDict = SpaceCopyTeamTemplate.packedSpaceDataOnEnter( self, player )
		packeDict[ "dbID" ] = player.databaseID
		packeDict[ "teamID" ] = player.teamMailbox.id if player.teamMailbox else 0
		return packeDict