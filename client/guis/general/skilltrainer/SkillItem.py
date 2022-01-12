# -*- coding: gb18030 -*-
#
# $Id: SkillItem.py,v 1.6 2008-06-27 03:19:45 huangyongwei Exp $

"""
implement listitem class
"""
"""
composing :
	GUI.Window
		-- lbText ( GUI.Text )
		-- lbState ( GUI.Text )
"""

from guis import *
from LabelGather import labelGather
from guis.controls.ListItem import SingleColListItem
from guis.controls.StaticText import StaticText

class SkillItem( SingleColListItem ) :
	def __init__( self, item ) :
		SingleColListItem.__init__( self, item )
		self.commonBackColor = ( 255, 255, 255, 255 )
		self.selectedBackColor = ( 255, 255, 255, 255 )
		self.highlightBackColor = ( 255, 255, 255, 255 )

		self.__pyLbLevel = StaticText( item.lbLevel )
		self.__level = 0
		self.__name = ""

	# ----------------------------------------------------------------
	# protected methods
	# ----------------------------------------------------------------
	def onStateChanged_( self, state ) :
		self.__pyLbLevel.font = self.font
		self.__pyLbLevel.color = self.foreColor
		elements = self.getGui().elements
		for element in elements.values():
			element.visible = state in [ UIState.HIGHLIGHT, UIState.SELECTED ]


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setCommonForeColor( self, color ) : #使角色需要等级与技能名称的颜色一致
		SingleColListItem._setCommonForeColor( self, color )
		self.__pyLbLevel.color = color
		
	def _getLevel( self ) :
		return self.__level

	def _setLevel( self, level ) :
		self.__level = level
		self.__pyLbLevel.text = labelGather.getText( "SkillTrainer:main", "skillLevel" )%level

	def _getName( self ):
		return self.__name

	def _setName( self, name ):
		self.__name = name

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	commonForeColor = property( SingleColListItem._getCommonForeColor, _setCommonForeColor )
	level = property( _getLevel, _setLevel )
	name = property( _getName, _setName )