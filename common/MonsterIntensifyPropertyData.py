# -*- coding: gb18030 -*-
#
# $Id: MonsterIntensifyPropertyData.py,v 1.12 2008-07-15 04:21:55 kebiao Exp $

"""
��Ὠ����Դ���ز��֡�
"""

import BigWorld
import Language
from bwdebug import *
import Function
import time
from   config.server import MonsterIntensifyProperty

class MonsterIntensifyPropertyData:
	_instance = None
	def __init__( self ):
		"""
		���캯����
		@param configPath:	���������ļ�·��
		@type  configPath:	string
		"""
		assert MonsterIntensifyPropertyData._instance is None		# ���������������ϵ�ʵ��
		self._datas = MonsterIntensifyProperty.Datas	# key is BuffTime::_id and value is instance of BuffTime which derive from it.
		MonsterIntensifyPropertyData._instance = self

	@staticmethod
	def instance():
		"""
		ͨ�� action id ��ȡactionʵ��
		"""
		if MonsterIntensifyPropertyData._instance is None:
			MonsterIntensifyPropertyData._instance = MonsterIntensifyPropertyData()
		return MonsterIntensifyPropertyData._instance

	def __getitem__( self, key ):
		"""
		ȡ��Skillʵ��
		"""
		return self._datas[ key ]

	def getAttrs( self, id, level ):
		if not id in self._datas:
			return None
		onlyLevelList = []	# Ψһ�ȼ�
		manyLevelList = []	# �ȼ�����
		for key in self._datas[ id ].keys():
			try:
				levelRange = eval( key )	# �ȼ�����
				if levelRange[0] == levelRange[1]:
					onlyLevelList.append( key )
				else:
					manyLevelList.append( key )
			except:
				ERROR_MSG( "MonsterIntensifyProperty config is wrong! id(%s),level(%s)" % ( id, key ) )
				continue

		for onlyLevel in onlyLevelList:
			ol = eval( onlyLevel )
			if level >= ol[0] and level <= ol[1]:
				return self._datas[ id ][ onlyLevel ]
		for manyLevel in manyLevelList:
			ml = eval( manyLevel )
			if level >= ml[0] and level <= ml[1]:
				return self._datas[ id ][ manyLevel ]
		return None

	def getAttr( self, id, level, attr ):
		if not id in self._datas:
			return None
		onlyLevelList = []	# Ψһ�ȼ�
		manyLevelList = []	# �ȼ�����
		for key in self._datas[ id ].keys():
			try:
				levelRange = eval( key )	# �ȼ�����
				if levelRange[0] == levelRange[1]:
					onlyLevelList.append( key )
				else:
					manyLevelList.append( key )
			except:
				ERROR_MSG( "MonsterIntensifyProperty config is wrong! id(%s),level(%s)" % ( id, key ) )
				continue

		for onlyLevel in onlyLevelList:
			ol = eval( onlyLevel )
			if level >= ol[0] and level <= ol[1]:
				if attr in self._datas[ id ][ onlyLevel ]:
					return self._datas[ id ][ onlyLevel ][ attr ]
		for manyLevel in manyLevelList:
			ml = eval( manyLevel )
			if level >= ml[0] and level <= ml[1]:
				if attr in self._datas[ id ][ manyLevel ]:
					return self._datas[ id ][ manyLevel ][ attr ]
		return None

def instance():
	return MonsterIntensifyPropertyData.instance()

#
# $Log: not supported by cvs2svn $
#
#
