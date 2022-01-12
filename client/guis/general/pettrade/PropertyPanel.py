# -*- coding: gb18030 -*-
#
# $Id: PropertyPanel.py,v 1.13 2008-08-22 02:06:51 qilan Exp $

"""
implement PropertyPanel class
"""

from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from guis.controls.StaticText import StaticText
from guis.controls.ComboBox import ComboBox
from guis.controls.Button import Button
from guis.tooluis.CSRichText import CSRichText
from AttributePanel import AttributePanel
from ItemsFactory import PetSkillItem as SkillItemInfo
from NPCModelLoader import NPCModelLoader
g_npcmodel = NPCModelLoader.instance()
from PetFormulas import formulas
from LabelGather import labelGather
import skills as Skill
import csdefine
import GUIFacade

class PropertyPanel( Control ):

	_baseAttrs = {}
	_baseAttrs["hp"]			= ( "HP", "HPMax" ) # 生命
	_baseAttrs["mp"]			= ( "MP", "MPMax" ) # 法力

	_proAttrs = {} #具体属性
	_proAttrs["spirit"]		= ( "nimbus", "nimbusMax" ) # 灵力
	_proAttrs["const"]		= ( "calcaneus", "calcaneusMax" ) # 根骨
	_proAttrs["life"]		= ( "life", "lifeMax" ) #寿命
	_proAttrs["ability"] = ( "", "ability" ) #成长度
	_proAttrs["takeLevel"] = ( "", "takeLevel" )#携带等级

	_comAttrs = {} #可强化属性
	_comAttrs["habitus"]		= ( "corporeity", "ec_corporeity" )#体质
	_comAttrs["force"]			= ( "strength",  "ec_strength" )# 力量
	_comAttrs["brains"]			= ( "intellect" , "ec_intellect" )# 智力
	_comAttrs["agility"]		= ( "dexterity", "ec_dexterity" ) # 敏捷
	_comAttrs["freepoint"]		= ( "", "ec_free" ) # 自由加点

	_typeAttrs = {} #类型属性
	_typeAttrs["character"]		= "character"
	_typeAttrs["isBreed"]		= "procreated"
	_typeAttrs["type"]			= "ptype"
	_typeAttrs["ability"]		= "ability"
	_typeAttrs["hierarchy"]		= "hierarchy"

	_phCombatAttrs = {} #物理战斗属性
	_phCombatAttrs["damage"] 		= "damage" # 平均物理攻击
	_phCombatAttrs["recovery"] 	= "armor"	# 物理防御
	_phCombatAttrs["duck"] 		= "dodge_probability" # 闪避
	_phCombatAttrs["cruel"]		= "double_hit_probability"# 物理暴击
	_phCombatAttrs["blows"]		= "resist_hit_probability" # 招架

	_magCombatAttrs = {} #法术战斗属性
	_magCombatAttrs["damage"]		= "magic_damage" # 法术攻击
	_magCombatAttrs["recovery"]	= "magic_armor" # 法术防御
	_magCombatAttrs["duck"]		= "dodge_probability" # 闪避
	_magCombatAttrs["cruel"]		= "magic_double_hit_probability" # 法术暴击

	_resistAttrs = {} #抗性属性
	_resistAttrs["fix"]			= "resistFixProbability"
	_resistAttrs["giddy"]		= "resistGiddyProbability"
	_resistAttrs["sleep"]		= "resistSleepProbability"
	_resistAttrs["hush"]		= "resistChenmoProbability"

	__labelTexts = { "type":
			{csdefine.PET_TYPE_STRENGTH:	labelGather.getText( "petTrade:main", "miStrength" ),
			csdefine.PET_TYPE_BALANCED:	labelGather.getText( "petTrade:main", "miBalanced" ),
			csdefine.PET_TYPE_SMART:	labelGather.getText( "petTrade:main", "miSmart" ),
			csdefine.PET_TYPE_INTELLECT:	labelGather.getText( "petTrade:main", "miIntellect" )
			},
			"isBreed":
				{csdefine.PET_PROCREATE_STATUS_NONE:	labelGather.getText( "petTrade:main", "miunprocreate" ),
				csdefine.PET_PROCREATE_STATUS_PROCREATING:	labelGather.getText( "petTrade:main", "miProcreating" ),
				csdefine.PET_PROCREATE_STATUS_PROCREATED:	labelGather.getText( "petTrade:main", "miProcreated" )
				},
			"character":
				{ csdefine.PET_CHARACTER_SUREFOOTED:	labelGather.getText( "petTrade:main", "miSurefooted" ),
				csdefine.PET_CHARACTER_CLOVER:	labelGather.getText( "petTrade:main", "miClover" ),
				csdefine.PET_CHARACTER_CANNILY:	labelGather.getText( "petTrade:main", "miCannily" ),
				csdefine.PET_CHARACTER_BRAVE:	labelGather.getText( "petTrade:main", "miBrave" ),
				csdefine.PET_CHARACTER_LIVELY:	labelGather.getText( "petTrade:main", "miLively" )
				},
			"hierarchy":
				{csdefine.PET_HIERARCHY_GROWNUP:labelGather.getText( "petTrade:main", "miInfancy1" ),
				csdefine.PET_HIERARCHY_INFANCY1:labelGather.getText( "petTrade:main", "miInfancy2" ),
				csdefine.PET_HIERARCHY_INFANCY2:labelGather.getText( "petTrade:main", "miInfancy3" ),
				}
			}
	_pet_genders = {  csdefine.GENDER_MALE: labelGather.getText( "petTrade:main", "miMale" ),
		csdefine.GENDER_FEMALE: labelGather.getText( "petTrade:main", "miFemale" )
		}

	def __init__( self, panel = None, pyBinder = None ):
		Control.__init__( self, panel, pyBinder )
		self.__initialize( panel )

	def subclass( self, panel, pyBinder ) :
		Control.subclass( self, panel, pyBinder )
		self.__initialize( panel )
		return True

	def __initialize( self, panel ):
		if panel is None:return
		self.pyPetsCB_ = ComboBox( panel.petsCB )
		self.pyPetsCB_.autoSelect = False
		self.pyPetsCB_.text = ""
		self.pyPetsCB_.foreColor = (252,235,179)

		self.pyFrontBtn_ = Button( panel.frontBtn )
		self.pyFrontBtn_.setStatesMapping( UIState.MODE_R2C2 )

		self.pyNextBtn_ = Button( panel.nextBtn )
		self.pyNextBtn_.setStatesMapping( UIState.MODE_R2C2 )

		self.__pyPetImage = PyGUI( panel.petImage ) #宠物头像
		self.__pyLbLevel = StaticText( panel.lbLevel ) #宠物等级
		self.__pyLbLevel.text = ""

		self.__pyAttrPanel = AttributePanel( panel.propertyPanel, self ) #
		self.__pyPhyPanel = PhyPanel( panel.phyPanel, self ) #物理战斗属性
		self.__pyMagPanel = MagicPanel( panel.magicPanel, self ) #法术战斗属性
		self.__pyPointPanel = PointPanel( panel.baseProperty, self ) #加点属性

		self.__pyProSkillPanel = SkillsPanel( panel.proskillPanel, self ) #职业技能
		self.__pyGenSkillPanel = SkillsPanel( panel.genskillPanel, self ) #天赋技能
		self.__pyResistPanel = ResistPanel( panel.resistPanel, self ) #抗性
		
		self.__pyStGenSkill = StaticText(panel.stGenSkill,self)
		self.__pyStProSkill = StaticText(panel.stProSkill,self)

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setPyLabel( self.__pyStGenSkill, "petTrade:main", "stGenSkill" )
		labelGather.setPyLabel( self.__pyStProSkill, "petTrade:main", "stProSkill" )
		labelGather.setLabel( panel.mp_item.stName, "petTrade:main", "mp_item" )
		labelGather.setLabel( panel.hp_item.stName, "petTrade:main", "hp_item" )

		self.__initProLabels( panel )

	# ------------------------------------------------------------
	# private
	# ------------------------------------------------------------

	def initPetsCB_( self ):

		pass

	def __initProLabels( self, panel ):
		self.__pyLabels = {}
		self.__pyBaseItems = {}
		for name, item in panel.children:
			if "label_" not in name :continue
			tag = name.split("_")[1]
			pyLabel = StaticText( item )
			pyLabel.text = ""
			pyLabel.tag = tag
			self.__pyLabels[tag] = pyLabel

		for name, item in panel.children: #血、蓝条
			if "_item" not in name :continue
			tag = name.split( "_" )[0]
			pyItem = PropertyItem( tag, item )
			self.__pyBaseItems[tag] = pyItem
	# ------------------------------------------------------------
	# public
	# ------------------------------------------------------------
	def resumePanels_( self ): #重置界面
		self.pyPetsCB_.text = ""
		self.__pyAttrPanel.clearItems()
		self.__pyPhyPanel.setUIState( 0 )
		self.__pyMagPanel.setUIState( 0 )
		self.__pyPointPanel.setUIState( 0 )
		self.__pyProSkillPanel.clearItems()
		self.__pyGenSkillPanel.clearItems()
		self.__pyResistPanel.setUIState( 0 )
		self.__pyPetImage.texture = ""
		self.__pyLbLevel.text = ""
		for tag, pyLabel in self.__pyLabels.iteritems():
			pyLabel.text = ""
		for pyItem in self.__pyBaseItems.values():
			pyItem.update( (0,0) )

	def onPetSelected_( self, pyItem ):
		player = BigWorld.player()
		if pyItem is None:return
		self.pyPetsCB_.text = pyItem.petName
		outEpitome = player.pcg_getActPetEpitome()
		petEpitome = pyItem.epitome
		print "haha petEpitome",petEpitome
		dbid = petEpitome.databaseID
		hierarchy = petEpitome.hierarchy #宠物辈分
		hierColor = ( 255, 255, 255, 255 )
		hierText = ""
		if formulas.isHierarchy( hierarchy, csdefine.PET_HIERARCHY_GROWNUP ): #成年宠物
			hierColor = ( 255, 255, 255, 255 )
			hierText = labelGather.getText( "petTrade:main", "miInfancy1" )
		elif formulas.isHierarchy( hierarchy, csdefine.PET_HIERARCHY_INFANCY1 ): #一代宝宝
			hierColor = ( 0, 0, 255, 255 )
			hierText = labelGather.getText( "petTrade:main", "miInfancy2" )
		else: #二代宝宝
			hierColor = ( 254, 163, 8, 255 )
			hierText = labelGather.getText( "petTrade:main", "miInfancy3" )
		for tag, tuple in self._baseAttrs.iteritems(): #血、蓝属性
			pyBaseItem = self.__pyBaseItems.get( tag )
			if pyBaseItem is None:return
			pyBaseItem.update( ( getattr( petEpitome, tuple[0] ), getattr( petEpitome, tuple[1] ) ) )
		for tuple in self._proAttrs.itervalues(): #具体属性
			for attrName in tuple:
				self.__setAttr( petEpitome, attrName )
		for tuple in self._comAttrs.itervalues(): #普通属性
			for attrName in tuple:
				self.__setAttr( petEpitome, attrName )
		for attrName in self._typeAttrs.itervalues(): #类型属性
			self.__setAttr( petEpitome, attrName )
		for attrName in self._resistAttrs.itervalues(): #抗性属性
			self.__setAttr( petEpitome, attrName )
		for attrName in self._phCombatAttrs.itervalues(): #物理战斗属性
			self.__setAttr( petEpitome, attrName )
		for attrName in self._magCombatAttrs.itervalues(): #法术战斗属性
			self.__setAttr( petEpitome, attrName )
		self.__pyLbLevel.text = petEpitome.level
		proSkills = [] # 职业技能
		genSkills = [] # 天赋技能
		self.__pyProSkillPanel.clearItems()
		self.__pyGenSkillPanel.clearItems()
		for skillID in petEpitome.skills:
			skillInfo = SkillItemInfo( Skill.getSkill( skillID ) )
			if skillInfo.isPassive:
				genSkills.append( skillInfo )
			else:
				proSkills.append( skillInfo )
		for index, skillInfo in enumerate ( genSkills ):
			self.__pyGenSkillPanel.initSkill( index, skillInfo )
		for index, skillInfo in enumerate ( proSkills ):
			self.__pyProSkillPanel.initSkill( index, skillInfo )
		modelNumber = petEpitome.modelNumber
		self.__pyPetImage.texture = g_npcmodel.getHeadTexture( modelNumber )
		self.__pyResistPanel.setUIState( 1 ) # 解锁UI
		player.si_changePet( dbid )

	def targetPetChange_( self, epitome ): # 对方宠物信息
		hierarchy = epitome.hierarchy #宠物辈分
		hierColor = ( 255, 255, 255, 255 )
		hierText = ""
		if formulas.isHierarchy( hierarchy, csdefine.PET_HIERARCHY_GROWNUP ): #成年宠物
			hierColor = ( 255, 255, 255, 255 )
			hierText = labelGather.getText( "petTrade:main", "miInfancy1" )
		elif formulas.isHierarchy( hierarchy, csdefine.PET_HIERARCHY_INFANCY1 ): #一代宝宝
			hierColor = ( 0, 0, 255, 255 )
			hierText = labelGather.getText( "petTrade:main", "miInfancy2" )
		else: #二代宝宝
			hierColor = ( 254, 163, 8, 255 )
			hierText = labelGather.getText( "petTrade:main", "miInfancy3" )
		self.pyPetsCB_.text = epitome.name
		for tag, tuple in self._baseAttrs.iteritems(): #血、蓝属性
			pyBaseItem = self.__pyBaseItems.get( tag )
			if pyBaseItem is None:return
			pyBaseItem.update( ( getattr( epitome, tuple[0] ), getattr( epitome, tuple[1] ) ) )
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
		self.__pyProSkillPanel.clearItems()
		self.__pyGenSkillPanel.clearItems()
		for skillID in epitome.skills:
			skillInfo = SkillItemInfo( Skill.getSkill( skillID ) )
			if skillInfo.isPassive:
				genSkills.append( skillInfo )
			else:
				proSkills.append( skillInfo )
		for index, skillInfo in enumerate ( genSkills ):
			self.__pyGenSkillPanel.initSkill( index, skillInfo )
		for index, skillInfo in enumerate ( proSkills ):
			self.__pyProSkillPanel.initSkill( index, skillInfo )
		outPet = BigWorld.player().pcg_getActPet()
		modelNumber = epitome.modelNumber
		self.__pyPetImage.texture = g_npcmodel.getHeadTexture( modelNumber )
		self.__pyLbLevel.text = str( epitome.level )
		self.__pyResistPanel.setUIState( 1 ) # 解锁UI

	def __setAttr( self, epitome, attrName ): # 设置宠物各属性
		dbid = epitome.databaseID
		for key, tuple in self._proAttrs.iteritems(): # 更新属性栏
			if attrName in tuple:
				if key in ["takeLevel", "ability"]: # 可携带等级
					value0 = -1
					value1 = getattr( epitome, tuple[1] )
				else:
					value0 = getattr( epitome, tuple[0] )
					value1 = getattr( epitome, tuple[1] )
				self.__pyAttrPanel.updateInfo( key, dbid, ( value0, value1 ) )
		for tag, attr in self._typeAttrs.iteritems(): # 更新类型，性别等
			if attrName == attr:
				value = getattr( epitome, attrName )
				self.__updateLabelInfo( epitome, tag, value )
		for key, tuple in self._comAttrs.iteritems(): # 更新可强化属性
			if attrName in tuple:
				if key == "freepoint": # 自由点
					value0 = -1
					value1 = getattr( epitome, tuple[1] )
				else:
					value0 = getattr( epitome, tuple[0] )
					value1 = getattr( epitome, tuple[1] )
				self.__pyPointPanel.updateInfo( key, epitome, ( int(value0), int(value1) ) )
		for tag, attr in self._resistAttrs.iteritems():
			if attrName == attr:
				value = getattr( epitome, attrName )
				self.__pyResistPanel.updateInfo( epitome, tag, value )
		for tag, attr in self._phCombatAttrs.iteritems():
			if attrName == attr:
				value = getattr( epitome, attrName )
				self.__pyPhyPanel.updateInfo( dbid, tag, value )
		for tag, attr in self._magCombatAttrs.iteritems():
			if attrName == attr:
				value = getattr( epitome, attrName )
				self.__pyMagPanel.updateInfo( dbid, tag, value )

	def __updateLabelInfo( self, epitome, tag, value ):
		if epitome is None:return
		for typeTag, pyLabel in self.__pyLabels.iteritems():
			if typeTag == tag:
				if typeTag == "isBreed":
					breedStr = self.__getLabelText( tag, value )
					pyLabel.text = "%s%s"%( self._pet_genders[epitome.gender], breedStr )
				else:
					pyLabel.text = self.__getLabelText( tag, value )

#			if tag == "basenimbus":
#				self.__pyLabels[tag].text = "初灵:%i"%value

	def __getLabelText( self, tag, value ):
		resultStr = ""
		btnTexts = self.__labelTexts.get( tag )
		if btnTexts is not None:
			for key, str in btnTexts.iteritems():
				if key == value:
					resultStr = str
					break
		return resultStr

# -----------------------------------------------------
class PhyPanel( PyGUI ): # tabCtr中的物理战斗属性
	def __init__( self, panel = None, pyBinder = None ):
		PyGUI.__init__( self, panel )

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setLabel( panel.panel.damage_item.stName, "petTrade:phyPanel", "damage_item" )
		labelGather.setLabel( panel.panel.recovery_item.stName, "petTrade:phyPanel", "recovery_item" )
		labelGather.setLabel( panel.panel.duck_item.stName, "petTrade:phyPanel", "duck_item" )
		labelGather.setLabel( panel.panel.blows_item.stName, "petTrade:phyPanel", "blows_item" )
		labelGather.setLabel( panel.panel.cruel_item.stName, "petTrade:phyPanel", "cruel_item" )
		labelGather.setLabel( panel.stTitle, "petTrade:phyPanel", "stTitle" )

		self.__initPanel( panel.panel )

	def __initPanel( self, panel ):
		self.__pyLabels = {}
		for name, item in panel.children:
			if "_item" not in name:continue
			tag = name.split("_")[0]
			pyItem = StaticText( item.lbValue )
			pyItem.text = ""
			pyItem.charSpace = -1
			pyItem.fontSize = 12
			pyItem.color = (255, 255, 255)
			self.__pyLabels[tag] = pyItem

	# -----------------------------------------
	def updateInfo( self, dbid, tag, value ):
		player = BigWorld.player()
		outPet = player.pcg_getActPetEpitome()
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
	def __init__( self, panel = None, pyBinder = None ):
		PyGUI.__init__( self, panel )

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setLabel( panel.panel.recovery_item.stName, "petTrade:magicPanel", "recovery_item" )
		labelGather.setLabel( panel.panel.duck_item.stName, "petTrade:magicPanel", "duck_item" )
		labelGather.setLabel( panel.panel.cruel_item.stName, "petTrade:magicPanel", "cruel_item" )
		labelGather.setLabel( panel.panel.damage_item.stName, "petTrade:magicPanel", "damage_item" )
		labelGather.setLabel( panel.stTitle, "petTrade:magicPanel", "stTitle" )

		self.__initPanel( panel.panel )

	def __initPanel( self, panel ):
		self.__pyLabels = {}
		for name, item in panel.children:
			if "_item" not in name:continue
			tag = name.split("_")[0]
			pyItem = StaticText( item.lbValue )
			pyItem.text = ""
			pyItem.charSpace = -1
			pyItem.fontSize = 12
			pyItem.color = (255, 255, 255)
			self.__pyLabels[tag] = pyItem

	#------------------------------------
	def updateInfo( self, dbid, tag, value ):
		player = BigWorld.player()
#		outPet = player.pcg_getActPetEpitome()
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

# -------------------------------------------------------
class PointPanel( PyGUI ):
	def __init__( self, panel = None, pyBinder = None ):
		PyGUI.__init__( self, panel )

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setLabel( panel.panel.freepoint_item.stName, "petTrade:pointPanel", "freepoint_item" )
		labelGather.setLabel( panel.panel.habitus_item.stName, "petTrade:pointPanel", "habitus_item" )
		labelGather.setLabel( panel.panel.agility_item.stName, "petTrade:pointPanel", "agility_item" )
		labelGather.setLabel( panel.panel.brains_item.stName, "petTrade:pointPanel", "brains_item" )
		labelGather.setLabel( panel.panel.force_item.stName, "petTrade:pointPanel", "force_item" )
		labelGather.setLabel( panel.stTitle, "petTrade:pointPanel", "stTitle" )

		self.__initPanel( panel.panel )

	def __initPanel( self, panel ):
		self.__pyItems ={}
		for name, item in panel.children:
			if "_item" not in name:continue
			tag = name.split( "_" )[0]
			pyItem = IntentifyItem( tag, item )
			self.__pyItems[tag] = pyItem

	def setUIState( self, num ):
		for pyItem in self.__pyItems.itervalues():
			pyItem.setState( num )

	def updateInfo( self, tag, epitome, tuple ):
		if self.__pyItems.has_key( tag ):
			pyItem = self.__pyItems[tag]
			pyItem.update( epitome, tuple )

# -------------------------------------------------
# -------------------------------------------------
from guis.controls.Icon import Icon

class IntentifyItem( Control ):
	def __init__( self, tag, item = None ):
		Control.__init__( self, item )
		self.__tag = tag
		self.__epitome = None
		self.__pyLbValue = StaticText( item.lbValue )
		self.__pyLbValue.text = ""
		self.__pyLbValue.charSpace = -1
		self.__pyLbValue.fontSize = 12
		self.__pyLbValue.color = (255, 255, 255)
		self.__pyLbFree = StaticText( item.lbFree )
		self.__pyLbFree.text = ""
		self.__pyLbFree.charSpace = -1
		self.__pyLbFree.fontSize = 12

		self.__pyTipsIcon = Icon( item.freeIcon )
		self.__pyTipsIcon.crossFocus = True
		self.__pyTipsIcon.onMouseEnter.bind( self.__showTips )
		self.__pyTipsIcon.onMouseLeave.bind( self.__hideTips )

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
		self.__pyLbFree.text =  "X" + str( tuple[1] )

# ------------------------------------------------------
from guis.controls.SkillItem import SkillItem as BaseItem
class SkillsPanel( PyGUI ):
	def __init__( self, skillsPanel = None, pyBinder = None ):
		PyGUI.__init__( self, skillsPanel )
		self.__initPanel( skillsPanel )
		self.__skills = {} # 保存技能属性

	def __initPanel( self, skillsPanel ): # 初始化技能图标
		self.__pyItems = {}
		for name, item in skillsPanel.children:
			if "item_" not in name : continue
			index = int( name.split( "_" )[1] )
			pyItem = BaseItem( item )
			pyItem.index = index
			self.__pyItems[index] = pyItem

	# ---------------------------------------------------------
	def getItem( self, index ) :
		if index < 0 : return None
		if index >= len( self.__pyItems ) : return None
		return self.__pyItems[index]

	def initSkill( self, index, itemInfo ): # 初始化技能
		if self.__pyItems.has_key( index ):
			pyItem = self.__pyItems[index]
			if not self.__skills.has_key( itemInfo.id ):
				self.__skills[itemInfo.id] = ( index, itemInfo )
				pyItem.update( itemInfo )

	def addSkill( self, itemInfo ):
		for index, pyItem in self.__pyItems.iteritems():
			if pyItem.itemInfo is None:
				pyItem.update( itemInfo )
				self.__skills[itemInfo.id] = ( index, itemInfo )
				break

	def removeSkill( self, skillID ): # 移除技能
		if self.__skills.has_key( skillID ):
			index, iteminfo = self.__skills.pop( skillID )
			if self.__pyItems.has_key( index ):
				pyItem = self.__pyItems[index]
				pyItem.update( None )

	def upateSkill( self, oldSkillID, newSkillInfo ): # 更新技能
		if self.__skills.has_key( oldSkillID ):
			index, iteminfo = self.__skills.pop( oldSkillID )
			if self.__pyItems.has_key( index ):
				pyItem = self.__pyItems[index]
				self.__skills[newSkillInfo.id] = ( index, newSkillInfo )
				pyItem.update( newSkillInfo )

	def clearItems( self ):
		self.__skills = {}
		for pyItem in self.__pyItems.itervalues():
			pyItem.update( None )

	# -------------------------------------------------
	def _getpyItems( self ):
		return self.__pyItems

	pyItems = property( _getpyItems )

# ----------------------------------------------------------------
from guis.controls.ProgressBar import HProgressBar as ProgressBar

class ResistPanel( PyGUI ):
	def __init__( self, panel = None, pyBinder = None ):
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

	def updateInfo( self, epitome, tag, value ):
		if self.__pyItems.has_key( tag ):
			pyItem = self.__pyItems[tag]
			pyItem.update( epitome, value )

	def clearItems( self ):
		for pyItem in self.__pyItems.itervalues():
			pyItem.update( 0.0 )

class ResistItem( ProgressBar ):

	_dsp_dict = eval( labelGather.getText( "petTrade:main", "dspDict" ) )

	def __init__( self, tag, resistItem ):
		ProgressBar.__init__( self, resistItem, pyBinder = None )
		self.__tag = tag
		self.crossFocus = True
		self.valStr = ""
		self.value = 0.0
		self.__epitome = None

	def __getDescription( self, tag):
		if self._dsp_dict.has_key( tag ):
			if self.__epitome is None: return
			dsp = self._dsp_dict[tag]%( self.__epitome.name, self.valStr )
			return dsp

	# ----------------------------------------------------------------------
	def onMouseEnter_( self ):
		Control.onMouseEnter_( self )
		dsp = self.__getDescription( self.tag )
		if dsp == "": return
		toolbox.infoTip.showToolTips( self, dsp )
		return True

	def onMouseLeave_( self ):
		Control.onMouseLeave_( self )
		toolbox.infoTip.hide()
		return True

	# ---------------------------------------------------------------
	def setState( self, num ):
		self.crossFocus = num > 0
		if num <= 0:
			self.value = num
			self.valStr = "%0.1f%%" % ( float(num)*100.0 )

	def update( self, epitome, value ):# 更新状态值
		rate = float( value )
		self.valStr = "%0.1f%%" % ( rate*100.0 )
		self.value = value
		self.__epitome = epitome

	# -------------------------------------------------------------------
	def _getTag( self ):

		return self.__tag

	def _setTag( self, tag ):

		self.__tag = tag

	tag = property( _getTag, _setTag )

# --------------------------------------------------------------------
from guis.controls.Control import Control
from guis.controls.ProgressBar import HProgressBar as ProgressBar

class PropertyItem( Control ):
	def __init__( self, tag, item = None ):
		Control.__init__( self, item )
		self.__tag = tag
		self.__dbid = -1
		self.__initItem( item )

	def __initItem( self, item ):
		self.__pyBar = ProgressBar( item.bar )
		self.__pyBar.value = 0.0
		self.__pyBar.clipMode = "RIGHT"

		self.__pyLbValue = StaticText( item.lbValue )
		self.__pyLbValue.text = ""
		self.__pyLbValue.color = (255, 255, 255)

	def onMouseEnter_( self ):
		Control.onMouseEnter_( self )
		return True

#	def setState( self, num ):
#		self.__pyPropertyBtn.enable = num > 0
#		if num == 0:
#			self.__pyHpBag.visible = False

	def update( self,tuple ):
		self.__pyLbValue.text = "%d/%d"%( tuple[0], tuple[1] )
		if tuple[1] == 0:
			self.__pyBar.value = 0
		else:
			self.__pyBar.value = float( tuple[0] )/tuple[1]
