# -*- coding: gb18030 -*-

# $Id: NPCExpLoader.py,v 1.2 2007-11-23 06:40:31 phw Exp $

import Language
from bwdebug import *
from config import npc_exp

class NPCExpLoader:
	"""
	���ﾭ�����ü�����
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert NPCExpLoader._instance is None
		# key == ��Ӧ�Ĺ���ȼ�
		# value == �ڸõȼ�������ܻ�õľ���
		self._datas = npc_exp.Datas
		NPCExpLoader._instance = self

	def get( self, level ):
		"""
		���ݵ�ȡ�ö�Ӧ�ľ���ֵ
		
		@return: INT
		"""
		try:
			return self._datas[level]
		except KeyError:
			if level != 0:
				ERROR_MSG( "level %i has not in table." % level )
			return 0

	@staticmethod
	def instance():
		"""
		"""
		if NPCExpLoader._instance is None:
			NPCExpLoader._instance = NPCExpLoader()
		return NPCExpLoader._instance


#
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/11/17 03:10:09  phw
# no message
#
#