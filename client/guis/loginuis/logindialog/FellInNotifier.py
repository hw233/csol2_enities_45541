# -*- coding: gb18030 -*-

"""
排队提示窗口
"""

from AbstractTemplates import Singleton
from guis import *
import MessageBox
from guis.controls.Button import Button
from LabelGather import labelGather
from guis.tooluis.messagebox.MsgBox import MsgBox

class FellInNotifier( Singleton, MsgBox ) :
	def __init__( self ) :
		box = GUI.load( "guis/loginuis/logindialog/fellinnotifier.gui" )
		uiFixer.firstLoadFix( box )
		MsgBox.__init__( self, box )
		self.activable_ = False
		self.canHide = False

		self.pyGiveUpBtn_ = Button( box.okBtn, self )					# 放弃按钮
		self.pyGiveUpBtn_.setStatesMapping( UIState.MODE_R3C1 )
		self.pyGiveUpBtn_.onLClick.bind( self.__giveUp )
		labelGather.setPyBgLabel( self.pyGiveUpBtn_, "LoginDialog:FellInNotifier", "btnGiveup" )
		self.pyCloseBtn_.onLClick.bind( self.__giveUp )
		self.setOkButton( self.pyGiveUpBtn_ )

		self.defRes_ = MessageBox.RS_OK
		self.__callback = None


	def dispose( self ) :
		self.pyGiveUpBtn_.dispose()
		MsgBox.dispose( self )
		self.__callback = None


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __feedback( self, resultID ) :
		"""
		点击按钮后的返回
		"""
		def query( rs_id ):
			if rs_id == RS_OK:
				rds.gameMgr.accountLogoff()
				self.hide()

		showMessage( 0x0b41, "", MB_OK_CANCEL, query, self )		# "确定要放弃排队吗？"
		self.__callback( resultID )

	def __giveUp( self ):
		"""
		放弃排队
		"""
		self.notifyCallback_( self.defRes_ )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@classmethod
	def show( SELF, msg, title, callback, pyOwner = None ) :
		pyBox = SELF()
		pyBox.__callback = callback
		MsgBox.show( pyBox, msg, title, pyBox.__feedback, pyOwner )
		return pyBox

	@classmethod
	def hide( SELF ):
		if not SELF.insted : return
		pyBox = SELF()
		pyBox.dispose()
		SELF.releaseInst()