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
		self.__triggers["EVT_ON_ENTER_WUTING"] = self.__onEnterWuting			# ��������
		self.__triggers["EVT_ON_LEAVE_WUTING"] = self.__onLeaveWuting			# �뿪����
		self.__triggers["EVT_ON_ENTER_DANCE_SPACE"] = self.__onEnterDanceSpace	# �������踱��
		self.__triggers["EVT_ON_LEAVE_DANCE_SPACE"] = self.__onLeaveDanceSpace	# �뿪���踱��
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )
		
	def __onShowDancersRank( self ):
		"""
		������
		"""
		rds.ruisMgr.highDance.show()
		BigWorld.player().cell.askforDanceInfos()
		
	def __onPratice( self ):
		"""
		��ϰ
		"""	
		def query( rs_id ):
			if rs_id == RS_YES:
				BigWorld.player().gotoDanceSpace( 0 )
		showMessage( mbmsgs[0x11a2] ,"", MB_YES_NO, query )
		
	def __onQuit( self ):
		"""
		�˳�
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
		��ֹ��ϰ
		"""
		BigWorld.player().cancelParctice()	
			
	def __onEnterWuting( self ):
		"""
		��������
		"""
		self.__pyBtnRank.visible = True
		self.__pyBtnPratice.visible = True
		self.__pyBtnQuit.visible = True
		self.__pyBtnQuitPratice.visible = False
		RootGUI.show( self )
		
	def __onLeaveWuting( self ):
		"""
		�뿪����
		"""
		self.hide()
		rds.ruisMgr.highDance.hide()
		
	def __onEnterDanceSpace( self,type ):
		"""
		�������踱��
		"""
		if type == 1:		#��ս����
			self.__pyBtnRank.visible = False
			self.__pyBtnPratice.visible = False
			self.__pyBtnQuit.visible = True
			self.__pyBtnQuitPratice.visible = False
		else:				#��ϰ����
			self.__pyBtnRank.visible = False
			self.__pyBtnPratice.visible = False
			self.__pyBtnQuit.visible = True
			self.__pyBtnQuitPratice.visible = True
		RootGUI.show( self )
		
	def __onLeaveDanceSpace( self, type ):
		"""
		�뿪���踱��
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