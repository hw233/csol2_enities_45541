# -*- coding: gb18030 -*-
#
# $Id: ListPanel.py,v 1.36 2008-08-25 07:06:18 huangyongwei Exp $

"""
implement list items panel calss
items in this panel can be selected
2006/09/16 : writen by huangyongwei
"""

"""
composing :
	WindowsGUIComponent
	scroll bar
"""

import weakref
from guis import *
from ListItem import ListItem
from ItemsPanel import ItemsPanel

class ListPanel( ItemsPanel ) :
	def __init__( self, panel, scrollBar, pyBinder = None ) :
		ItemsPanel.__init__( self, panel, scrollBar, pyBinder )

		self.__selectable = True					# 选项是否可被选中
		self.__pySelItem = None						# 当前选中的选项
		self.__pyHighlightItem = None				# 当前处于高亮状态的选项
		self.__autoSelect = True					# 是否自动选中鼠标按下处的选项
		self.__mouseUpSelect = False				# 鼠标提起时选中选项
		self.__rMouseSelect = False					# 是否允许鼠标右键选中选项（功能与左键一样）

	def __del__( self ) :
		ItemsPanel.__del__( self )
		if Debug.output_del_ListPanel :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		ItemsPanel.generateEvents_( self )
		self.__onItemSelectChanged = self.createEvent_( "onItemSelectChanged" )
		self.__onItemLClick = self.createEvent_( "onItemLClick" )
		self.__onItemRClick = self.createEvent_( "onItemRClick" )

	@property
	def onItemSelectChanged( self ) :
		return self.__onItemSelectChanged

	@property
	def onItemLClick( self ) :
		return self.__onItemLClick

	@property
	def onItemRClick( self ) :
		return self.__onItemRClick


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __viewSelectItem( self ) :
		pySelItem = self.pySelItem
		trueTop = pySelItem.top - self.scroll
		trueBottom = pySelItem.bottom - self.scroll
		if trueTop < 0 :
			self.scroll = pySelItem.top
		elif trueBottom > self.height :
			self.scroll = pySelItem.bottom - self.height


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onItemSelectChanged_( self, pyItem, selected ) :
		if not selected :
			self.__pySelItem = None
			self.onItemSelectChanged( None )
		elif pyItem != self.__pySelItem :
			if self.__pySelItem :
				self.__pySelItem.onSelectChanged.unbind( self.onItemSelectChanged_ )
				self.__pySelItem.selected = False
				self.__pySelItem.onSelectChanged.bind( self.onItemSelectChanged_ )
			self.__pySelItem = pyItem
			self.__viewSelectItem()
			self.onItemSelectChanged( pyItem )

	def onItemLClick_( self, pyItem ) :
		self.onItemLClick( pyItem )

	def onItemRClick_( self, pyItem ) :
		self.onItemRClick( pyItem )

	def onItemHighlight_( self, pyItem ) :
		pyHItem = self.pyHighlightItem
		if pyItem == pyHItem : return
		if pyHItem : pyHItem.setState( UIState.COMMON )
		self.__pyHighlightItem = weakref.ref( pyItem )

	# -------------------------------------------------
	def onScroll_( self, value ) :
		"""
		内容随滚动条滚动时被调用
		"""
		ItemsPanel.onScroll_( self, value )
		pyHItem = self.pyHighlightItem
		if pyHItem is not None :
			pyHItem.onMouseLeave_()

	# -------------------------------------------------
	def onLMouseDown_( self, key, mods ) :
		ItemsPanel.onKeyDown_( self, key, mods )
		self.tabStop = True
		return True

	def onKeyDown_( self, key, mods ) :
		pyCon = uiHandlerMgr.getTabInUI()
		if pyCon != self :
			return ItemsPanel.onKeyDown_( self, key, mods )
		if mods == 0 and key == KEY_UPARROW :
			self.upSelect()
			return True
		elif mods == 0 and key == KEY_DOWNARROW :
			self.downSelect()
			return True
		return False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addItem( self, pyItem, index=-1 ) :
		"""
		add an python item
		@type			pyItem : instance of python gui
		@param			pyItem : the item you want to remove
		@return				   : None
		"""
		if isDebuged :
			assert isinstance( pyItem, ListItem ), "item '%s' added to the list panel must inherit from ListItem!" % str( pyItem )
		pre = pyItem not in self.pyItems_
		if pre : pyItem.selected = False
		ItemsPanel.addItem( self, pyItem, index )
		lat = pyItem in self.pyItems_
		if not ( pre and lat ) : return
		pyItem.autoSize = False
		pyItem.width = self.width
		pyItem.rMouseSelect = self.__rMouseSelect
		pyItem.onSelectChanged.bind( self.onItemSelectChanged_ )
		pyItem.onLClick.bind( self.onItemLClick_ )
		pyItem.onRClick.bind( self.onItemRClick_ )
		pyItem.onHighlight.bind( self.onItemHighlight_ )
		pyItem.selectable = self.selectable
		pyItem.mouseUpSelect = self.mouseUpSelect
		if self.__autoSelect and self.itemCount == 1 :
			self.pyItems[0].selected = True

	def addItems( self, pyItems ) :
		"""
		add a list of python items
		@type			pyItems : a list of python items
		@param			pyItems : the items you want to remove
		@return					: None
		"""
		for pyItem in pyItems :
			self.addItem( pyItem )

	def removeItem( self, pyItem ) :
		"""
		remove a python item
		@type			pyItem : instance of python item
		@param			pyItem : the item you want to remove
		@return				   : None
		"""
		pySelItem = self.pySelItem
		selIndex = -1
		pre = pyItem in self.pyItems_									# 要删除的 Item 是否在我的选项列表中
		isSelItem = pySelItem == pyItem									# 要删除的选项是否是当前选中的选项
		if pre and isSelItem :
			selIndex = self.pyItems_.index( pyItem )					# 当前选中选项的索引
		ItemsPanel.removeItem( self, pyItem )							# 调用基类方法移除指定选项
		lat = pyItem not in self.pyItems_								# 判断要移除的选项是否还在选项列表中（是否移除成功）
		if not ( pre and lat ) : return									# 移除失败则返回

		pyItem.onSelectChanged.unbind( self.onItemSelectChanged_ )		# 取消
		pyItem.onLClick.unbind( self.onItemLClick_ )					# 所有的
		pyItem.onRClick.unbind( self.onItemRClick_ )					# 事件
		pyItem.onHighlight.unbind( self.onItemHighlight_ )				# 绑定
		if isSelItem : pySelItem.selected = False						# 如果移除的选项是当前被选中的选项，则取消选项的选中状态
		if not isSelItem : return										# 如果删除的选项不是当前选中的选项

		pySelItem = None
		if self.__autoSelect :											# 如果自动选择开关是打开的
			if self.itemCount :
				if selIndex == 0 : pySelItem = self.pyItems_[0]			# 如果之前选中的是第一个
				elif selIndex == self.itemCount : pySelItem = self.pyItems_[-1]		# 如果之前选中的是最后一个
				else : pySelItem = self.pyItems_[selIndex]
				pySelItem.selected = True								# 选中新的选项
			else :
				self.__pySelItem = None									# 则，将当前选中选项设置为 None，表示没有选中选项
		else :															# 如果自动选择开关没有打开
			self.__pySelItem = None										# 则，将当前选中选项设置为 None，表示没有选中选项
		self.onItemSelectChanged( pySelItem )							# 触法选择改变事件

	def clearItems( self ) :
		"""
		clear all python items
		"""
		for pyItem in self.pyItems_ :
			pyItem.onSelectChanged.unbind( self.onItemSelectChanged_ )
			pyItem.onLClick.unbind( self.onItemLClick_ )
			pyItem.onRClick.unbind( self.onItemRClick_ )
			pyItem.onHighlight.unbind( self.onItemHighlight_ )
			if pyItem.selected : pyItem.selected = False
		ItemsPanel.clearItems( self )
		pySelItem = self.__pySelItem
		self.__pySelItem = None
		if pySelItem is not None :
			self.onItemSelectChanged( None )

	# -------------------------------------------------
	def upSelect( self ) :
		if self.itemCount == 0 : return True
		pyItems = self.pyItems
		selIndex = self.selIndex
		if selIndex < 0 :
			pyItems[-1].selected = True
		elif selIndex == 0 :
			pyItems[self.itemCount - 1].selected = True
		elif selIndex > 0 :
			pyItems[selIndex - 1].selected = True

	def downSelect( self ) :
		if self.itemCount == 0 : return
		pyItems = self.pyItems
		selIndex = self.selIndex
		if selIndex < 0 or selIndex == self.itemCount - 1 :
			pyItems[0].selected = True
		elif selIndex < self.itemCount - 1 :
			pyItems[selIndex + 1].selected = True


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getSelItem( self ) :
		return self.__pySelItem

	def _setSelItem( self, pyItem ) :
		if pyItem is None :
			if self.__pySelItem :
				self.__pySelItem.selected = False
		elif pyItem not in self.pyItems_ :
			DEBUG_MSG( "item %s is not belong to the list panel!" )
		else :
			pyItem.selected = True

	# ---------------------------------------
	def _getHighlightItem( self ) :
		if self.__pyHighlightItem is None :
			return None
		return self.__pyHighlightItem()

	# ---------------------------------------
	def _getSelIndex( self ) :
		try :
			return self.pyItems.index( self.pySelItem )
		except : pass
		return -1

	def _setSelIndex( self, index ) :
		try :
			self.pyItems[index].selected = True
		except :
			DEBUG_MSG( "index %d is out of range!" % index )

	# -------------------------------------------------
	def _getAutoSelect( self ) :
		return self.__autoSelect

	def _setAutoSelect( self, auto ) :
		if not self.__selectable : return
		self.__autoSelect = auto

	# -------------------------------------------------
	def _getSelectable( self ) :
		return self.__selectable

	def _setSelectable( self, selectable ) :
		if not selectable : self.autoSelect = False
		self.__selectable = selectable
		for pyItem in self.pyItems :
			pyItem.selectable = selectable

	# -------------------------------------------------
	def _getMouseUpSelect( self ) :
		return self.__mouseUpSelect

	def _setMouseUpSelect( self, value ) :
		self.__mouseUpSelect = value
		for pyItem in self.pyItems :
			pyItem.mouseUpSelect = value

	# ---------------------------------------
	def _getRMouseSelect( self ) :
		return self.__rMouseSelect

	def _setRMouseSelect( self, value ) :
		self.__rMouseSelect = value
		for pyItem in self.pyItems :
			pyItem.rMouseSelect = value

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pySelItem = property( _getSelItem, _setSelItem )					# get current selected item
	pyHighlightItem = property( _getHighlightItem )						# get item which is in highlight state currently
	selIndex = property( _getSelIndex, _setSelIndex )					# get or set current selected item's index
	autoSelect = property( _getAutoSelect, _setAutoSelect )				# if it is True, when remove an selected item, it will auto select a new item
	selectable = property( _getSelectable, _setSelectable )				# default is True
	mouseUpSelect = property( _getMouseUpSelect, _setMouseUpSelect )	# if it is true, the item will be selected by click
																		# otherwise the item will be selected by mouse down
																		# default is false
	rMouseSelect = property( _getRMouseSelect, _setRMouseSelect )		# if it true, the right mouse can select a item also
																		# default is false
