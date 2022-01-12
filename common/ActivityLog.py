# -*- coding: gb18030 -*-
"""
此部分主要作用有：
1、任务
2、活动（奖励部分）
3、副本参与
"""
import csdefine
import BigWorld
from Message_logger import *
from bwdebug import *


#任务类型活动（三环几率在任务类型活动中）
QUEST_ACTIVITYS = {	csdefine.ACTIVITY_LOOP_QUEST_30_59 		: [80102,80103,80104],
					csdefine.ACTIVITY_LOOP_QUEST_60_95 		: [80105,80106,80107],
					csdefine.ACTIVITY_TAO_FA				: [30101,30102,30103,30104,30105,30106,30107],
					csdefine.ACTIVITY_NORMAL_DART			: [30401001,30401002,30401003,30401004,30401005,30401006,30401007,30401008,30401009,30401010,30402001,30402002,30402003,30402004,30402005,30402006,30402007,30402008,30402009,30402010,30401031,30401032,30402031,30402032],
					csdefine.ACTIVITY_EXP_DART				: [30401011,30401012,30401013,30401014,30401015,30401016,30401017,30401018,30401019,30401020,30402011,30402012,30402013,30402014,30402015,30402016,30402017,30402018,30402019,30402020,30401033,30402033,30401037,30402037],
					csdefine.ACTIVITY_FAMILY_DART			: [30401021,30401022,30401023,30401024,30401025,30401026,30401027,30401028,30401029,30401030,30402021,30402022,30402023,30402024,30402025,30402026,30402027,30402028,30402029,30402030,30401035,30401036,30402035,30402036],
					csdefine.ACTIVITY_CAI_LIAO_QUEST		: [30501,30502,30503,30504,30505,30506,30507],
					csdefine.ACTIVITY_KE_JU_QUEST			: [30701001,30701002,30701003],
					csdefine.ACTIVITY_JIAO_FEI_QUEST		: [30801001,30803001,30801002,30801003],
					csdefine.ACTIVITY_CHU_YAO_QUEST			: [30803002,30803003,30803004,30803005,30803006],
					csdefine.ACTIVITY_SHANG_HUI_QUEST		: [40101002,40101003,40101004,40101005,40101006,40101007,40101008,40101009,40101010,40101011,40101012,40101013,40101014,40101015,40101016,40101017,40101018,40101019,40101020,40101021,40101022,40101023,40101024,40101025,40101026,40101027,40101028,40101029,40101030,40101031,40101032,40101033,40101034,40101035,40101036,40101037,40101038,40101039,40101040,40101041,40101042,40101043,40101044,40101045,40101046,40101047,40101048,40101049,40101050,40101051,40101052,40101053,40101054,40101055,40101056,40101057,40101058,40101059,40101060,40101061,40101062,40101063,40101064,40101065,40101066,40101067,40101068,40101069,40101070,40101071,40101072,40101073,40101074,40101075,40101076,40101077,40101078,40101079,40101080,40101081,40101082,40101083,40101084,40101085,40101086,40101087,40101088,40101089,40101090,40101091,40101092,40101093,40101094,40101095,40101096,40101097,40101098,40101099,40101100,40101101,40101102],
					csdefine.ACTIVITY_SHENG_WANG			: [40201001,40201012,40201017,40201022,50401002,50401005,50401011,50401014,50401019,50401025,50401028,50401034,50401037,40201002,40201013,40201018,40201023,50401003,50401006,50401012,50401015,50401020,50401026,50401029,50401035,50401038,40201003,40201014,40201019,40201024,50401004,50401007,50401013,50401016,50401021,50401027,50401030,50401036,50401039,40201004,40201015,40201020,40201025,50401008,50401017,50401022,50401031,50401040,40201005,40201016,40201021,40201026,50401009,50401018,50401023,50401032,50401041,40201006,50401058,50401059,50401060,50401061,50401062,40201007,40201008,40201009,40201010,50401050,50401053,40201027,40201032,40201037,40201040,40201045,50401051,50401054,40201028,40201033,40201038,40201041,40201046,50401052,50401055,40201029,40201034,40201039,40201042,40201047,50401056,40201030,40201035,40201043,40201048,50401057,40201031,40201036,40201044,40201049,50401064,50401065],
					csdefine.ACTIVITY_FAMILY_RICHANG_QUEST	: [60101],
					csdefine.ACTIVITY_TONG_JISHI_QUEST		: [60204],
					csdefine.ACTIVITY_TONG_JIANSHE_QUEST	: [60203],
					csdefine.ACTIVITY_TONG_RICHANG_QUEST	: [60202],
					csdefine.ACTIVITY_TONG_MERCHANT			: [60201001,60201002,60201003,60201004,60201005],
					csdefine.ACTIVITY_SHEN_GUI_MI_JING		: [40301001],
					csdefine.ACTIVITY_SHI_LUO_BAO_ZHANG		: [40301003],
					csdefine.ACTIVITY_WU_YAO_QIAN_SHAO		: [40301002],
					csdefine.ACTIVITY_QUEST_SHOUJI			:[50101021,50101022,50101023,50101024,50101025,50101026,50101027],
					csdefine.ACTIVITY_QUEST_LAN_LV			:[50201],
					}


#副本类型活动
COPYSPACE_ACTIVITYS = {
	csdefine.SPACE_TYPE_CITY_WAR				:	csdefine.ACTIVITY_TONG_DUO_CHENG,
	csdefine.SPACE_TYPE_TONG_ABA				:	csdefine.ACTIVITY_BANG_HUI_LEI_TAI,
	csdefine.SPACE_TYPE_TIAN_GUAN				:	csdefine.ACTIVITY_CHUANG_TIAN_GUAN,
	csdefine.SPACE_TYPE_RACE_HORSE				:	csdefine.ACTIVITY_SAI_MA,
	csdefine.SPACE_TYPE_POTENTIAL				:	csdefine.ACTIVITY_POTENTIAL,
	csdefine.SPACE_TYPE_WU_DAO					:	csdefine.ACTIVITY_WU_DAO_DA_HUI,
	csdefine.SPACE_TYPE_SHEN_GUI_MI_JING		:	csdefine.ACTIVITY_SHEN_GUI_MI_JING,
	csdefine.SPACE_TYPE_WU_YAO_QIAN_SHAO		:	csdefine.ACTIVITY_WU_YAO_QIAN_SHAO,
	csdefine.SPACE_TYPE_WU_YAO_WANG_BAO_ZANG	:	csdefine.ACTIVITY_SHI_LUO_BAO_ZHANG,
	csdefine.SPACE_TYPE_SHUIJING				:	csdefine.ACTIVITY_SHUI_JING,
	csdefine.SPACE_TYPE_HUNDUN					:	csdefine.ACTIVITY_HUN_DUN_RU_QIN,
	csdefine.SPACE_TYPE_TEAM_COMPETITION		:	csdefine.ACTIVITY_TEAM_COMPETITION,
	csdefine.SPACE_TYPE_DRAGON					:	csdefine.ACTIVITY_DRAGON,
	csdefine.SPACE_TYPE_PROTECT_TONG			:	csdefine.ACTIVITY_TONG_PROTECT,
	csdefine.SPACE_TYPE_POTENTIAL_MELEE			:	csdefine.ACTIVITY_QIAN_NENG_LUAN_DOU,
	csdefine.SPACE_TYPE_EXP_MELEE				:	csdefine.ACTIVITY_JING_YAN_LUAN_DOU,
	csdefine.SPACE_TYPE_PIG						:	csdefine.ACTIVITY_DU_DU_ZHU,
	csdefine.SPACE_TYPE_YAYU					:	csdefine.ACTIVITY_ZHENG_JIU_YA_YU,
	csdefine.SPACE_TYPE_XIE_LONG_DONG_XUE		:	csdefine.ACTIVITY_XIE_LONG,
	csdefine.SPACE_TYPE_FJSG					:	csdefine.ACTIVITY_FENG_JIAN_SHEN_GONG,
	csdefine.SPACE_TYPE_TONG_COMPETITION		:	csdefine.ACTIVITY_BANG_HUI_JING_JI,
	csdefine.SPACE_TYPE_ROLE_COMPETITION		:	csdefine.ACTIVITY_GE_REN_JING_JI,
	csdefine.SPACE_TYPE_SHE_HUN_MI_ZHEN			:	csdefine.ACTIVITY_SHE_HUN_MI_ZHEN,
	csdefine.SPACE_TYPE_TEACH_KILL_MONSTER		:	csdefine.ACTIVITY_SHI_TU,
	csdefine.SPACE_TYPE_KUAFU_REMAINS			:	csdefine.ACTIVITY_KUA_FU,
	csdefine.SPACE_TYPE_RABBIT_RUN				:	csdefine.ACTIVITY_RUN_RABBIT,
	csdefine.SPACE_TYPE_BEFORE_NIRVANA			:	csdefine.ACTIVITY_BEFORE_NIRVANA,
	csdefine.SPACE_TYPE_CHALLENGE				:	csdefine.ACTIVITY_CHALLENGE_FUBEN,
	csdefine.SPACE_TYPE_TEAM_CHALLENGE			:	csdefine.ACTIVITY_TEAM_CHALLENGE,
	csdefine.SPACE_TYPE_PLOT_LV40				:	csdefine.ACTIVITY_PLOT_LV40,
	csdefine.SPACE_TYPE_PLOT_LV60				:	csdefine.ACTIVITY_PLOT_LV60,
	csdefine.SPACE_TYPE_TOWER_DEFENSE			:	csdefine.ACTIVITY_TOWER_DEFENSE,
	csdefine.SPACE_TYPE_YXLM					:	csdefine.ACTIVITY_YING_XIONG_LIAN_MENG,
	csdefine.SPACE_TYPE_YE_ZHAN_FENG_QI			:	csdefine.ACTIVITY_YE_ZHAN_FENG_QI,
	csdefine.SPACE_TYPE_TONG_TURN_WAR			:	csdefine.ACTIVITY_TONG_TURN_WAR,
	csdefine.SPACE_TYPE_YXLM_PVP				:	csdefine.ACTIVITY_YING_XIONG_LIAN_MENG_PVP,
	csdefine.SPACE_TYPE_FENG_HUO_LIAN_TIAN		:	csdefine.ACTIVITY_TONG_FENG_HUO_LIAN_TIAN,
	csdefine.SPACE_TYPE_TIAO_WU					:	csdefine.ACTIVITY_TIAO_WU,
	}



MONSTER_DIED_ABOUT_ACTIVITYS =	{	#csdefine.ACTIVITY_XING_XIU					:	[ 20613008,20613009,20613010,20613011,20613012,20613013,20613014,20613015,20613016,20613017,20613018,20613019,20613020,20613021,20613022,20613023,20613024,20613025,20613026,20613027,20613028,20613029,20623005,20623006,20623007,20623008,20623009,20623010,20623011,20623012,20623013,20623014,20623015,20623016,20623017,20623018,20623019,20623020,20623021,20623022,20623023,20623024,20623025,20623026,20633006,20633007,20633008,20633009,20633010,20633011,20633012,20633013,20633014,20633015,20633016,20633017,20633018,20633019,20633020,20633021,20633022,20633023,20633024,20633025,20633026,20643006,20643007,20643008,20643009,20643010,20643011,20643012,20643013,20643014,20643015,20643016,20643017,20643018,20643019,20643020,20643021,20643022,20643023,20643024,20643025,20643026,20643027,20653007,20653008,20653009,20653010,20653011,20653012,20653013,20653014,20653015,20653016,20653017,20653018,20653019,20653020,20653021,20653022,20653023,20653024,20653025,20653026,20653027,20613030,20613031,20613032,20613033,20613034,20613035,20613036,20613037,20613038,20613039,20613040,20613041,20613042,20613043,20613044,20613045,20613046,20613047,20613048,20613049,20613050,20613051,20623027,20623028,20623029,20623030,20623031,20623032,20623033,20623034,20623035,20623036,20623037,20623038,20623039,20623040,20623041,20623042,20623043,20623044,20623045,20623046,20623047,20623048,20633027,20633028,20633029,20633030,20633031,20633032,20633033,20633034,20633035,20633036,20633037,20633038,20633039,20633040,20633041,20633042,20633043,20633044,20633045,20633046,20633047,20643028,20643029,20643030,20643031,20643032,2064303320643034,20643035,20643036,20643037,20643038,20643039,20643040,20643041,20643042,20643043,20643044,20643045,20643046,20643047,20643048,20643049,20653028,20653029,20653030,20653031,20653032,20653033,20653034,20653035,20653036,20653037,20653038,20653039,20653040,20653041,20653042,20653043,20653044,20653045,20653046,20653047,20653048 ],	#星宿挑战
									csdefine.ACTIVITY_CHUANG_TIAN_GUAN			:	[ 20611156,20621156,20631156,20641156,20651156 ],	#闯天关
									csdefine.ACTIVITY_BIN_LIN_CHENG_XIA			:	[ 20614002,20624003,20634002,20644001,20654002,20614004,20624005,20624008 ],	#兵临城下
									csdefine.ACTIVITY_DU_DU_ZHU					:	[ 20354002 ],
									csdefine.ACTIVITY_FENG_JIAN_SHEN_GONG		:	[ 20742031 ],	#封剑神宫
									csdefine.ACTIVITY_HUN_DUN_RU_QIN			:	[ 20124001,20134001,20144001 ],		#混沌入侵
									csdefine.ACTIVITY_NIU_MO_WANG				:	[ 20714003 ],						#牛魔王
									csdefine.ACTIVITY_QIAN_NIAN_DU_WA			:	[ 20334003 ],						#千年毒蛙
									csdefine.ACTIVITY_JING_YAN_LUAN_DOU			:	[ 20654003 ],						#经验乱斗
									csdefine.ACTIVITY_QIAN_NENG_LUAN_DOU		:	[ 20754009 ],						#潜能乱斗
									csdefine.ACTIVITY_SHE_HUN_MI_ZHEN			:	[ 20714004 ],						#摄魂迷阵
									csdefine.ACTIVITY_SHUI_JING					:	[ 20724002 ],						#水晶副本
									csdefine.ACTIVITY_TIAN_JIANG_QI_SHOU		:	[ 20314006 ],						#天降奇兽
									csdefine.ACTIVITY_ZHENG_JIU_YA_YU			:	[ 20754011 ],						#拯救猰貐
									csdefine.ACTIVITY_DUO_LUO_LIE_REN			:	[ 20134003 ],						#堕落猎人55
									csdefine.ACTIVITY_BAI_SHE_YAO				:	[ 20724004 ],						#白蛇妖56
									csdefine.ACTIVITY_JU_LING_MO				:	[ 20714002 ],						#巨灵魔57
									csdefine.ACTIVITY_XIAO_TIAN_DA_JIANG		:	[ 20724005 ],						#啸天大将58
									csdefine.ACTIVITY_FENG_KUANG_JI_SHI			:	[ 20144003 ],						#疯狂祭师59
									csdefine.ACTIVITY_HAN_DI_DA_JIANG			:	[ 20754012 ],						#憾地大将60
									csdefine.ACTIVITY_SHENG_LIN_ZHI_WANG		:	[],									#森林之主
									csdefine.ACTIVITY_NU_MU_LUO_SHA				:	[],									#怒目罗刹
									csdefine.ACTIVITY_YE_WAI_BOSS				:	[ 20324001,20354001,20314001,20324002,20344001,20344002,20314002,20324003,20334001,20314003,20344003,20654001,20254001,20624001,20444001,20344004,20714001,20614001,20314004,20334002,20624002,20744001,20754001,20754002,20344005,20634001,20744002,20744003,20324004,20614003,20434001,20454001,20324005,20724001,20624004,20214001,20624007,20644003,20334004,20624006,20644004,20654004 ],
									csdefine.ACTIVITY_TONG_PROTECT				:	[20114002,20124002,20134002,20144002],
									}






class DirectWriteActivityLogMgr:
	"""
	"""
	def __init__( self ):
		"""
		"""
		pass

	def addRecord( self, activityType, action, param1 = "", param2 = "", param3 = "", param4 = "", param5 = "", param6 = "" ):
		"""
		"""
		try:
			LOG_Activity( str(activityType), str(action), param1, param2, param3, param4, param5, param6 )
		except:
			LOG_EXCEPTION("log_error", "error", ERROR_MESSAGE() )


def addQuestActivityLog( recordMgr, activityType,action, dbid, questID , param1, param2, param3, param4 ):
	"""
	增加任务类型活动日志
	"""
	if questID in g_activityLog.questIDToActivity:
		recordMgr.addRecord( str(g_activityLog.questIDToActivity[questID]), str(action), str(dbid), param1, param2, param3, param4 )
	elif int(action) == csdefine.ACTIVITY_ACTION_REWARD_MONEY:
		recordMgr.addRecord( str(csdefine.ACTIVITY_QUEST_JU_QING), str(action), str(dbid), param1, param2, param3, param4 )



def addCopySpaceLog( recordMgr, activityType, action, dbid, spaceType, param1, param2, param3, param4 ):
	"""
	增加副本类型活动日志
	"""
	if spaceType in COPYSPACE_ACTIVITYS:
		recordMgr.addRecord( str(COPYSPACE_ACTIVITYS[spaceType]), str(action), str(dbid), param1, param2, param3, param4 )


def addOtherLog( recordMgr, activityType, action, param1 = "", param2 = "", param3 = "", param4 = "", param5 = "", param6 = "" ):
	"""
	增加其他类型活动日志
	"""
	recordMgr.addRecord( activityType, action, str(param1), str(param2), str(param3), str(param4), str(param5), str(param6) )


def addMonsterDieLog( recordMgr, activityType, action, monsterID, dbid, id, param1, param2, param3 ):
	"""
	增加怪物死亡
	"""
	monsterID = int( monsterID )
	if monsterID in g_activityLog.monsterIDToActivity:
		player = BigWorld.entities.get( id, None )
		if  player is not None:
			recordMgr.addRecord( str(g_activityLog.monsterIDToActivity[monsterID]), str(action), str(player.databaseID) )
			for memberInfo in player.teamMembers:
				member = BigWorld.entities.get( memberInfo["mailbox"].id, None )
				if member is None:
					continue
				if member.id == player.id:
					continue
				if member is not None:
					if player.spaceID == member.spaceID and player.position.flatDistTo( member.position ) <= 100.0:
						recordMgr.addRecord( str(g_activityLog.monsterIDToActivity[monsterID]), str(action), str(member.databaseID) )


def addChangeMonsterLog( recordMgr, activityType, action, monsterID, dbid, id, param1, param2, param3 ):
	"""
	#NPC转怪物
	"""
	monsterID = int( monsterID )
	if monsterID in g_activityLog.monsterIDToActivity:
		player = BigWorld.entities.get( id, None )
		recordMgr.addRecord( str(g_activityLog.monsterIDToActivity[monsterID]), str(csdefine.ACTIVITY_ACTION_COPY_START), dbid )
		if  player is not None:
			recordMgr.addRecord( str(g_activityLog.monsterIDToActivity[monsterID]), str(action), dbid )
			for memberInfo in player.teamMembers:
				member = BigWorld.entities.get(  memberInfo["mailbox"].id, None )
				if member is None or member.id == player.id:
					continue
				if player.spaceID == member.spaceID and player.position.flatDistTo( member.position ) <= 100.0:
					recordMgr.addRecord( str(g_activityLog.monsterIDToActivity[monsterID]), str(action), str(member.databaseID) )

class ActivityLog:
	"""
	活动日志
	"""
	__inst = None
	def __init__( self ):
		"""
		"""
		pass

	def __init__( self ) :
		assert ActivityLog.__inst is None
		self.processMgr = DirectWriteActivityLogMgr()
		self.questIDToActivity = {}
		self.monsterIDToActivity = {}
		self.change()

	@classmethod
	def instance( SELF ) :
		if SELF.__inst is None :
			SELF.__inst = ActivityLog()
		return SELF.__inst


	def addLog( self, parentActivityType, activityType, action, param1 = "", param2 = "", param3 = "", param4 = "", param5 = "", param6 = ""  ):
		"""
		@param: activityType
				type: 	int
				des:	用于指定活动的类型,在csdefine中定义
		@param: action
				type:	int
				des:	用于指定某个活动的一项行为,例如（ 接取任务, 放弃任务 ）
		@param：intParam1
				type:	不确定（可以是字符串,也可以是整数）
				des:	这个参数在Activity中使用。
						当activityType是csdefine.ACTIVITY_PARENT_TYPE_QUEST(任务类型活动),这个参数是整数,表示任务ID
						当activityType是csdefine.ACTIVITY_PARENT_TYPE_SPACECOPY（副本类型活动）,这个参数是字符串,表示spaceType
		@param：intParam2
				type:	int
				des:	一般是指角色的DBID,可以为空
		"""
		ACTIVITY_PARENT_TYPE_HANDLES[parentActivityType]( self.processMgr, activityType, action, param1, param2, param3, param4, param5, param6 )

	def change( self ):
		"""
		"""
		for i in QUEST_ACTIVITYS:
			for j in QUEST_ACTIVITYS[i]:
				self.questIDToActivity[j] = i

		for i in MONSTER_DIED_ABOUT_ACTIVITYS:
			for j in MONSTER_DIED_ABOUT_ACTIVITYS[i]:
				self.monsterIDToActivity[j] = i

g_activityLog = ActivityLog()




#活动主类型
ACTIVITY_PARENT_TYPE_HANDLES = {
							csdefine.ACTIVITY_PARENT_TYPE_QUEST			: addQuestActivityLog,
							csdefine.ACTIVITY_PARENT_TYPE_SPACECOPY		: addCopySpaceLog,
							csdefine.ACTIVITY_PARENT_TYPE_OTHER			: addOtherLog,
							csdefine.ACTIVITY_PARENT_TYPE_MONSTER_DIED	: addMonsterDieLog,
							csdefine.ACTIVITY_PARENT_TYPE_CHANGE_MONSTER: addChangeMonsterLog,
							}



#测试代码
def test1( player ):
	"""
	怪物死亡
	"""
	pType = csdefine.ACTIVITY_PARENT_TYPE_MONSTER_DIED
	aType = 0
	action = csdefine.ACTIVITY_ACTION_MONSTER_DIED
	g_activityLog.addLog( pType, aType, action, "20714003", player.databaseID, player.id )


def test2( player ):
	"""
	进入副本
	"""
	pType = csdefine.ACTIVITY_PARENT_TYPE_SPACECOPY
	aType = 0
	action = csdefine.ACTIVITY_PARENT_TYPE_SPACECOPY
	g_activityLog.addLog( pType, aType, action, player.databaseID, "shuijing" )


def test3( player ):
	"""
	接取任务
	"""
	pType = csdefine.ACTIVITY_PARENT_TYPE_QUEST
	aType = 0
	action = csdefine.ACTIVITY_QUEST_ACTION_ACCEPT
	g_activityLog.addLog( pType, aType, action, 30803002, player.databaseID  ) 


def test4( player ):
	"""
	完成任务
	"""
	pType = csdefine.ACTIVITY_PARENT_TYPE_QUEST
	aType = 0
	action = csdefine.ACTIVITY_QUEST_ACTION_COMPLETE
	g_activityLog.addLog( pType, aType, action, 30803002, player.databaseID  ) 


def test5( player ):
	"""
	放弃任务
	"""
	pType = csdefine.ACTIVITY_PARENT_TYPE_QUEST
	aType = 0
	action = csdefine.ACTIVITY_QUEST_ACTION_ABANDON
	g_activityLog.addLog( pType, aType, action, 30803002, player.databaseID  ) 


def test6( player ):
	"""
	放弃任务
	"""
	pType = csdefine.ACTIVITY_PARENT_TYPE_CHANGE_MONSTER
	aType = 0
	action = csdefine.ACTIVITY_ACTION_ROLE_TRIGGER
	g_activityLog.addLog( pType, aType, action, "20334003", player.databaseID, player.id )

def test( player ):
	test1( player )
	test2( player )
	test3( player )
	test4( player )
	test5( player )
	test6( player )