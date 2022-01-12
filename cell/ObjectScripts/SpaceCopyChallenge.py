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

from config import ChallengeAvatarSkills # ��������

FUBEN_LIVING_TIME = 60 * 60
KICK_PLAYER_KEY = 1000002
PI_SHAN_ENTER_NPC = "10121093"

class SpaceCopyChallenge( SpaceCopy ):
	"""
	"""
	def __init__( self ):
		SpaceCopy.__init__( self )
			
		self.spaceSkills = ChallengeAvatarSkills.Datas
		self.spaceFixedSkill = {} # �̶��ȼ�����
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
		���ݸ�����section����ʼ������ȡ��entity���ԡ�
		ע��ֻ����createEntity()ʱ��Ҫ��ֵ�Զ���entity���г�ʼ��ʱ���б�Ҫ�ŵ��˺�����ʼ����
		Ҳ����˵�������ʼ�����������Զ�����������Ӧ��.def���������ġ�
		
		@param section: PyDataSection, ����һ���ĸ�ʽ�洢��entity���Ե�section
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
		# ���Լ�ע�ᵽ������
		if not len( self.challengeNos ):
			return
			
		if BigWorld.globalData.has_key( "SpaceChallengeMgr" ):
			BigWorld.globalData["SpaceChallengeMgr"].registerSpaceInfo( self.challengeNos, self.className, self.birthPosition, self.birthDirection )
		else: #���������û����
			ChallengeSpaceTempList = []
			ChallengeSpaceTempList.append( ( self.challengeNos, self.className, self.birthPosition, self.birthDirection ) )
			if BigWorld.globalData.has_key( "ChallengeSpaceTempList" ):
				ChallengeSpaceTempList.extend( BigWorld.globalData[ "ChallengeSpaceTempList" ] )
			
			BigWorld.globalData["ChallengeSpaceTempList"] = ChallengeSpaceTempList
			
	def initDoor( self ):
		doorInfo = self._spaceConfigInfo[ "Doormap" ]

	def packedDomainData( self, player ):
		"""
		@param player:	������ʵ��
		"""
		data = {
				"spaceChallengeKey"	:	player.spaceChallengeKey,
				"spaceChallengeGate":	player.query( "spaceChallengeGate", None ),
				"dbID" 				: 	player.databaseID,
				}
		return data
	
	def packedSpaceDataOnEnter( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
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
		����ͨ�أ�����������
		"""
		e = BigWorld.createEntity( "SpaceDoorChallenge", selfEntity.spaceID, self.doorPosition, (0, 0, 0), self.doorProperty )
		if e != None:
			e.modelScale = self.doorProperty[ "modelScale" ]
	
	def createPiShanEnterNPC( self, selfEntity, level ):
		# ������ɽ�����Ľ���NPC
		if not selfEntity.queryTemp( "isCreateEnterPiShanNPC", False ):
			dict = {}
			dict[ "level" ] = level
			g_objFactory.getObject( PI_SHAN_ENTER_NPC ).createEntity(  selfEntity.spaceID, self.birthPosition, self.birthDirection, dict )
			selfEntity.setTemp( "isCreateEnterPiShanNPC", True )

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		if BigWorld.globalData.has_key( "SCC_piShanNPC_%s" % selfEntity.params[ "spaceChallengeKey" ] ):
			#�鿴�����Ƿ�Ҫ����
			if selfEntity.params[ "spaceChallengeGate" ] < 150: # ��ս��������ǵ�150��150�������⹦�ܸ���
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
			#��ʼ�����������ڸ���ͣ����ʱ��
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
		# �뿪����ص�
		if playerEntity.spaceChallengeKey:
			BigWorld.globalData["SpaceChallengeMgr"].playerLeave( playerEntity.spaceChallengeKey, playerEntity.base )
	
	def onConditionChange( self, selfEntity, params ):
		SpaceCopy.onConditionChange( self, params )
		# monsterType 2Ϊ��boss, 1ΪBOSS, 0ΪС��
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
		# ��ǰ����ֻ���Ĺأ����Ե����Ĺ�ͨ���󣬸�������
		if selfEntity.params[ "spaceChallengeGate" ] == csconst.HUA_SHAN_PI_SHAN_GATE:
			BigWorld.globalData["SpaceChallengeMgr"].endChallenge( selfEntity.params[ "spaceChallengeKey" ] )
			
		if selfEntity.params[ "spaceChallengeGate" ] < 140:
			self.createDoor( selfEntity )
	
	def requestInitSpaceSkill( self, playerEntity ):
		# ��ɫ������Ҫ�渱���ȼ��仯���仯��40������1�����ܡ���140������-91������ 
		avatarType = csconst.CHALLENGE_AVATAR_LIST.get( playerEntity.getClass() )
		playerEntity.client.initSpaceSkills( self.spaceSkills[ avatarType ], csdefine.SPACE_TYPE_CHALLENGE )
	
	def checkDomainLeaveEnable( self, entity ):
		"""
		��cell�ϼ��ÿռ��뿪������
		���ӣ�ĳ���������û�ﵽĳĿ��ʱ�� ��Զ�������뿪�� �������.
		"""
		if entity.queryTemp( "isChallengeGotoGate"):
			entity.removeTemp( "isChallengeGotoGate" )
			return csstatus.SPACE_OK
		
		if entity.isTeamCaptain() and entity.spaceChallengeKey:
			return csstatus.CHALLENGE_SPACE_LEAVE_IS_CAPTAIN
		
		return csstatus.SPACE_OK
