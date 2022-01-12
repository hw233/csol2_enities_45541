# -*- coding: gb18030 -*-
#
# $Id: MessagePanel.py,v 1.10 2008-08-30 09:05:30 huangyongwei Exp $

"""
implement panel for showing chating message

2007/04/18: writen by huangyongwei
2008/04/02: rewriten by huangyongwei ( new version )
2009/04/06: rewriten by huangyongwei:
			将系统信息合整到一个聊天框中分页显示
"""


import time
from guis import *
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ScrollPanel import VScrollPanel
from guis.general.chatwindow.channelcolorsetter.ColorSetter import ColorSetter
import csdefine

FOMAT_CHANNELS = [ csdefine.CHAT_CHANNEL_SYSTEM,
		csdefine.CHAT_CHANNEL_COMBAT,
		csdefine.CHAT_CHANNEL_PERSONAL,
		csdefine.CHAT_CHANNEL_MESSAGE,
		csdefine.CHAT_CHANNEL_SC_HINT,
		csdefine.CHAT_CHANNEL_MSGBOX,
		csdefine.CHAT_CHANNEL_SYSBROADCAST,
		csdefine.CHAT_CHANNEL_NPC_SPEAK,
		csdefine.CHAT_CHANNEL_NPC_TALK,
		]

class MSGPanel( VScrollPanel ) :
	__cc_max_count		= 50						# 最多保留的消息条数
	__cc_vs_duration	= 120						# 持续显示时间
	__cc_paste_interval = 0.1						# 消息刷新间隔

	def __init__( self, panel, sbar ) :
		VScrollPanel.__init__( self, panel, sbar )
		self.mouseScrollFocus = True
		self.pySBar.v_dockStyle = "VFILL"
		self.pySBar.h_dockStyle = "RIGHT"
		self.pySBar.onLMouseDown.bind( self.__onSBarLMouseDown )
		self.skipScroll = False
		self.perScroll = 32							# 单位滚动值
		self.pyRichs_ = []							# 存放所有消息 CSRichText
		self.__persistCBIDs = {}					# 持续显示 callback ID
		self.__allPersistsCBID = 0					# 全部重新持续显示延时 callback ID
		self.__widthChangedDelayCBID = 0			# 宽度改变时，延时处理消息重排 callback ID
		self.__msgsBuffer = []						# 消息缓冲
		self.__pasteCBID = 0						# 缓冲时间到达时，添加消息的 callback ID


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		产生控件事件
		"""
		VScrollPanel.generateEvents_( self )
		self.__onLinkMessageLClick = self.createEvent_( "onLinkMessageLClick" )
		self.__onLinkMessageRClick = self.createEvent_( "onLinkMessageRClick" )

	@property
	def onLinkMessageLClick( self ) :
		"""
		左键点击某个超链接消息时被触发
		"""
		return self.__onLinkMessageLClick

	@property
	def onLinkMessageRClick( self ) :
		"""
		右键点击某个超链接消息时被触发
		"""
		return self.__onLinkMessageRClick


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __flushWidth( self ) :
		"""
		消息板面宽度改变时被调用
		"""
		self.__cancelAllPersists()
		width = self.width
		key = self.__generatePersistKey()
		def fn( pyRich ) :
			pyRich.maxWidth = width
			pyRich.detectKey = key
			pyRich.visible = True
		self.__layoutItems( fn )
		self.scroll = self.maxScroll
		cbid = BigWorld.callback( self.__cc_vs_duration, \
			Functor( self.__vsPersistArrived, key, self.pyRichs_ ) )	# 这里直接用 __repersistAll 的原因是避免再循环一次
		self.__persistCBIDs[key] = cbid

	def __flushHeight( self ) :
		"""
		消息板面高度改变时被调用
		"""
		self.__cancelAllPersists()
		key = self.__generatePersistKey()
		def fn( pyRich ) :
			pyRich.detectKey = key
			pyRich.visible = True
		self.__layoutItems( fn )
		self.scroll = self.maxScroll
		cbid = BigWorld.callback( self.__cc_vs_duration, \
			Functor( self.__vsPersistArrived, key, self.pyRichs_ ) )	# 这里直接用 __repersistAll 的原因是避免再循环一次
		self.__persistCBIDs[key] = cbid

	# -------------------------------------------------
	def __getMSGRich( self ) :
		"""
		获取一个消息 CSRichText
		"""
		if len( self.pyRichs_ ) >= self.__cc_max_count :
			pyRich = self.pyRichs_.pop( 0 )
			pyRich.visible = True
			return pyRich
		pyRich = CSRichText()
		pyRich.opGBLink = True
		self.addPyChild( pyRich )
		pyRich.onComponentLClick.bind( self.onLinkMessageLClick_ )
		pyRich.onComponentRClick.bind( self.onLinkMessageRClick_ )
		pyRich.maxWidth = self.width
		return pyRich

	def __layoutItems( self, fn = None ) :
		"""
		重新设置所有消息的位置
		"""
		top = 0
		for pyRich in self.pyRichs_ :
			if fn : fn( pyRich )
			pyRich.top = top
			top = pyRich.bottom
		if top < self.height :							# 说明消息窗口可以显示完所有消息
			bottom = self.height
			for pyRich in reversed( self.pyRichs_ ) :
				pyRich.bottom = bottom
				bottom = pyRich.top
			self.maxScroll = 0
		else :
			self.maxScroll = top - self.height

	# -------------------------------------------------
	def __generatePersistKey( self ) :
		"""
		生成一个持续显示键
		"""
		key = 0
		while True :
			if key not in self.__persistCBIDs :
				return key
			key += 1

	def __vsPersistArrived( self, key, pyRichs ) :
		"""
		隐藏时间到达
		"""
		self.__persistCBIDs.pop( key )
		for pyRich in pyRichs :
			if pyRich.detectKey == key :
				pyRich.visible = False

	def __vsPersist( self, pyRichs ) :
		"""
		延迟显示指定消息
		"""
		key = self.__generatePersistKey()
		for pyRich in pyRichs :
			pyRich.visible = True
			pyRich.detectKey = key								# 记录下所有持续侦测键( 因为 CSRichText 是重复利用的 )
		cbid = BigWorld.callback( self.__cc_vs_duration, \
			Functor( self.__vsPersistArrived, key, pyRichs ) )
		self.__persistCBIDs[key] = cbid

	def __cancelAllPersists( self ) :
		"""
		取消所有持续显示
		"""
		for cbid in self.__persistCBIDs.itervalues() :
			BigWorld.cancelCallback( cbid )
		self.__persistCBIDs = {}

	def __repersistAll( self ) :
		"""
		全部消息的延迟隐藏，重新持续显示
		"""
		def vsPersist() :
			self.__cancelAllPersists()
			self.__vsPersist( self.pyRichs_ )
		BigWorld.cancelCallback( self.__allPersistsCBID )
		self.__allPersistsCBID = BigWorld.callback( 0.3, vsPersist )	# 使用 callback 延时一会再显示的原因是，防止过频地 reset

	# -------------------------------------------------
	def __onSBarLMouseDown( self, mods ) :
		"""
		滚动条被点击时触发
		"""
		self.__repersistAll()

	# -------------------------------------------------
	def __addMessage( self, msg, color ,chid) :
		"""
		添加一条消息
		"""
		scroll = self.maxScroll - self.scroll			# 记下原来的滚动位置
		count = len( self.pyRichs_ )					# 原来的消息数量
		pyRich = self.__getMSGRich()
		decHeight = pyRich.height						# 增加的高度
		if chid not in FOMAT_CHANNELS:
			pyRich.text_axi = ""
		else:
			pyRich.text = ""
		if len( color ) == 3 : color += ( 255,)			# foreColor必须是4个元素，否则CSRichText插件解释时会出错
		pyRich.foreColor = color
		if chid not in FOMAT_CHANNELS:
			pyRich.text_axi = msg
		else:
			pyRich.text = msg
		self.pyRichs_.append( pyRich )

		# 重新调整所有消息的位置
		self.__layoutItems()

		# 添加消息后，原来的滚动位置改变，恢复原来的滚动位置
		gap = 2 * pyRich.lineHeight
		if scroll < max( gap, pyRich.height ) :			# 之前，滚动条是滚到最后的
			self.scroll = self.maxScroll				# 保持在最后位置
		elif count >= self.__cc_max_count :				# 之前，滚动条是滚到中间的,并且消息 CSRichText 已经循环使用
			self.scroll -= decHeight					# 则，保持原来的滚动位置
		self.__vsPersist( [pyRich] )					# 持续显示一段时间
		return pyRich

	# -------------------------------------------------
	def __cacheMessage( self, msg, color, chid ) :
		"""缓冲消息"""
		if len( self.__msgsBuffer ) > self.__cc_max_count :
			self.__msgsBuffer.pop( 0 )
		self.__msgsBuffer.append( ( msg, color, chid ) )
		if self.gui.parent.visible :
			self.startPasting()

	def __pasteMessages( self ) :
		"""粘贴所有缓冲的消息"""
		if len( self.__msgsBuffer ) == 0 :
			self.__pasteCBID = 0
			return
		msg, color, chid = self.__msgsBuffer.pop( 0 )
		pyRich = self.__addMessage( msg, color ,chid)
		pyRich.chid = chid
		self.__pasteCBID = BigWorld.callback( self.__cc_paste_interval, \
												self.__pasteMessages )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMouseScroll_( self, dz ) :
		"""
		鼠标滚轮滚动时被触发
		"""
		VScrollPanel.onMouseScroll_( self, dz )
		self.__repersistAll()
		return True

	# -------------------------------------------------
	def onLinkMessageLClick_( self, pyCom ) :
		"""
		左键点击某个超链接消息时被调用
		"""
		self.onLinkMessageLClick( pyCom )

	def onLinkMessageRClick_( self, pyCom ) :
		"""
		右键点击某个超链接消息时被调用
		"""
		self.onLinkMessageRClick( pyCom )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addChanelMessage( self, channel, msg ) :
		"""
		添加一条频道消息
		"""
		chid = channel.id
		color = ColorSetter().getChannelColor( chid )
		self.__cacheMessage( msg, color, chid )
		#pyRich = self.__addMessage( msg, color )
		#pyRich.chid = chid

	def addCommonMessage( self, msg, color ) :
		"""
		显示一条普通消息
		"""
		self.__cacheMessage( msg, color, None )
		#pyRich = self.__addMessage( msg, color )
		#pyRich.chid = None

	def clearMessages( self ) :
		"""
		清除所有消息
		"""
		self.__cancelAllPersists()
		for pyRich in self.pyRichs_ :
			self.delPyChild( pyRich )
		self.pyRichs_ = []
		self.__msgsBuffer = []	# 清空缓冲消息

	def resetMSGColor( self, chcolors ) :
		"""
		重新设置频道颜色
		"""
		for pyRich in self.pyRichs_ :
			color = chcolors.get( pyRich.chid, None )
			if color : pyRich.foreColor = color

	# -------------------------------------------------
	def startPasting( self ) :
		"""开启消息粘贴操作"""
		if self.__pasteCBID == 0 :						# 粘贴没启动
			self.__pasteMessages()						# 粘贴一条消息

	def stopPasting( self ) :
		"""停止粘贴操作"""
		#if self.__pasteCBID != 0 :
		BigWorld.cancelCallback( self.__pasteCBID )
		self.__pasteCBID = 0

	# -------------------------------------------------
	def upScrollHistory( self ) :
		"""
		上翻历史信息（上翻一页）
		"""
		self.scroll -= self.height

	def downScrollHistory( self ) :
		"""
		下翻历史信息（下翻一页）
		"""
		self.scroll += self.height

	def scrollToEnd( self ) :
		"""
		滚动到最新收到的信息处
		"""
		self.scroll = self.maxScroll


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setWidth( self, width ) :
		VScrollPanel._setWidth( self, width )
		BigWorld.cancelCallback( self.__widthChangedDelayCBID )
		self.__widthChangedDelayCBID = BigWorld.callback( 0.5, self.__flushWidth )	# 宽度重排消耗比较大，因此宽度改变频度过高时，延时重排

	def _setHeight( self, height ) :
		VScrollPanel._setHeight( self, height )
		self.__flushHeight()


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	width = property( VScrollPanel._getWidth, _setWidth )
	height = property( VScrollPanel._getHeight, _setHeight )
