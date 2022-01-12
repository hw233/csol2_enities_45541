# -*- coding: gb18030 -*-
#

"""
"""
import Math
import time
import random

import BigWorld
from bwdebug import *
import csdefine
import csstatus
import csconst
import ItemTypeEnum
import ChatObjParser
import Function

import cschannel_msgs

from ItemSystemExp import StuffMergeExp
from ItemSystemExp import EquipIntensifyExp
from ItemSystemExp import EquipStuddedExp
from ItemSystemExp import EquipBindExp
from ItemSystemExp import EquipMakeExp
from ItemSystemExp import EquipQualityExp
from ItemSystemExp import SpecialComposeExp
from ItemSystemExp import EquipSplitExp
from ItemSystemExp import RemoveCrystalExp
from ItemSystemExp import TalismanExp
from ItemSystemExp import EquipGodWeaponExp
from ItemSystemExp import ChangePropertyExp
from ItemSystemExp import EquipImproveQualityExp
from ItemSystemExp import SpecialStuffComposeExp
from ItemSystemExp import EquipAttrExp
from config.item.EquipEffects import serverDatas

g_stuff = StuffMergeExp.instance()
g_equipMake = EquipMakeExp.instance()
equipGodExp = EquipGodWeaponExp.instance()
g_equipIntensify = EquipIntensifyExp.instance()
g_equipStuff = EquipStuddedExp.instance()
equipSplitExp = EquipSplitExp.instance()
g_equipBind = EquipBindExp.instance()
g_removeCrystal = RemoveCrystalExp.instance()
g_equipQuality = EquipQualityExp.instance()
specom = SpecialComposeExp.instance()
talismanSplitExp = TalismanExp.instance()
g_changeProperty = ChangePropertyExp.instance()
g_equipImproveQuality = EquipImproveQualityExp.instance()
g_stuffComp = SpecialStuffComposeExp.instance()

import Const
from Love3 import g_itemsDict as g_items
from items.TalismanEffectLoader import TalismanEffectLoader
g_talisman = TalismanEffectLoader.instance()
from items.EquipEffectLoader import EquipEffectLoader
g_equipEffect = EquipEffectLoader.instance()
g_itemPropAttrExp = EquipAttrExp.instance()

from MsgLogger import g_logger

class ItemBagSpecialInterface:
	"""
	"""
	def __init__( self ):
		"""
		初始化状态。
		"""
		pass

	def doCasketFucntionInterface( self, functionIndex ):
		"""
		# 执行神机匣功能
		@param functionIndex: 神机匣功能索引
		@type  functionIndex: UINT8
		"""
		if  self.getState() == csdefine.ENTITY_STATE_VEND:
			self.statusMessage( csstatus.CASKET_FORBID_USED_IN_VENDING )
			return

		if self.iskitbagsLocked():	# 背包上锁，by姜毅
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return
		try:
			kitCasketItem = self.kitbags[csdefine.KB_CASKET_ID]
		except KeyError:
			ERROR_MSG( "src(%i) Can't find kitCasket in kitbag %s" % ( self.id, csdefine.KB_CASKET_ID ) )
			return
		useDegree = kitCasketItem.getUseDegree()	#获得神机匣的使用次数
		if useDegree <= 0:
			self.statusMessage( csstatus.CASKET_CANT_USE )
			DEBUG_MSG( "(%s):kitCasket has been used out." % self.getName() )
			return
		fucAggregate = {
							csdefine.CASKET_FUC_EQUIPSTILETTO	:	self.equipStiletto,
							csdefine.CASKET_FUC_EQUIPSPLIT		:	self.equipSplit,
							csdefine.CASKET_FUC_EQUIPSTUDDED	:	self.equipStudded,
#							csdefine.CASKET_FUC_EQUIPINTENSIFY	:	self.equipIntensify,
							csdefine.CASKET_FUC_EQUIPREBUILD	:	self.equipRebuild,
#							csdefine.CASKET_FUC_EQUIPBIND		:	self.equipBind,
							#csdefine.CASKET_FUC_SPECIALCOMPOSE	:	self.specialCompose,
							csdefine.CASKET_FUC_TALISMANFIX		:	self.addTalismanLife,
							csdefine.CASKET_FUC_TALISMAN_SPLIT	:	self.talismanSplit,	# 法宝分解
							csdefine.CASKET_FUC_TALISMAN_INS	:	self.talismanInstensify,	# 法宝强化
							csdefine.CASKET_FUC_CHANGEPROPERTY	:	self.itb_changePropertyPrefix,
							csdefine.CASKET_FUC_IMPROVEQUALITY	:	self.equipImproveQuality,	#绿装升品
							}
		if fucAggregate[functionIndex]():
			# 做神机匣次数减少的处理
			useDegree -= 1
			kitCasketItem.setUseDegree( useDegree )
			self.client.onUpdateUseDegree( useDegree )
		self.client.unLockCasket()

	def stuffComposeCost( self, baseAmount, itemID ):
		"""
		计算材料合成消费 by姜毅
		"""
		cost = g_stuff.getPrice( baseAmount, itemID )
		return cost

	def stuffComposeInterface( self, baseAmount ):
		"""
		@param baseAmount: 合成基数
		@type  baseAmount: int
		@return Bool
		"""
		# 材料合成说明：在当前神机匣里的所有物品为合成来源对象
		# 必须所有物品种类和数量 完全符合合成公式才允许合成
		# 否则合成不能进行
		if self.getState() == csdefine.ENTITY_STATE_VEND:
			self.statusMessage( csstatus.CASKET_FORBID_USED_IN_VENDING )
			return False
		if not csdefine.KB_CASKET_ID in self.kitbags:
			ERROR_MSG( "src(%i) Can't find kitCasket in kitbag %s" % ( self.id, csdefine.KB_CASKET_ID ) )
			self.client.unLockCasket()
			return False

		kitCasket = self.kitbags[csdefine.KB_CASKET_ID]
		useDegree = kitCasket.getUseDegree()								# 获取神机匣的使用次数
		if useDegree <= 0:
			# 神机匣使用次数为零
			self.client.unLockCasket()
			self.statusMessage( csstatus.CASKET_CANT_USE )
			return False
		if self.getFreeOrderFK( csdefine.KB_CASKET_ID ) == -1:
			# 背包至少要有一个空位
			self.client.unLockCasket()
			self.statusMessage( csstatus.CASKET_CANT_NEED_SPACE )
			return False

		kitCasketItems = self.getCasketItems()				# 神机匣内所有物品
		if len( kitCasketItems ) == 0:
			self.client.unLockCasket()
			return False		# 没有物品
		mItems = {}															# { ID：数量 }
		dstBinded = False
		for item in kitCasketItems:
			if item.isBinded(): dstBinded = True
			if item.isFrozen():
				self.client.unLockCasket()
				self.statusMessage( csstatus.CASKET_CANT_VENDSTATE )
				return False
			if mItems.has_key( item.id ):
				mItems[item.id] += item.amount
			else:
				mItems[item.id] = item.amount
		srcItemID = 0										# 合成物品的ID
		additiveInfo = {}
		for srcID in mItems:
			if g_stuff.canMerge( srcID ) and mItems[srcID] >= baseAmount:
				srcItemID = srcID
				additiveInfo = g_stuff.getAdditiveInfo( baseAmount, srcID )
				break
		additiveItems = additiveInfo.copy()	# 多个对象为了不改变静态配置的原值 by 姜毅

		lenAdd = len( additiveItems )
		if srcItemID == 0 or lenAdd + 1 != len( mItems ):
			self.client.unLockCasket()
			self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
		srcAmount = mItems[srcItemID]										# 物品的数量
		dstAmount = int( srcAmount / baseAmount )							# 最大合成的次数
		if dstAmount <= 0:
			self.client.unLockCasket()
			self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
		if lenAdd > 0:
			for additiveItemID in additiveItems:
				if additiveItemID not in mItems or mItems[additiveItemID] < additiveItems[additiveItemID]:
					self.client.unLockCasket()
					self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
					return False
			isBreak = False
			for d in xrange(1, dstAmount + 1):
				for additiveItemID in additiveItems:
					if additiveItems[additiveItemID] * d > mItems[additiveItemID]:
						isBreak = True
						break
				if isBreak:
					break
				dstAmount = d
		# 消耗计算
		if dstAmount > useDegree: dstAmount = useDegree						# 生成材料的个数
		# 材料合成要收费啦 by姜毅
		payMoneyStuC = int(self.stuffComposeCost( baseAmount, srcItemID ) * dstAmount)
		if not self.payMoney( payMoneyStuC, csdefine.CHANGE_MONEY_STUFFCOMPOSE ):	#先交钱 后提货
			self.client.unLockCasket()
			self.statusMessage( csstatus.EQUIP_REPAIR_NOT_ENOUGH_MONEY )
			return False

		needAmount = dstAmount * baseAmount									# 需要材料的个数
		for additiveItemID in additiveItems:										# 需要添加物个数
				additiveItems[additiveItemID] *= dstAmount
		useDegree = useDegree - dstAmount										# 神机匣使用次数处理
		kitCasket.setUseDegree( useDegree )
		self.client.onUpdateUseDegree( useDegree )
		# 去掉使用的材料
		for srcItem in kitCasketItems:
			if srcItem.id != srcItemID: continue
			srcAmount = srcItem.getAmount()
			if needAmount > srcAmount:
				# 如果需要的数量大于它的数量，那么全部销毁它
				needAmount = needAmount - srcAmount
				self.removeItem_( srcItem.getOrder(), reason = csdefine.DELETE_ITEM_STUFFCOMPOSE )
			else:
				self.removeItem_( srcItem.getOrder(), needAmount, csdefine.DELETE_ITEM_STUFFCOMPOSE )
				needAmount = 0
				break
		# 去掉添加剂 by 姜毅
		if lenAdd > 0:
			for srcItem in kitCasketItems:
				if srcItem.id not in additiveItems or additiveItems[srcItem.id] == 0: continue
				srcAmount = srcItem.getAmount()
				if additiveItems[srcItem.id] > srcAmount:
					additiveItems[srcItem.id] -= srcAmount
					self.removeItem_( srcItem.getOrder(), reason = csdefine.DELETE_ITEM_STUFFCOMPOSE )
				else:
					self.removeItem_( srcItem.getOrder(), additiveItems[srcItem.id], csdefine.DELETE_ITEM_STUFFCOMPOSE )
					additiveItems[srcItem.id] = 0
		odds = g_stuff.getOdds( baseAmount, srcItemID )						# 获取合成几率
		# 每次合成，都单独计算成功率
		successCount = 0
		failCount = 0
		totoalCount  = dstAmount
		for i in xrange( totoalCount ):
			if Function.estimate( odds ):
				successCount += 1
			else:
				failCount += 1
		# ----------------
		# 生成新的材料
		dstItemID = g_stuff.getDstItemID( baseAmount, srcItemID )		# 生成新材料的ID
		maxStack = item.getStackable()									# 生成材料最大叠加数
		dstAmount -= failCount
		while dstAmount > 0:
			kitSpace = self.getFreeOrderFK( csdefine.KB_CASKET_ID )		# 神机匣剩余空间
			if kitSpace == -1:
				# 背包不足，理论上不可能出现此现象，除非非正常数据
				break
			if dstAmount >= maxStack:
				# 如果要生成的数量大于最大叠加数
				dstItem = g_items.createDynamicItem( dstItemID )	# 创建物品
				dstItem.setAmount( maxStack )
				if dstBinded: dstItem.setBindType( ItemTypeEnum.CBT_HAND )
				self.addItemByOrderAndNotify_( dstItem, kitSpace, csdefine.ADD_ITEM_STUFFCOMPOSE )
				dstAmount -= maxStack
			else:
				dstItem = g_items.createDynamicItem( dstItemID )
				dstItem.setAmount( dstAmount )
				if dstBinded: dstItem.setBindType( ItemTypeEnum.CBT_HAND )
				self.addItemByOrderAndNotify_( dstItem, kitSpace, csdefine.ADD_ITEM_STUFFCOMPOSE )
				dstAmount = 0
			try:
				g_logger.equipStuffComposeLog( self.databaseID, self.getName(), dstItem.uid, dstItem.name(), dstItem.getAmount() )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
		if totoalCount == failCount:
			self.statusMessage( csstatus.MERGE_STUFF_FAILED )
			self.client.onCasketResult( 2 )
			self.client.unLockCasket()
			return False
		elif totoalCount == successCount:
			self.statusMessage( csstatus.MERGE_STUFF_SUCCEED )
			self.client.onCasketResult( 5 )
			self.client.unLockCasket()
			return True
		else:
			self.client.onCasketResult( 5 )
			self.client.unLockCasket()
			self.statusMessage( csstatus.MERGE_STUFF_INFO, totoalCount,successCount,failCount)
			return True

	def calStilettoCost( self, equipLevel, slotCount ):
		#1.05^道具等级*250*1.9^(孔数-1)*品质/3 by姜毅  原公式int(math.pow(equipLevel,1.05)*(100+25*math.pow(slotCount,2)))
		return int( 120 * equipLevel * 2 ** ( slotCount - 1 ))

	def equipStiletto( self ):
		"""
		装备打孔
		@return Bool
		"""
		kitCasketItems = self.getCasketItems()
		equips = []
		needBind = False
		for item in kitCasketItems:
			if item.isFrozen():
				self.statusMessage( csstatus.CASKET_CANT_VENDSTATE )
				return False
			if item.isEquip():
				equips.append( item )
			else:
				self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
				return False

		if len( equips ) == 0:
			self.statusMessage( csstatus.CASKET_PLAEASE_INPUT_EQUIP )
			return False
		if len( equips ) != 1:
			self.statusMessage( csstatus.CASKET_NEED_ONE_EQUIP_ONLY )
			return False

		equip = equips[0]
		if equip.isBinded(): needBind = True
		if not equip.canStiletto():
			self.statusMessage( csstatus.CASKET_STUDDED_CANT )
			return False
		currSlot = equip.getLimitSlot()
		if currSlot >= equip.getMaxSlot():
			self.statusMessage( csstatus.CASKET_STUDDED_MAXSLOT )
			return False
		equipLevel = equip.getReqLevel()
		stilettoCost = self.calStilettoCost( equipLevel, currSlot )
		if not self.payMoney( stilettoCost, csdefine.CHANGE_MONEY_EQUIPSTILETTO ):
			self.statusMessage( csstatus.CASKET_BIND_NEED_MONEY )
			return False

		# 打孔成功率 by姜毅
		odds = g_equipStuff.getStilettoOdds( currSlot )
		oddReal = int( random.random() * 100 )
		if oddReal > odds:
			self.statusMessage( csstatus.CASKET_REBUID_FAILED )
			return False
		newItem = equip.copy()
		if needBind: newItem.setBindType( ItemTypeEnum.CBT_PICKUP, self )
		self.deleteItem_( equip.order, reason = csdefine.DELETE_ITEM_EQUIPSTILETTO )
		newItem.setLimitSlot( currSlot + 1 )
		self.addItemByOrder_( newItem, self.getFreeOrderFK( csdefine.KB_CASKET_ID ), csdefine.ADD_ITEM_EQUIPSTILETTO )
		self.client.onCasketResult( 4 )
		self.statusMessage( csstatus.CASKET_STILETTO_SUCCESS )
		try:
			g_logger.equipStilettoLog( self.databaseID, self.getName(), equip.uid, newItem.uid, newItem.name(), currSlot, newItem.getLimitSlot() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )
		return True

	def equipSplit( self ):
		"""
		装备拆分
		"""
		kitCasketItems = self.getCasketItems()
		if len( kitCasketItems ) == 0:
			self.statusMessage( csstatus.CASKET_PLAEASE_INPUT_EQUIP )
			return False
		elif len( kitCasketItems ) != 1:
			self.statusMessage( csstatus.CASKET_EQUIP_SPLIT_AMOUNT_ERROR )	#只能分解一件属性装备
			return False
		equip = kitCasketItems[0]
		if not equip.isEquip():
			self.statusMessage( csstatus.CASKET_ITEM_CANT_BE_SPLITED ) # 物品不能被分解
			return False
		if equip.isFrozen():		#被冻结的物品不能被神机匣使用
			self.statusMessage( csstatus.CASKET_CANT_VENDSTATE )
			return False
		if equip.isWhite():	#白装不能拆分
			if Language.LANG == Language.LANG_GBK:
				self.statusMessage( csstatus.CASKET_EQUIP_CANNOT_SPLIT )
			elif Language.LANG == Language.LANG_BIG5:
				self.statusMessage( csstatus.CASKET_EQUIP_CANNOT_SPLIT_BIG5 )
			return False
		isBinded = equip.isBinded()	#分解的装备是否绑定 直接影响到分解出来的材料是否绑定 by姜毅
		# 道具等级^1.5*品质 by姜毅 原公式 payMoney  = int( math.ceil( equip.getLevel() ** 1.5 * 10 ) )
		payMoney = int(0.3 * equip.getLevel() ** 1.5 * equip.getQuality())
		if self.money < payMoney:	#如果钱不够
			self.statusMessage( csstatus.CASKET_SPLIT_PAY_FAILD )
			return False

		splitItem = []
		tempDic = equipSplitExp.getSpecifySplitInfo( equip.id )
		if tempDic:		#先检查该物品是不是配置好的特例物品
			amount = tempDic["MATERIAL_AMOUNT"]
			itemlist = tempDic.get( "ITEM_IDS", [] )
			if itemlist:
				splitItem = [ self.createDynamicItem( itemID ) for itemID in itemlist]
				if amount != len( splitItem ):
					DEBUG_MSG("split Item %s ,MATERIAL_AMOUNT is not match ITEM_IDS ")
			else:
				totalodds    = tempDic["TOTAL_ODDS"]
				materialodds = tempDic["MATERIAL_ODDS"]
				for i in xrange( amount ):
					odds = random.random() * totalodds
					for level,modds in enumerate( materialodds ):
						if odds <= modds:
							templist = equipSplitExp.getMaterial( level )
							item = self.createDynamicItem( random.choice( templist ) )
							splitItem.append( item )
							break
		else:				#如果不是就按照等级和品质来随机
			if equip.getLevel() < 20:
				self.statusMessage( csstatus.CASKET_SPLIT_FAILD_LOWLEVEL )
				return False
			datas = equipSplitExp.getSplitInfo( equip.getLevel(), equip.getQuality() )
			if not datas:
				return False
			totalodds    = datas["TOTAL_ODDS"]
			amount       = datas["MATERIAL_AMOUNT"]
			materialodds = datas["MATERIAL_ODDS"]
			for i in xrange( amount ):
				odds = random.random() * totalodds
				for level,modds in enumerate( materialodds ):
					if odds <= modds:
						itemlist = equipSplitExp.getMaterial( level )
						item = self.createDynamicItem( random.choice( itemlist ) )
						splitItem.append( item )
						break
		if not splitItem:
			return False
		if not self.payMoney( payMoney, csdefine.CHANGE_MONEY_EQUIPSPLIT ):		#先交钱 后提货! 收不到钱，绝不交货！
			self.statusMessage( csstatus.CASKET_SPLIT_PAY_FAILD )
			return False
		self.removeItem_( equip.order, reason = csdefine.DELETE_ITEM_EQUIPSPLIT )	#移除装备
		for item in splitItem:
			if isBinded:
				item.setBindType( ItemTypeEnum.CBT_PICKUP, self )
			self.addItemByOrderAndNotify_( item, self.getFreeOrderFK( csdefine.KB_CASKET_ID ), csdefine.ADD_ITEM_EQUIPSPLIT )
		self.statusMessage( csstatus.CASKET_EQUIP_SPLIT_SUCCESS )
		try:
			g_logger.equipSplitLog( self.databaseID, self.getName(), equip.uid, equip.name() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )
		return True

	def equipStudded( self ):
		"""
		装备镶嵌
		@return Bool
		"""
		mItems = {}
		equips = []
		stuffItems = []
		needBind = False
		kitCasketItems = self.getCasketItems()
		for item in kitCasketItems:
			if item.isFrozen():		#被冻结的物品不能被神机匣使用
				self.statusMessage( csstatus.CASKET_CANT_VENDSTATE )
				return False
			if item.isEquip():
				equips += [item]
			else:
				if mItems.has_key( item.id ):
					mItems[item.id] += item.amount
				else:
					mItems[item.id] = item.amount
					stuffItems += [item]
		if len( equips ) == 0:
			self.statusMessage( csstatus.CASKET_PLAEASE_INPUT_EQUIP )
			return False
		elif len( equips ) != 1:
			self.statusMessage( csstatus.CASKET_NEED_ONE_EQUIP_ONLY )
			return False

		equip = equips[0]
		stuff = g_equipStuff.getStuff()
		# 在这仅仅比较字典里面的key值，而不是之前的key值和value值都要满足才能镶嵌。
		m = []
		for e in stuff:
			m.append( e.keys() )
		if mItems.keys() not in m:
			self.statusMessage( csstatus.CASKET_STUDDED_MATIRAL_IS_WRONG )
			return
		stuffItem = stuffItems[0]
		studdedEffect = stuffItem.getBjExtraEffect()
		if len( studdedEffect ) == 0:
			self.statusMessage( csstatus.CASKET_STUDDED_NEED_NO_EMPTY )
			return False
		equipType = equip.getType()
		if equipType not in stuffItem.query( "bj_slotLocation", [] ):
			self.statusMessage( csstatus.CASKET_STUDDED_TYPE_NO_NEED )
			return
		if equip.getSlot() >= equip.getLimitSlot():
			self.statusMessage( csstatus.CASKET_STUDDED_NO_SLOT )
			return False
		if equip.getReqLevel() < stuffItem.getLevel():
			self.statusMessage( csstatus.CASKET_STUDDED_NO_SUPPORT )
			return False

		if equip.isBinded() or stuffItem.isBinded(): needBind = True

		# 每个镶嵌属性都有属性共存表。不能共存的属性则不能镶嵌
		stuffLevel = stuffItem.getLevel()
		coexistEffectIDs = []
		bjEffect = equip.getBjExtraEffect()

		# 获取装备镶嵌属性 检查是否有同类水晶已镶嵌 by姜毅
		keys = equip.getBjExtraEffect()
		if len( keys ) > 0:
			for keySingle in keys:
				keyList = serverDatas.get( keySingle, [] )
				if stuff in keyList:
					self.statusMessage( csstatus.CASKET_STUDDED_NOT_REPEAT )
					return False

		for data in bjEffect:
			coexistEffectIDs.extend( g_equipEffect.getNoCoexist( data[0] ) )
		for key, value in studdedEffect:
			if key in coexistEffectIDs:
				self.statusMessage( csstatus.CASKET_STUDDED_NO_MORE )
				return False

		newItem = equip.copy()
		if needBind: newItem.setBindType( ItemTypeEnum.CBT_PICKUP, self )
		self.removeItem_( equip.order, reason = csdefine.DELETE_ITEM_EQUIPSTUDDED )
		newStuddedEffect = []
		for effect in studdedEffect:
			newStuddedEffect.append(effect + (stuffItem.id,))
		newItem.addBjExtraEffect( newStuddedEffect )
		newItem.setSlot( equip.getSlot() + 1 )

		self.addItemByOrderAndNotify_( newItem, self.getFreeOrderFK( csdefine.KB_CASKET_ID ), csdefine.ADD_ITEM_EQUIPSTUDDED )
		# 加入水晶镶嵌广播 by姜毅
		# 水晶数量 - 1
		stuffItem.setAmount( stuffItem.getAmount() -1, self, csdefine.DELETE_ITEM_EQUIPSTUDDED )
		if stuffItem.id != ItemTypeEnum.ITEM_GREENCRYSTAL and stuffLevel >= Const.SUTD_BROADCAST_LEVEL:
			self.addItemAndRadio( newItem, ItemTypeEnum.ITEM_GET_STUD, "", "", stuffItem.name(), reason = csdefine.ADD_ITEM_EQUIPSTUDDED )
		self.client.onCasketResult( 4 )
		self.statusMessage( csstatus.CASKET_STUDDED_SUCCESS )
		try:
			g_logger.equipStuddedLog( self.databaseID, self.getName(), equip.uid, newItem.uid, newItem.name(), equip.getSlot(), newItem.getSlot(), str(studdedEffect) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )
		return True

	def itb_removeCrystal( self, srcEntityID, crystalId ):
		"""
		Exposed method.
		水晶摘除
		@param crystalId: 水晶的id
		@type  crystalId: object-id
		@return Bool
		"""
		if not self.hackVerify_( srcEntityID ) :
			self.client.unLockCasket()
			return
		if self.getState() == csdefine.ENTITY_STATE_VEND:
			self.statusMessage( csstatus.CASKET_FORBID_USED_IN_VENDING )
			return
		if not csdefine.KB_CASKET_ID in self.kitbags:
			ERROR_MSG( "src(%i) Can't find kitCasket in kitbag %s" % ( self.id, csdefine.KB_CASKET_ID ) )
			self.client.unLockCasket()
			return

		kitCasket = self.kitbags[csdefine.KB_CASKET_ID]
		useDegree = kitCasket.getUseDegree()								# 获取神机匣的使用次数
		if useDegree <= 0:
			# 神机匣使用次数为零
			self.client.unLockCasket()
			self.statusMessage( csstatus.CASKET_CANT_USE )
			return
		if self.getFreeOrderFK( csdefine.KB_CASKET_ID ) == -1:
			# 背包至少要有一个空位
			self.client.unLockCasket()
			self.statusMessage( csstatus.CASKET_CANT_NEED_SPACE )
			return

		equips = []
		removeTallys = []
		mItem = {}
		kitCasketItems = self.getCasketItems( True )
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
			self.statusMessage( csstatus.CASKET_PLAEASE_INPUT_EQUIP )
			return
		elif len( equips ) != 1:
			self.statusMessage( csstatus.CASKET_NEED_ONE_EQUIP_ONLY )
			return

		equip = equips[0]
		effectList = equip.getBjExtraEffect()
		if len( effectList ) == 0:
			self.statusMessage( csstatus.CASKET_EQUIP_HAVENOT_BESTUDDED )
			return

		crystal = self.createDynamicItem( crystalId )
		stuff = g_removeCrystal.getStuff()
		if ( len( removeTallys ) != 1 or ( mItem not in stuff ) ):			#所有摘除符的id
			self.statusMessage( csstatus.CASKET_TALLY_WRONG )
			return
		elif removeTallys[0].getLevel() < crystal.getLevel():
			self.statusMessage( csstatus.CASKET_TALLY_LEVEL_WRONG )
			return

		orderID = self.getNormalKitbagFreeOrder()
		if orderID == -1:
			self.statusMessage( csstatus.CIB_MSG_BAG_HAS_FULL )
			self.client.unLockCasket()
			return

		stuffEffectList = []
		for effectInfo in effectList:
			if effectInfo[2] != crystalId:
				stuffEffectList.append( effectInfo )
		equip.setBjExtraEffect( stuffEffectList, self )
		equip.setSlot( equip.getSlot() - 1,self )

		crystal.setBindType( ItemTypeEnum.CBT_PICKUP, self )
		self.addItemByOrderAndNotify_( crystal, orderID, csdefine.ADD_ITEM_REMOVECRYSTAL )
		self.removeItem_( removeTallys[0].order,reason = csdefine.DELETE_ITEM_REMOVECRYSTAL)

		self.client.onCasketResult( 8 )
		self.statusMessage( csstatus.CASKET_REMOVE_CRYSTAL_SUCCESS )

		useDegree -= 1
		kitCasket.setUseDegree( useDegree )
		self.client.onUpdateUseDegree( useDegree )
		self.client.unLockCasket()
		try:
			g_logger.crystalRemoveLog( self.databaseID, self.getName(), equip.uid, equip.name(), crystal.getLevel() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )

	def equipIntensify( self, uids ):
		"""
		装备强化
		@return Bool
		"""
		itemList = [ self.getItemByUid_( uid ) for uid in uids ]
		if len( itemList ) == 0:
			# 请放入要灌注属性的装备
			self.statusMessage( csstatus.CASKET_PLAEASE_INPUT_EQUIP )
			return
		dragonItems = []	# 龙珠
		luckItems = []		# 幸运宝石
		equips = []			# 装备
		needBind = False
		isUsedLuckItem = 0	#标识是否加入了幸运宝石，加入了就赋值为加入的幸运宝石的ID
		for item in itemList:
			if item.isFrozen():		#被冻结的物品不能被神机匣使用
				self.statusMessage( csstatus.CASKET_CANT_VENDSTATE )
				return False
			if item.isEquip():
				equips += [item]
			elif g_equipIntensify.isDragonGem( item ):	# 是否龙珠
				if len( dragonItems ) and dragonItems[0].id != item.id:
					self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
					return False
				dragonItems.append( item )
			elif g_equipIntensify.isLuckGem( item ):	# 是否幸运宝石
				if len( luckItems ) and luckItems[0].id != item.id:
					self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
					return False
				luckItems.append( item )
			else:
				self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
				return False

		if len( equips ) == 0:
			self.statusMessage( csstatus.CASKET_PLAEASE_INPUT_EQUIP )
			return False
		elif len( equips ) != 1:
			self.statusMessage( csstatus.CASKET_NEED_ONE_EQUIP_ONLY )
			return False
		# 判断是否有龙珠
		if len( dragonItems ) == 0:
			self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
		dragonGem = dragonItems[0]
		luckItem = None
		if len( luckItems ): luckItem = luckItems[0]
		equip = equips[0]
		if equip.isBinded() or dragonGem.isBinded() or ( luckItem is not None and luckItem.isBinded() ):
			needBind = True
		equipLevel = equip.getReqLevel()
		intensifyLevel = equip.getIntensifyLevel()
		# 判断装备是否可强化
		if not equip.canIntensify():
			self.statusMessage( csstatus.CASKET_INTENSIFY_NO_SUPPORT )
			return False
		if intensifyLevel >= csdefine.EQUIP_INTENSIFY_MAX_LEVEL:
			self.statusMessage( csstatus.CASKET_INTENSIFY_MAXLEVEL )
			return False
		# 每一种龙珠对应30级的装备
		minLevel = g_equipIntensify.getMinLevel( dragonGem.id )
		maxLevel = g_equipIntensify.getMaxLevel( dragonGem.id )
		if equipLevel < minLevel or equipLevel > maxLevel:
			self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
		# 强化要收费啦 by姜毅
		levelEqu = equip.getReqLevel()
		intensifyCost = int(g_equipIntensify.getReqMoney( levelEqu, intensifyLevel + 1 ))
		if not self.payMoney( intensifyCost, csdefine.CHANGE_MONEY_EQUIPINTENSIFY  ):					#先交钱 后提货
			self.statusMessage( csstatus.EQUIP_REPAIR_NOT_ENOUGH_MONEY )
			return False
		excOdds = 0.0
		if luckItem:
			excOdds = g_equipIntensify.getExtraOdds( luckItem.id )	# 根据幸运水晶获得额外成功率
		odds = g_equipIntensify.getOdds( intensifyLevel + 1 )
		newItem = equip.copy()
		if needBind: newItem.setBindType( ItemTypeEnum.CBT_PICKUP, self )
		self.removeItem_( equip.order, reason = csdefine.DELETE_ITEM_EQUIPINTENSIFY )
		if Function.estimate( odds + excOdds ):
			g_equipIntensify.setIntensifyValue( newItem, dragonGem.id, intensifyLevel + 1 )	# 由龙珠的类型和强化级别设置装备强化提升值
			newInstLevel = intensifyLevel + 1
			newItem.setIntensifyLevel( newInstLevel )
			# 加入装备强化广播 by姜毅
			if newInstLevel >= Const.INSTENSIFY_BROADCAST_LEVEL:
				self.addItemAndRadio( newItem, ItemTypeEnum.ITEM_GET_EQUIP_INSTENSIFY, "", "", "", str( newInstLevel ), reason = csdefine.ADD_ITEM_EQUIPINTENSIFY )
			self.client.onCasketResult( 5 )
			self.statusMessage( csstatus.EQUIP_INTENSIFY_SUCCEED )
		else:
			newIntensifyLevel = g_equipIntensify.getFiledLevel( intensifyLevel )
			g_equipIntensify.setIntensifyFailedValue( newItem, dragonGem.id, newIntensifyLevel )
			newItem.setIntensifyLevel( newIntensifyLevel )
			self.client.onCasketResult( 2 )
			self.statusMessage( csstatus.EQUIP_INTENSIFY_FAILED )
		addResut = self.addItemByOrderAndNotify_( newItem, self.getNormalKitbagFreeOrder(), csdefine.ADD_ITEM_EQUIPINTENSIFY )
		# 龙珠数量-1，幸运宝石数量-1
		if addResut:					#添加物品成功，通知客户端
			self.client.onUpdateIntensifyItem( newItem.uid )
		dragonGem.setAmount( dragonGem.getAmount() -1, self, csdefine.DELETE_ITEM_EQUIPINTENSIFY )
		if luckItem:
			luckItem.setAmount( luckItem.getAmount() -1, self, csdefine.DELETE_ITEM_EQUIPINTENSIFY )
			isUsedLuckItem = luckItem.id
		try:
			g_logger.equipIntensifyLog( self.databaseID, self.getName(), equip.uid, newItem. uid,newItem.name(), equip.getIntensifyLevel(), newItem.getIntensifyLevel() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )
		return True

	def equipImproveQuality( self ):
		"""
		绿装升品
		@return Bool
		"""
		kitCasketItems = self.getCasketItems()
		badgeItems = []			#徽章
		equip = None				#装备
		needBind = False
		for item in kitCasketItems:
			if item.isFrozen():		#被冻结的物品不能被神机匣使用
				self.statusMessage(csstatus.CASKET_CANT_VENDSTATE)
				return False
			if item.isEquip():
				if equip != None and equip.id != item.id:
					self.statusMessage( csstatus.CASKET_NEED_ONE_EQUIP_ONLY )
					return False
				equip = item
			elif g_equipImproveQuality.isBadge( item ):		#是否是徽章
				if len( badgeItems ) and badgeItems[0].id != item.id:
					self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
					return False
				badgeItems.append( item )
			else:
				self.statusMessage(csstatus.CASKET_MATIRAL_IS_WRONG)
				return False
		if equip == None:
			self.statusMessage( csstatus.CASKET_PLAEASE_INPUT_EQUIP )
			return False
		#判断是否有徽章
		if len( badgeItems ) == 0:
			self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
		badgeItem = badgeItems[0]
		if equip.isGreen() == False:
			self.statusMessage( csstatus.CASKET_EQUIP_CANNOT_IMPROVE_BIG5 )
			return False
		equipLevel = equip.getReqLevel()
		minLevel = 90			#升品最低等级
		maxLevel = 149			#升品最高等级
		if equipLevel < minLevel or equipLevel > maxLevel:
			self.statusMessage( csstatus.CASKET_CANT_IMPROVE_LEVEL_LIMIT )
			return False
		if equip.isBinded() or badgeItem.isBinded():
			needBind = True
		equipPrefix = equip.getPrefix()
		odds=g_equipImproveQuality.getOdds( badgeItem.id , equipPrefix )
		if odds == 0:
			self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
		newItem = equip.copy()
		if needBind: newItem.setBindType( ItemTypeEnum.CBT_PICKUP , self )
		self.removeItem_( equip.order, reason = csdefine.DELETE_ITEM_IMPROVEQUALITY)
		if Function.estimate(odds):
			g_equipImproveQuality.setImproveQualityPrefix( newItem ,badgeItem.id)
			self.client.onCasketResult( 1 )
			self.statusMessage( csstatus.CASKET_IMPROVE_QUALITY_SUCCESS)
		else:
			g_equipImproveQuality.setImproveQualityFailedPrefix( newItem ,badgeItem.id)
			self.client.onCasketResult( 2 )
			self.statusMessage( csstatus.CASKET_IMPROVE_QUALITY_FAILED)
		self.addItemByOrderAndNotify_( newItem , self.getFreeOrderFK(csdefine.KB_CASKET_ID), csdefine.ADD_ITEM_IMPROVEQUALITY)
		badgeItem.setAmount( badgeItem.getAmount()-1, self,csdefine.DELETE_ITEM_IMPROVEQUALITY)
		# 写日志
		try:
			g_logger.equipImproveLog( self.databaseID, self.getName(), equip.uid, newItem.uid, newItem.name() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )
		return True


	def equipRebuild( self ):
		"""
		装备改造
		@return Bool
		"""
		kitCasketItems = self.getCasketItems()
		if len( kitCasketItems ) == 0: return False
		wEquips = []
		qEquips = []
		for item in kitCasketItems:
			# 计算出神机匣里面有多少件装备
			# 只能有一件白色装备和两件非白色的同品质装备
			# 才能进行改造
			if item.isFrozen():		#被冻结的物品不能被神机匣使用
				self.statusMessage( csstatus.CASKET_CANT_VENDSTATE )
				return False
			if not item.isEquip():
				self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
				return False
			if item.isWhite():
				wEquips.append( item )
			else:
				qEquips.append( item )

		# 判定放入的装备数量是否合格
		if len( wEquips ) != 1 or len( qEquips ) != 2:
			self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False

		wEquip = wEquips[0]
		qEquip1 = qEquips[0]
		qEquip2 = qEquips[1]

		# 如果其中一件装备绑定 那么合成出来的装备也绑定 by姜毅
		bindResult = False
		if wEquip.isBinded() or qEquip1.isBinded() or qEquip2.isBinded():
			bindResult = True

		# 装备类型必须一致，比如防具和武器一起将无法合成  2008-10-28 gjx
		maskCode = 0x030000 # 装备类型判断掩码
		if wEquip.getType() & maskCode == ItemTypeEnum.ITEM_WEAPON:		# 武器
			if qEquip1.getType() & maskCode != ItemTypeEnum.ITEM_WEAPON:
				self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
				return False
			elif qEquip2.getType() & maskCode != ItemTypeEnum.ITEM_WEAPON:
				self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
				return False
		elif wEquip.getType() & maskCode == ItemTypeEnum.ITEM_ARMOR:	# 防具
			if qEquip1.getType() & maskCode != ItemTypeEnum.ITEM_ARMOR :
				self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
				return False
			elif qEquip2.getType() & maskCode != ItemTypeEnum.ITEM_ARMOR :
				self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
				return False
		elif wEquip.getType() & maskCode == ItemTypeEnum.ITEM_ORNAMENT:	# 首饰
			if qEquip1.getType() & maskCode != ItemTypeEnum.ITEM_ORNAMENT :
				self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
				return False
			elif qEquip2.getType() & maskCode != ItemTypeEnum.ITEM_ORNAMENT :
				self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
				return False
		else:
			self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False

		if wEquip.getLevel() < 20 or qEquip1.getLevel() < 20 or qEquip2.getLevel() < 20:
			self.statusMessage( csstatus.CASKET_CANT_REBUILD_LEVEL_LIMIT )
			return False

		# 判定放入的装备是否在同一等级段
		if not qEquip1.getLevel()/10 == qEquip2.getLevel()/10 == wEquip.getLevel()/10:
			self.statusMessage( csstatus.CASKET_CANT_REBUILD_DLEVEL_EQUIP )
			return False

		# 判定放入的装备品质是否合格
		if qEquip1.getQuality() != qEquip2.getQuality():
			self.statusMessage( csstatus.CASKET_CANT_REBUILD_QUALITY_WRONG )
			return False

		# 判定money够不够
		#装备合成烧钱再更改 by姜毅
		lvm = qEquip1.getLevel()
		if lvm > 0 and lvm <= 50:    #1~50 1.1^道具等级*100*品质/3
			money = int(1.1 ** lvm * 100 * qEquip1.getQuality() /3)
		else:           #51~150 1.03^道具等级*2700 *品质/3
			money = int(1.03 ** lvm * 2700 * qEquip1.getQuality() /3)
		if not self.payMoney( money, csdefine.CHANGE_MONEY_EQUIPREBUILD ):
			self.statusMessage( csstatus.CASKET_BIND_NEED_MONEY )
			return False

		# 生成相关信息
		itemID = wEquip.id
		quality = qEquip1.getQuality()

		# 生成前缀
		r = random.randint( 0, 100 )
		if qEquip1.isGreen():
			pList = ItemTypeEnum.CPT_GREEN
		else:
			pList = ItemTypeEnum.CPT_NO_GREEN

		# 默认前缀
		prefix = pList[0]
		for p in pList:
			if g_equipQuality.getRebuildRate( p ) >= r:
				prefix = p
				break

		# 删除和加入装备
		for equip in qEquips:
			self.removeItem_( equip.order, reason = csdefine.DELETE_ITEM_EQUIPREBUILD )
		newItem = wEquip.copy()
		self.removeItem_( wEquip.order, reason = csdefine.DELETE_ITEM_EQUIPREBUILD )

		# 如果其中一件装备绑定 那么合成出来的装备也绑定 by姜毅
		if bindResult:
			newItem.setBindType( ItemTypeEnum.CBT_PICKUP )
		newItem.setQuality( quality )
		newItem.setPrefix( prefix )
		newItem.createRandomEffect()

		# 需求，合成装备等级取10整 by姜毅
		newReqLevel = newItem.getReqLevel()/10*10
		if newReqLevel <= 0: newReqLevel = 1
		newItem.setReqLevel( newReqLevel )

		self.addItemByOrderAndNotify_( newItem, self.getFreeOrderFK( csdefine.KB_CASKET_ID ), csdefine.ADD_ITEM_EQUIPREBUILD )

		self.client.onCasketResult( 4 )
		self.statusMessage( csstatus.CASKET_REBUID_SUCCEED )
		try:
			g_logger.equipReBuildLog( self.databaseID, self.getName(), wEquip.uid, newItem.uid, newItem.fullName(), \
				[ wEquip.getQuality(), wEquip.getPrefix() ], [ newItem.getQuality(),newItem.getPrefix() ]\
				 )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )
		return True

	def equipBind( self, srcEntityID, uids ):
		"""
		Exposed method.
		装备认主
		@return Bool
		"""
		if not self.hackVerify_( srcEntityID ) :
			self.client.unLockCasket()
			return
			
		try:
			kitCasketItem = self.kitbags[csdefine.KB_CASKET_ID]
		except KeyError:
			ERROR_MSG( "src(%i) Can't find kitCasket in kitbag %s" % ( self.id, csdefine.KB_CASKET_ID ) )
			return
		useDegree = kitCasketItem.getUseDegree()	#获得神机匣的使用次数
		if useDegree <= 0:
			self.statusMessage( csstatus.CASKET_CANT_USE )
			DEBUG_MSG( "(%s):kitCasket has been used out." % self.getName() )
			return

		itemList = [ self.getItemByUid_( uid ) for uid in uids ]
		if len( itemList ) == 0:
			# 请放入要灌注属性的装备
			self.statusMessage( csstatus.CASKET_PLAEASE_INPUT_EQUIP )
			return
		# 计算出神机匣里面有多少件装备
		# 只能有一件装备才能进行强化
		# 记录下不是装备的材料类型和数据
		# 生成格式 {"ItemID": amount, ...}
		mItems = []
		equips = []
		stuff = g_equipBind.getStuff()
		for item in itemList:
			if item.isFrozen():		#被冻结的物品不能被神机匣使用
				self.statusMessage( csstatus.CASKET_CANT_VENDSTATE )
				return False
			if item.isEquip():
				equips += [item]
			elif item.id in stuff:
				mItems += [item]
			else:
				self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
				return False

		if len( equips ) == 0:
			self.statusMessage( csstatus.CASKET_PLAEASE_INPUT_EQUIP )
			return False
		elif len( equips ) != 1:
			self.statusMessage( csstatus.CASKET_NEED_ONE_EQUIP_ONLY )
			return False
		if len( mItems ) == 0:
			self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False

		equip = equips[0]
		stuffItem = mItems[0]
		# 加入不能认主的装备类型判断 by姜毅
		if equip.getType() in [ ItemTypeEnum.ITEM_SYSTEM_TALISMAN, ItemTypeEnum.ITEM_SYSTEM_KASTONE, ItemTypeEnum.ITEM_FASHION1, ItemTypeEnum.ITEM_FASHION2, ItemTypeEnum.ITEM_POTENTIAL_BOOK ]:
			self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
		if equip.isWhite():
			self.statusMessage( csstatus.CASKET_WHITEEQUIP_IS_WRONG )
			return False
		if equip.isObey():
			self.statusMessage( csstatus.KIT_EQUIP_OBEY_YET )
			return False
		#装备认主公式修改 by姜毅
		lvm = equip.getLevel()
		if lvm > 0 and lvm <= 50:    #1~50 1.1^道具等级*100*品质/3
			money = int(1.1 ** lvm * 100 * equip.getQuality() /3)
		else:           #51~150 1.03^道具等级*2700 *品质/3
			money = int(1.03 ** lvm * 2700 * equip.getQuality() /3)
		if not self.payMoney( money, csdefine.CHANGE_MONEY_EQUIPBIND ):
			self.statusMessage( csstatus.CASKET_BIND_NEED_MONEY )
			return False
		newItem = equip.copy()
		self.removeItem_( equip.order, reason = csdefine.DELETE_ITEM_EQUIPBIND )
		newItem.setObey( ItemTypeEnum.COB_OBEY )
		newItem.setBindType( ItemTypeEnum.CBT_HAND )
		# 认主后 装备基础属性提升10% by姜毅
		self.addItemByOrderAndNotify_( newItem, self.getNormalKitbagFreeOrder(), csdefine.ADD_ITEM_EQUIPBIND )
		stuffItem.setAmount( stuffItem.getAmount() -1, self, csdefine.DELETE_ITEM_EQUIPBIND )
		self.client.onCasketResult( 4 )
		
		#神机匣次数减1
		useDegree -= 1
		kitCasketItem.setUseDegree( useDegree )
		self.client.onUpdateUseDegree( useDegree )
			
		self.statusMessage( csstatus.KIT_EQUIP_OBEY_SUCCESS )
		try:
			g_logger.equipBindLog( self.databaseID, self.getName(), equip.uid, newItem.uid, newItem.name() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )
		return True

	# ----------------------------------------------------------------
	# 特殊合成
	# ----------------------------------------------------------------
	def specialCompose( self, idx ):
		"""
		特殊合成
		@return Bool
		"""
		sc = self.sc_canUseSkill( idx ) #配方格式,like as {"itemID":item.id, "raFixedAttr":{}, "maxCount":5,"quality":5}
		if not sc:return  #索引为idx的配方不能使用
		quality = sc[ "quality" ] #卷轴品质
		scrollID = sc[ "itemID" ] #卷轴物品ID
		scAttrL = sc[ "raFixedAttr" ] #卷轴的随机属性
		scAttr = {}
		for attrInfo  in scAttrL:
			scAttr[attrInfo[0]] = attrInfo[1]
		
		#根据卷轴ID获得材料、目标物品等配置
		bindResult= specom.getIsBind( scrollID )  #生成的物品是否绑定
		money     = specom.getRequireMoney( scrollID ) #消耗的金钱
		dstItemID = specom.getDstItemID( scrollID )  #目标物品ID
		dstAmount = specom.getDstItemCount( scrollID )  #目标物品的数量
		mItems    = specom.getMaterials( scrollID ) #合成材料及其数量
		
		#-----------------判断配置是否合理----------------
		if not dstItemID:
			return False
		if not dstAmount:
			return False
		if not  mItems:
			return False
		
		#------------------判断背包空位-------------------
		orderIDs = self.getAllNormalKitbagFreeOrders()
		if len( orderIDs ) < dstAmount :
			self.statusMessage( csstatus.CASKET_EQUIP_SPECIAL_COMPOSE_NO_SPACE )
			return False
		
		#------------------判断背包中是否存在所有材料--------------
		freezes = [] #需要锁定的物品order列表
		dstItemLevel = 0  #目标物品的等级
		for iteminfo in mItems:
			itemID = iteminfo[0]
			count  = iteminfo[1]
			if itemID == 0: continue
			sitems = self.findItemsByIDFromNK( itemID )
			scount = 0
			for item in sitems:
				scount += item.getAmount()
				freezes.append( item.getOrder() )
				if item.isEquip():
					dstItemLevel = item.getReqLevel()
			if scount < count:
				self.statusMessage( csstatus.CASKET_EQUIP_SPECIAL_COMPOSE_LACK_METERIAL )
				return False
		
		#------------------锁定所有材料背包格子--------------
		for order in freezes:
			self.freezeItem_( order )
		
		#--------------------------------------消耗的金钱---------------
		if not self.payMoney( int( money ), csdefine.CHANGE_MONEY_SPECIALCOMPOSE ):
			self.statusMessage( csstatus.CASKET_BIND_NEED_MONEY )
			return False
		
		#--------------------------------------移除材料--------------
		for itemInfo in mItems:
			itemID = itemInfo[0]
			count  = itemInfo[1]
			if itemID == 0: continue
			if not self.removeItemTotal(  itemID, count, csdefine.DELETE_ITEM_SPECIALCOMPOSE ):
				self.statusMessage( csstatus.CASKET_EQUIP_SPECIAL_COMPOSE_DEL_METERIAL_ERROR )
				return False
			
		#--------------------------解锁之前锁定的格子----------------
		for order in freezes:
			self.unfreezeItem_( order )
		
		#--------------------------------------创建合成品------------
		newItem = g_items.createDynamicItem( dstItemID )
		if newItem is None: return False
		newItem.setAmount( dstAmount )
		#增加卷轴已经随机到的属性
		if newItem.isEquip():
			newItem.setQuality( quality )
			#随机产生卷轴剩下的随机属性（ 绿色2个，粉色3个）
			scrollLevel = g_items.getLevel( scrollID )
			randomEffect = g_itemPropAttrExp.getScrollComposeRandomEffect( scrollID, scrollLevel, scAttr, quality )
			randomEffect.update( scAttr )
			newItem.set( "eq_extraEffect", randomEffect, self )
			newItem.setReqLevel( dstItemLevel )

		if bindResult == True:
			newItem.setBindType( ItemTypeEnum.CBT_PICKUP )

		self.addItemByOrderAndNotify_( newItem, self.getNormalKitbagFreeOrder(), csdefine.ADD_ITEM_SPECIALCOMPOSE )
		self.statusMessage( csstatus.MERGE_STUFF_SUCCEED )
		
		#--------------------------合成成功，减少配方次数-----------
		self.sc_usedSkill( idx )
		try:
			g_logger.equipSpecialComposeLog( self.databaseID, self.getName(), newItem.uid, newItem.name() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )
		return True
	
	def addTalismanLife( self ):
		"""
		法宝充值，神机匣功能
		"""
		talismanItems = []
		lifeItems = []
		kitCasketItems = self.getCasketItems()
		for item in kitCasketItems:
			if item.isFrozen():		#被冻结的物品不能被神机匣使用
				self.statusMessage( csstatus.CASKET_CANT_VENDSTATE )
				return False
			if item.id == csconst.TALISMAN_ADD_LIFE_ITEM:
				lifeItems.append( item )
			elif item.getType() == ItemTypeEnum.ITEM_SYSTEM_TALISMAN:
				talismanItems.append( item )
			else:
				# 只能放入法宝和女娲石
				self.statusMessage( csstatus.TALISMAN_ADDLIFE_NEED_TANDN )
				return False

		talismanCount = len( talismanItems )
		if talismanCount == 0:
			# 请放入需要充值的法宝
			self.statusMessage( csstatus.TALISMAN_ADDLIFE_NEED_TAl )
			return False
		if talismanCount > 1:
			# 一次只能给一个法宝充值
			self.statusMessage( csstatus.TALISMAN_ADDLIFE_ONCE )
			return False

		if len( lifeItems ) == 0:
			# 请放入女娲石
			self.statusMessage( csstatus.TALISMAN_ADDLIFE_NEED_NWS )
			return False

		lifeCount = sum([item.amount for item in lifeItems])
		addTime = Const.TALISMAN_ADD_LIFE_TIME
		if addTime <= 0: return False

		# 先给法宝充值
		talismanItem = talismanItems[0]
		lifeItem = lifeItems[0]
		# 如果deadTime是None，说明此法宝未被激活
		# 未被激活的法宝直接返回，对已激活的法宝才需要重新设置死亡时间
		if not talismanItem.isActiveLifeTime(): return False
		lifeTime = talismanItem.getLifeTime()
		talismanItem.setLifeTime( lifeTime + addTime, self )

		# 并添加到管理器中
		uid = talismanItem.uid
		deadTime = talismanItem.getDeadTime()

		# 法宝当前已激活，并未死亡，则移除旧的管理器中的记录
		if deadTime > 0:
			self.removeLifeItemsFromManage( [uid], [deadTime] )
		else:
			deadTime = time.time()

		# 法宝已激活，但死亡，则需添加在物品管理器中
		newDeadTime = deadTime + addTime
		talismanItem.setDeadTime( newDeadTime, self )

		# 移除女娲石
		lifeItem.setAmount( lifeItem.getAmount() -1, self, csdefine.DELETE_ITEM_ADDTALISMANLIFE )
		# 通知客户端成功
		self.statusMessage( csstatus.TALISMAN_ADDLIFE_SUCCESS )

		self.addLifeItemsToManage( [uid], [newDeadTime] )
		try:
			g_logger.talismanAddLifeLog( self.databaseID, self.getName(), talismanItem.uid, talismanItem.name(), deadTime,newDeadTime )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )
		return True

	def talismanSplit( self ):
		"""
		法宝分解 by 姜毅
		"""
		kitCasketItems = self.getCasketItems()
		if len(kitCasketItems) != 1:
			self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
		talismanItem = kitCasketItems[0]
		if talismanItem.isFrozen():		#被冻结的物品不能被神机匣使用
			self.statusMessage( csstatus.CASKET_CANT_VENDSTATE )
			return False
		if talismanItem.getType() != ItemTypeEnum.ITEM_SYSTEM_TALISMAN:
			self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
		grade = talismanItem.getGrade()
		cost = talismanSplitExp.getSplitCost( grade )
		if not self.payMoney( cost, csdefine.CHANGE_MONEY_TALISMAN_SPLIT ):
			self.statusMessage( csstatus.CASKET_BIND_NEED_MONEY )
			return False
		binded = talismanItem.isBinded()
		resultID = talismanSplitExp.getSplitInfo( grade )
		awarder = g_rewards.fetch( resultID, self )
		if awarder is None or len( awarder.items ) <= 0: return
		for item in awarder.items:
			if binded:item.setBindType( ItemTypeEnum.CBT_PICKUP )
			self.addItemByOrderAndNotify_( item, self.getFreeOrderFK( csdefine.KB_CASKET_ID ), csdefine.ADD_ITEM_TALISMAN_SPLIT )
		self.removeItem_( talismanItem.order, reason = csdefine.DELETE_ITEM_EQUIPSPLIT )	#移除装备
		try:
			g_logger.talismanSplitLog( self.databaseID, self.getName(), talismanItem.uid, talismanItem.name() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )
		return True

	def talismanInstensify( self ):
		"""
		法宝强化 by 姜毅
		"""
		talismanItem = None
		talismanItems = []
		lifeItems = []
		luckeyItems = []
		kitCasketItems = self.getCasketItems()
		if len( kitCasketItems ) < 2:
			self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
		for item in kitCasketItems:
			if item.isFrozen():		#被冻结的物品不能被神机匣使用
				self.statusMessage( csstatus.CASKET_CANT_VENDSTATE )
				return False
			if item.id == csconst.TALISMAN_ADD_LIFE_ITEM:	# 女娲石
				lifeItems.append( item )
			elif item.getType() == ItemTypeEnum.ITEM_SYSTEM_TALISMAN:	# 法宝
				talismanItems.append( item )
			elif g_equipIntensify.isLuckGem( item ):	# 是否幸运宝石
				luckeyItems.append( item )
			else:
				self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )	# 只能放入法宝和女娲石或者幸运石
				return False
		if len( talismanItems ) != 1 or len( lifeItems ) < 1:
			self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
		# 判断装备是否可强化
		oldtalismanItem = talismanItems[0]
		lifeItem = lifeItems[0]
		intensifyLevel = oldtalismanItem.getIntensifyLevel()
		if intensifyLevel >= csdefine.EQUIP_INTENSIFY_MAX_LEVEL:
			self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False

		luckItem = None
		excOdds = 0.0
		if len( luckeyItems ) > 0:
			luckItem = luckeyItems[0]
			excOdds = g_equipIntensify.getExtraOdds( luckItem.id )	# 根据幸运水晶获得额外成功率
		odds = g_equipIntensify.getOdds( intensifyLevel + 1 )
		talismanItem = oldtalismanItem.copy()
		if oldtalismanItem.isBinded():
			talismanItem.setBindType( ItemTypeEnum.CBT_PICKUP )
		self.removeItem_( oldtalismanItem.order, reason = csdefine.DELETE_ITEM_TALISMAN_INTENSIFY )
		if Function.estimate( odds + excOdds ):
			talismanItem.addIntensifyLevel( 1 )
			newInstLevel = intensifyLevel + 1
			if newInstLevel >= Const.INSTENSIFY_BROADCAST_LEVEL:
				self.addItemAndRadio( talismanItem, ItemTypeEnum.ITEM_GET_EQUIP_INSTENSIFY, "", "", "", str( newInstLevel ), reason = csdefine.ADD_ITEM_TALISMAN_INTENSIFY )
			self.client.onCasketResult( 5 )
			self.statusMessage( csstatus.EQUIP_INTENSIFY_SUCCEED )
		else:
			newIntensifyLevel = g_equipIntensify.getFiledLevel( intensifyLevel )
			talismanItem.setIntensifyLevel( newIntensifyLevel )
			self.client.onCasketResult( 2 )
			self.statusMessage( csstatus.EQUIP_INTENSIFY_FAILED )
		self.addItemByOrderAndNotify_( talismanItem, self.getFreeOrderFK( csdefine.KB_CASKET_ID ), csdefine.ADD_ITEM_EQUIPINTENSIFY )

		lifeItem.setAmount( lifeItem.getAmount() -1, self, csdefine.DELETE_ITEM_TALISMAN_INTENSIFY )
		if luckItem:
			luckItem.setAmount( luckItem.getAmount() -1, self, csdefine.DELETE_ITEM_TALISMAN_INTENSIFY )
		try:
			g_logger.talismanIntensifyLog( self.databaseID, self.getName(), talismanItem.uid, talismanItem.name(), oldtalismanItem.getIntensifyLevel() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )
		return True

	# ----------------------------------------------------------------
	# 法宝
	# ----------------------------------------------------------------
	def addTalismanExpInterface( self ):
		"""
		增加法宝经验
		"""
		# 如果人物经验为0，直接返回
		if self.EXP == 0: return

		# 判断该法宝物品是否存在
		item = self.getItem_( ItemTypeEnum.CEL_TALISMAN )
		if item is None:
			self.statusMessage( csstatus.TALISMAN_NO_WIELD )
			return

		# 判断是不是法宝类型
		if item.getType() != ItemTypeEnum.ITEM_SYSTEM_TALISMAN:
			self.statusMessage( csstatus.TALISMAN_SHAN_ZHAI )
			return

		# 如果法宝达到最高等级，直接返回
		itemLevel = item.getLevel()
		if itemLevel >= 150: return

		# 法宝吸取经验增加规则，法宝等级只能在其品质等级范围内有经验值变化 by姜毅
		expMap = csconst.TALISMAN_LEVELUP_MAP
		grade = item.getGrade()
		if itemLevel >= expMap[grade][0]:
			self.statusMessage( expMap[grade][1] )
			return

		# 如果法宝的等级大于玩家的等级
		if itemLevel >= self.level:
			self.statusMessage( csstatus.TALISMAN_TOP_LEVEL )
			return

		# 计算法宝升级还需要多少经验
		nDValue = item.getMaxExp() - item.getExp()
		# 表示玩家当前经验够法宝升级的了
		if nDValue <= self.EXP:
			# 玩家经验处理
			self.addExp( -nDValue, csdefine.CHANGE_EXP_FABAO )
			# 法宝升级处理
			item.setExp( 0, self )
			item.setLevel( itemLevel + 1, self )
		else:
			item.addExp( self.EXP, self )
			self.addExp( -self.EXP, csdefine.CHANGE_EXP_FABAO )

		# 通知客户端法宝升级成功
		self.client.onTalismanLvUp()

	def addTalismanPotentialInterface( self ):
		"""
		法宝技能升级
		"""
		# 如果人物潜能点为0，直接返回
		if self.potential == 0: return

		# 判断该法宝物品是否存在
		item = self.getItem_( ItemTypeEnum.CEL_TALISMAN )
		if item is None:
			self.statusMessage( csstatus.TALISMAN_NO_WIELD )
			return

		# 判断是不是法宝类型
		if item.getType() != ItemTypeEnum.ITEM_SYSTEM_TALISMAN:
			self.statusMessage( csstatus.TALISMAN_SHAN_ZHAI )
			return

		# 如果法宝技能达到最高等级，直接返回
		skillLevel = item.getSkillLevel()
		if skillLevel >= 150: return

		# 法宝吸取潜能增加规则，法宝等级只能在其品质等级范围内有潜能变化 by姜毅
		expMap = csconst.TALISMAN_LEVELUP_MAP
		grade = item.getGrade()
		if skillLevel >= expMap[grade][0]:
			self.statusMessage( expMap[grade][2] )
			return

		if skillLevel >= item.getLevel():
			self.statusMessage( csstatus.TALISMAN_SKILL_TOP_LEVEL )
			return

		# 计算法宝技能升级还需要多少潜能
		nDValue = item.getMaxPotential() - item.getPotential()
		# 表示玩家当前潜能点够法宝技能升级的了
		if nDValue <= self.potential:
			# 玩家潜能点处理
			if self.payPotential( nDValue ):
				# 法宝技能升级处理
				item.setPotential( 0, self )
				item.setSkillLevel( skillLevel + 1, self )
				self.statusMessage( csstatus.ACCOUNT_LOST_PROTEN_FABAO, int(nDValue) )
		else:
			poten = self.potential
			if self.payPotential( self.potential ):
				item.addPotential( poten, self )
				self.statusMessage( csstatus.ACCOUNT_LOST_PROTEN_FABAO, int(poten) )

		# 通知客户端法宝技能升级成功
		self.client.onTalismanSkillLvUp()

	def updateTalismanGradeInterface( self ):
		"""
		提升法宝品质
		"""
		# 判断物品是否存在
		order = ItemTypeEnum.CWT_TALISMAN
		talismanItem = self.getItem_( order )
		if talismanItem is None:
			self.statusMessage( csstatus.TALISMAN_NO_WIELD )
			return

		# 判断是不是法宝类型
		if talismanItem.getType() != ItemTypeEnum.ITEM_SYSTEM_TALISMAN:
			self.statusMessage( csstatus.TALISMAN_SHAN_ZHAI )
			return

		grade = talismanItem.getGrade()
		level = talismanItem.getLevel()

		# 升级到仙品需要法宝50级
		if grade == ItemTypeEnum.TALISMAN_COMMON and level < csconst.TALISMAN_UPTO_IMMORTAL_LEVEL:
			self.statusMessage( csstatus.TALISMAN_UPDATE_TOI_NEED_LEVEL )
			return
		# 升级到神品需要法宝100级
		if grade == ItemTypeEnum.TALISMAN_IMMORTAL and level < csconst.TALISMAN_UPTO_DEITY_LEVEL:
			self.statusMessage( csstatus.TALISMAN_UPDATE_TOD_NEED_LEVEL )
			return
		# 判断法宝品质等级是否已经达到最高等级
		if grade == ItemTypeEnum.TALISMAN_DEITY:
			self.statusMessage( csstatus.TALISMAN_GRADE_TOP )
			return

		# 查找玩家身上是否有相对应的材料物品
		needItemID = g_talisman.getUpItem( grade )
		needItemAmount = g_talisman.getUpItemAmount( grade )
		needItemList = self.findItemsByIDFromNKCK( needItemID )
		amount = sum( [item.amount for item in needItemList] )
		if amount < needItemAmount:
			self.statusMessage( csstatus.TALISMAN_UPDATE_GRADE_NEED )
			return

		talismanItem.setGrade( grade + 1, self )

		for item in needItemList:
			if needItemAmount <= 0: break
			amount = item.amount
			if amount <= needItemAmount:
				item.setAmount( 0, self, csdefine.DELETE_ITEM_UPDATETALISMANGRADE )
				needItemAmount -= amount
			else:
				item.setAmount( amount - needItemAmount, self, csdefine.DELETE_ITEM_UPDATETALISMANGRADE )

		# 更新法宝模型图标数据,玩家实时更换
		model = talismanItem.model()
		self.talismanNum = model
		talismanItem.set( "model", model, self )
		icon = talismanItem.icon()
		talismanItem.set( "icon", icon, self )

		self.statusMessage( csstatus.TALISMAN_UPDATE_SUCCESS )

	def activateTalismanAttrInterface( self, uid ):
		"""
		激活法宝属性
		"""
		# 天罡石是否存在
		srcItem = self.getItemByUid_( uid )
		if srcItem is None:
			self.statusMessage( csstatus.CIB_MSG_ITEM_NOT_EXIST )
			return
		# 是否是天罡石类型
		if srcItem.getType() != ItemTypeEnum.ITEM_SYSTEM_GODSTONE:
			return
		# 判断玩家法宝是否存在
		order = ItemTypeEnum.CWT_TALISMAN
		talismanItem = self.getItem_( order )
		if talismanItem is None:
			self.statusMessage( csstatus.TALISMAN_NO_WIELD )
			return
		# 判断是不是法宝类型
		if talismanItem.getType() != ItemTypeEnum.ITEM_SYSTEM_TALISMAN:
			self.statusMessage( csstatus.TALISMAN_SHAN_ZHAI )
			return
		# 根据使用的天罡石确定能够激活的品级
		useGrade = g_talisman.getAcGradeByItemID( srcItem.id )
		if useGrade is None: return

		# 判断法宝当前的品级属性是否能用该物品激活
		grade = talismanItem.getGrade()
		if useGrade > grade:
			self.statusMessage( csstatus.TALISMAN_GRADE_LESS )
			return
		effect = []
		if useGrade == ItemTypeEnum.TALISMAN_COMMON:
			effect = list( talismanItem.getCommonEffect() )
			func = talismanItem.setCommonEffect
		elif useGrade == ItemTypeEnum.TALISMAN_IMMORTAL:
			effect = list( talismanItem.getImmortalEffect() )
			func = talismanItem.setImmortalEffect
		elif useGrade == ItemTypeEnum.TALISMAN_DEITY:
			effect = list( talismanItem.getDeityEffect() )
			func = talismanItem.setDeityEffect
		if len( effect ) == 0: return

		newData = None
		gIndex = 0
		for index, data in enumerate( effect ):
			key, state = data
			if state: continue
			newData = ( key, True )
			effect.pop( index )
			effect.insert( index, newData )
			gIndex = index
			break

		# 表示没有需要激活的属性
		if newData is None:
			self.statusMessage( csstatus.TALISMAN_GRADE_NONEED )
			return

		srcItem.setAmount( srcItem.getAmount() -1, self, csdefine.DELETE_ITEM_ACTIVATETALISMANATTR )
		# 生效激活的属性
		func( effect, self )
		key, state = newData
		# 获取属性脚本
		effectKey =  g_talisman.getEffectID( key )
		effectClass = g_equipEffect.getEffect( effectKey )
		if effectClass is None: return
		# 计算附加属性
		initEffectValue = g_talisman.getInitValue( key )
		param = g_talisman.getUpParam( key )
		value = initEffectValue + talismanItem.getLevel() * param
		# 附加属性
		effectClass.attach( self, value, talismanItem )
		# 重新计算属性,Note: 不应该这么做,yk 2009-4-16 16:29
		self.calcDynamicProperties()

		self.client.onActivatyAttrCB( useGrade, gIndex )
		# 通知客户端激活属性成功
		self.statusMessage( csstatus.TALISMAN_AC_SUCCESS )

	def rebuildTalismanAttrInterface( self, grades, indexs ):
		"""
		改造法宝属性
		"""
		if len( grades ) == 0 or len( indexs ) == 0: return
		# 判断物品是否存在
		order = ItemTypeEnum.CWT_TALISMAN
		talismanItem = self.getItem_( order )
		if talismanItem is None:
			self.statusMessage( csstatus.TALISMAN_NO_WIELD )
			return
		# 判断是不是法宝类型
		if talismanItem.getType() != ItemTypeEnum.ITEM_SYSTEM_TALISMAN:
			self.statusMessage( csstatus.TALISMAN_SHAN_ZHAI )
			return

		# 判断玩家携带的材料是否足够
		reDatas = {}
		for grade in grades:
			rebuildItemID = g_talisman.getRebuildItem( grade )
			rAmount = g_talisman.getRebuildItemAmount( grade )
			if reDatas.has_key( rebuildItemID ):
				reDatas[rebuildItemID] += rAmount
			else:
				reDatas[rebuildItemID] = rAmount

		noteItemDatas = {}
		for itemID, amount in reDatas.iteritems():
			itemsList = self.findItemsByIDFromNKCK( itemID )
			noteItemDatas[itemID] = itemsList
			totalAmount = sum( [item.amount for item in itemsList] )
			if totalAmount < amount:
				self.statusMessage( csstatus.TALISMAN_REBUILDSTONE_LESS )
				return

		GRADE_GET_MAPS = { 	ItemTypeEnum.TALISMAN_COMMON 	: talismanItem.getCommonEffect,
							ItemTypeEnum.TALISMAN_IMMORTAL 	: talismanItem.getImmortalEffect,
							ItemTypeEnum.TALISMAN_DEITY 	: talismanItem.getDeityEffect,
							}

		GRADE_SET_MAPS = { 	ItemTypeEnum.TALISMAN_COMMON 	: talismanItem.setCommonEffect,
							ItemTypeEnum.TALISMAN_IMMORTAL 	: talismanItem.setImmortalEffect,
							ItemTypeEnum.TALISMAN_DEITY 	: talismanItem.setDeityEffect,
							}
		data = []
		# 开始改造属性
		for grade, index in zip( grades, indexs ):
			func = GRADE_GET_MAPS.get( grade )
			if func is None: return
			effect = list( func() )
			if len( effect ) <= index: return
			data.append( ( grade, effect[index], index ) )
		if len( data ) == 0: return

		isCalc = False
		for grade, effect, index in data:
			key, state = effect
			newKey = g_talisman.getEffects( grade )
			if newKey == key: continue
			newEffect = list( GRADE_GET_MAPS.get( grade )() )
			newEffect[index] = ( newKey, state )
			GRADE_SET_MAPS[grade]( newEffect, self )
			# 如果当前的属性石已激活的，则要做一些事情
			if not state: continue
			# 表示有属性改变了，需要实时计算玩家属性
			isCalc = True
			effectKey =  g_talisman.getEffectID( key )
			effectClass = g_equipEffect.getEffect( effectKey )
			newEffectKey =  g_talisman.getEffectID( newKey )
			newEffectClass = g_equipEffect.getEffect( newEffectKey )
			if ( effectClass is None ) or ( newEffectClass is None ): continue
			tmLevel = talismanItem.getLevel()
			# 卸载旧属性
			initEffectValue = g_talisman.getInitValue( key )
			param = g_talisman.getUpParam( key )
			value = initEffectValue + tmLevel * param
			effectClass.detach( self, value, talismanItem )
			# 加载新属性
			newInitEffectValue = g_talisman.getInitValue( newKey )
			newParam = g_talisman.getUpParam( newKey )
			newValue = newInitEffectValue + tmLevel * newParam
			newEffectClass.attach( self, newValue, talismanItem )
		if isCalc:
			# 重新计算属性
			self.calcDynamicProperties()

		# 到这里就算改造成功了，把材料都删除了
		for itemID, items in noteItemDatas.iteritems():
			needItemAmount = reDatas[itemID]
			for item in items:
				if needItemAmount <= 0: break
				amount = item.amount
				if amount <= needItemAmount:
					item.setAmount( 0, self, csdefine.DELETE_ITEM_REBUILDTALISMANATTR )
					needItemAmount -= amount
				else:
					item.setAmount( amount - needItemAmount, self, csdefine.DELETE_ITEM_REBUILDTALISMANATTR )
					break
		# 改造成功 客户端的显示更新放到完成改造后 读取法宝属性做界面更新 by姜毅
		self.client.onRebuildAttrCB( 0, 0, 0 )
		self.statusMessage( csstatus.TALISMAN_REBUILD_SUCCESS )

	def reloadTalismanSkillInterface( self ):
		"""
		重新刷技能
		"""
		# 判断物品是否存在
		order = ItemTypeEnum.CWT_TALISMAN
		talismanItem = self.getItem_( order )
		if talismanItem is None:
			self.statusMessage( csstatus.CIB_MSG_ITEM_NOT_EXIST )
			return

		# 判断是不是法宝类型
		if talismanItem.getType() != ItemTypeEnum.ITEM_SYSTEM_TALISMAN:
			self.statusMessage( csstatus.TALISMAN_SHAN_ZHAI )
			return

		# 查找玩家身上是否有相对应的材料物品
		needItemID = csconst.TALISMAN_UPDATE_SKILL_ID
		needItem = self.findItemFromNKCK_( needItemID )
		if needItem is None:
			self.statusMessage( csstatus.TALISMAN_UPDATE_SKILL_NEED )
			return

	def equipGodWeaponInterface( self, weaponItem ):
		"""
		神器炼制
		"""
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return
		level = weaponItem.getReqLevel()
		if level < 50:
			return
		quality = weaponItem.getQuality()
		if quality != ItemTypeEnum.CQT_GREEN:
			return
		stuffs = equipGodExp.getGodWeaponStuff( level )
		if len( stuffs ) <= 0:
			return
		c_item_id = stuffs[0]	# 神器普物品ID
		x_item_id = stuffs[1]	# 刑天石物品ID
		c_items = self.findItemsByIDFromNKCK( c_item_id )
		if len( c_items ) <= 0:
			return
		x_items = self.findItemsByIDFromNKCK( x_item_id )
		if len( x_items ) <= 0:
			return
		needAmount = stuffs[2]	# 所需刑天石数量
		totalAmount = 0
		for xi in x_items:
			if xi.isFrozen():
				ERROR_MSG( "equip god weapon make item %s %i is fozen."%( xi.name(), xi.uid ) )
				return
			totalAmount += xi.getAmount()
		if totalAmount < needAmount:
			return
		c_item = c_items[0]
		if c_item.isFrozen():
			ERROR_MSG( "equip god weapon make item %s %i is fozen."%( c_item.name(), c_item.uid ) )
			return

		weaponItem2 = weaponItem.new()
		self.removeItem_( weaponItem.getOrder(), reason = csdefine.DELETE_ITEM_GOD_WEAPON_MAKE )
		# 消耗神器普
		self.removeItem_( c_item.getOrder(), reason = csdefine.DELETE_ITEM_GOD_WEAPON_MAKE )
		# 消耗刑天石
		for xi in x_items:
			amount = xi.getAmount()
			if amount > needAmount:
				self.removeItem_( xi.getOrder(), needAmount, reason = csdefine.DELETE_ITEM_GOD_WEAPON_MAKE )
				break
			else:
				self.removeItem_( xi.getOrder(), reason = csdefine.DELETE_ITEM_GOD_WEAPON_MAKE )
				needAmount -= amount

		skillID = equipGodExp.getGodWeaponSkill( level )	# 制作出来的神器在指定的技能列表中进行随机，属性可以向下兼容。
		# 神器化
		weaponItem2.setGodWeapon( skillID )
		self.addItemAndNotify_( weaponItem2, csdefine.ADD_ITEM_GOD_WEAPON_MAKE )

		# 客户端表现和提示
		self.client.onEquipGodWeapon()
		# 老是给别人添麻烦的广播
		d_item = ChatObjParser.dumpItem( weaponItem2 )	# 用于物品消息链接
		self.base.chat_handleMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, "", cschannel_msgs.BCT_GOD_WEAPON%( self.getName(), "${o0}" ), [d_item,] )
		try:
			g_logger.equipGodLog( self.databaseID, self.getName(), weaponItem.uid, weaponItem2.uid, weaponItem.name(), weaponItem.getIntensifyLevel(), skillID )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )

	# ----------------------------------------------------------------
	# 装备制造
	# ----------------------------------------------------------------
	def equipMakeIntereface( self, makeItemID, orders ):
		"""
		装备制造
		@param makeItemID	: 要制造装备的ID
		@type  makeItemID	: ITEM_ID
		@param orders		: array of Uint8
		@type  orders		: order 列表
		@return Bool
		"""
		if self.actionSign( csdefine.ACTION_FORBID_TALK ):				#判断是否能跟NPC对话 完成操作
			self.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
			return
		mItems = {}
		stuffBind = False	#只要打造材料中，有一个是绑定材料，那么这次打造出的装备，即为拾取绑定属性。by姜毅
		for order in zip( orders ):
			item = self.getItem_( order[0] )
			if item is None: continue
			if item.isFrozen():		#被冻结的物品不能被npc打造商使用
				self.statusMessage( csstatus.CASKET_CANT_VENDSTATE )
				return False
			if item is None:
				ERROR_MSG( "%s(%i): no such Item( totId = %i )." % ( self.getName(), self.id, order ) )
				return False
			if item.isBinded():
				stuffBind = True
			if mItems.has_key( item.id ):
				mItems[item.id] += item.amount
			else:
				mItems[item.id] = item.amount

		if not g_equipMake.isCanMake( makeItemID, mItems ):
			self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False

		equip = self.createDynamicItem( makeItemID )

		pinkOdds = g_equipMake.getOdds( equip, mItems, ItemTypeEnum.CQT_PINK )
		goldOdds = g_equipMake.getOdds( equip, mItems, ItemTypeEnum.CQT_GOLD )
		blueOdds = g_equipMake.getOdds( equip, mItems, ItemTypeEnum.CQT_BLUE )
#		whiteOdds = g_equipMake.getOdds( equip, mItems, ItemTypeEnum.CQT_WHITE )

		rate_ep = random.random()

		if rate_ep <= pinkOdds:		#新加规则，绿装不能打造出来，所以从粉装开始
			quality = ItemTypeEnum.CQT_PINK
			prefix = g_equipMake.getPrefix( quality, pinkOdds )
		elif rate_ep <= goldOdds:
			quality = ItemTypeEnum.CQT_GOLD
			prefix = g_equipMake.getPrefix( quality, goldOdds )
		elif rate_ep <= blueOdds:
			quality = ItemTypeEnum.CQT_BLUE
			prefix = g_equipMake.getPrefix( quality, blueOdds )
		else:
			quality = ItemTypeEnum.CQT_WHITE
			prefix = g_equipMake.getPrefix( quality, 0 )

		if equip is None: return False

		#装备制作收费了 by姜毅
		lvm = equip.getLevel()
		if lvm > 0 and lvm <= 50:    #1~50 1.1^道具等级*100
			money = int(1.1 ** lvm * 100)
		else:           #51~150 1.03^道具等级*2700
			money = int(1.03 ** lvm * 2700)
		if not self.payMoney( money, csdefine.CHANGE_MONEY_EQUIPMAKE ):							#先交钱 后提货
			self.statusMessage( csstatus.EQUIP_REPAIR_NOT_ENOUGH_MONEY )
			return False

		for order in zip( orders ):
			self.removeItem_( order[0], reason = csdefine.DELETE_ITEM_EQUIPMAKE  )

		oldquality = equip.getQuality()
		oldprefix  = equip.getPrefix()
		equip.setQuality( quality )
		equip.setPrefix( prefix )
		if stuffBind:
			equip.setBindType( ItemTypeEnum.CBT_PICKUP )
		equip.createRandomEffect()
		equip.set( "creator", self.getName() )

		# 需求，打造装备等级取10整 by姜毅
		newReqLevel = equip.getReqLevel()/10*10
		if newReqLevel <= 0: newReqLevel = 1
		equip.setReqLevel( newReqLevel )

		self.addItem( equip, csdefine.ADD_ITEM_EQUIPMAKE )
		self.statusMessage( csstatus.CASKET_MAKE_SUCCESS )
		try:
			g_logger.equipMakeLog( self.databaseID, self.getName(), equip.uid, equip.name(), oldquality, equip.getQuality(), oldprefix, equip.getPrefix() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )
		
	def itb_changePropertyPrefix( self ):
		"""
		绿装洗前缀
		随机地改变绿装的附加属性前缀
		"""
		kitCasketItems = self.getCasketItems()
		greenEquips = []
		pinkEquips = []
		stuffItems = []
		mItems = {}
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
			self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return
		elif len( greenEquips ) != 1:
			self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return
		if len( pinkEquips ) != 2:
			self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return
		greenEquip = greenEquips[0]
		if not greenEquip.isSystemEquip():
			self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return
		stuff = g_changeProperty.getStuff()
		if mItems not in stuff:
			self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG  )
			return
		if not 60 <= greenEquip.getLevel() <= 149:
			self.statusMessage( csstatus.CASKET_MATIRAL_EQUIP_IS_WRONG )
			return
		for item in pinkEquips:
			if item.getLevel()/10 != greenEquip.getLevel()/10 or item.getWieldOrders() != greenEquip.getWieldOrders():
				self.statusMessage( csstatus.CASKET_PINK_EQUIP_IS_WRONG )
				return
		level = stuffItems[0].getLevel()
		if not( level <= greenEquip.getLevel() < level + 30 ):
			self.statusMessage( csstatus.CASKET_TOOL_LEVEL_IS_WRONG  )
			return

		newEquip = greenEquip.copy()
		self.removeItem_( greenEquip.order, reason = csdefine.DELETE_ITEM_CHANGEPROPERTY )
		self.removeItem_( stuffItems[0].order, reason = csdefine.DELETE_ITEM_CHANGEPROPERTY )
		for item in pinkEquips:
			self.removeItem_( item.order, reason = csdefine.DELETE_ITEM_CHANGEPROPERTY )
		newEquip.createRandomEffect()
		self.addItemByOrderAndNotify_( newEquip, self.getFreeOrderFK( csdefine.KB_CASKET_ID ), csdefine.ADD_ITEM_CHANGEPROPERTY )
		try:
			g_logger.equipChangePropertyLog( self.databaseID, self.getName(), greenEquip.uid, newEquip.uid, newEquip.name(), greenEquip.query("propertyPrefix",""), newEquip.query("propertyPrefix","") )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )
		return True

	# ----------------------------------------------------------------
	# 特殊材料合成
	# ----------------------------------------------------------------
	def specialStuffCompose( self, srcEntityID, uids ):
		"""
		
		特殊材料合成
		@return Bool
		"""
		if not self.hackVerify_( srcEntityID ) :
			self.client.unLockCasket()
			return
			
		try:
			kitCasketItem = self.kitbags[csdefine.KB_CASKET_ID]
		except KeyError:
			ERROR_MSG( "src(%i) Can't find kitCasket in kitbag %s" % ( self.id, csdefine.KB_CASKET_ID ) )
			return
		useDegree = kitCasketItem.getUseDegree()	#获得神机匣的使用次数
		if useDegree <= 0:
			self.statusMessage( csstatus.CASKET_CANT_USE )
			DEBUG_MSG( "(%s):kitCasket has been used out." % self.getName() )
			return
			
		itemList = [ self.getItemByUid_( uid ) for uid in uids ]
		if len( itemList ) == 0:
			# 请放入要灌注属性的装备
			self.statusMessage( csstatus.CASKET_PLAEASE_INPUT_EQUIP )
			return
		lvm = 0 #收费用的道具平均等级
		qua = 0 #收费用的道具平均品质
		if len( itemList ) == 0:
			self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
		mItems = {}
		lqItems = {}
		bindResult = False
		for item in itemList:
			if item.isFrozen():		#被冻结的物品不能被神机匣使用
				self.statusMessage( csstatus.CASKET_CANT_VENDSTATE )
				return False
			if not self.haveEnoughCredit( item ):
				self.statusMessage( csstatus.CIB_NO_ENOUGH_SPECIAL_COMPOSE_PRESTIGE )
				return False
			if mItems.has_key( item.id ):
				mItems[item.id] += item.amount
			else:
				mItems[item.id] = item.amount
			if not lqItems.has_key( item.id ):
				lqItems[item.id] = ( item.getLevel(), item.getQuality())
			if item.isType( ItemTypeEnum.ITEM_EQUIPMAKE_SCROLL ) and item.isBinded():
				bindResult = True

		dstInfo = g_stuffComp.getDstItemInfo( mItems )
		if not dstInfo:
			self.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return False
		itemInfo = dstInfo[0]
		propInfo = dstInfo[1]
		composeItemID, amount = itemInfo

		#--------------------------------------计算消耗的金钱-------
		for lqTuple in lqItems.values():
			lvm += lqTuple[0]
			qua += lqTuple[1]
		#特殊合成要收费啦 by姜毅
		lvm = int( lvm / len( mItems ) )
		qua = int( qua / len( mItems ) )
		if lvm > 0 and lvm <= 50:    #1~50 1.1^道具等级*100*品质/3
			money = 1.1 ** lvm * 100 * qua /3
		else:           #51~150 1.03^道具等级*2700 *品质/3
			money = 1.03 ** lvm * 2700 * qua /3
		if not self.payMoney( int( money )*amount, csdefine.CHANGE_MONEY_SPECIALCOMPOSE ):
			self.statusMessage( csstatus.CASKET_BIND_NEED_MONEY )
			return False

		#--------------------------------------移除材料--------------
		baseItems = g_stuffComp.getBaseMaterials( composeItemID )
		baseItem = {}						# baseItem需要消耗物品,such as: {40206001: 1, 80101002: 1, 80201002: 5, 80101026: 1, 80101014: 1}

		for element in baseItems:
			if set( mItems.keys() ) == set( element.keys() ):
				baseItem = element.copy()
				break

		for item in itemList:
			itemID = item.id
			if baseItem.has_key( itemID ) and baseItem[itemID] > 0:
				if item.amount >= baseItem[itemID]:
					self.removeItem_( item.order, baseItem[itemID], csdefine.DELETE_ITEM_SPECIALCOMPOSE )
					baseItem[itemID] = 0
				else:
					self.removeItem_( item.order, item.amount, csdefine.DELETE_ITEM_SPECIALCOMPOSE )
					baseItem[itemID] = baseItem[itemID] - item.amount

		#--------------------------------------创建合成品------------

		newItem = g_items.createDynamicItem( composeItemID )
		if newItem is None: return False
		newItem.setAmount( amount )

		# 应卷轴制作新需求 增加固定品质 前缀 属性前缀的设置 by姜毅
		if newItem.isEquip():
			quality = propInfo[0]
			prefix = propInfo[1]
			propPrefixID = propInfo[2]
			if prefix:
				newItem.setPrefix( prefix )
				if quality:
					newItem.setQuality( quality )
			if propPrefixID:
				newItem.fixedCreateRandomEffect(quality, prefix, propPrefixID, self) # 根据固定的前缀 品质 属性前缀 创建物品的随机属性
			# 需求，合成装备等级取10整 by姜毅
			newReqLevel = newItem.getReqLevel()/10*10
			if newReqLevel <= 0: newReqLevel = 1
			newItem.setReqLevel( newReqLevel )

		if bindResult == True:
			newItem.setBindType( ItemTypeEnum.CBT_PICKUP )

		self.addItemByOrderAndNotify_( newItem, self.getNormalKitbagFreeOrder(), csdefine.ADD_ITEM_SPECIALCOMPOSE )
		self.client.onCasketResult( 4 )
		
		#神机匣次数减1
		useDegree -= 1
		kitCasketItem.setUseDegree( useDegree )
		self.client.onUpdateUseDegree( useDegree )
		
		self.statusMessage( csstatus.MERGE_STUFF_SUCCEED )
		try:
			g_logger.equipStuffComposeLog( self.databaseID, self.getName(), newItem.uid, newItem.name() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )
		return True

	def getCasketItems( self, isCrys = False ):
		"""
		获取神机匣普通物品
		"""
		items = self.getItems( csdefine.KB_CASKET_ID )
		if isCrys: #如果是水晶摘除
			items = [item for item in items if item.getOrder()%csdefine.KB_MAX_SPACE >= csdefine.KB_CASKET_SPACE]
		else:
			items = [item for item in items if item.getOrder()%csdefine.KB_MAX_SPACE < csdefine.KB_CASKET_SPACE]
		return items
	