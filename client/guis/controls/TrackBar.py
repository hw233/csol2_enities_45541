# -*- coding: gb18030 -*-
#
# $Id: TrackBar.py,v 1.14 2008-08-21 09:07:12 huangyongwei Exp $

"""
implement track bar class

2007.6.26: writen by huangyongwei
"""
"""
composing :
	Window
		-- slider   ( GUI.XXX )		-> sliding button
"""

from guis import *
from Control import Control

class HTrackBar( Control ) :
	def __init__( self, tbar = None, pyBinder = None ) :
		Control.__init__( self, tbar, pyBinder )
		self.__initialize( tbar )

		self.__stepCount = -1

	def subclass( self, tbar, pyBinder = None ) :
		Control.subclass( self, tbar, pyBinder )
		self.__initialize( tbar )

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_TrackBar :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		Control.generateEvents_( self )
		self.__onSlide = self.createEvent_( "onSlide" )

	@property
	def onSlide( self ) :
		return self.__onSlide


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, tbar ) :
		if tbar is None : return
		self.focus = True
		self.pySlider_ = Slider( tbar.slider, self )

	# -------------------------------------------------
	def __getMaxLen( self ) :
		return self.width - self.pySlider_.width

	# -------------------------------------------------
	def __slide( self, currLen ) :
		stepCount = self.__stepCount
		if stepCount == 0 : return
		maxLen = self.__getMaxLen()
		if stepCount > 0 :
			step = maxLen / stepCount
			currCount = round( currLen / step )
			currLen = currCount * step
		self.pySlider_.left = currLen
		value = currLen / maxLen
		self.onSlide( value )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLMouseDown_( self, mods ) :
		maxLen = self.__getMaxLen()
		mx = self.mousePos.x - self.pySlider_.width / 2
		self.value = mx / maxLen
		return True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def upScroll( self ) :
		if self.value < self.__stepCount :
			self.value = 0
		else :
			self.value -= self.__stepCount

	def downScroll( self ) :
		if self.value > 1 - self.__stepCount :
			self.value = 1
		else :
			self.value += self.__stepCount


	# ----------------------------------------------------------------
	# friend methods of slider
	# ----------------------------------------------------------------
	def onSlide__( self, dx ) :
		maxLen = self.__getMaxLen()
		oldLen = self.pySlider_.left
		if dx < 0 and oldLen <= 0 : return
		if dx > 0 and oldLen >= maxLen : return
		newLen = oldLen + dx
		if newLen <= 0 and dx < 0 :
			newLen = 0
		elif newLen >= maxLen and dx > 0 :
			newLen = maxLen
		self.__slide( newLen )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getValue( self ) :
		maxLen = self.__getMaxLen()
		currLen = self.pySlider_.left
		return currLen / maxLen

	def _setValue( self, value ) :
		value = min( max( value, 0 ), 1 )
		maxLen = self.__getMaxLen()
		currLen = value * maxLen
		self.__slide( currLen )

	# ---------------------------------------
	def _getStepCount( self ) :
		return self.__stepCount

	def _setStepCount( self, count ) :
		self.__stepCount = count


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	value = property( _getValue, _setValue )					# float: 获取/设置当前活动值( 0 ~ 1 之间)
	stepCount = property( _getStepCount, _setStepCount )		# int: 滑条值分成多少等分（如果为 -1，则滑条平滑滑动，如果为 0 则无法移动）


# --------------------------------------------------------------------
# class of Slider
# --------------------------------------------------------------------
class Slider( Control ) :
	def __init__( self, slider, pyBinder ) :
		Control.__init__( self, slider, pyBinder )
		self.focus = True
		self.crossFocus = True
		self.moveFocus = True

		self.__mouseSit = 0
		self.__canSlide = False

		self.__mappings = {}
		self.__mappings[UIState.COMMON] = self.mapping
		self.__mappings[UIState.HIGHLIGHT] = self.mapping
		self.__mappings[UIState.PRESSED] = self.mapping

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_TrackBar :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def setStatesMapping( self, mode ) :
		"""
		set states gui mapping
		"""
		row, col = mode
		self.__mappings[UIState.COMMON] = util.getStateMapping( self.size, mode, UIState.ST_R1C1 )
		state = ( 1 / col + 1, 1 % col + 1 )
		self.__mappings[UIState.HIGHLIGHT] = util.getStateMapping( self.size, mode, state )
		state = ( 2 / col + 1, 2 % col + 1 )
		self.__mappings[UIState.PRESSED] = util.getStateMapping( self.size, mode, state )
		state = ( 3 / col + 1, 3 % col + 1 )
		self.__mappings[UIState.DISABLE] = util.getStateMapping( self.size, mode, state )
		self.setState( UIState.COMMON )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLMouseDown_( self, mods ) :
		self.__mouseSit = self.mousePos[0]
		self.setState( UIState.PRESSED )
		self.__canSlide = True
		uiHandlerMgr.capUI( self )
		return True

	def onLMouseUp_( self, mods ) :
		self.__canSlide = False
		self.setState( UIState.COMMON )
		uiHandlerMgr.uncapUI( self )
		return True

	def onMouseEnter_( self ) :
		if not BigWorld.isKeyDown( KEY_LEFTMOUSE ) :
			self.setState( UIState.HIGHLIGHT )
		return True

	def onMouseMove_( self, dx, dy ) :
		if not self.__canSlide : return False
		if dx == 0 : return True
		mouseX = self.mousePos[0]
		if dx > 0 and mouseX < self.__mouseSit : return True
		if dx < 0 and mouseX > self.__mouseSit : return True
		self.pyBinder.onSlide__( mouseX - self.__mouseSit )
		return True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setState( self, state ) :
		self.mapping = self.__mappings[state]

