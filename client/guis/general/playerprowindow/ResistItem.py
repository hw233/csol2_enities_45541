# -*- coding: gb18030 -*-
#
# $Id: ResistItem.py,v 1.5 2008-08-19 09:31:11 huangyongwei Exp $
from guis import *
from LabelGather import labelGather
from guis.controls.Control import Control
from guis.controls.ProgressBar import HProgressBar

class ResistItem( HProgressBar ):

	_dsp_dict = { "Giddy": labelGather.getText( "PlayerProperty:EquipPanel", "Giddy" ),
		"Sleep":labelGather.getText( "PlayerProperty:EquipPanel", "Sleep" ),
		"Fix":labelGather.getText( "PlayerProperty:EquipPanel", "Fix" ),
		"Hush":labelGather.getText( "PlayerProperty:EquipPanel", "Hush" )
		}

	def __init__( self, tag, resistBar ):
		HProgressBar.__init__( self, resistBar, pyBinder = None )
		self.__tag = tag
		self.crossFocus = True
		self.value = 0
		self.__valText = ""
		self.clipMode = "RIGHT"

	def __getDescription( self, tag):
		if self._dsp_dict.has_key( tag ):
			dsp = self._dsp_dict[tag]%self.__valText
		return dsp

	# ----------------------------------------------------------------------
	def onMouseEnter_( self,):
		HProgressBar.onMouseEnter_( self )
		tag = self.tag
		dsp = self.__getDescription( tag )
		toolbox.infoTip.showToolTips( self, dsp )
		return True

	def onMouseLeave_( self ):
		HProgressBar.onMouseLeave_( self )
		toolbox.infoTip.hide()
		return True

	# ---------------------------------------------------------------
	def updateValue( self, value ):# 更新状态值
		rate = float( value )
		self.value = rate
		self.__valText = "%0.1f" % ( rate*100.0 ) + "%"
	# -------------------------------------------------------------------
	def _getTag( self ):

		return self.__tag

	def _setTag( self, tag ):

		self.__tag = tag

	tag = property( _getTag, _setTag )