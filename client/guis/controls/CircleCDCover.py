# -*- coding: gb18030 -*-
#
# this module implement CircleCDCover
# written by gjx 2009-6-16

# CircleCDCover 用于技能冷却的界面表现，围绕图标中心顺时针/逆时针递减

from guis import *
from guis.controls.CircleShader import CircleShader
from guis.controls.Control import Control
from Time import Time


class CircleCDCover( CircleShader, Control ) :

	__cb_interval = 0.01		# 更新间隔

	def __init__( self, cover = None, pyBinder = None ) :
		CircleShader.__init__( self, cover )
		Control.__init__( self, cover, pyBinder )
		self.focus = False
		self.__lastTime = 0
		self.__endTime = 0
		self.__startValue = 0
		self.__cdCBID = 0

		self.__initialize( cover )
		self.reset()

	def __initialize( self, cover ) :
		pass

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_CircleCDCover :
			INFO_MSG( str( self ) )

	def subclass( self, cover, pyBinder = None ) :
		Control.subclass( self, cover, pyBinder )
		self.__initialize( cover )
		return self


	# ----------------------------------------------------------------
	# event
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
	def __countdown( self ) :
		now = Time.time()
		remainTime = self.__endTime - now
		if remainTime > 0 :
			self.value = self.__startValue * remainTime / self.__lastTime
			self.__cdCBID = BigWorld.callback( self.__cb_interval, self.__countdown )
		else :
			self.__onCDOver()

	def __setDefValue( self, lastTime ) :
		self.__lastTime = lastTime
		self.__endTime = Time.time() + self.__lastTime

	def __onCDOver( self ) :
		self.reset()
		self.onUnfreezed()

	def __cancelCallback( self ) :
		BigWorld.cancelCallback( self.__cdCBID )
		self.__cdCBID = 0


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def unfreeze( self, lastTime, startValue = 1 ) :
		self.reset( startValue )
		if lastTime > 0 :
			self.__setDefValue( lastTime )
			self.__countdown()

	def reset( self, value = 0 ) :
		self.__cancelCallback()
		self.value = value
		self.__startValue = self.value


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getEndTime( self ) :
		"""
		获取结束时间
		"""
		return self.__endTime

	endTime = property( _getEndTime )								# 获取冷却结束时间
