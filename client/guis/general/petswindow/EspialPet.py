# -*- coding: gb18030 -*-
#
# $Id: EspialWindow.py Exp $

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.common.PyGUI import PyGUI
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.controls.ODComboBox import ODComboBox
import skills as Skill
from ItemsFactory import PetSkillItem as SkillItemInfo
from guis.general.petswindow.petpanel.PetModelRender import PetModelRender
from guis.general.petswindow.petpanel.AttributeItem import PropertyItem
from guis.general.petswindow.petpanel.AttributeItem import ResistItem
from guis.general.petswindow.petpanel.AttributeItem import EnhanceItem
from guis.general.petswindow.petpanel.SkillItem import SkillItem
import GUIFacade
import csdefine
import csconst
import csstatus
import math
import Const

class EspialPet( Window ):

	__baseAttrs = {} #��������
	__baseAttrs["name"]			= "uname" 							# ����
	__baseAttrs["gender"] 		= "gender" 							# �Ա�
	__baseAttrs["species"]		= "species" 						# ����
	__baseAttrs["level"]		= "level" 							# �ȼ�
	__baseAttrs["ability"]		= "ability" 						# �ɳ���

	__proAttrs = {} # ��������
	__proAttrs["hp"]			= ( "HP", "HPMax" ) 				# ����
	__proAttrs["mp"]			= ( "MP", "MPMax" )					# ����
	__proAttrs["exp"]			= ( "EXP","EXPMax" ) 				# ����
	__proAttrs["nimbus"]		= ( "nimbus", "nimbusMax" ) 		# ����
	__proAttrs["calcaneus"]		= ( "calcaneus", "calcaneusMax" ) 	# ����
	__proAttrs["joyancy"]		= ( "joyancy", "joyancyMax" ) 	# ���ֶ�
	__proAttrs["life"]		= ( "life", "lifeMax" ) 				# ����

	__enhanceAttrs = {} # ��ǿ������
	__enhanceAttrs["habitus"]		= ( "corporeity", "ec_corporeity" )	#����
	__enhanceAttrs["force"]			= ( "strength",  "ec_strength" )	#����
	__enhanceAttrs["intellect"]		= ( "intellect" , "ec_intellect" )	#����
	__enhanceAttrs["agility"]		= ( "dexterity", "ec_dexterity" )  #����
	__enhanceAttrs["freedom"]		= ( "", "ec_free" ) #���ɼӵ�

	__extrAttrs = {} #��������
	__extrAttrs["character"]	= "character"
	__extrAttrs["isBreed"]		= "procreated"
	__extrAttrs["type"]			= "ptype"
	__extrAttrs["takeLevel"]	= "takeLevel"

	__phCombatAttrs = {} # ����ս������
	__phCombatAttrs["damage"] 		= "damage" # ƽ��������
	__phCombatAttrs["recovery"] 	= "armor"	# �������
	__phCombatAttrs["duck"] 		= "dodge_probability" # ����
	__phCombatAttrs["cruel"]		= "double_hit_probability"# ������
	__phCombatAttrs["blows"]		= "resist_hit_probability" # �м�

	__magCombatAttrs = {} # ����ս������
	__magCombatAttrs["damage"]		= "magic_damage" # ��������
	__magCombatAttrs["recovery"]	= "magic_armor" # ��������
	__magCombatAttrs["duck"]		= "dodge_probability" # ����
	__magCombatAttrs["cruel"]		= "magic_double_hit_probability" # ��������

	__resistAttrs = {} # ��������
	__resistAttrs["fix"]		= "resist_fix_probability"
	__resistAttrs["giddy"]		= "resist_giddy_probability"
	__resistAttrs["sleep"]		= "resist_sleep_probability"
	__resistAttrs["hush"]		= "resist_chenmo_probability"

	__extrTexture = { "type":
			{csdefine.PET_TYPE_STRENGTH:	labelGather.getText( "PetsWindow:PetsPanel", "type_strength" ),
			csdefine.PET_TYPE_BALANCED:	labelGather.getText( "PetsWindow:PetsPanel", "type_blanced" ),
			csdefine.PET_TYPE_SMART:	labelGather.getText( "PetsWindow:PetsPanel", "type_smart" ),
			csdefine.PET_TYPE_INTELLECT:	labelGather.getText( "PetsWindow:PetsPanel", "type_intellect" )
			},
			"isBreed":
				{csdefine.PET_PROCREATE_STATUS_NONE:	labelGather.getText( "PetsWindow:PetsPanel", "status_none" ),
				csdefine.PET_PROCREATE_STATUS_PROCREATING:	labelGather.getText( "PetsWindow:PetsPanel", "status_procreating" ),
				csdefine.PET_PROCREATE_STATUS_PROCREATED:	labelGather.getText( "PetsWindow:PetsPanel", "status_procreated" )
				},
			"character":
				{ csdefine.PET_CHARACTER_SUREFOOTED:	labelGather.getText( "PetsWindow:PetsPanel", "character_surefooted" ),
				csdefine.PET_CHARACTER_CLOVER:	labelGather.getText( "PetsWindow:PetsPanel", "character_clover" ),
				csdefine.PET_CHARACTER_CANNILY:	labelGather.getText( "PetsWindow:PetsPanel", "character_cannily" ),
				csdefine.PET_CHARACTER_BRAVE:	labelGather.getText( "PetsWindow:PetsPanel", "character_brave" ),
				csdefine.PET_CHARACTER_LIVELY:	labelGather.getText( "PetsWindow:PetsPanel", "character_lively" )
				}
			}

	_pet_hierarchy = { csdefine.PET_HIERARCHY_GROWNUP : ( labelGather.getText( "PetsWindow:PetsPanel", "hierarchy_grownup" ), ( 255, 255, 255, 255 ) ),
					   csdefine.PET_HIERARCHY_INFANCY1 : ( labelGather.getText( "PetsWindow:PetsPanel", "hierarchy_infancy1" ), ( 0, 128, 255, 255 ) ),
					   csdefine.PET_HIERARCHY_INFANCY2 : ( labelGather.getText( "PetsWindow:PetsPanel", "hierarchy_infancy2" ), ( 254, 163, 8, 255 ) ),
					   }

	def __init__( self ):
		wnd = GUI.load( "guis/general/petswindow/espwindow.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True

		self.__triggers = {}
		self.__registerTriggers()
		self.__turnModelCBID = 0
		self.__trapID = 0
		self.espialPet = None
		self.__initialize( wnd )

	def __initialize( self, wnd ):
		labelGather.setLabel( wnd.lbTitle, "PetsWindow:PetEspial", "lbTitle" )
		self.__pyCBPets = ODComboBox( wnd.cbPets )					#���������б�
		self.__pyCBPets.autoSelect = True
		self.__pyCBPets.enable = False

		self.__pyPetRender = PetModelRender( wnd.petRender ) 		#����ģ��

		self.__pyBtnLeft = Button( wnd.btnLeft )					#ģ��������ת��ť
		self.__pyBtnLeft.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnLeft.onLMouseDown.bind( self.__turnLeft )

		self.__pyBtnRight = Button( wnd.btnRight )				#ģ������ת��ť
		self.__pyBtnRight.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnRight.onLMouseDown.bind( self.__turnRight )

		self.__pyBtnChangName = Button( wnd.btnRename )				#�������
		self.__pyBtnChangName.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnChangName.enable = False
		labelGather.setPyBgLabel( self.__pyBtnChangName, "PetsWindow:PetsPanel", "renameBtn" )

		self.__pyBtnFeed = Button( wnd.btnFeed )
		self.__pyBtnFeed.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnFeed.enable = False
		labelGather.setPyBgLabel( self.__pyBtnFeed, "PetsWindow:PetsPanel", "btnFeed" )

		self.__pyBtnDome = Button( wnd.btnDome )
		self.__pyBtnDome.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnDome.enable = False
		labelGather.setPyBgLabel( self.__pyBtnDome, "PetsWindow:PetsPanel", "btnDome" )

		self.__pyBtnRestore = Button( wnd.btnRestore )
		self.__pyBtnRestore.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnRestore.enable = False
		labelGather.setPyBgLabel( self.__pyBtnRestore, "PetsWindow:PetsPanel", "btnRestore" )

		self.__pyBtnCombine = Button( wnd.btnCombine )
		self.__pyBtnCombine.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCombine.enable = False
		labelGather.setPyBgLabel( self.__pyBtnCombine, "PetsWindow:PetsPanel", "btnCombine" )

		self.__pyBtnEnhance = Button( wnd.btnEnhance )
		self.__pyBtnEnhance.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnEnhance.enable = False
		labelGather.setPyBgLabel( self.__pyBtnEnhance, "PetsWindow:PetsPanel", "btnEnhance" )

		self.__pyBaseAttrs = {}										#�������ԣ��Ա𡢳ɳ��ȵ�
		self.__pyExtrAtts = {}										#��չ���ԣ����Ը��
		self.__pySkItems = {}										#���＼��
		self.__pyAttrItems = {}										#��������
		self.__pyPhysAtrrs = {}										#��������ս������
		self.__pyMaggicAttrs = {}									#���﷨��ս������
		self.__pyEnhanceItems = {}									#ǿ������
		self.__pyResistItems = {}									#���￹��
		for name, item in wnd.children:
			if name.startswith( "base_" ):
				tag = name.split( "_" )[1]
				pyStBase = StaticText( item )
				pyStBase.text = ""
				pyStBase.color = ( 255.0, 255.0, 255.0 )
				self.__pyBaseAttrs[tag] = pyStBase
			if name.startswith( "extr_" ):
				tag = name.split( "_" )[1]
				pyStExtr = StaticText( item )
				pyStExtr.text = ""
				self.__pyExtrAtts[tag] = pyStExtr
			if name.startswith( "skItem_" ):
				pySkItem = SkillItem( item )
				pySkItem.update( None )
				index = int( name.split( "_" )[1] )
				self.__pySkItems[index] = pySkItem
			if name.endswith( "_item" ):
				tag = name.split( "_" )[0]
				pyItem = PropertyItem( item )
				pyItem.name = labelGather.getText( "PetsWindow:PetsPanel", name )
				self.__pyAttrItems[tag] = pyItem
			if name.startswith( "physics_" ):
				tag = name.split( "_" )[1]
				pyStPhyAttr = CombatAttr( item )
				pyStPhyAttr.title = labelGather.getText( "PetsWindow:PetsPanel", name )
				pyStPhyAttr.text = ""
				self.__pyPhysAtrrs[tag] = pyStPhyAttr
			if name.startswith( "maggic_" ):
				tag = name.split( "_" )[1]
				pyStMaggicAttr = CombatAttr( item )
				pyStMaggicAttr.title = labelGather.getText( "PetsWindow:PetsPanel", name )
				pyStMaggicAttr.text = ""
				self.__pyMaggicAttrs[tag] = pyStMaggicAttr
			if name.endswith( "_enhance"):
				tag = name.split( "_" )[0]
				pyItem = EnhanceItem( item )
				pyItem.name = labelGather.getText( "PetsWindow:PetsPanel", name )
				self.__pyEnhanceItems[tag] = pyItem
			if name.startswith( "resist_" ):
				tag = name.split( "_" )[1]
				pyItem = ResistItem( item )
				pyItem.tag = tag
				self.__pyResistItems[tag] = pyItem
	
		labelGather.setLabel( wnd.nameText, "PetsWindow:PetsPanel", "nameText" )
		labelGather.setLabel( wnd.takeNumText, "PetsWindow:PetsPanel", "takeNumText" )
		labelGather.setLabel( wnd.abilityText, "PetsWindow:PetsPanel", "abilityText" )
		labelGather.setLabel( wnd.levelText, "PetsWindow:PetsPanel", "levelText" )
		labelGather.setLabel( wnd.skillText0, "PetsWindow:PetsPanel", "activeText0" )
		labelGather.setLabel( wnd.skillText1, "PetsWindow:PetsPanel", "activeText1" )
		labelGather.setLabel( wnd.skillText2, "PetsWindow:PetsPanel", "geniusText0" )
		labelGather.setLabel( wnd.skillText3, "PetsWindow:PetsPanel", "geniusText1" )
		labelGather.setLabel( wnd.magicBg.bgTitle.stTitle, "PetsWindow:PetsPanel", "magicAttr" )
		labelGather.setLabel( wnd.physBg.bgTitle.stTitle, "PetsWindow:PetsPanel", "phyisAttr" )

	# ----------------------------------------------------------------
	# pribvate
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_RECEIVE_TARGET_PETDATAS"] = self.__onShowPet
		self.__triggers["EVT_ON_TARGET_PET_WITHDRAW"] = self.__onPetWithdraw
		self.__triggers["EVT_ON_HIDE_TARGET_PET"] = self.__onHidePet

		for key in self.__triggers.iterkeys() :
			GUIFacade.registerEvent( key, self )

	def __unregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			GUIFacade.unregisterEvent( key, self )

	# ---------------------------------------------------------------
	def __onShowPet( self, petDatas, pet ):
		"""
		���³�������
		"""
		if petDatas is None:return
		self.espialPet = pet

		# �������ﲻһ����ģ��
		modelNumber = petDatas["modelNumber"].lower()
		hierarchy = petDatas["species"] & csdefine.PET_HIERARCHY_MASK
		if hierarchy == csdefine.PET_HIERARCHY_INFANCY2:
			modelNumber += Const.PET_ATTACH_MODELNUM
		self.__pyPetRender.resetModel( modelNumber )

		skills = petDatas["attrSkillBox"]
		self.__setPetSkills( skills )
		for key, tuple in self.__proAttrs.iteritems(): # ����������
			value0 = 0
			value1 = 0
			if key == "joyancy":
				value0 = petDatas.get( tuple[0], 0 )
				value1 = csconst.PET_JOYANCY_UPPER_LIMIT
			elif key == "life":
				value0 = petDatas.get( tuple[0], 0 )
				value1 = csconst.PET_LIFE_UPPER_LIMIT
			else:
				value0 = petDatas.get( tuple[0], 0 )
				value1 = petDatas.get( tuple[1], 0 )
			self.__pyAttrItems[key].update( ( value0, value1 ) )
		for tag, attr in self.__extrAttrs.iteritems():
			value = petDatas.get( attr, 0 )
			if tag == "takeLevel":
				self.__pyExtrAtts[tag].text = labelGather.getText( "PetsWindow:PetEspial", "takeLevel" )%value
			else:
				self.__pyExtrAtts[tag].text = self.__getExtrText( tag, value )
		for key, tuple in self.__enhanceAttrs.iteritems(): # ���¿�ǿ������
			if key == "freedom": # ���ɵ�
				value0 = -1
				value1 = petDatas.get( tuple[1], 0 )
			else:
				value0 = petDatas.get( tuple[0], 0 )
				value1 = petDatas.get( tuple[1], 0 )
			self.__pyEnhanceItems[key].update( ( value0, value1) )
		for tag, attr in self.__resistAttrs.iteritems():
			value = petDatas.get( attr, 0 )
			self.__pyResistItems[tag].update( value )
		for tag, attr in self.__phCombatAttrs.iteritems():
			value = petDatas.get( attr, 0 )
			pyPhysAtrr = self.__pyPhysAtrrs[tag]
			valueStr = ""
			if tag in ["duck","cruel", "blows"]:
				valueStr = "%0.1f%%" % ( value*100.0 )
			elif tag == "damage":
				minValue = petDatas["damage_min"]
				maxvalue = petDatas["damage_max"]
				valueStr = str(int(math.ceil((minValue + maxvalue )/2)))
			else:
				valueStr = str(int( math.ceil(value)))
			pyPhysAtrr.text = valueStr
		for tag, attr in self.__magCombatAttrs.iteritems():
			value = petDatas.get( attr, 0 )
			pyMaggicAttr = self.__pyMaggicAttrs[tag]
			if tag in ["duck","cruel", "blows"]:
				pyMaggicAttr.text = "%0.1f%%" % ( value*100.0 )
			else:
				pyMaggicAttr.text = str(int(math.ceil(value)))
		for tag, attr in self.__baseAttrs.iteritems():
			value = petDatas.get( attr )
			pyStBase = self.__pyBaseAttrs.get( tag, None )
			if pyStBase is None:continue
			valueStr = ""
			if tag == "gender":
				if value == csdefine.GENDER_MALE:
					valueStr = labelGather.getText( "PetsWindow:PetFoster", "gender_male" )
				else:
					valueStr = labelGather.getText( "PetsWindow:PetFoster", "gender_female" )
			elif tag == "level":
				valueStr = labelGather.getText( "PetsWindow:PetEspial", "petLevel" )%value 
			elif tag == "species":
				hierText, hierColor = self._pet_hierarchy.get( value, ( labelGather.getText( "PetsWindow:PetStorage", "typeStr" ), ( 255, 255, 255, 255 ) ) )
				pyStBase.color = hierColor
				valueStr = hierText
			elif tag == "ability":
				valueStr = "%d"%value
			elif tag == "name":
				valueStr = "%s"%value
			pyStBase.text = valueStr
		self.__trapID = BigWorld.player().addTrapExt( 30.0, self.__onEntitiesTrapThrough )#�򿪴��ں�Ϊ�����ӶԻ�����
		self.show()

	def __delTrap( self ) :
		player = BigWorld.player()
		if self.__trapID :
			player.delTrap( self.__trapID )
			self.__trapID = 0

	def __onEntitiesTrapThrough( self, entitiesInTrap ):
		if self.espialPet and self.espialPet not in entitiesInTrap:
			BigWorld.player().statusMessage( csstatus.VIEW_BE_LIMITED )
			self.__delTrap()
			self.hide()

	def __onPetWithdraw( self ):
		"""
		�鿴���ﱻ����
		"""
		self.hide()

	def __onHidePet( self ):
		"""
		���ؽ���
		"""
		self.hide()

	def __onLastKeyUpEvent( self, key, mods ) :
		"""
		�������ͷ�״̬
		"""
		if key != KEY_LEFTMOUSE : return
		BigWorld.cancelCallback( self.__turnModelCBID )
		LastKeyUpEvent.detach( self.__onLastKeyUpEvent )

	def __turnRight( self ):
		"""
		ģ����ת
		"""
		BigWorld.cancelCallback( self.__turnModelCBID )
		self.__turnModel( True )
		LastKeyUpEvent.attach( self.__onLastKeyUpEvent )
		return True

	def __turnLeft( self ):
		"""
		ģ����ת
		"""
		BigWorld.cancelCallback( self.__turnModelCBID )
		self.__turnModel( False )
		LastKeyUpEvent.attach( self.__onLastKeyUpEvent )
		return True

	def __turnModel( self, isRTurn ) :
		"""
		turning model on the mirror
		"""
		self.__pyPetRender.yaw += ( isRTurn and -0.1 or 0.1 )
		if BigWorld.isKeyDown( KEY_LEFTMOUSE ) :
			self.__turnModelCBID = BigWorld.callback( 0.1, Functor( self.__turnModel, isRTurn ) )

	def __setPetSkills( self, skills ):
		"""
		���³��＼��
		"""
		self.__clearPetSks()
		for skillID in skills:
			skillInfo = SkillItemInfo( Skill.getSkill( skillID ) )
			self.__onAddSkill( skillInfo )

	def __onAddSkill( self, skillInfo ):
		"""
		��Ӽ���
		"""
		isPassive = skillInfo.isPassive
		for index, pySkItem in self.__pySkItems.iteritems():
			if isPassive: #�츳����
				if not pySkItem.itemInfo and index >= 5:
					pySkItem.update( skillInfo )
					break
			else: #��������
				if not pySkItem.itemInfo and index < 5:
					pySkItem.update( skillInfo )
					break

	def __clearPetSks( self ):
		"""
		��������＼��
		"""
		for pyItem in self.__pySkItems.itervalues():
			pyItem.update( None )

	def __getExtrText( self, tag, value ):
		strResult = ""
		extrTexts = self.__extrTexture.get( tag, None )
		if extrTexts:
			for key, str in extrTexts.iteritems():
				if key == value:
					strResult = str
					break
		return strResult

	# --------------------------------------------------------------
	# public
	# --------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def show( self ):
		self.__pyPetRender.enableDrawModel()
		Window.show( self )

	def hide( self ):
		self.espialPet = None
		self.__turnModelCBID = 0
		Window.hide( self )
		self.__pyPetRender.disableDrawModel()

	def onLeaveWorld( self ):
		self.hide()

class CombatAttr( PyGUI ):
	def __init__( self, attrItem ):
		PyGUI.__init__( self, attrItem )
		self.__pyTitleText = StaticText( attrItem.titleText )
		self.__pyTitleText.color = ( 236.0, 218.0, 157.0 )
		self.__pyStValue = StaticText( attrItem.stValue )
		self.__pyStValue.color = ( 255.0, 255.0, 255.0 )
		self.__pyStValue.text = ""

	def updateValue( self, value ):
		self.__pyStValue.text = str( value )

	def clearValue( self ):
		self.__pyStValue.text = ""

	def _getText( self ):
		return self.__pyStValue.text

	def _setText( self, text ):
		self.__pyStValue.text = text

	def _getTitle( self ):
		return self.__pyTitleText.text
	
	def _setTitle( self, title ):
		self.__pyTitleText.text = title

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	text = property( _getText, _setText )
	title = property( _getTitle, _setTitle )