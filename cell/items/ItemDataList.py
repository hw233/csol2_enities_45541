# -*- coding: gb18030 -*-
#
# $Id: ItemDataList.py,v 1.16 2008-08-09 08:57:22 wangshufeng Exp $

"""
@var	instance: 自定义类型道具基础实例，也是全局的道具实例
@type	instance: dict
"""

import sys
import Language
import BigWorld
from bwdebug import *
import Function
import ItemAttrClass
import Math
from  config.item import Items
import Math


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
		self._itemDict = {}			# 已加载的物品数据
		self._itemData = Items.Datas		# 物品总数据

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
				printStackTrace()
				ERROR_MSG( "item %i not found." % int( itemID ) )
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
			
			# 检测配置中的冗余字段，以更直接的方式反映出配置问题 by mushuang
			if not attrMap.has_key( key ):
				ERROR_MSG( "Redundant field in item data, please check configuration! itemID(%s),key(%s)"%(str(itemID),key) )
			else:
				attrMap[ key ].readFromConfig( item, e )
			
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

	def	getType( self, id ):
		"""
		转变物品ID
		"""
		try:
			return self._getItemDict( id )["type"]
		except:
			return 0

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

	def getReqClass( self, id ):
		"""
		根据ID获得物品的职业需求

		@return: 物品编号"
		@rtype:  String
		"""
		try:
			return self._getItemDict( id )["reqClasses"]
		except:
			return []
			
	def getStacCount( self, id ):
		"""
		根据ID来获得可叠加个数
		"""
		try:
			return self._getItemDict( id )["stackable"]
		except:
			return 0

	def createDynamicItem( self, id, amount = 1 ):
		"""
		创建动态物品
		@param id: 物品关键字名称
		@type  id: int
		@return: see GItemBase.createDynamicItem method; if item not found, return None
		"""
		gobj = self._getItemDict( id )
		if gobj is None: return None
		try :												# 添加异常处理，防止物品不配置 Script 时，会中断执行（2008.09.28）
			obj = gobj["dynClass"]( gobj )
		except TypeError :
			msg = "item which id is %i has no script!" % id
			sys.excepthook( Exception, msg, sys.exc_traceback )
			return None
		obj.setAmount( amount )
		return obj

	def createEntity( self, id, spaceID, position, direction, srcDict = None ):
		"""
		创建一个Entity扔到地图上

		@param   spaceID: 地图ID号
		@type    spaceID: INT32
		@param  position: 道具产生后放在哪个位置
		@type   position: VECTOR3
		@param direction: 道具产生后放的方向
		@type  direction: VECTOR3
		@param   srcDict: 附加的属性字典数据，该参数默认值为None
		@type    srcDict: CItemBase
		@return:          一个新的道具entity，if item not found, return None
		@rtype:           Entity
		"""
		position = Math.Vector3( position )
		if srcDict is None:
			obj = self.createDynamicItem( id, True )
			if obj is None: return None
			tmpDict = { "itemProp" : obj }
		else:
			if not srcDict.has_key( "itemProp" ):
				tmpDict = srcDict.copy()
				obj = self.createDynamicItem( id, True )
				if obj is None: return None
				tmpDict["itemProp"] = obj
			else:
				tmpDict = srcDict
		position = Math.Vector3(position)
		# entity与地表做碰撞，确保可以放在地面上
		position.y += 0.1  #修正调用的点处于所要的面上时，拾取面失败的情况
		for amend in [-10, 10]:
			pos = ( position[0], position[1] + amend, position[2] )
			r = BigWorld.collide( spaceID, position, pos )
			if r is not None:
				break
		if r is not None:
			pos = r[0]
		else:
			pos = position
		return BigWorld.createEntity( "DroppedItem", spaceID, pos, direction, tmpDict )

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
		if obj is None: return None
		obj.loadFromDict( valDict )
		return obj



#
# $Log: not supported by cvs2svn $
# Revision 1.15  2008/08/09 01:49:06  wangshufeng
# 物品id类型调整，STRING -> INT32,相应调整代码。
#
# Revision 1.14  2008/04/24 03:20:32  yangkai
# no message
#
# Revision 1.13  2008/04/23 04:22:11  yangkai
# no message
#
# Revision 1.12  2008/04/23 03:58:16  yangkai
# no message
#
# Revision 1.11  2008/02/23 10:27:45  yangkai
# 添加接口 getLevel();getReqClass()
#
# Revision 1.10  2008/01/25 10:06:04  yangkai
# 配置文件路径修改
#
# Revision 1.9  2007/11/28 02:08:54  yangkai
# 移除了无用的 from ItemTypeEnum import *
#
# Revision 1.8  2007/11/24 03:53:47  yangkai
# no message
#
# Revision 1.7  2007/11/24 03:08:04  yangkai
# 物品系统调整
# 调整物品配置加载代码
#
# Revision 1.6  2007/09/28 02:17:49  yangkai
# 配置文件路径更改:
# res/server/config  -->  res/config
#
# Revision 1.5  2007/06/23 02:38:37  phw
# method modified: load(), 取消了对文件配置的直接依赖，改为通过从一个配置存放位置列表中搜索
#
# Revision 1.4  2006/12/21 09:29:02  phw
# 物品初始化时强制转换物品id为小写
#
# Revision 1.3  2006/08/18 06:57:02  phw
# 修改接口：
#     load()；CITI_* to CIST_*
#     createFromDict()；增加对item是否None的判断
#
# Revision 1.2  2006/08/11 02:57:00  phw
# 属性更名：修改所有itemInstance.keyName或itemInstance.id()为itemInstance.id
#
# Revision 1.1  2006/08/09 08:23:37  phw
# no message
#
#