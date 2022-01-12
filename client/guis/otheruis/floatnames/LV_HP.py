# -*- coding: gb18030 -*-
#
# $Id: MonsterName.py,v 1.13 2008-06-27 03:20:42 huangyongwei Exp $

"""
implement level and hpbar combinner
2009.02.13：tidy up by huangyongwei
"""


from guis import *
from guis.common.GUIBaseObject import GUIBaseObject
from guis.common.PyGUI import PyGUI
from guis.controls.StaticText import StaticText
from guis.controls.ProgressBar import HProgressBar as ProgressBar
from LabelGather import labelGather

class LV_HP( GUIBaseObject ) :
	def __init__( self, bg ) :
		GUIBaseObject.__init__( self, bg )
		self.__pyLbLevel = StaticText( bg.lbLevel )
		self.__pyLbLevel.setFloatNameFont()
		self.__pyHPBg = PyGUI( bg.hpBg )
		self.__pyHPBar = ProgressBar( bg.hpBg.hpBar )

		self.__level = 1


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def __layout( self ) :
		if self.__pyLbLevel.visible and self.__pyLbLevel.text != "" :
			self.__pyLbLevel.left = 0
			if self.__pyHPBg.visible :
				self.__pyHPBg.left = self.__pyLbLevel.right + 6
				self.width = self.__pyHPBg.right + 1
			else :
				self.width = self.__pyLbLevel.right + 1
			self.visible = True
		else :
			if self.__pyHPBg.visible :
				self.__pyHPBg.left = 0
				self.width = self.__pyHPBg.right + 1
				self.visible = True
			else :
				self.visible = False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def toggleLevel( self, visible ) :
		"""
		显示/隐藏等级
		"""
		self.__pyLbLevel.visible = visible
		self.__layout()

	def toggleHPBar( self, visible ) :
		self.__pyHPBg.visible = visible
		self.__layout()


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getLevel( self ) :
		return self.__level

	def _setLevel( self, level ) :
		self.__level = level
		strLevel = ""
		if level > 0 : strLevel = labelGather.getText( "FloatName:LV_HP", "level", level )
		self.__pyLbLevel.text = strLevel
		self.__layout()

	def _getHPValue( self ) :
		return self.__pyHPBar.value

	def _setHPValue( self, value ) :
		self.__pyHPBar.value = value
	
	def _getHPTexture( self ):
		return self.__pyHPBar.texture
	
	def _setHPTexture( self, texture ):
		self.__pyHPBar.texture = texture

	def _getHPColor( self, color ):
		return self.__pyHPBar.color

	def _setHPColor( self, color ):
		self.__pyHPBar.color = color

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	level = property( _getLevel, _setLevel )
	hpValue = property( _getHPValue, _setHPValue )
	hpTexture = property( _getHPTexture, _setHPTexture )
	color = property( _getHPColor, _setHPColor )
