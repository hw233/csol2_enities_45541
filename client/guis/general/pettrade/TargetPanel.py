# -*- coding: gb18030 -*-
#
# $Id: TargetPanel.py,v 1.1 2008-05-30 09:51:44 fangpengjun Exp $

"""
implement TargetPanel class
"""

from guis import *
from PropertyPanel import PropertyPanel
import GUIFacade

class TargetPanel( PropertyPanel ):
	def __init__( self, panel = None, pyBinder = None ):
		PropertyPanel.__init__( self, panel, pyBinder )
		self.pyPetsCB_.readOnly = False
		self.pyPetsCB_.enable = False
		self.pyFrontBtn_.enable = False
		self.pyNextBtn_.enable = False
		
	def subclass( self, panel, pyBinder ):
		PropertyPanel.subclass( self, panel, pyBinder )
		return self
	
	def onPetChange( self, epitome ):
		PropertyPanel.targetPetChange_( self, epitome )
	
	def onResumePanels( self ):
		PropertyPanel.resumePanels_( self )
	