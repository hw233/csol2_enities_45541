# -*- coding: gb18030 -*-
#
# $Id: ContextMenu.py,v 1.29 2008-08-30 09:04:58 huangyongwei Exp $

"""
implement contextmenu class。

2008.04.15 : writen by huangyongwei
"""

import weakref
from guis import *
from guis.UIFixer import hfUILoader
from guis.common.PyGUI import PyGUI
from guis.common.FlexExWindow import HVFlexExWindow
from Control import Control
from StaticText import StaticText
from CheckBox import CheckBox


# --------------------------------------------------------------------
# items panel
# --------------------------------------------------------------------
class Items( HVFlexExWindow ) :
	def __init__( self, panel = None, pyParent = None, pyMenu = None ) :
		if panel is None :
			panel = hfUILoader.load( "guis_v2/controls/contextmenu/panel.gui" )
		HVFlexExWindow.__init__( self, panel )
		self.__itemWidth = 0										# 选项宽度
		self.__pyMenu = None										# 所属菜单
		self.__pyParentItem = None									# 所属菜单选项
		self.__initialize( panel, pyParent, pyMenu )
		self.__pyItems = []

	def subclass( self, panel, pyParent, pyMenu ) :
		HVFlexExWindow.subclass( self, panel )
		self.__initialize( self, panel, pyParent, pyMenu )

	def dispose( self ) :
		self.clear()
		HVFlexExWindow.dispose( self )

	def __del__( self ) :
		self.clear()
		HVFlexExWindow.__del__( self )
		if Debug.output_del_ContextMenu :
			INFO_MSG( "delete Context MenuItem:<%i>" % id( self ) )

	# ---------------------------------------
	def __initialize( self, panel, pyParent, pyMenu ) :
		if panel is None : return
		self.posZSegment = ZSegs.L2									# 设置为第二层
		self.movable_ = False										# 不可以被移动
		self.activable_ = False										# 不可激活
		self.hitable_ = True										# 屏蔽鼠标所在位置
		self.escHide_ = True										# 可以按 esc 隐藏
		self.__pyClipPanel = PyGUI( panel.clipPanel )				# 菜单项板面
		if pyMenu : self.__pyMenu = weakref.ref( pyMenu )			# 设置所属菜单
		if pyParent : self.__pyParentItem = weakref.ref( pyParent )	# 设置所属菜单项

		self.addToMgr( "contextMenuItems" )							# 添加到 UI 管理器


	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __repr__( self ) :
		try :
			return "MenuItems" + str( self.__pyItems )
		except :
			return "MenuItems<%s>" % id( self )

	def __str__( self ) :
		return self.__repr__()

	def __contains__( self, pyItem ) :
		return pyItem in self.__pyItems

	def __iter__( self ) :
		return self.__pyItems.__iter__()

	def __getitem__( self, index ) :
		return self.__pyItems[index]

	def __getslice__( self, start, end ) :
		return self.__pyItems.__getslice__( start, end )

	def __radd__( self, pyItems ) :
		return pyItems + self.__pyItems


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getItemMaxRealWidth( self ) :
		"""
		获得菜单项中最大的真实宽度
		"""
		maxWith = 0
		for pyItem in self.__pyItems :
			maxWith = max( pyItem.getRealWidth(), maxWith )
		return maxWith

	# -------------------------------------------------
	def __pasteItem( self, pyItem ) :
		"""
		粘贴一个选项
		"""
		pyPItem = self.pyParentItem
		while pyPItem is not None :						# 判断选项是否是我的父选项（避免添加父选项造成死循环）
			if pyPItem == pyItem :
				DEBUG_MSG( "you can't add its parent node as its child node!" )
				return False
			pyPItem = pyPItem.pyParent

		if pyItem.pySelfItems is not None :				# 如果菜单项已经在我的列表中，则删除之并重新添加
			pyItem.pySelfItems.remove( pyItem )
		self.__pyClipPanel.addPyChild( pyItem )
		return True

	def __layoutItems( self ) :
		"""
		重新排列菜单位置，pyStart 表示从哪个菜单项开始设置
		"""
		top = 0
		for pyItem in self.__pyItems :
			if not pyItem.visible :
				continue
			else :
				pyItem.top = top
				top = pyItem.bottom
		if top == 0 and self.pyParentItem :						# 如果没有可见菜单项
			self.pyParentItem.close()							# 则通知所属父菜单项收起全部子菜单
		else :													# 否则重新调整菜单列表高度
			space = self.height - self.__pyClipPanel.bottom
			self.__pyClipPanel.height = top
			height = self.__pyClipPanel.bottom + space
			HVFlexExWindow._setHeight( self, height )
		self.__rewidth( self.__itemWidth )						# 设置当前的宽度为菜单项中最大真实宽度

	def __rewidth( self, width ) :
		"""
		重新设置菜单项的宽度
		"""
		for pyItem in self.__pyItems :
			pyItem.rewidth__( width )
		space = self.width - self.__pyClipPanel.right
		self.__pyClipPanel.width = width
		width = self.__pyClipPanel.right + space
		HVFlexExWindow._setWidth( self, width )

	# -------------------------------------------------
	def __bindAddedItem( self, pyItem ) :
		"""
		绑定一个添加的菜单项
		"""
		pyItem.setMenu__( self.pyMenu )
		pyItem.setSelfItems__( self )
		width = pyItem.getRealWidth()
		if width > self.__itemWidth :							# 菜单宽度为最大宽度选项的宽度
			self.__itemWidth = width
		pyItem.rewidth__( self.__itemWidth )					# 设置新添加选项的宽度
		self.__layoutItems()
		if self.pyParentItem :
			self.pyParentItem.onItemAdded__( pyItem )

	# ----------------------------------------------------------------
	# friend methods
	# ----------------------------------------------------------------
	def setMenu__( self, pyMenu ) :
		"""
		设置所属菜单
		"""
		if pyMenu is None :
			self.__pyMenu = None
		else :
			self.__pyMenu = weakref.ref( pyMenu )
		for pyItem in self.__pyItems :
			pyItem.setMenu__( pyMenu )

	# -------------------------------------------------
	def onItemRewidth__( self, pyItem ) :
		"""
		当某个菜单项的宽度改变时，该函数被调用
		"""
		width = pyItem.getRealWidth()
		if width > self.__pyClipPanel.width :
			self.__rewidth( width )

	# -------------------------------------------------
	def getPopUpItem__( self ) :
		"""
		获取处于弹出状态的子菜单项
		"""
		for pyItem in self.__pyItems :
			if pyItem.isPopUp :
				return pyItem
		return None

	def onItemToogleVisible__( self, pyItem ) :
		"""
		当某个子菜单项隐藏/显示时被调用
		"""
		self.__layoutItems()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def isMouseHitSubMenu_( self ) :
		if self.isMouseHit() : return True
		for pyItem in self.__pyItems :
			if pyItem.isMouseHitSubMenu__() :
				return True
		return False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def adds( self, pyItems ) :
		"""
		添加一组菜单项
		@type			pyItems : list/tuple of MenuItem
		@param			pyItems : 要添加的菜单选项列表
		"""
		for pyItem in pyItems :
			self.add( pyItem )

	def add( self, pyItem ) :
		"""
		添加一个菜单项
		@type			pyItem : MenuItem
		@param			pyItem : 要添加的菜单选项
		"""
		if not self.__pasteItem( pyItem ) :
			return
		self.__pyItems.append( pyItem )
		self.__bindAddedItem( pyItem )

	def insert( self, index, pyItem ) :
		"""
		插入一个菜单项
		@type			index  : int
		@param			index  : 插入的位置
		@type			pyItem : MenuItem
		@param			pyItem : 要插入的菜单选项
		"""
		if index < 0 or index >= self.count :
			DEBUG_MSG( "index is out of range!" )
			return
		if not self.__pasteItem( pyItem ) :
			return
		self.__pyItems.insert( index, pyItem )
		self.__bindAddedItem( pyItem )

	def remove( self, pyItem ) :
		"""
		删除一个菜单项
		@type			pyItem : MenuItem
		@param			pyItem : 要删除的菜单选项
		"""
		if isDebuged :
			assert pyItem in self.__pyItems, "%s is not in self!" % pyItem
		self.__pyClipPanel.delPyChild( pyItem )
		self.__pyItems.remove( pyItem )
		pyItem.setMenu__( None )
		pyItem.setSelfItems__( None )
		self.__itemWidth = 0
		for pyItem in self.__pyItems :
			width = pyItem.getRealWidth()
			if width > self.__itemWidth :
				self.__itemWidth = width
		if self.count > 0 :
			self.__layoutItems()
		else :
			self.hide()
		if self.pyParentItem :
			self.pyParentItem.onItemRemoved__( pyItem )

	def clear( self ) :
		"""
		清除所有菜单项
		"""
		for pyItem in self.__pyItems :
			self.__pyClipPanel.delPyChild( pyItem )
			pyItem.setMenu__( None )
			pyItem.setSelfItems__( None )
		if self.pyParentItem :
			self.pyParentItem.onItemRemoveds__( pyItem )
		self.__itemWidth = 0
		self.hide()
		self.__pyItems = []

	def reset( self ) :
		"""
		重新设置所有选项状态
		"""
		for pyItem in self.__pyItems :
			pyItem.reset()

	# -------------------------------------------------
	def show( self, pyOwner = None ) :
		self.reset()
		HVFlexExWindow.show( self, pyOwner, False )

	def hide( self ) :
		for pyItem in self.__pyItems :
			if pyItem.isPopUp :
				pyItem.close()
		HVFlexExWindow.hide( self )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getMenu( self ) :
		if self.__pyMenu is None :
			return None
		return self.__pyMenu()

	def _getParentItem( self ) :
		if self.__pyParentItem is None :
			return None
		return self.__pyParentItem()

	# -------------------------------------------------
	def _getCount( self ) :
		return len( self.__pyItems )

	# -------------------------------------------------
	def _getFirst( self ) :
		if self.count > 0 :
			return self.__pyItems[0]
		return None

	def _getLast( self ) :
		if self.count > 0 :
			return self.__pyItems[-1]
		return None

	# -------------------------------------------------
	def _getTopEdgeHeight( self ) :
		return self.__pyClipPanel.top

	def _getBottomEdgeHeight( self ) :
		return self.height - self.__pyClipPanel.bottom


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyMenu = property( _getMenu )											# 获取所属菜单
	pyParentItem = property( _getParentItem )								# 获取所属菜单项
	count = property( _getCount )											# 获取菜单项的数量
	pyFirst = property( _getFirst )											# 获取第一个菜单项
	pyLast = property( _getLast )											# 获取第二个菜单项
	width = property( HVFlexExWindow._getWidth )							# 获取菜单列表的宽度
	height = property( HVFlexExWindow._getHeight )							# 获取菜单列表的高度

	itemWidth = property( lambda self : self.__itemWidth )					# 获取菜单项的宽度
	topEdgeHeight = property( _getTopEdgeHeight )							# 获取顶边沿高度
	bottomEdgeHeight = property( _getBottomEdgeHeight )						# 获取底边沿高度


# --------------------------------------------------------------------
# implement context menu class
# --------------------------------------------------------------------
"""
composing :
	GUI.Window
		-- lt : GUI.Simple
		-- t  : GUI.Simple ( tiled = True )
		-- rt : GUI.Simple
		-- l  : GUI.Simple ( tiled = True )
		-- bg : GUI.Simple ( tiled = True )
		-- r  : GUI.Simple ( tiled = True )
		-- lb : GUI.Simple
		-- b  : GUI.Simple ( tiled = True )
		-- rb : GUI.Simple

		-- clipPanel : GUI.Window
"""

class ContextMenu( Items ) :
	cg_pyMenus_ = WeakSet()					# 记录下所有菜单实例

	def __init__( self, panel = None ) :
		Items.__init__( self, panel, None, self )
		LastKeyUpEvent.attach( ContextMenu.__onLastKeyUp )		# 不会重复附加的，如果事件列表中已经有，则不会再附加，因此这里不需要判断
																# LastKeyEvent 列表中是否有被注册的菜单函数
		self.__autoPopUp = True									# 是否自动弹出，如果为 True，则鼠标右键点击 binders 时，菜单将会弹出
		self.__pyBinders = WeakList()							# 触发ui，如果 autoPopUp 为 True，则右键点击这些 binders 则会弹出菜单
																# 如果 autoPopUp 为 False，则左键点击这些 Triggers，将会弹出/收起菜单
		self.__vsDetectCBID = 0									# 侦测 binder 是否可见，不可见则隐藏菜单
		self.__loadingHide = True								# 进入传送状态时是否关闭菜单

		ContextMenu.cg_pyMenus_.add( self )					# 添加到全局表

	def __del__( self ) :
		if len( ContextMenu.cg_pyMenus_ ) == 0 :				# 如果所有菜单实例都被删除
			LastKeyUpEvent.detach( ContextMenu.__onLastKeyUp )	# 则吊销 LastKeyUpEvent 事件
		self.__unbindBindersClickEvent()						# 取消绑定控件的事件绑定
		self.__pyBinders.clear()								# 取消对绑定控件的引用
		Items.__del__( self )
		if Debug.output_del_ContextMenu :
			INFO_MSG( "delete Context Menu:<%i>" % id( self ) )


	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __repr__( self ) :
		return "ContextMenu instance at %s" % hex( id( self ) )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		产生事件
		"""
		Items.generateEvents_( self )
		self.__onBeforePopUp = self.createEvent_( "onBeforePopup" )				# 当菜单弹出时被触发
		self.__onBeforeClose = self.createEvent_( "onBeforeClose" )				# 当菜单关闭前被触发
		self.__onAfterPopUp = self.createEvent_( "onAfterPopUp" )				# 当菜单弹出后被触发
		self.__onAfterClose = self.createEvent_( "onAfterClose" )				# 当菜单收起后被触发
		self.__onItemClick = self.createEvent_( "onItemClick" )					# 当一个菜单项被点击时被触发
		self.__onItemCheckChanged = self.createEvent_( "onItemCheckChanged" )	# 当一个菜单项被选中时被触发

	@property
	def onBeforePopup( self ) :
		"""
		当菜单弹出前被触发（如果该事件接收者返回 －1，则菜单弹出失败）
		"""
		return self.__onBeforePopUp

	@property
	def onBeforeClose( self ) :
		"""
		当菜单关闭前被触发
		"""
		return self.__onBeforeClose

	@property
	def onAfterPopUp( self ) :
		"""
		当菜单弹出后被触发
		"""
		return self.__onAfterPopUp

	@property
	def onAfterClose( self ) :
		"""
		当菜单收起后被触发
		"""
		return self.__onAfterClose

	@property
	def onItemClick( self ) :
		"""
		当一个菜单项被点击时被触发
		"""
		return self.__onItemClick

	@property
	def onItemCheckChanged( self ) :
		"""
		当一个菜单项被选中时被触发
		"""
		return self.__onItemCheckChanged


	# ---------------------------------------------------------------
	# private
	# ---------------------------------------------------------------
	def __locateToCursor( self ) :
		"""
		自动设置弹出位置
		"""
		px, py = csol.pcursorPosition()
		if px + self.width <= BigWorld.screenWidth() :
			self.left = px
		else :
			self.right = px
		if py + self.height <= BigWorld.screenHeight() :
			self.top = py
		else :
			self.bottom = py

	def __detectBinderVisible( self ) :
		"""
		侦测 binder 是否可见，不可见则隐藏菜单
		"""
		if not self.rvisible or len( self.__pyBinders ) == 0 :
			BigWorld.cancelCallback( self.__vsDetectCBID )
			return
		for pyBinder in self.__pyBinders :
			if pyBinder.rvisible :
				self.__vsDetectCBID = BigWorld.callback( 1.5, Functor( self.__detectBinderVisible ) )
				return
		self.hide()
		BigWorld.cancelCallback( self.__vsDetectCBID )

	def __bindBindersClick( self, pyBinder = None ) :
		"""
		注册 binder 的左键点击事件, 如果 pyBinder 为 None, 则注册当前所有 binder
		如果 autoPopUp 属性值为 False，则默认左键点击 binder 时，显示菜单
		"""
		def bind( pyBinder ) :
			if hasattr( pyBinder, "onLClick" ) :
				pyBinder.onLClick.bind( self.__onBinderLClick )		# 注意：bind 函数有两个版本，这里就算对同一个 binder 重复绑定多次也不会出现重复

		if pyBinder is None :
			for pyBinder in self.__pyBinders :
				bind( pyBinder )
		else :
			bind( pyBinder )

	def __unbindBindersClickEvent( self, pyBinder = None ) :
		"""
		反注册 binder 的左键点击事件，如果 pyBinder 为 None，则取消注册当前所有 binder
		"""
		def unbind( pyBinder ) :
			if hasattr( pyBinder, "onLClick" ) :
				pyBinder.onLClick.unbind( self.__onBinderLClick )

		if pyBinder is None :
			for pyBinder in self.__pyBinders :
				unbind( pyBinder )
		else :
			unbind( pyBinder )

	# -------------------------------------------------
	def __onBinderLClick( self, pyBinder ) :
		"""
		左键点击触发的 UI 时被调用
		"""
		if self.__autoPopUp : return
		if not self.rvisible :
			self.show( pyBinder )
		else :
			self.hide()

	# ---------------------------------------
	def __isHitTrigger( self ) :
		"""
		判断鼠标是否落在某个 trigger 上
		"""
		for pyBinder in self.__pyBinders :
			if pyBinder.isMouseHit() :
				return True
		return False

	def __onLastKeyDown( self, key, mods ) :
		"""
		无论什么情况下，按下键盘键或鼠标时都会被调用
		"""
		if self.isMouseHitMenu() :							# 如果鼠标在菜单上
			return
		if not self.autoPopUp :								# 如果菜单不是右键点击自动弹出的
			return
		if self.__isHitTrigger() and \
			key == KEY_RIGHTMOUSE :							# 如果鼠标在菜单归属控件上，并且在其下按下鼠标右键
				return
		if key == KEY_LEFTMOUSE or \
			key == KEY_RIGHTMOUSE or \
			key == KEY_RETURN or \
			key == KEY_NUMPADENTER :
				self.hide()

	@staticmethod
	def __onLastKeyUp( key, mods ) :
		"""
		无论什么情况下，提起键盘键或鼠标时都会被调用
		"""
		if mods != 0 : return
		if key != KEY_RIGHTMOUSE : return				# 如果提起的不是右键，则不会弹出菜单
		pyRoot = rds.ruisMgr.getMouseHitRoot()
		if pyRoot is None : return						# 右键没有击中任何 UI，则不会弹出菜单
		for pyMenu in ContextMenu.cg_pyMenus_ :
			for pyBinder in pyMenu.__pyBinders :
				if not pyBinder.rvisible :				# 如果绑定控件不可见
					continue
				if pyBinder.pyTopParent != pyRoot :		# 如果鼠标没有在绑定控件的父窗口上
					continue
				if not pyBinder.isMouseHit() :			# 如果鼠标没有在绑定控件上
					continue
				pyMenu.popup( pyBinder )				# 如果鼠标右键点击了菜单绑定控件，则显示菜单
				return


	# ---------------------------------------------------------------
	# frient methods
	# ---------------------------------------------------------------
	def onItemClick__( self, pyItem ) :
		"""
		当某个菜单项被点击时调用
		"""
		self.onItemClick( pyItem )
		if pyItem.clickClose :
			self.hide()										# 注释后点击任何选项都不关闭菜单

	def onItemCheckChanged__( self, pyItem ) :
		"""
		当某个菜单项被选中/取消选中状态时被调用
		"""
		self.onItemCheckChanged( pyItem )


	# ---------------------------------------------------------------
	# public
	# ---------------------------------------------------------------
	def afterStatusChanged( self, oldStatus, newStatus ) :
		"""
		游戏状态改变时调用
		"""
		if oldStatus == newStatus : return
		if newStatus == Define.GST_SPACE_LOADING :
			if self.visible and self.__loadingHide :
				self.hide()

	def isMouseHitMenu( self ) :
		"""
		判断鼠标是否落在菜单上，包括子菜单项
		"""
		return self.isMouseHitSubMenu_()

	# -------------------------------------------------
	def addBinder( self, pyBinder ) :
		"""
		添加一个绑定控件
		"""
		if pyBinder not in self.__pyBinders :
			self.__pyBinders.append( pyBinder )
			if not self.autoPopUp :
				self.__bindBindersClick( pyBinder )

	def addBinders( self, pyBinders ) :
		"""
		添加一组绑定控件
		"""
		for pyBinder in pyBinders :
			self.addBinder( pyBinder )

	def removeBinder( self, pyBinder ) :
		"""
		删除绑定控件
		"""
		if pyBinder in self.__pyBinders :
			self.__pyBinders.remove( pyBinder )
			self.__unbindBindersClickEvent( pyBinder )

	def clearBinders( self ) :
		"""
		删除所有绑定控件
		"""
		for pyBinder in self.__pyBinders :
			self.__unbindBindersClickEvent( pyBinder )
		self.__pyBinders.clear()

	# -------------------------------------------------
	def popup( self, pyOwner = None ) :
		"""
		弹出菜单（弹出菜单时，菜单的位置将会跟随鼠标）
		注：你可以注册 onBeforePopup 事件，在事件中选择性的决定是否要弹出菜单：
			onBeforePopup 返回 True 则显示，否则不显示。因此当你注册了 onBeforePopup 事件，并且要显示菜单，则事件中一定要返回 True
			同时你可以在 onBeforePopup 事件中设置菜单的位置
		"""
		pyItem = self.getPopUpItem__()						# 获得处于弹出状态的子菜单项
		if pyItem : pyItem.close()							# 先收起处于弹出状态的菜单项的子菜单
		if self.onBeforePopup() >= 0 :						# 在这里判断的目的是，使得菜单弹出之前，用户可以在 onBeforePopup 中修改菜单项
			if self.pyItems.count == 0 : return				# 没有任何菜单项，
			self.__locateToCursor()							# 自动设置菜单的位置为跟随鼠标
			Items.show( self, pyOwner )
			self.__detectBinderVisible()					# 侦测 binder 是否可见，不可见则隐藏菜单
			LastKeyDownEvent.attach( self.__onLastKeyDown )
			self.onAfterPopUp()
		elif self.rvisible :
			self.hide()

	def close( self ) :
		"""
		收起菜单
		"""
		self.hide()

	# ---------------------------------------
	def show( self, pyOwner = None ) :
		"""
		显示菜单（显示菜单时，菜单位置要自己设置）
		注：你可以注册 onBeforePopup 事件，在事件中选择性的决定是否要弹出菜单：
			onBeforePopup 返回 True 则显示，否则不显示。因此当你注册了 onBeforePopup 事件，并且要显示菜单，则事件中一定要返回 True
			同时你可以在 onBeforePopup 事件中设置菜单的位置
		"""
		pyItem = self.getPopUpItem__()						# 获得处于弹出状态的子菜单项
		if pyItem : pyItem.close()							# 先收起处于弹出状态的菜单项的子菜单
		if self.onBeforePopup() :							# 在这里判断的目的是，使得菜单弹出之前，用户可以在 onBeforePopup 中修改菜单项
			if self.pyItems.count == 0 : return				# 没有任何菜单项，
			Items.show( self, pyOwner )
			self.__detectBinderVisible()					# 侦测 binder 是否可见，不可见则隐藏菜单
			LastKeyDownEvent.attach( self.__onLastKeyDown )
			self.onAfterPopUp()
		elif self.rvisible :
			self.hide()

	def hide( self ) :
		"""
		隐藏菜单
		"""
		LastKeyDownEvent.detach( self.__onLastKeyDown )
		self.onBeforeClose()
		Items.hide( self )
		self.onAfterClose()


	# ---------------------------------------------------------------
	# property methods
	# ---------------------------------------------------------------
	def _setVisible( self, visible ) :
		raise "'visible' is a read-only property.\n'popup' and 'close' called to toggle context menu!"

	# -------------------------------------------------
	def _getItems( self ) :
		return self

	# -------------------------------------------------
	def _getAutoPopUp( self ) :
		return self.__autoPopUp

	def _setAutoPopUp( self, autoPopUp ) :
		self.__autoPopUp = autoPopUp
		if autoPopUp :
			self.__unbindBindersClickEvent()
		else :
			self.__bindBindersClick()

	# -------------------------------------------------
	def _getBinders( self ) :
		return self.__pyBinders[:]

	# -------------------------------------------------
	def _getLoadingHide( self ) :
		return self.__loadingHide

	def _setLoadingHide( self, loadingHide ) :
		self.__loadingHide = loadingHide

	# ---------------------------------------------------------------
	# properties
	# ---------------------------------------------------------------
	visible = property( Items._getVisible, _setVisible )						# 获取可见性
	pyItems = property( _getItems )												# 获取所有菜单项版面
	autoPopUp = property( _getAutoPopUp, _setAutoPopUp )						# 获取/设置是否自动弹出
	loadingHide = property( _getLoadingHide, _setLoadingHide )					# 获取/设置进入传送状态时是否关闭菜单

	pyBinders = property( _getBinders )											# 获取菜单所有绑定（所属）的控件


# --------------------------------------------------------------------
# implement menu item
# --------------------------------------------------------------------
class MenuItem( Control ) :
	__cg_commonItem = None
	__cg_checkableItem = None
	__cg_splitter = None

	def __init__( self, style = MIStyle.COMMON, item = None ) :
		"""
		@type					style : MACRO DEFINATION
		@param					style : 菜单样式，在 uidefine.py 中定义( 如果 item 不是 None，则该值无效 )
		@type					item  : engine ui
		@param					item  : 引擎 ui
		"""
		if MenuItem.__cg_commonItem is None :
			MenuItem.__cg_commonItem = GUI.load( "guis_v2/controls/contextmenu/commonitem.gui" )
			MenuItem.__cg_checkableItem = GUI.load( "guis_v2/controls/contextmenu/checkitem.gui" )
			MenuItem.__cg_splitter = GUI.load( "guis_v2/controls/contextmenu/splitter.gui" )

		if item is None :												# 如果没有传入的 UI，则加载默让的 UI
			if style == MIStyle.COMMON :
				item = util.copyGuiTree( MenuItem.__cg_commonItem )
			if style == MIStyle.CHECKABLE :
				item = util.copyGuiTree( MenuItem.__cg_checkableItem )
			if style == MIStyle.SPLITTER :
				item = util.copyGuiTree( MenuItem.__cg_splitter )
			uiFixer.firstLoadFix( item )
		Control.__init__( self, item )
		self.__pySubItems = None
		self.pyText_ = None											# 文本标签（如果没有，则表示是分隔条）
		self.pyCheckBox_ = None										# 复选框
		self.pyArrow_ = None										# 子菜单箭头
		self.state_ = UIState.COMMON								# 菜单状态
		self.__style = style										# 菜单样式
		self.__clickClose = True									# 点击菜单项后，是否关闭整个菜单(仅对没子菜单项的菜单项有效)
		self.__initialize( item, style )

		self.__pyMenu = None										# 所属的菜单
		self.__pySelfItems = None									# 所属菜单列表选项版面

	def dispose( self ) :
		if self.pySelfItems :
			self.pySelfItems.remove( self )
		if self.__pySubItems :
			self.__pySubItems.dispose()
		Control.dispose( self )

	def __del__( self ) :
		del self.__pyMenu
		if self.__pySubItems :
			self.__pySubItems.dispose()
		Control.__del__( self )
		if Debug.output_del_ContextMenu :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, item, style ) :
		if hasattr( item, "lbText" ) :									# 如果有标签
			self.pyText_ = StaticText( item.lbText )
			self.focus = True
			self.crossFocus = True
			self.__pySubItems = Items( pyParent = self, pyMenu = None ) # 子菜单项版面
		if hasattr( item, "arrow" ) :									# 如果有子菜单箭头
			self.pyArrow_ = PyGUI( item.arrow )
			self.pyArrow_.h_dockStyle = "RIGHT"
			self.pyArrow_.visible = False
		if hasattr( item, "checkBox" ) :								# 如果有 check 按钮
			self.pyCheckBox_ = CheckBox( item.checkBox )
			self.pyCheckBox_.focus = False
			self.pyCheckBox_.h_dockStyle = "RIGHT"
			self.pyCheckBox_.checked = False
			self.pyCheckBox_.onCheckChanged.bind( self.onCheckChanged_ )
			self.__clickClose = False									# 如果菜单项是可选中菜单项，点击菜单项不会关闭整个菜单

		self.foreColors_ = {}											# 各种状态下的前景色
		self.foreColors_[UIState.COMMON] = 255, 255, 255, 255
		self.foreColors_[UIState.HIGHLIGHT] = 255, 255, 255, 255
		self.foreColors_[UIState.DISABLE] = 128, 128, 128, 255
		self.backColors_ = {}											# 各种状态下的背景色
		self.backColors_[UIState.COMMON] = 255, 255, 255, 0
		self.backColors_[UIState.HIGHLIGHT] = 10, 36, 106, 255
		self.backColors_[UIState.DISABLE] = 255, 255, 255, 0


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __setSubItemsPosition( self ) :
		"""
		设置子菜单项的位置
		"""
		pySubItems = self.__pySubItems
		if pySubItems is None : return
		pySelfItems = self.pySelfItems								# 所在菜单版面
		if pySelfItems is None : return
		right = pySelfItems.right + pySubItems.width
		if right <= BigWorld.screenWidth() :						# 如果从右边列出不会超出屏幕最大宽度
			pySubItems.left = pySelfItems.right - 2					# 则从右边列出
		else :														# 否则
			pySubItems.right = pySelfItems.left + 2					# 从左边列出

		top = self.topToScreen - pySubItems.topEdgeHeight
		if top + pySubItems.height <= BigWorld.screenHeight() :		# 如果向下列出不会超出屏幕的最大高度
			pySubItems.top = top									# 则向下列出
		else :														# 否则向上列出
			pySubItems.bottom = self.bottomToScreen + pySubItems.bottomEdgeHeight

	def __getCheckBoxWidth( self ) :
		"""
		获取 CheckBox 的宽度
		"""
		if self.pyCheckBox_ :
			return self.pyCheckBox_.width
		return 0

	def __getArrowWidth( self ) :
		"""
		获取子菜单项箭头的大小
		"""
		if self.pyArrow_ and self.pySubItems.count :
			return self.pyArrow_.width
		return 0


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMouseEnter_( self ) :
		"""
		鼠标进入时被调用
		"""
		Control.onMouseEnter_( self )
		self.setState( UIState.HIGHLIGHT )
		self.popup()

	def onMouseLeave_( self ) :
		"""
		鼠标离开时被调用
		"""
		Control.onMouseLeave_( self )
		if not self.isPopUp :
			self.setState( UIState.COMMON )
		else :
			px, py = csol.pcursorPosition()
			if self.__pySubItems.left + 2 >= self.rightToScreen : 		# 子菜单显示在右边
				if px < self.rightToScreen :							# 鼠标并非滑向子菜单
					self.close()										# 则隐藏子菜单
			elif self.__pySubItems.right - 2 <= self.leftToScreen :		# 子菜单显示在左边
				if px > self.leftToScreen :								# 鼠标并非滑向子菜单
					self.close()										# 则隐藏子菜单

	# ---------------------------------------
	def onLClick_( self, mods ) :
		if self.checkable and self.clickCheck :
			self.checked = not self.checked
		Control.onLClick_( self, mods )
		if self.pyMenu is not None :
			self.pyMenu.onItemClick__( self )
			if self.pySubItems.count == 0 :
				self.setState( UIState.COMMON )

	def onCheckChanged_( self, checked ) :
		if self.pyMenu is not None :
			self.pyMenu.onItemCheckChanged__( self )

	# ---------------------------------------
	def onEnable_( self ) :
		"""
		从无效变为有效状态时被调用
		"""
		Control.onEnable_( self )
		if self.__style != MIStyle.SPLITTER :		# 分隔条样式不响应 enable 属性的更改
			self.setState( UIState.COMMON )
		if self.pyArrow_ :
			self.pyArrow_.materialFX = "BLEND"

	def onDisable_( self ) :
		"""
		变为无效状态时被调用
		"""
		Control.onDisable_( self )
		if self.__style != MIStyle.SPLITTER :		# 分隔条样式不响应 enable 属性的更改
			self.setState( UIState.DISABLE )
			if self.isPopUp :						# 如果子菜单处于弹出状态
				self.pySubItems.hide()				# 则收起子菜单
		if self.pyArrow_ :
			self.pyArrow_.materialFX = "COLOUR_EFF"


	# ----------------------------------------------------------------
	# firend mehods
	# ----------------------------------------------------------------
	def setMenu__( self, pyMenu ) :
		"""
		设置所属菜单
		"""
		if pyMenu is None :
			self.__pyMenu = None
		else :
			self.__pyMenu = weakref.ref( pyMenu )
		if self.__pySubItems is not None :
			self.__pySubItems.setMenu__( pyMenu )

	def setSelfItems__( self, pyItems ) :
		"""
		设置所属的父菜单项
		"""
		if pyItems is None :
			self.__pySelfItems = None
		else :
			self.__pySelfItems = weakref.ref( pyItems )
		if self.pySubItems :
			self.pySubItems.hide()

	# -------------------------------------------------
	def onItemAdded__( self, pyItem ) :
		"""
		当添加了一个子菜单项后，该函数被调用
		"""
		if self.pyArrow_ is not None :
			self.pyArrow_.visible = True

	def onItemRemoved__( self, pyItem ) :
		"""
		当某个子菜单项被删除时，该函数被调用
		"""
		if self.pySubItems.count == 0 :
			if self.pyArrow_ is not None :
				self.pyArrow_.visible = False
			self.close()

	def onItemRemoveds__( self, pyItem ) :
		"""
		当某个子菜单项清空选项时被调用
		"""
		if self.pyArrow_ is not None :
			self.pyArrow_.visible = False
		self.close()

	# ---------------------------------------
	def isMouseHitSubMenu__( self ) :
		"""
		判断鼠标是否落在 item 或子 item 上
		"""
		if self.isMouseHit() :
			return True
		if self.__pySubItems is None :
			return False
		return self.__pySubItems.isMouseHitSubMenu_()

	def rewidth__( self, width ) :
		"""
		重新设置菜单项的宽度
		"""
		Control._setWidth( self, width )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setState( self, state ) :
		"""
		设置状态的外观
		@type			state : MACRO DEFINATION
		@param			state : UIState.COMMON / UIState.HIGHLIGHT / UIState.DISABLE
		"""
		if self.__style == MIStyle.SPLITTER :
			return
		self.color = self.backColors_[state]
		if self.pyText_ is not None :
			self.pyText_.color = self.foreColors_[state]
		self.state_ = state

	# -------------------------------------------------
	def resetMemuPanel( self, panel ) :
		"""
		重新设置子菜单项版面样式
		@type				panel : engine ui
		@param				panel : 子菜单项版面 ui
		"""
		self.__pySubItems.subclass( panel, self, self.pyMenu )

	def getRealWidth( self ) :
		"""
		获取菜单项的真实宽度
		"""
		if self.pyText_ is None : return 0
		stuffWidth = 0														# checkBox 的宽度，或箭头的宽度（取最大者）
		if self.pySelfItems is not None :
			for pyItem in self.pySelfItems :
				stuffWidth = max( stuffWidth, pyItem.__getCheckBoxWidth() )
				stuffWidth = max( stuffWidth, pyItem.__getArrowWidth() )
		else :
			stuffWidth = max( stuffWidth, self.__getCheckBoxWidth() )
			stuffWidth = max( stuffWidth, self.__getArrowWidth() )
		return self.pyText_.right + self.pyText_.left + stuffWidth

	# -------------------------------------------------
	def popup( self ) :
		"""
		弹出子菜单
		"""
		pyItem = self.pySelfItems.getPopUpItem__()
		if pyItem is not None :
			pyItem.close()													# 收起同级菜单项的子菜单
		if self.pySubItems and self.pySubItems.count :
			self.__setSubItemsPosition()
			self.pySubItems.show()

	def close( self ) :
		"""
		收起子菜单
		"""
		if self.isPopUp :
			self.pySubItems.hide()
		self.setState( UIState.COMMON )

	def reset( self ) :
		"""
		恢复原始状态
		"""
		if self.state_ != UIState.DISABLE :
			self.setState( UIState.COMMON )
		if self.state_ == UIState.HIGHLIGHT :
			pySubItems = self.pySubItems
			if pySubItems :
				pySubItems.reset()


	# ----------------------------------------------------------------
	# property mehtods
	# ----------------------------------------------------------------
	def _getMenu( self ) :
		if self.__pyMenu is None :
			return None
		return self.__pyMenu()

	def _getSelfItems( self ) :
		if self.__pySelfItems is None :
			return None
		return self.__pySelfItems()

	# ---------------------------------------
	def _getSubItems( self ) :
		return self.__pySubItems

	def _getVisibleSubItems( self ) :
		return [pyItem for pyItem in self.__pySubItems if pyItem.visible]

	# -------------------------------------------------
	def _getText( self ) :
		if self.pyText_ is None :
			return ""
		return self.pyText_.text

	def _setText( self, text ) :
		if self.pyText_ is None :
			return
		self.pyText_.text = text
		self.width = self.getRealWidth()

	def _getFont( self ) :
		if self.pyText_ is None :
			return ""
		return self.pyText_.font

	def _setFont( self, font ) :
		if self.pyText_ is None :
			return
		self.pyText_.font = font
		self.width = self.getRealWidth()

	# ---------------------------------------
	def _getCharSpace( self ) :
		if self.pyText_ is None :
			return 0
		return self.pyText_.charSpace

	def _setCharSpace( self, space ) :
		if self.pyText_ is None :
			return
		self.pyText_._setCharSpace( space )

	def _getLimning( self ) :
		if self.pyText_ is None :
			return Font.LIMN_NONE
		return self.pyText_.limning

	def _setLimning( self, style ) :
		if self.pyText_ is None :
			return
		self.pyText_.limning = style

	def _getLimnColor( self ) :
		if self.pyText_ is None :
			return Font.defLimnColor
		return self.pyText_.limnColor

	def _setLimnColor( self, color ) :
		if self.pyText_ is None :
			return
		self.pyText_._setLimnColor( color )

	# -------------------------------------------------
	def _getCheckable( self ) :
		return self.pyCheckBox_ is not None

	def _getChecked( self ) :
		assert self.pyCheckBox_, "it is not a checkable item!"
		return self.pyCheckBox_.checked

	def _setChecked( self, checked ) :
		assert self.pyCheckBox_, "it is not a checkable item!"
		if self.pyCheckBox_ is None : return
		self.pyCheckBox_.checked = checked

	# ---------------------------------------
	def _getClickCheck( self ) :
		if self.pyCheckBox_ :
			return self.pyCheckBox_.clickCheck
		return False

	def _setClickCheck( self, clickCheck ) :
		if self.pyCheckBox_ :
			self.pyCheckBox_.clickCheck = clickCheck

	# ---------------------------------------
	def _getClickClose( self ) :
		if self.pySubItems.count :
			return False
		return self.__clickClose

	def _setClickClose( self, clickClose ) :
		self.__clickClose = clickClose

	# ---------------------------------------
	def _getIsPopUp( self ) :
		if self.__pySubItems is None :
			return False
		return self.__pySubItems.rvisible

	# -------------------------------------------------
	def _getCommonForeColor( self ) :
		return self.foreColors_[UIState.COMMON]

	def _setCommonForeColor( self, color ) :
		self.foreColors_[UIState.COMMON] = color
		self.pyText_.color = color

	def _getHighlightForeColor( self ) :
		return self.foreColors_[UIState.HIGHLIGHT]

	def _setHighlightForeColor( self, color ) :
		self.foreColors_[UIState.HIGHLIGHT] = color

	def _getDisableForeColor( self ) :
		return self.foreColors_[UIState.DISABLE]

	def _setDisableForeColor( self, color ) :
		self.foreColors_[UIState.DISABLE] = color

	# -------------------------------------------------
	def _getCommonBackColor( self ) :
		return self.backColors_[UIState.COMMON]

	def _setCommonBackColor( self, color ) :
		self.backColors_[UIState.COMMON] = color

	def _getHighlightBackColor( self ) :
		return self.backColors_[UIState.HIGHLIGHT]

	def _setHighlightBackColor( self, color ) :
		self.backColors_[UIState.HIGHLIGHT] = color

	def _getDisableBackColor( self ) :
		return self.backColors_[UIState.DISABLE]

	def _setDisableBackColor( self, color ) :
		self.backColors_[UIState.DISABLE] = color

	# -------------------------------------------------
	def _setVisible( self, visible ) :
		Control._setVisible( self, visible )
		if self.pySelfItems :
			self.pySelfItems.onItemToogleVisible__( self )			# 通知所属菜单列表，重新排列菜单项
		if not visible :											# 如果置为不可见
			self.setState( UIState.COMMON )
			if self.__pySubItems :
				self.__pySubItems.hide()							# 则隐藏所有子菜单

	# -------------------------------------------------
	def _setWidth( self, width ) :
		Control._setWidth( self, width )
		if self.pySelfItems is not None :
			self.pySelfItems.onItemRewidth__( self )				# 通知选项列表重新设置所有选项的宽度


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyMenu = property( _getMenu )														# 获取所属菜单
	pySelfItems = property( _getSelfItems )												# 获取所属的父菜单项
	pySubItems = property( _getSubItems )												# 获取子菜单项版面
	pyVSSubItems = property( _getVisibleSubItems )										# 获取所有可见菜单项
	itemStyle = property( lambda self : self.__style )									# 菜单项样式
	text = property( _getText, _setText )												# 获取/设置菜单文本
	font = property( _getFont, _setFont )												# 获取/设置字体
	charSpace = property( _getCharSpace, _setCharSpace )								# 获取/设置字间距
	limning = property( _getLimning, _setLimning )										# 获取/设置描边样式
	limnColor = property( _getLimnColor, _setLimnColor )								# 获取/设置描边颜色

	checkable = property( _getCheckable )												# 获得该菜单项是否可被选中
	checked = property( _getChecked, _setChecked )										# 获取/设置菜单的选中状态
	clickCheck = property( _getClickCheck, _setClickCheck )								# 获取/设置点击时，是否选中
	clickClose = property( _getClickClose, _setClickClose )								# 获取/设置菜单项被鼠标点击后，是否关闭整个菜单
	isPopUp = property( _getIsPopUp )													# 获得子菜单项是否处于弹出状态

	commonForeColor = property( _getCommonForeColor, _setCommonForeColor )				# 获取/设置普通状态下的前景色
	highlightForeColor = property( _getHighlightForeColor, _setHighlightForeColor)		# 获取/设置高亮状态下的前景色
	disableForeColor = property( _getDisableForeColor, _setDisableForeColor )			# 获取/设置无效状态下的前景色

	commonBackColor = property( _getCommonBackColor, _setCommonBackColor )				# 获取/设置普通状态下的背景色
	highlightBackColor = property( _getHighlightBackColor, _setHighlightBackColor ) 	# 获取/设置高亮状态下的背景色
	disableBackColor = property( _getDisableBackColor, _setDisableBackColor )			# 获取/设置无效状态下的背景色

	visible = property( Control._getVisible, _setVisible )								# 获取/设置菜单项的可见性

	width = property( Control._getWidth, _setWidth )									# 获取/设置菜单项的宽度


# --------------------------------------------------------------------
# implement default menuitem class
# --------------------------------------------------------------------
class DefMenuItem( MenuItem ) :
	"""
	默认样式的菜单项
	"""
	def __init__( self, text = "", style = MIStyle.COMMON ) :
		MenuItem.__init__( self, style )
		self.text = text
