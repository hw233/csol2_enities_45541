# -*- coding: gb18030 -*-
#
# $Id: TongSpecialItemsData.py $

"""
��������̳���Ʒ����
"""

import BigWorld
import Language
import csconst
from bwdebug import *
import Function
import time
from config import TongSpecialItems

class TongSpecialItemsData:
	
	_instance = None
	
	def __init__( self, configPath = None ):
		"""
		���캯����
		@param configPath:	���������ļ�·��
		@type  configPath:	string
		"""
		assert TongSpecialItemsData._instance is None		# ���������������ϵ�ʵ��
		self._datas = TongSpecialItems.Datas	# key is BuffTime::_id and value is instance of BuffTime which derive from it.
		TongSpecialItemsData._instance = self

		#if configPath is not None:
		#	self.load( configPath )

	@staticmethod
	def instance():
		"""
		ͨ�� action id ��ȡactionʵ��
		"""
		if TongSpecialItemsData._instance is None:
			TongSpecialItemsData._instance = TongSpecialItemsData()
		return TongSpecialItemsData._instance

	def __getitem__( self, key ):
		"""
		"""
		return self._datas[ key ]

	def getDatas( self ):
		
		return self._datas
	
	def hasSpecialItem( self, itemID ):
		return itemID in self._datas

def tongSpeItem_instance():
	return TongSpecialItemsData.instance()