# -*- coding: gb18030 -*-
#
# $Id: QTRequirement.py,v 1.22 2008/08/12 08:04:10 zhangyuxing Exp $

"""
"""

import csdefine
import cschannel_msgs
import ShareTexts as ST
import csconst
from bwdebug import *
import time
import Language
import BigWorld
from CrondScheme import *

# 映射任务脚本与实例化类型
# 此映射主要用于从配置中初始化实例时使用
# key = 目标类型字符串，取自各类型的类名称;
# value = 继承于QTRequirement的类，用于根据类型实例化具体的对像；
quest_requirement_type_maps = {}

def MAP_QUEST_REQUIRE_TYPE( classObj ):
	"""
	映射任务目标类型与实例化类型
	"""
	quest_requirement_type_maps[classObj.__name__] = classObj

def createRequirement( strType ):
	"""
	创建需求实例

	@return: instance of QTRequirement or derive from it
	@type:   QTRequirement
	"""
	try:
		return quest_requirement_type_maps[strType]()
	except KeyError:
		ERROR_MSG( "can't create instance by %s type." % strType )
		return None

				
#星期对照
DAY_MAP = {0:"Monday",1:"Tuesday", 2:"Wednesday", 3:"Thursday", 4:"Friday", 5:"Saturday", 6:"Sunday"}


# ------------------------------------------------------------>
# abstract class
# ------------------------------------------------------------>
class QTRequirement:
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: 初始化参数,参数格式由每个实例自己规定
		@type  section: pyDataSection
		@return: None
		"""
		pass

	def query( self, playerEntity ):
		"""
		判断player是否符合要求

		@param playerEntity: 玩家entity实例
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		pass

	def getDetail( self ):
		"""
		返回要求相关的描述

		@return: String
		@rtype:  String
		"""
		pass


# ------------------------------------------------------------>
# QTRQuestComplete；已完成某任务
# ------------------------------------------------------------>
class QTRQuestComplete( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: questID
		@type  section: pyDataSection
		@return: None
		"""
		self._questID = section.readInt( "param1" )

	def query( self, playerEntity ):
		"""
		判断player是否符合要求

		@param playerEntity: 玩家entity实例
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return playerEntity.questIsCompleted( self._questID )

	def getDetail( self ):
		"""
		返回要求相关的描述

		@return: String
		@rtype:  String
		"""
		return ""


# ------------------------------------------------------------>
# QTROneOfQuestsComplete；已完成某些任务之一
# ------------------------------------------------------------>
class QTROneOfQuestsComplete( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		"""
		questIDs = section.readString( "param1" )
		self.questsList = questIDs.split( "," )

	def query( self, playerEntity ):
		"""
		判断player是否符合要求

		@param playerEntity: 玩家entity实例
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		for i in self.questsList:
			if playerEntity.questIsCompleted( int(i) ):
				return True
			
		return False

	def getDetail( self ):
		"""
		返回要求相关的描述

		@return: String
		@rtype:  String
		"""
		return ""


# ------------------------------------------------------------>
# QTRQuestHas；已经接了某个任务
# ------------------------------------------------------------>
class QTRQuestHas( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: questID
		@type  section: pyDataSection
		@return: None
		"""
		self._questID = section.readInt( "param1" )

	def query( self, playerEntity ):
		"""
		判断player是否符合要求

		@param playerEntity: 玩家entity实例
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return playerEntity.has_quest( self._questID )

	def getDetail( self ):
		"""
		返回要求相关的描述

		@return: String
		@rtype:  String
		"""
		return ""


# ------------------------------------------------------------>
# QTRQuestNotHas；没有接某些任务中的任何一个
# ------------------------------------------------------------>
class QTRQuestNotHas( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: questID
		@type  section: pyDataSection
		@return: None
		"""
		self._questIDs = section.readString( "param1" ).split( ";" )

	def query( self, playerEntity ):
		"""
		判断player是否符合要求

		@param playerEntity: 玩家entity实例
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		for i in self._questIDs:
			if playerEntity.questIsCompleted( int(i) ) or playerEntity.has_quest( int(i) ):
				return False
		return True

	def getDetail( self ):
		"""
		返回要求相关的描述

		@return: String
		@rtype:  String
		"""
		return ""


# ------------------------------------------------------------>
# QTRLevel
# ------------------------------------------------------------>
class QTRLevel( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: minLevel, maxLevel; maxLevel is optional.
		@type  section: pyDataSection
		@return: None
		"""
		self._minLvl = section.readInt( "param1" )
		self._maxLvl = section.readInt( "param2" )

	def query( self, playerEntity ):
		"""
		判断player是否符合要求

		@param playerEntity: 玩家entity实例
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if self._maxLvl > 0:
			return (playerEntity.level >= self._minLvl) and (playerEntity.level <= self._maxLvl)
		return playerEntity.level >= self._minLvl

	def getDetail( self ):
		"""
		返回要求相关的描述

		@return: String
		@rtype:  String
		"""
		return cschannel_msgs.QUEST_INFO_1 % ( self._minLvl, self._maxLvl )


# ------------------------------------------------------------>
# QTRClass
# ------------------------------------------------------------>
class QTRClass( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: classValue；值为RACES_MAP里的之一或其组合
		@type  section: pyDataSection
		@return: None
		"""
		self._classes = section.readInt( "param1" ) << 4

	def query( self, playerEntity ):
		"""
		判断player是否符合要求

		@param playerEntity: 玩家entity实例
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return playerEntity.getClass() == self._classes

	def getDetail( self ):
		"""
		返回要求相关的描述

		@return: String
		@rtype:  String
		"""
		return cschannel_msgs.QUEST_INFO_2 % csconst.g_chs_class[self._classes]


# ------------------------------------------------------------>
# QTRSpecialFlag
# ------------------------------------------------------------>
class QTRSpecialFlag( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: flag, value
		@type  section: pyDataSection
		@return: None
		"""
		self._flag = section.readString( "param1" )
		self._value = section.readInt( "param2" )

	def query( self, playerEntity ):
		"""
		判断player是否符合要求

		@param playerEntity: 玩家entity实例
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		try:
			mapping = playerEntity.getMapping()["questSpecialFlag"]
			value = mapping[self._flag]
		except KeyError:
			value = 0
		return value == self._value

	def getDetail( self ):
		"""
		返回要求相关的描述

		@return: String
		@rtype:  String
		"""
		return ""


# ------------------------------------------------------------>
# QTRTitle
# ------------------------------------------------------------>
class QTRTitle( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: titleID
		@type  section: pyDataSection
		@return: None
		"""
		self._title = section.readInt( "param1" )

	def query( self, playerEntity ):
		"""
		判断player是否符合要求

		@param playerEntity: 玩家entity实例
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return playerEntity.hasTitle( self._title )

	def getDetail( self ):
		"""
		返回要求相关的描述

		@return: String
		@rtype:  String
		"""
		return ""


# ------------------------------------------------------------>
# QTRItem
# ------------------------------------------------------------>
class QTRItem( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: itemID, amount, isEquiped
		@type  section: pyDataSection
		@return: None
		"""
		self._itemID = section.readInt( "param1" )
		self._amount = section.readInt( "param2" )
		self._isEquiped = section.readBool( "param3" )

	def query( self, playerEntity ):
		"""
		判断player是否符合要求

		@param playerEntity: 玩家entity实例
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if self._isEquiped:
			item = playerEntity.findItemFromEK_( self._itemID )
		else:
			item = playerEntity.findItemFromNKCK_( self._itemID )
		if item is None: return False
		return item.getAmount() >= self._amount

	def getDetail( self ):
		"""
		返回要求相关的描述

		@return: String
		@rtype:  String
		"""
		return ""


# ------------------------------------------------------------>
# QTRTeam
# ------------------------------------------------------------>
class QTRTeam( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: minMember, maxMember, isCaptain
		@type  section: pyDataSection
		@return: None
		"""
		self._minMember = section.readInt( "param1" )		# 0 表示无限制
		self._maxMember = section.readInt( "param2" )		# 0 表示无限制
		self._isCaptain = section.readInt( "param3" )		# 0 表示无限制

	def query( self, playerEntity ):
		"""
		判断player是否符合要求

		@param playerEntity: 玩家entity实例
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if self._minMember > 0 and playerEntity.getTeamCount() < self._minMember: return False
		if self._maxMember > 0 and playerEntity.getTeamCount() > self._maxMember: return False
		if self._isCaptain > 0 and not playerEntity.isTeamCaptain(): return False
		return True

	def getDetail( self ):
		"""
		返回要求相关的描述

		@return: String
		@rtype:  String
		"""
		return ""


# ------------------------------------------------------------>
# QTRSkill
# ------------------------------------------------------------>
class QTRSkill( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: skillID
		@type  section: pyDataSection
		@return: None
		"""
		self._skillID = section.readInt( "param1" )

	def query( self, playerEntity ):
		"""
		判断player是否符合要求

		@param playerEntity: 玩家entity实例
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return playerEntity.hasSkill( self._skillID )

	def getDetail( self ):
		"""
		返回要求相关的描述

		@return: String
		@rtype:  String
		"""
		return ""


# ------------------------------------------------------------>
# QTRBuff
# ------------------------------------------------------------>
class QTRBuff( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: skillID
		@type  section: pyDataSection
		@return: None
		"""
		self._skillID = section.readInt( "param1" )

	def query( self, playerEntity ):
		"""
		判断player是否符合要求

		@param playerEntity: 玩家entity实例
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return len( playerEntity.findBuffsByBuffID( self._skillID ) ) > 0

	def getDetail( self ):
		"""
		返回要求相关的描述

		@return: String
		@rtype:  String
		"""
		return ""

# ------------------------------------------------------------>
# QTRWithoutBuff
# ------------------------------------------------------------>
class QTRWithoutBuff( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: skillID
		@type  section: pyDataSection
		@return: None
		"""
		self._buffID = section.readInt( "param1" )

	def query( self, playerEntity ):
		"""
		判断player是否符合要求

		@param playerEntity: 玩家entity实例
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return not len( playerEntity.findBuffsByBuffID( self._buffID ) ) > 0

	def getDetail( self ):
		"""
		返回要求相关的描述

		@return: String
		@rtype:  String
		"""
		return ""

# ------------------------------------------------------------>
# QTRPKSwitch
# ------------------------------------------------------------>
class QTRPKSwitch( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: status; 0 == 关闭PK，1 == 打开PK
		@type  section: pyDataSection
		@return: None
		"""
		self._status = section.readBool( "param1" )

	def query( self, playerEntity ):
		"""
		判断player是否符合要求

		@param playerEntity: 玩家entity实例
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return playerEntity.pkSwitch == self._status

	def getDetail( self ):
		"""
		返回要求相关的描述

		@return: String
		@rtype:  String
		"""
		return ""


# ------------------------------------------------------------>
# QTRPKValue
# ------------------------------------------------------------>
class QTRPKValue( QTRequirement ):
	LT = -1		# 小于
	EQ = 0		# 等于
	BT = 1		# 大于
	# 由于用的是链表，因此顺序很重要
	MAP_STATUS = [
				lambda player, value: player.pkValue < value,
				lambda player, value: player.pkValue == value,
				lambda player, value: player.pkValue > value,
			]
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: value, status; status == 0 相等，1 大于，-1 小于
		@type  section: pyDataSection
		@return: None
		"""
		self._value = section.readInt( "param1" )
		self._status = self.EQ
		status = section.readInt( "param2" )
		if status > 0:
			self._status = self.BT
		elif status < 0:
			self._status = self.LT

	def query( self, playerEntity ):
		"""
		判断player是否符合要求

		@param playerEntity: 玩家entity实例
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return self.MAP_STATUS[self._status + 1]( playerEntity, self._value )

	def getDetail( self ):
		"""
		返回要求相关的描述

		@return: String
		@rtype:  String
		"""
		return ""


# ------------------------------------------------------------>
# QTRGroupQuestHas；已经接了某个环任务的子任务
# ------------------------------------------------------------>
class QTRGroupQuestHas( QTRQuestHas ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: questID
		@type  section: pyDataSection
		@return: None
		"""
		self._groupQuestID = section.readInt( "param1" )								#环任务ID
		self._subQuestID = section.readInt( "param2" )									#子任务ID

	def query( self, playerEntity ):
		"""
		判断player是否符合要求

		@param playerEntity: 玩家entity实例
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return playerEntity.has_quest( self._groupQuestID ) and playerEntity.getQuestTasks( self._groupQuestID ).query( "subQuestID" ) == self._subQuestID

	def getDetail( self ):
		"""
		返回要求相关的描述

		@return: String
		@rtype:  String
		"""
		return ""



class QTRFamily( QTRequirement ):
	"""
	"""
	def __init__( self, *args ):
		pass
	
	
	def query( self, player ):
		"""
		"""
		return player.isJoinFamily()



class QTRNormalDartCount( QTRequirement ):
	"""
	"""
	def __init__( self, *args ):
		pass
	
	def init( self, section ):
		"""
		@param section: format: questID
		@type  section: pyDataSection
		@return: None
		"""
		self._count = section.readInt( "param1" )								#普通运镖次数
	
	def query( self, player ):
		"""
		"""
		date = time.localtime()[2]
		if date != player.questNormalDartRecord.date:
			player.questNormalDartRecord.date = date
			player.questNormalDartRecord.dartCount = 0
		return player.questNormalDartRecord.dartCount == self._count

class QTRExpDartCount( QTRequirement ):
	"""
	"""
	def __init__( self, *args ):
		pass
	
	def init( self, section ):
		"""
		@param section: format: questID
		@type  section: pyDataSection
		@return: None
		"""
		self._count = section.readInt( "param1" )								#贵重运镖次数
	
	def query( self, player ):
		"""
		"""
		date = time.localtime()[2]
		if date != player.questExpDartRecord.date:
			player.questExpDartRecord.date = date
			player.questExpDartRecord.dartCount = 0
		return player.questExpDartRecord.dartCount == self._count


class QTRFamilyDartCount( QTRequirement ):
	"""
	"""
	def __init__( self, *args ):
		pass
	
	def init( self, section ):
		"""
		@param section: format: questID
		@type  section: pyDataSection
		@return: None
		"""
		self._count = section.readInt( "param1" )								#家族运镖次数
	
	def query( self, player ):
		"""
		"""
		date = time.localtime()[2]
		if date != player.questFamilyDartRecord.date:
			player.questFamilyDartRecord.date = date
			player.questFamilyDartRecord.dartCount = 0
		return player.questFamilyDartRecord.dartCount == self._count


class QTRTongDartCount( QTRequirement ):
	"""
	"""
	def __init__( self, *args ):
		pass
	
	def init( self, section ):
		"""
		@param section: format: questID
		@type  section: pyDataSection
		@return: None
		"""
		# 帮会每天可以开启帮会运镖次数为帮会中最大可以容纳人数/10
		pass
	
	def query( self, player ):
		"""
		"""
		if player.tong_dbID <= 0:
			return False
		date = time.localtime()[2]
		if date != player.questTongDartRecord.date:
			player.questTongDartRecord.date = date
			player.questTongDartRecord.dartCount = 0
		return player.questTongDartRecord.dartCount < 1		# CSOL-2118 帮会运镖每人每天只能接一次


class QTRDartPrestige( QTRequirement ):
	"""
	"""
	def __init__( self, *args ):
		pass
	
	def init( self, section ):
		"""
		@param section: format: questID
		@type  section: pyDataSection
		@return: None
		"""
		self._param1 = section.readInt( "param1" )								#声望值
		self._param2 = section.readInt( "param2" )								#声望值
	
	def query( self, player ):
		"""
		"""
		return player.getPrestige( self._param1 ) >= self._param2



class QTRQuestNotComplete( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: questID
		@type  section: pyDataSection
		@return: None
		"""
		self._questID = section.readInt( "param1" )

	def query( self, playerEntity ):
		"""
		判断player是否符合要求

		@param playerEntity: 玩家entity实例
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		quest = playerEntity.getQuest( self._questID )
		if quest.getStyle() == csdefine.QUEST_STYLE_FIXED_LOOP:
			lpLog = playerEntity.getLoopQuestLog( self._questID, True )
			if not lpLog.checkStartTime():
				# 接任务日期与当前时间不是同一天，也就表示需要重置任务状态
				lpLog.reset()
			if lpLog.getDegree() >= quest._finish_count:
				# 已完成任务次数过多，不可以再接
				return False
		
		return not playerEntity.questIsCompleted( self._questID )

	def getDetail( self ):
		"""
		返回要求相关的描述

		@return: String
		@rtype:  String
		"""
		return ""
		

# 根据策划的需求，现在跑商等级跟玩家可完成任务的次数没有联系
class QTRMerchantTongReq( QTRequirement ):
	def __init__( self ):
		"""
		一级别跑商需求
		"""
		pass

	def init( self, section ):
		"""
		@param section: format: questID
		@type  section: pyDataSection
		@return: None
		"""
		self.questID = section.readInt( "param1" )					#任务ID
		self.merlevel = section.readInt( "param2" )					#跑商等级


	def query( self, playerEntity ):
		"""
		判断playerEntity是否符合要求

		@param playerEntity: 玩家entity实例
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if not playerEntity.isJoinTong():
			return False
		return True

	def getDetail( self ):
		"""
		返回要求相关的描述

		@return: String
		@rtype:  String
		"""
		return ""


class QTRTongDutyReq( QTRequirement ):
	"""
		帮会职务需求
	"""
	
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: questID
		@type  section: pyDataSection
		@return: None
		"""
		self.tongDuty = section.readInt( "param1" )	# 帮会职务

	def query( self, playerEntity ):
		"""
		判断playerEntity是否符合要求

		@param playerEntity: 玩家entity实例
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return playerEntity.isJoinTong() and playerEntity.tong_grade == self.tongDuty

	def getDetail( self ):
		"""
		返回要求相关的描述

		@return: String
		@rtype:  String
		"""
		return ""


# ------------------------------------------------------------>
# QTRPrestige
# ------------------------------------------------------------>
class QTRPrestige( QTRequirement ):
	def __init__( self ):
		pass


	def init( self, section ):
		"""
		@param section: format: minLevel, maxLevel; maxLevel is optional.
		@type  section: pyDataSection
		@return: None
		"""
		self._factionID = section.readInt( "param1" )	# 势力ID
		self._maxValue = section.readInt( "param2" )	# 声望最大值
		self._minValue = section.readInt( "param3" )	# 声望最小值

	def query( self, playerEntity ):
		"""
		判断player是否符合要求

		@param playerEntity: 玩家entity实例
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return playerEntity.getPrestige( self._factionID ) < self._maxValue


# ------------------------------------------------------------>
# QTRFixTime
# ------------------------------------------------------------>
class QTRActivityFixTime( QTRequirement ):
	def __init__( self ):
		pass


	def init( self, section ):
		"""
		@param section: format: minLevel, maxLevel; maxLevel is optional.
		@type  section: pyDataSection
		@return: None
		"""
		self._type = section.readInt( "param1" ) #_type 包括 3(乡试)，4(会试)，5(殿试)
		self._longM = section.readInt( "param2" ) #分钟
		
	def query( self, playerEntity ):
		"""
		@param playerEntity: 玩家entity实例
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if self._type == csdefine.ACTIVITY_EXAMINATION_XIANGSHI:
			return BigWorld.globalData.has_key( "AS_XiangshiActivityStart" )
		if self._type == csdefine.ACTIVITY_EXAMINATION_HUISHI:
			return BigWorld.globalData.has_key( "AS_HuishiActivityStart" )
		if self._type == csdefine.ACTIVITY_EXAMINATION_DIANSHI:
			return BigWorld.globalData.has_key( "AS_DianshiActivityStart" )
		return False
			

class QTRTong( QTRequirement ):
	"""
	"""
	def __init__( self, *args ):
		pass
	

	def query( self, player ):
		"""
		"""
		return player.isJoinTong()



# ------------------------------------------------------------>
# QTRGruopConuntRqt
# ------------------------------------------------------------>
class QTRGruopConuntRqt( QTRequirement ):
	"""
	需要环任务组数（当玩家做的该环任务组数超过限制就不显示绿色叹号了）
	"""
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: classValue；值为RACES_MAP里的之一或其组合
		@type  section: pyDataSection
		@return: None
		"""
		self._questID = section.readInt( "param1" )
		self._reapeatTime = section.readInt( "param2" )

	def query( self, playerEntity ):
		"""
		判断player是否符合要求

		@param playerEntity: 玩家entity实例
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if not playerEntity.checkStartGroupTime( self._questID ):
			return True
		
		if self._reapeatTime <= playerEntity.getGroupQuestCount( self._questID ) and playerEntity.isGroupQuestRecorded( self._questID ):
			playerEntity.resetGroupQuest( self._questID )
			playerEntity.setGroupQuestRecorded( self._questID, False )
		
		if self._reapeatTime <= playerEntity.getGroupQuestCount( self._questID ):
			if not playerEntity.newDataGroupQuest( self._questID ):
				return False
		return True

	def getDetail( self ):
		"""
		返回要求相关的描述

		@return: String
		@rtype:  String
		"""
		return ""


class QTRInTongTerritory( QTRequirement ):
	"""
	"""
	def __init__( self, *args ):
		pass
	

	def query( self, player ):
		"""
		"""
		id = player.getCurrentSpaceBase().id
		spaceEntity = BigWorld.entities.get( id )
		if spaceEntity.isReal():
			if "tongDBID" in spaceEntity.params and spaceEntity.params[ "tongDBID" ] == player.tong_dbID:
				return True
		
		return False


class QTRInTime( QTRequirement ):
	"""
	是否处于指定时间中
	注：该类任务NPC头顶任务标记通过AI辅助更新
	"""
	def __init__( self, *args ):
		"""
		"""
		pass


	def init( self, section ):
		"""
		@param section: format: minLevel, maxLevel; maxLevel is optional.
		@type  section: pyDataSection
		@return: None
		"""
		self._cmd = section.readString( "param1" )			# scheme 字符串 如：" * * 3 * *" (参见 CrondScheme.py)
		self._presistMinute = section.readInt( "param2" )	# 持续时间
		self.scheme = Scheme()
		self.scheme.init( self._cmd )

	def query( self, player ):
		"""
		"""
		year, month, day, hour, minute = time.localtime( time.time() - self._presistMinute * 60 )[:5]
		nextTime = self.scheme.calculateNext( year, month, day, hour, minute )
		if nextTime < time.time():
			return True
		return False

class QTRCamp( QTRequirement ):
	"""
	是否属于某阵营
	"""
	def __init__( self, *args ):
		"""
		"""
		self._camp = csdefine.ENTITY_CAMP_NONE

	def init( self, section ):
		"""
		@param section: format: minLevel, maxLevel; maxLevel is optional.
		@type  section: pyDataSection
		@return: None
		"""
		self._camp = section.readInt( "param1" )

	def query( self, player ):
		"""
		"""
		return self._camp == player.getCamp()

#-------------------------------------------------------------
# QTRCampActivityCondition
#-------------------------------------------------------------

class QTRCampActivityCondition( QTRequirement ):
	"""
	阵营活动开启的地图和类型是否符合任务要求
	"""
	def __init__( self, *args ):
		"""
		"""
		self._spaceName = ""
		self._activityType = ""

	def init( self, section ):
		"""
		@type  section: pyDataSection
		@return: None
		"""
		self._spaceName = section.readString( "param1" )
		self._activityType = section.readString( "param2" )

	def query( self, player ):
		"""
		"""
		if not BigWorld.globalData.has_key( "CampActivityCondition" ):
			return False
			
		temp = BigWorld.globalData["CampActivityCondition"]
		
		if self._spaceName != "" and self._spaceName not in temp[0]:
			return False
		
		if self._activityType != "":
			types = [ int( i ) for i in self._activityType.split( "," ) ]		# 可以匹配多种活动
			if temp[1] not in types:
				return False
			
		return True


# 注册各分类
MAP_QUEST_REQUIRE_TYPE( QTRClass )			# CLASS_*
MAP_QUEST_REQUIRE_TYPE( QTRQuestComplete )	# questID
MAP_QUEST_REQUIRE_TYPE( QTRQuestHas )		# questID
MAP_QUEST_REQUIRE_TYPE( QTRQuestNotHas )	# questID
MAP_QUEST_REQUIRE_TYPE( QTRLevel )			# minLevel, maxLevel; maxLevel是可选的.
MAP_QUEST_REQUIRE_TYPE( QTRSpecialFlag )	# flag, value
MAP_QUEST_REQUIRE_TYPE( QTRTitle )			# titleID
MAP_QUEST_REQUIRE_TYPE( QTRItem )			# itemID, itemAmount, isEquiped; isEquiped eq 0 表示判断的是普通物品栏,否则表示判断的是装备栏.
MAP_QUEST_REQUIRE_TYPE( QTRTeam )			# minMember, maxMember, isCaptain; all param value eq 0 that point to not check.
MAP_QUEST_REQUIRE_TYPE( QTRSkill )			# skillID
MAP_QUEST_REQUIRE_TYPE( QTRBuff )			# skillID
MAP_QUEST_REQUIRE_TYPE( QTRWithoutBuff )	# skillID
MAP_QUEST_REQUIRE_TYPE( QTRPKSwitch )		# status; 0 == 关闭PK，1 == 打开PK
MAP_QUEST_REQUIRE_TYPE( QTRPKValue )		# value, status; status == 0 相等，1 大于，-1 小于
MAP_QUEST_REQUIRE_TYPE( QTRGroupQuestHas )		# questID
MAP_QUEST_REQUIRE_TYPE(QTRFamily)
MAP_QUEST_REQUIRE_TYPE(QTRNormalDartCount)
MAP_QUEST_REQUIRE_TYPE(QTRExpDartCount)
MAP_QUEST_REQUIRE_TYPE(QTRFamilyDartCount)
MAP_QUEST_REQUIRE_TYPE(QTRTongDartCount)
MAP_QUEST_REQUIRE_TYPE(QTRDartPrestige)
MAP_QUEST_REQUIRE_TYPE(QTRQuestNotComplete)
MAP_QUEST_REQUIRE_TYPE(QTRMerchantTongReq)	# 跑商等级、帮会等级对应跑商任务次数
MAP_QUEST_REQUIRE_TYPE(QTRPrestige)
MAP_QUEST_REQUIRE_TYPE(QTRActivityFixTime)
MAP_QUEST_REQUIRE_TYPE(QTRTong)				# 需要加入帮会
MAP_QUEST_REQUIRE_TYPE(QTRTongDutyReq)		# 需要帮会职务
MAP_QUEST_REQUIRE_TYPE( QTROneOfQuestsComplete )	#完成一组任务中的任意一个就算完成
MAP_QUEST_REQUIRE_TYPE( QTRGruopConuntRqt )		# 需要环任务组数（当玩家做的该环任务组数超过限制就不显示绿色叹号了）
MAP_QUEST_REQUIRE_TYPE( QTRInTongTerritory )	#是否处于自身帮会领地中
MAP_QUEST_REQUIRE_TYPE( QTRInTime )				#是否处于指定时间段中
MAP_QUEST_REQUIRE_TYPE( QTRCamp )				#是否属性某阵营
MAP_QUEST_REQUIRE_TYPE( QTRCampActivityCondition )				# 阵营活动开启的地图和类型是否符合任务要求

#
# $Log: QTRequirement.py,v $
# Revision 1.22  2008/08/12 08:04:10  zhangyuxing
# no message
#
# Revision 1.21  2008/08/12 01:33:57  zhangyuxing
# 增加家族接任务需求
#
# Revision 1.20  2008/08/09 01:50:39  wangshufeng
# 物品id类型调整，STRING -> INT32,相应调整代码。
#
# Revision 1.19  2008/07/31 03:45:27  zhangyuxing
# no message
#
# Revision 1.18  2008/07/30 07:30:07  zhangyuxing
# 修改一处 self._id 的代码错误
#
# Revision 1.17  2008/07/30 05:56:36  zhangyuxing
# 增加环任务任务条件
#
# Revision 1.16  2008/04/03 06:31:33  phw
# KitbagBase::find2All()改名为find()，并更改返回值从原来的( order, toteID, itemInstance )改为itemInstance
# KitbagBase::findAll2All()改名为findAll()，并更改返回值从原来的( order, toteID, itemInstance )改为itemInstance
# 根据以上的变化，调整相关使用到以上接口的代码
#
# Revision 1.15  2007/12/06 07:43:05  phw
# 修改了初始化方式，从原来的字符串参数改为section实例参数
#
# Revision 1.14  2007/11/28 00:38:48  phw
# 修正QTRPKValue中MAP_STATUS的语法错误
#
# Revision 1.13  2007/11/27 09:26:58  phw
# class removed: QTRRace, QTRQuest
# class added: QTRQuestComplete, QTRQuestHas, QTRQuestNotHas, QTRBuff, QTRPKSwitch, QTRPKValue,
#
# Revision 1.12  2007/11/27 01:52:00  phw
# 所有职业变量加上前缀'CLASS_'，所有性别变量加上前缀'GENDER_'，如原来的战士'FIGHTER'变为'CLASS_FIGHTER'，其余类同
#
# Revision 1.11  2007/11/02 03:59:51  phw
# 把原来在__init__.py中的实例创建改为在模块自己身上做
#
# Revision 1.10  2007/06/14 09:59:20  huangyongwei
# 重新整理了宏定义
#
# Revision 1.9  2006/08/05 08:31:02  phw
# 修改接口：
#     QTRItem::query();
#     from: return item[2].amount >= self._amount
#     to:   return item[2].getAmount() >= self._amount
#
# Revision 1.8  2006/08/02 03:15:15  phw
# 修改接口：
#     QTRSkill::init(); 修正了没有转换字符串参数为整数的BUG
# 删除：from Resource.QuestLoader import QuestsFlyweight
#
# Revision 1.7  2006/04/06 06:50:26  phw
# 加入奖励技能和技能需要判断
#
# Revision 1.6  2006/03/28 09:49:23  phw
# 修正国家和职业需求取值不正确的BUG
#
# Revision 1.5  2006/03/25 07:36:34  phw
# fix QTRLevel and QTRQuest
#
# Revision 1.4  2006/03/22 02:27:00  phw
# 修改了对已接任务的默认状态
#
# Revision 1.3  2006/03/10 05:15:14  phw
# 增加了新的需求类
#
# Revision 1.2  2006/03/07 10:00:49  phw
# 完善QTRQuest,支持0 没有接; 1 已接; 2 已完成
#
# Revision 1.1  2006/01/24 02:20:50  phw
# no message
#
#