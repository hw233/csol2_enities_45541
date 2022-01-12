# -*- coding: gb18030 -*-
#
import event.EventCenter as ECenter
from guis import *
from LabelGather import labelGather
from guis.common.RootGUI import RootGUI
from guis.controls.ButtonEx import HButtonEx
from HighDance import HighDance
from config.client.msgboxtexts import Datas as mbmsgs

class HighDanceEntrance( RootGUI ) :
	
	def __init__( self ) :
		wnd = GUI.load( "guis/general/highdance/highDanceEntrance.gui"  )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		self.h_dockStyle = "HFILL"
		self.v_dockStyle = "BOTTOM"
		self.posZSegment = ZSegs.L5
		self.movable_ = False
		self.activable_ = False
		self.escHide_ 		 = False
		self.focus = False
		
		self.__initialize( wnd )
		self.__triggers = {}
		self.__registerTriggers()
		
	def __initialize( self, wnd ):	
		self.__pyBtnRank = HButtonEx( wnd. btnRank )
		self.__pyBtnRank.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnRank.onLClick.bind( self.__onShowDancersRank )
		labelGather.setPyBgLabel( self.__pyBtnRank, "HighDance:HighDance", "btnRank" )
		
		self.__pyBtnPratice = HButtonEx( wnd. btnPratice )
		self.__pyBtnPratice.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnPratice.onLClick.bind( self.__onPratice )
		labelGather.setPyBgLabel( self.__pyBtnPratice, "HighDance:HighDance", "btnPratice" )
		
		self.__pyBtnQuit = HButtonEx( wnd. btnQuit )
		self.__pyBtnPratice.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnQuit.onLClick.bind( self.__onQuit )
		labelGather.setPyBgLabel( self.__pyBtnQuit, "HighDance:HighDance", "btnQuit" )
		
		self.__pyBtnQuitPratice = HButtonEx( wnd. btnQuitPratice )
		self.__pyBtnQuitPratice.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnQuitPratice.onLClick.bind( self.__onBreakPratice )
		labelGather.setPyBgLabel( self.__pyBtnQuitPratice, "HighDance:HighDance", "btnQuitPratice" )
		
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ENTER_WUTING"] = self.__onEnterWuting			# 进入舞厅
		self.__triggers["EVT_ON_LEAVE_WUTING"] = self.__onLeaveWuting			# 离开舞厅
		self.__triggers["EVT_ON_ENTER_DANCE_SPACE"] = self.__onEnterDanceSpace	# 进入跳舞副本
		self.__triggers["EVT_ON_LEAVE_DANCE_SPACE"] = self.__onLeaveDanceSpace	# 离开跳舞副本
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )
		
	def __onShowDancersRank( self ):
		"""
		舞王榜
		"""
		rds.ruisMgr.highDance.show()
		BigWorld.player().cell.askforDanceInfos()
		
	def __onPratice( self ):
		"""
		练习
		"""	
		def query( rs_id ):
			if rs_id == RS_YES:
				BigWorld.player().gotoDanceSpace( 0 )
		showMessage( mbmsgs[0x11a2] ,"", MB_YES_NO, query )
		
	def __onQuit( self ):
		"""
		退出
		"""
		player = BigWorld.player()
		if player.getSpaceLabel() == "fu_ben_wu_tai_001":
			def query( rs_id ):
				if rs_id == RS_YES:
					BigWorld.player().quitDance()		
			showMessage( mbmsgs[0x11a1] ,"", MB_YES_NO, query )
		else:
			BigWorld.player().quitDance()
		
	def __onBreakPratice( self ):
		"""
		中止练习
		"""
		BigWorld.player().cancelParctice()	
			
	def __onEnterWuting( self ):
		"""
		进入舞厅
		"""
		self.__pyBtnRank.visible = True
		self.__pyBtnPratice.visible = True
		self.__pyBtnQuit.visible = True
		self.__pyBtnQuitPratice.visible = False
		RootGUI.show( self )
		
	def __onLeaveWuting( self ):
		"""
		离开舞厅
		"""
		self.hide()
		rds.ruisMgr.highDance.hide()
		
	def __onEnterDanceSpace( self,type ):
		"""
		进入跳舞副本
		"""
		if type == 1:		#挑战副本
			self.__pyBtnRank.visible = False
			self.__pyBtnPratice.visible = False
			self.__pyBtnQuit.visible = True
			self.__pyBtnQuitPratice.visible = False
		else:				#练习副本
			self.__pyBtnRank.visible = False
			self.__pyBtnPratice.visible = False
			self.__pyBtnQuit.visible = True
			self.__pyBtnQuitPratice.visible = True
		RootGUI.show( self )
		
	def __onLeaveDanceSpace( self, type ):
		"""
		离开跳舞副本
		"""
		self.hide()

	# -------------------------------------------------	
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )
		
	def hide( self ):
		self.__pyBtnRank.visible = True
		self.__pyBtnPratice.visible = True
		self.__pyBtnQuit.visible = True
		self.__pyBtnQuitPratice.visible = False
		RootGUI.hide( self )
		
	def onLeaveWorld( self ) :
		self.hide()