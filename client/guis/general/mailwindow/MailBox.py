# -*- coding: gb18030 -*-
#
# $Id: MailBox.py,v 1.14 2008-08-30 09:10:29 huangyongwei Exp $

"""
implement mailbox  class
"""
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from guis.controls.TextBox import TextBox
from guis.controls.TabCtrl import TabPanel
from guis.controls.ContextMenu import ContextMenu
from guis.controls.ContextMenu import DefMenuItem
from guis.controls.ODPagesPanel import ODPagesPanel
from config.client.msgboxtexts import Datas as mbmsgs
from ReadWindow import ReadWindow
from LetterItem import LetterItem
import event.EventCenter as ECenter
import csdefine

class MailBox( TabPanel ):
	
	_cc_items_rows = ( 7,1 )

	def __init__( self, panel, pyBinder = None ):
		TabPanel.__init__( self, panel, pyBinder )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True
		self.__triggers = {}
		self.__registerTriggers()
		self.__initPanel( panel )
#		self.__createLetterMenu()

	def __initPanel( self, panel ):
		self.__pyBtnRestore = HButtonEx( panel.btnRestore ) #回复信件
		self.__pyBtnRestore.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnRestore.enable = False
		self.__pyBtnRestore.onLClick.bind( self.__onRestoreMail )
		labelGather.setPyBgLabel( self.__pyBtnRestore, "MailWindow:panel_0", "btnRestore" )

		self.__pyBtnDel = HButtonEx( panel.btnDel ) #删除信件
		self.__pyBtnDel.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnDel.enable = False
		self.__pyBtnDel.onLClick.bind( self.__onDelMail )
		labelGather.setPyBgLabel( self.__pyBtnDel, "MailWindow:panel_0", "btnDel" )

		self.__pyBtnRead = HButtonEx( panel.btnRead ) #阅读信件
		self.__pyBtnRead.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnRead.enable = False
		self.__pyBtnRead.onLClick.bind( self.__onReadMail )
		labelGather.setPyBgLabel( self.__pyBtnRead, "MailWindow:panel_0", "btnRead" )

		self.__pyStTotalNum = StaticText( panel.stTotNums )
		self.__pyStTotalNum.text = ""
		
		self.__pyLettersPage = ODPagesPanel( panel.lettersPanel, panel.pgIdxBar )
		self.__pyLettersPage.onViewItemInitialized.bind( self.__initListItem )
		self.__pyLettersPage.onDrawItem.bind( self.__drawListItem )
		self.__pyLettersPage.selectable = True
		self.__pyLettersPage.onItemSelectChanged.bind( self.__onLetterSelected )
		self.__pyLettersPage.viewSize = self._cc_items_rows


	def __createLetterMenu( self ):
		self.__pyLetterMenu = ContextMenu()								# modified by hyw( 2008.04.17 )
#		self.__pyLetterMenu.onItemClick.bind( self.__onItemClick )
		self.pyItem0 = DefMenuItem( labelGather.getText( "MailWindow:main", "readLetter" ) )
		self.pyItem1 = DefMenuItem( labelGather.getText( "MailWindow:main", "delLetter" ) )
		self.__pyLetterMenu.pyItems.adds( [self.pyItem0, self.pyItem1] )


	# ------------------------------------------------------
	# private
	# ------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_MAIL_ADD_LETTER"]	= self.__onAddLetter # 接收新的邮件
		self.__triggers["EVT_ON_MAIL_DEL_LETTER"] = self.__onDelLetter # 删除邮件
		self.__triggers["EVT_ON_MAIL_READ_LETTER"] = self.__onReadLetter #阅读信件回调
		self.__triggers["EVT_ON_MAIL_HAS_GETTEN_ITEM"] = self.__onItemHasTaken # 取走物品的回调
		self.__triggers["EVT_ON_MALL_HAS_GETTEN_MONEY"] = self.__onMoneyHasTaken  #取走所有金钱		
		self.__triggers["EVT_ON_MAIL_HAS_GETTEN_ALL_ITEMS"] = self.__onHasGettenAllItems# 取走了所有物品		
		self.__triggers["EVT_ON_MAIL_UPDATE_LETTER"] = self.__onUpdateletter # 更新邮件信息
		self.__triggers["EVT_ON_MAIL_SELECTED"] = self.__onMailSelected
		
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __unregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )

	# -----------------------------------------------------------
	def __initListItem( self, pyViewItem ):
		pyLetter = LetterItem()
		pyViewItem.pyLetter = pyLetter
		pyViewItem.addPyChild( pyLetter )
		pyViewItem.dragFocus = False
		pyViewItem.focus = False
		pyLetter.left = 0
		pyLetter.top = 0
	
	def __drawListItem( self, pyViewItem ):
		letter = pyViewItem.pageItem
		pyLetter = pyViewItem.pyLetter
		pyLetter.update( letter )
		if letter is not None:
			pyLetter.selected = pyViewItem.selected
			pyViewItem.focus = letter is not None
		curPageIndex = self.__pyLettersPage.pageIndex
		itemCount = self.__pyLettersPage.itemCount
		self.__pyStTotalNum.text = labelGather.getText( "MailWindow:panel_0", "stTotalNums" )%itemCount
	
	def __onLetterSelected( self, index ):
		selLetter = self.__pyLettersPage.selItem
		if selLetter is None:return
		mailType = selLetter["senderType"]
		mailID = selLetter["mailID"]
		self.__pyBtnRestore.enable = mailID != -1 and mailType == csdefine.MAIL_SENDER_TYPE_PLAYER #信件不为空并且为玩家信件
		self.__pyBtnDel.enable = mailID != -1
		self.__pyBtnRead.enable = mailID != -1
		
	def __onAddLetter( self, index, letter ):
		mailID = letter["mailID"]
		if not letter in self.__pyLettersPage.items:
			self.__pyLettersPage.insterItem( 0, letter )
		itemCount = self.__pyLettersPage.itemCount
		self.__pyStTotalNum.text = labelGather.getText( "MailWindow:panel_0", "stTotalNums" )%itemCount

	def __onUpdateletter( self, mailID ):
		player = BigWorld.player()
		mails = player.mails
		newLetter = mails[mailID]
		for pyViewItem in self.__pyLettersPage.pyViewItems:
			letter = pyViewItem.pageItem
			pyLetter = pyViewItem.pyLetter
			if letter is None:continue
			if mailID == letter["mailID"]:
				pyLetter.update( newLetter )

	def __onRestoreMail( self ):
		selLetter = self.__pyLettersPage.selItem
		if selLetter is None:return
		recieName = selLetter["senderNamer"]
		mailType = selLetter["senderType"]
		if mailType != csdefine.MAIL_SENDER_TYPE_PLAYER:return #不是玩家信件，不需回复
		ECenter.fireEvent( "EVT_ON_RESTORE_MAIL", recieName )

	def __onDelMail( self ): #删除信件
		selLetter = self.__pyLettersPage.selItem
		if selLetter is None:return
		player = BigWorld.player()
		mailID = selLetter["mailID"]
		if mailID < 0:return
		if player.mailHasItemConut( mailID ) > 0 or selLetter["money"] != 0:
			def query( rs_id ):
				if rs_id == RS_OK:
					player.mail_delete( mailID )
			# "邮件%s含有物品或金钱，确定删除?"
			showMessage( mbmsgs[0x0441] % selLetter["title"],"", MB_OK_CANCEL, query, pyOwner = self )
			return True
		player.mail_delete( mailID )

	def __onReadMail( self ):
		selLetter = self.__pyLettersPage.selItem
		if selLetter is None:return
		player = BigWorld.player()
		mailID = selLetter["mailID"]
		player.mail_read( mailID )
		selLetter.update( selLetter )

	def __onDelLetter( self, mailID ): #删除一个邮件
		for letter in self.__pyLettersPage.items:
			if letter["mailID"] == mailID:
				self.__pyLettersPage.removeItem( letter )
#		self.__layoutLetters() # 重新排列信件
		itemCount = self.__pyLettersPage.itemCount
		self.__pyBtnDel.enable = itemCount > 0
		self.__pyStTotalNum.text = labelGather.getText( "MailWindow:panel_0", "stTotalNums" )%itemCount
		if ReadWindow.getInstance() and ReadWindow.getInstance().mailID == mailID: #如果删除的信件是正在阅读的信件
			ReadWindow.getInstance().hide()

	def __onReadLetter( self, mailID ):
		ReadWindow.instance().onReadLetter( mailID, self.pyBinder )
		for pyViewItem in self.__pyLettersPage.pyViewItems:
			letter = pyViewItem.pageItem
			pyLetter = pyViewItem.pyLetter
			if letter is None:continue
			if letter["mailID"] == mailID:
				letter = BigWorld.player().mails[mailID]
				pyLetter.update( letter )
				
				
	def __layoutLetters( self ):
		self.__clearLetters()
		for index, tuple in enumerate ( self.__mailLetters.itervalues() ):
			letter = tuple[1]
			if self.__pyLetters.has_key( index ):
				pyLetter = self.__pyLetters[index]
				pyLetter.update( letter )

	def __clearLetters( self ):
		self.__pyLettersPage.clearItems()

	def __onMailSelected( self, mailID ):
		for pyViewItem in self.__pyLettersPage.pyViewItems:
			pyLetter = pyViewItem.pyLetter
			letter = pyViewItem.pageItem
			if letter is None:continue
			if letter["mailID"] == mailID:
				self.__pyLettersPage.selItem = letter

	def __updateLetter( self, index, letter ): #更新界面控件
		if self.__pyLetters.has_key( index ):
			letterItem = self.__pyLetters[index]
			letterItem.update( letter )

	def __onItemHasTaken( self, mailID, index ): # 取走物品的回调
		for pyViewItem in self.__pyLettersPage.pyViewItems:
			letter = pyViewItem.pageItem
			pyLetter = pyViewItem.pyLetter
			if letter is None:continue
			if letter["mailID"] == mailID:
				letter = BigWorld.player().mails[mailID]
				pyLetter.update( letter )
	
	def __onMoneyHasTaken(self, mailID ):
		for pyViewItem in self.__pyLettersPage.pyViewItems:
			letter = pyViewItem.pageItem
			pyLetter = pyViewItem.pyLetter
			if letter is None:continue
			if letter["mailID"] == mailID:
				letter = BigWorld.player().mails[mailID]	
				letter["money"] = 0
				pyLetter.update( letter )		
				
	
	def __onHasGettenAllItems( self, mailID, failedIndexList ):
		for pyViewItem in self.__pyLettersPage.pyViewItems:
			letter = pyViewItem.pageItem
			pyLetter = pyViewItem.pyLetter
			if letter is None:continue
			if letter["mailID"] == mailID:
				letter = BigWorld.player().mails[mailID]
				letter["money"] = 0
				pyLetter.update( letter )
		self.__onMoneyHasTaken( mailID )



	def __onLetterRClick( self, pyLetter ): # 信件右键菜单
		self.pySelletter = pyLetter
		self.__pyLetterMenu.addBinder( pyLetter )			# hyw( 2008.04.17 )

	# --------------------------------------------
	# pubic
	# --------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def reset( self ):
		self.__clearLetters()
		self.__pyBtnDel.enable = False
		self.__pyBtnRead.enable = False
		self.__pyBtnRestore.enable = False
