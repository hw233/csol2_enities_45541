# -*- coding: gb18030 -*-
#
# $Id: ItemsBagFacade.py,v 1.81 2008-08-20 01:52:39 yangkai xp $

from guis import *
import math
import ItemTypeEnum
from bwdebug import *
import BigWorld
import csstatus
import csconst
from event.EventCenter import *
from ItemBagRole import ItemBagRole
import funcEquip
from ItemsFactory import ObjectItem
from ItemSystemExp import *
import csdefine
from items.EquipEffectLoader import EquipEffectLoader
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
g_equipEffect = EquipEffectLoader.instance()
import Language
import Const
from TopGradeStuff import TopStuffID
from config.item.EquipEffects import serverDatas
import config.client.labels.GUIFacade as lbDatas
from love3 import gbref
from config.client.msgboxtexts import Datas as mbmsgs
from MessageBox import showMessage
from MessageBox import MB_OK_CANCEL
from MessageBox import RS_OK
from ItemSystemExp import RemoveCrystalExp
from ItemSystemExp import ChangePropertyExp
from ItemSystemExp import EquipImproveQualityExp
from config.client import casketFuncDsp

talismanSplitExp = TalismanExp.instance()
g_changeProperty = ChangePropertyExp.instance()
g_equipImproveQuality = EquipImproveQualityExp.instance()
g_removeCrystal = RemoveCrystalExp.instance()

ITEM_CRYSTAL_TYPE = 0x80301
class ItemsBagFacade:
	@staticmethod
	def reset():
		ItemsBagFacade.SplitItem = []

# --------------------------------------------------------------------
def __allowOperate() :
	player = BigWorld.player()
	if player is None : return False
	if not player.isPlayer() : return False
	if not player.isDead() :
		return True
	else:
		player.statusMessage( csstatus.ROLE_DIE_CANT_ITEM )		# add by 姜毅
	return False

# ------------------------------->
# 用于让底层调用
# ------------------------------->
def onKitbagItemUpdate( kitbagOrder, itemOrder, itemInstance ):
	"""
	物品栏的某个物品更新事件

	@param  kitbagOrder: 哪个背包
	@param    itemOrder: 物品在背包中的位置
	@param itemInstance: 物品实例，如果实品不存在了则为None
	"""
	if itemInstance is None:
		fireEvent( "EVT_ON_KITBAG_ITEM_INFO_CHANGED", kitbagOrder, itemOrder, None )
	else:
		itemInfo = ObjectItem( itemInstance )
		fireEvent( "EVT_ON_KITBAG_ITEM_INFO_CHANGED", kitbagOrder, itemOrder, itemInfo )

def onKitbagItemLockChanged( kitbagOrder, itemOrder, isLocked ):
	"""
	物品栏的某个位置锁定状态改变

	@param  kitbagOrder: INT; 哪个背包
	@param    itemOrder: INT; 物品在背包中的位置
	@param     isLocked: BOOL; 当前是否为上锁状态
	"""
	fireEvent( "EVT_ON_KITBAG_ITEM_LOCK_CHANGED", kitbagOrder, itemOrder, isLocked )


# ------------------------------->
# Items about
# ------------------------------->
def getKitbagItemDescription( kitbagOrder, itemOrder ):
	"""
	取得某个背包某个位置的物品信息
	@return: string
	"""
	player = BigWorld.player()
	if kitbagOrder not in player.kitbags:
		return ""
	order = kitbagOrder * csdefine.KB_MAX_SPACE + itemOrder
	item = player.getItem_( order )
	if item is None:
		return ""
	return item.description( player )

def autoUseKitbagItem( item ):
	"""
	自动判断并使用物品

	@param item: 道具
	@type  item: Item
	"""
	if not __allowOperate() : return
	player = BigWorld.player()
	BigWorld.player().useItem( item.uid )


def highLightEquipItem( kitOrder, orderID ):
	equipList = []
	if not __allowOperate() : return
	player = BigWorld.player()
	orderID = kitOrder * csdefine.KB_MAX_SPACE + orderID
	item = player.getItem_( orderID  )
	if item is None: return
	type = item.query("type")
	equipSet =ItemTypeEnum.m_cwt2cist
	for key,vals in equipSet.iteritems():
		valist = list( vals )
		if type in valist:
			k = key
			if k in funcEquip.m_cwt2cel:
				value = funcEquip.m_cwt2cel[k]
				equipList = list(value)
	fireEvent( "EVT_ON_HIGHLIGHT_ITEM", equipList )

def dehighLightEquipItem(  kitOrder, orderID ):
	itemList = []
	if not __allowOperate() : return
	player = BigWorld.player()
	orderID = kitOrder * csdefine.KB_MAX_SPACE + orderID
	item = player.getItem_( orderID  )
	if item is None:
#		player.statusMessage( csstatus.CIB_MSG_ITEM_NOT_EXIST )
		return
	type = item.query("type")
	equipSet =ItemTypeEnum.m_cwt2cist
	for key,vals in equipSet.iteritems():
		valist = list( vals )
		if type in valist:
			k = key
			if  k in funcEquip.m_cwt2cel:
				value = funcEquip.m_cwt2cel[k]
				itemList = list(value)
	fireEvent( "EVT_ON_DEHIGHLIGHT_ITEM", itemList )

def getSameTypeEquipDescriptions( kitbagID, orderID ) :
	player = BigWorld.player()
	orderID = csdefine.KB_MAX_SPACE * kitbagID + orderID
	item = player.getItem_( orderID )
	if item is None : return []
	if not item.isEquip() : return []
	dsp = []
	equipOrders = item.getWieldOrders()
	for index, order in enumerate( equipOrders ) :
		if order < 0 : continue
		eqItem = player.getItem_( order )
		if eqItem is None: continue
		text = lbDatas.ITEMS_CURREQUIP
		dsp.append( eqItem.description( player ) )
		if index > len(dsp) - 1: #防止index越界
			index = len(dsp) - 1
		dsp[index].insert(0,[text])
	return dsp

def getSameTypeEquipDecriptionsII( itemInfo ):
	"""
	"""
	player = BigWorld.player()
	if not itemInfo.baseItem.isEquip() : return []
	dsp = []
	equipOrders = itemInfo.baseItem.getWieldOrders()
	for index, order in enumerate( equipOrders ) :
		if order < 0 : continue
		eqItem = player.getItem_( order )
		if eqItem is None: continue
		text = lbDatas.ITEMS_CURREQUIP
		dsp.append( eqItem.description( player ) )
		if index > len(dsp) - 1: #防止index越界
			index = len(dsp) - 1
		dsp[index].insert(0,[text])
	return dsp

def getWarningVal( ):
	return 0.10

def getAbateval():
	return 0.01

def autoMoveKitbagItem( srcKitTote, srcOrderID, dstKitTote, dstOrderID ):
	"""
	移动某个道具到某个位置

	需要考虑源背包和目标背包类型，有可能需要根据不同类型做出不同的操作

	@param  srcKitTote: 源背包唯一标识
	@type   srcKitTote: INT8
	@param    srcOrder: 源背包的源位置
	@type     srcOrder: INT8
	@param  dstKitTote: 目标背包唯一标识
	@type   dstKitTote: INT8
	@param    dstOrder: 目标背包的目标位置，目标位置必须是空的
	@type     dstOrder: INT8
	"""
	if not __allowOperate() : return

	player = BigWorld.player()
	player.swapItem( srcKitTote, srcOrderID, dstKitTote, dstOrderID )

def destroyKitbagItem( uid ):
	"""
	销毁一个物品

	@param     uid: 物品的唯一ID
	@type      uid: INT64
	"""
	if not __allowOperate() : return
	BigWorld.player().destroyItem( uid )

def splitKitbagItem( uid, amount ):
	"""
	分开一个可叠加的道具。

	@param     uid: 物品的唯一ID
	@type      uid: INT64
	@param      amount: 表示从源物品里面分出多少个来
	@type       amount: UINT16
	"""
	if not __allowOperate() : return
	player = BigWorld.player()
	if player is None : return
	player.splitItem( uid, amount )

def isCooldownType( uid, cooldownType ) :
	"""
	判断是否允许显示 cooldown 表现
	uid		：物品的唯一ID
	cooldownType：coolDown 类型
	"""
	player = BigWorld.player()
	item = player.getItemByUid_( uid )
	if item is None : return False
	return item.isCooldownType( cooldownType )

def moveKbItemToKitTote( srcKitbag, srcIndex, kitBagID ):
	if not __allowOperate(): return
	player = BigWorld.player()
	player.moveKbItemToKitTote( srcKitbag, srcIndex, kitBagID )

def swapKitbag( srckitBagID, dstkitBagID ):
	if not __allowOperate(): return
	BigWorld.player().swapKitbag( srckitBagID, dstkitBagID )

def moveKitbagToKbItem( srckitBagID, dstkitBagID, dstOrder ):
	if not __allowOperate(): return
	BigWorld.player().moveKitbagToKbItem( srckitBagID, dstkitBagID, dstOrder )
# -----------------------------------------------------------------------

def addSplitItem( uid ):
	if not __allowOperate(): return
	player = BigWorld.player()
	item = player.getItemByUid_( uid )
	if item is None:
		player.statusMessage( csstatus.SPILT_ITEM_NOT_EXIST )
		return
	stackNum = item.amount
	if stackNum == 1:
		player.statusMessage( csstatus.SPLIT_ITEM_CANT_ONE )
		return
	iteminfo = ObjectItem( item )
	ItemsBagFacade.SplitItem = [uid]
	fireEvent( "EVT_ON_UPDATE_SPLIT_ITEM", iteminfo )


def removeSplitItem( ):
	if not __allowOperate(): return
	ItemsBagFacade.SplitItem = []
	fireEvent( "EVT_ON_UPDATE_SPLIT_ITEM", None )

def upDateKitBagItems( targetIndex ):
	if not __allowOperate(): return
	if targetIndex == 1:return
	player = BigWorld.player()
	fireEvent( "EVT_ON_UPDATE_PACK_ITEMS", targetIndex )
	items = player.getItems( targetIndex )
	for item in items:
		# 如果物品正在被交易中，那么不显示。wsf
		if item in player.si_myItem.itervalues():
			continue
		itemInfo = ObjectItem( item )
		fireEvent( "EVT_ON_KITBAG_ADD_ITEM", itemInfo )

def removeKitbagCB( kitBagID ):

	fireEvent( "EVT_ON_UPDATE_PACK_ITEM", kitBagID, None )

def addKitbagCB( kitBagID, kitBag):
	kitBagInfo = ObjectItem( kitBag )
	fireEvent( "EVT_ON_UPDATE_PACK_ITEM", kitBagID, kitBagInfo )

# --------------------------------------------------------------------------
# 神机匣相关
def getCasketFuncDsp( funType ):
	"""
	@type funType: int
	"""
	try:
		return casketFuncDsp.Datas[ funType ]
	except:
		ERROR_MSG("Key Error! when funType = ", funType)
		return ""

def getCasketItems( isCrys = False ): # 获得神机匣中物品
	player = BigWorld.player()
	items = player.getItems( csdefine.KB_CASKET_ID )
	if isCrys: #如果是水晶摘除
		items = [item for item in items if item.getOrder()%csdefine.KB_MAX_SPACE >= csdefine.KB_CASKET_SPACE]
	else:
		items = [item for item in items if item.getOrder()%csdefine.KB_MAX_SPACE < csdefine.KB_CASKET_SPACE]
	return items

# 这里神机匣里面7个功能中，材料合成走单独的接口
# 因为其接口参数和其他的不一样
def doCasketFunction( funIndex ):
	if not __allowOperate(): return
	player = BigWorld.player()
	try:
		kitCasketItem = player.kitbags[csdefine.KB_CASKET_ID]
	except KeyError:
		ERROR_MSG( "src(%i) Can't find kitCasket in kitbag %s" % ( player.id, csdefine.KB_CASKET_ID ) )
		return
	useDegree = kitCasketItem.getUseDegree()
	if useDegree <= 0:
		player.statusMessage( csstatus.CASKET_CANT_USE )
		DEBUG_MSG( "(%s):kitCasket has been used out." % player.getName() )
		return
	if player.isCasketLocked: return
	if player.state == csdefine.ENTITY_STATE_VEND:
		player.statusMessage( csstatus.CASKET_CANT_USE_WHEN_VEND )
		return
	if player.iskitbagsLocked():
		player.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
		return
	player.lockCasket()
	if funcDict[ funIndex ]():
		if funIndex == csdefine.CASKET_FUC_SPECIALCOMPOSE:
			def query(rs_id):
				if rs_id == RS_OK:
					player.cell.doCasketFunction( funIndex )
				else:player.unLockCasket()
			showMessage(mbmsgs[0x00a4],"",MB_OK_CANCEL,query)
			return True
		player.cell.doCasketFunction( funIndex )
	else:
		player.unLockCasket()

# ---------------------------------------------------------------
# 材料合成
# ---------------------------------------------------------------
def stuffComposeCost( baseAmount ):
	"""
	计算材料合成消费 by姜毅
	@param baseAmount : 合成基数
	@type baseAmount : int
	@param stuff : 材料等级
	@type stuff : int
	@return int
	"""
#	if not __allowOperate(): return 0
	kitCasketItems = getCasketItems()
	if len( kitCasketItems ) == 0: return 0
	player = BigWorld.player()
	mItems = {}
	levelForCost = 0 #为计算烧钱而捕捉的物品等级 by姜毅
	for item in kitCasketItems:
		if mItems.has_key( item.id ):
			mItems[item.id] += item.amount
		else:
			mItems[item.id] = item.amount
		levelForCost = item.getLevel()

	tSID = TopStuffID
	srcItemID = 0
	additiveInfo = {}
	g_stuff = StuffMergeExp.instance()
	for srcID in mItems:
		if g_stuff.canMerge( srcID ) and mItems[srcID] >= baseAmount:
			srcItemID = srcID
			additiveInfo = g_stuff.getAdditiveInfo( baseAmount, srcID )
			break
	if srcItemID == 0 or len(mItems) != (len(additiveInfo) + 1) or srcItemID in tSID:
		return 0

	srcAmount = mItems[srcItemID]
	dstAmount = int( srcAmount/baseAmount )

	if len( additiveInfo ) > 0:
		for additiveItemID in additiveInfo:
			if additiveItemID not in mItems or mItems[additiveItemID] < additiveInfo[additiveItemID]:
				return 0
		isBreak = False
		for d in xrange(1, dstAmount + 1):
			for additiveItemID in additiveInfo:
				if additiveInfo[additiveItemID] * d > mItems[additiveItemID]:
					isBreak = True
					break
			if isBreak:
				break
			dstAmount = d
	cost = g_stuff.getPrice( baseAmount, srcItemID ) * dstAmount
	return int(cost)

def stuffCompose( baseAmount ):
	"""
	材料合成
	@param baseAmount: 合成基数
	@type  baseAmount: int
	@return INT
	"""
	if not __allowOperate(): return
	kitCasketItems = getCasketItems()
	if len( kitCasketItems ) == 0: return
	player = BigWorld.player()
	if player.isCasketLocked: return False
	mItems = {}
	levelForCost = 0 #为计算烧钱而捕捉的物品等级 by姜毅
	for item in kitCasketItems:
		if mItems.has_key( item.id ):
			mItems[item.id] += item.amount
		else:
			mItems[item.id] = item.amount
		levelForCost = item.getLevel()
	srcItemID = 0										# 合成物品的ID
	additiveInfo = {}
	g_stuff = StuffMergeExp.instance()
	for srcID in mItems:
		if g_stuff.canMerge( srcID ) and mItems[srcID] >= baseAmount:
			srcItemID = srcID
			additiveInfo = g_stuff.getAdditiveInfo( baseAmount, srcID )
			break
	additiveItems = additiveInfo.copy()	# 多个对象为了不改变静态配置的原值 by 姜毅
	lenAdd = len( additiveItems )
	if srcItemID == 0 or lenAdd + 1 != len( mItems ):
		player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return False
	srcAmount = mItems[srcItemID]										# 物品的数量
	dstAmount = int( srcAmount / baseAmount )							# 最大合成的次数
	if dstAmount <= 0:
		player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return False
	if lenAdd > 0:
		for additiveItemID in additiveItems:
			if additiveItemID not in mItems or mItems[additiveItemID] < additiveItems[additiveItemID]:
				player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
				return False
	payMoneyStuC = stuffComposeCost( baseAmount )
	if player.money < int(payMoneyStuC):							#先交钱 后提货
		player.statusMessage( csstatus.EQUIP_REPAIR_NOT_ENOUGH_MONEY )
		return False
	if player.state == csdefine.ENTITY_STATE_VEND:
		player.statusMessage( csstatus.CASKET_CANT_USE_WHEN_VEND )
		return False
	player.lockCasket()
	player.cell.stuffCompose( baseAmount )

def stuffBindCheck( isRebuit = False ):
	"""
	材料合成检查材料绑定性 by 姜毅
	"""
	kitCasketItems = getCasketItems()
	if len( kitCasketItems ) == 0: return False
	binds = 0
	for item in kitCasketItems:
		if item.isBinded(): binds += 1
	if binds > 0 and binds < len( kitCasketItems ): return True
	return False

def getStuffMergeOdds( baseAmount ):
	"""
	根据材料合成基数获取成功率
	@param baseAmount: 合成基数
	@type  baseAmount: int
	@return None
	"""
	mItems = {}
	kitCasketItems = getCasketItems()
	for item in kitCasketItems:
		if mItems.has_key( item.id ):
			mItems[item.id] += item.amount
		else:
			mItems[item.id] = item.amount
	srcItemID = 0
	additiveInfo = {}
	g_stuff = StuffMergeExp.instance()
	for srcID in mItems:
		if g_stuff.canMerge( srcID ) and mItems[srcID] >= baseAmount:
			srcItemID = srcID
			additiveInfo = g_stuff.getAdditiveInfo( baseAmount, srcID )
			break
	if srcItemID == 0:
		return 0
	if len( additiveInfo ): #需要催化剂
		activeID = additiveInfo.keys()[0] #催化剂ID
		if len(mItems) != ( len(additiveInfo) + 1 ) or \
			not activeID in mItems:
				return 0
	else:
		if len(mItems) != ( len(additiveInfo) + 1 ):
			return 0
	return g_stuff.getOdds( baseAmount, srcItemID )

# ---------------------------------------------------------------
# 装备打孔
# ---------------------------------------------------------------
def getStilettoOdds():
	"""
	根据装备已有孔数获取成功率 by姜毅
	"""
	kitCasketItems = getCasketItems()
	equips = []
	stuffItems = []
	for item in kitCasketItems:
		if item.isFrozen(): return 0
		if item.isEquip():
			equips.append( item )
		else: return 0

	if len( equips ) != 1: return 0
	equip = equips[0]
	if not equip.canStiletto(): return 0
	currSlot = equip.getLimitSlot()
	g_sto = EquipStuddedExp.instance()
	odds = g_sto.getStilettoOdds( currSlot )
	return odds

def getStilettoCost( tag ):
	"""
	获得装备打孔花费
	@param tag: 神机匣功能索引
	@type  tag: int
	@return INT
	"""
	player = BigWorld.player()
	kitCasketItems = getCasketItems()
	equips = []
	for item in kitCasketItems:
		if item.isFrozen(): return 0
		if item.isEquip():
			equips.append( item )
		else: return 0
	if len( equips ) != 1: return 0
	equip = equips[0]
	if not equip.canStiletto(): return 0
	currSlot = equip.getLimitSlot()
	if currSlot >= equip.getMaxSlot(): return 0
	equipLevel = equip.getReqLevel()

	stilettoCost = calStilettoCost( equipLevel, currSlot )
	return stilettoCost

def calStilettoCost( equipLevel,slotCount ):
	return int( 120 * equipLevel * 2 ** ( slotCount - 1 )) #同步更新了公式 by姜毅

def equipStiletto():
	"""
	装备打孔
	"""
	player = BigWorld.player()
	kitCasketItems = getCasketItems()
	equips = []
	for item in kitCasketItems:
		if item.isFrozen():
			player.statusMessage( csstatus.CASKET_CANT_VENDSTATE )
			return False
		if item.isEquip():
			equips.append( item )
		else:
			player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False

	if len( equips ) == 0:
		player.statusMessage( csstatus.CASKET_PLAEASE_INPUT_EQUIP )
		return False

	if len( equips ) != 1:
		player.statusMessage( csstatus.CASKET_NEED_ONE_EQUIP_ONLY )
		return False

	equip = equips[0]
	equipLevel = equip.getReqLevel()


	if not equip.canStiletto():
		player.statusMessage( csstatus.CASKET_STUDDED_CANT )
		return False

	currSlot = equip.getLimitSlot()
	if currSlot >= equip.getMaxSlot():
		player.statusMessage( csstatus.CASKET_STUDDED_MAXSLOT )
		return False

	stilettoCost = calStilettoCost( equipLevel, currSlot )
	if player.money < stilettoCost:
		player.statusMessage( csstatus.CASKET_BIND_NEED_MONEY )
		return False

	return True


# ---------------------------------------------------------------
# 装备强化
# ---------------------------------------------------------------
def getIntensifyCost( tag ):
	"""
	获取强化所需金钱 by姜毅
	"""
	if len( getCasketItems() ) == 0:return 0
	equips = []			# 装备
	g_equipIntensify = EquipIntensifyExp.instance()
	for item in getCasketItems():
		if item.isEquip():
			equips += [item]

	if len( equips ) != 1:
		return 0

	equip = equips[0]
	equipLevel = equip.getReqLevel()

	intensifyLevel = equip.getIntensifyLevel()
	if intensifyLevel >= csdefine.EQUIP_INTENSIFY_MAX_LEVEL:
		return 0

	player = BigWorld.player()
	levelEqu = equip.getReqLevel()
	intensifyCost = g_equipIntensify.getReqMoney( levelEqu, intensifyLevel + 1 )
	#intensifyCost = getIntensifyCost( 0, intensifyCost )

	return int(intensifyCost)

def getIntensifyInfo( tag ):
	"""
	获得装备强化成功率
	@param tag: 神机匣功能索引
	@type  tag: int
	@return Int
	"""
	if len( getCasketItems() ) == 0:return 0

	dragonItems = []	# 龙珠
	luckItems = []		# 幸运宝石
	equips = []			# 装备
	g_equipIntensify = EquipIntensifyExp.instance()
	for item in getCasketItems():
		if item.isEquip():
			equips += [item]
		elif g_equipIntensify.isDragonGem( item ):	# 是否龙珠
			if len( dragonItems ) and dragonItems[0].id != item.id:
				return 0
			dragonItems.append( item )
		elif g_equipIntensify.isLuckGem( item ):	# 是否幸运宝石
			if len( luckItems ) and luckItems[0].id != item.id:
				return 0
			luckItems.append( item )
		else:
			return 0
	if len( equips ) != 1:
		return 0
	if len( dragonItems ) == 0:
		return 0

	equip = equips[0]
	equipLevel = equip.getReqLevel()
	dragonGem = dragonItems[0]

	# 每一种龙珠对应30级的装备
	minLevel = g_equipIntensify.getMinLevel( dragonGem.id )
	maxLevel = g_equipIntensify.getMaxLevel( dragonGem.id )
	if equipLevel < minLevel or equipLevel > maxLevel:
		return 0

	intensifyLevel = equip.getIntensifyLevel()
	if intensifyLevel >= csdefine.EQUIP_INTENSIFY_MAX_LEVEL:
		return -1

	# 获取是否放入的额外提升强化成功率的幸运水晶
	excOdds = 0
	if len( luckItems ):
		excOdds += g_equipIntensify.getExtraOdds( luckItems[0].id )	# 根据幸运水晶获得额外成功率

	odds = g_equipIntensify.getOdds( intensifyLevel + 1 )
	return min( odds + excOdds, 100 )

def equipIntensify():
	"""
	装备强化
	"""
	if len( getCasketItems() ) == 0:return 0
	g_equipIntensify = EquipIntensifyExp.instance()

	dragonItems = []	# 龙珠
	luckItems = []		# 幸运宝石
	equips = []			# 装备
	player = BigWorld.player()
	for item in getCasketItems():
		if item.isEquip():
			equips += [item]
		elif g_equipIntensify.isDragonGem( item ):	# 是否龙珠
			if len( dragonItems ) and dragonItems[0].id != item.id:
				player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
				return False
			dragonItems.append( item )
		elif g_equipIntensify.isLuckGem( item ):	# 是否幸运宝石
			if len( luckItems ) and luckItems[0].id != item.id:
				player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
				return False
			luckItems.append( item )
		else:
			player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False

	if len( equips ) == 0:
		player.statusMessage( csstatus.CASKET_PLAEASE_INPUT_EQUIP )
		return False
	elif len( equips ) != 1:
		player.statusMessage( csstatus.CASKET_NEED_ONE_EQUIP_ONLY )
		return False
	if len( dragonItems ) == 0:
		player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return False

	equip = equips[0]
	dragonGem = dragonItems[0]
	equipLevel = equip.getReqLevel()

	# 判断装备是否可强化
	if not equip.canIntensify():
		player.statusMessage( csstatus.CASKET_INTENSIFY_NO_SUPPORT )
		return False

	# 每一种龙珠对应30级的装备
	minLevel = g_equipIntensify.getMinLevel( dragonGem.id )
	maxLevel = g_equipIntensify.getMaxLevel( dragonGem.id )
	if equipLevel < minLevel or equipLevel > maxLevel:
		player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return False

	intensifyLevel = equip.getIntensifyLevel()
	if intensifyLevel >= csdefine.EQUIP_INTENSIFY_MAX_LEVEL:
		player.statusMessage( csstatus.CASKET_INTENSIFY_MAXLEVEL )
		return False

	player = BigWorld.player()
	levelEqu = equip.getReqLevel()
	intensifyCost = g_equipIntensify.getReqMoney( levelEqu, intensifyLevel + 1 )
	#intensifyCost = getIntensifyCost( 0, intensifyCost )
	if player.money < int(intensifyCost):							#先交钱 后提货
		player.statusMessage( csstatus.EQUIP_REPAIR_NOT_ENOUGH_MONEY )
		return False
	return True

def equipInteBindCheck( isRebuit = False ):
	"""
	装备强化检查材料绑定性 by 姜毅
	"""
	g_equipIntensify = EquipIntensifyExp.instance()
	binded = 0
	for item in getCasketItems():
		if item.isEquip() and item.isBinded(): return False
		if not ( g_equipIntensify.isDragonGem( item ) or g_equipIntensify.isLuckGem( item ) ):	continue
		if item.isBinded(): binded += 1
	if binded > 0: return True
	return False

# ---------------------------------------------------------------
# 装备改造
# ---------------------------------------------------------------
def getEquipRebuildCost( tag, isRebuild = False ):
	"""
	获取装备改造所耗费的金钱
	注意,该函数只是简单的从神机匣中取出一件白色装备，接着按照公式
	计算出消耗的金钱，没有进行能否成功合成的判断，因此在使用时应该先调用
	合成几率计算函数（getEquipRebuildOdds）获取几率判断后再调用此函数。
	@param tag: 神机匣功能索引
	@type  tag: int
	@return Int
	"""
	kitCasketItems = getCasketItems()
	if len( kitCasketItems ) == 0: return 0
	player = BigWorld.player()
	wEquips = []
	qEquips = []
	for item in kitCasketItems:
		# 计算出神机匣里面有多少件装备
		# 只能有一件白色装备和两件非白色的同品质装备
		# 才能进行改造
		if not item.isEquip():
			return 0
		if item.isWhite():
			wEquips.append( item )
		else:
			qEquips.append( item )
	# 判定放入的装备数量是否合格
	if len( wEquips ) != 1 or len( qEquips ) != 2:
		return 0
	wEquip = wEquips[0]
	qEquip1 = qEquips[0]
	qEquip2 = qEquips[1]
	# 装备类型必须一致，比如防具和武器一起将无法合成  2008-10-28 gjx
	maskCode = 0x030000 # 装备类型判断掩码
	if wEquip.getType() & maskCode == ItemTypeEnum.ITEM_WEAPON:		# 武器
		if qEquip1.getType() & maskCode != ItemTypeEnum.ITEM_WEAPON:
			return 0
		elif qEquip2.getType() & maskCode != ItemTypeEnum.ITEM_WEAPON:
			return 0
	elif wEquip.getType() & maskCode == ItemTypeEnum.ITEM_ARMOR:	# 防具
		if qEquip1.getType() & maskCode != ItemTypeEnum.ITEM_ARMOR :
			return 0
		elif qEquip2.getType() & maskCode != ItemTypeEnum.ITEM_ARMOR :
			return 0
	elif wEquip.getType() & maskCode == ItemTypeEnum.ITEM_ORNAMENT:	# 首饰
		if qEquip1.getType() & maskCode != ItemTypeEnum.ITEM_ORNAMENT :
			return 0
		elif qEquip2.getType() & maskCode != ItemTypeEnum.ITEM_ORNAMENT :
			return 0
	else:
		return 0
	# 装备等级限制
	if wEquip.getLevel() < 20 or qEquip1.getLevel() < 20 or qEquip2.getLevel() < 20:
		return 0
	# 判定放入的装备是否在同一等级段
	if not qEquip1.getLevel()/10 == qEquip2.getLevel()/10 == wEquip.getLevel()/10:
		return 0
	# 判定放入的装备品质是否合格
	if qEquip1.getQuality() != qEquip2.getQuality():
		return False
	if isRebuild:
		if wEquip.isBinded() and qEquip1.isBinded() and qEquip2.isBinded():
			return 0
		elif wEquip.isBinded() or qEquip1.isBinded() or qEquip2.isBinded():
			return 0
	# 判定money够不够
	#同步修改烧钱公式 by姜毅
	money = 0
	lvm = qEquip1.getLevel()
	if lvm > 0 and lvm <= 50:    #1~50 1.1^道具等级*100*品质/3
		money = 1.1 ** lvm * 100 * qEquip1.getQuality() /3
	else:           #51~150 1.03^道具等级*2700 *品质/3
		money = 1.03 ** lvm * 2700 * qEquip1.getQuality() /3
	return int( money )

def getEquipRebuildOdds( tag ):
	"""
	获取装备改造成功率
	@param tag: 神机匣功能索引
	@type  tag: int
	@return Int
	"""
	kitCasketItems = getCasketItems()
	if len( kitCasketItems ) == 0: return 0
	player = BigWorld.player()
	wEquips = []
	qEquips = []
	for item in kitCasketItems:
		# 计算出神机匣里面有多少件装备
		# 只能有一件白色装备和两件非白色的同品质装备
		# 才能进行改造
		if not item.isEquip():
			return 0
		if item.isWhite():
			wEquips.append( item )
		else:
			qEquips.append( item )

	# 判定放入的装备数量是否合格
	if len( wEquips ) != 1 or len( qEquips ) != 2:
		return 0

	wEquip = wEquips[0]
	qEquip1 = qEquips[0]
	qEquip2 = qEquips[1]

	# 装备类型必须一致，比如防具和武器一起将无法合成  2008-10-28 gjx
	maskCode = 0x030000 # 装备类型判断掩码
	if wEquip.getType() & maskCode == ItemTypeEnum.ITEM_WEAPON:		# 武器
		if qEquip1.getType() & maskCode != ItemTypeEnum.ITEM_WEAPON:
			return 0
		elif qEquip2.getType() & maskCode != ItemTypeEnum.ITEM_WEAPON:
			return 0
	elif wEquip.getType() & maskCode == ItemTypeEnum.ITEM_ARMOR:	# 防具
		if qEquip1.getType() & maskCode != ItemTypeEnum.ITEM_ARMOR :
			return 0
		elif qEquip2.getType() & maskCode != ItemTypeEnum.ITEM_ARMOR :
			return 0
	elif wEquip.getType() & maskCode == ItemTypeEnum.ITEM_ORNAMENT:	# 首饰
		if qEquip1.getType() & maskCode != ItemTypeEnum.ITEM_ORNAMENT :
			return 0
		elif qEquip2.getType() & maskCode != ItemTypeEnum.ITEM_ORNAMENT :
			return 0
	else:
		return 0

	# 装备等级限制
	if wEquip.getLevel() < 20 or qEquip1.getLevel() < 20 or qEquip2.getLevel() < 20:
		return 0

	# 判定放入的装备是否在同一等级段
	if not qEquip1.getLevel()/10 == qEquip2.getLevel()/10 == wEquip.getLevel()/10:
		return 0

	# 判定放入的装备品质是否合格
	if qEquip1.getQuality() != qEquip2.getQuality():
		return 0

	return 100

def getEquipImproveOdds( ):
	"""
	获取绿装升品成功率
	"""
	kitCasketItems = getCasketItems()
	badgeItems = []			#徽章
	equip = None				#装备
	needBind = False
	player = BigWorld.player()
	for item in kitCasketItems:
		if item.isFrozen():		#被冻结的物品不能被神机匣使用
			return 0
		if item.isEquip():
			if equip != None and equip.id != item.id:
				return 0
			equip = item
		elif g_equipImproveQuality.isBadge( item ):		#是否是徽章
			if len( badgeItems ) and badgeItems[0].id != item.id:
				return 0
			badgeItems.append( item )
		else:
			return 0
	if equip == None:
		return 0
	#判断是否有徽章
	if len( badgeItems ) == 0:
		return 0
	badgeItem = badgeItems[0]
	if equip.isGreen() == False:
		return 0
	equipLevel = equip.getReqLevel()
	minLevel = 90			#升品最低等级
	maxLevel = 149			#升品最高等级
	if equipLevel < minLevel or equipLevel > maxLevel:
		return 0
	if equip.isBinded() or badgeItem.isBinded():
		needBind = True
	equipPrefix = equip.getPrefix()
	odds=g_equipImproveQuality.getOdds( badgeItem.id , equipPrefix )
	return odds

def equipBindCheck( isRebuild = False ):
	"""
	检查装备合成材料中是否有已绑定的装备 by姜毅
	@type isRebuild		: bool
	@param isRebuild	: 是否用于equipRebuild函数 这东西是基于判定次序需求的
	"""
	kitCasketItems = getCasketItems()
	if len( kitCasketItems ) == 0: return False
	player = BigWorld.player()
	wEquips = []
	qEquips = []
	for item in kitCasketItems:
		# 计算出神机匣里面有多少件装备
		# 只能有一件白色装备和两件非白色的同品质装备
		# 才能进行改造
		if not item.isEquip():
			player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
		if item.isWhite():
			wEquips.append( item )
		else:
			qEquips.append( item )

	# 判定放入的装备数量是否合格
	if len( wEquips ) != 1 or len( qEquips ) != 2:
		player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return False

	wEquip = wEquips[0]
	qEquip1 = qEquips[0]
	qEquip2 = qEquips[1]

	# 装备类型必须一致，比如防具和武器一起将无法合成  2008-10-28 gjx
	maskCode = 0x030000 # 装备类型判断掩码
	if wEquip.getType() & maskCode == ItemTypeEnum.ITEM_WEAPON:		# 武器
		if qEquip1.getType() & maskCode != ItemTypeEnum.ITEM_WEAPON:
			player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
		elif qEquip2.getType() & maskCode != ItemTypeEnum.ITEM_WEAPON:
			player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
	elif wEquip.getType() & maskCode == ItemTypeEnum.ITEM_ARMOR:	# 防具
		if qEquip1.getType() & maskCode != ItemTypeEnum.ITEM_ARMOR :
			player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
		elif qEquip2.getType() & maskCode != ItemTypeEnum.ITEM_ARMOR :
			player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
	elif wEquip.getType() & maskCode == ItemTypeEnum.ITEM_ORNAMENT:	# 首饰
		if qEquip1.getType() & maskCode != ItemTypeEnum.ITEM_ORNAMENT :
			player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
		elif qEquip2.getType() & maskCode != ItemTypeEnum.ITEM_ORNAMENT :
			player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
	else:
		player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return False

	# 装备等级限制
	if wEquip.getLevel() < 20 or qEquip1.getLevel() < 20 or qEquip2.getLevel() < 20:
		player.statusMessage( csstatus.CASKET_CANT_REBUILD_LEVEL_LIMIT )
		return False

	# 判定放入的装备是否在同一等级段
	if not qEquip1.getLevel()/10 == qEquip2.getLevel()/10 == wEquip.getLevel()/10:
		player.statusMessage( csstatus.CASKET_CANT_REBUILD_DLEVEL_EQUIP )
		return False

	# 判定放入的装备品质是否合格
	if qEquip1.getQuality() != qEquip2.getQuality():
		player.statusMessage( csstatus.CASKET_CANT_REBUILD_QUALITY_WRONG )
		return False

	if isRebuild:
		if wEquip.isBinded() and qEquip1.isBinded() and qEquip2.isBinded():
			return False
		elif wEquip.isBinded() or qEquip1.isBinded() or qEquip2.isBinded():
			return True

	# 判定money够不够
	#money = ( qEquip1.getLevel() + qEquip2.getLevel() ) * 25
	#money = int( math.ceil( wEquip.getLevel() ** 2.5 * 0.6 ) ) # 消耗金钱的新计算公式 gjx 2008-10-28
	#同步修改烧钱公式 by姜毅
	lvm = qEquip1.getLevel()
	if lvm > 0 and lvm <= 50:    #1~50 1.1^道具等级*100*品质/3
		money = 1.1 ** lvm * 100 * qEquip1.getQuality() /3
	else:           #51~150 1.03^道具等级*2700 *品质/3
		money = 1.03 ** lvm * 2700 * qEquip1.getQuality() /3
	if player.money < int(money):
		player.statusMessage( csstatus.CASKET_BIND_NEED_MONEY )
	return False

def equipRebuild():
	"""
	装备改造
	"""
	equipBindCheck()
	return True
# ---------------------------------------------------------------
# 装备炼化
# ---------------------------------------------------------------
def getSmeltOdds( tag ):
	"""
	@param tag: 神机匣功能索引
	@type  tag: int
	@return Int
	"""
	pass

# ---------------------------------------------------------------
# 装备拆分
# ---------------------------------------------------------------
def equipSplit():
	"""
	装备拆分
	"""
	equips = []
	kitCasketItems = getCasketItems()
	player = BigWorld.player()
	if len(kitCasketItems) == 0:
		player.statusMessage( csstatus.CASKET_PLAEASE_INPUT_EQUIP )
		return False
	elif len(kitCasketItems) != 1:
		player.statusMessage( csstatus.CASKET_EQUIP_SPLIT_AMOUNT_ERROR )
		return False
	equip = kitCasketItems[0]
	if not equip.isEquip():	#不是装备
		player.statusMessage( csstatus.CASKET_ITEM_CANT_BE_SPLITED )
		return False
	if equip.isWhite():	#白装不能拆分
		if Language.LANG == Language.LANG_GBK:
			player.statusMessage( csstatus.CASKET_EQUIP_CANNOT_SPLIT )
		elif Language.LANG == Language.LANG_BIG5:
			player.statusMessage( csstatus.CASKET_EQUIP_CANNOT_SPLIT_BIG5 )
		return False
	payMoney = int( 0.3 * equip.getLevel() ** 1.5 * equip.getQuality() )
	if player.money < int(payMoney):	#如果钱不够
		player.statusMessage( csstatus.CASKET_SPLIT_PAY_FAILD )
		return False
	return True

def getSplitExpense():
	"""
	获取装备拆分的花费
	"""
	equips = []
	payMoney = 0
	kitCasketItems = getCasketItems()
	player = BigWorld.player()
	if len(kitCasketItems) == 0:
#		player.statusMessage( csstatus.CASKET_PLAEASE_INPUT_EQUIP )
		payMoney = 0
	elif len(kitCasketItems) == 1:
		equip = kitCasketItems[0]
		if not equip.isEquip():	#不是装备
#			player.statusMessage( csstatus.CASKET_EQUIP_SPLIT_AMOUNT_ERROR )
			payMoney = 0
		if equip.isWhite():	#白装不能拆分
#			player.statusMessage( csstatus.CASKET_EQUIP_CANNOT_SPLIT )
			payMoney = 0
		payMoney = int( 0.3 * equip.getLevel() ** 1.5 * equip.getQuality() ) #这里同步修改了花费公式
	return int(payMoney)
# ---------------------------------------------------------------
# 装备镶嵌
# ---------------------------------------------------------------

def equipStudded():
	"""
	装备镶嵌
	"""
	mItems = {}
	equips = []
	stuffItems = []
	kitCasketItems = getCasketItems()
	player = BigWorld.player()
	for item in kitCasketItems:
		if item.isEquip():
			equips += [item]
		else:
			if mItems.has_key( item.id ):
				mItems[item.id] += item.amount
			else:
				mItems[item.id] = item.amount
				stuffItems += [item]
	if len( equips ) == 0:
		player.statusMessage( csstatus.CASKET_PLAEASE_INPUT_EQUIP )
		return False
	elif len( stuffItems ) == 0:
		player.statusMessage( csstatus.CASKET_NEET_CRYSTAL )
		return False
	elif len( equips ) != 1:
		player.statusMessage( csstatus.CASKET_NEED_ONE_EQUIP_ONLY )
		return False
	equip = equips[0]
	stuff = EquipStuddedExp.instance().getStuff()
	if mItems in stuff:
		stuffItem = stuffItems[0]
		studdedEffect = stuffItem.getBjExtraEffect()
		if len( studdedEffect ) == 0:
			player.statusMessage( csstatus.CASKET_STUDDED_NEED_NO_EMPTY )
			return False
		if not equip.getLimitSlot():
			player.statusMessage( csstatus.CASKET_NEET_STILETTO_FIRST )
			return False
		if equip.getSlot() >= equip.getLimitSlot():
			player.statusMessage( csstatus.CASKET_STUDDED_NOT_HOLD )
			return False
		if stuffItem.getReqLevel() > equip.getReqLevel():
			player.statusMessage( csstatus.CASKET_STUDDED_NO_SUPPORT )
			return False
		# 一个类型水晶只能嵌一个 by姜毅
		keys = equip.getBjExtraEffect()
		if len( keys ) > 0:
			for keySingle in keys:
				keyList = serverDatas.get( keySingle, [] )
				if stuff in keyList:
					player.statusMessage( csstatus.CASKET_STUDDED_NO_MORE )
					return False
	return True

def equipStuddedBindCheck( isRebuit = False ):
	"""
	装备镶嵌检查材料的绑定特性 by姜毅
	"""
	if not isRebuit: return False
	kitCasketItems = getCasketItems()
	binded = 0
	for item in kitCasketItems:
		if item.isEquip() and item.isBinded(): return False
		elif item.isBinded() and item.getType() == ITEM_CRYSTAL_TYPE: binded += 1
	if binded > 0: return True
	return False

# ---------------------------------------------------------------
# 装备绑定  改为装备认主 by姜毅
# ---------------------------------------------------------------
def getBindCost( tag ):
	"""
	获取装备认主花费
	@param tag: 神机匣功能索引
	@type  tag: int
	@return Int
	"""
	kitCasketItems = getCasketItems()
	if len( kitCasketItems ) == 0:
		return 0
	equips = []
	for item in kitCasketItems:
		if item.isFrozen():
			return 0
		if item.isEquip():
			equips += [item]

	if len( equips ) != 1:
		return 0
	equip = equips[0]
	if equip.getType() in [ ItemTypeEnum.ITEM_SYSTEM_TALISMAN, ItemTypeEnum.ITEM_SYSTEM_KASTONE, ItemTypeEnum.ITEM_FASHION1, ItemTypeEnum.ITEM_FASHION2, ItemTypeEnum.ITEM_POTENTIAL_BOOK ]:
		return 0
	if equip.isObey():
		return 0
	#money = equip.getReqLevel() * g_bind.getPerCost()
	#同步装备认主公式修改 by姜毅
	lvm = equip.getLevel()
	if lvm > 0 and lvm <= 50:    #1~50 1.1^道具等级*100*品质/3
		money = 1.1 ** lvm * 100 * equip.getQuality() /3
	else:           #51~150 1.03^道具等级*2700 *品质/3
		money = 1.03 ** lvm * 2700 * equip.getQuality() /3
	return int(money)

def equipBind():
	"""
	装备认主
	"""
	kitCasketItems = getCasketItems()
	stuff = EquipBindExp.instance().getStuff()
	player = BigWorld.player()
	if len( kitCasketItems ) == 0:
		player.statusMessage( csstatus.CASKET_PLAEASE_INPUT_EQUIP )
		return False
	mItems = []
	equips = []
	for item in kitCasketItems:
		if item.isEquip():
			equips += [item]
		elif item.id in stuff:
			mItems += [item]
		else:
			player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False

	if len( equips ) == 0:
		player.statusMessage( csstatus.CASKET_PLAEASE_INPUT_EQUIP )
	elif len( equips ) != 1:
		player.statusMessage( csstatus.CASKET_NEED_ONE_EQUIP_ONLY )
		return False
	if len( mItems ) == 0:
		player.statusMessage( csstatus.MERGE_ORNAMENT_NEED_MATERIAL )
		return False
	equip = equips[0]
	# 加入不能认主的装备类型判断 by姜毅
	if equip.getType() in [ ItemTypeEnum.ITEM_SYSTEM_TALISMAN, ItemTypeEnum.ITEM_SYSTEM_KASTONE, ItemTypeEnum.ITEM_FASHION1, ItemTypeEnum.ITEM_FASHION2, ItemTypeEnum.ITEM_POTENTIAL_BOOK ]:
		player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return False
	if equip.isWhite():
		player.statusMessage( csstatus.CASKET_WHITEEQUIP_IS_WRONG )
		return False
	if equip.isObey():
		player.statusMessage( csstatus.KIT_EQUIP_OBEY_YET )
		return False

	#money = equip.getReqLevel() * g_bind.getPerCost()
	#同步装备认主公式修改 by姜毅
	lvm = equip.getLevel()
	if lvm > 0 and lvm <= 50:    #1~50 1.1^道具等级*100*品质/3
		money = 1.1 ** lvm * 100 * equip.getQuality() /3
	else:           #51~150级 1.03^道具等级*2700 *品质/3
		money = 1.03 ** lvm * 2700 * equip.getQuality() /3
	if player.money < int(money):
		player.statusMessage( csstatus.CASKET_BIND_NEED_MONEY )
		return False

	bindType = equip.getBindType()
	isBinded = equip.isBinded()
	if bindType == ItemTypeEnum.CBT_EQUIP and not isBinded:
		funIndex = csdefine.CASKET_FUC_EQUIPBIND
		def query( rs_id ):
			if rs_id == RS_OK:
				player.cell.doCasketFunction( funIndex )
		showMessage( mbmsgs[0x00a5], "", MB_OK_CANCEL, query )
		return False
	return True

def specialCompCost( tag ):
	"""
	特殊合成收费 by姜毅
	"""
	return rds.specialCompose.getRequireMoney()

def specialCompose():
	"""
	特殊合成
	@return Bool
	"""
	specom = rds.specialCompose
	#根据卷轴ID获得材料、目标物品等配置
	bindResult= specom.getIsBind( scrollID )  #生成的物品是否绑定
	money     = specom.getRequireMoney( scrollID ) #消耗的金钱
	dstItemID = specom.getDstItemID( scrollID )  #目标物品ID
	dstAmount = specom.getDstItemCount( scrollID )  #目标物品的数量
	mItems    = specom.getMaterials( scrollID ) #合成材料及其数量
	p = BigWorld.player()
	if p.__class__.__name__ != "PlayerRole":return False
	#-----------------判断配置是否合理----------------
	if not dstItemID:return False
	if not dstAmount:return False
	if not mItems:return False
	
	#------------------判断背包空位-------------------
	orderIDs = p.getAllNormalKitbagFreeOrders()
	if len( orderIDs ) < dstAmount :
		p.statusMessage( csstatus.CASKET_EQUIP_SPECIAL_COMPOSE_NO_SPACE )
		return False
	
	#------------------判断背包中是否存在所有材料--------------
	for iteminfo in mItems:
		itemID = iteminfo[0]
		count  = iteminfo[1]
		sitems = p.findItemsByIDFromNK( itemID )
		scount = 0
		for item in sitems:
			scount += item.getAmount()
		if scount < count:
			p.statusMessage( csstatus.CASKET_EQUIP_SPECIAL_COMPOSE_LACK_METERIAL )
			return False
	if p.money < int( money ):
		p.statusMessage( csstatus.CASKET_BIND_NEED_MONEY )
		return False
	return True

def talismanFix(): #法宝修复
	talismanItems = []
	lifeItems = []
	player = BigWorld.player()
	kitCasketItems = player.getItems( csdefine.KB_CASKET_ID )
	for item in kitCasketItems:
		if item.isFrozen():		#被冻结的物品不能被神机匣使用
			player.statusMessage( csstatus.CASKET_CANT_VENDSTATE )
			return False
		if item.id == csconst.TALISMAN_ADD_LIFE_ITEM:
			lifeItems.append( item )
		elif item.getType() == ItemTypeEnum.ITEM_SYSTEM_TALISMAN:
			talismanItems.append( item )
		else:
			# 只能放入法宝和女娲石
			player.statusMessage( csstatus.TALISMAN_ADDLIFE_NEED_TANDN )
			return False

	talismanCount = len( talismanItems )
	if talismanCount == 0:
		# 请放入需要充值的法宝
		player.statusMessage( csstatus.TALISMAN_ADDLIFE_NEED_TAl )
		return False
	if talismanCount > 1:
		# 一次只能给一个法宝充值
		player.statusMessage( csstatus.TALISMAN_ADDLIFE_ONCE )
		return False

	if not talismanItems[0].isActiveLifeTime():
		# 法宝未激活
		player.statusMessage( csstatus.TALISMAN_NOT_ACTIVE )
		return False

	if len( lifeItems ) == 0:
		# 请放入女娲石
		player.statusMessage( csstatus.TALISMAN_ADDLIFE_NEED_NWS )
		return False
	lifeCount = sum([item.amount for item in lifeItems])
	addTime = Const.TALISMAN_ADD_LIFE_TIME * lifeCount
	if addTime <= 0: return False
	player.cell.addTalismanLife()
	return True

def talismanSplitCheck():
	"""
	法宝分解 绑定性检测 by 姜毅
	"""
	kitCasketItems = getCasketItems()
	if len(kitCasketItems) != 1:
		return False
	talismanItem = kitCasketItems[0]
	if talismanItem.isFrozen() or \
		talismanItem.getType() != ItemTypeEnum.ITEM_SYSTEM_TALISMAN or \
		not talismanItem.isBinded():		#被冻结的物品不能被神机匣使用
		return False
	return True

def getTaliSplitCost( item = None ):
	"""
	获取法宝分解费用
	"""
	talismanItem = None
	if item is None:
		kitCasketItems = getCasketItems()
		if len(kitCasketItems) != 1:
			return 0
		talismanItem = kitCasketItems[0]
		if talismanItem.isFrozen() or \
			talismanItem.getType() != ItemTypeEnum.ITEM_SYSTEM_TALISMAN:		#被冻结的物品不能被神机匣使用
			return 0
	else:
		talismanItem = item
	grade = talismanItem.getGrade()
	return talismanSplitExp.getSplitCost( grade )

def talismanSplit():
	"""
	法宝分解 by 姜毅
	"""
	kitCasketItems = getCasketItems()
	player = BigWorld.player()
	if len(kitCasketItems) != 1:
		player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return False
	talismanItems = kitCasketItems[0]
	if talismanItems.isFrozen():		#被冻结的物品不能被神机匣使用
		player.statusMessage( csstatus.CASKET_CANT_VENDSTATE )
		return False
	if talismanItems.getType() != ItemTypeEnum.ITEM_SYSTEM_TALISMAN:		# 只能放入法宝
		player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return False
	payMoney = getTaliSplitCost( talismanItems )
	if player.money < int(payMoney):	#如果钱不够
		player.statusMessage( csstatus.CASKET_SPLIT_PAY_FAILD )
		return False
	return True

def getTaliInstCost():
	"""
	获取法宝强化费用
	"""
	return 0

def talismanIntensifyCheck():
	"""
	法宝强化 绑定性检测 by 姜毅
	"""
	kitCasketItems = getCasketItems()
	g_equipIntensify = EquipIntensifyExp.instance()
	for item in kitCasketItems:
		if item.id == csconst.TALISMAN_ADD_LIFE_ITEM and item.isBinded():	# 女娲石
			return True
		elif item.getType() == ItemTypeEnum.ITEM_SYSTEM_TALISMAN and item.isBinded():	# 法宝
			return True
		elif g_equipIntensify.isLuckGem( item ) and item.isBinded():	# 是否幸运宝石
			return True
	return False

def talismanIntensifyOdd():
	"""
	法宝强化成功率
	"""
	talismanItem = None
	talismanItems = []
	lifeItems = []
	luckeyItems = []
	kitCasketItems = getCasketItems()
	if len( kitCasketItems ) < 2:
		self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return 0
	g_equipIntensify = EquipIntensifyExp.instance()
	for item in kitCasketItems:
		if item.isFrozen():		#被冻结的物品不能被神机匣使用
			return 0
		if item.id == csconst.TALISMAN_ADD_LIFE_ITEM:	# 女娲石
			lifeItems.append( item )
		elif item.getType() == ItemTypeEnum.ITEM_SYSTEM_TALISMAN:	# 法宝
			talismanItems.append( item )
		elif g_equipIntensify.isLuckGem( item ):	# 是否幸运宝石
			luckeyItems.append( item )
		else:
			return 0
	if len( talismanItems ) != 1 or len( lifeItems ) < 1:
		return 0
	oldtalismanItem = talismanItems[0]
	intensifyLevel = oldtalismanItem.getIntensifyLevel()
	luckItem = None
	excOdds = 0.0
	if len( luckeyItems ) > 0:
		luckItem = luckeyItems[0]
		excOdds = g_equipIntensify.getExtraOdds( luckItem.id )	# 根据幸运水晶获得额外成功率
	odds = g_equipIntensify.getOdds( intensifyLevel + 1 )
	return odds + excOdds

def talismanIntensify():
	"""
	法宝强化 by 姜毅
	"""
	talismanItem = None
	talismanItems = []
	lifeItems = []
	luckeyItems = []
	kitCasketItems = getCasketItems()
	player = BigWorld.player()
	if len( kitCasketItems ) < 2:
		player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return False
	g_equipIntensify = EquipIntensifyExp.instance()
	for item in kitCasketItems:
		if item.isFrozen():		#被冻结的物品不能被神机匣使用
			player.statusMessage( csstatus.CASKET_CANT_VENDSTATE )
			return False
		if item.id == csconst.TALISMAN_ADD_LIFE_ITEM:	# 女娲石
			lifeItems.append( item )
		elif item.getType() == ItemTypeEnum.ITEM_SYSTEM_TALISMAN:	# 法宝
			talismanItems.append( item )
		elif g_equipIntensify.isLuckGem( item ):	# 是否幸运宝石
			luckeyItems.append( item )
		else:
			player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )	# 只能放入法宝和女娲石或者幸运石
			return False
	if len( talismanItems ) != 1 or len( lifeItems ) < 1:
		player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return False
	oldtalismanItem = talismanItems[0]
	intensifyLevel = oldtalismanItem.getIntensifyLevel()
	"""
	if not talismanItem.canIntensify():
		self.statusMessage( csstatus.CASKET_INTENSIFY_NO_SUPPORT )
		return False
	"""
	if intensifyLevel >= csdefine.EQUIP_INTENSIFY_MAX_LEVEL:
		self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return False

	return True

def changePropertyPrefix():
	"""
	装备洗前缀
	"""
	kitCasketItems = getCasketItems()
	greenEquips = []
	pinkEquips = []
	stuffItems = []
	mItems = {}
	player = BigWorld.player()
	for item in kitCasketItems:
		if item.isEquip():
			if item.isGreen():
				greenEquips += [item]
			elif item.isPink():
				pinkEquips += [item]
		else:
			if mItems.has_key( item.id ):
				mItems[item.id] += item.amount
			else:
				mItems[item.id] = item.amount
				stuffItems += [item]
	if len( greenEquips ) == 0:
		player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return False
	elif len( greenEquips ) != 1:
		player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return False
	if len( pinkEquips ) != 2:
		player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return False
	greenEquip = greenEquips[0]
	if not greenEquip.query( "isSystemItem" ):
		player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return False
	stuff = g_changeProperty.getStuff()
	if mItems not in stuff:
		player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG  )
		return False
	if not 60 <= greenEquip.getLevel() <= 149:
		player.statusMessage( csstatus.CASKET_MATIRAL_EQUIP_IS_WRONG )
		return False
	for item in pinkEquips:
		if item.getLevel()/10 != greenEquip.getLevel()/10 or item.getWieldOrders() != greenEquip.getWieldOrders():
			player.statusMessage( csstatus.CASKET_PINK_EQUIP_IS_WRONG )
			return False
	level = stuffItems[0].getLevel()
	if not( level <= greenEquip.getLevel() < level + 30 ):
		player.statusMessage( csstatus.CASKET_TOOL_LEVEL_IS_WRONG  )
		return False
	return True

def equipImproveQuality():
	"""
	绿装升品
	"""
	kitCasketItems = getCasketItems()
	badgeItems = []			#徽章
	equip = None				#装备
	needBind = False
	player = BigWorld.player()
	for item in kitCasketItems:
		if item.isFrozen():		#被冻结的物品不能被神机匣使用
			player.statusMessage(csstatus.CASKET_CANT_VENDSTATE)
			return False
		if item.isEquip():
			if equip != None and equip.id != item.id:
				player.statusMessage( csstatus.CASKET_NEED_ONE_EQUIP_ONLY )
				return False
			equip = item
		elif g_equipImproveQuality.isBadge( item ):		#是否是徽章
			if len( badgeItems ) and badgeItems[0].id != item.id:
				player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
				return False
			badgeItems.append( item )
		else:
			player.statusMessage(csstatus.CASKET_MATIRAL_IS_WRONG)
			return False
	if equip == None:
		player.statusMessage( csstatus.CASKET_PLAEASE_INPUT_EQUIP )
		return False
	#判断是否有徽章
	if len( badgeItems ) == 0:
		player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return False
	badgeItem = badgeItems[0]
	if equip.isGreen() == False:
		player.statusMessage( csstatus.CASKET_EQUIP_CANNOT_IMPROVE_BIG5 )
		return False
	equipLevel = equip.getReqLevel()
	minLevel = 90			#升品最低等级
	maxLevel = 149			#升品最高等级
	if equipLevel < minLevel or equipLevel > maxLevel:
		player.statusMessage( csstatus.CASKET_CANT_IMPROVE_LEVEL_LIMIT )
		return False
	if equip.isBinded() or badgeItem.isBinded():
		needBind = True
	equipPrefix = equip.getPrefix()
	odds=g_equipImproveQuality.getOdds( badgeItem.id , equipPrefix )
	if odds == 0:
		player.statusMessage( csstatus.CASKET_EQUIP_OR_MATIRAL_IS_WRONG )
		return False
	return True

bindCheck = {
			csdefine.CASKET_FUC_STUFFCOMPOSE	:	stuffBindCheck,
			csdefine.CASKET_FUC_EQUIPREBUILD		:	equipBindCheck,
			csdefine.CASKET_FUC_EQUIPSTUDDED	:	equipStuddedBindCheck,
			csdefine.CASKET_FUC_EQUIPINTENSIFY	:	equipInteBindCheck,
			csdefine.CASKET_FUC_TALISMAN_SPLIT	:	talismanSplitCheck,
			csdefine.CASKET_FUC_TALISMAN_INS	:	talismanIntensifyCheck,
			}

funcDict = {
		csdefine.CASKET_FUC_EQUIPINTENSIFY	: equipIntensify,	# 装备强化
		csdefine.CASKET_FUC_EQUIPREBUILD	: equipRebuild, 	# 装备改造
		csdefine.CASKET_FUC_EQUIPSTUDDED	: equipStudded,		# 装备镶嵌
		csdefine.CASKET_FUC_EQUIPSTILETTO	: equipStiletto, 	# 装备打孔
		#csdefine.CASKET_FUC_EQUIPSMELT		: equipSmelt, 		# 装备炼化
		csdefine.CASKET_FUC_EQUIPSPLIT		: equipSplit, 		# 装备拆分
		csdefine.CASKET_FUC_EQUIPBIND		: equipBind, 		# 装备认主
		csdefine.CASKET_FUC_SPECIALCOMPOSE  : specialCompose,	# 特殊合成
		csdefine.CASKET_FUC_TALISMANFIX		: talismanFix,		# 法宝修复
		csdefine.CASKET_FUC_TALISMAN_SPLIT	: talismanSplit,	# 法宝分解
		csdefine.CASKET_FUC_TALISMAN_INS	: talismanIntensify,	# 法宝强化
		csdefine.CASKET_FUC_CHANGEPROPERTY	: changePropertyPrefix,#装备洗前缀
		csdefine.CASKET_FUC_IMPROVEQUALITY  : equipImproveQuality, #绿装升品

		}

def equipGodWeapon( weaponItem ):
	"""
	神器炼制
	"""
	player = BigWorld.player()
	if player is None:
		return
	level = weaponItem.getReqLevel()
	quality = weaponItem.getQuality()
	if quality != ItemTypeEnum.CQT_GREEN:
		player.statusMessage( csstatus.GW_LEVEL_NOT_ENOUTH )
		return
	equipGodExp = EquipGodWeaponExp.instance()
	maxLevel = equipGodExp.getGodWeaponMaxLevel()
	minLevel = equipGodExp.getGodWeaponMinLevel()
	if level >= maxLevel:
		player.statusMessage( csstatus.GW_LEVEL_MAX, maxLevel )
		return
	if level < minLevel:
		player.statusMessage( csstatus.GW_LEVEL_NOT_ENOUTH, minLevel )
		return
	stuffs = equipGodExp.getGodWeaponStuff( level )
	if len( stuffs ) <= 0:
		return
	c_item_id = stuffs[0]	# 神器普物品ID
	x_item_id = stuffs[1]	# 刑天石物品ID
	c_items = player.findItemsByIDFromNKCK( c_item_id )
	if len( c_items ) <= 0:
		player.statusMessage( csstatus.GW_MAKE_NEED_ITEM, gbref.rds.itemsDict.id2name( c_item_id ) )
		return
	x_items = player.findItemsByIDFromNKCK( x_item_id )
	needAmount = stuffs[2]	# 所需刑天石数量
	if len( x_items ) <= 0:
		player.statusMessage( csstatus.GW_MAKE_NEED_ITEM2, needAmount, gbref.rds.itemsDict.id2name( x_item_id ) )
		return
	totalAmount = 0
	for xi in x_items:
		if xi.isFrozen():
			player.statusMessage( csstatus.CIB_MSG_FROZEN )
			return
		totalAmount += xi.getAmount()
	if totalAmount < needAmount:
		player.statusMessage( csstatus.GW_MAKE_NEED_ITEM2, needAmount,  x_items[0].name() )
		return
	c_item = c_items[0]
	if c_item.isFrozen():
		player.statusMessage( csstatus.CIB_MSG_FROZEN )
		return

	player.cell.equipGodWeapon( weaponItem )



def moveItemFromCKToCommon( srcKitbagID, srcOrder ) :
	"""
	神机匣中右键取出物品到普通包裹
	"""
	player = BigWorld.player()
	srcOrderID = srcKitbagID * csdefine.KB_MAX_SPACE + srcOrder       #获得源包裹内物品的全局Order
	srcItem = player.getItem_( srcOrderID )
	stackable = srcItem.getStackable()
	if stackable > 1:
		dstKitbagID = -1
		for kitbagID in csconst.KB_SEARCH_COMMON:
			for dstItem in player.getItemsFKWithBind( srcItem.id, kitbagID, srcItem.isBinded() ):
				if stackable - dstItem.amount < srcItem.amount:
					continue
				dstKitbagID = dstItem.getKitID()
				dstOrderID = dstItem.getOrder()
				dstOrder = dstOrderID % csdefine.KB_MAX_SPACE 		 #根据全局dstOrderID获得物品所在的包裹中的格子号
				break
			if dstKitbagID != -1:
				player.combineItem( srcKitbagID, srcOrder, dstKitbagID, dstOrder )   #对同类可叠加物品进行合并
				return
	orderID = player.getNormalKitbagFreeOrder()
	if orderID != -1:									# 普通包裹还有空位
		dstKitbagID = orderID/csdefine.KB_MAX_SPACE		# 根据order 获得kitbagID
		order = orderID % csdefine.KB_MAX_SPACE         # 根据全局orderID获得当前包裹中的order
		player.moveItem( srcKitbagID, srcOrder, dstKitbagID, order )

def removeCrystal( crystalId ):
	"""
	水晶摘除
	"""
	equips = []
	removeTallys = []
	mItem = {}
	kitCasketItems = getCasketItems( True )
	player = BigWorld.player()
	for item in kitCasketItems:
		if item.isEquip():
			equips += [item]
		else:
			if mItem.has_key( item.id ):
				mItem[item.id] += item.amount
			else:
				mItem[item.id] = item.amount
				removeTallys += [item]
	if len( equips ) == 0:
		player.statusMessage( csstatus.CASKET_PLAEASE_INPUT_EQUIP )
		return False
	elif len( equips ) != 1:
		player.statusMessage( csstatus.CASKET_NEED_ONE_EQUIP_ONLY )
		return False
	equip = equips[0]
	effectList = equip.getBjExtraEffect()
	if len( effectList ) == 0:
		player.statusMessage( csstatus.CASKET_EQUIP_HAVENOT_BESTUDDED )
		return False
	if crystalId <= 0:
		player.statusMessage( csstatus.CASKET_CHOOSE_CRYSTAL )
		return False
	crystal = player.createDynamicItem( crystalId )
	stuff = g_removeCrystal.getStuff()
	if len( removeTallys ) == 0:
		player.statusMessage( csstatus.CASKET_TALLY_WRONG )
		return False
	if ( len( removeTallys ) != 1 or ( mItem not in stuff ) ):			#所有摘除符的id
		player.statusMessage( csstatus.CASKET_TALLY_WRONG_ONLY )
		return False
	elif removeTallys[0].getLevel() < crystal.getLevel():
		player.statusMessage( csstatus.CASKET_TALLY_LEVEL_WRONG )
		return False
	player.lockCasket()
	player.cell.itb_removeCrystal( crystalId )