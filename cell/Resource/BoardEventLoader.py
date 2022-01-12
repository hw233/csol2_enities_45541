# -*- coding: gb18030 -*-

import Language
from bwdebug import *
from SmartImport import smartImport

class BoardEventLoader:
	"""
	棋盘事件数据加载
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert BoardEventLoader._instance is None
		self._eventDatas = {}
		BoardEventLoader._instance = self

	def load( self, configPath ):
		"""
		加载棋盘事件配置
		"""
		sect = Language.openConfigSection( configPath )
		assert sect is not None, "open %s false." % configPath

		for childSect in sect.values():
			id = childSect["id"].asInt
			eventName = childSect["eventName"].asString
			try:
				eventMod = smartImport( "Resource." + eventName )
				eventModInst = eventMod()
			except ImportError, err:
				ERROR_MSG( "%s, id: %i."%( err, id ) )
				continue
			assert not self._eventDatas.has_key( id ), "id %i eventName: %s is exist already in. reading file %s" % ( id, eventName, childSect.asString )
			eventModInst.init( childSect )
			self._eventDatas[id] = eventModInst
		# 清除缓冲
		Language.purgeConfig( configPath )

	def __getitem__( self, key ):
		"""
		取得棋盘事件实例
		"""
		assert key in self._eventDatas, "BoardEvent %i not find!" % key
		return self._eventDatas[key]

	def has( self, key ):
		"""
		"""
		return key in self._eventDatas

	@staticmethod
	def instance():
		"""
		"""
		if BoardEventLoader._instance is None:
			BoardEventLoader._instance = BoardEventLoader()
		return BoardEventLoader._instance

def g_boardEventLoader():
	return BoardEventLoader.instance()