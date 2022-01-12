# -*- coding: gb18030 -*-

# $Id: RoleChat.py,v 1.17 2008-08-30 09:03:04 huangyongwei Exp $
"""
implement broadcast receiver for player

2009.03.28 : writen by huangyongwei
"""

import weakref
import csdefine
import WordsProfanity
import event.EventCenter as ECenter
from cscollections import MapList
from ChatFacade import chatFacade, emotionParser
from guis import *
from guis.common.Window import Window
from guis.tooluis.CSRichText import CSRichText
from guis.common.FrameEx import VFrameEx

class Receiver( Window ) :
	__cc_initialized  = False
	__cc_textures = {}
	__cc_textures[csdefine.CHAT_CHANNEL_WELKIN_YELL] = ( "", "", "", "", "" )	# 天音背景贴图
	__cc_textures[csdefine.CHAT_CHANNEL_TUNNEL_YELL] = ( "", "", "", "", "" )	# 地音背景贴图

	__cc_prefies = {}
	__cc_prefies[csdefine.CHAT_CHANNEL_WELKIN_YELL] = "[%s]: @B%s"
	__cc_prefies[csdefine.CHAT_CHANNEL_TUNNEL_YELL] = "[%s]: @B%s"

	__cc_delay_time = 8.0						# 窗口显示时间

	def __init__( self, pyBinder ) :
		wnd = GUI.load( "guis/general/chatwindow/rolebroadcaster/receiver/golden_wnd.gui" )
		if not self.__cc_initialized :
			Receiver.__cc_initialized = True
			self.__cc_textures[csdefine.CHAT_CHANNEL_WELKIN_YELL] = \
				wnd.elements['frm_t'].texture, wnd.elements['frm_b'].texture, wnd.elements['frm_bg'].texture
			tunnelWnd = GUI.load( "guis/general/chatwindow/rolebroadcaster/receiver/argent_wnd.gui" )
			self.__cc_textures[csdefine.CHAT_CHANNEL_TUNNEL_YELL] = \
				tunnelWnd.elements['frm_t'].texture, tunnelWnd.elements['frm_b'].texture, tunnelWnd.elements['frm_bg'].texture
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.activable_ = False
		self.movable_ = False
		self.posZSegment = ZSegs.L2
		self.escHide_ = False
		self.h_dockStyle = "RIGHT"
		self.v_dockStyle = "BOTTOM"
		self.focus = False
		self.addToMgr()

		self.__pyBinder = pyBinder									# 注意：这里产生了交叉引用，但是目前 pyReceiver 是不需要释放的对象，因此不做弱引用了

		self.__pyWnd = 	VFrameEx(wnd)

		self.__pyTPMsg = CSRichText(wnd.msgPanel)
		self.__fader = wnd.fader
		self.__fader.speed = 0.0
		self.__fader.value = 0
		self.__fader.reset()

		self.__mapChannel = csdefine.CHAT_CHANNEL_WELKIN_YELL		# 当前显示的频道
		self.__delayCBID = 0


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __resetTexture( self, channelID ) :
		"""
		根据频道更换贴图
		"""
		wnd = self.getGui()
		frm_t, frm_b, frm_bg = self.__cc_textures[channelID]
		wnd.elements['frm_t'].texture = frm_t
		wnd.elements['frm_b'].texture = frm_b
		wnd.elements['frm_bg'].texture = frm_bg

	# -------------------------------------------------
	def __delay( self ) :
		self.__fader.value = 0
		self.__delayCBID = BigWorld.callback( self.__fader.speed, self.hide )
		self.__pyBinder.onMessageHid( self )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def showMessage( self, channelID, speaker, msg ) :
		"""
		显示广播信息
		"""
		self.__mapChannel = channelID
		self.__resetTexture( channelID )
		self.__pyTPMsg.text = self.__cc_prefies[channelID] % ( speaker, msg )
		self.__pyWnd.height = min(self.__pyTPMsg.height + 30,110)

		self.show()



	def isShowwing( self ) :
		"""
		是否处于显示消息状态
		"""
		return self.__fader.value > 0

	def getMapChannel( self ) :
		"""
		获取当前显示的频道
		"""
		return self.__mapChannel

	# -------------------------------------------------
	def onLeaveWorld( self ) :
		self.hide()

	def show( self ) :
		Window.show( self )
		self.__fader.value = 1.0
		BigWorld.cancelCallback( self.__delayCBID )
		self.__delayCBID = BigWorld.callback( self.__cc_delay_time, self.__delay )

	def hide( self ) :
		BigWorld.cancelCallback( self.__delayCBID )
		Window.hide( self )

	def isMouseHit( self ) :
		return False


# --------------------------------------------------------------------
# implement receiver manager
# --------------------------------------------------------------------
class Receivers( object ) :
	__cc_receivers		= 2											# 消息窗口数量

	def __init__( self ) :
		self.__pyReceivers = [Receiver( self ) \
			for i in xrange( self.__cc_receivers )]					# 消息接收窗口

		self.__msgs = MapList()										# 消息队列
		self.__msgs[csdefine.CHAT_CHANNEL_WELKIN_YELL] = []			# 天音消息队列
		self.__msgs[csdefine.CHAT_CHANNEL_TUNNEL_YELL] = []			# 地音消息队列

		self.__showed = MapList()									# 频道状态( 显示的消息数量 )
		self.__showed[csdefine.CHAT_CHANNEL_WELKIN_YELL] = 0		# 初始为未显示状态
		self.__showed[csdefine.CHAT_CHANNEL_TUNNEL_YELL] = 0

		self.__triggers = {}
		self.__registerTriggers()

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		chatFacade.bindChannelHandler( csdefine.CHAT_CHANNEL_WELKIN_YELL, self.__onReceiveWelkin )
		chatFacade.bindChannelHandler( csdefine.CHAT_CHANNEL_TUNNEL_YELL, self.__onReceiveTunnel )
		self.__triggers["EVT_ON_ROLE_LEAVE_WORLD"] = self.onLeaveWorld
		for trigger in self.__triggers :
			ECenter.registerEvent( trigger, self )

	# -------------------------------------------------
	def __layoutReceivers( self ) :
		"""
		重新排列所有
		"""
		bottom = ruisMgr.quickBar.top - 2
		for pyReceiver in self.__pyReceivers :
			if pyReceiver.isShowwing :
				pyReceiver.bottom = bottom
				bottom = pyReceiver.top

	# ---------------------------------------
	def __getFreeReceivers( self ) :
		"""
		获取空闲的消息窗口
		"""
		for pyReceiver in self.__pyReceivers :
			if not pyReceiver.isShowwing() :
				return pyReceiver
		return None

	def __showMessage( self ) :
		"""
		显示一条地音消息
		"""
		pyReceiver = self.__getFreeReceivers()				# 获取一个空闲窗口
		if pyReceiver is None : return

		# 优先显示当前没有显示的频道
		for channelID, count in self.__showed.items() :
			if count > 0 : continue
			if len( self.__msgs[channelID] ) :
				speaker, msg = self.__msgs[channelID].pop( 0 )
				self.__showed[channelID] += 1
				pyReceiver.showMessage( channelID, speaker, msg )
				return

		# 再显示有队列中有等候消息的频道
		for channelID, msgs in self.__msgs.items() :
			if not len( msgs ) : continue
			speaker, msg = msgs.pop( 0 )
			self.__showed[channelID] += 1
			pyReceiver.showMessage( channelID, speaker, msg )
			return

	# -------------------------------------------------
	def __onReceiveWelkin( self, channel, spkID, spkName, msg, statusID = None ) :
		"""
		收到天音
		"""
		if not rds.viewInfoMgr.getSetting( "chat", "welkinAndTunel" ) : return			# 设置为不显示天音弹窗则直接退出
		self.__msgs[csdefine.CHAT_CHANNEL_WELKIN_YELL].append( ( spkName, msg ) )
		self.__showMessage()
		self.__layoutReceivers()

	def __onReceiveTunnel( self, channel, spkID, spkName, msg, statusID = None ) :
		"""
		接收地音
		"""
		if not rds.viewInfoMgr.getSetting( "chat", "welkinAndTunel" ) : return			# 设置为不显示地音弹窗则直接退出
		self.__msgs[csdefine.CHAT_CHANNEL_TUNNEL_YELL].append( ( spkName, msg ) )
		self.__showMessage()
		self.__layoutReceivers()


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self, role ) :
		if role != BigWorld.player() :
			return
		for channelID in self.__msgs :
			self.__msgs[channelID] = []
		for channelID in self.__showed :
			self.__showed[channelID] = 0

	# -------------------------------------------------
	def onMessageHid( self, pyReceiver ) :
		"""
		当某个消息窗口将要关闭时调用
		"""
		channelID = pyReceiver.getMapChannel()
		self.__showed[channelID] -= 1
		self.__showMessage()
		self.__layoutReceivers()
