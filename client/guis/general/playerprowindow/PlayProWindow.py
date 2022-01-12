# -*- coding: gb18030 -*-
#
# $Id: PlayProWindow.py,v 1.23 2008-08-26 02:18:12 huangyongwei Exp $

import GUIFacade
import csdefine
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.StaticText import StaticText
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabPage
from guis.controls.Button import Button
from EquipPanel import EquipPanel
from TitlesPanel import TitlesPanel
from PrestigeWindow import PrestigeWindow
from GemPanel import GemPanel
from TalisPanel import TalisPanel
from Helper import courseHelper
import ItemTypeEnum
from ItemsFactory import ObjectItem as ItemInfo
from config.client.msgboxtexts import Datas as mbmsgs

class PlayProWindow( Window ):

	titles_map = { 0: labelGather.getText( "PlayerProperty:EquipPanel", "lbTitle" ),
				1: labelGather.getText( "PlayerProperty:TitlePanel", "lbTitle" ),
				2: labelGather.getText( "PlayerProperty:PrestPanel", "lbTitle" ),
				3: labelGather.getText( "PlayerProperty:GemPanel", "lbTitle" ),
				4: labelGather.getText( "PlayerProperty:TalisPanel", "lbTitle" )
				}

	def __init__( self ):
		wnd = GUI.load( "guis/general/playerprowindow/window.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True

		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( wnd )

	def __initialize( self, wnd ):
		self.__pyLbTitle = StaticText( wnd.lbTitle )
		self.__pyLbTitle.text = ""
		self.__pyLbTitle.charSpace = 2

		self.__pyTabCtr = TabCtrl( wnd.tc )
		self.__pyEquipPanel = EquipPanel( csdefine.KB_EQUIP_ID, wnd.tc.panel_0, self )
		self.__pyEquipBtn = TabButton( wnd.tc.btn_0 )
		self.__pyEquipBtn.selectedForeColor = ( ( 142, 216, 217, 255 ) )
		labelGather.setPyBgLabel( self.__pyEquipBtn, "PlayerProperty:main", "btn_0" )
#		self.__pyEquipBtn.disableMapping = util.getStateMapping( self.__pyEquipBtn.size, UIState.MODE_R3C1, UIState.ST_R1C1 )
#		self.__pyEquipBtn.commonMapping = util.getStateMapping( self.__pyEquipBtn.size, UIState.MODE_R3C1, UIState.ST_R2C1 )
#		self.__pyEquipBtn.selectedMapping = util.getStateMapping(self.__pyEquipBtn.size, UIState.MODE_R3C1, UIState.ST_R3C1 )
		self.__pyTabCtr.addPage( TabPage( self.__pyEquipBtn, self.__pyEquipPanel ) )

		self.__pyTitlePanel = TitlesPanel( wnd.tc.panel_1, self )
		self.__pyTitleBtn = TabButton( wnd.tc.btn_1 )
		self.__pyTitleBtn.selectedForeColor = ( 142, 216, 217, 255 )
		labelGather.setPyBgLabel( self.__pyTitleBtn, "PlayerProperty:main", "btn_1" )
		self.__pyTabCtr.addPage( TabPage( self.__pyTitleBtn, self.__pyTitlePanel ) )

		self.__pyCreditPanel = PrestigeWindow( wnd.tc.panel_2, self )
		self.__pyCreditBtn = TabButton( wnd.tc.btn_2 )
		self.__pyCreditBtn.selectedForeColor = ( 142, 216, 217, 255 )
		labelGather.setPyBgLabel( self.__pyCreditBtn, "PlayerProperty:main", "btn_2" )
#		self.__pyCreditBtn.disableMapping = util.getStateMapping( self.__pyCreditBtn.size, UIState.MODE_R3C1, UIState.ST_R1C1 )
#		self.__pyCreditBtn.commonMapping = util.getStateMapping( self.__pyCreditBtn.size, UIState.MODE_R3C1, UIState.ST_R2C1 )
#		self.__pyCreditBtn.selectedMapping = util.getStateMapping(self.__pyCreditBtn.size, UIState.MODE_R3C1, UIState.ST_R3C1 )
		self.__pyTabCtr.addPage( TabPage( self.__pyCreditBtn, self.__pyCreditPanel ) )

		self.__pyGemPanel = GemPanel( wnd.tc.panel_3 )
		self.__pyGemBtn = TabButton( wnd.tc.btn_3 )
		self.__pyGemBtn.selectedForeColor = ( 142, 216, 217, 255 )
		labelGather.setPyBgLabel( self.__pyGemBtn, "PlayerProperty:main", "btn_3" )
		self.__pyGemPage = TabPage( self.__pyGemBtn, self.__pyGemPanel )
		self.__pyGemPage.enable = False
#		self.__pyGemBtn.disableMapping = util.getStateMapping( self.__pyGemBtn.size, UIState.MODE_R3C1, UIState.ST_R1C1 )
#		self.__pyGemBtn.commonMapping = util.getStateMapping( self.__pyGemBtn.size, UIState.MODE_R3C1, UIState.ST_R2C1 )
#		self.__pyGemBtn.selectedMapping = util.getStateMapping(self.__pyGemBtn.size, UIState.MODE_R3C1, UIState.ST_R3C1 )
		self.__pyTabCtr.addPage( self.__pyGemPage  )

		self.__pyTalisPanel = TalisPanel( wnd.tc.panel_4 )
		self.__pyTalisBtn = TabButton( wnd.tc.btn_4 )
		self.__pyTalisBtn.selectedForeColor = ( 142, 216, 217, 255 )
		labelGather.setPyBgLabel( self.__pyTalisBtn, "PlayerProperty:main", "btn_4" )
		self.__pyTalisPage = TabPage( self.__pyTalisBtn, self.__pyTalisPanel )
		self.__pyTalisPage.enable = False
		self.__pyTabCtr.addPage( self.__pyTalisPage  )

		self.__pyTabCtr.onTabPageSelectedChanged.bind( self.__onPageChange )

	# ----------------------------------------------------------------
	# pribvate
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_EQUIP_WINDOW"] = self.__toggleEquipPanel
		self.__triggers["EVT_ON_TOGGLE_CREDIT_WINDOW"] = self.__toggleCreditPanel
		self.__triggers["EVT_ON_TOGGLE_GEM_WINDOW"] = self.__toggleGemPanel
		self.__triggers["EVT_ON_EXP_GEM_ACRIVATED"] = self.__toggleActiveGem #开启宝石界面
		self.__triggers["EVT_ON_EXP_GEM_SHOW"] = self.__showGem #显示宝石界面
		self.__triggers["EVT_ON_ROLE_ACTIVE_TALISNAM"] = self.__onActiveTalis #是否装备法宝
		self.__triggers["EVT_ON_TOGGLE_TALISMAN_WINDOW"] = self.__toggleTalisman
		for key in self.__triggers.iterkeys() :
			GUIFacade.registerEvent( key, self )

	def __unregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			GUIFacade.unregisterEvent( key, self )

	# -------------------------------------------------
	def __toggleEquipPanel( self ) :
		if self.visible and self.__pyTabCtr.pySelPage.index == 0 :
			self.hide()
		else :
			self.__pyEquipPanel.initSociaInfo()
			self.__pyLbTitle.text = self.titles_map[0]
			self.show( 0 )

	def __toggleCreditPanel( self ) :
		if self.visible and self.__pyTabCtr.pySelPage.index == 1 :
			self.hide()
		else :
			self.__pyLbTitle.text = self.titles_map[1]
			self.show( 1 )

	def __toggleTalisman( self ) :
		"""
		打开/关闭法宝界面
		"""
		if self.visible and self.__pyTabCtr.pySelPage.index == 4 :
			self.hide()
		else :
			if self.__pyTalisPage.enable :
				self.__pyLbTitle.text = self.titles_map[4]
				self.show( 4 )
			else :
				self.pyMsgBox = getattr( self, "pyMsgBox", None )
				if self.pyMsgBox : self.pyMsgBox.hide()
				# "您未装备法宝"
				self.pyMsgBox = showAutoHideMessage( 3.0, 0x0d21, mbmsgs[0x0c22] )

	def __toggleGemPanel( self ) :
		if self.visible and self.__pyTabCtr.pySelPage.index == 3 :
			self.hide()
		else :
			if not BigWorld.player().isRoleTrainGemActive():
				self.pyBox = getattr( self, "pyBox", None )
				if self.pyBox:self.pyBox.hide()
				# "您的的经验代练界面尚未激活"
				self.pyBox = showAutoHideMessage( 3.0, 0x0d22, mbmsgs[0x0c22] )
				return
			self.__pyLbTitle.text = self.titles_map[3]
			self.show( 3 )

	def __toggleActiveGem( self ):
		self.__pyGemPage.enable = True

	def __showGem( self ):
		if not BigWorld.player().isRoleTrainGemActive():
			return
		self.__pyLbTitle.text = self.titles_map[3]
		self.show(3)

	def __onActiveTalis( self, itemInfo ):
		self.__pyTalisPage.enable = itemInfo is not None
		self.__pyTalisPanel.upDateTalisman( itemInfo )
		if itemInfo is None and self.__pyTabCtr.pySelPage.index == 3: #当前选择为法宝但被卸下,则选择玩家属性
			self.__pyTabCtr.pySelPage = self.__pyTabCtr.pyPages[0]

	def __onPageChange( self, pyCtrl ):
		selIndex = pyCtrl.pySelPage.index
		self.__pyLbTitle.text = self.titles_map[selIndex]
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def __disableModelRenderer( self ):
		if not self.rvisible:
			self.__pyEquipPanel.onHide()			# 主要是disable ModelRenderer的渲染

	def onEnterWorld( self ) :
		player = BigWorld.player()
		itemsBag = player.itemsBag
		self.__pyEquipPanel.onEnterWorld()
		self.__pyTitlePanel.onEnterWorld()
		BigWorld.callback( 1.0, self.__disableModelRenderer )
		self.__pyTitlePanel.onEnterWorld()
		self.__pyGemPage.enable = player.isRoleTrainGemActive()
#		self.__pyTalisPage.enable = itemsBag.orderHasItem( ItemTypeEnum.CEL_TALISMAN ) #判断玩家是否装备了法宝
		if itemsBag.orderHasItem( ItemTypeEnum.CEL_TALISMAN ):
			item = itemsBag.getByOrder( ItemTypeEnum.CEL_TALISMAN )
			itemInfo = ItemInfo( item )
			self.__pyTalisPanel.upDateTalisman( itemInfo )

	def onLeaveWorld( self ) :
		self.__pyEquipPanel.reset()
		self.__pyCreditPanel.reset()
		self.__pyGemPage.enable = False
		self.__pyTalisPage.enable = False
		self.__pyGemPanel.reset()
		self.__pyTalisPanel.reset()
		self.__pyTitlePanel.reset()
		self.hide()

	# -------------------------------------------------
	def show( self, index = 0 ) :
		self.__pyGemPage.enable = BigWorld.player().isRoleTrainGemActive()
		count = self.__pyTabCtr.pageCount
		if index < 0 or index >= count : index = 0
		self.__pyTabCtr.pyPages[index].selected = True
		self.__pyGemPanel.initGes()
		self.__pyTabCtr.pySelPage.pyPanel.onShow()
		self.__pyTabCtr.pyPanels[1].firstLog = True
		Window.show( self )

	def hide( self ):
		Window.hide( self )
		self.__pyEquipPanel.resetModelAngle()
		self.__pyTabCtr.pySelPage.pyPanel.onHide()
