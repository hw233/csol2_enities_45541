# -*- coding: gb18030 -*-
#
# $Id: Repairer.py,v 1.8 2008-08-29 02:40:08 huangyongwei Exp $

"""
implement repair tool
－－2008/02/02 : writen by huangyongwei
"""

from guis import *
from guis.common.RootGUI import RootGUI
from config.client.msgboxtexts import Datas as mbmsgs
import csdefine
import GUIFacade

class TaofaLocker( RootGUI ) :
	def __init__( self ) :
		vui = GUI.Simple( "" )
		RootGUI.__init__( self, vui )
		self.moveFocus = False
		self.size = 0, 0
		self.right = 0
		self.bottom = 0
		self.pyMsgBox = None
		self.selInfo = None
		self.__pySender = None

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __searchDaofa( self ) :
		pyRoot = ruisMgr.getMouseHitRoot()
		if pyRoot is None : return None
		def verfier( pyUI ) :
			if not pyUI.rvisible :
				return False, 0
			if not pyUI.isMouseHit() :
				return False, 0
			if hasattr( pyUI, "getLockInfo" ) :
				return True, -1
			return False, 1
		pyUIs = util.postFindPyGui( pyRoot.getGui(), verfier )
		if not len( pyUIs ) : return None
		return pyUIs[0].getLockInfo( self )

	def __lock( self ) :
		if self.selInfo is None : return
		if self.selInfo == self.__pySender :
			self.cancelLocking()
		else :
			player = BigWorld.player()
			player.lockDaofa( self.selInfo.uid )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onKeyDown_( self, key, mods ) :
		if key == KEY_ESCAPE :
			self.cancelLocking()
		return True

	def onKeyUp_( self, key, mods ) :
		return True

	# ---------------------------------------
	def onLMouseDown_( self, mods ) :
		if not self.isInUsed() : return
		if self.pyMsgBox and self.pyMsgBox.visible:
			self.pyMsgBox.hide()
		rds.ccursor.lock( "lock" )	#锁住鼠标
		if self.__pySender.isMouseHit() :
			self.cancelLocking()
		else :
			def query( rs_id ):
				if rs_id == RS_OK:
					self.__lock()
			msgId, name = self.__getLockMsg()
			if msgId == 0x10ab:
				showAutoHideMessage( 3.0, msgId, mbmsgs[0x0c22] )
				self.cancelLocking()
				return 
			self.pyMsgBox = showMessage( mbmsgs[msgId] % name, "", MB_OK_CANCEL, query )
		return True

	def __getLockMsg( self ):
		daofa = self.__searchDaofa()
		if daofa is None : 
			return 0x10ab, ""
		else:
			self.selInfo = daofa
			name = daofa.name
			if daofa.isLocked:
				return 0x10aa, name
			else:
				return 0x10a9, name

	def onRMouseDown_( self, mods ) :
		self.cancelLocking()
		return True

	def onLMouseUp_( self, mods ) :
		if self.isInUsed() and self.pyMsgBox is not None \
		and not self.pyMsgBox.visible:
			rds.ccursor.lock( "lock" )	#锁住鼠标
		elif self.pyMsgBox is not None and self.pyMsgBox.visible:
			self.cancelLocking()
		return True

	def onRMouseUp_( self, mods ) :
		return True

	# ---------------------------------------
	def onLClick_( self, mods ) :
		return True

	def onRClick( self, mods ) :
		return True

	# ---------------------------------------
	def onMouseMove_( self, dx, dy ) :
		return False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def enterLocking( self, pySender ) :
		self.visible = True
		self.focus = True
		self.__pySender = pySender
		rds.ccursor.lock( "lock" )	#锁住鼠标
		self.addToMgr( "taoHeartLocker" )
		uiHandlerMgr.uncapUI()
		uiHandlerMgr.capUI( self )

	def cancelLocking( self ) :
		rds.ccursor.normal()
		self.removeFromMgr()
		self.__pySender = None
		uiHandlerMgr.uncapUI( self )
		rds.ccursor.unlock( "lock", "normal" )	#解锁鼠标
		self.visible = False
		self.focus = False

	def isInUsed( self ) :
		return self.__pySender is not None
