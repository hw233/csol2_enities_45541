# -*- coding: gb18030 -*-
#
# $Id: FoundTong.py,v 1.4 2008-08-14 02:20:08 kebiao Exp $

"""
implement FoundTong window
"""
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TextBox import TextBox
from config.client.msgboxtexts import Datas as mbmsgs
import csdefine
import csstatus
import BigWorld

class FoundTong( Window ):
	__instance=None
	def __init__( self ):
		assert FoundTong.__instance is None,"FoundTong instance has been created"
		FoundTong.__instance=self
		panel = GUI.load( "guis/tooluis/nameinput/namepanel.gui" )
		uiFixer.firstLoadFix( panel )
		Window.__init__( self, panel )

		self.__pyTextBox = TextBox( panel.textBox.box, self )			# text for input value
		self.__pyTextBox.onTextChanged.bind( self.onTextChange_ )
		self.__pyTextBox.inputMode = InputMode.COMMON
		self.maxLength = 14

		self.__pyBtnOk = HButtonEx( panel.btnOk, self )
		self.__pyBtnOk.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOk.enable = False
		self.__pyBtnOk.onLClick.bind( self.__onOk )
		labelGather.setPyBgLabel( self.__pyBtnOk, "RelationShip:RelationPanel", "btnOk" )
		self.setOkButton( self.__pyBtnOk )

		self.__pyBtnCancel = HButtonEx( panel.btnCancel, self)
		self.__pyBtnCancel.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCancel.onLClick.bind( self.__onCancel )
		labelGather.setPyBgLabel( self.__pyBtnCancel, "RelationShip:RelationPanel", "btnCancel" )
		self.pyCancelButton = self.__pyBtnCancel

		labelGather.setLabel( panel.lbTitle, "RelationShip:TongPanel", "lbTitle" )
		labelGather.setLabel( panel.inputName, "RelationShip:TongPanel", "inputName" )
		
		self.addToMgr( "foundTong" )

		self.pressedOK_ = False

		self.callback_ = lambda *args : False

	@staticmethod
	def instance():
		if FoundTong.__instance is None:
			FoundTong.__instance=FoundTong()
		return FoundTong.__instance

	# -------------------------------------------------
	def __onOk( self ) :
		player = BigWorld.player()
		if self.notify_() :
			player.cell.createTong( self.__pyTextBox.text, csdefine.TONG_CREATE_REASON_NOMAL )
			self.__pyTextBox.text = ""
			self.hide()

	def __onCancel( self ) :
		self.hide()

	def __del__(self):
		pass
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def notify_( self ) :
		player = BigWorld.player()
		text = self.__pyTextBox.text
		if text == "" : return False

		if player.tong_dbID > 0:
			# "�Բ������Ѿ���һ������ˡ�"
			showAutoHideMessage( 3.0, 0x0761, mbmsgs[0x0c22], pyOwner = self )
			return False
		elif len( text ) > 14 :	# ������ƺϷ��Լ��
			# "���ֳ��Ȳ��ܳ��� 14 ���ֽ�"
			showAutoHideMessage( 3.0, 0x0762, mbmsgs[0x0c22], pyOwner = self )
			return False
		elif text == "" :
			# "��������û�����Ч�����������롣"
			showAutoHideMessage( 3.0, 0x0763, mbmsgs[0x0c22], pyOwner = self )
			return False
		elif not rds.wordsProfanity.isPureString( text ) :
			# "���Ʋ��Ϸ���"
			showAutoHideMessage( 3.0, 0x0764, mbmsgs[0x0c22], pyOwner = self )
			return False
		elif self.__isHasDigit( text ):#��������
			# "�������ֻ���ɺ��ֺ���ĸ��ɣ�"
			showAutoHideMessage( 3.0, 0x0765, mbmsgs[0x0c22], pyOwner = self )
			return False
		elif rds.wordsProfanity.searchNameProfanity( text ) is not None :
			# "����������н��ôʻ�!"
			showAutoHideMessage( 3.0, 0x0766, mbmsgs[0x0c22], pyOwner = self )
			return False
		elif csdefine.TONG_CREATE_MONEY > player.money:
			# "�Բ��𣬴������������Ҫ30���,���Ľ�Ǯ���㡣"
			showAutoHideMessage( 3.0, 0x0767, mbmsgs[0x0c22], pyOwner = self )
			return False
		elif csdefine.TONG_CREATE_LEVEL > player.level:
			# "�Բ��𣬴��������Ҫ����45����"
			showAutoHideMessage( 3.0, 0x0768, mbmsgs[0x0c22], pyOwner = self )
			return False
		try :
			self.callback_( DialogResult.OK, text )
		except :
			EXCEHOOK_MSG()
		self.pressedOK_ = True
		return True

	def __isHasDigit( self, text ):
		for letter in text:
			if letter.isdigit():
				return True
			else:
				continue
		return False

	def onTextChange_( self ) :
		self.__pyBtnOk.enable = self.__pyTextBox.text != ""

	# ---------------------------------------------------------
	# public
	# ---------------------------------------------------------
	def show( self ) :
		player = BigWorld.player()
		if player.tong_dbID > 0:
			player.statusMessage( csstatus.TONG_CREATE_HAS_A_TONG )
			return
		elif player.level < csdefine.TONG_CREATE_LEVEL:
			player.statusMessage( csstatus.TONG_CREATE_LEVEL_INVALID, csdefine.TONG_CREATE_LEVEL )
			return
		elif player.money < csdefine.TONG_CREATE_MONEY:
			player.statusMessage( csstatus.TONG_CREATE_MONEY_INVALID )
			return
		Window.show( self )
		self.__pyTextBox.tabStop = True

	def hide( self ):
		Window.hide( self )
		self.dispose()
		FoundTong.__instance=None
		self.__pyTextBox.tabStop = False
		self.removeFromMgr()

	def onLeaveWorld( self ) :
		self.hide()

	def onActivated( self ) :
		"""
		�����ڼ���ʱ������
		"""
		Window.onActivated( self )
		self.__pyTextBox.tabStop = True
