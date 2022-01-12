# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyPotential.py,v 1.17 2008-06-23 01:32:24 kebiao Exp $

"""
���������й���10��ˢ�µ㣬ÿ��8�����ꡣ
�������¹����������������ָ�ڸ�������ʱ�����븱������ң���������������ҡ���������������Ҳ���ٷ����ı䡣
����
1����ң����ȷ������5�飬ÿ�����ȷ��3���㣬������15�����
2����ң����ȷ������6�飬ÿ�����ȷ��5���㣬������30�����
3����ң����ȷ������9�飬ÿ�����ȷ��5���㣬������45�����
4����ң�10�飬ÿ�����ȷ��6���㣬������60�����
5����ң�10�飬ȫ��8���㣬������80�����
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


_TIMER_ID_DESTROY_TIME_ = 0x10 #������Ȼ����ʱ�� TIMER_ID
_QUERY_TEAM_STATE_		= 0x11 #���������Ҷ���״�� �Ƿ�������� �߳�

#����Ļ���ID   �ֱ��Ӧ սʿ�����ͣ� ���֣� ��ʦ�� ǿ����ְҵ�ĵ�11��ID
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

# �°汾���ӵ�С��ˢ�¹�������
monsterDatas = {}
"""
�˷�	10~50	սʿ	GW1118
GW1120	�񱩺���;Ѳɽ����;ɽկ����
�񱩺���;Ѳɽ����;ɽկ����
		����	GW1119
GW0475	������̽;ɽҰ����;ɽկ�̿�
������̽;ɽҰ����;ɽկ�̿�
		ǿ��	GW1116	ɽկ����;�����̴�;�ؼ�ǿ��
"""
for lv in xrange( 10, 51 ):
	d = {}
	# �����������ӦmonsterData սʿ������ ...
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
	# �����������ӦmonsterData սʿ������ ...
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
	# �����������ӦmonsterData սʿ������ ...
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

# ��������ˢ�ֵ����ӳ������
tmpmapping = {
		# ���� ���� ѡ������������ ˢ�ֵ�������� ��
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

# ���ݲ�ͬ���������ͣ���������ĵȼ�(���������._title)
changeLevelMapping = {
						cschannel_msgs.POTENTIAL_JIAO_FEI : 0,
						cschannel_msgs.POTENTIAL_CHU_YAO : 1,
						cschannel_msgs.POTENTIAL_JIANG_MO : 2,
					 }

_SPACE_LIVE_TIME = 3600

class SpaceCopyPotential( SpaceCopyTeam ):
	"""
	ע���˽ű�ֻ������ƥ��SpaceDomainCopy��SpaceCopy��̳�������ࡣ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopyTeam.__init__( self )

	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
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
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		@param entity: ͨ��Ϊ���
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		# ��ɫ�ڸ����е��߻����������ܳ����������
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
		�����Լ������ݳ�ʼ������ selfEntity ������
		"""
		SpaceCopyTeam.initEntity( self, selfEntity )
		# ����Ӫ�������� ������
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
		Ӫ������ˢ��
		"""
		if selfEntity.queryTemp( "yjnm_count", 0 ) > 0:
			posData = positions.pop( random.randint( 0, len( positions ) - 1 ) )
			selfEntity.createNPCObject( "10111182", posData[0], posData[1], { "tempMapping" : {  } } )
			selfEntity.setTemp( "yjnm_count", selfEntity.queryTemp( "yjnm_count", 0 ) - 1 )

	def castBossSmallMonsters( self, selfEntity ):
		"""
		ˢBOSS��С��
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
		ˢ��
		"""
		# ����ٻ�����
		monster_Count = 0
		cmc = selfEntity.queryTemp( "ConjureMonsterCount", 0 ) + 1
		selfEntity.setTemp( "ConjureMonsterCount", cmc ) # ��¼ˢ�ִ���
		questLevel = selfEntity.params[ "questLevel" ]
		changeLevel = selfEntity.params[ "changeLevel" ]

		if cmc <= 1:   # �ٻ�С��
			spawnPointBaseMBList = selfEntity.queryTemp( "spawnPointPotentialBaseMB", [] )
			level = questLevel + changeLevel
			monster_Count = len( spawnPointBaseMBList )
			selfEntity.setTemp( "Monster_Count", monster_Count )
			selfEntity.setTemp( "Monster_CountMax", monster_Count )

			#��������ʹ��
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
#			# ������������
#			for x in xrange( pgroups ):
#				idx = random.randint( 0, len( tmpPos ) - 1 )
#				tp = list( tmpPos.pop( idx ) )
#				for x1 in xrange( points ):
#					idx1 = random.randint( 0, len( tp ) - 1 )
#					positions.append( tp.pop( idx1 ) )
#
#			positions1 = list( positions )
#
#			# ˢ�����й���
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
#			#��������ʹ��
#			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEVEL, 		"" )
#			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_COPY_TITLE, cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN )
#			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, time.time() )
#			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, _SPACE_LIVE_TIME )
#			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, monster_Count )
#			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 0 )
		elif cmc == 2: # �ٻ�BOSS
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

			# ֪ͨ������boss ����
			self.statusMessageAllPlayer( selfEntity, BOSS_SPEAK[ random.randint( 0, len( BOSS_SPEAK ) - 1 ) ], monInfo[ "uname" ] )

	def banishAllPlayer( self, selfEntity ):
		"""
		����������ҳ�����
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
		if selfEntity.queryTemp( "timer_castMon", 0 ) == id: # ˢ�� ����¼������
			selfEntity.removeTemp( "timer_castMon" )
			self.castMonsters( selfEntity )
		elif selfEntity.queryTemp( "timer_leaveSpace", 0 ) == id:    # ���һ��BOSS��ɱ�� ��ʼ������������¼� ֪ͨ����뿪��������
			selfEntity.removeTemp( "timer_leaveSpace" )
			## ֪ͨNPC���٣� �����ʧ��NPC��Ϣ��ô���������� ��NPC�Լ�60���ӵ�����ʱ�������Լ� ���NPC����ʱ�䵽�������˾Ͳ���Ҫ��������������
			if selfEntity.queryTemp( "NPC_Dead", 0 ) == 0:
				selfEntity.params[ "NPCObjMailbox" ].cell.remoteScriptCall( "onDestroySelf", () )

			# ֪ͨ�������뿪����
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
			# ����Ƿ������뿪���� �о��߳�����  ���ﱻ���������ô�ø���һ����һ�����鴴����
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
		һ��entity���뵽spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onEnter()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: �����space��entity mailbox
		@param params: dict; �����spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnEnter()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopyTeam.onEnterCommon( self, selfEntity, baseMailbox, params )

		# ��������ȼ���ÿ��������ң� �����������ж�
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
		һ��entity׼���뿪spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onLeave()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: Ҫ�뿪��space��entity mailbox
		@param params: dict; �뿪��spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnLeave()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopyTeam.onLeaveCommon( self, selfEntity, baseMailbox, params )
		realEntity = BigWorld.entities[ baseMailbox.id ]
		realEntity.removeTemp( "questLevel" )
		realEntity.removeTemp( "space" )
		realEntity.removeTemp( "spaceClassName" )
		realEntity.removeTemp( "ownerDatabaseID" )
		if realEntity.findBuffsByBuffID( 99026 ):
			realEntity.removeBuffByBuffID( 99026, [ csdefine.BUFF_INTERRUPT_NONE ] )	# �����ʱ�������buff

	def statusMessageAllPlayer( self, selfEntity, msgKey, *args ):
		"""
		֪ͨ������ ָ������Ϣ
		"""
		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				p = BigWorld.entities[ e.id ]
				p.statusMessage( msgKey, *args )
			else:
				ERROR_MSG( "player %i not found" % e.id )

	def onKillMonster( self, selfEntity, isBoss ):
		"""
		ɱ������֪ͨ
		"""
		# ���ﱻɱ ��¼��ǰ����
		monster_Count = selfEntity.queryTemp( "Monster_Count", 0 ) - 1
		monster_CountMax = selfEntity.queryTemp( "Monster_CountMax", 1 )

		conjureMonsterCount = selfEntity.queryTemp( "ConjureMonsterCount", 0 )
		if conjureMonsterCount < 2:
			# ֪ͨ������ ����ʣ�µĹ�����Ϣ
			self.statusMessageAllPlayer( selfEntity, csstatus.ROLE_QUEST_POTENTIAL_KILL_INFO, cschannel_msgs.POTENTIAL_ZHUA_YA, monster_CountMax - monster_Count, monster_CountMax )

		#�ж��Ƿ����еĹ��ﶼ��ɱ��\ �������ɱ��  ��ô����ˢ��
		if monster_Count <= 0:
			selfEntity.setTemp( "timer_castMon", selfEntity.addTimer( 5.0, 0, 0x01 ) )

		if isBoss:
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 0 )

			# ���ˢ�ִ�������  ��ô����˳�ʱ��
			for e in selfEntity._players:
				# ֪ͨ���� �¼�����
				if BigWorld.entities.has_key( e.id ):	# �����С��ͼ�У���p����real entityʹ�á�
					p = BigWorld.entities[ e.id ]
					self.castPotentialBuff( p )
					ptQuestID = selfEntity.params[ "questID" ]
					p.questTaskIncreaseState( ptQuestID, 0 )
					potentialQDT = p.questsTable[ptQuestID]
					specialPtQuestID = potentialQDT.query( "specialPtQuestID", 0 )
					if specialPtQuestID:	# ����������⸱������һ���������
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
		����NPC����ʱ�䵽�� NPC����֪ͨ
		"""
		selfEntity = BigWorld.entities[ selfEntity.id ]
		if selfEntity.queryTemp( "timer_destroy", 0 ) == 0:
			selfEntity.setTemp( "timer_destroy", selfEntity.addTimer( 0, 60.0, _TIMER_ID_DESTROY_TIME_ ) )
		selfEntity.setTemp( "NPC_Dead", 1 )

	def createDoor( self, selfEntity ):
		"""
		����Door
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
		�������� Ǳ�ܼ��� BUFF
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
# �����µĲ߻��������޸���
#
# Revision 1.15  2008/04/30 06:36:37  kebiao
# ���Ӵ�����ʾ
#
# Revision 1.14  2008/04/30 01:45:41  kebiao
# �޸ĸ���base�Ĵ洢����
#
# Revision 1.13  2008/04/28 06:58:15  kebiao
# no message
#
# Revision 1.12  2008/04/28 06:51:37  kebiao
# �޸� Ĭ�ϴ�����Ϊfengming ������Գ��Ĵ���
#
# Revision 1.11  2008/04/25 06:21:51  kebiao
# no message
#
# Revision 1.10  2008/04/25 06:14:20  kebiao
# ���ɱ����Ϣ��ʾ
#
# Revision 1.9  2008/04/15 06:50:28  zhangyuxing
# ������ɸ�������ʱ����ʾ����˳�����
#
# Revision 1.8  2008/04/09 06:35:39  kebiao
# ���BOSS�������޸Ĵ�������ʱ �ֵ�copy���BUG
#
# Revision 1.7  2008/03/25 02:48:36  kebiao
# �޸�����ˢ�ַ�ʽ
#
# Revision 1.6  2008/03/14 07:49:50  kebiao
# no message
#
# Revision 1.5  2008/02/23 08:39:47  kebiao
# ����Ǳ������
#
# Revision 1.4  2008/02/20 06:37:48  kebiao
# ����Ǳ�ܵ���
#
# Revision 1.2  2008/02/18 08:52:47  kebiao
# Ǳ���������
#
# Revision 1.1  2008/02/14 02:25:08  kebiao
# no message
#
#
