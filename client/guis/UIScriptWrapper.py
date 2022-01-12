# -*- coding: gb18030 -*-
#
# $Id: UIScriptWrapper.py,v 1.1 2008-06-21 01:34:49 huangyongwei Exp $

"""
This module script wrapper for engine ui

2008/06/13: writen by huangyongwei
"""

import weakref
import GUI
import Debug
import util
from bwdebug import *


# --------------------------------------------------------------------
# implement wrapping function
# --------------------------------------------------------------------
def wrap( ui, pyUI ) :
	"""
	对引擎 UI 与 ptyhon UI 创建弱引用封装器
	@type				ui	 : engine UI
	@param				ui	 : 引擎 UI
	@type				pyUI : python UI / None
	@param				pyUI : python UI( 如果它为 None，则表示清除引擎 UI 的 script 引用 )
	@return					 : None
	"""
	GUIBaseObject = __import__( "guis/common/GUIBaseObject" ).GUIBaseObject
	if isDebuged : assert isinstance( ui, GUI.Simple ) == True, "ui must be an engine ui!"
	#assert isinstance( pyUI, GUIBaseObject ) == True, "pyUI must inherit from GUIBaseObject"
	if pyUI is None :
		ui.script = None
	else :
		ui.script = _ScriptWrapper( ui, pyUI )

def unwrap( ui ) :
	"""
	对引擎 UI 进行解包，获取引擎 UI 所对应的 python UI
	@type				ui : engine ui
	@param				ui : 引擎 UI
	@rtype				   : python UI
	@return				   : 返回引擎 UI 的 script 所对应的 python UI
	"""
	if ui.script is None : return None
	return getattr( ui.script, "pyUI", ui.script )			# 如果有包装器，则通过包装器返回，否则直接返回 script


# --------------------------------------------------------------------
# implement inner script wrapper class
# --------------------------------------------------------------------
class _ScriptWrapper( object ) :
	__slots__ = ( "_ScriptWrapper__weakUI", "_ScriptWrapper__pyWeakUI" )
	"""
	主要负责将 python UI 与 引擎 UI 建立引用关系
	而这种关系又不会产生交叉引用，以使得，当没有脚本引用 python UI 时，它能得到及时的释放
	"""
	def __init__( self, ui, pyUI ) :
		self.__weakUI = weakref.ref( ui, self.__onDie )				# 引用引擎 UI
		self.__pyWeakUI = weakref.ref( pyUI, self.__onPyDie )		# 引用 python UI


	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __del__( self ) :
		if Debug.output_del_ScriptWrapper :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def ui( self ) :
		"""
		获取对应的引擎 UI
		"""
		if self.__weakUI is None :
			return None
		return self.__weakUI()

	@property
	def pyUI( self ) :
		"""
		获取对应的 python UI
		"""
		if self.__pyWeakUI is None :
			return None
		return self.__pyWeakUI()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onDie( self, weaker ) :
		"""
		当对应的引擎 UI 销毁时被调用
		注意：一般情况下，当该方法被调用时，意味着该引擎 UI 所对应的 python ui 已经被释放掉
			  或者，它所对应的 python UI 已经改为引用别的引擎对象。
			  因为，python UI 对引擎 UI 有强引用关系，所以，python 没有释放，引擎 UI 也不会释放的
		"""
		del self.__weakUI									# 取消对引擎 UI 的引用
		del self.__pyWeakUI									# 取消对 pthon UI 的引用
															# 注意：这里不能删除 python UI 本身，因为引擎 UI 释放并不代表 python UI 已经释放
															# 有可能还有别的脚本还会 python UI 有引用

	def __onPyDie( self, weaker ) :
		"""
		当对应的 python UI 销毁时被调用
		注意：当 python UI 删除时，它所对应的引擎 UI 也要释放掉
			  而要释放引擎 UI，则需要清除所有有可能对引擎 UI 的引用
		"""
		ui = self.ui
		if ui is None : return
		ui.script = None									# 清除 ui 的 script 包装器
		ui.focus = False									# 从 focus 列表中删除
		ui.moveFocus = False								# 从 moveFocus 列表中删除
		ui.crossFocus = False								# 从 crollsFocus 列表中删除
		ui.dragFocus = False								# 从 dragFocus 列表中删除
		ui.dropFocus = False								# 从 dropFocus 列表中删除
		if ui.parent :										# 如果有父亲
			ui.parent.delChild( ui )						# 则，将 UI 从它的父亲中撤离
		elif ui in GUI.roots() :							# 如果 UI 还在 root 列表中
			GUI.delRoot( ui )								# 则从列表中清除
		for n, ch in ui.children :							# 同时
			ui.delChild( ch )								# 释放它所有的子 UI
		del self.__weakUI									# 取消对引擎 UI 的引用
		del self.__pyWeakUI									# 取消对 pthon UI 的引用


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		pyUI = self.pyUI
		if hasattr( pyUI, "handleKeyEvent" ) :
			return pyUI.handleKeyEvent( down, key, mods )
		return False

	def handleAxisEvent( self, axis, value, dTime ):
		pyUI = self.pyUI
		if hasattr( pyUI, "handleAxisEvent" ) :
			return pyUI.handleAxisEvent( axis, value, dTime )
		return False

	def handleMouseButtonEvent( self, comp, key, down, mods, pos ) :
		pyUI = self.pyUI
		if hasattr( pyUI, "handleMouseButtonEvent" ) :
			return pyUI.handleMouseButtonEvent( comp, key, down, mods, pos )
		return False

	def handleMouseClickEvent( self, comp, pos ) :
		pyUI = self.pyUI
		if hasattr( pyUI, "handleMouseClickEvent" ) :
			return pyUI.handleMouseClickEvent( comp, pos )
		return False

	def handleMouseEvent( self, comp, pos ) :
		pyUI = self.pyUI
		if hasattr( pyUI, "handleMouseEvent" ) :
			return pyUI.handleMouseEvent( comp, pos )
		return False

	def handleMouseEnterEvent( self, comp, pos ) :
		pyUI = self.pyUI
		if hasattr( pyUI, "handleMouseEnterEvent" ) :
			return pyUI.handleMouseEnterEvent( comp, pos )
		return False

	def handleMouseLeaveEvent( self, comp, pos ) :
		pyUI = self.pyUI
		if hasattr( pyUI, "handleMouseLeaveEvent" ) :
			return pyUI.handleMouseLeaveEvent( comp, pos )
		return False

	def handleDragStartEvent( self, comp, pos ) :
		pyUI = self.pyUI
		if hasattr( pyUI, "handleDragStartEvent" ) :
			return pyUI.handleDragStartEvent( comp, pos )
		return False

	def handleDragStopEvent( self, comp, pos ) :
		pyUI = self.pyUI
		if hasattr( pyUI, "handleDragStopEvent" ) :
			return pyUI.handleDragStopEvent( comp, pos )
		return False

	def handleDragEnterEvent( self, comp, pos, dragged ) :
		pyUI = self.pyUI
		if hasattr( pyUI, "handleDragEnterEvent" ) :
			return pyUI.handleDragEnterEvent( comp, pos, dragged )
		return False

	def handleDragLeaveEvent( self, comp, pos, dragged ) :
		pyUI = self.pyUI
		if hasattr( pyUI, "handleDragLeaveEvent" ) :
			return pyUI.handleDragLeaveEvent( comp, pos, dragged )
		return False

	def handleDropEvent( self, comp, pos, dropped ) :
		pyUI = self.pyUI
		if hasattr( pyUI, "handleDropEvent" ) :
			return pyUI.handleDropEvent( comp, pos, dropped )
		return False
