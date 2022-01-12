# -*- coding: gb18030 -*-
#
# $Id: ChangeNamePanel.py,v 1.10 2008-08-26 02:17:50 huangyongwei Exp $

"""
implement ChangeNamePanel item class
"""
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.TextBox import TextBox
from guis.controls.ButtonEx import HButtonEx

from config.client.msgboxtexts import Datas as mbmsgs
import BigWorld
import csdefine
import GUIFacade

class ChangeNamePanel( Window ):
	__instance=None
	def __init__( self, pyBinder=None ):
		assert ChangeNamePanel.__instance is None,"ChangeNamePanel window has been created"
		ChangeNamePanel.__instance=self
		panel = GUI.load( "guis/tooluis/nameinput/namepanel.gui" )
		uiFixer.firstLoadFix( panel )
		Window.__init__( self, panel )
		self.__petPdid = -1

		self.__pyTextBox = TextBox( panel.textBox.box, self )			# text for input value
		self.__pyTextBox.onTextChanged.bind( self.onTextChange_ )
		self.__pyTextBox.inputMode = InputMode.COMMON
		self.maxLength = 16

		self.__pyBtnOk = HButtonEx( panel.btnOk, self )
		self.__pyBtnOk.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOk.onLClick.bind( self.__onOk )
		self.setOkButton( self.__pyBtnOk )
		labelGather.setPyBgLabel( self.__pyBtnOk, "PetsWindow:ChangeName", "btnOk" )

		self.__pyBtnCancel = HButtonEx( panel.btnCancel,self)
		self.__pyBtnCancel.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCancel.onLClick.bind( self.__onCancel )
		self.pyCancelButton = self.__pyBtnCancel
		labelGather.setPyBgLabel( self.__pyBtnCancel, "PetsWindow:ChangeName", "btnCancel" )
		
		labelGather.setLabel( panel.lbTitle, "PetsWindow:ChangeName", "lbTitle" )
		labelGather.setLabel( panel.inputName, "PetsWindow:ChangeName", "inputName" )
		self.pressedOK_ = False
		self.callback_ = lambda *args : False
		self.posZSegment 	 = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True
		self.addToMgr( "petChangeNamePanel" )

	@staticmethod
	def instance():
		"""
		"""
		if ChangeNamePanel.__instance is None :
			ChangeNamePanel.__instance=ChangeNamePanel()
		return ChangeNamePanel.__instance

	@staticmethod
	def getInstance():
		"""
		return None or the exclusive instance of ChangeNamePanel
		"""
		return ChangeNamePanel.__instance

	def __del__(self):
		"""
		just for testing memory leak
		"""
		pass


	# -------------------------------------------------
	def __onOk( self ) :
		player = BigWorld.player()
		petEpitome = player.pcg_getPetEpitomes()[self.__petPdid]
		if self.notify_() :
			petEpitome.rename( self.__pyTextBox.text )
			self.__pyTextBox.text = ""
			self.hide()

	def __onCancel( self ) :
		self.hide()
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def notify_( self ) :
		text = self.__pyTextBox.text
		if text == "" : return False

		if len( text ) > 14 :	# wsf,加入宠物名字合法性检测
			# "名字长度不得超过7个汉字或14个英文字母"
			showAutoHideMessage( 3.0, 0x0cc1, mbmsgs[0x0c22] )
			return False
		elif text == "" :
			# "您输入的用户名无效，请重新输入。"
			showAutoHideMessage( 3.0, 0x0cc2, mbmsgs[0x0c22] )
			return False
		elif not rds.wordsProfanity.isPureString( text ) :
			# "名称不合法！"
			showAutoHideMessage( 3.0, 0x0cc3, mbmsgs[0x0c22] )
			return False
		elif rds.wordsProfanity.searchNameProfanity( text ) is not None :
			# "输入的名字有禁用词汇!"
			showAutoHideMessage( 3.0, 0x0cc4, mbmsgs[0x0c22] )
			return False

		try :
			self.callback_( DialogResult.OK, text )
		except :
			EXCEHOOK_MSG()
		self.pressedOK_ = True
		return True

	def onTextChange_( self ) :
		self.__pyBtnOk.enable = self.__pyTextBox.text != ""

	# ---------------------------------------------------------
	# public
	# ---------------------------------------------------------
	def show( self, bdid, pyBinder = None ) :
		self.__petPdid = bdid
		Window.show( self, pyBinder )

	def hide( self ):
		self.__petPdid = -1
		ChangeNamePanel.__instance=None
		Window.hide( self )
		self.dispose()

	def onActivated( self ) :
		"""
		当窗口激活时被调用
		"""
		Window.onActivated( self )
		self.__pyTextBox.tabStop = True
