# -*- coding: gb18030 -*-

# 组队申请列表/队伍成员界面
# written by gjx 2009-8-8
# modified by gjx 2009-9-17

from guis import *
from guis.common.Window import Window
from guis.controls.TabCtrl import TabPage
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabCtrl
from TeamInfoPanel import ApplicantPanel
from TeamInfoPanel import TeammatePanel
from LabelGather import labelGather
import event.EventCenter as ECenter


class TeamInfoWindow( Window ) :

	def __init__( self ) :
		wnd = GUI.load( "guis/general/teammateinfo/teaminfo/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.h_dockStyle = "LEFT"
		self.v_dockStyle = "TOP"

		self.__initialize( wnd.tc )

		self.__triggers = {}
		self.__registerTriggers()

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setLabel( wnd.tc.btn_0.lbText, "teammateinfo:teamInfoWindow", "btn_0" )
		labelGather.setLabel( wnd.tc.btn_1.lbText, "teammateinfo:teamInfoWindow", "btn_1" )
		labelGather.setLabel( wnd.lbTitle, "teammateinfo:teamInfoWindow", "lbTitle" )
		labelGather.setLabel( wnd.tc.header.header_2.stTitle, "teammateinfo:teamInfoWindow", "miLevel" )
		labelGather.setLabel( wnd.tc.header.header_1.stTitle, "teammateinfo:teamInfoWindow", "miMetier" )
		labelGather.setLabel( wnd.tc.header.header_0.stTitle, "teammateinfo:teamInfoWindow", "miPlName" )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, tabCtrl ) :
		self.__pyTabCtrl = TabCtrl( tabCtrl )					# 分页控件

		pyTabBtn = TabButton( tabCtrl.btn_0 )				# 队伍列表
		pyTabPanel = TeammatePanel( tabCtrl.panel_0, self )
		self.__pyTmPage = TabPage( pyTabBtn, pyTabPanel )
		self.__pyTabCtrl.addPage( self.__pyTmPage )

		pyTabBtn = TabButton( tabCtrl.btn_1 )				# 组队申请列表
		pyTabPanel = ApplicantPanel( tabCtrl.panel_1, self )
		self.__pyAppPage = TabPage( pyTabBtn, pyTabPanel )
		self.__pyTabCtrl.addPage( self.__pyAppPage )
		self.__pyAppPage.enable = False

	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_SHOW_TEAM_INFO_WND"] = self.__triggleShow
		self.__triggers["EVT_ON_TEAM_CAPTAIN_CHANGED"] = self.__onCaptainChanged		# 队长改变
		self.__triggers["EVT_ON_TEAM_DISBANDED"] = self.__onTeamDisbanded				# 队伍解散
		self.__triggers["EVT_ON_TEAM_MEMBER_REJOIN"] = self.__onRejoin					# 队员下线后重上
		self.__triggers["EVT_ON_TEAM_MEMBER_ADDED"] = self.__onMemberJoinIn				# 队员加入
		self.__triggers["EVT_ON_TEAM_MEMBER_LEFT"] = self.__onMemberLeft				# 队员离队
		self.__triggers["EVT_ON_TEAM_MEMBER_LEVEL_CHANGED"] = self.__onLevelChanged		# 队员等级改变
		self.__triggers["EVT_ON_TEAM_MEMBER_NAME_CHANGED"] = self.__onNameChanged		# 队员名字改变
		self.__triggers["EVT_ON_FOLLOW_STATE_CHANGE"] = self.__onFollowStateChanged		# 玩家组队跟随状态变化
		self.__triggers["EVT_ON_APPLIED_JOIN_TEAM"] = self.__addApplicant				# 玩家申请加入队伍
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	# -------------------------------------------------
	# about team
	# -------------------------------------------------
	def __triggleShow( self ):
		if not self.visible:
			self.show()
		else:
			self.hide()
			
	def __onCaptainChanged( self, captainID ) :
		"""
		队长改变通知
		"""
		player = BigWorld.player()
		if player.isCaptain() :
			self.__pyAppPage.enable = True
		else :
			if self.__pyTabCtrl.pySelPage == self.__pyAppPage :
				self.__pyTabCtrl.pySelPage = self.__pyTmPage
			self.__pyAppPage.enable = False

		self.__pyTmPage.pyPanel.onCaptainChanged( captainID )

	def __onTeamDisbanded( self ) :
		"""
		队伍解散通知
		"""
		if self.__pyTabCtrl.pySelPage == self.__pyAppPage :
			self.__pyTabCtrl.pySelPage = self.__pyTmPage
		self.__pyAppPage.enable = False
		self.__pyAppPage.pyPanel.reset()
		self.__pyTmPage.pyPanel.onTeamDisbanded()

	def __onMemberJoinIn( self, teammate ) :
		"""
		队员加入
		"""
		self.__pyTmPage.pyPanel.onMemberJoinIn( teammate )

	def __onRejoin( self, oldEntityID, newEntityID ) :
		"""
		队员重新加入
		"""
		self.__pyTmPage.pyPanel.onRejoin( oldEntityID, newEntityID )

	def __onMemberLeft( self, teammateID ) :
		"""
		队员离队
		"""
		self.__pyTmPage.pyPanel.onMemberLeft( teammateID )

	def __onLevelChanged( self, teammateID, level ) :
		"""
		队员等级改变
		"""
		self.__pyTmPage.pyPanel.onTMLevelChanged( teammateID, level )

	def __onNameChanged( self, teammateID, name ) :
		"""
		队员名字改变
		"""
		self.__pyTmPage.pyPanel.onTMNameChanged( teammateID, name )

	def __onFollowStateChanged( self ) :
		"""
		更随状态发生变化
		"""
		self.__pyTmPage.pyPanel.onFollowStateChanged()

	def __addApplicant( self, name, metier, level, entityID ) :
		"""
		申请入队
		"""
		self.__pyAppPage.pyPanel.addApplicant( name, metier, level, entityID )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[ eventMacro ]( *args )

	def onLeaveWorld( self ) :
		self.hide()
		self.__pyAppPage.pyPanel.reset()
		self.__pyTmPage.pyPanel.reset()
		if self.__pyTabCtrl.pySelPage == self.__pyAppPage :
			self.__pyTabCtrl.pySelPage = self.__pyTmPage
		self.__pyAppPage.enable = False

	def show( self ) :
		if self.__pyTabCtrl.pySelPage == self.__pyAppPage :
			ECenter.fireEvent( "EVT_ON_SET_CAPTAIN_MARK_NORMAL" )
		self.__pyAppPage.pyPanel.resetState()
		self.__pyTmPage.pyPanel.resetState()
		Window.show( self )
