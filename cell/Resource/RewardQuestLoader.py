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
	悬赏任务相关加载器
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert RewardQuestLoader._instance is None
		# key == 对应的npc className
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
		初始化悬赏任务时间和概率数据
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
		初始化悬赏任务的任务数据
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
		根据配置读取刷新时间
		"""
		return self._timeData
		
	def getTimeDataFromToday( self ):
		"""
		根据配置读取当天的刷新时间
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
		根据配置读取任务数据
		"""
		return self._questDatas
		
	def getRandomQuestDatas( self ):
		"""
		根据配置读取任务是否是随机组任务
		"""
		return self._randomQuestDatas
	
	def getQuestDataFromLevelAndType( self, bigType, smallType, level ):
		"""
		根据配置读取相应大类中相应小类的相应等级可以接取任务
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
		根据配置读取系统刷新、初等道具刷新、高等道具刷新任务品质的概率
		"""
		return self._probilityDatas
		
	def getSystemProbilityData( self ):
		"""
		根据配置读取系统刷新任务品质的概率
		"""
		return self._probilityDatas[ "systemRefresh" ]

	def getLowItemProbilityData( self ):
		"""
		根据配置读取系统刷新任务品质的概率
		"""
		return self._probilityDatas[ "lowItemRefresh" ]

	def getHighItemProbilityData( self ):
		"""
		根据配置读取系统刷新任务品质的概率
		"""
		return self._probilityDatas[ "highItemRefresh" ]

	@staticmethod
	def instance():
		"""
		"""
		if RewardQuestLoader._instance is None:
			RewardQuestLoader._instance = RewardQuestLoader()
		return RewardQuestLoader._instance


