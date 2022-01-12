# -*- coding: gb18030 -*-
#
# $Id: StorageTenancy.py,v 1.4 2008-08-26 02:16:51 huangyongwei Exp $

"""
implement StorageTenancy class
"""
from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.common.Window import Window
from guis.controls.StaticText import StaticText
from guis.controls.ButtonEx import HButtonEx
from guis.controls.SelectableButton import SelectableButton
from guis.controls.Control import Control
from guis.controls.SelectorGroup import SelectorGroup
from guis.controls.ListItem import ListItem
from PetFormulas import formulas
import GUIFacade
import csconst
import csdefine

class StorageTenancy( Window ):

	def __init__( self ):
		wnd = GUI.load( "guis/general/petswindow/aboutnpc/storagetenancy.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True
		self.__triggers = {}
		self.__registerTriggers()
		self.__initWnd( wnd )

	def __initWnd( self, wnd ):
		labelGather.setLabel( wnd.lbTitle, "PetsWindow:StorageTenancy", "lbTitle" )
		self.__pyStorages = SelectorGroup()
		for name, item in wnd.children: # 初始化大小仓库
			if "storage_" not in name:continue
			type = int( name.split( "_" )[1] )
			pyStorage = StorageItem( item )
			pyStorage.setStatesMapping( UIState.MODE_R3C1 )
			if csconst.pst_storeCount.has_key( type ):
				num =csconst.pst_storeCount[type]
				pyStorage.tenancyType = type
				pyStorage.spaceStr = labelGather.getText( "PetsWindow:StorageTenancy", "spaceNums" )%num
			pyStorage.type = type
			self.__pyStorages.addSelector( pyStorage )
		self.__pyStorages.onSelectChanged.bind( self.__onSelectChange )
		self.__pyTenancyPanel = TenancyPanel( wnd.tenancyPanel ) # 设置租赁按钮

		self.__pyBtnBack = HButtonEx( wnd.btnBack )
		self.__pyBtnBack.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnBack.onLClick.bind( self.__onBack )
		labelGather.setPyBgLabel( self.__pyBtnBack, "PetsWindow:StorageTenancy", "btnBack" )

	# ------------------------------------------------------------------------
	# private
	# ------------------------------------------------------------------------
	def __registerTriggers( self ) :
		"""
		register event triggers
		"""
		self.__triggers["EVT_ON_PST_OPEN_STORAGE_TENANCY"] = self.__onStorageTencany
		self.__triggers["EVT_ON_PST_STORAGE_TENANCY_RESULT"] = self.__onTencanyResult
		for macroName in self.__triggers.iterkeys():
			GUIFacade.registerEvent( macroName, self )

	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for macroName in self.__triggers.iterkeys() :
			GUIFacade.unregisterEvent( macroName, self )

	# ----------------------------------------------------
	def __onStorageTencany( self, ObjectID  ):
		player = BigWorld.player()
		distance = csconst.COMMUNICATE_DISTANCE
		if hasattr( GUIFacade.getGossipTarget(), "getRoleAndNpcSpeakDistance" ):
			distance = GUIFacade.getGossipTarget().getRoleAndNpcSpeakDistance()
		self.__trapID = player.addTrapExt( csconst.COMMUNICATE_DISTANCE, self.__onEntitiesTrapThrough )#打开窗口后为玩家添加对话陷阱
		self.show()

	def __delTrap( self ) :
		player = BigWorld.player()
		if self.__trapID :
			player.delTrap( self.__trapID )									#删除玩家的对话陷阱
			self.__trapID = 0

	def __onEntitiesTrapThrough( self, entitiesInTrap ):
		player = BigWorld.player()
		gossiptarget = GUIFacade.getGossipTarget()						#获取当前对话NPC
		if gossiptarget and gossiptarget not in entitiesInTrap:				#如果NPC离开玩家对话陷阱
			player.mailOverWithNPC()
			self.hide()														#隐藏当前繁殖窗

	def __onTencanyResult( self, result ):
		if result:
			self.hide()
		else:
			# 金元宝不足
			showAutoHideMessage( 3.0, 0x0ca1, "", self )

	def __onBack( self ):
		entity = GUIFacade.getGossipTarget()
		if entity is not None:
			GUIFacade.gossipHello( entity )
			self.hide()

	def __onSelectChange( self, pyCon ): # 选择某一仓库类型
		if pyCon is None: return
		type = pyCon.type
		self.__pyTenancyPanel.setCostByType( type ) # 设置不同类型、不同时间的花费显示

	# ---------------------------------------------------------------------------
	# public
	# ---------------------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		"""
		triggering from client base
		"""
		self.__triggers[macroName]( *args )

	def onLeaveWorld( self ) :	# wsf add
		"""
		角色离开世界
		"""
		self.hide()

	def show( self ):
		Window.show( self )

	def hide( self ):
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )
		Window.hide( self )

# ------------------------------------------------------------------
class StorageItem( SelectableButton ):
	def __init__( self, panel ):
		SelectableButton.__init__( self, panel )
		self.__pyLbType = StaticText( panel.lbType )
		self.__pyLbType.text = ""

		self.__pyLbSpace = StaticText( panel.lbSpace )
		self.__pyLbSpace.text = ""

		self.__tenancyType = -1

	def _getTenancyType( self ):
		return self.__tenancyType

	def _setTenancyType( self, type ):
		self.__tenancyType = type
		if type == csdefine.PET_STORE_TYPE_LARGE:
			self.__pyLbType.text = labelGather.getText( "PetsWindow:StorageTenancy", "bigStorage" )
		else:
			self.__pyLbType.text = labelGather.getText( "PetsWindow:StorageTenancy", "smallStorage" )

	def _getSpaceStr( self ):
		return self.__pyLbSpace.text

	def _setSpaceStr( self, spaceStr ):
		self.__pyLbSpace.text = spaceStr

	tenancyType = property( _getTenancyType, _setTenancyType )
	spaceStr = property( _getSpaceStr, _setSpaceStr )

# -------------------------------------------------------------------
class TenancyPanel( PyGUI ):
	def __init__( self, panel ):
		PyGUI.__init__( self, panel )
		self.__initPanel( panel )
		self.__type = -1

	def __initPanel( self, panel ):
		self.__pyTenancys = {}
		for name, item in panel.children:
			if "tenancy_" not in name:continue
			key = int( name.split( "_" )[1] )
			pyTenancy = TenancyItem( item )
			pyTenancy.text = labelGather.getText( "PetsWindow:StorageTenancy", name )
			pyTenancy.leaseTimes = key
			self.__pyTenancys[key] = pyTenancy

	def setCostByType( self, type ):
		self.__type = type
		for key, pyTenancy in self.__pyTenancys.iteritems():
			pyTenancy.setCost( type )

	def _gettype( self ):
		return self.__type

	def _setType( self, type ):
		self.__type = type

	type = property( _gettype, _setType )
# -------------------------------------------------------------------
class TenancyItem( Control ):
	def __init__( self, item ):
		Control.__init__( self, item )
		self.__leaseTimes = 0 # 租赁时间倍数，单位为15天
		self.__storageType = 0 # 租赁类型，大和小

		self.__pyTenancyBtn = HButtonEx( item.tenancyBtn )
		self.__pyTenancyBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyTenancyBtn.enable = False
		self.__pyTenancyBtn.onLClick.bind( self.__onTenancy )
	
		self.__pyStTime = StaticText( item.tenancyBtn.lbText )

		self.__pyLblbCost = StaticText( item.lbCost )
		self.__pyLblbCost.text = ""

	def __onTenancy( self ):
		player = BigWorld.player()
		npc = GUIFacade.getGossipTarget()
		player.base.pst_hireStorage( self.__storageType, self.__leaseTimes )

	def setCost( self, storageType ):
		self.__storageType = storageType
		self.__pyTenancyBtn.enable = True
		cost = formulas.getStorageCost( storageType, self.__leaseTimes )
		self.__pyLblbCost.text = labelGather.getText( "PetsWindow:StorageTenancy", "costText" )%cost

	def _getLeaseTimes( self ):
		return self.__leaseTimes

	def _setLeaseTimes( self, times ):
		self.__leaseTimes = times

	def _getText( self ):
		return self.__pyStTime.text

	def _setText( self, text ):
		self.__pyStTime.text = text

	leaseTimes = property( _getLeaseTimes, _setLeaseTimes )
	text = property( _getText, _setText )
