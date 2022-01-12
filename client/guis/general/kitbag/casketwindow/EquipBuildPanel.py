# -*- coding: gb18030 -*-
# $Id: EquipBuildPanel.py

from guis import *
from LabelGather import labelGather
from guis.controls.ButtonEx import HButtonEx
from guis.common.PyGUI import PyGUI
from guis.controls.TabCtrl import TabPanel
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import g_newLine
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis.MLUIDefine import ItemQAColorMode
from ItemsFactory import ObjectItem
from CastKitItem import ExtractEquipItem, ExtractItem, CastKitStuff
from guis.controls.ListPanel import ListPanel
from guis.controls.ListItem import ListItem
from OblivYesNoBox import OblivYesNoBox
from ItemSystemExp import SpecialComposeExp
from config.client.labels.items import lbs_CEquipMakeScroll
from ItemSystemExp import EquipAttrExp
g_itemPropAttrExp = EquipAttrExp.instance()
from items.ItemDataList import ItemDataList
g_items = ItemDataList.instance()
from guis.MLUIDefine import QAColor
import utils
import Define
import ItemTypeEnum
import items

class EquipBuildPanel( TabPanel ):
	"""
	装备打造面板
	"""
	_cc_draws_count = 10				#图纸数
	
	_cc_main_index = 4
	_cc_wire_index = 7
	
	_inite_scoll = { "itemID":0,"raFixedAttr":[], "maxCount":0,"quality":0}		#空配方，用来初始化配方格
	
	_item_dsp = { "product":labelGather.getText( "CasketWindow:EquipBuildPanel", "proDsp" ),	#物品格说明
					"draw":labelGather.getText( "CasketWindow:EquipBuildPanel", "drawDsp" ),
					}
	
	def __init__( self, panel ):
		TabPanel.__init__( self, panel )
		self.__triggers = {}
		self.__registerTriggers()
		
		self.__pyDrawsPanel = ListPanel( panel.drawPanel.spanel, panel.drawPanel.sbar )
		self.__pyDrawsPanel.viewCols = 2
		self.__pyDrawsPanel.autoSelect = False
		self.__pyDrawsPanel.colSpace = -3.0
		self.__pyDrawsPanel.rowSpace = 3.0
		self.__pyDrawsPanel.onItemSelectChanged.bind( self.__onDrawSelected )
		self.__pyDrawsPanel.left = 0.0
		
		
		self.__pyStuffItems = {}
		for name, item in panel.stuffPanel.children:						#材料
			if not name.startswith( "item_" ):continue
			tags = name.split( "_" )
			stuffTag = tags[1]
			pyStuffItem = StuffItem( item, self, "stuff" )
			if len( tags ) >= 3:											#主材和辅材
				index = int( tags[2] )
				if stuffTag in self.__pyStuffItems:
					self.__pyStuffItems[stuffTag][index] = pyStuffItem
				else:
					self.__pyStuffItems[stuffTag] = {index:pyStuffItem}
			else:
				self.__pyStuffItems[stuffTag] = pyStuffItem				#白装和线材

		self.__pyProdutItem = ExtractEquipItem( panel.stuffPanel.eqProduct, self, "product" )		#成品
		
		self.__pyBtnBuy = HButtonEx( panel.stuffPanel.btnBuy )					#购买商城道具
		self.__pyBtnBuy.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyBtnBuy, "CasketWindow:EquipBuildPanel", "buy" )
		self.__pyBtnBuy.onLClick.bind( self.__onBuy )
		
		self.__pyBtnBuild = HButtonEx( panel.stuffPanel.btnBuild )					#打造装备
		self.__pyBtnBuild.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnBuild.enable = False
		labelGather.setPyBgLabel( self.__pyBtnBuild, "CasketWindow:EquipBuildPanel", "build" )
		self.__pyBtnBuild.onLClick.bind( self.__onBuild )
		
		self.__pyBtnObliv = HButtonEx( panel.drawPanel.btnObl )					#遗忘图纸
		self.__pyBtnObliv.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnObliv.enable = False
		labelGather.setPyBgLabel( self.__pyBtnObliv, "CasketWindow:EquipBuildPanel", "obliv" )
		self.__pyBtnObliv.onLClick.bind( self.__onObliv )
		
		self.__pyRtCost = CSRichText( panel.stuffPanel.rtCost )
		self.__pyRtCost.align = "L"
		self.__pyRtCost.text = ""
		
		labelGather.setLabel( panel.drawPanel.title.stTitle, "CasketWindow:EquipBuildPanel", "draw" )
		labelGather.setLabel( panel.stuffPanel.title.stTitle, "CasketWindow:EquipBuildPanel", "stuff" )
		labelGather.setLabel( panel.stuffPanel.eqTitle.stTitle, "CasketWindow:EquipBuildPanel", "whiteEquip" )
		labelGather.setLabel( panel.stuffPanel.wireTitle.stTitle, "CasketWindow:EquipBuildPanel", "wireStuff" )
		labelGather.setLabel( panel.stuffPanel.mainTitle.stTitle, "CasketWindow:EquipBuildPanel", "mainStuff" )
		labelGather.setLabel( panel.stuffPanel.aidTitle.stTitle, "CasketWindow:EquipBuildPanel", "aidStuff" )
		self.__initeDrawsPanel()
	
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ROLE_GET_SCROLL_SKILL"] = self.__onGetScrollSkill
		self.__triggers["EVT_ON_ROLE_DEL_SCROLL_SKILL"] = self.__onDelScrollSkill
		self.__triggers["EVT_ON_KITBAG_ADD_ITEM"] = self.__onUpdateStuffItem
		self.__triggers["EVT_ON_KITBAG_UPDATE_ITEM"] = self.__onUpdateStuffItem
		self.__triggers["EVT_ON_KITBAG_REMOVE_ITEM"] = self.__onUpdateStuffItem
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )
	# ---------------------------------------------------------------------------
	def __onGetScrollSkill( self, scroll, index ):
		"""
		增加一个配方技能
		"""
		for pyDrawItem in self.__pyDrawsPanel.pyItems:
			drawInfo = pyDrawItem.drawInfo
			if drawInfo is None:
				pyDrawItem.updateDraw( scroll, index )
				break
				
	def __onDelScrollSkill( self, idx ):
		"""
		删除一个配方技能,重新刷新
		"""
		if idx > self.__pyDrawsPanel.itemCount:
			return
		player = BigWorld.player()
		for pyDraw in self.__pyDrawsPanel.pyItems:
			pyDraw.updateDraw( None, -1 )
		for index, scoll in enumerate( player.scrollSkill ):
			self.__onGetScrollSkill( scoll, index )
		pySelItem = self.__pyDrawsPanel.pySelItem
		drawInfo = pySelItem.drawInfo
		self.__setStuffInfos( drawInfo )
		if len( player.scrollSkill ) < 0:
			self.__pyBtnObliv.enable = False
	
	def __onUpdateScrollSkill( self, oldDrawID, scroll ):
		"""
		更新一个配方技能
		"""
		for pyDrawItem in self.__pyDrawsPanel.pyItems:
			drawInfo = pyDrawItem.drawInfo
			if drawInfo is None:continue
			if drawInfo["itemID"] == oldDrawID:
				pyDrawItem.updateDraw( scroll )
				
	def __onDrawSelected( self, pyDraw ):
		"""
		选择一个配方技能
		"""
		drawInfo = pyDraw.drawInfo
		self.__setStuffInfos( drawInfo )
		self.__pyBtnObliv.enable = drawInfo is not None

	def __setStuffInfos( self, drawInfo ):
		self.__pyBtnBuy.enable = drawInfo is not None
		if drawInfo is None:
			self.__resetStuffItems()
			self.__pyRtCost.text = ""
			self.__pyProdutItem.update( None )
			self.__pyBtnBuild.enable = False
		else:
			player = BigWorld.player()
			specom = rds.specialCompose
			scrollID = drawInfo["itemID"]
			scAttrL = drawInfo[ "raFixedAttr" ] #卷轴的随机属性
			quality = drawInfo["quality"]
			scAttr = {}
			for attrInfo  in scAttrL:
				scAttr[attrInfo[0]] = attrInfo[1]
			dstItemID = specom.getDstItemID( scrollID )  #目标物品ID
			dstAmount = specom.getDstItemCount( scrollID )  #目标物品的数量
			mItems    = specom.getMaterials( scrollID ) #合成材料及其数量
			canBuild = True
			for index, iteminfo in enumerate( mItems ):		#srcItemID1 - srcItemID2 为一般卷轴主材、srcItemID3为稀有卷轴主材 srcItemID5为一般卷轴辅材
				itemID = iteminfo[0]						#srcItemID6- srcItemID7 为稀有卷轴辅材 、srcItemID8 为线材 、srcItemID9为白装 
				count  = iteminfo[1]						#需要材料数
				if itemID == 0:continue
				item = player.createDynamicItem( itemID )
				itemInfo = ObjectItem( item )
				if itemInfo is None:continue
				sitems = player.findItemsByIDFromNK( itemID )			#在玩家背包查找材料及数量
				scount = 0
				for sitem in sitems:
					if sitem.isEquip() and sitem.getQuality() != ItemTypeEnum.CQT_WHITE:				#不是白装，不计数
						continue
					scount += sitem.getAmount()
				if scount < count:
					canBuild = False
				pyStuffItem = None
				if item.isEquip():										# 白装
					pyStuffItem = self.__pyStuffItems["equip"]
				if index < self._cc_main_index:							#主材
					pyStuffItem = self.__pyStuffItems["main"][index]
				elif index < self._cc_wire_index:						#辅材
					pyStuffItem = self.__pyStuffItems["aid"][index - self._cc_main_index]
				elif  index == self._cc_wire_index:						#线材
					pyStuffItem = self.__pyStuffItems["wire"]
				if pyStuffItem is None:continue
				pyStuffItem.updateStuff( itemInfo, scount, count )
			self.__pyBtnBuild.enable = canBuild
			equipStatus = Define.ITEM_STATUS_NATURAL
			dstItem = player.createDynamicItem( dstItemID )
			dstEpInfo = ObjectItem( dstItem )
			self.__pyProdutItem.update( dstEpInfo )
			itemid = SpecialComposeExp._instance.getDstItemID( scrollID )
			item = g_items.createDynamicItem( itemid )
			des = item.description( player )
			scrollLevel = g_items.getLevel( scrollID )
			randomEffect = g_itemPropAttrExp.getScrollComposeRandomEffect( scrollID, scrollLevel, scAttr, quality )
			fixedAttr = labelGather.getText( "CasketWindow:EquipBuildPanel", "fixedAttr" )
			des.append( [ PL_Font.getSource( fixedAttr, fc = "c1" ) ] )
			colorFunc = lambda v, arg1, arg2 : v and arg1 or arg2
			g_equipEffects = items.EquipEffectLoader.EquipEffectLoader.instance()
			for attrType, value in scAttr.items():
				effectClass = g_equipEffects.getEffect( attrType )
				if effectClass is None: continue
				maxValue = g_equipEffects.getEffectMax( item, attrType )
				desList = effectClass.descriptionList( value )
				color = colorFunc( value >= maxValue, "c6", ( 0, 255, 0 ) )			# 当属性值达到最大时显示为金黄色
				des.append( [PL_Font.getSource( desList[0] + desList[1] , fc = color )] )
			randomAttr = labelGather.getText( "CasketWindow:EquipBuildPanel", "randomAttr" )
			des.append( [ PL_Font.getSource( randomAttr, fc = "c1" ) ] )
			for effect in randomEffect:
				des.append( [ PL_Font.getSource( "???:???", fc = "c4" ) ] )
			self.__pyProdutItem.description = des
			util.setGuiState( self.__pyProdutItem.pyItemBg_.getGui(), ( 4, 2 ), ItemQAColorMode[quality] )
			if not canBuild:
				equipStatus = Define.ITEM_STATUS_USELESSNESS
			self.__pyProdutItem.updateUseStatus( equipStatus )
			cost = player.sc_getComposeCost( scrollID )
			costText = labelGather.getText( "CasketWindow:EquipBuildPanel", "rtMoney" )%utils.currencyToViewText( cost )
			self.__pyRtCost.text =  PL_Font.getSource( costText, fc = ( 255, 255, 255, 255 ) )
	
	def __resetStuffItems( self ):
		"""
		清空材料格
		"""
		for stfTag, stuffItems in self.__pyStuffItems.items():
			if stfTag in ["equip", "wire"]:
				stuffItems.updateStuff( None )
			else:
				for stuffItem in stuffItems.values():
					stuffItem.updateStuff( None )

	def __initeDrawsPanel( self ):
		"""
		初始化图纸格子
		"""
		for index in range( self._cc_draws_count ):
			item = GUI.load( "guis/general/kitbag/casketwindow/drawitem.gui" )
			uiFixer.firstLoadFix( item )
			pyDraw = DrawItem( item, index, self, "draw" )
			self.__pyDrawsPanel.addItem( pyDraw )
	
	def __onBuy( self, pyBtn ):
		"""
		购买
		"""
		if pyBtn is None:return
		rds.ruisMgr.specialShop.show( self.pyTopParent )
	
	def __onBuild( self, pyBtn ):
		"""
		开始打造
		"""
		if pyBtn is None:return
		pySelItem = self.__pyDrawsPanel.pySelItem
		selIndex = self.__pyDrawsPanel.selIndex
		player = BigWorld.player()
		drawInfo = pySelItem.drawInfo
		if drawInfo is None:return
		if selIndex >= 0:
			player.cell.doSpecialCompose( selIndex )
	
	def __onObliv( self, pyBtn ):
		"""
		遗忘技能
		"""
		pySelItem = self.__pyDrawsPanel.pySelItem
		if pySelItem is None:return
		selIndex = pySelItem.index
		player = BigWorld.player()
		drawInfo = pySelItem.drawInfo
		if drawInfo is None:return
		if selIndex < 0:return
		def query( rs_id ):
			if rs_id == RS_YES:
				player.delScrollSkill( selIndex )
		OblivYesNoBox().show( query, drawInfo, self )

	def __onUpdateStuffItem( self, itemInfo ) :
		"""
		背包更新物品
		"""
		id = itemInfo.id
		pyItem = self.__getPyItemByID( id )
		if pyItem is not None:
			sitems = BigWorld.player().findItemsByIDFromNK( id )
			scount = 0
			for sitem in sitems:
				if sitem.isEquip() and sitem.getQuality() != ItemTypeEnum.CQT_WHITE:				#不是白装，不计数
					continue
				scount += sitem.getAmount()
			pyItem.updateCount( scount )
		self.__refreshStatus()

	def __getPyItemByID( self, id ):
		"""
		根据UI查找界面上对应格子
		"""
		pyItemByID = None
		for stfTag, stuffItems in self.__pyStuffItems.items():
			if stfTag in ["equip", "wire"]:
				if stuffItems.itemInfo is None:continue
				if stuffItems.itemInfo.id == id: 
					pyItemByID = stuffItems
					break
			else:
				for stuffItem in stuffItems.values():
					if stuffItem.itemInfo is None:continue
					if stuffItem.itemInfo.id == id : 
						pyItemByID = stuffItem
						break
		return pyItemByID
	
	def __refreshStatus( self ):
		"""
		刷新目标装备和打造按钮的状态
		"""
		pySelDraw = self.__pyDrawsPanel.pySelItem
		if pySelDraw is None:return
		drawInfo = pySelDraw.drawInfo
		if drawInfo is None:return
		specom = rds.specialCompose
		scrollID = drawInfo["itemID"]
		mItems    = specom.getMaterials( scrollID )
		canBuild = True
		for mItem in mItems :		#srcItemID1 - srcItemID2 为一般卷轴主材、srcItemID3为稀有卷轴主材 srcItemID5为一般卷轴辅材
			itemID = mItem[0]						#srcItemID6- srcItemID7 为稀有卷轴辅材 、srcItemID8 为线材 、srcItemID9为白装 
			count  = mItem[1]						#需要材料数
			sitems = BigWorld.player().findItemsByIDFromNK( itemID )
			scount = 0
			for sitem in sitems:
				if sitem.isEquip() and sitem.getQuality() != ItemTypeEnum.CQT_WHITE:				#不是白装，不计数
					continue
				scount += sitem.getAmount()
			if scount < count:
				canBuild = False
		self.__pyBtnBuild.enable = canBuild
		equipStatus = Define.ITEM_STATUS_NATURAL
		if not canBuild:
			equipStatus = Define.ITEM_STATUS_USELESSNESS
		self.__pyProdutItem.updateUseStatus( equipStatus )

	def __lockItems( self, locked ) :
		"""
		打开/关闭界面时改变背包中对应物品的颜色
		"""
		pyItems = []
		for stfTag, stuffItems in self.__pyStuffItems.items():
			if stfTag in ["equip", "wire"]:
				pyItems.append( stuffItems )
			else:
				for stuffItem in stuffItems.values():
					pyItems.append( stuffItem )
		for pyItem in pyItems :
			if pyItem.itemInfo is None: continue
			self.__lockItem( pyItem.itemInfo, locked )

	def __lockItem( self, itemInfo, locked ) :
		"""
		通知背包锁定/解锁某个物品
		"""
		kitbagID = itemInfo.kitbagID
		if kitbagID > -1 :
			orderID = itemInfo.orderID
			ECenter.fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", kitbagID, orderID, locked )

	# ----------------------------------------------------------------
	# friend methods
	# ----------------------------------------------------------------
	def onStoneDrop__( self, pyTarget, pyDropped ) :
		"""
		拖放到材料格
		"""
		pass
	
	def onEquipDrop__( self, pyTarget, pyDropped ) :
		"""
		拖放到装备格
		"""
		pass

	def onItemRemove__( self, pyItem ) :
		"""
		右击移除物品
		"""
		pass

	def onItemMouseEnter__( self, pyItem ):
		"""
		显示物品格描述信息
		"""
		tag = pyItem.tag
		dsp = self._item_dsp.get( tag, "" )
		if dsp != "":
			toolbox.infoTip.showToolTips( self, dsp )

	def onItemMouseLeave__( self ):
		"""
		隐藏物品格描述信息
		"""
		toolbox.infoTip.hide()

	# ----------------------------------------------------------
	#public
	# ---------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )

	def onShow( self ):
		self.__lockItems( True )
	
	def onHide( self ):
		self.__lockItems( False )
	
	def onEnterWorld( self ):
		player = BigWorld.player()
		for pyDraw in self.__pyDrawsPanel.pyItems:
			pyDraw.updateDraw( None, -1 )
		for index, scoll in enumerate( player.scrollSkill ):
			self.__onGetScrollSkill( scoll, index )
	
	def onLeaveWorld( self ):
		for pyDraw in self.__pyDrawsPanel.pyItems:
			pyDraw.updateDraw( None, -1 )

# -------------------------------------------------------------------------
class StuffItem( CastKitStuff ):
	"""
	材料
	"""
	def __init__( self, item, pyBinder = None, tag = "" ):
		CastKitStuff.__init__( self, item, pyBinder, tag )
		self.count = 0
	
	def updateStuff( self, itemInfo, scount = 0, count = 0 ):
		self.count = count
		CastKitStuff.update( self, itemInfo )
		CastKitStuff.setItemStatus( self, scount, count )
	
	def updateCount( self, scount ):
		"""
		更新背包已存在物品数量
		"""
		CastKitStuff.setItemStatus( self, scount, self.count )

# -------------------------------------------------------------------------
class DrawItem( ListItem, ExtractItem ):
	def __init__( self, item, index, pyBinder = None, tag = "" ):
		ListItem.__init__( self, item, pyBinder )
		ExtractItem.__init__( self, item, pyBinder, tag )
		self.__pyCover = PyGUI( item.cover )
		self.drawInfo = None
		self.index = index
		self.commonBackColor = 255, 255, 255, 255
		self.highlightBackColor = 255, 255, 255, 255
		self.selectedBackColor = 255, 255, 255, 255

	def __setItemQuality( self, itemBg, quality ):
		util.setGuiState( itemBg, ( 4, 2 ), ItemQAColorMode[quality] )
		
	def updateDraw( self, draw, index ):
		"""
		更新卷轴
		"""
		self.drawInfo = draw
		player = BigWorld.player()
		self.index = index
		if draw is not None:
			drawID = draw["itemID"]
			quality = draw["quality"]
			scAttrL = draw[ "raFixedAttr" ] #卷轴的随机属性
			scAttr = {}
			for attrInfo  in scAttrL:
				scAttr[attrInfo[0]] = attrInfo[1]
			drawItem = g_items.createDynamicItem( drawID )
			itemInfo = ObjectItem( drawItem )
			self.__setItemQuality( self.pyItemBg_.getGui(), quality )
			ExtractItem.update( self, itemInfo )
			itemid = SpecialComposeExp._instance.getDstItemID( drawID )
			item = g_items.createDynamicItem( itemid )
			des = item.description( player )
			des.insert( 0,[ PL_Font.getSource( drawItem.name(), fc = QAColor[quality] ) ] )
			des.insert( 1,[ PL_Font.getSource( lbs_CEquipMakeScroll[4], fc = "c8" ) ] )
			fixedAttr = labelGather.getText( "CasketWindow:EquipBuildPanel", "fixedAttr" )
			des.append( [ PL_Font.getSource( fixedAttr, fc = "c1" ) ] )
			colorFunc = lambda v, arg1, arg2 : v and arg1 or arg2
			g_equipEffects = items.EquipEffectLoader.EquipEffectLoader.instance()
			for attrType, value in scAttr.items():
				effectClass = g_equipEffects.getEffect( attrType )
				if effectClass is None: continue
				maxValue = g_equipEffects.getEffectMax( item, attrType )
				desList = effectClass.descriptionList( value )
				color = colorFunc( value >= maxValue, "c6", ( 0, 255, 0 ) )			# 当属性值达到最大时显示为金黄色
				des.append( [PL_Font.getSource( desList[0] + desList[1] , fc = color )] )
			randomAttr = labelGather.getText( "CasketWindow:EquipBuildPanel", "randomAttr" )
			scrollLevel = g_items.getLevel( drawID )
			randomEffect = g_itemPropAttrExp.getScrollComposeRandomEffect( drawID, scrollLevel, scAttr, quality )
			randomAttr = labelGather.getText( "CasketWindow:EquipBuildPanel", "randomAttr" )
			des.append( [ PL_Font.getSource( randomAttr, fc = "c1" ) ] )
			for effect in randomEffect:
				des.append( [ PL_Font.getSource( "???:???", fc = "c4" ) ] )
			self.description = des
		else:
			ExtractItem.update( self, draw )
			self.__setItemQuality( self.pyItemBg_.getGui(), 1 )
		

	def _getSelected( self ) :
		ListItem._getSelected( self )

	def _setSelected( self, isSelected ) :
		ListItem._setSelected( self, isSelected )
		self.__pyCover.visible = isSelected

	selected = property( _getSelected, _setSelected )