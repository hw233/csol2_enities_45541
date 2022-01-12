# -*- coding: gb18030 -*-
#
# $Id: Repairer.py,v 1.8 2008-08-29 02:40:08 huangyongwei Exp $

"""
implement repair tool
����2008/02/02 : writen by huangyongwei
"""

from guis import *
from guis.common.RootGUI import RootGUI
from config.client.msgboxtexts import Datas as mbmsgs
import csdefine
import GUIFacade

class Repairer( RootGUI ) :
	def __init__( self ) :
		vui = GUI.Simple( "" )
		RootGUI.__init__( self, vui )
		self.moveFocus = False
		self.size = 0, 0
		self.right = 0
		self.bottom = 0
		self.pyBox = None
		self.selInfo = None
		self.__pySender = None

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __searchTargetInfo( self ) :
		pyRoot = ruisMgr.getMouseHitRoot()
		if pyRoot is None : return None

		def verfier( pyUI ) :
			if not pyUI.rvisible :
				return False, 0
			if not pyUI.isMouseHit() :
				return False, 0
			if hasattr( pyUI, "getRepairInfo" ) :
				return True, -1
			return False, 1

		pyUIs = util.postFindPyGui( pyRoot.getGui(), verfier )
		if not len( pyUIs ) : return None
		return pyUIs[0].getRepairInfo( self )

	def __repair( self ) :
		if self.selInfo is None : return
		if self.selInfo == self.__pySender :
			self.cancelUsing()
		else :
			GUIFacade.repairOneEquip( *self.selInfo )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onKeyDown_( self, key, mods ) :
		if key == KEY_ESCAPE :
			self.cancelUsing()
		return True

	def onKeyUp_( self, key, mods ) :
		return True

	# ---------------------------------------
	def onLMouseDown_( self, mods ) :
		if not self.isInUsed() : return
		if self.pyBox and self.pyBox.visible:
			self.pyBox.hide()
		rds.ccursor.lock( "repairing" )	#��ס���
		if self.__pySender.isMouseHit() :
			self.cancelUsing()
		else :
			def query( rs_id ):
				if rs_id == RS_OK:
					self.__repair()
			msg = self.__getRepairMsg()
			if msg == "":
				# "��װ������Ҫ����"
				showAutoHideMessage( 3.0, 0x0a41, mbmsgs[0x0c22] )
				self.cancelUsing()
				return #����Ҫ����
			elif msg is None:
				# "��ѡ����Ҫ�����װ��"
				showAutoHideMessage( 3.0, 0x0a42, mbmsgs[0x0c22] )
				self.cancelUsing()
				return
			# "%s���Ƿ�ȷ����Ҫ����?"
			self.pyBox = showMessage( mbmsgs[0x0a43] % msg, "", MB_OK_CANCEL, query )
		return True

	def __getRepairMsg( self ):
		info = self.__searchTargetInfo()
		if info is None : return
		self.selInfo = info
		repairType, kitBagID, orderID = info
		baseItem = BigWorld.player().getItem_( kitBagID * csdefine.KB_MAX_SPACE + orderID )
		if baseItem is None:return
		if not baseItem.isEquip():return
		repairMsg = GUIFacade.calcuOneRepairPrice( baseItem, repairType )
		return repairMsg

	def onRMouseDown_( self, mods ) :
		self.cancelUsing()
		return True

	def onLMouseUp_( self, mods ) :
		if self.isInUsed() and self.pyBox is not None \
		and not self.pyBox.visible:
			rds.ccursor.lock( "repair" )	#��ס���
		elif self.pyBox is not None and self.pyBox.visible:
			self.cancelUsing()
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
	def enterUsing( self, pySender ) :
		self.visible = True
		self.focus = True
		self.__pySender = pySender
		rds.ccursor.lock( "repair" )	#��ס���
		self.addToMgr( "tradeRepairer" )
		uiHandlerMgr.uncapUI()
		uiHandlerMgr.capUI( self )

	def cancelUsing( self ) :
		rds.ccursor.normal()
		self.removeFromMgr()
		self.__pySender = None
		uiHandlerMgr.uncapUI( self )
		rds.ccursor.unlock( "repair", "normal" )	#��ס���
		self.visible = False
		self.focus = False

	def isInUsed( self ) :
		return self.__pySender is not None
