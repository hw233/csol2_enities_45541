# -*- coding: gb18030 -*-
#
# $Id: PetItem.py,v 1.3 2008-06-27 03:18:06 huangyongwei Exp $

"""
implement ware item
"""
from guis import *
from LabelGather import labelGather
from guis.controls.Control import Control
from guis.common.PyGUI import PyGUI	# wsf
from guis.controls.StaticText import StaticText
from NPCModelLoader import NPCModelLoader
g_npcmodel = NPCModelLoader.instance()
import GUIFacade
import csdefine
import Const
from AbstractTemplates import MultiLngFuncDecorator

class deco_InitPetName( MultiLngFuncDecorator ) :

	@staticmethod
	def locale_big5( SELF, pyPetName ) :
		"""
		繁体版下重新调整部分属性字体的尺寸
		"""
		pyPetName.charSpace = -1.0
		pyPetName.fontSize = 11

class PetItem( Control ):

	_pet_types = {
		csdefine.PET_TYPE_STRENGTH:	labelGather.getText( "PetsWindow:PetsPanel", "type_strength" ),
		csdefine.PET_TYPE_BALANCED:	labelGather.getText( "PetsWindow:PetsPanel", "type_blanced" ),
		csdefine.PET_TYPE_SMART:	labelGather.getText( "PetsWindow:PetsPanel", "type_smart" ),
		csdefine.PET_TYPE_INTELLECT: labelGather.getText( "PetsWindow:PetsPanel", "type_intellect" )
		}
		
	def __init__( self, dragMark = 0, pyBinder = None ):
		item = GUI.load( "guis/general/petswindow/aboutnpc/petinfo.gui" )
		uiFixer.firstLoadFix( item )
		Control.__init__( self, item, pyBinder )
		self.crossFocus = True
		self.dragFocus = False
		self.focus = False
		self.__pyPanel = PyGUI( item.infoPanel )
		self.__pyHead = PyGUI( item.petHead )
		self.__pyLbName = StaticText( item.infoPanel.lbName )
		self.__pyLbName.text = ""
		self.__initPetName( self.__pyLbName )
		self.__pyLbInfo = StaticText( item.infoPanel.lbInfo )
		self.__pyLbInfo.text = ""
		self.__dbid = -1
		self.__panelState = ''
		self.__petHeadState = ''
		self.__selected = False
		self.__state = ''
		self.dragMark = dragMark

	@deco_InitPetName
	def __initPetName( self, pyPetName ):
		charSpace = 0.0
		fontSize = 13
		if pyPetName.font == "MSYHBD.TTF":
			charSpace = -1.0
			fontSize = 12
		pyPetName.charSpace = charSpace
		pyPetName.fontSize = fontSize

	def __seekHeadTexture( self, species, modelNumber ):
		"""
		根据宠物的类型和模型编号获取头像贴图
		"""
		hierarchy = species & csdefine.PET_HIERARCHY_MASK
		if hierarchy == csdefine.PET_HIERARCHY_INFANCY2 and \
		self.dragMark != DragMark.MY_PET_PANEL:
			modelNumber += Const.PET_ATTACH_MODELNUM
		return g_npcmodel.getHeadTexture( modelNumber )
			
	def updateInfo( self, pet ):
		if pet.dbid != '':			# 更新宠物的信息 			
			self.__dbid = pet.dbid
			self.__pyHead.gui.PetHead.textureName = self.__seekHeadTexture( pet.species, pet.modelNumber )
			self.__pyLbName.text = pet.name
			type = pet.species&csdefine.PET_TYPE_MASK
			if self._pet_types.has_key( type ):
					typeStr = self._pet_types[type]
			else:
				typeStr = labelGather.getText( "PetsWindow:PetStorage", "typeStr" )
			self.__pyLbInfo.text = labelGather.getText( "PetsWindow:PetStorage", "petInfo" )%( pet.level, typeStr )
			self.state = pet.itemState
		
		else:
			self.state = pet.itemState
			self.__dbid = -1
			self.__pyHead.gui.PetHead.textureName = ""
			self.__pyLbName.text = ""
			self.__pyLbInfo.text = ""
	
	def _getPanelState( self ):
		return self.__panelState

	def _setPanelState( self, state ):
		self.__panelState = state
		elements = self.__pyPanel.getGui().elements
		for ename, element in elements.items():
			element.mapping = util.getStateMapping( element.size, UIState.MODE_R3C1, state )
			if ename in ["panelState"]:
				element.mapping = util.hflipMapping( element.mapping )
				
	def _getPetHeadState( self ):
		return self.__petHeadState
				
	def _setPetHeadState( self, state ):
		self.__petHeadState = state
		petHead = self.__pyHead.getGui()
		util.setGuiState( petHead,UIState.MODE_R3C1, state )

	def _getSelected( self ):
		return self.__selected

	def _setSelected( self, selected ):
		if self.__state == 'normal':
			if selected:
				self.panelState = ( 3, 1 )
			else:
				self.panelState = ( 2, 1 )
			self.__selected = selected
		else: 
			pass
			
	def _getState( self ):
		return self.__state
		
	def _setState(self,state ):
		if state == 'normal':
			self.petHeadState = ( 2, 1 )
			self.panelState = ( 2, 1 )
		elif state == 'setUp':
			self.petHeadState = ( 3, 1 )
			self.panelState = ( 2, 1 )
		else:
			self.petHeadState = ( 1, 1 )
			self.panelState = ( 1, 1 )
			
		self.__state = state	

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	panelState = property( _getPanelState, _setPanelState )
	petHeadState = property( _getPetHeadState, _setPetHeadState)
	selected = property( _getSelected, _setSelected )
	state = property( _getState, _setState )

