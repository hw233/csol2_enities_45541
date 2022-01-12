# -*- coding: gb18030 -*-

# implement auto active window.
# written by ganjinxing 2009-12-1

from bwdebug import INFO_MSG
from guis import *
from guis.common.RootGUI import RootGUI
from guis.controls.StaticText import StaticText
from AbstractTemplates import Singleton
from LabelGather import labelGather

class AutoActWindow( Singleton, RootGUI ) :

	__pyMsgBox = None

	def __init__( self ) :
		wnd = GUI.load( "guis/loginuis/autoactivewindow/actwnd.gui" )
		RootGUI.__init__( self, wnd )
		self.escHide_ = False
		self.movable_ = False
		self.posZSegment = ZSegs.L3
		self.h_dockStyle = "CENTER"

		self.__pyText = StaticText( wnd.lbText )
		self.addToMgr( "autoActWindow" )

	def __del__( self ) :
		RootGUI.__del__( self )
		if Debug.output_del_AutoActWindow :
			INFO_MSG( str( self ) )

	def dispose( self ) :
		RootGUI.dispose( self )
		self.removeFromMgr()
		self.__class__.releaseInst()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@classmethod
	def __showMsg( SELF, msg ) :
		def query( res ) :
			SELF.__pyMsgBox = None
		if SELF.__pyMsgBox is None :
			SELF.__pyMsgBox = showMessage( msg, "", MB_OK, query )
		else :
			SELF.__pyMsgBox.show( msg, "", query, None )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@classmethod
	def handleFeedback( SELF, connectResult ) :
		pyWnd = SELF()
		if connectResult == ( 1, -253 ) :					# 登陆不成功，自动激活
			labelGather.setPyLabel( pyWnd.__pyText, "LoginDialog:autoActWnd", "activing" )
			pyWnd.show()
			return True
		else :
			SELF.hide()
			return connectResult == ( 1, -252 ) 			# 等于( 1, -252 )表示激活成功

	@classmethod
	def hide( SELF ) :
		if not SELF.insted :
			return
		pyWnd = SELF()
		RootGUI.hide( pyWnd )
		pyWnd.dispose()
