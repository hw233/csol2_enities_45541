# -*- coding: gb18030 -*-
#
# $Id: QuestLoader.py,v 1.25 2008-09-05 02:51:09 kebiao Exp $

"""
"""

import sys
from bwdebug import *
import csdefine
import csstatus
import Language
import Function
from ObjectScripts.GameObjectFactory import g_objFactory

# ----------------------------->
# QuestsFlyweight
# ----------------------------->
class QuestsFlyweight:
	"""
	"""
	_instance = None
	def __init__( self ):
		assert QuestsFlyweight._instance is None, "instance already exist in"
		self._quests = {}		# key == questID, Long type; value == instance of Quest
		self._questPotentials = {} #Ǳ������ע��� ר���ṩ��Ǳ������ʵ��ĳЩ���������ܵ�.
		self._questSecondData = {}	# ��ɫ�����Ӧ���뾭��,���Ǯ��������{ playerLelve: [ secondExp, secondMoney ] }
		
	def __getitem__( self, questID ):
		return self._quests[questID]

	def load( self, configFilePath ):
		"""
		��һ�������б����������
		"""
		
		random_group_quest = {}
		tong_space_copy_quest_grp = None
		tong_space_copy_quest	= []

		files = Language.searchConfigFile( configFilePath, ".xml" )			# ��ȡ�õ�����·���������ļ�

		for filename in files:
			fileSection = Language.openConfigSection( filename  )
			if fileSection is None:
				#raise SystemError, "Can not Load : %s " % filename
				ERROR_MSG( "Can't load the quest config %s" % (filename) )
				continue
			
			for section in fileSection.values():
				quest_type = section.readString( "instance_type" ).lower()
				q = QuestModule.getQuestModule( quest_type )()
				try:
					q.init( section )
				except Exception, errstr:
					ERROR_MSG( "while loading '%s' error." % section.readString( "id" ), errstr )
					sys.excepthook( Exception, errstr, sys.exc_traceback )

				if q.getID() in self._quests:
					ERROR_MSG( "Quest ID conflict.", q.getID() )
					continue
				self._quests[q.getID()] = q

				# д�������Ŀ��
				objectIDs = q.getObjectIdsOfStart()
				for iObjectID in objectIDs:
					if len( iObjectID ):
						npc = self._getNPCInstance( iObjectID )
						if not npc:
							ERROR_MSG( q.getID(), "Quest start object not found.", iObjectID  )
						else:
							npc.addStartQuest( q.getID() )

				# д�뽻����Ŀ��
				objectIDs = q.getObjectIdsOfFinish()
				for iObjectID in objectIDs:
					if len( iObjectID ):
						npc = self._getNPCInstance( iObjectID )
						if not npc:
							ERROR_MSG( q.getID(), "Quest finish object not found.", iObjectID )
						else:
							npc.addFinishQuest( q.getID() )


				if quest_type == "random":
					questID = q.getGroupID()	# ȡ�������������ID��
					if not random_group_quest.has_key( questID ):
						random_group_quest[ questID ] = [ q.getID() ]
					else:
						random_group_quest[ questID ].append( q.getID() )

				# ����ḱ������������
				if quest_type == "tong_space_copy":
					tong_space_copy_quest.append( q )
				if quest_type == "tong_space_copy_grp":
					tong_space_copy_quest_grp = q


			Language.purgeConfig( filename )	# ��ջ�����

		INFO_MSG( "Load standard quest config finish." )

		for i in random_group_quest:
			if self._quests.has_key( i ):
				for key in random_group_quest[i]:
					try:
						self._quests[i].addChild( key, self._quests[key] )
					except:
						ERROR_MSG( "Random quest: %s init failed!"%key )
			else:
				ERROR_MSG( "QuestGroup id: '%s' is not found. ChildQuest id List:"%i, random_group_quest[i] )


		# ��ʼ����ḱ������
		if tong_space_copy_quest_grp != None:
			for quest in tong_space_copy_quest:
				tong_space_copy_quest_grp.addChild( quest )
		else:
			ERROR_MSG( "tong_space_copy_group not found, all tong_space_copy quest ignored!" )


		# ����Ǳ�׼������
		self.initCustomQuest()

		# �뾭�����Ǯ���ó�ʼ��
		self.initSecondData()

	def initSecondData( self ):
		"""
		�뾭�����Ǯ���ó�ʼ��
		"""
		configPath = "config/quest/QuestLoopDatas/QuestLoopDatas.xml"
		section = Language.openConfigSection( configPath )
		assert section is not None, "open %s Faild." % configPath
		successCount = 0
		faildedCount = 0
		for sec in section.values():
			level = sec["level"].asInt
			sExp = sec["sExp"].asFloat
			sMoney = sec["sMoney"].asInt
			if level is None or sExp is None or sMoney is None:
				faildedCount += 1
				continue
			self._questSecondData[ sec["level"].asInt ] = [ sec["sExp"].asFloat, sec["sMoney"].asInt ]
			successCount += 1
		INFO_MSG( "Load configPath,successCount:%i,faildedCount:%i." % ( successCount, faildedCount ) )


	def getSecondExpByLevel( self, level ):
		"""
		���ݵȼ�����뾭��

		@param level : entity����
		@type level : UNT16
		"""
		try:
			return self._questSecondData[level][0]
		except KeyError:
			ERROR_MSG( "can not find level:%i." % level )
			return None

	def getSecondMoneyByLevel( self, level ):
		"""
		���ݵȼ�������Ǯ

		@param level : entity����
		@type level : UNT16
		"""
		try:
			return self._questSecondData[level][1]
		except KeyError:
			ERROR_MSG( "can not find level:%i." % level )
			return None

	def initCustomQuest( self ):
		"""
		�Զ���ű�����
		"""
		count1 = 0
		from QuestModule import CustomQuestSet
		for q in CustomQuestSet.__all__:
			id = q.getID()
			self._quests[id] = q
			count1 += 1

			# д�������Ŀ��
			objectID = q.getObjectIdsOfStart()
			if len( objectID ):
				npc = self._getNPCInstance( objectID )
				if not npc:
					ERROR_MSG( q.getID(), "Quest start object not found.", q.getObjectIdsOfStart() )
				else:
					npc.addStartQuest( q.getID() )

			# д�뽻����Ŀ��
			objectID = q.getObjectIdsOfFinish()
			if len( objectID ):
				npc = self._getNPCInstance( objectID )
				if not npc:
					ERROR_MSG( q.getID(), "Quest finish object not found.", q.getObjectIdsOfFinish() )
				else:
					npc.addFinishQuest( q.getID() )
		INFO_MSG( "Load CustomQuest config finish. %i success." % count1 )

	def _getNPCInstance( self, keyName ):
		"""
		@return: instance/None
		"""
		return g_objFactory.getObject( keyName )

	def getQuestTitle( self, questID ):
		return self._quests[questID].getTitle()

	def questAbandoned( self, questID, player ):
		"""
		@see also: Quest::abandon method
		"""
		self._quests[questID].abandoned( player )

	def registerPotentialQuest( self, lvMin, lvMax, questID ):
		"""
		ע��Ǳ������
		#Ǳ������ע��� ר���ṩ��Ǳ������ʵ��ĳЩ���������ܵ�.
		"""
		for x in xrange( lvMin, lvMax + 1 ):
			self._questPotentials[ x ] = questID #Ǳ������ע��� ר���ṩ��Ǳ������ʵ��ĳЩ���������ܵ�.

	def getPotentialLvQuestMapping( self, level ):
		"""
		����ĳһ�����ȡǱ��������Ӧ������������ID
		"""
		return self._questPotentials[ level ]

	@staticmethod
	def instance():
		if QuestsFlyweight._instance is None:
			QuestsFlyweight._instance = QuestsFlyweight()
		return QuestsFlyweight._instance

import QuestModule