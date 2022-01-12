# -*- coding: gb18030 -*-
# 角色统计模块

from bwdebug import *
import csdefine
import csconst
import Language
import items
import csstatus
import time
import sys

class Statistic():
	"""
	角色统计模块
	"""
	_instance = None

	def __init__( self ):
		assert Statistic._instance is None, "Statistic instance already exist in"
		Statistic._instance = self
		self.restrictLevel = 0

	@staticmethod
	def instance():
		if Statistic._instance is None:
			Statistic._instance = Statistic()
		return Statistic._instance

	def load( self, xmlPath = "" ):
		"""
		载入：config/server/questTypeStr.xml，用来给任务分类统计
		"""
		self.section = Language.openConfigSection( xmlPath )
		assert self.section is not None,"open file( path:%s ) error:not exist!" % xmlPath

	def initStat( self, roleEntity ):
		"""
		初始化角色统计
		"""
		self.refreshDayStat( roleEntity )

	def refreshDayStat( self, roleEntity ):
		"""
		如果新一天，刷新一下角色一天的统计
		"""
		statDay = roleEntity.statistic.get( "statDay", 0 )		# 获取记录数据中 某天
		
		today = self.getToday()
		if today != statDay:	# 如果新一天，重新开始记录
			roleEntity.statistic = { "statDay" : today }

	def getToday( self ):
		"""
		获取现在第几天(like:20091113)
		"""
		year, month, day = time.localtime()[:3]
		return year * 10000 + month * 100 + day

	def addQuestDayStat( self, roleEntity, questID ):
		"""
		新增记录统计
		"""
		recordType = self.getQuestType( questID )
		if len(recordType) == 0:return		# 如果不需要统计的返回
		
		roleEntity.addDayStat( recordType )

	def getQuestType( self, questID ):
		"""
		根据questID，返回任务类型
		"""
		typeTag = str( questID )[0:3]
		
		if typeTag == "602":
			typeTag = str( questID )[0:5]
		elif typeTag == "403":
			typeTag = str( questID )
		return self.section.readString( typeTag )
