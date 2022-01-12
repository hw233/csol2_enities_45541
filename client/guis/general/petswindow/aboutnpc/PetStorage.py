# -*- coding: gb18030 -*-
#
# $Id: PetStorage.py,v 1.7 2008-08-26 02:16:51 huangyongwei Exp $

"""
implement PetStorage Window
"""

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from guis.controls.ComboBox import ComboBox
from guis.controls.ODListPanel import ODListPanel
from guis.controls.ODPagesPanel import ODPagesPanel
from PetItem import PetItem
from gbref import rds
import event.EventCenter as ECenter
import GUIFacade
import csdefine
import csconst
import Const

class PetStorage( Window ):

	_cc_items_rows = ( 6, 1 )
	state1 = 'normal'
	state2 = 'setUp'
	state3 = 'notSetUp'

	def __init__( self ):
		wnd = GUI.load( "guis/general/petswindow/aboutnpc/petstorage.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True
		self.__trapID=None
		self.__storeCount = 0	# 当前仓库的大小
		self.__triggers = {}
		self.__storePetDataList = []
		self.__registerTriggers()
		self.__initeWnd( wnd )
		self.aa=45
		rds.mutexShowMgr.addMutexRoot( self, MutexGroup.PET1 )				# 添加到MutexGroup.PET1互斥组

	def __initeWnd( self, wnd ):
		labelGather.setLabel( wnd.lbTitle, "PetsWindow:PetStorage", "lbTitle" )
		self.__pyLbMyNum = StaticText( wnd.lbMyNum )
		self.__pyLbMyNum.text = ""

		self.__pyLbStorageNum = StaticText( wnd.lbStorageNum )
		self.__pyLbStorageNum.text = ""

		self.__pyMyList = ODListPanel( wnd.myPanel, wnd.myBar ) # 玩家宠物面板
		self.__pyMyList.onViewItemInitialized.bind( self.__onInitMyPet )
		self.__pyMyList.selectable = True
		self.__pyMyList.rMouseSelect = True
		self.__pyMyList.onDrawItem.bind( self.__onDrawMyPet )
		self.__pyMyList.onItemRClick.bind( self.__savePet )
		self.__pyMyList.onItemSelectChanged.bind( self.__onMyPetSelect )
		self.__pyMyList.ownerDraw = True
		self.__pyMyList.itemHeight = 63.0
		self.__pyMyList.viewSize = self._cc_items_rows

		self.__pyStoragePage = ODPagesPanel( wnd.storagePanel, wnd.pgIdxBar ) # 仓库面板
		self.__pyStoragePage.onViewItemInitialized.bind( self.__initStorePet)
		self.__pyStoragePage.onDrawItem.bind( self.__drawStorePet )
		self.__pyStoragePage.selectable = True
		self.__pyStoragePage.rMouseSelect = True
		self.__pyStoragePage.onItemRClick.bind( self.__takePet )
		self.__pyStoragePage.onItemSelectChanged.bind( self.__onStorePetSelect )
		self.__pyStoragePage.viewSize = self._cc_items_rows

		self.__pyLbTime = StaticText( wnd.lbTime )
		self.__pyLbTime.text = ""

		self.__pyBtnBack = HButtonEx( wnd.btnBack )
		self.__pyBtnBack.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnBack.onLClick.bind( self.__onBack )
		labelGather.setPyBgLabel( self.__pyBtnBack, "PetsWindow:PetStorage", "btnBack" )

	# --------------------------------------------------------------------
	# pravite
	# --------------------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_PST_OPEN_PET_STORAGE"]	 = self.__onEnterStorage # 进入宠物存储对话
		self.__triggers["EVT_ON_PST_OPEN_STORAGE_TIME"] = self.__onUpdateTime # 更新租赁剩余时间
		self.__triggers["EVT_ON_PST_STORED_PET"]	 = self.__onStorePet # 存储某一个宠物成功后的回调
		self.__triggers["EVT_ON_PST_TAKEN_PET"]	 = self.__onTakePet	# 取出某个宠物成功后的回调
		self.__triggers["EVT_ON_PCG_REMOVE_PET"]	= self.__onPetRemoved # 玩家放生一个宠物时调用
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )

	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( eventMacro, self )
	# ---------------------------------------------------------------
	def __onInitMyPet( self, pyViewItem ):
		pyMyPet = PetItem( DragMark.MY_PET_PANEL )
		pyViewItem.pyMyPet = pyMyPet
		pyViewItem.addPyChild( pyMyPet )
		pyMyPet.pos = 0, 0

	def __onDrawMyPet( self, pyViewItem ):
		petInfo = pyViewItem.listItem
		pyMyPet = pyViewItem.pyMyPet
		pyMyPet.selected = pyViewItem.selected
		if petInfo is None:
			petInfo = StorePet( self.state2)
		pyMyPet.updateInfo( petInfo )
	
	def __initStorePet( self, pyViewItem ):
		pyStorePet = PetItem()
		pyViewItem.pyStorePet = pyStorePet
		pyViewItem.addPyChild( pyStorePet )
		pyViewItem.dragFocus = False
		pyViewItem.focus = True
		pyStorePet.pos = 0, 0
	
	def __drawStorePet( self, pyViewItem ):
		petInfo = pyViewItem.pageItem
		pyStorePet = pyViewItem.pyStorePet
		pyStorePet.selected = pyViewItem.selected
		if petInfo is None:
			petInfo = StorePet( self.state3 )
		pyStorePet.updateInfo( petInfo )
	
	def __savePet( self, index ):
		selPetData = self.__pyMyList.selItem
		if selPetData is None:return
		BigWorld.player().pst_storePet( selPetData.dbid )
	
	def __takePet( self, index ):
		selPetData = self.__pyStoragePage.selItem
		if selPetData is None:return
		BigWorld.player().pst_takePet( selPetData.dbid )
	
	def __onMyPetSelect( self, selIndex ):
		if selIndex < 0: return
		for pyViewItem in self.__pyMyList.pyViewItems:
			itemIndex = pyViewItem.itemIndex
			pyMyPet = pyViewItem.pyMyPet
			pyMyPet.selected = itemIndex == selIndex
		
	def __onStorePetSelect( self, selIndex ):
		if selIndex < 0: return
		for pyViewItem in self.__pyStoragePage.pyViewItems:
			itemIndex = pyViewItem.itemIndex
			pyStorePet = pyViewItem.pyStorePet
			pyStorePet.selected = itemIndex == selIndex

	def __onEnterStorage( self, type, overdue, petDict ):
		player = BigWorld.player()
		distance = csconst.COMMUNICATE_DISTANCE
		if hasattr( GUIFacade.getGossipTarget(), "getRoleAndNpcSpeakDistance" ):
			distance = GUIFacade.getGossipTarget().getRoleAndNpcSpeakDistance()
		self.__trapID = BigWorld.addPot( GUIFacade.getGossipTarget().matrix,csconst.COMMUNICATE_DISTANCE, self.__onEntitiesTrapThrough )#打开窗口后为玩家添加对话陷阱
		if overdue: # 到期
			pass
		else: # 没有到期
			pass
		self.__pyMyList.clearItems()
		self.__storeCount = csconst.pst_storeCount[type]
		self.__storePetDataList = []
		for dbid, petData in petDict.items():
			petData.itemState = self.state1
			self.__storePetDataList.append( petData )
		self.__refeshStorePet()		
		self.show()

	def __delTrap( self ) :
		if self.__trapID is not None:
			BigWorld.delPot( self.__trapID )									#删除玩家的对话陷阱
			self.__trapID = None

	def __onEntitiesTrapThrough( self, isEnter,handle ):
		if not isEnter:				#如果NPC离开玩家对话陷阱
			BigWorld.player().mailOverWithNPC()
			self.hide()														#隐藏当前繁殖窗口

	# -------------------------------------------------------------------
	def __onUpdateTime( self, time ):
		remainDays = time/( 24*3600 )
		remainHours = ( time%( 24*3600 ) )/3600
		self.__pyLbTime.text = labelGather.getText( "PetsWindow:PetStorage", "remainTime" )%( remainDays, remainHours )

	def __onStorePet( self, pet ): # 存放宠物
		petData = StorePet(self.state1, pet["databaseID"], pet["name"], pet["level"], pet["species"], pet["modelNumber"] )
		for petStoreData in self.__storePetDataList:
			if pet["databaseID"] == petStoreData.dbid:
				return
		self.__storePetDataList.append( petData )
		self.__refeshMyList()
		self.__refeshStorePet()
	
	def __onTakePet( self, dbid ): # 取出宠物
		player = BigWorld.player()
		petEpitomes = player.pcg_getPetEpitomes()
		epitome = petEpitomes.get( dbid, None )
		if epitome is None:return
		for petData in self.__storePetDataList:
			if petData.dbid == dbid:
				self.__storePetDataList.remove( petData )
		self.__refeshStorePet()
		self.__refeshMyList()	
		
		maxNum = player.pcg_getKeepingCount()

	def __onPetRemoved( self, dbid ):
		self.__refeshMyList()

	def __onBack( self ):
		entity = GUIFacade.getGossipTarget()
		if entity is not None:
			GUIFacade.gossipHello( entity )
			self.hide()
			
	def __refeshStorePet( self ):
		self.__pyStoragePage.clearItems()
		for petData in self.__storePetDataList:
			self.__pyStoragePage.addItem( petData )
		restSetUpNum = self.__storeCount - len( self.__storePetDataList )
		for i in range( restSetUpNum ):
			petData = StorePet( self.state2 )
			self.__pyStoragePage.addItem( petData )
		storeCount = len( self.__storePetDataList )
		self.__pyLbStorageNum.text = labelGather.getText( "PetsWindow:PetStorage", "storageNums" )%( storeCount, self.__storeCount )
			
	def __refeshMyList( self ):
		player = BigWorld.player()
		petEpitomes = player.pcg_getPetEpitomes()	#玩家身上宠物
		maxNum = player.pcg_getKeepingCount()		#可携带宠物数量
		self.__pyMyList.clearItems()
		for dbid, epitome in petEpitomes.iteritems():		#绘制宠物信息
			petData = StorePet( self.state1, dbid, epitome.name, epitome.level, epitome.species, epitome.modelNumber )
			self.__pyMyList.addItem( petData )
		setUpNum = maxNum  - len( petEpitomes )		# 已开启宠物格子数量
		for i in range( setUpNum ):
			petData = StorePet( self.state2 )
			self.__pyMyList.addItem( petData )
		notSetUpNum = 6 - maxNum		# 未开启宠物格子数量
		for i in range( notSetUpNum ):
			petData = StorePet( self.state3 )
			self.__pyMyList.addItem( petData )
		self.__pyLbMyNum.text = labelGather.getText( "PetsWindow:PetStorage", "myNums" )%( len( petEpitomes ), maxNum )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def show( self ):
		player = BigWorld.player()
		petEpitomes = player.pcg_getPetEpitomes()
		maxNum = player.pcg_getKeepingCount()
		self.__pyLbMyNum.text = labelGather.getText( "PetsWindow:PetStorage", "myNums" )%( len( petEpitomes ), maxNum )
		self.__refeshMyList()	
		Window.show( self )

	def hide( self ):
		self.__pyStoragePage.clearItems()
		self.__pyMyList.clearItems()
		self.__delTrap()
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )
		Window.hide( self )
		

	def onLeaveWorld( self ):
		self.hide()
		

class StorePet:
	def __init__( self, itemState, dbid = '', name = '', level = '', species = '', modelNumber = '', state = '' ):
		self.itemState = itemState
		self.dbid = dbid
		self.name = name
		self.level = level
		self.species = species
		self.modelNumber = modelNumber
