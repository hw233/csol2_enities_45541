# -*- coding: gb18030 -*-
#
# $Id: TongBeastData.py

"""
���������Ϣ���ز��֡�
"""

import BigWorld
import Language
import csconst
from bwdebug import *
import Function
import time
from config.client import BeastAttr

class TongBeastData:
	_instance = None
	def __init__( self ):
		"""
		���캯����
		@param configPath:	���������ļ�·��
		@type  configPath:	string
		"""
		assert TongBeastData._instance is None		# ���������������ϵ�ʵ��
		self._datas = BeastAttr.Datas	# key is BuffTime::_id and value is instance of BuffTime which derive from it.
		TongBeastData._instance = self

	@staticmethod
	def instance():
		"""
		ͨ�� action id ��ȡactionʵ��
		"""
		if TongBeastData._instance is None:
			TongBeastData._instance = TongBeastData()
		return TongBeastData._instance

	def __getitem__( self, key ):
		"""
		ȡ��ʵ��
		"""
		return self._datas[ key ]
	
	def getDatas( self ):
		return self._datas

def instance():
	return TongBeastData.instance()

#
# $Log: not supported by cvs2svn $
#
#
