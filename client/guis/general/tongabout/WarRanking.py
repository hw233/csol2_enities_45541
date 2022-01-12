# -*- coding: gb18030 -*-
#
# $Id: WarRanking.py Exp $

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.common.PyGUI import PyGUI
from guis.controls.Button import Button
from guis.controls.ListPanel import ListPanel
from guis.controls.ODComboBox import ODComboBox
from guis.controls.StaticLabel import StaticLabel
from guis.controls.RichText import RichText
import csconst
import GUIFacade

class WarRanking( Window ):
	"""
	逐鹿榜
	"""
	def __init__( self ):
		wnd = GUI.load( "guis/general/tongabout/citywar/wnd.gui")
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 	= True
		self.gbIndex = 0
		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( wnd )

	def __initialize( self, wnd ):
		self.__pyRtOwner = RichText( wnd.rtOwner )
		self.__pyRtOwner.text = ""
		self.__pyListPanel = ListPanel( wnd.listPanel.clipPanel, wnd.listPanel.sbar )
		self.__pyListPanel.autoSelect = True
		self.__pyListPanel.colSpace = 5.0
		self.__pyListPanel.onItemSelectChanged.bind( self.__onItemSelected )

		self.__pyCitiesCB = ODComboBox( wnd.citiesCB )
		self.__pyCitiesCB.autoSelect = False
		self.__pyCitiesCB.ownerDraw = True
		self.__pyCitiesCB.pyBox_.foreColor = 236, 218, 157
		self.__pyCitiesCB.onViewItemInitialized.bind( self.onInitialized_ )
		self.__pyCitiesCB.onDrawItem.bind( self.onDrawItem_ )
		self.__pyCitiesCB.onItemLClick.bind( self.__onCitySelected )
		for spaceName, name in csconst.TONG_CITYWAR_CITY_MAPS.iteritems():
			city = City( name, spaceName )
			self.__pyCitiesCB.addItem( city )

		self.__pyShutBtn = Button( wnd.shutBtn )
		self.__pyShutBtn.setStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.__pyShutBtn, "TongAbout:warRanking", "shutBtn" )
		self.__pyShutBtn.onLClick.bind( self.__onShut )

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setLabel( wnd.btnChief.lbText, "TongAbout:warRanking", "chiefNameText" )
		labelGather.setLabel( wnd.btnTong.lbText, "TongAbout:warRanking", "tongNameText" )
		labelGather.setLabel( wnd.btnSess.lbText, "TongAbout:warRanking", "indexText" )
		labelGather.setLabel( wnd.stCityName, "TongAbout:warRanking",  "stCityName" )
		labelGather.setLabel( wnd.lbTitle, "TongAbout:warRanking", "lbTitle" )


	def __registerTriggers( self ):
		self.__triggers["EVT_ON_RECIEVE_CITY_TONGMASTER"] = self.__onRecieveTongMaster
		self.__triggers["EVT_ON_RECEIVE_MASTERCITY"] = self.__onRecieveMasterCityName
		self.__triggers["EVT_ON_RECEIVE_CURMASTER"] = self.__onRecieveCurMaster
		for macroName in self.__triggers.iterkeys():
			ECenter.registerEvent( macroName, self )

	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for macroName in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( macroName, self )

	# ----------------------------------------------------
	def onInitialized_( self, pyViewItem ):
		pyLabel = StaticLabel()
		pyLabel.crossFocus = True
		pyLabel.foreColor = 236, 218, 157
		pyLabel.h_anchor = "CENTER"
		pyViewItem.addPyChild( pyLabel )
		pyViewItem.pyLabel = pyLabel
	
	def onDrawItem_( self, pyViewItem ):
		pyPanel = pyViewItem.pyPanel
		if pyViewItem.selected :
			pyViewItem.pyLabel.foreColor = pyPanel.itemSelectedForeColor			# 选中状态下的前景色
			pyViewItem.color = pyPanel.itemSelectedBackColor				# 选中状态下的背景色
		elif pyViewItem.highlight :
			pyViewItem.pyLabel.foreColor = pyPanel.itemHighlightForeColor		# 高亮状态下的前景色
			pyViewItem.color = pyPanel.itemHighlightBackColor				# 高亮状态下的背景色
		else :
			pyViewItem.pyLabel.foreColor = pyPanel.itemCommonForeColor
			pyViewItem.color = pyPanel.itemCommonBackColor
		pyLabel = pyViewItem.pyLabel
		pyLabel.width = pyViewItem.width
		pyLabel.foreColor = 236, 218, 157
		pyLabel.left = 1.0
		pyLabel.top = 1.0
		pyLabel.text = pyViewItem.listItem.name
		
	def __onRecieveTongMaster( self, index, tongName, date, chiefName ):
		"""
		接收排行榜数据
		"""
		if index in self.__getRankIndexs():return
		item = GUI.load( "guis/general/tongabout/citywar/rankitem.gui" )
		uiFixer.firstLoadFix( item )
		pyRankItem = RankItem( item )
		pyRankItem.update( index, tongName, date, chiefName )
		self.__pyListPanel.addItem( pyRankItem )
		self.__pyListPanel.sort( key = lambda pyRankItem: pyRankItem.index, reverse = True ) #倒序
		pyItems = self.__pyListPanel.pyItems
		for itemIndex, pyListItem in enumerate( pyItems ):
			if itemIndex == 0:
				pyListItem.setBgStatus( True )
			else:
				pyListItem.setBgStatus( False )
		ownerName = labelGather.getText( "TongAbout:warRanking","noOwner" )
		if len( pyItems ) > 0:
			ownerName = pyItems[0].pyCols_[1].text
		self.__pyRtOwner.text = labelGather.getText( "TongAbout:warRanking","cityOwner" )%ownerName
		if self.visible:return
		self.show()
	
	def __onRecieveMasterCityName( self, cityName ):
		if self.__pyCitiesCB.selItem.spaceName == cityName :return
		for city in self.__pyCitiesCB.items:
			if city.spaceName == cityName:
				self.__pyCitiesCB.selItem = city
				self.__pyCitiesCB.pyBox_.text = city.name
				
	def __onRecieveCurMaster( self, tongName ):
		if tongName:
			self.__pyRtOwner.text = labelGather.getText( "TongAbout:warRanking","cityOwner" )%tongName
		else:
			ownerName = labelGather.getText( "TongAbout:warRanking","noOwner" )
			self.__pyRtOwner.text = labelGather.getText( "TongAbout:warRanking","cityOwner" )%ownerName

	def __getRankIndexs( self ):
		pyRankItems = self.__pyListPanel.pyItems
		return [pyRankItem.index for pyRankItem in pyRankItems]

	def __onItemSelected( self, pyItem ):
		pass

	def __onCitySelected( self, selIndex ):
		if selIndex < 0:return
		self.__pyCitiesCB.pyBox_.text = self.__pyCitiesCB.selItem.name
		self.__pyListPanel.clearItems()
		selItem = self.__pyCitiesCB.selItem
		spaceName = selItem.spaceName
		BigWorld.player().tong_requestQueryCityTongMasters( spaceName )
		ownerName = labelGather.getText( "TongAbout:warRanking","noOwner" )
		self.__pyRtOwner.text = labelGather.getText( "TongAbout:warRanking","cityOwner" )%ownerName

	def __onShut( self ):
		self.hide()

	# ---------------------------------------------------------
	# public
	# ---------------------------------------------------------
	def onEvent( self, evtMacro, *args ) :
		self.__triggers[evtMacro]( *args )

	def show( self ):
		spaceID = BigWorld.player().spaceID
		spaceName = BigWorld.getSpaceDataFirstForKey( spaceID, csconst.SPACE_SPACEDATA_KEY )
		for city in self.__pyCitiesCB.items:
			if city.spaceName == spaceName:
				self.__pyCitiesCB.selItem = city
				self.__pyCitiesCB.pyBox_.text = city.name
		Window.show( self )

	def hide( self ):
		self.__pyListPanel.clearItems()
		Window.hide( self )
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )

	def onLeaveWorld( self ):
		self.hide()


# -------------------------------------------------------------------
from guis.common.PyGUI import PyGUI
from guis.common.Frame import HVFrame
from guis.controls.ListItem import MultiColListItem

class RankItem( MultiColListItem ):

	def __init__( self, rankItem ):
		MultiColListItem.__init__( self, rankItem )
		self.foreColor = ( 237, 230, 155, 255 )
		self.commonForeColor = self.foreColor
		self.highlightForeColor = self.foreColor
		self.selectedForeColor = self.foreColor
		self.commonBackColor = ( 255, 255, 255, 255 )
		self.selectedBackColor = ( 255, 255, 255, 255 )
		self.highlightBackColor = ( 255, 255, 255, 255 )
		self.index = -1

	def update( self, index, tongName, date, chiefName ):
		self.index = index
		self.setTextes( labelGather.getText( "TongAbout:warRanking", "miIndex" )%( index + 1), tongName, chiefName )

	def setBgStatus( self, status ):
		elements = self.getGui().elements
		for elem in elements.values():
			elem.visible = status

class City:
	def __init__( self, name, spaceName ):
		self.name = name
		self.spaceName = spaceName