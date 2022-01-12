# -*- coding: gb18030 -*-

"""
implement animation dice class

"""

import os
from guis import *
from guis.controls.Icon import Icon

class DiceAnim( Icon ):
	"""
	ɫ�Ӷ���
	"""
	_animTexture = "guis/general/destranscopy/dices/dices.texanim"
	_staticTexturePath = "guis/general/destranscopy/dices/static/%d.dds"
	
	def __init__( self, dice, pyBinder = None ) :
		Icon.__init__( self, dice )
		self.focus = False
		self.crossFocus = True
		self.__staticTexure = ""							# ��̬��ͼ·��,
		self.__isPlaying = False							# �Ƿ��ڲ��Ŷ���״̬
		self.__point = 0
		
	def play( self ) :
		"""
		���Ŷ���
		"""
		self.__isPlaying = True
		Icon._setTexture( self, self._animTexture )
		self.mapping = ( ( 0, 0 ), ( 0, 1, ), ( 1, 1 ), ( 1, 0 ) )

	def stop( self ) :
		"""
		ֹͣ��������
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