# -*- coding: gb18030 -*-
#
# $Id: PetPanel.py $

"""
implement petpanel
"""
from guis import *
import ShareTexts
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.controls.TabCtrl import TabPanel
from guis.controls.ODComboBox import ODComboBox
from guis.controls.ComboBox import ComboItem
from guis.controls.ProgressBar import HProgressBar as ProgressBar
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from guis.tooluis.fulltext.FullText import FullText
import skills as Skill
from config.client.msgboxtexts import Datas as mbmsgs
from ItemsFactory import PetSkillItem as SkillItemInfo
from PetEnhance import PetEnhance
from PetModelRender import PetModelRender
from ChangeNamePanel import ChangeNamePanel
from AttributeItem import PropertyItem
from AttributeItem import ResistItem
from AttributeItem import EnhanceItem
from SkillItem import SkillItem
from PetCombine import PetCombine
from PetFormulas import formulas
import csstatus
import csdefine

# ----------------------------------------------------------------
# ������������ߴ�������
# ----------------------------------------------------------------
from AbstractTemplates import MultiLngFuncDecorator

class deco_PetResizePropertyItems( MultiLngFuncDecorator ) :

	@staticmethod
	def locale_big5( SELF ) :
		"""
		����������µ���������������ĳߴ�
		"""
		pyAttrItems = SELF._PetPanel__pyAttrItems
		for pyItem in pyAttrItems.itervalues() :
			pyItem._PropertyItem__pyStValue.charSpace = -1
			pyItem._PropertyItem__pyStValue.fontSize = 11


class PetPanel( TabPanel ):

	__baseAttrs = {} #��������
	__baseAttrs["name"]			= "name" 							# ����
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
	__proAttrs["joyancy"]			= ( "joyancy", "joyancyMax" ) 	# ���ֶ�
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
	__extrAttrs["isBinded"]		= "isBinded"

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
	__resistAttrs["fix"]		= "resistFixProbability"
	__resistAttrs["giddy"]		= "resistGiddyProbability"
	__resistAttrs["sleep"]		= "resistSleepProbability"
	__resistAttrs["hush"]		= "resistChenmoProbability"

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
				},
			"isBinded":
				{0:"",
				1:labelGather.getText( "PetsWindow:PetsPanel", "isBinded" ),
				},
			}

	_pet_hierarchy = { csdefine.PET_HIERARCHY_GROWNUP : ( labelGather.getText( "PetsWindow:PetsPanel", "hierarchy_grownup" ), ( 255, 255, 255, 255 ) ),
					   csdefine.PET_HIERARCHY_INFANCY1 : ( labelGather.getText( "PetsWindow:PetsPanel", "hierarchy_infancy1" ), ( 0, 0, 255, 255 ) ),
					   csdefine.PET_HIERARCHY_INFANCY2 : ( labelGather.getText( "PetsWindow:PetsPanel", "hierarchy_infancy2" ), ( 254, 163, 8, 255 ) ),
					   }

	def __init__( self, panel, pyBinder = None ):
		TabPanel.__init__( self, panel )

		#self.__pyChangeName = ChangeNamePanel( self )
		self.__pyPetCombine = PetCombine( self )
		self.__triggers = {}
		self.__registerTriggers()
		self.__turnModelCBID = 0
		self.__cancelCoverCBID = 0
		self.__selViewEpitome = None
		self.__invalidItems = []				# �����ü���
		self.__initialize( panel )
		self.__resizePropertyItems()			# ���ݵ�ǰ���԰汾�����������Եĳߴ�

		self.__pyMsgBox = None

	def __initialize( self, panel):
		self.__pyStPetsNum = StaticText( panel.stPetsNum )
		self.__pyStPetsNum.text = ""
		
		self.__pyStCombat = StaticText( panel.combatText )
		self.__pyStCombat.text = ""

		self.__pyPetRender = PetModelRender( panel.petRender ) 		#����ģ��

		self.__pyBtnLeft = Button( panel.btnLeft )					#ģ��������ת��ť
		self.__pyBtnLeft.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnLeft.onLMouseDown.bind( self.__turnLeft )

		self.__pyBtnRight = Button( panel.btnRight )				#ģ������ת��ť
		self.__pyBtnRight.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnRight.onLMouseDown.bind( self.__turnRight )

		self.__pyBtnChangName = HButtonEx( panel.btnRename )				#�������
		self.__pyBtnChangName.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnChangName.onLClick.bind( self.__onRenameName )
		labelGather.setPyBgLabel( self.__pyBtnChangName, "PetsWindow:PetsPanel", "renameBtn" )

		self.__pyBtnFeed = HButtonEx( panel.btnFeed )
		self.__pyBtnFeed.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnFeed.onLClick.bind( self.__onFeed )
		labelGather.setPyBgLabel( self.__pyBtnFeed, "PetsWindow:PetsPanel", "btnFeed" )

		self.__pyBtnDome = HButtonEx( panel.btnDome )
		self.__pyBtnDome.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnDome.onLClick.bind( self.__onDome )
		labelGather.setPyBgLabel( self.__pyBtnDome, "PetsWindow:PetsPanel", "btnDome" )

		self.__pyBtnRestore = HButtonEx( panel.btnRestore )
		self.__pyBtnRestore.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnRestore.onLClick.bind( self.__onRestor )
		labelGather.setPyBgLabel( self.__pyBtnRestore, "PetsWindow:PetsPanel", "btnRestore" )

		self.__pyBtnCombine = HButtonEx( panel.btnCombine )
		self.__pyBtnCombine.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCombine.enable = False
		self.__pyBtnCombine.onLClick.bind( self.__onCombine )
		labelGather.setPyBgLabel( self.__pyBtnCombine, "PetsWindow:PetsPanel", "btnCombine" )

		self.__pyBtnEnhance = HButtonEx( panel.btnEnhance )
		self.__pyBtnEnhance.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnEnhance.onLClick.bind( self.__onEnhance )
		labelGather.setPyBgLabel( self.__pyBtnEnhance, "PetsWindow:PetsPanel", "btnEnhance" )


		self.__pyBtnBattle = HButtonEx( panel.btnBattle )				#�����ս
		self.__pyBtnBattle.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnBattle.onLClick.bind( self.__onBattle )
		labelGather.setPyBgLabel( self.__pyBtnBattle, "PetsWindow:PetsPanel", "btnBattle" )

		self.__pyBtnWithdraw = HButtonEx( panel.btnWithdraw )			#�����ջ�
		self.__pyBtnWithdraw.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnWithdraw.onLClick.bind( self.__onWithdraw )
		labelGather.setPyBgLabel( self.__pyBtnWithdraw, "PetsWindow:PetsPanel", "btnWithdraw" )

		self.__pyBtnFree = HButtonEx( panel.btnFree )					#�������
		self.__pyBtnFree.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnFree.onLClick.bind( self.__onFree )
		labelGather.setPyBgLabel( self.__pyBtnFree, "PetsWindow:PetsPanel", "btnFree" )

		self.__pyCBPets = ODComboBox( panel.cbPets )					#���������б�
		self.__pyCBPets.autoSelect = True
		self.__pyCBPets.ownerDraw = True
		self.__pyCBPets.itemHeight = 25
		self.__pyCBPets.onViewItemInitialized.bind( self.onInitialized_ )
		self.__pyCBPets.onDrawItem.bind( self.onDrawItem_ )
		self.__pyCBPets.onItemSelectChanged.bind( self.__onPetSelected )

		self.__pyBaseAttrs = {}										#�������ԣ��Ա𡢳ɳ��ȵ�
		self.__pyExtrAtts = {}										#��չ���ԣ����Ը��
		self.__pySkItems = {}										#���＼��
		self.__pyAttrItems = {}										#��������
		self.__pyPhysAtrrs = {}										#��������ս������
		self.__pyMaggicAttrs = {}									#���﷨��ս������
		self.__pyEnhanceItems = {}									#ǿ������
		self.__pyResistItems = {}									#���￹��
		for name, item in panel.children:
			if name.startswith( "base_" ):
				tag = name.split( "_" )[1]
				pyStBase = StaticText( item )
				pyStBase.text = ""
				pyStBase.color = ( 255.0, 255.0, 255.0 )
				self.__pyBaseAttrs[tag] = pyStBase
			elif name.startswith( "extr_" ):
				tag = name.split( "_" )[1]
				pyStExtr = StaticText( item )
				pyStExtr.text = ""
				self.__pyExtrAtts[tag] = pyStExtr
			elif name.startswith( "skItem_" ):
				pySkItem = SkillItem( item )
				pySkItem.update( None )
				index = int( name.split( "_" )[1] )
				self.__pySkItems[index] = pySkItem
			elif name.startswith( "physics_" ):
				tag = name.split( "_" )[1]
				pyStPhyAttr = CombatAttr( item )
				pyStPhyAttr.text = ""
				pyStPhyAttr.title = labelGather.getText( "PetsWindow:PetsPanel", name )
				self.__pyPhysAtrrs[tag] = pyStPhyAttr
			elif name.startswith( "maggic_" ):
				tag = name.split( "_" )[1]
				pyStMaggicAttr = CombatAttr( item )
				pyStMaggicAttr.text = ""
				pyStMaggicAttr.title = labelGather.getText( "PetsWindow:PetsPanel", name )
				self.__pyMaggicAttrs[tag] = pyStMaggicAttr
			elif name.startswith( "resist_" ):
				tag = name.split( "_" )[1]
				pyItem = ResistItem( item )
				pyItem.tag = tag
				self.__pyResistItems[tag] = pyItem
			elif name.endswith( "_item" ):
				tag = name.split( "_" )[0]
				pyItem = PropertyItem( item )
				pyItem.update(( "--", "--" ))
				pyItem.name = labelGather.getText( "PetsWindow:PetsPanel", name )
				self.__pyAttrItems[tag] = pyItem
			elif name.endswith( "_enhance"):
				tag = name.split( "_" )[0]
				pyItem = EnhanceItem( item )
				pyItem.name = labelGather.getText( "PetsWindow:PetsPanel", name )
				pyItem.update(( -1, -1 ))
				self.__pyEnhanceItems[tag] = pyItem
		labelGather.setLabel( panel.nameText, "PetsWindow:PetsPanel", "nameText" )
		labelGather.setLabel( panel.takeNumText, "PetsWindow:PetsPanel", "takeNumText" )
		labelGather.setLabel( panel.abilityText, "PetsWindow:PetsPanel", "abilityText" )
		labelGather.setLabel( panel.levelText, "PetsWindow:PetsPanel", "levelText" )
		labelGather.setLabel( panel.skillText0, "PetsWindow:PetsPanel", "activeText0" )
		labelGather.setLabel( panel.skillText1, "PetsWindow:PetsPanel", "activeText1" )
		labelGather.setLabel( panel.skillText2, "PetsWindow:PetsPanel", "geniusText0" )
		labelGather.setLabel( panel.skillText3, "PetsWindow:PetsPanel", "geniusText1" )
		labelGather.setLabel( panel.magicBg.bgTitle.stTitle, "PetsWindow:PetsPanel", "magicAttr" )
		labelGather.setLabel( panel.physBg.bgTitle.stTitle, "PetsWindow:PetsPanel", "phyisAttr" )

	@deco_PetResizePropertyItems
	def __resizePropertyItems( self ) :
		"""
		���µ���������������ĳߴ�
		Ĭ�ϰ汾�²������κβ���
		"""
		pass

	def __registerTriggers( self ):
		self.__triggers["EVT_ON_PCG_ADD_PET"]		 	= self.__onPetAdded
		self.__triggers["EVT_ON_PCG_REMOVE_PET"]		= self.__onPetRemoved
		self.__triggers["EVT_ON_PET_ATTR_CHANGED"]	 	= self.__onAttrUpdate
		self.__triggers["EVT_ON_ENTITY_NAME_CHANGED"] 	= self.__onNameChange
		self.__triggers["EVT_ON_PCG_KEEPING_COUNT_CHANGED"] = self.__onPetAmountChange
		self.__triggers["EVT_ON_PET_ENTER_WORKLD"] 		= self.__onPetEnterWorld
		self.__triggers["EVT_ON_PET_LEAVE_WORLD"]		= self.__onPetLeaveWorld # ����leaveworldʱ����
		# ����������ջ�
		self.__triggers["EVT_ON_PET_CONJURED"]			= self.__onPetConjured
		self.__triggers["EVT_ON_PET_WITHDRAWED"]		= self.__onPetWithdraw
		self.__triggers["EVT_ON_PST_STORED_PET"] 		= self.__onStoredPet
		self.__triggers["EVT_ON_PCG_SHOW_COMBINE"]		= self.__onPetCombine # ����ϳ�
		self.__triggers["EVT_ON_PET_PCG_WITHDRAW"]		= self.__onPetWithdraws
		# ���＼��
		self.__triggers["EVT_ON_PET_ADD_SKILL"]			= self.__onAddSkill
		self.__triggers["EVT_ON_PET_REMOVE_SKILL"]		= self.__onRemoveSkill
		self.__triggers["EVT_ON_PET_UPDATE_SKILL"]		= self.__onUpdateSkill
		self.__triggers["EVT_ON_SHOW_PET_INVALID_COVER"] = self.__coverInvalidItem	# ��������ü���ʱ��ʾ��ɫ�߿�
		self.__triggers["EVT_ON_BEFORE_PET_ADD_SKILL"] = self.__clearPetSks	# �������ϵļ���
		self.__triggers["EVT_ON_PET_PANEL_REFRESH"] = self.__onRefresh    # ˢ�����
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		"""
		deregister all events
		"""
		for key in self.__triggers.iterkeys() :
			ECenter.deregisterEvent( key, self )
	# ------------------------------------------------------------------------
	# private
	# ------------------------------------------------------------------------
	def onInitialized_( self, pyViewItem ):
		pyPetEpitome = PetItem()
		pyPetEpitome.focus = False
		pyPetEpitome.crossFocus = False
		pyViewItem.addPyChild( pyPetEpitome )
		pyViewItem.pyPetEpitome = pyPetEpitome

	def onDrawItem_( self, pyViewItem ):
		pyPanel = pyViewItem.pyPanel
		if pyViewItem.selected :
			pyViewItem.pyPetEpitome.foreColor = pyPanel.itemSelectedForeColor			# ѡ��״̬�µ�ǰ��ɫ
			pyViewItem.color = pyPanel.itemSelectedBackColor				# ѡ��״̬�µı���ɫ
		elif pyViewItem.highlight :
			pyViewItem.pyPetEpitome.foreColor = pyPanel.itemHighlightForeColor		# ����״̬�µ�ǰ��ɫ
			pyViewItem.color = pyPanel.itemHighlightBackColor				# ����״̬�µı���ɫ
		else :
			pyViewItem.pyPetEpitome.foreColor = pyPanel.itemCommonForeColor
			pyViewItem.color = pyPanel.itemCommonBackColor
		pyPetEpitome = pyViewItem.pyPetEpitome
		pyPetEpitome.left = 1.0
		pyPetEpitome.top = 1.0
		petEpitome = pyViewItem.listItem
		pyPetEpitome.text = petEpitome.name

	def __onPetWithdraws( self ):
		"""
		���ﲻ�ܺ��ַ�ʽ���ն�����ˢ���� by����
		"""
		player = BigWorld.player()
		backToSel = self.__selViewEpitome
		for pyViewItem in self.__pyCBPets.pyViewItems:
			self.__onPetSelected( pyViewItem.itemIndex )
		self.__onPetSelected( backToSel.itemIndex )

	def __onPetAdded( self, petEpitome ):
		"""
		��ӳ���
		"""
		if not petEpitome in self.__pyCBPets.items:
			self.__pyCBPets.addItem( petEpitome )
		existNum = self.__pyCBPets.itemCount
		maxNum = BigWorld.player().pcg_getKeepingCount()
		self.__pyStPetsNum.text = "%d/%d"%( existNum, maxNum )
		self.__setUIsState( existNum )

	def __onPetRemoved( self, dbid ) :
		"""
		�Ƴ�����
		"""
		for petEpitome in self.__pyCBPets.items:
			if petEpitome.databaseID == dbid:
				self.__pyCBPets.removeItem( petEpitome )
		existNum = self.__pyCBPets.itemCount
		maxNum = BigWorld.player().pcg_getKeepingCount()
		self.__pyStPetsNum.text = "%d/%d"%( existNum, maxNum )
		self.__setUIsState( existNum )
		if existNum > 0:
			self.__onPetSelected( self.__pyCBPets.selIndex )
			selItem = self.__pyCBPets.selItem
			self.__pyCBPets.pyBox_.text = selItem.name
			for pyViewItem in self.__pyCBPets.pyViewItems:
				self.onDrawItem_( pyViewItem )
		else:
			self.clearPetAttr()
			self.__pyCBPets.pyBox_.text = ""
#		toolbox.infoTip.hideOperationTips( 0x004d )

	def __onPetAmountChange( self ):
		"""
		��Я�����������ı�
		"""
		existNum = self.__pyCBPets.itemCount
		maxNum = BigWorld.player().pcg_getKeepingCount()
		self.__pyStPetsNum.text = "%d/%d"%( existNum, maxNum )

	def __setUIsState( self, existNum ):
		"""
		���ݳ����������ý���
		"""
		self.__pyBtnChangName.enable = existNum > 0
		self.__pyBtnBattle.enable = existNum > 0
		self.__pyBtnFree.enable = existNum > 0
		self.__pyBtnFeed.enable = existNum > 0
		self.__pyBtnDome.enable = existNum > 0
		self.__pyBtnRestore.enable = existNum > 0
		self.__pyBtnCombine.enable = existNum > 0
		self.__pyBtnEnhance.enable = existNum > 0
		if existNum <= 0:
			self.__pyCBPets.text = ""

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

	def __onPetSelected( self, selIndex ):
		"""
		ѡ�������б�ĳ������
		"""
		if selIndex < 0:return
		selViewEpitome = self.__pyCBPets.pyViewItems[selIndex]
		if selViewEpitome is None:
			self.reset()
			return
		player = BigWorld.player()
		selEpitome = selViewEpitome.listItem
		self.__pyCBPets.pyBox_.text = selEpitome.name
		self.__selViewEpitome = selViewEpitome
		epitome = player.pcg_getPetEpitomes()[selEpitome.databaseID]
		self.__pyPetRender.resetModel( epitome.modelNumber.lower() )
		skills = getattr( epitome, "skills" )
		self.__setPetSkills( skills )
		toolbox.infoTip.hideOperationTips( 0x004b )
		for tuple in self.__proAttrs.itervalues(): #��������
			for attrName in tuple:
				self.__setPetAttrs( selEpitome.databaseID, attrName )
		for tuple in self.__enhanceAttrs.itervalues():#��ͨ����
			for attrName in tuple:
				self.__setPetAttrs( selEpitome.databaseID, attrName )
		for attrName in self.__extrAttrs.itervalues(): #��������
			self.__setPetAttrs( selEpitome.databaseID, attrName )
		for attrName in self.__baseAttrs.itervalues(): #��Ҫ����
			self.__setPetAttrs( selEpitome.databaseID, attrName )
		for attrName in self.__resistAttrs.itervalues(): #��������
			self.__setPetAttrs( selEpitome.databaseID, attrName )
		for attrName in self.__phCombatAttrs.itervalues(): #����ս������
			self.__setPetAttrs( selEpitome.databaseID, attrName )
		for attrName in self.__magCombatAttrs.itervalues(): #����ս������
			self.__setPetAttrs( selEpitome.databaseID, attrName )
		if player.pcg_getActPet() is None:return
		if selEpitome.databaseID != player.pcg_getActPet().databaseID:
			self.__pyBtnBattle.visible = True
			self.__pyBtnWithdraw.visble = False
			self.__pyBtnCombine.enable = False
			self.__pyBtnEnhance.enable = False
			self.__pyStCombat.text = ""
			self.__setSkillDragged()
		else:
			self.__pyBtnCombine.enable = True
			self.__pyBtnEnhance.enable = True
			self.__pyStCombat.text = labelGather.getText( "PetsWindow:PetsPanel", "joinBattle" )
			self.__setSkillDragged( True )

	def __onAttrUpdate( self, dbid, attrName ):
		"""
		���³���ĸ�����
		"""
		player = BigWorld.player()
		epitome = player.pcg_getPetEpitomes().get( dbid )
		pyViewItem = self.__getViewItem( dbid )
		if pyViewItem:
			pyPetEpitome = pyViewItem.pyPetEpitome
			petEpitome = pyViewItem.listItem
		if not epitome or not pyViewItem:return
		pyPetEpitome.text = epitome.name
		selItem = self.__pyCBPets.selItem
		if selItem.databaseID == dbid:
			self.__pyCBPets.pyBox_.text = epitome.name
		if attrName == "life":
			tuple = self.__proAttrs[attrName]
			value0 = getattr( epitome, tuple[0] )
			if value0 <= 0.0: #��ʾ�����ľ���־
				pyPetEpitome.markVisible = True
				pyPetEpitome.markState = ( 1, 2 )
		if attrName == "joyancy": # ���ֶȻ�Ӱ�����Ĺ���
			self.__onPetSelected( self.__selViewEpitome.itemIndex )
		if petEpitome is self.__pyCBPets.selItem:
			self.__setPetAttrs( dbid, attrName )

	def __getViewItem( self, dbid ):
		"""
		ͨ��dbid��ȡ���µĳ���
		"""
		for pyViewItem in self.__pyCBPets.pyViewItems:
			petEpitome = pyViewItem.listItem
			if petEpitome.databaseID == dbid:
				return pyViewItem
		return None

	def __setPetAttrs( self, dbid, attrName ):
		"""
		���¸�����
		"""
		player = BigWorld.player()
		outPetEpitome = player.pcg_getActPetEpitome()
		epitome = player.pcg_getPetEpitomes()[dbid]
		pyViewItem = self.__getViewItem( dbid )
		pyPetEpitome = pyViewItem.pyPetEpitome
		if epitome is None:
			epitome = self.__pyCBPets.selItem
		for key, tuple in self.__proAttrs.iteritems(): # ����������
			if attrName in tuple:
				value0 = getattr( epitome, tuple[0] )
				value1 = getattr( epitome, tuple[1] )
				if key == "life":
					if value0 <= 0.0: #��ʾ�����ľ���־
						pyPetEpitome.markVisible = True
						pyPetEpitome.markState = ( 1, 2 )
				self.__pyAttrItems[key].update( ( value0, value1 ) )
		for tag, attr in self.__extrAttrs.iteritems():
			if attrName == attr:
				value = getattr( epitome, attrName )
				if tag == "takeLevel":
					self.__pyExtrAtts[tag].text = labelGather.getText( "PetsWindow:PetEspial", "takeLevel" )%value
				else:
					self.__pyExtrAtts[tag].text = self.__getExtrText( tag, value )
		for key, tuple in self.__enhanceAttrs.iteritems(): # ���¿�ǿ������
			if attrName in tuple:
				if key == "freedom": # ���ɵ�
					value0 = -1
					value1 = getattr( epitome, tuple[1] )
				else:
					value0 = getattr( epitome, tuple[0] )
					value1 = getattr( epitome, tuple[1] )
				self.__pyEnhanceItems[key].update( ( value0, value1) )
		for tag, attr in self.__resistAttrs.iteritems():
			if attrName == attr:
				value = getattr( epitome, attrName )
				self.__pyResistItems[tag].update( value )
		for tag, attr in self.__phCombatAttrs.iteritems():
			if attrName == attr:
				value = getattr( epitome, attrName )
				pyPhysAtrr = self.__pyPhysAtrrs[tag]
				if tag in ["duck","cruel", "blows"]:
					pyPhysAtrr.text = "%0.1f%%" % ( value*100.0 )
				else:
					pyPhysAtrr.text = str( value )
		for tag, attr in self.__magCombatAttrs.iteritems():
			if attrName == attr:
				value = getattr( epitome, attrName )
				pyMaggicAttr = self.__pyMaggicAttrs[tag]
				if tag in ["duck","cruel", "blows"]:
					pyMaggicAttr.text = "%0.1f%%" % ( value*100.0 )
				else:
					pyMaggicAttr.text = str( value )
		if self.__baseAttrs.has_key( attrName ): # ������ͨ����
			name = self.__baseAttrs[attrName]
			value = getattr( epitome, name )
			pyStBase = self.__pyBaseAttrs.get( name, None )
			if pyStBase is None:return
			pyStBase = self.__pyBaseAttrs[name]
			valueStr = ""
			if name == "gender":
				if value == csdefine.GENDER_MALE:
					valueStr = ShareTexts.GENDER_UNIT_MALE
				else:
					valueStr = ShareTexts.GENDER_UNIT_FEMALE
			if name == "level":
				valueStr = labelGather.getText( "PetsWindow:PetEspial", "petLevel")%value
			if name == "species":
				hierText, hierColor = self._pet_hierarchy.get( csdefine.PET_HIERARCHY_MASK & value, ( labelGather.getText( "PetsWindow:PetStorage", "typeStr"), ( 255, 255, 255, 255 ) ) )
				pyStBase.color = hierColor
				valueStr = hierText
			if name == "ability":
				valueStr = "%d"%value
			pyStBase.text = valueStr

		if outPetEpitome is None: return
		else:
			if dbid != outPetEpitome.databaseID:
				self.__pyBtnBattle.visible = True
				self.__pyBtnWithdraw.visible = False
			else:
				self.__pyBtnWithdraw.visible = True
				self.__pyBtnBattle.visible = False

	def __setPetSkills( self, skills ):
		"""
		���³��＼��
		"""
		self.__clearPetSks()
		for skillID in skills:
			skillInfo = SkillItemInfo( Skill.getSkill( skillID ) )
			self.__onAddSkill( skillInfo )

	def __onStoredPet( self, pet ):
		"""
		�洢����
		"""
		player = BigWorld.player()
		epitomes = player.pcg_getPetEpitomes()

	def __onFeed( self ): # ���Ӿ���
		player = BigWorld.player()
		if not player.isRoleTrainGemActive() :
			player.statusMessage( csstatus.PET_GEM_IS_NOT_ACTIVE )
			return
		gemExp = player.getPetGemExp()
		if gemExp <= 0 :
			player.statusMessage( csstatus.PET_GEM_EXPERIENCE_EMPTY )
			return
		petEpitome = self.__pyCBPets.selItem
		if petEpitome is None:return
		databaseID = petEpitome.databaseID
		petEpitomes = player.pcg_getPetEpitomes()
		petEpitome = petEpitomes.get( databaseID, None )
		if petEpitome is None:return
		if player.level < petEpitome.level - 5 : 			# ����ȼ�����
			player.statusMessage( csstatus.PET_TRAIN_LEVEL_LIMIT )
			return
		value = formulas.getAbsorbExpUpper( petEpitome.level )
		if value > 0:
			player.cell.ptn_feedPetEXP( databaseID, value )
		else:
			player.statusMessage( csstatus.PET_TRAIN_CANT_FEED )

	def __onDome( self ):
		"""
		���ӿ��ֶ�
		"""
		if self.__selViewEpitome is None:return
		petEpitome = self.__selViewEpitome.listItem
		databaseID = petEpitome.databaseID
		epitome = BigWorld.player().pcg_getPetEpitomes()[databaseID]
		epitome.addJoyancy()
		return True

	def __onRestor( self ):
		"""
		��������
		"""
		if self.__selViewEpitome is None:return
		petEpitome = self.__selViewEpitome.listItem
		databaseID = petEpitome.databaseID
		epitome = BigWorld.player().pcg_getPetEpitomes()[databaseID]
		epitome.addLife()

	def __onCombine( self ):
		"""
		����ϳ�
		"""
		player = BigWorld.player()
		player.pcg_onShowCombineDialog()

	def __onEnhance( self ):
		"""
		����ǿ��
		"""
		if self.__selViewEpitome is None:return
		petEpitome = self.__selViewEpitome.listItem
		databaseID = petEpitome.databaseID
		rds.ruisMgr.petEnhance.show( databaseID, self )

	def __enableSelectButton( self ) :
		petCount = self.__pyCBPets.itemCount
		currIndex = self.__pyCBPets.selIndex
		self.__pyNextBtn.enable = currIndex < petCount - 1
		self.__pyFrontBtn.enable = currIndex > 0

	def __onPetConjured( self, dbid ):
		"""
		�����ս
		"""
		pyViewItem = self.__getViewItem( dbid )
		pyPetEpitome = pyViewItem.pyPetEpitome
		pyPetEpitome.markVisible = True
		pyPetEpitome.markState = ( 1, 1 )
		petEpitome = self.__selViewEpitome.listItem
		seldbid = petEpitome.databaseID
		self.__pyBtnCombine.enable = seldbid == dbid
		if seldbid == dbid:
			self.__pyBtnWithdraw.visible = True
			self.__pyBtnBattle.visible = False
		self.__pyBtnEnhance.enable = True
		self.__pyStCombat.text = labelGather.getText( "PetsWindow:PetsPanel", "joinBattle" )
		self.__setSkillDragged( True )
		toolbox.infoTip.hideOperationTips( 0x004c )

	def __onPetWithdraw( self, dbid ):
		"""
		�����ٻ�
		"""
		pyViewItem = self.__getViewItem( dbid )
		pyPetEpitome = pyViewItem.pyPetEpitome
		pyPetEpitome.markVisible = False
		self.__pyBtnCombine.enable = False
		self.__pyBtnEnhance.enable = False
		self.__pyStCombat.text = ""
		self.__setSkillDragged()

	def __onFree( self ):
		"""
		�������
		"""
		if self.__selViewEpitome is None:return
		epitome = self.__selViewEpitome.listItem
		isVendedPet = getattr( epitome, "isVended", False )
		isVendState = BigWorld.player().state == csdefine.ENTITY_STATE_VEND
		if isVendState and isVendedPet :
			# �������ڳ��ۣ����ܷ�����
			showAutoHideMessage( 3.0, 0x0ce2, "", MB_OK, pyOwner = self.pyBinder )
			return
		pet = epitome.getEntity()
		if pet is not None :									# ���Ҫ�����ĳ��ﴦ�ڳ���״̬(hyw--2009.07.18)
			if pet.getState() == csdefine.ENTITY_STATE_FIGHT :
				# "���ﴦ��ս���в��ܷ�����"
				showAutoHideMessage( 3.0, 0x0ce1, "", MB_OK, pyOwner = self.pyBinder )
				return
		name = epitome.name
		def query( rs_id ):
			if rs_id == RS_OK:
				epitome.free()
		# "ȷ���ѳ���%s����?"
		if self.__pyMsgBox is not None:
			self.__pyMsgBox.visible = False
			self.__pyMsgBox = None
		self.__pyMsgBox = showMessage( mbmsgs[0x0501] % name,"", MB_OK_CANCEL, query, pyOwner = self.pyBinder )

	def __onPetEnterWorld( self, dbid ):
		"""
		����EnterWorld
		"""
		player = BigWorld.player()
		outPetEpitome = player.pcg_getActPetEpitome()
		self.__pyBtnCombine.enable = True
		self.__pyBtnEnhance.enable = True
		self.__pyStCombat.text = labelGather.getText( "PetsWindow:PetsPanel", "joinBattle" )

	def __onPetLeaveWorld( self, dbid ):
		"""
		����LeaveWorld
		"""
		self.__pyBtnWithdraw.visible = False
		self.__pyBtnBattle.visible = True
		self.__pyBtnCombine.enable = False
		self.__pyBtnEnhance.enable = False
		self.__pyStCombat.text = ""

	def __onPetCombine( self, outPet, pets ):
		"""
		����ϳ�
		"""
		self.__pyPetCombine.onShow( outPet, pets, self )

	def __getExtrText( self, tag, value ):
		strResult = ""
		extrTexts = self.__extrTexture.get( tag, None )
		if extrTexts:
			for key, str in extrTexts.iteritems():
				if key == value:
					strResult = str
					break
		return strResult

	def __onPetTrainExpChange( self, value ):
		existNum = self.__pyCBPets.itemCount
		canFeed = int( value ) > 0 and  existNum > 0
		self.__pyBtnFeed.enable = canFeed

	def __onNameChange( self, entityID, name ):
		pass

	# ----------------------------���＼��-----------------------------
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

	def __onRefresh( self ):
		self.__onPetSelected( self.__selViewEpitome.itemIndex )
	
	def __onRemoveSkill( self, skillID ):
		"""
		�Ƴ�����
		"""
		for index, pySkItem in self.__pySkItems.items():
			itemInfo = pySkItem.itemInfo
			if itemInfo is None:continue
			if itemInfo.id == skillID:
				pySkItem.update( None )
				break

	def __onUpdateSkill( self, oldSkillID, newSkillInfo ):
		"""
		���¼���
		"""
		for index, pySkItem in self.__pySkItems.iteritems():
			itemInfo = pySkItem.itemInfo
			if itemInfo is None:continue
			if itemInfo.id == oldSkillID:
				pySkItem.update( newSkillInfo )

	def __coverInvalidItem( self, skillID ):
		"""
		��������ü���ʱ��ʾ��ɫ�߿�
		"""
		BigWorld.cancelCallback( self.__cancelCoverCBID )
		self.__hideInvalidCovers()
		for pyItem in self.__pySkItems.itervalues() :
			if pyItem.itemInfo is None : continue
			if pyItem in self.__invalidItems : continue
			if pyItem.itemInfo.id == skillID :
				self.__invalidItems.append( pyItem )
				toolbox.itemCover.showInvalidItemCover( pyItem.pySItem )
		self.__cancelCoverCBID = BigWorld.callback( 1, self.__hideInvalidCovers )		# �����1����Զ�����

	def __hideInvalidCovers( self ) :
		"""
		���ز����ü��ܵĺ�ɫ�߿�
		"""
		for pyItem in self.__invalidItems :
			toolbox.itemCover.hideItemCover( pyItem.pySItem )
		self.__invalidItems = []

	def __clearPetSks( self ):
		"""
		��������＼��
		"""
		for pyItem in self.__pySkItems.itervalues():
			pyItem.update( None )

	def __onRenameName( self ):
		"""
		�������
		"""
		petEpitome = self.__selViewEpitome.listItem
		ChangeNamePanel.instance().show( petEpitome.databaseID, self )

	def __onBattle( self ):
		"""
		�����ս
		"""
		petEpitome = self.__selViewEpitome.listItem
		toolbox.infoTip.hideOperationTips( 0x0042 )
		petEpitome.conjure()
		self.pyTopParent.clearIndications()

	def __onWithdraw( self ):
		"""
		�ٻس���
		"""
		player = BigWorld.player()
		petEpitome = self.__selViewEpitome.listItem
		petEntity = petEpitome.getEntity()
		if petEntity is None :return
		if not petEpitome.conjured:
			player.statusMessage( csstatus.PET_WITHDRAW_FAIL_NOT_OUT )
			return
		elif petEntity.state == csdefine.ENTITY_STATE_FIGHT:
			player.statusMessage( csstatus.PET_WITHDRAW_FAIL_IN_FIGHT )
			return
		self.__pyBtnBattle.visible = True
		self.__pyBtnWithdraw.visible = False
		petEpitome.withdraw()
		
	def __setSkillDragged( self, dragged = False ):
		"""
		ֻ�г�ս�ĳ��＼�ܲ��ܱ��϶�
		"""
		for item in self.__pySkItems.itervalues():
			item.setDragFocus( dragged )

	# ------------------------------------------------------------------
	# callbacks
	# -------------------------------------------------------------------
	def onShow( self ) :
		"""
		������ʾʱ������
		"""
		self.__pyPetRender.enableDrawModel()
		TabPanel.onShow( self )
		rds.helper.courseHelper.openWindow( "chongwushuxing_chuangkou" )

	def onHide( self ) :
		"""
		��������ʱ������
		"""
		TabPanel.onHide( self )
		self.__pyPetRender.disableDrawModel()
		toolbox.infoTip.hideOperationTips( 0x004b )
		toolbox.infoTip.hideOperationTips( 0x004c )
		toolbox.infoTip.hideOperationTips( 0x004d )

	def onMove( self, dx, dz ):
		pass
#		toolbox.infoTip.moveOperationTips( 0x004b )
#		toolbox.infoTip.moveOperationTips( 0x004c )
#		toolbox.infoTip.moveOperationTips( 0x004d )

	# --------------------------------------------------------------
	# public
	# --------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onTrigger( self ) :
		player = BigWorld.player()
		outPetEpitome = player.pcg_getActPetEpitome()
		self.__pyBtnWithdraw.visible = False
		existNum = self.__pyCBPets.itemCount
		maxNum = BigWorld.player().pcg_getKeepingCount()
		self.__pyStPetsNum.text = "%d/%d"%( existNum, maxNum )
		self.__setUIsState( existNum )
		selEpitome = None
		if outPetEpitome is None:
			self.__pyBtnBattle.visible = True
			self.__pyBtnWithdraw.visible = False
			self.__pyBtnEnhance.enable = False
			selEpitome = self.__pyCBPets.selItem
		else:
			dbid = outPetEpitome.databaseID
			pyViewItem = self.__getViewItem( dbid )
			if pyViewItem is None:return
			selEpitome = pyViewItem.listItem
			self.__pyCBPets.selItem = selEpitome
			self.__pyBtnWithdraw.visible = True
			self.__pyBtnBattle.visible = False
			self.__pyBtnEnhance.enable = True
		if selEpitome is None:return
#		toolbox.infoTip.showOperationTips( 0x004b, self.__pyCBPets )
#		toolbox.infoTip.showOperationTips( 0x004c, self.__pyBtnBattle )
#		toolbox.infoTip.showOperationTips( 0x004d, self.__pyBtnFree )
		self.__pyExtrAtts["takeLevel"].text = labelGather.getText( "PetsWindow:PetEspial", "takeLevel" )%selEpitome.takeLevel
		return True

	def setComIndex( self, index ):
		if index < 0 or index > self.__pyCBPets.itemCount - 1:
			return
		selIndex = self.__pyCBPets.selIndex
		if index == selIndex:return
		petEpitome = self.__pyCBPets.items[index]
		self.__pyCBPets.selItem = petEpitome			# ��������ᴥ��onItemSelectChanged��Ϣ

	def reset( self ):
		self.clearPetAttr()
		self.__pyCBPets.clearItems()
		self.__pyCBPets.pyBox_.text = ""

	def clearPetAttr( self ):
		self.__selViewEpitome = None
		self.__clearPetSks()
		self.__pyPetRender.clearModel()
		for pyStBase in self.__pyBaseAttrs.itervalues():
			pyStBase.text = ""
		for pyStExtr in self.__pyExtrAtts.itervalues():
			pyStExtr.text = ""
		for pyPhyAttr in self.__pyPhysAtrrs.itervalues():
			pyPhyAttr.text = ""
		for pyMaggAttr in self.__pyMaggicAttrs.itervalues():
			pyMaggAttr.text = ""
		for pyEnhanceItem in self.__pyEnhanceItems.itervalues():
			pyEnhanceItem.update(( -1, -1 ))
		for pyResistItem in self.__pyResistItems.itervalues():
			pyResistItem.update( 0 )
		for pyAttrItem in self.__pyAttrItems.itervalues():
			pyAttrItem.update(( "--", "--" ))

	def indiacteSummonPet( self, idtId ) :
		"""
		ָ������ٻ�����
		"""
		if self.__pyBtnBattle.rvisible :
			toolbox.infoTip.showHelpTips( idtId, self.__pyBtnBattle )
			self.pyTopParent.addVisibleOpIdt( idtId )

# -----------------------------------------------------------------
class PetItem( ComboItem ):
	def __init__( self ) :
		item = GUI.load( "guis/general/petswindow/petitem.gui" )
		uiFixer.firstLoadFix( item )
		ComboItem.__init__( self, item = item )
		self.__initialize( item )

	def __initialize( self, item ) :
		self.__pyMark = PyGUI( item.outMark )
		self.__pyMark.visible = False

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onStateChanged_( self, state ) :
		pass

	def onMouseEnter_( self ) :
		"""
		after mouse entered, will be called
		"""
		ComboItem.onMouseEnter_( self )
		if self.pyText_.width > self.width - self.pyText_.left :
			FullText.show( self, self.pyText_ )
		return True

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getMarkVisible( self ) :
		return self.__pyMark.visible

	def _setMarkVisible( self, visible ) :
		self.__pyMark.visible = visible

	# -------------------------------------------------
	def _getMarkState( self ):
		return util.getStateMapping( self.__pyMark.getGui().size, ( 1, 2 ), ( 1, 1 ) )

	def _setMarkState( self, state ):
		util.setGuiState( self.__pyMark.getGui(), ( 1, 2 ), state )

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	markVisible = property( _getMarkVisible, _setMarkVisible )
	markState = property( _getMarkState, _setMarkState )

class CombatAttr( PyGUI ):
	def __init__( self, attrItem ):
		PyGUI.__init__( self, attrItem )
		self.__pyStValue = StaticText( attrItem.stValue )
		self.__pyStValue.color = ( 255.0, 255.0, 255.0 )
		self.__pyStValue.text = ""

		self.__pyTitleText = StaticText( attrItem.titleText )
		self.__pyTitleText.color = ( 236.0, 218.0, 157.0 )

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
