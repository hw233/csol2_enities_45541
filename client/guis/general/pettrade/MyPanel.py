# -*- coding: gb18030 -*-
#
# $Id: MyPanel.py,v 1.4 2008-08-13 07:44:59 fangpengjun Exp $

"""
implement MyPanel
"""

from guis import *
from PropertyPanel import PropertyPanel
import GUIFacade
import csdefine
from bwdebug import *

class MyPanel( PropertyPanel ):
	def __init__( self, panel = None, pyBinder = None ):
		PropertyPanel.__init__( self, panel, pyBinder )
		self.pyPetsCB_.onItemSelectChanged.bind( self.onPetSelected_ )
		self.pyFrontBtn_.onLClick.bind( self.__onSelectFront )
		self.pyNextBtn_.onLClick.bind( self.__onSelectNext )
		self.__petItems = {}
		self.__triggers = {}
		self.__registerTriggers()

	def subclass( self, panel, pyBinder ):
		PropertyPanel.subclass( self, panel, pyBinder )
		return self

	def __onSelectFront( self ):
		if self.pyPetsCB_.itemCount < 1:return
		selIndex = self.pyPetsCB_.selIndex
		foreIndex = selIndex - 1
		if foreIndex < 0 : return
		foreItem = self.pyPetsCB_.pyItems[foreIndex]
		self.pyPetsCB_.pySelItem = foreItem
#		dbid = foreItem.epitome.databaseID
#		BigWorld.player().si_changePet( dbid )
		#self.onPetSelected_( foreItem )

	def __registerTriggers( self ):
		"""
		"""
		self.__triggers["EVT_ON_PCG_ADD_PET"]		 	= self.__onPetAdded
		self.__triggers["EVT_ON_PCG_REMOVE_PET"]		= self.__onPetRemoved
		self.__triggers["EVT_ON_PET_CONJURED"]		= self.__onPetConjured
		self.__triggers["EVT_ON_PET_WITHDRAWED"]	= self.__onPetWithdraw
		for key in self.__triggers:
			GUIFacade.registerEvent( key, self )

	def __unregisterTriggers( self ):
		"""
		"""
		for key in self.__triggers:
			GUIFacade.unregisterEvent( key, self )

	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def __onPetAdded( self, petEpitome ):
		"""
		"""
		pyItem = PetItem()
		pyItem.petName = petEpitome.name
		pyItem.epitome = petEpitome
		pyItem.petID = petEpitome.databaseID
		self.__petItems[pyItem.petID] = pyItem
		self.pyPetsCB_.addItem( pyItem )

	def __onPetRemoved( self, petDBID ):
		"""
		"""
		for item in self.pyPetsCB_.pyItems:
			if item.petID == petDBID:
				self.pyPetsCB_.removeItem( item )
				if item.petName == self.pyPetsCB_.text:
					self.onResumePanels()
				break

	def __onPetConjured( self, petDBID ):
		"""
		"""
		for item in self.pyPetsCB_.pyItems:
			if item.petID == petDBID:
				self.pyPetsCB_.removeItem( item )
				if item.petName == self.pyPetsCB_.text:
					self.onResumePanels()
				break

	def __onPetWithdraw( self, petDBID ):
		"""
		"""
		petEpitome = BigWorld.player().pcg_getPetEpitome( petDBID )
		pyItem = PetItem()
		pyItem.petName = petEpitome.name
		pyItem.epitome = petEpitome
		pyItem.petID = petDBID
		self.__petItems[petDBID] = pyItem
		self.pyPetsCB_.addItem( pyItem )

	def __onSelectNext( self ):
		if self.pyPetsCB_.itemCount < 1:return
		selIndex = self.pyPetsCB_.selIndex
		nextIndex = selIndex + 1
		if nextIndex > self.pyPetsCB_.itemCount - 1:return
		nextItem = self.pyPetsCB_.pyItems[nextIndex]
		self.pyPetsCB_.pySelItem = nextItem
#		dbid = foreItem.nextItem.databaseID
#		BigWorld.player().si_changePet( dbid )
		#self.onPetSelected_( nextItem )

	def __enableSelectButton( self ) :
		petCount = self.pyPetsCB_.itemCount
		currIndex = self.pyPetsCB_.selIndex
		self.pyNextBtn_.enable = currIndex < petCount - 1
		self.pyFrontBtn_.enable = currIndex > 0

	def onPetSelected_( self, pyItem ):
		self.__enableSelectButton()
		PropertyPanel.onPetSelected_( self, pyItem )
		if pyItem is None:return
		dbid = pyItem.epitome.databaseID
		BigWorld.player().si_changePet( dbid )

	def onPetChange( self, dbid ):
		if self.__petItems.has_key( dbid ):
			petItem = self.__petItems[dbid]
			self.pyPetsCB_.pySelItem = petItem
			#self.onPetSelected_( petItem )

	def onResumePanels( self ):
		PropertyPanel.resumePanels_( self )
		if self.pyPetsCB_.isDropDown:
			self.pyPetsCB_.cancelDrop()

	def setState( self, state ):
		self.pyPetsCB_.enable = ( state != csdefine.TRADE_SWAP_SURE )
		self.pyFrontBtn_.enable = ( state != csdefine.TRADE_SWAP_SURE )
		self.pyNextBtn_.enable = ( state != csdefine.TRADE_SWAP_SURE )

	def initPetsCB( self ):
		player = BigWorld.player()
		self.pyPetsCB_.clearItems()
		petEpitomes = player.pcg_getPetEpitomes()
		outPetEpitome = player.pcg_getActPetEpitome()
		for dbid, petEpitome in petEpitomes.iteritems():
			if not petEpitome.conjured and not petEpitome.isBinded:
				pyItem = PetItem()
				pyItem.petName = petEpitome.name
				pyItem.epitome = petEpitome
				pyItem.petID = dbid
				pyItem.anchor = 'CENTER'
				pyItem.foreColor = (252,235,179)
				self.__petItems[dbid] = pyItem
				self.pyPetsCB_.addItem( pyItem )
#		if not outPetEpitome is None:
#			bdid = outPetEpitome.databaseID
#			pyItem = self.__petItems[bdid]
#			self.pyPetsCB_.pySelItem = pyItem
#			self.onPetSelected_( pyItem )

# ------------------------------------------------------
from guis.controls.ComboBox import ComboItem
from guis.controls.StaticText import StaticText
from guis.common.PyGUI import PyGUI
class PetItem( ComboItem ):
	__cg_item = None

	def __init__( self ) :
		if PetItem.__cg_item is None :
			PetItem.__cg_item = GUI.load( "guis/general/petswindow/petitem.gui" )

		item = util.copyGuiTree( PetItem.__cg_item  )
		uiFixer.firstLoadFix( item )
		ComboItem.__init__( self,item.lbText.text, item )
#		ComboItem.__init__( self, item )
		self.__petID = -1
		self.__initialize( item )

	def __initialize( self, item ) :
#		self.__pyLbID = StaticText( item.lbID )
#		self.__pyLbName = StaticText( item.lbText )
		self.__pyMark = PyGUI( item.outMark )
		self.__pyMark.visible = False

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getMarkVisible( self ) :
		return self.__pyMark.visible

	def _setMarkVisible( self, visible ) :
		self.__pyMark.visible = visible

	# -------------------------------------------------
	def _getPetID( self ) :
		return self.__petID

	def _setPetID( self, id ) :
		self.__petID = id

	# ---------------------------------------
	def _getPetName( self ) :
		return self.text

	def _setPetName( self, name ) :
		self.text = name

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	petID = property( _getPetID, _setPetID )
	petName = property( _getPetName, _setPetName )
	markVisible = property( _getMarkVisible, _setMarkVisible )