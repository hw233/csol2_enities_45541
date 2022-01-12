# -*- coding: gb18030 -*-
#
# $Id: QuestDataType.py,v 1.22 2008/08/20 01:27:24 zhangyuxing Exp $

"""
����Ŀ���������һ��ʵ���Ͷ�Ӧһ������Ŀ�ꡣ
ʵ���Զ����������ͽӿڣ�����������⡣
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
		�����������
		"""
		if not self._datas.has_key( "type" ):
			return csdefine.QUEST_TYPE_NONE
		return self._datas["type"]

	def getStyle( self ):
		"""
		�����������
		"""
		if not self._datas.has_key( "style" ):
			return csdefine.QUEST_TYPE_NONE
		return self._datas["style"]


	def getTasks( self ):
		"""
		��������б�
		"""
		return self._tasks

	def setTasks( self, taskDict ):
		"""
		���������б�
		"""
		self._tasks = taskDict

	def getAcceptTime( self ):
		"""
		����������ܵ�ʱ��
		"""
		return self._acceptTime

	def query( self, key, default = None ):
		"""
		��ѯ��չ����

		@return: ����ؼ��ֲ������򷵻�defaultֵ
		"""
		try:
			return self._datas[key]
		except KeyError:
			return default

	def set( self, key, value ):
		"""
		д����չ����

		@param   key: �κ�PYTHONԭ����(����ʹ���ַ���)
		@param value: �κ�PYTHONԭ����(����ʹ�����ֻ��ַ���)
		"""
		self._datas[key] = value

	def isCompleted( self, player ):
		"""
		��ѯ�Ƿ���������Ŀ�궼�Ѵﵽ
		"""
		for i in self._tasks:
			if not self._tasks[i].isCompleted( player ):
				return False
		return True


	def isCompletedForNoStart( self, player ):
		"""
		��ѯ�Ƿ���������Ŀ�궼�Ѵﵽ
		"""
		for i in self._tasks:
			if not self._tasks[i].isCompletedForNoStart( player ):
				return False
		return True


	def complete( self, player ):
		"""
		������񣬽���һЩ��������
		"""
		for i in self._tasks:
			self._tasks[i].complete( player )

	def deliverIsComplete( self, itemID, player ):
		"""
		�����ص���Ʒ�Ƿ����ռ����

		@param itemID: ��Ʒ��ʶ��
		@type  itemID: STRING
		@param player: ���ʵ��
		@type  player: Role Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_DELIVER and self._tasks[i].getDeliverID() == itemID:
				return self._tasks[i].isCompleted( player )

			if self._tasks[i].getType() in csconst.QUEST_OBJECTIVE_SUBMIT_TYPES and self._tasks[i].getSubmitID() == itemID:
				return self._tasks[i].isCompleted( player )
			
			# ��Ӫ��ռ�����:Ҫ�ռ�ָ����ͼ����Ʒ,������Ϊ�����
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_CAMPACT_DELIVER and self._tasks[i].isValidSpace( player) and self._tasks[i].getDeliverID() == itemID:
				return self._tasks[i].isCompleted( player )

		ERROR_MSG( "quest not in need of %s." % itemID )
		return True	# �����Ŀ����û��ͬ�����Ʒ�ռ�����Ϊ����ɣ�����������������Ϊ����������д����

	def increaseKilled( self, player, monsterEntity ):
		"""
		�����������һ����npcID���Ӧ������Ŀ�겢��ɱ����������1

		@return: ���������Ŀ�����ҵ�����ص�NPC��ʶ�򷵻�taskIndex�����򷵻�-1
		@rtype:  INT
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_KILL and self._tasks[i].getKilledName() == monsterEntity.className:
				if self._tasks[i].add( player, 1 ):
					return i		# ���ҵ�һ���ҵ���
				else:
					return -1
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_KILL_WITH_PET and self._tasks[i].getKilledName() == monsterEntity.className:
				if self._tasks[i].add( player, 1 ):
					return i		# ���ҵ�һ���ҵ���
				else:
					return -1
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_KILLS and monsterEntity.className in self._tasks[i].getKilledName():
				if self._tasks[i].add( player, 1 ):
					return i		# ���ҵ�һ���ҵ���
				else:
					return -1
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_CAMP_KILL and monsterEntity.className in self._tasks[i].getKilledName():
				if self._tasks[i].add( player, 1 ):
					return i		# ���ҵ�һ���ҵ���
				else:
					return -1
		return -1


	def increaseDartKilled( self, player, dartQuestID, factionID ):
		"""
		�����������һ����npcID���Ӧ������Ŀ�겢��ɱ����������1

		@return: ���������Ŀ�����ҵ�����ص�NPC��ʶ�򷵻�taskIndex�����򷵻�-1
		@rtype:  INT
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_DART_KILL and self.getType() == csdefine.QUEST_TYPE_ROB:
				#����ǽ���������ɱ���ڳ�
				if factionID and self._tasks[i].getFaction() != int( factionID ):
					return -1
				if self._tasks[i].add( player, dartQuestID, 1 ):
					return i		# ���ҵ�һ���ҵ���
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
					return i,j,m,n		# ��������Ŀ��INDEX �� ��ɴ���
				else:
					return -1,-1,-1,-1

		return -1, -1, -1, -1


	def addNormalAnswerQuestion( self, player, questionType, isRight ):
		"""
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_QUESTION:
				if self._tasks[i].add( player, questionType, isRight ): return i		# ���ҵ�һ���ҵ���
				else:             return -1
		return -1

	def getQuestionCount( self, questionType ):
		"""
		��������
			����Ѵ��������
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_QUESTION:
				if self._tasks[i].str1 == str( questionType ):
					return self._tasks[i].val2 - self._tasks[i].val1
		return -1

	def increaseEvolution( self, player, className ):
		"""
		�����������һ����npcID���Ӧ������Ŀ�겢��������������1

		@return: ���������Ŀ�����ҵ�����ص�NPC��ʶ�򷵻�taskIndex�����򷵻�-1
		@rtype:  INT
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_EVOLUTION and self._tasks[i].getEvolutClassName() == className:
				if self._tasks[i].add( player, 1 ):
					return i		# ���ҵ�һ���ҵ���
				else:
					return -1
		return -1

	def updateBuffState( self, buffID, val ):
		"""
		�����������һ����npcID���Ӧ������Ŀ�겢��������������1

		@return: ���������Ŀ�����ҵ�����ص�NPC��ʶ�򷵻�taskIndex�����򷵻�-1
		@rtype:  INT
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_HASBUFF and self._tasks[i].getBuffID() == buffID:
				if self._tasks[i].add( buffID, val ):
					return i		# ���ҵ�һ���ҵ���
				else:
					return -1
		return -1

	def updatePetActState( self, player, isActive ):
		"""
		�����������һ������ļ���״̬�����ı������Ŀ��֪ͨ��+1����-1

		@return: ���������Ŀ�����ҵ�����ص�NPC��ʶ�򷵻�taskIndex�����򷵻�-1
		@rtype:  INT
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_PET_ACT:
				addNumber = isActive and 1 or -1
				if self._tasks[i].add( player, addNumber ):
					return i		# ���ҵ�һ���ҵ���
				else:
					return -1
		return -1

	def roleDieAffectQuest( self, player ):
		"""
		����������һ����ɫ��������Ӱ�������Ŀ��

		@return: ���������Ŀ�����ҵ�����Ҫ��Ӱ�������Ŀ���򷵻�taskIndex�����򷵻�-1
		@rtype:  INT
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_TIME and self.getType() == csdefine.QUEST_TYPE_ROB and not player.isRobbingComplete():
				if self._tasks[i].isCompleted( player ):	# ���û�г�ʱ
					player.statusMessage( csstatus.ROLE_QUEST_ROBBING_DIE )
				if player.hasFlag( csdefine.ROLE_FLAG_CP_ROBBING ):
					player.removeFlag( csdefine.ROLE_FLAG_CP_ROBBING )
				else:
					player.removeFlag( csdefine.ROLE_FLAG_XL_ROBBING )
				#����ǽ��������ʱ��Ŀ��
				if self._tasks[i].setFailed():
					#��������ʧ�ܣ�������ʱ�����꣩
					return i	# ���ҵ�һ���ҵ���
				else:
					return -1
		return -1

	def addPetEvent( self, player, eventType ):
		"""
		�����������һ����npcID���Ӧ������Ŀ�겢��ɱ����������1

		@return: ���������Ŀ�����ҵ�����ص�NPC��ʶ�򷵻�taskIndex�����򷵻�-1
		@rtype:  INT
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_PET_EVENT and self._tasks[i].getEventType() == eventType :
				if self._tasks[i].add( 1 ): return i		# ���ҵ�һ���ҵ���
				else:             return -1
		return -1

	def handleDartFailed( self ):
		"""
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_TIME:
				if self._tasks[i].setFailed(): return i		# ���ҵ�һ���ҵ���
				else:             return -1
		return -1


	def increaseLevel( self, level ):
		"""
		�ȼ��仯
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_LEVEL:
				if self._tasks[i].setLevel( level ): return i		# ���ҵ�һ���ҵ���
				else:             return -1
		return -1


	def increaseSkillLearned( self, player, skillID ):
		"""
		�ȼ��仯
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_SKILL_LEARNED:
				if self._tasks[i].isCompleted( player ):continue
				if self._tasks[i].add( player, skillID ): return i		# ���ҵ�һ���ҵ���
		return -1
	
	
	def increaseLivingSkillLearned( self, player, skillID ):
		"""
		�ȼ��仯
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_LIVING_SKILL_LEARNED:
				if self._tasks[i].add( player, skillID ): 
					return i		# ���ҵ�һ���ҵ���
				else:
					return -1
		return -1


	def questFinish( self, questID ):
		"""
		�������
		"""
		for i in self._tasks:
			if self._tasks[i].getType() in [csdefine.QUEST_OBJECTIVE_QUEST, csdefine.QUEST_OBJECTIVE_QUEST_NORMAL]:
				if self._tasks[i].setQuestFinish( questID ): return i		# ���ҵ�һ���ҵ���
				else:             return -1
		return -1

	def addDeliverAmount( self, player, item, quantity ):
		"""
		Ϊһ��������Ʒ��Ŀ������������������Ϊ���٣�

		@return: �����ָ��������Ŀ�����ҵ�����item.id��ص�task�򷵻����task�������е�����λ�ã����򷵻�-1
		@rtype:  INT
		"""
		for i in  self._tasks:
			if self._tasks[i].getType() in [ csdefine.QUEST_OBJECTIVE_DELIVER, csdefine.QUEST_OBJECTIVE_CAMPACT_DELIVER ] and self._tasks[i].getDeliverID() == item.id:
				if self._tasks[i].add( player, quantity ): return i		# ���ظ�������Ŀ������
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
				if self._tasks[i].addPet( player, self.getQuestID(), dbid ): return i		# ���ظ�������Ŀ������
				else:                    return -1
		return -1

	def subDeliverPetAmount( self, player, className, dbid ):
		"""
		"""
		for i in  self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_DELIVER_PET and self._tasks[i].getDeliverPetID() == className:
				if self._tasks[i].subPet( player, self.getQuestID(), dbid ): return i		# ���ظ�������Ŀ������
				else:                    return -1
		return -1


	def addPetAmount( self, player, quantity ):
		"""
		"""
		for i in  self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_OWN_PET :
				if self._tasks[i].add( player, quantity ): return i		# ���ظ�������Ŀ������
				else:                    return -1
		return -1

	def clearTeamAmount( self, player ):

		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_TEAM:
				if self._tasks[i].clean( player ): return i		# ���ظ�������Ŀ������
				else:                    return -1


	def increaseItemUsed( self, player, itemID ):
		"""
		Ϊһ��ʹ����Ʒ������Ŀ������һ��ʹ��������

		@return: �����ָ��������Ŀ�����ҵ�����itemID��ص�task�򷵻����task�������е�����λ�ã����򷵻�-1
		@rtype:  INT
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_EVENT_USE_ITEM and self._tasks[i].getItemID() == itemID:
				if self._tasks[i].add( player, 1 ):
					return i		# ���ҵ�һ���ҵ���
				else:
					return -1
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_CAMPACT_EVENT_USE_ITEM and self._tasks[i].isValidSpace( player ) and self._tasks[i].getItemID() == itemID:
				if self._tasks[i].add( player, 1 ):
					return i		# ���ҵ�һ���ҵ���
				else:
					return -1
		return -1


	def addTalk( self, player, className ):
		"""
		"""
		for i in self._tasks:
			if self._tasks[i].getType() in [ csdefine.QUEST_OBJECTIVE_TALK, csdefine.QUEST_OBJECTIVE_CAMPACT_TALK ] and self._tasks[i].getClassName() == className:
				if self._tasks[i].add( player, 1 ):
					return i		# ���ҵ�һ���ҵ���
				else:
					return -1
		return -1


	def isIndexTaskComplete( self, player, index):
		"""
		����taskID(������ȡ��ĳ����Ŀ���������
		"""
		if self._tasks.has_key( index ):
			try:
				return self._tasks[index].isCompleted(player)
			except KeyError, errstr:
				raise KeyError, "quest %i has no task index %i." % (self._questID, index)
		else:
			return False

	def getSubmitInfo( self ):			#������Ʒ�ύ����Ϣ���ɷ������ṩ
		"""
		��ѯ�ύ����Ŀ����ύ��Ϣ
		"""
		for task in self._tasks.itervalues():
			if task.getType() == csdefine.QUEST_OBJECTIVE_SUBMIT:
				return ( task.getItem(), task.getQuality() )
		return None

	def getObjectiveDetail( self, player ):
		"""
		�������Ŀ������
		"""
		return [ task.getDetail( player ) for task in self._tasks.itervalues() ]

	def getIERightRate( self, obj ):
		"""
		��ÿƾٴ������ȷ��
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_IMPERIAL_EXAMINATION:
				return self._tasks[i].float( self._tasks[i].str1 ) / self._tasks[i].val2
		return 0.0


	def addPotentialFinish( self, player ):
		"""
		���һ��Ǳ������

		@return: ���������Ŀ�����ҵ�����ص�NPC��ʶ�򷵻�taskIndex�����򷵻�-1
		@rtype:  INT
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_POTENTIAL_FINISH:
				if self._tasks[i].add( 1 ): return i		# ���ҵ�һ���ҵ���
				else:             return -1
		return -1


	def increaseSkillUsed( self, player, skillID, className ):
		"""
		ʹ��ĳ����
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_EVENT_USE_SKILL and self._tasks[i].getSkillID() == skillID and ( className == self._tasks[i].getClassName() or self._tasks[i].getClassName() == ""):
				if self._tasks[i].add( player, 1 ):
					return i		# ���ҵ�һ���ҵ���
				else:
					return -1
		return -1


	def updateSetRevivePos( self, player, spaceName ):
		"""
		���ð󶨵㴥��
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_EVENT_REVIVE_POS and spaceName == self._tasks[i].getSpaceName():
				if self._tasks[i].add( player, 1 ):
					return i		# ���ҵ�һ���ҵ���
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
					return i		# ���ҵ�һ���ҵ���
				else:
					return -1
		return -1

	def onChangeCampMorale( self, player, camp, amount ):
		"""
		���ӻ������Ӫʿ��
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_ADD_CAMP_MORALE:
				if self._tasks[i].add( player, camp, amount ):
					return i		# ���ҵ�һ���ҵ���
				else:
					return -1
		return -1
	
	def increaseVehicleActived( self, player, vehicleID ):
		"""
		��輤��
		"""
		for i in self._tasks:
			if self._tasks[i].getType() == csdefine.QUEST_OBJECTIVE_VEHICLE_ACTIVED:
				if self._tasks[i].add( player, vehicleID ):
					return i		# ���ҵ�һ���ҵ���
				else:
					return -1
		return -1
		
	##################################################################
	# BigWorld User Defined Type �Ľӿ�                              #
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
			return None	# ���ڱ�ʶ�ڴ���������ʱ�Ƿ����������������һ��Ϳ��԰�����ɾ��(����)

		return obj

	def getDictFromObj( obj ):
		if obj:
			return { "qID":obj._questID, "datas":obj._datas, "tasks":obj._tasks.values(), "acceptTime" : obj._acceptTime }
		# obj is None����ʾ���������⣬ֱ�ӷ���Ĭ�����ݣ�qIDΪ0��ʾû��ָ���κ�����
		return { "qID":0, "datas":{}, "tasks":[], "acceptTime" : 0 }

#
# $Log: QuestDataType.py,v $
# Revision 1.22  2008/08/20 01:27:24  zhangyuxing
# ���ӳ���ָ�����񴥷�
#
# Revision 1.21  2008/08/15 09:23:13  zhangyuxing
# �ϲ�����������Ʒ�ύ�Ĳ�ѯ
#
# Revision 1.20  2008/08/09 08:43:25  songpeifang
# ���ӽӿڻ����������id
#
# Revision 1.19  2008/08/07 09:04:01  zhangyuxing
# �Գ����������ͱ仯����֧��
#
# Revision 1.18  2008/08/04 06:33:08  zhangyuxing
# ���ӻ���������ɴ���
#
# Revision 1.17  2008/07/30 06:02:23  zhangyuxing
# �޸Ļ����������¼��ѯ�ĺ���������
#
# Revision 1.16  2008/07/28 01:08:46  zhangyuxing
# ���ӵȼ�����Ŀ��
#
# Revision 1.15  2008/07/22 03:22:38  yangkai
# ������� acceptTime
#
# Revision 1.14  2008/07/14 04:36:52  zhangyuxing
# ����ȼ��仯��������ɲ�ѯ
#
# Revision 1.13  2008/01/30 02:59:35  zhangyuxing
# ���ӣ� ����ֱ���ύ�������ɲ�ѯ
#
# Revision 1.12  2008/01/22 08:20:40  zhangyuxing
# �����˳�����Ŀ�仯�Ĵ���
#
# Revision 1.11  2008/01/11 07:00:34  zhangyuxing
# �޸ļ�����
#
# Revision 1.10  2008/01/09 04:05:23  zhangyuxing
# �����������Ŀ�����ز���
#
# Revision 1.9  2007/12/29 02:42:27  phw
# method modified: isIndexTaskComplete(), �����˶��ض��������ϸ���
#
# Revision 1.8  2007/12/26 09:06:31  phw
# method modified: addDeliverAmount(), ������ʹ�ò���ȷ�Ĳ�ѯ��ʽ����ѯ��Ʒʵ�����Ե�����
#
# Revision 1.7  2007/12/18 02:20:08  zhangyuxing
# �޸ļ򵥴���
#
# Revision 1.6  2007/12/17 11:36:08  zhangyuxing
# �޸ģ� addDeliverAmount , ֧�� QUEST_OBJECTIVE_SUBMIT ��������Ŀ��
#
# Revision 1.5  2007/12/08 09:32:54  phw
# ��Ի����ݽ����˴�������������ʱ�����־��������None
#
# Revision 1.4  2007/12/05 00:35:06  zhangyuxing
# ������״̬�����仯�ļ���У�
# ����������Ŀ��ķ�ʽ���޸ġ����ҷ���Ҳֱ�ӷ��ش��Ŀ���key.
#
# Revision 1.3  2007/12/04 03:07:22  zhangyuxing
# 1.֧��������Ŀ������֧�֣���Ӧ�ķ��� tasks_�ķ�ʽҲ���ı䡣
# 2.�� ���ݴ����� QuestDataType �Ĵ���������ֵ�ķ�ʽ������Դ���
#
# Revision 1.2  2007/11/02 03:38:46  phw
# method removed: questIncreaseItemUsed() -> increaseItemUsed()
#
# Revision 1.1  2007/11/02 03:33:34  phw
# �������QuestTasksDataType.py
#
#
