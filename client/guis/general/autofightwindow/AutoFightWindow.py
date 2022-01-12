# -*- coding: gb18030 -*-
#
# $Id: AutoFightWindow.py,v 1.5 2008-07-24 09:40:16 wangshufeng Exp $

"""
implement autofight window
"""
from guis import *
from cscustom import Rect
import Language
from AbstractTemplates import MultiLngFuncDecorator
from LabelGather import labelGather
from guis.common.Window import Window
from guis.common.FrameEx import HVFrameEx
from guis.common.PyGUI import PyGUI
from guis.controls.ButtonEx import HButtonEx
from guis.controls.CheckBox import CheckBoxEx
from guis.controls.TextBox import TextBox
from guis.controls.RadioButton import RadioButtonEx
from guis.controls.CheckerGroup import CheckerGroup
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from PlusSkillSet import PlusSkillSet
from PickupSet import PickupSet
import csstatus
import Const
import Font

class deco_InitTextFont( MultiLngFuncDecorator ) :

	@staticmethod
	def locale_big5( SELF, pyRestores ) :
		"""
		繁体版下重新调整部分属性字体的尺寸
		"""
		for pyRestore in pyRestores.values():
			pyRestore.pyChecker.charSpace = -1.0


class AutoFightWindow( Window ) :
	__instance = None

	auto_radius = { "small": 30,
				"midd": 60,
				"big": 0
	}

	check_dsps = { "Role_HP": labelGather.getText( "AutoFightWindow:main", "Role_HP"),
			"Role_MP": labelGather.getText( "AutoFightWindow:main", "Role_MP"),
			"Pet_HP": labelGather.getText( "AutoFightWindow:main", "Pet_HP"),
			"Pet_MP": labelGather.getText( "AutoFightWindow:main", "Pet_MP"),
			"Pet_Joyancy": labelGather.getText( "AutoFightWindow:main", "Pet_Joyancy"),
			"Equip_Repair": labelGather.getText( "AutoFightWindow:main", "Equip_Repair")
			}

	def __init__( self ) :
		assert AutoFightWindow.__instance is None,"AutoFightWindow instance has been created"
		AutoFightWindow.__instance=self
		wnd = GUI.load( "guis/general/autofightwindow/wnd.gui" )
		if Language.LANG == Language.LANG_BIG5:
			wnd = GUI.load( "guis/general/autofightwindow/wnd_big5.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.__autoPickup = True
		self.__autoPlus = True
		self.__autoConjure = True
		self.__autoRadius = 30
		self.__autoResue = False
		self.__autoRepair = False
		self.__triggers = {}
		self.__registerTriggers()
		self.__pyRtWarnResue = None
		self.__pyAutoResue = None
		self.__initialize( wnd )
		self.addToMgr("autoFightWindow")

	def __del__(self):
		"""
		just for testing memory leak
		"""
		if Debug.output_del_AutoFightWindow :
			INFO_MSG( str( self ) )

	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_AUTOFIGHT_WINDOW"] = self.__toggleAuotFightWindow
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __unregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )

	def __initialize( self, wnd ) :
		"""
		初始化界面
		"""
		labelGather.setPyLabel( self.pyLbTitle_, "AutoFightWindow:main", "lbTitle" )
		self.__pyRestores = {}
		self.__pyRadiusGroup = CheckerGroup()
		self.__pyPluses = {}
		self.__pyMediaFrame = HVFrameEx( wnd.medicaFrm )
		self.__pySkSetPanel = PyGUI( wnd.assistFrm )
		for name, item in wnd.medicaFrm.children:
			if name.startswith( "Role_" ) or \
				name.startswith( "Pet_" ): #恢复状态
				pyRestore = RestoreItem( item )
				pyRestore.tag = name
				pyRestore.dsp = self.check_dsps.get( name, "" )
				self.__pyRestores[name] = pyRestore
		for name, item in wnd.assistFrm.children:
			if name.startswith( "bound_" ): #设置自动战斗范围
				radiusTag = name.split( "_" )[1]
				pyRadius = RadioButtonEx( item )
				labelGather.setPyLabel( pyRadius, "AutoFightWindow:main", name )
				pyRadius.radius = self.auto_radius.get( radiusTag, 0 )
				self.__pyRadiusGroup.addChecker( pyRadius )
			if name.startswith( "plus_" ): #增益技能对象
				index = int( name.split( "_" )[1] )
				pyPlus = CheckBoxEx( item )
				labelGather.setPyLabel( pyPlus, "AutoFightWindow:main", name )
				self.__pyPluses[index] = pyPlus
		self.__pyRadiusGroup.onCheckChanged.bind( self.__onAutoRadiusChange )

		if hasattr( wnd.assistFrm, "Equip_Repair" ):
			pyEquipRest = RestoreItem( wnd.assistFrm.Equip_Repair )
			pyEquipRest.tag = "Equip_Repair"
			pyEquipRest.dsp = self.check_dsps.get( pyEquipRest.tag, "" )
			self.__pyRestores[pyEquipRest.tag] = pyEquipRest
			labelGather.setPyLabel( pyEquipRest.pyChecker, "AutoFightWindow:main", "ckb_Equip_Repair" )

		self.__pyBtnPickUp = HButtonEx( wnd.assistFrm.btnPickup )
		self.__pyBtnPickUp.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnPickUp.onLClick.bind( self.__onSetPickup )
		labelGather.setPyBgLabel( self.__pyBtnPickUp, "AutoFightWindow:main", "btnPickup" )

		self.__pyRtWarnBeckon = CSRichText( wnd.medicaFrm.rtWarnBeckon )
		self.__pyRtWarnBeckon.text = ""

		if hasattr( wnd.medicaFrm, "rtWarnResue" ):
			self.__pyRtWarnResue = CSRichText( wnd.medicaFrm.rtWarnResue )
			self.__pyRtWarnResue.text = ""

		self.__pyAutoPick = CheckBoxEx( wnd.assistFrm.autoPickup )
		self.__pyAutoPick.checked = True
		self.__pyAutoPick.crossFocus = True
		self.__pyAutoPick.dsp = labelGather.getText( "AutoFightWindow:main", "autoPick")
		self.__pyAutoPick.onCheckChanged.bind( self.__onAutoPick )
		self.__pyAutoPick.onMouseEnter.bind( self.__onShowDsp )
		self.__pyAutoPick.onMouseLeave.bind( self.__onHideDsp )
		self.__pyAutoPick.onLMouseDown.bind( self.__onHideDsp )

		self.__pyAutoPlusSk = CheckBoxEx( wnd.assistFrm.autoPlusSk )
		self.__pyAutoPlusSk.checked = True
		self.__pyAutoPlusSk.crossFocus = True
		self.__pyAutoPlusSk.dsp = labelGather.getText( "AutoFightWindow:main", "plusSkDsp")
		self.__pyAutoPlusSk.onCheckChanged.bind( self.__onAutoPlus )
		self.__pyAutoPlusSk.onMouseEnter.bind( self.__onShowDsp )
		self.__pyAutoPlusSk.onMouseLeave.bind( self.__onHideDsp )
		self.__pyAutoPlusSk.onLMouseDown.bind( self.__onHideDsp )
		labelGather.setPyLabel( self.__pyAutoPlusSk, "AutoFightWindow:main", "autoPlusSk" )

		self.__pyAutoConjure = CheckBoxEx( wnd.medicaFrm.autoConjure )
		self.__pyAutoConjure.checked = True
		self.__pyAutoConjure.crossFocus = True
		self.__pyAutoConjure.dsp = labelGather.getText( "AutoFightWindow:main", "conjurDsp")
		self.__pyAutoConjure.onCheckChanged.bind( self.__onAutoConjure )
		self.__pyAutoConjure.onMouseEnter.bind( self.__onShowDsp )
		self.__pyAutoConjure.onMouseLeave.bind( self.__onHideDsp )
		self.__pyAutoConjure.onLMouseDown.bind( self.__onHideDsp )
		labelGather.setPyLabel( self.__pyAutoConjure, "AutoFightWindow:main", "autoConjure" )

		if hasattr( wnd.medicaFrm, "autoResue" ):
			self.__pyAutoResue = CheckBoxEx( wnd.medicaFrm.autoResue )					#是否使用归命符箓
			self.__pyAutoResue.checked = False
			self.__pyAutoResue.crossFocus = True
			self.__pyAutoResue.dsp = labelGather.getText( "AutoFightWindow:main", "resueDsp")
			self.__pyAutoResue.onCheckChanged.bind( self.__onAutoResue )
			self.__pyAutoResue.onMouseEnter.bind( self.__onShowDsp )
			self.__pyAutoResue.onMouseLeave.bind( self.__onHideDsp )
			self.__pyAutoResue.onLMouseDown.bind( self.__onHideDsp )
			labelGather.setPyLabel( self.__pyAutoResue, "AutoFightWindow:main", "autoResue" )

		self.__pyBtnPlus = HButtonEx( wnd.assistFrm.btnPlus )
		self.__pyBtnPlus.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnPlus.onLClick.bind( self.__onSetPlus )
		labelGather.setPyBgLabel( self.__pyBtnPlus, "AutoFightWindow:main", "btnPlus" )

		self.__pyBtnCommend = HButtonEx( wnd.btnCommend )
		self.__pyBtnCommend.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCommend.onLClick.bind( self.__onCommendConfig )
		labelGather.setPyBgLabel( self.__pyBtnCommend, "AutoFightWindow:main", "btnCommend" )

		self.__pyBtnSave = HButtonEx( wnd.btnSave )
		self.__pyBtnSave.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnSave.onLClick.bind( self.__onSaveConfig )
		labelGather.setPyBgLabel( self.__pyBtnSave, "AutoFightWindow:main", "btnSave" )

		labelGather.setPyLabel( self.__pyRestores["Role_HP"].pyChecker, "AutoFightWindow:main", "ckb_Role_HP" )
		labelGather.setPyLabel( self.__pyRestores["Role_MP"].pyChecker, "AutoFightWindow:main", "ckb_Role_MP" )
		labelGather.setPyLabel( self.__pyRestores["Pet_HP"].pyChecker, "AutoFightWindow:main", "ckb_Pet_HP" )
		labelGather.setPyLabel( self.__pyRestores["Pet_MP"].pyChecker, "AutoFightWindow:main", "ckb_Pet_MP" )
		labelGather.setPyLabel( self.__pyRestores["Pet_Joyancy"].pyChecker, "AutoFightWindow:main", "ckb_Pet_Joyancy" )
		labelGather.setPyLabel( self.__pyAutoPick, "AutoFightWindow:main", "autoPickup" )
		labelGather.setLabel( wnd.assistFrm.boundText, "AutoFightWindow:main", "choiceRange" )
		labelGather.setLabel( wnd.medicaFrm.bgTitle.stTitle, "AutoFightWindow:main", "mediaSeting" )
		labelGather.setLabel( wnd.assistFrm.bgTitle.stTitle, "AutoFightWindow:main", "assiSeting" )
		labelGather.setLabel( wnd.assistFrm.plusSkText, "AutoFightWindow:main", "choiceTarget" )
		self.__initTextFont( self.__pyRestores )

	@deco_InitTextFont
	def __initTextFont( self, pyRestores):
		for pyRestore in pyRestores.values():
			pyRestore.pyChecker.charSpace = 1
			pyRestore.pyChecker.limning = Font.LIMN_NONE

	def __onAutoPick( self, checked ):
		"""
		是否自动拾取
		"""
		self.__autoPickup = checked
		self.__pyBtnPickUp.enable = checked

	def __onAutoPlus( self, checked ):
		"""
		是否自动施放增益技能
		"""
		self.__autoPlus = checked
		self.__pyBtnPlus.enable = checked
		for pyPlus in self.__pyPluses.values():
			pyPlus.checked = False
			pyPlus.enable = checked

	def __onAutoConjure( self, checked ):
		"""
		是否自动召唤宠物出战
		"""
		self.__autoConjure = checked
		self.__pyAutoConjure.checked = checked

	def __onAutoResue( self, checked ):
		"""
		是否使用归命符箓复活
		"""
		hasReboinItem = self.__hasReboinItem()
		if checked and not hasReboinItem:
			def query( rs_id ):
				if rs_id == RS_YES:
					ECenter.fireEvent( "EVT_ON_TOGGLE_SPECIAL_SHOP" )
			showMessage( 0x00c7, "", MB_YES_NO, query, self )
		checked = checked and hasReboinItem
		self.__autoResue = checked
		self.__pyAutoResue.checked = checked
#		self.__pyAutoResue.checker_.visible = checked

	def __onAutoRadiusChange( self, pyChecker ):
		if pyChecker is None:return
		radius = pyChecker.radius
		self.__autoRadius = radius

	def __hasReboinItem( self ):
		reboinItems = BigWorld.player().findItemsFromNKCK_( Const.AUTO_FIGHT_REBOIN_ITEM_ID )
		if len( reboinItems ) > 0:
			return True
		return False

	def __onSetPlus( self ):
		"""
		设置增益技能
		"""
		PlusSkillSet.inst.show( self )

	def __onSetPickup( self ):
		"""
		设置自动拾取
		"""
		PickupSet.inst.show( self )

	def __onCommendConfig( self ):
		"""
		推荐设置
		"""
		comConfig = {}
		player = BigWorld.player()
		for resTag, pyRestore in self.__pyRestores.items():
			if resTag == "Equip_Repair":
				pyRestore.checked = False
				pyRestore.percent = 0.0
			else:
				pyRestore.checked = True
				pyRestore.percent = 0.6
		self.__pyAutoPick.checked = True
		self.__pyAutoConjure.checked = True
		comConfig["isAutoConjure"] = self.__autoConjure
		self.__pyAutoPlusSk.checked = True
		comConfig["isAutoPlus"] = self.__autoPlus
		comConfig["autoReboin"] = self.__autoResue
		self.__pyRadiusGroup.pyCurrChecker = self.__pyRadiusGroup.pyCheckers[2]
		comConfig["radius"] = self.__pyRadiusGroup.pyCurrChecker.radius
		comConfig["radiusAdd"] = 15
		for index, pyPlus in self.__pyPluses.items():
			pyPlus.checked = True

	def __onSaveConfig( self ):
		"""
		保存设置
		"""
		autoConfig = {}
		player = BigWorld.player()
		for resTag, pyRestore in self.__pyRestores.items():
			checked = pyRestore.checked
			percent = pyRestore.percent
			if resTag == "Pet_Joyancy":
				autoConfig["isAutoAddJoy"] = checked
				autoConfig["joyLess"] = int( percent* 100 )
			elif resTag == "Role_HP":
				player.setRoleHpRestorePercent( percent )
			elif resTag == "Role_MP":
				player.setRoleMpRestorePercent( percent )
			elif resTag == "Pet_HP":
				player.setPetHpRestorePercent( percent )
			elif resTag == "Pet_MP":
				player.setPetMpRestorePercent( percent )
			else:
				player.setAutoRepairRate( percent*100 )
		pickupSetInst = PickupSet.inst
		isIgnorePickUp = pickupSetInst.isIgnorePickUp
		pickUpTypes = pickupSetInst.getPickUpTypes()
		autoConfig["isAutoConjure"] = self.__autoConjure
		autoConfig["isAutoPlus"] = self.__autoPlus
		autoConfig["radius"] = self.__autoRadius
		autoConfig["radiusAdd"] = 15
		autoConfig["repairRate"] = 0
		autoConfig["autoRepair"] = self.__autoRepair
		if self.__pyRestores.has_key( "Equip_Repair" ):
			pyRepair = self.__pyRestores["Equip_Repair"]
			autoConfig["repairRate"] = pyRepair.percent*100
			autoConfig["autoRepair"] = pyRepair.checked
		autoConfig["autoReboin"] = self.__autoResue
		autoConfig["isIgnorePickUp"] = isIgnorePickUp
		player.setAutoFightConfig( autoConfig )
		player.setPickItemNeed( self.__autoPickup )
		player.setPickUpTypes( isIgnorePickUp, pickUpTypes )
		autoPlus = []
		for index, isPlus in enumerate( player.autoPlusInfo ):
			pyPlus = self.__pyPluses.get( index, None )
			if pyPlus is None:return
			checked = pyPlus.checked
			player.autoPlusInfo[index] = checked
			autoPlus.append( checked )
		player.setAutoPlusInfo( autoPlus )
		player.statusMessage( csstatus.AUTO_FIGHT_SETTING_HAS_SAVED )
		self.hide()

	def __toggleAuotFightWindow( self ):
		player = BigWorld.player()
		plusObjects = player.autoPlusInfo			#施放增益技能对象
		percent = 0.0
		for resTag, pyRestore in self.__pyRestores.items():
			if resTag == "Pet_Joyancy":
				checked = player.autoFightConfig["isAutoAddJoy"]
				percent = player.autoFightConfig["joyLess"]
				pyRestore.checked = checked
			elif resTag == "Role_HP":
				percent = player.getRoleHpRestorePercent()
			elif resTag == "Role_MP":
				percent = player.getRoleMpRestorePercent()
			elif resTag == "Pet_HP":
				percent = player.getPetHpRestorePercent()
			elif resTag == "Pet_MP":
				percent = player.getPetMpRestorePercent()
			else:
				percent = player.getAutoRepairRate()/100.0
			pyRestore.percent = percent
			if resTag != "Pet_Joyancy":
				pyRestore.checked = percent > 0.0
		for pyRadius in self.__pyRadiusGroup.pyCheckers:
			pyRadius.checked = pyRadius.radius == player.autoFightConfig["radius"]
		for index, isPlus in enumerate( plusObjects ):
			pyPlus = self.__pyPluses.get( index, None )
			if pyPlus is None:return
			pyPlus.checked = int( isPlus )
		self.__pyAutoPick.checked = player.getPickItemNeed()
		self.__pyAutoPlusSk.checked = player.autoFightConfig["isAutoPlus"]
		self.__pyAutoConjure.checked = player.autoFightConfig["isAutoConjure"]
		self.__pyRtWarnBeckon.text = PL_Font.getSource( labelGather.getLabel( "AutoFightWindow:main", "rtWarnBeckon" ).text, fc = ( 0, 255, 0) )
#		toolbox.infoTip.showOperationTips( 0x0095, self.__pyMediaFrame, Rect(( 16, 20 ), (235, 115 )))
#		toolbox.infoTip.showOperationTips( 0x0096, self.__pyAutoConjure )
#		toolbox.infoTip.showOperationTips( 0x0097, self.__pyRadiusGroup.pyCheckers[0])
#		toolbox.infoTip.showOperationTips( 0x0098, self.__pyAutoPick )
#		toolbox.infoTip.showOperationTips( 0x0099, self.__pySkSetPanel, Rect(( 3, 100 ), (285, 85 )))
		if self.__pyAutoResue:
			self.__pyAutoResue.checked = player.autoFightConfig["autoReboin"]
		if self.__pyRtWarnResue:
			self.__pyRtWarnResue.text = PL_Font.getSource( labelGather.getLabel( "AutoFightWindow:main", "rtWarnResue" ).text, fc = ( 0, 255, 0 ) )

	def __onShowDsp( self, pyChecker ):
		if pyChecker is None:return
		toolbox.infoTip.showToolTips( self, pyChecker.dsp )

	def __onHideDsp( self ):
		toolbox.infoTip.hide()

	def toggleAuotFightWindow(self):
		if self.visible:
			self.hide()
		else:
			self.show()
		self.__toggleAuotFightWindow()

	def onMove_( self, dx, dy ):
		Window.onMove_( self, dx, dy )
#		toolbox.infoTip.moveOperationTips( 0x0095 )
#		toolbox.infoTip.moveOperationTips( 0x0096 )
#		toolbox.infoTip.moveOperationTips( 0x0097 )
#		toolbox.infoTip.moveOperationTips( 0x0098 )
#		toolbox.infoTip.moveOperationTips( 0x0099 )
	# ---------------------------------------------------------------
	# public
	# ---------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ):
		self.hide()

	def hide( self ):
		Window.hide( self )
		self.removeFromMgr()
		self.dispose()
		self.__unregisterTriggers()
		self.__triggers={}
		AutoFightWindow.__instance = None
#		toolbox.infoTip.hideOperationTips( 0x0095 )
#		toolbox.infoTip.hideOperationTips( 0x0096 )
#		toolbox.infoTip.hideOperationTips( 0x0097 )
#		toolbox.infoTip.hideOperationTips( 0x0098 )
#		toolbox.infoTip.hideOperationTips( 0x0099 )

	@staticmethod
	def instance():
		"""
		get the exclusive instance of AutoFightWindow
		"""
		if AutoFightWindow.__instance is None:
			AutoFightWindow.__instance = AutoFightWindow()
		return AutoFightWindow.__instance

	@staticmethod
	def getInstance():
		"""
		"""
		return AutoFightWindow.__instance

from guis.controls.StaticText import StaticText

class RestoreItem( PyGUI ):
	def __init__( self, item ):
		PyGUI.__init__( self, item )

		self.__checkded = False
		self.__percent = 0.0
		self.__dsp = ""
		self.__pyCheckBox = CheckBoxEx( item.checkBox )
		self.__pyCheckBox.checked = False
		self.__pyCheckBox.crossFocus = True
		self.__pyCheckBox.onCheckChanged.bind( self.__onCheck )
		self.__pyCheckBox.onMouseEnter.bind( self.__onShowDsp )
		self.__pyCheckBox.onMouseLeave.bind( self.__onHideDsp )
		self.__pyCheckBox.onLMouseDown.bind( self.__onHideDsp )

		self.__pyTextBox = TextBox( item.inputBox.box )
		self.__pyTextBox.inputMode = InputMode.INTEGER
		self.__pyTextBox.filterChars = ['-', '+']
		self.__pyTextBox.maxLength = 2

	def __onCheck( self, checked ):
		if self.tag == "Equip_Repair":
			hasRepairItem = self.hasRepairItem()
			if checked and not hasRepairItem:
				def query( rs_id ):
					if rs_id == RS_YES:
						ECenter.fireEvent( "EVT_ON_TOGGLE_SPECIAL_SHOP" )
				showMessage( 0x00ca, "", MB_YES_NO, query, self.pyTopParent )
			self.__pyCheckBox.checked = checked and hasRepairItem
#			self.__pyCheckBox.checker_.visible = checked
		self.__checkded = checked
		self.__pyTextBox.enable = checked

	def __onShowDsp( self ):
		toolbox.infoTip.showToolTips( self, self.__dsp )

	def __onHideDsp( self ):
		toolbox.infoTip.hide()

	def hasRepairItem( self ):
		repItems = BigWorld.player().findItemsFromNKCK_( Const.AUTO_FIGHT_REPAIR_ITEM_ID )
		if len( repItems ) > 0:
			return True
		return False

	def _getPercent( self ):
		if self.__checkded:
			self.__percent = int( self.__pyTextBox.text )/100.0
		else:
			self.__percent = 0.0
		return self.__percent

	def _setPercent( self, percent ):
		self.__pyTextBox.text = str( int( round( percent* 100 ) ) )
		self.__percent = percent

	def _getChecked( self ):
		return self.__checkded

	def _setChecked( self, checked ):
		self.__pyCheckBox.checked = checked
		self.__checkded = checked
		if self.tag == "Equip_Repair":
			checked &= self.hasRepairItem()
		self.__pyTextBox.enable = checked

	def _getDsp( self ):
		return self.__dsp

	def _setDsp( self, dsp ):
		self.__dsp = dsp

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	percent = property( _getPercent, _setPercent )
	checked = property( _getChecked, _setChecked )
	dsp = property( _getDsp, _setDsp )
	pyChecker = property( lambda self : self.__pyCheckBox )