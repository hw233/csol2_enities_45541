# -*- coding: gb18030 -*-
#
# $Id: TongBuildingData.py,v 1.12 2008-07-15 04:21:55 kebiao Exp $

"""
������Դ���ز��֡�
"""

import BigWorld
import Language
import csconst
from bwdebug import *
import Function
import time
from config import TongBuilding

class TongBuildingData:
	_instance = None
	def __init__( self ):
		"""
		���캯����
		@param configPath:	���������ļ�·��
		@type  configPath:	string
		"""
		assert TongBuildingData._instance is None		# ���������������ϵ�ʵ��
		self._datas = TongBuilding.Datas	# key is BuffTime::_id and value is instance of BuffTime which derive from it.
		TongBuildingData._instance = self

	@staticmethod
	def instance():
		"""
		ͨ�� action id ��ȡactionʵ��
		"""
		if TongBuildingData._instance is None:
			TongBuildingData._instance = TongBuildingData()
		return TongBuildingData._instance

	def __getitem__( self, key ):
		"""
		ȡ��Skillʵ��
		"""
		return self._datas[ key ]
		
	
	def getDatas( self ):
		return self._datas

def instance():
	return TongBuildingData.instance()

#
# $Log: not supported by cvs2svn $
#
#
