# -*- coding: gb18030 -*-

"""
物品刷使用的前提条件是：假定在一个物品格的生命周期内，它不会从一
个窗口转移到另一个窗口上，也就是任何时候调用 pyItem.pyTopParent
得到的应该是同一个窗口实例。
"""

import weakref
import BigWorld
import ItemTypeEnum
import event.EventCenter as ECenter
from bwdebug import ERROR_MSG
from Function import Functor
from VehicleHelper import isVehicleBook, isVehicleEquip

from Weaker import WeakSet
from ExtraEvents import ControlEvent
from AbstractTemplates import Singleton

CUSTOM_ITEM_TYPE_PET 		= 1
CUSTOM_ITEM_TYPE_VEHICLE 	= 2
CUSTOM_ITEM_TYPE_LVLIMIT	= 3


class ItemsBrush( Singleton ) :

	def __init__( self ) :
		self.__typesToParents = {}								# 物品类型到窗口的映射表
		self.__parentsToItems = {}								# 窗口到物品格的映射表
		self.__refToWindows = []								# 窗口的弱引用列表

		self.__triggers = {}
		self.__registerEvents()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerEvents( self ) :
		"""
		"""
		self.__triggers["EVT_ON_PLAYER_UP_VEHICLE"] = self.__onVehicleUpdate		# 上骑宠
		self.__triggers["EVT_ON_PLAYER_DOWN_VEHICLE"] = self.__onVehicleUpdate		# 下骑宠
		self.__triggers["EVT_ON_VEHICLE_LEVEL_UPDATE"] = self.__onVehicleUpdate		# 骑宠等级改变
		self.__triggers["EVT_ON_PET_ENTER_WORKLD"] = self.__onPetUpdate				# 召唤宠物
		self.__triggers["EVT_ON_PET_WITHDRAWED"] = self.__onPetUpdate				# 收回宠物
		self.__triggers["EVT_ON_PET_LEVEL_CHANGE"] = self.__onPetUpdate				# 宠物等级改变
		self.__triggers["EVT_ON_ROLE_LEVEL_CHANGED"] = self.__onPlayerLevelUpdate	# 玩家等级改变
		for trigger in self.__triggers.iterkeys() :
			ECenter.registerEvent( trigger, self )

	# -------------------------------------------------
	def __onVehicleUpdate( self, *args ) :
		"""
		骑宠类型的道具刷新
		"""
		self.__brushItems( CUSTOM_ITEM_TYPE_VEHICLE )

	def __onPetUpdate( self, *args ) :
		"""
		宠物类型的道具刷新
		"""
		self.__brushItems( CUSTOM_ITEM_TYPE_PET )

	def __onPlayerLevelUpdate( self, *args ) :
		"""
		跟角色等级相关的道具刷新
		"""
		self.__brushItems( CUSTOM_ITEM_TYPE_LVLIMIT )
		self.__neatenLVLimitItems()

	# -------------------------------------------------
	def __onWindowShows( self, pyWnd ) :
		"""
		绑定的窗口打开时调用
		"""
		pyItems = self.__parentsToItems.get( id( pyWnd ) )
		if pyItems :
			for pyItem in pyItems :
				pyItem.updateUseStatus( pyItem.itemInfo.checkUseStatus() )	# 更新物品的可使用状态
		elif pyItems is None :
			ERROR_MSG( "Window %s( %i ) isn't exist in the items brush!" % ( str( pyWnd ), id( pyWnd ) ) )

	def __onWindowReleases( self, parentId, weaker ) :
		"""
		绑定的窗口释放时调用
		"""
		self.__removeWindow( parentId )
		self.__refToWindows.remove( weaker )

	# -------------------------------------------------
	def __removeWindow( self, parentId ) :
		"""
		移除掉窗口相关的数据
		"""
		pyItems = self.__parentsToItems.get( parentId )
		if pyItems is not None :
			del self.__parentsToItems[ parentId ]
		for itemType, parents in self.__typesToParents.items() :
			if parentId not in parents : continue
			parents.remove( parentId )
			if len( parents ) == 0 :
				del self.__typesToParents[ itemType ]

	# -------------------------------------------------
	def __brushItems( self, itemType ) :
		"""
		刷新指定类型道具的界面表现
		"""
		parents = self.__typesToParents.get( itemType )
		if parents is None : return
		for parentId in parents :
			pyItems = self.__parentsToItems.get( parentId )
			if not pyItems : continue
			pyItems = pyItems.set()										# 将哈希表转换为列表
			if not pyItems[0].pyTopParent.visible : continue			# 如果物品所在的窗口当前不可见，则不刷新
			for pyItem in pyItems :
				if self.__convertType( pyItem ) is itemType :
					pyItem.updateUseStatus( pyItem.itemInfo.checkUseStatus() )

	def __convertType( self, pyItem ) :
		"""
		将道具的类型转换为本模块自定义的类型，例如：
		将宠物的红和蓝统一定义为宠物类型道具
		"""
		baseItem = pyItem.itemInfo.baseItem
		itemType = baseItem.getType()
		if itemType in ItemTypeEnum.PET_DRUG_LIST:
				return CUSTOM_ITEM_TYPE_PET
		elif isVehicleBook( baseItem ) or isVehicleEquip( baseItem ) :
			return CUSTOM_ITEM_TYPE_VEHICLE
		elif baseItem.getReqLevel() > 1 :
			if not baseItem.queryReqClasses() or \
			BigWorld.player().getClass() in baseItem.queryReqClasses() :
				return CUSTOM_ITEM_TYPE_LVLIMIT
		return None

	# -------------------------------------------------
	def __neatenLVLimitItems( self ) :
		"""
		整理角色相关的等级限制物品
		"""
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def attach( self, pyItem ) :
		"""
		绑定道具物品格子
		"""
		if pyItem.itemInfo is None :							# 如果道具已被移走
			self.detach( pyItem )								# 则将其移除
			return
		itemType = self.__convertType( pyItem )
		if itemType is None :									# 如果不是需要更新的道具类型
			self.detach( pyItem )								# 则将其移除
			return
		# 以下操作是保存物品类型到窗口的映射
		parentId = id( pyItem.pyTopParent )						# 获取窗口的唯一ID（其实是其内存地址）
		parents = self.__typesToParents.get( itemType )
		if parents is None :
			self.__typesToParents[ itemType ] = set( [ parentId ] )
		else :
			parents.add( parentId )
		# 以下操作是保存窗口到物品格的映射
		pyItems = self.__parentsToItems.get( parentId )
		if pyItems is None :
			showEvent = getattr( pyItem.pyTopParent, "onBeforeShow", None )
			if isinstance( showEvent, ControlEvent ) :			# 绑定窗口打开的消息，以便在窗口打开时刷新一遍界面表现
				showEvent.bind( self.__onWindowShows )
			self.__parentsToItems[ parentId ] = WeakSet( [ pyItem ] )
			realseCb = Functor( self.__onWindowReleases, parentId )	# 对父窗口添加弱引用，以便在窗口释放时得到回调通知，释放相关资源
			self.__refToWindows.append( weakref.ref( pyItem.pyTopParent, realseCb ) )
		else :
			pyItems.add( pyItem )

	def detach( self, pyItem ) :
		"""
		移除道具物品格子
		"""
		parentId = id( pyItem.pyTopParent )
		pyItems = self.__parentsToItems.get( parentId )
		if pyItems is None : return
		if pyItem in pyItems :
			pyItems.remove( pyItem )							# 从窗口和物品格的映射表中移除
		if len( pyItems ) == 0 :								# 如果该窗口不再有需刷新的物品格
			for itemType, parents in self.__typesToParents.iteritems() :
				if parentId not in parents : continue
				parents.remove( parentId )

	def clearDataOfWindow( self, pyWnd ) :
		"""
		该接口提供给外部调用，可将窗口相关的道具格
		子的所有数据从物品刷中清除
		"""
		showEvent = getattr( pyWnd, "onBeforeShow", None )
		if isinstance( showEvent, ControlEvent ) :				# 解绑窗口打开的消息
			showEvent.unbind( self.__onWindowShows )
		self.__removeWindow( id( pyWnd ) )

	# -------------------------------------------------
	def onEvent( self, evtMacro, *args ) :
		"""
		绑定的事件触发时调用
		"""
		self.__triggers[evtMacro]( *args )


itemsBrush = ItemsBrush()

