# -*- coding: gb18030 -*-
#
# $Id: NPCObject.py,v 1.32 2008-09-04 07:45:07 kebiao Exp $

"""
任务及对话基础
"""

import random
import Language
import Love3
import csdefine
import csconst
from bwdebug import *
from GameObject import GameObject
import Love3
from Resource.NPCTalkLoader import NPCTalkLoader
from config import NPCQuestSign
import csstatus
g_npcTalk = NPCTalkLoader.instance()

from Resource.QuestBubbleGuider import QuestBubbleGuider
qstGuider = QuestBubbleGuider.instance()

MIN_SIGN_LEVEL = 99999999			#最低等级
LEVEL_MINUS = 10					#等级限制

class NPCObject( GameObject ):
	"""
	NPC的基类
	"""
	def __init__( self ):
		"""
		初始化
		"""
		GameObject.__init__( self )
		self.dialog = None						# NPC的对话
		self._questStartList = set()			# 任务开始列表, set of questID
		self._questFinishList = set()			# 任务结束列表, set of questID
		self._npcQuestSignData = NPCQuestSign.Datas

	def getStartCount( self ):
		"""
		取可接的任务数量
		"""
		return len( self._questStartList )

	def getFinishCount( self ):
		"""
		取完成的任务数量
		"""
		return len( self._questFinishList )

	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		根据给定的section，初始化（读取）entity属性。
		注：只有在createEntity()时需要把值自动对entity进行初始化时才有必要放到此函数初始化，
		也就是说，这里初始化的所有属性都必须是在相应的.def中声明过的。

		@param section: PyDataSection, 根据一定的格式存储了entity属性的section
		"""
		GameObject.onLoadEntityProperties_( self, section )

		self.setEntityProperty( "uname", 		section.readString( "uname" ) )					# 中文名称
		self.setEntityProperty( "title",		section.readString( "title" ) )					# 头衔

		flagSection = section["flags"]
		flag = 0
		if flagSection:
			flags = flagSection.readInts( "item" )
			for v in flags: flag |= 1 << v
		
		flag &= 0x7FFFFFFFFFFFFFFE	# 去看默认的第0位标识，这个是特殊标识，用于代码主动指定
		
		# entity的标志集合，如是否可交易、是否有任务、是否能合成装备等等；ENTITY_FLAG_*
		self.setEntityProperty( "flags",	flag )

		self.setEntityProperty( "walkSpeed",	int( section.readFloat( "walkSpeed" ) * csconst.FLOAT_ZIP_PERCENT ) )				# 走速度
		self.setEntityProperty( "runSpeed",		int( section.readFloat( "runSpeed" ) * csconst.FLOAT_ZIP_PERCENT ) )				# 跑速度

		modelNumbers = [ e.lower() for e in section["modelNumber"].readStrings( "item" ) ]				# 模型编号列表
		self.setEntityProperty( "modelNumber",	modelNumbers )
		modelScales = section[ "modelScale" ].readStrings( "item" )    # 模型使用比例列表
		self.setEntityProperty( "modelScale",	modelScales )
		if section.has_key( "nameColor" ):
			nameColor = section.readInt( "nameColor" )					#头顶名称颜色标记
			self.setEntityProperty( "nameColor",	nameColor )

	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		GameObject.load( self, section )

		# phw: 策划决定使用标准的任务配置模式，我们可以使任务自己直接向任务发布NPC插入任务。
		# 因此此代码很有可能不再使用。
		# read quest start/finish list
		#questSection = section["quests"]
		#if questSection:
		#	self._questStartList = set( questSection.readInts( "quest_start" ) )
		#	self._questFinishList = set( questSection.readInts( "quest_end" ) )

		self.dialog = g_npcTalk.get( self.className )

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		初始化自己的entity的数据
		"""
		selfEntity.setEntityType( csdefine.ENTITY_TYPE_NPC_OBJECT )

	def addStartQuest( self, questID ):
		"""
		virtual method.
		增加一个任务到开始列表中
		"""
		self._questStartList.add( questID )

	def hasStartQuest( self, questID ):
		"""
		判断指定的任务ID是否存在于开始任务列表中

		@return: BOOL
		"""
		return questID in self._questStartList

	def addFinishQuest( self, questID ):
		"""
		virtual method.
		增加一个任务到完成列表中
		"""
		self._questFinishList.add( questID )

	def hasFinishQuest( self, questID ):
		"""
		判断指定的任务ID是否存在于完成任务列表中

		@return: BOOL
		"""
		return questID in self._questFinishList

	def gossipWith( self, selfEntity, playerEntity, dlgKey ):
		"""
		与玩家对话；未声明(不能声明)的方法，因此重载此方法的上层如果需要访问自己的私有属性请自己判断self.isReal()。

		@param   selfEntity: 与自己对应的Entity实例，传这个参数是为了方便以后的扩充
		@type    selfEntity: Entity
		@param playerEntity: 说话的玩家
		@type  playerEntity: Entity
		@param       dlgKey: 对话关键字
		@type        dlgKey: str
		@return: 无
		"""
		if self.questQuestionHandle( selfEntity, playerEntity, dlgKey ):
			return
		if dlgKey == "Talk" :
			self.embedQuests( selfEntity, playerEntity )
		if self.dialog:
			self.dialog.doTalk( dlgKey, playerEntity, selfEntity )
		playerEntity.sendGossipComplete( selfEntity.id )

	def getQuest( self, questID ):
		"""
		取得一个任务的全局实例
		"""
		try:
			return Love3.g_taskData[questID]
		except KeyError:
			ERROR_MSG("questID(%i) not exist!" % questID )
			return None

	def _isStartObject( self, quest ):
		"""
		检查玩家当前目标是否为接任务的对象

		@return: BOOL
		@rtype:  BOOL
		"""
		return quest.getID() in self._questStartList

	def _isFinishObject( self, quest ):
		"""
		检查玩家当前目标是否为交任务的对象

		@return: BOOL
		@rtype:  BOOL
		"""
		return quest.getID() in self._questFinishList

	def questSelect( self, selfEntity, playerEntity, questID ):
		"""
		请求选择一个任务
		"""
		quest = self.getQuest( questID )
		state = self.questQuery( selfEntity, playerEntity, questID )
		if state == csdefine.QUEST_STATE_NOT_HAVE:		# 还没有接该任务
			quest.gossipDetail( playerEntity, selfEntity )
		elif state == csdefine.QUEST_STATE_NOT_FINISH:	# 还没有完成目标
			quest.gossipIncomplete( playerEntity, selfEntity )
		elif state == csdefine.QUEST_STATE_FINISH:		# 已完成目标
			if self._isFinishObject( quest ):
				quest.gossipPrecomplete( playerEntity, selfEntity )
		elif state == csdefine.QUEST_STATE_COMPLETE:		# 该任务已经做过了
			pass
		elif state == csdefine.QUEST_STATE_DIRECT_FINISH: #该任务是直接完成的任务类型
			if self._isFinishObject( quest ):
				quest.gossipDetail( playerEntity, selfEntity )
		else:
			# 不够条件接任务
			playerEntity.endGossip( selfEntity )
			pass
		return

	def questAccept( self, selfEntity, playerEntity, questID ):
		"""
		请求接任务
		"""
		quest = self.getQuest( questID )
		state = self.questQuery( selfEntity, playerEntity, questID )
		if state != csdefine.QUEST_STATE_NOT_HAVE:
			INFO_MSG( "can't accept quest %i, state = %i." % (questID, state) )
			return
		# 记录此ID，以让任务里面能根据需要而进行操作对话目标
		# 除非以后有特殊原因，否则暂时不需要考虑在accept完成后把targetID置为0
		playerEntity.targetID = selfEntity.id
		quest.accept( playerEntity )

	def questChooseReward( self, selfEntity, playerEntity, questID, rewardIndex, codeStr ):
		"""
		请求交任务, 同时选择任务奖励(如果有)。
		"""
		quest = self.getQuest( questID )
		state = self.questQuery( selfEntity, playerEntity, questID )
		if state != csdefine.QUEST_STATE_FINISH and state != csdefine.QUEST_STATE_DIRECT_FINISH:
			INFO_MSG( "can't choose quest reward %i, state = %i." % (questID, state) )
			return
		try:
			if not quest.complete( playerEntity, rewardIndex, codeStr ):
				return
			quest.gossipComplete( playerEntity, selfEntity )
		except:
			playerEntity.questRemove( questID, 0 )
			playerEntity.questFinishQuest( questID )
			EXCEHOOK_MSG("questID(%i) has bug in complete function! playerName:%s" % ( questID, playerEntity.getName()) )
		nextQuestID = quest.getNextQuest( playerEntity )
		if nextQuestID != 0:
			# 激活下一个任务
			if self.questQuery( selfEntity, playerEntity, nextQuestID ) == csdefine.QUEST_STATE_NOT_HAVE:		# 还没有接该任务
				self.getQuest( nextQuestID ).gossipDetail( playerEntity, selfEntity )
				#self.getQuest( nextQuestID ).startGossip(  playerEntity, selfEntity , "Talk" )

	def questQuery( self, selfEntity, playerEntity, questID ):
		"""
		查询玩家对某一个任务的进行状态。
		@return: 返回值类型请查看common里的QUEST_STATE_*
		@rtype:  UINT8
		"""
		quest = self.getQuest( questID )
		if quest == None:
			return
		state = quest.query( playerEntity )
		if state == csdefine.QUEST_STATE_FINISH:
			if self._isFinishObject( quest ):
				return state										# 任务目标已完成
			else:
				return csdefine.QUEST_STATE_NOT_ALLOW
		if state == csdefine.QUEST_STATE_NOT_HAVE:
			if self._isStartObject( quest ):						# 只有是发放任务的对象才能查询能否接任务
				return state										# 还未接该任务
			else:
				return csdefine.QUEST_STATE_NOT_ALLOW				# 不够条件接该任务
		if state == csdefine.QUEST_STATE_NOT_FINISH:
			if self._isFinishObject( quest ):
				return state										# 任务目标未完成
			else:
				return csdefine.QUEST_STATE_NOT_ALLOW
		if state == csdefine.QUEST_STATE_DIRECT_FINISH:				# 直接完成的任务目标
			if self._isFinishObject( quest ):
				return state
			else:
				return csdefine.QUEST_STATE_NOT_ALLOW
		return state

	def questStatus( self, selfEntity, playerEntity ):
		"""
		查询一个游戏对象所有任务相对于玩家的状态，状态将通过回调返回给client相对应的GameObject。

		@param   selfEntity: 与自己对应的Entity实例，传这个参数是为了方便以后的扩充
		@type    selfEntity: Entity
		@param playerEntity: 玩家
		@type  playerEntity: Entity
		@return: 无
		"""
		level,signID = self.getQuestStateLevel( playerEntity)
		playerEntity.clientEntity( selfEntity.id ).onQuestStatus( signID )
		

	def getQuestStateLevel( self, player ):
		"""
		"""
		signID = -1
		level = MIN_SIGN_LEVEL
		
		sign_levels = [(level,signID)]
		questList = list(self._questStartList) + list(self._questFinishList) 
		
		for questId in questList:
			quest = self.getQuest( questId )
			curState = quest.query( player )
			if quest == None or quest.getType() == csdefine.QUEST_TYPE_MEMBER_DART:
				continue  #任务不存在或者任务类型为成员运镖任务将跳过
			if ( player.level - quest.getLevel() > LEVEL_MINUS and quest.getStyle() == csdefine.QUEST_STYLE_NORMAL and quest.getType() != csdefine.QUEST_TYPE_DART  ) and  (questId in self._questStartList) and \
				curState not in [ csdefine.QUEST_STATE_FINISH, csdefine.QUEST_STATE_NOT_FINISH, csdefine.QUEST_STATE_DIRECT_FINISH ]:#低于玩家10及以上的可接任务将不显示任务标识
					continue
			
			stateL = [csdefine.QUEST_STATE_NOT_HAVE, csdefine.QUEST_STATE_FINISH, csdefine.QUEST_STATE_NOT_FINISH, csdefine.QUEST_STATE_DIRECT_FINISH]

			if  (questId in self._questStartList and curState == csdefine.QUEST_STATE_NOT_HAVE ) or (questId in self._questFinishList and curState in stateL[1:] ):
				tempId = quest.getType()*10 + curState	# *10主要用于计算出和配置对应的signID
				if curState == csdefine.QUEST_STATE_DIRECT_FINISH:
					if quest._query_tasks( player ) != csdefine.QUEST_STATE_FINISH:
						continue
					if questId in self._questFinishList:
						tempId = 91	
				try:
					tempLevel = self._npcQuestSignData[ tempId ][ 'level' ]
				except KeyError:
					continue
				if tempLevel < level:
					level = tempLevel
					signID = tempId
			sign_levels.append(( level,signID))
			
		proStateLeve = self.getProQuestStateLevel( player )
		if proStateLeve:
			sign_levels.append( proStateLeve )

		sign_levels.sort()
		return ( sign_levels[0])
	
	
	def getProQuestStateLevel( self, player ):
		"""
		获取处理npc头顶任务对话标识的优先等级
		"""
		for questID, questData in player.questsTable.items():							#
			tskData = qstGuider.getQuestTaskByCls( self.className, questID )
			if tskData is None:continue
			tasks = questData.getTasks()
			for taskIndex, task in tasks.items():
				isComplete = task.isCompleted( player )
				if tskData[0] == taskIndex and \
				isComplete == tskData[1]:
					return ( 150, 6 )
		return None

	def hasFixLoop( self, player, questList, state ):
		"""
		"""
		for id in questList:
			quest = self.getQuest( id )
			if quest == None:
				continue
			m_state = quest.query( player )
			if m_state == state and quest.getStyle() == csdefine.QUEST_STYLE_FIXED_LOOP:
				return True
		return False


	def hasDirectFinishQuests( self, player ):
		"""
		检查是否有指定玩家可以交的任务。
		@param player: 玩家实体
		@type  player: entity
		@return: True:有直接可交的任务 False:没有直接可交的任务
		@rtype: bool
		"""
		for id in self._questFinishList:
			quest = self.getQuest( id )
			if quest == None:
				continue
			state = quest.query( player )
			if state == csdefine.QUEST_STATE_DIRECT_FINISH:
				return True
		return False

	def hasFixedLoopQuests( self, player ):
		"""
		检查是否有指定玩家可以交的任务。
		@param player: 玩家实体
		@type  player: entity
		@return: True:有直接可交的任务 False:没有直接可交的任务
		@rtype: bool
		"""
		for id in self._questFinishList:
			quest = self.getQuest( id )
			if quest == None:
				continue
			state = quest.query( player )
			if state == csdefine.QUEST_STATE_DIRECT_FINISH:
				return True
		return False

	def hasFinishQuests( self, player ):
		"""
		检查是否有指定玩家可以交的任务。
		@param player: 玩家实体
		@type  player: entity
		@return: True:有可交的任务 False:没有可交的任务
		@rtype: bool
		"""
		for id in self._questFinishList:
			quest = self.getQuest( id )
			if quest == None:
				continue
			state = quest.query( player )
			if state == csdefine.QUEST_STATE_FINISH:			# 可以交但还没交
				return True
		return False

	def hasIncompleteQuests( self, player ):
		"""
		检查是否有指定玩家已接但不可以交的任务。
		@param player: 玩家实体
		@type  player: entity
		@return: True:有可交的任务 False:没有可交的任务
		@rtype: bool
		"""
		for id in self._questFinishList:
			quest = self.getQuest( id )
			if quest == None:
				continue
			state = quest.query( player )
			if state == csdefine.QUEST_STATE_NOT_FINISH:			# 已接但还不可以交的任务
				return True
		return False

	def hasStartQuests( self, player ):
		"""
		检查是否有指定玩家可以接的任务。
		@param player: 玩家实体
		@type  player: entity
		@return: True:有可交的任务 False:没有可交的任务
		@rtype: bool
		"""
		for id in self._questStartList:
			quest = self.getQuest( id )
			if quest == None or quest.getType() == csdefine.QUEST_TYPE_MEMBER_DART:
				continue
			state = quest.query( player )
			if state == csdefine.QUEST_STATE_NOT_HAVE:		# 可以接但还没有接
				return True
		return False

	def hasStartQuestsLevelSuit( self, player ):
		"""
		检查是否有指定玩家可以接的任务(并且级别合适)
		@param player: 玩家实体
		@type  player: entity
		@return: True:有可交的任务 False:没有可交的任务
		@rtype: bool
		"""
		for id in self._questStartList:
			quest = self.getQuest( id )
			if quest == None:
				continue
			state = quest.query( player )
			# 可以接但还没有接, 而且级别合适
			if state == csdefine.QUEST_STATE_NOT_HAVE and player.level - quest._level <= 5:
				return True
		return False

	def embedQuests( self, selfEntity, player ):
		"""
		嵌入指定玩家所有可以显示的任务。
		"""
		#quests = []
		for id in self._questStartList:
			quest = self.getQuest( id )
			if quest == None:
				continue
			questType = quest.getType()
			questStyle = quest.getStyle()
			state = self.questQuery( selfEntity, player, id )
			#不显示不够条件接或者已经完成的任务
			if state != csdefine.QUEST_STATE_NOT_ALLOW and state != csdefine.QUEST_STATE_COMPLETE:
				if self.hasFinishQuest( id ) and state == csdefine.QUEST_STATE_FINISH:
					#如果这个任务同时也是交的而且任务已经可以交了 那么不加入开始列表
					continue
				#如果接任务NPC 任务有“任务目标未完成对话”，显示该任务选项，玩家点击后显示“任务目标未完成对话”
				if state == csdefine.QUEST_STATE_FINISH:
					#否则不显示该任务
					continue
				if not quest.hasOption():
					continue
				#quests.append( id )
				player.addGossipQuestOption( id, self.convertState( questType, questStyle, state ) )

		for id in self._questFinishList:
			quest = self.getQuest( id )
			if quest == None:
				continue
			questType = quest.getType()
			questStyle = quest.getStyle()
			state = self.questQuery( selfEntity, player, id )
			#显示任务已接，但未完成任务目标 和任务已接，且已完成任务目标
			if state in [csdefine.QUEST_STATE_NOT_FINISH, csdefine.QUEST_STATE_FINISH, csdefine.QUEST_STATE_DIRECT_FINISH]:
				if self.hasStartQuest( id ) and state != csdefine.QUEST_STATE_FINISH:   #如果NPC同时也是发行这个任务的人，那么只有任务完成可交才做事
					continue
				#quests.append( id )
				if state == csdefine.QUEST_STATE_DIRECT_FINISH:
					if quest._query_tasks( player ) == csdefine.QUEST_STATE_FINISH:
						state = csdefine.QUEST_STATE_FINISH
				player.addGossipQuestOption( id, self.convertState( questType, questStyle, state ) )
	
	def convertState( self, questType, questStyle, state ):
		"""
		"""
		if questStyle == csdefine.QUEST_STYLE_DIRECT_FINISH:
			state = csdefine.QUEST_STATE_DIRECT_FINISH
		if questType == csdefine.QUEST_TYPE_MERCHANT:
			if state == csdefine.QUEST_STATE_NOT_HAVE:
				state =  csdefine.QUEST_STATE_NOT_HAVE_BLUE
			elif state == csdefine.QUEST_STATE_FINISH:
				state = csdefine.QUEST_STATE_DIRECT_FINISH
		return state

	def createEntity( self, spaceID, position, direction, param = None ):
		"""
		创建一个NPC实体在地图上
		@param   spaceID: 地图ID号
		@type    spaceID: INT32
		@param  position: entity的出生位置
		@type   position: VECTOR3
		@param direction: entity的出生方向
		@type  direction: VECTOR3
		@param      param: 该参数默认值为None，传给实体的数据
		@type    	param: dict
		@return:          一个新的NPC Entity
		@rtype:           Entity
		"""
		if param is None:
			param = {}

		if not param.has_key( "modelNumber" ): # 如果外部有定义那么不进行更新
			modelNumbers = self.getEntityProperty( "modelNumber" )
			modelScales = self.getEntityProperty( "modelScale" )
			if len( modelNumbers ):
				index = random.randint( 0, len(modelNumbers) - 1 )
				param["modelNumber"] = modelNumbers[ index ]
				if len( modelScales ) ==  1:
					param["modelScale"] = float( modelScales[ 0 ] )
				elif len( modelScales ) >= ( index + 1 ):
					param["modelScale"] = float( modelScales[ index ] )
				else:
					param["modelScale"] = 1.0
			else:
				param["modelNumber"] = ""
				param["modelScale"] = 1.0
		return GameObject.createEntity( self, spaceID, position, direction, param )

	def onDestroySelfTimer( self, selfEntity ):
		"""
		删除自身
		"""
		pass


	def onRequestCell( self, selfEntity, cellMailbox, baseMailbox ):
		"""
		创建副本空间 entity的cell返回
		"""
		pass

	def questQuestionHandle(  self, selfEntity, playerEntity, dlgKey ):
		"""
		NPC对话控制
		"""
		if dlgKey == "START ANSWER":
			if playerEntity.query("last_question_type",0) != playerEntity.query("question_type"):
				playerEntity.set( "last_question_type",playerEntity.query("question_type") )
				questionID = "-1"
			else:
				questionID = playerEntity.query( "current_question_id", "-1" )
			typeQuestionKeys = []															#符合当前任务类型的 题目ID列表
			for i in Love3.g_questQuestionSection.keys():
				if Love3.g_questQuestionSection[i]["type"].asInt == playerEntity.query("question_type"):
					typeQuestionKeys.append( i )
			
			#避免接到重复的题目
			for i in playerEntity.queryTemp( "question_id_list", [] ):
				if i in typeQuestionKeys:
					typeQuestionKeys.remove( i )
			
			if len( typeQuestionKeys ) == 0:
				for i in Love3.g_questQuestionSection.keys():
					if Love3.g_questQuestionSection[i]["type"].asInt == playerEntity.query("question_type"):
						typeQuestionKeys.append( i )
			
			if questionID == "-1":
				questionID = typeQuestionKeys[random.randint(0, len( typeQuestionKeys ) - 1)]
				playerEntity.set( "current_question_id", questionID )
				question_id_list = playerEntity.queryTemp( "question_id_list", [] )
				question_id_list.append( questionID )
				playerEntity.setTemp( "question_id_list", question_id_list )
			questDsp = Love3.g_questQuestionSection[questionID]["questionDes"].asString
			answerList = [] #答案选项
			questA = Love3.g_questQuestionSection[questionID]["a"].asString
			questB = Love3.g_questQuestionSection[questionID]["b"].asString
			questC = Love3.g_questQuestionSection[questionID]["c"].asString
			answerList = [questA, questB, questC]
			questD = Love3.g_questQuestionSection[questionID]["d"].asString
			if questD != "":
				answerList.append( questD )
			questE = Love3.g_questQuestionSection[questionID]["e"].asString
			if questE != "":
				answerList.append( questE )
			
			info = ""
			try:
				info = Love3.g_questQuestionSection[questionID]["info"].asString
			except:
				pass
			count = playerEntity.questsTable.getQuestionCount( playerEntity.query("question_type") )
			playerEntity.clientEntity( selfEntity.id ).onSendQuetions( questDsp, answerList, count, info )
		elif dlgKey == "a":

			self.answerProcess( selfEntity, playerEntity, "a" )
		elif dlgKey == "b":

			self.answerProcess( selfEntity, playerEntity, "b" )
		elif dlgKey == "c":

			self.answerProcess( selfEntity, playerEntity, "c" )
		elif dlgKey == "d":

			self.answerProcess( selfEntity, playerEntity, "d" )
		elif dlgKey == "e":

			self.answerProcess( selfEntity, playerEntity, "e" )		
		else:
			return False
		

		return True

	def answerProcess( self, selfEntity, playerEntity, answerID ):
		
		if playerEntity.query( "current_question_id" ) == None:
			return
		if Love3.g_questQuestionSection[playerEntity.query( "current_question_id" )]['answer'].asString == answerID:
			#通知回答正确记数，回答正确记数
			playerEntity.statusMessage( csstatus.IE_ANSWER_TRUE )			
			playerEntity.questTaskAddNormalAnswerQuestion( playerEntity.query("question_type"), True )
			playerEntity.clientEntity( selfEntity.id ).onAnswerSuceed( True )
		else:
			#通知回答错误记数
			playerEntity.statusMessage( csstatus.IE_ANSWER_FALSE )
			playerEntity.questTaskAddNormalAnswerQuestion( playerEntity.query("question_type"), False )
			playerEntity.clientEntity( selfEntity.id ).onAnswerSuceed( False )
			
	def canUseBank( self, srcEntity, roleEntity ):
		"""
		14:03 2011-5-4 by wsf
		原本考虑增加npc钱庄操作接口，继承此接口的npc才会有钱庄功能，但由于当前钱庄的所有操作都是玩家的独立操作，
		因此仅添加此函数负责验证是否可以进行钱庄操作，如以后重构钱庄系统再考虑npc合理的负责一部分钱庄操作行为。

		@param srcEntity : 此脚本对应的entity
		@param roleEntity : 玩家entity，目前只有玩家才能使用钱庄
		"""
		return csstatus.BANK_CAN_USE
		
	def onDestroy( self, selfEntity ):
		"""
		virtual method
		"""
		pass
		
	def onEnterTrapExt( self, selfEntity, entity, range, controllerID ):
		"""
		virtual method
		"""
		pass
		
	def onLeaveTrapExt( self, selfEntity, entity, range, userData ):
		"""
		virtual method
		"""
		pass
		
# NPCObject.py
