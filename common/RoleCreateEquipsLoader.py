# -*- coding: gb18030 -*-

import Language
import random
from bwdebug import *
import Language

class RoleCreateEquipsLoader:
	"""
	角色初始化装备数据加载
	"""
	_instance = None
	def __init__( self ):
		assert RoleCreateEquipsLoader._instance is None
		self._datas = {}
		RoleCreateEquipsLoader._instance = self
	
	def loadEquipDatas( self, config ):
		section = Language.openConfigSection( config )
		assert section != None
		for csect in section.values():
			prof = csect["class"].asInt
			equipOrder = csect["equipLocation"].asInt
			equipID = csect[ "equipID" ].asInt
			if prof in self._datas:
				self._datas[prof][equipOrder] = equipID
			else:
				self._datas[prof] = { equipOrder:equipID }
	
	def getEuipsByClass( self, prof ):
		"""
		通过职业获取装备数据
		"""
		return self._datas.get( prof, {} )

	@staticmethod
	def instance():
		"""
		"""
		if RoleCreateEquipsLoader._instance is None:
			RoleCreateEquipsLoader._instance = RoleCreateEquipsLoader()
		return RoleCreateEquipsLoader._instance

equipsLoader = RoleCreateEquipsLoader.instance()
