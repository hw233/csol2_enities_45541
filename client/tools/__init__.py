# -*- coding: gb18030 -*-
#
# $Id: __init__.py,v 1.4 2008-08-30 09:12:53 huangyongwei Exp $
#
"""
implement cameras, it moved from love3.py
2008/07/29: created by huangyongwei
"""

# --------------------------------------------------------------------
# 注意：添加到管理器中的工具必须实现 ITool 接口
#
# --------------------------------------------------------------------

import csol
import love3
from guis import *
from ITool import ITool
from guis.controls.ContextMenu import ContextMenu
from guis.controls.ContextMenu import DefMenuItem
from config.client.msgboxtexts import Datas as mbmsgs

# --------------------------------------------------------------------
# implement tool manager
# --------------------------------------------------------------------
class ToolMgr :
	__inst = None

	def __init__( self ) :
		self.__pyTools = {}						# 保存所有注册的工具
		self.__pyToolsMenu = None				# 列出所有工具的菜单
		self.__pyCurrTool = None				# 当前正在使用的工具

		self.__isShowAllHitUIs = False			# 临时变量，显示所有鼠标击中的 UI
		self.__pyMouseHitUI = None
		self.__mousePos = ( 0, 0 )

	@classmethod
	def instance( SELF ) :
		if SELF.__inst is None :
			SELF.__inst = ToolMgr()
		return SELF.__inst


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def __isMouseHit( self ) :
		"""
		鼠标是否击中任何一个工具
		"""
		for pyTool in self.__pyTools.itervalues() :
			if not pyTool.visible : continue
			if pyTool.isMouseHit() :
				return True
		return False

	def __showTool( self, pyUI ) :
		"""
		显示指定工具
		"""
		if self.__pyCurrTool.visible : return
		if pyUI is None :
			# "找不到合适的控件"
			showAutoHideMessage( 3.0, 0x0e41, "" )
			return
		for pyTool in self.__pyTools.itervalues() :
			if pyTool.visible :
				# "请首先关闭 %s"
				showAutoHideMessage( 3.0, mbmsgs[0x0e42] % pyTool.getCHName(), "" )
				return
		self.__pyCurrTool.show( pyUI )

	# -------------------------------------------------
	def __listTools( self ) :
		"""
		在菜单中列出所有工具
		"""
		if self.__pyToolsMenu :
			self.__pyToolsMenu.popup()
			return
		self.__pyToolsMenu = ContextMenu()
		self.__pyToolsMenu.onItemClick.bind( self.__onToolMenuItemClick )
		for name in self.__pyTools :
			pyItem = DefMenuItem( name )
			self.__pyToolsMenu.pyItems.add( pyItem )
		self.__pyToolsMenu.popup()

	def __listHitUIs( self, pyUIs ) :
		"""
		列出所有鼠标击中的 UI
		"""
		self.__pyUIsMenu = ContextMenu()
		self.__pyUIsMenu.onItemClick.bind( self.__onUIMenuItemClick )
		for name, pyUI in pyUIs :
			pyItem = DefMenuItem( name )
			pyItem.pyMapUI = pyUI
			self.__pyUIsMenu.pyItems.add( pyItem )
		self.__pyUIsMenu.popup()

	# -------------------------------------------------
	def __onToolMenuItemClick( self, pyItem ) :
		"""
		选择某个工具时被调用
		"""
		self.__pyCurrTool = self.__pyTools[pyItem.text]
		if pyItem.text == "剧情编辑器" :
			self.__pyCurrTool.show( None )
			return
		if self.__isShowAllHitUIs :								# 列出鼠标击中的 UI 让用户选择
			pyUIs = self.__pyCurrTool.getHitUIs( self.__pyMouseHitUI, self.__mousePos )
			if len( pyUIs ) :
				self.__listHitUIs( pyUIs )
		else :													# 直接选择指定的 UI（由工具自己提供）
			pyUI = self.__pyCurrTool.getHitUI( self.__pyMouseHitUI, self.__mousePos )
			self.__showTool( pyUI )

	def __onUIMenuItemClick( self, pyItem ) :
		"""
		选择列出选中的某个 UI
		"""
		self.__showTool( pyItem.pyMapUI )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addTool( self, pyTool ) :
		"""
		添加一个工具到管理器
		"""
		assert isinstance( pyTool, ITool ), "tool added to manager must be implemented ITool"
		self.__pyTools[pyTool.getCHName()] = pyTool

	# -------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		if down and key in [KEY_MOUSE0, KEY_MOUSE1] and \
			mods == MODIFIER_SHIFT | MODIFIER_CTRL | MODIFIER_ALT :
				if self.__isMouseHit() : return True							# 鼠标击中其中一个工具
				self.__pyMouseHitUI = ruisMgr.getMouseHitRoot()					# 纪录下要被工具操作的窗口
				self.__mousePos = csol.pcursorPosition()
				if self.__pyMouseHitUI is None : return True
				self.__listTools()
				self.__isShowAllHitUIs = ( key == KEY_MOUSE1 )
				return True
		elif down and key in [KEY_P] and \
			mods == MODIFIER_SHIFT | MODIFIER_CTRL | MODIFIER_ALT :				# 剧情编辑器快捷键
				self.__pyCurrTool = self.__pyTools["剧情编辑器"]
				self.__pyCurrTool.show( None )
		elif self.__pyCurrTool and self.__pyCurrTool.rvisible :
			if self.__pyCurrTool.preKeyEvent( down, key, mods ) :
				return True
		return False


# --------------------------------------------------------------------
# global instnace
# --------------------------------------------------------------------
toolMgr = ToolMgr.instance()

# --------------------------------------------------------------------
# change global event function
# --------------------------------------------------------------------
l3_handleKeyEvent = love3.handleKeyEvent
def handleKeyEvent( down, key, mods ):
	if toolMgr.handleKeyEvent( down, key, mods ) :
		return True
	return l3_handleKeyEvent( down, key, mods )

love3.handleKeyEvent = handleKeyEvent
