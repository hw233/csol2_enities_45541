# -*- coding: gb18030 -*-
#
# $Id: DartNPC.py,v 1.2 2008-09-05 03:50:52 zhangyuxing Exp $


from bwdebug import *
import csdefine
from NPC import NPC
import ECBExtend



timerBegin = 7200 											#两个小时

class DartNPC( NPC ):
	"""
	NPC基类
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		NPC.__init__( self )
		self.addTimer( timerBegin, 0, ECBExtend.QUERY_DART_MESSAGE_CBID )			#每隔两个小时查询镖局信息一次
		
		
	
	def refreshDartMessage( self, key, dartMessages ):
		"""
		define method
		更新镖局数据
		"""
		self.setTemp( key, dartMessages )
	
	
	def getDartMessage( self, key ):
		"""
		"""
		return self.queryTemp( key, [] )
	
	
	def onQueryDartMessage( self ):
		"""
		向数据库查询运镖数据
		"""
		self.base.queryDartMessage()
		self.addTimer( timerBegin, 0, ECBExtend.QUERY_DART_MESSAGE_CBID )			#每隔两个小时查询镖局信息一次
