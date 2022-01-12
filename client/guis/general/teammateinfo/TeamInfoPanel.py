# -*- coding: gb18030 -8-

# This module implements the TeamInfoPanel which views teammate and team applicants info
# written by gjx 2009-9-16

from guis import *
from guis.controls.TabCtrl import TabPanel
from guis.controls.ODListPanel import ODListPanel
from guis.controls.ButtonEx import HButtonEx
from RowItem import RowItem
from LabelGather import labelGather
import event.EventCenter as ECenter
import time
import csconst
import csstatus


# --------------------------------------------------------------------
# 队伍信息面板基类
# --------------------------------------------------------------------
class TeamInfoPanel( TabPanel ) :

	def __init__( self, panel, pyBinder ) :
		TabPanel.__init__( self, panel, pyBinder )
		self.initialize_( panel )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def initialize_( self, panel ) :
		"""
		初始化列表
		"""
		class ListPanel( ODListPanel ) :
			def getViewItem_( self ) :
				return RowItem( self )
		self.pyInfoPanel_ = ListPanel( panel.infoPanel, panel.scrollBar )
		self.pyInfoPanel_.onViewItemInitialized.bind( self.onInitItem_ )
		self.pyInfoPanel_.onDrawItem.bind( self.onDrawItem_ )
		self.pyInfoPanel_.itemHeight = 23
		self.pyInfoPanel_.ownerDraw = True

	# -------------------------------------------------
	def onDrawItem_( self, pyRowItem ) :
		"""
		重画信息行
		"""
		pyRowItem.refreshInfo( pyRowItem.listItem )

	def onInitItem_( self, pyRowItem )	 :
		"""
		初始化信息行，开启自定义绘制后必须的方法
		"""
		pass

	# -------------------------------------------------
	def onSelected_( self ) :
		"""
		被选中为可见面板或被设置为可见面板
		"""
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def clearPanel( self ) :
		"""
		清空面板信息
		"""
		self.pyInfoPanel_.clearItems()

	def resetState( self ) :
		"""
		刷新面板信息的选择状态
		"""
		self.pyInfoPanel_.resetState()


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _setVisible( self, visible ) :
		TabPanel._setVisible( self, visible )
		if visible : self.onSelected_()

	# -------------------------------------------------
	visible = property( TabPanel._getVisible, _setVisible )


# --------------------------------------------------------------------
# 申请入队的玩家信息面板
# --------------------------------------------------------------------
class ApplicantPanel( TeamInfoPanel ) :

	__MAX_AMOUNT = 20											# 列表允许最大申请人数

	def __init__( self, panel, pyBinder ) :
		TeamInfoPanel.__init__( self, panel, pyBinder )

		self.__detectCBID = 0									# 申请超时检查回调ID


	# ----------------------------------------------------------------
	# virtual method
	# ----------------------------------------------------------------
	def initialize_( self, panel ) :
		TeamInfoPanel.initialize_( self, panel )

		self.__pyRefuseBtn = HButtonEx( panel.refuseBtn )			# 拒绝按钮
		self.__pyRefuseBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyRefuseBtn.onLClick.bind( self.__refuse )

		self.__pyClearBtn = HButtonEx( panel.clearBtn )			# 清空按钮
		self.__pyClearBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyClearBtn.onLClick.bind( self.__clear )

		self.__pyInviteBtn = HButtonEx( panel.acceptBtn )			# 邀请按钮
		self.__pyInviteBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyInviteBtn.onLClick.bind( self.__invite )

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setPyBgLabel( self.__pyRefuseBtn, "teammateinfo:teamInfoWindow", "refuseBtn" )
		labelGather.setPyBgLabel( self.__pyClearBtn, "teammateinfo:teamInfoWindow", "clearBtn" )
		labelGather.setPyBgLabel( self.__pyInviteBtn, "teammateinfo:teamInfoWindow", "acceptBtn" )


	# -------------------------------------------------
	# private
	# -------------------------------------------------
	def __refuse( self ) :
		"""
		拒绝某个玩家的组队邀请，在规定时间间隔内
		被拒玩家无法再发送给我的邀请
		"""
		selApplicant = self.pyInfoPanel_.selItem
		if selApplicant is None : return
		self.pyInfoPanel_.removeItem( selApplicant )
		BigWorld.player().refusePlayerJoinTeam( selApplicant[3], selApplicant[0] )

	def __clear( self ) :
		"""
		清空列表中的所有邀请玩家
		"""
		self.clearPanel()

	def __invite( self ) :
		"""
		邀请选中的玩家加入队伍
		"""
		selApplicant = self.pyInfoPanel_.selItem
		if selApplicant is None : return
		self.pyInfoPanel_.removeItem( selApplicant )
		BigWorld.player().allowPlayerJoinTeam( selApplicant[3], selApplicant[0] )

	def __startFilter( self ) :
		if not self.__detectCBID :
			self.__filter()

	def __filter( self ) :
		"""
		检查并移除超时组队申请者
		"""
		if self.pyInfoPanel_.itemCount == 0 :
			ECenter.fireEvent( "EVT_ON_SET_CAPTAIN_MARK_NORMAL" )
			self.__shutdownFilter()
			return
		currTime = time.time()
		for applicant in self.pyInfoPanel_.items :
			if currTime - applicant[-1] < 60 : continue
			self.pyInfoPanel_.removeItem( applicant )
		self.__detectCBID = BigWorld.callback( 1, self.__filter )

	def __shutdownFilter( self ) :
		if self.__detectCBID :
			BigWorld.cancelCallback( self.__detectCBID )
			self.__detectCBID = 0

	def __enableButtons( self ) :
		"""
		根据玩家的状态变化，使能各个功能按钮
		"""
		player = BigWorld.player()
		isCaptain = player.isCaptain()
		self.__pyRefuseBtn.enable = isCaptain
		self.__pyInviteBtn.enable = isCaptain


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onSelected_( self ) :
		self.resetState()
		ECenter.fireEvent( "EVT_ON_SET_CAPTAIN_MARK_NORMAL" )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addApplicant( self, name, metier, level, entityID ) :
		"""
		接收到邀请组队的玩家信息
		@param	name		: 申请者的名字
		@param	metier		: 申请者的职业
		@param	level		: 申请者的等级
		@param	entityID	: 申请者的entity id
		"""
		for index, n in enumerate( self.pyInfoPanel_.items ) :
			if name == n[0] :
				self.pyInfoPanel_.removeItemOfIndex( index )
				break
		else :
			BigWorld.player().statusMessage( csstatus.TEAM_NOTIFY_NEW_APPLICANT, name )
		pclass = csconst.g_chs_class[ metier ]						# 职业转换为文字
		applicant = ( name, pclass, level, entityID, time.time() )	# 存储为元组
		self.pyInfoPanel_.addItem( applicant )
		itemAmount = self.pyInfoPanel_.itemCount
		if itemAmount > self.__MAX_AMOUNT :
			self.pyInfoPanel_.removeItemOfIndex( 0 )
		self.__startFilter()
		if not self.visible or not self.pyBinder.visible :
			ECenter.fireEvent( "EVT_ON_NOTIFY_NEW_TEAM_APPLICANT" )

	def reset( self ) :
		self.clearPanel()
		self.__shutdownFilter()


# --------------------------------------------------------------------
# 队员信息面板
# --------------------------------------------------------------------
class TeammatePanel( TeamInfoPanel ) :

	def __init__( self, panel, pyBinder ) :
		TeamInfoPanel.__init__( self, panel, pyBinder )


	# ----------------------------------------------------------------
	# virtual method
	# ----------------------------------------------------------------
	def initialize_( self, panel ) :
		TeamInfoPanel.initialize_( self, panel )

		self.__pyJoinBtn = HButtonEx( panel.joinBtn )			# 组队按钮
		self.__pyJoinBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyJoinBtn.onLClick.bind( self.__joinTeam )

		self.__pyKickBtn = HButtonEx( panel.kickBtn )			# 剔除按钮
		self.__pyKickBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyKickBtn.onLClick.bind( self.__kickAway )
		self.__pyKickBtn.enable = False

		self.__pyFollowBtn = HButtonEx( panel.followBtn )		# 邀请队员跟随按钮
		self.__pyFollowBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyFollowBtn.onLClick.bind( self.__follow )
		self.__pyFollowBtn.enable = False

		self.__pyCancelFollowBtn = HButtonEx( panel.cancelBtn )# 取消跟随按钮
		self.__pyCancelFollowBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyCancelFollowBtn.onLClick.bind( self.__cancelFollow )
		self.__pyCancelFollowBtn.visible = False

		self.__pyLeaveBtn = HButtonEx( panel.leaveBtn )		# 离队按钮
		self.__pyLeaveBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyLeaveBtn.onLClick.bind( self.__leaveTeam )
		self.__pyLeaveBtn.enable = False

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setPyBgLabel( self.__pyJoinBtn, "teammateinfo:teamInfoWindow", "joinBtn" )
		labelGather.setPyBgLabel( self.__pyKickBtn, "teammateinfo:teamInfoWindow", "kickBtn" )
		labelGather.setPyBgLabel( self.__pyFollowBtn, "teammateinfo:teamInfoWindow", "followBtn" )
		labelGather.setPyBgLabel( self.__pyCancelFollowBtn, "teammateinfo:teamInfoWindow", "cancelBtn" )
		labelGather.setPyBgLabel( self.__pyLeaveBtn, "teammateinfo:teamInfoWindow", "leaveBtn" )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __joinTeam( self ) :
		"""
		进入组队模式/自建队伍
		"""
		player = BigWorld.player()
		if not player.isInTeam() :
			player.inviteJoinTeamNear( player )				# 邀请自己既是自建队伍
		else :
			player.prepareForTeamInvite()

	def __kickAway( self ) :
		"""
		剔除某玩家
		"""
		player = BigWorld.player()
		if not player.isCaptain() : return
		selTm = self.pyInfoPanel_.selItem
		if selTm is None : return
		player.teamDisemploy( selTm[3] )

	def __follow( self ) :
		"""
		队长邀请队员跟随
		"""
		player = BigWorld.player()
		if not player.isCaptain() : return
		player.team_leadTeam()

	def __cancelFollow( self ) :
		"""
		取消跟随
		"""
		player = BigWorld.player()
		if player.isTeamLeading() :
			player.team_cancelFollow( csstatus.TEAM_CANCEL_FOLLOW )

	def __leaveTeam( self ) :
		"""
		离开队伍
		"""
		player = BigWorld.player()
		if player.isInTeam() :
			player.leaveTeam()

	def __enableButtons( self ) :
		"""
		根据玩家的状态变化，使能各个功能按钮
		"""
		player = BigWorld.player()
		isTeamLeading = player.isTeamLeading()
		isCaptain = player.isCaptain()
		self.__pyFollowBtn.enable = isCaptain
		self.__pyFollowBtn.visible = not isCaptain or not isTeamLeading
		self.__pyCancelFollowBtn.visible = isCaptain and isTeamLeading
		self.__pyKickBtn.enable = isCaptain
		self.__pyLeaveBtn.enable = player.isInTeam()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onSelected_( self ) :
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onMemberJoinIn( self, teammate ) :
		"""
		新队员加入
		"""
		metier = csconst.g_chs_class[ teammate.raceclass ]			# 职业转换为文字
		tmInfo = ( teammate.name, metier, teammate.level, teammate.objectID )
		self.pyInfoPanel_.addItem( tmInfo )
		if teammate.objectID == BigWorld.player().captainID :		# 如果加进来的是队长
			for tm in self.pyInfoPanel_.items :						# 把队长放到第一个位置
				if tm[3] == teammate.objectID : break
				self.pyInfoPanel_.removeItem( tm )
				self.pyInfoPanel_.addItem( tm )

	def onRejoin( self, oldEntityID, newEntityID ) :
		"""
		队员下线后重上
		"""
		tmMembers = self.pyInfoPanel_.items
		for index, tm in enumerate( tmMembers ) :
			if tm[3] == oldEntityID :
				newInfo = ( tm[0], tm[1], tm[2], newEntityID )
				self.pyInfoPanel_.updateItem( index, newInfo )
				break

	def onMemberLeft( self, teammateID ) :
		"""
		队员离队
		"""
		tmMembers = self.pyInfoPanel_.items
		for index, tm in enumerate( tmMembers ) :
			if tm[3] == teammateID :
				self.pyInfoPanel_.removeItemOfIndex( index )
				break
		self.__enableButtons()

	def onTeamDisbanded( self ) :
		"""
		队伍解散
		"""
		self.clearPanel()
		self.__enableButtons()

	def onTMLevelChanged( self, teammateID, level ) :
		"""
		队员等级改变
		"""
		tmMembers = self.pyInfoPanel_.items
		for index, tm in enumerate( tmMembers ) :
			if tm[3] == teammateID :
				newInfo = ( tm[0], tm[1], level, tm[3] )
				self.pyInfoPanel_.updateItem( index, newInfo )
				break

	def onTMNameChanged( self, teammateID, name ) :
		"""
		队员名字改变
		"""
		tmMembers = self.pyInfoPanel_.items
		for index, tm in enumerate( tmMembers ) :
			if tm[3] == teammateID :
				newInfo = ( name, tm[1], tm[2], tm[3] )
				self.pyInfoPanel_.updateItem( index, newInfo )
				break

	def onCaptainChanged( self, captainID ) :
		"""
		队长改变，由于队长要保持在第一个，因此需要重新排列
		"""
		for tm in self.pyInfoPanel_.items :
			if tm[3] == captainID : break
			self.pyInfoPanel_.removeItem( tm )
			self.pyInfoPanel_.addItem( tm )
		self.__enableButtons()

	def onFollowStateChanged( self ):
		"""
		跟随状态发生变化
		"""
		self.__enableButtons()

	# -------------------------------------------------
	def reset( self ) :
		"""
		重置界面工作在此进行
		"""
		self.clearPanel()
		self.__pyFollowBtn.enable = False
		self.__pyFollowBtn.visible = True
		self.__pyCancelFollowBtn.visible = False
		self.__pyKickBtn.enable = False
		self.__pyLeaveBtn.enable = False
