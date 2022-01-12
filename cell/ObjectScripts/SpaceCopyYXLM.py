# -*- coding: gb18030 -*-

# 英雄联盟
import time
import random
import BigWorld

import csconst
import csdefine
import csstatus
from bwdebug import *
import random
import ECBExtend

from CopyContent import *

from SpaceCopyTeamTemplate import SpaceCopyTeamTemplate
from GameObjectFactory import g_objFactory
import time

PLAYER_SOLDIER_MONSTER_TYPE = 11			# 玩家小兵
NPC_SOLDIER_MONSTER_TYPE = 22			# NPC小兵
ELITE_MONSTER_TYPE = 1					# 精英

SPAWN_ELITE_1	=	111
SPAWN_ELITE_2	=	222
SPAWN_ELITE_3	=	333

SPACE_LAST_TIME = 1800

class CCAttackBase( CopyContent ):
	"""
	进攻基地
	"""
	def __init__( self ):
		self.key = "attckBase"
		self.val = 1
		
	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.addTimer( SPACE_LAST_TIME, 0, NEXT_CONTENT )					# 30分钟后副本关闭
		spaceEntity.addTimer( 3 * 60, 0, SPAWN_ELITE_1 )
		spaceEntity.addTimer( 6 * 60, 0, SPAWN_ELITE_2 )
		spaceEntity.addTimer( 9 * 60, 0, SPAWN_ELITE_3 )
	
	def doConditionChange( self, spaceEntity, params ):
		"""
		条件改变通知
		"""
		CopyContent.doConditionChange( self, spaceEntity, params )
		if params.has_key( "spawnPlayerSoldier" ):											# 刷玩家的小兵
			spaceEntity.base.spawnMonsters( {"monsterType":  PLAYER_SOLDIER_MONSTER_TYPE, "level": spaceEntity.teamLevel } )
		if params.has_key( "spawnNPCSoldier" ):												# 刷NPC的小兵
			spaceEntity.base.spawnMonsters( {"monsterType":  NPC_SOLDIER_MONSTER_TYPE, "level": spaceEntity.teamLevel } )
		if params.has_key( "playerBaseIsKilled" ):
			spaceEntity.addTimer( 60, 0, NEXT_CONTENT )		# 玩家基地被攻破，提前结束副本,5秒钟后玩家被传出副本
			self.givePlayerReward( spaceEntity, False )		# 给予玩家少量奖励
		if params.has_key( "monsterBaseIsKilled" ):
			spaceEntity.addTimer( 60, 0, NEXT_CONTENT )		# 怪物基地被攻破，提前结束副本
			self.givePlayerReward( spaceEntity, True )		# 给予玩家获胜奖励
		if params.has_key( "reason" ) and params["reason"] == "timeOver":
			return True
		return False
	
	def givePlayerReward( self, spaceEntity, isWin ):
		"""
		给奖励
		@param isWin : 玩家是否胜出
		@param Type : bool
		"""
		if isWin:
			for e in spaceEntity._players:
				if BigWorld.entities.has_key( e.id ):
					print" give win reward"
		else:
			for e in spaceEntity._players:
				if BigWorld.entities.has_key( e.id ):
					print" give lose reward"
	
	def onTimer( self, spaceEntity, id, userArg ):
		if userArg == SPAWN_ELITE_1 or userArg == SPAWN_ELITE_2 or userArg == SPAWN_ELITE_3:			# 刷精英
			spaceEntity.base.spawnMonsters( {"monsterType":  ELITE_MONSTER_TYPE, "level": spaceEntity.teamLevel } )
		else:
			CopyContent.onTimer( self, spaceEntity, id, userArg )
	
class SpaceCopyYXLM( SpaceCopyTeamTemplate ):
	"""
	宝藏副本（英雄联盟）
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopyTeamTemplate.__init__( self )
		self.isSpaceDesideDrop = True
		self.recordKey = "yingxionglianmeng_record"
		self.patrolLists = []
		self.patrolNpcs = []
		self.spaceBirthInf = None
		
	def load( self, section ):
		SpaceCopyTeamTemplate.load( self, section )
		pos = tuple( [ float(x) for x in section[ "Space" ][ "birthPos/position" ].asString.split() ] )
		direction = tuple( [ float(x) for x in section[ "Space" ][ "birthPos/direction" ].asString.split() ] )
		self.spaceBirthInf = ( pos, direction )
		
	def initContent( self ):
		self.contents.append( CCWait() )
		self.contents.append( CCAttackBase() )
		self.contents.append( CCKickPlayersProcess() )
	
	def packedDomainData( self, entity ):
		"""
		"""
		d = { "dbID" : entity.databaseID, "spaceKey" : entity.databaseID}
		if entity.teamMailbox:
			# 已加入队伍，取队伍数据
			d["teamID"] = entity.teamMailbox.id
			d["captainDBID"] = entity.getTeamCaptainDBID()
			d["membersDBID"] = entity.getTeamMemberDBIDs()
			# 取得所有队员basemailboxs
			teamMemberMailboxsList = entity.getTeamMemberMailboxs()
			if entity.getTeamCaptainMailBox() in teamMemberMailboxsList:
				teamMemberMailboxsList.remove( entity.getTeamCaptainMailBox() )
				
			if entity.isTeamCaptain():
				d["teamLevel"] = entity.level
				d["teamMaxLevel"] = min( entity.level + 3, csconst.ROLE_LEVEL_UPPER_LIMIT )
				d[ "membersMailboxs" ] = teamMemberMailboxsList
			
			d[ "teamInfos" ] = entity.popTemp( "YX_teamInofs", [] )	
			d[ "difficulty" ] = entity.popTemp( "YXLMEnterType" )
			d[ "robotInfos" ] = entity.popTemp( "YX_robotInfos" )
			d["spaceKey"] = entity.teamMailbox.id
		return d
		
	def packedSpaceDataOnEnter( self, entity ):
		"""
		"""
		packDict = SpaceCopyTeamTemplate.packedSpaceDataOnEnter( self, entity )
		if entity.teamMailbox:
			packDict[ "teamID" ] =  entity.teamMailbox.id
			
		packDict[ "playerDBID" ] = entity.databaseID
		return packDict
	
	def packedSpaceDataOnLeave( self, entity ):
		"""
		"""
		packDict = SpaceCopyTeamTemplate.packedSpaceDataOnLeave( self, entity )
		packDict["playerDBID"] = entity.databaseID
		packDict["player_accumPoint"] = entity.accumPoint
		return packDict
		
	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		根据给定的section，初始化（读取）entity属性。
		注：只有在createEntity()时需要把值自动对entity进行初始化时才有必要放到此函数初始化，
		也就是说，这里初始化的所有属性都必须是在相应的.def中声明过的。

		@param section: PyDataSection, 根据一定的格式存储了entity属性的section
		"""
		SpaceCopyTeamTemplate.onLoadEntityProperties_( self, section )
		if section.has_key( "patrolLists" ):
			str1 = section["patrolLists"].asString
			self.patrolLists = str1.split('|')
		if section.has_key( "patrolNpcs" ):
			str2 = section["patrolNpcs"].asString
			self.patrolNpcList = str2.split('|')
		
	def initPatrolInfo( self, spaceEntity ):
		"""
		设置副本巡逻路线和巡逻NPC信息
		"""
		random.shuffle( self.patrolLists )
		tempList = []
		for i in self.patrolLists:
			tempList.append( i )
		spaceEntity.setTemp( "spacePatrolLists", tempList )
		spaceEntity.setTemp( "spacePatrolNpcList", self.patrolNpcList )
	
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		if baseMailbox and params[ "databaseID" ] not in selfEntity._enterRecord:
			baseMailbox.cell.remoteAddActivityCount( selfEntity.id, csdefine.ACTIVITY_YING_XIONG_LIAN_MENG, self.recordKey )
			
		SpaceCopyTeamTemplate.onEnterCommon( self, selfEntity, baseMailbox, params )
		for i in selfEntity.queryTemp( "playerAccumPointList", [] ):			# 玩家第二次进副本时，恢复上次的气运值
			if i[0] == params["playerDBID"]:
				baseMailbox.cell.addAccumPoint( i[1] )
				break
		
		if BigWorld.entities.has_key( baseMailbox.id ):
			player = BigWorld.entities[baseMailbox.id]
			if player.isInTeam():
				player.setTemp( "onEnterYXLM", params['teamID'] )
		
		if not selfEntity.queryTemp( "tempHaveCome", False ):	# 只设置一次
			selfEntity.setTemp( "tempHaveCome", True )
			selfEntity.setTemp( "copyStartTime", time.time() )	# 副本开始时间
		
		# 副本界面使用
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, selfEntity.queryTemp( "copyStartTime" ) )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, SPACE_LAST_TIME )
	
	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		# 玩家气运值记录
		playerAccumRecord = selfEntity.queryTemp( "playerAccumPointList", [] )			# [( playerDBID , accumPoint ),...]
		for info in playerAccumRecord:
			if info[0] == params["playerDBID"]:				# 先移掉原来的玩家气运值记录
				playerAccumRecord.remove( info )
				break
		playerAccumRecord.append( ( params["playerDBID"], params["player_accumPoint"] ) )
		selfEntity.setTemp( "playerAccumPointList", playerAccumRecord )			# 记录玩家最新的气运值数据
		baseMailbox.cell.resetAccumPoint()
		SpaceCopyTeamTemplate.onLeaveCommon( self, selfEntity, baseMailbox, params )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		某role在该副本中死亡
		"""
		role.setTemp( "role_die_to_revive_type",csdefine.REVIVE_ON_SPACECOPY )
	
	def getEnterInf( self, playerEntity ):
		# 获取出生点坐标
		return self.spaceBirthInf