# -*-coding:gb18030 -*-

from bwdebug import *
from SpaceCopyTeam import SpaceCopyTeam
import BigWorld
import csconst
import time
import csdefine
import Const

PREPARE_CLOSE_SPACE_USERAGE = 1
BOSSCOUNT					= 1

class SpaceCopyTeachKillMonster( SpaceCopyTeam ):
	"""
	"""
	def __init__( self ):
		SpaceCopyTeam.__init__( self )
		self.masterSkillList = []			# 师父的副本专属技能
		self.prenticeSkillList = []			# 徒弟的副本专属技能
		self.warTotalTime = 0			# 副本持续时间
		self.doorData = {}

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		初始化自己的entity的数据
		"""
		#DEBUG_MSG( "--->>>self.params",selfEntity.params.items() )
		SpaceCopyTeam.initEntity( self, selfEntity )
		selfEntity.addTimer( self.warTotalTime, 0, PREPARE_CLOSE_SPACE_USERAGE )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_TEACH_MONSTER_LEVEL, selfEntity.params["monsterLevel"] )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, csconst.TEACH_SPACE_MONSTER_COUNT )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, time.time() )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, self.warTotalTime )
		selfEntity.setTemp( "bossCount", BOSSCOUNT )	# 副本可刷boss的个数为BOSSCOUNT

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopyTeam.onEnterCommon( self, selfEntity, baseMailbox, params )
		if params["isMaster"]:
			baseMailbox.client.initSpaceSkills( self.masterSkillList, csdefine.SPACE_TYPE_TEACH_KILL_MONSTER )
		else:
			baseMailbox.client.initSpaceSkills( self.prenticeSkillList, csdefine.SPACE_TYPE_TEACH_KILL_MONSTER )
		baseMailbox.cell.teach_enterKillMonsterSpaceSuccess()

	def packedSpaceDataOnEnter( self, playerEntity ):
		"""
		打包玩家进入空间时的数据
		"""
		# 玩家如果在师徒副本中上线，此时关系数据有可能还没初始化完毕，仅仅根据iAmMaster判断是否师父是不准确的
		# 目前暂时通过玩家的级别来判断是否师父，以后会修改空间进入机制，在玩家的数据加载完毕后才会进入空间。
		packDict = SpaceCopyTeam.packedSpaceDataOnEnter( self, playerEntity )
		packDict[ "dbID" ] = playerEntity.databaseID
		packDict[ "isMaster" ] = playerEntity.iAmMaster() or playerEntity.level >= csconst.TEACH_MASTER_MIN_LEVEL
		return packDict

	def packedDomainData( self, entity ):
		"""
		打包向domain申请进入空间时的数据
		"""
		members = entity.getAllMemberInRange( csconst.TEACH_SPACE_ENTER_TEAMMATE_DISTANCE )
		totalLevel = 0
		for player in members:
			totalLevel += player.level
		playerCount = len( members )
		monsterLevel = totalLevel / playerCount

		d = { 'dbID' : entity.databaseID }
		if entity.teamMailbox:
			# 已加入队伍，取队伍数据
			d["teamID"] = entity.teamMailbox.id
			d["captainDBID"] = entity.getTeamCaptainDBID()
			d["membersDBID"] = entity.getTeamMemberDBIDs()
			d["monsterLevel"] = monsterLevel
			d["playerCount"] = playerCount
			d["spaceKey"]	 = entity.teamMailbox.id
		return d

	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		根据给定的section，初始化（读取）entity属性。
		注：只有在createEntity()时需要把值自动对entity进行初始化时才有必要放到此函数初始化，
		也就是说，这里初始化的所有属性都必须是在相应的.def中声明过的。

		@param section: PyDataSection, 根据一定的格式存储了entity属性的section
		"""
		SpaceCopyTeam.onLoadEntityProperties_( self, section )
		self.masterSkillList = [ int( skillID ) for skillID in section.readString( "masterSkills" ).split( ";" ) ]
		self.prenticeSkillList = [ int( skillID ) for skillID in section.readString( "prenticeSkills" ).split( ";" ) ]
		self.warTotalTime = section.readFloat( "warTotalTime" )
		doorSection = section["Door"]
		self.doorData["name"] = doorSection.readString( "name" )
		self.doorData["position"] = doorSection.readVector3( "Pos" )
		self.doorData["radius"] = doorSection.readFloat("radius")
		self.doorData["destSpace"] = doorSection.readString("DestSpace")
		self.doorData["destPosition"] = doorSection.readVector3("DestPos")
		self.doorData["modelNumber"] = doorSection.readString("modelNumber")
		self.doorData["modelScale"] = doorSection.readFloat("modelScale")

	def canUseSkill( self, playerEntity, skillID ):
		"""
		"""
		if playerEntity.iAmMaster():
			return skillID in self.masterSkillList
		else:
			return skillID in self.prenticeSkillList

	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if userArg == PREPARE_CLOSE_SPACE_USERAGE:	# 先把玩家传送出副本，10秒后关闭空间
			for playerBase in selfEntity._players:
				playerBase.cell.gotoForetime()
			#selfEntity.base.closeSpace( True )
			selfEntity.addTimer( 10, 0, Const.SPACE_TIMER_ARG_CLOSE )
		else:
			SpaceCopyTeam.onTimer( self, selfEntity, id, userArg )

	def createDoor( self, selfEntity ):
		"""
		创建离开副本的传送门
		"""
		BigWorld.createEntity( "SpaceDoor", selfEntity.spaceID, self.doorData["position"], (0, 0, 0), self.doorData )
		#if otherDict.has_key( 'modelScale' ) and otherDict[ 'modelScale' ] != 0.0:
		#	door.modelScale = otherDict[ 'modelScale' ]

	def onLeaveTeam( self, playerEntity ):
		"""
		玩家离开队伍的处理
		"""
		playerEntity.gotoForetime()

	def requestInitSpaceSkill( self, playerEntity ):
		"""
		初始化副本技能
		"""
		if playerEntity.iAmMaster():
			playerEntity.client.initSpaceSkills( self.masterSkillList, csdefine.SPACE_TYPE_TEACH_KILL_MONSTER )
		else:
			playerEntity.client.initSpaceSkills( self.prenticeSkillList, csdefine.SPACE_TYPE_TEACH_KILL_MONSTER )
