# -*- coding: gb18030 -*-
#
# $Id: RoleSelector.py,v 1.37 2008-08-26 02:20:55 huangyongwei Exp $

"""
implement role selection dialog
"""
import csconst
import event.EventCenter as ECenter
import reimpl_login
from LoginMgr import roleSelector
from guis import *
from LabelGather import labelGather
from guis.general.delrolebox import DelRoleBoxshow
from guis.loginuis import *
from guis.common.PyGUI import PyGUI
from guis.common.RootGUI import RootGUI
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.inputbox.InputBox import InputBox
from RoleDelVerifier import RoleDelVerifier
from config.client.msgboxtexts import Datas as mbmsgs

class RoleSelector( RootGUI ) :
	__cc_fade_speed = 0.2

	def __init__( self ) :
		wnd = GUI.load( "guis/loginuis/roleselector/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		self.h_dockStyle = "HFILL"
		self.v_dockStyle = "VFILL"
		self.focus = 0
		self.moveFocus = False
		self.posZSegment = ZSegs.L4				# in uidefine.py
		self.activable_ = True						# if a root gui can be ancriated, when it becomes the top gui, it will rob other gui's input focus
		self.escHide_ 		 = False
		self.__initialize( wnd )

		self.__triggers = {}
		self.__registerTriggers()

		shortcutMgr.setHandler( "ROLE_SELECTOR_CREATE_ROLE", self.__createRole )
		shortcutMgr.setHandler( "ROLE_SELECTOR_DEL_ROLE", self.__deleteRole )
		shortcutMgr.setHandler( "ROLE_SELECTOR_CHOOSE_SERVER", self.__chooseServer )
		shortcutMgr.setHandler( "ROLE_SELECTOR_ENTER_WORLD", self.__enterGame )

	@reimpl_login.deco_guiRoleSelectorInitialze
	def __initialize( self, wnd ) :
		self.__fader = wnd.fader
		self.__fader.speed = self.__cc_fade_speed
		self.__fader.value = 0
		self.__fader.reset()

		self.__pyBtnsPanel = PyGUI( wnd.btnsPanel )
		self.__pyBtnsPanel.h_dockStyle = "S_RIGHT"
		self.__pyBtnsPanel.v_dockStyle = "S_BOTTOM"

		self.__pyBtnBack = HButtonEx( wnd.btnsPanel.btnBack )			# 返回上页
		self.__pyBtnBack.onLClick.bind( self.__chooseServer )
		self.__pyBtnBack.setExStatesMapping( UIState.MODE_R4C1 )

		self.__pyBtnOthers = HButtonEx( wnd.btnsPanel.btnOthers )		# 下一页
		self.__pyBtnOthers.onLClick.bind( self.__toNextRoles )
		self.__pyBtnOthers.setExStatesMapping( UIState.MODE_R4C1 )

		self.__pyBtnRename = HButtonEx( wnd.btnsPanel.btnRename )		# 改名
		self.__pyBtnRename.onLClick.bind( self.__renameRole )
		self.__pyBtnRename.setExStatesMapping( UIState.MODE_R4C1 )

		self.__pyBtnCreate = HButtonEx( wnd.btnsPanel.btnCreate )		# 创建角色
		self.__pyBtnCreate.onLClick.bind( self.__createRole )
		self.__pyBtnCreate.setExStatesMapping( UIState.MODE_R4C1 )

		self.__pyBtnDel = HButtonEx( wnd.btnsPanel.btnDel )			# 删除角色
		self.__pyBtnDel.onLClick.bind( self.__deleteRole )
		self.__pyBtnDel.setExStatesMapping( UIState.MODE_R4C1 )

		self.__pyBtnQuit = HButtonEx( wnd.btnsPanel.btnQuit )			# 退出
		self.__pyBtnQuit.onLClick.bind( self.__quitGame )
		self.__pyBtnQuit.setExStatesMapping( UIState.MODE_R4C1 )

		self.__pyBtnEnterGame = HButtonEx( wnd.btnEnterGame )			# 进入游戏
		self.__pyBtnEnterGame.h_dockStyle = "CENTER"
		self.__pyBtnEnterGame.v_dockStyle = "S_BOTTOM"
		self.__pyBtnEnterGame.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnEnterGame.onLClick.bind( self.__enterGame )
		self.__pyBtnEnterGame.enable = False

		# ---------------------------------------------
		# 设置文本
		# ---------------------------------------------
		labelGather.setPyBgLabel( self.__pyBtnEnterGame, "RoleSelector:main", "btnEnter" )
		labelGather.setPyBgLabel( self.__pyBtnBack, "RoleSelector:main", "btnBack" )
		labelGather.setPyBgLabel( self.__pyBtnCreate, "RoleSelector:main", "btnCreate" )
		labelGather.setPyBgLabel( self.__pyBtnDel, "RoleSelector:main", "btnDel" )
		labelGather.setPyBgLabel( self.__pyBtnQuit, "RoleSelector:main", "btnExit" )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_SHOW_ROLE_SELECTOR"] = self.__enter
		self.__triggers["EVT_ON_HIDE_ROLE_SELECTOR"] = self.__leave
		self.__triggers["EVT_ON_GAME_RECONNECT"] = self.hide
		self.__triggers["EVT_ON_SELECT_ROLE"] = self.__onSelectRole
		self.__triggers["EVT_ON_DESELECT_ROLE"] = self.__onDeselectRole
		self.__triggers["EVT_ON_RENAME_ROLE_SUCCESS"] = self.__onRoleRenamed
		self.__triggers["EVT_ON_LEAVE_LOGIN_STATE"] = self.__onLeaveLoginState
		self.__triggers["EVT_ON_RS_PAGE_CHANGED"] = self.__onPageCountChanged
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )

	def __registerControlTriggers( self ) :
		self.__triggers["EVT_ON_LOST_CONTROL"]		= self.__onLostControl
		self.__triggers["EVT_ON_GOT_CONTROL"]		= self.__onGotControl
		ECenter.registerEvent( "EVT_ON_LOST_CONTROL", self )
		ECenter.registerEvent( "EVT_ON_GOT_CONTROL", self )

	def __deregisterControlTriggers( self ) :
		self.__triggers.pop( "EVT_ON_LOST_CONTROL" )
		self.__triggers.pop( "EVT_ON_GOT_CONTROL" )
		ECenter.unregisterEvent( "EVT_ON_LOST_CONTROL", self )
		ECenter.unregisterEvent( "EVT_ON_GOT_CONTROL", self )

	# --------------------------------------------
	def __onSelectRole( self ) :
		self.__pyBtnEnterGame.enable = True
		self.__pyBtnOthers.visible = rds.roleSelector.getPageCount() > 1
		self.__pyBtnRename.visible = False
		self.__pyBtnDel.enable = True
		self.__pyBtnBack.enable = True
		self.__pyBtnCreate.enable = True
		roleInfo = rds.roleSelector.getSelectedRoleInfo()

		if roleInfo and "_" in roleInfo.getName() :
			self.__pyBtnRename.visible = True
		else :
			self.__pyBtnRename.visible = False

	def __onDeselectRole( self ) :
		"""
		角色取消选中时调用
		"""
		self.__pyBtnBack.enable = True
		self.__pyBtnCreate.enable = True
		self.__pyBtnDel.enable = False
		self.__pyBtnEnterGame.enable = False
		self.__pyBtnRename.visible = False

	def __onRoleRenamed( self, roleDBID, newName ) :
		"""
		角色被改名
		"""
		# "角色成功改名为：%s"
		showMessage( mbmsgs[0x0b61] % newName, "", MB_OK, pyOwner = self )
		roleInfo = rds.roleSelector.getSelectedRoleInfo()
		if roleInfo and "_" in roleInfo.getName() :
			self.__pyBtnRename.visible = True
		else :
			self.__pyBtnRename.visible = False

	def __onLeaveLoginState( self ) :
		pass

	def __onPageCountChanged( self ) :
		"""
		角色候选页数
		"""
		self.__pyBtnOthers.visible = rds.roleSelector.getPageCount() > 1

	def __onLostControl( self ) :
		self.enable = False

	def __onGotControl( self ) :
		self.enable = True

	# --------------------------------------------
	def __enter( self ) :
		self.show()

	def __leave( self ) :
		self.__fader.value = 0
		BigWorld.callback( self.__cc_fade_speed, self.hide )

	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def onButtonClick( self, pyBtn ) :
		pyBtn.handler()

	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@reimpl_login.deco_guiRoleSelectorOnStatusChanged
	def afterStatusChanged( self, oldStatus, newStatus ) :
		if newStatus == Define.GST_ROLE_SELECT and \
			( oldStatus == Define.GST_ENTER_ROLESELECT_LOADING or \
			oldStatus == Define.GST_BACKTO_ROLESELECT_LOADING or \
			oldStatus == Define.GST_ROLE_CREATE ) :
				self.show()
		elif self.visible and newStatus != Define.GST_OFFLINE :
			self.hide()

	def show( self ) :
		self.__registerControlTriggers()
		self.__fader.value = 1
		RootGUI.show( self )
		rds.roleSelector.unlockContrl()
		self.__pyBtnCreate.enable = True
		self.__pyBtnBack.enable = True

	def hide( self ) :
		if self.visible:
			self.__deregisterControlTriggers()
		RootGUI.hide( self )

	# ----------------------------------------------------------------
	# private button handlers
	# ----------------------------------------------------------------
	def __toNextRoles( self ) :
		"""
		下一组角色
		"""
		rds.roleSelector.nextGroup()

	def __renameRole( self ) :
		"""
		重命名角色
		"""
		def callback( res, text ) :
			if res == DialogResult.OK :
				rds.roleSelector.renameSelRole( text )
			rds.roleSelector.unlockContrl()
		rds.roleSelector.lockContrl()
		msg = labelGather.getText( "RoleSelector:main", "renameTitle" )
		InputBox().show( msg, callback, self )

	def __createRole( self ) :
		if not self.visible : return False
		if not self.__pyBtnCreate.enable : return False
		if roleSelector.getRoleCount() >= csconst.LOGIN_ROLE_UPPER_LIMIT :
			def query( rs_id ):
				rds.roleSelector.unlockContrl()
			rds.roleSelector.lockContrl()
			# "存在角色数量已经达到上限！"
			showAutoHideMessage( 3.0, 0x0b62, "", MB_OK, query )
			return False
		roleSelector.createRole()
		return True

	def __deleteRole( self ) :
		if not self.visible : return False
		if not self.__pyBtnDel.enable : return False
		roleInfo = roleSelector.getSelectedRoleInfo()
		if roleInfo is None :
			# "请选择一个角色！"
			showAutoHideMessage( 3.0, 0x0b63, "", pyOwner = self )
			return
		def query( result, text ) :
			if result == DialogResult.OK:								# 如果点击确定
				if text.lower() == "delete":
					roleID = roleInfo.getID()
					roleName = roleInfo.getName()
					roleSelector.deleteRole( roleID, roleName )					# 角色删除
					rds.roleSelector.unlockContrl()
				else :
					def queryTemp( rs_id ):
						rds.roleSelector.unlockContrl()
					rds.roleSelector.lockContrl()
					# "输入错误，删除取消"
					showAutoHideMessage( 3.0, 0x0b64, "", MB_OK, queryTemp )
			else:
				rds.roleSelector.unlockContrl() # 按下“取消”键时还原界面各按钮的可点击状态

		rds.roleSelector.lockContrl()
		tip = labelGather.getText( "RoleSelector:main", "delRoleTip" )
		tip = tip % ( roleInfo.getName(), roleInfo.getLevel(), roleInfo.getCHClass() )
		RoleDelVerifier().show( tip, query, self )						# 显示角色删除确定界面
		return True

	def __chooseServer( self, pyBtn ) :
		if pyBtn.visible :
			rds.gameMgr.accountLogoff()

	def __quitGame( self ) :
		rds.gameMgr.quitGame()

	def __enterGame( self ) :
		"""
		choose a role and enter world
		"""
		if not self.visible : return False
		if not self.__pyBtnEnterGame.enable : return False
		roleInfo = roleSelector.getSelectedRoleInfo()
		if roleInfo is None :
			# "请选择一个角色！"
			showAutoHideMessage( 3.0, 0x0b63, "", MB_OK, pyOwner = self )
		else :
			rds.roleSelector.lockContrl()
			roleSelector.enterGame()
		return True
