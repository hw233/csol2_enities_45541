# -*- coding: gb18030 -*-
#
# $Id: FullText.py,v 1.3 2008-06-27 08:17:54 huangyongwei Exp $

"""
common global functions.
"""

import weakref
from AbstractTemplates import Singleton
from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.FlexExWindow import HVFlexExWindow
from guis.controls.StaticText import StaticText

class FullText( Singleton, HVFlexExWindow ) :
	def __init__( self ) :
		wnd = GUI.load( "guis/controls/scrollpanel/nosbar_3/panel.gui" )
		uiFixer.firstLoadFix( wnd )
		HVFlexExWindow.__init__( self, wnd )
		wnd.elements["frm_bg"].colour.alpha = 240
		self.activable_ = False
		self.escHide_ = False
		self.hitable_ = False
		self.movable_ = False
		self.visible = False
		self.focus = False
		self.addToMgr()

		self.__pyBinder = None
		self.__delayShowCBID = 0						# 延时一会显示
		self.__delayHideCBID = 0						# 延时一会隐藏
		self.__vsDetectCBID = 0							# 是否需要显示侦测

		self.edgeLeft_ = wnd.elements["frm_l"].size.x	# 左边宽度
		self.edgeTop_ = wnd.elements["frm_t"].size.y	# 顶部高度

	def __del__( self ) :
		HVFlexExWindow.__del__( self )
		if Debug.output_del_FullText :
			INFO_MSG( str( self ) )

	def dispose( self ) :
		HVFlexExWindow.dispose( self )
		self.__class__.releaseInst()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __visibleDetect( self ) :
		"""
		循环侦测鼠标是否在加长显示对象上，如果不在，则隐藏
		"""
		pyBinder = self.pyBinder
		if pyBinder and pyBinder.rvisible :
			self.__vsDetectCBID = BigWorld.callback( 1.0, self.__visibleDetect )
		else :
			self.hide()

	def __locate( self ) :
		"""
		设置提示条的位置
		"""
		cursorPos = rds.ccursor.pos
		self.left = cursorPos[0]
		self.bottom = cursorPos[1]
		scw, sch = BigWorld.screenSize()
		if self.right > scw :
			self.right = scw
		if self.top < 0 :
			self.top = rds.ccursor.dpos[1]

	def __delayShow( self, pyOwner, pyUI ) :
		"""
		延迟显示
		"""
		BigWorld.cancelCallback( self.__vsDetectCBID )
		if not pyOwner.isMouseHit() : return
		self.onFullDuplicate_( pyUI )
		LastKeyDownEvent.attach( self.__onLastKeyDown )
		HVFlexExWindow.show( self, pyOwner )
		self.__locate()
		self.__vsDetectCBID = BigWorld.callback( 1.0, self.__visibleDetect )

	# -------------------------------------------------
	def __onLastKeyDown( self, key, mods ) :
		if key == KEY_LEFTMOUSE or \
			key == KEY_RIGHTMOUSE :
				self.hide()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onFullDuplicate_( self, pyUI ) :
		"""
		复制要完全显示的 UI 副本
		"""
		gui = self.gui
		dup = util.copyGuiTree( pyUI.gui )
		gui.addChild( dup, "dup" )
		self.__pyDup = PyGUI( dup )
		self.__pyDup.pos = self.edgeLeft_, self.edgeTop_/2
		self.width = self.__pyDup.width + self.edgeLeft_ * 2
		self.height = self.__pyDup.height + self.edgeTop_ * 2

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@classmethod
	def show( SELF, pyOwner, pyUI, delayShow = True ) :
		"""
		浮动显示完整文本
		@type			pyOwner	  : python ui
		@param			pyOwner	  : 文本背景 ui
		@type			pyUI	  : GUIBaseObject
		@param			pyUI	  : 要加长显示的 UI
		@type			delayShow : bool
		@param			delayShow : 是否延时一会再显示
		@return					  : None
		"""
		pyFullText = SELF()
		pyFullText.__pyBinder = weakref.ref( pyOwner )
		BigWorld.cancelCallback( pyFullText.__delayShowCBID )
		BigWorld.cancelCallback( pyFullText.__delayHideCBID )
		if delayShow :
			BigWorld.callback( 0.3, Functor( pyFullText.__delayShow, pyOwner, pyUI ) )
		else :
			pyFullText.__delayShow( pyOwner, pyUI )

	@classmethod
	def hide( SELF ) :
		"""
		隐藏浮动文本
		"""
		if not SELF.insted : return
		pyFullText = SELF.inst
		HVFlexExWindow.hide( pyFullText )
		pyFullText.__pyBinder = None
		BigWorld.cancelCallback( pyFullText.__delayShowCBID )
		BigWorld.cancelCallback( pyFullText.__delayHideCBID )
		BigWorld.cancelCallback( pyFullText.__vsDetectCBID )
		LastKeyDownEvent.detach( pyFullText.__onLastKeyDown )
		pyFullText.__delayHideCBID = BigWorld.callback( 1.0, pyFullText.dispose )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getBinder( self ) :
		if self.__pyBinder is None :
			return None
		return self.__pyBinder()


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyBinder = property( _getBinder )
