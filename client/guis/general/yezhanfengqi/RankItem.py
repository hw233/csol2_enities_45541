# -*- coding: gb18030 -*-
#
# $Id: ChartsItem.py, fangpengjun Exp $

"""
implement charts item class

"""
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.ODListPanel import ViewItem
from guis.controls.ListItem import ListItem
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from LabelGather import labelGather
import csconst
import Const

class RankItem( ListItem ):

	class __SubItem( CSRichText ):
		def __init__( self, item, pyBinder ):
			CSRichText.__init__( self, item, pyBinder )
			self.focus = False
			self.crossFocus = True
			self.realText = ""
			self.showTips = False
			self.autoNewline = False
			self.__pyStText = StaticText( item.lbText )
			self.__pyStText.text = ""
			self.align = "C"

		# ----------------------------------------------------------------
		# protected
		# ----------------------------------------------------------------
		def onMouseEnter_( self ):
			"""
			鼠标进入时被调用
			注意：这里不要回调 Lavel 的 onMouseEnter_
			"""
			self.pyBinder.onMouseEnter_()
			if self.showTips: #有多行，则浮动框显示
				toolbox.infoTip.showToolTips( self, self.realText )
			return True

		def onMouseLeave_( self ):
			"""
			鼠标离开时被调用
			注意：这里不要回调 Lavel 的 onMouseLeave_
			"""
			self.pyBinder.onMouseLeave_()
			toolbox.infoTip.hide()
			return True
	# ---------------------------------------------------------

	def __init__( self, item = None, pyBinder = None ):
		ListItem.__init__( self, item, pyBinder )
		self.pyCols_ = []
		self.index = -1
		self.__isPlayer = False		#是否为玩家自己
		self.selected = False
		self.commonBackColor = 255, 255, 255, 255
		self.highlightBackColor = 255, 255, 255, 255
		self.selectedBackColor = 255, 255, 255, 255
		self.__initialize( item )

	def subclass( self, item, pyBinder = None ):
		ListItem.subclass( self, item, pyBinder )
		self.__initialize( item )

	def __del__( self ) :
		ListItem.__del__( self )
		if Debug.output_del_ListItem :
			INFO_MSG( str( self ) )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, item ):
		if item is None : return
		self.__initCells( item )

	def __initCells( self, item ) :
		for name, ch in item.children :
			if "col_" not in name : continue
			pyCol = RankItem.__SubItem( ch, self )
			index = int( name.split( "_" )[1] )
			btnTitles = self.pyBinder.getBtnTitles()
			pyCol.maxWidth = btnTitles[index].width
			self.pyCols_.append( pyCol )
	
	def __getCenterPos( self, index ):
		btnTitles = self.pyBinder.getBtnTitles()
		centerPos = self.pyCols_[index].maxWidth/2.0
		startPos = 0.0
		for i in range( index ):
			startPos += self.pyCols_[i].maxWidth
		centerPos += startPos
		return centerPos
	
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onStateChanged_( self, state ):
		if self.isPlayer:return
		elements = self.getGui().elements
		for element in elements.values():
			element.visible = state in [ UIState.HIGHLIGHT, UIState.SELECTED ]

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setTextes( self, *textes ):
		"""
		设置每个col内容
		"""
		assert len( textes ) == len( self.pyCols_ )
		for index, pyCol in enumerate( self.pyCols_ ) :
			textStr = str( textes[index] )
			cellText = PL_Font.getSource( textStr, fc = ( 255, 250, 190, 255 ) )
			pyCol.realText = cellText
			pyCol.text = cellText
			pyCol.showTips = False
			pyCol.center = self.__getCenterPos( index )
			if pyCol.width > pyCol.maxWidth :
				pyCol.showTips = True
				textStr = textStr[:6]
				cellText = PL_Font.getSource( textStr, fc = ( 255, 250, 190, 255 ) )
				pyCol.text = cellText + "..."	

	def updateRank( self, rankData ):
		"""
		更新rankData信息
		"""
		player = BigWorld.player()
		self.isPlayer = player.id == rankData["roleID"]
		roleName = labelGather.getText( "YezhanFengQi:main", "masked" )
		if self.isPlayer:
			roleName = player.getName()
		expStr = ""
		rewardsStr = ""
		if self.pyBinder.isSvrTrigger:
			roleName = rankData["roleName"]
			expStr = rankData["exp"]
			rewardsStr = PL_Font.getSource( utils.currencyToViewText( int( rankData["rewards"] ), fc = ( 255, 250, 190, 255 ) ) )
		self.setTextes( roleName, 
					rankData["bekill"], 
					rankData["kill"], 
					rankData["chest"], 
					rankData["intergral"],
					expStr,
					rewardsStr )
	
	def setKillInfos( self, kill, beKill ):
		"""
		设置击杀信息
		"""
		self.pyCols_[1].text = str( beKill )
		self.pyCols_[2].text = str( kill )
	
	def setIntergal( self, intergal ):
		"""
		设置积分信息
		"""
		self.pyCols_[4].text = str( intergal )
	
	def setBoxNum( self, boxNum ):
		"""
		设置宝箱数
		"""
		self.pyCols_[3].text = str( boxNum )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getCols( self ):
		return self.pyCols_[:]

	# ---------------------------------------
	def _getIsPlayer( self ):
		return self.__isPlayer

	def _setIsPlayer( self, isPlayer ):
		self.__isPlayer = isPlayer
		if isPlayer:
			elements = self.getGui().elements
			for element in elements.values():
				element.visible = True

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyCols = property( _getCols )													# 获取所有子列
	isPlayer = property( _getIsPlayer, _setIsPlayer )					# 是否与玩家相关