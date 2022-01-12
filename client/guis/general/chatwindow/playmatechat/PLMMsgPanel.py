# -*- coding: gb18030 -*-

from guis import *
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ItemsPanel import ItemsPanel

from ChatFacade import chatFacade

class PLMMsgPanel( ItemsPanel ) :

	L_INDENT = 10										# 左缩进距离
	RF_INTERVAL = 0.02									# 消息添加间隔

	def __init__( self, panel, sbar, pyBinder = None ) :
		ItemsPanel.__init__( self, panel, sbar, pyBinder )
		self.focus = True
		self.__msgQueue = []							# 消息队列
		self.__pasteCBID = 0


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __pasteMsg( self, flushText, indentedText ) :
		if flushText != "" :
			pyTRich = CSRichText()							# 顶格文本
			pyTRich.maxWidth = self.width
			pyTRich.text = flushText
			self.addItem( pyTRich )
			pyTRich.left = 0
		if indentedText != "" :
			pyCRich = CSRichText()						# 缩进文本
			pyCRich.opGBLink = True
			pyCRich.maxWidth = self.width - self.L_INDENT
			pyCRich.text = indentedText
			self.addItem( pyCRich )
			pyCRich.left = self.L_INDENT
		self.scroll = self.maxScroll

	def __pasteMsgGradual( self ) :
		"""
		逐个粘贴消息
		"""
		if len( self.__msgQueue ) == 0 : return
		chid, spkID, spkName, msg, date = self.__msgQueue.pop( 0 )
		channel = chatFacade.getChannel( chid )
		title, msg = channel.formatMsg( spkID, spkName, msg, date )
		self.__pasteMsg( title, msg )
		if len( self.__msgQueue ) :
			self.__pasteCBID = BigWorld.callback( self.RF_INTERVAL, self.__pasteMsgGradual )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addMessage( self, channel, spkID, spkName, msg, date ) :
		"""
		每次添加一条消息
		"""
		if len( self.__msgQueue ) :
			self.__msgQueue.append( ( channel.id, spkID, spkName, msg, date ) )
			return
		title, msg = channel.formatMsg( spkID, spkName, msg, date )
		self.__pasteMsg( title, msg )

	def addMessages( self, msgs ) :
		"""
		每次添加多条消息
		"""
		noPasting = len( self.__msgQueue ) == 0
		self.__msgQueue.extend( msgs )
		if noPasting :
			BigWorld.callback( self.RF_INTERVAL, self.__pasteMsgGradual )

	def breakPaste( self ) :
		"""
		打断粘贴
		"""
		if len( self.__msgQueue ) :
			BigWorld.cancelCallback( self.__pasteCBID )
			self.__msgQueue = []

	def reset( self ) :
		"""
		重设消息界面
		"""
		self.breakPaste()
		self.clearItems()