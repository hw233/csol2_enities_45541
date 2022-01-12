# -*- coding: gb18030 -*-
import csdefine
from Time import *

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

	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskTeam )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		"""
		return self.val1 >= self.val2


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

	def copyFrom( self, taskInstance ):
		"""
		从一个任务目标里复制新数据(这个通常只用于client)
		"""
		assert isinstance( taskInstance, QTTaskEnterSpace )
		self.__dict__.update( taskInstance.__dict__ )
		
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_TIME,					QTTaskTime )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_KILL,					QTTaskKill )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_KILLS,					QTTaskKills )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_DART_KILL,				QTTaskKillDart )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_DELIVER,				QTTaskDeliver )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_EVENT_USE_ITEM,		QTTaskEventItemUsed )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SKILL_LEARNED,			QTTaskSkillLearned )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_LIVING_SKILL_LEARNED,	QTTaskLivingSkillLearned )
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