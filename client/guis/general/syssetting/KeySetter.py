# -*- coding: gb18030 -*-
#
# $Id: TabCtrl.py,v 1.18 2008-08-01 09:47:33 huangyongwei Exp $

"""
implement key setting item

2008.12.12: writen by huangyongwei
"""

from guis import *
from guis.controls.ListItem import ListItem
from guis.controls.StaticText import StaticText
from config.client.msgboxtexts import Datas as mbmsgs
from LabelGather import labelGather
from MessageBox import *
import event.EventCenter as ECenter

class KeySetter( ListItem ) :
	__cg_setter = None
	__cg_flashCBID = 0
	
	__keys_map = {"MINUS":"-","EQUALS":"=","BACKSLASH":"\\"}

	def __init__( self, scInfo, pyBinder = None ) :
		if KeySetter.__cg_setter is None :
			KeySetter.__cg_setter = GUI.load( "guis/general/syssetting/keysetter.gui" )

		setter = util.copyGuiTree( KeySetter.__cg_setter )
		uiFixer.firstLoadFix( setter )
		ListItem.__init__( self, setter, pyBinder )
		self.__bar = setter.bar
		self.__flasher = setter.bar.flasher
		self.__flasher.speed = 0.3

		self.__pyTitle = StaticText( setter.stTitle )					# 快捷键标题
		self.__pyTitle.color = 252.0, 235.0, 179.0
		self.__pyTitle.text = scInfo.comment

		self.__pyKeyName = StaticText( setter.bar.stKeyName )			# 快捷键键名

		self.__barMappings = {}
		self.__barMappings[UIState.COMMON] = util.getStateMapping( self.__bar.size, UIState.MODE_R3C1, UIState.ST_R1C1 )
		self.__barMappings[UIState.HIGHLIGHT] = util.getStateMapping( self.__bar.size, UIState.MODE_R3C1, UIState.ST_R2C1 )
		self.__barMappings[UIState.SELECTED] = util.getStateMapping( self.__bar.size, UIState.MODE_R3C1, UIState.ST_R3C1 )

		self.__scInfo = scInfo
		scInfo.setShortcutChangeCallback( self.__onShortcutChanged )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __flash( self ) :
		"""
		闪烁激活的快捷键设置条
		"""
		value = self.__flasher.value
		if value > 0.99 :
			self.__flasher.value = 0.5
		elif value < 0.51 :
			self.__flasher.value = 1.0
		BigWorld.cancelCallback( KeySetter.__cg_flashCBID )
		KeySetter.__cg_flashCBID = BigWorld.callback( 0.6, self.__flash )

	def __unflash( self ) :
		"""
		停止闪烁
		"""
		BigWorld.cancelCallback( KeySetter.__cg_flashCBID )
		self.__flasher.value = 1.0
		self.__flasher.reset()

	# -------------------------------------------------
	def __onShortcutChanged( self, scInfo ) :
		"""
		快捷键改变时被调用
		"""
		scString = scInfo.shortcutString
		if scString == "" : scString = labelGather.getText( "gamesetting:keySetter", "keyDefText" )
		if scString in self.__keys_map:
			scString = self.__keys_map[scString]
		self.__pyKeyName.text = scString


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onKeyDown_( self, key, mods ) :
		"""
		键盘按键按下时被调用
		"""
		if key == KEY_TAB and mods == MODIFIER_ALT :					# 切换窗口（将窗口变为非激活状态后，需要恢复原来的设置）
			rds.shortcutMgr.cancel( self.__scInfo.tag )
			return

		def clearVerify( result ) :										# 清除按键提示
			if result != RS_YES : return
			rds.shortcutMgr.setShortcut( self.__scInfo.tag, 0, 0 )
			self.pyBinder.onKeyChanged( True )
			ECenter.fireEvent( "EVT_ON_SHORTCUT_CHANGED", True )

		def dupVerify( dupSCInfo, result ) :							# 按键重复提示
			if result != RS_YES : return
			rds.shortcutMgr.setShortcut( dupSCInfo.tag, 0, 0 )
			rds.shortcutMgr.setShortcut( self.__scInfo.tag, key, mods )
			self.pyBinder.onKeyChanged( True )
			ECenter.fireEvent( "EVT_ON_SHORTCUT_CHANGED", True )

		def getText( scInfo ):
			classifySCs = rds.shortcutMgr.getClassifyShortcuts()
			for tag, info in classifySCs.iteritems():
				if scInfo in info:
					return tag

		scInfo = rds.shortcutMgr.getShortcutViaKey( self.__scInfo.pri, key, mods )
		if scInfo :														# 指定的快捷键是否已经被设置
			if scInfo == self.__scInfo :								# 重复按了两下相同的快捷键
				# "当前已经设置为该按键，重复设置将会清除该设置，是否继续？"
				showAutoHideMessage( 8.0, 0x08a1, "", MB_YES_NO, clearVerify, self )
			else :
				# "按键重复，导致“%s-->%s”变为未设置。"
				text = getText( scInfo )
				msg = mbmsgs[0x08a2] % ( text, scInfo.comment )
				callback = Functor( dupVerify, scInfo )
				showAutoHideMessage( 8.0, msg, "", MB_YES_NO, callback, self )
		else :
			rds.shortcutMgr.setShortcut( self.__scInfo.tag, key, mods )
			self.pyBinder.onKeyChanged( True )
			ECenter.fireEvent( "EVT_ON_SHORTCUT_CHANGED", True )
		return True

	# -------------------------------------------------
	def onTabIn_( self ) :
		"""
		当获得焦点时被调用
		"""
		ListItem.onTabIn_( self )
		self.__flash()

	def onTabOut_( self ) :
		"""
		当焦点离开时被调用
		"""
		ListItem.onTabOut_( self )
		self.__unflash()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setState( self, state ) :
		"""
		改变状态
		"""
		ListItem.setState( self, state )
		if self.selected :
			self.__bar.mapping = self.__barMappings[UIState.SELECTED]
			self.__pyKeyName.color = 255.0, 234.0, 0.0
		else :
			self.__bar.mapping = self.__barMappings[state]
			self.__pyKeyName.color = 255.0, 255.0, 255.0

#		print "-------->>> Trace :", self.aaa

	# -------------------------------------------------
	def setToDefault( self ) :
		"""
		设置为默认快捷键
		"""
		rds.shortcutMgr.setToDefault( self.__scInfo.tag )
