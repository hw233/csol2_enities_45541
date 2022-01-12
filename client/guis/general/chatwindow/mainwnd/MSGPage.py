# -*- coding: gb18030 -*-
#
# $Id: tabpage.py,v 1.10 2008-08-30 09:05:30 huangyongwei Exp $

"""
implement tabpage for showing chating message

2009/08/26: writen by huangyongwei
"""

import csdefine
import csconst
import event.EventCenter as ECenter
from ChatFacade import chatFacade
from LabelGather import labelGather
from guis import *
from guis.common.RootGUI import RootGUI
from guis.common.WndResizer import WndResizer
from guis.controls.Control import Control
from guis.controls.TabCtrl import TabPanel
from guis.controls.TabCtrl import TabPage
from MSGTab import MSGTab
from MSGPanel import MSGPanel

class MSGTabPanel( TabPanel ) :
	def onShow( self ) :
		"""版面显示时调用"""
		TabPanel.onShow( self )
		if self.pyTabPage :
			self.pyTabPage.pyMSGPanel.startPasting()

	def onHide( self ) :
		"""版面关闭时调用"""
		TabPanel.onShow( self )
		if self.pyTabPage :
			self.pyTabPage.pyMSGPanel.stopPasting()


class MSGPage( Control, TabPage ) :
	__cc_def_color		= 28, 28, 28, 180		# 默认背景色

	def __init__( self, pyBinder ) :
		pg = GUI.load( "guis/general/chatwindow/mainwnd/tpgmsg.gui" )
		uiFixer.firstLoadFix( pg )
		self.__isInitPages = False				# 标记，防止重复产生两次事件
		Control.__init__( self, pg, pyBinder )
		self.__isInitPages = True
		self.__initialize( pg )
		self.color = self.__cc_def_color

		self.__locked = True					# 是否锁住分页
		self.__docked = True					# 是否处于停靠状态（停靠主窗口）
		self.deletable_ = True					# 是否可以被删除
		self.unlockable_ = False				# 是否可被解锁
		self.defCareCHIDs_ = set()				# 默认接收其消息的频道
		self.__careCHIDs = set()				# 接收其消息的频道（因为每收到消息，都要获取此关注频道，
												# 因此，为了不影响速度，这里设置为公开，但赋值时，请注意，
												# 应该赋予一个 set，而不是 list 或 tuple）

		self.pyFiller_ = None					# 分离时的托盘
		self.__cursorToFillerPos = 0, 0			# 鼠标到 filler 的位置

	def dispose( self ) :
		if self.pyFiller_ :
			self.pyFiller_.dispose()
			self.pyFiller_ = None
		for chid in self.__careCHIDs :
			chatFacade.unbindChannelHandler( chid, self.__onReceiveMessage )
		Control.dispose( self )

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_ChatMSGPage :
			INFO_MSG( str( self ) )

	def __initialize( self, pg ) :
		pyBtnTab = MSGTab( pg.btnTab )						# TabButton
		pyBtnTab.onRMouseUp.bind( self.__onTabRMouseUp )
		pyTPBg = MSGTabPanel( pg.tpMSG )					# MSGTabPanel
		TabPage.__init__( self, pyBtnTab, pyTPBg )
		self.pyMSGPanel_ = MSGPanel( pg.tpMSG.cpMSG, pg.tpMSG.sbar )
		self.pyMSGPanel_.h_dockStyle = "HFILL"
		self.pyMSGPanel_.v_dockStyle = "VFILL"


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		产生控件事件
		"""
		if self.__isInitPages :
			TabPage.generateEvents_( self )
			Control.generateEvents_( self )
			self.__onTabMouseUp = self.createEvent_( "onTabMouseUp" )
			del self.__isInitPages

	@property
	def onTabMouseUp( self ) :
		return self.__onTabMouseUp


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onTabRMouseUp( self, pyBtn ) :
		"""
		鼠标右键点击 tab 按钮时被触发
		"""
		self.onTabMouseUp( pyBtn )

	# -------------------------------------------------
	def __onReceiveMessage( self, channel, spkID, spkName, msg, statusID = None ) :
		"""
		接收频道消息
		"""
		if channel.id not in self.__careCHIDs : return
		msg_temp = msg.split("/ltime")
		if len( msg_temp ) > 1 :
			msg = msg_temp[0]
		msg = channel.formatMsg( spkID, spkName, msg )
		self.pyMSGPanel_.addChanelMessage( channel, msg )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onSelectChanged_( self, selected ) :
		"""
		页面显示/隐藏时被调用
		"""
		TabPage.onSelectChanged_( self, selected )

	def onMenuItemClick_( self, pyItem ) :
		"""
		菜单选项被点击是触发
		"""
		pass

	# ---------------------------------------
	def onStartDrag_( self ) :
		"""
		开始拖动页面
		"""
		if self.__docked :											# 处于停靠状态
			btnLeft = self.pyBtn.left								# 记录 undock 前按钮的位置
			self.undock( self.posToScreen )							# 脱离父体( tab 按钮往左走了 )
			space = btnLeft - self.pyBtn.left						# 按钮往左走动的距离
			self.pyFiller_.left += space							# 将窗口往右移
		self.__cursorToFillerPos = self.pyFiller_.mousePos			# 记录下鼠标相对 filler 的位置

	def onDragging_( self ) :
		"""
		拖动页面
		"""
		cx, cy = csol.pcursorPosition()
		x, y = self.__cursorToFillerPos
		self.pyFiller_.pos = cx - x, cy - y
		self.pyBinder.onPageMoving_( self )

	def onStopDrag_( self ) :
		"""
		结束页面拖动
		"""
		self.pyBinder.onPageStopMoving_( self )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isMouseHit( self ) :
		if self.pyBtn.isMouseHit() :
			return True
		return self.pyPanel.isMouseHit()

	# -------------------------------------------------
	def reset( self ) :
		"""
		重置频道为默认设置（角色进入世界时调用）
		"""
		self.pyMSGPanel_.clearMessages()
		self.__careCHIDs.clear()
		self.careCHIDs = self.defCareCHIDs_
		self.color = self.__cc_def_color

	# -------------------------------------------------
	def dock( self, index ) :
		"""
		设置为停靠状态
		"""
		self.__docked = True
		if self.pyFiller_ :
			self.pyFiller_.dispose()
			self.pyFiller_ = None
		self.pyBinder.onPageDocked_( self, index )

	def undock( self, pos ) :
		"""
		取消停靠，并移到指定位置上
		"""
		self.__docked = False							# 取消停靠
		self.__locked = False							# 取消锁定状态
		self.pyBinder.onPageLeft_( self )				# 通知脱离父体
		self.pyFiller_ = PageWindow( self, pos )		# 添加到脱离窗口中
		self.selected = True


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getPGName( self ) :
		return self.pyBtn.text

	def _setPGName( self, name ) :
		self.pyBtn.text = name

	# ---------------------------------------
	def _getColor( self ) :
		return self.pyPanel.color

	def _setColor( self, color ) :
		self.pyBtn.selectedBackColor = color
		self.pyPanel.color = color

	# -------------------------------------------------
	def _setLocked( self, lock ) :
		if self.unlockable_ :					# 不可以被解锁
			self.__locked = True
		else :
			self.__locked = lock

	# -------------------------------------------------
	def _getCareCHIDs( self ) :
		return self.__careCHIDs

	def _setCareCHIDs( self, chids ) :
		news = chids.difference( self.__careCHIDs )
		olds = self.__careCHIDs.difference( chids )
		self.__careCHIDs = set([])
		self.__careCHIDs.update( chids )
		for chid in news :
			chatFacade.bindChannelHandler( chid, self.__onReceiveMessage )
		for chid in olds :
			chatFacade.unbindChannelHandler( chid, self.__onReceiveMessage )

	# -------------------------------------------------
	def _getPos( self ) :
		if self.pyFiller_ :
			return self.pyFiller_.pos
		return Control._getPos( self )

	def _setPos( self, pos ) :
		if self.pyFiller_ :
			self.pyFiller_.pos = pos
		else :
			Control._setPos( self, pos )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyMSGPanel = property( lambda self : self.pyMSGPanel_ )				# GUIBaseObject: 显示消息的版面
	enable = property( lambda self : True, lambda self, v : v )			# bool: 屏蔽 enable 属性
	pgName = property( _getPGName, _setPGName )							# str: 获取/设置页名
	color = property( _getColor, _setColor )							# Color/tuple: 获取/设置版面颜色
	unlockable = property( lambda self : self.unlockable_ )				# bool: 获取分页是否可以被解锁
	deletable = property( lambda self : self.deletable_ )				# bool: 获取分页是否可被删除
	locked = property( lambda self : self.__locked, _setLocked )		# bool: 获取/设置是否锁定分页
	docked = property( lambda self : self.__docked )					# bool: 获取是否处于停靠主窗口状态
	careCHIDs = property( _getCareCHIDs, _setCareCHIDs )				# set: 获取/设置页面关注的信息频道

	pos = property( _getPos, _setPos )									# Vector2: 位置


# --------------------------------------------------------------------
# 综合分页
# --------------------------------------------------------------------
class GatherPage( MSGPage ) :
	def __init__( self, pyBinder) :
		MSGPage.__init__( self, pyBinder )
		self.pgName = labelGather.getText( "ChatWindow:MSGReceiver", "tpGather" )
		self.deletable_ = False					# 不可被删除
		self.unlockable_ = True					# 不可被解锁
		self.defCareCHIDs_ = set( [ \
			csdefine.CHAT_CHANNEL_NEAR,			# 附近,
			csdefine.CHAT_CHANNEL_LOCAL,		# 本地,
			csdefine.CHAT_CHANNEL_TEAM,			# 队伍,
			csdefine.CHAT_CHANNEL_TONG,			# 帮会,
			csdefine.CHAT_CHANNEL_WHISPER,		# 密语,
			csdefine.CHAT_CHANNEL_WORLD,		# 世界,
			csdefine.CHAT_CHANNEL_RUMOR,		# 谣言,
			csdefine.CHAT_CHANNEL_WELKIN_YELL,	# 天音
			csdefine.CHAT_CHANNEL_TUNNEL_YELL,	# 地音

			# GM/公告频道
			csdefine.CHAT_CHANNEL_SYSBROADCAST,	# 广播,

			# NPC 发言频道
			csdefine.CHAT_CHANNEL_NPC_SPEAK,	# NPC,

			# 系统提示频道
			csdefine.CHAT_CHANNEL_SYSTEM,		# 系统,
			csdefine.CHAT_CHANNEL_MESSAGE,		# 消息
			csdefine.CHAT_CHANNEL_CAMP,			# 阵营
			] )

		self.__triggers = {}
		self.__registerTriggers()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_CHAT_RECEIVE_ROLE_INFO"] = self.__onReceiveRoleInfo
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	# -------------------------------------------------
	def __onReceiveRoleInfo( self, msg ) :
		"""
		接收角色信息
		"""
		color = ( 255, 255, 255 )
		self.pyMSGPanel_.addCommonMessage( msg, color )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	# -------------------------------------------------
	def dock( self, index ) :
		"""
		屏蔽停靠操作
		"""
		pass

	def undock( self, pos ) :
		"""
		屏蔽撤销停靠操作
		"""
		pass


# --------------------------------------------------------------------
# 个人分页
# --------------------------------------------------------------------
class PersonalPage( MSGPage ) :
	def __init__( self, pyBinder ) :
		MSGPage.__init__( self, pyBinder )
		self.pgName = csconst.CHAT_CHID_2_NAME[csdefine.CHAT_CHANNEL_PERSONAL]
		self.deletable_ = False					# 不可被删除
		self.defCareCHIDs_ = set( [
			csdefine.CHAT_CHANNEL_TEAM,			# 队伍,
			csdefine.CHAT_CHANNEL_TONG,			# 帮会,
			csdefine.CHAT_CHANNEL_PERSONAL,		# 个人,
			csdefine.CHAT_CHANNEL_WHISPER,		# 密语,
			] )


# --------------------------------------------------------------------
# 战斗分页
# --------------------------------------------------------------------
class CombatPage( MSGPage ) :
	def __init__( self, pyBinder ) :
		MSGPage.__init__( self, pyBinder )
		self.pgName = csconst.CHAT_CHID_2_NAME[csdefine.CHAT_CHANNEL_COMBAT]
		self.deletable_ = False				# 不可被删除
		self.defCareCHIDs_ = set( [csdefine.CHAT_CHANNEL_COMBAT] )		# 战斗,

# --------------------------------------------------------------------
# 帮会分页
# --------------------------------------------------------------------
class TongPage( MSGPage ) :
	def __init__( self, pyBinder ) :
		MSGPage.__init__( self, pyBinder )
		self.pgName = csconst.CHAT_CHID_2_NAME[csdefine.CHAT_CHANNEL_TONG]
		self.deletable_ = False											# 不可被删除
		self.defCareCHIDs_ = set( [csdefine.CHAT_CHANNEL_TONG] )		# 帮会,
		

# --------------------------------------------------------------------
# 帮战分页
# --------------------------------------------------------------------
class TongBattlePage( MSGPage ) :
	def __init__( self, pyBinder ) :
		MSGPage.__init__( self, pyBinder )
		self.pgName = csconst.CHAT_CHID_2_NAME[csdefine.CHAT_CHANNEL_TONG_CITY_WAR]
		self.deletable_ = False											# 不可被删除
		self.defCareCHIDs_ = set( [csdefine.CHAT_CHANNEL_TONG_CITY_WAR] )		# 帮会,



# --------------------------------------------------------------------
# 分页窗口，聊天分页被拖出来后将会放到分页窗口中
# --------------------------------------------------------------------
class PageWindow( RootGUI ) :
	__cc_tab_left			= 4						# 分页按钮的左距
	__cc_width_range		= ( 300, 700 )
	__cc_height_range		= ( 120, 600 )

	def __init__( self, pyPage, pos ) :
		wnd = GUI.load( "guis/general/chatwindow/mainwnd/pagefiller.gui" )
		RootGUI.__init__( self, wnd )
		self.focus = False
		self.movable_ = False						# 标示窗口是否可以移动
		self.activable_ = False						# 标示窗口是否可被激活
		self.escHide_ = False						# 按 esc 键是否会隐藏
		pyPage.pyBtn.left = self.__cc_tab_left

		self.pyPage_ = pyPage
		self.addPyChild( pyPage )
		self.addToMgr()
		self.__initResizers( wnd )

		pyPage.pos = 0, 0
		self.pos = pos
		self.size = pyPage.size
		pyPage.h_dockStyle = "HFILL"
		pyPage.v_dockStyle = "VFILL"
		self.show()

	def __del__( self ) :
		RootGUI.__del__( self )
		if Debug.output_del_ChatMSGPage :
			INFO_MSG( str( self ) )

	def dispose( self ) :
		self.pyPage_ = None
		RootGUI.dispose( self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initResizers( self, wnd ) :
		"""
		初始化大小调节器
		"""
		boards = { "r" : wnd.resizeHit_r, "t" : wnd.resizeHit_t, \
			"rt" : wnd.resizeHit_rt, "b" : wnd.resizeHit_b, "rb" : wnd.resizeHit_rb }
		self.__pyWndResizer = WndResizer( self, boards )
		self.__pyWndResizer.setWidthRange( self.__cc_width_range )
		self.__pyWndResizer.setHeightRange( self.__cc_height_range )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isMouseHit( self ) :
		if self.pyPage_.pyBtn.isMouseHit() :
			return True
		if self.__pyWndResizer.isMouseHit() :
			return True
		return False
