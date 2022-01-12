# -*- coding: gb18030 -*-

"""
2009.10.14: writen by hyw
"""

import math
import csol
import keys
import Const
from AbstractTemplates import Singleton
from guis import *
from LabelGather import labelGather
from event import EventCenter as ECenter
from guis.common.GUIBaseObject import GUIBaseObject
from guis.common.Window import Window
from guis.controls.Control import Control
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.CSRichText import CSRichText
from guis.controls.StaticText import StaticText
from guis.controls.TextBox import TextBox
from config.client.msgboxtexts import Datas as mbmsgs


class Guarder( Singleton, Window ) :
	__cc_one_of_ten_radian		= math.pi * 0.2						# ʮ��֮һԲ�ܣ�ÿ����ť�ļ���Ƕȣ�
	__cc_rotate_interval		= 0.004								# ��תʱ����

	def __init__( self ) :
		wnd = GUI.load( "guis/loginuis/logindialog/guarder/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.movable_ = False
		self.escHide_ = False
		self.addToMgr()
		self.__pyRTTips = CSRichText( wnd.rtTips )
		self.__pyRTTips.foreColor = 144, 255, 36
		self.__pyRTTips.text = labelGather.getLabel( "LoginDialog:guarder", "tips" ).text
		self.__pyRTAdvice = CSRichText( wnd.rtAdvice )
		self.__pyRTAdvice.foreColor = 255, 250, 190
		self.__pyRTAdvice.text = labelGather.getLabel( "LoginDialog:guarder", "advice" ).text

		self.pyBtnClear_ = HButtonEx( wnd.btnClear )					# �����ť
		self.pyBtnClear_.setExStatesMapping( UIState.MODE_R3C1 )
		self.pyBtnClear_.onLClick.bind( self.onClearClick_ )
		self.pyBtnOk_ = HButtonEx( wnd.btnOk )							# ȷ����ť
		self.pyBtnOk_.enable = False
		self.pyBtnOk_.setExStatesMapping( UIState.MODE_R3C1 )
		self.pyBtnOk_.onLClick.bind( self.onOkClick_ )
		self.pyBtnCancel_ = HButtonEx( wnd.btnCancel )					# ȡ����ť
		self.pyBtnCancel_.setExStatesMapping( UIState.MODE_R3C1 )
		self.pyBtnCancel_.onLClick.bind( self.onCancelClick_ )
		labelGather.setLabel( wnd.lbTitle, "LoginDialog:guarder", "title" )
		labelGather.setPyBgLabel( self.pyBtnClear_, "LoginDialog:guarder", "btnClear" )
		labelGather.setPyBgLabel( self.pyBtnOk_, "LoginDialog:guarder", "btnOk" )
		labelGather.setPyBgLabel( self.pyBtnCancel_, "LoginDialog:guarder", "btnCancel" )

		self.pyPswArea_ = PasswdArea( self,
			wnd.pswArea1,											# ��������1
			wnd.pswArea2,											# ��������2
			wnd.pswArea3 )											# ��������3

		self.pyNumsPanel_ = Control( wnd.numPanel )					# ���ְ�ť����
		self.__npCPos = wnd.numPanel.size * 0.5						# ���ְ�ť��������λ��
		self.__nbRadius = wnd.numPanel.width / 3					# ���ְ�ťΧ�ɵ�Բ�İ뾶
		self.pyNumBtns_ = []										# ���ְ�ť
		self.__initNumBtns()										# ��ʼ�����ְ�ť

		self.__rotateSpeed = 0										# ��ת�ٶ�
		self.__cucrrRadium = 0.0									# ��ǰ�Ƕ�
		self.__rotateCBID = 0										# ��ת��ť�� callback ID
		self.__layoutNumBtns( self.__cucrrRadium )

		self.__callback = None
		self.__triggers = {}
		self.__registerEvents()

	def __del__( self ) :
		Window.__del__( self )
		if Debug.output_LoginDialogGuarder :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerEvents( self ) :
		self.__triggers["EVT_ON_PASSED_ACCOUNT_GUARDER"] = self.__onPassedAccountGuard
		self.__triggers["EVT_ON_LOST_ACCOUNT_GUARDER"] = self.__onLostAccountGuard
		self.__triggers["EVT_ON_KICKOUT_OVERTIME"] = self.__onKickoutOvertime
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __unregisterEvents( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )
		del self.__triggers

	# -------------------------------------------------
	def __initNumBtns( self ) :
		"""
		��ʼ���������ְ�ť
		"""
		btn = GUI.load( "guis/loginuis/logindialog/guarder/btn_num.gui" )
		uiFixer.firstLoadFix( btn )
		for idx in xrange( 10 ) :
			pyBtnNum = NumButton( btn )
			pyBtnNum.strNumber = str( idx )
			pyBtnNum.text = pyBtnNum.strNumber
			pyBtnNum.mapKey = getattr( keys, "KEY_%i" % idx )
			pyBtnNum.onLClick.bind( self.onNumBtnClick_ )
			pyBtnNum.onMouseEnter.bind( self.onNumBtnMouseEnter_ )
			pyBtnNum.onMouseLeave.bind( self.onNumBtnMouseLeave_ )
			self.pyNumsPanel_.addPyChild( pyBtnNum )
			pyBtnNum.setStatesMapping( UIState.MODE_R2C2 )
			pyBtnNum.isOffsetText = True
			self.pyNumBtns_.append( pyBtnNum )
			btn = util.copyGuiTree( btn )

	def __showNumTextes( self ) :
		"""
		��ʾ�������ּ����ı�
		"""
		for pyBtn in self.pyNumBtns_ :
			pyBtn.text = pyBtn.strNumber

	def __hideNumTextes( self ) :
		"""
		�����������ּ����ı�
		"""
		for pyBtn in self.pyNumBtns_ :
			pyBtn.text = ""

	# -------------------------------------------------
	def __pointInCircle( self, radian ) :
		"""
		���ݸ������ȼ�����Բ���ϵĵ�����꣨ע�⣺��ʼλ����ƽ�� X �ᣬ���ҷ������ң�
		"""
		x = -self.__nbRadius * math.sin( radian )
		y = self.__nbRadius * math.cos( radian )
		return Math.Vector2( x, y ) + self.__npCPos

	def __layoutNumBtns( self, radian ) :
		"""
		�����������ְ�ť
		"""
		for idx, pyBtn in enumerate( self.pyNumBtns_ ) :
			nRadian = radian + idx * self.__cc_one_of_ten_radian
			pyBtn.centerPos = self.__pointInCircle( nRadian )

	# ---------------------------------------
	def __calcRotateSpeed( self ) :
		"""
		������ת�ٶ�
		"""
		npPos = self.pyNumsPanel_.posToScreen					# ���ְ�ť���������Ļ��λ��
		cPos = npPos + self.__npCPos							# Բ�������Ļ��λ��
		mPos = Math.Vector2( csol.pcursorPosition() )			# ���λ��
		mDist = mPos.distTo( cPos )								# ��굽Բ�ľ���
		mDistArc = mDist - self.__nbRadius						# ��굽Բ������
		self.__rotateSpeed = 0.1 * mDistArc / 1024				# ��ת�ٶ�( 512 Ϊ 1024 �� 768 �ֱ�������Ļһ����)

	def __rotateNumBtns( self ) :
		"""
		��ת���ְ�ť
		"""
		self.__calcRotateSpeed()
		self.__layoutNumBtns( self.__cucrrRadium )
		self.__cucrrRadium += self.__rotateSpeed
		BigWorld.cancelCallback( self.__rotateCBID )
		self.__rotateCBID = BigWorld.callback( self.__cc_rotate_interval, self.__rotateNumBtns )

	def __startRotate( self ) :
		"""
		��ʼ��������
		"""
		self.__rotateCBID = BigWorld.callback( self.__cc_rotate_interval, self.__rotateNumBtns )

	def __stopRotate( self ) :
		"""
		ֹͣ��ת
		"""
		BigWorld.cancelCallback( self.__rotateCBID )

	# -------------------------------------------------
	def __onPassedAccountGuard( self ) :
		"""
		����������ȷ�ص�
		"""
		self.hide()

	def __onLostAccountGuard( self, count ) :
		"""
		�����������ص�
		"""
		def callback( res ) :
			self.pyBtnCancel_.enable = True
			self.pyBtnOk_.enable = self.pyPswArea_.isReady()
		if count == Const.ACC_GUARD_WRONG_TIMES :
			# "�������ܱ��� %i �Σ���������������飬����׼����������룡"
			msg = mbmsgs[0x0b22] % Const.ACC_GUARD_WRONG_TIMES
		else :
			# "������ܱ�����!"
			msg = 0x0b21
		showMessage( msg, "", MB_OK, callback, self )

	def __onKickoutOvertime( self ) :
		"""
		�����ܱ�����ʱ��̫�������ߵ�
		"""
		self.__callback( DialogResult.CANCEL, "" )
		self.hide()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onClearClick_( self ) :
		"""
		���������������
		"""
		self.pyPswArea_.clear()

	def onOkClick_( self ) :
		"""
		���ȷ����ť
		"""
		self.__callback( DialogResult.OK, self.pyPswArea_.password )
		self.pyBtnOk_.enable = False
		self.pyBtnCancel_.enable = False

	def onCancelClick_( self ) :
		"""
		���ȡ����ť
		"""
		self.__callback( DialogResult.CANCEL, "" )
		self.hide()

	def onNumBtnClick_( self, pyBtn ) :
		"""
		��������ְ�ť
		"""
		self.pyPswArea_.input( pyBtn.mapKey )

	def onNumBtnMouseEnter_( self ) :
		"""
		���������ְ�ť
		"""
		self.__hideNumTextes()
		self.__stopRotate()

	def onNumBtnMouseLeave_( self ) :
		"""
		����뿪���ְ�ť
		"""
		self.__showNumTextes()
		self.__startRotate()

	# -------------------------------------------------
	def onPasswordChanged_( self, pswArea ) :
		"""
		��������ʱ������
		"""
		self.pyBtnOk_.enable = pswArea.isReady()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def onActivated( self ) :
		Window.onInactivated( self )
		self.pyPswArea_.tabIn()

	def resetSitesOfMatrix( self, pswSegs ) :
		"""
		�������þ��������
		"""
		self.pyPswArea_.setPswSegments( pswSegs )	# ����������
		self.pyBtnOk_.enable = True
		self.pyBtnCancel_.enable = True
		self.pyPswArea_.clear()

	def show( self, pswSegs, callback, pyOwner ) :
		"""
		��ʾ�ܱ�����
		callback ��������������
			DialogResult				# ��ǵ���ˡ�ȷ�������ǡ�ȡ������ť
			password					# ���봮
		"""
		if self.__callback :
			self.__callback( DialogResult.CANCEL, "" )
		self.__callback = callback
		self.center = BigWorld.screenWidth() * 0.5
		self.middle = BigWorld.screenHeight() * 0.5
		self.resetSitesOfMatrix( pswSegs )
		Window.show( self, pyOwner )
		if not self.pyNumsPanel_.isMouseHit() :		# ��ת���ְ�ť
			self.__startRotate()

	def hide( self ) :
		Window.hide( self )
		self.__unregisterEvents()
		self.__stopRotate()
		self.__callback = None
		self.removeFromMgr()
		self.pyPswArea_.dispose()
		self.__class__.releaseInst()


# --------------------------------------------------------------------
# ������ʾ��
# --------------------------------------------------------------------
class PasswdBox( TextBox ) :
	__cc_pswd_len			= 3			# ����γ���
	def __init__( self, box ) :
		TextBox.__init__( self, box )
		self.inputMode = InputMode.PASSWORD

		self.pyPreBox = None
		self.pyNextBox = None

	def dispose( self ) :
		self.pyPreBox = None
		self.pyNextBox = None
		TextBox.dispose( self )

	def __del__( self ) :
		if Debug.output_LoginDialogGuarder :
			INFO_MSG( str( self ) )
		TextBox.__del__( self )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isFull( self ) :
		"""
		�Ƿ�ﵽ������볤��
		"""
		return self.length == self.__cc_pswd_len

	def manualInput( self, key ) :
		"""
		�ֶ�����һ���ַ�
		"""
		if not self.tabStop : return False
		if self.pyRText_.text != "" :
			TextBox.keyInput_( self, KEY_DELETE, 0 )
		if not self.isFull() :
			TextBox.keyInput_( self, key, 0 )
		if self.pyNextBox and self.isFull() and self.pyRText_.text == "" :
			self.pyNextBox.tabStop = True
			TextBox.keyInput_( self.pyNextBox, KEY_LEFTARROW, MODIFIER_CTRL )
		return True

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def keyInput_( self, key, mods ) :
		if key == KEY_BACKSPACE :
			TextBox.keyInput_( self, key, mods )
			if self.text == "" and self.pyPreBox :
				self.pyPreBox.tabStop = True
			return True
		elif key == KEY_LEFTARROW :
			if self.pyPreBox and self.pyLText_.text == "" :
				self.pyPreBox.tabStop = True
				return True
			return TextBox.keyInput_( self, key, mods )
		elif key == KEY_RIGHTARROW :
			if self.pyNextBox and self.isFull() and self.pyRText_.text == "" :
				self.pyNextBox.tabStop = True
				TextBox.keyInput_( self.pyNextBox, KEY_LEFTARROW, MODIFIER_CTRL )
				return
			return TextBox.keyInput_( self, key, mods )
		elif key == KEY_DELETE :
			return TextBox.keyInput_( self, key, mods )
		return False


# --------------------------------------------------------------------
class PasswdArea( object ) :
	__cc_psw_group_len			= 10							# ÿ�����������

	def __init__( self, pyBinder, *areaPanels ) :
		self.__pyBinder = pyBinder
		self.pySTNames_ = []
		self.pyBoxes_ = []
		pyPreBox = None
		for idx, panel in enumerate( areaPanels ) :
			pySTName = StaticText( panel.stName )				# �������
			self.pySTNames_.append( pySTName )

			pyBox = PasswdBox( panel.tbPsw )					# ���������
			pyBox.onTextChanged.bind( self.__onBoxTextChanged )
			pyBox.pyPreBox = pyPreBox
			if pyPreBox : pyPreBox.pyNextBox = pyBox
			pyPreBox = pyBox
			self.pyBoxes_.append( pyBox )

	def dispose( self ) :
		self.__pyBinder = None
		for pyBox in self.pyBoxes_ :
			pyBox.dispose()

	def __del__( self ) :
		if Debug.output_LoginDialogGuarder :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onBoxTextChanged( self ) :
		"""
		�����ַ�ʱ������
		"""
		self.__pyBinder.onPasswordChanged_( self )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setPswSegments( self, pswSegs ) :
		"""
		�����ܱ����������
		"""
		segCount = len( pswSegs )								# ��������
		assert segCount == len( self.pySTNames_ ), \
			"the number of password input segments are not match with guard card's!"	# ���������������ܱ�����һ��

		for idx, ( row, col )  in enumerate( pswSegs ) :
			row = chr( ord( 'A' ) - 1 + row )
			self.pySTNames_[idx].text = row + str( col )

	# -------------------------------------------------
	def input( self, key ) :
		"""
		����һ�������ַ�
		"""
		for pyBox in self.pyBoxes_ :
			if pyBox.manualInput( key ) :
				return
		pyBox = self.pyBoxes_[0]
		pyBox.tabStop = True
		pyBox.manualInput( key )

	def tabIn( self ) :
		"""
		��ȡ����
		"""
		self.pyBoxes_[0].tabStop = True

	def clear( self ) :
		"""
		������������
		"""
		for pyBox in self.pyBoxes_ :
			pyBox.text = ""
		self.pyBoxes_[0].tabStop = True

	# -------------------------------------------------
	def isReady( self ) :
		"""
		�Ƿ�ȫ������ζ��Ѿ��������
		"""
		for pyBox in self.pyBoxes_ :
			if pyBox.length == 0 :
				return False
		return True


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getPassword( self ) :
		psw = []
		for pyBox in self.pyBoxes_ :
			psw.append( pyBox.text )
		return ",".join( psw)


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	password = property( _getPassword )


# --------------------------------------------------------------------
# ���ְ�ť
# --------------------------------------------------------------------
class NumButton( Button ) :
	def __init__( self, btn ) :
		Button.__init__( self, btn )
		self.canTabIn = False
		self.__isMouseIn = False

	def __del__( self ) :
		if Debug.output_LoginDialogGuarder :
			INFO_MSG( str( self ) )
		Button.__del__( self )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMouseEnter_( self ) :
		self.__isMouseIn = True
		return Button.onMouseEnter_( self )

	def onMouseLeave_( self ) :
		self.__isMouseIn = False
		return Button.onMouseLeave_( self )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getCenterPos( self ) :
		x = Button._setCenter( self )
		y = Button._setMiddle( self )
		return Math.Vector2( x, y )

	def _setCenterPos( self, pos ) :
		x, y = pos
		Button._setCenter( self, x )
		Button._setMiddle( self, y )
		if self.isMouseHit() :
			if not self.__isMouseIn :
				self.onMouseEnter_()
		else :
			if self.__isMouseIn :
				self.onMouseLeave_()


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	centerPos = property( _getCenterPos, _setCenterPos )
