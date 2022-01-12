# -*- coding: gb18030 -*-
#
# $Id: ReadWindow.py,v 1.8 2008-08-26 02:15:13 huangyongwei Exp $

"""
implement readwindow  class
"""
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from guis.tooluis.CSTextPanel import CSTextPanel
from guis.general.StoreWindow.CompareDspItem import CompareDspItem
from ItemsFactory import ObjectItem as ItemInfo
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
import event.EventCenter as ECenter
from MailItem import MailItem
import csdefine
import csstatus
from Time import Time
from bwdebug import *
from ChatFacade import emotionParser
import GUIFacade

class ReadWindow( Window ):
	__instance=None
	def __init__( self, pyBinder = None):
		assert ReadWindow.__instance is None,"ReadWindow instance has been created"
		ReadWindow.__instance=self
		wnd = GUI.load( "guis/general/mailwindow/readpanel/window.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.mailID = -1
		self.recitems = {}
		self.addToMgr( "readWindow" )
		self.__pyRecItems = {} #收到的物品格
		self.__triggers = {}
		self.pyBinder = pyBinder
		self.__registerTriggers()
		self.__initialize( wnd )

	@staticmethod
	def instance():
		if ReadWindow.__instance is None:
			ReadWindow.__instance=ReadWindow()
		return ReadWindow.__instance

	@staticmethod
	def getInstance():
		"""
		return the exclusive instance of ReadWindow
		"""
		return ReadWindow.__instance


	def __del__(self):
		"""
		just for testing memory leak
		"""
		Window.__del__( self )
		if Debug.output_del_ReadWindow :
			INFO_MSG( str( self ) )

	def __initialize( self, wnd ):
		labelGather.setPyLabel( self.pyLbTitle_, "MailWindow:ReadWindow", "lbTitle" )
		labelGather.setLabel( wnd.addresserText, "MailWindow:ReadWindow", "addresserText" )
		labelGather.setLabel( wnd.themeText, "MailWindow:ReadWindow", "themeText" )

		self.__pybtnRecede = HButtonEx( wnd.btnRecede ) #退信
		self.__pybtnRecede.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyLabel( self.__pybtnRecede, "MailWindow:ReadWindow", "btnRecede" )
		self.__pybtnRecede.onLClick.bind( self.__onRecede )

		self.__pyBtnAll = HButtonEx( wnd.btnAll ) #全部收取
		self.__pyBtnAll.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyLabel( self.__pyBtnAll, "MailWindow:ReadWindow", "btnAll" )
		self.__pyBtnAll.onLClick.bind( self.__onRecedeAll )

		self.__pyTxtName = StaticText( wnd.lbName )
		self.__pyTxtName.text = ""

		self.__pyTxtTitle = StaticText( wnd.lbTheme )
		self.__pyTxtTitle.text = ""

		self.__pyRtMore = CSRichText( wnd.rtMore )
		self.__pyRtMore.align = "L"
		self.__pyRtMore.text = ""

		self.__pyReceivePanel = CSTextPanel( wnd.contentPanel, wnd.scrollBar )
		self.__pyReceivePanel.opGBLink = True
		self.__pyReceivePanel.spacing = 2.0

		for name, item in wnd.children: #初始化发送物品格
			if name.startswith( "reItem_" ):
				index = int( name.split( "_" )[1] )
				pyRecItem = MailItem( item, DragMark.MAIL_RECEIVE_ITEM, index )
				self.__pyRecItems[index] = pyRecItem
	# -------------------------------------------------------------------------
	# pravite
	# -------------------------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_MAIL_HAS_GETTTEN_MONEY"] = self.__onHasGettenMoney 		# 取走金钱
		self.__triggers["EVT_ON_MAIL_HAS_GETTEN_ITEM"] = self.__onHasGettenItem 		# 取走物品
		self.__triggers["EVT_ON_MAIL_HAS_GETTEN_ALL_ITEMS"] = self.__onHasGettenAllItems# 取走了所有物品

		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __unregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self  )

	# ----------------------------------------------------------------
	def __onReadLetter( self, mailID ):
		
		player = BigWorld.player()
		self.__clearItems()
		if player.mails.has_key( mailID ):
			self.mailID = mailID
			letter = player.mails[mailID]
			self.__pyTxtName.text = letter["senderNamer"]
			try:
				self.__pyTxtTitle.text = letter["title"]
				self.__pyReceivePanel.text = emotionParser.parseRcvMsg( letter["content"] )
			except:
				BigWorld.player().statusMessage( csstatus.MAIL_TITLE_OR_CONTENT_TOO_LONG, letter["mailID"] )
			items = letter["items"]
			receiveTime = letter["receiveTime"]
			if player.mailHasItemConut( mailID ) > 0:
				self.recitems = items.copy()
				for index, item in items.iteritems():
					itemInfo = None
					if item is not None:
						itemInfo = ItemInfo( item )
					if self.__pyRecItems.has_key( index ):
						self.__pyRecItems[index].update( itemInfo, mailID )
			money = letter["money"]
			if money > 0:
				moneyText = utils.currencyToViewText( money )
				self.__pyRtMore.text = labelGather.getText( "MailWindow:ReadWindow", "rtMoney", moneyText )
				self.__pyRtMore.text += PL_NewLine.getSource()
			else:
				self.__pyRtMore.text = ""
				
			self.__pyBtnAll.enable = len( items ) > 0 or money != 0
			#如果邮件是NPC和系统邮件 则退信按钮不可用 by姜毅
			if letter["senderType"] == csdefine.MAIL_SENDER_TYPE_PLAYER:
				self.__pybtnRecede.enable = True
			else:
				self.__pybtnRecede.enable = False
		timeTuple = Time.localtime( receiveTime )
		hour = timeTuple[3]
		rtTime = labelGather.getText( "MailWindow:ReadWindow", "rtTime" )
		self.__pyRtMore.text += PL_Font.getSource( rtTime%( timeTuple[1], timeTuple[2], PL_Space.getSource(5), hour, timeTuple[4] ), fc = ( 230, 227, 185 ) )

	def __onHasGettenMoney( self, mailID ): # 取走金钱的回调
		if mailID == self.mailID:
			player = BigWorld.player()
			letter = player.mails[mailID]
			receiveTime = letter["receiveTime"]
			timeTuple = Time.localtime( receiveTime )
			hour = timeTuple[3]
			rtTime = labelGather.getText( "MailWindow:ReadWindow", "rtTime" )
			self.__pyRtMore.text = PL_Font.getSource( rtTime%( timeTuple[1], timeTuple[2], PL_Space.getSource(5), hour, timeTuple[4] ), fc = ( 230, 227, 185 ) )	
	

					
	def __onHasGettenItem( self, mailID, index ): # 取走物品的回调
		if mailID == self.mailID:
			#self.__clearItems()
			self.recitems[index] = None
			#for iIndex, item in self.recitems.iteritems():
			#itemInfo = None
			#if item is not None:
			#	itemInfo = ItemInfo( item )
			if self.__pyRecItems.has_key( index  ):
				self.__pyRecItems[index].update( None, mailID )

	def __onHasGettenAllItems( self, mailID, failedIndexList ): # 取走所有物品的回调
		if mailID == self.mailID:
			self.__clearItems()
			for index in xrange( len( self.recitems ) ):
				if index in failedIndexList:
					itemInfo = None
					item = self.recitems[index]
					if item is not None:
						itemInfo = ItemInfo( item )
					if self.__pyRecItems.has_key( index  ):
						self.__pyRecItems[index].update( itemInfo, mailID )
		self.__onHasGettenMoney( mailID )

	

	def __onRecede( self ): #退信
		player = BigWorld.player()
		player.base.mail_playerReturn( self.mailID )

	def __onRecedeAll( self ):
		player = BigWorld.player()
		player.mail_getMoney( self.mailID )
		player.mail_getAllItem( self.mailID )

	def __clearItems( self ):
		for pyRecItem in self.__pyRecItems.itervalues():
			pyRecItem.update( None, -1 )
	# -------------------------------------------------------
	# public
	# -------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def onReadLetter( self, mailID, pyOwner ):
		self.__onReadLetter( mailID )
		self.show( pyOwner )

	def show( self, pyOwner = None ):
		Window.show( self, pyOwner )

	def hide( self ):
		Window.hide( self )
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )
		self.removeFromMgr()
		self.__unregisterTriggers()
		self.dispose()
		self.__triggers={}
		ReadWindow.__instance=None

	def onLeaveWorld( self ):
		self.__pyTxtName.text = ""
		self.__pyTxtTitle.text = ""
		self.recitems = {}
		self.mailID = -1
		self.__clearItems()
		self.hide()