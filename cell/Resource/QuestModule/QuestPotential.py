# -*- coding: gb18030 -*-
#
# $Id: QuestPotential.py,v 1.40 2008-09-05 03:53:23 kebiao Exp $

"""
"""
import BigWorld
import cschannel_msgs
import ShareTexts as ST
import csdefine
import random
import csconst
import items
import math
import time
import new
import sys
import Love3
import ItemTypeEnum
import QTReward
import QuestTaskDataType

from Resource.QuestLoader import QuestsFlyweight
from ObjectScripts.GameObjectFactory import g_objFactory
from Resource.SkillLoader import g_skills
from QTTask import *
from Quest import *
from bwdebug import *
from Resource.QuestRewardFromTableLoader import QuestRewardFromTableLoader

g_quests = QuestsFlyweight.instance()
g_questRewardFromTable = QuestRewardFromTableLoader.instance()
"""
# ������Ǳ�ܵ�����
g_potential = {
	10:200, 11:220, 12:240, 13:260, 14:280, 15:300, 16:320, 17:340, 18:370, 19:390, 20:410, 21:430, 22:450, 23:470, 24:490, 25:510, 26:530, 27:550, 28:570, 29:600, 30:620, 31:640, 32:660, 33:680, 34:700, 35:720, 36:740, 37:760, 38:780, 39:800, 40:830, 41:850, 42:870, 43:890, 44:910, 45:930, 46:950, 47:970, 48:990, 49:1010, 50:1040, 51:1060, 52:1080, 53:1100, 54:1120, 55:1140, 56:1160, 57:1180, 58:1200, 59:1220, 60:1240, 61:1270, 62:1290, 63:1310, 64:1330, 65:1350, 66:1370, 67:1390, 68:1410, 69:1430, 70:1450, 71:1470, 72:1500, 73:1520, 74:1540, 75:1560, 76:1580, 77:1600, 78:1620, 79:1640, 80:1660, 81:1680, 82:1700, 83:1730, 84:1750, 85:1770, 86:1790, 87:1810, 88:1830, 89:1850, 90:1870, 91:1890, 92:1910, 93:1930, 94:1960, 95:1980, 96:2000, 97:2020, 98:2040, 99:2060, 100:2080, 101:2100, 102:2120, 103:2140, 104:2160, 105:2190, 106:2210, 107:2230, 108:2250, 109:2270, 110:2290, 111:2310, 112:2330, 113:2350, 114:2370, 115:2390, 116:2420, 117:2440, 118:2460, 119:2480, 120:2500, 121:2520, 122:2540, 123:2560, 124:2580, 125:2600, 126:2630, 127:2650, 128:2670, 129:2690, 130:2710, 131:2730, 132:2750, 133:2770, 134:2790, 135:2810, 136:2830, 137:2860, 138:2880, 139:2900, 140:2920, 141:2940, 142:2960, 143:2980, 144:3000, 145:3020, 146:3040, 147:3060, 148:3090, 149:3110, 150:3130,
}

# ��������Ʒ������
g_rewardItems = {
	#���񼶱����� 11-30�� [��ƷID ]
	30  : [ 80101001, 80101007, 80101013, 80101019, 80101025, ], # �������ϣ�ԭ����˿��ľ�ġ���ʯ��Ƥ�
	50  : [ 80101002, 80101008, 80101014, 80101020, 80101026, ], # һ�����ϣ�һ������һ��˿��һ��ľ�ġ�һ����ʯ��һ��Ƥ�
	80  : [ 80101003, 80101009, 80101015, 80101021, 80101027, ], # �������ϣ�������������˿�񡢶���ľ�ġ�������ʯ������Ƥ�
	100 : [ 80101004, 80101010, 80101016, 80101022, 80101028, ], # �������ϣ�������������˿������ľ�ġ�������ʯ������Ƥ�
	130 : [ 80101005, 80101011, 80101017, 80101023, 80101029, ], # �ļ����ϣ��ļ������ļ�˿���ļ�ľ�ġ��ļ���ʯ���ļ�Ƥ�
	150 : [ 80101006, 80101012, 80101018, 80101024, 80101030, ], # �弶���ϣ��弶�����弶˿���弶ľ�ġ��弶��ʯ���弶Ƥ�
}
# ��������Ʒ�ļ���
g_rewardItemsRate = [
    #���񼶱����� 11-30 �� ����
	( 30, 0.1 ),
	( 50, 0.05 ),
	( 80, 0.05 ),
	( 100, 0.03 ),
	( 130, 0.03 ),
	( 150, 0.001 ),
]

"""
#������NPC�����ֺ�ģ����Ϣ
"""
g_objNPCInfo = {
	cschannel_msgs.POTENTIAL_SHAN_ZEI_ZHAO_LONG : ( "gw1114", "gw1115", "gw1116", "gw1117" ),
	cschannel_msgs.POTENTIAL_SHAN_ZEI_ZHANG_GUI : ( "gw1114", "gw1115", "gw1116", "gw1117" ),
	cschannel_msgs.POTENTIAL_SHAN_ZEI_WAN_ZHONG : ( "gw1114", "gw1115", "gw1116", "gw1117" ),
	cschannel_msgs.POTENTIAL_SHAN_ZEI_HONG_WU : ( "gw1114", "gw1115", "gw1116", "gw1117" ),
	cschannel_msgs.POTENTIAL_TU_FEI_XU_BA : ( "gw1114", "gw1115", "gw1116", "gw1117" ),
	cschannel_msgs.POTENTIAL_TU_FEI_WANG_MA_ZI : ( "gw1114", "gw1115", "gw1116", "gw1117" ),
	cschannel_msgs.POTENTIAL_TU_FEI_LIU_JIN : ( "gw1114", "gw1115", "gw1116", "gw1117" ),
	cschannel_msgs.POTENTIAL_TU_FEI_YANG_BIAO : ( "gw1114", "gw1115", "gw1116", "gw1117" ),
	cschannel_msgs.POTENTIAL_CAO_KOU_HUANG_XIN : ( "gw1114", "gw1115", "gw1116", "gw1117" ),
	cschannel_msgs.POTENTIAL_CAO_KOU_ZHANG_HUA : ( "gw1114", "gw1115", "gw1116", "gw1117" ),
	cschannel_msgs.POTENTIAL_CAO_KOU_DUAN_LIU : ( "gw1114", "gw1115", "gw1116", "gw1117" ),
	cschannel_msgs.POTENTIAL_CAO_KOU_JIN_QUAN : ( "gw1114", "gw1115", "gw1116", "gw1117" ),
	cschannel_msgs.POTENTIAL_QIANG_DAO_ZHU_FENG : ( "gw1114", "gw1115", "gw1116", "gw1117" ),
	cschannel_msgs.POTENTIAL_QIANG_DAO_GUO_SAN : ( "gw1114", "gw1115", "gw1116", "gw1117" ),
	cschannel_msgs.POTENTIAL_QIANG_DAO_SUN_HAI : ( "gw1114", "gw1115", "gw1116", "gw1117" ),
	cschannel_msgs.POTENTIAL_QIANG_DAO_QIAN_SHU : ( "gw1114", "gw1115", "gw1116", "gw1117" ),
	cschannel_msgs.POTENTIAL_KUANG_BAO_SHOU_YAO : ( "gw1121", ),
	cschannel_msgs.POTENTIAL_HEI_SHAN_LAO_YAO : ( "gw1129", ),
	cschannel_msgs.POTENTIAL_ZHAO_ZE_YAO_WANG : ( "gw1128", ),
	cschannel_msgs.POTENTIAL_SHI_XUE_KUANG_YAO : ( "gw1125", ),
	cschannel_msgs.POTENTIAL_MO_XING	   : ( "gw1130", ),
	cschannel_msgs.POTENTIAL_MO_YIN 	   : ( "gw1124", ),
	cschannel_msgs.POTENTIAL_MO_YI     : ( "gw1126", ),
	cschannel_msgs.POTENTIAL_MO_CHUI     : ( "gw1127", ),
}
"""
"""
�˷�	10~50	ǿ��	GW1114	����÷�»�
			����	GW1115	ɽ����ʿ��
			սʿ	GW1117	�ݿ��׸���
����	51~100	ǿ��	GW1127	ţħ��
			սʿ	GW1121	������ܾ�
				GW1125	��ʨ����
			����	GW0484	�����ǹ�
��ħ	101~150
"""
g_objNPCInfo = {}
#�����ֱ��Ӧ սʿ0������1�� ����2�� ��ʦ3�� ǿ����4 ��ϸ�� res\entities\cell\ObjectScripts\SpaceCopyPotential.py-> monsterData
for lv in xrange( 10, 51 ):
	d = {}
	d[ 0 ] = (
				( ("GW1114_5",), ( cschannel_msgs.POTENTIAL_MEI_WEN_HUA, ) ),
	)
	d[ 1 ] = (
				( ("GW1115_5",), ( cschannel_msgs.POTENTIAL_BU_XUE_HAO, ) ),
			)
	d[ 2 ] = (
				( ("GW1117_5",), ( cschannel_msgs.POTENTIAL_YI_GEN_JIN, ) ),
			)
#	d[ 4 ] = (
#				( ("GW1114_1",), ( cschannel_msgs.POTENTIAL_TU_FEI_MEI_WEN_HUA, ) ),
#	)
#	d[ 1 ] = (
#				( ("GW1115_1",), ( cschannel_msgs.POTENTIAL_SHAN_ZEI_BO_SHI_ZI, ) ),
#			)
#	d[ 0 ] = (
#				( ("GW1117_1",), ( cschannel_msgs.POTENTIAL_CAO_KOU_YI_GEN_JIN, ) ),
#			)
	g_objNPCInfo[ lv ] = d

#�����ֱ��Ӧ սʿ0������1�� ����2�� ��ʦ3�� ǿ����4 ��ϸ�� res\entities\cell\ObjectScripts\SpaceCopyPotential.py-> monsterData
for lv in xrange( 51, 101 ):
	d = {}
	d[ 3 ] = (
				( ("GW1127_5", ), ( cschannel_msgs.POTENTIAL_NIU_ZHAN_SHAN, ) ),
			)
	d[ 4 ] = (
				( ("GW1125_5", ), ( cschannel_msgs.POTENTIAL_SHI_WU_CHANG, ) ),
			)
	d[ 5 ] = (
				( ("GW1191_2", ), ( cschannel_msgs.POTENTIAL_HOU_TONG_TIAN, ) ),
			)
	d[ 6 ] = (
				( ("GW1250_2", ), ( cschannel_msgs.POTENTIAL_YU_FAN_JIANG, ) ),
			)
	d[ 7 ] = (
				( ("GW1300_2", ), ( cschannel_msgs.POTENTIAL_TANG_LANG, ) ),
			)
	d[ 8 ] = (
				( ("GW1121_5", ), ( cschannel_msgs.POTENTIAL_XIONG_TIAN_LEI , ) ),
			)
#	d[ 4 ] = (
#				( ("GW1127_1", ), ( cschannel_msgs.POTENTIAL_NIU_MO_WANG,   ) ),
#				( ("GW0487_1", ), ( cschannel_msgs.POTENTIAL_DUO_LUO_TIAN_JIANG, ) ),
#			)
#	d[ 0 ] = (
#				( ( "GW1125_1", ), ( cschannel_msgs.POTENTIAL_HUANG_SHI_LAO_YAO, ) ),
#				( ( "GW0489_1", ), ( cschannel_msgs.POTENTIAL_NIU_YAO_XIAO_JIANG, ) ),
#				( ( "GW0490_1", ), ( cschannel_msgs.POTENTIAL_HUN__TIAN_BING, ) ),
#			)
#	d[ 1 ] = (
#				( ("gw0491_1", ), ( cschannel_msgs.POTENTIAL_XUE_JIAN_YAO_JIANG, ) ),
#			)
#	d[ 2 ] = (
#				( ("gw0492_1", ), ( cschannel_msgs.POTENTIAL_SHEN_GONG_YAO_JIANG, ) ),
#			)
	g_objNPCInfo[ lv ] = d

for lv in xrange( 101, 151 ):
	d = {}
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
	
	g_objNPCInfo[ lv ] = d
	
# �������15��ʱ����Ϣ
g_Dialog_LevelLower15 = cschannel_msgs.POTENTIAL_VOICE14
POTENTIAL_LOW_LEVEL   = 15

class QuestPotential( Quest ):
	def __init__( self ):
		"""
		"""
		Quest.__init__( self )
		self._reward_lv = {}
		self.rewardsItemList = {}
		self.rewardsItemRate = 0
		self._style = csdefine.QUEST_STYLE_POTENTIAL
		"""
		for info in g_potential.iteritems():
			instance = QTReward.createReward( "QTRewardPotential" )
			instance._potential = info[1]
			self._reward_lv[ info[0] ] = instance
		"""

	def init( self, section ):
		"""
		virtual method.
		@param section: ���������ļ�section
		@type  section: pyDataSection
		"""
		Quest.init( self, section )

		self.setType( 1, csdefine.QUEST_TYPE_POTENTIAL )
		self._playerLvLimit = ( section[ 'canLvMin' ].asInt, section[ 'canLvMax' ].asInt ) # ���������ҿɽӵ� ��С��������󼶱�Ĳ��� 11-50
		QuestsFlyweight.instance().registerPotentialQuest( self._playerLvLimit[0], self._playerLvLimit[1], self.getID() )
		self._playerLvLimitTalks = ( section[ 'canLvMinTalk' ].asString, section[ 'canLvMaxTalk' ].asString )
		self._castNPCID = section[ 'castNPCID' ].asString  #ˢ�����븱����NPC�ı��
		self.maps_Names = {}
		self.questSpaceName = [] #self.questSpaceName = [ "potential1", "potential1", ]	#����������Ӧ�ĸ���SID
		for item in section[ 'questSpaceName' ].values():
			self.questSpaceName.append( (item["mapType"].asString, item["mapName"].asString, item["rate"].asFloat) )
			self.maps_Names[ item["mapType"].asString ] = item["mapName"].asString

		self.castNPCMaps = []
		for item in section[ 'castNPCMaps' ].values():
			pmapping = {}
			d = { "mapSID" : item[ "mapSID" ].asString, "points" : pmapping }
			self.maps_Names[ item[ "mapSID" ].asString ] = item[ "mapName" ].asString

			for item1 in item[ "points" ].values():
				points = []
				lvMin = item1[ "lvMin" ].asInt
				lvMax = item1[ "lvMax" ].asInt

				for info in item1[ "points" ].values():
					points.append( ( info[ "spaceName" ].asString, info[ "pos" ].asVector3 ) )

				for xy in xrange( lvMin, lvMax + 1 ):
					pmapping[ xy ] = points

			self.castNPCMaps.append( d )
		
		#init reward item
		for reItem in section[ 'rewards_items' ].values():
			if reItem["itemID"].asInt < 0:
				continue
			f_Rate = reItem["rate"].asFloat
			self.rewardsItemList[ reItem["itemID"].asInt ] = (reItem["amount"].asInt, f_Rate)
			if self.rewardsItemRate == 0 and f_Rate > 0: #ȡ��һ������
				self.rewardsItemRate = int(f_Rate * 100)
		
		#init reward potential
		pDataInfos = g_questRewardFromTable.get(str( self.getID() ))
		for key, value in pDataInfos.iteritems():
			instance = QTReward.createReward( "QTRewardPotential" )
			instance._potential = value["potential"]
			self._reward_lv[ key] = instance

	def getRewardsDetail( self, player ):
		"""
		��ý�������ϸ��
		"""
		lv = player.level
		if player.has_quest( self._id ):
			lv = player.questsTable[ self._id ].query( "qLevel", 0 )
		return [ self._reward_lv[ lv ].transferForClient( player, self._id ) ]

	def validQuestCondition( self, player ):
		"""
		"""
		if player.level < self._playerLvLimit[0] or player.level > self._playerLvLimit[1]:
			return False
		return True

	def checkRequirement( self, player ):
		"""
		virtual method.
		�ж���ҵ������Ƿ��㹻�ӵ�ǰ����
		@return: ����ﲻ���������Ҫ���򷵻�False��
		@rtype:  BOOL
		"""
		if not self.validQuestCondition( player ):
			return False
		return Quest.checkRequirement( self, player )

	def castNPC( self, player ):
		"""
		���� player�ļ��� ˢ��ָ��NPC��ĳ��
		@param      player: instance of Role Entity
		@type       player: Entity
		"""
		data = self.castNPCMaps[ random.randint( 0, len( self.castNPCMaps ) - 1 ) ]

		# �߻�Ҫ��Ӹü����� ���ȡһ������������,�����ֵ��keyֵ��һ��������ģ�����������
		sortPoints = data[ "points" ].keys()
		sortPoints.sort()
		randomLV = random.randint( sortPoints[0], player.level )
		if randomLV > player.level:
			randomLV = player.level

		posData = data[ "points" ][ randomLV ][ random.randint( 0, len( data[ "points" ][ randomLV ] ) - 1 ) ]
		#ѡ��ˢ�µ�ͼ ���� NPC���
		mapName = posData[ 0 ]
		pos = posData[ 1 ]
		tmp = g_objNPCInfo[ player.level ]
		tmpItem = tmp.items()[ random.randint( 0, len( tmp ) - 1 ) ]
		classType = tmpItem[0]
		tpInfo = tmpItem[1][ random.randint( 0, len( tmpItem[1] ) - 1 ) ]
		npcName = tpInfo[1][ random.randint( 0, len( tpInfo[1] ) - 1 ) ]
		mn = tpInfo[0][ random.randint( 0, len( tpInfo[0] ) - 1 ) ]
		title = cschannel_msgs.POTENTIAL_VOICE15 % player.getName()
		state = { "randomWalkRange" : 3, "spawnPos" : pos, "level" : 0, "uname" : npcName, "modelNumber" : mn.lower(), "lifetime" : 60.0 * 60.0, "title" : title, "tempMapping" : { "ownerDatabaseID" : player.databaseID, "questID" : self.getID(), "monClassType" : classType } }

		# ���ڱ��ؿռ�����Ҫת���ռ� ֱ���ڵ�ǰ�ռ䴴��
		currentMapName = player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		player.createNPCObjectFormBase( mapName, self._castNPCID, pos, player.direction, state )


		#��NPC�����Ϣ���浽������� �ڽ�������ʱ��Ҫ���浽�����У��������ߺ���Ϣ��ʧPotentialIssuer
		player.setTemp( "potential_objnpc", npcName )
		player.setTemp( "des_position", pos )
		player.setTemp( "potential_map", self.maps_Names[ mapName ] )
		player.setTemp( "dest_space_id", mapName )
		player.setTemp( "monClassType", classType )
		player.setTemp( "potential_issuer_map", self.maps_Names[ currentMapName ] )

	def newTasks_( self, player ):
		"""
		virtual method. call by accept() method.
		��ʼ�����񣬲���һ���뵱ǰ������ص�����Ŀ��ʵ��

		@return: instance of QuestDataType or derive it���������Ŀ�����ʧ������뷵��None
		@rtype:  QuestDataType/None
		"""
		self.castNPC( player )
		self.gossipWith( player, BigWorld.entities[ player.popTemp( "qpnpc_id", 0 ) ], "Q30801001.5" )

		tasks = Quest.newTasks_( self, player )
		npcName   = player.queryTemp( "potential_objnpc", "" )
		smap = player.queryTemp( "dest_space_id", "" )
		pos = player.queryTemp( "des_position", ( 0, 0, 0 ) )
		tasks.set( "potential_objnpc",  npcName )
		tasks.set( "dest_space_id",  smap )
		tasks.set( "des_position",  pos )
		tasks.set( "potential_map",  player.queryTemp( "potential_map", "" ) )
		tasks.set( "potential_issuer_map",  player.queryTemp( "potential_issuer_map", "" ) )
		tasks.set( "potential_issuer",  player.queryTemp( "potential_issuer", "" ) )
		tasks.set( "potential_issuer_id",  player.queryTemp( "potential_issuer_id", "" ) )
		tasks.set( "monClassType", player.queryTemp( "monClassType", "zhaobudao" ) )
		tasks.set( "qLevel", player.level )
		tasks.set( "style", self._style )			#������ʽ�洢
		tasks.set( "type", self._type )				#�������ʹ洢
		tasks.set( "lineNumber", player.getCurrentSpaceLineNumber() )

		intPosX = int( pos[0] )
		intPosZ = int( pos[2] )
		newPos = ( intPosX, intPosZ )
		#������� Ǳ��ר������
		instance = QuestTaskDataType.createTask( "QTTaskPotential" )
		instance.index = 0
		instance.str2 = cschannel_msgs.POTENTIAL_VOICE37 % ( npcName, str(newPos), '['+str(pos)+']' + '*' + smap )
		instance.val1 = 0
		instance.val2 = 1
		instance1 = QuestTaskDataType.createTask( "QTTaskTime" )
		instance1.index = 1
		instance1._lostTime = 60 * 60
		tasks.setTasks( { instance.index : instance.newTaskBegin( player, tasks ), instance1.index : instance1.newTaskBegin( player, tasks ) }  )
		
		"""
		for lvMax, rate in g_rewardItemsRate:
			# ȷ���ȼ���
			if player.level <= lvMax:
				break

		# ֻ�ܻ�øõȼ��εĽ���
		if random.random() <= rate:
			itemIDs = g_rewardItems[ lvMax ]
			tasks.set( "rewardItemID", itemIDs[ random.randint( 0, len( itemIDs ) - 1 ) ] )
		"""
		if random.randint(1, 100) <= self.rewardsItemRate:
			itemIDs = self.rewardsItemList.keys()
			tasks.set( "rewardItemID", itemIDs[ random.randint( 0, len( itemIDs ) - 1 ) ] )
		return tasks

	def onAccept( self, player, tasks ):
		"""
		virtual method.
		ִ������ʵ�ʴ���
		"""
		if player.isTeamCaptain():
			#���峤��Χ30�׷�Χ���������м����Ա��������������
			for e in player.getAllMemberInRange( 30 ):
				initdict = tasks.__dict__.copy()
				ts = new.instance( tasks.__class__, initdict )
				e.potentialQuestShare( self.getID(), ts )
		else:
			player.questAdd( self, tasks )
			player.statusMessage( csstatus.ROLE_QUEST_QUEST_ACCEPTED, self._title )

	def sendQuestLog( self, playerEntity, questLog ):
		"""
		����������־

		@param questLog: ������־; instance of QuestDataType
		"""
		npc    = playerEntity.questsTable[ self._id ].query( "potential_objnpc", "" )			#�������npc��
		map    = playerEntity.questsTable[ self._id ].query( "potential_map", "" )				#��ͼ���
		imap   = playerEntity.questsTable[ self._id ].query( "potential_issuer_map", "" )		#��ͼ������
		pos    = playerEntity.questsTable[ self._id ].query( "des_position", ( 0, 0, 0 ) )		#�������ɵ�npc��������÷�»���������λ��
		issuer = playerEntity.questsTable[ self._id ].query( "potential_issuer", "" )			#�������ɵ�npc�����硰����÷�»�����
		isuserID = playerEntity.questsTable[ self._id ].query( "potential_issuer_id", "" )		#�������npc��id
		smap = playerEntity.questsTable[ self._id ].query( "dest_space_id", "" )
		lv = playerEntity.questsTable[ self._id ].query( "qLevel", 0 )
		lineNumber = playerEntity.questsTable[ self._id ].query( "lineNumber", 0 )

		self._msg_objective = cschannel_msgs.POTENTIAL_VOICE16
		self._msg_log_detail = cschannel_msgs.POTENTIAL_VOICE17
		self._msg_objective = self._msg_objective % npc
		intPosX = int( pos[0] )
		intPosZ = int( pos[2] )
		newPos = ( intPosX, intPosZ )
		self._msg_detail = self._msg_log_detail % ( imap, issuer, isuserID, isuserID, map, smap, pos[0],pos[1], pos[2], lineNumber, '['+str(pos)+']', npc, str(newPos), '['+str(pos)+']' + '*' + smap ) #��������Ϣ�����ͼ���� Ӧ��Ǳ�������Զ�Ѱ· by����
		playerEntity.client.onQuestLogAdd( self._id, self._can_share, self._completeRuleType, questLog, lv, self.getRewardsDetail(playerEntity) )

	def reward_( self, player, rewardIndex = 0 ):
		"""
		virtual method. call by complete() method.
		��������ɽ�����

		@param      player: instance of Role Entity
		@type       player: Entity
		@param rewardIndex: ѡ������
		@type  rewardIndex: UINT8
		@return: BOOL
		@rtype:  BOOL
		"""
		lv = player.questsTable[ self._id ].query( "qLevel", 0 )
		rewardItemID = player.questsTable[ self._id ].query( "rewardItemID", 0 )
		rewardItem = None
		if rewardItemID > 0:
			rewardItem = items.instance().createDynamicItem( rewardItemID, 1 )
			ret = player.checkItemsPlaceIntoNK_( [ rewardItem ] )
			if ret == csdefine.KITBAG_NO_MORE_SPACE:
				player.statusMessage( csstatus.ROLE_QUEST_KITBAG_FULL_FOR_COMPLETE )
				return False
			elif ret == csdefine.KITBAG_ITEM_COUNT_LIMIT:
				player.statusMessage( csstatus.ROLE_QUEST_KITBAG_ITEM_LIMIT_FOR_COMPLETE )
				return False

		if not self._reward_lv[ lv ].check( player ):
			return False

		if 	rewardItem is not None:
			player.addItemAndRadio( rewardItem, ItemTypeEnum.ITEM_GET_QUEST, reason = csdefine.ADD_ITEM_QUESTPOTENTIAL )

		self._reward_lv[ lv ].do( player, g_quests.getPotentialLvQuestMapping( lv ) )
		return Quest.reward_( self, player, rewardIndex )

	def abandoned( self, player, flags ):
		"""
		virtual method.
		���񱻷��������������ʲô���顣

		@param player: instance of Role Entity
		@type  player: Entity
		@return: None
		"""
		BigWorld.globalData[ "PotentialQuestMgr" ].onUnRegisterPotentialObject( player.databaseID )
		# ����ҳͷ� ��ӷ�ʡ
		Love3.g_skills[122152001].receiveLinkBuff( player, player )
		for domain in BigWorld.globalData["SpaceDomainPotential"].values():
			domain.onDisableQuest( player.databaseID  )
		DEBUG_MSG( "player=%i, dbid=%i" % ( player.id, player.databaseID ) )
		return Quest.abandoned( self, player, flags )

	def gossipWith( self, player, issuer, dlgKey ):
		"""
		virtual method.
		����Ի�(�ڱ�׼��������£��˽ӿ�����û��ʹ��)

		@param player: ���entity
		@param issuer: ���������entity(��������������Ķ���)
		@param dlgKey: String; �Ի��ؼ���
		"""
		qids = player.findQuestByType( csdefine.QUEST_TYPE_POTENTIAL )

		if len( qids ) <= 0 :
			qID = self.getID()
		else:
			qID = qids[ 0 ]

		state = g_quests[ qID ].query( player )

		if dlgKey == "Talk":
			buff = g_skills[ 122152001 ].getBuffLink( 0 ).getBuff()
			if player.isInTeam() and not player.isTeamCaptain() and state == csdefine.QUEST_STATE_NOT_HAVE:
				player.setGossipText(cschannel_msgs.POTENTIAL_VOICE18)
				player.sendGossipComplete( issuer.id )
				return
			if len( player.findBuffsByBuffID( buff.getBuffID() ) ) > 0:
				player.setGossipText(cschannel_msgs.POTENTIAL_VOICE19)
				player.sendGossipComplete( issuer.id )
				return
			if player.level < POTENTIAL_LOW_LEVEL:
#				player.setGossipText( self._playerLvLimitTalks[0] )
				player.setGossipText( g_Dialog_LevelLower15 )
				player.sendGossipComplete( issuer.id )
				return
			elif player.level < self._playerLvLimit[ 0 ]:
				questID = g_quests.getPotentialLvQuestMapping( player.level )
				quest = g_quests[ questID ]
				if not quest.castNPCMaps:
					player.setGossipText( cschannel_msgs.POTENTIAL_VOICE5 )
					player.sendGossipComplete( issuer.id )
					ERROR_MSG( "Level %i, QuestPotential %i from %s has no castMaps."%( player.level, questID, issuer.className ) )
					return
				npcID = quest.getObjectIdsOfStart()
				npcID = npcID[ random.randint( 0, len( npcID )-1 ) ]
				npcName = g_objFactory.getObject( npcID ).getName()
				map = quest.maps_Names[ quest.castNPCMaps[0][ "mapSID" ] ]
				t = self._playerLvLimitTalks[0]
				t = t.replace( "[map]", map )
				t = t % ( npcName, npcID, npcID )
				player.setGossipText( t )
				player.sendGossipComplete( issuer.id )
				return
			if not player.has_quest( self.getID() ) and player.level > self._playerLvLimit[ 1 ]:
				questID = g_quests.getPotentialLvQuestMapping( player.level )
				quest = g_quests[ questID ]
				if not quest.castNPCMaps:
					player.setGossipText( cschannel_msgs.POTENTIAL_VOICE5 )
					player.sendGossipComplete( issuer.id )
					ERROR_MSG( "Level %i, QuestPotential %i from %s has no castMaps."%( player.level, questID, issuer.className ) )
					return
				npcID = quest.getObjectIdsOfStart()
				npcID = npcID[ random.randint( 0, len( npcID ) - 1 ) ]
				npcName = g_objFactory.getObject( npcID ).getName()
				map = quest.maps_Names[ quest.castNPCMaps[0][ "mapSID" ] ]
				t = self._playerLvLimitTalks[ 1 ]
				t = t.replace( "[map]", map )
				player.setGossipText( t % ( npcName, npcID, npcID ) )
				player.sendGossipComplete( issuer.id )
				return
			if state == csdefine.QUEST_STATE_NOT_HAVE:
				player.setGossipText(cschannel_msgs.POTENTIAL_VOICE20)
				player.addGossipOption( "Q30801001.1", cschannel_msgs.GOSSIP_4, state )
				player.sendGossipComplete( issuer.id )
			elif state == csdefine.QUEST_STATE_FINISH:
				player.setGossipText(cschannel_msgs.POTENTIAL_VOICE21)
				player.addGossipOption( "Q30801001.3", cschannel_msgs.GOSSIP_5, state )
				player.sendGossipComplete( issuer.id )
			elif state == csdefine.QUEST_STATE_NOT_FINISH:
				player.setGossipText(cschannel_msgs.POTENTIAL_VOICE22)
				player.addGossipOption( "Q30801001.2", cschannel_msgs.GOSSIP_6, state )
				player.sendGossipComplete( issuer.id )
		elif dlgKey == "Q30801001.1":
			if state == csdefine.QUEST_STATE_NOT_HAVE:
				player.setTemp( "potential_issuer", g_objFactory.getObject( issuer.className ).getName() )	# ����npc��
				player.setTemp( "potential_issuer_id", issuer.className )									# ����npc id
				player.setTemp( "qpnpc_id", issuer.id )
				self.gossipDetail( player, issuer )
		elif dlgKey == "Q30801001.2":
			player.setGossipText(cschannel_msgs.POTENTIAL_VOICE23)
			player.addGossipOption( "Q30801001.4", cschannel_msgs.GOSSIP_7, state )
			player.sendGossipComplete( issuer.id )
		elif dlgKey == "Q30801001.3":
			g_quests[ qID ].complete( player, 0 )
			player.endGossip( issuer.id )
		elif dlgKey == "Q30801001.4":
			player.endGossip( issuer.id )
			player.abandonQuest( player.id, qID )
		elif dlgKey == "Q30801001.5":
			npc = player.queryTemp( "potential_objnpc", "" )
			map = player.queryTemp( "potential_map", "" )
			pos = player.queryTemp( "des_position", ( 0, 0, 0 ) )
			smap = player.queryTemp( "dest_space_id", "" )
			player.setGossipText( cschannel_msgs.POTENTIAL_VOICE24	% ( npc,  int(pos[0]), int(pos[2]), '['+str(pos)+']' + '*' + smap,  map, smap, pos[0], pos[1], pos[2], player.getCurrentSpaceLineNumber(), '['+str(pos)+']' ) )
			player.sendGossipComplete( issuer.id )

	def gossipDetail( self, playerEntity, issuer = None ):
		"""
		����������������԰ף�
		��ʾ�˶԰׺�Ϳ��Ե㡰accept���������ˣ�
		���issuerΪNone���ʾ��������Ǵ���Ʒ������player�������
		"""
		if issuer:	targetID = issuer.id
		else:		targetID = 0
		_msg_detail = cschannel_msgs.POTENTIAL_VOICE25
		_msg_objective = cschannel_msgs.POTENTIAL_VOICE26
		playerEntity.sendQuestRewards( self._id, self.getRewardsDetail( playerEntity ) )
		playerEntity.sendQuestDetail( self._id, self.getLevel( playerEntity ), targetID )



	def onComplete( self, player ):
		"""
		�����ύ���֪ͨ
		"""

		player.questPotentialFinish()
		return
#
# $Log: not supported by cvs2svn $
# Revision 1.39  2008/09/05 02:51:39  kebiao
# �޸��µ�ˢ�ֵ㷽ʽ�ͶԻ���ʽ
#
# Revision 1.38  2008/08/22 01:26:47  kebiao
# �����ϴε�����ƷID ����һЩ�жϲ����� �Ѿ�����
#
# Revision 1.37  2008/08/09 08:41:14  songpeifang
# �����˶�Ǳ�ܸ���npc����·����Զ�Ѱ·����
#
# Revision 1.36  2008/08/09 01:52:32  wangshufeng
# ��Ʒid���͵�����STRING -> INT32,��Ӧ�������롣
#
# Revision 1.35  2008/08/07 08:57:41  zhangyuxing
# newTaskBegin ��������tasks��Ϊ����
#
# Revision 1.34  2008/07/07 06:00:12  kebiao
# �޸�����Ի�
#
# Revision 1.33  2008/07/01 03:07:53  zhangyuxing
# ������Ʒ���뱳������ʧ�ܵ�״̬
#
# Revision 1.32  2008/06/19 08:55:26  kebiao
# �����µĲ߻��������޸���
#
# Revision 1.31  2008/05/06 07:13:02  zhangyuxing
# ���������У�����ȼ����ж�
#
# Revision 1.30  2008/05/06 02:33:24  kebiao
# ����������ʱ������
#
# Revision 1.29  2008/03/28 07:20:01  kebiao
# ������ֵ
#
# Revision 1.28  2008/03/28 06:50:14  kebiao
# ������ֵ
#
# Revision 1.27  2008/03/28 03:40:37  zhangyuxing
# �޸ķ�������ķ�����ʽ
#
# Revision 1.26  2008/03/12 05:38:58  kebiao
# �޸�addGossipOption��ؽӿ�
#
# Revision 1.25  2008/02/23 08:40:06  kebiao
# ����Ǳ������
#
# Revision 1.24  2008/02/18 08:52:58  kebiao
# Ǳ���������
#
# Revision 1.23  2008/02/14 02:25:59  kebiao
# no message
#
# Revision 1.22  2008/02/03 08:17:59  kebiao
# ����NPCˢ�µ�����
#
# Revision 1.21  2008/02/03 00:52:18  kebiao
# Ǳ���������
#
# Revision 1.20  2008/01/28 06:13:50  kebiao
# ��д��ģ��
#
#