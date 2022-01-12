# -*- coding: gb18030 -*-
#
# $Id: WarRanking.py Exp $

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.common.PyGUI import PyGUI
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabPanel
from guis.controls.TabCtrl import TabPage
from guis.controls.TabCtrl import TabButton
from guis.controls.ODListPanel import ODListPanel
from guis.controls.ODListPanel import ViewItem
from guis.tooluis.fulltext.FullText import FullText
from WarIntergral import TaxisButton
import GUIFacade
import csconst

class WarFixture( Window ):
	def __init__( self ):
		wnd = GUI.load( "guis/general/tongabout/citywar/fixtureswnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_  = True
		self.__triggers = {}
		self.__registerTriggers()
		self.addToMgr()
		self.__trapID = 0
		self.__initialize( wnd )

	def __initialize( self, wnd ):
		self.__pyStTitle = StaticText( wnd.lbTitle )
		self.__pyStTitle.text = ""
		self.__pyTabCtrl = TabCtrl( wnd.tabCtrl )
		index = 0
		while True :											#初始化TabCtrl
			tabName = "btn_" + str( index )
			tabBtn = getattr( wnd.tabCtrl, tabName, None )
			if tabBtn is None : break
			panelName = "panel_" + str( index )
			tabPanel = getattr( wnd.tabCtrl, panelName, None )
			if tabPanel is None : break
			pyTabBtn = TabButton( tabBtn )
			pyTabBtn.setStatesMapping( UIState.MODE_R3C1 )
			labelGather.setPyBgLabel( pyTabBtn, "TongAbout:WarFixture", tabName )
			pyTabPanel = None
			if index == 0:
				pyTabPanel = RankPanel( tabPanel )
				pyTabPanel.isSort = True
			else:
				pyTabPanel = StatusPanel( tabPanel )
			pyTabPage = TabPage( pyTabBtn, pyTabPanel )
			pyTabPage.selected = False
			self.__pyTabCtrl.addPage( pyTabPage )
			index += 1
		self.__pyTabCtrl.onTabPageSelectedChanged.bind( self.__onPageSelected )

	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_OPEN_CITYWAR_INFO_WND"] = self.__onShowWnd
		#self.__triggers["EVT_ON_RECIEVE_CITYWAR_POINTS"] =  self.__onRecPoints
		self.__triggers["EVT_ON_RECIEVE_CITYWAR_TABLE"] = self.__onRecWarTable
		for trigger in self.__triggers :
			ECenter.registerEvent( trigger, self )

	def __desregisterTriggers( self ) :
		for trigger in self.__triggers :
			ECenter.unregisterEvent( trigger, self )
	# ------------------------------------------------------------
	def __onShowWnd( self, type ):
		"""
		弹出查询界面
		"""
		player = BigWorld.player()
		distance = csconst.COMMUNICATE_DISTANCE
		if hasattr( GUIFacade.getGossipTarget(), "getRoleAndNpcSpeakDistance" ):
			distance = GUIFacade.getGossipTarget().getRoleAndNpcSpeakDistance()
		self.__trapID = player.addTrapExt( csconst.COMMUNICATE_DISTANCE, self.__onEntitiesTrapThrough )
		self.show( )
	# -----------------------------------------------------------
	def __delTrap( self ) :
		player = BigWorld.player()
		if self.__trapID :
			player.delTrap( self.__trapID )
			self.__trapID = 0

	def __onEntitiesTrapThrough( self, entitiesInTrap ):
		gossiptarget = GUIFacade.getGossipTarget()
		if gossiptarget and gossiptarget not in entitiesInTrap:
			self.hide()

	def __onRecPoints( self, datas ):
		"""
		城战积分数据
		"""
		pySelPage = self.__pyTabCtrl.pySelPage
		index = pySelPage.index
		if index != 0:return
		self.__pyStTitle.text = labelGather.getText( "TongAbout:WarFixture", "lbTitle_0" )
		pyPanel = pySelPage.pyPanel
		pyPanel.clearItems()
		pyPanel.updateDatas( datas )

	def __onRecWarTable( self, datas ):
		"""
		收到比赛数据，根据数据区分是赛程还是赛况
		"""
		pySelPage = self.__pyTabCtrl.pySelPage
		index = pySelPage.index
		if index == 0:return
		if type == 0:
			self.__pyStTitle.text = labelGather.getText( "TongAbout:WarFixture", "lbTitle_1" )
		else:
			self.__pyStTitle.text = labelGather.getText( "TongAbout:WarFixture", "lbTitle_2" )
		pyPanel = pySelPage.pyPanel
		pyPanel.setStatusByType( type, datas )

	def __onPageSelected( self, pyTabCtrl ):
		index = pyTabCtrl.pySelPage.index
		player = BigWorld.player()
		spaceID = player.spaceID
		cityName = BigWorld.getSpaceDataFirstForKey( spaceID, csconst.SPACE_SPACEDATA_KEY )
		player.cell.tong_onQueryCityWarTable( cityName )

	# -------------------------------------------------------------
	def onEvent( self, evtMacro, *agrs ) :
		self.__triggers[evtMacro]( *agrs )

	def onLeaveWorld( self ):
		self.hide()

	def show( self ):
		self.__pyTabCtrl.pySelPage = self.__pyTabCtrl.pyPages[0]
		player = BigWorld.player()
		cityName = BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_KEY )
		player.cell.tong_onQueryCityWarTable( cityName )
		Window.show( self )

	def hide( self ):
		self.__trapID = 0
		Window.hide( self )

# ---------------------------------------------------------------------------
class RankPanel( TabPanel ):
	"""
	积分排名
	"""
	def __init__( self, panel ):
		TabPanel.__init__( self, panel )
		self.__isSort = False
		self.__initialize( panel )

	def __initialize( self, panel ):

		self.__pyListPanel = ODListPanel( panel.listPanel, panel.listBar )
		self.__pyListPanel.onItemSelectChanged.bind( self.__interSelChanged )
		self.__pyListPanel.onViewItemInitialized.bind( self.__onInitItem )
		self.__pyListPanel.onDrawItem.bind( self.__onDrawItem )
		self.__pyListPanel.autoSelect = False
		self.__pyListPanel.itemHeight = 24.0
		self.__pyListPanel.ownerDraw = True

		self.__pyTaxisBtns = {}
		for name, item in panel.children:
			if name.startswith( "taxisBtn_" ):
				index = int( name.split( "_" )[1] )
				pyTaxisBtn = TaxisButton( item )
				pyTaxisBtn.taxisIndex = index
				pyTaxisBtn.setStatesMapping( UIState.MODE_R4C1 )
				labelGather.setPyBgLabel( pyTaxisBtn, "TongAbout:WarFixture", name )
				pyTaxisBtn.onLClick.bind( self.__onSortByTaxi )
				self.__pyTaxisBtns[index] = pyTaxisBtn
		
		labelGather.setLabel( panel.explainText, "TongAbout:WarFixture", "warTips" )

	def __onInitItem( self, pyViewItem ) :
		"""
		初始化添加的NPC列表项
		"""
		pyRankItem = RankItem( pyViewItem )
		pyViewItem.pyRankItem = pyRankItem
		pyViewItem.addPyChild( pyRankItem )
		pyRankItem.pos = 0, 0

	def __onDrawItem( self, pyViewItem ) :
		rankInfo = pyViewItem.listItem
		pyRankItem = pyViewItem.pyRankItem
		pyRankItem.updateInfo( rankInfo )

	def __interSelChanged( self, pyViewItem ):
		pass

	def __onSortByTaxi( self, pyBtn ) :
		taxisIndex = pyBtn.taxisIndex
		taxisReverse = pyBtn.taxisReverse
		self.__pyListPanel.sort( key = lambda item : item[taxisIndex], reverse = taxisReverse )

	def updateDatas( self, datas ):
		datas.sort( key = lambda data : data["point"], reverse = True ) #按积分从高到低排序
		for index, data in enumerate( datas ):
#			tongDBID = data["tongDBID"]
			tongName = data["tongName"]
			winCount = data["winCount"]
			failCount = data["failCount"]
			dogfallCount = data["dogfallCount"]
			point = data["point"]
			self.__pyListPanel.addItem( [index + 1, tongName, winCount, failCount, dogfallCount, point] )

	def clearItems( self ):
		self.__pyListPanel.clearItems()

	def _getIsSort( self ):
		return self.__isSort

	def _setIsSort( self, isSort ):
		self.__isSort = isSort
		for pyTaxisBtn in self.__pyTaxisBtns.itervalues():
			pyTaxisBtn.isSort = isSort

	isSort = property( _getIsSort, _setIsSort )								# 是否排序

# ------------------------------------------------------------
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
import Language
class StatusPanel( TabPanel ):
	"""
	赛况、赛程面板
	"""
	week_maps = {	1:labelGather.getText( "TongAbout:BuildReSearch", "number_1" ),
				2:labelGather.getText( "TongAbout:BuildReSearch", "number_2" ),
				3:labelGather.getText( "TongAbout:BuildReSearch", "number_3" ),
				4:labelGather.getText( "TongAbout:BuildReSearch", "number_4" ),
				5:labelGather.getText( "TongAbout:BuildReSearch", "number_5" )
	}
	
	def __init__( self, panel ):
		TabPanel.__init__( self, panel )
		self.__initialize( panel )

	def __initialize( self, panel ):
		self.__pyListPanel = ODListPanel( panel.listPanel, panel.listBar )
		self.__pyListPanel.onItemSelectChanged.bind( self.__interSelChanged )
		self.__pyListPanel.autoSelect = False
		self.__pyListPanel.itemHeight = 24.0
		self.__pyListPanel.ownerDraw = True						# 开启自定义绘制

		self.__pyStStatus = StaticText( panel.stStatus )
		self.__pyStStatus.text = ""

		self.__pyTitleBgs = {}
		for name, item in panel.children:
			if name.startswith( "headTitle_" ):
				index = int( name.split( "_" )[1] )
				pyTitleBg = TitleBg( item, self.__pyListPanel )
				pyTitleBg.isSort = True
				pyTitleBg.index = index
				self.__pyTitleBgs[index] = pyTitleBg

	def __onInitLapItem( self, pyViewItem ) :
		"""
		初始化赛况
		"""
		pyLapItem = LaptimesItem( pyViewItem )
		pyViewItem.pyLapItem = pyLapItem
		pyViewItem.addPyChild( pyLapItem )
		pyLapItem.pos = 1, 0

	def __onDrawLapItem( self, pyViewItem ) :
		lapInfo = pyViewItem.listItem
		pyLapItem = pyViewItem.pyLapItem
		pyLapItem.updateInfo( lapInfo )

	def __onInitFixtItem( self, pyViewItem ):
		"""
		初始化赛赛程
		"""
		pyFixtItem = FixtureItem( pyViewItem )
		pyViewItem.pyFixtItem = pyFixtItem
		pyViewItem.addPyChild( pyFixtItem )
		pyFixtItem.pos = 1, 0

	def __onDrawFixtItem( self, pyViewItem ) :
		fixtInfo = pyViewItem.listItem
		pyFixtItem = pyViewItem.pyFixtItem
		pyFixtItem.updateInfo( fixtInfo )

	def __interSelChanged( self, pyInter ):
		pass

	def setStatusByType( self, type, datas ):
		for pyTitleBg in self.__pyTitleBgs.itervalues():
			pyTitleBg.visible = pyTitleBg.index == type
		self.__pyListPanel.clearItems()
		index = self.pyTabPage.index
		self.__pyListPanel.onViewItemInitialized.unbind( self.__onInitFixtItem )
		self.__pyListPanel.onDrawItem.unbind( self.__onDrawFixtItem )
		self.__pyListPanel.onViewItemInitialized.unbind( self.__onInitLapItem )
		self.__pyListPanel.onDrawItem.unbind( self.__onDrawLapItem )
		titles = {}
		if type == 0:
			self.__pyListPanel.onViewItemInitialized.bind( self.__onInitLapItem )
			self.__pyListPanel.onDrawItem.bind( self.__onDrawLapItem )
			titles = { 0: labelGather.getText( "TongAbout:WarFixture", "battleResults" )}
		else:
			titles = {	0: labelGather.getText( "TongAbout:WarFixture", "matchTime" ),
						1: labelGather.getText( "TongAbout:WarFixture", "battleTwo" )}
			self.__pyListPanel.onViewItemInitialized.bind( self.__onInitFixtItem )
			self.__pyListPanel.onDrawItem.bind( self.__onDrawFixtItem )
			if len( datas ) <= 0: #无比赛赛程数据
				self.__pyStStatus.text = labelGather.getText( "TongAbout:WarFixture", "noMatch" )
			else:
				self.__pyStStatus.text = ""
		self.__pyTitleBgs[type].setTaxisBtnTitle( titles )
		for data in datas:
			newData = []
			if type == 0: #赛况数据
				data0 = data[0]
				data1 = data[1]
				status = data[2]
				statusStr = ""
				resultColor = 255, 255, 255, 255
				flagStr = ""
				if status == 0:
					statusStr = labelGather.getText( "TongAbout:WarFixture", "battlePing" )
					resultColor = 1, 188, 54, 255
				else:
					statusStr = labelGather.getText( "TongAbout:WarFixture", "battleWin" )
					resultColor = 255, 24, 0, 255
					if Language.LANG == Language.LANG_GBK:
						flagStr = PL_Image.getSource( "guis/general/tongabout/citywar/winflag.gui" ) + PL_Space.getSource( 4 )
					elif Language.LANG == Language.LANG_BIG5:
						flagStr = PL_Image.getSource( "guis/general/tongabout/citywar/winflag_big5.gui" ) + PL_Space.getSource( 4 )
					if status == 2: #第二个胜
						data0 = data[1]
						data1 = data[0]
				statusStr = "%s%s%s"%( PL_Space.getSource( 4 ), PL_Font.getSource( statusStr, fc = resultColor ), PL_Space.getSource( 4 ) )
				resultStr = "%s%s%s%s"%( flagStr, data0, statusStr, data1 )
				newData = [resultStr]
			else:
				timeStr = labelGather.getText( "TongAbout:WarFixture", "battleTime" )%( self.week_maps[index], PL_Space.getSource( 2 ) )
				tongStr = "%s%sVS%s%s"%( data[0], PL_Space.getSource( 4 ), PL_Space.getSource( 4 ), data[1] )
				newData = [timeStr, tongStr]
			self.__pyListPanel.addItem( newData )

# ----------------------------------------------------------------
class TitleBg( PyGUI ):
	def __init__( self, titleBg, pyBinder = None ):
		PyGUI.__init__( self, titleBg )
		self.__pyTaxisBtns = {}
		self.pyBinder = pyBinder
		for name, item in titleBg.children:
			if name.startswith( "taxisBtn_" ):
				pyTaxisBtn = TaxisButton( item )
				index = int( name.split("_")[1])
				pyTaxisBtn.taxisIndex = index
				pyTaxisBtn.setStatesMapping( UIState.MODE_R4C1 )
				pyTaxisBtn.onLClick.bind( self.__onSortByTaxi )
				self.__pyTaxisBtns[index] = pyTaxisBtn

	def __onSortByTaxi( self, pyBtn ) :
		taxisIndex = pyBtn.taxisIndex
		taxisReverse = pyBtn.taxisReverse
		self.pyBinder.sort( key = lambda item : item[taxisIndex], reverse = taxisReverse )
	
	def setTaxisBtnTitle( self, titles ):
		for index, pyTaxisBtn in self.__pyTaxisBtns.items():
			if titles.has_key( index ):
				pyTaxisBtn.text = titles[index]

	def _getIsSort( self ):
		return self.__isSort

	def _setIsSort( self, isSort ):
		self.__isSort = isSort
		for pyTaxisBtn in self.__pyTaxisBtns.itervalues():
			pyTaxisBtn.isSort = isSort

	isSort = property( _getIsSort, _setIsSort )								# 是否排序

# ---------------------------------------------------------------------------
from WarRanking import bgTextures
from guis.controls.Control import Control

class BaseItem( Control ):
	def __init__( self, gui, pyBinder = None ):
		Control.__init__( self, gui, pyBinder )
		self.focus = True
		self.crossFocus = True
		self.__bguis = {}
		self.__pyCols = {}
		for name, item in gui.children:
			if name.startswith( "col_" ):
				index = int( name.split( "_" )[1] )
				pyCol = ColItem( item, self )
				self.__pyCols[index] = pyCol
			else:
				self.__bguis[name] = PyGUI( item )

	def onMouseEnter_( self ):
		Control.onMouseEnter_( self )
		for name, pyBgui in self.__bguis.iteritems():
			pyBgui.texture = "guis/general/tongabout/citywar/frame_bgs/%s.dds"%( bgTextures[name]%3 )

	def onMouseLeave_( self ):
		Control.onMouseLeave_( self )
		for name, pyBgui in self.__bguis.iteritems():
			pyBgui.texture = "guis/general/tongabout/citywar/frame_bgs/%s.dds"%( bgTextures[name]%1 )

	def updateInfo( self, datas ):
		for index, data in enumerate( datas ):
			pyCol = self.__pyCols.get( index, None )
			if pyCol is None:continue
			pyCol.text = str( data )

class RankItem( BaseItem ):
	__cg_item = None
	def __init__( self, pyBinder):
		if RankItem.__cg_item is None:
			RankItem.__cg_item = GUI.load( "guis/general/tongabout/citywar/sortitem.gui" )
		item = util.copyGuiTree( RankItem.__cg_item )
		uiFixer.firstLoadFix( item )
		BaseItem.__init__( self, item, pyBinder)

	def updateInfo( self, datas ):
		BaseItem.updateInfo( self, datas )

class LaptimesItem( BaseItem ):
	__cg_item = None
	def __init__( self, pyBinder):
		if LaptimesItem.__cg_item is None:
			LaptimesItem.__cg_item = GUI.load( "guis/general/tongabout/citywar/laptimesitem.gui" )
		item = util.copyGuiTree( LaptimesItem.__cg_item )
		uiFixer.firstLoadFix( item )
		BaseItem.__init__( self, item, pyBinder)

	def updateInfo( self, datas ):
		BaseItem.updateInfo( self, datas )

class FixtureItem( BaseItem ):
	__cg_item = None
	def __init__( self, pyBinder):
		if FixtureItem.__cg_item is None:
			FixtureItem.__cg_item = GUI.load( "guis/general/tongabout/citywar/fixtureitem.gui" )
		item = util.copyGuiTree( FixtureItem.__cg_item )
		uiFixer.firstLoadFix( item )
		BaseItem.__init__( self, item, pyBinder)

	def updateInfo( self, datas ):
		BaseItem.updateInfo( self, datas )
# -----------------------------------------------------------
from guis.tooluis.CSRichText import CSRichText
class ColItem( CSRichText ):
	def __init__( self, colItem, pyBinder = None ):
		CSRichText.__init__( self, colItem )
		self.__pyStaticText = StaticText( colItem.lbText )
		self.__pyStaticText = ""
		self.foreColor = 255, 250, 190, 255
		self.text = ""
		self.align = "C"

	def onMouseEnter_( self ) :
		if self.lineCount > 1: #有换行
			toolbox.fullText.show( self, self.text )
		return CSRichText.onMouseEnter_( self )

	def onMouseLeave_( self ) :
		oolbox.fullTextt.hide()
		return CSRichText.onMouseLeave_( self )