# -*- coding: gb18030 -*-
# $Id: PasswordWindow.py,v 1.16 2008-08-26 02:22:20 huangyongwei Exp $

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.TextBox import TextBox
from guis.controls.Button import Button
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabPage
from PasswordOperate import PasswordOperate
from PasswordSetting import PasswordSetting

class PasswordWindow( Window ):
	__instance=None
	def __init__( self ):
		assert PasswordWindow.__instance is None,"PasswordWindow has been created"
		PasswordWindow.__instance=self
		wnd = GUI.load( "guis/tooluis/passwordbox/passwordwindow.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment 	 = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True
		self.lockStatus = -1
		self.callback_ = lambda *args : False
		self.__initialize( wnd )
		self.addToMgr("passwordWindow")

	@staticmethod
	def instance():
		"""
		get the exclusive instance of PasswordWindow
		"""
		if PasswordWindow.__instance  is None:
			PasswordWindow.__instance=PasswordWindow()
		return PasswordWindow.__instance

	@staticmethod
	def getInstance():
		"""
		return PasswordWindow.__instance: if PasswordWindow.__instance is noen it
		will return None , else return the exclusive instance
		"""
		return PasswordWindow.__instance

	def __del__(self):
		"""
		just for testing for memory leak
		"""
		pass


	def __initialize( self, wnd ):
		self.__pyTabCtr = TabCtrl( wnd.tc )

		self.__pyOperatePanel = PasswordOperate( wnd.tc.panel_0, self )
		self.__pyOperateBtn = TabButton( wnd.tc.tab_0 )
		labelGather.setPyBgLabel( self.__pyOperateBtn, "PasswordBox:PasswordOperate", "btnOperate" )
		self.__pyOperateBtn.selectedForeColor = ( 142, 216, 217, 255 )
		self.__pyOperatePage = TabPage( self.__pyOperateBtn, self.__pyOperatePanel )
		self.__pyOperateBtn.onLClick.bind( self.__onOperate )
		self.__pyTabCtr.addPage( self.__pyOperatePage )

		self.__pySettingPanel = PasswordSetting( wnd.tc.panel_1, self )
		self.__pySettingBtn = TabButton( wnd.tc.tab_1 )
		labelGather.setPyBgLabel( self.__pySettingBtn, "PasswordBox:PasswordSetting", "btnSetting" )
		self.__pySettingBtn.selectedForeColor = ( 142, 216, 217, 255 )
		self.__pySettingBtn.onLClick.bind( self.__onSetting )
		self.__pySettingPage = TabPage( self.__pySettingBtn, self.__pySettingPanel )
		self.__pyTabCtr.addPage( self.__pySettingPage )

	# -----------------------------------------------------------------
	# pravite
	# -----------------------------------------------------------------
	def __onLockStatusChange( self, lockStatus ):
		self.lockStatus = lockStatus

	def __onSetting( self ):
		if self.lockStatus&0x01 == 0x01: #修改密码界面
			def change( result, oldpassword, newpassword ):
				if result == PassResult.CHANGERESULT:
					self.pyOwner.setPassWord( oldpassword, newpassword ) # 修改密码
			self.__pyTabCtr.pySelPage = self.__pySettingPage
			self.__pySettingPanel.show( change, self.lockStatus )

	def __onOperate( self ):
		if self.lockStatus&0x02 == 0x02: # 激活密码操作界面
			self.__pyTabCtr.pySelPage = self.__pyOperatePage
			self.__pySettingPanel.show( self.callback_, self.lockStatus )


	# -----------------------------------------------------------------
	# pubkic
	# -----------------------------------------------------------------
	def show( self, callback, lockStatus, pyOwner = None ):
		self.callback_ = callback
		self.lockStatus = lockStatus
		if lockStatus == 0:	# 没有设置密码，激活密码设置
			self.__pyTabCtr.pyPages[1].selected = True
			def set( result, oldpassword, newpassword ):
				if result == PassResult.SETRESULT:
					self.pyOwner.setPassWord( oldpassword, newpassword )
			self.__pySettingPanel.show( set, self.lockStatus )
			self.__pyOperateBtn.enable = False
		elif lockStatus&0x01 == 0x01: # 已设置了密码，激活密码操作界面
			self.__pyOperateBtn.enable = True
			self.__pyTabCtr.pyPages[0].selected = True
			self.__pyOperatePanel.show( self.callback_, self.lockStatus )
			self.__pySettingPanel.updateLockStatus( lockStatus )
		Window.show( self, pyOwner )

	def updateLockStatus( self, lockStatus, pyOwner ):
		if self.pyOwner == pyOwner :
			self.__onLockStatusChange( lockStatus )
			self.__pyOperatePanel.updateLockStatus( lockStatus )
			self.__pySettingPanel.updateLockStatus( lockStatus )

	def hide( self ):
		Window.hide( self )
		self.removeFromMgr()
		self.dispose()
		self.__trrigers={}
		self.__pySettingPanel.dispose()
		self.__pyOperatePanel=None
		PasswordWindow.__instance=None

	def onKeyDown_( self, key, mods ) :
		"""
		"""
		keyEventHandler = getattr( self.__pyTabCtr.pySelPage.pyPanel, "keyEventHandler", None )
		if callable( keyEventHandler ) :
			return keyEventHandler( key, mods )
		return Window.onKeyDown_( self, key, mods )
