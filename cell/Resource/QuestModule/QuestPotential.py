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
# 任务奖励潜能点数据
g_potential = {
	10:200, 11:220, 12:240, 13:260, 14:280, 15:300, 16:320, 17:340, 18:370, 19:390, 20:410, 21:430, 22:450, 23:470, 24:490, 25:510, 26:530, 27:550, 28:570, 29:600, 30:620, 31:640, 32:660, 33:680, 34:700, 35:720, 36:740, 37:760, 38:780, 39:800, 40:830, 41:850, 42:870, 43:890, 44:910, 45:930, 46:950, 47:970, 48:990, 49:1010, 50:1040, 51:1060, 52:1080, 53:1100, 54:1120, 55:1140, 56:1160, 57:1180, 58:1200, 59:1220, 60:1240, 61:1270, 62:1290, 63:1310, 64:1330, 65:1350, 66:1370, 67:1390, 68:1410, 69:1430, 70:1450, 71:1470, 72:1500, 73:1520, 74:1540, 75:1560, 76:1580, 77:1600, 78:1620, 79:1640, 80:1660, 81:1680, 82:1700, 83:1730, 84:1750, 85:1770, 86:1790, 87:1810, 88:1830, 89:1850, 90:1870, 91:1890, 92:1910, 93:1930, 94:1960, 95:1980, 96:2000, 97:2020, 98:2040, 99:2060, 100:2080, 101:2100, 102:2120, 103:2140, 104:2160, 105:2190, 106:2210, 107:2230, 108:2250, 109:2270, 110:2290, 111:2310, 112:2330, 113:2350, 114:2370, 115:2390, 116:2420, 117:2440, 118:2460, 119:2480, 120:2500, 121:2520, 122:2540, 123:2560, 124:2580, 125:2600, 126:2630, 127:2650, 128:2670, 129:2690, 130:2710, 131:2730, 132:2750, 133:2770, 134:2790, 135:2810, 136:2830, 137:2860, 138:2880, 139:2900, 140:2920, 141:2940, 142:2960, 143:2980, 144:3000, 145:3020, 146:3040, 147:3060, 148:3090, 149:3110, 150:3130,
}

# 任务奖励物品的数据
g_rewardItems = {
	#任务级别上限 11-30： [物品ID ]
	30  : [ 80101001, 80101007, 80101013, 80101019, 80101025, ], # 初级材料（原铁、丝绸、木材、玉石、皮革）
	50  : [ 80101002, 80101008, 80101014, 80101020, 80101026, ], # 一级材料（一级铁、一级丝绸、一级木材、一级玉石、一级皮革）
	80  : [ 80101003, 80101009, 80101015, 80101021, 80101027, ], # 二级材料（二级铁、二级丝绸、二级木材、二级玉石、二级皮革）
	100 : [ 80101004, 80101010, 80101016, 80101022, 80101028, ], # 三级材料（三级铁、三级丝绸、三级木材、三级玉石、三级皮革）
	130 : [ 80101005, 80101011, 80101017, 80101023, 80101029, ], # 四级材料（四级铁、四级丝绸、四级木材、四级玉石、四级皮革）
	150 : [ 80101006, 80101012, 80101018, 80101024, 80101030, ], # 五级材料（五级铁、五级丝绸、五级木材、五级玉石、五级皮革）
}
# 任务奖励物品的几率
g_rewardItemsRate = [
    #任务级别上限 11-30 ： 几率
	( 30, 0.1 ),
	( 50, 0.05 ),
	( 80, 0.05 ),
	( 100, 0.03 ),
	( 130, 0.03 ),
	( 150, 0.001 ),
]

"""
#进副本NPC的名字和模型信息
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
剿匪	10~50	强防	GW1114	土匪梅温华
			剑客	GW1115	山贼卜士孜
			战士	GW1117	草寇易根金
除妖	51~100	强防	GW1127	牛魔王
			战士	GW1121	百年黑熊精
				GW1125	黄狮老妖
			剑客	GW0484	疾风狼怪
降魔	101~150
"""
g_objNPCInfo = {}
#索引分别对应 战士0，剑客1， 射手2， 法师3， 强防型4 详细见 res\entities\cell\ObjectScripts\SpaceCopyPotential.py-> monsterData
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

#索引分别对应 战士0，剑客1， 射手2， 法师3， 强防型4 详细见 res\entities\cell\ObjectScripts\SpaceCopyPotential.py-> monsterData
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
	
# 级别低于15级时的信息
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
		@param section: 任务配置文件section
		@type  section: pyDataSection
		"""
		Quest.init( self, section )

		self.setType( 1, csdefine.QUEST_TYPE_POTENTIAL )
		self._playerLvLimit = ( section[ 'canLvMin' ].asInt, section[ 'canLvMax' ].asInt ) # 这个任务玩家可接的 最小级别与最大级别的参数 11-50
		QuestsFlyweight.instance().registerPotentialQuest( self._playerLvLimit[0], self._playerLvLimit[1], self.getID() )
		self._playerLvLimitTalks = ( section[ 'canLvMinTalk' ].asString, section[ 'canLvMaxTalk' ].asString )
		self._castNPCID = section[ 'castNPCID' ].asString  #刷出进入副本的NPC的编号
		self.maps_Names = {}
		self.questSpaceName = [] #self.questSpaceName = [ "potential1", "potential1", ]	#该任务所对应的副本SID
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
			if self.rewardsItemRate == 0 and f_Rate > 0: #取出一个机率
				self.rewardsItemRate = int(f_Rate * 100)
		
		#init reward potential
		pDataInfos = g_questRewardFromTable.get(str( self.getID() ))
		for key, value in pDataInfos.iteritems():
			instance = QTReward.createReward( "QTRewardPotential" )
			instance._potential = value["potential"]
			self._reward_lv[ key] = instance

	def getRewardsDetail( self, player ):
		"""
		获得奖励描述细节
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
		判断玩家的条件是否足够接当前任务。
		@return: 如果达不到接任务的要求则返回False。
		@rtype:  BOOL
		"""
		if not self.validQuestCondition( player ):
			return False
		return Quest.checkRequirement( self, player )

	def castNPC( self, player ):
		"""
		根据 player的级别 刷出指定NPC到某点
		@param      player: instance of Role Entity
		@type       player: Entity
		"""
		data = self.castNPCMaps[ random.randint( 0, len( self.castNPCMaps ) - 1 ) ]

		# 策划要求从该级别下 随机取一个级别的坐标点,由于字典的key值不一定是有序的，所以先排序
		sortPoints = data[ "points" ].keys()
		sortPoints.sort()
		randomLV = random.randint( sortPoints[0], player.level )
		if randomLV > player.level:
			randomLV = player.level

		posData = data[ "points" ][ randomLV ][ random.randint( 0, len( data[ "points" ][ randomLV ] ) - 1 ) ]
		#选定刷新地图 坐标 NPC编号
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

		# 对于本地空间则不需要转换空间 直接在当前空间创建
		currentMapName = player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		player.createNPCObjectFormBase( mapName, self._castNPCID, pos, player.direction, state )


		#将NPC相关信息保存到玩家身上 在接受任务时需要保存到任务中，避免下线后信息丢失PotentialIssuer
		player.setTemp( "potential_objnpc", npcName )
		player.setTemp( "des_position", pos )
		player.setTemp( "potential_map", self.maps_Names[ mapName ] )
		player.setTemp( "dest_space_id", mapName )
		player.setTemp( "monClassType", classType )
		player.setTemp( "potential_issuer_map", self.maps_Names[ currentMapName ] )

	def newTasks_( self, player ):
		"""
		virtual method. call by accept() method.
		开始新任务，产生一个与当前任务相关的任务目标实例

		@return: instance of QuestDataType or derive it；如果任务目标产生失败则必须返回None
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
		tasks.set( "style", self._style )			#任务样式存储
		tasks.set( "type", self._type )				#任务类型存储
		tasks.set( "lineNumber", player.getCurrentSpaceLineNumber() )

		intPosX = int( pos[0] )
		intPosZ = int( pos[2] )
		newPos = ( intPosX, intPosZ )
		#添加任务 潜能专用任务
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
			# 确定等级段
			if player.level <= lvMax:
				break

		# 只能获得该等级段的奖励
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
		执行任务实际处理
		"""
		if player.isTeamCaptain():
			#在族长周围30米范围内搜索所有家族成员并发送任务邀请
			for e in player.getAllMemberInRange( 30 ):
				initdict = tasks.__dict__.copy()
				ts = new.instance( tasks.__class__, initdict )
				e.potentialQuestShare( self.getID(), ts )
		else:
			player.questAdd( self, tasks )
			player.statusMessage( csstatus.ROLE_QUEST_QUEST_ACCEPTED, self._title )

	def sendQuestLog( self, playerEntity, questLog ):
		"""
		发送任务日志

		@param questLog: 任务日志; instance of QuestDataType
		"""
		npc    = playerEntity.questsTable[ self._id ].query( "potential_objnpc", "" )			#接任务的npc名
		map    = playerEntity.questsTable[ self._id ].query( "potential_map", "" )				#地图编号
		imap   = playerEntity.questsTable[ self._id ].query( "potential_issuer_map", "" )		#地图中文名
		pos    = playerEntity.questsTable[ self._id ].query( "des_position", ( 0, 0, 0 ) )		#任务生成的npc（如土匪梅温华）的坐标位置
		issuer = playerEntity.questsTable[ self._id ].query( "potential_issuer", "" )			#任务生成的npc名（如“土匪梅温华”）
		isuserID = playerEntity.questsTable[ self._id ].query( "potential_issuer_id", "" )		#接任务的npc的id
		smap = playerEntity.questsTable[ self._id ].query( "dest_space_id", "" )
		lv = playerEntity.questsTable[ self._id ].query( "qLevel", 0 )
		lineNumber = playerEntity.questsTable[ self._id ].query( "lineNumber", 0 )

		self._msg_objective = cschannel_msgs.POTENTIAL_VOICE16
		self._msg_log_detail = cschannel_msgs.POTENTIAL_VOICE17
		self._msg_objective = self._msg_objective % npc
		intPosX = int( pos[0] )
		intPosZ = int( pos[2] )
		newPos = ( intPosX, intPosZ )
		self._msg_detail = self._msg_log_detail % ( imap, issuer, isuserID, isuserID, map, smap, pos[0],pos[1], pos[2], lineNumber, '['+str(pos)+']', npc, str(newPos), '['+str(pos)+']' + '*' + smap ) #在描述信息加入地图名称 应付潜能任务自动寻路 by姜毅
		playerEntity.client.onQuestLogAdd( self._id, self._can_share, self._completeRuleType, questLog, lv, self.getRewardsDetail(playerEntity) )

	def reward_( self, player, rewardIndex = 0 ):
		"""
		virtual method. call by complete() method.
		给任务完成奖励。

		@param      player: instance of Role Entity
		@type       player: Entity
		@param rewardIndex: 选择奖励。
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
		任务被放弃，对玩家做点什么事情。

		@param player: instance of Role Entity
		@type  player: Entity
		@return: None
		"""
		BigWorld.globalData[ "PotentialQuestMgr" ].onUnRegisterPotentialObject( player.databaseID )
		# 给玩家惩罚 添加反省
		Love3.g_skills[122152001].receiveLinkBuff( player, player )
		for domain in BigWorld.globalData["SpaceDomainPotential"].values():
			domain.onDisableQuest( player.databaseID  )
		DEBUG_MSG( "player=%i, dbid=%i" % ( player.id, player.databaseID ) )
		return Quest.abandoned( self, player, flags )

	def gossipWith( self, player, issuer, dlgKey ):
		"""
		virtual method.
		任务对话(在标准任务情况下，此接口现在没有使用)

		@param player: 玩家entity
		@param issuer: 激活任务的entity(发放任务或接任务的对像)
		@param dlgKey: String; 对话关键字
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
				player.setTemp( "potential_issuer", g_objFactory.getObject( issuer.className ).getName() )	# 存入npc名
				player.setTemp( "potential_issuer_id", issuer.className )									# 存入npc id
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
		任务故事内容描述对白；
		显示此对白后就可以点“accept”接任务了；
		如果issuer为None则表示任务可能是从物品触发或player共享得来
		"""
		if issuer:	targetID = issuer.id
		else:		targetID = 0
		_msg_detail = cschannel_msgs.POTENTIAL_VOICE25
		_msg_objective = cschannel_msgs.POTENTIAL_VOICE26
		playerEntity.sendQuestRewards( self._id, self.getRewardsDetail( playerEntity ) )
		playerEntity.sendQuestDetail( self._id, self.getLevel( playerEntity ), targetID )



	def onComplete( self, player ):
		"""
		任务提交完成通知
		"""

		player.questPotentialFinish()
		return
#
# $Log: not supported by cvs2svn $
# Revision 1.39  2008/09/05 02:51:39  kebiao
# 修改新的刷怪点方式和对话方式
#
# Revision 1.38  2008/08/22 01:26:47  kebiao
# 由于上次调整物品ID 导致一些判断不对了 已经修正
#
# Revision 1.37  2008/08/09 08:41:14  songpeifang
# 增加了对潜能副本npc的引路蜂和自动寻路功能
#
# Revision 1.36  2008/08/09 01:52:32  wangshufeng
# 物品id类型调整，STRING -> INT32,相应调整代码。
#
# Revision 1.35  2008/08/07 08:57:41  zhangyuxing
# newTaskBegin 增加任务tasks作为参数
#
# Revision 1.34  2008/07/07 06:00:12  kebiao
# 修改任务对话
#
# Revision 1.33  2008/07/01 03:07:53  zhangyuxing
# 增加物品进入背包返回失败的状态
#
# Revision 1.32  2008/06/19 08:55:26  kebiao
# 按照新的策划按进行修改了
#
# Revision 1.31  2008/05/06 07:13:02  zhangyuxing
# 任务条件中，补充等级的判断
#
# Revision 1.30  2008/05/06 02:33:24  kebiao
# 添加任务完成时间条件
#
# Revision 1.29  2008/03/28 07:20:01  kebiao
# 调整数值
#
# Revision 1.28  2008/03/28 06:50:14  kebiao
# 调整数值
#
# Revision 1.27  2008/03/28 03:40:37  zhangyuxing
# 修改放弃任务的放弃方式
#
# Revision 1.26  2008/03/12 05:38:58  kebiao
# 修改addGossipOption相关接口
#
# Revision 1.25  2008/02/23 08:40:06  kebiao
# 调整潜能任务
#
# Revision 1.24  2008/02/18 08:52:58  kebiao
# 潜能任务调整
#
# Revision 1.23  2008/02/14 02:25:59  kebiao
# no message
#
# Revision 1.22  2008/02/03 08:17:59  kebiao
# 增加NPC刷新点坐标
#
# Revision 1.21  2008/02/03 00:52:18  kebiao
# 潜能任务调整
#
# Revision 1.20  2008/01/28 06:13:50  kebiao
# 重写该模块
#
#