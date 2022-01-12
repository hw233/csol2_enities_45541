# -*- coding: gb18030 -*-
#
# $Id: TongCityWarManager.py,v 1.1 2008-08-25 09:28:44 kebiao Exp $

import time
import BigWorld
import csdefine
import csstatus
import csconst
import random
from bwdebug import *
from Function import Functor

CONST_FETE_MAX_VALUE = 200

class TongFeteManager:
	def __init__( self ):
		self._feteOverTimerID = 0				# 祭祀活动结束timer
		self.feteReset()

	def onManagerInitOver( self ):
		"""
		virtual method.
		管理器初始化完毕
		"""
		pass

	def feteReset( self ):
		"""
		重置活动的所有数据
		"""
		self.feteLogs = {}
		self.feteCompleteList = [] 					# 完成任务的帮会列表

	def onMemberLoginTong( self, tongDBID, baseEntity, baseEntityDBID ):
		"""
		define method.
		成员登陆通知
		"""
		tm = time.localtime()
		if tm[6] != 6:
			return

		if tongDBID in self.feteLogs:
			tongEntity = self.findTong( tongDBID )
			if tongEntity:
				tongEntity.initMemberFeteData( baseEntityDBID, self.feteLogs[ tongDBID ] )

	def requestFete( self, tongDBID, playerTongGrade, playerBase ):
		"""
		defined method.
		帮主申请祭祀活动
		"""
		if not self.checkMemberDutyRights( playerTongGrade, csdefine.TONG_RIGHT_ACTIVITY ):
			self.statusMessage( playerBase, csstatus.TONG_FETE_GRADE_INVALID )
			return
		"""
		tm = time.localtime()
		if tm[6] != 6:
			self.statusMessage( playerBase, csstatus.TONG_FETE_DATE_INVALID )
			return
		"""
		if tongDBID in self.feteLogs:
			self.statusMessage( playerBase, csstatus.TONG_FETE_OVER_INVALID )
			return

		tongMB = self.findTong( tongDBID )
		if tongMB:
			tongMB.requestFete( playerBase )

	def onRequestFeteSuccessfully( self, tongDBID ):
		"""
		define method.
		申请帮会祭祀成功
		"""
		self.feteLogs[ tongDBID ] = 0	# 帮会DBID 和 信奉值
		if self._feteOverTimerID <= 0:
			t = time.localtime()
			# 计算从当前时间到活动结束的秒时间
			h = 21 - t[3]
			m = 59 - t[4]
			s = 60 - t[5]
			total = ( 60 * 60 * h ) + ( m * 60 ) + s
			self._feteOverTimerID = self.addTimer( total, 0, 0 )

	def addTongFeteValue( self, tongDBID, value ):
		"""
		define method.
		帮会成员完成了祭祀活动
		"""
		if tongDBID in self.feteLogs:
			if CONST_FETE_MAX_VALUE > self.feteLogs[ tongDBID ] + value:
				self.feteLogs[ tongDBID ] += value
				tongEntity = self.findTong( tongDBID )
				if tongEntity:
					tongEntity.onUpdateFeteData( self.feteLogs[ tongDBID ] )
			else:
				if not tongDBID in self.feteCompleteList:
					self.feteCompleteList.append( tongDBID )
					tongEntity = self.findTong( tongDBID )
					if tongEntity:
						tongEntity.onFeteComplete()

	def onOverFete( self ):
		"""
		时间到了 活动结束
		"""
		for tongDBID in self.feteLogs:
			if not tongDBID in self.feteCompleteList:
				tongEntity = self.findTong( tongDBID )
				if tongEntity:
					tongEntity.onOverFete()

		self.feteReset()

	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""
		if self._feteOverTimerID == timerID:
			self.onOverFete()
			self._feteOverTimerID = 0				# 祭祀活动结束timer
#
# $Log: not supported by cvs2svn $
#