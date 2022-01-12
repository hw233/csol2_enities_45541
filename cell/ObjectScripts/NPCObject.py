# -*- coding: gb18030 -*-
#
# $Id: NPCObject.py,v 1.32 2008-09-04 07:45:07 kebiao Exp $

"""
���񼰶Ի�����
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

MIN_SIGN_LEVEL = 99999999			#��͵ȼ�
LEVEL_MINUS = 10					#�ȼ�����

class NPCObject( GameObject ):
	"""
	NPC�Ļ���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		GameObject.__init__( self )
		self.dialog = None						# NPC�ĶԻ�
		self._questStartList = set()			# ����ʼ�б�, set of questID
		self._questFinishList = set()			# ��������б�, set of questID
		self._npcQuestSignData = NPCQuestSign.Datas

	def getStartCount( self ):
		"""
		ȡ�ɽӵ���������
		"""
		return len( self._questStartList )

	def getFinishCount( self ):
		"""
		ȡ��ɵ���������
		"""
		return len( self._questFinishList )

	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		���ݸ�����section����ʼ������ȡ��entity���ԡ�
		ע��ֻ����createEntity()ʱ��Ҫ��ֵ�Զ���entity���г�ʼ��ʱ���б�Ҫ�ŵ��˺�����ʼ����
		Ҳ����˵�������ʼ�����������Զ�����������Ӧ��.def���������ġ�

		@param section: PyDataSection, ����һ���ĸ�ʽ�洢��entity���Ե�section
		"""
		GameObject.onLoadEntityProperties_( self, section )

		self.setEntityProperty( "uname", 		section.readString( "uname" ) )					# ��������
		self.setEntityProperty( "title",		section.readString( "title" ) )					# ͷ��

		flagSection = section["flags"]
		flag = 0
		if flagSection:
			flags = flagSection.readInts( "item" )
			for v in flags: flag |= 1 << v
		
		flag &= 0x7FFFFFFFFFFFFFFE	# ȥ��Ĭ�ϵĵ�0λ��ʶ������������ʶ�����ڴ�������ָ��
		
		# entity�ı�־���ϣ����Ƿ�ɽ��ס��Ƿ��������Ƿ��ܺϳ�װ���ȵȣ�ENTITY_FLAG_*
		self.setEntityProperty( "flags",	flag )

		self.setEntityProperty( "walkSpeed",	int( section.readFloat( "walkSpeed" ) * csconst.FLOAT_ZIP_PERCENT ) )				# ���ٶ�
		self.setEntityProperty( "runSpeed",		int( section.readFloat( "runSpeed" ) * csconst.FLOAT_ZIP_PERCENT ) )				# ���ٶ�

		modelNumbers = [ e.lower() for e in section["modelNumber"].readStrings( "item" ) ]				# ģ�ͱ���б�
		self.setEntityProperty( "modelNumber",	modelNumbers )
		modelScales = section[ "modelScale" ].readStrings( "item" )    # ģ��ʹ�ñ����б�
		self.setEntityProperty( "modelScale",	modelScales )
		if section.has_key( "nameColor" ):
			nameColor = section.readInt( "nameColor" )					#ͷ��������ɫ���
			self.setEntityProperty( "nameColor",	nameColor )

	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		GameObject.load( self, section )

		# phw: �߻�����ʹ�ñ�׼����������ģʽ�����ǿ���ʹ�����Լ�ֱ�������񷢲�NPC��������
		# ��˴˴�����п��ܲ���ʹ�á�
		# read quest start/finish list
		#questSection = section["quests"]
		#if questSection:
		#	self._questStartList = set( questSection.readInts( "quest_start" ) )
		#	self._questFinishList = set( questSection.readInts( "quest_end" ) )

		self.dialog = g_npcTalk.get( self.className )

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		��ʼ���Լ���entity������
		"""
		selfEntity.setEntityType( csdefine.ENTITY_TYPE_NPC_OBJECT )

	def addStartQuest( self, questID ):
		"""
		virtual method.
		����һ�����񵽿�ʼ�б���
		"""
		self._questStartList.add( questID )

	def hasStartQuest( self, questID ):
		"""
		�ж�ָ��������ID�Ƿ�����ڿ�ʼ�����б���

		@return: BOOL
		"""
		return questID in self._questStartList

	def addFinishQuest( self, questID ):
		"""
		virtual method.
		����һ����������б���
		"""
		self._questFinishList.add( questID )

	def hasFinishQuest( self, questID ):
		"""
		�ж�ָ��������ID�Ƿ��������������б���

		@return: BOOL
		"""
		return questID in self._questFinishList

	def gossipWith( self, selfEntity, playerEntity, dlgKey ):
		"""
		����ҶԻ���δ����(��������)�ķ�����������ش˷������ϲ������Ҫ�����Լ���˽���������Լ��ж�self.isReal()��

		@param   selfEntity: ���Լ���Ӧ��Entityʵ���������������Ϊ�˷����Ժ������
		@type    selfEntity: Entity
		@param playerEntity: ˵�������
		@type  playerEntity: Entity
		@param       dlgKey: �Ի��ؼ���
		@type        dlgKey: str
		@return: ��
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
		ȡ��һ�������ȫ��ʵ��
		"""
		try:
			return Love3.g_taskData[questID]
		except KeyError:
			ERROR_MSG("questID(%i) not exist!" % questID )
			return None

	def _isStartObject( self, quest ):
		"""
		�����ҵ�ǰĿ���Ƿ�Ϊ������Ķ���

		@return: BOOL
		@rtype:  BOOL
		"""
		return quest.getID() in self._questStartList

	def _isFinishObject( self, quest ):
		"""
		�����ҵ�ǰĿ���Ƿ�Ϊ������Ķ���

		@return: BOOL
		@rtype:  BOOL
		"""
		return quest.getID() in self._questFinishList

	def questSelect( self, selfEntity, playerEntity, questID ):
		"""
		����ѡ��һ������
		"""
		quest = self.getQuest( questID )
		state = self.questQuery( selfEntity, playerEntity, questID )
		if state == csdefine.QUEST_STATE_NOT_HAVE:		# ��û�нӸ�����
			quest.gossipDetail( playerEntity, selfEntity )
		elif state == csdefine.QUEST_STATE_NOT_FINISH:	# ��û�����Ŀ��
			quest.gossipIncomplete( playerEntity, selfEntity )
		elif state == csdefine.QUEST_STATE_FINISH:		# �����Ŀ��
			if self._isFinishObject( quest ):
				quest.gossipPrecomplete( playerEntity, selfEntity )
		elif state == csdefine.QUEST_STATE_COMPLETE:		# �������Ѿ�������
			pass
		elif state == csdefine.QUEST_STATE_DIRECT_FINISH: #��������ֱ����ɵ���������
			if self._isFinishObject( quest ):
				quest.gossipDetail( playerEntity, selfEntity )
		else:
			# ��������������
			playerEntity.endGossip( selfEntity )
			pass
		return

	def questAccept( self, selfEntity, playerEntity, questID ):
		"""
		���������
		"""
		quest = self.getQuest( questID )
		state = self.questQuery( selfEntity, playerEntity, questID )
		if state != csdefine.QUEST_STATE_NOT_HAVE:
			INFO_MSG( "can't accept quest %i, state = %i." % (questID, state) )
			return
		# ��¼��ID���������������ܸ�����Ҫ�����в����Ի�Ŀ��
		# �����Ժ�������ԭ�򣬷�����ʱ����Ҫ������accept��ɺ��targetID��Ϊ0
		playerEntity.targetID = selfEntity.id
		quest.accept( playerEntity )

	def questChooseReward( self, selfEntity, playerEntity, questID, rewardIndex, codeStr ):
		"""
		��������, ͬʱѡ��������(�����)��
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
			# ������һ������
			if self.questQuery( selfEntity, playerEntity, nextQuestID ) == csdefine.QUEST_STATE_NOT_HAVE:		# ��û�нӸ�����
				self.getQuest( nextQuestID ).gossipDetail( playerEntity, selfEntity )
				#self.getQuest( nextQuestID ).startGossip(  playerEntity, selfEntity , "Talk" )

	def questQuery( self, selfEntity, playerEntity, questID ):
		"""
		��ѯ��Ҷ�ĳһ������Ľ���״̬��
		@return: ����ֵ������鿴common���QUEST_STATE_*
		@rtype:  UINT8
		"""
		quest = self.getQuest( questID )
		if quest == None:
			return
		state = quest.query( playerEntity )
		if state == csdefine.QUEST_STATE_FINISH:
			if self._isFinishObject( quest ):
				return state										# ����Ŀ�������
			else:
				return csdefine.QUEST_STATE_NOT_ALLOW
		if state == csdefine.QUEST_STATE_NOT_HAVE:
			if self._isStartObject( quest ):						# ֻ���Ƿ�������Ķ�����ܲ�ѯ�ܷ������
				return state										# ��δ�Ӹ�����
			else:
				return csdefine.QUEST_STATE_NOT_ALLOW				# ���������Ӹ�����
		if state == csdefine.QUEST_STATE_NOT_FINISH:
			if self._isFinishObject( quest ):
				return state										# ����Ŀ��δ���
			else:
				return csdefine.QUEST_STATE_NOT_ALLOW
		if state == csdefine.QUEST_STATE_DIRECT_FINISH:				# ֱ����ɵ�����Ŀ��
			if self._isFinishObject( quest ):
				return state
			else:
				return csdefine.QUEST_STATE_NOT_ALLOW
		return state

	def questStatus( self, selfEntity, playerEntity ):
		"""
		��ѯһ����Ϸ�������������������ҵ�״̬��״̬��ͨ���ص����ظ�client���Ӧ��GameObject��

		@param   selfEntity: ���Լ���Ӧ��Entityʵ���������������Ϊ�˷����Ժ������
		@type    selfEntity: Entity
		@param playerEntity: ���
		@type  playerEntity: Entity
		@return: ��
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
				continue  #���񲻴��ڻ�����������Ϊ��Ա������������
			if ( player.level - quest.getLevel() > LEVEL_MINUS and quest.getStyle() == csdefine.QUEST_STYLE_NORMAL and quest.getType() != csdefine.QUEST_TYPE_DART  ) and  (questId in self._questStartList) and \
				curState not in [ csdefine.QUEST_STATE_FINISH, csdefine.QUEST_STATE_NOT_FINISH, csdefine.QUEST_STATE_DIRECT_FINISH ]:#�������10�����ϵĿɽ����񽫲���ʾ�����ʶ
					continue
			
			stateL = [csdefine.QUEST_STATE_NOT_HAVE, csdefine.QUEST_STATE_FINISH, csdefine.QUEST_STATE_NOT_FINISH, csdefine.QUEST_STATE_DIRECT_FINISH]

			if  (questId in self._questStartList and curState == csdefine.QUEST_STATE_NOT_HAVE ) or (questId in self._questFinishList and curState in stateL[1:] ):
				tempId = quest.getType()*10 + curState	# *10��Ҫ���ڼ���������ö�Ӧ��signID
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
		��ȡ����npcͷ������Ի���ʶ�����ȵȼ�
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
		����Ƿ���ָ����ҿ��Խ�������
		@param player: ���ʵ��
		@type  player: entity
		@return: True:��ֱ�ӿɽ������� False:û��ֱ�ӿɽ�������
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
		����Ƿ���ָ����ҿ��Խ�������
		@param player: ���ʵ��
		@type  player: entity
		@return: True:��ֱ�ӿɽ������� False:û��ֱ�ӿɽ�������
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
		����Ƿ���ָ����ҿ��Խ�������
		@param player: ���ʵ��
		@type  player: entity
		@return: True:�пɽ������� False:û�пɽ�������
		@rtype: bool
		"""
		for id in self._questFinishList:
			quest = self.getQuest( id )
			if quest == None:
				continue
			state = quest.query( player )
			if state == csdefine.QUEST_STATE_FINISH:			# ���Խ�����û��
				return True
		return False

	def hasIncompleteQuests( self, player ):
		"""
		����Ƿ���ָ������ѽӵ������Խ�������
		@param player: ���ʵ��
		@type  player: entity
		@return: True:�пɽ������� False:û�пɽ�������
		@rtype: bool
		"""
		for id in self._questFinishList:
			quest = self.getQuest( id )
			if quest == None:
				continue
			state = quest.query( player )
			if state == csdefine.QUEST_STATE_NOT_FINISH:			# �ѽӵ��������Խ�������
				return True
		return False

	def hasStartQuests( self, player ):
		"""
		����Ƿ���ָ����ҿ��Խӵ�����
		@param player: ���ʵ��
		@type  player: entity
		@return: True:�пɽ������� False:û�пɽ�������
		@rtype: bool
		"""
		for id in self._questStartList:
			quest = self.getQuest( id )
			if quest == None or quest.getType() == csdefine.QUEST_TYPE_MEMBER_DART:
				continue
			state = quest.query( player )
			if state == csdefine.QUEST_STATE_NOT_HAVE:		# ���Խӵ���û�н�
				return True
		return False

	def hasStartQuestsLevelSuit( self, player ):
		"""
		����Ƿ���ָ����ҿ��Խӵ�����(���Ҽ������)
		@param player: ���ʵ��
		@type  player: entity
		@return: True:�пɽ������� False:û�пɽ�������
		@rtype: bool
		"""
		for id in self._questStartList:
			quest = self.getQuest( id )
			if quest == None:
				continue
			state = quest.query( player )
			# ���Խӵ���û�н�, ���Ҽ������
			if state == csdefine.QUEST_STATE_NOT_HAVE and player.level - quest._level <= 5:
				return True
		return False

	def embedQuests( self, selfEntity, player ):
		"""
		Ƕ��ָ��������п�����ʾ������
		"""
		#quests = []
		for id in self._questStartList:
			quest = self.getQuest( id )
			if quest == None:
				continue
			questType = quest.getType()
			questStyle = quest.getStyle()
			state = self.questQuery( selfEntity, player, id )
			#����ʾ���������ӻ����Ѿ���ɵ�����
			if state != csdefine.QUEST_STATE_NOT_ALLOW and state != csdefine.QUEST_STATE_COMPLETE:
				if self.hasFinishQuest( id ) and state == csdefine.QUEST_STATE_FINISH:
					#����������ͬʱҲ�ǽ��Ķ��������Ѿ����Խ��� ��ô�����뿪ʼ�б�
					continue
				#���������NPC �����С�����Ŀ��δ��ɶԻ�������ʾ������ѡ���ҵ������ʾ������Ŀ��δ��ɶԻ���
				if state == csdefine.QUEST_STATE_FINISH:
					#������ʾ������
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
			#��ʾ�����ѽӣ���δ�������Ŀ�� �������ѽӣ������������Ŀ��
			if state in [csdefine.QUEST_STATE_NOT_FINISH, csdefine.QUEST_STATE_FINISH, csdefine.QUEST_STATE_DIRECT_FINISH]:
				if self.hasStartQuest( id ) and state != csdefine.QUEST_STATE_FINISH:   #���NPCͬʱҲ�Ƿ������������ˣ���ôֻ��������ɿɽ�������
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
		����һ��NPCʵ���ڵ�ͼ��
		@param   spaceID: ��ͼID��
		@type    spaceID: INT32
		@param  position: entity�ĳ���λ��
		@type   position: VECTOR3
		@param direction: entity�ĳ�������
		@type  direction: VECTOR3
		@param      param: �ò���Ĭ��ֵΪNone������ʵ�������
		@type    	param: dict
		@return:          һ���µ�NPC Entity
		@rtype:           Entity
		"""
		if param is None:
			param = {}

		if not param.has_key( "modelNumber" ): # ����ⲿ�ж�����ô�����и���
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
		ɾ������
		"""
		pass


	def onRequestCell( self, selfEntity, cellMailbox, baseMailbox ):
		"""
		���������ռ� entity��cell����
		"""
		pass

	def questQuestionHandle(  self, selfEntity, playerEntity, dlgKey ):
		"""
		NPC�Ի�����
		"""
		if dlgKey == "START ANSWER":
			if playerEntity.query("last_question_type",0) != playerEntity.query("question_type"):
				playerEntity.set( "last_question_type",playerEntity.query("question_type") )
				questionID = "-1"
			else:
				questionID = playerEntity.query( "current_question_id", "-1" )
			typeQuestionKeys = []															#���ϵ�ǰ�������͵� ��ĿID�б�
			for i in Love3.g_questQuestionSection.keys():
				if Love3.g_questQuestionSection[i]["type"].asInt == playerEntity.query("question_type"):
					typeQuestionKeys.append( i )
			
			#����ӵ��ظ�����Ŀ
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
			answerList = [] #��ѡ��
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
			#֪ͨ�ش���ȷ�������ش���ȷ����
			playerEntity.statusMessage( csstatus.IE_ANSWER_TRUE )			
			playerEntity.questTaskAddNormalAnswerQuestion( playerEntity.query("question_type"), True )
			playerEntity.clientEntity( selfEntity.id ).onAnswerSuceed( True )
		else:
			#֪ͨ�ش�������
			playerEntity.statusMessage( csstatus.IE_ANSWER_FALSE )
			playerEntity.questTaskAddNormalAnswerQuestion( playerEntity.query("question_type"), False )
			playerEntity.clientEntity( selfEntity.id ).onAnswerSuceed( False )
			
	def canUseBank( self, srcEntity, roleEntity ):
		"""
		14:03 2011-5-4 by wsf
		ԭ����������npcǮׯ�����ӿڣ��̳д˽ӿڵ�npc�Ż���Ǯׯ���ܣ������ڵ�ǰǮׯ�����в���������ҵĶ���������
		��˽���Ӵ˺���������֤�Ƿ���Խ���Ǯׯ���������Ժ��ع�Ǯׯϵͳ�ٿ���npc����ĸ���һ����Ǯׯ������Ϊ��

		@param srcEntity : �˽ű���Ӧ��entity
		@param roleEntity : ���entity��Ŀǰֻ����Ҳ���ʹ��Ǯׯ
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
