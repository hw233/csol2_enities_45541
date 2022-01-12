# -*- coding: gb18030 -*-
#
"""
implement AttributeItems
"""
from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.controls.Button import Button
from guis.controls.Control import Control
from guis.controls.StaticText import StaticText
from guis.controls.ProgressBar import HProgressBar as ProgressBar
import BigWorld
import csdefine

#宠物抗性条
class ResistItem( ProgressBar ):

	def __init__( self, resistItem ):
		ProgressBar.__init__( self, resistItem, pyBinder = None )
		self.crossFocus = True
		self.valStr = ""
		self.value = 0.0

	def __getDescription( self, tag):
			dsp = labelGather.getText( "PetsWindow:PetsPanel", tag, self.valStr )
			return dsp

	# ----------------------------------------------------------------------
	def onMouseEnter_( self,):
		Control.onMouseEnter_( self )
		dsp = self.__getDescription( self.tag )
		if dsp == "": return
		toolbox.infoTip.showToolTips( self, dsp )
		return True

	def onMouseLeave_( self ):
		Control.onMouseLeave_( self )
		toolbox.infoTip.hide()
		return True

	# ---------------------------------------------------------------
	def setState( self, num ):
		self.crossFocus = num > 0

	def update( self, value ):# 更新状态值
		rate = float( value )
		self.valStr = "%0.1f%%" % ( rate*100.0 )
		self.value = value

	# -------------------------------------------------------------------
	def _getTag( self ):

		return self.__tag

	def _setTag( self, tag ):

		self.__tag = tag

	tag = property( _getTag, _setTag )

# -----------------------------------------------------------------------
#宠物经验、寿命等属性
class PropertyItem( Control ):
	def __init__( self, item = None ):
		Control.__init__( self, item )
		self.__initItem( item )

	def __initItem( self, item ):
		self.__pyValueBar = ProgressBar( item.valueBar )
		self.__pyValueBar.value = 0.0
		self.__pyValueBar.clipMode = "RIGHT"

		self.__pyStValue = StaticText( item.stValue )
		self.__pyStValue.color = ( 255.0, 255.0, 255.0 )
		self.__pyStValue.text = ""
		self.__pyStValue.fontSize = 12
		
		self.__pyStName = StaticText( item.stName )
		self.__pyStName.color = ( 236.0, 218.0, 157.0 )

	def onMouseEnter_( self ):
		Control.onMouseEnter_( self )
		return True

	def update( self, tuple ):
		if tuple[1] == 0:
			self.__pyValueBar.value = 0
			self.__pyStValue.text = "%d/%d"%( tuple[0], tuple[1] )
		elif tuple[1] == "--":
			self.__pyStValue.text = "-- / --"
			self.__pyValueBar.value = 0
		else:
			self.__pyValueBar.value = float( tuple[0] )/tuple[1]
			self.__pyStValue.text = "%d/%d"%( tuple[0], tuple[1] )

	def _getName( self ):
		return self.__pyStName.text
	
	def _setName( self, text ):
		self.__pyStName.text = text

	name = property( _getName, _setName )

# --------------------------------------------------------------------------
#宠物强化属性
class EnhanceItem( PyGUI ):
	def __init__( self, item ):
		PyGUI.__init__( self, item )
		
		self.__pyStName = StaticText( item.stName )
		self.__pyStName.color = ( 236.0, 218.0, 157.0 )
		self.__pyStValue = StaticText( item.stValue )
		self.__pyStValue.color = ( 255.0, 255.0, 255.0 )
		self.__pyStValue.text = ""
		
		self.__pyStEnhaneNum = StaticText( item.stEnhNum )
		self.__pyStEnhaneNum.color = ( 255.0, 255.0, 255.0 )
		self.__pyStEnhaneNum.text = ""
	
	def update( self, tuple ):
		if tuple[0] == -1:
			self.__pyStValue.text = ""
		else:
			self.__pyStValue.text = str(int( tuple[0] ) )
		if tuple[1] == -1:
			self.__pyStEnhaneNum.text = ""
		else:
			self.__pyStEnhaneNum.text =  "X" + str( tuple[1] )
	
	def _getName( self ):
		return self.__pyStName.text
	
	def _setName( self, text ):
		self.__pyStName.text = text

	name = property( _getName, _setName )