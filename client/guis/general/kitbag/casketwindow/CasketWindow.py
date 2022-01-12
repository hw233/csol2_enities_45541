# -*- coding: gb18030 -*-
# $Id: CasketWindow.py

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabPanel
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabPage
from AttrExtractPanel import AttrExtractPanel
from AttrPourPanel import AttrPourPanel
from EquipBuildPanel import EquipBuildPanel
from EquipIntensifyPanel import EquipIntensifyPanel
from SpecialStuffComPanel import SpecialStuffComPanel
from guis.OpIndicatorObj import OpIndicatorObj
from EquipBindPanel import EquipBindPanel

class CasketWindow( Window, TabCtrl, OpIndicatorObj ):
	"""
	新版神机匣 
	"""
	_func_maps = { 0:EquipBuildPanel, 1:AttrExtractPanel, 2:AttrPourPanel, 3:EquipIntensifyPanel, 4: SpecialStuffComPanel, 5:EquipBindPanel }
	
	def __init__( self, kitbagID = 0, pyBinder = None ):
		wnd = GUI.load( "guis/general/kitbag/casketwindow/newwnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		TabCtrl.__init__( self, wnd )
		OpIndicatorObj.__init__( self )
		self.__kitbagID = kitbagID
		self.__pyBinder = pyBinder
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.canBeUpgrade_ 	 = True
		self.escHide_ 		 = True
		self.pyItems = {}					#神机匣背包格子
		self.__triggers = {}
		self.__registerTriggers()

		self.__initialize( wnd )
		self.addToMgr( "casketWindow" )
		setattr( rds.ruisMgr,"casketWindow",self )
	
	def __initialize( self, wnd ):
		labelGather.setPyLabel( self.pyLbTitle_, "CasketWindow:main", "lbTitle" )
		self.__pyPanels = {}
		for index,  panelCls in self._func_maps.items():
			tabName = "tab_" + str( index )
			tab = getattr( wnd, tabName, None )
			if tab is None : continue
			panelName = "panel_" + str( index )
			panel = getattr( wnd, panelName, None )
			if panel is None : continue
			pyBtn = TabButton( tab )
			labelGather.setPyBgLabel( pyBtn, "CasketWindow:main", tabName )
			if panelCls is None:continue
			pyPanel = panelCls( panel )
			pyPage = TabPage( pyBtn, pyPanel )
			self.addPage( pyPage )
		self.onTabPageSelectedChanged.bind( self.__onTabFucChanged )

	# -----------------------------------------------------------------------------
	# pravite
	# -----------------------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		产生事件
		"""
		TabCtrl.generateEvents_( self )
		Window.generateEvents_( self )

	def __registerTriggers( self ):

		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )

	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( eventMacro, self )
	# -----------------------------------------------------------
	
	def __onTabFucChanged( self, pyTabCtr ):
		if pyTabCtr is None:return
		self.clearIndications()
		rds.opIndicator.fireRegIdtsOfTrigger( ( "gui_visible","casketWindow" ) )
		rds.opIndicator.fireRegIdtsOfTrigger( ( "gui_sub_panel_visible","casketWindow" ) )
		
	def __showSelectSubPanel( self, idtId, btnKey ):
		pyBtn = self.pyBtns[btnKey]
		if not pyBtn.selected:
			toolbox.infoTip.showHelpTips( idtId, pyBtn )
			self.addVisibleOpIdt( idtId )
			
	def __showDragItem( self, idtId, *agrs ):
		panelIndex = agrs[0]
		if len(agrs) == 2:
			itemType = agrs[1]
			self.pyPanels[panelIndex].showDragItemIndication( idtId, itemType )	
		else:
			self.pyPanels[panelIndex].showOkIndication( idtId )	
		
	def _initOpIndicationHandlers( self ) :
		"""
		"""
		trigger = ( "gui_visible","casketWindow" )
		condition = ( "quest_uncompleted", )
		idtIds = rds.opIndicator.idtIdsOfCmd( condition, trigger )
		for i in idtIds :
			self._opIdtHandlers[i] = self.__showSelectSubPanel
			
		trigger = ( "gui_sub_panel_visible","casketWindow" )
		condition = ( "quest_uncompleted", )
		idtIds = rds.opIndicator.idtIdsOfCmd( condition, trigger )
		for i in idtIds :
			self._opIdtHandlers[i] = self.__showDragItem
			
	def onMove_( self, dx, dy ) :
		self.relocateIndications()

	# -----------------------------------------------------------------------------
	# public
	# -----------------------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def show( self, pyOwner = None ):
		"""
		显示窗口
		"""
		self.__pyBinder.onBeforeShow()
		for pyTabPage in self.pyPages:
			pyPanel = pyTabPage.pyPanel
			pyPanel.onShow()
		Window.show( self )
		rds.opIndicator.fireRegIdtsOfTrigger( ( "gui_visible","casketWindow" ) )
		rds.opIndicator.fireRegIdtsOfTrigger( ( "gui_sub_panel_visible","casketWindow" ) )

	def hide( self ):
		"""
		隐藏窗口
		"""
		for pyTabPage in self.pyPages:
			pyPanel = pyTabPage.pyPanel
			pyPanel.onHide()
		Window.hide( self )

	def onLeaveWorld( self ):
		"""
		离开游戏调用
		"""
		for pyTabPage in self.pyPages:
			pyPanel = pyTabPage.pyPanel
			pyPanel.onLeaveWorld()
		self.hide()
	
	def onEnterWorld( self ):
		"""
		进入游戏
		"""
		self.pyPages[0].pyPanel.onEnterWorld()
	
	def delItems( self ):
		"""
		清空各面板
		"""
		pass
	
	def getItem( self, orderID ):
		"""
		获取物品
		"""
		pass