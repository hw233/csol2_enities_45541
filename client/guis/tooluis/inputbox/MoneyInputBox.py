# -*- coding: gb18030 -*-
#
# 输入创世币专用
# written by ganjinxing 2009-12-26

from guis import *
from bwdebug import *
from guis.common.Window import Window
from guis.common.GUIBaseObject import GUIBaseObject
from guis.controls.Control import Control
from guis.ExtraEvents import ControlEvent
from guis.controls.TabSwitcher import TabSwitcher
from guis.controls.StaticText import StaticText
from guis.controls.TextBox import TextBox
from guis.controls.ButtonEx import HButtonEx
from AbstractTemplates import Singleton
from LabelGather import labelGather

import weakref

class MoneyInputBox( Singleton, Window ) :

	def __init__( self ) :
		wnd = GUI.load( "guis/tooluis/inputbox/money_input_box.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )

		self.__pressedOk = False
		self.__callback = None

		self.__initialize( wnd )
		self.addToMgr()

	def __del__( self ) :
		Window.__del__( self )
		if Debug.output_del_MoneyInputBox :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		self.__moneyBox = MoneyBar( wnd.inputBoxs, self )
		self.__moneyBox.onTextChanged.bind( self.onTextChanged_ )

		self.__pyNotifyText = StaticText( wnd.notifyText )

		self.__pyCancelBtn = HButtonEx( wnd.cancelBtn )
		self.__pyCancelBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyCancelBtn.onLClick.bind( self.__onCancel )

		self.__pyOkBtn = HButtonEx( wnd.OKBtn )
		self.__pyOkBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyOkBtn.onLClick.bind( self.__onOK )
		self.__pyOkBtn.enable = False
		self.setOkButton( self.__pyOkBtn )

		labelGather.setPyBgLabel( self.__pyOkBtn, "MoneyInputBox:main", "btnOk" )
		labelGather.setPyBgLabel( self.__pyCancelBtn, "MoneyInputBox:main", "btnCancel" )

	def __onCancel( self ) :
		"""
		点击了取消按钮
		"""
		self.__pressedOk = False
		self.hide()

	def __onOK( self ) :
		"""
		点击了确定按钮
		"""
		self.__pressedOk = True
		self.hide()

	def __notify( self, res ) :
		"""
		触发回调
		@param		res : 点击结果( DialogResult.CANCEL/DialogResult.OK )
		@type		res : INT
		"""
		try :
			money = self.__moneyBox.money
			self.__callback( res, money )
		except :
			EXCEHOOK_MSG()
		self.__pressedOk = False


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onTextChanged_( self ) :
		self.__pyOkBtn.enable = self.__moneyBox.money > 0


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def dispose( self ) :
		"""
		释放实例
		"""
		Window.dispose( self )
		self.__class__.releaseInst()

	def show( self, callback, notifyText = "", pyOwner = None ) :
		"""
		@param		callback 	: 回调函数( 带两个参数 )
		@type		callback 	: function
		@param		notifyText	: 提示输入信息
		@type		notifyText	: str
		@param		pyOwner		: 父窗口
		@type		pyOwner		: python ui
		"""
		if self.__callback :
			self.__notify( DialogResult.CANCEL )
		self.__callback = callback
		if notifyText != "" :
			self.__pyNotifyText.text = notifyText
		Window.show( self, pyOwner )
		self.__moneyBox.money = 0
		self.__moneyBox.tabStop = True

	def hide( self ) :
		"""
		窗口关闭时调用
		"""
		Window.hide( self )
		if self.__pressedOk :
			self.__notify( DialogResult.OK )
		else :
			self.__notify( DialogResult.CANCEL )
		self.__callback = None
		self.removeFromMgr()
		self.dispose()

	def onActivated( self ) :
		"""
		当窗口激活时被调用
		"""
		Window.onActivated( self )
		self.__moneyBox.tabStop = True


class MoneyBox( object ) :

	def __init__( self, boxsPanel, pyBinder = None ) :
		self.__pyBoxGold = self.__createDefBox( boxsPanel.goldBox, 7 )
		self.__pyBoxSilver = self.__createDefBox( boxsPanel.silverBox, 2 )
		self.__pyBoxCoin = self.__createDefBox( boxsPanel.coinBox, 2 )

		self.__pyTabSwitcher = TabSwitcher( [self.__pyBoxGold,
											 self.__pyBoxSilver,
											 self.__pyBoxCoin,
											] )
		self.__pyBinder = None
		if pyBinder is not None :
			self.__pyBinder = weakref.ref( pyBinder )

		self.__onTextChanged = ControlEvent( "onTextChanged", self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __createDefBox( self, box, maxLength ) :
		pyBox = TextBox( box.box )
		pyBox.inputMode = InputMode.INTEGER
		pyBox.filterChars = [ "-","+" ]
		pyBox.maxLength = maxLength
		pyBox.onTabIn.bind( self.__onTextBoxTabIn )
		pyBox.onTextChanged.bind( self.onTextChanged_ )
		return pyBox

	def __onTextBoxTabIn( self, pyBox ) :
		"""
		某个box获得焦点
		"""
		pyBox.selectAll()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onTextChanged_( self ) :
		"""
		文字改变
		"""
		self.onTextChanged()


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	@property
	def onTextChanged( self ) :
		return self.__onTextChanged


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getReadOnly( self ) :
		return self.__pyBoxGold.readOnly and \
		self.__pyBoxSilver.readOnly and \
		self.__pyBoxCoin.readOnly

	def _setReadOnly( self, readOnly ) :
		self.__pyBoxGold.readOnly = readOnly
		self.__pyBoxSilver.readOnly = readOnly
		self.__pyBoxCoin.readOnly = readOnly

	def _getMoney( self ) :
		goldText = self.__pyBoxGold.text.strip()
		silverText = self.__pyBoxSilver.text.strip()
		copperText = self.__pyBoxCoin.text.strip()
		value = 0
		if goldText != "" :
			value += int( goldText ) * 10000
		if silverText != "" :
			value += int( silverText ) * 100
		if copperText != "" :
			value += int( copperText )
		return value

	def _setMoney( self, money ) :
		self.__pyBoxGold.text = str( money / 10000 )
		self.__pyBoxSilver.text = str( money % 10000 / 100 )
		self.__pyBoxCoin.text = str( money % 100 )

	def _getTabStop( self ) :
		return self.__pyBoxGold.tabStop or \
		self.__pyBoxSilver.tabStop or \
		self.__pyBoxCoin.tabStop

	def _setTabStop( self, tabStop ) :
		if tabStop :
			if not self.tabStop :
				self.__pyBoxGold.tabStop = tabStop
		else :
			self.__pyBoxGold.tabStop = tabStop
			self.__pyBoxSilver.tabStop = tabStop
			self.__pyBoxCoin.tabStop = tabStop

	def _getMaxGoldLength( self ) :
		return self.__pyBoxGold.maxLength

	def _setMaxGoldLength( self, length ) :
		self.__pyBoxGold.maxLength = length

	def _getPyBinder( self ) :
		if self.__pyBinder is None :
			return None
		return self.__pyBinder()

	readOnly = property( _getReadOnly, _setReadOnly )			# 是否只读
	tabStop = property( _getTabStop, _setTabStop )				# 设置/获取焦点
	money = property( _getMoney, _setMoney )					# 设置/获取输入的金钱
	maxGoldLength = property( _getMaxGoldLength, _setMaxGoldLength ) # 获取/设置最大金币输入长度
	pyBinder = property( _getPyBinder )


class MoneyBar( GUIBaseObject ) :
	"""
	这个最后将把MoneyBox替换掉
	"""
	def __init__( self, bar, pyBinder = None ) :
		GUIBaseObject.__init__( self, bar )
		self.__pyBoxGold = self.__createBox( bar.box_gold, 9 )
		self.__pyBoxSilver = self.__createBox( bar.box_silver, 2 )
		self.__pyBoxCoin = self.__createBox( bar.box_coin, 2 )

		self.__pyTabSwitcher = TabSwitcher( [self.__pyBoxGold,
											 self.__pyBoxSilver,
											 self.__pyBoxCoin,
											] )
		self.__pyBinder = None
		if pyBinder is not None :
			self.__pyBinder = weakref.ref( pyBinder )

		self.__onTextChanged = ControlEvent( "onTextChanged", self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __createBox( self, box, maxLength ) :
		pyBox = TextBox( box )
		pyBox.inputMode = InputMode.INTEGER
		pyBox.filterChars = [ "-","+" ]
		pyBox.maxLength = maxLength
		pyBox.onTabIn.bind( self.__onTextBoxTabIn )
		pyBox.onTextChanged.bind( self.onTextChanged_ )
		return pyBox

	def __onTextBoxTabIn( self, pyBox ) :
		"""
		某个box获得焦点
		"""
		pyBox.selectAll()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onTextChanged_( self ) :
		"""
		文字改变
		"""
		self.onTextChanged()


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	@property
	def onTextChanged( self ) :
		return self.__onTextChanged


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getReadOnly( self ) :
		return self.__pyBoxGold.readOnly and \
		self.__pyBoxSilver.readOnly and \
		self.__pyBoxCoin.readOnly

	def _setReadOnly( self, readOnly ) :
		self.__pyBoxGold.readOnly = readOnly
		self.__pyBoxSilver.readOnly = readOnly
		self.__pyBoxCoin.readOnly = readOnly

	def _getMoney( self ) :
		goldText = self.__pyBoxGold.text.strip()
		silverText = self.__pyBoxSilver.text.strip()
		copperText = self.__pyBoxCoin.text.strip()
		value = 0
		if goldText != "" :
			value += int( goldText ) * 10000
		if silverText != "" :
			value += int( silverText ) * 100
		if copperText != "" :
			value += int( copperText )
		return value

	def _setMoney( self, money ) :
		self.__pyBoxGold.text = str( money / 10000 )
		self.__pyBoxSilver.text = str( money % 10000 / 100 )
		self.__pyBoxCoin.text = str( money % 100 )

	def _getTabStop( self ) :
		return self.__pyBoxGold.tabStop or \
		self.__pyBoxSilver.tabStop or \
		self.__pyBoxCoin.tabStop

	def _setTabStop( self, tabStop ) :
		if tabStop :
			if not self.tabStop :
				self.__pyBoxGold.tabStop = tabStop
		else :
			self.__pyBoxGold.tabStop = tabStop
			self.__pyBoxSilver.tabStop = tabStop
			self.__pyBoxCoin.tabStop = tabStop

	def _getMaxGoldLength( self ) :
		return self.__pyBoxGold.maxLength

	def _setMaxGoldLength( self, length ) :
		self.__pyBoxGold.maxLength = length

	def _getPyBinder( self ) :
		if self.__pyBinder is None :
			return None
		return self.__pyBinder()
	
	def _getTabInControls( self ):
		return self.__pyTabSwitcher.pyTabInControls

	readOnly = property( _getReadOnly, _setReadOnly )			# 是否只读
	tabStop = property( _getTabStop, _setTabStop )				# 设置/获取焦点
	money = property( _getMoney, _setMoney )					# 设置/获取输入的金钱
	maxGoldLength = property( _getMaxGoldLength, _setMaxGoldLength ) # 获取/设置最大金币输入长度
	pyBinder = property( _getPyBinder )
	pyTabInControls = property( _getTabInControls )