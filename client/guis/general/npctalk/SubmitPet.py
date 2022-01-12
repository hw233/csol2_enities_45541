# -*- coding: gb18030 -*-
#
# $Id: SubmitPet.py,v 1.2 2008-09-01 09:04:26 fangpengjun Exp $

from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.controls.StaticText import StaticText
from guis.controls.Button import Button
from guis.controls.ListPanel import ListPanel
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font

class SubmitPet( PyGUI ):
	def __init__( self, panel ):
		PyGUI.__init__( self, panel )
		self.visible = True
		self.__pyMyPets = ListPanel( panel.myPetsPanel.clipPanel, panel.myPetsPanel.sbar )
		self.__pyMyPets.autoSelect = False
		self.__pyMyPets.rMouseSelect = True
		self.__pyMyPets.onItemLClick.bind( self.__onMyPetLClick )
		self.__pyMyPets.onItemRClick.bind( self.__onMyPetRClick )

		self.__pyQuestPets = ListPanel( panel.questPetsPanel.clipPanel, panel.questPetsPanel.sbar )
		self.__pyQuestPets.autoSelect = False
		self.__pyQuestPets.rMouseSelect = True
		self.__pyQuestPets.onItemLClick.bind( self.__onQuestPetLClick )
		self.__pyQuestPets.onItemRClick.bind( self.__onQuestPetRClick )

		self.__pyBtnTransfer = Button( panel.btnTransfer )
		self.__pyBtnTransfer.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnTransfer.enable = False
		self.__pyBtnTransfer.onLClick.bind( self.__onTransferPet )
		labelGather.setPyBgLabel( self.__pyBtnTransfer, "NPCTalkWnd:submit", "btnTransfer" )

		self.__pyRTObject = CSRichText( panel.objectText )
		self.__pyRTObject.opGBLink = True
		self.__pyRTObject.align = "R"
		self.__pyRTObject.text = ""

		labelGather.setLabel( panel.lbNeedPet, "NPCTalkWnd:submit", "needPet" )
		labelGather.setLabel( panel.myPetsPanel.stTitle, "NPCTalkWnd:submit", "curPets" )
		labelGather.setLabel( panel.questPetsPanel.stTitle, "NPCTalkWnd:submit", "questPets" )
		self.__subpets = [] #提交宠物列表
	# ------------------------------------------------
	# private
	# ------------------------------------------------
	def __onMyPetLClick( self, pySelPet ):
		self.__pyBtnTransfer.enable = pySelPet is not None
		for pyPet in self.__pyMyPets.pyItems:
			pyPet.lighted = not pyPet.petID != pySelPet.petID

	def __onQuestPetLClick( self, pySelPet ):
		self.__pyBtnTransfer.enable = pySelPet is not None
		for pyPet in self.__pyQuestPets.pyItems:
			pyPet.lighted = not pyPet.petID != pySelPet.petID

	def __onMyPetRClick( self, pyPet ):
		if pyPet is None: return
		if pyPet in self.__pyMyPets.pyItems \
		and pyPet not in self.__pyQuestPets.pyItems:
			self.__pyMyPets.removeItem( pyPet )
			self.__pyQuestPets.addItem( pyPet )
			pyPet.lighted = False
			self.__subpets.append( pyPet.petID )

	def __onQuestPetRClick( self, pyPet ):
		if pyPet is None: return
		if pyPet in self.__pyQuestPets.pyItems \
		and pyPet not in self.__pyMyPets.pyItems:
			self.__pyQuestPets.removeItem( pyPet )
			self.__pyMyPets.addItem( pyPet )
			pyPet.lighted = False
			self.__subpets.remove( pyPet.petID )

	def __onTransferPet( self ):
		myPyPet = self.__pyMyPets.pySelItem
		questPyPet = self.__pyQuestPets.pySelItem
		if myPyPet is not None:
			self.__pyMyPets.removeItem( myPyPet )
			self.__pyQuestPets.addItem( myPyPet )
			myPyPet.lighted = False
			self.__subpets.append( myPyPet.petID )
		if questPyPet is not None:
			self.__pyQuestPets.removeItem( questPyPet )
			self.__pyMyPets.addItem( questPyPet )
			questPyPet.lighted = False
			self.__subpets.remove( questPyPet.petID )

	def initMyPets( self ):
		player = BigWorld.player()
		Epitomes = player.pcg_getPetEpitomes()
		for bdid, petEpitome in Epitomes.iteritems():
			if petEpitome.conjured:continue
			petItem = GUI.load( "guis/general/npctalk/petitem.gui" )
			uiFixer.firstLoadFix( petItem )
			pyPetItem = PetItem( petItem, self )
			pyPetItem.petID = bdid
			pyPetItem.setPetInfo( petEpitome )
			self.__pyMyPets.addItem( pyPetItem )

	def setAimText( self, aimItems ):
		isComplete = aimItems[-1]
		condition = "%s: %s " % ( aimItems[1], aimItems[2] )
		text = ""
		if isComplete:
			text = PL_Font.getSource( condition, fc = ( 255, 255, 255, 255 ) )
		else:
			text = PL_Font.getSource( condition, fc = ( 127, 127, 127, 255 ) )
		self.__pyRTObject.text = text

	def getSubPets( self ):
		return self.__subpets

# ------------------------------------------------------------
# PetItem
# ------------------------------------------------------------
from guis.controls.ListItem import ListItem
from NPCModelLoader import NPCModelLoader
g_npcmodel = NPCModelLoader.instance()

class PetItem( ListItem ):
	def __init__( self, petItem, pyBinder = None ):
		ListItem.__init__( self, petItem, pyBinder )
		self.__pyPetHead = PyGUI( petItem.petHead )
		self.__pyPetHead.texture = ""

		self.__pyStName = StaticText( petItem.stName )
		self.__pyStName.text = ""

		self.__pyStLevel = StaticText( petItem.stLevel )
		self.__pyStLevel.text = ""

		self.__pyLightCircle = PyGUI( petItem.lightCircle )
		self.__pyLightCircle.visible = False

		self.__petID = -1

	def __lighted( self ):
		self.__pyLightCircle.visible = True

	def __disLighted( self ):
		self.__pyLightCircle.visible = False

	def onMouseEnter_( self ):
		ListItem.onMouseEnter_( self )
		self.__pyLightCircle.visible = True
		return True

	def onMouseLeave_( self ):
		ListItem.onMouseLeave_( self )
		if self.selected:
			return
		else:
			self.__pyLightCircle.visible = False
		return True

	def setPetInfo( self, petEpitome ):
		if petEpitome is None :return
		modelNumber =petEpitome.modelNumber
		self.__pyPetHead.texture = g_npcmodel.getHeadTexture( modelNumber )
		self.__pyStName.text = petEpitome.name
		self.__pyStLevel.text = labelGather.getText( "NPCTalkWnd:submit", "petLevel" )%petEpitome.level

	def _getLighted( self ):
		return self.__pyLightCircle.rvisible

	def _setLighted( self, lighted ):
		if lighted:
			self.__lighted()
		else:
			self.__disLighted()
		self.selected = lighted

	def _getPetID( self ):
		return self.__petID

	def _setPetID( self, petID ):
		self.__petID = str( petID )

	lighted = property( _getLighted, _setLighted )
	petID = property( _getPetID, _setPetID )
