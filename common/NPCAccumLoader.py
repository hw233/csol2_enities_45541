# -*- coding: gb18030 -*-

# NPCAccumLoader.py, 2012-09-06  added by dqh

import Language
from bwdebug import *
from config import npc_accum

class NPCAccumLoader:
	"""
	��������ֵ���ü�����
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert NPCAccumLoader._instance is None
		# key == ��Ӧ�Ĺ���ȼ�
		# value == �ڸõȼ�������ܻ�õ�����ֵ
		self._datas = npc_accum.Datas
		NPCAccumLoader._instance = self

	def get( self, level ):
		"""
		���ݵȼ�ȡ�ö�Ӧ����ֵ
		
		@return: INT
		"""
		try:
			return self._datas[level]
		except KeyError:
			if level != 0:
				ERROR_MSG( "Level %i has not in table npc_accum." % level )
			return 0

	@staticmethod
	def instance():
		"""
		"""
		if NPCAccumLoader._instance is None:
			NPCAccumLoader._instance = NPCAccumLoader()
		return NPCAccumLoader._instance
