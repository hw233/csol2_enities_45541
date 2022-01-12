# -*- coding: gb18030 -*-
#
# $Id: PetCombine.py,v 1.9 2008-07-21 02:58:43 huangyongwei Exp $

"""
implement petcombine
"""
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ListPanel import ListPanel
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.controls.Button import Button
import event.EventCenter as ECenter
from PetFormulas import formulas
import csdefine

# ----------------------------------------------------------------
# 调整属性字体尺寸修饰器
# ----------------------------------------------------------------
from AbstractTemplates import MultiLngFuncDecorator

class deco_PCBResizePropertyItems( MultiLngFuncDecorator ) :

	@staticmethod
	def locale_big5( SELF ) :
		"""
		繁体版下重新调整部分属性字体的尺寸
		"""
		SELF._PetCombine__pyLbSpirit.fontSize = 10
		SELF._PetCombine__pyLbSpirit.charSpace = -1

		SELF._PetCombine__pyLbNature.fontSize = 10
		SELF._PetCombine__pyLbNature.charSpace = -1


class PetCombine( Window ):
	__guiSource=ResMgr.openSection("guis/general/petswindow/petpanel/petitem.gui")
	def __init__( self, pyBinder = None ):
		wnd = GUI.load( "guis/general/petswindow/petpanel/petcombine.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )

		self.__pyPetItems = {}
		self.__CombinePet = None # 主战宠物
		self.__triggers = {}
		self.__registerTriggers()
		#self.combineDsp =
		self.__initialize( wnd )
		self.addToMgr( "petCombineWindow" )
		self.__resizePropertyItems()

	def __initialize( self, wnd ):
		labelGather.setLabel( wnd.lbTitle, "PetsWindow:PetCombine", "lbTitle" )
		labelGather.setLabel( wnd.adultPets, "PetsWindow:PetCombine", "adultPets" )
		labelGather.setLabel( wnd.comPetText, "PetsWindow:PetCombine", "comPetText" )
		labelGather.setLabel( wnd.nameBar.lbText, "PetsWindow:PetCombine", "nameText" )
		labelGather.setLabel( wnd.abilityBar.lbText, "PetsWindow:PetCombine", "abilityText" )
		labelGather.setLabel( wnd.petPanel.spiritText, "PetsWindow:PetCombine", "spiritText" )
		labelGather.setLabel( wnd.petPanel.natureText, "PetsWindow:PetCombine", "natureText" )
		self.__pyRtInfo = CSRichText( wnd.rtInfo )
		self.__pyRtInfo.text = ""

		self.__pyBtnCombine = Button( wnd.btnCombine )
		self.__pyBtnCombine.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCombine.onLClick.bind( self.__onCombinePet )
		self.__pyBtnCombine.enable = False
		labelGather.setPyBgLabel( self.__pyBtnCombine, "PetsWindow:PetCombine", "btnCombine" )

		self.__pyBtnCancel = Button( wnd.btnCancel )
		self.__pyBtnCancel.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCancel.onLClick.bind( self.__onCancel )
		labelGather.setPyBgLabel( self.__pyBtnCancel, "PetsWindow:PetCombine", "btnCancel" )

		self.__pyPetsPanel = ListPanel( wnd.petsPanel.clipPanel, wnd.petsPanel.sbar )
		self.__pyPetsPanel.onItemSelectChanged.bind( self.__onPetSelectedChanged )
		self.__pyPetsPanel.autoSelect = False

		self.__pyRtName = CSRichText( wnd.petPanel.rtName )
		self.__pyRtName.text = ""

		self.__pySpiritText = StaticText( wnd.petPanel.spiritText )
		self.__pySpiritText.visible = False

		self.__pyNatureText = StaticText( wnd.petPanel.natureText )
		self.__pyNatureText.visible = False

		self.__pyLbSpirit = StaticText( wnd.petPanel.lbSpirit )
		self.__pyLbSpirit.text = ""

		self.__pyLbNature = StaticText( wnd.petPanel.lbNature )
		self.__pyLbNature.text = ""

	@deco_PCBResizePropertyItems
	def __resizePropertyItems( self ) :
		"""
		重新调整部分属性字体的尺寸
		默认版本下不进行任何操作
		"""
		pass

	#------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_PCG_SHOW_COMBINE"]	= self.__onShow
		self.__triggers["EVT_ON_PCG_REMOVE_PET"] = self.__onRemovePet
		self.__triggers["EVT_ON_PCG_ADD_PET"]	= self.__onAddPet
		self.__triggers["EVT_ON_PET_ATTR_CHANGED"]	 = self.__onAttrUpdate
		self.__triggers["EVT_ON_PCG_HIDE_COMBINE"]	= self.hide
		for trigger in self.__triggers :
			ECenter.registerEvent( trigger, self )

	def __deregisterTriggers( self ) :
		"""
		deregister all events
		"""
		for key in self.__triggers.iterkeys():
			ECenter.registerEvent( key, self )
	# --------------------------------------------------------
	def __onShow( self, outPet, pets ):
		self.__pyPetsPanel.clearItems()
		player = BigWorld.player()
		if outPet is None:
			self.__clearUIs( )
		else:
			self.__CombinePet = outPet
			hierarchy = outPet.hierarchy #宠物辈分
			if formulas.isHierarchy( hierarchy, csdefine.PET_HIERARCHY_GROWNUP ): #成年宠物
				hierColor = ( 255, 255, 255, 255 )
			elif formulas.isHierarchy( hierarchy, csdefine.PET_HIERARCHY_INFANCY1 ): #一代宝宝
				hierColor = ( 0, 0, 255, 255 )
			else: #二代宝宝
				hierColor = ( 254, 163, 8, 255 )
			self.__pyRtName.text = PL_Font.getSource( outPet.name, fc = hierColor )
			self.__pyLbSpirit.text = "%d/%d"%( outPet.nimbus, outPet.nimbusMax )
			self.__pyLbNature.text = "%d/%d"%( outPet.calcaneus, outPet.calcaneusMax )
			self.__pySpiritText.visible = True
			self.__pyNatureText.visible = True
			for pet in pets:
				petItem = GUI.load(PetCombine.__guiSource)
				uiFixer.firstLoadFix( petItem )
				pyPetItem = PetItem( petItem, pet )
				pyPetItem.resetPet( pet )
				dbid = pet.databaseID
				pyPetItem.petID = dbid
				pyPetItem.ability = pet.ability
				self.__pyPetItems[dbid] = pyPetItem
				self.__pyPetsPanel.addItem( pyPetItem )

	def __onRemovePet( self, bdid ): # 放生一个宠物
		player = BigWorld.player()
		if self.__CombinePet is None:return
		if bdid == self.__CombinePet.databaseID:
			self.__clearUIs()
			self.__pyPetsPanel.clearItems()
		else:
			if self.__pyPetItems.has_key( bdid ):
				pyItem = self.__pyPetItems[bdid]
				self.__pyPetsPanel.removeItem( pyItem )

	def __onAddPet( self, petEpitome ):
		if petEpitome is None:return
		player = BigWorld.player()
		outPet = player.pcg_getActPet()
		addPet = petEpitome.getEntity()
		if addPet is None or outPet is None :return
		if petEpitome.databaseID == outPet.databaseID \
		or self.__pyPetItems.has_key( petEpitome.databaseID ):
			return
		if addPet.level >= outPet.level - 5 :
			petItem = GUI.load(PetCombine.__guiSource)
			uiFixer.firstLoadFix( petItem )
			pyPetItem = PetItem( petItem, addPet )
			pyPetItem.petID = addPet.databaseID
			pyPetItem.resetPet( addPet )
			self.__pyPetItems[petEpitome.databaseID] = pyPetItem
			self.__pyPetsPanel.addItem( pyPetItem )

	def __onAttrUpdate( self, dbid, attr ):
		outPetEpitome = BigWorld.player().pcg_getActPetEpitome()
		if outPetEpitome is None:return
		if dbid == outPetEpitome.databaseID:
			if attr in ["nimbus", "nimbusMax"] :
				self.__pyLbSpirit.text = "%d/%d"%( outPetEpitome.nimbus, outPetEpitome.nimbusMax )
			elif attr == "calcaneus":
				self.__pyLbNature.text = "%d/%d"%( outPetEpitome.calcaneus, outPetEpitome.calcaneusMax )

	def __clearUIs( self ):
		self.__pyRtName.text = ""
		self.__pySpiritText.visible = False
		self.__pyNatureText.visible = False
		self.__pyLbSpirit.text = ""
		self.__pyLbNature.text = ""

	def __onPetSelectedChanged( self, pyItem ):
		self.__pyBtnCombine.enable = pyItem is not None

	def __onCombinePet( self ):
		selPetItem = self.__pyPetsPanel.pySelItem
		if selPetItem is None:
			# "必须选择一个材料宠物！"
			showMessage( 0x04c1, "", MB_OK )
			return
		BigWorld.player().pcg_combinePet( selPetItem.petID )

	def __onCancel( self ):
		self.hide()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventName, *args ) :
		self.__triggers[eventName]( *args )

	def onShow( self, outPet, pets, pyOwner ):
		self.__onShow( outPet, pets )
		if self.__pyRtInfo.text== "":
			self.__pyRtInfo.text = labelGather.getText( "PetsWindow:PetCombine", "explain" )
		Window.show( self, pyOwner )

	def hide( self ):
		Window.hide( self )

# --------------------------------------------------------
# PetItem
# --------------------------------------------------------
from guis.controls.ListItem import MultiColListItem

class PetItem( MultiColListItem ):
	def __init__( self, item, pet ):
		MultiColListItem.__init__( self, item )
		self.__pet = None
		self.__petID = -1
		self.highlightForeColor = ( 255, 255, 255, 255 )
		self.commonBackColor = ( 255, 255, 255, 0 )
		self.selectedBackColor = ( 118, 111, 67, 0 )
		self.highlightBackColor = ( 118, 111, 67, 0 )
		self.resetPet( pet )

	def resetPet( self, pet  ):
		self.__pet = pet
		name = pet.name
		ability = pet.ability
		hierarchy = pet.hierarchy #宠物辈分
		hierColor = ( 200, 200, 200, 200 )
		if formulas.isHierarchy( hierarchy, csdefine.PET_HIERARCHY_GROWNUP ): #成年宠物
			hierColor = ( 255, 255, 255, 255 )
		elif formulas.isHierarchy( hierarchy, csdefine.PET_HIERARCHY_INFANCY1 ): #一代宝宝
			hierColor = ( 0, 0, 255, 255 )
		else: #二代宝宝
			hierColor = ( 254, 163, 8, 255 )
		self.pyCols[0].commonForeColor = hierColor
		self.pyCols[0].highlightForeColor = hierColor
		self.pyCols[0].selectedForeColor = hierColor
		self.setTextes( name, ability )
		

	def _getPetID( self ):
		return self.__petID

	def _setPetID( self, petID ):
		self.__petID = petID

	petID = property( _getPetID, _setPetID )