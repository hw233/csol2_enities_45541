# -*- coding: gb18030 -*-
#
# $Id: CreditPanel.py,v 1.1 2007-11-23 05:49:36 fangpengjun Exp $

from guis import *
from guis.controls.TabCtrl import TabPanel

class CreditPanel( TabPanel ):
	def __init__( self, panel = None, pyBinder = None ):
		TabPanel.__init__( self, panel, pyBinder )
