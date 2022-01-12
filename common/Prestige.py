# -*- coding: gb18030 -*-
#
# $Id: Prestige.py,v 1.1 2008-08-30 10:05:25 wangshufeng Exp $

import BigWorld
import csdefine
import csconst
import csstatus

from bwdebug import *

from FactionMgr import factionMgr						# npc势力配置


class Prestige( dict ):
	"""
	玩家声望自定义类型传输解析脚本
	"""
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.

		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		prestigeItems = []
		d = { "items":prestigeItems }
		for prestigeID, value in obj.iteritems():
			prestigeItems.append( { "id": prestigeID, "value": value } )
		return d

	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.
		
		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = Prestige()
		for v in dict[ "items" ]:
			obj[ v["id"] ] = v["value"]
		return obj

	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, Prestige )
		
	def addPrestige( self, factionID, value ):
		"""
		增加声望
		
		@param factionID : 势力factionID
		@type factionID : UINT8
		@param value : 增加的声望值
		@type value : INT32
		"""
		if self[ factionID ] >= csconst.PRESTIGE_UPLIMIT and value > 0:	# 声望已达最大值，不能再增加了。
			return False
		self[ factionID ] += value
		if self[ factionID ] > csconst.PRESTIGE_UPLIMIT:
			self[ factionID ] = csconst.PRESTIGE_UPLIMIT
		if self[ factionID ] < csconst.PRESTIGE_LOWERLIMIT:
			self[ factionID ] = csconst.PRESTIGE_LOWERLIMIT
		return True
		
	def getPrestige( self, factionID ):
		"""
		获得对应factionID的势力声望
		
		@param factionID : 势力factionID
		@type factionID : UINT8
		"""
		return self[ factionID ]
		
	def turnOnPrestige( self, factionID, value ):
		"""
		开启声望
		
		@param factionID : 势力factionID
		@type factionID : UINT8
		@param value : 增加的声望值
		@type value : INT32
		"""
		defaultValue = factionMgr.getPrestige( factionID )
		self[ factionID ] = value + defaultValue	# 声望的开启方式为第一次增加声望时
		
	def initPrestigeDefalut( self ):
		"""
		初始化有初始值的势力的声望 by 姜毅
		"""
		for factionID in factionMgr.factionDict:
			defaultValue = factionMgr.getPrestige( factionID )
			if defaultValue > 0: self[ factionID ] = defaultValue	# 初始化声望时，对于有天赋声望的直接开启并赋予天赋声望
		
		
# 构造自定义类型的实例
instance = Prestige()


#
#$Log: not supported by cvs2svn $
#
