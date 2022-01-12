# -*- coding: gb18030 -*-
#
# $Id: ChatWindow.py,v 1.60 2008-09-04 01:00:31 huangyongwei Exp $

"""
imlement chating window

2007/04/16: writen by huangyongwei
2008/04/01: rewriten by huangyongwei( used new texture )
2009/04/08: rewriten by huangyongwei
			将系统消息合整到一个消息接收窗口的两个不同分页中
			细化了各个组件的职能
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
		self.posZSegment = ZSegs.L4													# 将聊天界面放到最后面，不遮盖其它界面
		self.activable_ = True
		self.escHide_ = False
		self.__triggers = {}
		self.__registerTriggers()
		self.__clipCBID = 0

		self.pySYSBroadcaster_ = SYSBroadcaster()									# 系统广播
		self.pySYSBroadcaster_.addToMgr()

		self.__pyPnlFunc = PyGUI( wnd.pnlMsg )
		self.__pyPnlFunc.h_dockStyle = "HFILL"
		self.__pyPnlFunc.v_dockStyle = "VFILL"

		self.pyReceiver_ = MSGReceiver( wnd.pnlMsg.tcMSG, self )					# 消息接收器
		self.pyReceiver_.h_dockStyle = "HFILL"
		self.pyReceiver_.v_dockStyle = "VFILL"
		self.pyReceiver_.onLinkMessageLClick.bind( self.__onMSGLinkLClick )
		self.pyReceiver_.onLinkMessageRClick.bind( self.__onMSGLinkRClick )
		self.pySpeakerMenu_ = SpeakerMenu( self )									# 消息发送对象操作菜单( 指定 pySpeakerMenu_ 为 ChatWindow 的友元类 )

		self.pyFuncBar_ = FuncBar( wnd.pnlMsg.funcBar, self )						# 消息发送功能条
		self.pyFuncBar_.h_dockStyle = "HFILL"
		self.pyFuncBar_.v_dockStyle = "BOTTOM"

		self.pyBCTCaster_ = BCTSender()												# 广播窗口

		self.pyBtns_ = {}															# 存放按钮实例
		self.__initiButtons( wnd )													# 初始化所有功能按钮

		boards = {}
		boards["r"] = wnd.pnlMsg.resizeHit_r
		boards["t"] = wnd.pnlMsg.resizeHit_t
		boards["rt"] = wnd.pnlMsg.resizeHit_rt
		self.__pyWndResizer = WndResizer( self, boards )
		self.__pyWndResizer.setWidthRange( self.__cc_width_range )
		self.__pyWndResizer.setHeightRange( self.__cc_height_range )
		self.__pyWndResizer.onBeginResized.bind( self.__onBeginResize )

		self.__chatLogViewer = ChatLogViewer()
		self.width = 357											# 默认宽度
		self.__vsFurlExtendBtns()
		self.initsize = self.size

	def __initiButtons( self, wnd ) :
		"""初始化所有功能按钮"""
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
		进入夜战凤栖,收起聊天框
		"""
		self.__onFurlClick()
		self.pyBtns_["extend"].enable = False
	
	def __onExitFengQi( self, role ):
		"""
		进入夜战凤栖,展开聊天框
		"""
		self.__onExtendClick()
		self.pyBtns_["extend"].enable = True

	def __onSwitchFengQiChat( self, unLocked ):
		"""
		锁定/解锁聊天框
		"""
		if unLocked:
			self.__onExtendClick()
		else:
			self.__onFurlClick()
		self.pyBtns_["extend"].enable = unLocked
			
	def __onMSGLinkLClick( self, pyCom ) :
		"""
		左键点击消息上的超链接时被触发
		"""
		if pyCom.linkMark.startswith( "viewRoleInfo:" ) :				# 如果是显示玩家信息，则返回
			mark, name = pyCom.linkMark.split( ":" )
			player = BigWorld.player()
			if name == player.getName() : return						# 如果点击的是玩家本身，则返回
			if BigWorld.isKeyDown( KEY_LALT ) :
				player.chat_requireRoleInfo( name )						# 申请发送所点击的玩家信息
			else :														# 将所点击玩家作为私聊对象
				self.pyFuncBar_.whisperTo( name )						# 与点击对象密语

	def __onMSGLinkRClick( self, pyCom ) :
		"""
		右键点击消息上的超链接时被触发
		"""
		if pyCom.linkMark.startswith( "viewRoleInfo:" ) :
			mark, name = pyCom.linkMark.split( ":" )
			self.pySpeakerMenu_.tmpBindName = name
			self.pySpeakerMenu_.popup( name )

	def __onHistyoryClick( self ) :
		"""
		打开历史纪录窗口
		"""
		if self.__chatLogViewer.visible :
			self.__chatLogViewer.hide()
		else :
			self.__chatLogViewer.show()

	def __onSettingClick( self ) :
		"""
		打开设置菜单
		"""
		pyBtn = self.pyBtns_["setting"]
		pos = ( pyBtn.rightToScreen, pyBtn.topToScreen )
		self.pyReceiver_.showSettingMenu( pos )

	def __onBroadcaseClick( self ) :
		"""
		打开广播编辑界面
		"""
		if self.pyBCTCaster_.visible :
			self.pyBCTCaster_.hide()
		else :
			self.pyBCTCaster_.show()

	def __onSetChnsClick( self ) :
		"""
		打开频道设置界面
		"""
		self.pyReceiver_.showChannelFilter()

	def __onUpClick( self ) :
		"""
		消息向上滚动
		"""
		self.pyReceiver_.upScrollHistory()

	def __onDownClick( self ) :
		"""
		消息向下滚动
		"""
		self.pyReceiver_.downScrollHistory()

	def __onToEndClick( self ) :
		"""
		消息滚动到地下
		"""
		self.pyReceiver_.scrollMSGToEnd()

	def __onExtendClick( self ) :
		"""
		展开消息版面
		"""
		self.__pyPnlFunc.visible = True
		self.__pyPnlFunc.gui.shader_clip.value = 1
		BigWorld.cancelCallback( self.__clipCBID )
		self.__vsFurlExtendBtns()

	def __onFurlClick( self ) :
		"""
		收起消息版面
		"""
		clipShader = self.__pyPnlFunc.gui.shader_clip
		clipShader.value = 0
		self.__clipCBID = BigWorld.callback( clipShader.speed, self.__onHidePnlFunc )
		self.__vsFurlExtendBtns()

	def __onHidePnlFunc( self ) :
		"""
		隐藏消息版面的回调
		"""
		self.__pyPnlFunc.visible = False

	def __vsFurlExtendBtns( self ) :
		"""
		显示/隐藏伸缩按钮
		"""
		self.pyBtns_["furl"].visible = not self.__isFurl()
		self.pyBtns_["extend"].visible = self.__isFurl()

	# -------------------------------------------------
	def __onBeginResize( self, pyBoard ) :
		"""
		开始改变大小时被触发
		"""
		self.pyFuncBar_.showBar()

	def __isFurl( self ) :
		return self.__pyPnlFunc.gui.shader_clip.value == 0

	def __onBtnMouseEnter( self, pyBtn ) :
		"""
		鼠标进入按钮
		"""
		tips = labelGather.getText( "ChatWindow:main", pyBtn.flag )
		toolbox.infoTip.showToolTips( pyBtn, tips )

	def __onBtnMouseLeave( self ) :
		"""
		鼠标离开按钮
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
		self.size = self.initsize  		#每次登陆游戏时重置为原始大小
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
		切换至id指定的频道
		"""
		self.pyFuncBar_.selectChinnelViaID( chid )

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	isResizing = property( lambda self : self.__pyWndResizer.isResizing )


# --------------------------------------------------------------------
# implement speaker operation menu
# 指定 SpeakerMenu 为 ChatWindow 的友元类，因此它可访问 ChatWidow 的任何属性和方法。
# 原因：其实 SpeakerMenu 的选项应该在 ChatWindow 中添加，选项事件也应该在 ChatWindow
# 	  中接收，但为了更加清晰，因此将菜单的实现独立出来，因此把这个特定菜单设置为
#	  ChatWindow 的友元类是合理的。
# --------------------------------------------------------------------
class SpeakerMenu( ContextMenu ) :
	def __init__( self, pyBinder ) :
		ContextMenu.__init__( self )
		self.__pyBinder = pyBinder															# 注意：这个地方不用弱引用，将会产生交叉引用，但该菜单需要常驻内存，因此没关系
		pyItem1 = DefMenuItem( labelGather.getText( "ChatWindow:tMenu", "miWhisper" ) )		# 私聊
		pyItem1.onLClick.bind( self.__onSMItemWhisper )										# 主意：这种写法存在交叉链接，但聊天窗口常驻内存，这个可忽略（其他用户，若遇到可能随时释放的对象不要仿效）
		pyItem2 = DefMenuItem( labelGather.getText( "ChatWindow:tMenu", "miViewRole" ) )	# 查看玩家信息
		pyItem2.onLClick.bind( self.__onSMItemShowInfo )
		pyItem3 = DefMenuItem( labelGather.getText( "ChatWindow:tMenu", "miCopy" ) )		# 复制玩家名字
		pyItem3.onLClick.bind( self.__onSMItemCopy )
		self.adds( [pyItem1, pyItem2, pyItem3] )
		self.add( DefMenuItem( style = MIStyle.SPLITTER ) )
		pyItem4 = DefMenuItem( labelGather.getText( "ChatWindow:tMenu", "miInviteBuddy" ) )	# 加为好友
		pyItem4.onLClick.bind( self.__onSMItemMakeFriend )
		pyItem5 = DefMenuItem( labelGather.getText( "ChatWindow:tMenu", "miBlacklist" ) )	# 加入黑名单
		pyItem5.onLClick.bind( self.__onSMItemDriveOut )
		pyItem6 = DefMenuItem( labelGather.getText( "ChatWindow:tMenu", "miFriendChat" ) )	#好友聊天
		pyItem6.onLClick.bind( self.__onFriendChat )
		self.adds( [pyItem4, pyItem5, pyItem6] )
		self.add( DefMenuItem( style = MIStyle.SPLITTER ) )
		pyItem7 = DefMenuItem( labelGather.getText( "ChatWindow:tMenu", "miMakeTeam" ) )	# 组队
		pyItem7.onLClick.bind( self.__onSMItemInviteTeam )
		pyItem8 = DefMenuItem( labelGather.getText( "ChatWindow:tMenu", "miInviteTong" ) )	# 邀请加入帮会
		pyItem8.onLClick.bind( self.__onSMItemInviteTong )
		self.adds( [pyItem7, pyItem8] )

		self.__mapName = ""


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onSMItemWhisper( self ) :
		"""
		将点击的玩家名字将其作为私聊对象
		"""
		self.__pyBinder.pyFuncBar_.whisperTo( self.__mapName )

	def __onSMItemShowInfo( self ) :
		"""
		根据点击的玩家的名字，显示玩家信息
		"""
		BigWorld.player().chat_requireRoleInfo( self.__mapName )

	def __onSMItemCopy( self ) :
		"""
		复制点击的玩家名字
		"""
		self.__pyBinder.pyFuncBar_.insertMessage( self.__mapName )
		csol.setClipboard( self.__mapName ) # 将内容放到粘贴板中

	def __onSMItemMakeFriend( self ) :
		"""
		将点击的玩家名字作为友好友邀请
		"""
		BigWorld.player().addFriend( self.__mapName )

	def __onSMItemDriveOut( self ) :
		"""
		将点击的玩家名字加入黑名单
		"""
		BigWorld.player().addBlacklist( self.__mapName )

	def __onFriendChat( self ):
		"""
		好友聊天
		"""
		plmChatMgr.onOriginateChat( self.__mapName )

	def __onSMItemInviteTeam( self ) :
		"""
		将点击的玩家名字邀请其加入队伍
		"""
		BigWorld.player().inviteJoinTeam( self.__mapName )

	def __onSMItemInviteTong( self ) :
		"""
		将点击的玩家名字接邀请其加入帮会
		"""
		BigWorld.player().tong_requestJoinByPlayerName( self.__mapName )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def popup( self, name ) :
		self.__mapName = name
		player = BigWorld.player()
		if name == player.getName() :						# 如果点击的是玩家自己
			for pyItem in self.pyItems :
				pyItem.visible = False
			self.pyItems[2].visible = True								# 则只允许复制名字，其他的操作全变为灰色
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
