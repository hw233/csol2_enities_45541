# -*- coding: gb18030 -*-
#
# $Id: QuestsDataType.py,v 1.25 2008-08-20 01:27:24 zhangyuxing Exp $

"""
用于玩家身上，保存所有的任务列表和当前完成状态。
实现自定义数据类型接口，解决传输问题。
"""

import csstatus
import csdefine
from bwdebug import *
import struct
import Language

class QuestsDataType:
	def __init__( self ):
		self._quests = {}		# key == questID, value == instance of QuestDataType

	def __getitem__( self, questID ):
		return self._quests[questID]

	def __len__( self ):
		return len( self._quests )

	def iteritems( self ):
		return self._quests.iteritems()

	def has_quest( self, questID ):
		"""
		判断是否有指定的quest

		@return: BOOL
		"""
		return questID in self._quests

	def keys( self ) :
		"""
		获取所有任务 ID（ hyw -- 2008.06.10 ）
		"""
		return self._quests.keys()

	def items( self ) :
		"""
		获取所有任务（ hyw -- 2008.06.10 ）
		"""
		return self._quests.items()

	def add( self, questID, tasks ):
		"""
		加入一个任务

		@param tasks: 任务目标列表
		@type  tasks: QuestDataType
		@return: None
		"""
		self._quests[questID] = tasks

	def remove( self, questID ):
		"""
		删除一个任务
		"""
		try:
			del self._quests[questID]
		except KeyError:
			ERROR_MSG( "quest not found, questID =", questID )

	def query( self, questID, key, default = None ):
		"""
		查询扩展数据

		@return: 如果关键字不存在则返回default值
		"""
		tasks = self._quests[questID]
		return tasks.query( key, default = None )

	def set( self, questID, key, value ):
		"""
		写入扩展数据

		@param   key: 任何PYTHON原类型(建议使用字符串)
		@param value: 任何PYTHON原类型(建议使用数字或字符串)
		"""
		tasks = self._quests[questID]
		tasks.set( key, value )

	def addAnswerQuestion( self, player, isRight ):
		"""
		"""
		resultTuple = []
		
		for questID, quest in self._quests.iteritems():
			index, val, index2, val2 = quest.addAnswerQuestion( player, isRight )
			if index != -1:
				resultTuple.append( (questID, index, val) )
			if index2 != -1:
				resultTuple.append( (questID, index2, val2) )
		return resultTuple

	def addNormalAnswerQuestion( self, player, questionType, isRight ):
		"""
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.addNormalAnswerQuestion( player,questionType, isRight )
			if index != -1:
				resultList.append( (questID, index) )
		return resultList




	def increaseKilled( self, player, monsterEntity ):
		"""
		在任务里查找一个与npcID相对应的任务目标并给杀死数量增加1

		@return: 如果在任务目标中找到了相关的NPC标识则返回(questID, taskIndex)，否则返回None
		@rtype:  None/Tuple
		"""
		resultList = []
		
		for questID, quest in self._quests.iteritems():
			index = quest.increaseKilled( player, monsterEntity )
			if index != -1:
				resultList.append( (questID, index) )
		return resultList
		
	def increaseDartKilled( self, player, dartQuestID, factionID ):
		"""
		在任务里查找一个与npcID相对应的任务目标并给杀死数量增加1

		@return: 如果在任务目标中找到了相关的NPC标识则返回(questID, taskIndex)，否则返回None
		@rtype:  None/Tuple
		"""
		resultList = []
		
		for questID, quest in self._quests.iteritems():
			if quest.getType() == csdefine.QUEST_TYPE_ROB:		# 劫镖任务成功需要移去玩家身上的劫镖标记
				if player.hasFlag( csdefine.ROLE_FLAG_CP_ROBBING ):
					player.removeFlag( csdefine.ROLE_FLAG_CP_ROBBING )
				else:
					player.removeFlag( csdefine.ROLE_FLAG_XL_ROBBING )
			index = quest.increaseDartKilled( player, dartQuestID, factionID )
			if index != -1:
				resultList.append( (questID, index) )
		return resultList
		
	def updatePetActState( self, player, isActive ):
		"""
		在任务里查找一个宠物的激活状态发生改变的任务目标通知其是否完成目标
		@return: 如果在任务目标中找到了相关的NPC标识则返回(questID, taskIndex)，否则返回None
		@rtype:  None/Tuple
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.updatePetActState( player, isActive )
			if index != -1:
				resultList.append( (questID, index) )
		return resultList
		
	def increaseEvolution( self, player, className ):
		"""
		在任务里查找一个与npcID相对应的任务目标并给进化数量增加1

		@return: 如果在任务目标中找到了相关的NPC标识则返回(questID, taskIndex)，否则返回None
		@rtype:  None/Tuple
		"""
		resultList = []
		
		for questID, quest in self._quests.iteritems():
			index = quest.increaseEvolution( player, className )
			if index != -1:
				resultList.append( (questID, index) )
		return resultList
		
	def roleDieAffectQuest( self, player ):
		"""
		在任务里查找会因角色死亡而受影响的任务目标

		@return: 如果在任务目标中找到了需要受影响的任务目标则返回(questID, taskIndex)，否则返回None
		@rtype:  None/Tuple
		"""
		resultList = []
		
		for questID, quest in self._quests.iteritems():
			index = quest.roleDieAffectQuest( player )
			if index != -1:
				resultList.append( (questID, index) )
		return resultList

	def addDeliverAmount( self, player, item, quantity ):
		"""
		为一个递送物品的目标增加数量（负数则为减少）

		@return: 如果在任务目标中找到了相关的物品标识则返回(questID, taskIndex)，否则返回None
		@rtype:  None/Tuple
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.addDeliverAmount( player, item, quantity ) #index 改为了任务达成目标的索引
			if index != -1:
				resultList.append( (questID, index) )
		return resultList

	def addYinpiaoDeliverAmount( self, player, item ):
		"""
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.addYinpiaoDeliverAmount( player, item ) #index 改为了任务达成目标的索引
			if index != -1:
				resultList.append( (questID, index) )
		return resultList
		

	def addPetEvent( self, player, eventType ):
		"""
		宠物事件触发
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.addPetEvent( player, eventType ) #index 改为了任务达成目标的索引
			if index != -1:
				resultList.append( (questID, index) )
		return resultList



	def addDeliverPetAmount( self, player, className, dbid ):
		"""
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.addDeliverPetAmount( player, className, dbid )
			if index != -1:
				resultList.append( (questID, index) )
		return resultList
		
	def subDeliverPetAmount( self, player, className, dbid ):
		"""
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.subDeliverPetAmount( player, className, dbid )
			if index != -1:
				resultList.append( (questID, index) )
		return resultList

	def increaseLevel( self, level ):
		"""
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.increaseLevel( level ) #index
			if index != -1:
				resultList.append( (questID, index) ) 
		return resultList

	def increaseSkillLearned( self, player, skillID ):
		"""
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.increaseSkillLearned( player, skillID ) #index
			if index != -1:
				resultList.append( (questID, index) ) 
		return resultList
	
	def increaseLivingSkillLearned( self, player, skillID ):
		"""
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.increaseLivingSkillLearned( player, skillID ) #index
			if index != -1:
				resultList.append( (questID, index) ) 
		return resultList

	def increaseSkillUsed( self, player, skillID, className ):
		"""
		使用某技能
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.increaseSkillUsed( player, skillID, className )
			if index != -1 and index != None:
				resultList.append( (questID, index) )
		return resultList


	def questFinish( self, finishQuestID ):
		"""
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.questFinish( finishQuestID ) #index
			if index != -1:
				resultList.append( (questID, index) ) 
		return resultList

	def addPetAmount( self, player, quantity ):
		"""
		宠物数量变化处理
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.addPetAmount( player, quantity ) #index 改为了任务达成目标的索引
			if index != -1:
				resultList.append( (questID, index) ) 
		return resultList

	def clearTeamAmount( self, player ):
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.clearTeamAmount( player )
			if index != -1:
				resultList.append( (questID, index) ) 
		return resultList

	def increaseItemUsed( self, player, itemID ):
		"""
		为一个使用物品的任务目标增加一个使用数量。

		@return: 如果在指定的任务目标中找到了与itemID相关的task则返回这个task在任务中的索引位置，否则返回-1
		@rtype:  int
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.increaseItemUsed( player, itemID )
			if index != -1 and index != None:	# index有可能为None -spf
				resultList.append( (questID, index) )
		return resultList


	def addTalk( self, player, targetClassName ):
		"""
		和指定NPC对话，完成任务。
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.addTalk( player, targetClassName )
			if index != -1:
				resultList.append( (questID, index) )
		return resultList
		
	
	def updateBuffState( self, buffID, val ):
		"""
		在任务里查找一个与npcID相对应的任务目标并给进化数量增加1

		@return: 如果在任务目标中找到了相关的NPC标识则返回(questID, taskIndex)，否则返回None
		@rtype:  None/Tuple
		"""
		resultList = []
		
		for questID, quest in self._quests.iteritems():
			index = quest.updateBuffState( buffID, val )
			if index != -1:
				resultList.append( (questID, index) )
		return resultList


	def getReadQuestID( self ):
		"""
		取得真正的物品掉落关联ID列表。以及子任务和父任务关联字典

		@return type :  such as " ( [...], {...} ) "
		"""
		tempIDList = []
		tempIDDict = {}
		for id in self._quests:
			tempID = id
			tempTask = self._quests[id]
			if tempTask.query("style") in [ csdefine.QUEST_STYLE_RANDOM_GROUP,  csdefine.QUEST_STYLE_LOOP_GROUP ]:
				tempID = tempTask.query("subQuestID")
				tempIDDict[tempID] = id
			tempIDList.append( tempID )

		return ( tempIDList, tempIDDict )

	def handleDartFailed( self, player ):
		resultList = []
		for questID, quest in self._quests.iteritems():
			if quest.getType() == csdefine.QUEST_TYPE_DART or quest.getType() == csdefine.QUEST_TYPE_MEMBER_DART:
				if player.hasFlag( csdefine.ROLE_FLAG_XL_DARTING ):
					player.removeFlag( csdefine.ROLE_FLAG_XL_DARTING )
				else:
					player.removeFlag( csdefine.ROLE_FLAG_CP_DARTING )
				index = quest.handleDartFailed() #index
				if index != -1:
					resultList.append( (questID, index) ) 
		return resultList
		

	def addPotentialFinish( self, player ):
		"""
		宠物事件触发
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.addPotentialFinish( player ) #index 改为了任务达成目标的索引
			if index != -1:
				resultList.append( (questID, index) )
		return resultList


	def getQuestionCount( self, questionType ):
		"""
		答题任务：
			获得剩余提述数量
		"""
		count = -1
		for questID, quest in self._quests.iteritems():
			count = quest.getQuestionCount( questionType )
			if count != -1:
				return count
		return count


	def updateSetRevivePos( self, player, spaceName ):
		"""
		设置绑定点触发
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.updateSetRevivePos( player, spaceName )
			if index != -1 and index != None:
				resultList.append( (questID, index) )
		return resultList

	def enterNewSpaceTrigger( self, player, spaceLabel ):
		"""
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.getIndexEnterSpace( player, spaceLabel )
			if index != -1 and index != None:
				resultList.append( (questID, index) )
		return resultList
		
	def onChangeCampMorale( self, player, camp, amount ):
		"""
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.onChangeCampMorale( player, camp, amount )
			if index != -1 and index != None:
				resultList.append( (questID, index) )
		return resultList
	
	def increaseVehicleActived( self, player, VehicleID ):
		"""
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.increaseVehicleActived( player, VehicleID )
			if index != -1 and index != None:
				resultList.append( (questID, index) )
		return resultList
		
		
	##################################################################
	# BigWorld User Defined Type 的接口                              #
	##################################################################
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.

		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		items = []
		d = { "values":items }
		for k, v in obj._quests.iteritems():
			items.append( v )
		return d

	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.

		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = QuestsDataType()
		for value in dict["values"]:
			if value:	# 如果value为None则表示数据有错，将会直接忽略
				obj._quests[value.getQuestID()] = value
		return obj

	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, QuestsDataType )

instance = QuestsDataType()


#
# $Log: not supported by cvs2svn $
# Revision 1.24  2008/08/07 09:04:20  zhangyuxing
# 对宠物数量类型变化进行支持
#
# Revision 1.23  2008/07/31 09:27:33  zhangyuxing
# no message
#
# Revision 1.22  2008/07/28 01:08:56  zhangyuxing
# 增加等级任务目标
#
# Revision 1.21  2008/07/14 04:36:52  zhangyuxing
# 加入等级变化，任务完成查询
#
# Revision 1.20  2008/06/10 09:00:45  huangyongwei
# 添加了：
# keys()
# 和
# items()
# 方法
#
# Revision 1.19  2008/01/31 03:12:14  zhangyuxing
# 怪物掉落物品兼顾随机任务的处理
#
# Revision 1.18  2008/01/22 08:20:44  zhangyuxing
# 增加了宠物数目变化的处理
#
# Revision 1.17  2008/01/11 06:59:24  zhangyuxing
# 杀怪任务的刷新返回为列表
#
# Revision 1.16  2008/01/09 04:05:29  zhangyuxing
# 增加组队任务目标的相关操作
#
# Revision 1.15  2007/12/17 11:37:03  zhangyuxing
# 调整： addDeliverAmount 的参数 调整
#
# Revision 1.14  2007/12/08 09:33:21  phw
# 针对坏数据进行了处理，如果QuestData实例为None则认为是坏数据，忽略掉该数据
#
# Revision 1.13  2007/12/05 00:35:26  zhangyuxing
# 在任务状态发生变化的检测中：
# 遍里任务达成目标的方式被修改。而且返回也直接返回达成目标的key.
#
# Revision 1.12  2007/11/02 05:59:33  phw
# 修正了import不存在的 QuestTasksDataType 的问题
#
# Revision 1.11  2007/11/02 03:37:52  phw
# method removed: has_deliver(), has_kill()
# method removed: questIncreaseItemUsed() -> increaseItemUsed()
#
# Revision 1.10  2007/06/14 10:46:50  huangyongwei
# 整理了全局变量
#
# Revision 1.9  2007/03/07 02:29:58  kebiao
# 修改了使用FIXED_DICT类型
#
# Revision 1.8  2006/10/13 08:35:55  chenzheming
# 修改怪物死的时候调用increaseKilled函数所传的参数
#
# Revision 1.7  2006/09/07 07:18:00  chenzheming
# no message
#
# Revision 1.6  2006/03/28 09:03:52  phw
# 增加increaseActiveItem()
#
# Revision 1.5  2006/03/22 02:34:02  phw
# 适应1.7版的自定义类型，作相应修改
#
# Revision 1.4  2006/03/20 03:18:54  wanhaipeng
# Mark stream.将来要改对！！！
#
# Revision 1.3  2006/03/16 07:09:23  wanhaipeng
# Change bind Format.
#
# Revision 1.2  2006/03/02 10:04:57  phw
# no message
#
# Revision 1.1  2006/01/24 02:31:33  phw
# no message
#
#
