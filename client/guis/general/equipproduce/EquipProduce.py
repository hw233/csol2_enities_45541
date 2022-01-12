# -*- coding: gb18030 -*-
#
# $Id: EquipProduce.py,v 1.21 2008-08-26 03:40:38 fangpengjun Exp $

"""
implement EquipProduceclass
"""
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.common.PyGUI import PyGUI
from guis.controls.StaticText import StaticText
from guis.controls.ODComboBox import ODComboBox
from guis.controls.TreeView import VTreeView as TreeView
from guis.controls.TreeView import TreeNode
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.CSRichText import CSRichText
from guis.controls.StaticLabel import StaticLabel
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from StuffsPanel import StuffsPanel
from StuffsInfo import StuffsInfo
from ItemsFactory import ObjectItem
from HelpItem import HelpItem
from RatioItem import RatioItem
from gbref import rds
import items as Items
import ItemTypeEnum
import csdefine
import csconst
import GUIFacade
import csstatus
from config.client import equipstr
from config.client.help.MaterialName import LackItemDatas
import reimpl_equipProduce

class EquipProduce( Window ):

	_ratio_color = {
				ItemTypeEnum.CQT_PINK:( labelGather.getText( "EquipProduce:main", "ratio_pink" ), ( 254, 0, 156, 255 ) ),
				ItemTypeEnum.CQT_GOLD:( labelGather.getText( "EquipProduce:main", "ratio_gold" ), ( 255, 215, 0, 255 ) ),
				ItemTypeEnum.CQT_BLUE:( labelGather.getText( "EquipProduce:main", "ratio_blue" ),( 0, 229, 233, 255 ) ),
				ItemTypeEnum.CQT_WHITE:( labelGather.getText( "EquipProduce:main", "ratio_white" ), ( 255, 255, 255, 255 ) )
			}

	def __init__( self ):
		wnd = GUI.load( "guis/general/equipproduce/window.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True
		self.__triggers = {}
		self.__registerTriggers()
		self.stuffKOs = {}		# 字典，储存kitbag id（key）和order id（value）
		self.__trapID = 0
		self.__entityID = 0
		self.__lastEquip = () 	# 保存上次最后选择的节点
		self.__findItemOrders = []		# 自动放入搜索到的材料order集合
		self.__pyStRatios = {}
		self.equips = equipstr.Datas
		self.__initialize( wnd )

		rds.mutexShowMgr.addMutexRoot( self, MutexGroup.TRADE1 )				# 添加到MutexGroup.TRADE1互斥组

	def __initialize( self, wnd ):
		labelGather.setPyLabel( self.pyLbTitle_, "EquipProduce:main", "lbTitle" )
		
		self.__pyCBPro = ODComboBox( wnd.cbPro )
		self.__pyCBPro.autoSelect = False
		self.__pyCBPro.ownerDraw = True
		self.__pyCBPro.pyBox_.foreColor = ( 236, 215, 157, 255 )
		self.__pyCBPro.onViewItemInitialized.bind( self.onInitialized_ )
		self.__pyCBPro.onDrawItem.bind( self.onDrawItem_ )
		self.__pyCBPro.onItemSelectChanged.bind( self.__onProfeSelected )
		self.__initItems()

		self.__pyCBEquip = ODComboBox( wnd.cbEquip )
		self.__pyCBEquip.autoSelect = False
		self.__pyCBEquip.ownerDraw = True
		self.__pyCBEquip.pyBox_.foreColor = ( 236, 215, 157, 255 )
		self.__pyCBEquip.onViewItemInitialized.bind( self.onInitialized_ )
		self.__pyCBEquip.onDrawItem.bind( self.onDrawItem_ )
		self.__pyCBEquip.onItemSelectChanged.bind( self.__onTypeSelected )

		self.__pyTVEquip = TreeView( wnd.tvEquip.clipPanel, wnd.tvEquip.sbar )
		self.__pyTVEquip.onTreeNodeSelected.bind( self.__onEquipSelected )
		self.__pyTVEquip.nodeOffset = 2.0

		self.__pyStQuality = StaticText( wnd.stQuality )
		self.__pyStQuality.text = ""

		self.__pyMaterialsPanel = StuffsInfo( wnd.materialPanel )

		self.__pyMaterialsBag = StuffsPanel( wnd.materialsBag )

		self.__pyEquipItem = BOItem( wnd.equipItem.item )

		self.__pyRtMoney = CSRichText( wnd.rtMoney )
		self.__pyRtMoney.align = "L"
		self.__pyRtMoney.maxWidth = 200.0

		self.__pyBtnOK = HButtonEx( wnd.btnOK )
		self.__pyBtnOK.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOK.onLClick.bind( self.__onProduce )
		self.__pyBtnOK.enable = False
		labelGather.setPyBgLabel( self.__pyBtnOK, "EquipProduce:main", "btnOK" )

		self.__pyBtnAuto = HButtonEx( wnd.btnAuto )
		self.__pyBtnAuto.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnAuto.onLClick.bind( self.__onAutoButton )
		self.__pyBtnAuto.enable = False
		labelGather.setPyBgLabel( self.__pyBtnAuto, "EquipProduce:main", "btnAuto" )

		labelGather.setLabel( wnd.succText, "EquipProduce:main", "succText" )
		labelGather.setLabel( wnd.warnText, "EquipProduce:main", "warnText" )
		labelGather.setLabel( wnd.materText, "EquipProduce:main", "materText" )

		self.__initRatioLabels( self.__pyStRatios, wnd )
		self.__initHelpLinks( wnd )

	@reimpl_equipProduce.deco_equipProInit
	def __initRatioLabels( self, pyStRatios, wnd ):
		for name, item in wnd.children:
			if "quality_" not in name:continue
			quality = int( name.split("_")[1] )
			ratioColor = self._ratio_color.get( quality, None )
			if ratioColor is None:continue
			pyRatioText = RatioItem( item )
			pyRatioText.title = ratioColor[0]
			pyRatioText.titleColor = ratioColor[1]
			pyRatioText.text = ""
			pyStRatios[quality] = pyRatioText

	def __initHelpLinks( self, wnd ):
		self.__helpRTs = {}
		for name, item in wnd.children:
			if name.startswith( "proRT_" ):
				index = int( name.split( "_" )[1] )
				pyHelpItem = HelpItem( item )
				pyHelpItem.text = labelGather.getText( "EquipProduce:main", name )
				pyHelpItem.mark = ( 1, 25 )
				self.__helpRTs[index] = pyHelpItem

	def __initItems( self ):
		for equipType, typeSet in self.equips.iteritems():
			equipStr = typeSet[0]
			cbItem = CBItem( equipType, equipStr )
			self.__pyCBPro.addItem( cbItem )
	
	def onInitialized_( self, pyViewItem ):
		pyLabel = StaticLabel()
		pyLabel.crossFocus = True
		pyLabel.foreColor = 236, 218, 157
		pyLabel.h_anchor = "CENTER"
		pyViewItem.addPyChild( pyLabel )
		pyViewItem.pyLabel = pyLabel

	def onDrawItem_( self, pyViewItem ):
		pyPanel = pyViewItem.pyPanel
		if pyViewItem.selected :
			pyViewItem.pyLabel.foreColor = pyPanel.itemSelectedForeColor			# 选中状态下的前景色
			pyViewItem.color = pyPanel.itemSelectedBackColor				# 选中状态下的背景色
		elif pyViewItem.highlight :
			pyViewItem.pyLabel.foreColor = pyPanel.itemHighlightForeColor		# 高亮状态下的前景色
			pyViewItem.color = pyPanel.itemHighlightBackColor				# 高亮状态下的背景色
		else :
			pyViewItem.pyLabel.foreColor = pyPanel.itemCommonForeColor
			pyViewItem.color = pyPanel.itemCommonBackColor
		pyLabel = pyViewItem.pyLabel
		pyLabel.width = pyViewItem.width
		pyLabel.foreColor = 236, 218, 157
		pyLabel.left = 1.0
		pyLabel.top = 1.0
		cbItem = pyViewItem.listItem
		pyLabel.text = cbItem.name

	# ----------------------------------------------------------
	# pravite
	# ----------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_TOGGLE_EQUIP_PRODUCE_WND"] = self.__onWndShow #与NPC对话弹出制造窗口
		self.__triggers["EVT_ON_ADD_STUFF_ITEM"] = self.__onAddStuff
		self.__triggers["EVT_ON_REMOVE_STUFF_ITEM"] = self.__onRemoveStuff
		self.__triggers["EVT_ON_KITBAG_REMOVE_ITEM"] = self.__onRemoveItem
		self.__triggers["EVT_ON_SWRAP_PACK_ITEMS"] = self.__onSwapKitBags	#添加对包裹位换位的处理2008-07-24 spf
		self.__triggers["EVT_ON_KITBAG_SWAP_ITEM"] = self.__onSwapItems		#添加对包裹内物品换位的处理2008-07-24 spf
		self.__triggers["EVT_ON_KITBAG_UPDATE_STUFF_ORDERS"] = self.__onUpdateStuffOrders#更新物品的位置索引2008-07-24 spf
		self.__triggers["EVT_ON_KITBAG_UPDATE_ITEM"] = self.__onKitbagUpdateItem		#某个物品信息发生改变2008-07-25 spf
		self.__triggers["EVT_ON_REPLACE_STUFF_ITEM"] = self.__onReplaceStuff			#换掉合成面板中的材料 2008-08-11 spf
		self.__triggers["EVT_ON_GET_PRODUCE_STUFF_FROM_KITBAG"] = self.__getItemFromKitBag
		self.__triggers["EVT_ON_GET_AUTO_STUFF"] = self.__onAutoSuffs
		self.__triggers["EVT_ON_ROLE_DEAD"] = self.hide


		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )
	# -------------------------------------------------------
	def __onWndShow( self ):
		player = BigWorld.player()
		player.tradeState = csdefine.TRADE_PRODUCE
		self.show()
		self.__addTrap()

	def __addTrap( self ):#打开窗口后为玩家添加对话陷阱
		player = BigWorld.player()
		distance = csconst.COMMUNICATE_DISTANCE
		self.__entityID = GUIFacade.getGossipTargetID()
		if hasattr( GUIFacade.getGossipTarget(), "getRoleAndNpcSpeakDistance" ):
			distance = GUIFacade.getGossipTarget().getRoleAndNpcSpeakDistance()
		self.__trapID = player.addTrapExt( distance, self.__onEntitiesTrapThrough )

	def __onEntitiesTrapThrough( self, entitiesInTrap ):
		gossiptarget = GUIFacade.getGossipTarget()#获取当前对话NPC
		if gossiptarget and gossiptarget not in entitiesInTrap:#如果NPC离开玩家对话陷阱
			self.hide()

	def __delTrap( self ) :
		player = BigWorld.player()
		if self.__trapID :
			player.delTrap( self.__trapID )	#删除玩家的对话陷阱
			self.__trapID = 0

	def __onProfeSelected( self, selIndex ): #选择装备职业
		if selIndex < 0:return
		selItem = self.__pyCBPro.selItem
		equipType = selItem.tag
		self.__pyCBPro.pyBox_.text = selItem.name
		if self.equips.has_key( equipType ):
			equipSet = self.equips[equipType]
			self.__pyCBEquip.clearItems()
			self.__pyTVEquip.pyNodes.clear()
			for typeID, typeStr in equipSet[1].iteritems():
				cbItem = CBItem( typeID, typeStr )
				self.__pyCBEquip.addItem( cbItem )
		for pyLabel in self.__pyStRatios.itervalues():
			pyLabel.text = ""
		self.__pyMaterialsPanel.clear()
		self.__pyStQuality.text = ""
		lastType = ""
		if self.__lastEquip:
			if self.__lastEquip[0] != selItem.name:#选择全部
				lastType = labelGather.getText( "EquipProduce:main", "allType" )
			else:
				lastType = self.__lastEquip[1]
		for cbItem in self.__pyCBEquip.items:
			if cbItem.name == lastType:
				self.__pyCBEquip.selItem = cbItem
#				self.__onTypeSelected( pyViewItem.itemIndex )
		self.__pyBtnAuto.enable = False

	def __onTypeSelected( self, selIndex ): #选择类备类型,并添加树节点
		if selIndex < 0:return
		selItem = self.__pyCBEquip.selItem
		tag = selItem.tag
		name = selItem.name
		self.__pyCBEquip.pyBox_.text = name
		self.__pyTVEquip.pyNodes.clear()
		typeTag = self.__pyCBPro.selItem.tag # 职业节点标记
		if tag in ["8","106","303"] and typeTag != "201" \
		or tag == "9" and typeTag == "201":# 全部
			equipSet = self.equips[typeTag]
			for typeID, typeStr in equipSet[1].iteritems():
				if typeTag in ["1","3"]: # 武器
					newTag = "0" + typeID
				else:
					newTag = "0" + typeTag[0:2] + typeID +"0"+ typeTag[2]
				node = GUI.load("guis/general/equipproduce/eqtypenode.gui")
				uiFixer.firstLoadFix( node )				
				typeNode = TreeNode( node )
				typeNode.selectable = False
				typeNode.text = typeStr
				sameTypeEquips = rds.equipMake.getSameTypeEquips( newTag )
				self.__addEquipNodes( typeNode, sameTypeEquips )
		else: #单个类型
			node = GUI.load("guis/general/equipproduce/eqtypenode.gui")
			uiFixer.firstLoadFix( node )
			typeNode = TreeNode( node )
			typeNode.text = name
			typeNode.selectable = False
			typeNode.extend()
			if typeTag in ["1","3"]: # 武器、饰品
				newTag = "0" + tag
			else: # 防具
				newTag = "0" + typeTag[0:2] + tag +"0"+ typeTag[2]
			sameTypeEquips = rds.equipMake.getSameTypeEquips( newTag )
			self.__addEquipNodes( typeNode, sameTypeEquips )
		for pyLabel in self.__pyStRatios.itervalues():
			pyLabel.text = ""
		proStr = self.__pyCBPro.selItem.name
		self.__lastEquip = ( proStr, name )
		self.__pyMaterialsPanel.clear()
		self.__pyStQuality.text = ""
		self.__pyBtnAuto.enable = False

	def __addEquipNodes( self, typeNode, equips ):
		if len( equips ) <= 0:return
		equips.sort()
		for tuple in equips:
			equipNode = EquipNode()
			equipNode.showPlusMinus = False
			equipID, infoDict = tuple
			equipNode.equipID = equipID
			equipNode.text = labelGather.getText( "EquipProduce:main", "equipInfo" )%( infoDict["name"], infoDict["level"] )
			equipNode.stuffs = infoDict["stuff"]
			typeNode.pyNodes.add( equipNode )
		self.__pyTVEquip.pyNodes.add( typeNode )

	def __onEquipSelected( self, equipNode ): #选择某个装备节点
		if equipNode is None:return
		stuffs = equipNode.stuffs
		index = -1
		self.__pyStQuality.text =""
		equipID = equipNode.equipID
		self.__pyMaterialsPanel.clear()
		for stuffID, amount in stuffs.iteritems():
			stuff = Items.instance().createDynamicItem( stuffID )
			stuffInfo = ObjectItem( stuff )
			index += 1
			self.__pyMaterialsPanel.updateItem( index, stuffInfo, amount )
			count = self.__getStuffNum( stuffID )
			self.__pyMaterialsPanel.updateNum( stuffID, count ) #设置材料已有数量
			equipID = equipNode.equipID
			equip = Items.instance().createDynamicItem( equipID )
			newReqLevel = equip.getReqLevel()/10*10
			if newReqLevel <= 0: newReqLevel = 1
			equip.set( "reqLevel", newReqLevel, BigWorld.player() )
			equipInfo = ObjectItem( equip )
			self.__pyEquipItem.update( equipInfo )
		if self.__isCanMake():
			self.__setMakeRatio()
		else:
			for pyLabel in self.__pyStRatios.itervalues():
				pyLabel.text = ""
		self.__pyBtnOK.enable = self.__isCanMake()
		self.__pyBtnAuto.enable = True
		#装备制作收费了 这里是费用显示用到的 by姜毅
		lvm = equip.getLevel()
		if lvm < 50:    #1~50 1.1^道具等级*100
			money = 1.1 ** lvm * 100
		else:           #51~150 1.03^道具等级*2700
			money = 1.03 ** lvm * 2700
		#在下面添加ui处理代码

		self.__pyRtMoney.text = labelGather.getText( "EquipProduce:main", "rtMoney", utils.currencyToViewText( int( money ) ) )

	def __getStuffNum( self, stuffID ): #获取该ID材料所有满足条件材料数量,应该转化为最低要求材料数量
		stuffInfos = self.__pyMaterialsBag.getStuffInfos( ) #从下面材料栏中所有物品信息
		stuffIDList = rds.equipMake.getClassList( stuffID ) #获取可以制造该装备的材料ID列表
		count = 0 #一个类型材料数量
		for stuffInfo in stuffInfos:
			amount = 0 #一个ID材料数量
			basItem = stuffInfo.baseItem
			id = basItem.id
			if id in stuffIDList:
				amount = amount + basItem.getAmount()
			count += amount
		return count

	def __setMakeRatio( self ):#获取各品质百分比
		equipNode = self.__pyTVEquip.pySelNode
		if equipNode is None:return
		qualityRatios = {}
		ratios = {}
		sumRatio = 0.0
		equip = Items.instance().createDynamicItem( equipNode.equipID )
		makeStuffs = self.__getSameStuffs()
		if not self.__isCanMake():
			for pyLabel in self.__pyStRatios.itervalues():
				pyLabel.text = ""
			self.__pyStQuality.text = ""
			return
		for quality, colTuple in self._ratio_color.iteritems(): #设置百分比标签
			if self.__pyStRatios.has_key( quality ):
				pyRatioText = self.__pyStRatios[quality]
				rate = rds.equipMake.getOdds( equip, makeStuffs, quality ) * 100
				qualityRatios[quality] = rate
				sumRatio += rate

		# 修改装备颜色概率显示 by姜毅
		totelRate = 100.0
		q_keys = [ItemTypeEnum.CQT_PINK,ItemTypeEnum.CQT_GOLD,ItemTypeEnum.CQT_BLUE,ItemTypeEnum.CQT_WHITE]
		for r in q_keys:	# 品质从高到低处理，需要倒排
			if qualityRatios[r] > 100.0: qualityRatios[r] = 100.0
			if qualityRatios[r] >= totelRate: qualityRatios[r] = totelRate
			totelRate -= qualityRatios[r]

		self.__pyStRatios[ItemTypeEnum.CQT_PINK].text = "%0.1f%%"%qualityRatios[ItemTypeEnum.CQT_PINK]
		self.__pyStRatios[ItemTypeEnum.CQT_GOLD].text = "%0.1f%%"%qualityRatios[ItemTypeEnum.CQT_GOLD]
		self.__pyStRatios[ItemTypeEnum.CQT_BLUE].text = "%0.1f%%"%qualityRatios[ItemTypeEnum.CQT_BLUE]
		self.__pyStRatios[ItemTypeEnum.CQT_WHITE].text = "%0.1f%%"%qualityRatios[ItemTypeEnum.CQT_WHITE]

		ratios[ItemTypeEnum.CQT_PINK] = float( "%0.1f"%qualityRatios[ItemTypeEnum.CQT_PINK] )
		ratios[ItemTypeEnum.CQT_GOLD] = float( "%0.1f"%qualityRatios[ItemTypeEnum.CQT_GOLD])
		ratios[ItemTypeEnum.CQT_BLUE] = float( "%0.1f"%qualityRatios[ItemTypeEnum.CQT_BLUE] )
		ratios[ItemTypeEnum.CQT_WHITE] = float( "%0.1f"%qualityRatios[ItemTypeEnum.CQT_WHITE])

		self.__setQualityStr( equip, ratios )

	def __setQualityStr( self, equip, ratios ):
		"""
		设置品质标签,更新装备图标信息
		"""
		equipQuality = ItemTypeEnum.CQT_WHITE
		maxRatio = max( ratio for ratio in ratios.itervalues() )
		for quality, ratio in ratios.iteritems():
			if maxRatio == ratio:
				equipQuality = quality
				self.__setQuaTextColor( self.__pyStQuality, quality )
		player = BigWorld.player()
		equip.set( "quality", equipQuality, player )
		newReqLevel = equip.getReqLevel()/10*10
		if newReqLevel <= 0: newReqLevel = 1
		equip.set( "reqLevel", newReqLevel, player )
		self.__pyEquipItem.update( ObjectItem( equip ) )

	@reimpl_equipProduce.deco_equipProSet
	def __setQuaTextColor( self, pyStQuality, quality ):
		pyStQuality.text = self._ratio_color[quality][0]
#		pyStQuality.color = self._ratio_color[quality][1]

	def __getSameStuffs( self ):
		makeStuffs = {}
		equipNode = self.__pyTVEquip.pySelNode
		if equipNode is None:return
		equipID = equipNode.equipID
		stuffs = equipNode.stuffs
		stuffInfos = self.__pyMaterialsBag.getStuffInfos( )
		for stuffInfo in stuffInfos:
			hasAdded = False
			stuffID = stuffInfo.id
			stuff = stuffInfo.baseItem
			for baseID, num in stuffs.iteritems():
				stuffIDList = rds.equipMake.getClassList( baseID )
				if stuffID in stuffIDList and hasAdded == False:
					if makeStuffs.has_key( stuffID ):
						makeStuffs[stuffID] += stuff.getAmount()
					else:
						makeStuffs[stuffID] = stuff.getAmount()
					hasAdded = True
				else:
					if hasAdded == False:
						if makeStuffs.has_key( stuffID ):
							makeStuffs[stuffID] += stuff.getAmount()
						else:
							makeStuffs[stuffID] = stuff.getAmount()
						hasAdded = True
		return makeStuffs

	def __onAddStuff( self, kitbagID, orderID, index ): #添加材料
		orderID = kitbagID * csdefine.KB_MAX_SPACE + orderID
		item = BigWorld.player().getItem_( orderID )
		if item is None:
			return
		itemInfo = ObjectItem( item )
		count = item.getAmount()
		id = item.id
		if self.stuffKOs.has_key( kitbagID ) and self.stuffKOs[kitbagID] != None and orderID in self.stuffKOs[kitbagID]:
			return
		if not self.stuffKOs.has_key( kitbagID ):
			self.stuffKOs[kitbagID] = []
		equipNode = self.__pyTVEquip.pySelNode
		if equipNode is None or not equipNode.selected: #2008年07月23日spf
			return
		stuffs = equipNode.stuffs
		for baseID, num in stuffs.iteritems():
			oneList = rds.equipMake.getClassList( baseID )
			if id in oneList:
				self.__pyMaterialsPanel.changeNum( baseID, count )
		self.stuffKOs[kitbagID].append( orderID )
		self.__pyMaterialsBag.update( itemInfo, index )
		if self.__isCanMake():
			self.__setMakeRatio()
		self.__pyBtnOK.enable = self.__isCanMake()

	def getSameTypeStuffNum( self, stuffID ):
		"""
		计算同种类型的材料的总数 2008-08-12 spf
		@pram stuffID : 随便一个材料的ID，根据这个ID来计算装备合成面板中属于这种材料的所有材料的总数
		"""
		count = 0
		equipNode = self.__pyTVEquip.pySelNode
		baseStauffID = stuffID
		if equipNode is None or not equipNode.selected:
			return
		stuffs = equipNode.stuffs
		for baseID, num in stuffs.iteritems():
			oneList = rds.equipMake.getClassList( baseID )
			if stuffID in oneList:
				baseStauffID = baseID
				break
		stuffInfos = self.__pyMaterialsBag.getStuffInfos( )
		for stuffInfo in stuffInfos:
			sID = stuffInfo.id
			stuff = stuffInfo.baseItem
			if sID in rds.equipMake.getClassList( baseID ):
				count += stuff.getAmount()
		return count

	def __onReplaceStuff( self, kitbagID, orderID, index, srcKitbarID, srcOrderID ):
		convertedOrderID = kitbagID * csdefine.KB_MAX_SPACE + orderID
		srcOrderID = srcKitbarID * csdefine.KB_MAX_SPACE + srcOrderID
		if  self.stuffKOs.has_key( kitbagID ) and convertedOrderID in self.stuffKOs[kitbagID]\
			and not (  self.stuffKOs.has_key( srcKitbarID ) and srcOrderID in self.stuffKOs[srcKitbarID] ):
			self.__onRemoveStuff( kitbagID, orderID, index )

	def __onRemoveStuff( self, kitbagID, orderID, index ): #移除材料栏某一材料
		orderID = kitbagID * csdefine.KB_MAX_SPACE + orderID
		if orderID in self.stuffKOs[kitbagID]:
			self.stuffKOs[kitbagID].remove( orderID )
		equipNode = self.__pyTVEquip.pySelNode
		stuffID = self.__pyMaterialsBag.getStuffID( index )
		count = self.__pyMaterialsBag.getStuffNum( index )
		stuffs = equipNode.stuffs
		for baseID, num in stuffs.iteritems():
			oneList = rds.equipMake.getClassList( baseID )
			if stuffID in oneList:
				self.__pyMaterialsPanel.changeNum( baseID, -count )
		self.__pyMaterialsBag.update( None, index )
		self.__setMakeRatio()
		self.__pyBtnOK.enable = self.__isCanMake()

	def __onRemoveItem( self, itemInfo ): #从背包移除材料的回调
		if itemInfo is None:
			return
		orderID = itemInfo.kitbagID * csdefine.KB_MAX_SPACE + itemInfo.orderID
		if not ( self.stuffKOs.has_key( itemInfo.kitbagID ) and orderID in self.stuffKOs[itemInfo.kitbagID] ):
			return
		self.__pyMaterialsBag.removeItem( itemInfo.kitbagID, itemInfo.orderID )

	def __onSwapKitBags( self, srcKitbagID, srckitInfo, dstKitbagID, dstkitInfo ): # 交换背包2008-07-24 spf
		"""
		背包位上的背包发生改变的处理
		"""
		self.__pyMaterialsBag.swapItemsUpdateOrders( srcKitbagID, -1, dstKitbagID, -1 )

	def __onSwapItems( self, srcKitbagID, srcIndex, srcItemInfo, dstKitbagID, dstIndex, dstItemInfo ): #交换物品2008-07-24 spf
		"""
		背包的物品位置发生改变时,装备合成栏里也要改变存储的对应的背包内物品位置的索引
		"""
		self.__pyMaterialsBag.swapItemsUpdateOrders( srcKitbagID, srcIndex, dstKitbagID, dstIndex )

	def __onUpdateStuffOrders( self, oldKitbagID, newKitbagID, oldOrderID, newOrderID ):#2008-07-24 spf
		"""
		背包的物品位置发生改变时,合成面板进行处理后的回调,回调的原因是合成栏对应的背包物品索引存储在这个文件中
		"""
		oldOrderID = oldKitbagID * csdefine.KB_MAX_SPACE + oldOrderID
		newOrderID = newKitbagID * csdefine.KB_MAX_SPACE + newOrderID
		self.stuffKOs[oldKitbagID].remove( oldOrderID )
		if not self.stuffKOs.has_key( newKitbagID ):
			self.stuffKOs[newKitbagID] = []
		self.stuffKOs[newKitbagID].append( newOrderID )

	def __onKitbagUpdateItem( self, objItemInfo ) :#2008-08-12 spf
		"""
		背包的物品数量,属性等发生改变时,装备合成栏里也要跟着改变
		@pram objItemInfo : 发生了属性改变的物品的信息
		"""
		if objItemInfo is None:
			return
		orderID = objItemInfo.kitbagID * csdefine.KB_MAX_SPACE + objItemInfo.orderID
		if not ( self.stuffKOs.has_key( objItemInfo.kitbagID ) and orderID in self.stuffKOs[objItemInfo.kitbagID] ):
			return
		index = self.__pyMaterialsBag.getStuffPanelIndex( objItemInfo.kitbagID, objItemInfo.orderID )
		stuffID = self.__pyMaterialsBag.getStuffID( index )
		self.__pyMaterialsBag.update( objItemInfo, index )
		count = self.getSameTypeStuffNum( stuffID )
		self.__pyMaterialsPanel.updateNum( stuffID, count )
		if self.__isCanMake():
			self.__setMakeRatio()
		self.__pyBtnOK.enable = self.__isCanMake()

	def __onProduce( self ): #开始制造
		if not self.__isCanMake():return
		equipID = self.__pyTVEquip.pySelNode.equipID
		stuffs = []
		for stfs in self.stuffKOs.itervalues():
			if stfs:
				stuffs += stfs
		BigWorld.player().cell.equipMake( equipID, stuffs )

	def __isCanMake( self ): #判断是否能制造
		equipNode = self.__pyTVEquip.pySelNode
		if equipNode is None:return
		equipID = equipNode.equipID
		makeStuffs = self.__getSameStuffs()
		isCanMake = rds.equipMake.isCanMake( equipID, makeStuffs )
		return isCanMake

	def __getItemFromKitBag( self, kitbagID, orderID ):
		equipNode = self.__pyTVEquip.pySelNode
		if not equipNode or not equipNode.selected: return
		player = BigWorld.player()
		orderID = kitbagID*csdefine.KB_MAX_SPACE + orderID
		item = player.getItem_( orderID )
		count = item.getAmount()
		id = item.id
		itemInfo = ObjectItem( item )
		if self.stuffKOs.has_key( kitbagID ) and self.stuffKOs[kitbagID] != None and orderID in self.stuffKOs[kitbagID]:
			return
		if not self.stuffKOs.has_key( kitbagID ):
			self.stuffKOs[kitbagID] = []
		stuffs = equipNode.stuffs
		for baseID, num in stuffs.iteritems():
			oneList = rds.equipMake.getClassList( baseID )
			if id in oneList:
				self.__pyMaterialsPanel.changeNum( baseID, count )
		self.stuffKOs[kitbagID].append( orderID )
		self.__pyMaterialsBag.getItemFromKitBag( itemInfo )
		if self.__isCanMake():
			self.__setMakeRatio()
		self.__pyBtnOK.enable = self.__isCanMake()

	def __onAutoButton( self ):
		"""
		玩家点击自动放入材料按钮
		"""
		# 判断当前是否选择装备节点
		equipNode = self.__pyTVEquip.pySelNode
		if equipNode is None: return

		# 判断玩家身上材料是否足够
		# 判断如果需要拆分物品需要的包裹空格位是否足够
		# 记录需要合并的物品ID
		# 记录需要拆分的物品数量
		needCoalitionID = []
		needCoalitionAmount = []
		self.__findItemOrders = []
		player = BigWorld.player()
		stuffs = equipNode.stuffs
		lackItemID = 0 # 记录所缺材料的ID，用于提示角色缺少哪种材料
		for stuffID, amount in stuffs.iteritems():
			stuffList = rds.equipMake.getClassList( stuffID )
			stuffList.sort( reverse = True )										# 从高级材料开始搜索，进行反向排序(由高到低)
			rAmount = amount														# 记录当前材料需要的数量
			for nStuff in stuffList:
				if rAmount <= 0: break
				items = player.findItemsByIDFromNKCK( nStuff )
				if len( items ) == 0:
					lackItemID = nStuff
					continue
				itemAmountCount = sum( [item.amount for item in items] )
				# 在这个材料上需求的数量足够
				if itemAmountCount > rAmount:
					# 根据物品数量进行排序
					#items.sort( key = lambda x: x.amount )
					# 找寻是否有物品和需求数量相当，有的话就直接记录下这个物品
					orders = [ item.order for item in items if item.amount == rAmount ]
					if len( orders ) == 0:
						needCoalitionID.append( items[0].id )
						needCoalitionAmount.append( rAmount )
					else:
						self.__findItemOrders.append( orders[0] )
					rAmount = 0
				else:
					orders = [ item.order for item in items if item.amount == itemAmountCount ]
					if len( orders ) == 0:
						needCoalitionID.append( items[0].id )
						needCoalitionAmount.append( itemAmountCount )
					else:
						self.__findItemOrders.append( orders[0] )
					rAmount -= itemAmountCount
				if rAmount > 0:
					lackItemID = nStuff

			if rAmount > 0:
				lackItemName = LackItemDatas.get( lackItemID, labelGather.getText( "EquipProduce:main", "stuffText" ) ) # 根据ID从配置中读取材料名
				player.statusMessage( csstatus.AUTO_STUFF_NO_ENOUGH, lackItemName, amount )
				return

		for order in self.__findItemOrders:
			item = player.getItem_( order )
			if item is None: continue
			if item.isFrozen():
				self.__findItemOrders = []
				player.statusMessage( csstatus.AUTO_STUFF_ITEM_FROZEN )
				return

		# 要进行拆分合并的所有物品中，只要有一个物品处于锁定状态，则不允许拆分
		for itemID in needCoalitionID:
			items = player.findItemsByIDFromNKCK( itemID )
			for item in items:
				if item.isFrozen():
					self.__findItemOrders = []
					player.statusMessage( csstatus.AUTO_STUFF_ITEM_FROZEN )
					return

		if len( needCoalitionID ) == 0:
			self.__onAutoSuffs()
		else:
			player.cell.autoInStuffs( needCoalitionID, needCoalitionAmount )

		self.__pyBtnAuto.enable = False
		BigWorld.callback( 2.0, self.__onWiteForAuto )

	def __onWiteForAuto( self ):
		self.__pyBtnAuto.enable = True

	def __onAutoSuffs( self, orders = [] ):
		"""
		自动放入材料
		"""
		# 清理显示面板数据
		self.__pyMaterialsBag.clear()
		self.__pyMaterialsPanel.resetNum()
		self.stuffKOs = {}

		# 判断当前是否选择装备节点
		equipNode = self.__pyTVEquip.pySelNode
		if equipNode is None: return

		findOrders = self.__findItemOrders
		findOrders.extend( orders )

		for order in findOrders:
			kit = order/csdefine.KB_MAX_SPACE
			orderID = order%csdefine.KB_MAX_SPACE
			self.__getItemFromKitBag( kit, orderID )

		self.__findItemOrders = []

	def __onStateLeave( self, state ):
		if state == csdefine.TRADE_PRODUCE:
			BigWorld.player().tradeState = csdefine.TRADE_NONE
	# -----------------------------------------------------
	# public
	# -----------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def show( self ):
		self.__lastEquip = ()
		metierType = BigWorld.player().getClass()
		equipType = "20" + str( int(metierType/16) )
		for type, typeSet in self.equips.items():
			if type == equipType:
				self.__pyCBPro.selIndex = self.equips.items().index( (type, typeSet) )
		for cbItem in self.__pyCBEquip.items:
			if cbItem.name == labelGather.getText( "EquipProduce:main", "allType" ):
				self.__pyCBEquip.selItem = cbItem
				self.__onTypeSelected( self.__pyCBEquip.selIndex )
		Window.show( self )

	def onLeaveWorld( self ):
		self.__lastEquip = ()
		self.hide()

	def hide( self ):
		self.__pyBtnAuto.enable = False
		self.__pyTVEquip.pyNodes.clear()
		self.__pyMaterialsPanel.clear()
		self.__pyMaterialsBag.clear()
		self.__pyEquipItem.update( None )
		self.stuffKOs = {}
		for pyLabel in self.__pyStRatios.itervalues():
			pyLabel.text = ""
		self.__onStateLeave( BigWorld.player().tradeState )
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )
		Window.hide( self )
		self.__delTrap()

# --------------------------------------------------------
# EquipNode
# --------------------------------------------------------
class EquipNode( TreeNode ):
	def __init__( self ):
		TreeNode.__init__( self )
		self.focus = True
		self.crossFocus = True
		self.selectable = True
		self.__equipID = ""
		self.__stuffs = {}

	def dispose( self ):
		TreeNode.dispose( self )

	def _getEquipID( self ):
		return self.__equipID

	def _setEuipID( self, id ):
		self.__equipID = id

	def _getStuffs( self ):
		return self.__stuffs

	def _setStuffs( self, stuffs ):
		self.__stuffs = stuffs

	equipID = property( _getEquipID, _setEuipID )
	stuffs = property( _getStuffs, _setStuffs )

class CBItem:
	def __init__( self, tag, name ):
		self.tag = tag
		self.name = name
