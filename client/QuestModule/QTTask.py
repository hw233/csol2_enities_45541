# -*- coding: gb18030 -*-
#
# $Id: QTTask.py,v 1.44 2008-09-05 01:44:30 zhangyuxing Exp $

"""
"""

import csdefine
from Time import *
import struct
from bwdebug import *
from gbref import rds
import items
import QuestTaskDataType as QTTask
import csconst
import BigWorld
import NPCDatasMgr
import StringFormat
from guis.tooluis.richtext_plugins.PL_Link import PL_Link
from LabelGather import labelGather
#from config.client.ForbidLinkIDs import forbidMonsters
#rom config.client.ForbidLinkIDs import forbidNPCs
from config.client.ForbidLinkMonsterID import Datas as forbidMonsters
from config.client.ForbidLinkNPCID import Datas as forbidNPCs

# ------------------------------------------------------------>
# QTTaskTime
# ------------------------------------------------------------>

class QTTaskTime( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str1 = ""
		self.str2 = ""
		self.val1 = 0	# 任务获取时间		int( time.time() + self._lostTime )
		self.val2 = 0	# 任务失败时间		int( time.time() )
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_TIME

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		ltime = self.val2 - int(Time.time())
		if ltime < 0:
			ltime = 0
			isCollapsed = True

		HH = ltime/60/60
		MM = ltime/60 - HH * 60
		SS = ltime%60

		s = ""
		if HH > 0:
			s += labelGather.getText( "QTTask:main", "miTimeHMS", HH, MM, SS )
		elif MM > 0:
			s += labelGather.getText( "QTTask:main", "miTimeMS", MM, SS )
		else:
			s += labelGather.getText( "QTTask:main", "miTimeS", SS )

		return ( self.getType(), self.index,labelGather.getText( "QTTask:main", "miTimeRemain" ), s, isCollapsed, False, "", self.showOrder, "" )

	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskTime )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return int(Time.time()) - self.val2 <= 0

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		return ""




# ------------------------------------------------------------>
# QTTaskKill
# ------------------------------------------------------------>
class QTTaskKill( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str1 = ""	# 要杀死的目标ID号
		self.str2 = ""	# 要杀死的目标名称
		self.val1 = 0	# 当前杀死数量
		self.val2 = 0	# 要杀死的数量
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_KILL

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		mname = self.str2
		linkMark = ""
		npcID = ""
		if self.str1 != "" and self.str1 not in [item["monsterID"] for item in forbidMonsters]:
			linkMark = "goto:%s" % self.str1
			mname = PL_Link.getSource( self.str2, linkMark, cfc = "c4", hfc = "c3" )	# 将怪物信息转化为超链接文本
		if linkMark: npcID = self.str1
		return ( self.getType(),  self.index, labelGather.getText( "QTTask:main", "miKill" ) + mname,
				detail2,
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				npcID
				)

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str2 ,min(self.val1, self.val2), self.val2 )

	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskKill )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

# ------------------------------------------------------------>
# QTTaskKills
# ------------------------------------------------------------>
class QTTaskKills( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str1 = ""	# 要杀死的目标ID号
		self.str2 = ""	# 要杀死的目标名称
		self.val1 = 0	# 当前杀死数量
		self.val2 = 0	# 要杀死的数量
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_KILLS

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		mname = self.str2
		if self.str1 != "" and self.str1 not in [item["monsterID"] for item in forbidMonsters]:
			linkMark = "goto:%s" % self.str1
			mname = PL_Link.getSource( self.str2, linkMark, cfc = "c4", hfc = "c3" )	# 将怪物信息转化为超链接文本
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(),  self.index, labelGather.getText( "QTTask:main", "miKill" ) + mname,
				detail2,
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				""
				)

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str2 ,min(self.val1, self.val2), self.val2 )

	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskKills )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

# ------------------------------------------------------------>
# QTTaskKill
# ------------------------------------------------------------>
class QTTaskKillWithPet( QTTaskKill ):
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_KILL_WITH_PET

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		mname = self.str2
		linkMark = ""
		npcID = ""
		if self.str1 != "" and self.str1 not in [item["monsterID"] for item in forbidMonsters]:
			linkMark = "goto:%s" % self.str1
			mname = PL_Link.getSource( self.str2, linkMark, cfc = "c4", hfc = "c3" )	# 将怪物信息转化为超链接文本
		if linkMark: npcID = self.str1
		return ( self.getType(),  self.index, labelGather.getText( "QTTask:main", "miKillWithPet" ) + mname,
				detail2,
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				npcID
				)




class QTTaskKillDart( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str1 = ""	# 要杀死的目标ID号
		self.val1 = 0	# 当前杀死数量
		self.val2 = 0	# 要杀死的数量
		"""
		QTTask.QuestTaskDataType.__init__( self )
		self.str2 = labelGather.getText( "QTTask:main", "dart_%s"%self.str1 )	# 要杀死的目标名称

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_DART_KILL

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(),  self.index, labelGather.getText( "QTTask:main", "miKill" ) + self.str2,
				detail2	,
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				""
				)

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str2 ,min(self.val1, self.val2), self.val2 )

	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskKillDart )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1


# ------------------------------------------------------------>
# QTTaskDeliver
# ------------------------------------------------------------>
class QTTaskDeliver( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str1 = ""	# 要收集的物品编号
		self.str2 = ""
		self.val1 = 0	# 当前收集数量
		self.val2 = 0	# 需要收集数量
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_DELIVER

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		mname = items.instance().id2name( int(self.str1) )
		linkMark = ""
		npcID = ""
		if self.str2 != "" and self.str2 not in [item["monsterID"] for item in forbidMonsters]:
			linkMark = "goto:%s" % self.str2
			mname = PL_Link.getSource( mname, linkMark, cfc = "c4", hfc = "c3" )	# 将怪物信息转化为超链接文本
		if linkMark: npcID = self.str2
		return ( self.getType(), 	self.index,
					labelGather.getText( "QTTask:main", "miDeliver" ) + mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					npcID
				)

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( items.instance().id2name( int(self.str1 )) ,min(self.val1, self.val2), self.val2 )


	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskDeliver )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

# ------------------------------------------------------------>
# QTTaskDeliverQuality
# ------------------------------------------------------------>
class QTTaskDeliverQuality( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str1 = ""	# 要收集的物品编号
		self.str2 = ""
		self.val1 = 0	# 当前收集数量
		self.val2 = 0	# 需要收集数量
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_DELIVER_QUALITY

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		
		name = self.getPorpertyName()
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					name,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					""
				)

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.getPorpertyName(), min(self.val1, self.val2), self.val2 )


	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskDeliverQuality )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

	def getPorpertyName( self ):
		"""
		取得需要的属性
		"""
		return eval( self.str2 )[0]

# ------------------------------------------------------------>
# QTTaskEventItemUsed
# ------------------------------------------------------------>
class QTTaskEventItemUsed( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str1 = ""	# 要使用的物品编号
		self.str2 = ""	# 任务目标描述
		self.val1 = 0	# 当前使用数量
		self.val2 = 0	# 需要使用数量
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_EVENT_USE_ITEM

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		if self.val2 <= 1 or self.val1 == -1:
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					self.str2,
					detail2,
					isCollapsed,
					self.isCompleted(),
					self.str1,
					self.showOrder,
					""
				)

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( items.instance().id2name( int( self.str1 )) ,min(self.val1, self.val2), self.val2 )


	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskEventItemUsed )
		self.__dict__.update( taskInstance.__dict__ )


# ------------------------------------------------------------>
# QTTaskSkillLearned
# ------------------------------------------------------------>
class QTTaskSkillLearned( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str2 = ""	# 任务目标描述
		self.str1 = ""	# 要学习的技能编号1
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SKILL_LEARNED

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		
		if self.isCompleted():
			detail2 = "1/1"
		else:
			detail2 = "0/1"
		if self.val1 == -1:
			isCollapsed = True	
			detail2 = ""
		mname = self.str2
		linkMark = ""
		npcID = ""
		if self.str1 != "" and self.str1 not in [item["monsterID"] for item in forbidMonsters]:
			linkMark = "goto:%d" % self.val2
			mname = PL_Link.getSource( self.str2, linkMark, cfc = "c4", hfc = "c3" )	# 将怪物信息转化为超链接文本
		if linkMark: npcID = self.val2
		return ( self.getType(), 	self.index,
					mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					npcID
				)

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		learnedStr = "0/1"
		if self.isCompleted():
			learnedStr = "1/1"
		msg = "%s   %s"
		return msg % ( self.str2 ,learnedStr )


	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1

	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskSkillLearned )
		self.__dict__.update( taskInstance.__dict__ )


# ------------------------------------------------------------>
# QTTaskLivingSkillLearned
# ------------------------------------------------------------>
class QTTaskLivingSkillLearned( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str2 = ""	# 任务目标描述
		self.str1 = ""	# 要学习的技能编号1
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_LIVING_SKILL_LEARNED

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		
		if self.isCompleted():
			detail2 = "1/1"
		else:
			detail2 = "0/1"
		
		if self.val1 == -1:
			isCollapsed = True	
			detail2 = ""
		mname = self.str2
		linkMark = ""
		npcID = ""
		if self.str1 != "" and self.str1 not in [item["monsterID"] for item in forbidMonsters]:
			linkMark = "goto:%d" % self.val2
			mname = PL_Link.getSource( self.str2, linkMark, cfc = "c4", hfc = "c3" )	# 将怪物信息转化为超链接文本
		if linkMark: npcID = self.val2
		return ( self.getType(), 	self.index,
					mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					npcID
				)

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		learnedStr = "0/1"
		if self.isCompleted():
			learnedStr = "1/1"
		msg = "%s   %s"
		return msg % ( self.str2 ,learnedStr )


	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1

	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskLivingSkillLearned )
		self.__dict__.update( taskInstance.__dict__ )

# ------------------------------------------------------------>
# QTTaskEventTrigger
# ------------------------------------------------------------>
class QTTaskEventTrigger( QTTask.QuestTaskDataType ):
	"""
	任务目标：物品使用事件（即在某地使用一个物品，使用后此目标即完成）
	"""
	def __init__( self, *args ):
		"""
		self.str1 = ""	# 要使用的物品编号
		self.str2 = ""	# 任务目标描述
		self.val1 = 0	# 当前完成状态数量
		self.val2 = 0	# 需要完成状态数量
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_EVENT_TRIGGER

	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskEventTrigger )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		# 失败标记,val1为-1时,为任务失败
		isCollapsed = False
		mname = self.str2
		linkMark = ""
		npcID = ""
		if self.str1 != "" and self.str1 not in [item["monsterID"] for item in forbidMonsters]:
			linkMark = "goto:%s" % self.str1
			mname = PL_Link.getSource( self.str2, linkMark, cfc = "c4", hfc = "c3" )	# 将怪物信息转化为超链接文本
		if linkMark: npcID = self.str1
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		elif self.val2 < 1 :
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					npcID
				)

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		if self.val1 == -1:
			return labelGather.getText( "QTTask:main", "miCollapsed", self.str2 )
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str2 ,min(self.val1, self.val2), self.val2)

# ------------------------------------------------------------>
# QTTaskOwnPet; 宠物拥有数量
# ------------------------------------------------------------>
class QTTaskOwnPet( QTTask.QuestTaskDataType ):
	def __init__( self, *args ):
		"""
		self.str1 = ""
		self.str2 = ""
		self.val1 = 0	# 当前拥有数量
		self.val2 = 0	# 需要拥有数量

		@param args: ( int ) as petAmount
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_OWN_PET

	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskOwnPet )
		self.__dict__.update( taskInstance.__dict__ )


	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		if self.val1 > self.val2:
			return ""
		return labelGather.getText( "QTTask:main", "miOwnPet_1", min(self.val1, self.val2), self.val2 )

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		
		mname = labelGather.getText( "QTTask:main", "miOwnPet_2" )
		linkMark = ""
		npcID = ""
		if self.str1 != "" and self.str1 not in [item["monsterID"] for item in forbidMonsters]:
			linkMark = "goto:%s" % self.str1
			mname = PL_Link.getSource( mname, linkMark, cfc = "c4", hfc = "c3" )	# 将怪物信息转化为超链接文本
		if linkMark: npcID = self.str1
		if self.val1 == -1:
			isCollapsed = True	
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					npcID
				)
#-------------------------------------------->
#QTTaskSubmit 提交任务目标
#-------------------------------------------->
class QTTaskSubmit( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str1 = ""	#物品ID
		self.str2 = ""  #物品属性以及数值
		self.val1 = 0	#玩家拥有物品数量
		self.val2 = 0	#任务需要的物品数量
		"""
		QTTask.questTaskDataType.__init__( self )


	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT


	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		
		name = items.instance().id2name( int(self.str1) ) + self.getExtraDescription()
		if self.val1 == -1:
			isCollapsed = True	
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					name,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					""
				)

	def getMsg( self ):
		"""
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s %s:    %i/%i"
		return msg % (items.instance().id2name( int( self.str1 ) ), self.getPorpertyName(), min(self.val1, self.val2), self.val2 )

	def getPorpertyName( self ):
		"""
		取得需要的属性
		"""
		return eval( self.str2 )[0]


	def getPorpertyValue( self ):
		"""
		取得需要的属性值
		"""
		return int(eval( self.str2 )[1])

	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskSubmit )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

	def getExtraDescription( self ):
		"""
		"""
		return 	self.getPorpertyName()


#-------------------------------------------->
#QTTaskTeam 组队任务
#-------------------------------------------->
class QTTaskTeam( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str1 = ""		#队友职业
		self.str2 = ""  	#
		self.val1 = 0		#该职业队友数量
		self.val2 = 0		#该职业队友需求数量
		"""
		QTTask.questTaskDataType.__init__( self )


	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_TEAM


	def getDetail( self ):
		"""
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True	
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					csconst.g_chs_class[ int( self.str1 ) << 4 ],
					detail2,
					isCollapsed,
					self.val1 >= self.val2,
					"",
					self.showOrder,
					""
				)

	def getMsg( self ):
		"""
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s    %i/%i"
		return msg % ( csconst.g_chs_class[ int( self.str1 ) << 4 ], min(self.val1, self.val2), self.val2 )


	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskTeam )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		"""
		return self.val1 >= self.val2

	def getOccupation( self ):
		"""
		获得需求对有职业
		"""
		return int( self.str1 ) << 4


# ------------------------------------------------------------>
# QTTaskLevel
# ------------------------------------------------------------>
class QTTaskLevel( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str1 = ""	# 要达到的等级描述
		self.val1 = 0	# 玩家当前等级数值
		self.val2 = 0	# 要达到的等级数值
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_LEVEL

	def getDetail( self ):
		"""
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True	
			detail2 = ""
		else:
			detail2 = labelGather.getText( "QTTask:main", "miLevel", BigWorld.player().level )
		return ( self.getType(),  self.index, self.str1,
				detail2,
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				""
				)

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str2 ,min(self.val1, self.val2), self.val2 )

	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskLevel )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= BigWorld.player().level


# ------------------------------------------------------------>
# QTTaskQuestNormal
# ------------------------------------------------------------>
class QTTaskQuestNormal( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str1 = ""	# 要达到的等级描述
		self.val1 = 0	# 玩家当前等级数值
		self.val2 = 0	# 要达到的等级数值
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_QUEST_NORMAL

	def getDetail( self ):
		"""
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		return ( self.getType(),  self.index, self.str1,
				"",
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				""
				)

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		return self.str1

	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskQuest )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2


# ------------------------------------------------------------>
# QTTaskQuest
# ------------------------------------------------------------>
class QTTaskQuest( QTTaskQuestNormal ):
	def __init__( self ):
		"""
		self.str1 = ""	# 要达到的等级描述
		self.val1 = 0	# 玩家当前等级数值
		self.val2 = 0	# 要达到的等级数值
		"""
		QTTaskQuestNormal.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_QUEST


# ------------------------------------------------------------>
# QTTaskSubmitPicture
# ------------------------------------------------------------>
class QTTaskSubmitPicture( QTTaskDeliver ):
	def __init__( self ):
		"""
		self.str1 = ""	#物品ID
		self.str2 = ""	#NPC calssName
		self.val1 = 0	#玩家拥有数量
		self.val2 = 0	#需要提交数量
		"""
		QTTaskDeliver.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_PICTURE

	def getDetail( self ):
		"""
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		mname = NPCDatasMgr.npcDatasMgr.getNPC( self.str2 ).name
		linkMark = ""
		npcID = ""
		if self.str2 != "" and self.str2 not in [item["monsterID"] for item in forbidMonsters]:
			linkMark = "goto:%s" % self.str2
			mname = PL_Link.getSource( mname, linkMark, cfc = "c4", hfc = "c3" )	# 将怪物信息转化为超链接文本
		if linkMark: npcID = self.str2
		return ( self.getType(),  self.index, mname + labelGather.getText( "QTTask:main", "miPicture" ),
				"",
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				npcID
				)

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		msg = "%s %s   %i/%i"
		return ""
		#return msg % ( items.instance()[int( self.str1 )]["name"], g_objFactory.getObject(self.str2).getName(), "的画像。", self.val1, self.val2 )


	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskSubmitPicture )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2

# ------------------------------------------------------------>
# QTTaskSubmitChangeBody
# ------------------------------------------------------------>
class QTTaskSubmitChangeBody( QTTaskSubmitPicture ):
	def __init__( self ):
		"""
		self.str1 = ""	#物品ID
		self.str2 = ""	#NPC calssName
		self.val1 = 0	#玩家拥有数量
		self.val2 = 0	#需要提交数量
		"""
		QTTaskSubmitPicture.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_CHANGE_BODY

	def getDetail( self ):
		"""
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		return ( self.getType(),  self.index, NPCDatasMgr.npcDatasMgr.getNPC( self.str2 ).name + labelGather.getText( "QTTask:main", "miChangeBody" ),
				"",
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				""
				)

	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskSubmitChangeBody )
		self.__dict__.update( taskInstance.__dict__ )

# ------------------------------------------------------------>
# QTTaskSubmitDance
# ------------------------------------------------------------>
class QTTaskSubmitDance( QTTaskSubmitPicture ):
	def __init__( self ):
		"""
		self.str1 = ""	#物品ID
		self.str2 = ""	#NPC calssName
		self.val1 = 0	#玩家拥有数量
		self.val2 = 0	#需要提交数量
		"""
		QTTaskSubmitPicture.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_DANCE

	def getDetail( self ):
		"""
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		mname = NPCDatasMgr.npcDatasMgr.getNPC( self.str2 ).name
		linkMark = ""
		npcID = ""
		if self.str2 != "" and self.str2 not in [item["monsterID"] for item in forbidMonsters]:
			linkMark = "goto:%s" % self.str2
			mname = PL_Link.getSource( mname, linkMark, cfc = "c4", hfc = "c3" )	# 将怪物信息转化为超链接文本
		if linkMark: npcID = self.str2
		return ( self.getType(),  self.index, mname + labelGather.getText( "QTTask:main", "miDance" ),
				"",
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				npcID
				)

	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskSubmitDance )
		self.__dict__.update( taskInstance.__dict__ )

# ------------------------------------------------------------>
# QTTaskDeliver
# ------------------------------------------------------------>
class QTTaskDeliverPet( QTTaskDeliver ):
	def __init__( self ):
		"""
		self.str1 = ""	# 要收集的宠物编号
		self.str2 = "" 	# 要收集的宠物名称
		self.val1 = 0	# 当前收集数量
		self.val2 = 0	# 需要收集数量
		"""
		QTTask.QTTaskDeliver.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_DELIVER_PET

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		
		mname = self.str2
		linkMark = ""
		npcID = ""
		if self.str1 != "" and self.str1 not in [item["monsterID"] for item in forbidMonsters]:
			linkMark = "goto:%s" % self.str1
			mname = PL_Link.getSource( self.str2, linkMark, cfc = "c4", hfc = "c3" )	# 将怪物信息转化为超链接文本
		if linkMark: npcID = self.str1
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					labelGather.getText( "QTTask:main", "miDeliverPet" ) + mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					npcID
				)

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str2 ,min(self.val1, self.val2), self.val2 )


	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskDeliver )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1


class QTTaskSubmit_Quality( QTTaskSubmit ):
	def __init__( self ):
		"""
		self.str1 = ""	#物品ID
		self.str2 = ""  #物品属性以及数值
		self.val1 = 0	#玩家拥有物品数量
		self.val2 = 0	#任务需要的物品数量
		"""
		QTTaskSubmit.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_QUALITY


	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskSubmit_Quality )
		self.__dict__.update( taskInstance.__dict__ )


class QTTaskSubmit_Slot( QTTaskSubmit ):
	def __init__( self ):
		"""
		self.str1 = ""	#物品ID
		self.str2 = ""  #物品属性以及数值
		self.val1 = 0	#玩家拥有物品数量
		self.val2 = 0	#任务需要的物品数量
		"""
		QTTaskSubmit.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_SLOT


	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskSubmit_Slot )
		self.__dict__.update( taskInstance.__dict__ )

class QTTaskSubmit_Effect( QTTaskSubmit ):
	def __init__( self ):
		"""
		self.str1 = ""	#物品ID
		self.str2 = ""  #物品属性以及数值
		self.val1 = 0	#玩家拥有物品数量
		self.val2 = 0	#任务需要的物品数量
		"""
		QTTaskSubmit.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_EFFECT


	def getMsg( self ):
		"""
		"""
		if self.val1 == self.val2:
			return ""
		msg = "%s %s:    %i/%i"
		return msg % (items.instance().id2name( int( self.str1 ) ), self.getPorpertyName(), min(self.val1, self.val2), self.val2 )


	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskSubmit_Effect )
		self.__dict__.update( taskInstance.__dict__ )


class QTTaskSubmit_Level( QTTaskSubmit ):
	def __init__( self ):
		"""
		self.str1 = ""	#物品ID
		self.str2 = ""  #物品属性以及数值
		self.val1 = 0	#玩家拥有物品数量
		self.val2 = 0	#任务需要的物品数量
		"""
		QTTaskSubmit.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_LEVEL


	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskSubmit_Level )
		self.__dict__.update( taskInstance.__dict__ )

class QTTaskSubmit_Empty( QTTaskSubmit ):
	def __init__( self ):
		"""
		self.str1 = ""	#物品ID
		self.str2 = ""  #物品属性以及数值
		self.val1 = 0	#玩家拥有物品数量
		self.val2 = 0	#任务需要的物品数量
		"""
		QTTaskSubmit.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_EMPTY

	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskSubmit_Empty )
		self.__dict__.update( taskInstance.__dict__ )

class QTTaskNotSubmit_Empty( QTTaskSubmit ):
	def __init__( self ):
		"""
		self.str1 = ""	#物品ID
		self.str2 = ""  #物品属性以及数值
		self.val1 = 0	#玩家拥有物品数量
		self.val2 = 0	#任务需要的物品数量
		"""
		QTTaskSubmit.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_NOT_SUBMIT_EMPTY

	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskNotSubmit_Empty )
		self.__dict__.update( taskInstance.__dict__ )

class QTTaskSubmit_Yinpiao( QTTaskSubmit ):
	def __init__( self ):
		"""
		self.str1 = ""	#物品ID
		self.str2 = ""  #物品属性以及数值
		self.val1 = 0	#玩家拥有物品数量
		self.val2 = 0	#任务需要的物品数量
		"""
		QTTaskSubmit.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_YINPIAO


	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskSubmit_Yinpiao )
		self.__dict__.update( taskInstance.__dict__ )

	def getMsg( self ):
		"""
		"""
		msg = "%s %s:%i    %i/%i"
		return msg % (items.instance().id2name( int( self.str1 ) ), self.getPorpertyName(), self.getPorpertyValue(), min(self.val1, self.val2), self.val2 )


class QTTaskSubmit_Binded( QTTaskSubmit ):
	def __init__( self ):
		"""
		self.str1 = ""	#物品ID
		self.str2 = ""  #物品属性以及数值
		self.val1 = 0	#玩家拥有物品数量
		self.val2 = 0	#任务需要的物品数量
		"""
		QTTaskSubmit.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_BINDED


	def getMsg( self ):
		"""
		"""
		if self.val1 == self.val2:
			return ""
		msg = "%s %s:    %i/%i"
		return msg % (items.instance().id2name( int( self.str1 ) ), self.getPorpertyName(), min(self.val1, self.val2), self.val2 )


	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskSubmit_Binded )
		self.__dict__.update( taskInstance.__dict__ )


# ------------------------------------------------------------>
# QTTaskKill
# ------------------------------------------------------------>
class QTTaskPetEvent( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.index = args[0]		# index
		self.str1 = args[1]			# 触发类型
		self.str2 = args[2]			# 任务描述
		self.val2 = args[3]			# 触发次数
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_PET_EVENT

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True	
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(),  self.index, self.str2,
				detail2,
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				""
				)

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str2 ,min(self.val1, self.val2), self.val2 )

	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskPetEvent )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

# ------------------------------------------------------------>
# QTTaskevolution
# ------------------------------------------------------------>
class QTTaskEvolution( QTTaskKill ):	#怪物进化 spf

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_EVOLUTION

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		
		mname = self.str2
		linkMark = ""
		npcID = ""
		if self.str1 != "" and self.str1 not in [item["monsterID"] for item in forbidMonsters]:
			npcData = rds.npcDatasMgr.getNPC( self.str2 )
			if npcData is not None:
				mname = labelGather.getText( "QTTask:main", "mibeat" ) + npcData.entityName
				linkMark = "goto:%s" % self.str2
			else:
				linkMark = "goto:%s" % self.str1
			mname = PL_Link.getSource( mname, linkMark, cfc = "c4", hfc = "c3" )	# 将怪物信息转化为超链接文本
		if linkMark: npcID = linkMark.split( ":" )[1]
		if self.val1 == -1:
			isCollapsed = True	
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(),  self.index, mname,
				detail2,
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				npcID
				)



# ------------------------------------------------------------>
# QTTaskEventTrigger
# ------------------------------------------------------------>
class QTTaskImperialExamination( QTTask.QuestTaskDataType ):
	"""
	"""
	def __init__( self, *args ):
		"""
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_IMPERIAL_EXAMINATION

	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskImperialExamination )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		# 失败标记,val1为-1时,为任务失败
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		elif self.val2 < 1 :
			detail2 = ""
		else:
			detail2 = labelGather.getText( "QTTask:main", "miRight_1", min(self.val1, self.val2), self.val2, self.str1 )
		return ( self.getType(), 	self.index,
					self.str2,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					""
				)

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		if self.val1 > self.val2:
			return ""
		return labelGather.getText( "QTTask:main", "miRight_2", self.str2 ,min(self.val1, self.val2), self.val2, self.str1 )


# ------------------------------------------------------------>
# QTTaskShowKaoGuan
# ------------------------------------------------------------>
from csconst import KAOGUANS
class QTTaskShowKaoGuan( QTTask.QuestTaskDataType ):
	"""
	"""
	def __init__( self, *args ):
		"""
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SHOW_KAOGUAN

	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskShowKaoGuan )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		
		detail = ""
		npcID = ""
		if KAOGUANS.has_key( self.val1+1 ):
			detail = KAOGUANS[self.val1+1]
			npcID = detail.split( ":" )[1].split( ";" )[0]

		if self.val1 == -1:
			isCollapsed = True	
			detail = ""
		return (self.getType(),
					self.index,
					self.str2,
					detail,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					npcID
				)

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		msg = ""
		if KAOGUANS.has_key( self.val1+1 ):
			msg = labelGather.getText( "QTTask:main", "miNextTest", self.val1 + 1 )
		return msg



# ------------------------------------------------------------>
# QTTaskQuestiong
# ------------------------------------------------------------>
class QTTaskQuestion( QTTaskEventTrigger ):
	"""
	任务目标：物品使用事件（即在某地使用一个物品，使用后此目标即完成）
	"""
	def __init__( self, *args ):
		"""
		self.str1 = ""	# 要使用的物品编号
		self.str2 = ""	# 任务目标描述
		self.val1 = 0	# 当前完成状态数量
		self.val2 = 0	# 需要完成状态数量
		"""
		QTTaskEventTrigger.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_QUESTION

	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskQuestion )
		self.__dict__.update( taskInstance.__dict__ )
		
	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		# 失败标记,val1为-1时,为任务失败
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		elif self.val2 < 1 :
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					self.str2,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					""
				)



# ------------------------------------------------------------>
# QTTaskPetAct	出战宠物	2009-07-15 14:30 SPF
# ------------------------------------------------------------>
class QTTaskPetAct( QTTaskEventTrigger ):
	"""
	任务目标：物品使用事件（即在某地使用一个物品，使用后此目标即完成）
	"""
	def __init__( self, *args ):
		"""
		self.str1 = ""	# 要使用的物品编号
		self.str2 = ""	# 任务目标描述
		self.val1 = 0	# 当前完成状态数量
		self.val2 = 0	# 需要完成状态数量
		"""
		QTTaskEventTrigger.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_PET_ACT

	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskPetAct )
		self.__dict__.update( taskInstance.__dict__ )

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		self.str2 = labelGather.getText( "QTTask:main", "miPetAct" )
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		elif self.val2 < 1 :
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					self.str2,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					""
				)

class QTTaskTalk( QTTaskEventTrigger ):
	"""
	"""
	def __init__( self, *args ):
		"""
		"""
		QTTaskEventTrigger.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_TALK

	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskTalk )
		self.__dict__.update( taskInstance.__dict__ )

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		# 失败标记,val1为-1时,为任务失败
		mname = self.str2
		linkMark = ""
		npcID = ""
		if self.str1 != "" and self.str1 not in [item["npcID"] for item in forbidNPCs]:
			linkMark = "goto:%s" % self.str1
			mname = PL_Link.getSource( self.str2, linkMark, cfc = "c4", hfc = "c3" )	# 将怪物信息转化为超链接文本
		if linkMark: npcID = self.str1
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		elif self.val2 < 1 :
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					npcID
				)


class QTTaskHasBuff( QTTaskEventTrigger ):
	"""
	"""
	def __init__( self, *args ):
		"""
		"""
		QTTaskEventTrigger.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_HASBUFF

	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskHasBuff )
		self.__dict__.update( taskInstance.__dict__ )

class QTTaskPotentialFinish( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.index = args[0]		# index
		self.str1 = args[1]			# 触发类型
		self.str2 = args[2]			# 任务描述
		self.val2 = args[3]			# 触发次数
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_POTENTIAL_FINISH

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True	
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(),  self.index, self.str1,
				detail2,
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				""
				)

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str1 ,min(self.val1, self.val2), self.val2 )

	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskPotentialFinish )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1


class QTTaskSubmit_LQEquip( QTTaskSubmit ):
	def __init__( self ):
		"""
		self.str1 = ""	#物品ID
		self.str2 = ""  #物品属性以及数值
		self.val1 = 0	#玩家拥有物品数量
		self.val2 = 0	#任务需要的物品数量
		"""
		QTTaskSubmit.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_LQEQUIP


	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskSubmit_LQEquip )
		self.__dict__.update( taskInstance.__dict__ )


	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		name = labelGather.getText( "QTTask:main", "miHighLevelEquip" )
		if self.val1 == -1:
			isCollapsed = True	
			detail2 = ""
		else:
			detail2 =  "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					name,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					""
				)

	def getMsg( self ):
		"""
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s %s:    %i/%i"
		return msg % (labelGather.getText( "QTTask:main", "miHighLevelEquip" ), self.getPorpertyName(), min(self.val1, self.val2), self.val2 )


	def getPorpertyName( self ):
		"""
		取得需要的属性
		"""
		return ""


# ------------------------------------------------------------>
# QTTaskEventSkillUsed
# ------------------------------------------------------------>
class QTTaskEventSkillUsed( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_EVENT_USE_SKILL

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		mname = self.str1.split(":")[0]
		linkMark = ""
		npcID = ""
		if self.str2 != "" and self.str2 not in [item["monsterID"] for item in forbidMonsters]:
			linkMark = "goto:%s" % self.str2
			mname = PL_Link.getSource( mname, linkMark, cfc = "c4", hfc = "c3" )	# 将怪物信息转化为超链接文本
		if linkMark: npcID = self.str2
		if self.val2 <= 1 or self.val1 == -1:
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					npcID
				)

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str1.split(":")[0] ,min(self.val1, self.val2), self.val2 )


	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskEventSkillUsed )
		self.__dict__.update( taskInstance.__dict__ )



# ------------------------------------------------------------>
# QTTaskEventUpdateSetRevivePos
# ------------------------------------------------------------>
class QTTaskEventUpdateSetRevivePos( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_EVENT_REVIVE_POS

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		if self.val2 <= 1 or self.val1 == -1:
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					self.str1,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					""
				)

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str1, min(self.val1, self.val2), self.val2 )


	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskEventUpdateSetRevivePos )
		self.__dict__.update( taskInstance.__dict__ )


class QTTaskEnterSpace( QTTask.QuestTaskDataType ):
	"""
	进入某一个空间
	"""	
	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2
		
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_ENTER_SPCACE

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str1, min(self.val1, self.val2), self.val2 )

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True	
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return (self.getType(),
					self.index,
					self.str1,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					""
				)

	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskEnterSpace )
		self.__dict__.update( taskInstance.__dict__ )

class QTTaskPotential( QTTask.QuestTaskDataType ):
	"""
	潜能任务专用
	"""
	def __init__( self, *args ):
		"""
		self.str1 = ""
		self.str2 = ""
		self.val1 = 0
		self.val2 = 0
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_POTENTIAL

	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskPotential )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		# 失败标记,val1为-1时,为任务失败
		isCollapsed = False
		mname = self.str2
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		elif self.val2 < 1 :
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					""
				)

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		if self.val1 == -1:
			return labelGather.getText( "QTTask:main", "miCollapsed", self.str2 )
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str2 ,min(self.val1, self.val2), self.val2 )
		
class QTTaskAddCampMorale( QTTask.QuestTaskDataType ):
	"""
	获取阵营士气
	"""
	def __init__( self, *args ):
		"""
		self.str1 = ""
		self.str2 = ""
		self.val1 = 0
		self.val2 = 0
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_ADD_CAMP_MORALE

	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskAddCampMorale )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		# 失败标记,val1为-1时,为任务失败
		isCollapsed = False
		mname = self.str1
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		elif self.val2 < 1 :
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					""
				)

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		if self.val1 == -1:
			return labelGather.getText( "QTTask:main", "miCollapsed", self.str1 )
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str1 ,min(self.val1, self.val2), self.val2 )
		
	
	
		
class QTTaskKill_CampActivity( QTTaskKill ):
	"""
	阵营活动击杀怪物任务
	"""
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_CAMP_KILL
		
	def getSpaceLabel( self ):
		"""
		获得目标所在地图
		"""
		spaces = self.str3.split(";")
		if len( spaces ) == 0:
			return ""
		return spaces[0]
	
	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		mname = self.str2
		linkMark = ""
		npcID = ""
		
		dstPos = None
		if self.str1 != "" and self.str1 not in [item["monsterID"] for item in forbidMonsters]:
			for i in self.str3.split(";"):
				if i == "":
					continue
				dstPos = rds.npcDatasMgr.getNPCPosition( self.str1, i )
				if not dstPos:
					continue
				pos = [ dstPos[0], dstPos[1], dstPos[2] ]
				linkMark = "goto:%s*%s"%( pos, i )
				break
			if not dstPos:
				linkMark = "goto:%s" % self.str2
			mname = PL_Link.getSource( self.str2, linkMark, cfc = "c4", hfc = "c3" )	# 将怪物信息转化为超链接文本
		if linkMark: npcID = self.str1
		return ( self.getType(),  self.index, labelGather.getText( "QTTask:main", "miKill" ) + mname,
				detail2,
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				npcID
				)
	
class QTTaskVehicleActived( QTTaskEventTrigger ):
	"""
	激活指定骑宠
	"""
	def __init__( self, *args ):
		"""
		"""
		QTTaskEventTrigger.__init__( self )
		
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_VEHICLE_ACTIVED
	
	def isCompleted( self ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2

	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskVehicleActived )
		self.__dict__.update( taskInstance.__dict__ )

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		self.str2 = labelGather.getText( "QTTask:main", "miVehicleAct" )
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		elif self.val2 < 1 :
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					self.str2,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					""
				)

class QTTaskDeliver_CampActivity( QTTaskDeliver ):
	"""
	阵营活动交付物品任务目标
	"""
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_CAMPACT_DELIVER
		
	def getSpaceLabel( self ):
		"""
		获得目标所在地图
		"""
		return self.str2.split(":")[0]

	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		mname = items.instance().id2name( int(self.str1) )
		linkMark = ""
		npcID = ""
		if self.str2 != "" and self.str2.split(":")[1] not in [item["monsterID"] for item in forbidMonsters]:	# str2 like: "spaceName:NPCID"
			spaceName = self.str2.split(":")[0]
			npcClassName = self.str2.split(":")[1]
			dstPos = rds.npcDatasMgr.getNPCPosition( npcClassName, spaceName )
			if dstPos:
				pos = [ dstPos[0], dstPos[1], dstPos[2] ]
				linkMark = "goto:%s*%s"%( pos, spaceName )
			else:
				linkMark = "goto:%s" % npcClassName
			mname = PL_Link.getSource( mname, linkMark, cfc = "c4", hfc = "c3" )	# 将怪物信息转化为超链接文本
		
		if linkMark: npcID = self.str2.split(":")[1]
		return ( self.getType(), 	self.index,
					labelGather.getText( "QTTask:main", "miDeliver" ) + mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					npcID
				)

class QTTaskTalk_CampActivity( QTTaskTalk ):
	"""
	阵营活动对话任务
	"""
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_CAMPACT_TALK
		
	def getSpaceLabel( self ):
		"""
		获得目标所在地图
		"""
		return self.str1.split(":")[0]
		
	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		# 失败标记,val1为-1时,为任务失败
		mname = self.str2
		linkMark = ""
		npcID = ""
		if self.str1 != "" and self.str1.split(":")[1] not in [item["npcID"] for item in forbidNPCs]:
			spaceName = self.str1.split(":")[0]
			npcClassName = self.str1.split(":")[1]
			dstPos = rds.npcDatasMgr.getNPCPosition( npcClassName, spaceName )
			if dstPos:
				pos = [ dstPos[0], dstPos[1], dstPos[2] ]
				linkMark = "goto:%s*%s"%( pos, spaceName )
			else:
				linkMark = "goto:%s" % npcClassName
			mname = PL_Link.getSource( mname, linkMark, cfc = "c4", hfc = "c3" )	# 将怪物信息转化为超链接文本
		
		if linkMark: npcID = self.str1.split(":")[1]
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		elif self.val2 < 1 :
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					npcID
				)


class QTTaskEventItemUsed_CampActivity( QTTaskEventItemUsed ):
	"""
	阵营活动使用物品任务目标:对指定地图上的目标使用物品
	"""
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_CAMPACT_EVENT_USE_ITEM
		
	def getSpaceLabel( self ):
		"""
		获得目标所在地图
		"""
		return self.str2.split(":")[0]
	
	def getDetail( self ):
		"""
		取得相关描述
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
		@rtype:  tuple
		"""
		className = self.str2.split(":")[1]
		mname = ""
		linkMark = ""
		npcID = ""
		if className != "" and className not in [item["npcID"] for item in forbidNPCs]:
			spaceName = self.str2.split(":")[0]
			mname = NPCDatasMgr.npcDatasMgr.getNPC( className ).name
			dstPos = rds.npcDatasMgr.getNPCPosition( className, spaceName )
			if dstPos:
				pos = [ dstPos[0], dstPos[1], dstPos[2] ]
				linkMark = "goto:%s*%s"%( pos, spaceName )
			else:
				linkMark = "goto:%s" % className
			mname = PL_Link.getSource( mname, linkMark, cfc = "c4", hfc = "c3" )	# 将怪物信息转化为超链接文本
			
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		if self.val2 <= 1 or self.val1 == -1:
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
			
		return ( self.getType(), 	self.index,
					self.str2.split(":")[2] % mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					self.str1,
					self.showOrder,
					className
				)

QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_TIME,					QTTaskTime )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_KILL,					QTTaskKill )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_KILLS,					QTTaskKills )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_DART_KILL,				QTTaskKillDart )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_DELIVER,				QTTaskDeliver )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_EVENT_USE_ITEM,		QTTaskEventItemUsed )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SKILL_LEARNED,			QTTaskSkillLearned )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_LIVING_SKILL_LEARNED,			QTTaskLivingSkillLearned )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_OWN_PET,				QTTaskOwnPet )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT,				QTTaskSubmit )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_TEAM,					QTTaskTeam )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_EVENT_TRIGGER,			QTTaskEventTrigger )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_LEVEL,					QTTaskLevel )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_QUEST,					QTTaskQuest )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_QUEST_NORMAL,			QTTaskQuestNormal )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_PICTURE,		QTTaskSubmitPicture)
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_CHANGE_BODY,	QTTaskSubmitChangeBody)
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_DANCE,			QTTaskSubmitDance)
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_DELIVER_PET,			QTTaskDeliverPet)
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_QUALITY,		QTTaskSubmit_Quality )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_SLOT,			QTTaskSubmit_Slot )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_EFFECT,			QTTaskSubmit_Effect )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_LEVEL,			QTTaskSubmit_Level )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_BINDED,			QTTaskSubmit_Binded )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_EMPTY,			QTTaskSubmit_Empty)
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_PET_EVENT,				QTTaskPetEvent )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_EVOLUTION,				QTTaskEvolution )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_YINPIAO,		QTTaskSubmit_Yinpiao )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_IMPERIAL_EXAMINATION,	QTTaskImperialExamination )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_KILL_WITH_PET,			QTTaskKillWithPet )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SHOW_KAOGUAN,			QTTaskShowKaoGuan )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_QUESTION,				QTTaskQuestion )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_PET_ACT,				QTTaskPetAct )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_TALK,					QTTaskTalk )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_HASBUFF,				QTTaskHasBuff )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_DELIVER_QUALITY,		QTTaskDeliverQuality )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_POTENTIAL_FINISH,		QTTaskPotentialFinish )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_LQEQUIP,		QTTaskSubmit_LQEquip )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_EVENT_USE_SKILL,		QTTaskEventSkillUsed )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_EVENT_REVIVE_POS,		QTTaskEventUpdateSetRevivePos )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_ENTER_SPCACE,			QTTaskEnterSpace )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_POTENTIAL,				QTTaskPotential )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_NOT_SUBMIT_EMPTY,		QTTaskNotSubmit_Empty )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_ADD_CAMP_MORALE,		QTTaskAddCampMorale )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_CAMP_KILL,				QTTaskKill_CampActivity )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_VEHICLE_ACTIVED,				QTTaskVehicleActived )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_CAMPACT_DELIVER,		 QTTaskDeliver_CampActivity )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_CAMPACT_TALK,		 QTTaskTalk_CampActivity )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_CAMPACT_EVENT_USE_ITEM, QTTaskEventItemUsed_CampActivity )



# $Log: not supported by cvs2svn $
# Revision 1.43  2008/08/20 01:26:25  zhangyuxing
# 增加宠物指引任务相关任务目标
#
# Revision 1.42  2008/08/15 09:19:37  zhangyuxing
# 合并提交特殊物品任务目标，增加强化，镶嵌，强化等级任务目标
#
# Revision 1.41  2008/08/12 07:13:31  zhangyuxing
# 修改物品类型 int , str 之间动态交换
#
# Revision 1.40  2008/08/07 08:59:22  zhangyuxing
# 增加提交宠物任务目标
#
# Revision 1.39  2008/08/04 06:30:58  zhangyuxing
# 增加提交画板任务目标
#
# Revision 1.38  2008/07/28 02:34:25  zhangyuxing
# 增加等级任务类型
#
# Revision 1.37  2008/07/14 06:19:15  zhangyuxing
# 加入等级变化，任务完成查询
#
# Revision 1.35  2008/06/13 05:34:17  wangshufeng
# 调整任务描述信息
#
# Revision 1.34  2008/05/28 08:55:38  zhangyuxing
# no message
#
# Revision 1.33  2008/05/16 01:37:35  zhangyuxing
# no message
#
# Revision 1.32  2008/05/12 07:13:54  wangshufeng
# 修改QTTaskEventTrigger的getDetail：if self.val2 <= 1修改为if self.val2 < 1
#
# Revision 1.31  2008/04/26 06:43:30  zhangyuxing
# no message
#
# Revision 1.30  2008/04/15 06:51:13  zhangyuxing
# 修改任务提示 分子大于分母的情况
#
# Revision 1.29  2008/01/25 09:24:59  kebiao
# modify:QTTaskEventTrigger  in COPYINSTANCE
#
# Revision 1.28  2008/01/22 08:19:44  zhangyuxing
# no message
#
# Revision 1.27  2008/01/22 02:20:26  phw
# fixed: TypeError: isCompleted() takes exactly 2 arguments (1 given)
#
# Revision 1.26  2008/01/09 03:48:46  zhangyuxing
# 增加任务目标
# QTTaskTeam（组队成员职业要求）
# QTTaskSubmitHole（孔数）
# 修改所有任务目标getDetail 方法的返回（增加了索引）
#
# Revision 1.25  2007/12/27 02:02:20  phw
# method modified: QTTaskEventTrigger::isCompleted(), 去掉多余的参数player
#
# Revision 1.24  2007/12/19 03:34:39  kebiao
# 添加事件触发任务 映射
#
# Revision 1.23  2007/12/19 03:32:52  kebiao
# add:QTTaskEventTrigger 事件触发任务
#
# Revision 1.22  2007/12/17 11:31:27  zhangyuxing
# 增加类： class QTTaskSubmit( QTTaskDeliver ):
#
# Revision 1.21  2007/12/08 09:23:54  phw
# 修正了QTTaskKill类没有显示怪物名称的问题
#
# Revision 1.20  2007/12/05 07:00:59  phw
# class added: QTTaskOwnPet
#
# Revision 1.19  2007/11/02 03:51:07  phw
# 修改继承模式，直接继承于QuestTaskDataType.QuestTaskDataType，并直接向QuestTaskDataType模块注册自己
#
# Revision 1.18  2007/09/19 01:19:57  phw
# method modified: QTTaskDeliver::addToStream(), QTTaskDeliver::loadFromStream(), 修正了"DeprecationWarning: 'L' format requires 0 <= number <= 4294967295"的提示
#
# Revision 1.17  2007/06/14 10:32:35  huangyongwei
# 整理了全局宏定义
#
# Revision 1.16  2007/05/18 01:56:39  kebiao
# no message
#
# Revision 1.15  2007/05/17 08:07:30  kebiao
# 修正时间显示格式
#
# Revision 1.14  2007/05/15 08:33:32  kebiao
# 使用Time 来解决服务器时间同步问题
#
# Revision 1.13  2007/03/20 01:31:53  phw
# method modified: QTTaskTime::getDetail(), 剩余时间小于0时视为0，且任务失败。
#
# Revision 1.12  2007/03/14 03:01:04  kebiao
# 去掉QTTASKTIME 的一个必将错误的判断
# 此处存在服务器和客户端时间同步问题 将来必将解决
#
# Revision 1.11  2007/03/12 06:55:52  kebiao
# 添加获取该task状态接口
#
# Revision 1.10  2007/03/09 06:32:23  kebiao
# 修正timeTask解包错误
#
# Revision 1.9  2007/02/12 07:16:05  phw
# QTTaskDeliver类型打包格式从"LLLLB"改为"LLLlB"
#
# Revision 1.8  2006/09/05 09:14:57  chenzheming
# no message
#
# Revision 1.7  2006/08/09 08:31:24  phw
# 导入模块ItemDataList改为导入items
#
# Revision 1.6  2006/08/05 08:17:58  phw
# 修改接口：
#     QTTaskDeliver::getDetail()
#     from: name = ItemDataList.instance()[self._deliverID].name
#     to:   name = ItemDataList.instance().id2name( self._deliverID )
#
# Revision 1.5  2006/03/28 07:18:52  phw
# changed TASK_OBJECTIVE_USE_ITEM to QUEST_OBJECTIVE_ACTIVE_ITEM
#
# Revision 1.4  2006/03/28 04:47:38  phw
# change class name from QTTaskUseItem to QTTaskActiveItem
#
# Revision 1.3  2006/03/28 03:38:22  phw
# 加入使用物品任务目标，getDetail()从原来的返回简单描述改为以下形式：
# @return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("野猪", "1/10", bool, bool)
#
# Revision 1.2  2006/01/24 09:36:57  phw
# no message
#
# Revision 1.1  2006/01/24 02:19:56  phw
# no message
#
#