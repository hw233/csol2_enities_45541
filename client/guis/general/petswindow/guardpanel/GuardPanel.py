# -*- coding: gb18030 -*-
#
# $Id: GuardPanel.py,

from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from guis.controls.TabCtrl import TabPanel
from guis.controls.Button import Button
from guis.controls.ProgressBar import HProgressBar
from guis.controls.ODPagesPanel import ODPagesPanel
from guis.controls.StaticText import StaticText
from guis.controls.RichText import RichText
from ItemsFactory import ObjectItem as ItemInfo
from GuardRender import GuardRender
from gbref import rds
from guis.general.petswindow.vehiclepanel.VehiclePanel import GuardAttr
from GuardInfosLoader import guardInfosLoader
from GuardItem import GuardItem
from config.skill.Skill.SkillDataMgr import Datas as skDatas
import skills
import Time
import items
import csstatus
import csdefine

class GuardPanel( TabPanel ):
	
	_cc_items_rows = ( 3, 2 )
	
	def __init__( self, panel, pyBinder = None ):
		TabPanel.__init__( self, panel, pyBinder )
		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( panel )
		self.__turnModelCBID = 0
		self.__allModels = {}
	
	def __initialize( self, panel ):
		self.__pyLifeBar = HProgressBar( panel.lifeBar )
		self.__pyLifeBar.clipMode = "RIGHT"
		self.__pyLifeBar.value = 0.0
		
		self.__pyStLifeRatio = StaticText( panel.stLifeRatio )
		self.__pyStLifeRatio.text = ""
		
		self.__pyStGuardName = StaticText( panel.stGuardName ) #骑宠名称
		self.__pyStGuardName.text= ""
		
		self.__pyBtnLeft = Button( panel.btnLeft ) #向左转动模型
		self.__pyBtnLeft.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnLeft.onLMouseDown.bind( self.__onTurnLeft )

		self.__pyBtnRight = Button( panel.btnRight ) #向右转动模型
		self.__pyBtnRight.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnRight.onLMouseDown.bind( self.__onTurnRight )
	
		self.__pyGuardsPage = ODPagesPanel( panel.guardsPanel, panel.pgIdxBar )
		self.__pyGuardsPage.onViewItemInitialized.bind( self.__initListItem )
		self.__pyGuardsPage.onDrawItem.bind( self.__drawListItem )
		self.__pyGuardsPage.selectable = True
		self.__pyGuardsPage.onItemSelectChanged.bind( self.__onGuardSelChange )
		self.__pyGuardsPage.viewSize = self._cc_items_rows
		
		self.__pyRtIntro = RichText( panel.introBg.rtIntro )
		self.__pyRtIntro.text = ""

		self.__pyGuardRender = GuardRender( panel.guardRender )
		
		self.__pyGuardAttrs = {}									#守护的属性
		for name, item in panel.children:
			if "attr_" not in name:continue
			tag = name.split( "_" )[1]
			pyVehicleAttr = GuardAttr( item )
			pyVehicleAttr.title = labelGather.getText( "PetsWindow:GuardPanel", tag )
			pyVehicleAttr.text = ""
			self.__pyGuardAttrs[tag] = pyVehicleAttr
		labelGather.setLabel( panel.nameText, "PetsWindow:VehiclesPanel", "nameText" )
		labelGather.setLabel( panel.expText, "PetsWindow:GuardPanel", "lifeText" )
		labelGather.setLabel( panel.listBg.bgTitle.stTitle, "PetsWindow:GuardPanel", "guardList")
		labelGather.setLabel( panel.attrsBg.bgTitle.stTitle, "PetsWindow:GuardPanel", "guardAttrs")
		labelGather.setLabel( panel.introBg.bgTitle.stTitle, "PetsWindow:GuardPanel", "guardIntro")

	# ----------------------------------------------------------
	# private
	# ----------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_PLAYERROLE_ADD_SKILL"] = self.__onAddSkill
		self.__triggers["EVT_ON_PLAYERROLE_REMOVE_SKILL"] = self.__onRemoveSkill
		self.__triggers["EVT_ON_PLAYERROLE_UPDATE_SKILL"] = self.__onUpateSkill
		self.__triggers["EVT_ON_GUARD_SELECTED"] = self.__onGuardSelected
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		"""
		deregister all events
		"""
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	 # ----------------------------------------------------------------------------
	 # ----------------------------------------------------------------------------
	def __onAddSkill( self, skillInfo ):
		"""
		添加守护召唤技能
		"""
		skillId = skillInfo.id
		if skillId in guardInfosLoader._datas:
			skill = skills.getSkill( skillId )
			level = skill.getLevel()
			guardInfo = guardInfosLoader.getGuardInfo( skillId )
			self.__pyGuardsPage.addItem( guardInfo )
		return
		pyTabPage = self.pyTabPage
		pyTabPage.pyBtn.visible = len( self.__pyGuardsPage.items )

	def __onRemoveSkill( self, skillInfo ):
		"""
		移除守护召唤技能
		"""
		skillId = skillInfo.id
		for pyViewItem in self.__pyGuardsPage.pyViewItems:
			guardInfo = pyViewItem.pageItem
			if guardInfo is None:continue
			if guardInfo.mapSkID == skillId:
				self.__pyGuardsPage.removeItem( guardInfo )
		pyTabPage = self.pyTabPage
	
	def __onUpateSkill( self, oldSkillID, skillInfo ):
		"""
		更新守护召唤技能
		"""
		skillId = skillInfo.id
		for idx, guardInfo in enumerate( self.__pyGuardsPage.items ): # 更新技能信息列表中相应位置技能
			if guardInfo.mapSkID == oldSkillID:
				guardInfo = guardInfosLoader.getGuardInfo( skillId )
				self.__pyGuardsPage.updateItem( idx, guardInfo )
				break
	 
	def __onGuardSelected( self, mapSkID ):
		for pyViewItem in self.__pyGuardsPage.pyViewItems:
			guardInfo = pyViewItem.pageItem
			pyGuard = pyViewItem.pyGuard
			if guardInfo is None:continue
			pyGuard.selected = guardInfo.mapSkID == mapSkID
			if guardInfo.mapSkID == mapSkID:
				self.__pyGuardsPage.selItem = guardInfo
				
	def __initListItem( self, pyViewItem ):
		"""
		初始化添加的商品列表项
		"""
		pyGuard = GuardItem()
		pyViewItem.pyGuard = pyGuard
		pyViewItem.addPyChild( pyGuard )
		pyViewItem.dragFocus = False
		pyViewItem.focus = False
		pyGuard.left = 0
		pyGuard.top = 0

	def __drawListItem( self, pyViewItem ) :
		"""
		重画商品列表项
		"""
		guardInfo = pyViewItem.pageItem
		pyGuard = pyViewItem.pyGuard
		pyGuard.selected = pyViewItem.selected
		pyGuard.update( guardInfo )
		pyViewItem.focus = guardInfo is not None

	def __onGuardSelChange( self, selIndex ):
		realms = { csdefine.PGNAGUAL_REALM_DIXIAN :"dixian",
				csdefine.PGNAGUAL_REALM_TIANXIAN :"tianxian",
				csdefine.PGNAGUAL_REALM_TAIYISANXIAN :"sanxian",
				csdefine.PGNAGUAL_REALM_DALUOJINXIAN :"jinxian",
				csdefine.PGNAGUAL_REALM_ZHUNSHENG :"zhunsheng",
			}
		types = { csdefine.PGNAGUAL_TYPE_NEAR_GROUP :"nearGroup",
				csdefine.PGNAGUAL_TYPE_NEAR_SINGLE :"nearSingle",
				csdefine.PGNAGUAL_TYPE_FAR_PHYSIC :"farPhysic",
				csdefine.PGNAGUAL_TYPE_FAR_MAGIC :"farMagic",
				}
		
		if selIndex < 0:return
		player = BigWorld.player()
		guardInfo = self.__pyGuardsPage.selItem
		# 刷新模型
		modelNum = guardInfo.model
		className = guardInfo.className
		self.__setModel( className, modelNum )
		self.__pyStGuardName.text = guardInfo.name
		typeTag = types.get( guardInfo.attackType, "" )
		typeStr = labelGather.getText( "PetsWindow:GuardPanel", typeTag )
		realmTag = realms.get( guardInfo.realm, "" )
		realmStr = labelGather.getText( "PetsWindow:GuardPanel", realmTag )
		self.__onAttrUpdate( "type", typeStr )
		self.__onAttrUpdate( "realm", realmStr )
		self.__onAttrUpdate( "life", guardInfo.HP )
		self.__onAttrUpdate( "airtrant", guardInfo.reqAccum )
		self.__onAttrUpdate( "atforce", guardInfo.damage )
		self.__pyRtIntro.text = guardInfo.dsp
		self.__pyLifeBar.value = 1.0
		self.__pyStLifeRatio.text = "%d/%d"%( guardInfo.HP, guardInfo.HP )

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
		self.__pyGuardRender.yaw += ( isRTurn and -0.1 or 0.1 )
		if BigWorld.isKeyDown( KEY_LEFTMOUSE ) :
			self.__turnModelCBID = BigWorld.callback( 0.1, Functor( self.__turnModel, isRTurn ) )
	
	def __setModel( self, className, modelNum ):
		"""
		设置DBID的模型
		"""
		player = BigWorld.player()
		if player is None: return

		if className in self.__allModels:
			model = self.__allModels[className]
			self.__pyGuardRender.update( className, model )
		else:
			rds.npcModel.createDynamicModelBG( modelNum, Functor( self.__onModelCreated, className, modelNum ) )

	def __onModelCreated( self, className, modelNum, model ):
		"""
		模型后线程加载完回调
		"""
		self.__allModels[className] = model
		selGuardInfo = self.__pyGuardsPage.selItem
		if selGuardInfo is None:return
		if className == selGuardInfo.className:
			self.__pyGuardRender.update( className, model )

	def __onAttrUpdate( self, attrTag, value ):
		"""
		更新守护属性
		"""
		if self.__pyGuardAttrs.has_key( attrTag ):
			pyStAttr = self.__pyGuardAttrs[attrTag]
			pyStAttr.text = str( value )
	
	def __clearAttrs( self ):
		for tag, pyStAttr in self.__pyGuardAttrs.iteritems():
			pyStAttr.text = ""
	# -------------------------------------------------------
	# public
	# -------------------------------------------------------
	def onShow( self ) :
		self.__pyGuardRender.enableDrawModel()
		TabPanel.onShow( self )
		player = BigWorld.player()
		guardDatas = guardInfosLoader._datas
		self.__pyGuardsPage.selItem = self.__pyGuardsPage.items[0]

	def onHide( self ) :
		TabPanel.onHide( self )
		self.__pyGuardRender.disableDrawModel()

	def onMove( self, dx, dz ):
		pass

	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def onTrigger( self ):
		player = BigWorld.player()

	def reset( self ):
		self.__pyGuardsPage.clearItems()
		self.__clearAttrs()
		self.__pyGuardRender.clearModel()
		self.__pyLifeBar.value = 0.0
		self.__pyStGuardName.text= ""
		self.__pyStLifeRatio.text = ""
		self.__turnModelCBID = 0
		self.__allModels = {}