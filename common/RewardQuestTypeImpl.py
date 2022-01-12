# -*- coding: gb18030 -*-
#

"""
悬赏任务数据类型
实现自定义数据类型接口，解决传输问题。
"""

import Language
from bwdebug import *
import time

class RewardQuestTypeImpl:
	def __init__( self ):
		self.questID = 0	# 任务唯一编号，用于区分当前数据是属于哪个任务的
		self.bigType = 0	# 任务大类
		self.quality = 0	# 任务品质
		self.spawnTime = 0	# 格式：2007101309；任务开始时间，用于判断是否在同一天的同一个时段（真实时间的一天）
		self.rewardsDetail = []	#悬赏任务奖励描述
		self.title = ""

	
	def setQuestID( self, questID ):
		"""
		设置任务ID
		"""
		self.questID = questID
	
	def getQuestID( self ):
		"""
		获取任务ID
		"""
		return self.questID
		
	def setBigType( self, bigType ):
		"""
		设置任务大类
		"""
		self.bigType = bigType
	
	def getBigType( self ):
		"""
		获取任务大类
		"""
		return self.bigType
		
	def setSmallType( self, smallType ):
		"""
		设置任务小类
		"""
		self.smallType = smallType
	
	def getSmallType( self ):
		"""
		获取任务小类
		"""
		return self.smallType
		
	def setQuality( self, quality ):
		"""
		设置任务品质
		"""
		self.quality = quality
	
	def getQuality( self ):
		"""
		获取任务品质
		"""
		return self.quality
		
	def setRewardsDetail( self, rewardsDetail ):
		"""
		设置任务奖励描述
		"""
		self.rewardsDetail = rewardsDetail
	
	def getRewardsDetail( self ):
		"""
		获取任务奖励描述
		"""
		return self.rewardsDetail
		
	def setTitle( self, title ):
		"""
		设置任务标题
		"""
		self.title = title
		
	def getTitle( self ):
		"""
		获取任务标题
		"""
		return self.title
		
	def reset( self ):
		"""
		重置数据，设置开始时间为今天，设置当前完成次数为0
		"""
		year, month, day, hour = time.localtime()[:4]
		self.spawnTime = year * 1000000 + month * 10000 + day * 100 + hour
	
	def checkStartTime( self ):
		"""
		检查接任务时间与当前时间是否是同一天
		@return: bool
		"""
		year, month, day, hour = time.localtime()[:4]
		curr = year * 1000000 + month * 10000 + day * 100 + hour
		return curr == self.spawnTime

	##################################################################
	# BigWorld User Defined Type 的接口                              #
	##################################################################
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.

		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		return { "questID":obj.questID, "bigType":obj.bigType, "smallType":obj.smallType, "quality":obj.quality, "rewardsDetail":obj.rewardsDetail, "title":obj.title, "spawnTime":obj.spawnTime }

	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.

		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = RewardQuestTypeImpl()
		obj.questID = dict["questID"]
		obj.bigType = dict["bigType"]
		obj.smallType = dict["smallType"]
		obj.quality = dict["quality"]
		obj.spawnTime = dict["spawnTime"]
		obj.rewardsDetail = dict["rewardsDetail"]
		obj.title = dict["title"]
		return obj

	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, RewardQuestTypeImpl )

instance = RewardQuestTypeImpl()


#
# $Log: not supported by cvs2svn $
#
