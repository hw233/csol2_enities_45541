# -*- coding: gb18030 -*-
#
# $Id: CompareDspItem.py,v 1.2 2008-08-19 09:31:37 huangyongwei Exp $



from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
import GUIFacade
from guis import *

class CompareDspItem( BOItem ) :
	def __init__( self, item = None, pyBinder = None ) :
		BOItem.__init__( self, item, pyBinder )


	def onDescriptionShow_( self ) :
		"""
		when mouse enter the item it will be called
		"""
		selfDsp = self.description
		if selfDsp is None : return
		if selfDsp == [] : return
		if selfDsp == "" : return

		equipDsps = GUIFacade.getSameTypeEquipDecriptionsII( self.itemInfo )
		#dsps = [selfDsp] + equipDsps
		toolbox.infoTip.showItemTips( self, selfDsp, *equipDsps )

