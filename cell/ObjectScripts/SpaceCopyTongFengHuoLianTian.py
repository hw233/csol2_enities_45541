# -*- coding: gb18030 -*-

import time
import Math
import csdefine
import ECBExtend
import utils
import random
import csconst
import Const
import cschannel_msgs
from bwdebug import *
from CopyContent import NEXT_CONTENT
from CopyContent import CopyContent
from CopyContent import CCKickPlayersProcess

from SpaceCopyTemplate import SpaceCopyTemplate
from GameObjectFactory import g_objFactory

FENG_HUO_LIAN_TIAN_BATTLE_FLAG		= "30112242"
ZHAO_HUAN_WU_ZI						= "30112240"
JI_FEN_WU_ZI						= "30112241"
LIGHT_WALL_CLASSNAME				= "20254054"
XIAN_FENG_GUAI_DICT					= { 0:{"left":"20129103", "mid":"20129104", "right":"20129105"}, 1:{"left":"20129108", "mid":"20129107", "right":"20129106"}}
FLAG_POSITION						= ( -11.203, 2.428, -58.216 )
RANDOM_RANGE_1						= -5
RANDOM_RANGE_2						= 5

WU_ZI_JIAN_GE_TIME					= 3*60
NOTICE_TIME_LIST					= [ 10*60, 3*60, 1*60 ]

ARG_WU_ZI							= 100
ARG_TOWER_AND_ALTAR					= 101
ARG_TONG_NOTICE_LIST				= [ 102, 103, 104 ]
ARG_DELAY_CLOSE						= 105

DELAY_CLOSE_TIME					= 30.0
CLOSE_SPECE_TIME					= 10.0

PK_PROTECT_TIME = 60				#PK保护时间60秒

CAN_CALL_AMOUNT				= 6				#能够召唤怪物的召唤物资数量

ROAD_MAPPING_NUM			= { "left":0, "mid":1, "right":2 }
NUM_MAPPING_ROAD			= { 0:"left", 1:"mid", 2:"right" }

ATTACK_SKILL_ID_LIST					= [ 111478001, 111479001, 111480001 ]
SPEED_SKILL_ID_LIST					= [ 111481001, 111482001, 111483001 ]
BUFF_ID_1							= 2002
BUFF_ID_2							= 6001

PROTECT_TIME				= 60


class CCProtectProcess( CopyContent ):
	"""
	1分钟准备时间
	"""
	def __init__( self ):
		self.key = "protectProcess"
		self.val = 1
	
	def onContent( self, spaceEntity ):
		"""
		内容执行
		"""
		self.spawnLightWall( spaceEntity )
		for e in spaceEntity._players:
			e.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )
			e.client.tongFHLTProtectTime( PROTECT_TIME )
		spaceEntity.setTemp( "startProtectTime", time.time() + PROTECT_TIME )
		spaceEntity.addTimer( PK_PROTECT_TIME, 0, NEXT_CONTENT )
	
	def onEnter( self, spaceEntity, baseMailbox, params ):
		"""
		内容期间，角色进入
		"""
		baseMailbox.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )				# 强制所有玩家进入和平模式
		protectTime = spaceEntity.queryTemp( "startProtectTime", 0.0 )
		if protectTime:
			baseMailbox.client.tongFHLTProtectTime( int( protectTime - time.time() ) )
	
	def onLeave( self, spaceEntity, baseMailbox, params ):
		"""
		内容期间，角色离开
		"""
		baseMailbox.cell.setSysPKMode( 0 )
		
	def endContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.removeTemp( "startProtectTime" )
		self.destroyLightWall( spaceEntity )
		CopyContent.endContent( self, spaceEntity )
		
	def onTimer( self, spaceEntity, id, userArg ):
		if userArg == ARG_DELAY_CLOSE:
			spaceEntity.getScript().kickAllPlayer( spaceEntity )
			spaceEntity.addTimer( CLOSE_SPECE_TIME, 0.0, Const.SPACE_TIMER_ARG_CLOSE )
		else:
			CopyContent.onTimer( self, spaceEntity, id, userArg )

	def spawnLightWall( self, spaceEntity ):
		lightWallPosition = spaceEntity.getScript().lightWallPositionList
		lightWallDirection = spaceEntity.getScript().lightWallDirectionList
		entityIDList = []
		for index,position in enumerate( lightWallPosition ):
			if position:
				pos = utils.vector3TypeConvert( position )
				if pos is None:
					ERROR_MSG( "Vector3 Type Error：%s Bad format '%s' in section." % ( self.__class__.__name__, position ) )
					return
				dir = utils.vector3TypeConvert( lightWallDirection[ index ] )
				if dir is None:
					ERROR_MSG( "Vector3 Type Error：%s Bad format '%s' in section." % ( self.__class__.__name__, lightWallDirection[ index ] ) )
					return
				entity = g_objFactory.getObject( LIGHT_WALL_CLASSNAME ).createEntity( spaceEntity.spaceID, pos, dir, { "spawnPos":tuple( pos ) } )
				entityIDList.append( entity.id )
		spaceEntity.setTemp( "lightWallClassNameList", entityIDList )
		
	def destroyLightWall( self, spaceEntity ):
		lightWallClassNameList = spaceEntity.queryTemp( "lightWallClassNameList", [] )
		if lightWallClassNameList:
			for id in lightWallClassNameList:
				entity = BigWorld.entities.get( id, None )
				if entity:
					entity.addTimer( 0.2, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )


class CCCombatProcess( CopyContent ):
	"""
	战斗时间
	"""
	def __init__( self ):
		self.key = "combatProcess"
		self.val = 1
		self.fengHuoLianTianBattleFlag = None
		self.leftJiFenWuZiPositionList = []
		self.leftJiFenWuZiAmountOfUnit = 0
		self.midJiFenWuZiPositionList = []
		self.midJiFenWuZiAmountOfUnit = 0
		self.rightJiFenWuZiPositionList = []
		self.rightJiFenWuZiAmountOfUnit = 0
		self.leftZhaoHuanWuZiPositionList = []
		self.leftZhaoHuanWuZiAmountOfUnit = 0
		self.midZhaoHuanWuZiPositionList = []
		self.midZhaoHuanWuZiAmountOfUnit = 0
		self.rightZhaoHuanWuZiPositionList = []
		self.rightZhaoHuanWuZiAmountOfUnit = 0
		
	
	def onContent( self, spaceEntity ):
		"""
		内容执行
		"""
		for e in spaceEntity._players:
			e.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_TONG )
			
		self.fengHuoLianTianBattleFlag = g_objFactory.getObject( FENG_HUO_LIAN_TIAN_BATTLE_FLAG ).createEntity( spaceEntity.spaceID, FLAG_POSITION, (0, 0, 0), { } )
		spaceEntity.addTimer( WU_ZI_JIAN_GE_TIME, 0, ARG_WU_ZI)
		if BigWorld.globalData.has_key( "fengHuoLianTianOverTime" ):
			spaceEntity.addTimer( int( BigWorld.globalData[ "fengHuoLianTianOverTime" ] - time.time() ) - NOTICE_TIME_LIST[0], 0, ARG_TONG_NOTICE_LIST[0] )
			spaceEntity.addTimer( int( BigWorld.globalData[ "fengHuoLianTianOverTime" ] - time.time() ) - NOTICE_TIME_LIST[1], 0, ARG_TONG_NOTICE_LIST[1] )
			spaceEntity.addTimer( int( BigWorld.globalData[ "fengHuoLianTianOverTime" ] - time.time() ) - NOTICE_TIME_LIST[2], 0, ARG_TONG_NOTICE_LIST[2] )
		self.spawnTowerAndAltar( spaceEntity )
		self.leftJiFenWuZiPositionList = spaceEntity.getScript().leftJiFenWuZiPositionList
		self.leftJiFenWuZiAmountOfUnit = spaceEntity.getScript().leftJiFenWuZiAmountOfUnit
		self.midJiFenWuZiPositionList = spaceEntity.getScript().midJiFenWuZiPositionList
		self.midJiFenWuZiAmountOfUnit = spaceEntity.getScript().midJiFenWuZiAmountOfUnit
		self.rightJiFenWuZiPositionList = spaceEntity.getScript().rightJiFenWuZiPositionList
		self.rightJiFenWuZiAmountOfUnit = spaceEntity.getScript().rightJiFenWuZiAmountOfUnit
		self.leftZhaoHuanWuZiPositionList = spaceEntity.getScript().leftZhaoHuanWuZiPositionList
		self.leftZhaoHuanWuZiAmountOfUnit = spaceEntity.getScript().leftZhaoHuanWuZiAmountOfUnit
		self.midZhaoHuanWuZiPositionList = spaceEntity.getScript().midZhaoHuanWuZiPositionList
		self.midZhaoHuanWuZiAmountOfUnit = spaceEntity.getScript().midZhaoHuanWuZiAmountOfUnit
		self.rightZhaoHuanWuZiPositionList = spaceEntity.getScript().rightZhaoHuanWuZiPositionList
		self.rightZhaoHuanWuZiAmountOfUnit = spaceEntity.getScript().rightZhaoHuanWuZiAmountOfUnit
	
	def onEnter( self, spaceEntity, baseMailbox, params ):
		"""
		内容期间，角色进入
		"""
		baseMailbox.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_TONG )
	
	def onLeave( self, spaceEntity, baseMailbox, params ):
		"""
		内容期间，角色离开
		"""
		pass
		
	def endContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.removeTemp( "startTowerAndAltar" )
	
	def onTimer( self, spaceEntity, id, userArg ):
		"""
		"""
		if userArg == ARG_WU_ZI:
			self.spawnMonster( spaceEntity )
		elif userArg in ARG_TONG_NOTICE_LIST:
			i = ARG_TONG_NOTICE_LIST.index( userArg )
			spaceEntity.noticeTongSituation( NOTICE_TIME_LIST[ i ] )
		elif userArg == ARG_DELAY_CLOSE:
			spaceEntity.getScript().kickAllPlayer( spaceEntity )
			spaceEntity.addTimer( CLOSE_SPECE_TIME, 0.0, Const.SPACE_TIMER_ARG_CLOSE )
		else:
			CopyContent.onTimer( self, spaceEntity, id, userArg )

	def spawnTowerAndAltar( self, spaceEntity ):
		tower_and_altar = list( spaceEntity.queryTemp( "tower_and_altar", set([])) )
		for i in tower_and_altar:
			if i == "left_tower_and_altar":
				tongDBID = spaceEntity.params[ "left" ]
			elif i == "right_tower_and_altar":
				tongDBID = spaceEntity.params[ "right" ]
			spawnPointMBList = spaceEntity.queryTemp( i, [] )
			if spawnPointMBList:
				for spawnPointMB in spawnPointMBList:
					params = {}
					params[ "tongDBID" ] = tongDBID
					spawnPointMB.cell.createEntity( params )
		for e in spaceEntity._players:
			e.cell.systemCastSpell( ATTACK_SKILL_ID_LIST[0] )
			e.cell.systemCastSpell( SPEED_SKILL_ID_LIST[0] )
		spaceEntity.setTemp( "startTowerAndAltar", True )

	def spawnMonster( self, spaceEntity ):
		"""
		刷新召唤物资以及积分物资
		"""
		self.spawnWuZiBox( spaceEntity, self.leftJiFenWuZiPositionList, self.leftJiFenWuZiAmountOfUnit, JI_FEN_WU_ZI )
		self.spawnWuZiBox( spaceEntity, self.midJiFenWuZiPositionList, self.midJiFenWuZiAmountOfUnit, JI_FEN_WU_ZI )
		self.spawnWuZiBox( spaceEntity, self.rightJiFenWuZiPositionList, self.rightJiFenWuZiAmountOfUnit, JI_FEN_WU_ZI )
		self.spawnWuZiBox( spaceEntity, self.leftZhaoHuanWuZiPositionList, self.leftZhaoHuanWuZiAmountOfUnit, ZHAO_HUAN_WU_ZI )
		self.spawnWuZiBox( spaceEntity, self.midZhaoHuanWuZiPositionList, self.midZhaoHuanWuZiAmountOfUnit, ZHAO_HUAN_WU_ZI )
		self.spawnWuZiBox( spaceEntity, self.rightZhaoHuanWuZiPositionList, self.rightZhaoHuanWuZiAmountOfUnit, ZHAO_HUAN_WU_ZI )
		spaceEntity.noticePlayers( cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_JI_FEN_WU_ZI_IS_APPEARING, [] )
		spaceEntity.noticePlayers( cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_ZHAO_HUAN_WU_ZI_IS_APPEARING, [] )
		spaceEntity.addTimer( WU_ZI_JIAN_GE_TIME, 0, ARG_WU_ZI)

	def spawnWuZiBox( self, spaceEntity, positionList, amountOfUnit, className ):
		"""
		刷新某一路的积分物资和召唤物资
		"""
		for position in positionList:
			if position:
				for i in xrange( amountOfUnit ):
					pos = utils.vector3TypeConvert( position )
					if pos is None:
						ERROR_MSG( "Vector3 Type Error：%s Bad format '%s' in section." % ( self.__class__.__name__, position ) )
						break
					pos = pos + Math.Vector3( random.randint(RANDOM_RANGE_1,RANDOM_RANGE_2), 0,random.randint(RANDOM_RANGE_1,RANDOM_RANGE_2) )
					collide = BigWorld.collide( spaceEntity.spaceID, ( pos.x, pos.y + 10, pos.z ), ( pos.x, pos.y - 10, pos.z ) )
					if collide != None:
						pos = Math.Vector3( pos.x, collide[0].y, pos.z )
					g_objFactory.getObject( className ).createEntity( spaceEntity.spaceID, pos, (0, 0, 0), { } )



class SpaceCopyTongFengHuoLianTian( SpaceCopyTemplate ):
	"""
	帮会夺城战复赛（烽火连天）
	"""
	def __init__( self ):
		SpaceCopyTemplate.__init__( self )
		self.isSpaceDesideDrop = True
		

	def load( self, section ):
		"""
		从配置中加载数据

		@type section : PyDataSection
		@param section : python data section load from npc's coonfig file
		"""
		SpaceCopyTemplate.load( self, section )
		
		data = section[ "Space" ][ "right_playerEnterPoint" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.right_playerEnterPoint = ( pos, direction )

		data = section[ "Space" ][ "left_playerEnterPoint" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.left_playerEnterPoint = ( pos, direction )
		
		self.leftJiFenWuZiPositionList = section[ "Space" ][ "leftRoadJiFenWuZi" ][ "positions" ].asString.split(";")
		self.leftJiFenWuZiAmountOfUnit = section[ "Space" ][ "leftRoadJiFenWuZi" ][ "amountOfUnit" ].asInt
		self.midJiFenWuZiPositionList = section[ "Space" ][ "midRoadJiFenWuZi" ][ "positions" ].asString.split(";")
		self.midJiFenWuZiAmountOfUnit = section[ "Space" ][ "midRoadJiFenWuZi" ][ "amountOfUnit" ].asInt
		self.rightJiFenWuZiPositionList = section[ "Space" ][ "rightRoadJiFenWuZi" ][ "positions" ].asString.split(";")
		self.rightJiFenWuZiAmountOfUnit = section[ "Space" ][ "rightRoadJiFenWuZi" ][ "amountOfUnit" ].asInt
		self.leftZhaoHuanWuZiPositionList = section[ "Space" ][ "leftRoadZhaoHuanWuZi" ][ "positions" ].asString.split(";")
		self.leftZhaoHuanWuZiAmountOfUnit = section[ "Space" ][ "leftRoadZhaoHuanWuZi" ][ "amountOfUnit" ].asInt
		self.midZhaoHuanWuZiPositionList = section[ "Space" ][ "midRoadZhaoHuanWuZi" ][ "positions" ].asString.split(";")
		self.midZhaoHuanWuZiAmountOfUnit = section[ "Space" ][ "midRoadZhaoHuanWuZi" ][ "amountOfUnit" ].asInt
		self.rightZhaoHuanWuZiPositionList = section[ "Space" ][ "rightRoadZhaoHuanWuZi" ][ "positions" ].asString.split(";")
		self.rightZhaoHuanWuZiAmountOfUnit = section[ "Space" ][ "rightRoadZhaoHuanWuZi" ][ "amountOfUnit" ].asInt
		self.lightWallPositionList = section[ "Space" ][ "lightWall_position" ][ "positions" ].asString.split(";")
		self.lightWallDirectionList = section[ "Space" ][ "lightWall_position" ][ "directions" ].asString.split(";")
		
		self.left_callMonsterPosList = section[ "Space" ][ "left_callMonsterPositions" ].asString.split(";")
		self.right_callMonsterPosList = section[ "Space" ][ "right_callMonsterPositions" ].asString.split(";")

	def initContent( self ):
		"""
		"""
		self.contents.append( CCProtectProcess() )
		self.contents.append( CCCombatProcess() )
		
	def packedDomainData( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		@param entity: 通常为玩家
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		# 返回databaseID，这样space domain能够此数据正确的记录副本的创建者，
		# 且不用担心玩家在短时间内（断）下线后重上时找回副本的问题；
		return { 'tongDBID' : entity.tong_dbID, "ename" : entity.getName(), "dbid" : entity.databaseID }
		
	def packedSpaceDataOnEnter( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于在玩家上线时需要在指定的space创建cell而获取数据；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		packDict = SpaceCopyTemplate.packedSpaceDataOnEnter( self, entity )
		packDict[ "tongDBID" ] = entity.tong_dbID
		packDict[ "ename" ] = entity.getName()
		packDict[ "databaseID" ] = entity.databaseID
		return packDict

	def packedSpaceDataOnLeave( self, entity ):
		"""
		获取entity离开时，向所在的space发送离开该space消息的额外参数；
		@param entity: 想要向space entity发送离开该space消息(onLeave())的entity（通常为玩家）
		@return: dict，返回要离开的space所需要的entity数据。如，有些space可能会需要比较离开的玩家名字与当前记录的玩家的名字，这里就需要返回玩家的playerName属性
		"""
		packDict = SpaceCopyTemplate.packedSpaceDataOnLeave( self, entity )
		packDict[ "tongDBID" ] = entity.tong_dbID
		packDict[ "ename" ] = entity.getName()
		packDict[ "databaseID" ] = entity.databaseID
		return packDict

	
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		SpaceCopyTemplate.onEnterCommon( self, selfEntity, baseMailbox, params )
		baseMailbox.cell.lockPkMode()													# 锁定pk模式，不能设置


	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		baseMailbox.cell.setSysPKMode( 0 )
		baseMailbox.cell.unLockPkMode()
		SpaceCopyTemplate.onLeaveCommon( self, selfEntity, baseMailbox, params )
		baseMailbox.client.tong_onLeaveFengHuoLianTianSpace()
	
	def onLeaveTeam( self, playerEntity ):
		"""
		"""
		pass
	
	def onLeaveTeamProcess( self, playerEntity ):
		"""
		队员离开队伍处理
		"""
		pass
		
		
	def getMBRelatedEntity( self, baseMailbox ):
		if BigWorld.entities.get( baseMailbox.id, None ):
			return BigWorld.entities[ baseMailbox.id ]

	def closeFengHuoLianTianRoom( self, selfEntity ):
		"""
		提前结束掉某场战争 由tongmanager 关闭所有房间
		"""
		selfEntity.setTemp( "isCurrentFengHuoLianTianOver", True )
		self.showMatchInfo( selfEntity )
		selfEntity.addTimer( DELAY_CLOSE_TIME, 0.0, ARG_DELAY_CLOSE )				#延迟30s关闭副本
		
	def callXianFengMonster( self, selfEntity, tongDBID ):
		"""
		召唤先锋怪
		"""
		if selfEntity.queryTemp( "isCallingMonster", False ):
			return
		if not selfEntity.tongCallMonsterDict.has_key( tongDBID ):
			amount = random.randint(0,2)
			tempString = NUM_MAPPING_ROAD[ amount ]
		else:
			num = 0
			tempList = [ 0, 1, 2 ]
			for i in xrange(3):
				amount = random.choice( tempList )
				tempList.remove( amount )
				roadString = NUM_MAPPING_ROAD[ amount ]
				if selfEntity.tongCallMonsterDict[ tongDBID ].has_key( roadString ) and selfEntity.tongCallMonsterDict[ tongDBID ][ roadString ] == 0:
					tempString = roadString
					break
				num += 1
			if num == 3:
				return
		flag = 0
		tongName = ""
		position = ""
		if tongDBID == selfEntity.params[ "left" ]:
			position = self.left_callMonsterPosList[ amount ]
			flag = 0
			tongName = selfEntity.params[ "leftTongName" ]
		elif tongDBID == selfEntity.params[ "right" ]:
			position = self.right_callMonsterPosList[ amount ]
			flag = 1
			tongName = selfEntity.params[ "rightTongName" ]
		if position:
			pos = utils.vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：%s Bad format '%s' in section." % ( self.__class__.__name__, position ) )
				return
			selfEntity.setTemp( "isCallingMonster", True )
			g_objFactory.getObject( XIAN_FENG_GUAI_DICT[ flag ][ tempString ] ).createEntity( selfEntity.spaceID, pos, (0, 0, 0), { "spawnPos":tuple( pos ), "ownTongDBID":tongDBID, "road":tempString } )
			selfEntity.decTongCallBoxAmount( tongDBID, CAN_CALL_AMOUNT, tempString )
			selfEntity.noticePlayers( cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_XIAN_FENG_IS_APPEARING% ( tongName, csconst.g_road_info[ tempString ] ), [] )
			
			
	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		某role在该副本中死亡
		"""
		DEBUG_MSG( "Role %i kill a enemy." % role.id )
		role.setTemp( "role_die_to_revive_type",csdefine.REVIVE_ON_SPACECOPY )
		role.addTimer( 7.0, 0, ECBExtend.ROLE_REVIVE_TIMER )
		# 杀人者找不到发生几率非常小，可以忽略这次记录
		if not killer:
			return

		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = killer.getOwner()
			if owner.etype == "MAILBOX" :
				return
			killer = owner.entity
			
		if killer.isEntityType( csdefine.ENTITY_TYPE_XIAN_FENG ):
			role.getCurrentSpaceBase().cell.onRoleBeKill( killer.ownTongDBID, 0, role.tong_dbID, role.databaseID )
		elif killer.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			role.getCurrentSpaceBase().cell.onRoleBeKill( killer.tong_dbID, killer.databaseID, role.tong_dbID, role.databaseID )

	def showMatchInfo( self, selfEntity ):
		"""
		将副本所有玩家踢出
		"""
		for mailbox in selfEntity._players:
			if BigWorld.entities.has_key( mailbox.id ):
				BigWorld.entities[ mailbox.id ].tong_onFengHuoLianTianOver()
			else:
				mailbox.cell.tong_onFengHuoLianTianOver()

	def kickAllPlayer( self, selfEntity ):
		"""
		将副本所有玩家踢出
		"""
		for mailbox in selfEntity._players:
			if BigWorld.entities.has_key( mailbox.id ):
				BigWorld.entities[ mailbox.id ].tong_leaveFengHuoLianTian()
			else:
				mailbox.cell.tong_leaveFengHuoLianTian()

