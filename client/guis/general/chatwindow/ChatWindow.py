# -*- coding: gb18030 -*-
#
# $Id: ChatWindow.py,v 1.60 2008-09-04 01:00:31 huangyongwei Exp $

"""
imlement chating window

2007/04/16: writen by huangyongwei
2008/04/01: rewriten by huangyongwei( used new texture )
2009/04/08: rewriten by huangyongwei
			��ϵͳ��Ϣ������һ����Ϣ���մ��ڵ�������ͬ��ҳ��
			ϸ���˸��������ְ��
"""

import csol
import csdefine
from LabelGather import labelGather
from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.RootGUI import RootGUI
from guis.common.WndResizer import WndResizer
from guis.controls.Button import Button
from guis.controls.ContextMenu import ContextMenu
from guis.controls.ContextMenu import DefMenuItem
from guis.general.chatwindow.mainwnd.MSGReceiver import MSGReceiver
from guis.general.chatwindow.playmatechat.PLMChatMgr import plmChatMgr
from guis.general.chatwindow.mainwnd.FuncBar import FuncBar
from guis.general.chatwindow.ChatLogViewer import ChatLogViewer
from guis.general.chatwindow.rolebroadcaster.Sender import Sender as BCTSender
from SYSBroadcaster import SYSBroadcaster

# --------------------------------------------------------------------
# implement window class
# --------------------------------------------------------------------
class ChatWindow( RootGUI ) :
	__cc_width_range		= ( 300, 700 )
	__cc_height_range		= ( 210, 600 )

	def __init__( self ) :
		wnd = GUI.load( "guis/general/chatwindow/mainwnd/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		self.h_dockStyle = "LEFT"
		self.v_dockStyle = "BOTTOM"
		self.focus = False
		self.posZSegment = ZSegs.L4													# ���������ŵ�����棬���ڸ���������
		self.activable_ = True
		self.escHide_ = False
		self.__triggers = {}
		self.__registerTriggers()
		self.__clipCBID = 0

		self.pySYSBroadcaster_ = SYSBroadcaster()									# ϵͳ�㲥
		self.pySYSBroadcaster_.addToMgr()

		self.__pyPnlFunc = PyGUI( wnd.pnlMsg )
		self.__pyPnlFunc.h_dockStyle = "HFILL"
		self.__pyPnlFunc.v_dockStyle = "VFILL"

		self.pyReceiver_ = MSGReceiver( wnd.pnlMsg.tcMSG, self )					# ��Ϣ������
		self.pyReceiver_.h_dockStyle = "HFILL"
		self.pyReceiver_.v_dockStyle = "VFILL"
		self.pyReceiver_.onLinkMessageLClick.bind( self.__onMSGLinkLClick )
		self.pyReceiver_.onLinkMessageRClick.bind( self.__onMSGLinkRClick )
		self.pySpeakerMenu_ = SpeakerMenu( self )									# ��Ϣ���Ͷ�������˵�( ָ�� pySpeakerMenu_ Ϊ ChatWindow ����Ԫ�� )

		self.pyFuncBar_ = FuncBar( wnd.pnlMsg.funcBar, self )						# ��Ϣ���͹�����
		self.pyFuncBar_.h_dockStyle = "HFILL"
		self.pyFuncBar_.v_dockStyle = "BOTTOM"

		self.pyBCTCaster_ = BCTSender()												# �㲥����

		self.pyBtns_ = {}															# ��Ű�ťʵ��
		self.__initiButtons( wnd )													# ��ʼ�����й��ܰ�ť

		boards = {}
		boards["r"] = wnd.pnlMsg.resizeHit_r
		boards["t"] = wnd.pnlMsg.resizeHit_t
		boards["rt"] = wnd.pnlMsg.resizeHit_rt
		self.__pyWndResizer = WndResizer( self, boards )
		self.__pyWndResizer.setWidthRange( self.__cc_width_range )
		self.__pyWndResizer.setHeightRange( self.__cc_height_range )
		self.__pyWndResizer.onBeginResized.bind( self.__onBeginResize )

		self.__chatLogViewer = ChatLogViewer()
		self.width = 357											# Ĭ�Ͽ��
		self.__vsFurlExtendBtns()
		self.initsize = self.size

	def __initiButtons( self, wnd ) :
		"""��ʼ�����й��ܰ�ť"""
		def createButton( btn, clickHandler, flag ) :
			pyBtn = Button( btn )
			pyBtn.flag = flag
			pyBtn.setStatesMapping( UIState.MODE_R4C1 )
			pyBtn.onLClick.bind( clickHandler )
			pyBtn.onMouseEnter.bind( self.__onBtnMouseEnter )
			pyBtn.onMouseLeave.bind( self.__onBtnMouseLeave )
			pyBtn.v_dockStyle = "BOTTOM"
			self.pyBtns_[flag] = pyBtn
		createButton( wnd.btnHistory, self.__onHistyoryClick, "history" )
		createButton( wnd.btnSetting, self.__onSettingClick, "setting" )
		createButton( wnd.btnBroadcast, self.__onBroadcaseClick, "broadcast" )
		createButton( wnd.btnSetChns, self.__onSetChnsClick, "set_chns" )
		createButton( wnd.btnUp, self.__onUpClick, "scroll_up" )
		createButton( wnd.btnDown, self.__onDownClick, "scroll_down" )
		createButton( wnd.btnToEnd, self.__onToEndClick, "scroll_end" )
		createButton( wnd.btnExtend, self.__onExtendClick, "extend" )
		createButton( wnd.btnFurl, self.__onFurlClick, "furl" )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_FENGQI_ON_ENTER"] = self.__onEnterFengQi
		self.__triggers["EVT_ON_FENGQI_ON_EXIT"] = self.__onExitFengQi
		self.__triggers["EVT_ON_PLAYER_SWITCH_FENGQI"] = self.__onSwitchFengQiChat
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )

	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( eventMacro, self )
	
	def __onEnterFengQi( self, role ):
		"""
		����ҹս����,���������
		"""
		self.__onFurlClick()
		self.pyBtns_["extend"].enable = False
	
	def __onExitFengQi( self, role ):
		"""
		����ҹս����,չ�������
		"""
		self.__onExtendClick()
		self.pyBtns_["extend"].enable = True

	def __onSwitchFengQiChat( self, unLocked ):
		"""
		����/���������
		"""
		if unLocked:
			self.__onExtendClick()
		else:
			self.__onFurlClick()
		self.pyBtns_["extend"].enable = unLocked
			
	def __onMSGLinkLClick( self, pyCom ) :
		"""
		��������Ϣ�ϵĳ�����ʱ������
		"""
		if pyCom.linkMark.startswith( "viewRoleInfo:" ) :				# �������ʾ�����Ϣ���򷵻�
			mark, name = pyCom.linkMark.split( ":" )
			player = BigWorld.player()
			if name == player.getName() : return						# ������������ұ����򷵻�
			if BigWorld.isKeyDown( KEY_LALT ) :
				player.chat_requireRoleInfo( name )						# ���뷢��������������Ϣ
			else :														# ������������Ϊ˽�Ķ���
				self.pyFuncBar_.whisperTo( name )						# ������������

	def __onMSGLinkRClick( self, pyCom ) :
		"""
		�Ҽ������Ϣ�ϵĳ�����ʱ������
		"""
		if pyCom.linkMark.startswith( "viewRoleInfo:" ) :
			mark, name = pyCom.linkMark.split( ":" )
			self.pySpeakerMenu_.tmpBindName = name
			self.pySpeakerMenu_.popup( name )

	def __onHistyoryClick( self ) :
		"""
		����ʷ��¼����
		"""
		if self.__chatLogViewer.visible :
			self.__chatLogViewer.hide()
		else :
			self.__chatLogViewer.show()

	def __onSettingClick( self ) :
		"""
		�����ò˵�
		"""
		pyBtn = self.pyBtns_["setting"]
		pos = ( pyBtn.rightToScreen, pyBtn.topToScreen )
		self.pyReceiver_.showSettingMenu( pos )

	def __onBroadcaseClick( self ) :
		"""
		�򿪹㲥�༭����
		"""
		if self.pyBCTCaster_.visible :
			self.pyBCTCaster_.hide()
		else :
			self.pyBCTCaster_.show()

	def __onSetChnsClick( self ) :
		"""
		��Ƶ�����ý���
		"""
		self.pyReceiver_.showChannelFilter()

	def __onUpClick( self ) :
		"""
		��Ϣ���Ϲ���
		"""
		self.pyReceiver_.upScrollHistory()

	def __onDownClick( self ) :
		"""
		��Ϣ���¹���
		"""
		self.pyReceiver_.downScrollHistory()

	def __onToEndClick( self ) :
		"""
		��Ϣ����������
		"""
		self.pyReceiver_.scrollMSGToEnd()

	def __onExtendClick( self ) :
		"""
		չ����Ϣ����
		"""
		self.__pyPnlFunc.visible = True
		self.__pyPnlFunc.gui.shader_clip.value = 1
		BigWorld.cancelCallback( self.__clipCBID )
		self.__vsFurlExtendBtns()

	def __onFurlClick( self ) :
		"""
		������Ϣ����
		"""
		clipShader = self.__pyPnlFunc.gui.shader_clip
		clipShader.value = 0
		self.__clipCBID = BigWorld.callback( clipShader.speed, self.__onHidePnlFunc )
		self.__vsFurlExtendBtns()

	def __onHidePnlFunc( self ) :
		"""
		������Ϣ����Ļص�
		"""
		self.__pyPnlFunc.visible = False

	def __vsFurlExtendBtns( self ) :
		"""
		��ʾ/����������ť
		"""
		self.pyBtns_["furl"].visible = not self.__isFurl()
		self.pyBtns_["extend"].visible = self.__isFurl()

	# -------------------------------------------------
	def __onBeginResize( self, pyBoard ) :
		"""
		��ʼ�ı��Сʱ������
		"""
		self.pyFuncBar_.showBar()

	def __isFurl( self ) :
		return self.__pyPnlFunc.gui.shader_clip.value == 0

	def __onBtnMouseEnter( self, pyBtn ) :
		"""
		�����밴ť
		"""
		tips = labelGather.getText( "ChatWindow:main", pyBtn.flag )
		toolbox.infoTip.showToolTips( pyBtn, tips )

	def __onBtnMouseLeave( self ) :
		"""
		����뿪��ť
		"""
		toolbox.infoTip.hide()

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )
		
	def onEnterWorld( self ) :
		RootGUI.onEnterWorld( self )
		self.pyReceiver_.onEnterWorld()
		self.pyFuncBar_.onEnterWorld()
		self.size = self.initsize  		#ÿ�ε�½��Ϸʱ����Ϊԭʼ��С
		self.__onExtendClick()
		self.show()

	def onLeaveWorld( self ) :
		RootGUI.onLeaveWorld( self )
		self.hide()
		self.pyReceiver_.onLeaveWorld()
		self.pyFuncBar_.onLeaveWorld()

	# -------------------------------------------------
	def isMouseHit( self ) :
		if self.__isFurl() :
			for pyBtn in self.pyBtns_.itervalues() :
				if pyBtn.isMouseHit() : return True
			return False
		else :
			return RootGUI.isMouseHit( self )

	def selectChinnelViaID( self, chid ) :
		"""
		�л���idָ����Ƶ��
		"""
		self.pyFuncBar_.selectChinnelViaID( chid )

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	isResizing = property( lambda self : self.__pyWndResizer.isResizing )


# --------------------------------------------------------------------
# implement speaker operation menu
# ָ�� SpeakerMenu Ϊ ChatWindow ����Ԫ�࣬������ɷ��� ChatWidow ���κ����Ժͷ�����
# ԭ����ʵ SpeakerMenu ��ѡ��Ӧ���� ChatWindow ����ӣ�ѡ���¼�ҲӦ���� ChatWindow
# 	  �н��գ���Ϊ�˸�����������˽��˵���ʵ�ֶ�����������˰�����ض��˵�����Ϊ
#	  ChatWindow ����Ԫ���Ǻ���ġ�
# --------------------------------------------------------------------
class SpeakerMenu( ContextMenu ) :
	def __init__( self, pyBinder ) :
		ContextMenu.__init__( self )
		self.__pyBinder = pyBinder															# ע�⣺����ط����������ã���������������ã����ò˵���Ҫ��פ�ڴ棬���û��ϵ
		pyItem1 = DefMenuItem( labelGather.getText( "ChatWindow:tMenu", "miWhisper" ) )		# ˽��
		pyItem1.onLClick.bind( self.__onSMItemWhisper )										# ���⣺����д�����ڽ������ӣ������촰�ڳ�פ�ڴ棬����ɺ��ԣ������û���������������ʱ�ͷŵĶ���Ҫ��Ч��
		pyItem2 = DefMenuItem( labelGather.getText( "ChatWindow:tMenu", "miViewRole" ) )	# �鿴�����Ϣ
		pyItem2.onLClick.bind( self.__onSMItemShowInfo )
		pyItem3 = DefMenuItem( labelGather.getText( "ChatWindow:tMenu", "miCopy" ) )		# �����������
		pyItem3.onLClick.bind( self.__onSMItemCopy )
		self.adds( [pyItem1, pyItem2, pyItem3] )
		self.add( DefMenuItem( style = MIStyle.SPLITTER ) )
		pyItem4 = DefMenuItem( labelGather.getText( "ChatWindow:tMenu", "miInviteBuddy" ) )	# ��Ϊ����
		pyItem4.onLClick.bind( self.__onSMItemMakeFriend )
		pyItem5 = DefMenuItem( labelGather.getText( "ChatWindow:tMenu", "miBlacklist" ) )	# ���������
		pyItem5.onLClick.bind( self.__onSMItemDriveOut )
		pyItem6 = DefMenuItem( labelGather.getText( "ChatWindow:tMenu", "miFriendChat" ) )	#��������
		pyItem6.onLClick.bind( self.__onFriendChat )
		self.adds( [pyItem4, pyItem5, pyItem6] )
		self.add( DefMenuItem( style = MIStyle.SPLITTER ) )
		pyItem7 = DefMenuItem( labelGather.getText( "ChatWindow:tMenu", "miMakeTeam" ) )	# ���
		pyItem7.onLClick.bind( self.__onSMItemInviteTeam )
		pyItem8 = DefMenuItem( labelGather.getText( "ChatWindow:tMenu", "miInviteTong" ) )	# ���������
		pyItem8.onLClick.bind( self.__onSMItemInviteTong )
		self.adds( [pyItem7, pyItem8] )

		self.__mapName = ""


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onSMItemWhisper( self ) :
		"""
		�������������ֽ�����Ϊ˽�Ķ���
		"""
		self.__pyBinder.pyFuncBar_.whisperTo( self.__mapName )

	def __onSMItemShowInfo( self ) :
		"""
		���ݵ������ҵ����֣���ʾ�����Ϣ
		"""
		BigWorld.player().chat_requireRoleInfo( self.__mapName )

	def __onSMItemCopy( self ) :
		"""
		���Ƶ�����������
		"""
		self.__pyBinder.pyFuncBar_.insertMessage( self.__mapName )
		csol.setClipboard( self.__mapName ) # �����ݷŵ�ճ������

	def __onSMItemMakeFriend( self ) :
		"""
		����������������Ϊ�Ѻ�������
		"""
		BigWorld.player().addFriend( self.__mapName )

	def __onSMItemDriveOut( self ) :
		"""
		�������������ּ��������
		"""
		BigWorld.player().addBlacklist( self.__mapName )

	def __onFriendChat( self ):
		"""
		��������
		"""
		plmChatMgr.onOriginateChat( self.__mapName )

	def __onSMItemInviteTeam( self ) :
		"""
		��������������������������
		"""
		BigWorld.player().inviteJoinTeam( self.__mapName )

	def __onSMItemInviteTong( self ) :
		"""
		�������������ֽ������������
		"""
		BigWorld.player().tong_requestJoinByPlayerName( self.__mapName )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def popup( self, name ) :
		self.__mapName = name
		player = BigWorld.player()
		if name == player.getName() :						# ��������������Լ�
			for pyItem in self.pyItems :
				pyItem.visible = False
			self.pyItems[2].visible = True								# ��ֻ���������֣������Ĳ���ȫ��Ϊ��ɫ
		else :
			grade = player.tong_grade
			canCons = player.isJoinTong() and player.tong_checkDutyRights( grade, csdefine.TONG_RIGHT_MEMBER_MANAGE )
			isFriend = name in player.friends
			isBlackList = name in player.blackList
			visibleMap = {4: not isFriend, 5: not isBlackList, 6: isFriend, 9: canCons}
			for index, pyItem in enumerate( self.pyItems ):
				if visibleMap.has_key( index ):
					pyItem.visible = visibleMap[index]
		ContextMenu.popup( self )
