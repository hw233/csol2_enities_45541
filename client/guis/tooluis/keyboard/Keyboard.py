# -*- coding: gb18030 -*-
#
# $Id: Keyboard.py,v 1.10 2008-08-26 02:21:57 huangyongwei Exp $

"""
implement little keyboard

2008.03.18: writen by huangyongwei
"""

import random
import keys
import love3
from AbstractTemplates import Singleton
from guis import *
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.controls.PushButton import PushButton
from LabelGather import labelGather


class Keyboard( Singleton, Window ) :
	_FONT_SIZE = 12		#键盘字体大小
	def __init__( self ) :
		wnd = GUI.load( "guis/tooluis/keyboard/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.__initialize( wnd )
		self.posZSegment = ZSegs.L3
		self.escHide_ = True
		self.activable_ = False
		self.h_dockStyle = "CENTER"
		self.v_dockStyle = "S_MIDDLE"
		self.addToMgr( "virKeyboard" )

	def __del__( self ) :
		Window.__del__( self )
		if Debug.output_del_Keyboard :
			INFO_MSG( str( self ) )

	def dispose( self ) :
		Window.dispose( self )
		self.__class__.releaseInst()
		del self.__pyCaps.onKeyDown_
		del self.__pyKeys


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		self.__pyCaps = PushButton( wnd.key_caps )					# caps lock 键
		self.__pyCaps.setStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyCaps,"LoginDialog:keyBoard", "upperSwitch" )
		self.__pyCaps.fontSize = self._FONT_SIZE
		self.__pyCaps.charSpace = -2
		self.__pyCaps.onKeyDown_ = self.__onKeyKeyDown				# 注：这里直接替换掉它的保护方法的做法不对（这是为了非常目的而做，不是库设计者不要这样做）
		self.__pyCaps.onPushed.bind( self.__onPushChanged )
		self.__pyCaps.onRaised.bind( self.__onPushChanged )

		self.__pyKeys = {}											# 所有非附加键

		pyBack = Button( wnd.key_back )								# backspace 键
		pyBack.fontSize = self._FONT_SIZE
		pyBack.isLetterKey = False
		self.__pyKeys[KEY_BACKSPACE] = pyBack
		self.__initChars( wnd )										# 初始化所有字符键

		for key, pyKey in self.__pyKeys.iteritems() :
			pyKey.mapKey = key
			pyKey.setStatesMapping( UIState.MODE_R2C2 )
			pyKey.onLMouseDown.bind( self.__onKeyMouseDown )
			pyKey.onLMouseUp.bind( self.__onKeyMouseUp )
			pyKey.onKeyDown_ = self.__onKeyKeyDown					# 这样做的目的是截获按键的消息，综合到本地的 __onKeyKeyDown 上执行(向焦点 UI 中输入)

	def __initChars( self, wnd ) :
		"""
		初始化所有字符键
		"""
		getKeyValue = lambda skey : getattr( keys, "KEY_%s" % skey.upper() )
		nuKeys = {}
		for i in xrange( 10 ) :										# 数字键
			keyValue = getKeyValue( str( i ) )
			nuKeys[keyValue] = ( str( i ), False )					# ( 键对应的字符, shift 是否有效 )

		chKeys = {}
		for i in xrange( ord( 'a' ), ord( 'z') + 1 ) :				# 字母键
			keyValue = getKeyValue( chr( i ) )
			chKeys[keyValue] = ( chr( i ), True )

		chKeys[KEY_MINUS] = ( '_', False )							# 减号键
		chKeys[KEY_PERIOD] = ( '.', False )							# 句号键

		for n, child in wnd.children :
			if "nu_" in n :
				key = random.choice( nuKeys.keys() )				# 随机选择一个数字键
				keyInfo = nuKeys.pop( key )
			elif "ch_" in n :
				key = random.choice( chKeys.keys() )				# 随机选择一个字母键
				keyInfo = chKeys.pop( key )
			else :
				continue
			pyChar = Button( child )
			pyChar.fontSize = self._FONT_SIZE
			pyChar.isOffsetText = True
			pyChar.text = keyInfo[0]
			pyChar.mapKey = key
			pyChar.isLetterKey = keyInfo[1]
			self.__pyKeys[key] = pyChar


	# ---------------------------------------------------------------------
	# private
	# ---------------------------------------------------------------------
	def __getKeyValue( self, pyKey ) :
		"""
		根据按键获取键值
		"""
		key = pyKey.mapKey
		if pyKey.isLetterKey and ( self.__pyCaps.pushed ) :
			return key, MODIFIER_SHIFT
		return key, 0

	def __testCapslock( self ) :
		"""
		根据 capslock 状态设置键盘
		"""
		isUpper = self.__pyCaps.pushed
		for pyKey in self.__pyKeys.itervalues() :
			if not pyKey.isLetterKey : continue
			text = pyKey.text
			if isUpper : text = text.upper()
			else : text = text.lower()
			pyKey.text = text

	# -------------------------------------------------
	def __onPushChanged( self ) :
		"""
		大小写模式变更
		"""
		csol.setKeyState( "CAPSLOCK", self.__pyCaps.pushed )
		self.__testCapslock()

	# ---------------------------------------
	def __onKeyMouseDown( self, pyKey ) :
		"""
		当鼠标在某按键上按下时被触发
		"""
		key, mods = self.__getKeyValue( pyKey )
		love3.handleKeyEvent( True, key, mods )

	def __onKeyMouseUp( self, pyKey ) :
		"""
		当鼠标按键在某按键上提起时被调用
		"""
		key, mods = self.__getKeyValue( pyKey )
		love3.handleKeyEvent( False, key, mods )

	# ---------------------------------------
	def __onKeyKeyDown( self, key, mods ) :
		"""
		按键的鼠标按下消息替代函数
		"""
		pyTabInUI = uiHandlerMgr.getTabInUI()
		if pyTabInUI is None : return False
		pyActRoot = rds.ruisMgr.getActRoot()
		if pyActRoot and pyActRoot.onKeyDown_( key, mods ) :	# 注：这里调用保护方法的做法不对（这是为了非常目的而做，不是库设计者不要这样做）
			return True
		return pyTabInUI.onKeyDown_( key, mods )

	# -------------------------------------------------
	def __onLastKeyDown( self, key, mods ) :
		if key == KEY_CAPSLOCK :
			self.__pyCaps.pushed = csol.getKeyState( "CAPSLOCK" )
		return False


	# ---------------------------------------------------------------------
	# protected
	# ---------------------------------------------------------------------
	def onKeyDown_( self, key, mods ) :
		return False

	def onLMouseDown_( self, mods ) :
		self.movable_ = self.mousePos[1] <= 18			# 只有鼠标点击到键盘标头才允许拖动键盘
		return Window.onLMouseDown_( self, mods )


	# ---------------------------------------------------------------------
	# public
	# ---------------------------------------------------------------------
	def show( self, pyOwner = None ) :
		LastKeyDownEvent.attach( self.__onLastKeyDown )
		self.__pyCaps.pushed = csol.getKeyState( "CAPSLOCK" )
		Window.show( self, pyOwner )

	def hide( self ) :
		LastKeyDownEvent.detach( self.__onLastKeyDown )
		Window.hide( self )
		self.dispose()
