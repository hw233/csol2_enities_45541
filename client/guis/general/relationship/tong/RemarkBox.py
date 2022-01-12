# -*- coding: gb18030 -*-
#
# $Id: FoundTong.py,v 1.4 2008-08-14 02:20:08 kebiao Exp $

"""
implement FoundTong window
"""
from guis import *
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TextBox import TextBox
from config.client.msgboxtexts import Datas as mbmsgs
from LabelGather import labelGather
import csdefine
import csstatus

class RemarkBox( Window ):
	def __init__( self ):
		panel = GUI.load( "guis/general/relationwindow/tongpanel/remark.gui" )
		uiFixer.firstLoadFix( panel )
		Window.__init__( self, panel )

		self.__pyRemarkBox = TextBox( panel.remarkBox.box, self )			# text for input value
		self.__pyRemarkBox.onTextChanged.bind( self.onTextChange_ )
		self.__pyRemarkBox.inputMode = InputMode.COMMON
		self.__pyRemarkBox.maxLength = 7

		self.__pyOkBtn = HButtonEx( panel.okBtn )
		self.__pyOkBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyOkBtn.onLClick.bind( self.__onOk )
		self.setOkButton( self.__pyOkBtn )

		self.__pyCancelBtn = HButtonEx( panel.cancelBtn )
		self.__pyCancelBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyCancelBtn.onLClick.bind( self.__onCancel )
		self.addToMgr( "remarkBox" )

		self.pressedOK_ = False

		self.__memberID = -1

		self.callback_ = lambda *args : False
		
		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setPyBgLabel( self.__pyCancelBtn, "TongAbout:RemarkBox", "cancelBtn" )
		labelGather.setPyBgLabel( self.__pyOkBtn, "TongAbout:RemarkBox", "okBtn" )
		labelGather.setLabel( panel.nameText, "TongAbout:RemarkBox", "nameText" )
		labelGather.setLabel( panel.lbTitle, "TongAbout:RemarkBox", "lbTitle" )

	# -------------------------------------------------
	def __onOk( self ) :
		player = BigWorld.player()
#		if self.__pyRemarkBox.tabStop:return
		if self.notify_() :
			remarkText = self.__pyRemarkBox.text.strip()
			player.tong_setMemberScholium( self.__memberID, remarkText )
			self.__pyRemarkBox.text = ""
			self.hide()

	def __onCancel( self ) :
		self.hide()
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def notify_( self ) :
		player = BigWorld.player()
		remarkText = self.__pyRemarkBox.text.strip()
		if len( remarkText ) > 7:
			# "备注不能超过7个字符!"
			showAutoHideMessage( 3.0, 0x0721, mbmsgs[0x0c22] )
			return False
		elif rds.wordsProfanity.searchMsgProfanity( remarkText ) is not None :
			# "输入的备注有禁用词汇!"
			showAutoHideMessage( 3.0, 0x0722, mbmsgs[0x0c22] )
			return False
		return True

	def onTextChange_( self ) :
		self.__pyOkBtn.enable = self.__pyRemarkBox.text != ""

	# ---------------------------------------------------------
	# public
	# ---------------------------------------------------------
	def show( self, memberID, pyOwner ) :
		player = BigWorld.player()
		self.__memberID = memberID
		member = player.tong_memberInfos.get( memberID, None )
		if member is None:return
		remark = member.getScholium()
		self.__pyRemarkBox.text = remark
		self.__pyRemarkBox.tabStop = True
		Window.show( self, pyOwner )

	def hide( self ):
		self.__pyRemarkBox.clear()
		Window.hide( self )

	def onLeaveWorld( self ) :
		self.__memberID = -1
		self.hide()

	def onActivated( self ) :
		"""
		当窗口激活时被调用
		"""
		Window.onActivated( self )
		self.__pyRemarkBox.tabStop = True