# -*- coding: gb18030 -*-
# ��ɫͳ��ģ��

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
	��ɫͳ��ģ��
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
		���룺config/server/questTypeStr.xml���������������ͳ��
		"""
		self.section = Language.openConfigSection( xmlPath )
		assert self.section is not None,"open file( path:%s ) error:not exist!" % xmlPath

	def initStat( self, roleEntity ):
		"""
		��ʼ����ɫͳ��
		"""
		self.refreshDayStat( roleEntity )

	def refreshDayStat( self, roleEntity ):
		"""
		�����һ�죬ˢ��һ�½�ɫһ���ͳ��
		"""
		statDay = roleEntity.statistic.get( "statDay", 0 )		# ��ȡ��¼������ ĳ��
		
		today = self.getToday()
		if today != statDay:	# �����һ�죬���¿�ʼ��¼
			roleEntity.statistic = { "statDay" : today }

	def getToday( self ):
		"""
		��ȡ���ڵڼ���(like:20091113)
		"""
		year, month, day = time.localtime()[:3]
		return year * 10000 + month * 100 + day

	def addQuestDayStat( self, roleEntity, questID ):
		"""
		������¼ͳ��
		"""
		recordType = self.getQuestType( questID )
		if len(recordType) == 0:return		# �������Ҫͳ�Ƶķ���
		
		roleEntity.addDayStat( recordType )

	def getQuestType( self, questID ):
		"""
		����questID��������������
		"""
		typeTag = str( questID )[0:3]
		
		if typeTag == "602":
			typeTag = str( questID )[0:5]
		elif typeTag == "403":
			typeTag = str( questID )
		return self.section.readString( typeTag )
