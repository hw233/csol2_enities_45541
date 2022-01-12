# -*- coding: gb18030 -*-
#
# written by zzh 2012-10-11

from guis import *
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from LabelGather import labelGather
import csconst
import GUIFacade
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabPage
from guis.controls.TabCtrl import TabButton
from SearchMaster import SearchMaster
from SearchPrentice import SearchPrentice

class SearchTeachWindow( Window ):
	def __init__( self ):
		wnd = GUI.load( "guis/general/searchteachwindow/window.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )		
		self.__initialize( wnd )
		self.__triggers = {}
		self.__registerTriggers()
		
		self.__trapID = None
	
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		self.__pyTabCtrl = TabCtrl( wnd.tc )
		pyMasterBtn = TabButton( wnd.tc.btn_0 )
		pyMasterBtn.setStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( pyMasterBtn, "SearchTeachWindow:main", "btn_0" )
		pyMasterPanel = SearchMaster(wnd.tc.panel_0 )
		pyPage = TabPage( pyMasterBtn, pyMasterPanel )
		self.__pyTabCtrl.addPage( pyPage )
		
		pyPrenticeBtn = TabButton( wnd.tc.btn_1 )
		pyPrenticeBtn.setStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( pyPrenticeBtn, "SearchTeachWindow:main", "btn_1" )
		pyPrenticePanel = SearchPrentice(wnd.tc.panel_1 )
		pyPage = TabPage( pyPrenticeBtn, pyPrenticePanel )
		self.__pyTabCtrl.addPage( pyPage )
		self.__pyTabCtrl.onTabPageSelectedChanged.bind( self.__onTabSelectChanged )
		
		self.__pyRefreshBtn = HButtonEx(wnd.btnReflash )
		self.__pyRefreshBtn.setStatesMapping( UIState.MODE_R3C1 )
		self.__pyRefreshBtn.onLClick.bind( self.__onClickRefreshBtn )
		
		self.__pyRequestBtn = HButtonEx(wnd.btnRequest )
		self.__pyRequestBtn.setStatesMapping( UIState.MODE_R3C1 )
		self.__pyRequestBtn.onLClick.bind( self.__onClickRequestBtn )
		
		self.__pyShutBtn = HButtonEx(wnd.btnShut )
		self.__pyShutBtn.setStatesMapping( UIState.MODE_R3C1 )
		self.__pyShutBtn.onLClick.bind( self.__onClickCloseBtn )
		
		labelGather.setPyLabel( self.pyLbTitle_, "SearchTeachWindow:main", "lbTitle" )
		labelGather.setPyBgLabel( self.__pyRefreshBtn, "SearchTeachWindow:main", "btnRefresh" )
		labelGather.setPyBgLabel( self.__pyRequestBtn, "SearchTeachWindow:main", "btnRequestToMaster" )
		labelGather.setPyBgLabel( self.__pyShutBtn, "SearchTeachWindow:main", "btnShut" )
		

	# -------------------------------------------------
	def __registerTriggers( self ) :
		"""
		"""
		self.__triggers["EVT_ON_TOGGLE_SEARCH_MASTER_AND_PRENTICE"] = self.show
		self.__triggers["EVT_ON_TOGGLE_ADD_MASTER_INFO"] = self.__onReceiveMasterInfo
		self.__triggers["EVT_ON_TOGGLE_ADD_PRENTICE_INFO"] = self.__onAddPrentice
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )
			
	def __onTabSelectChanged( self ) :
		"""
		根据分页设置按钮标题
		"""
		pySelPage = self.__pyTabCtrl.pySelPage
		index = pySelPage.index
		if index == 0:
			labelGather.setPyBgLabel( self.__pyRequestBtn, "SearchTeachWindow:main", "btnRequestToMaster" )
		elif index == 1:
			labelGather.setPyBgLabel( self.__pyRequestBtn, "SearchTeachWindow:main", "btnRequestToPrentice" )

	def __deregisterTriggers( self ) :
		"""
		"""
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )

	def onEvent( self, eventMacro, *args ) :
		"""
		"""
		self.__triggers[eventMacro]( *args )
		
	# -------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __addTrap( self ):
		if self.__trapID:
			self.__delTrap()

		distance = csconst.COMMUNICATE_DISTANCE
		if hasattr( GUIFacade.getGossipTarget(), "getRoleAndNpcSpeakDistance" ):
			distance = GUIFacade.getGossipTarget().getRoleAndNpcSpeakDistance()
		self.__trapID = BigWorld.addPot(GUIFacade.getGossipTarget().matrix ,distance, self.__onEntitiesTrapThrough )

	def __delTrap( self ) :
		if self.__trapID :
			BigWorld.delPot( self.__trapID )
			self.__trapID = None

	def __onEntitiesTrapThrough( self,isEnter, handle ):
		if not isEnter:
			self.hide()														#隐藏当前与NPC对话窗口

	def __onClickRefreshBtn( self ) :
		"""
		刷新界面，重新查询数据
		"""
		pyPanel = self.__pyTabCtrl.pySelPage.pyPanel
		pyPanel.requestPlayerInfo()

	def __onClickRequestBtn( self ) :
		"""
		请求拜师或者收徒
		"""
		pyPanel = self.__pyTabCtrl.pySelPage.pyPanel
		if self.__pyTabCtrl.pySelPage.index == 0:
			pyPanel.requestBePrentice()
		elif self.__pyTabCtrl.pySelPage.index == 1:
			pyPanel.requestBeMaster()

	def __onClickCloseBtn( self ):
		"""
		"""
		self.hide()

	def __onReceiveMasterInfo( self, master ):
		"""
		添加师傅信息
		@param		master	: 师傅信息列表
		@type		master	: list
		"""
		pyPanel = self.__pyTabCtrl.pyPages[0].pyPanel
		pyPanel.onAddMasterInfo( master )
		
	def __onAddPrentice( self, prentice ) :
		"""
		添加徒弟信息
		@param		prentice	: 徒弟信息列表
		@type		prentice	: list
		"""
		print "prentice---------------------:",prentice
		pyPanel = self.__pyTabCtrl.pyPages[1].pyPanel
		pyPanel.onAddPrenticeInfo( prentice )
		
	# ---------------------------------------------------------
	# public
	# ---------------------------------------------------------
	def show( self ) :
		level = BigWorld.player().level
		if csconst.TEACH_MASTER_MIN_LEVEL > level :
			self.__pyTabCtrl.pyPages[0].selected = True
		else:
			self.__pyTabCtrl.pyPages[1].selected = True
		Window.show( self )
		self.__addTrap()

	def hide( self ):
		self.__pyTabCtrl.pyPages[0].pyPanel.clearItems()
		self.__pyTabCtrl.pyPages[1].pyPanel.clearItems()
		Window.hide( self )
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )
		self.__delTrap()

	def onLeaveWorld( self ) :
		self.hide()
		
	@property
	def trapEntity( self ) :
		return BigWorld.entities.get( self.__trapID )
