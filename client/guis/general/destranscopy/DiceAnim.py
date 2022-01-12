# -*- coding: gb18030 -*-

"""
implement animation dice class

"""

import os
from guis import *
from guis.controls.Icon import Icon

class DiceAnim( Icon ):
	"""
	色子动画
	"""
	_animTexture = "guis/general/destranscopy/dices/dices.texanim"
	_staticTexturePath = "guis/general/destranscopy/dices/static/%d.dds"
	
	def __init__( self, dice, pyBinder = None ) :
		Icon.__init__( self, dice )
		self.focus = False
		self.crossFocus = True
		self.__staticTexure = ""							# 静态贴图路径,
		self.__isPlaying = False							# 是否处于播放动画状态
		self.__point = 0
		
	def play( self ) :
		"""
		播放动画
		"""
		self.__isPlaying = True
		Icon._setTexture( self, self._animTexture )
		self.mapping = ( ( 0, 0 ), ( 0, 1, ), ( 1, 1 ), ( 1, 0 ) )

	def stop( self ) :
		"""
		停止动画播放
		"""
		self.__isPlaying = False
		Icon._setTexture( self, self.__staticTexure )
		self.mapping = ( ( 0, 0 ), ( 0, 1, ), ( 1, 1 ), ( 1, 0 ) )

	def _getPoint( self ) :
		return self.__point

	def _setPoint( self, point ) :
		self.__point = point
		self.__staticTexure = self._staticTexturePath%point

	def _getPlaying( self ) :
		return self.__isPlaying
		
	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	point = property( _getPoint, _setPoint )
	playing = property( _getPlaying )