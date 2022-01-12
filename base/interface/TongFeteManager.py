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
		self._feteOverTimerID = 0				# ��������timer
		self.feteReset()

	def onManagerInitOver( self ):
		"""
		virtual method.
		��������ʼ�����
		"""
		pass

	def feteReset( self ):
		"""
		���û����������
		"""
		self.feteLogs = {}
		self.feteCompleteList = [] 					# �������İ���б�

	def onMemberLoginTong( self, tongDBID, baseEntity, baseEntityDBID ):
		"""
		define method.
		��Ա��½֪ͨ
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
		�����������
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
		���������ɹ�
		"""
		self.feteLogs[ tongDBID ] = 0	# ���DBID �� �ŷ�ֵ
		if self._feteOverTimerID <= 0:
			t = time.localtime()
			# ����ӵ�ǰʱ�䵽���������ʱ��
			h = 21 - t[3]
			m = 59 - t[4]
			s = 60 - t[5]
			total = ( 60 * 60 * h ) + ( m * 60 ) + s
			self._feteOverTimerID = self.addTimer( total, 0, 0 )

	def addTongFeteValue( self, tongDBID, value ):
		"""
		define method.
		����Ա����˼���
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
		ʱ�䵽�� �����
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
			self._feteOverTimerID = 0				# ��������timer
#
# $Log: not supported by cvs2svn $
#