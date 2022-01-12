# -*- coding: gb18030 -*-
#
# $Id: AffichePanel.py $

"""
implement AffichePanel class
"""
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TextBox import TextBox
from guis.tooluis.CSMLRichTextBox import CSMLRichTextBox
from config.client.msgboxtexts import Datas as mbmsgs
import csdefine

class AffichePanel( Window ):
	__instance=None
	def __init__( self ):
		assert AffichePanel.__instance is None,"AffichePanel instance has been created"
		AffichePanel.__instance=self
		panel = GUI.load( "guis/general/relationwindow/familypanel/affiche.gui" )
		uiFixer.firstLoadFix( panel )
		Window.__init__( self, panel )
		self.addToMgr( "affichePanel" )
		self.__initpanel( panel )

	@staticmethod
	def instance():
		"""
		to get the exclusive instance of AffichePanel
		"""
		if AffichePanel.__instance is None :
			AffichePanel.__instance =AffichePanel()
		return AffichePanel.__instance

	@staticmethod
	def getInstance():
		"""
		return AffichePanel.__instance :there are two cases,one is None ,the other is the exclusive instance
		of AffichePanel
		"""
		return AffichePanel.__instance

	def __del__(self):
		"""
		just for testing memory leak
		"""
		pass

	def __initpanel( self, panel ):
		self.__pyBtnOK = HButtonEx( panel.btnOk )
		self.__pyBtnOK.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOK.onLClick.bind( self.__onSetAffiche )
		self.__pyBtnOK.enable = False
		labelGather.setPyBgLabel( self.__pyBtnOK, "RelationShip:RelationPanel", "btnOk" )

		self.__pyBtnCancel = HButtonEx( panel.btnCancel )
		self.__pyBtnCancel.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCancel.onLClick.bind( self.__onCancel )
		labelGather.setPyBgLabel( self.__pyBtnCancel, "RelationShip:RelationPanel", "btnCancel" )

		self.__pyAfficheBox = CSMLRichTextBox( panel.editPanel, panel.editBar )
		self.__pyAfficheBox.maxLength = 220
		self.__pyAfficheBox.onTextChanged.bind( self.__onAfficheChange )
		self.__pyAfficheBox.text = ""
		labelGather.setLabel( panel.lbTitle, "RelationShip:FamilyPanel", "afficeTitle" )

	def __onSetAffiche( self ): # 设置帮会公告
		if self.checkNotify_():
			affiche = self.__pyAfficheBox.text
			BigWorld.player().tong_setAffiche( affiche )
			self.hide()

	def __onAfficheChange( self ): # 公告内容改变调用
		self.__pyBtnOK.enable = True

	def checkNotify_( self ):
		affiche = self.__pyAfficheBox.text
		if len( affiche ) > csdefine.TONG_AFFICHE_LENGTH_MAX:
			# "帮会公告必须在200字节内"
			showMessage( 0x06a1,"", MB_OK )
			return False
		if rds.wordsProfanity.searchMsgProfanity( affiche ) is not None :
			# "输入的内容有禁用词汇!"
			showAutoHideMessage( 3.0, 0x06a2, mbmsgs[0x0c22] )
			return False
		return True

	def __onCancel( self ):
		self.hide()

	def updateAffiche( self, affiche ):
		self.__pyAfficheBox.text = rds.wordsProfanity.filterMsg( affiche )

	# ------------------------------------------------------
	# public
	# ------------------------------------------------------
	def show( self, afficheText, pyOwner ):
		self.__pyAfficheBox.text = afficheText
		Window.show( self, pyOwner )
		self.__pyAfficheBox.tabStop = True
		self.__pyAfficheBox.selectAll()

	def hide( self ):
		Window.hide( self )
		self.dispose()
		self.removeFromMgr()
		AffichePanel.__instance=None
		self.__pyAfficheBox.tabStop = False

	def reset( self ):
		self.__pyAfficheBox.text = ""