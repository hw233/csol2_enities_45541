# -*- coding: gb18030 -*-

import time

import BigWorld

import csdefine
import cschannel_msgs
import csconst
import csstatus

from SpaceCopy import SpaceCopy
import ECBExtend

from ObjectScripts.GameObjectFactory import g_objFactory

from config import ChallengeAvatarSkills # 技能配置

FUBEN_LIVING_TIME = 60 * 60
KICK_PLAYER_KEY = 1000002
PI_SHAN_ENTER_NPC = "10121093"

class SpaceCopyChallenge( SpaceCopy ):
	"""
	"""
	def __init__( self ):
		SpaceCopy.__init__( self )
			
		self.spaceSkills = ChallengeAvatarSkills.Datas
		self.spaceFixedSkill = {} # 固定等级技能
		self.spaceFixedSkill["chiyou"] = []
		self.spaceFixedSkill["huangdi"] = []
		self.spaceFixedSkill["houyi"] = []
		self.spaceFixedSkill["nuwo"] = []
		
		self.birthPosition = (0, 0, 0)
		self.birthDirection = (0, 0, 1)
		self.challengeNos = []
		
	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		根据给定的section，初始化（读取）entity属性。
		注：只有在createEntity()时需要把值自动对entity进行初始化时才有必要放到此函数初始化，
		也就是说，这里初始化的所有属性都必须是在相应的.def中声明过的。
		
		@param section: PyDataSection, 根据一定的格式存储了entity属性的section
		"""
		SpaceCopy.onLoadEntityProperties_( self, section )
		
		self.birthPosition = section[ "Space" ][ "playerEnterPoint" ].readVector3( "pos" )
		self.birthDirection = section[ "Space" ][ "playerEnterPoint" ].readVector3( "direction" )
		self.challengeNos = [ int(i) for i in section[ "Space" ].readString( "challengeNo" ).split( "," ) ]
		
		self.doorPosition = section[ "Space" ][ "doorPoint" ].readVector3( "pos" )
		self.doorDirection = section[ "Space" ][ "doorPoint" ].readVector3( "direction" )

		self.doorProperty = {}
		self.doorProperty[ "useRectangle" ] = section[ "Space" ][ "doorPoint" ].readInt( "properties/useRectangle" )
		self.doorProperty[ "radius" ] = section[ "Space" ][ "doorPoint" ].readFloat( "properties/radius" )
		self.doorProperty[ "volume" ] = section[ "Space" ][ "doorPoint" ].readVector3( "properties/volume" )
		self.doorProperty[ "modelNumber" ] = section[ "Space" ][ "doorPoint" ].readString( "properties/modelNumber" )
		self.doorProperty[ "modelScale" ] = section[ "Space" ][ "doorPoint" ].readFloat( "properties/modelScale" )
		self.doorProperty[ "uname" ] = section[ "Space" ][ "doorPoint" ].readString( "properties/uname" )
	
	def load( self, section ):
		SpaceCopy.load( self, section )
		self.registerSelfToMgr()
		
	def registerSelfToMgr( self ):
		# 把自己注册到管理器
		if not len( self.challengeNos ):
			return
			
		if BigWorld.globalData.has_key( "SpaceChallengeMgr" ):
			BigWorld.globalData["SpaceChallengeMgr"].registerSpaceInfo( self.challengeNos, self.className, self.birthPosition, self.birthDirection )
		else: #如果管理器没启动
			ChallengeSpaceTempList = []
			ChallengeSpaceTempList.append( ( self.challengeNos, self.className, self.birthPosition, self.birthDirection ) )
			if BigWorld.globalData.has_key( "ChallengeSpaceTempList" ):
				ChallengeSpaceTempList.extend( BigWorld.globalData[ "ChallengeSpaceTempList" ] )
			
			BigWorld.globalData["ChallengeSpaceTempList"] = ChallengeSpaceTempList
			
	def initDoor( self ):
		doorInfo = self._spaceConfigInfo[ "Doormap" ]

	def packedDomainData( self, player ):
		"""
		@param player:	创建者实例
		"""
		data = {
				"spaceChallengeKey"	:	player.spaceChallengeKey,
				"spaceChallengeGate":	player.query( "spaceChallengeGate", None ),
				"dbID" 				: 	player.databaseID,
				}
		return data
	
	def packedSpaceDataOnEnter( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		"""
		packDict = SpaceCopy.packedSpaceDataOnEnter( self, entity )
		packDict[ "level" ] = entity.level
		packDict[ "challengeSpaceAvatar" ] = csconst.CHALLENGE_AVATAR_LIST.get( entity.getClass() )
		packDict[ "challengeSpaceType" ] = entity.query( "challengeSpaceType" )
		return packDict
	
	def canUseSkill( self, playerEntity, skillID ):
		avatarType = csconst.CHALLENGE_AVATAR_LIST.get( playerEntity.getClass() )
		if avatarType in self.spaceFixedSkill:
			if skillID in self.spaceFixedSkill[ avatarType ]:
				return True
			
		skillID = skillID / 1000
		if avatarType in self.spaceSkills:
			if skillID in self.spaceSkills[ avatarType ]:
				return True
				
		return False

	def createDoor( self, selfEntity ):
		"""
		副本通关，创建传送门
		"""
		e = BigWorld.createEntity( "SpaceDoorChallenge", selfEntity.spaceID, self.doorPosition, (0, 0, 0), self.doorProperty )
		if e != None:
			e.modelScale = self.doorProperty[ "modelScale" ]
	
	def createPiShanEnterNPC( self, selfEntity, level ):
		# 创建劈山副本的进入NPC
		if not selfEntity.queryTemp( "isCreateEnterPiShanNPC", False ):
			dict = {}
			dict[ "level" ] = level
			g_objFactory.getObject( PI_SHAN_ENTER_NPC ).createEntity(  selfEntity.spaceID, self.birthPosition, self.birthDirection, dict )
			selfEntity.setTemp( "isCreateEnterPiShanNPC", True )

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		if BigWorld.globalData.has_key( "SCC_piShanNPC_%s" % selfEntity.params[ "spaceChallengeKey" ] ):
			#查看沉香是否要创建
			if selfEntity.params[ "spaceChallengeGate" ] < 150: # 挑战副本最后是到150级150后是特殊功能副本
				level = BigWorld.globalData["SCC_piShanNPC_%s" % selfEntity.params[ "spaceChallengeKey" ] ]
				self.createPiShanEnterNPC( selfEntity, level )
			
		if selfEntity.queryTemp("firstPlayer", 0 ) == 0:
			spaceTime = BigWorld.globalData[ "SCC_time_%s" % selfEntity.params[ "spaceChallengeKey" ] ]
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEVEL, 		"" )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_COPY_TITLE, ""  )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME,  spaceTime )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, FUBEN_LIVING_TIME  )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_CHALLENGE_GATE, selfEntity.params[ "spaceChallengeGate" ]  )
			destroyTime = spaceTime + FUBEN_LIVING_TIME - time.time()
			#初始化玩家最多能在副本停留的时间
			selfEntity.addTimer( destroyTime, 0, KICK_PLAYER_KEY )
	
		SpaceCopy.onEnterCommon( self, selfEntity, baseMailbox, params )
		
		# init space skills
		baseMailbox.cell.requestInitSpaceSkill( baseMailbox.id )

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		SpaceCopy.onLeaveCommon( self, selfEntity, baseMailbox, params )
	
	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if userArg == KICK_PLAYER_KEY:
			for e in selfEntity._players:
				player = BigWorld.entities.get( e.id, None )
				if player is None:
					e.cell.challengeSpaceOnEnd()
				else:
					player.challengeSpaceOnEnd()
			return
			
		SpaceCopy.onTimer( self, selfEntity, id, userArg )
	
	def onLeaveTeam( self, playerEntity ):
		# 离开队伍回调
		if playerEntity.spaceChallengeKey:
			BigWorld.globalData["SpaceChallengeMgr"].playerLeave( playerEntity.spaceChallengeKey, playerEntity.base )
	
	def onConditionChange( self, selfEntity, params ):
		SpaceCopy.onConditionChange( self, params )
		# monsterType 2为大boss, 1为BOSS, 0为小怪
		monsterType = params[ "monsterType" ]
		if monsterType == 0:
			selfEntity.monsterNum -= 1
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, selfEntity.monsterNum  )
		elif monsterType == 1:
			selfEntity.bossNum -= 1
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, selfEntity.bossNum + selfEntity.bigBossNum  )
		elif monsterType == 2:
			selfEntity.bigBossNum -= 1
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, selfEntity.bossNum + selfEntity.bigBossNum  )
			BigWorld.globalData[ "SpaceChallengeMgr" ].callPiShanEnterNpc( selfEntity.params[ "spaceChallengeKey" ] )
		
		if selfEntity.monsterNum <= 0 and selfEntity.bossNum <= 0 and selfEntity.bigBossNum <= 0:
			self.onPassGate( selfEntity )

	def onPassGate( self, selfEntity ):
		# 当前副本只有四关，所以当第四关通过后，副本结束
		if selfEntity.params[ "spaceChallengeGate" ] == csconst.HUA_SHAN_PI_SHAN_GATE:
			BigWorld.globalData["SpaceChallengeMgr"].endChallenge( selfEntity.params[ "spaceChallengeKey" ] )
			
		if selfEntity.params[ "spaceChallengeGate" ] < 140:
			self.createDoor( selfEntity )
	
	def requestInitSpaceSkill( self, playerEntity ):
		# 角色技能需要随副本等级变化而变化，40级副本1级技能……140级副本-91级技能 
		avatarType = csconst.CHALLENGE_AVATAR_LIST.get( playerEntity.getClass() )
		playerEntity.client.initSpaceSkills( self.spaceSkills[ avatarType ], csdefine.SPACE_TYPE_CHALLENGE )
	
	def checkDomainLeaveEnable( self, entity ):
		"""
		在cell上检查该空间离开的条件
		例子：某场景在玩家没达到某目的时， 永远不允许离开， 比如监狱.
		"""
		if entity.queryTemp( "isChallengeGotoGate"):
			entity.removeTemp( "isChallengeGotoGate" )
			return csstatus.SPACE_OK
		
		if entity.isTeamCaptain() and entity.spaceChallengeKey:
			return csstatus.CHALLENGE_SPACE_LEAVE_IS_CAPTAIN
		
		return csstatus.SPACE_OK
