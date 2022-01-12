# -*- coding: gb18030 -*-

import csconst
from guis import *
from guis.controls.CheckBox import CheckBoxEx
from guis.tooluis.messagebox.MsgBox import YesNoBox
from config.client.msgboxtexts import Datas as mbmsgs
from LabelGather import labelGather

class VerifyBox( YesNoBox ) :
	def __init__( self ) :
		box = GUI.load( "guis/general/petswindow/vehiclePanel/verifybox.gui" )
		uiFixer.firstLoadFix( box )
		YesNoBox.__init__( self, box )
		self.activable_ = False
		self.pyCBReverify_ = CheckBoxEx( box.cbReverify )
		self.pyCBReverify_.checked = False
		self.minHeight_ = 186.0								# 设置最小高度

		self.__callback = None

		labelGather.setPyBgLabel( self.pyCBReverify_, "PetsWindow:VehiclesPanel", "cbNotify" )

	def dispose( self ) :
		global _pyBox
		_pyBox = None
		YesNoBox.dispose( self )
		self.__callback = None


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __feedback( self, resultID ) :
		"""
		点击按钮后的返回
		"""
		self.__callback( resultID, self.pyCBReverify_.checked )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, callback, pyOwner = None ) :
		self.__callback = callback
		self.pyMsgPanel_.top = 48.0
		# "是否要为骑宠传功？传送后的潜能将无法回收。"
		msg = mbmsgs[0x0d03]
		YesNoBox.show( self, msg, "", self.__feedback, pyOwner )
		if self.pyCBReverify_:
			self._YesNoBox__pyYesBtn.top = self.pyBgPanel_.bottom + 24.0
			self._YesNoBox__pyNoBtn.top = self.pyBgPanel_.bottom + 24.0
		return self

_pyBox = None

def show( callback, pyOwner = None ) :
	global _pyBox
	if _pyBox :
		_pyBox.show( callback, pyOwner )
	else :
		_pyBox = VerifyBox().show( callback, pyOwner )
