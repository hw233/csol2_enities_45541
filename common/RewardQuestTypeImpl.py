# -*- coding: gb18030 -*-
#

"""
����������������
ʵ���Զ����������ͽӿڣ�����������⡣
"""

import Language
from bwdebug import *
import time

class RewardQuestTypeImpl:
	def __init__( self ):
		self.questID = 0	# ����Ψһ��ţ��������ֵ�ǰ�����������ĸ������
		self.bigType = 0	# �������
		self.quality = 0	# ����Ʒ��
		self.spawnTime = 0	# ��ʽ��2007101309������ʼʱ�䣬�����ж��Ƿ���ͬһ���ͬһ��ʱ�Σ���ʵʱ���һ�죩
		self.rewardsDetail = []	#��������������
		self.title = ""

	
	def setQuestID( self, questID ):
		"""
		��������ID
		"""
		self.questID = questID
	
	def getQuestID( self ):
		"""
		��ȡ����ID
		"""
		return self.questID
		
	def setBigType( self, bigType ):
		"""
		�����������
		"""
		self.bigType = bigType
	
	def getBigType( self ):
		"""
		��ȡ�������
		"""
		return self.bigType
		
	def setSmallType( self, smallType ):
		"""
		��������С��
		"""
		self.smallType = smallType
	
	def getSmallType( self ):
		"""
		��ȡ����С��
		"""
		return self.smallType
		
	def setQuality( self, quality ):
		"""
		��������Ʒ��
		"""
		self.quality = quality
	
	def getQuality( self ):
		"""
		��ȡ����Ʒ��
		"""
		return self.quality
		
	def setRewardsDetail( self, rewardsDetail ):
		"""
		��������������
		"""
		self.rewardsDetail = rewardsDetail
	
	def getRewardsDetail( self ):
		"""
		��ȡ����������
		"""
		return self.rewardsDetail
		
	def setTitle( self, title ):
		"""
		�����������
		"""
		self.title = title
		
	def getTitle( self ):
		"""
		��ȡ�������
		"""
		return self.title
		
	def reset( self ):
		"""
		�������ݣ����ÿ�ʼʱ��Ϊ���죬���õ�ǰ��ɴ���Ϊ0
		"""
		year, month, day, hour = time.localtime()[:4]
		self.spawnTime = year * 1000000 + month * 10000 + day * 100 + hour
	
	def checkStartTime( self ):
		"""
		��������ʱ���뵱ǰʱ���Ƿ���ͬһ��
		@return: bool
		"""
		year, month, day, hour = time.localtime()[:4]
		curr = year * 1000000 + month * 10000 + day * 100 + hour
		return curr == self.spawnTime

	##################################################################
	# BigWorld User Defined Type �Ľӿ�                              #
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
