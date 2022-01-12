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
	__cc_textures[csdefine.CHAT_CHANNEL_WELKIN_YELL] = ( "", "", "", "", "" )	# ����������ͼ
	__cc_textures[csdefine.CHAT_CHANNEL_TUNNEL_YELL] = ( "", "", "", "", "" )	# ����������ͼ

	__cc_prefies = {}
	__cc_prefies[csdefine.CHAT_CHANNEL_WELKIN_YELL] = "[%s]: @B%s"
	__cc_prefies[csdefine.CHAT_CHANNEL_TUNNEL_YELL] = "[%s]: @B%s"

	__cc_delay_time = 8.0						# ������ʾʱ��

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

		self.__pyBinder = pyBinder									# ע�⣺��������˽������ã�����Ŀǰ pyReceiver �ǲ���Ҫ�ͷŵĶ�����˲�����������

		self.__pyWnd = 	VFrameEx(wnd)

		self.__pyTPMsg = CSRichText(wnd.msgPanel)
		self.__fader = wnd.fader
		self.__fader.speed = 0.0
		self.__fader.value = 0
		self.__fader.reset()

		self.__mapChannel = csdefine.CHAT_CHANNEL_WELKIN_YELL		# ��ǰ��ʾ��Ƶ��
		self.__delayCBID = 0


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __resetTexture( self, channelID ) :
		"""
		����Ƶ��������ͼ
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
		��ʾ�㲥��Ϣ
		"""
		self.__mapChannel = channelID
		self.__resetTexture( channelID )
		self.__pyTPMsg.text = self.__cc_prefies[channelID] % ( speaker, msg )
		self.__pyWnd.height = min(self.__pyTPMsg.height + 30,110)

		self.show()



	def isShowwing( self ) :
		"""
		�Ƿ�����ʾ��Ϣ״̬
		"""
		return self.__fader.value > 0

	def getMapChannel( self ) :
		"""
		��ȡ��ǰ��ʾ��Ƶ��
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
	__cc_receivers		= 2											# ��Ϣ��������

	def __init__( self ) :
		self.__pyReceivers = [Receiver( self ) \
			for i in xrange( self.__cc_receivers )]					# ��Ϣ���մ���

		self.__msgs = MapList()										# ��Ϣ����
		self.__msgs[csdefine.CHAT_CHANNEL_WELKIN_YELL] = []			# ������Ϣ����
		self.__msgs[csdefine.CHAT_CHANNEL_TUNNEL_YELL] = []			# ������Ϣ����

		self.__showed = MapList()									# Ƶ��״̬( ��ʾ����Ϣ���� )
		self.__showed[csdefine.CHAT_CHANNEL_WELKIN_YELL] = 0		# ��ʼΪδ��ʾ״̬
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
		������������
		"""
		bottom = ruisMgr.quickBar.top - 2
		for pyReceiver in self.__pyReceivers :
			if pyReceiver.isShowwing :
				pyReceiver.bottom = bottom
				bottom = pyReceiver.top

	# ---------------------------------------
	def __getFreeReceivers( self ) :
		"""
		��ȡ���е���Ϣ����
		"""
		for pyReceiver in self.__pyReceivers :
			if not pyReceiver.isShowwing() :
				return pyReceiver
		return None

	def __showMessage( self ) :
		"""
		��ʾһ��������Ϣ
		"""
		pyReceiver = self.__getFreeReceivers()				# ��ȡһ�����д���
		if pyReceiver is None : return

		# ������ʾ��ǰû����ʾ��Ƶ��
		for channelID, count in self.__showed.items() :
			if count > 0 : continue
			if len( self.__msgs[channelID] ) :
				speaker, msg = self.__msgs[channelID].pop( 0 )
				self.__showed[channelID] += 1
				pyReceiver.showMessage( channelID, speaker, msg )
				return

		# ����ʾ�ж������еȺ���Ϣ��Ƶ��
		for channelID, msgs in self.__msgs.items() :
			if not len( msgs ) : continue
			speaker, msg = msgs.pop( 0 )
			self.__showed[channelID] += 1
			pyReceiver.showMessage( channelID, speaker, msg )
			return

	# -------------------------------------------------
	def __onReceiveWelkin( self, channel, spkID, spkName, msg, statusID = None ) :
		"""
		�յ�����
		"""
		if not rds.viewInfoMgr.getSetting( "chat", "welkinAndTunel" ) : return			# ����Ϊ����ʾ����������ֱ���˳�
		self.__msgs[csdefine.CHAT_CHANNEL_WELKIN_YELL].append( ( spkName, msg ) )
		self.__showMessage()
		self.__layoutReceivers()

	def __onReceiveTunnel( self, channel, spkID, spkName, msg, statusID = None ) :
		"""
		���յ���
		"""
		if not rds.viewInfoMgr.getSetting( "chat", "welkinAndTunel" ) : return			# ����Ϊ����ʾ����������ֱ���˳�
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
		��ĳ����Ϣ���ڽ�Ҫ�ر�ʱ����
		"""
		channelID = pyReceiver.getMapChannel()
		self.__showed[channelID] -= 1
		self.__showMessage()
		self.__layoutReceivers()
