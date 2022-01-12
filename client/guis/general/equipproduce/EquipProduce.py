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
		self.stuffKOs = {}		# �ֵ䣬����kitbag id��key����order id��value��
		self.__trapID = 0
		self.__entityID = 0
		self.__lastEquip = () 	# �����ϴ����ѡ��Ľڵ�
		self.__findItemOrders = []		# �Զ������������Ĳ���order����
		self.__pyStRatios = {}
		self.equips = equipstr.Datas
		self.__initialize( wnd )

		rds.mutexShowMgr.addMutexRoot( self, MutexGroup.TRADE1 )				# ��ӵ�MutexGroup.TRADE1������

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
			pyViewItem.pyLabel.foreColor = pyPanel.itemSelectedForeColor			# ѡ��״̬�µ�ǰ��ɫ
			pyViewItem.color = pyPanel.itemSelectedBackColor				# ѡ��״̬�µı���ɫ
		elif pyViewItem.highlight :
			pyViewItem.pyLabel.foreColor = pyPanel.itemHighlightForeColor		# ����״̬�µ�ǰ��ɫ
			pyViewItem.color = pyPanel.itemHighlightBackColor				# ����״̬�µı���ɫ
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
		self.__triggers["EVT_ON_TOGGLE_EQUIP_PRODUCE_WND"] = self.__onWndShow #��NPC�Ի��������촰��
		self.__triggers["EVT_ON_ADD_STUFF_ITEM"] = self.__onAddStuff
		self.__triggers["EVT_ON_REMOVE_STUFF_ITEM"] = self.__onRemoveStuff
		self.__triggers["EVT_ON_KITBAG_REMOVE_ITEM"] = self.__onRemoveItem
		self.__triggers["EVT_ON_SWRAP_PACK_ITEMS"] = self.__onSwapKitBags	#��Ӷ԰���λ��λ�Ĵ���2008-07-24 spf
		self.__triggers["EVT_ON_KITBAG_SWAP_ITEM"] = self.__onSwapItems		#��Ӷ԰�������Ʒ��λ�Ĵ���2008-07-24 spf
		self.__triggers["EVT_ON_KITBAG_UPDATE_STUFF_ORDERS"] = self.__onUpdateStuffOrders#������Ʒ��λ������2008-07-24 spf
		self.__triggers["EVT_ON_KITBAG_UPDATE_ITEM"] = self.__onKitbagUpdateItem		#ĳ����Ʒ��Ϣ�����ı�2008-07-25 spf
		self.__triggers["EVT_ON_REPLACE_STUFF_ITEM"] = self.__onReplaceStuff			#�����ϳ�����еĲ��� 2008-08-11 spf
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

	def __addTrap( self ):#�򿪴��ں�Ϊ�����ӶԻ�����
		player = BigWorld.player()
		distance = csconst.COMMUNICATE_DISTANCE
		self.__entityID = GUIFacade.getGossipTargetID()
		if hasattr( GUIFacade.getGossipTarget(), "getRoleAndNpcSpeakDistance" ):
			distance = GUIFacade.getGossipTarget().getRoleAndNpcSpeakDistance()
		self.__trapID = player.addTrapExt( distance, self.__onEntitiesTrapThrough )

	def __onEntitiesTrapThrough( self, entitiesInTrap ):
		gossiptarget = GUIFacade.getGossipTarget()#��ȡ��ǰ�Ի�NPC
		if gossiptarget and gossiptarget not in entitiesInTrap:#���NPC�뿪��ҶԻ�����
			self.hide()

	def __delTrap( self ) :
		player = BigWorld.player()
		if self.__trapID :
			player.delTrap( self.__trapID )	#ɾ����ҵĶԻ�����
			self.__trapID = 0

	def __onProfeSelected( self, selIndex ): #ѡ��װ��ְҵ
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
			if self.__lastEquip[0] != selItem.name:#ѡ��ȫ��
				lastType = labelGather.getText( "EquipProduce:main", "allType" )
			else:
				lastType = self.__lastEquip[1]
		for cbItem in self.__pyCBEquip.items:
			if cbItem.name == lastType:
				self.__pyCBEquip.selItem = cbItem
#				self.__onTypeSelected( pyViewItem.itemIndex )
		self.__pyBtnAuto.enable = False

	def __onTypeSelected( self, selIndex ): #ѡ���౸����,��������ڵ�
		if selIndex < 0:return
		selItem = self.__pyCBEquip.selItem
		tag = selItem.tag
		name = selItem.name
		self.__pyCBEquip.pyBox_.text = name
		self.__pyTVEquip.pyNodes.clear()
		typeTag = self.__pyCBPro.selItem.tag # ְҵ�ڵ���
		if tag in ["8","106","303"] and typeTag != "201" \
		or tag == "9" and typeTag == "201":# ȫ��
			equipSet = self.equips[typeTag]
			for typeID, typeStr in equipSet[1].iteritems():
				if typeTag in ["1","3"]: # ����
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
		else: #��������
			node = GUI.load("guis/general/equipproduce/eqtypenode.gui")
			uiFixer.firstLoadFix( node )
			typeNode = TreeNode( node )
			typeNode.text = name
			typeNode.selectable = False
			typeNode.extend()
			if typeTag in ["1","3"]: # ��������Ʒ
				newTag = "0" + tag
			else: # ����
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

	def __onEquipSelected( self, equipNode ): #ѡ��ĳ��װ���ڵ�
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
			self.__pyMaterialsPanel.updateNum( stuffID, count ) #���ò�����������
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
		#װ�������շ��� �����Ƿ�����ʾ�õ��� by����
		lvm = equip.getLevel()
		if lvm < 50:    #1~50 1.1^���ߵȼ�*100
			money = 1.1 ** lvm * 100
		else:           #51~150 1.03^���ߵȼ�*2700
			money = 1.03 ** lvm * 2700
		#���������ui�������

		self.__pyRtMoney.text = labelGather.getText( "EquipProduce:main", "rtMoney", utils.currencyToViewText( int( money ) ) )

	def __getStuffNum( self, stuffID ): #��ȡ��ID������������������������,Ӧ��ת��Ϊ���Ҫ���������
		stuffInfos = self.__pyMaterialsBag.getStuffInfos( ) #�������������������Ʒ��Ϣ
		stuffIDList = rds.equipMake.getClassList( stuffID ) #��ȡ���������װ���Ĳ���ID�б�
		count = 0 #һ�����Ͳ�������
		for stuffInfo in stuffInfos:
			amount = 0 #һ��ID��������
			basItem = stuffInfo.baseItem
			id = basItem.id
			if id in stuffIDList:
				amount = amount + basItem.getAmount()
			count += amount
		return count

	def __setMakeRatio( self ):#��ȡ��Ʒ�ʰٷֱ�
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
		for quality, colTuple in self._ratio_color.iteritems(): #���ðٷֱȱ�ǩ
			if self.__pyStRatios.has_key( quality ):
				pyRatioText = self.__pyStRatios[quality]
				rate = rds.equipMake.getOdds( equip, makeStuffs, quality ) * 100
				qualityRatios[quality] = rate
				sumRatio += rate

		# �޸�װ����ɫ������ʾ by����
		totelRate = 100.0
		q_keys = [ItemTypeEnum.CQT_PINK,ItemTypeEnum.CQT_GOLD,ItemTypeEnum.CQT_BLUE,ItemTypeEnum.CQT_WHITE]
		for r in q_keys:	# Ʒ�ʴӸߵ��ʹ�����Ҫ����
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
		����Ʒ�ʱ�ǩ,����װ��ͼ����Ϣ
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

	def __onAddStuff( self, kitbagID, orderID, index ): #��Ӳ���
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
		if equipNode is None or not equipNode.selected: #2008��07��23��spf
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
		����ͬ�����͵Ĳ��ϵ����� 2008-08-12 spf
		@pram stuffID : ���һ�����ϵ�ID���������ID������װ���ϳ�������������ֲ��ϵ����в��ϵ�����
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

	def __onRemoveStuff( self, kitbagID, orderID, index ): #�Ƴ�������ĳһ����
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

	def __onRemoveItem( self, itemInfo ): #�ӱ����Ƴ����ϵĻص�
		if itemInfo is None:
			return
		orderID = itemInfo.kitbagID * csdefine.KB_MAX_SPACE + itemInfo.orderID
		if not ( self.stuffKOs.has_key( itemInfo.kitbagID ) and orderID in self.stuffKOs[itemInfo.kitbagID] ):
			return
		self.__pyMaterialsBag.removeItem( itemInfo.kitbagID, itemInfo.orderID )

	def __onSwapKitBags( self, srcKitbagID, srckitInfo, dstKitbagID, dstkitInfo ): # ��������2008-07-24 spf
		"""
		����λ�ϵı��������ı�Ĵ���
		"""
		self.__pyMaterialsBag.swapItemsUpdateOrders( srcKitbagID, -1, dstKitbagID, -1 )

	def __onSwapItems( self, srcKitbagID, srcIndex, srcItemInfo, dstKitbagID, dstIndex, dstItemInfo ): #������Ʒ2008-07-24 spf
		"""
		��������Ʒλ�÷����ı�ʱ,װ���ϳ�����ҲҪ�ı�洢�Ķ�Ӧ�ı�������Ʒλ�õ�����
		"""
		self.__pyMaterialsBag.swapItemsUpdateOrders( srcKitbagID, srcIndex, dstKitbagID, dstIndex )

	def __onUpdateStuffOrders( self, oldKitbagID, newKitbagID, oldOrderID, newOrderID ):#2008-07-24 spf
		"""
		��������Ʒλ�÷����ı�ʱ,�ϳ������д����Ļص�,�ص���ԭ���Ǻϳ�����Ӧ�ı�����Ʒ�����洢������ļ���
		"""
		oldOrderID = oldKitbagID * csdefine.KB_MAX_SPACE + oldOrderID
		newOrderID = newKitbagID * csdefine.KB_MAX_SPACE + newOrderID
		self.stuffKOs[oldKitbagID].remove( oldOrderID )
		if not self.stuffKOs.has_key( newKitbagID ):
			self.stuffKOs[newKitbagID] = []
		self.stuffKOs[newKitbagID].append( newOrderID )

	def __onKitbagUpdateItem( self, objItemInfo ) :#2008-08-12 spf
		"""
		��������Ʒ����,���Եȷ����ı�ʱ,װ���ϳ�����ҲҪ���Ÿı�
		@pram objItemInfo : ���������Ըı����Ʒ����Ϣ
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

	def __onProduce( self ): #��ʼ����
		if not self.__isCanMake():return
		equipID = self.__pyTVEquip.pySelNode.equipID
		stuffs = []
		for stfs in self.stuffKOs.itervalues():
			if stfs:
				stuffs += stfs
		BigWorld.player().cell.equipMake( equipID, stuffs )

	def __isCanMake( self ): #�ж��Ƿ�������
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
		��ҵ���Զ�������ϰ�ť
		"""
		# �жϵ�ǰ�Ƿ�ѡ��װ���ڵ�
		equipNode = self.__pyTVEquip.pySelNode
		if equipNode is None: return

		# �ж�������ϲ����Ƿ��㹻
		# �ж������Ҫ�����Ʒ��Ҫ�İ����ո�λ�Ƿ��㹻
		# ��¼��Ҫ�ϲ�����ƷID
		# ��¼��Ҫ��ֵ���Ʒ����
		needCoalitionID = []
		needCoalitionAmount = []
		self.__findItemOrders = []
		player = BigWorld.player()
		stuffs = equipNode.stuffs
		lackItemID = 0 # ��¼��ȱ���ϵ�ID��������ʾ��ɫȱ�����ֲ���
		for stuffID, amount in stuffs.iteritems():
			stuffList = rds.equipMake.getClassList( stuffID )
			stuffList.sort( reverse = True )										# �Ӹ߼����Ͽ�ʼ���������з�������(�ɸߵ���)
			rAmount = amount														# ��¼��ǰ������Ҫ������
			for nStuff in stuffList:
				if rAmount <= 0: break
				items = player.findItemsByIDFromNKCK( nStuff )
				if len( items ) == 0:
					lackItemID = nStuff
					continue
				itemAmountCount = sum( [item.amount for item in items] )
				# ���������������������㹻
				if itemAmountCount > rAmount:
					# ������Ʒ������������
					#items.sort( key = lambda x: x.amount )
					# ��Ѱ�Ƿ�����Ʒ�����������൱���еĻ���ֱ�Ӽ�¼�������Ʒ
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
				lackItemName = LackItemDatas.get( lackItemID, labelGather.getText( "EquipProduce:main", "stuffText" ) ) # ����ID�������ж�ȡ������
				player.statusMessage( csstatus.AUTO_STUFF_NO_ENOUGH, lackItemName, amount )
				return

		for order in self.__findItemOrders:
			item = player.getItem_( order )
			if item is None: continue
			if item.isFrozen():
				self.__findItemOrders = []
				player.statusMessage( csstatus.AUTO_STUFF_ITEM_FROZEN )
				return

		# Ҫ���в�ֺϲ���������Ʒ�У�ֻҪ��һ����Ʒ��������״̬����������
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
		�Զ��������
		"""
		# ������ʾ�������
		self.__pyMaterialsBag.clear()
		self.__pyMaterialsPanel.resetNum()
		self.stuffKOs = {}

		# �жϵ�ǰ�Ƿ�ѡ��װ���ڵ�
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
