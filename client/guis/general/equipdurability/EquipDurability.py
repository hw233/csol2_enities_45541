# -*- coding: gb18030 -*-
#
# $Id: EquipDurability.py,v 1.18 2008-08-26 02:13:43 huangyongwei Exp $

"""
imlement durabilityshow window
"""
from guis import *
import BigWorld
from guis.common.PyGUI import PyGUI
from guis.common.RootGUI import RootGUI
import ItemTypeEnum as ItemType
from DurabilityItem import DurabilityItem
from ItemsFactory import ObjectItem
import event.EventCenter as ECenter
import csdefine
import GUIFacade

class EquipDurability( RootGUI ):

	__cc_itemMaps = {
					  "weapon"    : ItemType.CEL_RIGHTHAND, 	#sword
					  "bow"       : ItemType.CEL_RIGHTHAND,		#bow
					  "shield"    : ItemType.CEL_LEFTHAND, 		#left hand
					  "head"      : ItemType.CEL_HEAD, 			#head
					  "body"      : ItemType.CEL_BODY, 			#jacket
					  "breech"    : ItemType.CEL_BREECH,		#trousers
					  "leftHand"  : ItemType.CEL_VOLA, 			#lefthand
					  "rightHand" : ItemType.CEL_VOLA,			#righthand
					  "waist"     : ItemType.CEL_HAUNCH,		#waist
					  "leftWrist" : ItemType.CEL_CUFF,			#leftWrist
					  "rightWrist": ItemType.CEL_CUFF,			#rightWrist
					   "shoes"    :  ItemType.CEL_FEET			#shose
					   }
	def __init__( self ):
		wnd = GUI.load( "guis/general/equipdurability/window.gui" )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		self.h_dockStyle = "RIGHT"
		self.v_dockStyle = "TOP"
		self.focus = False
		self.posZSegment = ZSegs.L5
		self.activable_ = False
		self.escHide_ 		 = False
		self.__itemInfo = None
		self.__triggers = {}
		self.__registerTriggers()
		self.__pyItems = {}
		self.__pyShowItems = []
		self.__initialize( wnd )

	#-------------------------------------------------------------------
	# private
	#-------------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_EQUIPBAG_ADD_ITEM"] = self.__onAddItems
		self.__triggers["EVT_ON_EQUIPBAG_REMOVE_ITEM"] = self.__onRemoveEquip
		self.__triggers["EVT_ON_EQUIPBAG_UPDATE_ITEM"] = self.__onUpdateEquip
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )
	#-------------------------------------------------------

	def __initialize( self, wnd ):
		self.__pyItems[ItemType.CEL_VOLA] = []
		self.__pyItems[ItemType.CEL_RIGHTHAND] = []
		self.__pyItems[ItemType.CEL_CUFF] = []
		for name,equip in wnd.children:
			if self.__cc_itemMaps.has_key( name ):
				if name == "leftHand" or name == "rightHand":
					pyItem = DurabilityItem( equip )
					self.__pyItems[ItemType.CEL_VOLA].append( pyItem )
				elif name == "leftWrist" or name == "rightWrist":
					pyItem = DurabilityItem( equip )
					self.__pyItems[ItemType.CEL_CUFF].append( pyItem )
				elif name == "weapon" or name == "bow":
						pyItem = DurabilityItem( equip )
						pyItem.name = name
						self.__pyItems[ItemType.CEL_RIGHTHAND].append( pyItem )
				else :
					mapIndex = self.__cc_itemMaps[name]
					pyItem = DurabilityItem( equip )
					pyItem.visibe = True
					self.__pyItems[mapIndex] = [pyItem]

	def __clearItems( self ):
		for itemList in self.__pyItems.itervalues():
			for pyItem in itemList:
				pyItem.visible = False

	def __onAddItems( self, itemInfo ):
		player = BigWorld.player()
		classRace = player.getClass()
		kitbagID = itemInfo.kitbagID
		if kitbagID == csdefine.KB_EQUIP_ID and \
			itemInfo.orderID not in [ItemType.CEL_NECK, ItemType.CEL_LEFTFINGER, ItemType.CEL_RIGHTFINGER, ItemType.CEL_CIMELIA ]:
			index = itemInfo.orderID
			pyItemList = self.__pyItems.get( index )
			if pyItemList is None: return
			if index == ItemType.CEL_RIGHTHAND: #右手武器
				tmpList = []
				if classRace == csdefine.CLASS_ARCHER: #如果是射手则只显示弓
					for pyItem in pyItemList:
						if pyItem.name == "bow":
							tmpList.append( pyItem )
				else:
					for pyItem in pyItemList:
						if pyItem.name == "weapon":
							tmpList.append( pyItem )
				for pyItem in tmpList:
					pyItem.update( itemInfo )
					if pyItem.showFlag == True and pyItem not in self.__pyShowItems:
						self.__pyShowItems.append( pyItem )
						self.__isOnShow()
			else:
				for pyItem in pyItemList:
					pyItem.update( itemInfo )
					if pyItem.showFlag == True and pyItem not in self.__pyShowItems:
						self.__pyShowItems.append( pyItem )
						self.__isOnShow()

	def __onRemoveEquip( self,itemInfo ):
		player = BigWorld.player()
		classRace = player.getClass()
		kitbagID = itemInfo.kitbagID
		if kitbagID == csdefine.KB_EQUIP_ID and \
			itemInfo.orderID not in [ItemType.CEL_NECK, ItemType.CEL_LEFTFINGER, ItemType.CEL_RIGHTFINGER, ItemType.CEL_CIMELIA ]:
			index = itemInfo.orderID
			pyItemList = self.__pyItems.get( index )
			if pyItemList is None: return
			if index == ItemType.CEL_RIGHTHAND: #右手武器
				tmpList = []
				if classRace == csdefine.CLASS_ARCHER: #如果是射手则只显示弓
					for pyItem in pyItemList:
						if pyItem.name == "bow":
							tmpList.append( pyItem )
				else:
					for pyItem in pyItemList:
						if pyItem.name == "weapon":
							tmpList.append( pyItem )
				for pyItem in tmpList:
					pyItem.update( None )
					if pyItem in self.__pyShowItems:
						self.__pyShowItems.remove( pyItem )
						self.__isOnShow()
			else:
				for pyItem in pyItemList:
					pyItem.update( None )
					if pyItem in self.__pyShowItems:
						self.__pyShowItems.remove( pyItem )
						self.__isOnShow()

	def __onUpdateEquip( self, itemInfo ):
		player = BigWorld.player()
		classRace = player.getClass()
		kitbagID = itemInfo.kitbagID
		if kitbagID == csdefine.KB_EQUIP_ID and \
			itemInfo.orderID not in [ItemType.CEL_NECK, ItemType.CEL_LEFTFINGER, ItemType.CEL_RIGHTFINGER, ItemType.CEL_CIMELIA ]:
			index = itemInfo.orderID
			pyItemList = self.__pyItems.get( index )
			if pyItemList is None: return
			if index == ItemType.CEL_RIGHTHAND: #右手武器
				tmpList = []
				if classRace == csdefine.CLASS_ARCHER: #如果是射手则只显示弓
					for pyItem in pyItemList:
						if pyItem.name == "bow":
							tmpList.append( pyItem )
				else:
					for pyItem in pyItemList:
						if pyItem.name == "weapon":
							tmpList.append( pyItem )
				for pyItem in tmpList:
					pyItem.update( itemInfo )
					if pyItem.showFlag == True and pyItem not in self.__pyShowItems:
						self.__pyShowItems.append( pyItem )
					elif pyItem.showFlag == False and pyItem in self.__pyShowItems:
						self.__pyShowItems.remove( pyItem )
					self.__isOnShow()
			else:
				for pyItem in pyItemList:
					pyItem.update( itemInfo )
					if pyItem.showFlag == True and pyItem not in self.__pyShowItems:
						self.__pyShowItems.append( pyItem )
					elif pyItem.showFlag == False and pyItem in self.__pyShowItems:
						self.__pyShowItems.remove( pyItem )
					self.__isOnShow()

	def __isOnShow( self ):
		if len( self.__pyShowItems ) >= 1:
			RootGUI.show( self )
			self.__showItems()
		elif len( self.__pyShowItems ) == 0:
			self.__clearItems()

	def __showItems( self ):
		self.__clearItems()
		player = BigWorld.player()
		classRace = player.getClass()
		for equip in player.getItems( csdefine.KB_EQUIP_ID ):
			if equip is None:continue
			itemInfo = ObjectItem( equip )
			orderID = equip.getOrder()
			if self.__pyItems.has_key( orderID ):
				pyItemList = self.__pyItems[orderID]
				if orderID == ItemType.CEL_RIGHTHAND:
					tmpList = []
					if classRace == csdefine.CLASS_ARCHER: #如果是射手则只显示弓
						for pyItem in pyItemList:
							if pyItem.name == "bow":
								tmpList.append( pyItem )
					else:
						for pyItem in pyItemList:
							if pyItem.name == "weapon":
								tmpList.append( pyItem )
					for pyItem in tmpList:
						pyItem.visible = True
				else:
					for pyItem in pyItemList:
						pyItem.visible = True
	#-------------------------------------------------------------
	# public
	#-------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ) :
		self.hide()

	def show( self ):
		self.__isOnShow()
		RootGUI.show( self )

	def hide( self ):
		RootGUI.hide( self )

	def afterStatusChanged( self, oldStatus, newStatus ) :

		if oldStatus == Define.GST_BACKTO_ROLESELECT_LOADING :
			self.__itemInfo = None
			#self.__pyItems = {}
			self.__pyShowItems = []