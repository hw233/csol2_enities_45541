# -*- coding: gb18030 -*-
# implement display and combat setting panel
# written by ganjinxing 2009-9-29


from guis import *
from guis.controls.TabCtrl import TabPanel
from guis.controls.RichText import RichText
from guis.controls.CheckBox import CheckBoxEx
from guis.controls.RadioButton import RadioButtonEx
from guis.controls.CheckerGroup import CheckerGroup
from guis.controls.Label import Label
import event.EventCenter as ECenter
from LabelGather import labelGather

class BaseInfoPanel( TabPanel ):

	_CKBOX = ResMgr.openSection( "guis_v2/controls/checkbox/medium/leftbox.gui" )
	_RDBOX = ResMgr.openSection( "guis/controls/radiobutton/bigger1/leftbtn.gui" )

	def __init__( self, panel, pyBinder ):
		TabPanel.__init__( self, panel, pyBinder )

		self.pyCheckers_ = {}
		self.radioGroups_ = {}
		self.tmpInfoKeys_ = set()

		self.triggers_ = {}
		self.registerTriggers_()
		self.initialize_( panel )

		self.changed = False

	def initialize_( self, panel ):
		pass

	def initElements_( self, elmsMap, module ) :
		"""
		初始化界面元素
		"""
		elmFactory = {
					'ckbox'		 : self.createChecker_,
					'radiobox'	 : self.createRadioBox_
					}
		for ( posX, posY, h_space, v_space, colCount ), elmsList in elmsMap.iteritems() :
			currRow = 0
			for index, ( keyStr, text ) in enumerate( elmsList ) :
				currCol = index % colCount
				elmInfo = keyStr.split( "_" )
				pyElm = elmFactory[ elmInfo[0] ]( elmInfo )
				pyElm.text = labelGather.getText( module, text )
				pyElm.left = posX + currCol * h_space
				pyElm.top = posY + currRow * v_space
				currRow += currCol == colCount - 1 and 1 or 0

	def createChecker_( self, elmInfo ) :
		"""
		创建一个可选项
		"""
		infoKey, itemKey = elmInfo[1], elmInfo[2]
		self.tmpInfoKeys_.add( (infoKey, itemKey) )
		ckGui = GUI.load( "guis_v2/controls/checkbox/medium/leftbox.gui" )
		uiFixer.firstLoadFix( ckGui )
		ckGui.textureName = ""
		pyChecker = CheckBoxEx( ckGui )
		pyChecker.clickCheck = False
		pyChecker.infoKey = infoKey
		pyChecker.itemKey = itemKey
		pyChecker.onLClick.bind( self.onCheckBoxClick_ )
		self.pyCheckers_[( infoKey, itemKey )] = pyChecker
		self.addPyChild( pyChecker )
		return pyChecker

	def createRadioBox_( self, elmInfo ) :
		"""
		创建一个单选项
		"""
		infoKey, itemKey, mark = elmInfo[1], elmInfo[2], elmInfo[3]
		self.tmpInfoKeys_.add( (infoKey, itemKey) )
		rdBox = GUI.load( "guis_v2/controls/radiobutton/medium/leftbtn.gui" )
		uiFixer.firstLoadFix( rdBox )
		rdBox.textureName = ""
		pyRadioBtn = RadioButtonEx( rdBox )
		pyRadioBtn.infoKey = infoKey
		pyRadioBtn.itemKey = itemKey
		pyRadioBtn.tmpBehave = bool( int( mark ) )
		pyRadioBtn.onLClick.bind( self.onRadioBtnClick_ )
		if ( infoKey, itemKey ) in self.radioGroups_ :
			self.radioGroups_[( infoKey, itemKey )].addChecker( pyRadioBtn )
		else :
			self.radioGroups_[( infoKey, itemKey )] = CheckerGroup()
			self.radioGroups_[( infoKey, itemKey )].addChecker( pyRadioBtn )
		self.addPyChild( pyRadioBtn )
		return pyRadioBtn
	
	def createHChecker_( self, elmInfo ):
		infoKey, itemKey = elmInfo[1], elmInfo[2]
		self.tmpInfoKeys_.add( (infoKey, itemKey) )
		ckGui = GUI.load( "guis/general/syssetting/helpCKBox.gui" )
		uiFixer.firstLoadFix( ckGui )
		pyHChecker = HCheckBoxEx( ckGui )
		pyHChecker.clickCheck = False
		pyHChecker.infoKey = infoKey
		pyHChecker.itemKey = itemKey
		pyHChecker.onLClick.bind( self.onCheckBoxClick_ )
		self.pyCheckers_[( infoKey, itemKey )] = pyHChecker
		self.addPyChild( pyHChecker )
		return pyHChecker

	def registerTriggers_( self ):
		self.triggers_["EVT_ON_VIEWINFO_CHANGED"] = self.onViewInfoChange_
		for key in self.triggers_.iterkeys() :
			ECenter.registerEvent( key, self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __unregisterTriggers( self ) :
		for key in self.triggers_.iterkeys() :
			ECenter.unregisterEvent( key, self )


 	# ----------------------------------------------------------------
 	# protected
 	# ----------------------------------------------------------------
	def onViewInfoChange_( self, infoKey, itemKey, oldValue, newValue ):
		pyChecker = self.pyCheckers_.get( ( infoKey, itemKey ), None )
		if pyChecker is not None :
			pyChecker.checked = newValue
		else :
			pyRadioGroup = self.radioGroups_.get( ( infoKey, itemKey ), None )
			if pyRadioGroup is not None :
				for pyRadio in pyRadioGroup.pyCheckers:
					if pyRadio.tmpBehave == newValue:
						pyRadioGroup.pyCurrChecker = pyRadio

	def onCheckBoxClick_( self, pyChecker ):
		infoKey = pyChecker.infoKey
		itemKey = pyChecker.itemKey
		value = rds.viewInfoMgr.getSetting( infoKey, itemKey )
		rds.viewInfoMgr.changeSetting( infoKey, itemKey, not value )
		self.changed = True
		ECenter.fireEvent( "EVT_ON_BASEINFO_CHANGED", self.changed )

	def onRadioBtnClick_( self, pyRadio ) :
		infoKey = pyRadio.infoKey
		itemKey = pyRadio.itemKey
		rds.viewInfoMgr.changeSetting( infoKey, itemKey, pyRadio.tmpBehave )
		self.changed = True
		ECenter.fireEvent( "EVT_ON_BASEINFO_CHANGED", self.changed )

	# ---------------------------------------------------------------------
	# public
	# ---------------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.triggers_[macroName]( *args )

	def setDefault( self ) :
		"""
		将各选项恢复默认设置
		"""
		for infoKey, itemKey in self.tmpInfoKeys_ :
			rds.viewInfoMgr.setToDefault( infoKey, itemKey )
		self.changed = False
		ECenter.fireEvent( "EVT_ON_BASEINFO_CHANGED", self.changed )

	def onApplied( self ) :
		rds.viewInfoMgr.save()
		self.changed = False
		ECenter.fireEvent( "EVT_ON_BASEINFO_CHANGED", self.changed )

	def onOK( self ) :
		self.__unregisterTriggers()

	def onCancel( self ) :
		self.__unregisterTriggers()

	def onEnterWorld( self ) :
		for ( infoKey, itemKey ), pyChecker in self.pyCheckers_.iteritems():
			value = rds.viewInfoMgr.getSetting( infoKey, itemKey )
			pyChecker.checked = value
		for ( infoKey, itemKey ), pyRadioGroup in self.radioGroups_.iteritems() :
			value = rds.viewInfoMgr.getSetting( infoKey, itemKey )
			for pyRadio in pyRadioGroup.pyCheckers:
				if pyRadio.tmpBehave == value:
					pyRadioGroup.pyCurrChecker = pyRadio

	def onActivated( self ) :
		"""
		所属窗口激活时被调用
		"""
		pass

	def onInactivated( self ) :
		pass

	def hide( self ):
		self.__unregisterTriggers()
		BaseInfoPanel._CKBOX = None
		BaseInfoPanel._RDBOX = None
		self.triggers_=None


class CombatPanel( BaseInfoPanel ) :

	def __init__( self, pyBinder = None ) :
		self.__rtElms = []
		panel = GUI.load( "guis/general/syssetting/combat.gui" )
		uiFixer.firstLoadFix( panel )
		BaseInfoPanel.__init__( self, panel, pyBinder )

	def initialize_( self, panel ):
		elmsMap = {
			( 15, 25, 150, 0, 2 ) : [
				( "hckbox_roleCombat_skillName", "combat_skillName", "roleCombat_skillName_dsp" ),
				( "hckbox_roleCombat_statusInfo", "combat_statusInfo", "roleCombat_statusInfo_dsp" ),
				( "hckbox_roleCombat_hitDamage", "combat_hitDamage", "roleCombat_hitDamage_dsp" ),
				( "hckbox_roleCombat_expObtain", "combat_expObtain", "roleCombat_expObtain_dsp" ),
				( "hckbox_roleCombat_revertUpLmt", "combat_revertUpLmt", "roleCombat_revertUpLmt_dsp" ),
				( "hckbox_roleCombat_baseInfo", "combat_baseInfo", "roleCombat_baseInfo_dsp" ),
				],#( 26, 38 )
			( 15, 145, 150, 0, 2 ) : [
				( "hckbox_petCombat_skillName", "combat_skillName", "petCombat_skillName_dsp" ),
				( "hckbox_petCombat_statusInfo", "combat_statusInfo", "petCombat_statusInfo_dsp" ),
				( "hckbox_petCombat_hitDamage", "combat_hitDamage", "petCombat_hitDamage_dsp" ),
				( "hckbox_petCombat_expObtain", "combat_expObtain", "petCombat_expObtain_dsp" ),
				( "hckbox_petCombat_revertUpLmt", "combat_revertUpLmt", "petCombat_revertUpLmt_dsp" ),
				( "hckbox_petCombat_baseInfo", "combat_baseInfo", "petCombat_baseInfo_dsp" ),
				],
			( 15, 265, 150, 0, 2 ) : [
				( "hckbox_targetCombat_skillName", "combat_skillName", "targetCombat_skillName_dsp" ),
				( "hckbox_targetCombat_statusInfo", "combat_statusInfo", "targetCombat_statusInfo_dsp" ),
				( "hckbox_targetCombat_hitDamage", "combat_hitDamage", "targetCombat_hitDamage_dsp" ),
				( "hckbox_targetCombat_revertUpLmt", "combat_revertUpLmt", "targetCombat_revertUpLmt_dsp" ),
				( "hckbox_targetCombat_baseInfo", "combat_baseInfo", "targetCombat_baseInfo_dsp" ),
				],
			( 15, 385, 0, 0, 1 ) : [
				( "hckbox_fightControl_counter", "fightControl_counter", "fightControl_counter_dsp" ),
				],
		}
		self.initElements_( elmsMap, "gamesetting:cmtPl" )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setLabel( panel.frame_roleInfo.bgTitle.stTitle, "gamesetting:cmtPl", "cbtRoleInfo" )
		labelGather.setLabel( panel.frame_petInfo.bgTitle.stTitle, "gamesetting:cmtPl", "cbtPetInfo" )
		labelGather.setLabel( panel.frame_targetInfo.bgTitle.stTitle, "gamesetting:cmtPl", "cbtTargetInfo" )
		labelGather.setLabel( panel.frame_AF.bgTitle.stTitle, "gamesetting:cmtPl", "cbtCtrlTitle" )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def initElements_( self, elmsMap, module ) :
		"""
		重写初始化界面元素的方法
		"""
		elmFactory = {
					'ckbox'		 : self.createChecker_,
					'radiobox'	 : self.createRadioBox_,
					'hckbox'	 : self.createHChecker_,
					}
		for ( posX, posY, h_space, v_space, colCount ), elmsList in elmsMap.iteritems() :
			currTop = posY
			for index, ( keyStr, text, dsp ) in enumerate( elmsList ) :
				currCol = index % colCount
				elmInfo = keyStr.split( "_" )
				pyElm = elmFactory[ elmInfo[0] ]( elmInfo )
				pyElm.text = labelGather.getText( module, text )
				pyElm.left = posX + currCol * h_space
				pyElm.top = currTop
				currTop = currCol == colCount - 1 and pyElm.bottom + 7 or currTop
				if dsp :
					pyElm.dsp = labelGather.getText( module, dsp )

class DisplayPanel( BaseInfoPanel ) :

	def __init__( self, pyBinder = None ) :
		panel = GUI.load( "guis/general/syssetting/display.gui" )
		uiFixer.firstLoadFix( panel )
		BaseInfoPanel.__init__( self, panel, pyBinder )

	def initialize_( self, panel ):
		#rds.shortcutMgr.setHandler( "FIXED_TOGGLE_DROPITEM_NAME", self.__handleLAltEvent )
		elmsMap = {
			( 15, 32, 115, 25, 3 ) : [						# ( posX, posY, h_space, v_space, colCount )
				( "ckbox_npc_name", "npc_name" ), ( "ckbox_npc_title", "npc_title" ),
				],#( 26, 24 )
			( 15, 90, 115, 25, 3 ) : [
				( "ckbox_monster_name", "monster_name" ),( "ckbox_monster_level", "monster_level" ), ( "ckbox_monster_HP", "monster_HP"),
				( "ckbox_monster_persistence", "monster_persistence" ),
				],#( 26, 83 )
			( 15, 173, 185, 28, 2 ) : [
				( "ckbox_dropItem_particle", "dropItem_particle" ), ( "ckbox_hide_centerMessage", "hide_centerMessage"),
				],#( 26, 167 )
			( 15, 245, 115, 25, 3 ) : [
				( "ckbox_entitySigns_teammate", "entitySigns_teammate" ),( "ckbox_entitySigns_npc", "entitySigns_npc" ), ( "ckbox_entitySigns_monster", "entitySigns_monster"),
				],#( 26, 229 )
			( 15, 318, 115, 25, 3 ) : [
				( "ckbox_hideQuickBar_valid", "hideQuickBar_valid" ),
				],#( 26, 288 )
			( 15, 385, 185, 28, 2 ) : [
				( "ckbox_bubble_visible", "bubble_visible" ),( "radiobox_bubble_style_0", "bubble_style_0"),
				( "ckbox_chat_welkinAndTunel", "chat_welkinAndTunel" ),( "radiobox_bubble_style_1", "bubble_style_1" ),
				],#( 26, 357 )
		}
		self.initElements_( elmsMap, "gamesetting:dspPl" )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setLabel( panel.frame_qbInfo.bgTitle.stTitle, "gamesetting:dspPl", "stQBTitle" )
		labelGather.setLabel( panel.frame_posInfo.bgTitle.stTitle, "gamesetting:dspPl", "stPosTitle" )
		labelGather.setLabel( panel.frame_dropItem.bgTitle.stTitle, "gamesetting:dspPl", "stDropTitle" )
		labelGather.setLabel( panel.frame_mstInfo.bgTitle.stTitle, "gamesetting:dspPl", "stMstTitle" )
		labelGather.setLabel( panel.frame_npcInfo.bgTitle.stTitle, "gamesetting:dspPl", "stNPCTitle" )
		labelGather.setLabel( panel.frame_chatBubble.bgTitle.stTitle, "gamesetting:dspPl", "stBubTitle" )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __handleLAltEvent( self ):
		pass


class RoleInfoPanel( BaseInfoPanel ) :

	def __init__( self, pyBinder = None ) :
		panel = GUI.load( "guis/general/syssetting/roleInfo.gui" )
		uiFixer.firstLoadFix( panel )
		BaseInfoPanel.__init__( self, panel, pyBinder )

	def initialize_( self, panel ):
		elmsMap = {
			( 15, 32, 115, 36, 3 ) : [
				( "ckbox_player_name", "player_name" ), ( "ckbox_player_title", "player_title" ), ( "ckbox_player_HP", "player_HP" ),
				( "ckbox_player_guild", "player_guild" ), ( "ckbox_playerPet_name", "playerPet_name" ),
				( "ckbox_playerPet_HP", "playerPet_HP" ), ( "ckbox_player_sign", "player_sign" ),
				],
			( 15, 180, 115, 36, 3 ) : [
				( "ckbox_teammate_name", "teammate_name" ), ( "ckbox_teammate_title", "teammate_title" ), ( "ckbox_teammate_HP", "teammate_HP" ),
				( "ckbox_teammate_guild", "teammate_guild" ), (  "ckbox_teammate_model", "teammate_model" ), ( "ckbox_teammate_sign", "teammate_sign" ),
				( "ckbox_teammatePet_name", "teammatePet_name" ), ( "ckbox_teammatePet_HP", "teammatePet_HP" ), ( "ckbox_teammatePet_model", "teammatePet_model" ),
				],
			( 15, 326, 115, 36, 3 ) : [
				( "ckbox_role_name", "role_name" ), ( "ckbox_role_title", "role_title" ), ( "ckbox_role_HP", "role_HP" ),
				( "ckbox_role_guild", "role_guild" ), (  "ckbox_role_model", "role_model" ), ( "ckbox_role_sign", "role_sign" ),
				( "ckbox_pet_name", "pet_name" ), ( "ckbox_pet_HP", "pet_HP" ), ( "ckbox_pet_model", "pet_model" ),
				],
		}
		self.initElements_( elmsMap, "gamesetting:roleInfo" )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setLabel( panel.frame_tmInfo.bgTitle.stTitle, "gamesetting:roleInfo", "stTMTitle" )
		labelGather.setLabel( panel.frame_selfInfo.bgTitle.stTitle, "gamesetting:roleInfo", "stSelfTitle" )
		labelGather.setLabel( panel.frame_otherInfo.bgTitle.stTitle, "gamesetting:roleInfo", "stOtherTitle" )

class HCheckBoxEx( CheckBoxEx ):
	def __init__( self, hckbox ):
		CheckBoxEx.__init__( self, hckbox )
		self.dsp = ""
		self.__pyLbHelp = Label( hckbox.lbHelp )
		self.__pyLbHelp.text = "(?)"
		self.__pyLbHelp.commonForeColor = 255, 255, 255, 255
		self.__pyLbHelp.highlightForeColor = 255.0, 251.0,182.0
		self.__pyLbHelp.pressedForeColor = 255.0, 251.0,182.0
		self.__pyLbHelp.onMouseEnter.bind( self.__onShowHelp )
		self.__pyLbHelp.onMouseLeave.bind( self.__onHideHelp )
		self.__pyLbHelp.onLClick.bind( self.__onHideHelp )
	
	def __onShowHelp( self ):
		toolbox.infoTip.showToolTips( self, self.dsp )
	
	def __onHideHelp( self ):
		toolbox.infoTip.hide()

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	def _setText( self, text ):
		CheckBoxEx._setText( self, text )
		self.__pyLbHelp.left = self.pyText_.right + 5.0
		self.width = self.__pyLbHelp.right + 2.0

	text = property( CheckBoxEx._getText, _setText )