# -*- coding: gb18030 -*-

# $Id: NPCTalkLoader.py,v 1.1 2008-01-15 06:05:46 phw Exp $

import Language
from bwdebug import *
from Resource.DialogManager import DialogManager

class NPCTalkLoader:
	"""
	NPC对话内容加载器
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert NPCTalkLoader._instance is None
		# key == npcID
		# value == DialogManager()
		self._datas = {}
		NPCTalkLoader._instance = self

	def load( self, configPath ):
		"""
		加载经验配置表
		"""
		section = Language.openConfigSection( configPath )
		assert section is not None, "open %s false." % configPath
		for node in section.values():
			self._datas[node.readString( "npcID" )] = DialogManager ( node["talks"] )
		# 清除缓冲
		Language.purgeConfig( configPath )

	def get( self, npcID ):
		"""
		根据npcID取得对话脚本
		
		@return: instance of DialogManager
		"""
		try:
			return self._datas[npcID]
		except KeyError:
			#WARNING_MSG( "npcID %s has not in table." % npcID )	怪物也算是NPC，但怪物太多，此提示作用也不大
			return None

	@staticmethod
	def instance():
		"""
		"""
		if NPCTalkLoader._instance is None:
			NPCTalkLoader._instance = NPCTalkLoader()
		return NPCTalkLoader._instance


#
# $Log: not supported by cvs2svn $
#