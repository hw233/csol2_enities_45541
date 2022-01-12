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
		player.statusMessage( csstatus.ROLE_DIE_CANT_ITEM )		# add by ����
	return False

# ------------------------------->
# �����õײ����
# ------------------------------->
def onKitbagItemUpdate( kitbagOrder, itemOrder, itemInstance ):
	"""
	��Ʒ����ĳ����Ʒ�����¼�

	@param  kitbagOrder: �ĸ�����
	@param    itemOrder: ��Ʒ�ڱ����е�λ��
	@param itemInstance: ��Ʒʵ�������ʵƷ����������ΪNone
	"""
	if itemInstance is None:
		fireEvent( "EVT_ON_KITBAG_ITEM_INFO_CHANGED", kitbagOrder, itemOrder, None )
	else:
		itemInfo = ObjectItem( itemInstance )
		fireEvent( "EVT_ON_KITBAG_ITEM_INFO_CHANGED", kitbagOrder, itemOrder, itemInfo )

def onKitbagItemLockChanged( kitbagOrder, itemOrder, isLocked ):
	"""
	��Ʒ����ĳ��λ������״̬�ı�

	@param  kitbagOrder: INT; �ĸ�����
	@param    itemOrder: INT; ��Ʒ�ڱ����е�λ��
	@param     isLocked: BOOL; ��ǰ�Ƿ�Ϊ����״̬
	"""
	fireEvent( "EVT_ON_KITBAG_ITEM_LOCK_CHANGED", kitbagOrder, itemOrder, isLocked )


# ------------------------------->
# Items about
# ------------------------------->
def getKitbagItemDescription( kitbagOrder, itemOrder ):
	"""
	ȡ��ĳ������ĳ��λ�õ���Ʒ��Ϣ
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
	�Զ��жϲ�ʹ����Ʒ

	@param item: ����
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
		if index > len(dsp) - 1: #��ֹindexԽ��
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
		if index > len(dsp) - 1: #��ֹindexԽ��
			index = len(dsp) - 1
		dsp[index].insert(0,[text])
	return dsp

def getWarningVal( ):
	return 0.10

def getAbateval():
	return 0.01

def autoMoveKitbagItem( srcKitTote, srcOrderID, dstKitTote, dstOrderID ):
	"""
	�ƶ�ĳ�����ߵ�ĳ��λ��

	��Ҫ����Դ������Ŀ�걳�����ͣ��п�����Ҫ���ݲ�ͬ����������ͬ�Ĳ���

	@param  srcKitTote: Դ����Ψһ��ʶ
	@type   srcKitTote: INT8
	@param    srcOrder: Դ������Դλ��
	@type     srcOrder: INT8
	@param  dstKitTote: Ŀ�걳��Ψһ��ʶ
	@type   dstKitTote: INT8
	@param    dstOrder: Ŀ�걳����Ŀ��λ�ã�Ŀ��λ�ñ����ǿյ�
	@type     dstOrder: INT8
	"""
	if not __allowOperate() : return

	player = BigWorld.player()
	player.swapItem( srcKitTote, srcOrderID, dstKitTote, dstOrderID )

def destroyKitbagItem( uid ):
	"""
	����һ����Ʒ

	@param     uid: ��Ʒ��ΨһID
	@type      uid: INT64
	"""
	if not __allowOperate() : return
	BigWorld.player().destroyItem( uid )

def splitKitbagItem( uid, amount ):
	"""
	�ֿ�һ���ɵ��ӵĵ��ߡ�

	@param     uid: ��Ʒ��ΨһID
	@type      uid: INT64
	@param      amount: ��ʾ��Դ��Ʒ����ֳ����ٸ���
	@type       amount: UINT16
	"""
	if not __allowOperate() : return
	player = BigWorld.player()
	if player is None : return
	player.splitItem( uid, amount )

def isCooldownType( uid, cooldownType ) :
	"""
	�ж��Ƿ�������ʾ cooldown ����
	uid		����Ʒ��ΨһID
	cooldownType��coolDown ����
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
		# �����Ʒ���ڱ������У���ô����ʾ��wsf
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
# ���ϻ���
def getCasketFuncDsp( funType ):
	"""
	@type funType: int
	"""
	try:
		return casketFuncDsp.Datas[ funType ]
	except:
		ERROR_MSG("Key Error! when funType = ", funType)
		return ""

def getCasketItems( isCrys = False ): # ������ϻ����Ʒ
	player = BigWorld.player()
	items = player.getItems( csdefine.KB_CASKET_ID )
	if isCrys: #�����ˮ��ժ��
		items = [item for item in items if item.getOrder()%csdefine.KB_MAX_SPACE >= csdefine.KB_CASKET_SPACE]
	else:
		items = [item for item in items if item.getOrder()%csdefine.KB_MAX_SPACE < csdefine.KB_CASKET_SPACE]
	return items

# �������ϻ����7�������У����Ϻϳ��ߵ����Ľӿ�
# ��Ϊ��ӿڲ����������Ĳ�һ��
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
# ���Ϻϳ�
# ---------------------------------------------------------------
def stuffComposeCost( baseAmount ):
	"""
	������Ϻϳ����� by����
	@param baseAmount : �ϳɻ���
	@type baseAmount : int
	@param stuff : ���ϵȼ�
	@type stuff : int
	@return int
	"""
#	if not __allowOperate(): return 0
	kitCasketItems = getCasketItems()
	if len( kitCasketItems ) == 0: return 0
	player = BigWorld.player()
	mItems = {}
	levelForCost = 0 #Ϊ������Ǯ����׽����Ʒ�ȼ� by����
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
	���Ϻϳ�
	@param baseAmount: �ϳɻ���
	@type  baseAmount: int
	@return INT
	"""
	if not __allowOperate(): return
	kitCasketItems = getCasketItems()
	if len( kitCasketItems ) == 0: return
	player = BigWorld.player()
	if player.isCasketLocked: return False
	mItems = {}
	levelForCost = 0 #Ϊ������Ǯ����׽����Ʒ�ȼ� by����
	for item in kitCasketItems:
		if mItems.has_key( item.id ):
			mItems[item.id] += item.amount
		else:
			mItems[item.id] = item.amount
		levelForCost = item.getLevel()
	srcItemID = 0										# �ϳ���Ʒ��ID
	additiveInfo = {}
	g_stuff = StuffMergeExp.instance()
	for srcID in mItems:
		if g_stuff.canMerge( srcID ) and mItems[srcID] >= baseAmount:
			srcItemID = srcID
			additiveInfo = g_stuff.getAdditiveInfo( baseAmount, srcID )
			break
	additiveItems = additiveInfo.copy()	# �������Ϊ�˲��ı侲̬���õ�ԭֵ by ����
	lenAdd = len( additiveItems )
	if srcItemID == 0 or lenAdd + 1 != len( mItems ):
		player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return False
	srcAmount = mItems[srcItemID]										# ��Ʒ������
	dstAmount = int( srcAmount / baseAmount )							# ���ϳɵĴ���
	if dstAmount <= 0:
		player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return False
	if lenAdd > 0:
		for additiveItemID in additiveItems:
			if additiveItemID not in mItems or mItems[additiveItemID] < additiveItems[additiveItemID]:
				player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
				return False
	payMoneyStuC = stuffComposeCost( baseAmount )
	if player.money < int(payMoneyStuC):							#�Ƚ�Ǯ �����
		player.statusMessage( csstatus.EQUIP_REPAIR_NOT_ENOUGH_MONEY )
		return False
	if player.state == csdefine.ENTITY_STATE_VEND:
		player.statusMessage( csstatus.CASKET_CANT_USE_WHEN_VEND )
		return False
	player.lockCasket()
	player.cell.stuffCompose( baseAmount )

def stuffBindCheck( isRebuit = False ):
	"""
	���Ϻϳɼ����ϰ��� by ����
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
	���ݲ��Ϻϳɻ�����ȡ�ɹ���
	@param baseAmount: �ϳɻ���
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
	if len( additiveInfo ): #��Ҫ�߻���
		activeID = additiveInfo.keys()[0] #�߻���ID
		if len(mItems) != ( len(additiveInfo) + 1 ) or \
			not activeID in mItems:
				return 0
	else:
		if len(mItems) != ( len(additiveInfo) + 1 ):
			return 0
	return g_stuff.getOdds( baseAmount, srcItemID )

# ---------------------------------------------------------------
# װ�����
# ---------------------------------------------------------------
def getStilettoOdds():
	"""
	����װ�����п�����ȡ�ɹ��� by����
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
	���װ����׻���
	@param tag: ���ϻ��������
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
	return int( 120 * equipLevel * 2 ** ( slotCount - 1 )) #ͬ�������˹�ʽ by����

def equipStiletto():
	"""
	װ�����
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
# װ��ǿ��
# ---------------------------------------------------------------
def getIntensifyCost( tag ):
	"""
	��ȡǿ�������Ǯ by����
	"""
	if len( getCasketItems() ) == 0:return 0
	equips = []			# װ��
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
	���װ��ǿ���ɹ���
	@param tag: ���ϻ��������
	@type  tag: int
	@return Int
	"""
	if len( getCasketItems() ) == 0:return 0

	dragonItems = []	# ����
	luckItems = []		# ���˱�ʯ
	equips = []			# װ��
	g_equipIntensify = EquipIntensifyExp.instance()
	for item in getCasketItems():
		if item.isEquip():
			equips += [item]
		elif g_equipIntensify.isDragonGem( item ):	# �Ƿ�����
			if len( dragonItems ) and dragonItems[0].id != item.id:
				return 0
			dragonItems.append( item )
		elif g_equipIntensify.isLuckGem( item ):	# �Ƿ����˱�ʯ
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

	# ÿһ�������Ӧ30����װ��
	minLevel = g_equipIntensify.getMinLevel( dragonGem.id )
	maxLevel = g_equipIntensify.getMaxLevel( dragonGem.id )
	if equipLevel < minLevel or equipLevel > maxLevel:
		return 0

	intensifyLevel = equip.getIntensifyLevel()
	if intensifyLevel >= csdefine.EQUIP_INTENSIFY_MAX_LEVEL:
		return -1

	# ��ȡ�Ƿ����Ķ�������ǿ���ɹ��ʵ�����ˮ��
	excOdds = 0
	if len( luckItems ):
		excOdds += g_equipIntensify.getExtraOdds( luckItems[0].id )	# ��������ˮ����ö���ɹ���

	odds = g_equipIntensify.getOdds( intensifyLevel + 1 )
	return min( odds + excOdds, 100 )

def equipIntensify():
	"""
	װ��ǿ��
	"""
	if len( getCasketItems() ) == 0:return 0
	g_equipIntensify = EquipIntensifyExp.instance()

	dragonItems = []	# ����
	luckItems = []		# ���˱�ʯ
	equips = []			# װ��
	player = BigWorld.player()
	for item in getCasketItems():
		if item.isEquip():
			equips += [item]
		elif g_equipIntensify.isDragonGem( item ):	# �Ƿ�����
			if len( dragonItems ) and dragonItems[0].id != item.id:
				player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
				return False
			dragonItems.append( item )
		elif g_equipIntensify.isLuckGem( item ):	# �Ƿ����˱�ʯ
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

	# �ж�װ���Ƿ��ǿ��
	if not equip.canIntensify():
		player.statusMessage( csstatus.CASKET_INTENSIFY_NO_SUPPORT )
		return False

	# ÿһ�������Ӧ30����װ��
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
	if player.money < int(intensifyCost):							#�Ƚ�Ǯ �����
		player.statusMessage( csstatus.EQUIP_REPAIR_NOT_ENOUGH_MONEY )
		return False
	return True

def equipInteBindCheck( isRebuit = False ):
	"""
	װ��ǿ�������ϰ��� by ����
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
# װ������
# ---------------------------------------------------------------
def getEquipRebuildCost( tag, isRebuild = False ):
	"""
	��ȡװ���������ķѵĽ�Ǯ
	ע��,�ú���ֻ�Ǽ򵥵Ĵ����ϻ��ȡ��һ����ɫװ�������Ű��չ�ʽ
	��������ĵĽ�Ǯ��û�н����ܷ�ɹ��ϳɵ��жϣ������ʹ��ʱӦ���ȵ���
	�ϳɼ��ʼ��㺯����getEquipRebuildOdds����ȡ�����жϺ��ٵ��ô˺�����
	@param tag: ���ϻ��������
	@type  tag: int
	@return Int
	"""
	kitCasketItems = getCasketItems()
	if len( kitCasketItems ) == 0: return 0
	player = BigWorld.player()
	wEquips = []
	qEquips = []
	for item in kitCasketItems:
		# ��������ϻ�����ж��ټ�װ��
		# ֻ����һ����ɫװ���������ǰ�ɫ��ͬƷ��װ��
		# ���ܽ��и���
		if not item.isEquip():
			return 0
		if item.isWhite():
			wEquips.append( item )
		else:
			qEquips.append( item )
	# �ж������װ�������Ƿ�ϸ�
	if len( wEquips ) != 1 or len( qEquips ) != 2:
		return 0
	wEquip = wEquips[0]
	qEquip1 = qEquips[0]
	qEquip2 = qEquips[1]
	# װ�����ͱ���һ�£�������ߺ�����һ���޷��ϳ�  2008-10-28 gjx
	maskCode = 0x030000 # װ�������ж�����
	if wEquip.getType() & maskCode == ItemTypeEnum.ITEM_WEAPON:		# ����
		if qEquip1.getType() & maskCode != ItemTypeEnum.ITEM_WEAPON:
			return 0
		elif qEquip2.getType() & maskCode != ItemTypeEnum.ITEM_WEAPON:
			return 0
	elif wEquip.getType() & maskCode == ItemTypeEnum.ITEM_ARMOR:	# ����
		if qEquip1.getType() & maskCode != ItemTypeEnum.ITEM_ARMOR :
			return 0
		elif qEquip2.getType() & maskCode != ItemTypeEnum.ITEM_ARMOR :
			return 0
	elif wEquip.getType() & maskCode == ItemTypeEnum.ITEM_ORNAMENT:	# ����
		if qEquip1.getType() & maskCode != ItemTypeEnum.ITEM_ORNAMENT :
			return 0
		elif qEquip2.getType() & maskCode != ItemTypeEnum.ITEM_ORNAMENT :
			return 0
	else:
		return 0
	# װ���ȼ�����
	if wEquip.getLevel() < 20 or qEquip1.getLevel() < 20 or qEquip2.getLevel() < 20:
		return 0
	# �ж������װ���Ƿ���ͬһ�ȼ���
	if not qEquip1.getLevel()/10 == qEquip2.getLevel()/10 == wEquip.getLevel()/10:
		return 0
	# �ж������װ��Ʒ���Ƿ�ϸ�
	if qEquip1.getQuality() != qEquip2.getQuality():
		return False
	if isRebuild:
		if wEquip.isBinded() and qEquip1.isBinded() and qEquip2.isBinded():
			return 0
		elif wEquip.isBinded() or qEquip1.isBinded() or qEquip2.isBinded():
			return 0
	# �ж�money������
	#ͬ���޸���Ǯ��ʽ by����
	money = 0
	lvm = qEquip1.getLevel()
	if lvm > 0 and lvm <= 50:    #1~50 1.1^���ߵȼ�*100*Ʒ��/3
		money = 1.1 ** lvm * 100 * qEquip1.getQuality() /3
	else:           #51~150 1.03^���ߵȼ�*2700 *Ʒ��/3
		money = 1.03 ** lvm * 2700 * qEquip1.getQuality() /3
	return int( money )

def getEquipRebuildOdds( tag ):
	"""
	��ȡװ������ɹ���
	@param tag: ���ϻ��������
	@type  tag: int
	@return Int
	"""
	kitCasketItems = getCasketItems()
	if len( kitCasketItems ) == 0: return 0
	player = BigWorld.player()
	wEquips = []
	qEquips = []
	for item in kitCasketItems:
		# ��������ϻ�����ж��ټ�װ��
		# ֻ����һ����ɫװ���������ǰ�ɫ��ͬƷ��װ��
		# ���ܽ��и���
		if not item.isEquip():
			return 0
		if item.isWhite():
			wEquips.append( item )
		else:
			qEquips.append( item )

	# �ж������װ�������Ƿ�ϸ�
	if len( wEquips ) != 1 or len( qEquips ) != 2:
		return 0

	wEquip = wEquips[0]
	qEquip1 = qEquips[0]
	qEquip2 = qEquips[1]

	# װ�����ͱ���һ�£�������ߺ�����һ���޷��ϳ�  2008-10-28 gjx
	maskCode = 0x030000 # װ�������ж�����
	if wEquip.getType() & maskCode == ItemTypeEnum.ITEM_WEAPON:		# ����
		if qEquip1.getType() & maskCode != ItemTypeEnum.ITEM_WEAPON:
			return 0
		elif qEquip2.getType() & maskCode != ItemTypeEnum.ITEM_WEAPON:
			return 0
	elif wEquip.getType() & maskCode == ItemTypeEnum.ITEM_ARMOR:	# ����
		if qEquip1.getType() & maskCode != ItemTypeEnum.ITEM_ARMOR :
			return 0
		elif qEquip2.getType() & maskCode != ItemTypeEnum.ITEM_ARMOR :
			return 0
	elif wEquip.getType() & maskCode == ItemTypeEnum.ITEM_ORNAMENT:	# ����
		if qEquip1.getType() & maskCode != ItemTypeEnum.ITEM_ORNAMENT :
			return 0
		elif qEquip2.getType() & maskCode != ItemTypeEnum.ITEM_ORNAMENT :
			return 0
	else:
		return 0

	# װ���ȼ�����
	if wEquip.getLevel() < 20 or qEquip1.getLevel() < 20 or qEquip2.getLevel() < 20:
		return 0

	# �ж������װ���Ƿ���ͬһ�ȼ���
	if not qEquip1.getLevel()/10 == qEquip2.getLevel()/10 == wEquip.getLevel()/10:
		return 0

	# �ж������װ��Ʒ���Ƿ�ϸ�
	if qEquip1.getQuality() != qEquip2.getQuality():
		return 0

	return 100

def getEquipImproveOdds( ):
	"""
	��ȡ��װ��Ʒ�ɹ���
	"""
	kitCasketItems = getCasketItems()
	badgeItems = []			#����
	equip = None				#װ��
	needBind = False
	player = BigWorld.player()
	for item in kitCasketItems:
		if item.isFrozen():		#���������Ʒ���ܱ����ϻʹ��
			return 0
		if item.isEquip():
			if equip != None and equip.id != item.id:
				return 0
			equip = item
		elif g_equipImproveQuality.isBadge( item ):		#�Ƿ��ǻ���
			if len( badgeItems ) and badgeItems[0].id != item.id:
				return 0
			badgeItems.append( item )
		else:
			return 0
	if equip == None:
		return 0
	#�ж��Ƿ��л���
	if len( badgeItems ) == 0:
		return 0
	badgeItem = badgeItems[0]
	if equip.isGreen() == False:
		return 0
	equipLevel = equip.getReqLevel()
	minLevel = 90			#��Ʒ��͵ȼ�
	maxLevel = 149			#��Ʒ��ߵȼ�
	if equipLevel < minLevel or equipLevel > maxLevel:
		return 0
	if equip.isBinded() or badgeItem.isBinded():
		needBind = True
	equipPrefix = equip.getPrefix()
	odds=g_equipImproveQuality.getOdds( badgeItem.id , equipPrefix )
	return odds

def equipBindCheck( isRebuild = False ):
	"""
	���װ���ϳɲ������Ƿ����Ѱ󶨵�װ�� by����
	@type isRebuild		: bool
	@param isRebuild	: �Ƿ�����equipRebuild���� �ⶫ���ǻ����ж����������
	"""
	kitCasketItems = getCasketItems()
	if len( kitCasketItems ) == 0: return False
	player = BigWorld.player()
	wEquips = []
	qEquips = []
	for item in kitCasketItems:
		# ��������ϻ�����ж��ټ�װ��
		# ֻ����һ����ɫװ���������ǰ�ɫ��ͬƷ��װ��
		# ���ܽ��и���
		if not item.isEquip():
			player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
		if item.isWhite():
			wEquips.append( item )
		else:
			qEquips.append( item )

	# �ж������װ�������Ƿ�ϸ�
	if len( wEquips ) != 1 or len( qEquips ) != 2:
		player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return False

	wEquip = wEquips[0]
	qEquip1 = qEquips[0]
	qEquip2 = qEquips[1]

	# װ�����ͱ���һ�£�������ߺ�����һ���޷��ϳ�  2008-10-28 gjx
	maskCode = 0x030000 # װ�������ж�����
	if wEquip.getType() & maskCode == ItemTypeEnum.ITEM_WEAPON:		# ����
		if qEquip1.getType() & maskCode != ItemTypeEnum.ITEM_WEAPON:
			player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
		elif qEquip2.getType() & maskCode != ItemTypeEnum.ITEM_WEAPON:
			player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
	elif wEquip.getType() & maskCode == ItemTypeEnum.ITEM_ARMOR:	# ����
		if qEquip1.getType() & maskCode != ItemTypeEnum.ITEM_ARMOR :
			player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
		elif qEquip2.getType() & maskCode != ItemTypeEnum.ITEM_ARMOR :
			player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
	elif wEquip.getType() & maskCode == ItemTypeEnum.ITEM_ORNAMENT:	# ����
		if qEquip1.getType() & maskCode != ItemTypeEnum.ITEM_ORNAMENT :
			player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
		elif qEquip2.getType() & maskCode != ItemTypeEnum.ITEM_ORNAMENT :
			player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
	else:
		player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return False

	# װ���ȼ�����
	if wEquip.getLevel() < 20 or qEquip1.getLevel() < 20 or qEquip2.getLevel() < 20:
		player.statusMessage( csstatus.CASKET_CANT_REBUILD_LEVEL_LIMIT )
		return False

	# �ж������װ���Ƿ���ͬһ�ȼ���
	if not qEquip1.getLevel()/10 == qEquip2.getLevel()/10 == wEquip.getLevel()/10:
		player.statusMessage( csstatus.CASKET_CANT_REBUILD_DLEVEL_EQUIP )
		return False

	# �ж������װ��Ʒ���Ƿ�ϸ�
	if qEquip1.getQuality() != qEquip2.getQuality():
		player.statusMessage( csstatus.CASKET_CANT_REBUILD_QUALITY_WRONG )
		return False

	if isRebuild:
		if wEquip.isBinded() and qEquip1.isBinded() and qEquip2.isBinded():
			return False
		elif wEquip.isBinded() or qEquip1.isBinded() or qEquip2.isBinded():
			return True

	# �ж�money������
	#money = ( qEquip1.getLevel() + qEquip2.getLevel() ) * 25
	#money = int( math.ceil( wEquip.getLevel() ** 2.5 * 0.6 ) ) # ���Ľ�Ǯ���¼��㹫ʽ gjx 2008-10-28
	#ͬ���޸���Ǯ��ʽ by����
	lvm = qEquip1.getLevel()
	if lvm > 0 and lvm <= 50:    #1~50 1.1^���ߵȼ�*100*Ʒ��/3
		money = 1.1 ** lvm * 100 * qEquip1.getQuality() /3
	else:           #51~150 1.03^���ߵȼ�*2700 *Ʒ��/3
		money = 1.03 ** lvm * 2700 * qEquip1.getQuality() /3
	if player.money < int(money):
		player.statusMessage( csstatus.CASKET_BIND_NEED_MONEY )
	return False

def equipRebuild():
	"""
	װ������
	"""
	equipBindCheck()
	return True
# ---------------------------------------------------------------
# װ������
# ---------------------------------------------------------------
def getSmeltOdds( tag ):
	"""
	@param tag: ���ϻ��������
	@type  tag: int
	@return Int
	"""
	pass

# ---------------------------------------------------------------
# װ�����
# ---------------------------------------------------------------
def equipSplit():
	"""
	װ�����
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
	if not equip.isEquip():	#����װ��
		player.statusMessage( csstatus.CASKET_ITEM_CANT_BE_SPLITED )
		return False
	if equip.isWhite():	#��װ���ܲ��
		if Language.LANG == Language.LANG_GBK:
			player.statusMessage( csstatus.CASKET_EQUIP_CANNOT_SPLIT )
		elif Language.LANG == Language.LANG_BIG5:
			player.statusMessage( csstatus.CASKET_EQUIP_CANNOT_SPLIT_BIG5 )
		return False
	payMoney = int( 0.3 * equip.getLevel() ** 1.5 * equip.getQuality() )
	if player.money < int(payMoney):	#���Ǯ����
		player.statusMessage( csstatus.CASKET_SPLIT_PAY_FAILD )
		return False
	return True

def getSplitExpense():
	"""
	��ȡװ����ֵĻ���
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
		if not equip.isEquip():	#����װ��
#			player.statusMessage( csstatus.CASKET_EQUIP_SPLIT_AMOUNT_ERROR )
			payMoney = 0
		if equip.isWhite():	#��װ���ܲ��
#			player.statusMessage( csstatus.CASKET_EQUIP_CANNOT_SPLIT )
			payMoney = 0
		payMoney = int( 0.3 * equip.getLevel() ** 1.5 * equip.getQuality() ) #����ͬ���޸��˻��ѹ�ʽ
	return int(payMoney)
# ---------------------------------------------------------------
# װ����Ƕ
# ---------------------------------------------------------------

def equipStudded():
	"""
	װ����Ƕ
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
		# һ������ˮ��ֻ��Ƕһ�� by����
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
	װ����Ƕ�����ϵİ����� by����
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
# װ����  ��Ϊװ������ by����
# ---------------------------------------------------------------
def getBindCost( tag ):
	"""
	��ȡװ����������
	@param tag: ���ϻ��������
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
	#ͬ��װ��������ʽ�޸� by����
	lvm = equip.getLevel()
	if lvm > 0 and lvm <= 50:    #1~50 1.1^���ߵȼ�*100*Ʒ��/3
		money = 1.1 ** lvm * 100 * equip.getQuality() /3
	else:           #51~150 1.03^���ߵȼ�*2700 *Ʒ��/3
		money = 1.03 ** lvm * 2700 * equip.getQuality() /3
	return int(money)

def equipBind():
	"""
	װ������
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
	# ���벻��������װ�������ж� by����
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
	#ͬ��װ��������ʽ�޸� by����
	lvm = equip.getLevel()
	if lvm > 0 and lvm <= 50:    #1~50 1.1^���ߵȼ�*100*Ʒ��/3
		money = 1.1 ** lvm * 100 * equip.getQuality() /3
	else:           #51~150�� 1.03^���ߵȼ�*2700 *Ʒ��/3
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
	����ϳ��շ� by����
	"""
	return rds.specialCompose.getRequireMoney()

def specialCompose():
	"""
	����ϳ�
	@return Bool
	"""
	specom = rds.specialCompose
	#���ݾ���ID��ò��ϡ�Ŀ����Ʒ������
	bindResult= specom.getIsBind( scrollID )  #���ɵ���Ʒ�Ƿ��
	money     = specom.getRequireMoney( scrollID ) #���ĵĽ�Ǯ
	dstItemID = specom.getDstItemID( scrollID )  #Ŀ����ƷID
	dstAmount = specom.getDstItemCount( scrollID )  #Ŀ����Ʒ������
	mItems    = specom.getMaterials( scrollID ) #�ϳɲ��ϼ�������
	p = BigWorld.player()
	if p.__class__.__name__ != "PlayerRole":return False
	#-----------------�ж������Ƿ����----------------
	if not dstItemID:return False
	if not dstAmount:return False
	if not mItems:return False
	
	#------------------�жϱ�����λ-------------------
	orderIDs = p.getAllNormalKitbagFreeOrders()
	if len( orderIDs ) < dstAmount :
		p.statusMessage( csstatus.CASKET_EQUIP_SPECIAL_COMPOSE_NO_SPACE )
		return False
	
	#------------------�жϱ������Ƿ�������в���--------------
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

def talismanFix(): #�����޸�
	talismanItems = []
	lifeItems = []
	player = BigWorld.player()
	kitCasketItems = player.getItems( csdefine.KB_CASKET_ID )
	for item in kitCasketItems:
		if item.isFrozen():		#���������Ʒ���ܱ����ϻʹ��
			player.statusMessage( csstatus.CASKET_CANT_VENDSTATE )
			return False
		if item.id == csconst.TALISMAN_ADD_LIFE_ITEM:
			lifeItems.append( item )
		elif item.getType() == ItemTypeEnum.ITEM_SYSTEM_TALISMAN:
			talismanItems.append( item )
		else:
			# ֻ�ܷ��뷨����Ů�ʯ
			player.statusMessage( csstatus.TALISMAN_ADDLIFE_NEED_TANDN )
			return False

	talismanCount = len( talismanItems )
	if talismanCount == 0:
		# �������Ҫ��ֵ�ķ���
		player.statusMessage( csstatus.TALISMAN_ADDLIFE_NEED_TAl )
		return False
	if talismanCount > 1:
		# һ��ֻ�ܸ�һ��������ֵ
		player.statusMessage( csstatus.TALISMAN_ADDLIFE_ONCE )
		return False

	if not talismanItems[0].isActiveLifeTime():
		# ����δ����
		player.statusMessage( csstatus.TALISMAN_NOT_ACTIVE )
		return False

	if len( lifeItems ) == 0:
		# �����Ů�ʯ
		player.statusMessage( csstatus.TALISMAN_ADDLIFE_NEED_NWS )
		return False
	lifeCount = sum([item.amount for item in lifeItems])
	addTime = Const.TALISMAN_ADD_LIFE_TIME * lifeCount
	if addTime <= 0: return False
	player.cell.addTalismanLife()
	return True

def talismanSplitCheck():
	"""
	�����ֽ� ���Լ�� by ����
	"""
	kitCasketItems = getCasketItems()
	if len(kitCasketItems) != 1:
		return False
	talismanItem = kitCasketItems[0]
	if talismanItem.isFrozen() or \
		talismanItem.getType() != ItemTypeEnum.ITEM_SYSTEM_TALISMAN or \
		not talismanItem.isBinded():		#���������Ʒ���ܱ����ϻʹ��
		return False
	return True

def getTaliSplitCost( item = None ):
	"""
	��ȡ�����ֽ����
	"""
	talismanItem = None
	if item is None:
		kitCasketItems = getCasketItems()
		if len(kitCasketItems) != 1:
			return 0
		talismanItem = kitCasketItems[0]
		if talismanItem.isFrozen() or \
			talismanItem.getType() != ItemTypeEnum.ITEM_SYSTEM_TALISMAN:		#���������Ʒ���ܱ����ϻʹ��
			return 0
	else:
		talismanItem = item
	grade = talismanItem.getGrade()
	return talismanSplitExp.getSplitCost( grade )

def talismanSplit():
	"""
	�����ֽ� by ����
	"""
	kitCasketItems = getCasketItems()
	player = BigWorld.player()
	if len(kitCasketItems) != 1:
		player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return False
	talismanItems = kitCasketItems[0]
	if talismanItems.isFrozen():		#���������Ʒ���ܱ����ϻʹ��
		player.statusMessage( csstatus.CASKET_CANT_VENDSTATE )
		return False
	if talismanItems.getType() != ItemTypeEnum.ITEM_SYSTEM_TALISMAN:		# ֻ�ܷ��뷨��
		player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return False
	payMoney = getTaliSplitCost( talismanItems )
	if player.money < int(payMoney):	#���Ǯ����
		player.statusMessage( csstatus.CASKET_SPLIT_PAY_FAILD )
		return False
	return True

def getTaliInstCost():
	"""
	��ȡ����ǿ������
	"""
	return 0

def talismanIntensifyCheck():
	"""
	����ǿ�� ���Լ�� by ����
	"""
	kitCasketItems = getCasketItems()
	g_equipIntensify = EquipIntensifyExp.instance()
	for item in kitCasketItems:
		if item.id == csconst.TALISMAN_ADD_LIFE_ITEM and item.isBinded():	# Ů�ʯ
			return True
		elif item.getType() == ItemTypeEnum.ITEM_SYSTEM_TALISMAN and item.isBinded():	# ����
			return True
		elif g_equipIntensify.isLuckGem( item ) and item.isBinded():	# �Ƿ����˱�ʯ
			return True
	return False

def talismanIntensifyOdd():
	"""
	����ǿ���ɹ���
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
		if item.isFrozen():		#���������Ʒ���ܱ����ϻʹ��
			return 0
		if item.id == csconst.TALISMAN_ADD_LIFE_ITEM:	# Ů�ʯ
			lifeItems.append( item )
		elif item.getType() == ItemTypeEnum.ITEM_SYSTEM_TALISMAN:	# ����
			talismanItems.append( item )
		elif g_equipIntensify.isLuckGem( item ):	# �Ƿ����˱�ʯ
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
		excOdds = g_equipIntensify.getExtraOdds( luckItem.id )	# ��������ˮ����ö���ɹ���
	odds = g_equipIntensify.getOdds( intensifyLevel + 1 )
	return odds + excOdds

def talismanIntensify():
	"""
	����ǿ�� by ����
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
		if item.isFrozen():		#���������Ʒ���ܱ����ϻʹ��
			player.statusMessage( csstatus.CASKET_CANT_VENDSTATE )
			return False
		if item.id == csconst.TALISMAN_ADD_LIFE_ITEM:	# Ů�ʯ
			lifeItems.append( item )
		elif item.getType() == ItemTypeEnum.ITEM_SYSTEM_TALISMAN:	# ����
			talismanItems.append( item )
		elif g_equipIntensify.isLuckGem( item ):	# �Ƿ����˱�ʯ
			luckeyItems.append( item )
		else:
			player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )	# ֻ�ܷ��뷨����Ů�ʯ��������ʯ
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
	װ��ϴǰ׺
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
	��װ��Ʒ
	"""
	kitCasketItems = getCasketItems()
	badgeItems = []			#����
	equip = None				#װ��
	needBind = False
	player = BigWorld.player()
	for item in kitCasketItems:
		if item.isFrozen():		#���������Ʒ���ܱ����ϻʹ��
			player.statusMessage(csstatus.CASKET_CANT_VENDSTATE)
			return False
		if item.isEquip():
			if equip != None and equip.id != item.id:
				player.statusMessage( csstatus.CASKET_NEED_ONE_EQUIP_ONLY )
				return False
			equip = item
		elif g_equipImproveQuality.isBadge( item ):		#�Ƿ��ǻ���
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
	#�ж��Ƿ��л���
	if len( badgeItems ) == 0:
		player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
		return False
	badgeItem = badgeItems[0]
	if equip.isGreen() == False:
		player.statusMessage( csstatus.CASKET_EQUIP_CANNOT_IMPROVE_BIG5 )
		return False
	equipLevel = equip.getReqLevel()
	minLevel = 90			#��Ʒ��͵ȼ�
	maxLevel = 149			#��Ʒ��ߵȼ�
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
		csdefine.CASKET_FUC_EQUIPINTENSIFY	: equipIntensify,	# װ��ǿ��
		csdefine.CASKET_FUC_EQUIPREBUILD	: equipRebuild, 	# װ������
		csdefine.CASKET_FUC_EQUIPSTUDDED	: equipStudded,		# װ����Ƕ
		csdefine.CASKET_FUC_EQUIPSTILETTO	: equipStiletto, 	# װ�����
		#csdefine.CASKET_FUC_EQUIPSMELT		: equipSmelt, 		# װ������
		csdefine.CASKET_FUC_EQUIPSPLIT		: equipSplit, 		# װ�����
		csdefine.CASKET_FUC_EQUIPBIND		: equipBind, 		# װ������
		csdefine.CASKET_FUC_SPECIALCOMPOSE  : specialCompose,	# ����ϳ�
		csdefine.CASKET_FUC_TALISMANFIX		: talismanFix,		# �����޸�
		csdefine.CASKET_FUC_TALISMAN_SPLIT	: talismanSplit,	# �����ֽ�
		csdefine.CASKET_FUC_TALISMAN_INS	: talismanIntensify,	# ����ǿ��
		csdefine.CASKET_FUC_CHANGEPROPERTY	: changePropertyPrefix,#װ��ϴǰ׺
		csdefine.CASKET_FUC_IMPROVEQUALITY  : equipImproveQuality, #��װ��Ʒ

		}

def equipGodWeapon( weaponItem ):
	"""
	��������
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
	c_item_id = stuffs[0]	# ��������ƷID
	x_item_id = stuffs[1]	# ����ʯ��ƷID
	c_items = player.findItemsByIDFromNKCK( c_item_id )
	if len( c_items ) <= 0:
		player.statusMessage( csstatus.GW_MAKE_NEED_ITEM, gbref.rds.itemsDict.id2name( c_item_id ) )
		return
	x_items = player.findItemsByIDFromNKCK( x_item_id )
	needAmount = stuffs[2]	# ��������ʯ����
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
	���ϻ���Ҽ�ȡ����Ʒ����ͨ����
	"""
	player = BigWorld.player()
	srcOrderID = srcKitbagID * csdefine.KB_MAX_SPACE + srcOrder       #���Դ��������Ʒ��ȫ��Order
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
				dstOrder = dstOrderID % csdefine.KB_MAX_SPACE 		 #����ȫ��dstOrderID�����Ʒ���ڵİ����еĸ��Ӻ�
				break
			if dstKitbagID != -1:
				player.combineItem( srcKitbagID, srcOrder, dstKitbagID, dstOrder )   #��ͬ��ɵ�����Ʒ���кϲ�
				return
	orderID = player.getNormalKitbagFreeOrder()
	if orderID != -1:									# ��ͨ�������п�λ
		dstKitbagID = orderID/csdefine.KB_MAX_SPACE		# ����order ���kitbagID
		order = orderID % csdefine.KB_MAX_SPACE         # ����ȫ��orderID��õ�ǰ�����е�order
		player.moveItem( srcKitbagID, srcOrder, dstKitbagID, order )

def removeCrystal( crystalId ):
	"""
	ˮ��ժ��
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
	if ( len( removeTallys ) != 1 or ( mItem not in stuff ) ):			#����ժ������id
		player.statusMessage( csstatus.CASKET_TALLY_WRONG_ONLY )
		return False
	elif removeTallys[0].getLevel() < crystal.getLevel():
		player.statusMessage( csstatus.CASKET_TALLY_LEVEL_WRONG )
		return False
	player.lockCasket()
	player.cell.itb_removeCrystal( crystalId )