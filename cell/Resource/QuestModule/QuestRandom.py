# -*- coding: gb18030 -*-
#
# $Id: QuestRandom.py,v 1.12 2008-08-07 08:58:13 zhangyuxing Exp $

"""
随机任务模块
"""

from bwdebug import *
import csstatus
from Quest import *
from QuestDataType import QuestDataType
from ObjectScripts.GameObjectFactory import g_objFactory
import Love3

class QuestRandom( Quest ):
	def __init__( self ):
		Quest.__init__( self )
		self._group_id = 0							#组任务ID
		self._point = 0								#随机任务分值
		self._minus_interval = 0					#任务的负向等级浮动最大差
		self._positive_interval = 0					#任务的正向等级浮动最大差
		self._patternDict = {}						#模式匹配参数字典
		self._style = csdefine.QUEST_STYLE_RANDOM	#任务样式


	def init( self, section ):
		"""
		@param section: 任务配置文件section
		@type  section: pyDataSection
		"""
		Quest.init( self, section )

		self._minus_interval = section.readInt( "minus_interval" )
		self._positive_interval = section.readInt( "positive_interval" )

		self._group_id = section.readInt( "random_group_id" )		# 随机任务组ID(也就是当前任务的parent id)

		self._point = section.readInt("point")						#随机子任务分值

		extSection = section["quest_pattern"]						#随机任务模式
		self._patternType = extSection.readInt( "type" )
		self._patternDict["p1"] = extSection.readString( "param1" )
		self._patternDict["p2"] = extSection.readString( "param2" )
		self._patternDict["p3"] = extSection.readString( "param3" )
		self._patternDict["p4"] = extSection.readString( "param4" )
		self._patternDict["p5"] = extSection.readString( "param5" )
		self._patternDict["p6"] = extSection.readString( "param6" )
		self._patternDict["p7"] = extSection.readString( "param7" )
		self._patternDict["p8"] = extSection.readString( "param8" )
		self._patternDict["p9"] = extSection.readString( "param9" )
		self._patternDict["p10"] = extSection.readString( "param10" )
		self._patternDict["p11"] = extSection.readString( "param11" )
		self._patternDict["p12"] = extSection.readString( "param12" )
		self._patternDict["p13"] = extSection.readString( "param13" )
		self._patternDict["p14"] = extSection.readString( "param14" )

		self.addToQuestBox()

	def getGroupQuest( self ):
		"""
		获得组任务
		"""
		return Love3.g_taskData[self._group_id]

	def getGroupID( self ):
		"""
		获得组任务ID
		"""
		return self._group_id


	def getPatternType( self ):
		"""
		获得自身任务模式类型
		"""
		return self._patternType


	def addToQuestBox( self ):
		"""
		处理任务箱子
		"""
		QuestBoxsDict = self.getQuestBoxsDict()
		for QuestBoxID in QuestBoxsDict:
			QuestBoxNpc = g_objFactory.getObject( QuestBoxID )
			if not QuestBoxNpc:
				ERROR_MSG( self.getID(), "QuestBox not found.", QuestBoxID )
			else:
				index = QuestBoxsDict[ QuestBoxID ]
				QuestBoxNpc.addQuestTask( self._group_id, index ) #任务箱子和组任务ID绑定

	def complete( self, player, rewardIndex, codeStr = "" ):
		"""
		"""
		#player.setTemp( "questKitTote", kitTote )
		#player.setTemp( "questOrder", order )
		self.setDecodeTemp( player, codeStr )
		player.setTemp( "questTeam", True )

		if not self.query( player ) == csdefine.QUEST_STATE_FINISH:
			#player.removeTemp( "questKitTote" )
			#player.removeTemp( "questOrder" )
			self.removeDecodeTemp( player, codeStr )
			player.removeTemp( "questTeam")
			return False

		player.setTemp( "RewardItemChoose" , rewardIndex )
		if not self.reward_( player, rewardIndex ):
			#player.removeTemp( "questKitTote" )
			#player.removeTemp( "questOrder" )
			self.removeDecodeTemp( player, codeStr )
			player.removeTemp( "questTeam")
			return False

		for e in self.afterComplete_:
			e.do( player )

		player.addSubQuestCount( self._group_id, 1 )
		player.addGroupPoint( self._group_id, self._point )
		questTitle = player.getQuest( self._group_id )._title

		#提示任务积分
		#player.statusMessage( csstatus.ROLE_QUEST_RANDON_POINT, self._point )
		player.removeTemp( "RewardItemChoose" )
		#player.removeTemp( "questKitTote" )
		#player.removeTemp( "questOrder" )
		#self.removeDecodeTemp( player, codeStr )
		player.removeTemp( "questTeam")
		player.statusMessage( csstatus.ROLE_QUEST_COMPLETE, questTitle )
		return True

	def query( self, player ):
		"""
		查询玩家完成该任务的情况，对于子任务的查询，都反馈为父任务的情况。
		"""
		return self.getGroupQuest().query( player )

	def fitPlayer( self, player ):
		"""
		判断这个任务是否适合玩家
		@rtype  section: bool
		"""
		return ( player.level >= self._level - self._minus_interval ) and ( player.level <= self._level + self._positive_interval )

	def getParamsDict( self ):
		"""
		"""
		return self._patternDict

	def setDecodeTemp( self, player, codeStr ):
		"""
		设置编码字符串临时变量
		"""
		for task in player.questsTable[self.getGroupID()].getTasks().itervalues():
			task.setPlayerTemp( player, codeStr )


	def removeDecodeTemp( self, player, codeStr ):
		"""
		删除编码字符串临时变量
		"""
		for task in player.questsTable[self.getGroupID()].getTasks().itervalues():
			task.removePlayerTemp( player )

	def getRewardsDetail( self, player ):
		"""
		获得奖励描述细节
		"""
		r = []
		for reward in self.rewards_:
			if reward.type() == csdefine.QUEST_REWARD_RANDOM_ITEMS:		# rewards_中如果有这种类型的奖励会出错，先屏蔽掉。其他任务类型也有这个问题，但因为目前没有配置，先不处理 by cwl
				continue
			r.append( reward.transferForClient( player, self.getGroupID() ) )
		if self.rewardsFixedItem_:
			r.append( self.rewardsFixedItem_.transferForClient( player, self.getGroupID() ) )
		if self.rewardsChooseItem_:
			r.append( self.rewardsChooseItem_.transferForClient( player, self.getGroupID() ) )
		# 策划说随机奖励不显示出来给玩家看，但为防止以后又要要求显示，所以要保留
		#if self.rewardsRandItem_:
		#	r.append( self.rewardsRandItem_.transferForClient( player, self.getGroupID() ) )
		return r

# $Log: not supported by cvs2svn $
# Revision 1.11  2008/07/31 09:24:08  zhangyuxing
# 修改一处命名错误
#
# Revision 1.10  2008/07/30 05:54:16  zhangyuxing
# getGroupQuestDegree 改名为： getGroupCount
# getGroupQuestCount  改名为： getSubQuestCount
#
# Revision 1.9  2008/07/28 01:11:14  zhangyuxing
# 修改通知任务完成的顺序
#
# Revision 1.8  2008/01/22 08:18:41  zhangyuxing
# 增加：扩展了模式的参数数目
#
# Revision 1.7  2008/01/11 06:51:43  zhangyuxing
# 增加任务样式 self._style
#
# Revision 1.6  2008/01/09 03:23:16  zhangyuxing
# 从新处理了随机子任务的所有方法和功能。
#
# Revision 1.5  2007/11/02 03:57:03  phw
# QuestTasksDataType -> QuestDataType
#
# Revision 1.4  2007/06/19 08:46:46  huangyongwei
# 任务状态的定义由原来的 csstatus 中转换到 csdefine 中
#
# Revision 1.3  2007/06/14 09:59:20  huangyongwei
# 重新整理了宏定义
#
# Revision 1.2  2007/05/05 08:19:51  phw
# model removed: whrandom
#
# Revision 1.1  2006/03/27 07:39:26  phw
# no message
#
#