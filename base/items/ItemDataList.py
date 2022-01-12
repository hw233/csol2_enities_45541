# -*- coding: gb18030 -*-
#
# $Id: ItemDataList.py,v 1.12 2008-08-09 08:57:37 wangshufeng Exp $

"""
@var	instance: 自定义类型道具基础实例，也是全局的道具实例
@type	instance: dict
"""

import Language
import BigWorld
from bwdebug import *
import Function
import ItemAttrClass
from  config.item import Items


class ItemDataList:
	"""
	自定义类型道具实例，主要用于加载全局道具类实例以及保存、传输一些道具的易变属性（自定义类型道具的保存和传输）。

	用例：
		>>> instance = ItemDataList( )	# 从config.item.Items.Datas数据源产生实例
		a = instance.createDynamicItem( 10502001, 1 )	# 产生新的物品——赤铁剑
		print a.getPrice()			# 获取价格

	@ivar _itemDict: 全局道具实例字典
	@type _itemDict: dict
	"""
	_instance = None
	def __init__( self ):
		assert ItemDataList._instance is None, "instance already exist in"
		ItemDataList._instance = self
		self._itemDict = {}
		self._itemData = Items.Datas

	@staticmethod
	def instance():
		if ItemDataList._instance is None:
			ItemDataList._instance = ItemDataList()
		return ItemDataList._instance

	def __getitem__( self, id ):
		"""
		取得某个全局道具实例

		@param id: 道具唯一标识符
		@type  id: ITEM_ID
		"""
		return self._getItemDict( id )

	def _getItemDict( self, itemID ):
		"""
		获取物品配置数据

		@return: item data dict; return None if item not found.
		"""
		if itemID not in self._itemDict:
			try:
				itemData = self._loadItemConf( itemID, self._itemData[ str( itemID ) ] )
			except KeyError:
				ERROR_MSG( "item %i not found." % itemID )
				return None
			if itemData is None: return None
			self._itemDict[itemID] = itemData		# 成功加载，把物品放到全局字典中
		return self._itemDict[itemID]

	def _loadItemConf( self, itemID, configDict ):
		"""
		加载一个物品

		@return: 已加载的item配置; 如果加载失败则返回None
		"""
		item = { "id":itemID, "dynClass":None }
		attrMap = ItemAttrClass.m_itemAttrMap
		for key, e in configDict.iteritems():
			# 过滤掉没有配置的属性
			try:
				if len( e ) == 0:
					continue
			except: #调用 len( 数值类型参数 ) 会抛出异常，而为数值时，该值不为空
				pass
			attrMap[ key ].readFromConfig( item, e )
		return item

	def id2name( self, id ):
		"""
		转换物品唯一编号为物品名称

		@return: 物品名称，如果找不到则返回空字符串""
		@rtype:  ITEM_ID
		"""
		try:
			return self._getItemDict( id )["name"]
		except TypeError:
			return ""

	def getLevel( self, id ):
		"""
		根据ID获得物品的等级

		@return: 物品编号"
		@rtype:  String
		"""
		try:
			return self._getItemDict( id )["level"]
		except:
			return 0

	def getType( self, id ):
		"""
		转变物品ID
		"""
		try:
			return self._getItemDict( id )["type"]
		except:
			return 0

	def createDynamicItem( self, id, amount = 1 ):
		"""
		创建动态物品
		@param id: 物品关键字名称
		@type  id: ITEM_ID
		@return: see GItemBase.createDynamicItem method; if item not found, return None
		"""
		gobj = self._getItemDict( id )
		if gobj is None: return None
		obj = gobj["dynClass"]( gobj )
		obj.setAmount( amount )
		return obj

	def createFromDict( self, valDict ):
		"""
		从字典中创建物品实例

		@param valDict: 物品的属性字典
		@type  valDict: dict
		@return:        继承于CItemBase的道具实例; 失败则返回None
		@rtype:         CItemBase
		"""
		# 此函数不处理异常，因为根本不可能出现异常，如果确实出现了，
		# 那就应该考虑我们的代码或某些动作是否把此处给忽略了
		id = valDict["id"]
		obj = self.createDynamicItem( id )			# 创建新的与之对应的对像
		if obj is None: return None
		obj.loadFromDict( valDict )
		return obj
