# -*- coding: gb18030 -*-
#
# written by ganjinxing 2009-11-23

"""
implement AntiRabotWindow
"""
from bwdebug import *
from guis import *
from LabelGather import labelGather
from AbstractTemplates import Singleton
from guis.common.PyGUI import PyGUI
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.controls.Control import Control
from guis.controls.StaticText import StaticText
from config.client.msgboxtexts import Datas as mbmsgs
import csconst


class AntiRabotWindow( Singleton, Window ) :

	__triggers = {}

	def __init__( self ) :
		wnd = GUI.load( "guis/general/antirabotwindow/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L2
		self.escHide_ = False
		self.h_dockStyle = "RIGHT"
		self.v_dockStyle = "MIDDLE"

		self.__currImgStr = ""
		self.__pyMsgBox = None
		self.__cdCBID = 0
		self.__leaveTime = 0
		self.__verifyTime = 0
		self.__initialize( wnd )
		self.addToMgr( "antiRabotWindow" )

	def __del__( self ) :
		Window.__del__( self )
		if Debug.output_del_AntiRabotWindow :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		self.__pyOKBtn = HButtonEx( wnd.okBtn )
		self.__pyOKBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyOKBtn.onLClick.bind( self.__onOK )
		
		self.__pyCancelBtn = HButtonEx( wnd.cancelBtn )
		self.__pyCancelBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyCancelBtn.onLClick.bind( self.__onCancel )

		self.__pyLeaveTime = StaticText( wnd.leaveTime )
		self.__pyVerifyImg = VerifyImage( wnd.picture )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyOKBtn, "AntiRabotWindow:main", "btnOK" )
		labelGather.setPyBgLabel( self.__pyCancelBtn, "AntiRabotWindow:main", "btnCancel" )
		labelGather.setLabel( self.gui.lbTitle, "AntiRabotWindow:main", "title" )
		labelGather.setLabel( self.gui.st_2, "AntiRabotWindow:main", "stClew" )

	def __onOK( self ) :
		clickPos = self.__pyVerifyImg.clickPos
		if clickPos is None :
			self.__showMsg( mbmsgs[0x01e1] )				# "请先点击选出不相同的形状！"
		else :
			BigWorld.player().base.answerRobotVerify( clickPos )
			self.hide()
	
	def __onCancel( self ):
		if BigWorld.player().__class__.__name__ == "PlayerAccount":	#登陆界面的,#取消 需要验证关闭，所有按钮有效 add by wuxo 2011-10-22
			BigWorld.player().base.cancelAnswer()
			rds.roleSelector.unlockContrl()
		elif BigWorld.player().__class__.__name__ == "PlayerRole":     #游戏中,取消为答错,add by wuxo 2011-10-24
			BigWorld.player().base.answerRobotVerify( (0,0) )
		self.hide()

	@classmethod
	def __onVerifyCheck( SELF, imgStr, count ) :
		SELF.inst.show( imgStr, count )

	def __countDown( self ) :
		self.__leaveTime -= 1
		if self.__leaveTime < 0 :
			self.hide()
			return
		text = labelGather.getText( "AntiRabotWindow:main", "leaveTime" )
		text %= ( self.__verifyTime, self.__leaveTime )
		self.__pyLeaveTime.text = text
		self.__cdCBID = BigWorld.callback( 1, self.__countDown )

	def __stopCountDown( self ) :
		if self.__cdCBID :
			BigWorld.cancelCallback( self.__cdCBID )
			self.__cdCBID = 0

	def __showMsg( self, msg ) :
		def query( res ) :
			self.__pyMsgBox = None
		if self.__pyMsgBox is None :
			self.__pyMsgBox = showMessage( msg, "", MB_OK, query, self )
		else :
			self.__pyMsgBox.show( msg, "", query, self )

	@classmethod
	def __onResolutionChanged( SELF, preReso ) :
		"""
		当屏幕分辨率改变时被调用
		"""
		if SELF.insted :
			SELF.inst.__pyVerifyImg.texture = SELF.inst.romanceTX

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def reset( self ) :
		self.__pyLeaveTime.text = ""
		self.__pyVerifyImg.onHide()
		self.__pyVerifyImg.texture = ""
		self.__stopCountDown()

	def dispose( self ) :
		Window.dispose( self )
		self.__class__.releaseInst()

	def show( self, imgStr, count ) :
		self.__currImgStr = imgStr
		self.__pyVerifyImg.texture = self.romanceTX
		leaveTime = csconst.IMAGE_VERIFY_TIME_MAP[count]
		self.__leaveTime = leaveTime
		self.__verifyTime = count
		self.__stopCountDown()
		self.__countDown()
		Window.show( self )

	def hide( self ) :
		self.__stopCountDown()
		Window.hide( self )
		self.dispose()
		self.removeFromMgr()

	def beforeStatusChanged( self, oldStatus, newStatus ) :
		if newStatus == Define.GST_OFFLINE :
			self.hide()

	def onLeaveWorld( self ) :
		self.hide()

	@classmethod
	def registerTriggers( SELF ) :
		SELF.__triggers["EVT_ON_ANTI_RABOT_VERIFY"] = SELF.__onVerifyCheck
		SELF.__triggers["EVT_ON_RESOLUTION_CHANGED"] = SELF.__onResolutionChanged
		for key in SELF.__triggers :
			ECenter.registerEvent( key, SELF )


	@classmethod
	def onEvent( SELF, evtMacro, *args ) :
		SELF.__triggers[evtMacro]( *args )


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getVerifyImage( self ) :
		try :
			return csol.binaryToTexture( self.__currImgStr )
		except :
			ERROR_MSG( "The image received is invalid!" )
			return "guis/empty.dds"

	romanceTX = property( _getVerifyImage )


class VerifyImage( Control ) :

	def __init__( self, img, pyBinder = None ) :
		Control.__init__( self, img, pyBinder )
		self.focus = True

		self.__clickPos = None
		self.__indicator = PyGUI( img.indicator )
		self.__indicator.width *= self.width / 128.0
		self.__indicator.height *= self.height / 64.0
		self.__indicator.visible = False


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLClick_( self, mods ) :
		posX, posY = self.mousePos
		self.__indicator.center = posX
		self.__indicator.middle = posY
		self.__indicator.visible = True
		posX *= 128.0 / self.width										# 贴图原始比例是128 * 64
		posY *= 64.0 / self.height										# 这里把放大的尺寸进行转换，以使它始终在原始比例范围内
		self.__clickPos = int( posX ), int( posY )
		return True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onHide( self ) :
		self.__indicator.visible = False


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getClickPos( self ) :
		return self.__clickPos

	clickPos = property( _getClickPos )


AntiRabotWindow.registerTriggers()