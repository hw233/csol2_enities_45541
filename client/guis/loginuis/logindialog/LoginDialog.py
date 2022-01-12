# -*- coding: gb18030 -*-
#
# $Id: LoginDialog.py,v 1.38 2008-07-25 07:48:17 huangyongwei Exp $

"""
do login dialog class
"""

import os
import hashlib
import Define
import event.EventCenter as ECenter
import MessageBox
from AbstractTemplates import Singleton
from gbref import rds
from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.common.RootGUI import RootGUI
from guis.controls.TextBox import TextBox
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.controls.ListPanel import ListPanel
from guis.controls.ListItem import SingleColListItem
from guis.controls.ProgressBar import HProgressBar
from guis.controls.CheckBox import CheckBoxEx
from guis.controls.RadioButton import RadioButtonEx
from guis.controls.CheckerGroup import CheckerGroup
from guis.tooluis.CSRichText import CSRichText
from guis.controls.TabSwitcher import TabSwitcher
from guis.tooluis.keyboard.Keyboard import Keyboard
from config.client.msgboxtexts import Datas as mbmsgs
from Guarder import Guarder
from FellInNotifier import FellInNotifier

# --------------------------------------------------------------------
# 登录窗口
# --------------------------------------------------------------------
class LoginDialog( RootGUI ) :
	__cc_fade_speed = 0.6
	__cc_max_input_length = 16

	def __init__( self ) :
		wnd = GUI.load( "guis/loginuis/logindialog/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		self.focus = False
		self.moveFocus = False
		self.escHide_ = False
		self.h_dockStyle = "HFILL"
		self.v_dockStyle = "VFILL"
		self.__initialize( wnd )
		self.__readyCallback = None
		self.__allowEnable = True				# 是否允许界面可用
		#BigWorld.callback( 2.0, self.__initAutoShow )
		self.__triggers = {}
		self.__registerTriggers()

	def __initialize( self, wnd ) :
		self.__fader = wnd.fader
		self.__fader.speed = self.__cc_fade_speed

		self.__pyBPanel = PyGUI( wnd.bPanel )								# 底部板面
		self.__pyRPanel = PyGUI( wnd.rPanel )								# 左下角板面

		self.__pyInfoBg = PyGUI( wnd.infobg )								# 登录信息板面
		self.__pyInfoBg.h_dockStyle = "CENTER"
		self.__pyInfoBg.v_dockStyle = "MIDDLE"

		self.__pyTBAct = TextBox( wnd.infobg.tbAccount )					# 输入账号文本框
		self.__pyTBAct.filterChars = [' ', ]								# 不允许空格
		self.__pyTBAct.maxLength = self.__cc_max_input_length				# 账号最大长度
		self.__pyTBAct.font = "system_small.font"
		self.__pyTBAct.onTextChanged.bind( self.__onTBActTextChanged )
		self.__pyTBAct.onTabIn.bind( self.__onTextBoxTabIn )
		self.__pyTBAct.onTabOut.bind( self.__onTextBoxTabOut )

		self.__pyBtnPasswd = TextBox( wnd.infobg.tbPasswd )					# 密码输入框
		self.__pyBtnPasswd.inputMode = InputMode.PASSWORD
		self.__pyBtnPasswd.passwordChar = '*'								# 密码掩码字符
		self.__pyBtnPasswd.maxLength = self.__cc_max_input_length
		self.__pyBtnPasswd.font = "system_small.font"
		self.__pyBtnPasswd.onTabIn.bind( self.__onTextBoxTabIn )
		self.__pyBtnPasswd.onTabOut.bind( self.__onTextBoxTabOut )

		self.__pyBtnKeyboard = Button( wnd.infobg.btnKeyboard )				# 打开虚拟键盘按钮
		self.__pyBtnKeyboard.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnKeyboard.onLClick.bind( self.__showKeyboard )

		self.__pyBtnTel = Button( wnd.bPanel.btnTel )						# 电话绑定按钮
		self.__pyBtnTel.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnTel.enable = False
		self.__pyBtnTel.onLClick.bind( self.__phoneBindSecret )

		self.__pyBtnCard = Button( wnd.bPanel.btnCard )						# 绑定保密卡按钮
		self.__pyBtnCard.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCard.onLClick.bind( self.__cardBindSecret )

		self.__pyRTTips = CSRichText( wnd.bPanel.rtTips )					# 电话号码提示标签
		self.__pyRTTips.spacing = 0

		# -----------------------------------
		self.__pbbg = wnd.infobg.elements["pbBg"]							# 登录进度条
		self.__pbbg.visible = False
		self.__pyPBInit = HProgressBar( wnd.infobg.pbInit )
		self.__pyPBInit.speed = 0.6
		self.__pyPBInit.onCurrentValueChanged.bind( self.__onPBCurrValueChanged )
		
		self.__pyRtAgeWarn = CSRichText( wnd.infobg.rtAgeWarn )
		self.__pyRtAgeWarn.align = "C"

		# -----------------------------------
		self.__pyCBRem = CheckBoxEx( wnd.infobg.cbRem )						# 是否保存复选框
		self.__pyCBRem.onCheckChanged.bind( self.__onCBSaveCheckedChanged )

		self.__pyRBTel = RadioButtonEx( wnd.bPanel.rbTel )					# 电话登录单选扭
		self.__pyRBTel.enable = False
		self.__pyRBCard = RadioButtonEx( wnd.bPanel.rbCard )				# 密码卡登录单选扭
		self.__pyRBCard.enable = False
		self.__rbLoginArray = CheckerGroup()
		self.__rbLoginArray.addCheckers( self.__pyRBTel, self.__pyRBCard )
#		self.__rbLoginArray.onCheckChanged.bind( self.__onAgeChanged )

		# -----------------------------------
		self.__pyBtnEnter = Button( wnd.infobg.btnEnter )					# 登录按钮
		self.__pyBtnEnter.onLClick.bind( self.__login )
		self.__pyBtnEnter.setStatesMapping( UIState.MODE_R4C1 )
		self.setOkButton( self.__pyBtnEnter )

		self.__pyBtnCharge = HButtonEx( wnd.rPanel.btnCharge )					# 充值按钮
		self.__pyBtnCharge.h_dockStyle = "S_RIGHT"
		self.__pyBtnCharge.v_dockStyle = "S_BOTTOM"
		self.__pyBtnCharge.onLClick.bind( self.__spend )
		self.__pyBtnCharge.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCharge.enable = False

		self.__pyBtnBack = HButtonEx( wnd.rPanel.btnBack )						# 上一步按钮
		self.__pyBtnBack.h_dockStyle = "S_RIGHT"
		self.__pyBtnBack.v_dockStyle = "S_BOTTOM"
		self.__pyBtnBack.onLClick.bind( self.__back )
		self.__pyBtnBack.setExStatesMapping( UIState.MODE_R4C1 )

		self.__pyBtnQuit = HButtonEx( wnd.rPanel.btnQuit )						# 退出按钮
		self.__pyBtnQuit.h_dockStyle = "S_LEFT"
		self.__pyBtnQuit.v_dockStyle = "S_BOTTOM"
		self.__pyBtnQuit.onLClick.bind( self.__quitGame )
		self.__pyBtnQuit.setExStatesMapping( UIState.MODE_R4C1 )

		self.__pyBtnReg = HButtonEx( wnd.rPanel.btnReg )						# 账号注册
		self.__pyBtnReg.h_dockStyle = "S_LEFT"
		self.__pyBtnReg.v_dockStyle = "S_BOTTOM"
		self.__pyBtnReg.onLClick.bind( self.__register )
		self.__pyBtnReg.setExStatesMapping( UIState.MODE_R4C1 )

		# -----------------------------------
		self.tabSwitcher = TabSwitcher( [self.__pyTBAct, self.__pyBtnPasswd] )	# 焦点转移控件

		accountName = rds.gameMgr.getGlobalOption( "historyAccount" )		# 获取纪录账号标记
		if accountName == "" :
			self.__pyCBRem.checked = False
		else :
			self.__pyTBAct.text = accountName
			self.__pyCBRem.checked = True

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setPyBgLabel( self.__pyBtnQuit, "LoginDialog:main", "btnQuit" )

		labelGather.setLabel( wnd.infobg.stAccount, "LoginDialog:main", "stAccount" )
		labelGather.setLabel( wnd.infobg.stPasswd, "LoginDialog:main", "stPasswd" )
		labelGather.setPyBgLabel( self.__pyRBTel, "LoginDialog:main", "rbTel" )
		labelGather.setPyBgLabel( self.__pyRBCard, "LoginDialog:main", "rbCard" )
		labelGather.setPyBgLabel( self.__pyBtnTel, "LoginDialog:main", "btnTel" )
		labelGather.setPyBgLabel( self.__pyBtnCard, "LoginDialog:main", "btnCard" )
		labelGather.setPyBgLabel( self.__pyRTTips, "LoginDialog:main", "rtTips" )

		labelGather.setPyBgLabel( self.__pyBtnReg, "LoginDialog:main", "btnReg" )
		labelGather.setPyBgLabel( self.__pyBtnCharge, "LoginDialog:main", "btnCharge" )
		labelGather.setPyBgLabel( self.__pyBtnBack, "LoginDialog:main", "btnBack" )
		labelGather.setPyBgLabel( self.__pyRtAgeWarn, "LoginDialog:main", "rtAgeWarn" )
		labelGather.setPyBgLabel( self.__pyBtnEnter, "LoginDialog:main", "btnEnter" )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_RESOLUTION_CHANGED"]		= self.__onResolutionChanged
		self.__triggers["EVT_ON_BEGIN_ENTER_RS_LOADING"]	= self.__onLoadRoleSelect
		self.__triggers["EVT_ON_BREAK_LOADING"]				= self.__onBreakLoading
		self.__triggers["EVT_ON_LOGIN_FAIL"]				= self.__onLoginFail
		self.__triggers["EVT_ON_LOST_CONTROL"]				= self.__onLostControl
		self.__triggers["EVT_ON_GOT_CONTROL"]				= self.__onGotControl
		self.__triggers["EVT_ON_LOGIN_WAIT"]				= self.__onLoginWait
		self.__triggers["EVT_ON_LOGIN_SUCCESS"]				= self.__onLoginSuccess

		self.__triggers["EVT_ON_SHOW_ACCOUNT_GUARDER"]		= self.__onShowAccountGuarder

		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )

	# -------------------------------------------------
	def __layout( self ) :
		width, height = BigWorld.screenSize()
		self.__pyRPanel.right = width
		self.__pyRPanel.bottom = height
		self.__pyBPanel.bottom = height
		self.__pyBPanel.center = self.__pyInfoBg.center

	def __initAutoShow( self ):
		showAutoHideMessage( 2.0, "", "", MB_OK ).pos = ( -305.0, -140.0 )

	# -------------------------------------------------
	def __detectProgress( self, progress ) :
		self.__pyPBInit.value = progress

	def __onPBCurrValueChanged( self, currValue ) :
		if currValue != 1 : return
		if self.__readyCallback is not None :
			self.__readyCallback()
			self.hide()

	# -------------------------------------------------
	def __onAgeChanged( self, pyRadio ) :
		self.__pyBtnEnter.enable = self.__pyRBMajor.checked

	def __saveAccount( self ) :
		userName = ""
		if self.__pyCBRem.checked :
			userName = self.__pyTBAct.text.strip()
		rds.gameMgr.setGlobalOption( "historyAccount", userName )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def __onResolutionChanged( self, preReso ) :
		"""
		屏幕分辨率改变时被调用
		"""
		self.__layout()

	def __onLoadRoleSelect( self, resLoader, callback ) :
		if rds.statusMgr.lastStatus() != Define.GST_LOGIN :
			return
		rds.ccursor.lock( "wait" )								# 锁定鼠标为等待标志
		self.__pbbg.visible = True
		self.enable = False
		self.__readyCallback = callback
		resLoader.setNotifier( self.__detectProgress )

	def __onBreakLoading( self ) :
		if self.visible :
			rds.ccursor.unlock( "wait", "normal" )				# 解除锁定鼠标
			self.__pyPBInit.reset( self.__pyPBInit.currValue )

	def __onLoginFail( self, msg ) :
		def callback( res ) :
			self.__pbbg.visible = False
			self.__pyPBInit.reset( 0 )
			self.enable = True
		self.enable = False
		showMessage( msg, "", MB_OK, callback, self )
		rds.ccursor.unlock( "wait", "normal" )					# 解除锁定鼠标

	def __onLoginWait( self, waitOrder, waitTime ):
		"""
		登录排队等待
		"""
		def callback( res ):
			self.enable = True

		if waitTime < 60:
			# "已提交您的登入申请。目前你排在第%i位，等待时间少于一分钟。"
			msg = mbmsgs[0x0b42] % waitOrder
		else:
			# "已提交您的登入申请。目前你排在第%i位，大概需要等待%i分钟。"
			msg = mbmsgs[0x0b43] % ( waitOrder, int( waitTime / 60 ) )
		FellInNotifier.show( msg, "", callback, self )

	def __onLoginSuccess( self ):
		"""
		登录成功
		"""
		self.__allowEnable = False
		FellInNotifier.hide()

	def __onShowAccountGuarder( self, pswSegs, state ) :
		"""
		显示密保输入界面
		"""
		def callback( res, psw ) :
			if res == DialogResult.OK :
				BigWorld.player().check_passwdProMatrixValue( psw )
			else :
				self.__allowEnable = True
				self.enable = True
				BigWorld.disconnect()
		self.enable = False
		self.__allowEnable = False
		if Guarder.insted :
			Guarder().resetSitesOfMatrix( pswSegs )
		else :
			Guarder().show( pswSegs, callback, self )

	def __onLostControl( self ) :
		self.enable = False

	def __onGotControl( self ) :
		if self.__allowEnable :
			self.enable = True

	# -------------------------------------------------
	def __login( self ) :
		servers = rds.gameMgr.getServers()
		if len( servers ) == 0 :
			ERROR_MSG( "no server to choice for login!" )
			return
		userName = self.__pyTBAct.text.strip()
		md5Psw = hashlib.md5( self.__pyBtnPasswd.text ).hexdigest()
		if userName == "" :
			if self.__pyTBAct.tabStop :
				# "请输入账号和密码!"
				showAutoHideMessage( 3.0, 0x0b44, "", pyOwner = self )
			else :
				self.__pyTBAct.tabStop = True
		else :
			self.__saveAccount()
			rds.loginer.requestLogin( servers[0], userName, md5Psw )
			self.enable = False

	def __quitGame( self ) :
		rds.gameMgr.quitGame( True )

	def __register( self ) :
		"""
		注册账号
		"""
		csol.openUrl( "http://www.gyyx.cn/member/MyRegister1.aspx" )

	def __spend( self ) :
		"""
		充值
		"""
		csol.openUrl( "http://www.cogame.cn" )

	def __back( self ) :
		"""
		上一步
		"""
		try :
			path = "%s\\launcher.exe" % os.getcwd()
			os.startfile( path )
		except WindowsError :
			# "找不到 launcher"
			showAutoHideMessage( 1.0, 0x0b45, "", MB_OK, pyOwner = self )
			return
		rds.gameMgr.quitGame( False )

	# -------------------------------------------------
	def __onTBActTextChanged( self ) :
		"""
		输入账号过程中被触发
		"""
		self.__saveAccount()

	def __onTextBoxTabIn( self, pyCon ) :
		"""
		输入框活得焦点被触发
		"""
		pyCon.foreColor = 255, 255, 255, 255

	def __onTextBoxTabOut( self, pyCon ) :
		"""
		输入框拾取焦点被触发
		"""
		pyCon.foreColor = 255, 255, 255, 220

	# -------------------------------------------------
	def __onCBSaveCheckedChanged( self, checked ) :
		"""
		是否保存账号信息
		"""
		self.__saveAccount()

	def __showKeyboard( self ) :
		"""
		显示小键盘
		"""
		keyboard = Keyboard()
		if keyboard.visible :
			keyboard.hide()
		else :
			keyboard.show( self )
			keyboard.center = self.__pyInfoBg.centerToScreen

	def __showHelp( self ) :
		"""
		显示帮助
		"""
		# "此功能未开通"
		showAutoHideMessage( 1.0, 0x0b46, "", MB_OK, pyOwner = self )

	def __phoneBindSecret( self ) :
		"""
		电话绑定保密
		"""
		# "此功能未开通"
		showAutoHideMessage( 1.0, 0x0b46, "", MB_OK, pyOwner = self )

	def __cardBindSecret( self ) :
		"""
		卡绑定保密
		"""
		csol.openUrl( "http://security.gyyx.cn/Matrix/BindMatrix.aspx" )


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onActivated( self ) :
		"""
		当窗口激活时被调用
		"""
		RootGUI.onActivated( self )
		self.__pyTBAct.tabStop = True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	# -------------------------------------------------
	def show( self ) :
		self.__registerTriggers()
		self.__pyPBInit.reset( 0 )
		self.enable = True
		self.__pbbg.visible = False
		self.__fader.value = 1
		self.__fader.reset()
		self.__layout()
		RootGUI.show( self )
		self.__pyTBAct.tabStop = True

	def hide( self ) :
		rds.ccursor.unlock( "wait", "normal" )		# 解除锁定鼠标
		self.__pyBtnPasswd.text = "" 				# 清空登录密码
		self.__fader.value = 0
		if Keyboard.insted :
			Keyboard().hide()
		func = Functor( RootGUI.hide, self )
		BigWorld.callback( self.__cc_fade_speed, func )
		self.__deregisterTriggers()

	# -------------------------------------------------
	def beforeStatusChanged( self, oldStatus, newStatus ) :
		if newStatus == Define.GST_LOGIN :
			self.__allowEnable = True
			self.show()
