# -*- coding: gb18030 -*-

# TaxisButton inherit from HButtonEx with its special display mode.
# written by ganjinxing 2009-10-19

from guis import *
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.common.Frame import HVFrame
from guis.common.PyGUI import PyGUI


class TaxisButton( Button ) :

	__pyHighlight_bg = None													# 高亮状态的背景
	__pyPressed_bg = None 													# 按下状态的背景

	def __init__( self, button = None, pyBinder = None ) :
		Button.__init__( self, button, pyBinder )
		self.isOffsetText = True

		if TaxisButton.__pyHighlight_bg is None :
			gui = GUI.load( "guis/general/commissionsale/shopsviewer/taxisbtnbg_highlight.gui" )
			uiFixer.firstLoadFix( gui )
			TaxisButton.__pyHighlight_bg = HVFrame( gui )
			gui = GUI.load( "guis/general/commissionsale/shopsviewer/taxisbtnbg_pressed.gui" )
			uiFixer.firstLoadFix( gui )
			TaxisButton.__pyPressed_bg = HVFrame( gui )

		self.__pyTaxisFlag = PyGUI( button.taxisFlag )
		self.__taxisFlagPos = self.__pyTaxisFlag.pos
		self.__taxisReverse = False											# 是否反序排列
		self.__setTaxisMapping()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __setTaxisMapping( self ) :
		if self.__taxisReverse :											# 如果当前按升序排列
			util.setGuiState( self.__pyTaxisFlag.getGui(), ( 2,1 ), ( 2,1 ) )
		else :
			util.setGuiState( self.__pyTaxisFlag.getGui(), ( 2,1 ), ( 1,1 ) )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def setStateView_( self, state ) :
		Button.setStateView_( self, state )
		self.__pyTaxisFlag.pos = self.__taxisFlagPos
		if state == UIState.HIGHLIGHT :
			self.addPyChild( TaxisButton.__pyHighlight_bg, "statusBg" )
			TaxisButton.__pyHighlight_bg.width = self.width + 1
			TaxisButton.__pyHighlight_bg.height = TaxisButton.__pyHighlight_bg.height
			TaxisButton.__pyHighlight_bg.pos = 0, 2.4
		elif state == UIState.PRESSED :
			self.addPyChild( TaxisButton.__pyPressed_bg, "statusBg" )
			TaxisButton.__pyPressed_bg.width = self.width + 1
			TaxisButton.__pyPressed_bg.height = TaxisButton.__pyPressed_bg.height
			TaxisButton.__pyPressed_bg.pos = 0, 2
			self.__pyTaxisFlag.left = self.__taxisFlagPos[0] + 1
			self.__pyTaxisFlag.top = self.__taxisFlagPos[1] + 1
		else :
			self.getGui().delChild( "statusBg" )

	def onLClick_( self, mode ) :
		if self.isMouseHit() :
			self.taxisReverse = not self.__taxisReverse
		return Button.onLClick_( self, mode )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getTaxisReverse( self ) :
		return self.__taxisReverse

	def _setTaxisReverse( self, reverse ) :
		self.__taxisReverse = reverse
		self.__setTaxisMapping()

	taxisReverse = property( _getTaxisReverse, _setTaxisReverse )			# 当前是否在反序排列


class TaxisButtonEx( HButtonEx ) :

	def __init__( self, button = None, pyBinder = None ) :
		HButtonEx.__init__( self, button, pyBinder )
		self.isOffsetText = True
		self.__taxisReverse = False											# 是否反序排列


	def onLClick_( self, mode ) :
		if self.isMouseHit() :
			self.taxisReverse = not self.__taxisReverse
		return HButtonEx.onLClick_( self, mode )


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getTaxisReverse( self ) :
		return self.__taxisReverse

	def _setTaxisReverse( self, reverse ) :
		self.__taxisReverse = reverse

	taxisReverse = property( _getTaxisReverse, _setTaxisReverse )			# 当前是否在反序排列

