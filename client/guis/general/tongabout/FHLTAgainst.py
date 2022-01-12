# -*- coding: gb18030 -*-
#
# $Id: TongFixture.py Exp $

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.common.PyGUI import PyGUI
from guis.common.PyGUI import PyGUI
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
import csstring
import GUIFacade
import csdefine
import csconst

MATCH_LEVEL_SIXTEEN = 1
MATCH_LEVEL_EIGHTH = 2
MATCH_LEVEL_QUATER = 3
MATCH_LEVEL_HALF = 4

OFFSET_MAP = { MATCH_LEVEL_EIGHTH:0, 					#折线偏移值
		MATCH_LEVEL_QUATER:4, 
		MATCH_LEVEL_HALF:6,
		}

class FHLTAgainst( Window ):
	"""
	夺城战复赛对战表
	"""
	
	def __init__( self ):
		wnd = GUI.load( "guis/general/tongabout/tongfhlt/fhltgst.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 	= True
		self.__triggers = {}
		self.__matchDatas = {}				#比赛信息
		self.__registerTriggers()
		self.__initialize( wnd )
	
	def __initialize( self, wnd ):
		self.__pyGrids = {}
		self.__pyLines = {}
		for name, item in wnd.children:
			if name.startswith( "grid_" ):					#帮会对战格子
				index = int( name.split("_")[-1] )
				prefix = name.split("_")[1]
				pyGrid = Grid( item, prefix, index )
				if self.__pyGrids.has_key( prefix ):
					self.__pyGrids[prefix][index] = pyGrid
				else:
					self.__pyGrids[prefix] = {index:pyGrid}
			elif name.startswith( "line_" ):				#对战连线
				index = int( name.split("_")[-1] )
				prefix = name.split("_")[1]
				pyLine = Line( item, prefix, index )
				if self.__pyLines.has_key( prefix ):
					self.__pyLines[prefix][index] = pyLine
				else:
					self.__pyLines[prefix] = {index:pyLine}
		
		self.__pyAgst = AgstLine( wnd.agst )
		self.__pyAgst.reSetFlag()
		
		labelGather.setPyLabel( self.pyLbTitle_, "TongAbout:FHLTAgainst", "lbTitle" )
	# -----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_SHOW_FHLTAGST_WND"] = self.__onShowWnd
		self.__triggers["EVT_ON_RECIEVE_FHLTAGST_DATAS"] = self.__onRecAgstDatas
		for trigger in self.__triggers :
			ECenter.registerEvent( trigger, self )

	def __desregisterTriggers( self ) :
		for trigger in self.__triggers :
			ECenter.unregisterEvent( trigger, self )

	# ------------------------------------------------------------
	def __onShowWnd( self ):
		"""
		显示界面
		"""
		self.show()
	
	def __onRecAgstDatas( self, datas ):
		"""
		接收对战数据
		"""
		self.__resetColors()
		for data in datas:
			matchLevel = data["matchLevel"]		#轮数
			if matchLevel in self.__matchDatas:
				self.__matchDatas[matchLevel].append( data )
			else:
				self.__matchDatas[matchLevel] = [data]
		levels = self.__matchDatas.keys()
		levels.sort( reverse = True )
		lackDatas = {}								#没有对阵信息的轮次
		for level in levels:
			pLevel = level - 1
			if self.__matchDatas.has_key( pLevel ):
				preMtchDatas = self.__getPreMtchDats( level, pLevel )						#获取上一轮，并此轮排序
				self.__matchDatas[pLevel] = preMtchDatas
			else:
				lackDatas[pLevel] = self.__getLackMathDatas( level )
		for mtchLevel, mtchDataList in self.__matchDatas.items():
			dataLen = len( mtchDataList )
			if mtchLevel == MATCH_LEVEL_SIXTEEN:					#设置帮会格名称
				for index, mtchData in enumerate( mtchDataList ):
					left = mtchData["versus"][0]
					right = mtchData["versus"][1]
					winner = mtchData["winner"]
					prefix = "left"
					if index >= dataLen/2:
						prefix = "right"
						index = index - dataLen/2
					isLeftWin = left == winner and winner != ""
					isRightWin = right == winner and winner != ""
					self.__pyGrids[prefix][index*2].setTongName( left, isLeftWin )
					self.__pyGrids[prefix][index*2+1].setTongName( right, isRightWin )
			else:														#设置对阵折线
				offset = OFFSET_MAP.get( mtchLevel, 0 )
				isleft = isright = False
				for index, mtchData in enumerate( mtchDataList ):
					left = mtchData["versus"][0]
					right = mtchData["versus"][1]
					winner = mtchData["winner"]
					level = mtchData["matchLevel"]
					prefix = "left"
					tmpIdx = index
					if index >= dataLen/2:
						prefix = "right"
						index = index - dataLen/2
					index += offset
					isLeftWin = left == winner and winner != ""
					isRightWin = right == winner and winner != ""
					self.__pyLines[prefix][index].setWinColor( isLeftWin, isRightWin )
					if level == MATCH_LEVEL_HALF:
						if tmpIdx == 0:
							isleft = winner != ""
						else:
							isright = winner != ""
				self.__pyAgst.setWinColor( isleft, isright )			#半决赛，设置旗帜
		
	def __getPreMtchDats( self, level, pLevel ):
		"""
		将上一轮数据排序
		"""
		matchDatas = self.__matchDatas.get( level, None )
		preMtchDatas = self.__matchDatas.get( pLevel, None )
		bTrees = []
		sortDatas = []
		if matchDatas and preMtchDatas:
			for matchData in matchDatas:
				left = matchData["versus"][0]
				right = matchData["versus"][1]
				bTree = [ None, None ]
				for pMtchData in preMtchDatas:
					pWiner = pMtchData["winner"]
					if pWiner == left:
						bTree[0] = pMtchData
					elif pWiner == right:
						bTree[1] = pMtchData
				bTrees.append( bTree )
			for btree in bTrees:
				if None in btree:
					btree.remove( None )
				sortDatas.extend( btree )
		return sortDatas

	def __getLackMathDatas( self, level ):
		"""
		获取缺少对阵信息的轮次数据
		"""
		lackDatas = []
		matchDatas = self.__matchDatas.get( level, None )
		if matchDatas:
			for matchData in matchDatas:
				left = matchData["versus"][0]
				right = matchData["versus"][1]
				winner = matchData["winner"]
				lackDatas.append( {'versus':[left,right], 'matchLevel': level - 1, 'winner':winner} )
		return lackDatas
	
	def __resetColors( self ):
		"""
		重置颜色
		"""
		for prefix, pyGrids in self.__pyGrids.items():
			for index, pyGrid in pyGrids.items():
				pyGrid.reSetTongName()
		for prefix, pyLines in self.__pyLines.items():
			for index, pyLine in pyLines.items():
				pyLine.lineColor = ( 87, 144, 155, 255 )
		self.__pyAgst.reSetFlag()

	# ---------------------------------------------------------
	# public
	# ---------------------------------------------------------
	def onEvent( self, evtMacro, *args ) :
		self.__triggers[evtMacro]( *args )

	def onLeaveWorld( self ):
		self.__resetColors()
		self.hide()
	
	def onEnterWorld( self ):
		pass

	def show( self ):
		self.__resetColors()
		player = BigWorld.player()
		cityName = BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_KEY )
		player.cell.tong_onQueryFHLTTable( cityName )
		Window.show( self )

	def hide( self ):
		Window.hide( self )

# -------------------------------------------------------------------------------------------
class Grid( PyGUI ):
	"""
	帮会名称格
	"""
	def __init__( self, item, prefix, index ):
		PyGUI.__init__( self, item )
		self.prefix = prefix
		self.index = index
		self.__pyLine = Line( item.line, prefix, index )
		self.grid = item.grid
		self.tongName = ""
		self.__pyNameRich = CSRichText( item.grid.rtName )
		self.__pyNameRich.align = "C"
		self.__pyNameRich.spacing = -2.0
		self.__pyNameRich.text = ""
		self.__pyBline = None
		if hasattr( item, "bline" ):
			self.__pyBline = PyGUI( item.bline )
		
	def setTongName( self, tongName, isWin ):
		if tongName != "":
			self.tongName = tongName
			tongName = csstring.toWideString( tongName )
		else:
			tongName = labelGather.getText( "TongAbout:FHLTAgainst", "default" )
		self.__pyNameRich.text = tongName
		self.setGridColor()
		self.setLineColor()
		if isWin:
			color = ( 255, 0, 0, 255 )
			self.setGridColor( color )
			self.setLineColor( color )
	
	def reSetTongName( self ):
		self.__pyNameRich.text = labelGather.getText( "TongAbout:TongFixture", "noTongApp" )
		self.setGridColor()
		self.setLineColor()

	def setLineColor( self, color = ( 87, 144, 155, 255 ) ):
		self.__pyLine.lineColor = color
		if self.__pyBline:
			self.__pyBline.color = color
	
	def setGridColor( self, color = ( 54, 109, 120, 255 ) ):
		gridElements = self.grid.elements
		for textKey, textElem in gridElements.items():
			if textKey == "frm_bg":continue
			textElem.colour = color

# ---------------------------------------------------------------------------------------
class Line( PyGUI ):
	"""
	对战线
	"""
	_colors_map = { "left":{ "top":["t","rt","r_0"], "bottom":["b","rb","r_1"]},
					"right":{ "top":["t","lt","l_0"], "bottom":["b","lb","l_1"]}
				}
	def __init__( self, line, prefix, index ):
		PyGUI.__init__( self, line )
		self.__color = 87, 144, 155, 255
		self.prefix = prefix
		self.index = index
		self.elements = line.elements

	def setPartColor( self, tb, color ):
		"""
		设置一部分折线的颜色
		tb: top bottom
		"""
		tbs = self._colors_map[self.prefix].get( tb, [ ] )
		for str in tbs:
			line = self.elements.get( "frm_%s"%str, None )
			if line is None:continue
			line.colour = color
	
	def setWinColor( self, isLeft, isRight ):
		"""
		设置2个帮会输赢颜色
		"""
		self.lineColor = ( 87, 144, 155, 255 )
		if isLeft:
			self.setPartColor( "top", ( 255, 0, 0, 255 ) )
		if isRight:
			self.setPartColor( "bottom", ( 255, 0, 0, 255 ) )
	
	def _getLineColor( self ):
		return self.__color
	
	def _setLineColor( self, color ):
		"""
		设置全部颜色
		"""
		self.__color = color
		for textKey, textElem in self.elements.items():
			textElem.colour = color

	lineColor = property( _getLineColor, _setLineColor )

class AgstLine( PyGUI ):
	"""
	对抗旗帜
	"""
	def __init__( self, agst ):
		PyGUI.__init__( self, agst )
		self.elements = agst.elements
		self.__pyFlag = PyGUI( agst.flag )
		
	def setWinColor( self, isLeft, isRight ):
		"""
		设置2个帮会输赢颜色
		"""
		self.__pyFlag.visible = isLeft or isRight
		if isLeft:
			self.elements["left"].colour = ( 255, 0, 0, 255 )
		if isRight:
			self.elements["right"].colour = ( 255, 0, 0, 255 )

	def reSetFlag( self ):
		self.lineColor = ( 87, 144, 155, 255 )
		self.__pyFlag.visible = False

	def _getLineColor( self ):
		return self.__color
	
	def _setLineColor( self, color ):
		"""
		设置全部颜色
		"""
		self.__color = color
		for textKey, textElem in self.elements.items():
			textElem.colour = color

	lineColor = property( _getLineColor, _setLineColor )