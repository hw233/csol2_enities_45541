# -*- coding: gb18030 -*-

#$Id: NPCModelLoader.py,v 1.6 2008-07-25 07:55:19 yangkai Exp $

import BigWorld
from bwdebug import *
import ResMgr
from gbref import rds
from config.client import NpcVoiceConfig
# ----------------------------------------------------------------------------------------------------
# NPC模型加载
# ----------------------------------------------------------------------------------------------------

class NPCVoiceLoader:
	"""
	NPC模型加载
	@ivar _data: 全局数据字典; key is id, value is dict like as {key：{...}}
	@type _data: dict
	"""
	_instance = None
	
	def __init__( self ):
		assert NPCVoiceLoader._instance is None, "instance already exist in"
		self._datas = NpcVoiceConfig.Datas
		# self._datas like as { npc_id : ( voice1,voice2,... ), npc_id2:(...),... }

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = NPCVoiceLoader()
		return self._instance
		
	def getClickVoice( self, npc_id ):
		"""
		获得NPC点击音效
		"""
		try:
			return self._datas[npc_id]
		except:
			return ()

	