# -*- coding: gb18030 -*-
#
# $Id: AttributePanel.py,v 1.3 2008-06-27 03:18:43 huangyongwei Exp $

"""
implement AttributePanel
"""
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from LabelGather import labelGather
import BigWorld
import csdefine

class AttributePanel( PyGUI ):
	def __init__( self, panel = None, pyBinder = None ):
		PyGUI.__init__( self, panel )
		self.__initPanel( panel )
		self.__dbid = -1

	def __initPanel( self, panel ):
		self.__pyLabels = {}
		for name, item in panel.children:
			if "_item" not in name:continue
			tag = name.split( "_" )[0]
			pyLabel = StaticText( item.lbValue )
			pyLabel.text = ""
			pyLabel.charSpace = -1
			pyLabel.fontSize = 12
			pyLabel.color = (255.0, 255.0, 255.0)
			self.__pyLabels[tag] = pyLabel

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setLabel( panel.life_item.stName, "petTrade:attributePanel", "life_item" )
		labelGather.setLabel( panel.takeLevel_item.stName, "petTrade:attributePanel", "takeLevel_item" )
		labelGather.setLabel( panel.spirit_item.stName, "petTrade:attributePanel", "spirit_item" )
		labelGather.setLabel( panel.const_item.stName, "petTrade:attributePanel", "const_item" )
		labelGather.setLabel( panel.ability_item.stName, "petTrade:attributePanel", "ability_item" )

#	def setCombineState( self, isCombine ):
#		self.__pyCombineBtn.enable = isCombine

	def updateInfo( self, tag, dbid, tuple ):
		self.__dbid = dbid
		if self.__pyLabels.has_key( tag ):
			pyLabel = self.__pyLabels[tag]
			if tuple[0] == -1:
				pyLabel.text = "%i"%tuple[1]
			else:
				pyLabel.text = "%i/%i"%( tuple[0], tuple[1] )

	def clearItems( self ):
		for pyLabel in self.__pyLabels.itervalues():
			pyLabel.text = ""

# ----------------------------------------------------------
class BaseAttrPanel( PyGUI ):
	def __init__( self, panel = None ):
		PyGUI.__init__( self, panel )
		self.__initPanel( panel )
		self.__dbid = -1

	def __initPanel( self, panel ):
		self.__pyItems = {}
		for name, item in panel.children:
			if "_item" not in name :continue
			tag = name.split( "_" )[0]
			pyItem = PropertyItem( tag, item )
			self.__pyItems[tag] = pyItem

	def updateInfo( self, tag, dbid, tuple ):
		self.__dbid = dbid
		if self.__pyItems.has_key( tag ):
			pyItem = self.__pyItems[tag]
			pyItem.update( tuple )

	def clearItems( self ):
		for pyItem in self.__pyItems.itervalues():
			pyItem.update( (0,0) )
