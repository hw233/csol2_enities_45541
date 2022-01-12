# -*- coding: gb18030 -*-
#
# $Id: SysSetting.py, fangpengjun Exp $

"""
implement KeySetting window class
"""
from guis import *
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabPage
from guis.controls.TabCtrl import TabPanel
import weakref
from AVPanel import AVPanel
from BaseInfoPanel import RoleInfoPanel
from BaseInfoPanel import DisplayPanel
from BaseInfoPanel import CombatPanel
from ShortcutPanel import SCActionPanel
from ShortcutPanel import SCDisplayPanel
from ShortcutPanel import SCQuickBarPanel
from ShortcutPanel import SCCombatPanel
from ShortcutPanel import ShortcutPanel
from LabelGather import labelGather


class GameSetting( Window ):

	__instance = None

	def __init__( self ):
		assert GameSetting.__instance is None , "GameSetting instance has been created"
		GameSetting.__instance = self
		wnd = GUI.load( "guis/general/syssetting/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.canBeUpgrade_ 	 = True
		self.escHide_ 		 = True
		self.weakrefList=[]
		
		self.__PANEL_MAP = { "AV" 				: [ AVPanel, False ],
							"roleInfo"			: [ RoleInfoPanel, False ],
							"display"			: [ DisplayPanel, False ],
							"combat"			: [ CombatPanel, False ],
							"shortcutAction"	: [ SCActionPanel, False ],
							"shortcutDisplay"	: [ SCDisplayPanel, False ],
							"shortcutCombat"	: [ SCCombatPanel, False ],
							"shortcutQuickBar"	: [ SCQuickBarPanel, False ],
							}

		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( wnd )

	@staticmethod
	def instance():
		if GameSetting.__instance is None:
			GameSetting.__instance = GameSetting()
		return GameSetting.__instance

	def __del__( self ) :
		if Debug.output_del_GameSetting :
			INFO_MSG( str( self ) )

	def __initialize( self, wnd ):
		self.pyCloseBtn_.onLClick.bind( self.__onCancel )

		self.__pySetDefaultBtn = HButtonEx( wnd.def_btn )
		self.__pySetDefaultBtn.isOffsetText = True
		self.__pySetDefaultBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pySetDefaultBtn.onLClick.bind( self.__onSetDefault)

		self.__pyOkBtn = HButtonEx( wnd.ok_btn )
		self.__pyOkBtn.isOffsetText = True
		self.__pyOkBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyOkBtn.onLClick.bind( self.__onOK )

		self.__pyAppBtn = HButtonEx( wnd.app_btn )
		self.__pyAppBtn.isOffsetText = True
		self.__pyAppBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyAppBtn.onLClick.bind( self.__onApplied )

		self.__pyTabCtrl = TabCtrl( wnd.tabCtrl )
		self.__pyTabCtrl.onTabPageSelectedChanged.bind( self.__onTabPageSelectedChanged )

		self.__createAllTabPage( wnd.tabCtrl )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pySetDefaultBtn, "gamesetting:main", "btnDef" )
		labelGather.setPyBgLabel( self.__pyOkBtn, "gamesetting:main", "btnOk" )
		labelGather.setPyBgLabel( self.__pyAppBtn, "gamesetting:main", "btnApp" )
		labelGather.setLabel( wnd.tabBtns_Frame.stTitle, "gamesetting:main", "stSetType" )
		labelGather.setLabel( wnd.lbTitle, "gamesetting:main", "lbTitle" )


	# ----------------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_RESOLUTION_CHANGED"] = self.__onResolutionChanged
		self.__triggers["EVT_ON_SHORTCUT_CHANGED"] = self.__onShortcutChanged
		self.__triggers["EVT_ON_BASEINFO_CHANGED"] = self.__onBaseInfoChanged
		self.__triggers["EVT_ON_AVPANEL_CHANGED"] = self.__onAVPanelChanged
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __unregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )

	def __createAllTabPage( self, tabCtrl ) :
		"""
		创建所有tab分页
		"""
		for cName, cGui in tabCtrl.children :
			if "tabBtn_" in cName :
				panelName = cName.split( "_" )[-1]
				pyTabBtn = self.__createTabBtn( cGui )
				pyTabBtn.name = panelName
				labelGather.setPyBgLabel( pyTabBtn, "gamesetting:main", cName )
				pyTabPanel = EmptyPanel( self )
				tabPage = TabPage( pyTabBtn, pyTabPanel )
				self.__pyTabCtrl.addPage( tabPage )
				
	def __onTabPageSelectedChanged( self ) :
		"""
		选中某分页时再创建该分页
		"""
		self.__enabelBtn()
		pySelPage = self.__pyTabCtrl.pySelPage
		if pySelPage is None : return
		pyBtn = pySelPage.pyBtn
		panelName = pyBtn.name
		panelInstance = self.__PANEL_MAP[ panelName ][-1]
		if panelInstance : return									  # 如果已经创建了该实例，则不再创建
		panelScript = self.__PANEL_MAP[ panelName ][0]
		if panelScript is None : return
		pyTabPanel = panelScript( self )
		pyTabPanel.onEnterWorld()
		self.__pyTabCtrl.addPyChild( pyTabPanel )
		self.weakrefList.append(weakref.ref(pyTabPanel))
		pyTabPanel.left = 170.0
		pyTabPanel.top = 0.0
		self.__PANEL_MAP[ panelName ][-1] = True
		pySelPage.setPage( pyBtn, pyTabPanel )
		pyBtn.selected = True
		
	def __createTabBtn( self, btnGui ) :
		"""
		创建tab按钮
		"""
		pyBtn = TabButton( btnGui )
		pyBtn.setStatesMapping( UIState.MODE_R4C1 )
		pyBtn.commonForeColor = 255.0, 251.0, 182.0
		pyBtn.highlightForeColor = 255.0, 251.0, 182.0
		pyBtn.selectedForeColor = 1.0, 246.0, 255.0
		pyBtn.isOffsetText = True
		pyBtn.effDisable = True
		return pyBtn
	
	def __onResolutionChanged( self, preReso ):
		"""
		分辨率改变
		"""
		avPanel = self.__pyTabCtrl.pyPages[3].pyPanel
		avPanel.onResolutionChanged( preReso )
		
	def __onShortcutChanged( self, changed ):
		"""
		快捷键设置改变
		"""
		self.__pyAppBtn.enable = changed

	def __onBaseInfoChanged( self, changed ):
		"""
		勾选项改变
		"""
		self.__pyAppBtn.enable = changed

	def __onAVPanelChanged( self, changed ):
		"""
		视频选项改变
		"""
		self.__pyAppBtn.enable = changed

	# -------------------------------------------------
	def __onSetDefault( self ): #某个面板内容默认设置
		pySelPage = self.__pyTabCtrl.pySelPage
		pySelPage.pyPanel.setDefault()

	def __onApplied( self ) :
		"""
		应用
		"""
		pySelPage = self.__pyTabCtrl.pySelPage
		pySelPage.pyPanel.onApplied()
#		rds.shortcutMgr.save()
#		rds.viewInfoMgr.save()

	def __onOK( self ):
		"""
		确定
		"""
		for pyPage in self.__pyTabCtrl.pyPages :
			pyPage.pyPanel.onOK()
		rds.shortcutMgr.save()
		rds.viewInfoMgr.save()
		self.hide()

	def __onCancel( self ):
		"""
		取消
		"""
		for pyPage in self.__pyTabCtrl.pyPages :
			pyPage.pyPanel.onCancel()
		rds.shortcutMgr.cancel()
		rds.viewInfoMgr.cancel()
		self.hide()

	def __enabelBtn( self ) :
		"""
		根据当前选择的面板使能按钮
		"""
		pySelPage = self.__pyTabCtrl.pySelPage
		pyPanel = None
		if pySelPage is not None :
			pyPanel = pySelPage.pyPanel
#			self.__pySetDefaultBtn.enable = not isinstance( pyPanel, AVPanel )
			if hasattr( pyPanel, "changed" ) and pyPanel.changed == False:
				self.__pyAppBtn.enable = pyPanel.changed
			else:
				self.__pyAppBtn.enable = True

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onKeyDown_( self, key, mods ):
		"""
		"""
		Window.onKeyDown_( self, key, mods )
		if ( mods == 0 ) and ( key == KEY_ESCAPE ):
			rds.shortcutMgr.cancel()
			rds.viewInfoMgr.cancel()
			self.hide()

	# ---------------------------------------------------------------------
	# public
	# ---------------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def onLeaveWorld( self ):
		self.__pyTabCtrl.pyPages[0].selected = True
		self.hide()

	def onEnterWorld( self ) :
		for pyPage in self.__pyTabCtrl.pyPages :
			pyPage.pyPanel.onEnterWorld()
	
	def initGraphicsSetting( self ):
		self.__pyTabCtrl.pyPages[3].selected = True

	def show( self ):
		self.addToMgr()
		self.__pyTabCtrl.pyPages[0].selected = True
		self.onEnterWorld()
		Window.show( self )

	def hide( self ):
		Window.hide( self )
		for i in xrange(len(self.weakrefList)):
			self.weakrefList.pop()().hide()
		GameSetting.__instance = None
		self.dispose()

	def onActivated( self ) :
		"""
		所属窗口激活时被调用
		"""
		Window.onActivated( self )
		for pyPage in self.__pyTabCtrl.pyPages :
			pyPage.pyPanel.onActivated()

	def onInactivated( self ) :
		"""
		所属窗口取消激活状态时被调用
		"""
		Window.onInactivated( self )
		for pyPage in self.__pyTabCtrl.pyPages :
			pyPage.pyPanel.onInactivated()

# --------------------------------------------------------------------
# 用一空的面板作为初始化窗口的默认面板
# --------------------------------------------------------------------
class EmptyPanel( TabPanel ) :

	def __init__( self, pyBinder = None ) :
		panel = GUI.Simple("")
		TabPanel.__init__( self, panel, pyBinder )

	def setDefault( self ) :
		pass

	def onApplied( self ) :
		pass

	def onOK( self ) :
		pass

	def onCancel( self ) :
		pass

	def onEnterWorld( self ) :
		pass

	def onActivated( self ) :
		pass

	def onInactivated( self ) :
		pass
	
	def initGraphicsSetting( self ):
		pass

	def onResolutionChanged( self, preReso ):
		pass