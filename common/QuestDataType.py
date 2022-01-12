# -*- coding: gb18030 -*-
#
# $Id: QuestDataType.py,v 1.22 2008/08/20 01:27:24 zhangyuxing Exp $

"""
任务目标管理器，一个实例就对应一个任务目标。
实现自定义数据类型接口，解决传输问题。
"""

import Language
from bwdebug import *
import struct
import csdefine
import csconst
import QuestTaskDataType
import BigWorld
import time
import csstatus

class QuestDataType:
	def __init__( self ):
		self._questID = 0	# quest id
		self._tasks = {}	# DICT of QuestTaskDataType(QTTask)
		self._datas = {}	# extend data
		self._acceptTime = int( time.time() )

#	def __getitem__( self, index ):
#		return self._tasks[index]

	def getQuestID( self ):
		"""
		"""
		return self._questID

	def setQuestID( self, questID ):
		"""
		"""
		self._questID = questID

	def getType( self ):
		"""
		获得任务类型
		"""
		if not self._datas.has_key( "type" ):
			return csdefine.QUEST_TYPE_NONE
		return self._datas["type"]

	def getStyle( self ):
		"""
		获得任务类型
		"""
		if not self._datas.has_key( "style" ):
			return csdefine.QUEST_TYPE_NONE
		return self._datas["style"]


	def getTasks( self ):
		"""
		获得任务列表
		"""
		return self._tasks

	def setTasks( self, taskDict ):
		"""
		设置任务列表
		"""
		self._tasks = taskDict

	def getAcceptTime( self ):
		"""
		返回任务接受的时间
		"""
		return self._acceptTime

	def query( self, key, default = None ):
		"""
		查询扩展数据

		@return: 如果关键字不存在则返回default值
		"""
		try:
			return self._datas[key]
		except KeyError:
			return default

	def set( self, key, value ):
		"""
		写入扩展数据

		@param   key: 任何PYTHON原类型(建议使用字符串)
		@param value: 任何PYTHON原类型(建议使用数字或字符串)
		"""
		self._datas[key] = value

	def isCompleted( self, player ):
		"""
		查询是否所有任务目标都已达到
		"""
		for i in self._tasks:
			if not self._tasks[i].isCompleted( player ):
				return False
		return True


	def isCompletedForNoStart( self, player ):
		"""
		查询是否所有任务目标都已达到
		"""
		for i in self._tasks:
			if not self._tasks[i].isCompletedForNoStart( player ):
				return False
		return True


	def complete( self, player ):
		"""
		完成任务，进行一些后续动作
		"""
		for i in self._tasks:
			self._tasks[i].complete( player )

	def deliverIsComplete( self, itemID, player ):
		"""
		检查相关的物品是否已收集完成

		@param itemID: 物品标识符
		@type  itemID: STRING
		@param player: 玩家实体
		@type  player: Role Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_DELIVER and self._tasks[i].getDeliverID() == itemID:
				return self._tasks[i].isCompleted( player )

			if self._tasks[i].getType() in csconst.QUEST_OBJECTIVE_SUBMIT_TYPES and self._tasks[i].getSubmitID() == itemID:
				return self._tasks[i].isCompleted( player )
			
			# 阵营活动收集任务:要收集指定地图的物品,否则认为已完成
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_CAMPACT_DELIVER and self._tasks[i].isValidSpace( player) and self._tasks[i].getDeliverID() == itemID:
				return self._tasks[i].isCompleted( player )

		ERROR_MSG( "quest not in need of %s." % itemID )
		return True	# 如果该目标中没有同类的物品收集则认为已完成，会出现这种情况是因为怪物数据填写错误

	def increaseKilled( self, player, monsterEntity ):
		"""
		在任务里查找一个与npcID相对应的任务目标并给杀死数量增加1

		@return: 如果在任务目标中找到了相关的NPC标识则返回taskIndex，否则返回-1
		@rtype:  INT
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_KILL and self._tasks[i].getKilledName() == monsterEntity.className:
				if self._tasks[i].add( player, 1 ):
					return i		# 查找第一次找到的
				else:
					return -1
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_KILL_WITH_PET and self._tasks[i].getKilledName() == monsterEntity.className:
				if self._tasks[i].add( player, 1 ):
					return i		# 查找第一次找到的
				else:
					return -1
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_KILLS and monsterEntity.className in self._tasks[i].getKilledName():
				if self._tasks[i].add( player, 1 ):
					return i		# 查找第一次找到的
				else:
					return -1
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_CAMP_KILL and monsterEntity.className in self._tasks[i].getKilledName():
				if self._tasks[i].add( player, 1 ):
					return i		# 查找第一次找到的
				else:
					return -1
		return -1


	def increaseDartKilled( self, player, dartQuestID, factionID ):
		"""
		在任务里查找一个与npcID相对应的任务目标并给杀死数量增加1

		@return: 如果在任务目标中找到了相关的NPC标识则返回taskIndex，否则返回-1
		@rtype:  INT
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_DART_KILL and self.getType() == csdefine.QUEST_TYPE_ROB:
				#如果是劫镖任务者杀死镖车
				if factionID and self._tasks[i].getFaction() != int( factionID ):
					return -1
				if self._tasks[i].add( player, dartQuestID, 1 ):
					return i		# 查找第一次找到的
				else:
					return -1
		return -1


	def addAnswerQuestion( self, player, isRight ):
		"""
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_IMPERIAL_EXAMINATION :
				if self._tasks[i].add( player, 1, isRight ):
					m = -1
					n = -1
					for t in self._tasks:
						if self._tasks[t].getType() == csdefine.QUEST_OBJECTIVE_SHOW_KAOGUAN :
							self._tasks[t].add( player, 1 )
							m = t
							n = self._tasks[t].val1
							break
					j = self._tasks[i].val1
					return i,j,m,n		# 包含任务目标INDEX 和 完成次数
				else:
					return -1,-1,-1,-1

		return -1, -1, -1, -1


	def addNormalAnswerQuestion( self, player, questionType, isRight ):
		"""
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_QUESTION:
				if self._tasks[i].add( player, questionType, isRight ): return i		# 查找第一次找到的
				else:             return -1
		return -1

	def getQuestionCount( self, questionType ):
		"""
		答题任务：
			获得已答题的数量
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_QUESTION:
				if self._tasks[i].str1 == str( questionType ):
					return self._tasks[i].val2 - self._tasks[i].val1
		return -1

	def increaseEvolution( self, player, className ):
		"""
		在任务里查找一个与npcID相对应的任务目标并给进化数量增加1

		@return: 如果在任务目标中找到了相关的NPC标识则返回taskIndex，否则返回-1
		@rtype:  INT
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_EVOLUTION and self._tasks[i].getEvolutClassName() == className:
				if self._tasks[i].add( player, 1 ):
					return i		# 查找第一次找到的
				else:
					return -1
		return -1

	def updateBuffState( self, buffID, val ):
		"""
		在任务里查找一个与npcID相对应的任务目标并给进化数量增加1

		@return: 如果在任务目标中找到了相关的NPC标识则返回taskIndex，否则返回-1
		@rtype:  INT
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_HASBUFF and self._tasks[i].getBuffID() == buffID:
				if self._tasks[i].add( buffID, val ):
					return i		# 查找第一次找到的
				else:
					return -1
		return -1

	def updatePetActState( self, player, isActive ):
		"""
		在任务里查找一个宠物的激活状态发生改变的任务目标通知其+1或者-1

		@return: 如果在任务目标中找到了相关的NPC标识则返回taskIndex，否则返回-1
		@rtype:  INT
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_PET_ACT:
				addNumber = isActive and 1 or -1
				if self._tasks[i].add( player, addNumber ):
					return i		# 查找第一次找到的
				else:
					return -1
		return -1

	def roleDieAffectQuest( self, player ):
		"""
		在任务里查找会因角色死亡而受影响的任务目标

		@return: 如果在任务目标中找到了需要受影响的任务目标则返回taskIndex，否则返回-1
		@rtype:  INT
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_TIME and self.getType() == csdefine.QUEST_TYPE_ROB and not player.isRobbingComplete():
				if self._tasks[i].isCompleted( player ):	# 如果没有超时
					player.statusMessage( csstatus.ROLE_QUEST_ROBBING_DIE )
				if player.hasFlag( csdefine.ROLE_FLAG_CP_ROBBING ):
					player.removeFlag( csdefine.ROLE_FLAG_CP_ROBBING )
				else:
					player.removeFlag( csdefine.ROLE_FLAG_XL_ROBBING )
				#如果是劫镖任务的时间目标
				if self._tasks[i].setFailed():
					#设置任务失败（即设置时间用完）
					return i	# 查找第一次找到的
				else:
					return -1
		return -1

	def addPetEvent( self, player, eventType ):
		"""
		在任务里查找一个与npcID相对应的任务目标并给杀死数量增加1

		@return: 如果在任务目标中找到了相关的NPC标识则返回taskIndex，否则返回-1
		@rtype:  INT
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_PET_EVENT and self._tasks[i].getEventType() == eventType :
				if self._tasks[i].add( 1 ): return i		# 查找第一次找到的
				else:             return -1
		return -1

	def handleDartFailed( self ):
		"""
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_TIME:
				if self._tasks[i].setFailed(): return i		# 查找第一次找到的
				else:             return -1
		return -1


	def increaseLevel( self, level ):
		"""
		等级变化
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_LEVEL:
				if self._tasks[i].setLevel( level ): return i		# 查找第一次找到的
				else:             return -1
		return -1


	def increaseSkillLearned( self, player, skillID ):
		"""
		等级变化
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_SKILL_LEARNED:
				if self._tasks[i].isCompleted( player ):continue
				if self._tasks[i].add( player, skillID ): return i		# 查找第一次找到的
		return -1
	
	
	def increaseLivingSkillLearned( self, player, skillID ):
		"""
		等级变化
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_LIVING_SKILL_LEARNED:
				if self._tasks[i].add( player, skillID ): 
					return i		# 查找第一次找到的
				else:
					return -1
		return -1


	def questFinish( self, questID ):
		"""
		任务完成
		"""
		for i in self._tasks:
			if self._tasks[i].getType() in [csdefine.QUEST_OBJECTIVE_QUEST, csdefine.QUEST_OBJECTIVE_QUEST_NORMAL]:
				if self._tasks[i].setQuestFinish( questID ): return i		# 查找第一次找到的
				else:             return -1
		return -1

	def addDeliverAmount( self, player, item, quantity ):
		"""
		为一个递送物品的目标增加数量（负数则为减少）

		@return: 如果在指定的任务目标中找到了与item.id相关的task则返回这个task在任务中的索引位置，否则返回-1
		@rtype:  INT
		"""
		for i in  self._tasks:
			if self._tasks[i].getType() in [ csdefine.QUEST_OBJECTIVE_DELIVER, csdefine.QUEST_OBJECTIVE_CAMPACT_DELIVER ] and self._tasks[i].getDeliverID() == item.id:
				if self._tasks[i].add( player, quantity ): return i		# 返回该任务达成目标索引
				else:                    return -1

			if	self._tasks[i].getType() in csconst.QUEST_OBJECTIVE_SUBMIT_TYPES and self._tasks[i].isFitProperty( item ):
				if self._tasks[i].add( player, quantity ): return i
				else:					return -1

			if	self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_SUBMIT_PICTURE and \
				self._tasks[i].getDeliverID() == item.id and \
				item.query("pictureTargetID", -1) == self._tasks[i].getNPCClassName():
				if self._tasks[i].add( player, quantity ): return i
				else:					return -1

			if	self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_SUBMIT_CHANGE_BODY and \
				self._tasks[i].getDeliverID() == item.id and \
				item.query("changeBodyTargetID", -1) == self._tasks[i].getNPCClassName():
				if self._tasks[i].add( player, quantity ): return i
				else:					return -1

			if	self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_SUBMIT_DANCE and \
				self._tasks[i].getDeliverID() == item.id and \
				item.query("danceTargetID", -1) == self._tasks[i].getNPCClassName():
				if self._tasks[i].add( player, quantity ): return i
				else:					return -1

			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_DELIVER_QUALITY and self._tasks[i].isFitProperty( item ):
				if self._tasks[i].add( player, quantity ): return i
				else:                    return -1
		return -1


	def addYinpiaoDeliverAmount( self, player, item ):
		"""
		"""
		for i in  self._tasks:
			if	self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_SUBMIT_YINPIAO:
				if self._tasks[i].isFitProperty( item ):
					if self._tasks[i].add( player, 1 ):
						return i
					else:
						return -1
				else:
					if self._tasks[i].add( player, -1 ):
						return i
					else:
						return -1
		return -1


	def addDeliverPetAmount( self, player, className, dbid ):
		"""
		"""
		for i in  self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_DELIVER_PET and self._tasks[i].getDeliverPetID() == className:
				if self._tasks[i].addPet( player, self.getQuestID(), dbid ): return i		# 返回该任务达成目标索引
				else:                    return -1
		return -1

	def subDeliverPetAmount( self, player, className, dbid ):
		"""
		"""
		for i in  self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_DELIVER_PET and self._tasks[i].getDeliverPetID() == className:
				if self._tasks[i].subPet( player, self.getQuestID(), dbid ): return i		# 返回该任务达成目标索引
				else:                    return -1
		return -1


	def addPetAmount( self, player, quantity ):
		"""
		"""
		for i in  self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_OWN_PET :
				if self._tasks[i].add( player, quantity ): return i		# 返回该任务达成目标索引
				else:                    return -1
		return -1

	def clearTeamAmount( self, player ):

		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_TEAM:
				if self._tasks[i].clean( player ): return i		# 返回该任务达成目标索引
				else:                    return -1


	def increaseItemUsed( self, player, itemID ):
		"""
		为一个使用物品的任务目标增加一个使用数量。

		@return: 如果在指定的任务目标中找到了与itemID相关的task则返回这个task在任务中的索引位置，否则返回-1
		@rtype:  INT
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_EVENT_USE_ITEM and self._tasks[i].getItemID() == itemID:
				if self._tasks[i].add( player, 1 ):
					return i		# 查找第一次找到的
				else:
					return -1
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_CAMPACT_EVENT_USE_ITEM and self._tasks[i].isValidSpace( player ) and self._tasks[i].getItemID() == itemID:
				if self._tasks[i].add( player, 1 ):
					return i		# 查找第一次找到的
				else:
					return -1
		return -1


	def addTalk( self, player, className ):
		"""
		"""
		for i in self._tasks:
			if self._tasks[i].getType() in [ csdefine.QUEST_OBJECTIVE_TALK, csdefine.QUEST_OBJECTIVE_CAMPACT_TALK ] and self._tasks[i].getClassName() == className:
				if self._tasks[i].add( player, 1 ):
					return i		# 查找第一次找到的
				else:
					return -1
		return -1


	def isIndexTaskComplete( self, player, index):
		"""
		根据taskID(索引）取的某个子目标的完成情况
		"""
		if self._tasks.has_key( index ):
			try:
				return self._tasks[index].isCompleted(player)
			except KeyError, errstr:
				raise KeyError, "quest %i has no task index %i." % (self._questID, index)
		else:
			return False

	def getSubmitInfo( self ):			#关于物品提交的信息，由服务器提供
		"""
		查询提交任务目标的提交信息
		"""
		for task in self._tasks.itervalues():
			if task.getType() == csdefine.QUEST_OBJECTIVE_SUBMIT:
				return ( task.getItem(), task.getQuality() )
		return None

	def getObjectiveDetail( self, player ):
		"""
		获得任务目标描述
		"""
		return [ task.getDetail( player ) for task in self._tasks.itervalues() ]

	def getIERightRate( self, obj ):
		"""
		获得科举答题的正确率
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_IMPERIAL_EXAMINATION:
				return self._tasks[i].float( self._tasks[i].str1 ) / self._tasks[i].val2
		return 0.0


	def addPotentialFinish( self, player ):
		"""
		完成一次潜能任务。

		@return: 如果在任务目标中找到了相关的NPC标识则返回taskIndex，否则返回-1
		@rtype:  INT
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_POTENTIAL_FINISH:
				if self._tasks[i].add( 1 ): return i		# 查找第一次找到的
				else:             return -1
		return -1


	def increaseSkillUsed( self, player, skillID, className ):
		"""
		使用某技能
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_EVENT_USE_SKILL and self._tasks[i].getSkillID() == skillID and ( className == self._tasks[i].getClassName() or self._tasks[i].getClassName() == ""):
				if self._tasks[i].add( player, 1 ):
					return i		# 查找第一次找到的
				else:
					return -1
		return -1


	def updateSetRevivePos( self, player, spaceName ):
		"""
		设置绑定点触发
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_EVENT_REVIVE_POS and spaceName == self._tasks[i].getSpaceName():
				if self._tasks[i].add( player, 1 ):
					return i		# 查找第一次找到的
				else:
					return -1
		return -1

	def getIndexEnterSpace( self, player, spaceLabel ):
		"""
		"""
		for i in self._tasks:
			task = self._tasks[i]
			if task.getType() == csdefine.QUEST_OBJECTIVE_ENTER_SPCACE and spaceLabel == task.getNeedSpaceLabel():
				if task.arrived():
					return i		# 查找第一次找到的
				else:
					return -1
		return -1

	def onChangeCampMorale( self, player, camp, amount ):
		"""
		增加或减少阵营士气
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_ADD_CAMP_MORALE:
				if self._tasks[i].add( player, camp, amount ):
					return i		# 查找第一次找到的
				else:
					return -1
		return -1
	
	def increaseVehicleActived( self, player, vehicleID ):
		"""
		骑宠激活
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_VEHICLE_ACTIVED:
				if self._tasks[i].add( player, vehicleID ):
					return i		# 查找第一次找到的
				else:
					return -1
		return -1
		
	##################################################################
	# BigWorld User Defined Type 的接口                              #
	##################################################################
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.

		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		return getDictFromObj(obj)

	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.

		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		return createObjFromDict(dict)

	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		if obj is None:
			return True
		return isinstance( obj, QuestDataType )

instance = QuestDataType()

if BigWorld.component in [ "db", "base" ]:
	def createObjFromDict( dict ):
		obj = QuestDataType()
		obj._questID = dict["qID"]
		obj._datas = dict["datas"]
		obj._tasks = dict["tasks"]
		obj._acceptTime = dict["acceptTime"]
		return obj

	def getDictFromObj( obj ):
		return { "qID":obj._questID, "datas":obj._datas, "tasks":obj._tasks, "acceptTime" : obj._acceptTime }
else:
	def createObjFromDict( dict ):
		if dict["qID"] <= 0:
			return None

		obj = QuestDataType()
		try:
			obj._questID = dict["qID"]
			obj._datas = dict["datas"]
			obj._acceptTime = dict["acceptTime"]
			for value in dict["tasks"]:
				obj._tasks[value.getIndex()] = value
		except Exception, error:
			ERROR_MSG( "restore data fault, use default param.", error, dict["qID"], dict["datas"], dict["tasks"], dict["acceptTime"] )
			return None	# 用于标识在创建此类型时是否出错，这样我们在上一层就可以把它给删除(忽略)

		return obj

	def getDictFromObj( obj ):
		if obj:
			return { "qID":obj._questID, "datas":obj._datas, "tasks":obj._tasks.values(), "acceptTime" : obj._acceptTime }
		# obj is None，表示数据有问题，直接返回默认数据，qID为0表示没有指向任何任务
		return { "qID":0, "datas":{}, "tasks":[], "acceptTime" : 0 }

#
# $Log: QuestDataType.py,v $
# Revision 1.22  2008/08/20 01:27:24  zhangyuxing
# 增加宠物指引任务触发
#
# Revision 1.21  2008/08/15 09:23:13  zhangyuxing
# 合并多种特殊物品提交的查询
#
# Revision 1.20  2008/08/09 08:43:25  songpeifang
# 增加接口获得任务类型id
#
# Revision 1.19  2008/08/07 09:04:01  zhangyuxing
# 对宠物数量类型变化进行支持
#
# Revision 1.18  2008/08/04 06:33:08  zhangyuxing
# 增加画板任务完成触发
#
# Revision 1.17  2008/07/30 06:02:23  zhangyuxing
# 修改环任务任务记录查询的函数的名字
#
# Revision 1.16  2008/07/28 01:08:46  zhangyuxing
# 增加等级任务目标
#
# Revision 1.15  2008/07/22 03:22:38  yangkai
# 添加属性 acceptTime
#
# Revision 1.14  2008/07/14 04:36:52  zhangyuxing
# 加入等级变化，任务完成查询
#
# Revision 1.13  2008/01/30 02:59:35  zhangyuxing
# 增加： 对于直接提交任务的完成查询
#
# Revision 1.12  2008/01/22 08:20:40  zhangyuxing
# 增加了宠物数目变化的处理
#
# Revision 1.11  2008/01/11 07:00:34  zhangyuxing
# 修改简单问题
#
# Revision 1.10  2008/01/09 04:05:23  zhangyuxing
# 增加组队任务目标的相关操作
#
# Revision 1.9  2007/12/29 02:42:27  phw
# method modified: isIndexTaskComplete(), 加入了对特定错误的详细输出
#
# Revision 1.8  2007/12/26 09:06:31  phw
# method modified: addDeliverAmount(), 修正了使用不正确的查询方式来查询物品实例属性的问题
#
# Revision 1.7  2007/12/18 02:20:08  zhangyuxing
# 修改简单错误
#
# Revision 1.6  2007/12/17 11:36:08  zhangyuxing
# 修改： addDeliverAmount , 支持 QUEST_OBJECTIVE_SUBMIT 这种任务目标
#
# Revision 1.5  2007/12/08 09:32:54  phw
# 针对坏数据进行了处理，遇到坏数据时输出日志，并返回None
#
# Revision 1.4  2007/12/05 00:35:06  zhangyuxing
# 在任务状态发生变化的检测中：
# 遍里任务达成目标的方式被修改。而且返回也直接返回达成目标的key.
#
# Revision 1.3  2007/12/04 03:07:22  zhangyuxing
# 1.支持任务达成目标索引支持，相应的访问 tasks_的方式也做改变。
# 2.在 数据传输中 QuestDataType 的创建对象和字典的方式做区别对待。
#
# Revision 1.2  2007/11/02 03:38:46  phw
# method removed: questIncreaseItemUsed() -> increaseItemUsed()
#
# Revision 1.1  2007/11/02 03:33:34  phw
# 用于替代QuestTasksDataType.py
#
#
