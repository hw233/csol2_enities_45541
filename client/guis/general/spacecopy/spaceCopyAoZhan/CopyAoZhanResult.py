# -*- coding: gb18030 -*-

import BigWorld
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ODListPanel import ODListPanel
from guis.common.GUIBaseObject import GUIBaseObject
from guis.controls.ListItem import MultiColListItem

class CopyAoZhanResult( Window ):
	def __init__( self ):
		wnd = GUI.load( "guis/general/spacecopyabout/spaceCopyAoZhan/copyAoZhanResult.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ = True
		self.h_dockStyle = "RIGHT"
		self.v_dockStyle = "TOP"

		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( wnd )

	def __initialize( self, wnd ):
		self.__pyBtnRound = HButtonEx( wnd.tc.btn_0 )	# 轮次
		self.__pyBtnRound.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyBtnRound, "SpaceCopyAoZhan:AoZhanResult", "btnRound" )

		self.__pyBtnGroup = HButtonEx( wnd.tc.btn_1 )	# 组别
		self.__pyBtnGroup.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyBtnGroup, "SpaceCopyAoZhan:AoZhanResult", "btnGroup" )

		self.__pyBtnVicOrDef = HButtonEx( wnd.tc.btn_2 )	# 胜负
		self.__pyBtnVicOrDef.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyBtnVicOrDef, "SpaceCopyAoZhan:AoZhanResult", "btnVicOrDef" )

		self.__pyBtnIntegral = HButtonEx( wnd.tc.btn_3 )	# 积分
		self.__pyBtnIntegral.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyBtnIntegral, "SpaceCopyAoZhan:AoZhanResult", "btnIntegral" )

		self.__pyResultList = ODListPanel( wnd.tc.clipPanel, wnd.tc.sbar )
		self.__pyResultList.onViewItemInitialized.bind( self.__initListItem )
		self.__pyResultList.onDrawItem.bind( self.__drawListItem )
		self.__pyResultList.ownerDraw = True
		self.__pyResultList.itemHeight = 23.0
		self.__pyResultList.autoSelect = False

		labelGather.setLabel( wnd.lbTitle, "SpaceCopyAoZhan:AoZhanResult", "lbTitle" )

	# ----------------------------------------------------------
	# pravite
	# ----------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_SHOW_AOZHAN_RESULT"] = self.__onShow
		self.__triggers["EVT_ON_HIDE_AOZHAN_RESULT"] = self.__onHide
		for key in self.__triggers.iterkeys():
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ):
		for key in self.__triggers.iterkeys():
			ECenter.unregisterEvent( key, self )

	def __initListItem( self, pyViewItem ):
		pyItem = ResultItem()
		pyViewItem.addPyChild( pyItem )
		pyItem.left = 0
		pyItem.top = 0
		pyViewItem.crossFocus = False
		pyViewItem.pyItem = pyItem

	def __drawListItem( self, pyViewItem ):
		pyItem = pyViewItem.pyItem
		pyItem.setText( pyViewItem.listItem )
		if pyViewItem.selected:
			pyItem.setColor( ( 60, 255, 0, 255 ) )
		else:
			pyItem.setColor( ( 255, 255, 208, 255 ) )

	def __onShow( self, info ):
		self.show( info )

	def __onHide( self ):
		self.hide()

	# ---------------------------------------------------------
	# public
	# ---------------------------------------------------------
	def onEvent( self, eventMacro, *args ):
		self.__triggers[eventMacro]( *args )

	def show( self, info ):
		for i in info[:]:
			if i == {}:
				info.remove(i)
		self.__pyResultList.clearItems()
		self.__pyResultList.addItems( info )
		self.__pyResultList.sort( key = lambda item: item["round"], reverse = False )
		Window.show( self )

	def hide( self ):
		GroupPanel.instance().hide()
		Window.hide( self )

# ----------------------------------------------------------------
class ResultItem( GUIBaseObject ):
	def __init__( self, pyBinder = None ):
		item = GUI.load( "guis/general/spacecopyabout/spaceCopyAoZhan/resultItem.gui" )
		uiFixer.firstLoadFix( item )
		GUIBaseObject.__init__( self, item )
		self.__groupInfo = []
		self.__initialize( item, pyBinder )

	def __initialize( self, item, pyBinder ) :
		self.__pyRtRound = CSRichText( item.rtRound )
		self.__pyRtRound.text = ""
		self.__pyRtRound.align = "C"

		self.__pyRtGruop = CSRichText( item.rtGroup )
		self.__pyRtGruop.crossFocus = True
		self.__pyRtGruop.text = ""
		self.__pyRtGruop.align = "C"
		self.__pyRtGruop.onMouseEnter.bind( self.__onMouseEnter )
		self.__pyRtGruop.onMouseLeave.bind( self.__onMouseLeave )

		self.__pyRtVicOrDef = CSRichText( item.rtVicOrDef )
		self.__pyRtVicOrDef.text = ""
		self.__pyRtVicOrDef.align = "C"

		self.__pyRtIntegral = CSRichText( item.rtIntegral )
		self.__pyRtIntegral.text = ""
		self.__pyRtIntegral.align = "C"

	def __onMouseEnter( self, pyRt ):
		if pyRt is None: return
		if self.__pyRtGruop.text == "--": return
		GroupPanel.instance().show( self.__groupInfo )

	def __onMouseLeave( self ):
		pass

	def setText( self, info ):
		"""
		更新列表项文本
		"""
		self.__pyRtRound.text		= str( info["round"] )
		self.__pyRtGruop.text		= str( info["group"] )
		self.__pyRtVicOrDef.text	= str( info["vicOrDef"] )
		self.__pyRtIntegral.text 	= str( info["score"] )
		self.__groupInfo = info["groupInfo"]

	def setColor( self, color ):
		"""
		更新列表项字体颜色
		"""
		self.__pyRtRound.foreColor = color
		self.__pyRtGruop.foreColor = color
		self.__pyRtVicOrDef.foreColor = color
		self.__pyRtIntegral.foreColor = color

class GroupPanel( Window ):
	__instance = None
	def __init__( self ):
		assert GroupPanel.__instance is None, "GroupPanel instance has been created."
		GroupPanel.__instance = self
		wnd = GUI.load( "guis/general/spacecopyabout/spaceCopyAoZhan/groupPanel.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ = True
		self.h_dockStyle = "CENTER"
		self.v_dockStyle = "TOP"
		self.addToMgr()

		self.__initialize( wnd )

	def __initialize( self, wnd ):
		self.__pyBtnVictor = HButtonEx( wnd.tc.btn_0 )	# 胜者
		self.__pyBtnVictor.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyBtnVictor, "SpaceCopyAoZhan:AoZhanResult", "btnVictor" )

		self.__pyBtnVS = HButtonEx( wnd.tc.btn_1 )
		self.__pyBtnVS.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyBtnVS, "SpaceCopyAoZhan:AoZhanResult", "btnVS" )

		self.__pyBtnLoser = HButtonEx( wnd.tc.btn_2 )	# 负者
		self.__pyBtnLoser.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyBtnLoser, "SpaceCopyAoZhan:AoZhanResult", "btnLoser" )

		self.__pyGroupList = ODListPanel( wnd.tc.clipPanel, wnd.tc.sbar )
		self.__pyGroupList.onViewItemInitialized.bind( self.__initListItem )
		self.__pyGroupList.onDrawItem.bind( self.__drawListItem )
		self.__pyGroupList.ownerDraw = True
		self.__pyGroupList.itemHeight = 23.0
		self.__pyGroupList.autoSelect = False

		labelGather.setLabel( wnd.lbTitle, "SpaceCopyAoZhan:AoZhanResult", "lbGroupTitle" )

	def __initListItem( self, pyViewItem ):
		pyItem = GroupItem()
		pyViewItem.addPyChild( pyItem )
		pyItem.left = 0
		pyItem.top = 0
		pyViewItem.crossFocus = False
		pyViewItem.pyItem = pyItem

	def __drawListItem( self, pyViewItem ):
		pyItem = pyViewItem.pyItem
		pyItem.setInfo( pyViewItem )

	@staticmethod
	def instance():
		if GroupPanel.__instance is None:
			GroupPanel.__instance = GroupPanel()
		return GroupPanel.__instance

	# ---------------------------------------------------------
	# public
	# ---------------------------------------------------------
	def show( self, groupInfo ):
		if not groupInfo: return
		self.__pyGroupList.clearItems()
		if type( groupInfo[0] ) == type( [] ):
			for index, info in enumerate( groupInfo[0] ):
				if index == 0:
					self.__pyGroupList.addItem( [info, groupInfo[1]] )
				else:
					self.__pyGroupList.addItem( [info, ""] )
		elif type( groupInfo[1] ) == type( [] ):
			for index, info in enumerate( groupInfo[1] ):
				if index == 0:
					self.__pyGroupList.addItem( [groupInfo[0], info] )
				else:
					self.__pyGroupList.addItem( ["", info] )
		else:
			self.__pyGroupList.addItem( groupInfo )
		Window.show( self )

# ---------------------------------------------------------
class GroupItem( MultiColListItem ):
	def __init__( self ):
		item = GUI.load( "guis/general/spacecopyabout/spaceCopyAoZhan/groupItem.gui" )
		uiFixer.firstLoadFix( item )
		MultiColListItem.__init__( self, item )
		self.commonBackColor = ( 255, 255, 255, 255 )
		self.selectedBackColor = ( 255, 255, 255, 255 )
		self.highlightBackColor = ( 255, 255, 255, 255 )
		self.focus = False

	def setInfo( self, pyViewItem ):
		groupInfo = pyViewItem.listItem
		victor = groupInfo[0]
		loser = groupInfo[1]
		self.setTextes( victor, loser )