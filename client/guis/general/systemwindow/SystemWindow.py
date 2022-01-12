# -*- coding: gb18030 -*-
#
# $Id: SystemWindow.py,v 1.18 2008-08-26 02:19:53 huangyongwei Exp $

"""
implement system setting window
"""

import BigWorld
import GUIFacade
from guis import *
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.general.syssetting.GameSetting import GameSetting
from LabelGather import labelGather
import csdefine
import csstatus
from VehicleHelper import isFalling

class SystemWindow( Window ) :

	__instance=None
	def __init__( self ) :
		assert SystemWindow.__instance is None , "SystemWindow instance has been created"
		SystemWindow.__instance=self
		wnd = GUI.load( "guis/general/systemwindow/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.escHide_ = True
		self.activable_ = True
		self.__initialize( wnd )
		self.h_dockStyle = "CENTER"							# 水平居中显示
		self.v_dockStyle = "MIDDLE"							# 垂直居中显示

		self.__triggers = {}
		self.__registerTriggers()

	def __initialize( self, wnd ) :
		pyBtn0 = self.__createPyBtn( wnd.btn_0, self.__sysSetting )				# 游戏设定
		labelGather.setPyBgLabel( pyBtn0, "systemwindow:main", "btn_0" )
		pyBtn1 = self.__createPyBtn( wnd.btn_1, self.__backToChoice )			# 返回选择
		labelGather.setPyBgLabel( pyBtn1, "systemwindow:main", "btn_1" )
		pyBtn2 = self.__createPyBtn( wnd.btn_2, self.__quitGame )				# 退出游戏
		labelGather.setPyBgLabel( pyBtn2, "systemwindow:main", "btn_2" )
		pyBtn3 = self.__createPyBtn( wnd.btn_3, self.__backToGame )				# 返回游戏
		labelGather.setPyBgLabel( pyBtn3, "systemwindow:main", "btn_3" )
		self.pyBtns_ = set( [pyBtn0, pyBtn1, pyBtn2, pyBtn3] )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setLabel( wnd.lbTitle, "systemwindow:main", "lbTitle" )

	def __del__( self ) :
		Window.__del__( self )
		if Debug.output_del_SystemWindow :
			INFO_MSG( str( self ) )

	def dispose( self ) :
		self.__deregisterTriggers()
		Window.dispose( self )

	@staticmethod
	def instance():
		if SystemWindow.__instance is None:
			SystemWindow.__instance=SystemWindow()
		return SystemWindow.__instance


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_RESOLUTION_CHANGED"] = self.__onResolutionChanged
		for key in self.__triggers.iterkeys() :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			GUIFacade.unregisterEvent( key, self )
		self.__triggers = {}

	# -------------------------------------------------
	def __onResolutionChanged( self, preReso ):
		self.h_dockStyle = "CENTER"
		self.v_dockStyle = "MIDDLE"
		
	def __createPyBtn( self, btn, func ) :
		pyBtn = HButtonEx( btn, self )
		pyBtn.isOffsetText = True
		pyBtn.focus = True
		pyBtn.setExStatesMapping( UIState.MODE_R4C1 )
		pyBtn.onLClick.bind( func )
		return pyBtn

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def onLeaveWorld( self ) :
		GameSetting.instance().onLeaveWorld()
		self.hide()

	def show( self ) :
		self.addToMgr()
		for pyBtn in self.pyBtns_ :
			pyBtn.resetSetate()
		self.h_dockStyle = "CENTER"
		self.v_dockStyle = "MIDDLE"
		Window.show( self )
	
	def toggleWindow( self ):
		if self.visible:
			self.hide()
		else:
			self.show()
	
	def onEnterWorld( self ):
		GameSetting.instance().initGraphicsSetting()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __backToGame( self ):
		self.hide()

	def hide(self):
		self.dispose()
		self.removeFromMgr()
		SystemWindow.__instance=None

	def __backToChoice( self ):
		if not self.__canLogout():
			return
		rds.gameMgr.logout()
		self.hide()

	def __quitGame( self ):
		if not self.__canLogout():
			return
		
		rds.gameMgr.quitGame( True )
		self.hide()

	def __canLogout( self ):
		player = BigWorld.player()
		if player.state == csdefine.ENTITY_STATE_FIGHT:
			player.statusMessage( csstatus.ROLE_FIGHT_CANNOT_LOGOUT )
			return False
			
		# 如果在掉落过程中，不允许下线
		if isFalling( player ):
			player.statusMessage( csstatus.CANT_LOGOUT_WHEN_FALLING )
			return False
		
		return True

	def __sysSetting( self ) :
#		rds.ruisMgr.gameSetting.instance().show()
		GameSetting.instance().show()
		self.hide()