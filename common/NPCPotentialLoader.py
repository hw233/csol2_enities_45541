# -*- coding: gb18030 -*-

# $Id: NPCPotentialLoader.py,v 1.2 2009-9-23 06:40:31 kebiao Exp $

import Language
from bwdebug import *
from config import npc_potential

class NPCPotentialLoader:
	"""
	����Ǳ�����ü�����
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert NPCPotentialLoader._instance is None
		# key == ��Ӧ�Ĺ���ȼ�
		# value == �ڸõȼ�������ܻ�õľ���
		self._datas = npc_potential.Datas
		NPCPotentialLoader._instance = self

	def get( self, level ):
		"""
		���ݵ�ȡ�ö�Ӧ�ľ���ֵ
		
		@return: INT
		"""
		try:
			return self._datas[level]
		except KeyError:
			if level != 0:
				printStackTrace()
				ERROR_MSG( "level %i has not in table." % level )
			return 0

	@staticmethod
	def instance():
		"""
		"""
		if NPCPotentialLoader._instance is None:
			NPCPotentialLoader._instance = NPCPotentialLoader()
		return NPCPotentialLoader._instance


