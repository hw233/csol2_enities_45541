# -*- coding: gb18030 -*-
#
# $Id: CooldownCover.py,v 1.9 2008-06-21 01:48:39 huangyongwei Exp $

"""
implement cover class

2007/03/19: writen by huanngyongwei
"""
"""
composing :
	GUI.Simple
"""

import time
from guis import *
from guis.controls.ClipShader import ClipShader
from guis.controls.Control import Control
from Time import Time

class Cover( Control ) :
	__cc_clip_speed 	= 0.2
	__cc_clip_interval  = 0.05

	def __init__( self, cover = None, pyBinder = None ) :
		Control.__init__( self, cover, pyBinder )
		self.__initialize( cover )

		self.__lastTime = 0
		self.__endTime = 0
		self.__startValue = 1
		self.__clipCBID = 0

		self.reset( 0 )

	def subclass( self, cover, pyBinder = None ) :
		Control.subclass( self, cover, pyBinder )
		self.__initialize( cover )
		return self

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_CooldownCover :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, cover ) :
		if cover is None : return
		self.focus = False
		self.__pyClipper = ClipShader( cover )
		self.__pyClipper.clipMode = "TOP"


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		Control.generateEvents_( self )
		self.__onUnfreezed = self.createEvent_( "onUnfreezed" )

	@property
	def onUnfreezed( self ) :
		return self.__onUnfreezed


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __countDown( self ) :
		"""
		cyclic clip
		"""
		now = Time.time()
		remainTime = self.__endTime - now
		if now < self.__endTime :
			self.__pyClipper.value = self.__startValue * remainTime / self.__lastTime
			self.__clipCBID = BigWorld.callback( self.__cc_clip_interval, Functor( self.__countDown ) )
		else :
			self.reset()
			self.onUnfreezed()

	# -------------------------------------------------
	def __setDefValues( self, lastTime ) :
		"""
		initialize correlative members
		"""
		self.__lastTime = lastTime
		self.__endTime = Time.time() + lastTime


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def unfreeze( self, lastTime, startValue = 1 ) :
		"""
		unfreeze
		"""
		self.reset( startValue )
		if lastTime > 0 :
			self.__setDefValues( lastTime )
			self.__countDown()

	def reset( self, value = 0 ) :
		BigWorld.cancelCallback( self.__clipCBID )
		value = max( 0, value )
		value = min( 1, value )
		self.__startValue = value
		self.__pyClipper.speed = 1
		self.__pyClipper.value = value
		self.__pyClipper.speed = Cover.__cc_clip_speed


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getEndTime( self ) :
		return self.__endTime


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	endTime = property( _getEndTime )
