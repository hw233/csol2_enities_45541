# -*- coding: gb18030 -*-
#
# $Id: EspialWindow.py,v 1.3 2008-09-05 08:05:00 fangpengjun Exp $
# 查看宠物属性窗口

from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.Window import Window
from guis.tooluis.CSRichText import CSRichText
from guis.controls.StaticText import StaticText
from guis.controls.BaseObjectItem import BaseObjectItem
from guis.controls.ProgressBar import HProgressBar
from guis.controls.SkillItem import SkillItem
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabPage
from guis.controls.TabCtrl import TabPanel
from guis.controls.TabCtrl import TabCtrl
from guis.controls.Button import Button
from guis.general.petswindow.petpanel.PetModelRender import PetModelRender
from ItemsFactory import PetSkillItem as SkillItemInfo
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
from NPCModelLoader import NPCModelLoader
from LabelGather import labelGather
g_npcmodel = NPCModelLoader.instance()
from PetFormulas import formulas
import skills as Skill
import csdefine


class EspialWindow( Window ):

	__instance = None

	_proAttrs = {} # 具体属性
	_proAttrs["hp"]			= ( "HPMax", "HPMax" ) # 生命
	_proAttrs["mp"]			= ( "MPMax", "MPMax" ) # 法力
	_proAttrs["spirit"]		= ( "nimbus", "nimbusMax" ) # 灵力
	_proAttrs["const"]		= ( "calcaneus", "calcaneusMax" ) # 根骨
	_proAttrs["life"]		= ( "life", "lifeMax" ) # 寿命

	_comAttrs = {} # 可强化属性
	_comAttrs["habitus"]		= ( "corporeity", "ec_corporeity" )#体质
	_comAttrs["force"]			= ( "strength",  "ec_strength" )# 力量
	_comAttrs["brains"]			= ( "intellect" , "ec_intellect" )# 智力
	_comAttrs["agility"]		= ( "dexterity", "ec_dexterity" ) # 敏捷
	_comAttrs["freepoint"]		= ( "", "ec_free" ) # 自由加点

	_typeAttrs = {} #类型属性
	_typeAttrs["character"]		= "character"
	_typeAttrs["isBreed"]		= "procreated"
	_typeAttrs["type"]			= "ptype"
	_typeAttrs["ability"]	= "ability"

	_phCombatAttrs = {} # 物理战斗属性
	_phCombatAttrs["damage"] 		= "damage" # 平均物理攻击
	_phCombatAttrs["recovery"] 	= "armor"	# 物理防御
	_phCombatAttrs["duck"] 		= "dodge_probability" # 闪避
	_phCombatAttrs["cruel"]		= "double_hit_probability"# 物理暴击
	_phCombatAttrs["blows"]		= "resist_hit_probability" # 招架

	_magCombatAttrs = {} # 法术战斗属性
	_magCombatAttrs["damage"]		= "magic_damage" # 法术攻击
	_magCombatAttrs["recovery"]	= "magic_armor" # 法术防御
	_magCombatAttrs["duck"]		= "dodge_probability" # 闪避
	_magCombatAttrs["cruel"]		= "magic_double_hit_probability" # 法术暴击

	_resistAttrs = {} # 抗性属性
	_resistAttrs["fix"]			= "resistFixProbability"
	_resistAttrs["giddy"]		= "resistGiddyProbability"
	_resistAttrs["sleep"]		= "resistSleepProbability"
	_resistAttrs["hush"]		= "resistChenmoProbability"

	_pet_types = {csdefine.PET_TYPE_STRENGTH:	labelGather.getText( "vendwindow:espialWindow", "miStrength" ),
			csdefine.PET_TYPE_BALANCED:	labelGather.getText( "vendwindow:espialWindow", "miBalanced" ),
			csdefine.PET_TYPE_SMART:	labelGather.getText( "vendwindow:espialWindow", "miSmart" ),
			csdefine.PET_TYPE_INTELLECT:	labelGather.getText( "vendwindow:espialWindow", "miIntellect" )
			}
	_pet_characters = { csdefine.PET_CHARACTER_SUREFOOTED:	labelGather.getText( "vendwindow:espialWindow", "miSurefooted" ),
		csdefine.PET_CHARACTER_CLOVER:	labelGather.getText( "vendwindow:espialWindow", "miClover" ),
		csdefine.PET_CHARACTER_CANNILY:	labelGather.getText( "vendwindow:espialWindow", "miCannily" ),
		csdefine.PET_CHARACTER_BRAVE:	labelGather.getText( "vendwindow:espialWindow", "miBrave" ),
		csdefine.PET_CHARACTER_LIVELY:	labelGather.getText( "vendwindow:espialWindow", "miLively" )
		}

	_pet_genders = {  csdefine.GENDER_MALE: labelGather.getText( "vendwindow:espialWindow", "miMale" ),
		csdefine.GENDER_FEMALE: labelGather.getText( "vendwindow:espialWindow", "miFemale" )
		}

	_pet_breeds = {csdefine.PET_PROCREATE_STATUS_NONE:	labelGather.getText( "vendwindow:espialWindow", "miUnprocreate" ),
			csdefine.PET_PROCREATE_STATUS_PROCREATING:	labelGather.getText( "vendwindow:espialWindow", "miProcreating" ),
			csdefine.PET_PROCREATE_STATUS_PROCREATED:	labelGather.getText( "vendwindow:espialWindow", "miProcreated" )
			}

	_pet_hierarchy = { csdefine.PET_HIERARCHY_GROWNUP : ( labelGather.getText( "vendwindow:espialWindow", "miGrownup" ), ( 255, 255, 255, 255 ) ),
					   csdefine.PET_HIERARCHY_INFANCY1 : ( labelGather.getText( "vendwindow:espialWindow", "miInfancy1" ), ( 0, 128, 255, 255 ) ),
					   csdefine.PET_HIERARCHY_INFANCY2 : ( labelGather.getText( "vendwindow:espialWindow", "miInfancy2" ), ( 254, 163, 8, 255 ) ),
					   }

	def __init__( self ):
		assert EspialWindow.__instance is None, "EspialWindow instance had been created! Please use the instance method to get the created instance!"
		wnd = GUI.load( "guis/general/vendwindow/buywindow/espialpet.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True
		self.__triggers = {}
		self.__turnModelCBID = 0
		self.addToMgr( "espialPet" )
		self.__initialize( wnd )

	def __initialize( self, wnd ):
		self.__pyPetHead = PyGUI( wnd.frame_baseInfo.petHead )
		self.__pyPetHead.texture = ""

		self.__pyStPetName = StaticText( wnd.frame_baseInfo.stName ) 		# 宠物名称
		self.__pyStPetName.text = ""

		self.__pyStPetLevel = StaticText( wnd.frame_baseInfo.stLevel ) 	# 宠物等级
		self.__pyStPetLevel.text = ""

		self.__pyRtAttr = CSRichText( wnd.frame_baseInfo.rtAttr ) 			# 属性
		self.__pyRtAttr.text = ""

		self.__pyRtInfo = CSRichText( wnd.frame_baseInfo.rtInfo ) 			# 信息
		self.__pyRtInfo.text = ""

		self.pyTakeLevel = StaticText( wnd.takeLevel )		# 可携带等级
		self.pyTakeLevel.text = ""

		self.__pyLeftBtn = Button( wnd.leftBtn )
		self.__pyLeftBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyLeftBtn.onLMouseDown.bind( self.__onTurnLeft )

		self.__pyRightBtn = Button( wnd.rightBtn )
		self.__pyRightBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyRightBtn.onLMouseDown.bind( self.__onTurnRight )

		self.__pyGeniusSKs = {} #天赋技能
		self.__pyInitiativeSKs = {} #主动技能
		for name, item in wnd.skPnl_genius.children:
			if not name.startswith( "skitem_" ):continue
			index = int( name.split( "_" )[1] )
			pyGeniusSK = SkillItem( item )
			self.__pyGeniusSKs[index] = pyGeniusSK
		for name, item in wnd.skPnl_initiative.children:
			if not name.startswith( "skitem_" ):continue
			index = int( name.split( "_" )[1] )
			pyInitiSK = SkillItem( item )
			self.__pyInitiativeSKs[index] = pyInitiSK

		self.__pyResistPanel = ResistPanel( wnd.resistPanel ) #宠物抗性
		self.__pyProPanel = PropertyPanel( wnd.proPanel ) #HP、MP等属性
		self.__pyPetRender = PetModelRender( wnd.petRender ) #宠物模型
		self.__pyPetRender.bgTexture = "guis/general/vendwindow/buywindow/render.tga" #设置宠物模型的背景图
		self.__pyBaseAttr = BaseAttr( wnd.baseAttr ) #体质、智力等属性
		self.__pyPhyPanel = PhyPanel( wnd.attr_physics )
		self.__pyMagicPanel = MagicPanel( wnd.attr_magic )

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setLabel( wnd.lbTitle, "vendwindow:espialWindow", "lbTitle" )
		labelGather.setLabel( wnd.baseAttr.title.stTitle, "vendwindow:espialWindow", "baseAttrTitle" )
		labelGather.setLabel( wnd.skPnl_genius.lbTitle, "vendwindow:espialWindow", "geniusTitle" )
		labelGather.setLabel( wnd.skPnl_initiative.lbTitle, "vendwindow:espialWindow", "initiativeTitle" )
		labelGather.setLabel( wnd.attr_physics.title.stTitle, "vendwindow:espialWindow", "physicsAttrTitle" )
		labelGather.setLabel( wnd.attr_magic.title.stTitle, "vendwindow:espialWindow", "magicAttrTitle" )


	# --------------------------------------------------------------------
	# pravite
	# --------------------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_PET_ATTR_CHANGED"]	 = self.__onAttrUpdate
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		"""
		deregister all events
		"""
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )

	def __onAttrUpdate( self, dbid, attrName ):
		pass

	def __onLastKeyUpEvent( self, key, mods ) :
		if key != KEY_LEFTMOUSE : return
		BigWorld.cancelCallback( self.__turnModelCBID )
		LastKeyUpEvent.detach( self.__onLastKeyUpEvent )

	def __onTurnLeft( self ):
		BigWorld.cancelCallback( self.__turnModelCBID )
		self.__turnModel( False )
		LastKeyUpEvent.attach( self.__onLastKeyUpEvent )
		return True

	def __onTurnRight( self ):
		BigWorld.cancelCallback( self.__turnModelCBID )
		self.__turnModel( True )
		LastKeyUpEvent.attach( self.__onLastKeyUpEvent )
		return True

	def __turnModel( self, isRTurn ) :
		"""
		turning model on the mirror
		"""
		self.__pyPetRender.yaw += ( isRTurn and -0.1 or 0.1 )
		if BigWorld.isKeyDown( KEY_LEFTMOUSE ) :
			self.__turnModelCBID = BigWorld.callback( 0.1, Functor( self.__turnModel, isRTurn ) )

	def __upDatePetInfo( self, epitome ):
		for tuple in self._proAttrs.itervalues(): # 具体属性
			for attrName in tuple:
				self.__setAttr( epitome, attrName )
		for tuple in self._comAttrs.itervalues():# 普通属性
			for attrName in tuple:
				self.__setAttr( epitome, attrName )
		for attrName in self._typeAttrs.itervalues(): # 类型属性
			self.__setAttr( epitome, attrName )
		for attrName in self._resistAttrs.itervalues():# 抗性属性
			self.__setAttr( epitome, attrName )
		for attrName in self._phCombatAttrs.itervalues(): # 物理战斗属性
			self.__setAttr( epitome, attrName )
		for attrName in self._magCombatAttrs.itervalues():# 法术战斗属性
			self.__setAttr( epitome, attrName )
		proSkills = [] # 职业技能
		genSkills = [] # 天赋技能
		for skillID in epitome.skills:
			skillInfo = SkillItemInfo( Skill.getSkill( skillID ) )
			if skillInfo.isPassive:
				genSkills.append( skillInfo )
			else:
				proSkills.append( skillInfo )
		for index, skillInfo in enumerate ( genSkills ):
			pyGenSK = self.__pyGeniusSKs.get( index )
			if pyGenSK is None:break
			pyGenSK.update( skillInfo )
		for index, skillInfo in enumerate ( proSkills ):
			pyActSK = self.__pyInitiativeSKs.get( index )
			if pyActSK is None:break
			pyActSK.update( skillInfo )
		modelNumber = epitome.modelNumber
		gendText = self._pet_genders.get( epitome.gender )
		if gendText is None:
			gendText = labelGather.getText( "vendwindow:espialWindow", "miUnKnown" )
		typeText = self._pet_types.get( epitome.ptype )
		if typeText is None:
			typeText.text = labelGather.getText( "vendwindow:espialWindow", "miUnKnown" )
		self.__pyRtAttr.text = "%s%s%s"%( typeText, PL_Space.getSource( 3 ), gendText )
		hierarchy = epitome.hierarchy #宠物辈分
		hierText, hierColor = self._pet_hierarchy.get( hierarchy, ( labelGather.getText( "vendwindow:espialWindow", "miUnKnown" ), (255,255,255,255) ) )
		self.pyTakeLevel.text = labelGather.getText( "vendwindow:espialWindow", "miTakeLevel", epitome.takeLevel )
		hierText = PL_Font.getSource( hierText, fc = hierColor )
		abilityText = labelGather.getText( "vendwindow:espialWindow", "miAbility", epitome.ability ) #成长度
		charaterText = self._pet_characters.get( epitome.character )
		if charaterText is None:
			charaterText = labelGather.getText( "vendwindow:espialWindow", "miUnKnown" )
		breedText = self._pet_breeds.get( epitome.procreated )
		if breedText is None:
			breedText.text = labelGather.getText( "vendwindow:espialWindow", "miUnKnown" )
		self.__pyRtInfo.text = "%s%s%s%s%s%s%s"%( hierText, PL_Space.getSource( 2 ), abilityText, PL_Space.getSource( 2 ),\
		charaterText, PL_Space.getSource( 2 ), breedText )
		self.__pyPetHead.texture = g_npcmodel.getHeadTexture( modelNumber )
		self.__pyPetRender.resetModel( epitome.modelNumber.lower() )
		self.__pyStPetLevel.text = str( epitome.level )
		self.__pyStPetName.text = epitome.name

	def __setAttr( self, epitome, attrName ): # 设置宠物各属性
		dbid = epitome.databaseID
		attrText = ""
		for key, tuple in self._proAttrs.iteritems(): # 更新属性栏
			if attrName in tuple:
				value0 = getattr( epitome, tuple[0] )
				value1 = getattr( epitome, tuple[1] )
				self.__pyProPanel.updateInfo( key, dbid, ( value0, value1 ) )
		for key, tuple in self._comAttrs.iteritems(): # 更新可强化属性
			if attrName in tuple:
				if key == "freepoint": # 自由点
					value0 = -1
					value1 = getattr( epitome, tuple[1] )
				else:
					value0 = getattr( epitome, tuple[0] )
					value1 = getattr( epitome, tuple[1] )
				self.__pyBaseAttr.updateInfo( key, epitome, ( int(value0), int(value1) ) )
		for tag, attr in self._resistAttrs.iteritems():
			if attrName == attr:
				value = getattr( epitome, attrName )
				self.__pyResistPanel.updateInfo( tag, value )
		for tag, attr in self._phCombatAttrs.iteritems():
			if attrName == attr:
				value = getattr( epitome, attrName )
				self.__pyPhyPanel.updateInfo( dbid, tag, value )
		for tag, attr in self._magCombatAttrs.iteritems():
			if attrName == attr:
				value = getattr( epitome, attrName )
				self.__pyMagicPanel.updateInfo( dbid, tag, value )

	# --------------------------------------------------------------
	# public
	# --------------------------------------------------------------

	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def show( self, petEmotion, pyOwner = None ):
		self.__pyPetRender.enableDrawModel()
		for pyGeniuSK in self.__pyGeniusSKs.itervalues():
			pyGeniuSK.update( None )
		for pyInitiSK in self.__pyInitiativeSKs.itervalues():
			pyInitiSK.update( None )
		self.__upDatePetInfo( petEmotion )
		self.__registerTriggers()
		Window.show( self, pyOwner )

	def hide( self ):
		Window.hide( self )
		self.__pyPetRender.disableDrawModel()
		for pyGeniuSK in self.__pyGeniusSKs.itervalues():
			pyGeniuSK.update( None )
		for pyInitiSK in self.__pyInitiativeSKs.itervalues():
			pyInitiSK.update( None )
		self.removeFromMgr()
		EspialWindow.__instance = None

	def onLeaveWorld( self ):
		self.__pyPetHead.texture = ""
		self.__pyStPetName.text = ""
		self.__pyStPetLevel.text = ""
		self.__pyRtAttr.text = ""
		self.__pyRtInfo.text = ""
		self.hide()

	# ------------------------------------------------
	@staticmethod
	def instance() :
		if EspialWindow.__instance is None :
			EspialWindow.__instance = EspialWindow()
		return EspialWindow.__instance

	def __del__( self ) :
		if Debug.output_del_EspialWindow :
			INFO_MSG( str( self ) )


# ----------------------------------------------------------------
# 调整属性字体尺寸修饰器
# ----------------------------------------------------------------
from AbstractTemplates import MultiLngFuncDecorator
from guis.general.petswindow.petpanel.AttributeItem import PropertyItem

class deco_PetEspInitPropertyItems( MultiLngFuncDecorator ) :

	@staticmethod
	def locale_big5( SELF, panel ) :
		"""
		繁体版下重新调整部分属性字体的尺寸
		"""
		pyAttrItems = SELF._PropertyPanel__pyItems
		for name, item in panel.children:
			if "_item" not in name :continue
			tag = name.split( "_" )[0]
			labelGather.setLabel( item.stName, "vendwindow:espialWindow", name ) # 设置标签
			pyItem = PropertyItem( item )
			pyItem._PropertyItem__pyStValue.charSpace = -1
			pyItem._PropertyItem__pyStValue.fontSize = 11
			pyAttrItems[tag] = pyItem
		pyAttrItems["life"]._PropertyItem__pyStValue.charSpace = -2


# ------------------------------------------------------------------
# HP、MP等属性面板
# -------------------------------------------------------------------
class PropertyPanel( PyGUI ):
	def __init__( self, proPanel ):
		PyGUI.__init__( self, proPanel )
		self.__pyItems = {}
		self.__initPanel( proPanel )

	@deco_PetEspInitPropertyItems
	def __initPanel( self, panel ):
		for name, item in panel.children:
			if "_item" not in name :continue
			tag = name.split( "_" )[0]
			labelGather.setLabel( item.stName, "vendwindow:espialWindow", name ) # 设置标签
			pyItem = PropertyItem( item )
			self.__pyItems[tag] = pyItem

	def updateInfo( self, tag, dbid, tuple ):
		self.__dbid = dbid
		if self.__pyItems.has_key( tag ):
			pyItem = self.__pyItems[tag]
			pyItem.update( tuple )

	def clearItems( self ):
		for pyItem in self.__pyItems.itervalues():
			pyItem.update( (0, 0) )

class BaseAttr( PyGUI ):
	def __init__( self, panel = None, pyBinder = None ):
		PyGUI.__init__( self, panel )
		self.__initPanel( panel )

	def __initPanel( self, panel ):
		self.__pyItems ={}
		for name, item in panel.children:
			if "_Item" not in name:continue
			tag = name.split( "_" )[0]
			labelGather.setLabel( item.stName, "vendwindow:espialWindow", name ) # 设置标签
			pyItem = IntentifyItem( tag, item )
			self.__pyItems[tag] = pyItem

	def setUIState( self, num ):
		for pyItem in self.__pyItems.itervalues():
			pyItem.setState( num )

	def updateInfo( self, tag, epitome, tuple ):
		if self.__pyItems.has_key( tag ):
			pyItem = self.__pyItems[tag]
			pyItem.update( epitome, tuple )

# -----------------------------------------------------
class PhyPanel( PyGUI ): # tabCtr中的物理战斗属性
	def __init__( self, panel = None ):
		PyGUI.__init__( self, panel )
		self.__initPanel( panel )

	def __initPanel( self, panel ):
		self.__pyLabels = {}
		for name, item in panel.children:
			if "_Item" not in name:continue
			tag = name.split("_")[0]
			labelGather.setLabel( item.stName, "vendwindow:espialWindow", name + "_0" ) # 设置标签
			pyItem = StaticText( item.lbValue )
			self.__pyLabels[tag] = pyItem
	# -----------------------------------------
	def updateInfo( self, dbid, tag, value ):
		if self.__pyLabels.has_key( tag ):
			pyLabel = self.__pyLabels[tag]
			if tag in ["duck","cruel", "blows"]:
				pyLabel.text = "%0.1f%%" % ( value*100.0 )
			else:
				pyLabel.text = "%0.1f"%value

	def setUIState( self, exitNum ):
		if exitNum == 0:
			for pyLabel in self.__pyLabels.itervalues():
				pyLabel.text = ""

# ------------------------------------------------------
class MagicPanel( PyGUI ): # tabCtr中的法术战斗属性
	def __init__( self, panel = None ):
		PyGUI.__init__( self, panel )
		self.__initPanel( panel )

	def __initPanel( self, panel ):
		self.__pyLabels = {}
		for name, item in panel.children:
			if "_Item" not in name:continue
			tag = name.split("_")[0]
			labelGather.setLabel( item.stName, "vendwindow:espialWindow", name + "_1" ) # 设置标签
			pyItem = StaticText( item.lbValue )
			self.__pyLabels[tag] = pyItem

	#------------------------------------
	def updateInfo( self, dbid, tag, value ):
		if self.__pyLabels.has_key( tag ):
			pyLabel = self.__pyLabels[tag]
			if tag in ["duck","cruel"]:
				pyLabel.text = "%0.1f%%" % ( value*100.0 )
			else:
				pyLabel.text = "%0.1f"%value

	def setUIState( self, exitNum ):
		if exitNum == 0:
			for pyLabel in self.__pyLabels.itervalues():
				pyLabel.text = ""

class ResistPanel( PyGUI ):
	def __init__( self, panel = None ):
		PyGUI.__init__( self, panel )
		self.__initPanel( panel )

	def __initPanel( self, panel ):
		self.__pyItems = {}
		for name, item in panel.children:
			if "resist_" not in name:continue
			tag = name.split( "_" )[1]
			pyItem = ResistItem( tag, item )
			self.__pyItems[tag] = pyItem

	def setUIState( self, num ):
		for pyItem in self.__pyItems.itervalues():
			pyItem.setState( num )

	def updateInfo( self, tag, value ):
		if self.__pyItems.has_key( tag ):
			pyItem = self.__pyItems[tag]
			pyItem.update( value )

	def clearItems( self ):
		for pyItem in self.__pyItems.itervalues():
			pyItem.update( 0.0 )

class ResistItem( HProgressBar ):

	_dsp_dict = eval( labelGather.getText( "vendwindow:espialWindow", "dsp_dict" ) )

	def __init__( self, tag, resistItem ):
		HProgressBar.__init__( self, resistItem, pyBinder = None )
		self.__tag = tag
		self.crossFocus = True
		self.valStr = ""
		self.value = 0.0

	def __getDescription( self, tag):
		if self._dsp_dict.has_key( tag ):
			dsp = self._dsp_dict[tag]%( self.valStr )
			return dsp

	# ----------------------------------------------------------------------
	def onMouseEnter_( self ):
		HProgressBar.onMouseEnter_( self )
		dsp = self.__getDescription( self.tag )
		if dsp == "": return
		toolbox.infoTip.showToolTips( self, dsp )
		return True

	def onMouseLeave_( self ):
		HProgressBar.onMouseLeave_( self )
		toolbox.infoTip.hide()
		return True

	# ---------------------------------------------------------------
	def setState( self, num ):
		self.crossFocus = num > 0

	def update( self, value ):# 更新状态值
		rate = float( value )
		self.valStr = "%0.1f%%" % ( rate*100.0 )
		self.value = value

	# -------------------------------------------------------------------
	def _getTag( self ):

		return self.__tag

	def _setTag( self, tag ):

		self.__tag = tag

	tag = property( _getTag, _setTag )

# --------------------------------------------------
from guis.controls.Control import Control
class IntentifyItem( Control ):
	def __init__( self, tag, item = None ):
		Control.__init__( self, item )
		self.__tag = tag
		self.__epitome = None
		self.__pyLbValue = StaticText( item.lbValue )
		self.__pyLbValue.text = ""

		self.__pyLbFree = StaticText( item.lbFree )
		self.__pyLbFree.text = ""

#		self.__pyTipsIcon = Icon( item.freeIcon )
#		self.__pyTipsIcon.crossFocus = True
#		self.__pyTipsIcon.onMouseEnter.bind( self.__showTips )
#		self.__pyTipsIcon.onMouseLeave.bind( self.__hideTips )

	def __showTips( self ):
		pass

	def __hideTips( self ):
		pass

	def setState( self, num ):
		if num == 0:
			self.__pyLbValue.text = ""
			self.__pyLbFree.text = ""

	def update( self, epitome, tuple ):
		self.__epitome = epitome
		if tuple[0] == -1:
			self.__pyLbValue.text = ""
		else:
			self.__pyLbValue.text = str( tuple[0] )
		self.__pyLbFree.text =  "X " + str( tuple[1] )