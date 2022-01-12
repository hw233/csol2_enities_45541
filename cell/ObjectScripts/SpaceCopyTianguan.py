# -*- coding: gb18030 -*-

from SpaceCopyTeamTemplate import SpaceCopyTeamTemplate
from CopyContent import NEXT_CONTENT
from CopyContent import CopyContent
from CopyContent import CCWait
from CopyContent import CCEndWait
from CopyContent import CCKickPlayersProcess
from GameObjectFactory import g_objFactory
import BigWorld
import csdefine
import cschannel_msgs
import csconst
import time
import ECBExtend

BASE_MONSTER_COUNT = 12
STEP_MONSTER_COUNT = 4
MIN_TEAM_MEMBERS = 3

MAX_GRADE = 6

#关卡所对应的怪物复活次数
gradeReviousDict = { 1 : 2,
					 2 : 3,
					 3 : 4,
					 4 : 5,
					 5 : 6,
					 6 : 0,
				}


class CCLevel( CopyContent ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		self.key = "level"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		刷怪数量和队伍有关。
		怪物复活次数和关数有关。
		"""
		grade = spaceEntity.queryTemp( "currentGrade", 1 )
		if len( spaceEntity._players ) >= 3:
			memberCount = ( BASE_MONSTER_COUNT + ( len( spaceEntity._players ) - MIN_TEAM_MEMBERS ) * STEP_MONSTER_COUNT ) * gradeReviousDict[grade]
		else:
			memberCount = BASE_MONSTER_COUNT * gradeReviousDict[grade]

		spaceEntity.base.spawnMonsters( { "copyLevel": spaceEntity.params["copyLevel"] + grade - 1, "grade" : grade, "teamcount" : len( spaceEntity._players ) } )
		spaceEntity.setTemp( "monsterCount", memberCount )
		spaceEntity.setTemp( "bossCount", 1 )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, memberCount  )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 1  )

	def onConditionChange( self, spaceEntity, params ):
		"""
		"""
		if "monsterType" not in params:
			return
		m = spaceEntity.queryTemp( "monsterCount" )
		b = spaceEntity.queryTemp( "bossCount" )
		if params["monsterType"] == 0:
			m -= 1
			spaceEntity.setTemp( "monsterCount", m )
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, spaceEntity.queryTemp( "monsterCount" )  )
		else:
			b -= 1
			spaceEntity.setTemp( "bossCount", b )
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, spaceEntity.queryTemp( "bossCount" )  )
		if m <= 0 and b <= 0:
			CopyContent.onConditionChange( self, spaceEntity, params )

	def endContent( self, spaceEntity ):
		"""
		内容结束
		"""
		spaceEntity.getScript().createDoor( spaceEntity,   spaceEntity.queryTemp( "currentGrade", 1 ) )
		if spaceEntity.queryTemp( "currentGrade", 1 ) < MAX_GRADE:
			if spaceEntity.queryTemp( "currentGrade", 1 ) < MAX_GRADE - 1:
				for player in spaceEntity._players:
					player.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.BCT_TGHD_GRADE_FINISH, [] )
			grade = spaceEntity.queryTemp( "currentGrade", 1 ) + 1
			spaceEntity.setTemp( "currentGrade", grade )
		else:
			boxEntity = g_objFactory.getObject( spaceEntity.getScript().lastBox ).createEntity( spaceEntity.spaceID, spaceEntity.getScript().lastBoxPosition, (0, 0, 0), {} )
			boxEntity.setTemp( 'spaceLevel', spaceEntity.params["copyLevel"] + MAX_GRADE - 1 )
		CopyContent.endContent( self, spaceEntity )


class SpaceCopyTianguan( SpaceCopyTeamTemplate ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopyTeamTemplate.__init__( self )
		self.recordKey = "tianguan_record"

	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		SpaceCopyTeamTemplate.load( self, section )
		self.total_gates_count 	= section['total_gates_count'].asInt
		self.lastBox 			= section[ "LastBox" ].asString
		self.lastBoxPosition 	= section[ "Reward_Position" ].asVector3
		spaceSec 				= section["Space"]
		keys 					= spaceSec.keys()
		KeySect 				= spaceSec.child(keys.index("Door"))
		for name, sect in KeySect.items():
			self._spaceConfigInfo[ "Doormap" ][name]["level"] = sect.readInt("level")


		self._spaceConfigInfo[ "TianguanDoormap" ] = self._spaceConfigInfo[ "Doormap" ]
		self._spaceConfigInfo[ "Doormap" ] = {}

	def initContent( self ):
		"""
		"""
		self.contents.append( CCWait() )
		self.contents.append( CCWait() )
		self.contents.append( CCLevel() )
		self.contents.append( CCWait() )
		self.contents.append( CCLevel() )
		self.contents.append( CCWait() )
		self.contents.append( CCLevel() )
		self.contents.append( CCWait() )
		self.contents.append( CCLevel() )
		self.contents.append( CCWait() )
		self.contents.append( CCLevel() )
		self.contents.append( CCWait() )
		self.contents.append( CCLevel() )
		self.contents.append( CCWait() )
		self.contents.append( CCEndWait() )
		self.contents.append( CCKickPlayersProcess() )

	def packedDomainData( self, player ):
		"""
		模仿普通副本的制作方式，给天关存储创建者的信息
		@param player:	创建者实例
		"""
		captain = BigWorld.entities.get( player.captainID )
		if captain:
			level = captain.level
		else:
			level = 0
		data = {"copyLevel" 		: 	level - 2,
				"dbID" 				: 	player.databaseID,
				"teamID" 			: 	player.teamMailbox.id,
				"captainDBID"		:	player.getTeamCaptainDBID(),
				"spaceKey"			:	player.teamMailbox.id,
				}
		return data

	def packedSpaceDataOnEnter( self, entity ):
		"""
		"""
		packDict = SpaceCopyTeamTemplate.packedSpaceDataOnEnter( self, entity )
		packDict[ "teamID" ] = entity.teamMailbox.id
		return packDict

	def createDoor( self, selfEntity, level = 0 ):
		"""
		"""
		print "Create Tianguan Door %s" % level
		configInfo = self.getSpaceConfig()
		for name, otherDict in configInfo[ "TianguanDoormap" ].iteritems():
			if otherDict['level'] == level:
				door = BigWorld.createEntity( "SpaceDoor", selfEntity.spaceID, otherDict["position"], (0, 0, 0), otherDict )
				if otherDict.has_key( 'modelScale' ) and otherDict[ 'modelScale' ] != 0.0:
					door.modelScale = otherDict[ 'modelScale' ]

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		if selfEntity.queryTemp("firstPlayer", 0 ) == 0:
			BigWorld.globalData['Tianguan_%i'%params['teamID'] ] = True
			selfEntity.setTemp('globalkey','Tianguan_%i'%params['teamID'])
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEVEL, 		"" )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_COPY_TITLE, ""  )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME,  time.time() )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, 1800  )
			selfEntity.addTimer( 1800, 0, 123453 )
			
		if baseMailbox and params[ "databaseID" ] not in selfEntity._enterRecord:
			baseMailbox.cell.remoteAddActivityCount( selfEntity.id, csdefine.ACTIVITY_CHUANG_TIAN_GUAN, self.recordKey )
			
		SpaceCopyTeamTemplate.onEnterCommon( self, selfEntity, baseMailbox, params )

	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if userArg == 123453:
			for e in selfEntity._players:
				player = BigWorld.entities.get( e.id, None )
				if player is None:
					e.cell.gotoForetime()
				else:
					player.gotoForetime()
			return

		SpaceCopyTeamTemplate.onTimer( self, selfEntity, id, userArg )
