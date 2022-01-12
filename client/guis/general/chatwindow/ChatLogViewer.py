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
		将此接口接口公开
		"""
		self.layoutItems_( startIndex )


class ChatLogViewer( Window ) :

	__REFRESH_INTERVAL = 0.02										# 消息添加间隔
	__CHAT_MAX_COUNT = 400											# 聊天消息最大保存数量
	__COMBAT_MAX_COUNT = 200										# 战斗消息最大保存数量
	__COMBAT_CNID = csdefine.CHAT_CHANNEL_COMBAT

	def __init__( self ) :
		wnd = GUI.load("guis/general/chatwindow/chatlogviewer/wnd.gui")
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.addToMgr( "chatLogViewer" )

		self.__usedTextObj = []										# 保存废弃的字段对象，以便重用
		self.__refreshCBID = 0										# 刷新回调ID，用回调的方法防止刷新过多数据时太卡
		self.__msgCounter = 0 										# 按消息的接收顺序递增

		self.__panelMsgIDs = []										# 界面上所有的消息ID
		self.__tmpInvalidMsg = {}									# 暂存已溢出而正准备往界面上添加的消息内容
		self.__overflowMsg = {}										# 暂存已溢出但当前在界面上显示的消息位置
		self.__addingMsgIDs = []									# 准备界面上添加的消息

		self.__currSelChannels = set()								# 当前所选择的频道
		self.__channels = MapList()									# 聊天消息( 频道颜色, { 消息ID:消息, ... } )
		self.__savePath = ""										# 信息保存路径(默认保存在对应的账号角色目录下)

		self.__setToDefaultChannels()								# 将选择频道设置为默认值
		self.__initChannels()
		self.__initialize( wnd )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		self.__pySaveBtn = HButtonEx( wnd.saveBtn )					# 保存日志按钮
		self.__pySaveBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pySaveBtn.onLClick.bind( self.__saveLog )
		self.__pySaveBtn.isOffsetText = True

		self.__pyRefreshBtn = HButtonEx( wnd.refreshBtn )				# 刷新界面信息按钮
		self.__pyRefreshBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyRefreshBtn.onLClick.bind( self.__onRefreshMsg )
		self.__pyRefreshBtn.isOffsetText = True

		self.__pySelCNBtn = HButtonEx( wnd.selChannelBtn )				# 选择频道按钮
		self.__pySelCNBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pySelCNBtn.onLClick.bind( self.__selChannel )
		self.__pySelCNBtn.isOffsetText = True

		#self.__pyTopBtn = HButtonEx( wnd.topBtn )						# 滚到到顶部按钮
		#self.__pyTopBtn.setExStatesMapping( UIState.MODE_R1C3 )
		#self.__pyTopBtn.onLClick.bind( self.__gotoTop )

		#self.__pyBottomBtn = HButtonEx( wnd.bottomBtn )				# 滚到到底部按钮
		#self.__pyBottomBtn.setExStatesMapping( UIState.MODE_R1C3 )
		#self.__pyBottomBtn.onLClick.bind( self.__gotoBottom )

		self.__pyMsgPanel = ChatLogPanel( wnd.pnl_content.clipPanel, wnd.pnl_content.sbar )
		self.__pyMsgPanel.skipScroll = False

		for chid, channel in chatFacade.channels.items() :			# 绑定接收消息的频道处理函数
			if not channel.setable : continue
			if chid == csdefine.CHAT_CHANNEL_PLAYMATE : continue	# 这里不记录独立窗口聊天消息
			chatFacade.bindChannelHandler( chid, self.__onReceiveMessage )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pySaveBtn, "ChatWindow:ChatLogViewer", "btnSave" )
		labelGather.setPyBgLabel( self.__pyRefreshBtn, "ChatWindow:ChatLogViewer", "btnRefresh" )
		labelGather.setPyBgLabel( self.__pySelCNBtn, "ChatWindow:ChatLogViewer", "btnCNSelect" )
		labelGather.setLabel( self.gui.lbTitle, "ChatWindow:ChatLogViewer", "lbTitle" )

	def __initChannels( self ) :
		"""
		初始化所有需要记录的频道
		"""
		for cnID in chatFacade.channels :
			self.__channels[ cnID ] = [ (255,255,255,255), MapList() ]

	# -------------------------------------------------
	# function
	# -------------------------------------------------
	def __gotoTop( self ) :
		"""
		把滚动条位置设置为顶部
		"""
		self.__pyMsgPanel.scroll = 0

	def __gotoBottom( self ) :
		"""
		把滚动条位置设置为底部
		"""
		self.__pyMsgPanel.scroll = self.__pyMsgPanel.maxScroll

	def __selChannel( self ) :
		"""
		点击选择频道按钮
		"""
		title = labelGather.getText( "ChatWindow:ChatLogViewer", "lbSelCNClew" )
		ChannelFilter().show( title, self.__currSelChannels, self.__onChannelSelected, self )

	def __saveLog( self ) :
		"""
		保存选中的频道消息到本地磁盘
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
				# 聊天记录已成功保存到%s文件中。
				msg = mbmsgs[0x0241] % ( rootPath + filePath.replace( "/", "\\" ) )
				showMessage( msg, "", MB_OK, None, self )
			except IOError, errstr :
				# "保存文件失败！%s"
				showMessage( mbmsgs[0x0242] % errstr, "", MB_OK, None, self )

		def query( result ) :
			if result == RS_YES : saveFile()

		fileExists = csol.resourceExists( filePath )				# 检查文件是否存在
		if fileExists :												# 如果存在则提示冲突
			# 文件%s已存在，是否覆盖？
			msg = mbmsgs[0x0243] % ( rootPath + filePath.replace( "/", "\\" ) )
			showMessage( msg, "", MB_YES_NO, query, self )
		else :
			s = ResMgr.openSection( filePath, True )				# 由于未找到其他方法创建文件夹
			s.save()												# 因此先用这个方法创建文件
			ResMgr.purge( filePath )
			saveFile()

	def __onRefreshMsg( self ) :
		"""
		刷新界面信息
		"""
		self.__refreshEfficient()

	def __onChannelSelected( self, isOK, selChannels ) :
		"""
		选择一个新的频道触发
		"""
		if not isOK : return
		if selChannels == self.__currSelChannels : return
		self.__currSelChannels = selChannels						# 保存选中的频道
		self.__addingMsgIDs = self.__getSelMsgIDs()					# 获取选择的所有频道消息
		self.__panelMsgIDs = self.__addingMsgIDs[:]
		self.__tmpInvalidMsg = {}
		self.__refreshMsg()

	def __shutdownRefresh( self ) :
		if self.__refreshCBID :
			BigWorld.cancelCallback( self.__refreshCBID )
			self.__refreshCBID = 0

	def __refreshMsg( self ) :
		"""
		刷新界面信息
		"""
		self.__shutdownRefresh()									# 停止之前的刷新
		self.__clearPanel()											# 清空消息界面
		self.__addMsgGradual()

	def __refreshEfficient( self ) :
		"""
		使用相对高效的方法刷新界面
		"""
		selMsgIDs = self.__getSelMsgIDs()							# 重设要添加到界面上的消息
		startIndex = 0
		remainMsg = [ i for i in self.__panelMsgIDs \
					if i not in self.__overflowMsg ]
		if len( remainMsg ) > 0 :
			startMsgID = remainMsg[-1]
			startIndex = selMsgIDs.index( startMsgID ) + 1
		self.__panelMsgIDs = selMsgIDs								# 保存当前界面上的所有消息ID
		self.__addingMsgIDs.extend( selMsgIDs[ startIndex : ] )		# 获取新加到界面上的消息ID
		self.__shutdownRefresh()									# 停止之前的刷新
		self.__removeOverflowMsg()									# 移除界面上的溢出消息
		self.__addMsgGradual()

	def __addMsgGradual( self ) :
		"""
		逐个添加消息到界面
		"""
		if len( self.__addingMsgIDs ) == 0 : return
		msgID = self.__addingMsgIDs.pop( 0 )
		msg, color = self.__getMsgContent( msgID )					# 获取消息内容
		self.__addMsgToPanel( msg, color )							# 添加消息到界面
		self.__refreshCBID = BigWorld.callback( self.__REFRESH_INTERVAL, self.__addMsgGradual )

	def __getSelMsgIDs( self ) :
		"""
		获取当前选中频道的所有消息ID
		"""
		selMsgIDs = []
		for channelID in self.__currSelChannels :
			msgCN = self.__channels.get( channelID, ((),[]) )
			selMsgIDs.extend( msgCN[1] )
		selMsgIDs.sort()											# 根据消息ID排序
		return selMsgIDs

	def __getMsgContent( self, msgID ) :
		"""
		根据消息ID，获取频道颜色及消息内容
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
		获取时间前缀
		"""
		return time.strftime( "[%y-%m-%d %H:%M:%S]", time.localtime() )

	def __getTextObj( self ) :
		"""
		获取可用的文本字段对象
		"""
		if len( self.__usedTextObj ) > 0 :
			return self.__usedTextObj.pop( 0 )
		pyText = CSRichText()
		pyText.opGBLink = True
		pyText.maxWidth = self.__pyMsgPanel.width
		return pyText

	def __addMsgToPanel( self, text, color ) :
		"""
		消息直接往界面上加
		"""
		pyText = self.__getTextObj()
		pyText.foreColor = color
		pyText.text = text
		scroll = self.__pyMsgPanel.scroll
		maxScroll = self.__pyMsgPanel.maxScroll
		self.__pyMsgPanel.addItem( pyText )
		offset = max( pyText.height, pyText.lineHeight * 2 )
		if maxScroll - scroll <= offset :						# 如果滚动条位于最底下，则保持该位置
			self.__pyMsgPanel.scroll = self.__pyMsgPanel.maxScroll
		scroll = self.__pyMsgPanel.scroll
		maxScroll = self.__pyMsgPanel.maxScroll

	def __checkCombatMsgOverflow( self ) :
		"""
		检查战斗信息的溢出情况
		"""
		combatMsg = self.__channels[self.__COMBAT_CNID]
		overCount = len( combatMsg[1] ) - self.__COMBAT_MAX_COUNT
		msgIDs = combatMsg[1].keys()
		while overCount > 0 :
			msgID = msgIDs.pop( 0 )
			overText = combatMsg[1].pop( msgID )
			if msgID in self.__addingMsgIDs :
				self.__tmpInvalidMsg[ msgID ] = ( overText, combatMsg[0] )
			if msgID in self.__panelMsgIDs :					# 记录下此消息在当前界面上的位置
				index = self.__panelMsgIDs.index( msgID )
				self.__overflowMsg[ msgID ] = index
			overCount -= 1

	def __checkChatMsgOverflow( self ) :
		"""
		检查非战斗消息的溢出情况
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
			overText =  overCN[1].pop( oldestMsgID )			# 移除消息
			if oldestMsgID in self.__addingMsgIDs :				# 这条消息正准备往界面上加，暂留消息内容
				self.__tmpInvalidMsg[ oldestMsgID ] = ( overText, overCN[0] )
			if oldestMsgID in self.__panelMsgIDs :				# 记录下此消息在当前界面上的位置
				index = self.__panelMsgIDs.index( oldestMsgID )
				self.__overflowMsg[ oldestMsgID ] = index
			overCount -= 1

	def __removeOverflowMsg( self ) :
		"""
		移除界面顶部指定数量的消息
		"""
		scroll = int( self.__pyMsgPanel.scroll )
		maxScroll = int( self.__pyMsgPanel.maxScroll )
		bottom = maxScroll
		decHeight = 0
		pyMsgItems = self.__pyMsgPanel.pyItems
		for msgID, msgIndex in self.__overflowMsg.iteritems() :		# 移除溢出的消息
			if msgID in self.__addingMsgIDs :					# 如果溢出的消息还没添加到界面上
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
		if scroll != maxScroll and bottom <= scroll :			# 如果滚动条不是位于最底下，则滚动到上次所查看内容的位置
			self.__pyMsgPanel.scroll -= decHeight
		self.__overflowMsg = {}

	def __clearPanel( self ) :
		"""
		清空消息面板
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
		清空所有消息
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
		接收到频道消息
		@param		channel	: 频道OBJ
		@param		spkID 	: 发言者的entity id
		@param		spkName	: 发言者名字
		@param		msg		: 消息内容（不包括频道前缀）
		"""
		msgCN = self.__channels.get( channel.id, None )
		if msgCN is None : return
		self.__msgCounter += 1										# 消息计数器增加
		msg = channel.formatMsg( spkID, spkName, msg, *args )
		timePrefix = self.__getTimePrefix()
		msg = timePrefix + msg
		color = channel.color
		if len( color ) == 3 : color = tuple( color ) + ( 255, )
		msgCN[1][ self.__msgCounter ] = msg
		msgCN[0] = color
		if channel.id == self.__COMBAT_CNID :						# 如果接收到了战斗消息
			self.__checkCombatMsgOverflow()							# 则检查战斗消息的溢出情况
		else :														# 否则
			self.__checkChatMsgOverflow()							# 检查聊天消息的溢出情况

	def __setToDefaultChannels( self ) :
		"""
		当前所选频道设置为默认值
		"""
		self.__currSelChannels = set([								# 下线后重新设置为默认频道
			csdefine.CHAT_CHANNEL_PERSONAL,							# 个人
		  	csdefine.CHAT_CHANNEL_TEAM,								# 队伍
		  	csdefine.CHAT_CHANNEL_TONG,								# 帮会
		  	csdefine.CHAT_CHANNEL_WHISPER,							# 私聊
		  	csdefine.CHAT_CHANNEL_MESSAGE,							# 消息
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
		accountName = rds.gameMgr.getCurrAccountInfo()["accountName"]	# 当前账号名
#		roleName = BigWorld.player().getName()							# 当前角色名
		self.__savePath = "account/%s/chatlogs/" % accountName
		self.__clearMessage()

	def show( self ) :
		Window.show( self )
		self.__refreshEfficient()
