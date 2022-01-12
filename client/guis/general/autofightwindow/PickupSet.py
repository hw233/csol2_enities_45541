# -*- coding: gb18030 -*-
#
# $Id: PlusSkillSet.py,v 1.5 2008-07-24 09:40:16 wangshufeng Exp $

"""
implement autofight window
"""
from guis import *
from guis.UIFixer import hfUILoader
from LabelGather import labelGather
from guis.common.Window import Window
from AbstractTemplates import Singleton
from guis.controls.Button import Button
from guis.controls.ODComboBox import ODComboBox, InputBox
from guis.controls.ListPanel import ListPanel
from guis.controls.StaticText import StaticText
from guis.controls.RadioButton import RadioButtonEx
from guis.controls.CheckerGroup import CheckerGroup
from guis.controls.TextBox import TextBox
from guis.controls.ListItem import SingleColListItem
from config.client.PickTypeConfig import Datas as pickupTypeDatas
import skills
import csdefine
import csstatus

class PickupSet( Singleton, Window ):

	__instance = None

	def __init__( self ):
		assert PickupSet.__instance is None,"PickupSet instance has been created"
		PickupSet.__instance = self
		wnd = GUI.load( "guis/general/autofightwindow/pickupset.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.__initialize( wnd )
		self.isIgnorePickUp = True
		self.addToMgr( "pickupSet" )
		self.__triggers={}
		self.__registerTriggers()

	def __del__(self):
		"""
		just for testing memory leak
		"""
		if Debug.output_del_PlusSkillSet:
			INFO_MSG( str( self ) )

	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_PICKUP_REMOVE_TYPE"] = self.__onRemovePickType
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __unregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )

	def __initialize( self, wnd ):
		labelGather.setPyLabel( self.pyLbTitle_, "AutoFightWindow:PickUpSet", "lbTitle" )
		self.__pyCbPickType = ODComboBox( wnd.cbPicks, ODTextBox )
		self.__pyCbPickType.onViewItemInitialized.bind( self.__onInitCBXItem )
		self.__pyCbPickType.onDrawItem.bind( self.__onDrawCBXItem )
		self.__pyCbPickType.onItemSelectChanged.bind( self.__onTypeSelected )
		self.__pyCbPickType.ownerDraw = True

		self.__pyTypeList = ListPanel( wnd.listPanel, wnd.listBar )
		self.__pyTypeList.onItemSelectChanged.bind( self.__onItemSelected )

		self.__pyPlusBtn = Button( wnd.btnPlus )
		self.__pyPlusBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyPlusBtn.onLClick.bind( self.__onAddPickType )

		self.__pyMinusBtn = Button( wnd.btnMinus )
		self.__pyMinusBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyMinusBtn.onLClick.bind( self.__onRmPickType )

		self.__pyCheckGroup = CheckerGroup()
		self.__pyCheckGroup.onCheckChanged.bind( self.__onTypeCheck )

		self.__pyRbIgnore = RadioButtonEx( wnd.cbIgnore)
		self.__pyRbIgnore.checked = False
		self.__pyRbIgnore.clickCheck = True
		self.__pyRbIgnore.text = labelGather.getText( "AutoFightWindow:PickUpSet", "cbIgnore" )
		self.__pyCheckGroup.addChecker( self.__pyRbIgnore )

		self.__pyRbPick = RadioButtonEx( wnd.cbPickup)
		self.__pyRbPick.checked = False
		self.__pyRbPick.clickCheck = True
		self.__pyRbPick.text = labelGather.getText( "AutoFightWindow:PickUpSet", "cbPickup" )
		self.__pyCheckGroup.addChecker( self.__pyRbPick )

		self.__pyOkBtn = Button( wnd.btnOK )
		self.__pyOkBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyOkBtn.onLClick.bind( self.__onSave )
		labelGather.setPyBgLabel( self.__pyOkBtn, "AutoFightWindow:PlusSkillSet", "btnOK" )

		self.__pyCancelBtn = Button( wnd.btnCancel )
		self.__pyCancelBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyCancelBtn.onLClick.bind( self.__onCancel )
		labelGather.setPyBgLabel( self.__pyCancelBtn, "AutoFightWindow:PlusSkillSet", "btnCancel" )

	def __onInitCBXItem( self, pyViewItem ) :
		"""初始化Combox的列表项"""
		staticText = hfUILoader.load( "guis/controls/odlistpanel/itemtext.gui" )
		pyText = StaticText( staticText )
		pyText.text = pyViewItem.listItem[0]
		pyViewItem.addPyChild( pyText )
		pyText.r_left = uiFixer.toFixedX( pyText.r_left )
		pyText.middle = pyViewItem.height / 2
		pyViewItem.pyText = pyText

	def __onDrawCBXItem( self, pyViewItem ) :
		"""更新列表项"""
		pyPanel = pyViewItem.pyPanel
		pyViewItem.pyText.text = pyViewItem.listItem[0]
		pyViewItem.pyText.font = pyPanel.font
		if pyViewItem.selected :
			pyViewItem.pyText.color = pyPanel.itemSelectedForeColor			# 选中状态下的前景色
			pyViewItem.color = pyPanel.itemSelectedBackColor				# 选中状态下的背景色
		elif pyViewItem.highlight :
			pyViewItem.pyText.color = pyPanel.itemHighlightForeColor		# 高亮状态下的前景色
			pyViewItem.color = pyPanel.itemHighlightBackColor				# 高亮状态下的背景色
		else :
			pyViewItem.pyText.color = pyPanel.itemCommonForeColor
			pyViewItem.color = pyPanel.itemCommonBackColor

	def __onRemovePickType( self, type ):
		pass

	def __onTypeSelected( self, index ):
		if index is None or index < 0 : return
		type = self.__pyCbPickType.items[ index ][1]
		self.__pyPlusBtn.enable = not self.__isInList( type )

	def __onItemSelected( self, pyItem ):
		if pyItem is None:return

	def __onTypeCheck( self, pyRadio ):
		"""
		排除选项
		"""
		if pyRadio is None:return
		self.isIgnorePickUp = pyRadio == self.__pyRbIgnore
		self.__onLoad( self.isIgnorePickUp )

	def __onAddPickType( self ):
		"""
		添加拾取物品类型
		"""
		pickType = self.__pyCbPickType.selItem
		if pickType is None:return
		type = pickType[1]
		if self.__isInList( type ):return
		pyTypeItem = SingleColListItem()
		pyTypeItem.height = 23.0
		pyTypeItem.type = type
		pyTypeItem.text = pickType[0]
		self.__pyTypeList.addItem( pyTypeItem )

	def __onRmPickType( self ):
		"""
		移除拾取物品类型
		"""
		pyTypeItem = self.__pyTypeList.pySelItem
		if pyTypeItem is None:return
		type = pyTypeItem.type
		self.__pyTypeList.removeItem( pyTypeItem )

	def __onSave( self ):
		"""
		保存自动拾取配置
		"""
		player = BigWorld.player()
		player.setIgnorePickUp( self.isIgnorePickUp )
		itemsTypes = [pyPickType.type for pyPickType in self.__pyTypeList.pyItems]
		player.setPickUpTypes( self.isIgnorePickUp, itemsTypes )
		player.statusMessage( csstatus.AUTO_FIGHT_PICKUP_HAS_SAVED )
		self.hide()

	def __onLoad( self, isIgnorePickUp ):
		"""
		加载自动拾取配置
		"""
		self.__pyTypeList.clearItems()
		pickupTypes = BigWorld.player().getPickUpTypes( isIgnorePickUp )
		for pickupType in pickupTypes:
			if self.__isInList( pickupType ):continue
			pyPickType = SingleColListItem()
			pyPickType.height = 23.0
			pyPickType.type = pickupType
			pyPickType.text = pickupTypeDatas.get( pickupType, "" )
			self.__pyTypeList.addItem( pyPickType )

	def __onCancel( self ):
		"""
		取消配置
		"""
		self.hide()

	def __isInList( self, pickType ):
		"""
		特定类型是否在
		"""
		types = [pyPickType.type for pyPickType in self.__pyTypeList.pyItems]
		return pickType in types

	@staticmethod
	def instance():
		"""
		get the exclusive instance of AutoFightWindow
		"""
		if PickupSet.__instance is None:
			PickupSet.__instance = PickupSet()
		return PickupSet.__instance

	@staticmethod
	def getInstance():
		"""
		"""
		return PickupSet.__instance

	def getPickUpTypes( self ):
		"""
		获取自动拾取物品类型
		"""
		return [pyPickType.type for pyPickType in self.__pyTypeList.pyItems]

	def show( self, pyOwner = None ):
		self.__pyCbPickType.clearItems()
		itemsTypes = pickupTypeDatas.keys()
		itemsTypes.sort( reverse = True )
		for itemsType in itemsTypes:
			typeName = pickupTypeDatas.get( itemsType, "" )
			self.__pyCbPickType.addItem( ( typeName, itemsType ) )
		player = BigWorld.player()
		self.isIgnorePickUp = player.autoFightConfig["isIgnorePickUp"]
		pickupTypes = player.getPickUpTypes( self.isIgnorePickUp )
		if self.isIgnorePickUp:
			self.__pyCheckGroup.pyCurrChecker = self.__pyRbIgnore
		else:
			self.__pyCheckGroup.pyCurrChecker = self.__pyRbPick
		for pickupType in pickupTypes:
			if self.__isInList( pickupType ):continue
			pyPickType = SingleColListItem()
			pyPickType.height = 23.0
			pyPickType.type = pickupType
			pyPickType.text = pickupTypeDatas.get( pickupType, "" )
			self.__pyTypeList.addItem( pyPickType )
		Window.show( self, pyOwner )

	def hide( self ):
		self.__unregisterTriggers()
		PickupSet.__instance=None
		Window.hide( self )


class ODTextBox( InputBox ) :

	def onItemSelectChanged_( self, index ) :
		"""
		选项改变时被调用
		"""
		pyCombo = self.pyComboBox
		self.text = "" if index < 0 else pyCombo.items[index][0]