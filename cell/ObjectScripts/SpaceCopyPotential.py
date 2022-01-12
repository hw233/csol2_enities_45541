# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyPotential.py,v 1.17 2008-06-23 01:32:24 kebiao Exp $

"""
副本场景中共有10组刷新点，每组8个坐标。
根据以下规则产生怪物，玩家数量指在副本创建时即进入副本的玩家，不包括后进入的玩家。怪物数量产生后也不再发生改变。
即：
1个玩家：随机确定其中5组，每组随机确定3个点，共产生15个怪物。
2个玩家：随机确定其中6组，每组随机确定5个点，共产生30个怪物。
3个玩家：随机确定其中9组，每组随机确定5个点，共产生45个怪物。
4个玩家：10组，每组随机确定6个点，共产生60个怪物。
5个玩家：10组，全部8个点，共产生80个怪物。
"""
import BigWorld
import cschannel_msgs
import ShareTexts as ST
import csstatus
import csdefine
import csconst
import random
import time
from bwdebug import *
from SpaceCopyTeam import SpaceCopyTeam
from ObjectScripts.GameObjectFactory import g_objFactory
from LevelEXP import AmendExp
from NPCExpLoader import NPCExpLoader
import csconst
import Love3
g_npcExp = NPCExpLoader.instance()


_TIMER_ID_DESTROY_TIME_ = 0x10 #副本自然死亡时限 TIMER_ID
_QUERY_TEAM_STATE_		= 0x11 #副本检查玩家队伍状况 是否有人离队 踢出

#怪物的基础ID   分别对应 战士，剑客， 射手， 法师， 强防型职业的第11级ID
monsterData 	= [ 20115001, 20125001, 20135001, 20145001, 20155001, ]
#bossMonsterData = [ 20116001, 20126001, 20136001, 20146001, 20156001, ]
bossMonsterData = {}
bossMonsterData[0] = [ 20116000, 20116001, 20116002, 20116003, 20116004]
bossMonsterData[1] = [ 20116005, 20116006, 20116007, 20116008, 20116009]
bossMonsterData[2] = [ 20116010, 20116011, 20116012, 20116013, 20116014]
bossMonsterData[3] = [ 20116015, 20116016, 20116017, 20116018, 20116019]
bossMonsterData[4] = [ 20116020, 20116021, 20116022, 20116023, 20116024]
bossMonsterData[5] = [ 20126000, 20126001, 20126002, 20126003, 20126004]
bossMonsterData[6] = [ 20146000, 20146001, 20146002, 20146003, 20146004]
bossMonsterData[7] = [ 20146005, 20146006, 20146007, 20146008, 20146009]
bossMonsterData[8] = [ 20156000, 20156001, 20156002, 20156003, 20156004]

# 新版本增加的小怪刷新规则数据
monsterDatas = {}
"""
剿匪	10~50	战士	GW1118
GW1120	狂暴悍匪;巡山精兵;山寨蛮兵
狂暴悍匪;巡山精兵;山寨蛮兵
		剑客	GW1119
GW0475	流寇哨探;山野恶贼;山寨刺客
流寇哨探;山野恶贼;山寨刺客
		强防	GW1116	山寨铁卫;铁甲侍从;重甲强盗
"""
for lv in xrange( 10, 51 ):
	d = {}
	# 这里的索引对应monsterData 战士，剑客 ...
	d[ 0 ] = (
			( ( "GW1118_1", ), ( cschannel_msgs.POTENTIAL_KUANG_BAO_HAN_FEI, cschannel_msgs.POTENTIAL_XUN_SHAN_JING_BING, cschannel_msgs.POTENTIAL_SHAN_ZHAI_MAN_BING, ) ),
			( ( "GW1120_1", ), ( cschannel_msgs.POTENTIAL_KUANG_BAO_HAN_FEI, cschannel_msgs.POTENTIAL_XUN_SHAN_JING_BING, cschannel_msgs.POTENTIAL_SHAN_ZHAI_MAN_BING, ) ),
			( ( "GW0475_1", ), ( cschannel_msgs.POTENTIAL_LIU_KOU_SHAO_TAN, cschannel_msgs.POTENTIAL_SHAN_YE_E_ZEI, cschannel_msgs.POTENTIAL_SHAN_ZHAI_CI_KE, ) ),
	)
	d[ 1 ] = (
			( ( "GW1119_1", ), ( cschannel_msgs.POTENTIAL_LIU_KOU_SHAO_TAN, cschannel_msgs.POTENTIAL_SHAN_YE_E_ZEI, cschannel_msgs.POTENTIAL_SHAN_ZHAI_CI_KE, ) ),
	)
	d[ 4 ] = (
			( ("GW1116_1", ), ( cschannel_msgs.POTENTIAL_SHAN_ZHAI_TIE_WEI, cschannel_msgs.POTENTIAL_TIE_JIA_SHI_CONG, cschannel_msgs.POTENTIAL_ZHONG_JIA_QIANG_DAO, ) ),
	)
	monsterDatas[ lv ] = d

for lv in xrange( 51, 101 ):
	d = {}
	# 这里的索引对应monsterData 战士，剑客 ...
	d[ 0 ] = (
			( ( "GW0433_1", ), ( cschannel_msgs.POTENTIAL_BING_JIA_KUANG_CHONG, ) ),
			( ( "gw0463_1", ), ( cschannel_msgs.POTENTIAL_DUO_WEN_YAO_BING, ) ),
			( ( "gw0494_1", ), ( cschannel_msgs.POTENTIAL_YAO_HUA__REN, ) ),
			)
	d[ 4 ] = (
			( ( "GW0441_1", ), ( cschannel_msgs.POTENTIAL_ZHONG_JIA_JI_KUI,  ) ),
			( ( "gw0448_2", ), ( cschannel_msgs.POTENTIAL_MAN_LI_XUE_REN,  ) ),
	)
	d[ 1 ] = (
			( ( "GW0430_1", ), ( cschannel_msgs.POTENTIAL_FENG_MO_LONG_WANG, ) ),
			( ( "GW0427_1", ), ( cschannel_msgs.POTENTIAL_FENG_MO_LONG_REN, ) ),
			( ( "GW0493_1", ), ( cschannel_msgs.POTENTIAL_HUO_YUN_XIAN_FENG, ) ),
	)
	d[ 3 ] = (
			( ( "GW0447_1", ), ( cschannel_msgs.POTENTIAL_ZENG_HEN_NV_YAO,  ) ),
			( ( "GW0409_1", ), ( cschannel_msgs.POTENTIAL_WU_FA_MAO_YAO,  ) ),
			( ( "gw1130_4", ), ( cschannel_msgs.POTENTIAL_HU_MEI_YAO,  ) ),
			( ( "GW0495_1", ), ( cschannel_msgs.POTENTIAL_MI_FA_YAO_REN,  ) ),
			( ( "GW0496_1", ), ( cschannel_msgs.POTENTIAL_E_JING, ) ),
	)
	d[ 2 ] = (
			( ( "GW0065_1", ), ( cschannel_msgs.POTENTIAL_HEI_YI_DA_PENG, ) ),
	)
	monsterDatas[ lv ] = d

for lv in xrange( 101, 151 ):
	d = {}
	# 这里的索引对应monsterData 战士，剑客 ...
	d[ 4 ] = (
				( ("gw0609_1", ), ( cschannel_msgs.POTENTIAL_MONSTER1,) ),
				( ("gw0643_1", ), (cschannel_msgs.POTENTIAL_MONSTER2, ) ),
				( ("gw1235_1", ), (cschannel_msgs.POTENTIAL_MONSTER12, ) ),
				( ("gw1240_1", ), (cschannel_msgs.POTENTIAL_MONSTER13, ) ),
			)
	d[ 0 ] = (
				( ("gw0612_1", ), ( cschannel_msgs.POTENTIAL_MONSTER3, ) ),
				( ("gw0633_1", ), ( cschannel_msgs.POTENTIAL_MONSTER4, ) ),
				( ("gw0605_1", ), ( cschannel_msgs.POTENTIAL_MONSTER5, ) ),
				( ("gw1242_1", ), ( cschannel_msgs.POTENTIAL_MONSTER14, ) ),
				( ("gw1243_1", ), ( cschannel_msgs.POTENTIAL_MONSTER15, ) ),
			)
	d[ 1 ] = (
				( ("gw0630_1", ), ( cschannel_msgs.POTENTIAL_MONSTER6, ) ),
				( ("gw0649_1", ), ( cschannel_msgs.POTENTIAL_MONSTER7, ) ),
				( ("gw0636_1", ), ( cschannel_msgs.POTENTIAL_MONSTER8, ) ),
				( ("gw0646_1", ), ( cschannel_msgs.POTENTIAL_MONSTER7, ) ),
			)
	d[ 3 ] = (
				( ("gw0615_1", ), ( cschannel_msgs.POTENTIAL_MONSTER9, ) ),
				( ("gw0621_1", ), ( cschannel_msgs.POTENTIAL_MONSTER10, ) ),
				( ("gw0639_1", ), ( cschannel_msgs.POTENTIAL_MONSTER11 , ) ),
				( ("gw1239_1", ), ( cschannel_msgs.POTENTIAL_MONSTER16, ) ),
				( ("gw1241_1", ), ( cschannel_msgs.POTENTIAL_MONSTER17, ) ),
				( ("gw1244_1", ), ( cschannel_msgs.POTENTIAL_MONSTER18 , ) ),
			)

	d[ 2 ] = (
				( ("gw0606_1", ), ( cschannel_msgs.POTENTIAL_MONSTER19,) ),
			)
	monsterDatas[ lv ] = d

# 按照人数刷怪的相关映射数据
tmpmapping = {
		# 人数 ：（ 选择坐标组数， 刷怪的坐标点数 ）
		1 : ( 5,  5 ),
		2 : ( 5,  7 ),
		3 : ( 6,  9 ),
		4 : ( 6, 12 ),
		5 : ( 6, 15 ),
}

BOSS_SPEAK = [		csstatus.POTENTIAL_QUEST_BOSS_SAY1,
					csstatus.POTENTIAL_QUEST_BOSS_SAY2,
					csstatus.POTENTIAL_QUEST_BOSS_SAY3,
					csstatus.POTENTIAL_QUEST_BOSS_SAY4,
					csstatus.POTENTIAL_QUEST_BOSS_SAY5,
					csstatus.POTENTIAL_QUEST_BOSS_SAY6,
					csstatus.POTENTIAL_QUEST_BOSS_SAY7,
					csstatus.POTENTIAL_QUEST_BOSS_SAY8,
					csstatus.POTENTIAL_QUEST_BOSS_SAY9,
					csstatus.POTENTIAL_QUEST_BOSS_SAY10,
					csstatus.POTENTIAL_QUEST_BOSS_SAY11,
					csstatus.POTENTIAL_QUEST_BOSS_SAY12,
					csstatus.POTENTIAL_QUEST_BOSS_SAY13,
]

# 根据不同的任务类型，调整怪物的等级(根据任务的._title)
changeLevelMapping = {
						cschannel_msgs.POTENTIAL_JIAO_FEI : 0,
						cschannel_msgs.POTENTIAL_CHU_YAO : 1,
						cschannel_msgs.POTENTIAL_JIANG_MO : 2,
					 }

_SPACE_LIVE_TIME = 3600

class SpaceCopyPotential( SpaceCopyTeam ):
	"""
	注：此脚本只能用于匹配SpaceDomainCopy、SpaceCopy或继承于其的类。
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopyTeam.__init__( self )

	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		SpaceCopyTeam.load( self, section )
		self._posData = []

#		for item in section[ "Space" ][ "monsterPoint" ].values():
#			points = []
#			for point in item.values():
#				points.append( ( eval( point["pos"].asString ), eval( point["direction"].asString ), int( eval( point["randomWalkRange"].asString ) ) ) )
#			self._posData.append( points )

		point = section[ "Space" ][ "doorPoint" ]
		self.doorPoint = ( eval( point["pos"].asString ), point["radius"].asFloat )

#		point = section[ "Space" ][ "BossPoint" ]
#		self.bossPoint = ( eval( point["pos"].asString ), eval( point["direction"].asString ), int( eval( point["randomWalkRange"].asString ) ) )
		
		self.bossPoint = {}
		if not section[ "Space" ][ "BossPoint" ].has_key("item"):
			ERROR_MSG( "SpaceCopyPotential:section[ 'Space' ][ 'BossPoint' ] hasn't key item." )
		else:
			for point in section[ "Space" ][ "BossPoint" ].values():
				if not point.has_key("pos"):
					ERROR_MSG( "SpaceCopyPotential:section[ 'Space' ][ 'BossPoint' ] hasn't values()." )
					break
				self.bossPoint[ point["playerAmount"].asInt ] = ( eval( point["pos"].asString ), eval( point["direction"].asString ), int( eval( point["randomWalkRange"].asString ) ) )
#			self.bossPoint.append( ( eval( point["pos"].asString ), eval( point["direction"].asString ), int( eval( point["randomWalkRange"].asString ) ), point["playerAmount"].asInt ) )

#		self.lowBossPoint = []
#		for point in section[ "Space" ][ "smallBossPoint" ].values():
#			self.lowBossPoint.append( ( eval( point["pos"].asString ), eval( point["direction"].asString ), int( eval( point["randomWalkRange"].asString ) ), point["playerAmount"].asInt ) )


		self.lowBossPoint = []
		for point in section[ "Space" ][ "smallBossPoint" ].values():
			self.lowBossPoint.append( ( eval( point["pos"].asString ), eval( point["direction"].asString ), int( eval( point["randomWalkRange"].asString ) ) ) )

	def packedDomainData( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		@param entity: 通常为玩家
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		# 角色在副本中掉线或者死亡可能出现这种情况
		dbID = entity.popTemp( "enterSpaceID" )
		if dbID is None:
			if entity.isInTeam():
				for e in entity.teamMembers:
					if entity.captainID == e["mailbox"].id:
						dbID = e["dbID"]
						break
			else:
				dbID = entity.databaseID

		datas = { 'dbID' : dbID, "spaceKey":dbID }
		questID = entity.popTemp( "questID", 0 )
		if questID > 0:
			datas[ "ownerDatabaseID" ]			= entity.popTemp( "potentialIssuer", 0 )
			datas[ "questID" ] 					= questID
			datas[ "NPCObjMailbox" ] 			= entity.popTemp( "NPCObjMailbox" )
			datas[ "NPCClassName" ] 			= entity.popTemp( "NPCClassName" )
			datas[ "monClassType" ] 			= entity.popTemp( "monClassType" )
			datas[ "bossModelNumber" ] 			= entity.popTemp( "bossModelNumber" )
			datas[ "bossName" ] 				= entity.popTemp( "bossName" )
			datas[ "castNPCMapName" ] 			= entity.popTemp( "castNPCMapName" )
			datas[ "leavePoint" ] 				= entity.popTemp( "leavePoint" )
			datas[ "questLevel" ]				= entity.popTemp( "questLevel" )
			datas[ "playerAmount" ]				= entity.popTemp( "playerAmount" )
			datas[ "teamID" ]					= -1
			datas[ "changeLevel" ]				= changeLevelMapping[ entity.getQuest( datas[ "questID" ] )._title ]

			if entity.isInTeam():
				datas[ "teamID" ] 				= entity.teamMailbox.id

		DEBUG_MSG( "potentialCreate:%s" % datas )
		return datas

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		用我自己的数据初始化参数 selfEntity 的数据
		"""
		SpaceCopyTeam.initEntity( self, selfEntity )
		# 设置营救难民活动， 及数量
		if random.randint( 0, 100 ) <= 20:
			selfEntity.setTemp( "yjnm_count", random.randint( 1, 2 ) )

		selfEntity.setTemp( "leaveSpaceInterval", 30 )
		selfEntity.setTemp( "timer_leaveSpaceInterval", selfEntity.addTimer( _SPACE_LIVE_TIME - 30, 10, 0x03 ) )
		try:
			selfEntity.params[ "NPCObjMailbox" ].cell.setTemp( "spaceBaseMailbox", selfEntity.base )
		except:
			EXCEHOOK_MSG("spacePrams:%s" % selfEntity.params)
			
		self.createDoor( selfEntity )
#		selfEntity.setTemp( "timer_castMon", selfEntity.addTimer( 1.0, 0, 0x01 ) )
		selfEntity.setTemp( "timer_teamCheck", selfEntity.addTimer( 0.0, 3.0, _QUERY_TEAM_STATE_ ) )

	def castRefugee( self, selfEntity, positions ):
		"""
		营救难民刷出
		"""
		if selfEntity.queryTemp( "yjnm_count", 0 ) > 0:
			posData = positions.pop( random.randint( 0, len( positions ) - 1 ) )
			selfEntity.createNPCObject( "10111182", posData[0], posData[1], { "tempMapping" : {  } } )
			selfEntity.setTemp( "yjnm_count", selfEntity.queryTemp( "yjnm_count", 0 ) - 1 )

	def castBossSmallMonsters( self, selfEntity ):
		"""
		刷BOSS的小怪
		"""
		questLevel = selfEntity.params[ "questLevel" ]
		changeLevel = selfEntity.params[ "changeLevel" ]
		mdata = monsterDatas[ questLevel ]
		mlen = len( mdata )
		count = 0
		for position, direction, randomWalkRange in self.lowBossPoint:
			count += 1
			mItem = mdata.items()[ random.randint( 0, mlen - 1 ) ]
			monsterID = str( monsterData[ mItem[ 0 ] ] - 11 + questLevel + changeLevel )
			minfo = mItem[ 1 ][ random.randint( 0, len( mItem[ 1 ] ) - 1 ) ]
			uname = minfo[ 1 ][ random.randint( 0, len( minfo[ 1 ] ) - 1 ) ]
			mmodelNumber = minfo[ 0 ][ random.randint( 0, len( minfo[ 0 ] ) - 1 ) ]
			monInfo = { "tempMapping" : { "space" : selfEntity.base, "spaceClassName" : selfEntity.className } }
			monInfo[ "spawnPos" ] = position
			monInfo[ "randomWalkRange" ] = randomWalkRange
			monInfo[ "modelNumber" ] = mmodelNumber.lower()
			monInfo[ "uname" ] = uname
			selfEntity.createNPCObject( monsterID, position, direction, monInfo )

		selfEntity.setTemp( "Monster_Count", len( self.lowBossPoint ) )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, count )

	def castMonsters( self, selfEntity ):
		"""
		刷怪
		"""
		# 获得召唤次数
		monster_Count = 0
		cmc = selfEntity.queryTemp( "ConjureMonsterCount", 0 ) + 1
		selfEntity.setTemp( "ConjureMonsterCount", cmc ) # 记录刷怪次数
		questLevel = selfEntity.params[ "questLevel" ]
		changeLevel = selfEntity.params[ "changeLevel" ]

		if cmc <= 1:   # 召唤小怪
			spawnPointBaseMBList = selfEntity.queryTemp( "spawnPointPotentialBaseMB", [] )
			level = questLevel + changeLevel
			monster_Count = len( spawnPointBaseMBList )
			selfEntity.setTemp( "Monster_Count", monster_Count )
			selfEntity.setTemp( "Monster_CountMax", monster_Count )

			#副本界面使用
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEVEL, 		"" )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_COPY_TITLE, cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, time.time() )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, _SPACE_LIVE_TIME )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, monster_Count )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 0 )
			for spawnPointBaseMB in spawnPointBaseMBList:
				spawnPointBaseMB.cell.createEntity( {"level":level} )
			spawnPointDarkBaseMBList = selfEntity.queryTemp( "spawnPointPotentialDarkBaseMB", [] )
			for spawnPointBaseMB in spawnPointDarkBaseMBList:
				spawnPointBaseMB.cell.createEntity( {"level":level} )
			
#			playerAmount = selfEntity.params[ "playerAmount" ]
#			positions = []
#			tmpPos = list( self._posData )
#			pgroups, points = tmpmapping[ playerAmount ]
#			# 获得所有坐标点
#			for x in xrange( pgroups ):
#				idx = random.randint( 0, len( tmpPos ) - 1 )
#				tp = list( tmpPos.pop( idx ) )
#				for x1 in xrange( points ):
#					idx1 = random.randint( 0, len( tp ) - 1 )
#					positions.append( tp.pop( idx1 ) )
#
#			positions1 = list( positions )
#
#			# 刷出所有怪物
#			mdata = monsterDatas[ questLevel ]
#			mlen = len( mdata )
#			for position, direction, randomWalkRange in positions:
#				mItem = mdata.items()[ random.randint( 0, mlen - 1 ) ]
#				monsterID = str( monsterData[ mItem[ 0 ] ] - 11 + questLevel + changeLevel )
#				minfo = mItem[ 1 ][ random.randint( 0, len( mItem[ 1 ] ) - 1 ) ]
#				uname = minfo[ 1 ][ random.randint( 0, len( minfo[ 1 ] ) - 1 ) ]
#				mmodelNumber = minfo[ 0 ][ random.randint( 0, len( minfo[ 0 ] ) - 1 ) ]
#				monInfo = { "tempMapping" : { "space" : selfEntity.base, "spaceClassName" : selfEntity.className } }
#				monInfo[ "spawnPos" ] = position
#				monInfo[ "randomWalkRange" ] = randomWalkRange
#				monInfo[ "modelNumber" ] = mmodelNumber.lower()
#				monInfo[ "uname" ] = uname
#				selfEntity.createNPCObject( monsterID, position, direction, monInfo )
#				self.castRefugee( selfEntity, positions1 )
#				monster_Count += 1
#
#			selfEntity.setTemp( "Monster_Count", monster_Count )
#			selfEntity.setTemp( "Monster_CountMax", monster_Count )
#
#			#副本界面使用
#			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEVEL, 		"" )
#			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_COPY_TITLE, cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN )
#			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, time.time() )
#			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, _SPACE_LIVE_TIME )
#			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, monster_Count )
#			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 0 )
		elif cmc == 2: # 召唤BOSS
			playerAmount = selfEntity.params[ "playerAmount" ]
			position, direction, randomWalkRange = self.bossPoint[ playerAmount ]
			monInfo = { "tempMapping" : { "space" : selfEntity.base, "spaceClassName" : selfEntity.className } }
			monInfo[ "spawnPos" ] = position
			monInfo[ "randomWalkRange" ] = randomWalkRange
			modelNumber = selfEntity.params[ "bossModelNumber" ]
			monInfo[ "uname" ] = selfEntity.params[ "bossName" ]
			if len( modelNumber ) > 0: monInfo[ "modelNumber" ] = modelNumber
			bossID = str( bossMonsterData[ selfEntity.params[ "monClassType" ] ][ playerAmount - 1 ] )
			monInfo["level"] = questLevel + changeLevel
			selfEntity.setTemp( "bossID", bossID )
			selfEntity.createNPCObject( bossID, position, direction, monInfo )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 1 )
#			self.castBossSmallMonsters( selfEntity )

			# 通知所有人boss 来了
			self.statusMessageAllPlayer( selfEntity, BOSS_SPEAK[ random.randint( 0, len( BOSS_SPEAK ) - 1 ) ], monInfo[ "uname" ] )

	def banishAllPlayer( self, selfEntity ):
		"""
		驱逐所有玩家出副本
		"""
		destSpace = selfEntity.params[ "castNPCMapName" ]
		destPosition, destDirection = selfEntity.params[ "leavePoint"]

		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].gotoSpace( destSpace, destPosition, destDirection )
			else:
				e.cell.gotoSpace( destSpace, destPosition, destDirection )

	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if selfEntity.queryTemp( "timer_castMon", 0 ) == id: # 刷怪 并记录次数等
			selfEntity.removeTemp( "timer_castMon" )
			self.castMonsters( selfEntity )
		elif selfEntity.queryTemp( "timer_leaveSpace", 0 ) == id:    # 最后一个BOSS被杀死 开始触发任务完成事件 通知玩家离开等清理工作
			selfEntity.removeTemp( "timer_leaveSpace" )
			## 通知NPC销毁， 如果丢失该NPC信息那么将忽略销毁 由NPC自己60分钟的生命时钟销毁自己 如果NPC自身时间到了销毁了就不需要我们再做销毁了
			if selfEntity.queryTemp( "NPC_Dead", 0 ) == 0:
				selfEntity.params[ "NPCObjMailbox" ].cell.remoteScriptCall( "onDestroySelf", () )

			# 通知所有人离开副本
			self.banishAllPlayer( selfEntity )
			# after by 60 second close this the space. prevent lost the space  for player.
			selfEntity.setTemp( "timer_destroy", selfEntity.addTimer( 1.0, 1.0, _TIMER_ID_DESTROY_TIME_ ) )
		elif selfEntity.queryTemp( "timer_leaveSpaceInterval", 0 ) == id:
			leaveTime = selfEntity.queryTemp( "leaveSpaceInterval", 30 )
			if leaveTime > 0:
				self.statusMessageAllPlayer( selfEntity, csstatus.POTENTIAL_QUEST_LEAVE_SPACE1, leaveTime )
				selfEntity.setTemp("leaveSpaceInterval", leaveTime - 10)
			else:
				self.statusMessageAllPlayer( selfEntity, csstatus.POTENTIAL_QUEST_LEAVE_SPACE2 )
				selfEntity.cancel( id )
				selfEntity.removeTemp( "timer_leaveSpaceInterval" )
				selfEntity.setTemp( "timer_leaveSpace", selfEntity.addTimer( 1.0, 0.0, 0x02 ) )
		elif selfEntity.queryTemp( "timer_destroy", 0 ) == id:
			if len( selfEntity._players ) <= 0:
				selfEntity.cancel( id )
				selfEntity.removeTemp( "timer_destroy" )
				selfEntity.base.closeSpace( True )
		elif selfEntity.queryTemp( "timer_teamCheck", 0 ) == id:
			# 检查是否有人离开队伍 有就踢出副本  这里被启动检查那么该副本一定是一个队伍创建的
			for e in selfEntity._players:
				if BigWorld.entities.has_key( e.id ):
					p = BigWorld.entities[ e.id ]
					if p.databaseID != selfEntity.params[ "ownerDatabaseID" ]:
						if p.teamMailbox == None:
							p.gotoForetime()
					else:
						if p.teamMailbox == None:
							selfEntity.params[ "teamID" ] = -1
						else:
							selfEntity.params[ "teamID" ] = p.teamMailbox.id

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopyTeam.onEnterCommon( self, selfEntity, baseMailbox, params )

		# 设置任务等级到每个进入玩家， 方便难民活动的判断
		questLevel = selfEntity.params[ "questLevel" ]
		realEntity = BigWorld.entities[ baseMailbox.id ]
		if BigWorld.entities.has_key( baseMailbox.id ) and realEntity.isReal():
			realEntity.setTemp( "questLevel", questLevel )
			realEntity.setTemp( "space", selfEntity.base )
			realEntity.setTemp( "spaceClassName", selfEntity.className )
			realEntity.setTemp( "ownerDatabaseID", selfEntity.params[ "ownerDatabaseID" ] )
		else:
			baseMailbox.cell.setTemp( "questLevel", questLevel )
			baseMailbox.cell.setTemp( "space", selfEntity.base )
			baseMailbox.cell.setTemp( "spaceClassName", selfEntity.className )
			baseMailbox.cell.setTemp( "ownerDatabaseID", selfEntity.params[ "ownerDatabaseID" ] )

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		一个entity准备离开space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onLeave()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 要离开此space的entity mailbox
		@param params: dict; 离开此space时需要的附加数据。此数据由当前脚本的packedDataOnLeave()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopyTeam.onLeaveCommon( self, selfEntity, baseMailbox, params )
		realEntity = BigWorld.entities[ baseMailbox.id ]
		realEntity.removeTemp( "questLevel" )
		realEntity.removeTemp( "space" )
		realEntity.removeTemp( "spaceClassName" )
		realEntity.removeTemp( "ownerDatabaseID" )
		if realEntity.findBuffsByBuffID( 99026 ):
			realEntity.removeBuffByBuffID( 99026, [ csdefine.BUFF_INTERRUPT_NONE ] )	# 清除临时飞行骑宠buff

	def statusMessageAllPlayer( self, selfEntity, msgKey, *args ):
		"""
		通知所有人 指定的信息
		"""
		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				p = BigWorld.entities[ e.id ]
				p.statusMessage( msgKey, *args )
			else:
				ERROR_MSG( "player %i not found" % e.id )

	def onKillMonster( self, selfEntity, isBoss ):
		"""
		杀死怪物通知
		"""
		# 怪物被杀 记录当前个数
		monster_Count = selfEntity.queryTemp( "Monster_Count", 0 ) - 1
		monster_CountMax = selfEntity.queryTemp( "Monster_CountMax", 1 )

		conjureMonsterCount = selfEntity.queryTemp( "ConjureMonsterCount", 0 )
		if conjureMonsterCount < 2:
			# 通知所有人 现在剩下的怪物信息
			self.statusMessageAllPlayer( selfEntity, csstatus.ROLE_QUEST_POTENTIAL_KILL_INFO, cschannel_msgs.POTENTIAL_ZHUA_YA, monster_CountMax - monster_Count, monster_CountMax )

		#判断是否所有的怪物都被杀死\ 如果都被杀了  那么触发刷怪
		if monster_Count <= 0:
			selfEntity.setTemp( "timer_castMon", selfEntity.addTimer( 5.0, 0, 0x01 ) )

		if isBoss:
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 0 )

			# 如果刷怪次数满了  那么添加退出时钟
			for e in selfEntity._players:
				# 通知任务 事件触发
				if BigWorld.entities.has_key( e.id ):	# 在这个小地图中，把p当作real entity使用。
					p = BigWorld.entities[ e.id ]
					self.castPotentialBuff( p )
					ptQuestID = selfEntity.params[ "questID" ]
					p.questTaskIncreaseState( ptQuestID, 0 )
					potentialQDT = p.questsTable[ptQuestID]
					specialPtQuestID = potentialQDT.query( "specialPtQuestID", 0 )
					if specialPtQuestID:	# 如果存在特殊副本任务，一并触发完成
						p.questTaskIncreaseState( specialPtQuestID, 0 )
				else:
					ERROR_MSG( "potentialDebug:can't fount player %i." %  e.id )

			if selfEntity.queryTemp( "leaveSpaceInterval", 30 ) == 30:
				selfEntity.cancel( selfEntity.queryTemp( "timer_leaveSpaceInterval", 0 ) )
				selfEntity.setTemp( "timer_leaveSpaceInterval", selfEntity.addTimer( 1, 10, 0x03 ) )

			for domain in BigWorld.globalData["SpaceDomainPotential"].itervalues():
				domain.onDisableQuest( selfEntity.params[ "ownerDatabaseID" ]  )
		else:
			selfEntity.setTemp( "Monster_Count", monster_Count )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, monster_Count )

	def onPotentialObjectDie( self, selfEntity ):
		"""
		任务NPC存在时间到期 NPC销毁通知
		"""
		selfEntity = BigWorld.entities[ selfEntity.id ]
		if selfEntity.queryTemp( "timer_destroy", 0 ) == 0:
			selfEntity.setTemp( "timer_destroy", selfEntity.addTimer( 0, 60.0, _TIMER_ID_DESTROY_TIME_ ) )
		selfEntity.setTemp( "NPC_Dead", 1 )

	def createDoor( self, selfEntity ):
		"""
		创建Door
		"""
		doordict = {"name" : cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN_CHUAN_SONG_DIAN}
		doordict["radius"] = self.doorPoint[1]
		doordict["destSpace"] = selfEntity.params[ "castNPCMapName" ]
		doordict["destPosition"] = selfEntity.params[ "leavePoint"][0]
		doordict["destDirection"] = selfEntity.params[ "leavePoint"][1]
		doordict["modelNumber"] = "gw7123"
		doordict["modelScale"] = 25
		BigWorld.createEntity( "SpaceDoor", selfEntity.spaceID, self.doorPoint[0], (0, 0, 0), doordict )

	def castPotentialBuff( self, player ):
		"""
		向玩家添加 潜能激发 BUFF
		"""
		if not player.isReal():
			DEBUG_MSG( "potentialDebug:player %i is ghost." %  player.id )

		for idx, buff in enumerate( player.attrBuffs ):
			if buff[ "skill" ].getBuffID() == 99006:
				level = buff[ "skill" ].getLevel() + 1

				if level > 20:
					level = 20

				player.removeBuff( idx, [ csdefine.BUFF_INTERRUPT_NONE ] )
				if level <= 10:
					skillID = 122167000 + level
					b = Love3.g_skills[ skillID ].getBuffLink(0).getBuff()
					b.receive( player, player )

				return

		buff = Love3.g_skills[ 122167001 ].getBuffLink(0).getBuff()
		buff.receive( player, player )

#
# $Log: not supported by cvs2svn $
# Revision 1.16  2008/06/19 08:55:14  kebiao
# 按照新的策划按进行修改了
#
# Revision 1.15  2008/04/30 06:36:37  kebiao
# 增加错误提示
#
# Revision 1.14  2008/04/30 01:45:41  kebiao
# 修改副本base的存储问题
#
# Revision 1.13  2008/04/28 06:58:15  kebiao
# no message
#
# Revision 1.12  2008/04/28 06:51:37  kebiao
# 修改 默认传出点为fengming 避免调试出的错误
#
# Revision 1.11  2008/04/25 06:21:51  kebiao
# no message
#
# Revision 1.10  2008/04/25 06:14:20  kebiao
# 添加杀怪信息显示
#
# Revision 1.9  2008/04/15 06:50:28  zhangyuxing
# 增加完成副本任务时，提示玩家退出副本
#
# Revision 1.8  2008/04/09 06:35:39  kebiao
# 添加BOSS发话，修改创建怪物时 字典copy相关BUG
#
# Revision 1.7  2008/03/25 02:48:36  kebiao
# 修改任务刷怪方式
#
# Revision 1.6  2008/03/14 07:49:50  kebiao
# no message
#
# Revision 1.5  2008/02/23 08:39:47  kebiao
# 调整潜能任务
#
# Revision 1.4  2008/02/20 06:37:48  kebiao
# 修正潜能点获得
#
# Revision 1.2  2008/02/18 08:52:47  kebiao
# 潜能任务调整
#
# Revision 1.1  2008/02/14 02:25:08  kebiao
# no message
#
#
