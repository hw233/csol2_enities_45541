# -*- coding: gb18030 -*-
#
# $Id: ItemDataList.py,v 1.21 2008-08-20 09:03:18 yangkai Exp $

"""
@var	instance: 自定义类型道具基础实例，也是全局的道具实例
@type	instance: dict
"""

import sys
import os
import Language
import BigWorld
from bwdebug import *
import Function
import ItemAttrClass
from config.item.Items import Datas as g_ItemsData


class ItemDataList:
	"""
	自定义类型道具实例，主要用于加载全局道具类实例以及保存、传输一些道具的易变属性（自定义类型道具的保存和传输）。

	用例：
		>>> instance = ItemDataList( )	# 初始化配置文件并产生实例
		a = instance.createDynamicItem( 10502001, 1 )	# 产生新的物品——赤铁剑
		print a.getPrice()			# 获取价格

	@ivar _itemDict: 全局道具实例字典
	@type _itemDict: dict
	"""
	_instance = None
	def __init__( self ):
		assert ItemDataList._instance is None, "instance already exist in"
		ItemDataList._instance = self
		self._itemDict = {}				# 已加载的物品列表

	@staticmethod
	def instance():
		if ItemDataList._instance is None:
			ItemDataList._instance = ItemDataList()
		return ItemDataList._instance

	def _getItemDict( self, itemID ):
		"""
		获取物品配置数据
		@return: item data dict; return None if item not found.
		"""
		if itemID not in self._itemDict:
			try:
				itemData = self._loadItemConf( itemID, g_ItemsData[ str( itemID ) ] )
			except KeyError:
				ERROR_MSG( "item %s not found." % itemID )
				return None
			if itemData is None: return None
			self._itemDict[itemID] = itemData		# 成功加载，把物品放到全局字典中
		return self._itemDict[itemID]

	def _loadItemConf( self, itemID, dict ):
		"""
		加载一个物品

		@return: 已加载的item配置; 如果加载失败则返回None
		"""
		item = { "id":itemID, "dynClass":None }
		attrMap = ItemAttrClass.m_itemAttrMap
		errsec = ""
		try :
			for key, dat in dict.iteritems():
				# 过滤掉没有配置的属性
			#	if len( dat ) == 0: continue
				errsec = key
				attrMap[key].readFromConfig( item, dat )
		except :
			ERROR_MSG( "item %s read section '%s' error!" % ( str( itemID ), errsec ) )
			return None
		return item

	def id2name( self, id ):
		"""
		转换物品唯一编号为物品名称

		@return: 物品名称，如果找不到则返回空字符串""
		@rtype:  String
		"""
		try:
			return self._getItemDict( id )["name"]
		except TypeError:
			return ""

	def id2model( self, id ):
		"""
		根据物品ID获取物品模型编号
		"""
		try:
			return self._getItemDict( id )["model"]
		except:
			return 0

	def id2particle( self, id ):
		"""
		根据物品ID获取物品光效配置
		"""
		try:
			return self._getItemDict( id )["particle"]
		except:
			return ""

	def id2type( self, id ):
		"""
		根据物品ID获取物品类型
		"""
		try:
			return self._getItemDict( id )["type"]
		except:
			return 0

	def id2quality( self, id ):
		"""
		根据物品ID获取物品品质
		"""
		try:
			return self._getItemDict( id )["quality"]
		except:
			return 0

	def createDynamicItem( self, id, amount = 1 ):
		"""
		创建动态物品
		@param id: 物品关键字名称
		@type  id: str
		@return: see GItemBase.createDynamicItem method; if item not found, return None
		"""
		gobj = self._getItemDict( id )
		if gobj is None: return None
		try :													# 添加异常处理，防止物品不配置 Script 时，会中断执行（2008.09.28）
			obj = gobj["dynClass"]( gobj )
		except TypeError :
			EXCEHOOK_MSG( "item which id is %i has no script!" % id )
			return None
		obj.setAmount( amount )
		return obj

	def createFromDict( self, valDict ):
		"""
		从字典中创建物品实例

		@param valDict: 物品的属性字典
		@type  valDict: dict
		@return:        继承于CItemBase的道具实例; 如果失败则返回None
		@rtype:         CItemBase
		"""
		# 此函数不处理异常，因为根本不可能出现异常，如果确实出现了，
		# 那就应该考虑我们的代码或某些动作是否把此处给忽略了
		id = valDict["id"]
		obj = self.createDynamicItem( id )			# 创建新的与之对应的对像
		if obj is None:
			ERROR_MSG( "can't find item: %i" % id )
			return None
		obj.loadFromDict( valDict )
		return obj
		
	
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
	
	def	getType( self, id ):
		"""
		转变物品ID
		"""
		try:
			return self._getItemDict( id )["type"]
		except:
			return 0
