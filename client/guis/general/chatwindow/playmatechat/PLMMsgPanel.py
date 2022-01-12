# -*- coding: gb18030 -*-

from guis import *
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ItemsPanel import ItemsPanel

from ChatFacade import chatFacade

class PLMMsgPanel( ItemsPanel ) :

	L_INDENT = 10										# ����������
	RF_INTERVAL = 0.02									# ��Ϣ��Ӽ��

	def __init__( self, panel, sbar, pyBinder = None ) :
		ItemsPanel.__init__( self, panel, sbar, pyBinder )
		self.focus = True
		self.__msgQueue = []							# ��Ϣ����
		self.__pasteCBID = 0


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __pasteMsg( self, flushText, indentedText ) :
		if flushText != "" :
			pyTRich = CSRichText()							# �����ı�
			pyTRich.maxWidth = self.width
			pyTRich.text = flushText
			self.addItem( pyTRich )
			pyTRich.left = 0
		if indentedText != "" :
			pyCRich = CSRichText()						# �����ı�
			pyCRich.opGBLink = True
			pyCRich.maxWidth = self.width - self.L_INDENT
			pyCRich.text = indentedText
			self.addItem( pyCRich )
			pyCRich.left = self.L_INDENT
		self.scroll = self.maxScroll

	def __pasteMsgGradual( self ) :
		"""
		���ճ����Ϣ
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
		ÿ�����һ����Ϣ
		"""
		if len( self.__msgQueue ) :
			self.__msgQueue.append( ( channel.id, spkID, spkName, msg, date ) )
			return
		title, msg = channel.formatMsg( spkID, spkName, msg, date )
		self.__pasteMsg( title, msg )

	def addMessages( self, msgs ) :
		"""
		ÿ����Ӷ�����Ϣ
		"""
		noPasting = len( self.__msgQueue ) == 0
		self.__msgQueue.extend( msgs )
		if noPasting :
			BigWorld.callback( self.RF_INTERVAL, self.__pasteMsgGradual )

	def breakPaste( self ) :
		"""
		���ճ��
		"""
		if len( self.__msgQueue ) :
			BigWorld.cancelCallback( self.__pasteCBID )
			self.__msgQueue = []

	def reset( self ) :
		"""
		������Ϣ����
		"""
		self.breakPaste()
		self.clearItems()