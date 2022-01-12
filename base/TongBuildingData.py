# -*- coding: gb18030 -*-
#
# $Id: TongBuildingData.py,v 1.12 2008-07-15 04:21:55 kebiao Exp $

"""
��Ὠ����Դ���ز��֡�
"""

import BigWorld
import Language
import csconst
import csdefine
from bwdebug import *
import Function
import time
from config import TongBuilding
from config import TongBuildingLevel

TONTG_KEY_TO_TYPE_DICT = {
				csdefine.TONG_BUILDING_TYPE_YSDT 	: "ysdt_level" ,	# ���´���
				csdefine.TONG_BUILDING_TYPE_JK 		: "jk_level" ,		# ���
				csdefine.TONG_BUILDING_TYPE_SSD 	: "ssd_level" ,		# ���޵�
				csdefine.TONG_BUILDING_TYPE_CK 		: "ck_level" ,		# �ֿ�
				csdefine.TONG_BUILDING_TYPE_TJP 	: "tjp_level" ,		# ������
				csdefine.TONG_BUILDING_TYPE_SD 		: "sd_level" ,		# �̵�
				csdefine.TONG_BUILDING_TYPE_YJY 	: "yjy_level" ,		# �о�Ժ
}

class TongBuildingData:
	_instance = None
	def __init__( self ):
		"""
		���캯����
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

class TongBuildingLevelData:
	_instance = None
	def __init__( self ):
		"""
		���캯����
		"""
		assert TongBuildingLevelData._instance is None		# ���������������ϵ�ʵ��
		self._datas = TongBuildingLevel.Datas
		TongBuildingLevelData._instance = self

	@staticmethod
	def instance():
		"""
		ͨ�� action id ��ȡactionʵ��
		"""
		if TongBuildingLevelData._instance is None:
			TongBuildingLevelData._instance = TongBuildingLevelData()
		return TongBuildingLevelData._instance

	def __getitem__( self, level, key ):
		return self._datas[ level ][ key ]
	
	def getBuildingLevel( self, level, key ):
		"""
		ȡ�Ľ�����ȼ�
		"""
		levelKey = TONTG_KEY_TO_TYPE_DICT[ key ]
		return self._datas[ level ][ levelKey ]

def instance():
	return TongBuildingData.instance()

def tbl_instance():
	return TongBuildingLevelData.instance()

#
# $Log: not supported by cvs2svn $
#
#
