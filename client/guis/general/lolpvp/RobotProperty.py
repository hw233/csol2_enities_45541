# -*- coding: gb18030 -*-
#
# $Id: EspialWindow.py Exp $

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.controls.ProgressBar import HProgressBar
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ButtonEx import HButtonEx
from guis.controls.ODPagesPanel import ODPagesPanel
from guis.controls.RichText import RichText
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from RobotRender import RobotRender
from RobotInfosLoader import robotInfosLoader
from guis.general.petswindow.vehiclepanel.VehiclePanel import GuardAttr as RobotAttr
from NPCModelLoader import NPCModelLoader
g_npcmodel = NPCModelLoader.instance()
import csdefine
import csconst
import GUIFacade

class RobotProperty( Window ):
	"""
	机器人属性界面
	"""
	_cc_items_rows = ( 3, 2 )

	def __init__( self ):
		wnd = GUI.load( "guis/general/lolpvp/prownd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True

		self.__triggers = {}
		self.__registerTriggers()
		self.__turnModelCBID = 0
		self.__trapID = 0
		self.__allModels = {}
		self.__teamNumber = 0
		self.__modifyIndex = -1
		self.__initialize( wnd )
	
	def __initialize( self, wnd ):
		self.__pyLifeBar = HProgressBar( wnd.lifeBar )
		self.__pyLifeBar.clipMode = "RIGHT"
		self.__pyLifeBar.value = 0.0
		
		self.__pyStLifeRatio = StaticText( wnd.stLifeRatio )
		self.__pyStLifeRatio.text = ""
		
		self.__pyStRobotName = StaticText( wnd.stGuardName ) #骑宠名称
		self.__pyStRobotName.text= ""
		
		self.__pyBtnLeft = Button( wnd.btnLeft ) #向左转动模型
		self.__pyBtnLeft.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnLeft.onLMouseDown.bind( self.__onTurnLeft )

		self.__pyBtnRight = Button( wnd.btnRight ) #向右转动模型
		self.__pyBtnRight.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnRight.onLMouseDown.bind( self.__onTurnRight )
	
		self.__pyRobotsPage = ODPagesPanel( wnd.guardsPanel, wnd.pgIdxBar )
		self.__pyRobotsPage.onViewItemInitialized.bind( self.__initListItem )
		self.__pyRobotsPage.onDrawItem.bind( self.__drawListItem )
		self.__pyRobotsPage.selectable = True
		self.__pyRobotsPage.onItemSelectChanged.bind( self.__onRobotSelChange )
		self.__pyRobotsPage.viewSize = self._cc_items_rows
		
		self.__pyBtnOk = HButtonEx( wnd.btnOk )
		self.__pyBtnOk.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnOk.onLClick.bind( self.__onOK ) #
		labelGather.setPyBgLabel( self.__pyBtnOk, "LolPVP:RobotProperty", "btnOk" )

		self.__pyBtnCancel = HButtonEx( wnd.btnCancel )
		self.__pyBtnCancel.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnCancel.onLClick.bind( self.__onCandel ) #
		labelGather.setPyBgLabel( self.__pyBtnCancel, "LolPVP:RobotProperty", "btnCancel" )
		
		self.__pyRtIntro = CSRichText( wnd.introBg.rtIntro )
		self.__pyRtIntro.text = ""

		self.__pyRobotRender = RobotRender( wnd.guardRender )
		
		self.__pyRobotAttrs = {}									#守护的属性
		for name, item in wnd.children:
			if "attr_" not in name:continue
			tag = name.split( "_" )[1]
			pyVehicleAttr = RobotAttr( item )
			pyVehicleAttr.title = labelGather.getText( "LolPVP:RobotProperty", tag )
			pyVehicleAttr.text = ""
			self.__pyRobotAttrs[tag] = pyVehicleAttr
		labelGather.setPyLabel( self.pyLbTitle_, "LolPVP:RobotProperty", "lbTitle" )
		labelGather.setLabel( wnd.nameText, "LolPVP:RobotProperty", "nameText" )
		labelGather.setLabel( wnd.expText, "LolPVP:RobotProperty", "lifeText" )
		labelGather.setLabel( wnd.listBg.bgTitle.stTitle, "LolPVP:RobotProperty", "robotList")
		labelGather.setLabel( wnd.attrsBg.bgTitle.stTitle, "LolPVP:RobotProperty", "robotAttrs")
		labelGather.setLabel( wnd.introBg.bgTitle.stTitle, "LolPVP:RobotProperty", "robotIntro")

	# ----------------------------------------------------------
	# private
	# ----------------------------------------------------------
	def __registerTriggers( self ):
#		self.__triggers["EVT_ON_PVE_ADD_ROBOT"] = self.__onAddRobot
#		self.__triggers["EVT_ON_PVE_REMOVE_ROBOT"] = self.__onRemovRobot
#		self.__triggers["EVT_ON_PVE_UPDATE_ROBOT"] = self.__onUpateRobot
		self.__triggers["EVT_ON_ROBOT_SELECTED"] = self.__onRobotSelected
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		"""
		deregister all events
		"""
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )
	# ----------------------------------------------------------------------
	def __initListItem( self, pyViewItem ):
		"""
		初始化添加的商品列表项
		"""
		pyRobot = RobotItem()
		pyViewItem.pyRobot = pyRobot
		pyViewItem.addPyChild( pyRobot )
		pyViewItem.dragFocus = False
		pyViewItem.focus = False
		pyRobot.left = 0
		pyRobot.top = 0

	def __drawListItem( self, pyViewItem ) :
		"""
		重画商品列表项
		"""
		robotInfo = pyViewItem.pageItem
		pyRobot = pyViewItem.pyRobot
		pyRobot.selected = pyViewItem.selected
		pyRobot.update( robotInfo )
		pyViewItem.focus = robotInfo is not None
	
	def __onAddRobot( self, robot ):
		"""
		增加机器人
		"""
		if robot is None:return
		objectID = robot.objectID
		if not objectID in [item.objectID for item in self.__pyRobotsPage.items]:
			self.__pyRobotsPage.addItem( robot )
	
	def __onRemovRobot( self, objectID ):
		"""
		删除机器人
		"""
		for robot in self.__pyRobotsPage.items:
			if robot.objectID == objectID:
				self.__pyRobotsPage.removeItem( robot )
	
	def __onUpateRobot( self, oldIndex, newRobot ):
		"""
		更新机器人
		"""
		pass
	
	def __onRobotSelChange( self, selIndex ):
		"""
		选择某个机器人
		"""
		if selIndex < 0:return
		player = BigWorld.player()
		robotInfo = self.__pyRobotsPage.selItem
		# 刷新模型
		modelNum = robotInfo.modelNum
		className = robotInfo.className
		robotInfos = player.baoZangRobotInfos
		if not className in robotInfos:return
		robotInfo = robotInfos[className]
		uiRbtInfo = robotInfosLoader.getRobotInfo( className )
		if uiRbtInfo is None:return
		level = robotInfo["level"]
		raceclass = robotInfo["robotClass"]
		soulCoin = robotInfo["accumPoint"]
		life = int( robotInfo["hp_max"] )
		force = robotInfo["damage"]
		self.__setModel( className, modelNum )
		self.__pyStRobotName.text = robotInfo["robotName"]
		self.__onAttrUpdate( "soulCoin", soulCoin )
		self.__onAttrUpdate( "life", life )
		self.__onAttrUpdate( "force", force )
		robotInfosLoader.setRbtExtraInfo( className, level, raceclass, soulCoin, life, 0, force )
		self.__pyRtIntro.text = uiRbtInfo.dsp
		self.__pyLifeBar.value = 1.0
		self.__pyStLifeRatio.text = "%d/%d"%( int( life ), int( life ) )
	
	def __onRobotSelected( self, className ):
		"""
		选择某个机器人
		"""
		for pyViewItem in self.__pyRobotsPage.pyViewItems:
			robotInfo = pyViewItem.pageItem
			pyRobot = pyViewItem.pyRobot
			if robotInfo is None:continue
			pyRobot.selected = robotInfo.className == className
			if robotInfo.className == className:
				self.__pyRobotsPage.selItem = robotInfo

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
		self.__pyRobotRender.yaw += ( isRTurn and -0.1 or 0.1 )
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
			self.__pyRobotRender.update( className, model )
		else:
			rds.npcModel.createDynamicModelBG( modelNum, Functor( self.__onModelCreated, className, modelNum ) )

	def __onModelCreated( self, className, modelNum, model ):
		"""
		模型后线程加载完回调
		"""
		self.__allModels[className] = model
		selRobotInfo = self.__pyRobotsPage.selItem
		if selRobotInfo is None:return
		if className == selRobotInfo.className:
			self.__pyRobotRender.update( className, model )

	def __onAttrUpdate( self, attrTag, value ):
		"""
		更新守护属性
		"""
		if self.__pyRobotAttrs.has_key( attrTag ):
			pyStAttr = self.__pyRobotAttrs[attrTag]
			pyStAttr.text = str( value )
	
	def __clearAttrs( self ):
		for tag, pyStAttr in self.__pyRobotAttrs.iteritems():
			pyStAttr.text = ""
	
	def __onOK( self ):
		"""
		确定选择
		"""
		selRobotInfo = self.__pyRobotsPage.selItem
		if selRobotInfo is None:return
		if self.__modifyIndex >= 0:
			ECenter.fireEvent( "EVT_ON_UPDATE_PVE_ROBOT", self.__teamNumber, self.__modifyIndex, selRobotInfo )
		else:
			ECenter.fireEvent( "EVT_ON_ADD_PVE_ROBOT", self.__teamNumber, selRobotInfo )
	
	def __onCandel( self ):
		"""
		取消选择
		"""
		self.hide()

	# ----------------------------------------------------------
	#public
	# ---------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ):
		self.hide()

	def show( self, teamNumber = 0, modifyIndex = -1, pyBinder = None ):
		self.__pyRobotsPage.clearItems()
		self.__teamNumber = teamNumber
		self.__modifyIndex = modifyIndex
		classNames = []
		if teamNumber == 0:
			classNames = csconst.YXLM_ROBOT_1
		else:
			classNames = csconst.YXLM_ROBOT_2
		for className in classNames:
			robotInfo = robotInfosLoader.getRobotInfo( className )
			if robotInfo is None:continue
			self.__pyRobotsPage.addItem( robotInfo )
		BigWorld.player().baoZangReqRobotInfos()
		self.__pyRobotRender.enableDrawModel()
		self.__pyRobotsPage.selIndex = 0
		Window.show( self, pyBinder )

	def hide( self ):
		Window.hide( self )
		self.__pyRobotRender.disableDrawModel()

# ------------------------------------------------------------------------------------------------

class RobotItem( Control ):
	def __init__( self ):
		vcItem = GUI.load( "guis/general/petswindow/vehicleitem.gui")
		uiFixer.firstLoadFix( vcItem )
		Control.__init__( self, vcItem )
		self.crossFocus = False
		self.dragFocus = False
		self.focus = False
		self.__pyCover = None
		self.__pyVehicleBg = PyGUI( vcItem.petBg )
		self.infoBg = vcItem.infoBg
		self.__pyItem = Item( vcItem.item, self )
		self.__pyRtInfo = CSRichText( vcItem.rtInfo )
		self.__pyRtInfo.top = 15.0
		self.__pyRtInfo.maxWidth = 100.0
		self.__pyRtInfo.align = "C"
		self.__pyRtInfo.lineFlat = "M"
		self.__pyRtInfo.fontSize = 14.0
		self.robotInfo = None
		self.__panelState = ( 1, 1 )
		if hasattr( vcItem, "cover" ) :
			self.__pyCover = PyGUI( vcItem.cover )
			self.__pyCover.visible = False

	# -------------------------------------------------------------
	# public
	# -------------------------------------------------------------
	def update( self, robotInfo ):
		name = ""
		if robotInfo:
			name = robotInfo.name
			nameText = PL_Font.getSource( "%s"%name, fc = ( 0, 255, 255, 255 ) )
			self.__pyRtInfo.text = nameText
			self.__pyItem.crossFocus = True
			util.setGuiState( self.__pyVehicleBg.getGui(), ( 1,2 ),( 1, 1 ) )
		else:
			self.__pyRtInfo.text = ""
			self.__pyItem.crossFocus = False
			util.setGuiState( self.__pyVehicleBg.getGui(), ( 1,2 ),( 1, 2 ) )
		self.robotInfo = robotInfo
		self.__pyItem.update( robotInfo )

	def __select( self ):
		self.panelState = ( 3, 1 )
		if self.__pyCover:
			self.__pyCover.visible = True

	def __deselect( self ):
		self.panelState = ( 1, 1 )
		if self.__pyCover:
			self.__pyCover.visible = False

	def revertVehicleName( self, baseItem ):
		"""
		还原骑宠类物品名字
		骑宠蛋(XXX) -> XXX
		"""
		name = baseItem.name()
		return name.split("(")[-1].split(")")[0]

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def getObjectItem( self ):
		return self.__pyItem

	def _getPanelState( self ):
		return self.__panelState

	def _setPanelState( self, state ):
		self.__panelState = state
		elements = self.infoBg.elements
		for ename, element in elements.items():
			element.mapping = util.getStateMapping( element.size, UIState.MODE_R3C1, state )
			if ename in ["frm_rt", "frm_r", "frm_rb"]:
				element.mapping = util.hflipMapping( element.mapping )

	def _getSelected( self ):
		return self.__selected

	def _setSelected( self, selected ):
		if selected:
			self.__select()
		else:
			self.__deselect()
		self.__selected = selected
	# -------------------------------------------------
	panelState = property( _getPanelState, _setPanelState )
	selected = property( _getSelected, _setSelected )

# ----------------------------------------------------------------------
import event.EventCenter as ECenter
from guis.controls.Item import Item as BOItem
from guis import *
import BigWorld

class Item( BOItem ):
	def __init__( self, item, pyBinder = None ):
		BOItem.__init__( self, item, pyBinder )
		self.focus = True
		self.crossFocus = True
		self.dragFocus = False
		self.selectable = True
		self.description = ""
		self.index = 0
		self.__initialize( item )

	def subclass( self, item ) :
		BOItem.subclass( self, item )
		self.__initialize( item )
		return True

	def __initialize( self, item ) :
		if item is None : return

	def onMouseEnter_( self ):
		#BOItem.onMouseEnter_( self )
		toolbox.itemCover.highlightItem( self )
		if self.pyBinder.robotInfo is None:return
		if self.pyBinder.selected:return
		self.pyBinder.panelState = ( 2, 1 )
		return True

	def onMouseLeave_( self ):
		BOItem.onMouseLeave_( self )
		if self.pyBinder.robotInfo is None:return
		if self.pyBinder.selected:return
		self.pyBinder.panelState = ( 1, 1 )
		return True

	def onRClick_( self,mods ):
		BOItem.onRClick_( self, mods )
		return True

	def onLClick_( self, mods ):
		if self.pyBinder.robotInfo is None:return
		BOItem.onLClick_( self, mods )
		robotInfo = self.pyBinder.robotInfo
		ECenter.fireEvent( "EVT_ON_ROBOT_SELECTED", robotInfo.className )
		return True

	# -------------------------------------------------
	def onDragStart_( self, pyDragged ) :
		BOItem.onDragStart_( self, pyDragged )
		if BigWorld.isKeyDown( KEY_LCONTROL ) :
			rds.ruisMgr.dragObj.attach = KEY_LCONTROL
		if self.itemInfo is None:return
		rds.ruisMgr.hideBar.enterShow()
		return True
	
	def onDragStop_( self, pyDragged ) :
		if self.pyBinder.robotInfo is None:return
		rds.ruisMgr.hideBar.leaveShow()
	# -----------------------------------------------
	# public
	# -----------------------------------------------
	def update( self, robotInfo ):
		"""
		update item
		"""
		headTexture = ""
		if robotInfo:
			modelNum = robotInfo.modelNum
			headTexture = g_npcmodel.getHeadTexture( modelNum )
		self.texture = headTexture
#		BOItem.update( self, robotInfo )