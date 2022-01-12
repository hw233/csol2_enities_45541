# -*- coding: gb18030 -*-
#
# $Id: RankWindow.py, fangpengjun Exp $

"""
implement RankWindow window class

"""
from guis import *
from guis.common.Window import Window
from guis.controls.StaticText import StaticText
from guis.controls.TextBox import TextBox
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabPage
from guis.controls.TabCtrl import TabButton
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ButtonEx import HButtonEx
from RankPanel import RankPanel
from LabelGather import labelGather
import GUIFacade
import csdefine
import csconst
import Const
import time

TONG_ACTIVEPOINT_TYPE = 6

class RankWindow( Window ):
	def __init__( self ):
		wnd = GUI.load( "guis/general/rankwindow/window.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True
		self.__triggers = {}
		self.__registerTriggers()
		self.__trapID = None
		self.__initialize( wnd )

	def __initialize( self, wnd ):
		self.__pyTabCtrl = TabCtrl( wnd.tabCtrl )
		for index in xrange( 6 ):
			tabName = "btn_" + str( index )
			tab = getattr( wnd.tabCtrl, tabName, None )
			if tab is None : continue
			panelName = "panel_" + str( index )
			panel = getattr( wnd.tabCtrl, panelName, None )
			if panel is None : continue
			pyBtn = TabButton( tab )
			labelGather.setPyBgLabel( pyBtn, "RankWindow:main", tabName )
			pyPanel = RankPanel( panel )
			pyPage = TabPage( pyBtn, pyPanel )
			pyPage.rankType = index
			self.__pyTabCtrl.addPage( pyPage )

		self.__pyTabCtrl.onTabPageSelectedChanged.bind( self.__onPageChange )

		self.__pyShutBtn = HButtonEx( wnd.shutBtn )				#�رհ�ť
		self.__pyShutBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyShutBtn.onLClick.bind( self.__onShut )

		self.__pyRtExpt = CSRichText( wnd.rtExplain ) 			#��ǰ���а�˵��
		self.__pyRtExpt.align = "C"
		self.__pyRtExpt.text = ""

		self.__pyRankInfo = CSRichText( wnd.rtInfo )				#�¿�˵��
		self.__pyRankInfo.text = labelGather.getText( "RankWindow:main", "bankInfo" )

		# ---------------------------------------------
		# ���ñ�ǩ
		# ---------------------------------------------
		labelGather.setLabel(  wnd.lbTitle, "RankWindow:main", "lbTitle" )
		labelGather.setPyBgLabel( self.__pyShutBtn, "RankWindow:main", "shutBtn" )
		labelGather.setLabel(  wnd.tabCtrl.panel_1.opt_0.lbText, "RankWindow:panel_1", "opt_0" )
		labelGather.setLabel(  wnd.tabCtrl.panel_1.opt_1.lbText, "RankWindow:panel_1", "opt_1" )
		labelGather.setLabel(  wnd.tabCtrl.panel_1.opt_2.lbText, "RankWindow:panel_1", "opt_2" )
		labelGather.setLabel(  wnd.tabCtrl.panel_1.opt_3.lbText, "RankWindow:panel_1", "opt_3" )
		labelGather.setLabel(  wnd.tabCtrl.panel_1.opt_4.lbText, "RankWindow:panel_1", "opt_4" )
		labelGather.setLabel(  wnd.tabCtrl.panel_1.opt_5.lbText, "RankWindow:panel_1", "opt_5" )
		labelGather.setLabel(  wnd.tabCtrl.panel_2.opt_0.lbText, "RankWindow:panel_2", "opt_0" )
		labelGather.setLabel(  wnd.tabCtrl.panel_2.opt_1.lbText, "RankWindow:panel_2", "opt_1" )
		labelGather.setLabel(  wnd.tabCtrl.panel_2.opt_2.lbText, "RankWindow:panel_2", "opt_2" )
		labelGather.setLabel(  wnd.tabCtrl.panel_2.opt_3.lbText, "RankWindow:panel_2", "opt_3" )
		labelGather.setLabel(  wnd.tabCtrl.panel_2.opt_4.lbText, "RankWindow:panel_2", "opt_4" )
		labelGather.setLabel(  wnd.tabCtrl.panel_3.opt_0.lbText, "RankWindow:panel_3", "opt_0" )
		labelGather.setLabel(  wnd.tabCtrl.panel_3.opt_1.lbText, "RankWindow:panel_3", "opt_1" )
		labelGather.setLabel(  wnd.tabCtrl.panel_3.opt_2.lbText, "RankWindow:panel_3", "opt_2" )
		labelGather.setLabel(  wnd.tabCtrl.panel_3.opt_3.lbText, "RankWindow:panel_3", "opt_3" )
		labelGather.setLabel(  wnd.tabCtrl.panel_3.opt_4.lbText, "RankWindow:panel_3", "opt_4" )
		labelGather.setLabel(  wnd.tabCtrl.panel_3.opt_5.lbText, "RankWindow:panel_3", "opt_5" )
		labelGather.setLabel(  wnd.tabCtrl.panel_3.opt_6.lbText, "RankWindow:panel_3", "opt_6" )
		labelGather.setLabel(  wnd.tabCtrl.panel_5.opt_0.lbText, "RankWindow:panel_5", "opt_0" )
		labelGather.setLabel(  wnd.tabCtrl.panel_5.opt_1.lbText, "RankWindow:panel_5", "opt_1" )
		labelGather.setLabel(  wnd.tabCtrl.panel_5.opt_2.lbText, "RankWindow:panel_5", "opt_2" )
		labelGather.setLabel(  wnd.tabCtrl.panel_5.opt_3.lbText, "RankWindow:panel_5", "opt_3" )
		labelGather.setLabel(  wnd.tabCtrl.panel_5.opt_4.lbText, "RankWindow:panel_5", "opt_4" )
		labelGather.setLabel(  wnd.tabCtrl.panel_5.opt_5.lbText, "RankWindow:panel_5", "opt_5" )
		labelGather.setLabel(  wnd.tabCtrl.panel_5.opt_6.lbText, "RankWindow:panel_5", "opt_6" )

	# -----------------------------------------------------------------------------
	# pravite
	# -----------------------------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_SHOW_RANK_WINDOW"] = self.__onShowRankWnd
		self.__triggers["EVT_ON_RECEIVE_RANK_DATA"] = self.__onRecRankDatas
		self.__triggers["EVT_ON_SET_RANKBTNS_STATE"] = self.__onSetBtnState
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )

	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( eventMacro, self )
	# -----------------------------------------------------------

	def __delTrap( self ) :
		if self.__trapID is not None:
			BigWorld.delPot( self.__trapID )									#ɾ����ҵĶԻ�����
			self.__trapID = None

	def __onEntitiesTrapThrough( self, isEnter,handle ):
		if not isEnter:				#���NPC�뿪��ҶԻ�����
			self.hide()														#���ص�ǰ���״���

	# -------------------------------------------------------------------
	def __onShowRankWnd( self ):
		"""
		�������а����
		"""
		targeter=GUIFacade.getGossipTarget()
		distance = csconst.COMMUNICATE_DISTANCE
		if hasattr( targeter, "getRoleAndNpcSpeakDistance" ):
			distance = targeter.getRoleAndNpcSpeakDistance()
		self.__trapID = BigWorld.addPot( targeter.matrix,distance+1, self.__onEntitiesTrapThrough )#�򿪴��ں�Ϊ�����ӶԻ�����
		self.show()

	def __onRecRankDatas( self, rankType, beginIndex, rankingDatas ):
		"""
		�������а�����
		"""
		for tabPage in self.__pyTabCtrl.pyPages:
			if tabPage.rankType == rankType:
				pyRankPanel = tabPage.pyPanel
				pyRankPanel.setRankItemInfo( beginIndex, rankingDatas )
				
	def __onSetBtnState( self, rankType, state ):
		"""
		����ҳ��״̬����ֹ��ҳ����Ϣû�����꣬����������ҳ����Ϣ
		"""
		for pyTabPage in self.__pyTabCtrl.pyPages:
			if pyTabPage.rankType == rankType or pyTabPage.enable == state:
				continue
			pyTabPage.enable = state

	def __onPageChange( self, pyTabCtrl ):
		"""
		ѡ��ͬ���а񣬸��²�ͬ˵��
		"""
		player = BigWorld.player()
		rankType = self.__pyTabCtrl.pySelPage.rankType
		pyRankPanel = self.__pyTabCtrl.pySelPage.pyPanel
		pyRankPanel.clearRanks()
		if rankType != TONG_ACTIVEPOINT_TYPE:
			self.__pyRtExpt.text = labelGather.getText( "RankWindow:main", "exp_%d"%rankType )
			player.beginQueryGameRanking( rankType )

	def __onShut( self ):
		"""
		�رմ���
		"""
		self.hide()

	# -----------------------------------------------------------------------------
	# public
	# -----------------------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def show( self ):
		"""
		��ʾ����
		"""

		Window.show( self )

	def hide( self ):
		"""
		���ش���
		"""
		for pyTabPage in self.__pyTabCtrl.pyPages:
			pyPanel = pyTabPage.pyPanel
			pyPanel.clearRanks()
		self.__delTrap()
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )
		Window.hide( self )

	def onLeaveWorld( self ):
		"""
		�뿪��Ϸ����
		"""
		self.hide()