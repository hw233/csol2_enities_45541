# -*- coding: gb18030 -*-
#
# $Id: ClipPanel.py,v 1.6 2008-06-21 01:44:11 huangyongwei Exp $

"""
implement clip panel class
this class just corresponds to GUIWindowComponent, and its engine gui must be GUIWindowComponent
it is used to clip the offside children

2007.03.16 : wirten by huangyongwei
"""
"""
composing :
	GUI.Window
"""

from guis import *
from Control import Control


# --------------------------------------------------------------------
# implement horizontal and vertical ClipPanel
# --------------------------------------------------------------------
class HVClipPanel( Control ) :
	def __init__( self, panel = None, pyBinder = None ) :
		Control.__init__( self, panel, pyBinder )
		self.__initialize( panel )

	def subclass( self, panel, pyBinder = None ) :
		Control.subclass( self, panel, pyBinder )
		self.__initialize( panel )
		return self

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_ClipPanel :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, panel ) :
		if panel is None : return
		assert( panel is not GUI.Window )
		self.__panel = panel


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getMaxScroll( self ) :
		return tuple( self.__panel.maxScroll )

	def _setMaxScroll( self, scroll ) :
		self.__panel.maxScroll = scroll

	def _getScroll( self ) :
		return tuple( self.__panel.scroll )

	def _setScroll( self, scroll ) :
		self.__panel.scroll = scroll

	def _getScrollRate( self ) :
		return self.h_scrollRate, self.v_scrollRate

	def _setScrollRate( self, rate ) :
		self.h_scrollRate = rate[0]
		self.v_scrollRate = rate[1]

	# ---------------------------------------
	def _getRMaxScroll( self ) :
		return self.rh_maxScroll, self.rv_maxScroll

	def _setRMaxScroll( self, scroll ) :
		hMaxScroll = s_util.toPXMeasure( scroll[0] )
		vMaxScroll = s_util.toPYMeasure( scroll[1] )
		self.__panel.maxScroll = hMaxScroll, vMaxScroll

	def _getRScroll( self ) :
		return self.rh_scroll, self.rv_scroll

	def _setRScroll( self, scroll ) :
		hScroll = s_util.toPXMeasure( scroll[0] )
		vScroll = s_util.toPYMeasure( scroll[1] )
		self.__panel.scroll = hScroll, vScroll

	# -------------------------------------------------
	def _getHMaxScroll( self ) :
		return self.__panel.maxScroll[0]

	def _setHMaxScroll( self, value ) :
		maxScroll = self.__panel.maxScroll
		self.__panel.maxScroll = ( value, maxScroll[1] )

	# ---------------------------------------
	def _getVMaxScroll( self ) :
		return self.__panel.maxScroll[1]

	def _setVMaxScroll( self, value ) :
		maxScroll = self.__panel.maxScroll
		self.__panel.maxScroll = ( maxScroll[0], value )

	# -------------------------------------------------
	def _getHScroll( self ) :
		return self.__panel.scroll[0]

	def _setHScroll( self, value ) :
		scroll = self.__panel.scroll
		self.__panel.scroll = ( value, scroll[1] )

	# ---------------------------------------
	def _getVScroll( self ) :
		return self.__panel.scroll[1]

	def _setVScroll( self, value ) :
		scroll = self.__panel.scroll
		self.__panel.scroll = ( scroll[0], value )

	def _getHScrollRate( self ) :
		if self.h_maxScroll == 0 : return 0
		return self.h_scroll / self.h_maxScroll

	def _setHScrollRate( self, rate ) :
		self.h_scroll = self.h_maxScroll * rate

	def _getVScrollRate( self ) :
		if self.v_maxScroll == 0 : return 0
		return self.v_scroll / self.v_maxScroll

	def _setVScrollRate( self, rate ) :
		self.v_scroll = self.v_maxScroll * rate

	# -------------------------------------------------
	def _getRHMaxScroll( self ) :
		return s_util.toRXMeasure( self.__panel.maxScroll[0] )

	def _setRHMaxScroll( self, value ) :
		maxScroll = self.__panel.maxScroll
		self.__panel.maxScroll = ( s_util.toPXMeasure( value ), maxScroll[1] )

	# ---------------------------------------
	def _getRVMaxScroll( self ) :
		return s_util.toRXMeasure( self.__panel.maxScroll[1] )

	def _setRVMaxScroll( self, value ) :
		maxScroll = self.__panel.maxScroll
		self.__panel.maxScroll = ( maxScroll[1], s_util.toPXMeasure( value ) )

	# -------------------------------------------------
	def _getRHScroll( self ) :
		return s_util.toRXMeasure( self.__panel.scroll[0] )

	def _setRHScroll( self, value ) :
		scroll = self.__panel.scroll
		self.__panel.scroll = ( s_util.toPXMeasure( value ), scroll[1] )

	# ---------------------------------------
	def _getRVScroll( self ) :
		return s_util.toRXMeasure( self.__panel.scroll[1] )

	def _setRVScroll( self, value ) :
		scroll = self.__panel.scroll
		self.__panel.scroll = ( scroll[0], s_util.toPXMeasure( value ) )

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	# get or set max scroll of the panel
	maxScroll = property( _getMaxScroll, _setMaxScroll )
	# get or set current scroll of the panel
	scroll = property( _getScroll, _setScroll )
	# get scroll rate
	scrollRate = property( _getScrollRate, _setScrollRate )
	# get or set max relative scroll of the panel
	r_maxScroll = property( _getRMaxScroll, _setRMaxScroll )
	# get or set current relative scroll of the panel
	r_scroll = property( _getRScroll, _setRScroll )

	# get or set the maxscroll value on horizontal( the same as GUI.Window().maxScroll[0] )
	h_maxScroll = property( _getHMaxScroll, _setHMaxScroll )
	# get or set the maxscroll value on vertical( the same as GUI.Window().maxScroll[1] )
	v_maxScroll = property( _getVMaxScroll, _setVMaxScroll )
	# get or set the scroll value on horizontal( the same as GUI.Window().scroll[0] )
	h_scroll = property( _getHScroll, _setHScroll )
	# get or set the scroll value on vertical( the same as GUI.Window().scroll[1] )
	v_scroll = property( _getVScroll, _setVScroll )
	# get horizontal scroll rate
	h_scrollRate = property( _getHScrollRate, _setHScrollRate )
	# get vertical scroll rate
	v_scrollRate = property( _getVScrollRate, _setVScrollRate )

	# get or set the relative maxscroll value on horizontal( the same as GUI.Window().maxScroll[0] )
	rh_maxScroll = property( _getRHMaxScroll, _setRHMaxScroll )
	# get or set the relative maxscroll value on vertical( the same as GUI.Window().maxScroll[1] )
	rv_maxScroll = property( _getRVMaxScroll, _setRVMaxScroll )
	# get or set the relative scroll value on horizontal( the same as GUI.Window().scroll[0] )
	rh_scroll = property( _getRHScroll, _setRHScroll )
	# get or set the relative scroll value on vertical( the same as GUI.Window().scroll[1] )
	rv_scroll = property( _getRVScroll, _setRVScroll )


# --------------------------------------------------------------------
# implement horizontal ClipPanel
# --------------------------------------------------------------------
class HClipPanel( Control ) :
	def __init__( self, panel = None, pyBinder = None ) :
		Control.__init__( self, panel, pyBinder )
		self.__initialize( panel )

	def subclass( self, panel, pyBinder = None ) :
		Control.subclass( self, panel, pyBinder )
		self.__initialize( panel )
		return self

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_ClipPanel :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, panel ) :
		if panel is None : return
		assert( panel is not GUI.Window )
		self.__panel = panel


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getMaxScroll( self ) :
		return self.__panel.maxScroll[0]

	def _setMaxScroll( self, scroll ) :
		self.__panel.maxScroll = scroll, self.__panel.maxScroll[1]

	def _getScroll( self ) :
		return self.__panel.scroll[0]

	def _setScroll( self, scroll ) :
		self.__panel.scroll = scroll, self.__panel.scroll[1]

	# ---------------------------------------
	def _getRMaxScroll( self ) :
		return s_util.toRXMeasure( self.__panel.maxScroll[0] )

	def _setRMaxScroll( self, scroll ) :
		scroll = s_util.toPXMeasure( scroll )
		self.__panel.maxScroll = scroll, self.__panel.maxScroll[1]

	def _getRScroll( self ) :
		return s_util.toRXMeasure( self.__panel.scroll[0] )

	def _setRScroll( self, scroll ) :
		scroll = s_util.toPXMeasure( scroll )
		self.__panel.scroll = scroll, self.__panel.scroll[1]

	# ---------------------------------------
	def _getScrollRate( self ) :
		if self.maxScroll == 0 : return 0
		return self.scroll / self.maxScroll

	def _setScrollRate( self, rate ) :
		self.scroll = self.maxScroll * rate


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	# get or set max scroll of the panel
	maxScroll = property( _getMaxScroll, _setMaxScroll )
	# get or set current scroll of the panel
	scroll = property( _getScroll, _setScroll )

	# get or set max relative scroll of the panel
	r_maxScroll = property( _getRMaxScroll, _setRMaxScroll )
	# get or set current relative scroll of the panel
	r_scroll = property( _getRScroll, _setRScroll )

	# get horizontal scroll rate
	scrollRate = property( _getScrollRate, _setScrollRate )


# --------------------------------------------------------------------
# implement vertical ClipPanel
# --------------------------------------------------------------------
class VClipPanel( Control ) :
	def __init__( self, panel = None, pyBinder = None ) :
		Control.__init__( self, panel, pyBinder )
		self.__initialize( panel )

	def subclass( self, panel, pyBinder = None ) :
		Control.subclass( self, panel, pyBinder )
		self.__initialize( panel )
		return self

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_ClipPanel :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, panel ) :
		if panel is None : return
		assert( panel is not GUI.Window )
		self.__panel = panel


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getMaxScroll( self ) :
		return self.__panel.maxScroll[1]

	def _setMaxScroll( self, scroll ) :
		self.__panel.maxScroll = self.__panel.maxScroll[0], scroll

	def _getScroll( self ) :
		return self.__panel.scroll[1]

	def _setScroll( self, scroll ) :
		self.__panel.scroll = self.__panel.scroll[0], scroll

	# ---------------------------------------
	def _getRMaxScroll( self ) :
		return s_util.toRXMeasure( self.__panel.maxScroll[1] )

	def _setRMaxScroll( self, scroll ) :
		scroll = s_util.toPXMeasure( scroll )
		self.__panel.maxScroll = self.__panel.maxScroll[0], scroll

	def _getRScroll( self ) :
		return s_util.toRXMeasure( self.__panel.scroll[1] )

	def _setRScroll( self, scroll ) :
		scroll = s_util.toPXMeasure( scroll )
		self.__panel.scroll = self.__panel.scroll[0], scroll

	# ---------------------------------------
	def _getScrollRate( self ) :
		if self.maxScroll == 0 : return 0
		return self.scroll / self.maxScroll

	def _setScrollRate( self, rate ) :
		self.scroll = self.maxScroll * rate


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	# get or set max scroll of the panel
	maxScroll = property( _getMaxScroll, _setMaxScroll )
	# get or set current scroll of the panel
	scroll = property( _getScroll, _setScroll )

	# get or set max relative scroll of the panel
	r_maxScroll = property( _getRMaxScroll, _setRMaxScroll )
	# get or set current relative scroll of the panel
	r_scroll = property( _getRScroll, _setRScroll )

	# get horizontal scroll rate
	scrollRate = property( _getScrollRate, _setScrollRate )
