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
# ��¼����
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
		self.__allowEnable = True				# �Ƿ�����������
		#BigWorld.callback( 2.0, self.__initAutoShow )
		self.__triggers = {}
		self.__registerTriggers()

	def __initialize( self, wnd ) :
		self.__fader = wnd.fader
		self.__fader.speed = self.__cc_fade_speed

		self.__pyBPanel = PyGUI( wnd.bPanel )								# �ײ�����
		self.__pyRPanel = PyGUI( wnd.rPanel )								# ���½ǰ���

		self.__pyInfoBg = PyGUI( wnd.infobg )								# ��¼��Ϣ����
		self.__pyInfoBg.h_dockStyle = "CENTER"
		self.__pyInfoBg.v_dockStyle = "MIDDLE"

		self.__pyTBAct = TextBox( wnd.infobg.tbAccount )					# �����˺��ı���
		self.__pyTBAct.filterChars = [' ', ]								# ������ո�
		self.__pyTBAct.maxLength = self.__cc_max_input_length				# �˺���󳤶�
		self.__pyTBAct.font = "system_small.font"
		self.__pyTBAct.onTextChanged.bind( self.__onTBActTextChanged )
		self.__pyTBAct.onTabIn.bind( self.__onTextBoxTabIn )
		self.__pyTBAct.onTabOut.bind( self.__onTextBoxTabOut )

		self.__pyBtnPasswd = TextBox( wnd.infobg.tbPasswd )					# ���������
		self.__pyBtnPasswd.inputMode = InputMode.PASSWORD
		self.__pyBtnPasswd.passwordChar = '*'								# ���������ַ�
		self.__pyBtnPasswd.maxLength = self.__cc_max_input_length
		self.__pyBtnPasswd.font = "system_small.font"
		self.__pyBtnPasswd.onTabIn.bind( self.__onTextBoxTabIn )
		self.__pyBtnPasswd.onTabOut.bind( self.__onTextBoxTabOut )

		self.__pyBtnKeyboard = Button( wnd.infobg.btnKeyboard )				# ��������̰�ť
		self.__pyBtnKeyboard.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnKeyboard.onLClick.bind( self.__showKeyboard )

		self.__pyBtnTel = Button( wnd.bPanel.btnTel )						# �绰�󶨰�ť
		self.__pyBtnTel.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnTel.enable = False
		self.__pyBtnTel.onLClick.bind( self.__phoneBindSecret )

		self.__pyBtnCard = Button( wnd.bPanel.btnCard )						# �󶨱��ܿ���ť
		self.__pyBtnCard.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCard.onLClick.bind( self.__cardBindSecret )

		self.__pyRTTips = CSRichText( wnd.bPanel.rtTips )					# �绰������ʾ��ǩ
		self.__pyRTTips.spacing = 0

		# -----------------------------------
		self.__pbbg = wnd.infobg.elements["pbBg"]							# ��¼������
		self.__pbbg.visible = False
		self.__pyPBInit = HProgressBar( wnd.infobg.pbInit )
		self.__pyPBInit.speed = 0.6
		self.__pyPBInit.onCurrentValueChanged.bind( self.__onPBCurrValueChanged )
		
		self.__pyRtAgeWarn = CSRichText( wnd.infobg.rtAgeWarn )
		self.__pyRtAgeWarn.align = "C"

		# -----------------------------------
		self.__pyCBRem = CheckBoxEx( wnd.infobg.cbRem )						# �Ƿ񱣴渴ѡ��
		self.__pyCBRem.onCheckChanged.bind( self.__onCBSaveCheckedChanged )

		self.__pyRBTel = RadioButtonEx( wnd.bPanel.rbTel )					# �绰��¼��ѡŤ
		self.__pyRBTel.enable = False
		self.__pyRBCard = RadioButtonEx( wnd.bPanel.rbCard )				# ���뿨��¼��ѡŤ
		self.__pyRBCard.enable = False
		self.__rbLoginArray = CheckerGroup()
		self.__rbLoginArray.addCheckers( self.__pyRBTel, self.__pyRBCard )
#		self.__rbLoginArray.onCheckChanged.bind( self.__onAgeChanged )

		# -----------------------------------
		self.__pyBtnEnter = Button( wnd.infobg.btnEnter )					# ��¼��ť
		self.__pyBtnEnter.onLClick.bind( self.__login )
		self.__pyBtnEnter.setStatesMapping( UIState.MODE_R4C1 )
		self.setOkButton( self.__pyBtnEnter )

		self.__pyBtnCharge = HButtonEx( wnd.rPanel.btnCharge )					# ��ֵ��ť
		self.__pyBtnCharge.h_dockStyle = "S_RIGHT"
		self.__pyBtnCharge.v_dockStyle = "S_BOTTOM"
		self.__pyBtnCharge.onLClick.bind( self.__spend )
		self.__pyBtnCharge.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCharge.enable = False

		self.__pyBtnBack = HButtonEx( wnd.rPanel.btnBack )						# ��һ����ť
		self.__pyBtnBack.h_dockStyle = "S_RIGHT"
		self.__pyBtnBack.v_dockStyle = "S_BOTTOM"
		self.__pyBtnBack.onLClick.bind( self.__back )
		self.__pyBtnBack.setExStatesMapping( UIState.MODE_R4C1 )

		self.__pyBtnQuit = HButtonEx( wnd.rPanel.btnQuit )						# �˳���ť
		self.__pyBtnQuit.h_dockStyle = "S_LEFT"
		self.__pyBtnQuit.v_dockStyle = "S_BOTTOM"
		self.__pyBtnQuit.onLClick.bind( self.__quitGame )
		self.__pyBtnQuit.setExStatesMapping( UIState.MODE_R4C1 )

		self.__pyBtnReg = HButtonEx( wnd.rPanel.btnReg )						# �˺�ע��
		self.__pyBtnReg.h_dockStyle = "S_LEFT"
		self.__pyBtnReg.v_dockStyle = "S_BOTTOM"
		self.__pyBtnReg.onLClick.bind( self.__register )
		self.__pyBtnReg.setExStatesMapping( UIState.MODE_R4C1 )

		# -----------------------------------
		self.tabSwitcher = TabSwitcher( [self.__pyTBAct, self.__pyBtnPasswd] )	# ����ת�ƿؼ�

		accountName = rds.gameMgr.getGlobalOption( "historyAccount" )		# ��ȡ��¼�˺ű��
		if accountName == "" :
			self.__pyCBRem.checked = False
		else :
			self.__pyTBAct.text = accountName
			self.__pyCBRem.checked = True

		# ---------------------------------------------
		# ���ñ�ǩ
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
		��Ļ�ֱ��ʸı�ʱ������
		"""
		self.__layout()

	def __onLoadRoleSelect( self, resLoader, callback ) :
		if rds.statusMgr.lastStatus() != Define.GST_LOGIN :
			return
		rds.ccursor.lock( "wait" )								# �������Ϊ�ȴ���־
		self.__pbbg.visible = True
		self.enable = False
		self.__readyCallback = callback
		resLoader.setNotifier( self.__detectProgress )

	def __onBreakLoading( self ) :
		if self.visible :
			rds.ccursor.unlock( "wait", "normal" )				# ����������
			self.__pyPBInit.reset( self.__pyPBInit.currValue )

	def __onLoginFail( self, msg ) :
		def callback( res ) :
			self.__pbbg.visible = False
			self.__pyPBInit.reset( 0 )
			self.enable = True
		self.enable = False
		showMessage( msg, "", MB_OK, callback, self )
		rds.ccursor.unlock( "wait", "normal" )					# ����������

	def __onLoginWait( self, waitOrder, waitTime ):
		"""
		��¼�Ŷӵȴ�
		"""
		def callback( res ):
			self.enable = True

		if waitTime < 60:
			# "���ύ���ĵ������롣Ŀǰ�����ڵ�%iλ���ȴ�ʱ������һ���ӡ�"
			msg = mbmsgs[0x0b42] % waitOrder
		else:
			# "���ύ���ĵ������롣Ŀǰ�����ڵ�%iλ�������Ҫ�ȴ�%i���ӡ�"
			msg = mbmsgs[0x0b43] % ( waitOrder, int( waitTime / 60 ) )
		FellInNotifier.show( msg, "", callback, self )

	def __onLoginSuccess( self ):
		"""
		��¼�ɹ�
		"""
		self.__allowEnable = False
		FellInNotifier.hide()

	def __onShowAccountGuarder( self, pswSegs, state ) :
		"""
		��ʾ�ܱ��������
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
				# "�������˺ź�����!"
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
		ע���˺�
		"""
		csol.openUrl( "http://www.gyyx.cn/member/MyRegister1.aspx" )

	def __spend( self ) :
		"""
		��ֵ
		"""
		csol.openUrl( "http://www.cogame.cn" )

	def __back( self ) :
		"""
		��һ��
		"""
		try :
			path = "%s\\launcher.exe" % os.getcwd()
			os.startfile( path )
		except WindowsError :
			# "�Ҳ��� launcher"
			showAutoHideMessage( 1.0, 0x0b45, "", MB_OK, pyOwner = self )
			return
		rds.gameMgr.quitGame( False )

	# -------------------------------------------------
	def __onTBActTextChanged( self ) :
		"""
		�����˺Ź����б�����
		"""
		self.__saveAccount()

	def __onTextBoxTabIn( self, pyCon ) :
		"""
		������ý��㱻����
		"""
		pyCon.foreColor = 255, 255, 255, 255

	def __onTextBoxTabOut( self, pyCon ) :
		"""
		�����ʰȡ���㱻����
		"""
		pyCon.foreColor = 255, 255, 255, 220

	# -------------------------------------------------
	def __onCBSaveCheckedChanged( self, checked ) :
		"""
		�Ƿ񱣴��˺���Ϣ
		"""
		self.__saveAccount()

	def __showKeyboard( self ) :
		"""
		��ʾС����
		"""
		keyboard = Keyboard()
		if keyboard.visible :
			keyboard.hide()
		else :
			keyboard.show( self )
			keyboard.center = self.__pyInfoBg.centerToScreen

	def __showHelp( self ) :
		"""
		��ʾ����
		"""
		# "�˹���δ��ͨ"
		showAutoHideMessage( 1.0, 0x0b46, "", MB_OK, pyOwner = self )

	def __phoneBindSecret( self ) :
		"""
		�绰�󶨱���
		"""
		# "�˹���δ��ͨ"
		showAutoHideMessage( 1.0, 0x0b46, "", MB_OK, pyOwner = self )

	def __cardBindSecret( self ) :
		"""
		���󶨱���
		"""
		csol.openUrl( "http://security.gyyx.cn/Matrix/BindMatrix.aspx" )


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onActivated( self ) :
		"""
		�����ڼ���ʱ������
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
		rds.ccursor.unlock( "wait", "normal" )		# ����������
		self.__pyBtnPasswd.text = "" 				# ��յ�¼����
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
