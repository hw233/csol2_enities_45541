# -*- coding: gb18030 -*-
#
# $Id: InputBox.py,v 1.27 2008-08-26 02:21:47 huangyongwei Exp $

"""
implement delete role verifier box

2009/05/09 : writen by huangyongwei
"""

from guis import *
from LabelGather import labelGather
from guis.tooluis.inputbox.InputBox import InputBox
from guis.controls.StaticText import StaticText

class VehicleDelVerifier( InputBox ) :
	def __init__( self ) :
		wnd = GUI.load( "guis/general/petswindow/vehiclePanel/verifier/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		InputBox.__init__( self, wnd )
		self.addToMgr()
		self.__pySTTip = StaticText( wnd.stTip )
		labelGather.setLabel( wnd.lbTitle, "PetsWindow:VehiclesPanel", "freeVehicle" )
		labelGather.setLabel( wnd.inputName, "PetsWindow:VehiclesPanel", "inputDel" )

	def show( self, tip, callback, pyOwner = None ) :
		self.__pySTTip.text = tip
		InputBox.show( self, "", callback, pyOwner )
	
	def hide(self):
		"""
		destroy  VehicleDelVerifier  instance
		"""
		InputBox.hide(self)
		self.removeFromMgr()
		
	def __del__(self):
		"""
		"""
		pass
