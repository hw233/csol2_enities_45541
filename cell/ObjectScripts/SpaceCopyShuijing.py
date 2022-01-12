# -*- coding: gb18030 -*-
#


import BigWorld
import cschannel_msgs
import ShareTexts as ST
from SpaceCopyTemplate import SpaceCopyTemplate
from SpaceCopy import SpaceCopy
import random
import time
import ECBExtend
import csdefine
import csconst
import csstatus
import utils
import copy

from bwdebug import *
from CopyContent import NEXT_CONTENT
from CopyContent import CopyContent
from CopyContent import CCWait
from CopyContent import CCEndWait
from CopyContent import CCKickPlayersProcess
from GameObject import GameObject
from Resource.PatrolMgr import PatrolMgr
from GameObjectFactory import g_objFactory
g_patrolMgr = PatrolMgr.instance()

SPAWN_MONSTER 		= 1 											#刷怪
FINISH_SHUIJING 	= 2												#完成水晶副本
SPAWN_MONSTER_BOSS	= 3												#刷大BOSS
CLOSE_SHUIJING		= 4												#副本结束
CLOSE_MAP			= 5												#删除副本地图
MOVE_OUT			= 6												#移出玩家
SHUIJING_COUNT		= 0											#水晶怪物数量
CALCULATE_MONSTER	= 10											#计算水晶怪物数量
NOTICE_SEND_AI_COMMAND		= 13									#通知光柱发送AI指令
NOTICE_PLAYER				= 15									#刷怪通知玩家

CHECKPOINTS_1		= 1												#第一关
CHECKPOINTS_2		= 2												#第二关
CHECKPOINTS_3		= 3												#第三关
GROUP				= 0												#第一波
GROUP_4				= 3												#第四波
CHECKPOINT_LIST		= [ CHECKPOINTS_1, CHECKPOINTS_2, CHECKPOINTS_3 ]	#所有关卡


SPAWN_MONSTER_INTERVAL				= 25.0					#25秒刷出下一波
SPAWN_MONSTER_INTERVAL_LIST			= [ 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30 ]			#第一波刷怪时间间隔列表
SPAWN_MONSTER2_INTERVAL		 	= 15.0								#前期刷怪速度，1-100颗，每7秒刷新一个；

SPAWN_MONSTER3_LAST_COUNT			= 5								#第三关一波剩余怪数量达到该值就开始刷下一波


SPAWN_SPEED_CHANGE_COUNT_FIRST	= 100								#刷怪速度改变的刷怪数
SPAWN_SPEED_CHANGE_COUNT_SECOND	= 180								#刷怪速度改变的刷怪数

ROOM1_VALUE						= 0									#房间一刷怪数
ROOM2_VALUE						= 0									#房间二刷怪数
ROOM3_VALUE						= 0									#房间三刷怪数
RANDOM_GROUP_NUM				= 2									#第三关随机选择的怪物的总的组数
GUANG_ZHU						= "20251118"						#光柱className
GUANG_ZHU_POSITION				= ( 376.700623, 34.745525, -35.112717 )			#光柱产生位置
GUANG_ZHU_DIRECTION				= ( 0, 0, 1 )						#光柱产生朝向
AI_COMMAND_ID_LIST				= [ 20, 30, 40 ]					#AI指令ID列表
MP3_PATH_LIST					= [ "chuangshi1387/21/21pbai3", "chuangshi1387/21/21pbai1", "chuangshi1387/21/21pbai2" ]
ROLE_NUM_LIMIT					= 3									#玩家上限数量

class CCRoom1( CopyContent ):
	"""
	第一关
	"""
	def __init__( self ):
		"""
		"""
		self.key = "room1"
		self.val = 1

	def onMonsterDie( self, spaceEntity, params ):
		"""
		"""
		spaceEntity.dieMonsterCount += 1
		for e in spaceEntity._players:
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].client.onStatusMessage( csstatus.MONSTER_KILLED_AMOUNT, str(( spaceEntity.dieMonsterCount, )) )
		if spaceEntity.dieMonsterCount == spaceEntity.shuijingMonsterCount:
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, spaceEntity.shuijingMonsterCount - spaceEntity.dieMonsterCount )
			spaceEntity.addTimer( 10.0, 0.0, NEXT_CONTENT )
			return
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, spaceEntity.shuijingMonsterCount - spaceEntity.dieMonsterCount )


	def endContent( self, spaceEntity ):
		"""
		内容结束
		"""
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", cschannel_msgs.SHUIJING_INFO_7, [])
		spaceEntity.setTemp( 'randGroup', str(CHECKPOINTS_2) + "and" + str(GROUP) )
		spaceEntity.getScript().checkPointTransition( spaceEntity, CHECKPOINTS_1 )
		CopyContent.endContent( self, spaceEntity )
		pass

	def onTimer( self, spaceEntity, id, userArg ):
		"""
		处理所有水晶副本维护工作
		"""
		if userArg == CALCULATE_MONSTER:
			spaceEntity.getScript().calCheckPointMonsterCount( spaceEntity, CHECKPOINTS_1 )
			pass
		elif userArg == SPAWN_MONSTER:											#刷怪
			self.spawnOneCheckPointMonster( spaceEntity )
			pass

		elif userArg == NEXT_CONTENT:
			self.endContent( spaceEntity )

		else:
			CopyContent.onTimer( self, spaceEntity, id, userArg )

	def spawnOneCheckPointMonster( self, spaceEntity ):
		"""
		刷新第一关卡怪物
		"""
		groupList = list( spaceEntity.queryTemp('groupCount', set([])) )		#需要刷怪的组数
		randGroup = spaceEntity.queryTemp( 'randGroup', str(CHECKPOINTS_1) + "and" + str(GROUP) )					#当前刷怪组数

		if randGroup in groupList:
			group = int(randGroup.split("and")[1])
			if randGroup == str(CHECKPOINTS_1) + "and" + str(GROUP):
				for e in spaceEntity._players:
					if BigWorld.entities.has_key( e.id ):
						BigWorld.entities[ e.id ].client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", cschannel_msgs.SHUIJING_INFO_5, [])
			elif randGroup == str(CHECKPOINTS_1) + "and" + str(GROUP_4):
				for e in spaceEntity._players:
					if BigWorld.entities.has_key( e.id ):
						BigWorld.entities[ e.id ].client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", cschannel_msgs.SHUIJING_INFO_6, [])
			randGroupSpawns = spaceEntity.queryTemp( randGroup )				#第几组刷怪点
			for i in xrange( 0, len( randGroupSpawns ) ):
				monsterSpawn 	= randGroupSpawns[i]
				spaceEntity.spawnMonsterCount += 1
				params = { "level": spaceEntity.shuijing_level, "randGroup": randGroup }
				monsterSpawn.cell.createEntity( params )
			spaceEntity.queryTemp('groupCount', set([])).remove( randGroup )
			key = str(CHECKPOINTS_1) + "and" + str( group + 1 )
			spaceEntity.setTemp( 'randGroup', key)
			if key in groupList:
				if group < len(SPAWN_MONSTER_INTERVAL_LIST):
					spaceEntity.addTimer( SPAWN_MONSTER_INTERVAL_LIST[ group ], 0.0, SPAWN_MONSTER )
		else:
			if len( groupList ) == 0:
				return

class CCRoom2( CopyContent ):
	"""
	第二关
	"""
	def __init__( self ):
		"""
		"""
		self.key = "room2"
		self.val = 1
		self.monsterCountList = []
	

	def onMonsterDie( self, spaceEntity, params ):
		"""
		"""
		spaceEntity.dieMonsterCount += 1
		for e in spaceEntity._players:
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].client.onStatusMessage( csstatus.MONSTER_KILLED_AMOUNT, str(( spaceEntity.dieMonsterCount, )) )
		if spaceEntity.dieMonsterCount == spaceEntity.shuijingMonsterCount:
			spaceEntity.addTimer( 0.0, 0.0, SPAWN_MONSTER_BOSS )
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, spaceEntity.shuijingMonsterCount - spaceEntity.dieMonsterCount )
			return
		elif spaceEntity.dieMonsterCount == spaceEntity.shuijingMonsterCount + 1:
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 0 )
			spaceEntity.addTimer( 10.0, 0.0, NEXT_CONTENT )
			return
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, spaceEntity.shuijingMonsterCount - spaceEntity.dieMonsterCount )

	def endContent( self, spaceEntity ):
		"""
		内容结束
		"""
		spaceEntity.setTemp( 'randGroup', str(CHECKPOINTS_3) + "and" + str(GROUP) )
		spaceEntity.getScript().checkPointTransition( spaceEntity, CHECKPOINTS_2 )
		spaceEntity.setTemp( "shuijing_SpawnMonster", False )
		CopyContent.endContent( self, spaceEntity )
		pass

	def onTimer( self, spaceEntity, id, userArg ):
		"""
		处理所有水晶副本维护工作
		"""
		if userArg == CALCULATE_MONSTER:
			spaceEntity.getScript().calCheckPointMonsterCount( spaceEntity, CHECKPOINTS_2 )
			pass
		elif userArg == SPAWN_MONSTER:											#刷怪
			self.spawnTwoCheckPointMonster( spaceEntity )
			pass
			
		elif userArg == SPAWN_MONSTER_BOSS:										#刷BOSS
			spawnMB = spaceEntity.queryTemp( str(CHECKPOINTS_2) + "and" +"-1" ).pop()
			spawnMB.cell.remoteCallScript( "spawnBoss", [ spaceEntity.shuijing_level + 3, str(CHECKPOINTS_2) ] )
			pass

		elif userArg == NEXT_CONTENT:
			self.endContent( spaceEntity )

		else:
			CopyContent.onTimer( self, spaceEntity, id, userArg )

	def spawnTwoCheckPointMonster( self, spaceEntity ):
		"""
		刷新第二关卡怪物
		"""
		groupList = list( spaceEntity.queryTemp('groupCount', set([])) )		#需要刷怪的组数
		randGroup = spaceEntity.queryTemp( 'randGroup', str(CHECKPOINTS_2) + "and" + str(GROUP) )					#当前刷怪组数

		if randGroup in groupList:
			group = int(randGroup.split("and")[1])
			for e in spaceEntity._players:
				if BigWorld.entities.has_key( e.id ):
					BigWorld.entities[ e.id ].client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", cschannel_msgs.SHUIJING_INFO_4%str( group+1 ), [])
			randGroupSpawns = spaceEntity.queryTemp( randGroup )				#第几组刷怪点
			for i in xrange( 0, len( randGroupSpawns ) ):
				monsterSpawn 	= randGroupSpawns[i]
				spaceEntity.spawnMonsterCount += 1
				params = { "level": spaceEntity.shuijing_level, "randGroup": randGroup }
				monsterSpawn.cell.createEntity( params )
			if randGroup == str(CHECKPOINTS_2) + "and" + str(GROUP):
				for e in spaceEntity._players:
					if BigWorld.entities.has_key( e.id ):
						BigWorld.entities[ e.id ].client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", cschannel_msgs.SHUIJING_INFO_3, [])
			spaceEntity.queryTemp('groupCount', set([])).remove( randGroup )
			key = str(CHECKPOINTS_2) + "and" + str( int(randGroup.split("and")[1]) + 1 )
			spaceEntity.setTemp( 'randGroup', key)
			if key in groupList:
				spaceEntity.addTimer( SPAWN_MONSTER_INTERVAL, 0.0, SPAWN_MONSTER )
		else:
			if len( groupList ) == 0:
				return

class CCRoom3( CopyContent ):
	"""
	第三关
	"""
	def __init__( self ):
		"""
		"""
		self.key = "room3"
		self.val = 1
	
	def onContent( self, spaceEntity ):
		"""
		内容开始执行
		"""
		for e in spaceEntity._players:
			e.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", cschannel_msgs.SHUIJING_INFO_2, [])

	def onMonsterDie( self, spaceEntity, params ):
		"""
		"""
		spaceEntity.dieMonsterCount += 1
		for e in spaceEntity._players:
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].client.onStatusMessage( csstatus.MONSTER_KILLED_AMOUNT, str(( spaceEntity.dieMonsterCount, )) )
		randGroup = spaceEntity.queryTemp( 'randGroup', str(CHECKPOINTS_3) + "and" + str(GROUP) )
		index = int( randGroup.split("and")[1] ) - 1
		DEBUG_MSG("shuijing:randGroup is %s,spaceEntity.id is %s"%( randGroup, spaceEntity.id ))
		monsterCountList = spaceEntity.queryTemp( "monsterCountList", [] )
		if index >= 0 and index < len( monsterCountList ) and spaceEntity.dieMonsterCount == monsterCountList[ index ]:
			spaceEntity.addTimer( 5.0, 0.0, SPAWN_MONSTER )
			spaceEntity.addTimer( 0.0, 0.0, NOTICE_PLAYER )
			spaceEntity.addTimer( 0.0, 0.0, NOTICE_SEND_AI_COMMAND )
		elif spaceEntity.dieMonsterCount == spaceEntity.shuijingMonsterCount:
			spaceEntity.addTimer( 5.0, 0.0, SPAWN_MONSTER_BOSS )
			spaceEntity.addTimer( 0.0, 0.0, NOTICE_PLAYER )
			spaceEntity.addTimer( 0.0, 0.0, NOTICE_SEND_AI_COMMAND )
		elif spaceEntity.dieMonsterCount == spaceEntity.shuijingMonsterCount + 1:
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 0 )
			spaceEntity.addTimer( 10.0, 0.0, NEXT_CONTENT )
			return

		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, spaceEntity.shuijingMonsterCount - spaceEntity.dieMonsterCount )

	def endContent( self, spaceEntity ):
		"""
		内容结束
		"""
		spaceEntity.removeTemp( "shuijing_SpawnMonster" )
		BigWorld.globalData[ "ShuijingManager" ].endShuijing( spaceEntity.params[ "shuijingKey" ] )
		#CopyContent.endContent( self, spaceEntity )
		pass

	def onTimer( self, spaceEntity, id, userArg ):
		"""
		处理所有水晶副本维护工作
		"""
		if userArg == CALCULATE_MONSTER:
			spaceEntity.getScript().calCheckPointMonsterCount( spaceEntity, CHECKPOINTS_3 )
			pass
		elif userArg == SPAWN_MONSTER:											#刷怪
			self.spawnThreeCheckPointMonster( spaceEntity )
			pass

		elif userArg == SPAWN_MONSTER_BOSS:										#刷BOSS
			spawnMB = spaceEntity.queryTemp( str(CHECKPOINTS_3) + "and" +"-1" ).pop()
			spawnMB.cell.remoteCallScript( "spawnBoss", [ spaceEntity.shuijing_level + 3, str(CHECKPOINTS_3) ] )
			randGroup = spaceEntity.queryTemp( 'randGroup', str(CHECKPOINTS_3) + "and" + str(GROUP) )
			key = str(CHECKPOINTS_3) + "and" + str( int(randGroup.split("and")[1]) + 1 )
			spaceEntity.setTemp( 'randGroup', key)

		elif userArg == NOTICE_SEND_AI_COMMAND:
			self.noticeSendAICommand( spaceEntity )
		
		elif userArg == NOTICE_PLAYER:
			randGroup = spaceEntity.queryTemp( 'randGroup', str(CHECKPOINTS_3) + "and" + str(GROUP) )
			msg = ""
			mp3_path = ""
			npcID = spaceEntity.queryTemp( "guangzhu", 0 )
			monster = BigWorld.entities.get( npcID )
			if int(randGroup.split("and")[1]) == 0:
				msg = cschannel_msgs.SHUIJING_INFO_8
				mp3_path = MP3_PATH_LIST[0]
			elif int(randGroup.split("and")[1]) == 1:
				msg = cschannel_msgs.SHUIJING_INFO_9
				mp3_path = MP3_PATH_LIST[1]
			elif int(randGroup.split("and")[1]) == 2:
				msg = cschannel_msgs.SHUIJING_INFO_10
				mp3_path = MP3_PATH_LIST[2]
			if npcID and monster:
				monster.planesAllClients( "onMakeASound", ( mp3_path, 0 ) )
			for e in spaceEntity._players:
				if BigWorld.entities.has_key( e.id ):
					BigWorld.entities[ e.id ].client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", msg, [])
					
		elif userArg == NEXT_CONTENT:
			self.endContent( spaceEntity )

		else:
			CopyContent.onTimer( self, spaceEntity, id, userArg )

	def spawnThreeCheckPointMonster( self, spaceEntity ):
		"""
		刷新第三关卡怪物
		"""
		groupList = list( spaceEntity.queryTemp('groupCount', set([])) )		#需要刷怪的组数
		randGroup = spaceEntity.queryTemp( 'randGroup', str(CHECKPOINTS_3) + "and" + str(GROUP) )					#当前刷怪组数

		if randGroup in groupList:
			randGroupSpawns = spaceEntity.queryTemp( randGroup )				#第几组刷怪点
			randomGroupList = spaceEntity.queryTemp( "randomGroupList", [] )
			tempClassNameList = []
			if randomGroupList:
				index = int(randGroup.split("and")[1])
				if index > len( randomGroupList ):
					ERROR_MSG("spawn point group is larger than RANDOM_GROUP_NUM,group is %s,RANDOM_GROUP_NUM is %s"%( index, RANDOM_GROUP_NUM ) )
					return
				tempClassNameList = randomGroupList[ index ].split(",")
			monsterCountList = spaceEntity.queryTemp( "monsterCountList", [] )
			monsterCountList.append( len( randGroupSpawns ) * len( tempClassNameList ) )
			spaceEntity.setTemp( "monsterCountList", monsterCountList )
			for i in xrange( 0, len( randGroupSpawns ) ):
				monsterSpawn 	= randGroupSpawns[i]
				spaceEntity.spawnMonsterCount += 1
				monsterSpawn.cell.remoteCallScript( "spawnThirdGroupMonster", [ spaceEntity.shuijing_level, randGroup, tempClassNameList ] )
			spaceEntity.queryTemp('groupCount', set([])).remove( randGroup )
			key = str(CHECKPOINTS_3) + "and" + str( int(randGroup.split("and")[1]) + 1 )
			spaceEntity.setTemp( 'randGroup', key)
		else:
			if len( groupList ) == 0:
				return

	def noticeSendAICommand( self, spaceEntity ):
		"""
		通知光柱发送AI指令
		"""
		npcID = spaceEntity.queryTemp( "guangzhu", 0 )
		randGroup = spaceEntity.queryTemp( 'randGroup', str(CHECKPOINTS_3) + "and" + str(GROUP) )
		index = int( randGroup.split("and")[1] )
		DEBUG_MSG("shuijing:randGroup is %s,spaceEntity.id is %s"%( randGroup, spaceEntity.id ))
		monster = BigWorld.entities.get( npcID )
		if npcID and monster and index < len( AI_COMMAND_ID_LIST ):
			monster.sendAICommand( monster.id, AI_COMMAND_ID_LIST[ index ] )
	
	def noticePlayerAndPlaySound( self, spaceEntity ):
		"""
		通知玩家同时播放语音
		"""
		randGroup = spaceEntity.queryTemp( 'randGroup', str(CHECKPOINTS_3) + "and" + str(GROUP) )
		msg = ""
		mp3_path = ""
		npcID = spaceEntity.queryTemp( "guangzhu", 0 )
		monster = BigWorld.entities.get( npcID )
		if int(randGroup.split("and")[1]) == 0:
			msg = cschannel_msgs.SHUIJING_INFO_8
			mp3_path = MP3_PATH_LIST[0]
		elif int(randGroup.split("and")[1]) == 1:
			msg = cschannel_msgs.SHUIJING_INFO_9
			mp3_path = MP3_PATH_LIST[1]
		elif int(randGroup.split("and")[1]) == 2:
			msg = cschannel_msgs.SHUIJING_INFO_10
			mp3_path = MP3_PATH_LIST[2]
		if npcID and monster:
			monster.planesAllClients( "onMakeASound", ( mp3_path, 0 ) )
		for e in spaceEntity._players:
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", msg, [])


class SpaceCopyShuijing( SpaceCopyTemplate ):
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopyTemplate.__init__( self )
		self.isSpaceCalcPkValue = True
		self.isSpaceDesideDrop = True
		self.recordKey = "shuijing_record"
		self.checkPoint = 0
		self.birthPositionDict = {}
		self.birthDirectionDict = {}
		self.monsterCountList = []
		self.randomGroupList = []
		self.thirdGroupShuiingCountList = []
		self.flyTeleportTrapDict = {}
		self.leaveTrapDict = {}
		
	def initContent( self ):
		"""
		"""
		self.contents.append( CCRoom1() )
		self.contents.append( CCRoom2() )
		self.contents.append( CCRoom3() )
	
	def registerSelfToMgr( self, checkPoint ):
		if BigWorld.globalData.has_key("ShuijingManager"):
			BigWorld.globalData["ShuijingManager"].registerShuijingInfo( checkPoint, self.className, self.birthPositionDict[ checkPoint ], self.birthDirectionDict[ checkPoint ] )
		else:
			shuijingTempList = []
			shuijingTempList.append( ( checkPoint, self.className, self.birthPositionDict[ checkPoint ], self.birthDirectionDict[ checkPoint ] ) )
			if BigWorld.globalData.has_key( "shuijingTempList" ):
				shuijingTempList.extend( BigWorld.globalData[ "shuijingTempList" ] )
			BigWorld.globalData[ "shuijingTempList" ] = shuijingTempList
		
	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		SpaceCopyTemplate.load( self, section )
		for checkPoint in CHECKPOINT_LIST:
			self.registerSelfToMgr( checkPoint )
		
	def onLoadEntityProperties_( self, section ):
		SpaceCopyTemplate.onLoadEntityProperties_( self, section )
		for playerEnterSect in section["Space"]["playerEnterPoint"].values():
			self.birthPositionDict[ playerEnterSect["checkPoint"].asInt ] = playerEnterSect[ "pos" ].asVector3
			self.birthDirectionDict[ playerEnterSect["checkPoint"].asInt ] = playerEnterSect[ "direction" ].asVector3
		if section[ "Space" ].has_key( "randomGroup" ):
			self.randomGroupList = section[ "Space" ][ "randomGroup" ].asString.split(";")
		for trapSect in section[ "Space" ][ "FlyTeleportTrapInfo" ].values():
			checkPoint = trapSect[ "checkPoint" ].asInt
			if not self.flyTeleportTrapDict.has_key( checkPoint ):
				self.flyTeleportTrapDict[ checkPoint ] = {}
				self.flyTeleportTrapDict[ checkPoint ][ "enterTrap" ] = {}
				self.flyTeleportTrapDict[ checkPoint ][ "leaveTrap" ] = {}
			#飞行开始陷阱数据
			self.flyTeleportTrapDict[ checkPoint ][ "enterTrap" ][ "lifetime" ] = trapSect[ "enterTrap" ][ "lifetime" ].asFloat
			self.flyTeleportTrapDict[ checkPoint ][ "enterTrap" ][ "radius" ] = trapSect[ "enterTrap" ][ "radius" ].asFloat
			self.flyTeleportTrapDict[ checkPoint ][ "enterTrap" ][ "enterSpell" ] = trapSect[ "enterTrap" ][ "enterSpell" ].asInt
			self.flyTeleportTrapDict[ checkPoint ][ "enterTrap" ][ "leaveSpell" ] = trapSect[ "enterTrap" ][ "leaveSpell" ].asInt
			self.flyTeleportTrapDict[ checkPoint ][ "enterTrap" ][ "modelNumber" ] = trapSect[ "enterTrap" ][ "modelNumber" ].asString
			self.flyTeleportTrapDict[ checkPoint ][ "enterTrap" ][ "isDisposable" ] = trapSect[ "enterTrap" ][ "isDisposable" ].asInt
			self.flyTeleportTrapDict[ checkPoint ][ "enterTrap" ][ "position" ] = trapSect[ "enterTrap" ][ "position" ].asVector3
			#飞行结束陷阱数据
			self.flyTeleportTrapDict[ checkPoint ][ "leaveTrap" ][ "lifetime" ] = trapSect[ "leaveTrap" ][ "lifetime" ].asFloat
			self.flyTeleportTrapDict[ checkPoint ][ "leaveTrap" ][ "radius" ] = trapSect[ "leaveTrap" ][ "radius" ].asFloat
			self.flyTeleportTrapDict[ checkPoint ][ "leaveTrap" ][ "enterSpell" ] = trapSect[ "leaveTrap" ][ "enterSpell" ].asInt
			self.flyTeleportTrapDict[ checkPoint ][ "leaveTrap" ][ "leaveSpell" ] = trapSect[ "leaveTrap" ][ "leaveSpell" ].asInt
			self.flyTeleportTrapDict[ checkPoint ][ "leaveTrap" ][ "modelNumber" ] = trapSect[ "leaveTrap" ][ "modelNumber" ].asString
			self.flyTeleportTrapDict[ checkPoint ][ "leaveTrap" ][ "isDisposable" ] = trapSect[ "leaveTrap" ][ "isDisposable" ].asInt
			self.flyTeleportTrapDict[ checkPoint ][ "leaveTrap" ][ "position" ] = trapSect[ "leaveTrap" ][ "position" ].asVector3
			
		if section[ "Space" ].has_key( "thirdGroupShuiingCount" ):
			self.thirdGroupShuiingCountList = section[ "Space" ][ "thirdGroupShuiingCount" ].asString.split(";")

	def packedDomainData( self, player ):
		"""
		"""
		captain = BigWorld.entities.get( player.captainID )
		if captain:
			level = captain.level
		else:
			level = 0
		data = { "shuijing_level"	: 	level,
				"dbID" 				: 	player.databaseID,
				"teamID" 			: 	player.teamMailbox.id,
				"shuijing_maxlevel"	: 	0,
				"shuijing_checkPoint"	: 	player.query( "shuijing_checkPoint", 1 ),
				"shuijingKey"		: 	player.shuijingKey,
				"captainDBID"		:	player.getTeamCaptainDBID(),
				"spaceKey"			:	player.teamMailbox.id,
				}
		return data


	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		if selfEntity.queryTemp("isFirstPlayer", 0 ) == 0:
			selfEntity.setTemp('isFirstPlayer', 1 )
			if selfEntity.params[ "shuijing_checkPoint" ] == 1:
				selfEntity.setTemp( "shuijing_checkPoint", 1)
				selfEntity.setTemp('shuijing_callEntity', 1 )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEVEL, 		"" )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_COPY_TITLE, cschannel_msgs.ACTIVITY_SHUIJING )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, time.time() )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, -1 )
		if len( selfEntity._players ) > ROLE_NUM_LIMIT:
			if selfEntity.queryTemp('leavePMB',None) is not None:
				selfEntity.queryTemp('leavePMB').cell.gotoForetime()
		SpaceCopyTemplate.onEnterCommon( self, selfEntity, baseMailbox, params )

	def onMonsterDie( self, selfEntity, params ):
		"""
		"""
		index = selfEntity.queryTemp( "contentIndex" )
		self.contents[index].onMonsterDie( selfEntity, params )


	def onLeaveTeam( self, playerEntity ):
		"""
		"""
		if playerEntity.queryTemp( 'leaveSpaceTime', 0 ) == 0:
			playerEntity.leaveTeamTimer = playerEntity.addTimer( 5, 0, ECBExtend.LEAVE_TEAM_TIMER )
		playerEntity.setTemp( "leaveSpaceTime", 5 )
		playerEntity.client.onLeaveTeamInSpecialSpace( 5 )
		playerEntity.getCurrentSpaceBase().cell.setLeaveTeamPlayerMB( playerEntity.base )


	def packedSpaceDataOnEnter( self, entity ):
		"""
		"""
		packDict = SpaceCopyTemplate.packedSpaceDataOnEnter( self, entity )
		packDict[ "teamID" ] = entity.teamMailbox.id
		return packDict

	def onLeaveTeamProcess( self, playerEntity ):
		"""
		队员离开队伍处理
		"""
		if not playerEntity.isInTeam() or playerEntity.query( "lastShuijintTeamID", 0 ) != playerEntity.getTeamMailbox().id:
			BigWorld.globalData[ "ShuijingManager" ].playerLeave( playerEntity.shuijingKey, playerEntity.base )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		某role在该副本中死亡
		"""
		pass
	
	def calCheckPointMonsterCount( self, selfEntity, checkPoint ):
		"""
		计算某一个关卡的怪物数量
		"""
		tempNumList = []
		selfEntity.shuijingMonsterCount = 0
		groupList = list( selfEntity.queryTemp('groupCount', set([])) )
		if checkPoint != CHECKPOINTS_3:				#不是第三关
			for i in groupList:
				if i.split("and")[ 0 ] == str( checkPoint ):
					spawnList = selfEntity.queryTemp(i)
					selfEntity.shuijingMonsterCount += len( spawnList )
		else:
			tempList = random.sample( self.randomGroupList, RANDOM_GROUP_NUM )
			selfEntity.setTemp( "randomGroupList", tempList )
			for tempString in tempList:
				tempNumList.append( len( tempString.split( "," ) ) )
			for i in groupList:
				if i.split("and")[ 0 ] == str( checkPoint ):
					spawnList = selfEntity.queryTemp(i)
					index = int(i.split("and")[1])
					if index > len(tempNumList):
						ERROR_MSG("spawn point group is larger than RANDOM_GROUP_NUM,group is %s,RANDOM_GROUP_NUM is %s"%( index, RANDOM_GROUP_NUM ) )
						break
					selfEntity.shuijingMonsterCount += len( spawnList ) * tempNumList[ index ]
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, selfEntity.shuijingMonsterCount )
		if selfEntity.queryTemp( "shuijing_checkPoint" ) != 1:					#不是第一关，都会有一个BOSS
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 1 )

	def checkPointTransition( self, selfEntity, checkPoint ):
		"""
		关卡之间的飞行传送的过渡
		"""
		selfEntity.setTemp( "shuijing_checkPoint", checkPoint + 1 )
		selfEntity.dieMonsterCount = 0
		BigWorld.globalData[ "ShuijingManager" ].passCheckPointDoor( selfEntity.params[ "shuijingKey" ])
		#创建开始飞行陷阱
		if self.flyTeleportTrapDict.has_key( checkPoint ) and self.flyTeleportTrapDict[ checkPoint ][ "enterTrap" ][ "enterSpell" ]:
			tempDict = self.flyTeleportTrapDict[ checkPoint ][ "enterTrap" ]
			self.createTrap( selfEntity, checkPoint, tempDict[ "position" ], tempDict )
		else:
			ERROR_MSG("enterTrap Spell is None,checkPoint is %s"%checkPoint)
		#创建飞行结束陷阱
		if self.flyTeleportTrapDict.has_key( checkPoint ) and self.flyTeleportTrapDict[ checkPoint ][ "leaveTrap" ][ "enterSpell" ]:
			tempDict = self.flyTeleportTrapDict[ checkPoint ][ "leaveTrap" ]
			self.createTrap( selfEntity, checkPoint, tempDict[ "position" ], tempDict )
		else:
			ERROR_MSG("enterTrap Spell is None,checkPoint is %s"%checkPoint)
		
	def createTrap( self, selfEntity, checkPoint, pos, trapDict ):
		"""
		创建陷阱
		"""
		enterDict = { "radius" : trapDict[ "radius" ], "enterSpell" : trapDict[ "enterSpell" ], "leaveSpell" : trapDict[ "leaveSpell" ], \
						"destroySpell" : trapDict[ "leaveSpell" ], "modelNumber" : trapDict[ "modelNumber" ], "lifetime" : trapDict[ "lifetime" ], \
						"casterID" : 0, "isDisposable" : trapDict[ "isDisposable" ] }
		BigWorld.createEntity( "AreaRestrictTransducer", selfEntity.spaceID, tuple( pos ), (0, 0, 0), enterDict )

	def spawnSpecialMonster( self, spaceEntity ):
		monster = g_objFactory.getObject( GUANG_ZHU ).createEntity( spaceEntity.spaceID, GUANG_ZHU_POSITION, GUANG_ZHU_DIRECTION, {"spawnPos": GUANG_ZHU_POSITION, "level": spaceEntity.shuijing_level })
		spaceEntity.setTemp( "guangzhu", monster.id)
		
	def onConditionChange( self, spaceEntity, params ):
		"""
		用于副本的事件变化通知。
		副本的事件变化可以是多个变化构成一个内容的完成，也可以是一个。
		"""
		#处理第三关水晶销毁通知副本，将已经销毁的className从thirdGroupMonsterList移除，
		#以便再次刷出同样className的水晶
		if params.has_key( "className" ):
			className = params[ "className" ]
			thirdGroupMonsterList = spaceEntity.queryTemp( "thirdGroupMonsterList", {} )
			if className in thirdGroupMonsterList.keys():
				thirdGroupMonsterList.pop( className )
				spaceEntity.setTemp( "thirdGroupMonsterList", thirdGroupMonsterList )
		#SpaceCopyTemplate.onConditionChange( self, spaceEntity, params )
		
	def spawnShuijing( self, spaceEntity, monsterIDList, monsterPosList ):
		"""
		define method
		用于产生第三关的水晶
		对于上一次没有消灭的水晶，继续保留，只刷新那些新增的className的水晶
		"""
		newMonsterIDList = copy.deepcopy( monsterIDList )
		newMonsterPosList = copy.deepcopy( monsterPosList )
		randGroup = spaceEntity.queryTemp( 'randGroup', str(CHECKPOINTS_3) + "and" + str(GROUP) )
		index = int( randGroup.split("and")[1] ) - 1
		count = int( self.thirdGroupShuiingCountList[ index ] )
		thirdGroupMonsterList = spaceEntity.queryTemp( "thirdGroupMonsterList", {} )
		for className in monsterIDList:
			if className in thirdGroupMonsterList.keys():
				newMonsterIDList.remove( className )
				count = count - 1
		for pos in monsterPosList:
			if pos in thirdGroupMonsterList.values():
				newMonsterPosList.remove( pos )
		if len( newMonsterIDList ) < count:
			randomIDList = random.sample( newMonsterIDList, len( newMonsterIDList ) )
			randomPosList = random.sample( newMonsterPosList, len( newMonsterPosList ) )
		else:
			randomIDList = random.sample( newMonsterIDList, count )
			randomPosList = random.sample( newMonsterPosList, count )
		for index,className in enumerate( randomIDList ):
			position = randomPosList[ index ]
			pos = utils.vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：%s Bad format '%s' in section." % ( self.__class__.__name__, position ) )
				break
			monster = g_objFactory.getObject( className ).createEntity( spaceEntity.spaceID, pos, (0,0,0), {"spawnPos": pos, "level": spaceEntity.shuijing_level })
			thirdGroupMonsterList[ className ] = randomPosList[ index ]
		spaceEntity.setTemp( "thirdGroupMonsterList", thirdGroupMonsterList )

	def getRevivePosition( self, spaceEntity ):
		checkPoint = spaceEntity.queryTemp( "shuijing_checkPoint", 1 )
		return self.birthPositionDict[ checkPoint ]

