# -*- coding: gb18030 -*-
#
# $Id: TongItemResearchData.py,v 1.12 2008-07-15 04:21:55 kebiao Exp $

"""
��Ὠ����Դ���ز��֡�
"""

import BigWorld
import Language
import csconst
from bwdebug import *
import Function
import time
from config import TongItemResearch

class TongItemResearchData:
	_instance = None
	def __init__( self, configPath = None ):
		"""
		���캯����
		@param configPath:	���������ļ�·��
		@type  configPath:	string
		"""
		assert TongItemResearchData._instance is None		# ���������������ϵ�ʵ��
		self._datas = TongItemResearch.serverDatas	# key is BuffTime::_id and value is instance of BuffTime which derive from it.
		self._clientDatas = TongItemResearch.Datas
		TongItemResearchData._instance = self

		#if configPath is not None:
		#	self.load( configPath )

	@staticmethod
	def instance():
		"""
		ͨ�� action id ��ȡactionʵ��
		"""
		if TongItemResearchData._instance is None:
			TongItemResearchData._instance = TongItemResearchData()
		return TongItemResearchData._instance

	def __getitem__( self, key ):
		"""
		ȡ��Skillʵ��
		"""
		return self._datas[ key ]

	def getDatas( self ):
		return self._datas

	def getClientDatas( self ):
		return self._clientDatas

def instance():
	return TongItemResearchData.instance()

#
# $Log: not supported by cvs2svn $
#
#
