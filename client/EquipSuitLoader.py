# -*- coding: gb18030 -*-

#$Id: EquipSuitLoader.py,v 1.3 2008-08-09 01:48:51 wangshufeng Exp $

from bwdebug import *
import Language
from items.ItemDataList import ItemDataList
from config.item import EquipSuits

g_items = ItemDataList.instance()

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

	def __init__( self ):
		assert EquipSuitLoader._instance is None, "instance already exist in"
		self._datas = EquipSuits.Datas	# like as { suitID : [itemID, ......], ...}
		self._suitName = EquipSuits.SuitName # like as { suitID : name , ......}	重新存储是因为不想打乱原来的结构,套装名的使用地方不是很多 hd

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

	def getSuit( self, EquipID ):
		"""
		根据装备ID获取该ID对应的全部套装的ID
		@type  EquitID	:	INT
		@param EquitID	:	单个装备的ID
		@return:	List 存储该套装备的ID的列表 以及该套装的名字
		@add by hd
		"""
		for suitkey in self._datas:
			if str(EquipID).endswith(str(suitkey)):
				if EquipID in self._datas[suitkey]:
					return ( self.getSuitChildName(suitkey) ,list(self._datas[suitkey]))		#返回该套装原始数据的副本 以免被外部不小心修改

	def getSuitID( self, EquipID ):
		"""
		根据装备ID获取该ID对应的全部套装的ID
		@type  EquitID	:	INT
		@param EquitID	:	单个装备的ID
		@return:	INT 返回该套装部件的ID
		@add by hd
		"""
		for suitkey in self._datas:
			if str(EquipID).endswith(str(suitkey)):
				if EquipID in self._datas[suitkey]:
					return suitkey

	def getSuitChildID(self, SuitId):
		"""
		根据套装ID 获取套装的部件ID
		"""
		if not SuitId:
			return []
		return self._datas.get(SuitId)

	def getSuitChildName( self, SuitId ):
		"""
		根据套装的ID 获取该套装的名字
		@type  SuitId	:	INT
		@param SuitId	:	套装的ID
		@return:	str 套装名
		@add by hd
		"""
		if not SuitId or not self._suitName:
			return None
		return self._suitName.get(SuitId)

	def getSuitChildNames( self, SuitId):
		"""
		根据套装的ID 获取该套装的所有部件的名字
		@type  SuitId	:	INT
		@param SuitId	:	套装的ID
		@return:	LIST 套装的所有部件名
		@add by hd
		"""
		equips = self._datas.get(SuitId)
		if not equips:
			return []
		equipNames = []  #存储该套装部件名字的列表
		for equip in equips:
			name = g_items.id2name(equip)
			equipNames.append( name )
		return equipNames


equipsuit = EquipSuitLoader.instance()

#$Log: not supported by cvs2svn $
#Revision 1.2  2008/04/07 02:49:25  yangkai
#no message
#
#Revision 1.1  2008/03/24 02:29:30  yangkai
#套装属性配置加载
#