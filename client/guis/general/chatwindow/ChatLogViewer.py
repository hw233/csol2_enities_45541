# -*- coding: gb18030 -*-

# implement ChatLogViewer class
# written by gjx 2009-8-22

import os
import csol
import time
import csdefine
from bwdebug import *
from guis import *
from ChatFacade import chatFacade
from LabelGather import labelGather
from cscollections import MapList
from guis.common.Window import Window
from guis.controls.ItemsPanel import ItemsPanel
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ButtonEx import HButtonEx
from event import EventCenter as ECenter
from config.client.msgboxtexts import Datas as mbmsgs
from guis.general.chatwindow.channelfilter.ChannelFilter import ChannelFilter


class ChatLogPanel( ItemsPanel ) :

	def removeItem( self, pyItem ) :
		"""
		rewrite this method for not layouting each time removes one item
		@type			pyItem : instance of python item
		@param			pyItem : the item you want to remove
		@return				   : None
		"""
		if pyItem not in self.pyItems_ :
			DEBUG_MSG( "the item %s is not in the items panel!" % pyItem )
			return
		self.delPyChild( pyItem )
		self.pyItems_.remove( pyItem )

	def layoutItems( self, startIndex = 0 ) :
		"""
		���˽ӿڽӿڹ���
		"""
		self.layoutItems_( startIndex )


class ChatLogViewer( Window ) :

	__REFRESH_INTERVAL = 0.02										# ��Ϣ��Ӽ��
	__CHAT_MAX_COUNT = 400											# ������Ϣ��󱣴�����
	__COMBAT_MAX_COUNT = 200										# ս����Ϣ��󱣴�����
	__COMBAT_CNID = csdefine.CHAT_CHANNEL_COMBAT

	def __init__( self ) :
		wnd = GUI.load("guis/general/chatwindow/chatlogviewer/wnd.gui")
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.addToMgr( "chatLogViewer" )

		self.__usedTextObj = []										# ����������ֶζ����Ա�����
		self.__refreshCBID = 0										# ˢ�»ص�ID���ûص��ķ�����ֹˢ�¹�������ʱ̫��
		self.__msgCounter = 0 										# ����Ϣ�Ľ���˳�����

		self.__panelMsgIDs = []										# ���������е���ϢID
		self.__tmpInvalidMsg = {}									# �ݴ����������׼������������ӵ���Ϣ����
		self.__overflowMsg = {}										# �ݴ����������ǰ�ڽ�������ʾ����Ϣλ��
		self.__addingMsgIDs = []									# ׼����������ӵ���Ϣ

		self.__currSelChannels = set()								# ��ǰ��ѡ���Ƶ��
		self.__channels = MapList()									# ������Ϣ( Ƶ����ɫ, { ��ϢID:��Ϣ, ... } )
		self.__savePath = ""										# ��Ϣ����·��(Ĭ�ϱ����ڶ�Ӧ���˺Ž�ɫĿ¼��)

		self.__setToDefaultChannels()								# ��ѡ��Ƶ������ΪĬ��ֵ
		self.__initChannels()
		self.__initialize( wnd )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		self.__pySaveBtn = HButtonEx( wnd.saveBtn )					# ������־��ť
		self.__pySaveBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pySaveBtn.onLClick.bind( self.__saveLog )
		self.__pySaveBtn.isOffsetText = True

		self.__pyRefreshBtn = HButtonEx( wnd.refreshBtn )				# ˢ�½�����Ϣ��ť
		self.__pyRefreshBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyRefreshBtn.onLClick.bind( self.__onRefreshMsg )
		self.__pyRefreshBtn.isOffsetText = True

		self.__pySelCNBtn = HButtonEx( wnd.selChannelBtn )				# ѡ��Ƶ����ť
		self.__pySelCNBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pySelCNBtn.onLClick.bind( self.__selChannel )
		self.__pySelCNBtn.isOffsetText = True

		#self.__pyTopBtn = HButtonEx( wnd.topBtn )						# ������������ť
		#self.__pyTopBtn.setExStatesMapping( UIState.MODE_R1C3 )
		#self.__pyTopBtn.onLClick.bind( self.__gotoTop )

		#self.__pyBottomBtn = HButtonEx( wnd.bottomBtn )				# �������ײ���ť
		#self.__pyBottomBtn.setExStatesMapping( UIState.MODE_R1C3 )
		#self.__pyBottomBtn.onLClick.bind( self.__gotoBottom )

		self.__pyMsgPanel = ChatLogPanel( wnd.pnl_content.clipPanel, wnd.pnl_content.sbar )
		self.__pyMsgPanel.skipScroll = False

		for chid, channel in chatFacade.channels.items() :			# �󶨽�����Ϣ��Ƶ��������
			if not channel.setable : continue
			if chid == csdefine.CHAT_CHANNEL_PLAYMATE : continue	# ���ﲻ��¼��������������Ϣ
			chatFacade.bindChannelHandler( chid, self.__onReceiveMessage )

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pySaveBtn, "ChatWindow:ChatLogViewer", "btnSave" )
		labelGather.setPyBgLabel( self.__pyRefreshBtn, "ChatWindow:ChatLogViewer", "btnRefresh" )
		labelGather.setPyBgLabel( self.__pySelCNBtn, "ChatWindow:ChatLogViewer", "btnCNSelect" )
		labelGather.setLabel( self.gui.lbTitle, "ChatWindow:ChatLogViewer", "lbTitle" )

	def __initChannels( self ) :
		"""
		��ʼ��������Ҫ��¼��Ƶ��
		"""
		for cnID in chatFacade.channels :
			self.__channels[ cnID ] = [ (255,255,255,255), MapList() ]

	# -------------------------------------------------
	# function
	# -------------------------------------------------
	def __gotoTop( self ) :
		"""
		�ѹ�����λ������Ϊ����
		"""
		self.__pyMsgPanel.scroll = 0

	def __gotoBottom( self ) :
		"""
		�ѹ�����λ������Ϊ�ײ�
		"""
		self.__pyMsgPanel.scroll = self.__pyMsgPanel.maxScroll

	def __selChannel( self ) :
		"""
		���ѡ��Ƶ����ť
		"""
		title = labelGather.getText( "ChatWindow:ChatLogViewer", "lbSelCNClew" )
		ChannelFilter().show( title, self.__currSelChannels, self.__onChannelSelected, self )

	def __saveLog( self ) :
		"""
		����ѡ�е�Ƶ����Ϣ�����ش���
		"""
		if self.__savePath == "" : return
		pyMsgItems = self.__pyMsgPanel.pyItems
		if len( pyMsgItems ) == 0 : return
		rootPath = os.getcwd() + "\\res\\"
		fileName = time.strftime( "%y%m%d_%H%M%S", time.localtime() ) + ".txt"
		filePath = self.__savePath + fileName

		def saveFile() :
			try :
				file = open( filePath, "w" )
				for pyMsg in pyMsgItems :
					text = pyMsg.viewText
					file.write( text + "\n" )
				file.flush()
				file.close()
				# �����¼�ѳɹ����浽%s�ļ��С�
				msg = mbmsgs[0x0241] % ( rootPath + filePath.replace( "/", "\\" ) )
				showMessage( msg, "", MB_OK, None, self )
			except IOError, errstr :
				# "�����ļ�ʧ�ܣ�%s"
				showMessage( mbmsgs[0x0242] % errstr, "", MB_OK, None, self )

		def query( result ) :
			if result == RS_YES : saveFile()

		fileExists = csol.resourceExists( filePath )				# ����ļ��Ƿ����
		if fileExists :												# �����������ʾ��ͻ
			# �ļ�%s�Ѵ��ڣ��Ƿ񸲸ǣ�
			msg = mbmsgs[0x0243] % ( rootPath + filePath.replace( "/", "\\" ) )
			showMessage( msg, "", MB_YES_NO, query, self )
		else :
			s = ResMgr.openSection( filePath, True )				# ����δ�ҵ��������������ļ���
			s.save()												# �������������������ļ�
			ResMgr.purge( filePath )
			saveFile()

	def __onRefreshMsg( self ) :
		"""
		ˢ�½�����Ϣ
		"""
		self.__refreshEfficient()

	def __onChannelSelected( self, isOK, selChannels ) :
		"""
		ѡ��һ���µ�Ƶ������
		"""
		if not isOK : return
		if selChannels == self.__currSelChannels : return
		self.__currSelChannels = selChannels						# ����ѡ�е�Ƶ��
		self.__addingMsgIDs = self.__getSelMsgIDs()					# ��ȡѡ�������Ƶ����Ϣ
		self.__panelMsgIDs = self.__addingMsgIDs[:]
		self.__tmpInvalidMsg = {}
		self.__refreshMsg()

	def __shutdownRefresh( self ) :
		if self.__refreshCBID :
			BigWorld.cancelCallback( self.__refreshCBID )
			self.__refreshCBID = 0

	def __refreshMsg( self ) :
		"""
		ˢ�½�����Ϣ
		"""
		self.__shutdownRefresh()									# ֹ֮ͣǰ��ˢ��
		self.__clearPanel()											# �����Ϣ����
		self.__addMsgGradual()

	def __refreshEfficient( self ) :
		"""
		ʹ����Ը�Ч�ķ���ˢ�½���
		"""
		selMsgIDs = self.__getSelMsgIDs()							# ����Ҫ��ӵ������ϵ���Ϣ
		startIndex = 0
		remainMsg = [ i for i in self.__panelMsgIDs \
					if i not in self.__overflowMsg ]
		if len( remainMsg ) > 0 :
			startMsgID = remainMsg[-1]
			startIndex = selMsgIDs.index( startMsgID ) + 1
		self.__panelMsgIDs = selMsgIDs								# ���浱ǰ�����ϵ�������ϢID
		self.__addingMsgIDs.extend( selMsgIDs[ startIndex : ] )		# ��ȡ�¼ӵ������ϵ���ϢID
		self.__shutdownRefresh()									# ֹ֮ͣǰ��ˢ��
		self.__removeOverflowMsg()									# �Ƴ������ϵ������Ϣ
		self.__addMsgGradual()

	def __addMsgGradual( self ) :
		"""
		��������Ϣ������
		"""
		if len( self.__addingMsgIDs ) == 0 : return
		msgID = self.__addingMsgIDs.pop( 0 )
		msg, color = self.__getMsgContent( msgID )					# ��ȡ��Ϣ����
		self.__addMsgToPanel( msg, color )							# �����Ϣ������
		self.__refreshCBID = BigWorld.callback( self.__REFRESH_INTERVAL, self.__addMsgGradual )

	def __getSelMsgIDs( self ) :
		"""
		��ȡ��ǰѡ��Ƶ����������ϢID
		"""
		selMsgIDs = []
		for channelID in self.__currSelChannels :
			msgCN = self.__channels.get( channelID, ((),[]) )
			selMsgIDs.extend( msgCN[1] )
		selMsgIDs.sort()											# ������ϢID����
		return selMsgIDs

	def __getMsgContent( self, msgID ) :
		"""
		������ϢID����ȡƵ����ɫ����Ϣ����
		"""
		for cnID, cn in self.__channels.items() :
			msg = cn[1].get( msgID, None )
			if msg is not None :
				return msg, cn[0]
		tmpMsg = self.__tmpInvalidMsg.get( msgID, None )
		if tmpMsg is not None :
			del self.__tmpInvalidMsg[ msgID ]
			return tmpMsg[0], tmpMsg[1]
		ERROR_MSG( "Can't find message by ID %d." % msgID )
		return "", ( 255,255,255,255 )

	# -------------------------------------------------
	def __getTimePrefix( self ) :
		"""
		��ȡʱ��ǰ׺
		"""
		return time.strftime( "[%y-%m-%d %H:%M:%S]", time.localtime() )

	def __getTextObj( self ) :
		"""
		��ȡ���õ��ı��ֶζ���
		"""
		if len( self.__usedTextObj ) > 0 :
			return self.__usedTextObj.pop( 0 )
		pyText = CSRichText()
		pyText.opGBLink = True
		pyText.maxWidth = self.__pyMsgPanel.width
		return pyText

	def __addMsgToPanel( self, text, color ) :
		"""
		��Ϣֱ���������ϼ�
		"""
		pyText = self.__getTextObj()
		pyText.foreColor = color
		pyText.text = text
		scroll = self.__pyMsgPanel.scroll
		maxScroll = self.__pyMsgPanel.maxScroll
		self.__pyMsgPanel.addItem( pyText )
		offset = max( pyText.height, pyText.lineHeight * 2 )
		if maxScroll - scroll <= offset :						# ���������λ������£��򱣳ָ�λ��
			self.__pyMsgPanel.scroll = self.__pyMsgPanel.maxScroll
		scroll = self.__pyMsgPanel.scroll
		maxScroll = self.__pyMsgPanel.maxScroll

	def __checkCombatMsgOverflow( self ) :
		"""
		���ս����Ϣ��������
		"""
		combatMsg = self.__channels[self.__COMBAT_CNID]
		overCount = len( combatMsg[1] ) - self.__COMBAT_MAX_COUNT
		msgIDs = combatMsg[1].keys()
		while overCount > 0 :
			msgID = msgIDs.pop( 0 )
			overText = combatMsg[1].pop( msgID )
			if msgID in self.__addingMsgIDs :
				self.__tmpInvalidMsg[ msgID ] = ( overText, combatMsg[0] )
			if msgID in self.__panelMsgIDs :					# ��¼�´���Ϣ�ڵ�ǰ�����ϵ�λ��
				index = self.__panelMsgIDs.index( msgID )
				self.__overflowMsg[ msgID ] = index
			overCount -= 1

	def __checkChatMsgOverflow( self ) :
		"""
		����ս����Ϣ��������
		"""
		chatCNs = []
		overCount = -self.__CHAT_MAX_COUNT
		for cnID, cn in self.__channels.items() :
			if cnID == self.__COMBAT_CNID : continue
			chatCNs.append( cn )
			overCount += len( cn[1] )
		while overCount > 0 :
			oldestCNMap = {}
			for msgCN in chatCNs :
				if len( msgCN[1] ) < 1 : continue
				oldestCNMap[ msgCN[1].keys()[0] ] = msgCN
			oldestMsgID = min( oldestCNMap )
			overCN = oldestCNMap[oldestMsgID]
			overText =  overCN[1].pop( oldestMsgID )			# �Ƴ���Ϣ
			if oldestMsgID in self.__addingMsgIDs :				# ������Ϣ��׼���������ϼӣ�������Ϣ����
				self.__tmpInvalidMsg[ oldestMsgID ] = ( overText, overCN[0] )
			if oldestMsgID in self.__panelMsgIDs :				# ��¼�´���Ϣ�ڵ�ǰ�����ϵ�λ��
				index = self.__panelMsgIDs.index( oldestMsgID )
				self.__overflowMsg[ oldestMsgID ] = index
			overCount -= 1

	def __removeOverflowMsg( self ) :
		"""
		�Ƴ����涥��ָ����������Ϣ
		"""
		scroll = int( self.__pyMsgPanel.scroll )
		maxScroll = int( self.__pyMsgPanel.maxScroll )
		bottom = maxScroll
		decHeight = 0
		pyMsgItems = self.__pyMsgPanel.pyItems
		for msgID, msgIndex in self.__overflowMsg.iteritems() :		# �Ƴ��������Ϣ
			if msgID in self.__addingMsgIDs :					# ����������Ϣ��û��ӵ�������
				self.__addingMsgIDs.remove( msgID )
				del self.__tmpInvalidMsg[ msgID ]
				continue
			pyMsgItem = pyMsgItems[ msgIndex ]
			bottom = min( bottom, pyMsgItem.bottom )
			decHeight += pyMsgItem.height
			self.__pyMsgPanel.removeItem( pyMsgItem )
			pyMsgItem.text = ""
			self.__usedTextObj.append( pyMsgItem )
		self.__pyMsgPanel.layoutItems()
		if scroll != maxScroll and bottom <= scroll :			# �������������λ������£���������ϴ����鿴���ݵ�λ��
			self.__pyMsgPanel.scroll -= decHeight
		self.__overflowMsg = {}

	def __clearPanel( self ) :
		"""
		�����Ϣ���
		"""
		pyMsgItems = self.__pyMsgPanel.pyItems
		self.__pyMsgPanel.clearItems()
		self.__pyMsgPanel.maxScroll = 0
		self.__overflowMsg = {}
		for pyMsg in pyMsgItems :
			if pyMsg in self.__usedTextObj : continue
			pyMsg.text = ""
			self.__usedTextObj.append( pyMsg )

	def __clearMessage( self ) :
		"""
		���������Ϣ
		"""
		self.__clearPanel()
		self.__usedTextObj = []
		self.__panelMsgIDs = []
		self.__addingMsgIDs = []
		self.__tmpInvalidMsg = {}
		self.__msgCounter = 0
		for cn in self.__channels.values() :
			cn[1].clear()

	# -------------------------------------------------
	def __onReceiveMessage( self, channel, spkID, spkName, msg, *args ) :
		"""
		���յ�Ƶ����Ϣ
		@param		channel	: Ƶ��OBJ
		@param		spkID 	: �����ߵ�entity id
		@param		spkName	: ����������
		@param		msg		: ��Ϣ���ݣ�������Ƶ��ǰ׺��
		"""
		msgCN = self.__channels.get( channel.id, None )
		if msgCN is None : return
		self.__msgCounter += 1										# ��Ϣ����������
		msg = channel.formatMsg( spkID, spkName, msg, *args )
		timePrefix = self.__getTimePrefix()
		msg = timePrefix + msg
		color = channel.color
		if len( color ) == 3 : color = tuple( color ) + ( 255, )
		msgCN[1][ self.__msgCounter ] = msg
		msgCN[0] = color
		if channel.id == self.__COMBAT_CNID :						# ������յ���ս����Ϣ
			self.__checkCombatMsgOverflow()							# ����ս����Ϣ��������
		else :														# ����
			self.__checkChatMsgOverflow()							# ���������Ϣ��������

	def __setToDefaultChannels( self ) :
		"""
		��ǰ��ѡƵ������ΪĬ��ֵ
		"""
		self.__currSelChannels = set([								# ���ߺ���������ΪĬ��Ƶ��
			csdefine.CHAT_CHANNEL_PERSONAL,							# ����
		  	csdefine.CHAT_CHANNEL_TEAM,								# ����
		  	csdefine.CHAT_CHANNEL_TONG,								# ���
		  	csdefine.CHAT_CHANNEL_WHISPER,							# ˽��
		  	csdefine.CHAT_CHANNEL_MESSAGE,							# ��Ϣ
		])


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onLeaveWorld( self ) :
		self.__clearMessage()
		self.__shutdownRefresh()
		self.__setToDefaultChannels()
		self.__savePath = ""
		self.hide()

	def onEnterWorld( self ) :
		accountName = rds.gameMgr.getCurrAccountInfo()["accountName"]	# ��ǰ�˺���
#		roleName = BigWorld.player().getName()							# ��ǰ��ɫ��
		self.__savePath = "account/%s/chatlogs/" % accountName
		self.__clearMessage()

	def show( self ) :
		Window.show( self )
		self.__refreshEfficient()
