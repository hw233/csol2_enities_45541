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
	_FONT_SIZE = 12		#���������С
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
		self.__pyCaps = PushButton( wnd.key_caps )					# caps lock ��
		self.__pyCaps.setStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyCaps,"LoginDialog:keyBoard", "upperSwitch" )
		self.__pyCaps.fontSize = self._FONT_SIZE
		self.__pyCaps.charSpace = -2
		self.__pyCaps.onKeyDown_ = self.__onKeyKeyDown				# ע������ֱ���滻�����ı����������������ԣ�����Ϊ�˷ǳ�Ŀ�Ķ��������ǿ�����߲�Ҫ��������
		self.__pyCaps.onPushed.bind( self.__onPushChanged )
		self.__pyCaps.onRaised.bind( self.__onPushChanged )

		self.__pyKeys = {}											# ���зǸ��Ӽ�

		pyBack = Button( wnd.key_back )								# backspace ��
		pyBack.fontSize = self._FONT_SIZE
		pyBack.isLetterKey = False
		self.__pyKeys[KEY_BACKSPACE] = pyBack
		self.__initChars( wnd )										# ��ʼ�������ַ���

		for key, pyKey in self.__pyKeys.iteritems() :
			pyKey.mapKey = key
			pyKey.setStatesMapping( UIState.MODE_R2C2 )
			pyKey.onLMouseDown.bind( self.__onKeyMouseDown )
			pyKey.onLMouseUp.bind( self.__onKeyMouseUp )
			pyKey.onKeyDown_ = self.__onKeyKeyDown					# ��������Ŀ���ǽػ񰴼�����Ϣ���ۺϵ����ص� __onKeyKeyDown ��ִ��(�򽹵� UI ������)

	def __initChars( self, wnd ) :
		"""
		��ʼ�������ַ���
		"""
		getKeyValue = lambda skey : getattr( keys, "KEY_%s" % skey.upper() )
		nuKeys = {}
		for i in xrange( 10 ) :										# ���ּ�
			keyValue = getKeyValue( str( i ) )
			nuKeys[keyValue] = ( str( i ), False )					# ( ����Ӧ���ַ�, shift �Ƿ���Ч )

		chKeys = {}
		for i in xrange( ord( 'a' ), ord( 'z') + 1 ) :				# ��ĸ��
			keyValue = getKeyValue( chr( i ) )
			chKeys[keyValue] = ( chr( i ), True )

		chKeys[KEY_MINUS] = ( '_', False )							# ���ż�
		chKeys[KEY_PERIOD] = ( '.', False )							# ��ż�

		for n, child in wnd.children :
			if "nu_" in n :
				key = random.choice( nuKeys.keys() )				# ���ѡ��һ�����ּ�
				keyInfo = nuKeys.pop( key )
			elif "ch_" in n :
				key = random.choice( chKeys.keys() )				# ���ѡ��һ����ĸ��
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
		���ݰ�����ȡ��ֵ
		"""
		key = pyKey.mapKey
		if pyKey.isLetterKey and ( self.__pyCaps.pushed ) :
			return key, MODIFIER_SHIFT
		return key, 0

	def __testCapslock( self ) :
		"""
		���� capslock ״̬���ü���
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
		��Сдģʽ���
		"""
		csol.setKeyState( "CAPSLOCK", self.__pyCaps.pushed )
		self.__testCapslock()

	# ---------------------------------------
	def __onKeyMouseDown( self, pyKey ) :
		"""
		�������ĳ�����ϰ���ʱ������
		"""
		key, mods = self.__getKeyValue( pyKey )
		love3.handleKeyEvent( True, key, mods )

	def __onKeyMouseUp( self, pyKey ) :
		"""
		����갴����ĳ����������ʱ������
		"""
		key, mods = self.__getKeyValue( pyKey )
		love3.handleKeyEvent( False, key, mods )

	# ---------------------------------------
	def __onKeyKeyDown( self, key, mods ) :
		"""
		��������갴����Ϣ�������
		"""
		pyTabInUI = uiHandlerMgr.getTabInUI()
		if pyTabInUI is None : return False
		pyActRoot = rds.ruisMgr.getActRoot()
		if pyActRoot and pyActRoot.onKeyDown_( key, mods ) :	# ע��������ñ����������������ԣ�����Ϊ�˷ǳ�Ŀ�Ķ��������ǿ�����߲�Ҫ��������
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
		self.movable_ = self.mousePos[1] <= 18			# ֻ������������̱�ͷ�������϶�����
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
