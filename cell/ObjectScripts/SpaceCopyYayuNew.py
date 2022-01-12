# -*- coding: gb18030 -*-

from SpaceCopyTeamTemplate import SpaceCopyTeamTemplate
import cschannel_msgs
from CopyContent import CopyContent
from CopyContent import CCKickPlayersProcess
from CopyContent import NEXT_CONTENT
from CopyContent import CCEndWait
import BigWorld
import csconst
import time
import csdefine
import ECBExtend
import csstatus
from config.server.YayuSpawnConfigScript import Datas as yayuMonster
from bwdebug import *


NUMBER_OF_YAYU_BOSS = 1
YAYU_DIED = 12456				# 猰貐死亡
STEP1_LAST_BATCH = 12457		# 第一阶段刷怪
STEP2_LAST_BATCH = 12458		# 第二阶段刷怪

class CCWait( CopyContent ):
	"""
	#等待
	"""
	def __init__( self ):
		"""
		"""
		self.key = "wait"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.addTimer( 5.0, 0, NEXT_CONTENT )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		return "reason" in params and params["reason"] == "timeOver"

class CCSpawnYayu( CopyContent ):
	"""
	#刷新猰貐
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanYayu"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.base.spawnYayu( spaceEntity.params["copyLevel"] )


	def onConditionChange( self, spaceEntity, params ):
		"""
		"""
		CopyContent.onConditionChange( self, spaceEntity, params )
		spaceEntity.base.setYayuID( params["yayuID"] )
		spaceEntity.setTemp("yayuID", params["yayuID"] )
		try:
			yayu = BigWorld.entities[ params["yayuID"] ]
			yayu.setHP( int( yayu.HP_Max * 0.5 ) )
		except:
			ERROR_MSG( "Space %i can't get Yayu by yuyuID %i") % ( spaceEntity.id, params["yayuID"] )

class CCTalkToYayu( CopyContent ):
	"""
	#和猰貐对话，暂时不使用，而是在对话里进行onConditionChange
	"""
	def __init__( self ):
		"""
		"""
		self.key = "talkToYayu"
		self.val = 1

class CCSpawnMonsterStep1( CopyContent ):
	"""
	#进入第一阶段
	"""
	def __init__( self ):
		"""
		"""
		self.key = "step1"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.addTimer( 1.0, 0, NEXT_CONTENT )
		spaceEntity.spawnDict.clear()
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_BATCH, "%i_%.2f" % ( 1, time.time() ) )
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE21%int(1), [] )

class CCSpawnMonster1( CopyContent ):
	"""
	#刷新怪物
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanMonster1"
		self.val = 1
		self.batch = 0

	def onContent( self, spaceEntity ):
		"""
		"""
		difficulty = spaceEntity.params[ "difficulty" ]
		self.batch =  spaceEntity.queryTemp( "step1_current_batch", 0 ) + 1
		if not yayuMonster[difficulty][1].has_key( self.batch ):
			self.batch = spaceEntity.queryTemp( "step1_current_batch" , 1 )
		spaceEntity.setTemp( "step1_current_batch" , self.batch )
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "batch" : self.batch, "step" : 1 , "difficulty": spaceEntity.params[ "difficulty" ] } )

		STEP_1_TIME = yayuMonster[difficulty][1][self.batch]["batch_time"]
		timerID = spaceEntity.addTimer( STEP_1_TIME, 0, STEP1_LAST_BATCH )
		spaceEntity.setTemp( "LAST_CONTENT_TIMER_ID", timerID )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_BATCH_TIME, "1_%i_%i"%(STEP_1_TIME,int(time.time())))
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE9, [] )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if "reason" in params and params["reason"] == "timeOver":
			return True
		return False

class CCSpawnMonsterStep2( CopyContent ):
	"""
	#进入第二阶段
	"""
	def __init__( self ):
		"""
		"""
		self.key = "step2"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.cancel( spaceEntity.popTemp( "LAST_CONTENT_TIMER_ID" ) )
		spaceEntity.addTimer( 10, 0, NEXT_CONTENT )
		spaceEntity.destroyMonsters()
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_BATCH, "%i_%.2f" % ( 2, time.time() ) )
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE21%int(2), [] )

class CCSpawnMonster2( CopyContent ):
	"""
	#第二阶段刷新怪物
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanMonster2"
		self.val = 1
		self.batch = 0

	def onContent( self, spaceEntity ):
		"""
		"""
		difficulty = spaceEntity.params[ "difficulty" ]
		self.batch =  spaceEntity.queryTemp( "step2_current_batch", 0 ) + 1
		if not yayuMonster[difficulty][2].has_key( self.batch ):
			self.batch = spaceEntity.queryTemp( "step2_current_batch" , 1 )
		spaceEntity.setTemp( "step2_current_batch" , self.batch )
		spaceEntity.base.spawnMonster( {"level" : spaceEntity.params["copyLevel"], "batch" : self.batch, "step" : 2 ,"difficulty": spaceEntity.params[ "difficulty" ] } )

		batch_time = yayuMonster[difficulty][2][self.batch]["batch_time"]								# 刷怪间隔
		batch_reduce = yayuMonster[difficulty][2][self.batch]["batch_reduce"]							# 每次刷怪递减时间
		min_interval = yayuMonster[difficulty][2][self.batch]["min_interval"]							# 最小刷怪间隔

		STEP_2_TIME = spaceEntity.queryTemp( "STEP_2_BATCH_TIME", batch_time + 10 ) - batch_reduce		#计算下次刷怪间隔
		if STEP_2_TIME <= min_interval:
			STEP_2_TIME = min_interval
		spaceEntity.setTemp( "STEP_2_BATCH_TIME", STEP_2_TIME )

		timerID = spaceEntity.addTimer( STEP_2_TIME, 0, STEP2_LAST_BATCH )
		spaceEntity.setTemp( "LAST_CONTENT_TIMER_ID", timerID )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_BATCH_TIME, "2_%i_%i"%( STEP_2_TIME,int(time.time())))
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE9, [] )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if "reason" in params and params["reason"] == "timeOver":
			return True
		return False

class CCSpawnMonsterStep3( CopyContent ):
	"""
	#进入第三阶段
	"""
	def __init__( self ):
		"""
		"""
		self.key = "step3"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.cancel( spaceEntity.popTemp( "LAST_CONTENT_TIMER_ID" ) )
		spaceEntity.addTimer( 10, 0, NEXT_CONTENT )
		spaceEntity.destroyMonsters()
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_BATCH, "%i_%.2f" % ( 3, time.time() ) )
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE21%int(3), [] )

class CCSpawnBoss( CopyContent ):
	"""
	#刷新BOSS
	"""
	def __init__( self ):
		"""
		"""
		self.key = "spwanBoss"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.base.spawnBoss( {"difficulty": spaceEntity.params[ "difficulty" ] ,"level" : spaceEntity.params["copyLevel"], "step" : 3, "batch" : 1 } )

		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE16, [] )
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.YA_YU_VOICE17, [] )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if "reason" in params and params["reason"] == "monsterDied" and params["monsterType"] == 1:
			count = spaceEntity.queryTemp("bossDiedCount", 0 )
			count += 1
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, NUMBER_OF_YAYU_BOSS - count )
			spaceEntity.setTemp("bossDiedCount", count )
			if NUMBER_OF_YAYU_BOSS == count:
				return True
		return False

class CCSuccess( CopyContent ):
	"""
	#成功拯救
	"""
	def __init__( self ):
		"""
		"""
		self.key = "success"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		#猰貐跳舞
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.YA_YU_VOICE4, [] )
		spaceEntity.addTimer( 60.0, 0, NEXT_CONTENT )
		self.createDoor( spaceEntity )
		yayu = BigWorld.entities.get( spaceEntity.queryTemp("yayuID", 0), None )
		if yayu is not None:
			yayu.onKillAllMonster()

	def createDoor( self, spaceEntity ):
		"""
		创建Door
		"""
		doordict = {"name" : cschannel_msgs.YA_YU_VOICE5}
		doordict["radius"] = 2.0
		doordict["destSpace"] = spaceEntity.params["spaceLabel"]
		doordict["destPosition"] = spaceEntity.params["position"]
		doordict["destDirection"] = ( 0, 0, 0 )
		doordict["modelNumber"] = "gw7504"
		doordict["modelScale"] = 25
		BigWorld.createEntity( "SpaceDoor", spaceEntity.spaceID, (13.308, 48.693, 120.754), (0, 0, 0), doordict )


	def doConditionChange(  self, spaceEntity, params ):
		"""
		对条件进行处理
		"""
		if "reason" in params and params["reason"] == "timeOver":
			return True

		return False

class SpaceCopyYayuNew( SpaceCopyTeamTemplate ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopyTeamTemplate.__init__( self )
		self.recordKey = "yayu_record_new"


	def initContent( self ):
		"""
		"""
		self.contents.append( CCWait() )
		self.contents.append( CCSpawnYayu() )
		self.contents.append( CCTalkToYayu() )
		self.contents.append( CCSpawnMonsterStep1() )
		self.contents.append( CCSpawnMonster1() )
		self.contents.append( CCSpawnMonsterStep2() )
		self.contents.append( CCSpawnMonster2() )
		self.contents.append( CCSpawnMonsterStep3() )
		self.contents.append( CCSpawnBoss() )
		self.contents.append( CCSuccess() )
		self.contents.append( CCEndWait() )
		self.contents.append( CCKickPlayersProcess() )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		某role在该副本中死亡,若30秒内未复活则回城复活
		"""
		role.addTimer( 30.0, 0, ECBExtend.WAIT_ROLE_REVIVE_CBID )

	def packedDomainData( self, player ):
		"""
		"""
		captain = BigWorld.entities.get( player.captainID )
		if captain:
			level = captain.level
		else:
			level = 0
		data = {"copyLevel"			: 	level,
				"dbID" 				: 	player.databaseID,
				"teamID" 			: 	player.teamMailbox.id,
				"captainDBID"		:	player.getTeamCaptainDBID(),
				"spaceLabel"		:	BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_KEY ),
				"position"			:	player.position,
				"difficulty"		:	player.queryTemp( "EnterSpaceCopyYayuType" ),
				"spaceKey"			:	player.teamMailbox.id,
				}
		return data

	def packedSpaceDataOnEnter( self, player ):
		"""
		"""
		packDict = SpaceCopyTeamTemplate.packedSpaceDataOnEnter( self, player )
		if player.teamMailbox:
			packDict[ "teamID" ] = player.teamMailbox.id

		packDict[ "dbID" ] = player.databaseID
		return packDict

	def onStartContent( self, selfEntity, baseMailbox, params ):
		"""
		"""
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_BATCH_TIME, "" )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, NUMBER_OF_YAYU_BOSS )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_YAYU_NEW_HP, 50 )

		selfEntity.setTemp("bossDiedCount", 0 )

		SpaceCopyTeamTemplate.onStartContent( self, selfEntity, baseMailbox, params )

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		if baseMailbox and params[ "databaseID" ] not in selfEntity._enterRecord:
			baseMailbox.cell.remoteAddActivityCount( selfEntity.id, csdefine.ACTIVITY_ZHENG_JIU_YA_YU_NEW, self.recordKey )
			
		SpaceCopyTeamTemplate.onEnterCommon( self, selfEntity, baseMailbox, params )
		baseMailbox.cell.checkTeamInCopySpace( selfEntity.base )

	def onYayuDie( self, selfEntity ):
		"""
		"""
		selfEntity.addTimer( 10.0, 0, YAYU_DIED )
		for e in selfEntity._players:						#通知玩家猰貐死亡了
			if BigWorld.entities.has_key( e.id ):
				e.client.onStatusMessage( csstatus.TASK_FAIL_FOR_YAYU_DIE, "" )
			else:
				#e.cell.gotoForetime()
				pass

	def onYayuHPChange( self, selfEntity, hp, hp_Max ):
		"""
		"""
		percent = int(hp*1.0/ hp_Max*100)
		if  int( BigWorld.getSpaceDataFirstForKey( selfEntity.spaceID, csconst.SPACE_SPACEDATA_YAYU_NEW_HP ) ) == percent:
			return
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_YAYU_NEW_HP, percent )

	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if userArg == YAYU_DIED:
			for e in selfEntity._players:
				if BigWorld.entities.has_key( e.id ):
					BigWorld.entities[ e.id ].gotoForetime()
				else:
					e.cell.gotoForetime()
			return

		if userArg == STEP1_LAST_BATCH or userArg == STEP2_LAST_BATCH:					# 阶段内刷怪
			self.getCurrentContent( selfEntity ).onContent(  selfEntity )

		SpaceCopyTeamTemplate.onTimer( self, selfEntity, id, userArg )
