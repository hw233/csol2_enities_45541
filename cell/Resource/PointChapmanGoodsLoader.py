# -*- coding: gb18030 -*-
#
# 用物品换物品的表格加载器 2009-01-12 SongPeifang
#

import Language
from bwdebug import *

class PointChapmanGoodsLoader:
	"""
	用物品换物品的表格加载器
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert PointChapmanGoodsLoader._instance is None
		PointChapmanGoodsLoader._instance = self
		self._datas = {} # key:value = 要换的物品ID:用来换该物品的物品的信息

	def load( self, configPath ):
		"""
		加载配置表
		"""
		section = Language.openConfigSection( configPath )
		assert section is not None, "open %s false." % configPath
		for node in section.values():
			key = node.readString( "itemID" )
			if key not in self._datas:
				self._datas[key] = {}
			self._datas[key]["point"] = node.readInt( "point" )

		# 清除缓冲
		Language.purgeConfig( configPath )

	def get( self, ID ):
		"""
		根据 ID 取得其对应商品列表

		@param npcID: NPC 编号
		@return: [( itemID, amount ), ...]
		"""
		try:
			return self._datas[ID]
		except KeyError:
			ERROR_MSG( "ID %s has no goods." % ( ID ) )
			return None

	@classmethod
	def instance( SELF ):
		"""
		"""
		if SELF._instance is None:
			SELF._instance = PointChapmanGoodsLoader()
		return SELF._instance
		
g_PointChapmanGoods = PointChapmanGoodsLoader.instance()