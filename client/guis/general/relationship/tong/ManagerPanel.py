# -*- coding: gb18030 -*-
#
# $Id: DutyPanel.py,v 1.4 2008-07-02 06:20:35 fangpengjun Exp $

"""
implement ManagerPanel window
"""
from guis import *
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TextBox import TextBox
import csdefine
from config.client.msgboxtexts import Datas as mbmsgs
from LabelGather import labelGather

class ManagerPanel( Window ):
	def __init__( self, panel ):
		Window.__init__( self, panel )
		self.activable_ = True
		self.pyNameBox_ = TextBox( panel.nameBox.box )
		self.pyNameBox_.inputMode = InputMode.COMMON

		self.pyBtnAdd_ = HButtonEx( panel.btnAdd )
		self.pyBtnAdd_.setExStatesMapping( UIState.MODE_R4C1 )
		self.pyBtnAdd_.enable = False

		self.pyBtnDel_ = HButtonEx( panel.btnDel )
		self.pyBtnDel_.setExStatesMapping( UIState.MODE_R4C1 )
		self.pyBtnDel_.enable = False

	def onKeyDown_( self, key, mods ) :
		if ( mods == 0 ) and ( key == KEY_RETURN  or key == KEY_NUMPADENTER ) :			# 如果按下了回车键
			self.pyNameBox_.tabStop = False
			return True
		return Window.onKeyDown_( self, key, mods )

	def show( self, pyOwner ):
		Window.show( self, pyOwner )
		self.pyNameBox_.tabStop = True

	def hide( self ):
		self.pyNameBox_.text = ""
		Window.hide( self )

	def onNameChange_( self ):
		pass
# --------------------------------------------------------------------
# 帮会成员管理
# --------------------------------------------------------------------
class MemberMgr( ManagerPanel ):
	__instance=None
	def __init__( self ):
		assert MemberMgr.__instance is None,"MemberMgr instance has been created"
		MemberMgr.__instance=self
		panel = GUI.load( "guis/general/relationwindow/tongpanel/membermgr.gui" )
		uiFixer.firstLoadFix( panel )
		ManagerPanel.__init__( self, panel )
		self.addToMgr( "memberMgr" )
		self.pyBtnAdd_.onLClick.bind( self.__onAddMember )
		self.pyBtnDel_.onLClick.bind( self.__onDelmember )
		self.pyNameBox_.onTextChanged.bind( self.__onNameChange )

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setLabel( panel.btnDel.lbText, "TongAbout:MemberMgr", "btnDel" )
		labelGather.setLabel( panel.btnAdd.lbText, "TongAbout:MemberMgr", "btnAdd" )
		labelGather.setLabel( panel.nameText, "TongAbout:MemberMgr", "nameText" )
		labelGather.setLabel( panel.lbTitle, "TongAbout:MemberMgr", "lbTitle" )

	@staticmethod
	def instance():
		"""
		get the exclusive instance of MemberMgr
		"""
		if MemberMgr.__instance is None:
			MemberMgr.__instance=MemberMgr()
		return MemberMgr.__instance

	def __del__(self):
		"""
		just for testing memory leak
		"""
		pass

	@staticmethod
	def getInstance():
		"""
		return MemberMgr.__instance, if MemberMgr.__instance is None ,return None,
		else return the exclusive instance of MemberMgr
		"""
		return MemberMgr.__instance

	def __onAddMember( self, pyBtn ):
		player = BigWorld.player()
		if pyBtn is None:return
		name = self.pyNameBox_.text
		if name == "":return
		player.tong_requestJoinByPlayerName( name )

	def __onDelmember( self, pyBtn ):
		if pyBtn is None:return
		name = self.pyNameBox_.text
		if name == "":return
		dbid = self.notify_( name )
		if dbid < 0:
			# "帮会没有该成员！"
			showAutoHideMessage( 3.0, 0x06c2, mbmsgs[0x0c22], pyOwner = self )
		if dbid > 0: #能获取成员dbid
			def query( rs_id ):
				if rs_id == RS_OK:
					BigWorld.player().tong_kickMember( dbid )
			# "确定将%s请出帮会？"
			showMessage( mbmsgs[0x06c1] % name, "", MB_OK_CANCEL, query )
			return True

	def __onNameChange( self, pyBox ):
		player = BigWorld.player()
		tongGrade = player.tong_grade
		conscGrade = kickMemberGrade = player.tong_checkDutyRights( tongGrade, csdefine.TONG_RIGHT_MEMBER_MANAGE )
		self.pyBtnAdd_.enable = pyBox.text != "" and conscGrade
		self.pyBtnDel_.enable = pyBox.text != "" and conscGrade

	def notify_( self, name):
		tongMerbers = BigWorld.player().tong_memberInfos
		for dbid, merber in tongMerbers.iteritems():
			if name == merber.getName():
				return dbid
		return -1

	def show( self, pyOwner = None ):
		ManagerPanel.show( self, pyOwner )

	def hide( self ):
		ManagerPanel.hide( self )
		self.dispose()
		MemberMgr.__instance=None


# -------------------------------------------------------------------------
# 帮会同盟管理
# ------------------------------------------------------------------------
class LeagueMgr( ManagerPanel ):
	__instance=None
	def __init__( self ):
		assert LeagueMgr.__instance is None,"LeagueMgr instance has been created"
		LeagueMgr.__instance=self
		panel = GUI.load( "guis/general/relationwindow/tongpanel/leaguemgr.gui" )
		uiFixer.firstLoadFix( panel )
		ManagerPanel.__init__( self, panel )
		self.addToMgr( "leagueMgr" )
		self.pyBtnAdd_.onLClick.bind( self.__onAddLeague )
		self.pyBtnDel_.onLClick.bind( self.__onDelLeague )
		self.pyNameBox_.onTextChanged.bind( self.__onNameChange )

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setLabel( panel.btnDel.lbText, "TongAbout:LeagueMgr", "btnDel" )
		labelGather.setLabel( panel.btnAdd.lbText, "TongAbout:LeagueMgr", "btnAdd" )
		labelGather.setLabel( panel.nameText, "TongAbout:LeagueMgr", "nameText" )
		labelGather.setLabel( panel.lbTitle, "TongAbout:LeagueMgr", "lbTitle" )

	@staticmethod
	def instance():
		"""
		to get the exclusive instance of LeagueMgr
		"""
		if LeagueMgr.__instance is None:
			LeagueMgr.__instance=LeagueMgr()
		return LeagueMgr.__instance

	def __del__(self):
		"""
		just for testing memory leak
		"""
		pass

	@staticmethod
	def getInstance():
		"""
		return LeagueMgr.__instance,if LeagueMgr.__instance is None , return None ,
		else return the exclusive instance of LeagueMgr
		"""
		return LeagueMgr.__instance

	def __onAddLeague( self, pyBtn ): #添加同盟
		if pyBtn is None:return
		player = BigWorld.player()
		name = self.pyNameBox_.text
		if name == "":return
		if name == player.tongName:
			# "不能添加自己帮会为同盟！"
			showAutoHideMessage( 3.0, 0x06c3, mbmsgs[0x0c22], pyOwner = self )
			return
		for dbid, league in player.tong_leagues.iteritems():
			if league == name:
				# "已存在该同盟帮会！"
				showAutoHideMessage( 3.0, 0x06c4, mbmsgs[0x0c22], pyOwner = self )
				return
		BigWorld.player().tong_requestTongLeague( name )

	def __onDelLeague( self, pyBtn ): #删除同盟
		if pyBtn is None:return
		name = self.pyNameBox_.text
		if name == "": return
		dbid = self.notify_( name )
		if dbid < 0:
			# "没有该同盟帮会！"
			showAutoHideMessage( 3.0, 0x06c5, mbmsgs[0x0c22], pyOwner = self )
		else: #能获取同盟帮会dbid
			def query( rs_id ):
				if rs_id == RS_OK:
					BigWorld.player().tong_leagueDispose( dbid )
			# 确定与%s帮会解除同盟关系？
			showMessage( mbmsgs[0x06c6] % name, "", MB_OK_CANCEL, query, self )
			return True

	def __onNameChange( self, pyBox ):
		player = BigWorld.player()
		self.pyBtnAdd_.enable = pyBox.text != "" and player.tong_checkDutyRights( player.tong_grade, csdefine.TONG_RIGHT_LEAGUE_MAMAGE )
		self.pyBtnDel_.enable = pyBox.text != "" and player.tong_checkDutyRights( player.tong_grade, csdefine.TONG_RIGHT_LEAGUE_MAMAGE )

	def notify_( self, name):
		tongLeagues = BigWorld.player().tong_leagues
		for dbid, league in tongLeagues.iteritems():
			if name == league:
				return dbid
		return -1

	def show( self, pyOwner = None ):
		ManagerPanel.show( self, pyOwner )

	def hide( self ):
		ManagerPanel.hide( self )
		self.dispose()
		LeagueMgr.__instance=None
