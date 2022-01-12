# -*- coding: gb18030 -*-

import Language
from bwdebug import *

class TongRobWarRewardLoader:
	"""
	�Ӷ�ս��������������Ϊ�������
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert TongRobWarRewardLoader._instance is None
		self._datas = {}
		TongRobWarRewardLoader._instance = self

	def load( self, configPath ):
		"""
		�������������
		"""
		section = Language.openConfigSection( configPath )
		assert section is not None, "open %s false." % configPath
		
		for node in section.values():
			level = node.readInt( "level" )
			exp = node.readInt( "exp" )
			
			if level not in self._datas:
				self._datas[level] = {}

			if 'exp' not in self._datas[level]:
				self._datas[level]['exp'] = exp
			
		# �������
		Language.purgeConfig( configPath )

	def get( self, level ):
		"""
		��ȡ������Ϣ
		"""
		try:
			return self._datas[level]
		except KeyError:
			DEBUG_MSG( "level %i has no reward from table." % ( level ) )
			return {}


	@staticmethod
	def instance():
		"""
		"""
		if TongRobWarRewardLoader._instance is None:
			TongRobWarRewardLoader._instance = TongRobWarRewardLoader()
		return TongRobWarRewardLoader._instance
