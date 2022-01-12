# -*- coding: gb18030 -*-
#
# $Id $

"""
帮会副本任务模块： by mushuang
参见 CSOL-9753
提示：
	帮会副本任务按照任务等级划分不同等级段玩家可接受的任务，比如：
	等级			可能出现任务					任务等级
	45-54	"击杀30颗白色水晶（水晶副本）；
			击杀30只巫妖仆从（神鬼秘境）；
			击杀30只魔纹虎（巫妖前哨）；"			50
	55-64	"击杀30颗白色水晶（水晶副本）；
			击杀30只巫妖仆从（神鬼秘境）；
			击杀30只魔纹虎（巫妖前哨）；
			击杀巫妖王之影（失落宝藏）；"			60
	65-74	"击杀30颗白色水晶（水晶副本）；
			击杀30只巫妖仆从（神鬼秘境）；
			击杀30只魔纹虎（巫妖前哨）；
			击杀巫妖王之影（失落宝藏）；
			击杀天关中5的小BOSS（天关）；
			击杀5只硬甲蓝魔（拯救猰貐）；"			70
	75-84	"击杀30颗白色水晶（水晶副本）；
			击杀30只巫妖仆从（神鬼秘境）；
			击杀30只魔纹虎（巫妖前哨）；
			击杀巫妖王之影（失落宝藏）；
			击杀天关中5的小BOSS（天关）；
			击杀5只硬甲蓝魔（拯救猰貐）；
			消灭10只邪恶龙灵（邪龙洞穴）；"			80
			
设计：
	帮会副本任务类似于随机任务组，对应地，有“帮会副本任务组”和“帮会副本子任务”。
帮会副本子任务是指那些不同等级段的玩家可以接受的任务（同服务器，同一天，同一等级段
的玩家接受到的帮会副本子任务相同）。每天零点（即使服务器连续运行数月，误差也可以控
制在1秒内）刷新今天的帮会副本子任务。

"帮会副本任务组"本身也是一个任务，但是在接任务的时候，它会将请求转发到“帮会副本子
任务”。换言之，玩家永远不可能接到"帮会副本任务组"任务。但是用"帮会副本任务组"的接
任务必须条件，可以让不符合接受帮会副本任务条件的玩家看不到帮会副本任务。

参见设计模式：组合
"""

from Quest import *
import QuestTongNormal
from QuestDataType import QuestDataType
from QuestRandomRecordType import QuestRandomRecordType
from ActivityRecordMgr import g_activityRecordMgr
from string import Template
from QTScript import QTSGiveItems
from bwdebug import *
import csdefine
import csstatus
import QTReward
import QTTask
import random
import time
from config.server.PlayerLevelToQuestLevelMap import Datas as mapPlayerLevelToQuestLevel # 将玩家等级映射为任务等级

# 策划规定帮会副本任务的有效期是24小时
QUEST_LIFE_TIME = 24 * 3600
PLAYER_REQUIRED_LEVEL = 45

class QuestTongSpaceCopyGroup( Quest ):
	def __init__( self ):
		Quest.__init__( self )
		self._style = csdefine.QUEST_STYLE_TONG_SPACE_COPY	# 任务样式
		# 把任务等级映射为玩家不同等级段的可选任务
		self._mapQuestLevelToQuests = {} #{ 任务等级1:[ 21,可选任务2, ... ], 任务等级2:[ 可选任务1, 可选任务2, ... ], ... }
		# 今天生成的不同任务等级的任务，有效期为一天，有效期过后会从不同等级段的可选任务中随机选取新的任务更新这个列表
		self._todayQuest = {} #{ 任务等级1:任务实例, 任务等级2:任务实例 ... }
		# 是否已经初始化的标志
		self._initialized = False
		# 刷新时间( 秒时间 )
		self._refreshTime = 0
		# 任务有效期
		self._lifeTime = QUEST_LIFE_TIME
		
		# 强制刷新任务标志
		self._forceRefresh = False
		
		self.__initTodayQuest()
		
	def __initTodayQuest( self ):
		"""
		初次刷新具体的任务实例，并将生成时间设定为指定的时间
		"""
		# 任务的初始刷新时间，目前策划规定为每天00:00:00刷新,如果需要更改时间请更改这三个变量
		hour = 0
		minute = 0
		second = 0
		
		
		# 设定初始刷新时间（ 注意：以后每次刷新时间为此次刷新时间 + 有效期 ）
		year,month,day = time.localtime()[:3]
		timeString = "%s %s %s %s %s %s" %( year, month, day, hour, minute, second )
		refreshTime = time.mktime( time.strptime( timeString , "%Y %m %d %H %M %S" ) )
		
		self.__doRefresh( refreshTime )
		
	
	def __getDateString( self ):
		"""
		得到当前日期字符串，形如20101111
		"""
		return time.strftime("(%Y, %m, %d)", time.localtime() )
		#year,month,day = time.localtime()[:3]
		#return "%s%s%s"%( year, month, day )
	
	def __canPlayerAcceptQuest( self, player ):
		"""
		检验玩家是否可以接受帮会副本任务
		"""
		# 获取玩家身上保存的上次参加帮会副本任务的字符串形式的日期
		# 日期形如：20101111
		
		#start 检测标志是否要更新（由于此标志在玩家登陆的时候才更新,所以在这里要手动检测一下）
		flagValue = player.queryRoleRecord("tongfuben_record")
		if flagValue == "":
			return True
			
		timeString = flagValue.split("_")[0]
		lastDateHash = hash( timeString )
		currDateHash = hash( self.__getDateString() )
		
		if currDateHash != lastDateHash:
			# 返回 false
			self.forceRefresh(player)
			return True
		#end 检测标志是否要更新
		
		if player.isActivityCanNotJoin( csdefine.ACTIVITY_TONG_FUBEN ) :
			return False
		
		return True
		
	def __getFitQuest( self, player ):
		"""
		根据玩家实际情况得到合适玩家的任务
		"""
		questLevel = mapPlayerLevelToQuestLevel.get( player.level, None )
		if questLevel == None:
			ERROR_MSG( "Config file is inconsistent with code!" )
			return None
		
		quest = self._todayQuest.get( questLevel, None )
		if quest == None:
			ERROR_MSG( "Can't find quest of specified questLevel! Quest config maybe wrong!" )
			return None
		
		return quest
		
	def __isRefreshNeeded( self ):
		"""
		检查当前时间，以确定是否需要刷新任务
		"""
		currentTimeInSec = time.time()
		refreshTimeInSec = self._refreshTime # 上次刷新时间
				
		# if 今天的任务已经过期 或者 强制刷新
		if currentTimeInSec - refreshTimeInSec >= self._lifeTime or self._forceRefresh :
			self._forceRefresh = False
			# 返回 True
			return True
		
		# 返回 False
		return False
		
	def __doRefresh( self, refreshTime ):
		"""
		刷新所有不同等级段的任务
		@refreshTime: 执行刷新的时间( 秒时间 )
		"""
		self._todayQuest = {}
		self._refreshTime = refreshTime
		
		for questLevel in self._mapQuestLevelToQuests:
			quest = random.choice( self._mapQuestLevelToQuests[ questLevel ] )
			self._todayQuest[ questLevel ] = quest
			

	def addChild( self, quest ):
		"""
		将一个任务实例加入到合适的等级段任务集合
		"""
		if not self._mapQuestLevelToQuests.has_key( quest._level ):
			self._mapQuestLevelToQuests[ quest._level ] = []

		self._mapQuestLevelToQuests[ quest._level ].append( quest )
		
	def accept( self, player ):
		"""
		virtual method.
		接任务，如果接任务失败了则返回False（例如玩家背包满了放不下任务道具）。

		@param     player: instance of Role Entity
		@type      player: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		# if 玩家不具备接受任务的条件：
		if not self.__canPlayerAcceptQuest( player ):
			# 提示玩家
			player.statusMessage( csstatus.TONG_SPACE_COPY_ONLY_ONE_CHANCE )
			# 返回
			return
			
		# if 没有初始化：
		if not self._initialized:
			# 初始化
			self.__initTodayQuest()
			# 标记为已经初始化
			self._initialized = True
		
		# if 需要刷新任务
		if self.__isRefreshNeeded():
			# 刷新任务
			self.__doRefresh( time.time() )
		
		
		quest = self.__getFitQuest( player )
		if quest == None:
			ERROR_MSG( "Can't find fit quest for player!" )
			return False
			
		return quest.accept( player )
	
	def baseAccept( self, player ):
		"""
		virtual method.
		接任务，如果接任务失败了则返回False（例如玩家背包满了放不下任务道具）。

		@param     player: instance of Role Entity
		@type      player: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		# 此接口在这个实现中不需要，留空
		pass
	
	def __hasLoggedQuest( self, player ):
		"""
		判断玩家是否仍然持有帮会副本任务
		"""
		questIDs = player.findQuestByType( csdefine.QUEST_STYLE_TONG_FUBEN )
		if 0 == len(questIDs):
			return False
		
		return True
		
	def __removeCurQuest( self, player ):
		"""
		移除帮会副本任务
		"""
		questIDs = player.findQuestByType( csdefine.QUEST_STYLE_TONG_FUBEN )
		if 0 == len(questIDs):
			return False
			
		for qid in questIDs:
			player.abandonQuest( player.id, qid )
	
	def query( self, player ):
		"""
		查询玩家对某一个任务的进行状态。

		@return: 返回值类型请查看common里的QUEST_STATE_*
		@rtype:  UINT8
		
		if self.__canPlayerAcceptQuest( player ) and self.checkRequirement( player ):
			# 如果有旧任务没有交，那么自动放弃旧任务。
			#if self.__hasLoggedQuest( player ) or self._forceRefresh:
				#self.__removeCurQuest( player )

			return csdefine.QUEST_STATE_NOT_HAVE # 可以接但还未接该任务
		"""	
		isCanAceept = csdefine.QUEST_STATE_NOT_ALLOW
		while(True):
			if not self.__canPlayerAcceptQuest( player ):
				break
			
			if not self.checkRequirement( player ):
				break
			
			if len(player.findQuestByType( csdefine.QUEST_STYLE_TONG_FUBEN )) != 0:
				break
			
			isCanAceept = csdefine.QUEST_STATE_NOT_HAVE
			break
			
		return isCanAceept

	def forceRefresh( self , player ):
		"""
		强制刷新任务
		"""
		player.setRoleRecord("tongfuben_record", "00000000_0")
		g_activityRecordMgr.initAllActivitysJoinState(player)
		self._forceRefresh = True