# -*- coding: gb18030 -*-
#
# $Id: ItemResearch.py, fangpengjun Exp $

"""
implement item Research window class

"""
from guis import *
import ShareTexts
from LabelGather import labelGather
from guis.common.Window import Window
from guis.common.PyGUI import PyGUI
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis.controls.ProgressBar import HFProgressBar
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
from guis.controls.Icon import Icon
from ModelRender import GodRender
from guis.controls.Icon import Icon
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
from ItemsFactory import ObjectItem as ItemInfo
from guis.controls.SelectorGroup import SelectorGroup
from TongBeastData import TongBeastData
tongBeastData = TongBeastData.instance()
from NPCModelLoader import NPCModelLoader
modelLoader = NPCModelLoader.instance()
from config.client.msgboxtexts import Datas as mbmsgs
import items
import GUIFacade
import csconst
import csdefine
import random
import Language
from config.client import tongBeastDsp

TONG_ACTIONVAL_LIMIT = {
	0 : ( ShareTexts.NUM_0, 0 ),
	1 : ( ShareTexts.NUM_1, 100 ),
	2 : ( ShareTexts.NUM_2, 200 ),
	3 : ( ShareTexts.NUM_3, 300 ),
	4 : ( ShareTexts.NUM_4, 400 ),
	5 : ( ShareTexts.NUM_5, 500 )
}

BEAS_INDEX_MAP = { 1: "10111139",
		2: "10111140",
		3: "10111141",
		4: "10111142"
		}

class ShenShouBeckon( Window ):

	def __init__( self ):
		wnd = GUI.load( "guis/general/tongabout/shenshoubeckon/window.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 	 = True
		self.selIndex = 0 #当前选择的神兽索引
		self.beckonIndex = 0 #当前召唤出的神兽
		self.__trapID = 0
		self.shenshouLevel = 0 #召唤出的神兽等级
		self.__turnModelCBID = 0
		self.__defaultColor = 255, 255, 255, 255
		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( wnd )

	def __initialize( self, wnd ):
		self.__pyBeckonBtn = Button( wnd.btnBeckon )
		self.__pyBeckonBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBeckonBtn.onLClick.bind( self.__beckonShenShou )
		labelGather.setPyBgLabel( self.__pyBeckonBtn, "TongAbout:ShenShouBeckon", "btnBeckon" )

		self.__pyStAction = StaticText( wnd.actionValue )
		self.__pyStAction.text = ""

		self.__pyStAcadeLevel = StaticText( wnd.stAcadLevel )#帮会神兽殿等级
		self.__pyStAcadeLevel.text = ""

		self.__pyRtUseMoney = CSRichText( wnd.rtUseMoney )
		self.__pyRtUseMoney.align = "L"
		self.__pyRtUseMoney.text = ""

		self.__pyStSelGod = StaticText( wnd.selGodAnimal ) #当前召唤出的神兽
		self.__pyStSelGod.text = ""

		self.__pyBtnLeft = Button( wnd.btnLeft )
		self.__pyBtnLeft.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnLeft.onLMouseDown.bind( self.__turnLeft )

		self.__pyBtnRight = Button( wnd.btnRight )
		self.__pyBtnRight.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnRight.onLMouseDown.bind( self.__turnRight )

		self.__pyGodRender = GodRender( wnd.modelRender )

		self.__pyRtResReq = CSRichText( wnd.rtReshReq )
		self.__pyRtResReq.align = "L"
		self.__pyRtResReq.lineFlat = "T"
		self.__pyRtResReq.text = ""

		self.__pyGodBeckon = Icon( wnd.godBeckon.icon )
		self.__pyGodBeckon.icon = ""
		self.__godsGroup = SelectorGroup()
		self.beastDatas = tongBeastData.getDatas()
		self.__pyGodIcons = {}
		self.__pyStAttrs = {}
		self.__pyAttrBar = {}
		for name, item in wnd.children:
			if name.startswith( "godAnimal_" ): #神兽图标
				index = int( name.split( "_" )[1])
				pyGodIcon = GodIcon( item, index )
				self.__pyGodIcons[index] = pyGodIcon
				self.__godsGroup.addSelector( pyGodIcon )
				beaClassName = BEAS_INDEX_MAP[index]
				if self.beastDatas.has_key( beaClassName ): #设置神兽头像
					modelNums = self.beastDatas[beaClassName][1]["modelNums"]
					if len( modelNums ) <= 0:return
					modelNumber = modelNums[random.randint(0, len( modelNums ) - 1 )]
					pyGodIcon.godTexture = modelLoader.getHeadTexture( modelNumber )
					pyGodIcon.modelNumber = modelNumber
			if name.startswith( "attr_" ): #神兽战斗属性
				attrStr = name[5:]
				pyStattr = AttrItem( item )
				pyStattr.title = labelGather.getText( "TongAbout:ShenShouBeckon", attrStr )
				pyStattr.text = ""
				self.__pyStAttrs[attrStr] = pyStattr
			if name.endswith( "_bar" ): #神兽血条和蓝条
				attrbar = name.split( "_" )[0]
				pyAttrBar = HFProgressBar( item.bar )
				pyAttrBar.clipMode = "RIGHT"
				pyAttrBar.value = 0.0
				self.__pyAttrBar[attrbar] = pyAttrBar

		labelGather.setLabel( wnd.lbTitle, "TongAbout:ShenShouBeckon", "lbTitle" )
		labelGather.setLabel( wnd.useMoneyText, "TongAbout:BuildReSearch", "useMoneyText" )
		labelGather.setLabel( wnd.actionText, "TongAbout:BuildReSearch", "actionText" )
		labelGather.setLabel( wnd.rendPanel.stTitle, "TongAbout:BuildReSearch", "resList" )
		labelGather.setLabel( wnd.reqPanel.bgTitle.stTitle, "TongAbout:ShenShouBeckon", "beckonReq" )
		labelGather.setLabel( wnd.statusPanel.bgTitle.stTitle, "TongAbout:ShenShouBeckon", "tongStatus" )
	# --------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_TONG_SHENSHOU_BRECKON"] = self.__toggleShows #弹出窗口
		self.__triggers["EVT_ON_TOGGLE_TONG_SET_SHENSHOU_INFO"] = self.__onCurShenshouChange #当前选择神兽改变通知
		self.__triggers["EVT_ON_TOGGLE_TONG_MONEY_CHANGE"] = self.__onTongMoneyChange #帮会资金改变
		self.__triggers["EVT_ON_TONG_SHENSHOU_SLECTED"] = self.__onSelectedShenshou #选择某一个神兽
		self.__triggers["EVT_ON_TONG_SHENSHOU_BRECKON_SUCCEED"] = self.__onBreckonSucc #神兽召唤成功后的回调
		self.__triggers["EVT_ON_TOGGLE_TONG_BUILD_INFO"] = self.__onReciveBuildInfo	#获取建筑信息
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )

	# -------------------------------------------------------
	def __toggleShows( self, shenshouLevel, shenshouType ):
		player = BigWorld.player()
		distance = csconst.COMMUNICATE_DISTANCE
		if hasattr( GUIFacade.getGossipTarget(), "getRoleAndNpcSpeakDistance" ):
			distance = GUIFacade.getGossipTarget().getRoleAndNpcSpeakDistance()
		self.__trapID = player.addTrapExt( distance, self.__onEntitiesTrapThrough )#打开窗口后为玩家添加对话陷阱
		self.__pyStAcadeLevel.text = labelGather.getText( "TongAbout:ShenShouBeckon", "ssLevel" )%shenshouLevel
		beaClassName = ""
		if shenshouType > 0: #没有召唤出来的神兽
			beaClassName = BEAS_INDEX_MAP[shenshouType]
		self.beckonIndex = shenshouType
		self.shenshouLevel = shenshouLevel
		if self.beastDatas.has_key( beaClassName ): #设置召唤出的神兽头像
			modelNums = self.beastDatas[beaClassName][1]["modelNums"]
			modelNum = ""
			if len( modelNums ) > 0:
				modelNum = modelNums[random.randint(0, len( modelNums ) - 1 )]
			self.__pyGodBeckon.icon = modelLoader.getHeadTexture( modelNum )
			self.__pyGodRender.resetModel( beaClassName )
			for attr, pyStattr in self.__pyStAttrs.iteritems():
				pyStattr.text = self.beastDatas[beaClassName][shenshouLevel][attr]
			for attrbar, pyAttrBar in self.__pyAttrBar.items():
				attrVal = self.beastDatas[beaClassName][shenshouLevel][attrbar]
				if attrVal <= 0:
					pyAttrBar.value = 0.0
				else:
					pyAttrBar.value = float( attrVal/attrVal )
			self.__pyStSelGod.text = self.beastDatas[beaClassName][shenshouLevel]["uname"]
		self.show()

	def __delTrap( self ) :
		player = BigWorld.player()
		if self.__trapID :
			player.delTrap( self.__trapID )									#删除玩家的对话陷阱
			self.__trapID = 0

	def __onEntitiesTrapThrough( self, entitiesInTrap ):
		gossiptarget = GUIFacade.getGossipTarget()							#获取当前对话NPC
		if gossiptarget and gossiptarget not in entitiesInTrap:				#如果NPC离开玩家对话陷阱
			self.__delTrap()
			self.hide()														#隐藏当前交易窗口

	def __onCurShenshouChange( self, shenshouLevel, shenshouType ):
		"""
		当前神兽改变通知
		"""
		self.__pyStAcadeLevel.text = labelGather.getText( "TongAbout:ShenShouBeckon", "ssLevel" )%shenshouLevel
		beaClassName = ""
		if shenshouType > 0: #没有召唤出来的神兽
			beaClassName = BEAS_INDEX_MAP[shenshouType]
		self.beckonIndex = shenshouType
		self.shenshouLevel = shenshouLevel
		if self.beastDatas.has_key( beaClassName ): #设置召唤出的神兽头像
			modelNums = self.beastDatas[beaClassName][1]["modelNums"]
			modelNum = ""
			if len( modelNums ) > 0:
				modelNum = modelNums[random.randint(0, len( modelNums ) - 1 )]
			self.__pyGodBeckon.icon = modelLoader.getHeadTexture( modelNum )
			self.__pyGodRender.resetModel( beaClassName )
			for attr, pyStattr in self.__pyStAttrs.iteritems():
				pyStattr.text = self.beastDatas[beaClassName][shenshouLevel][attr]
			for attrbar, pyAttrBar in self.__pyAttrBar.items():
				attrVal = self.beastDatas[beaClassName][shenshouLevel][attrbar]
				if attrVal <= 0:
					pyAttrBar.value = 0.0
				else:
					pyAttrBar.value = float( attrVal/attrVal )
			self.__pyStSelGod.text = self.beastDatas[beaClassName][shenshouLevel]["uname"]

	def __onSelectedShenshou( self, selIndex ):
		self.selIndex = selIndex
		for index, pyGodIcon in self.__pyGodIcons.items():
			pyGodIcon.selected = index == selIndex
		if self.__pyGodIcons.has_key( selIndex ):
			selPyIcon = self.__pyGodIcons[selIndex]
			modelNumber = selPyIcon.modelNumber
			self.__pyGodRender.resetModel( BEAS_INDEX_MAP[selIndex] )
		if BEAS_INDEX_MAP.has_key( selIndex ):
			className = BEAS_INDEX_MAP[selIndex]
			for attr, pyStattr in self.__pyStAttrs.iteritems():
				pyStattr.text = self.beastDatas[className][self.shenshouLevel][attr]
			for attrbar, pyAttrBar in self.__pyAttrBar.items():
				attrVal = self.beastDatas[className][self.shenshouLevel][attrbar]
				if attrVal <= 0:
					pyAttrBar.value = 0.0
				else:
					pyAttrBar.value = float( attrVal/attrVal )
		if BigWorld.player().tong_getCanUseMoney() >= 500000:
			reqmoney_color = ( 230, 227, 185 )
		else:
			reqmoney_color = ( 255, 0, 0 )
		priceText = utils.currencyToViewText( 500000 )
		req_Expense = labelGather.getText( "TongAbout:ItemReSearch", "consumMoney" )%( PL_Space.getSource( 4 ), priceText )
		req_Expense = PL_Font.getSource( req_Expense, fc = ( 230, 227, 185, 255 ) )
		req_Expense += PL_Font.getSource( fc = self.__defaultColor )
		self.__pyRtResReq.text = req_Expense
		self.__pyBeckonBtn.enable = selIndex != self.beckonIndex

	def __onBreckonSucc( self, index ):
		pass


	def __onTongMoneyChange( self, money ):
		"""
		帮会资金发生变化
		"""
		if not BigWorld.player().inWorld or not self.visible:
			return
		self.__showTongCanUseMoney()

	def __onReciveBuildInfo( self, buildData ):
		if buildData["type"] == csdefine.TONG_BUILDING_TYPE_JK: #金库信息
			self.__showTongCanUseMoney()

	def __showTongCanUseMoney( self ):
		"""
		显示帮会可用资金
		"""
		money = BigWorld.player().tong_getCanUseMoney()
		self.__pyRtUseMoney.text = utils.currencyToViewText( money )

	def __turnLeft( self ):
		BigWorld.cancelCallback( self.__turnModelCBID )
		self.__turnModel( False )
		LastKeyUpEvent.attach( self.__onLastKeyUpEvent )
		return True

	def __turnRight( self ):
		BigWorld.cancelCallback( self.__turnModelCBID )
		self.__turnModel( True )
		LastKeyUpEvent.attach( self.__onLastKeyUpEvent )
		return True

	def __turnModel( self, isRTurn ) :
		"""
		turning model on the mirror
		"""
		self.__pyGodRender.yaw += ( isRTurn and -0.1 or 0.1 )
		if BigWorld.isKeyDown( KEY_LEFTMOUSE ) :
			self.__turnModelCBID = BigWorld.callback( 0.1, Functor( self.__turnModel, isRTurn ) )

	def __onLastKeyUpEvent( self, key, mods ) :
		if key != KEY_LEFTMOUSE : return
		BigWorld.cancelCallback( self.__turnModelCBID )
		LastKeyUpEvent.detach( self.__onLastKeyUpEvent )

	def __beckonShenShou( self ):
		player = BigWorld.player()
		if self.selIndex == 0: return #第一个神兽为出战
		if self.selIndex == self.beckonIndex:
			# "该神兽已经存在!"
			showAutoHideMessage( 3.0, 0x09a1, mbmsgs[0x0c22] )
			return
		elif not player.tong_checkDutyRights( player.tong_grade, csdefine.TONG_RIGHT_PET_SELECT ):
			# "你没有选择神兽的权限!"
			showAutoHideMessage( 3.0, 0x09a2, mbmsgs[0x0c22] )
			return
		elif player.tong_getCanUseMoney() < 500000:
			# "帮会资金不足,选择或者更换神兽需要%d金帮会资金。"
			showAutoHideMessage( 3.0, mbmsgs[0x09a3] % 50, mbmsgs[0x0c22] )
			return

		player.tong_shenShouSelect( self.selIndex )

	# -----------------------------------------------------------
	# public
	# -----------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def show( self ):
		self.__showTongCanUseMoney()
		self.__onSelectedShenshou( 0 )
		self.__pyGodRender.enableDrawModel()
		Window.show( self )

	def hide( self ):
		Window.hide( self )
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )

	def onLeaveWorld( self ) :
		self.selIndex = 0
		self.beckonIndex = 0
		self.__pyGodRender.clearModel()
		self.__pyGodRender.disableDrawModel()
		for pyGodIcon in self.__pyGodIcons.itervalues():
			pyGodIcon.selected = False
		self.hide()

# -----------------------------------------------
from guis.common.PyGUI import PyGUI
from guis.controls.SelectableButton import SelectableButton

class GodIcon( SelectableButton ):
	def __init__( self, godIcon, index ):
		SelectableButton.__init__( self, godIcon )
		self.__pyIconBg = PyGUI( godIcon.iconBg )
		self.__pyGodIcon = Icon( godIcon.icon )
		self.__pyGodIcon.focus = True
		self.__pyGodIcon.crossFocus = True
		self.__pyGodIcon.onLClick.bind( self.__onGodSelected )
		self.__pyGodIcon.onMouseEnter.bind( self.__onGodEnter )
		self.__pyGodIcon.onMouseLeave.bind( self.__onGodLeave )
		if hasattr( godIcon,"cover" ):
			self.__pyCover = PyGUI( godIcon.cover )
			self.__pyCover.visible = False
		self.__selected = False
		self.index = index
		self.__modelNumber = ""

	def __onGodSelected( self, pyGodIcon ):
		if pyGodIcon is None:return
		ECenter.fireEvent( "EVT_ON_TONG_SHENSHOU_SLECTED", self.index )
		toolbox.infoTip.hide()

	def __onGodEnter( self, pyIcon ): #显示神兽信息
		beaDsp = self.getTongBeaDsp( self.index )
		toolbox.infoTip.showItemTips( self, beaDsp )

	def __onGodLeave( self, pyIcon ):
		toolbox.infoTip.hide()

	def getTongBeaDsp( self, selIndex ): #读取帮会建筑描述
		return tongBeastDsp.Datas[ selIndex ]
	# ----------------------------------------------------
	def __select( self ):
		if self.__pyCover:
			self.__pyCover.visible = True

	def __deselect( self ):
		if self.__pyCover:
			self.__pyCover.visible = False

	def _getSelected( self ):
		return self.__selected

	def _setSelected( self, selected ):
#		self.__pyReItem.selected = selected
		if selected:
			self.__select()
		else:
			self.__deselect()
		self.__selected = selected

	def _getGodTexture( self ):
		return self.__pyGodIcon.icon

	def _setGodTexure( self, texture ):
		self.__pyGodIcon.icon = texture

	def _getModelNumber( self ):
		return self.__modelNumber

	def _setModelNumber( self, modelNumber ):
		self.__modelNumber = modelNumber

	selected = property( _getSelected, _setSelected )
	godTexture = property( _getGodTexture, _setGodTexure )
	modelNumber = property( _getModelNumber, _setModelNumber )

class AttrItem( PyGUI ):
	def __init__( self, item ):
		PyGUI.__init__( self, item )
		self.__pyAttrText = StaticText( item.attrText )
		self.__pyStAttr = StaticText( item.attrValue )
		self.__pyStAttr.color = 255, 255, 255
		self.__pyStAttr.text = ""

	def _getText( self ):
		return self.__pyStAttr.text

	def _setText( self, text ):
		self.__pyStAttr.text = text

	def _getTitle( self ):
		return self.__pyAttrText.text

	def _setTitle( self, title ):
		self.__pyAttrText.text = title

	text = property( _getText, _setText )
	title = property( _getTitle, _setTitle )