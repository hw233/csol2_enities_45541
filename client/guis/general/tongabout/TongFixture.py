# -*- coding: gb18030 -*-
#
# $Id: TongFixture.py Exp $

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
import GUIFacade
import csdefine
import csconst

CITY_WAR_LEVEL_FINAL = 8

class TongFixture( Window ):
	"""
	帮会赛程窗口
	"""
	def __init__( self ):
		wnd = GUI.load( "guis/general/tongabout/tongfixture.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 	= True
		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( wnd )
	
	def __initialize( self, wnd ):
		self.__pyNameGrids = {}
		self.__pyBrokenGrids = {}
		for name, item in wnd.children:
			if name.startswith( "nameGrid_" ):
				index = int( name.split("_")[-1] )
				pyNameGrid = NameGrid( item )
				pyNameGrid.index = index
				pyNameGrid.setLineColor()
				pyNameGrid.setTongName("")
				self.__pyNameGrids[index] = pyNameGrid
			if name.startswith( "second_" ) or \
				name.startswith( "third_" ):
				prefix = name.split("_")[0]
				index = int( name.split("_")[-1] )
				pyBrokenGrid = NameGrid( item )
				pyBrokenGrid.lineColor = ( 87, 144, 155, 255 )
				if self.__pyBrokenGrids.has_key( prefix ):
					self.__pyBrokenGrids[prefix][index] = pyBrokenGrid
				else:
					self.__pyBrokenGrids[prefix] = {index:pyBrokenGrid}
	
		labelGather.setPyLabel( self.pyLbTitle_, "TongAbout:TongFixture", "lbTitle" )

	# -----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_OPEN_CITYWAR_INFO_WND"] = self.__onShowWnd
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
		self.show()

	def __onEntitiesTrapThrough( self, entitiesInTrap ):
		gossiptarget = GUIFacade.getGossipTarget()
		if gossiptarget and gossiptarget not in entitiesInTrap:
			self.hide()
	
	def __onRecWarTable( self, datas ):
		"""
		帮会赛程数据
		"""
		self.reset()
		quarterfinal = []
		semifinal = []
		final = None
		quartNumber = 0
		masterName = datas[0] #城主名称，可能为原城主、新决出的城主等
		for data in datas[1:]:
			matchLevel = data["matchLevel"]
			if matchLevel == csdefine.CITY_WAR_LEVEL_NONE: #无比赛
				pass
			elif matchLevel == csdefine.CITY_WAR_LEVEL_QUARTERFINAL: #四分之一决赛
				quarterfinal.append( data )
			elif matchLevel == csdefine.CITY_WAR_LEVEL_SEMIFINAL: #半决赛
				semifinal.append( data )
			else: #决赛
				final = data
		sortSemifinal = []			#半决赛
		sortQuarter = []			# 四分之一决赛
		quartNumber = len( quarterfinal )
		pySecondGrids = self.__pyBrokenGrids["second"]
		pyFinalGraid = self.__pyNameGrids[CITY_WAR_LEVEL_FINAL]
		pyFinalGraid.setTongName( masterName )
		if final: #有决赛
			nameVersus = final["versus"]
			winner = final["winner"]
			if masterName != "" and winner == masterName:
				pyFinalGraid.setGridColor((255, 138, 0, 255))
				pyFinalGraid.setLineColor((255, 138, 0, 255))
			if len( quarterfinal ) <= 0:
				if len( semifinal ) <= 0: #直接进入决赛
					tongName_0 = final["versus"][0]
					tongName_1 = final["versus"][1]
					semifinal = [{'versus': [tongName_0, tongName_1], 'matchLevel': 2, 'winner': winner}]
				else:
					sortSemifinal = semifinal
				for semi in semifinal:
					sortQuarter.append( {'versus':[semi["versus"][0],semi["versus"][1]], 'matchLevel': 1, 'winner':semi["winner"]} )
				if winner != "" and winner == masterName:
					pySecondGrids.get(0).lineColor = ( 255, 138, 0, 255 )
				pySecondGrids.get(1).lineColor = ( 87, 144, 155, 255 )
				
			if len( quarterfinal ) and len( semifinal ): #既有1/2，又有1/4决赛
				sortSemifinal = semifinal
				sortQuarter = quarterfinal
		else: #没决赛
			for pyBrokenGrid in pySecondGrids.values():
				pyBrokenGrid.lineColor = ( 87, 144, 155, 255 )
			pyFinalGraid.setGridColor()
			pyFinalGraid.setLineColor()
			if len( semifinal ): #有1/2决赛
				sortSemifinal = semifinal
				if len( quarterfinal ) > 0: #有1/4
					sortQuarter = quarterfinal
				else: #无1/4决赛
					for semi in sortSemifinal:
						sortQuarter.append( {'versus':[semi["versus"][0],semi["versus"][1]], 'matchLevel': 1, 'winner':semi["winner"]} )
						
			else: #无1/2决赛
				if len( quarterfinal ):
					sortQuarter = quarterfinal
		
		pyThirdGrids = self.__pyBrokenGrids["third"]
		for index, qdata in enumerate( sortQuarter ): #设置1/4决赛路径
			nameVersus = qdata["versus"]
			winner = qdata["winner"]
			for subIndex, name in enumerate( nameVersus ):
				pyNameGrid = self.__pyNameGrids.get( index*2+subIndex, None )
				if pyNameGrid is None:continue
				if pyNameGrid.index == CITY_WAR_LEVEL_FINAL:
					continue
				pyNameGrid.setTongName( name )
				if winner == name:
					pyNameGrid.setLineColor((255, 138, 0, 255))
					pyNameGrid.setGridColor((255, 138, 0, 255))
					pyThirdGrid = pyThirdGrids.get( index, None )
					if pyThirdGrid is None:continue
					pyThirdGrid.setBrokenTongName( name )
				else:
					pyNameGrid.setLineColor()
					pyNameGrid.setGridColor()
					
		for index, sdata in enumerate( sortSemifinal ):#设置1/2决赛路径
			nameVersus = sdata["versus"]
			winner = sdata["winner"]
			thIndex = self.__getTdIndexByName( winner )
			scIndex = self.__getScIndexByName( winner )
			pyTDGrid = pyThirdGrids.get( thIndex, None )
			pySCGrid = pySecondGrids.get( scIndex, None )
			if pyTDGrid is None:continue
			if pySCGrid is None:continue
			if final and final["winner"] == winner:
				pySCGrid.setLineColor(( 255, 138, 0, 255 ))
				pySCGrid.setGridColor((255, 138, 0, 255))
			pySCGrid.setBrokenTongName( winner )
			for subIndex, name in enumerate( nameVersus ):
				if winner == name:
					pyTDGrid.setLineColor(( 255, 138, 0, 255 ))
					pyTDGrid.setGridColor((255, 138, 0, 255))
	
	def __getTdIndexByName( self, name ):
		for index, pyNameGrid in self.__pyNameGrids.items():
			if index == CITY_WAR_LEVEL_FINAL:continue
			if pyNameGrid.tongName == name:
				return index/2
	
	def __getScIndexByName( self, name ):
		for index, pyNameGrid in self.__pyNameGrids.items():
			if index == CITY_WAR_LEVEL_FINAL:continue
			if pyNameGrid.tongName == name:
				return index/4

	# ---------------------------------------------------------
	# public
	# ---------------------------------------------------------
	def onEvent( self, evtMacro, *args ) :
		self.__triggers[evtMacro]( *args )
	
	def reset( self ):
		for pyNameGrid in self.__pyNameGrids.values():
			pyNameGrid.setTongName("")
			pyNameGrid.setLineColor()
			pyNameGrid.setGridColor()
		for brokenGrids in self.__pyBrokenGrids.values():
			for brokenGrid in brokenGrids.values():
				brokenGrid.setBrokenTongName("")
				brokenGrid.setLineColor()
				brokenGrid.setGridColor()

	def onLeaveWorld( self ):
		self.hide()
	
	def onEnterWorld( self ):
		self.reset()

	def show( self ):
		player = BigWorld.player()
		cityName = BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_KEY )
		player.cell.tong_onQueryCityWarTable( cityName )
		Window.show( self )

	def hide( self ):
		self.__trapID = 0
		self.reset()
		Window.hide( self )
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )

# ------------------------------------------------------------------
# 帮会名称格子
from guis.common.PyGUI import PyGUI
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
import csstring

class NameGrid( PyGUI ):
	def __init__( self, item ):
		PyGUI.__init__( self, item )
		self.index = -1
		self.__pyBrokenLine = BrokenLine( item.line )
		self.grid = item.grid
		self.tongName = ""
		self.__pyNameRich = CSRichText( self.grid.rtName )
		self.__pyNameRich.align = "C"
		self.__pyNameRich.spacing = -2.0
		self.__pyNameRich.text = ""
		self.__pyBline = None
		if hasattr( item, "bline" ):
			self.__pyBline = PyGUI( item.bline )
		
	
	def setTongName( self, tongName ):
		if tongName == "":
			tongName = labelGather.getText( "TongAbout:TongFixture", "noTongApp" )
			if self.index == CITY_WAR_LEVEL_FINAL:
				tongName = labelGather.getText( "TongAbout:TongFixture", "noTongOcc" )
		if self.index != CITY_WAR_LEVEL_FINAL:
			formatName = ""
			self.tongName = tongName
			tongName = csstring.toWideString( tongName )
			for ch in tongName:
				formatName += "%s%s"%( ch, PL_NewLine.getSource() )
			tongName = formatName
		self.__pyNameRich.text = tongName
	
	def setBrokenTongName( self, tongName ):
		if tongName != "":
			formatName = ""
			self.tongName = tongName
			tongName = csstring.toWideString( tongName )
			for ch in tongName:
				formatName += "%s%s"%( ch, PL_NewLine.getSource() )
			tongName = formatName
		self.__pyNameRich.text = tongName
	
	def setLineColor( self, color = ( 87, 144, 155, 255 ) ):
		self.__pyBrokenLine.lineColor = color
		if self.__pyBline:
			self.__pyBline.color = color
	
	def setGridColor( self, color = ( 54, 109, 120, 255 ) ):
		gridElements = self.grid.elements
		for textKey, textElem in gridElements.items():
			if textKey == "frm_bg":continue
			textElem.colour = color

# -------------------------------------------------------------------
# 晋级折线，红色表示晋级
class BrokenLine( PyGUI ):
	def __init__( self, line ):
		PyGUI.__init__( self, line )
		self.__color = 87, 144, 155, 255 
	
	def setLinesColor( self, lines, color ):
		for linestr in lines:
			line = self.getGui().elements.get( linestr, None )
			if line is None:continue
			line.colour = color
		
	
	def _getLineColor( self ):
		return self.__color
	
	def _setLineColor( self, color ):
		self.__color = color
		elements = self.getGui().elements
		for textKey, textElem in elements.items():
			textElem.colour = color

	lineColor = property( _getLineColor, _setLineColor )