# -*- coding: gb18030 -*-

#$Id: EquipSuitLoader.py,v 1.3 2008-08-09 01:48:51 wangshufeng Exp $

from bwdebug import *
import Language
from config.item.EquipSuits import Datas as g_EquipSuitData

# ----------------------------------------------------------------------------------------------------
# 装备套装配置加载
# ----------------------------------------------------------------------------------------------------

class EquipSuitLoader:
	"""
	装备套装配置加载
	@ivar _data: 全局数据字典; key is id, value is dict like as {key：[...], ...}
	@type _data: dict
	"""
	_instance = None

	def __init__( self, xmlConf = None ):
		assert EquipSuitLoader._instance is None, "instance already exist in"
		self._datas = g_EquipSuitData	# like as { suitID : [itemID, ......], ...}

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = EquipSuitLoader()
		return self._instance

	def isSuit( self, EquipIDList ):
		"""
		判断一个装备ID列表是否是套装
		@type  EquipIDList: List
		@param EquipIDList: 装备ID列表
		@return:        Bool
		"""
		return set( EquipIDList ) in [ set( k ) for k in self._datas.itervalues()]

#$Log: not supported by cvs2svn $
#Revision 1.2  2008/04/07 02:49:25  yangkai
#no message
#
#Revision 1.1  2008/03/24 02:29:30  yangkai
#套装属性配置加载
#