# -*- coding: gb18030 -*-


from SpaceCopyTeamTemplate import SpaceCopyTeamTemplate
import cschannel_msgs
import ShareTexts as ST
from CopyContent import CopyContent
from CopyContent import CCWait
from CopyContent import CCKickPlayersProcess
from CopyContent import NEXT_CONTENT
from CopyContent import CCEndWait
import BigWorld
import csconst
import time
import csdefine
import ECBExtend
import csstatus


class CCSpawnHundunLittleMonster( CopyContent ):
	"""
	#刷新小怪物
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanHundunLittleMonster"
		self.val = 30

	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.base.spawnMonsters( {"monsterType":  0, "level": spaceEntity.params["copyLevel"] } )


	def onConditionChange( self, spaceEntity, params ):
		"""
		"""
		for e in spaceEntity._players:
			if BigWorld.entities.has_key( e.id ):
				if BigWorld.entities[e.id].isReal():
					jifen = BigWorld.entities[e.id].query( "hundun_jifen", 0 )
					BigWorld.entities[e.id].set( "hundun_jifen",jifen + 1 )
					BigWorld.entities[e.id].client.onStatusMessage( csstatus.HUNDUN_CURRENT_JIFEN, str(( jifen + 1, )) )
		CopyContent.onConditionChange( self, spaceEntity, params )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, 30 - spaceEntity.queryTemp( self.key, 0 )  )

class CCSpawnHundunBigMonster( CopyContent ):
	"""
	#刷新大怪物
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanHundunBigMonster"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.base.spawnMonsters( {"monsterType":  1, "level": spaceEntity.params["copyLevel"] } )
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.BCT_HUNDUN_BOSS_NOTIFY, [] )


	def onConditionChange( self, spaceEntity, params ):
		"""
		"""
		for e in spaceEntity._players:
			if BigWorld.entities.has_key( e.id ):
				if BigWorld.entities[e.id].isReal():
					jifen = BigWorld.entities[e.id].query( "hundun_jifen", 0 )
					BigWorld.entities[e.id].set( "hundun_jifen",jifen + 20 )
					BigWorld.entities[e.id].client.onStatusMessage( csstatus.HUNDUN_CURRENT_JIFEN, str(( jifen + 20, )) )
		CopyContent.onConditionChange( self, spaceEntity, params )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 0 )
		self.createDoor( spaceEntity )

		self.destroyEnterMonster( spaceEntity )

	def createDoor( self, spaceEntity ):
		"""
		创建Door
		"""
		doordict = {"name" : cschannel_msgs.HUN_DUN_RU_QIN_CHUAN_SONG_DIAN}
		doordict["radius"] = 2.0
		doordict["destSpace"] = spaceEntity.params["spaceLabel"]
		doordict["destPosition"] = spaceEntity.params["position"]
		doordict["destDirection"] = ( 0, 0, 0 )
		doordict["modelNumber"] = "gw7123"
		doordict["modelScale"] = 25
		BigWorld.createEntity( "SpaceDoor", spaceEntity.spaceID, (111.796,-0.789,35.983), (0, 0, 0), doordict )

	def destroyEnterMonster( self, spaceEntity ):
		"""
		销毁进入的NPC
		"""
		for key in BigWorld.globalData.keys():
			if type(key) == type("cellApp_") and "cellApp_" in key:
				BigWorld.executeRemoteScript( "BigWorld.cellAppData['%s'].entityFunc( %i, '%s' )"%( key + "_actions", spaceEntity.params["enterMonsterID"], "destroy" ), BigWorld.globalData[key] )



class SpaceCopyHundun( SpaceCopyTeamTemplate ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopyTeamTemplate.__init__( self )


	def initContent( self ):
		"""
		"""
		self.contents.append( CCWait() )
		self.contents.append( CCSpawnHundunLittleMonster() )
		self.contents.append( CCSpawnHundunBigMonster() )
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
		if "HD_%i"%player.teamMailbox.id in BigWorld.cellAppData.keys():
			monsterID = BigWorld.cellAppData["HD_%i"%player.teamMailbox.id]

		data = {"copyLevel"			: 	level,
				"dbID" 				: 	player.databaseID,
				"teamID" 			: 	player.teamMailbox.id,
				"captainDBID"		:	player.getTeamCaptainDBID(),
				"spaceLabel"		:	BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_KEY ),
				"position"			:	player.position,
				"enterMonsterID"	:	monsterID,
				"spaceKey"			:	player.teamMailbox.id,
				}
		return data

	def packedSpaceDataOnEnter( self, player ):
		"""
		"""
		dict = SpaceCopyTeamTemplate.packedSpaceDataOnEnter( self, player )
		dict["dbID" ] = player.databaseID
		
		return dict


	def onStartContent( self, selfEntity, baseMailbox, params ):
		"""
		"""
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEVEL, 		"" )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_COPY_TITLE, cschannel_msgs.WIZCOMMAND_HUN__RU_QIN )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, time.time() )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, -1 )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, 30 )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 1 )

		SpaceCopyTeamTemplate.onStartContent( self, selfEntity, baseMailbox, params )

	def onEnter( self, selfEntity, baseMailbox, params ):
		"""
		"""
		SpaceCopyTeamTemplate.onEnter( self, selfEntity, baseMailbox, params )

		baseMailbox.cell.checkTeamInCopySpace( selfEntity.base )
