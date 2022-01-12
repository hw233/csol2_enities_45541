# -*- coding: gb18030 -*-
#
# $Id: QuestsDataType.py,v 1.25 2008-08-20 01:27:24 zhangyuxing Exp $

"""
����������ϣ��������е������б�͵�ǰ���״̬��
ʵ���Զ����������ͽӿڣ�����������⡣
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
		�ж��Ƿ���ָ����quest

		@return: BOOL
		"""
		return questID in self._quests

	def keys( self ) :
		"""
		��ȡ�������� ID�� hyw -- 2008.06.10 ��
		"""
		return self._quests.keys()

	def items( self ) :
		"""
		��ȡ�������� hyw -- 2008.06.10 ��
		"""
		return self._quests.items()

	def add( self, questID, tasks ):
		"""
		����һ������

		@param tasks: ����Ŀ���б�
		@type  tasks: QuestDataType
		@return: None
		"""
		self._quests[questID] = tasks

	def remove( self, questID ):
		"""
		ɾ��һ������
		"""
		try:
			del self._quests[questID]
		except KeyError:
			ERROR_MSG( "quest not found, questID =", questID )

	def query( self, questID, key, default = None ):
		"""
		��ѯ��չ����

		@return: ����ؼ��ֲ������򷵻�defaultֵ
		"""
		tasks = self._quests[questID]
		return tasks.query( key, default = None )

	def set( self, questID, key, value ):
		"""
		д����չ����

		@param   key: �κ�PYTHONԭ����(����ʹ���ַ���)
		@param value: �κ�PYTHONԭ����(����ʹ�����ֻ��ַ���)
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
		�����������һ����npcID���Ӧ������Ŀ�겢��ɱ����������1

		@return: ���������Ŀ�����ҵ�����ص�NPC��ʶ�򷵻�(questID, taskIndex)�����򷵻�None
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
		�����������һ����npcID���Ӧ������Ŀ�겢��ɱ����������1

		@return: ���������Ŀ�����ҵ�����ص�NPC��ʶ�򷵻�(questID, taskIndex)�����򷵻�None
		@rtype:  None/Tuple
		"""
		resultList = []
		
		for questID, quest in self._quests.iteritems():
			if quest.getType() == csdefine.QUEST_TYPE_ROB:		# ��������ɹ���Ҫ��ȥ������ϵĽ��ڱ��
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
		�����������һ������ļ���״̬�����ı������Ŀ��֪ͨ���Ƿ����Ŀ��
		@return: ���������Ŀ�����ҵ�����ص�NPC��ʶ�򷵻�(questID, taskIndex)�����򷵻�None
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
		�����������һ����npcID���Ӧ������Ŀ�겢��������������1

		@return: ���������Ŀ�����ҵ�����ص�NPC��ʶ�򷵻�(questID, taskIndex)�����򷵻�None
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
		����������һ����ɫ��������Ӱ�������Ŀ��

		@return: ���������Ŀ�����ҵ�����Ҫ��Ӱ�������Ŀ���򷵻�(questID, taskIndex)�����򷵻�None
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
		Ϊһ��������Ʒ��Ŀ������������������Ϊ���٣�

		@return: ���������Ŀ�����ҵ�����ص���Ʒ��ʶ�򷵻�(questID, taskIndex)�����򷵻�None
		@rtype:  None/Tuple
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.addDeliverAmount( player, item, quantity ) #index ��Ϊ��������Ŀ�������
			if index != -1:
				resultList.append( (questID, index) )
		return resultList

	def addYinpiaoDeliverAmount( self, player, item ):
		"""
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.addYinpiaoDeliverAmount( player, item ) #index ��Ϊ��������Ŀ�������
			if index != -1:
				resultList.append( (questID, index) )
		return resultList
		

	def addPetEvent( self, player, eventType ):
		"""
		�����¼�����
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.addPetEvent( player, eventType ) #index ��Ϊ��������Ŀ�������
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
		ʹ��ĳ����
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
		���������仯����
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.addPetAmount( player, quantity ) #index ��Ϊ��������Ŀ�������
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
		Ϊһ��ʹ����Ʒ������Ŀ������һ��ʹ��������

		@return: �����ָ��������Ŀ�����ҵ�����itemID��ص�task�򷵻����task�������е�����λ�ã����򷵻�-1
		@rtype:  int
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.increaseItemUsed( player, itemID )
			if index != -1 and index != None:	# index�п���ΪNone -spf
				resultList.append( (questID, index) )
		return resultList


	def addTalk( self, player, targetClassName ):
		"""
		��ָ��NPC�Ի����������
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.addTalk( player, targetClassName )
			if index != -1:
				resultList.append( (questID, index) )
		return resultList
		
	
	def updateBuffState( self, buffID, val ):
		"""
		�����������һ����npcID���Ӧ������Ŀ�겢��������������1

		@return: ���������Ŀ�����ҵ�����ص�NPC��ʶ�򷵻�(questID, taskIndex)�����򷵻�None
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
		ȡ����������Ʒ�������ID�б��Լ�������͸���������ֵ�

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
		�����¼�����
		"""
		resultList = []
		for questID, quest in self._quests.iteritems():
			index = quest.addPotentialFinish( player ) #index ��Ϊ��������Ŀ�������
			if index != -1:
				resultList.append( (questID, index) )
		return resultList


	def getQuestionCount( self, questionType ):
		"""
		��������
			���ʣ����������
		"""
		count = -1
		for questID, quest in self._quests.iteritems():
			count = quest.getQuestionCount( questionType )
			if count != -1:
				return count
		return count


	def updateSetRevivePos( self, player, spaceName ):
		"""
		���ð󶨵㴥��
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
	# BigWorld User Defined Type �Ľӿ�                              #
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
			if value:	# ���valueΪNone���ʾ�����д�����ֱ�Ӻ���
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
# �Գ����������ͱ仯����֧��
#
# Revision 1.23  2008/07/31 09:27:33  zhangyuxing
# no message
#
# Revision 1.22  2008/07/28 01:08:56  zhangyuxing
# ���ӵȼ�����Ŀ��
#
# Revision 1.21  2008/07/14 04:36:52  zhangyuxing
# ����ȼ��仯��������ɲ�ѯ
#
# Revision 1.20  2008/06/10 09:00:45  huangyongwei
# ����ˣ�
# keys()
# ��
# items()
# ����
#
# Revision 1.19  2008/01/31 03:12:14  zhangyuxing
# ���������Ʒ����������Ĵ���
#
# Revision 1.18  2008/01/22 08:20:44  zhangyuxing
# �����˳�����Ŀ�仯�Ĵ���
#
# Revision 1.17  2008/01/11 06:59:24  zhangyuxing
# ɱ�������ˢ�·���Ϊ�б�
#
# Revision 1.16  2008/01/09 04:05:29  zhangyuxing
# �����������Ŀ�����ز���
#
# Revision 1.15  2007/12/17 11:37:03  zhangyuxing
# ������ addDeliverAmount �Ĳ��� ����
#
# Revision 1.14  2007/12/08 09:33:21  phw
# ��Ի����ݽ����˴������QuestDataʵ��ΪNone����Ϊ�ǻ����ݣ����Ե�������
#
# Revision 1.13  2007/12/05 00:35:26  zhangyuxing
# ������״̬�����仯�ļ���У�
# ����������Ŀ��ķ�ʽ���޸ġ����ҷ���Ҳֱ�ӷ��ش��Ŀ���key.
#
# Revision 1.12  2007/11/02 05:59:33  phw
# ������import�����ڵ� QuestTasksDataType ������
#
# Revision 1.11  2007/11/02 03:37:52  phw
# method removed: has_deliver(), has_kill()
# method removed: questIncreaseItemUsed() -> increaseItemUsed()
#
# Revision 1.10  2007/06/14 10:46:50  huangyongwei
# ������ȫ�ֱ���
#
# Revision 1.9  2007/03/07 02:29:58  kebiao
# �޸���ʹ��FIXED_DICT����
#
# Revision 1.8  2006/10/13 08:35:55  chenzheming
# �޸Ĺ�������ʱ�����increaseKilled���������Ĳ���
#
# Revision 1.7  2006/09/07 07:18:00  chenzheming
# no message
#
# Revision 1.6  2006/03/28 09:03:52  phw
# ����increaseActiveItem()
#
# Revision 1.5  2006/03/22 02:34:02  phw
# ��Ӧ1.7����Զ������ͣ�����Ӧ�޸�
#
# Revision 1.4  2006/03/20 03:18:54  wanhaipeng
# Mark stream.����Ҫ�Ķԣ�����
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
