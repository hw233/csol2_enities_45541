# -*- coding: gb18030 -*-


import Language
import time
import copy
import csdefine
from bwdebug import *
from config.server.RewardQuestTimeAndProbility import Datas as datas_timeAndProbility
from config.server.RewardQuestRelatedQuestConfig import Datas as datas_relatedQuestConfig


class RewardQuestLoader:
	"""
	����������ؼ�����
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert RewardQuestLoader._instance is None
		# key == ��Ӧ��npc className
		# value == dict
		# 	key == questID
		#	value == array of tuple like as [(rate, itemID, amount), ...]
		# like as { npcID : { questID : [ (rate, itemID, amount), ... ], ... }, ...}
		self._questDatas = {}
		self._timeData = []
		self._probilityDatas = {}
		self._randomQuestDatas = {}
		RewardQuestLoader._instance = self



	def initTimeAndProbilityData( self ):
		"""
		��ʼ����������ʱ��͸�������
		"""
		data = datas_timeAndProbility[ 0 ]
		timeData = data[ "spawnTime" ].split(";")
		for refreshTime in timeData:
			t = [int(e) for e in refreshTime.split(":")]
			self._timeData.append( t )
		self._probilityDatas[ "lowItemRefresh" ] = {}
		self._probilityDatas[ "lowItemRefresh" ][ "white" ] = data[ "lowItemRefresh" ]["white"]
		self._probilityDatas[ "lowItemRefresh" ][ "blue" ] = data[ "lowItemRefresh" ]["blue"]
		self._probilityDatas[ "lowItemRefresh" ][ "purple" ] = data[ "lowItemRefresh" ]["purple"]
		self._probilityDatas[ "lowItemRefresh" ][ "green" ] = data[ "lowItemRefresh" ]["green"]
		self._probilityDatas[ "lowItemRefresh" ][ "minNum" ] = data[ "lowItemRefresh" ]["minNum"]
		self._probilityDatas[ "lowItemRefresh" ][ "maxNum" ] = data[ "lowItemRefresh" ]["maxNum"]
		self._probilityDatas[ "highItemRefresh" ] = {}
		self._probilityDatas[ "highItemRefresh" ][ "white" ] = data[ "highItemRefresh" ]["white"]
		self._probilityDatas[ "highItemRefresh" ][ "blue" ] = data[ "highItemRefresh" ]["blue"]
		self._probilityDatas[ "highItemRefresh" ][ "purple" ] = data[ "highItemRefresh" ]["purple"]
		self._probilityDatas[ "highItemRefresh" ][ "green" ] = data[ "highItemRefresh" ]["green"]
		self._probilityDatas[ "highItemRefresh" ][ "minNum" ] = data[ "highItemRefresh" ]["minNum"]
		self._probilityDatas[ "highItemRefresh" ][ "maxNum" ] = data[ "highItemRefresh" ]["maxNum"]
		self._probilityDatas[ "systemRefresh" ] = {}
		self._probilityDatas[ "systemRefresh" ][ "white" ] = data[ "systemRefresh" ]["white"]
		self._probilityDatas[ "systemRefresh" ][ "blue" ] = data[ "systemRefresh" ]["blue"]
		self._probilityDatas[ "systemRefresh" ][ "purple" ] = data[ "systemRefresh" ]["purple"]
		self._probilityDatas[ "systemRefresh" ][ "green" ] = data[ "systemRefresh" ]["green"]
		self._probilityDatas[ "systemRefresh" ][ "minNum" ] = data[ "systemRefresh" ]["minNum"]
		self._probilityDatas[ "systemRefresh" ][ "maxNum" ] = data[ "systemRefresh" ]["maxNum"]
		
	def initQuestData( self ):
		"""
		��ʼ�������������������
		"""
		for questData in datas_relatedQuestConfig:
			bigType = questData[ "bigType" ]
			smallType = questData[ "smallType" ]
			isRandomQuest = questData[ "isRandomQuest" ]
			if bigType not in self._questDatas:
				self._questDatas[ bigType ] = {}
			if smallType not in self._questDatas[ bigType ]:
				self._questDatas[ bigType ][ smallType ] = {}
			if bigType not in self._randomQuestDatas:
				self._randomQuestDatas[ bigType ] = {}
			self._randomQuestDatas[ bigType ][ smallType ] = isRandomQuest
			minLevel = questData[ "minLevel" ]
			maxLevel = questData[ "maxLevel" ]
			for level in xrange( minLevel, maxLevel + 1 ):
				if level not in self._questDatas[ bigType ][ smallType ]:
					self._questDatas[ bigType ][ smallType ][ level ] = []
				if bigType == csdefine.REWARD_QUEST_TYPE_CAMP:
					self._questDatas[ bigType ][ smallType ][ level ].append( ( questData[ "questID" ], questData[ "belongCamp" ] ) )
				else:
					self._questDatas[ bigType ][ smallType ][ level ].append( questData[ "questID" ] )

	def getTimeData( self ):
		"""
		�������ö�ȡˢ��ʱ��
		"""
		return self._timeData
		
	def getTimeDataFromToday( self ):
		"""
		�������ö�ȡ�����ˢ��ʱ��
		"""
		t = time.localtime()
		timeData = []
		for times in self._timeData:
			if len( times ) > 1:
				s = ( t[0], t[1], t[2], times[0], times[1], 0, t[6], t[7], t[8] )
			else:
				s = ( t[0], t[1], t[2], times[0], 0, 0, t[6], t[7], t[8] )
			timeData.append( time.mktime( s ) )
		return timeData
	
	def getQuestDatas( self ):
		"""
		�������ö�ȡ��������
		"""
		return self._questDatas
		
	def getRandomQuestDatas( self ):
		"""
		�������ö�ȡ�����Ƿ������������
		"""
		return self._randomQuestDatas
	
	def getQuestDataFromLevelAndType( self, bigType, smallType, level ):
		"""
		�������ö�ȡ��Ӧ��������ӦС�����Ӧ�ȼ����Խ�ȡ����
		"""
		if not self._questDatas.has_key( bigType ):
			return []
		if not self._questDatas[ bigType ].has_key( smallType ):
			return []
		if not self._questDatas[ bigType ][ smallType ].has_key( level ):
			return []
		return copy.deepcopy( self._questDatas[ bigType ][ smallType ][ level ] )
	
	def getProbilityDats( self ):
		"""
		�������ö�ȡϵͳˢ�¡����ȵ���ˢ�¡��ߵȵ���ˢ������Ʒ�ʵĸ���
		"""
		return self._probilityDatas
		
	def getSystemProbilityData( self ):
		"""
		�������ö�ȡϵͳˢ������Ʒ�ʵĸ���
		"""
		return self._probilityDatas[ "systemRefresh" ]

	def getLowItemProbilityData( self ):
		"""
		�������ö�ȡϵͳˢ������Ʒ�ʵĸ���
		"""
		return self._probilityDatas[ "lowItemRefresh" ]

	def getHighItemProbilityData( self ):
		"""
		�������ö�ȡϵͳˢ������Ʒ�ʵĸ���
		"""
		return self._probilityDatas[ "highItemRefresh" ]

	@staticmethod
	def instance():
		"""
		"""
		if RewardQuestLoader._instance is None:
			RewardQuestLoader._instance = RewardQuestLoader()
		return RewardQuestLoader._instance


