# -*- coding: gb18030 -*-
#
# $Id: Bank.py,v 1.22 2008-08-08 03:10:24 fangpengjun Exp $


import BigWorld
from bwdebug import *
import csconst
import csstatus
import csdefine
import ItemTypeEnum
import cschannel_msgs
import ShareTexts as ST

import time
import items
import sys

g_item = items.instance()

GOLD_ITEM_ID = 110103022	#元宝票

class Bank:
	"""
	钱庄系统接口

	bankLockerStatus表示钱庄密码锁状态的数据，密码锁的状态可以方便由此数据查询得出，不需要再def中声明过多的数据。规则如下：
	bankLockerStatus位长为8，使用其字节模式右边的第一位来表示钱庄是否设置密码的状态，当位字节模式为0时表示不锁定，为1时表示锁定；
	使用右边第二位来表示钱庄是否锁定的状态数据，设置则为0，否则为1。右边第三、四位考虑以后扩展需要。
	使用其右边第五、六、七位来表示钱庄解锁密码失败次数数据，最多可以表示7次失败，即字节模式为111，bankLockerStatus右移4位操作即可得操作数据，
	每失败一次可在移位后进行+1的10进制运算。

		钱庄密码锁状态数据bankLockerStatus的状态如下：
		0000 0000:无密码状态
		0000 0001:有密码状态
		0000 0010:锁定状态
		0111 0000:钱庄解锁失败次数
	"""
	def __init__( self ):
		"""
		"""
		#self.bankMoney 			# 钱庄存储的金钱，定义在def文件中
		#self.bagStatus 			# 钱庄包裹位状态，定义在def文件中
		#self.bankPassword			# 钱庄的密码数据，定义在def文件中
		#self.bankUnlockLimitTime	# 限制钱庄解锁行为时间，定义在def文件中

		# 初始化密码锁数据状态
		if self.bankPassword:		# 如果钱庄设置了密码
			self.bankLockerStatus |= 0x03	# 把字节模式设置为00000011

		if self.bankForceUnlockLimitTime > 0 :	# 如果玩家申请了强制解锁
			now = int( time.time() )
			forceUnlockLeaveTime = self.bankForceUnlockLimitTime - now
			if forceUnlockLeaveTime <= 0 : 			# 如果强制解锁时间已到
				self.__forceUnlockKitbag()			# 强制解锁背包
			else :
				self.__addForceUnlockTimer()		# 否则添加强制解锁的Timer

	def _isBankSetPassword( self ):
		"""
		验证是否设置了钱庄密码
		"""
		return not self.bankPassword == ""	# 表示密码存在与否状态的位是否为1

	def _isBankLocked( self ):
		"""
		验证钱庄是否被锁定
		"""
		return ( self.bankLockerStatus >> 1 ) & 0x01 == 1	# 表示钱庄是否被锁定与否状态位是否为1

	def _bankOperateVerify( self, srcEntityID, entityID ):
		"""
		验证是否能够进行钱庄操作

		@param entityID:寄卖npc的id
		@type entityID: OBJECT_ID
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return False
		npc = BigWorld.entities.get( entityID )
		if npc == None:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return False

		# 判断是否在允许交易范围内
		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.BANK_TRADER_TOO_FAR )
			DEBUG_MSG( "too far from trade npc: %i. ( srcEntityID: %s )" % ( entityID, self.playerName ) )
			return False

		if self._isBankLocked():
			self.statusMessage( csstatus.BANK_ITEM_CANNOT_MOVE )
			DEBUG_MSG( "钱庄被上锁了。" )
			return False

		if self.actionSign( csdefine.ACTION_FORBID_TALK ):				#判断是否能跟NPC对话 完成操作
			self.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
			return False
		
		statusID = npc.getScript().canUseBank( npc, self )
		if statusID != csstatus.BANK_CAN_USE:
			self.statusMessage( statusID )
			return False
			
		return True

	def _getRequireItemCount( self ):

		items = self.findItemsByIDFromNKCK( csdefine.ID_OF_ITEM_OPEN_BAG )
		count = 0
		for item in items:
			count += item.amount
		return count

	def bank_canActivateBag( self,amount ):
		"""
		判断是否能够激活包裹。
		"""
		return True

	def bank_activateBag( self, srcEntityID ):
		"""
		Exposed method.
		激活包裹
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return False
		# 判断包裹是否被锁住了
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return
		count = self._getRequireItemCount()
		self.base.bank_activateBag( count )

	def onBank_activateBagSuccess( self, itemAmount ):
		# 主要是用来给base提供的调用接口。
		# 激活仓库成功时用来处理剩下要做的事
		# @param:itemAmount		激活包裹后应该删除多少个金丝木
		# @type: int

		items = self.findItemsByIDFromNKCK( csdefine.ID_OF_ITEM_OPEN_BAG )
		# 为了防止金丝木等材料分堆时扣去问题 做一些处理 by姜毅
		if len( items ) > 1:
			for item in items:
				amount = item.getAmount()
				if itemAmount <= 0: break
				if amount > itemAmount: amount = itemAmount
				itemAmount -= amount
				self.removeItemByUid_( item.uid, amount, csdefine.DELETE_ITEM_ACTIVATEBAG )
		else:
			self.removeItemByUid_( items[0].uid,itemAmount, csdefine.DELETE_ITEM_ACTIVATEBAG )

	def bank_unfreezeBag( self, kitbagNum ):
		"""
		Define method.
		提供给base的回来解锁背包中被锁定包裹的接口

		param kitbagNum:背包包裹位号
		type kitbagNum:	UINT8
		"""
		if self.kitbags[kitbagNum].isFrozen():
			self.kitbags[kitbagNum].unfreeze()

	#------------------------------------往钱庄里存物品 BEGIN------------------------------
	def bank_storeItemFailed( self, itemOrder ):
		"""
		Define method.
		存储物品到钱庄失败

		@param itemOrder : 没存储成功的物品order
		@type itemOrder : INT16
		"""
		item = self.getItem_( itemOrder )
		if item is None:
			ERROR_MSG( "player( %s ) can not find item( order : %i )." % ( self.getName(), itemOrder) )
		else:
			item.unfreeze()

	def bank_storeItem2Order( self, srcEntityID, srcOrder, dstOrder, entityID ):
		"""
		Exposed method.
		往钱庄里存储物品的接口，已知目标物品格

		param srcOrder:	格子号
		type srcOrder:	INT16
		param bankBagNum:钱庄包裹位号
		type bankBagNum:UINT8
		param dstOrder:	格子号
		type dstOrder:	INT16
		param entityID:	钱庄npc的id
		type entityID:	OBJECT_ID
		"""
		if not self._bankOperateVerify( srcEntityID, entityID ):
			return
		if self.iskitbagsLocked():	# 背包上锁，by姜毅
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return

		kitbagNum = srcOrder / csdefine.KB_MAX_SPACE
		try:
			kitbag = self.kitbags[kitbagNum]
		except KeyError:
			ERROR_MSG( "包裹位置出错kitbagNum(%i)" % ( kitbagNum ) )
			return
		if kitbag.isFrozen():
			WARNING_MSG( "包裹被锁定。" )
			return
		if dstOrder % csdefine.KB_MAX_SPACE >= csconst.BANKBAG_NORMAL_ORDER_COUNT:
			HACK_MSG( "玩家(%s)钱庄格子位置( %i )不对。" % ( self.getName(), dstOrder ) )
			return

		item = self.getItem_(  srcOrder )
		if item is None:
			DEBUG_MSG( "物品不存在" )
			return
		if item.isFrozen():
			WARNING_MSG( "物品被锁定." )
			return
		if not item.canStore():
			self.statusMessage( csstatus.BANK_KITBAG_ITEM_UNSTOREABLE )
			return
		item.freeze()

		# 取得一份干净的物品数据发给base
		self.base.bank_storeItem2Order( srcOrder, item.copy(), dstOrder )

	def bank_storeItem2Bank( self, srcEntityID, srcOrder, entityID ):
		"""
		Exposed method.
		往钱庄里存储物品的接口，不指定包裹位与目标格子，在钱庄里查找第一个空位
		右键点击存储物品的接口

		param dstOrder:	格子号
		type dstOrder:	INT16
		param entityID:	钱庄npc的id
		type entityID:	OBJECT_ID
		"""
		if not self._bankOperateVerify( srcEntityID, entityID ):
			return
		if self.iskitbagsLocked():	# 背包上锁，by姜毅
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return

		kitbagNum = srcOrder / csdefine.KB_MAX_SPACE
		try:
			kitbag = self.kitbags[kitbagNum]
		except KeyError:
			ERROR_MSG( "包裹位置出错kitbagNum(%i)" % ( kitbagNum ) )
			return
		if kitbag.isFrozen():
			WARNING_MSG( "包裹被锁定。" )
			return
		item = self.getItem_(  srcOrder )
		if item is None:
			ERROR_MSG( "物品位置出错srcOrder(%i)" % ( srcOrder ) )
			return
		if item.isFrozen():
			WARNING_MSG( "物品被锁定." )
			return
		if not item.canStore():
			self.statusMessage( csstatus.BANK_KITBAG_ITEM_UNSTOREABLE )
			return
		item.freeze()
		self.base.bank_storeItem2Bank( srcOrder, item.copy() )

	def bank_storeItem2Bag( self, srcEntityID, srcOrder, bankBagNum, entityID ):
		"""
		Exposed method.
		往钱庄里存储物品的接口，仅指定了包裹位

		param kitbagNum:背包包裹位号
		type kitbagNum:	UINT8
		param dstOrder:	格子号
		type dstOrder:	INT16
		param bankBagNum:钱庄包裹位号
		type bankBagNum:UINT8
		param entityID:	钱庄npc的id
		type entityID:	OBJECT_ID
		"""
		if not self._bankOperateVerify( srcEntityID, entityID ):
			return
		if self.iskitbagsLocked():	# 背包上锁，by姜毅
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return
		if bankBagNum < csdefine.BANK_COMMON_ID or bankBagNum >= csdefine.BANK_COUNT:		# 包裹位参数检查
			HACK_MSG( "包裹位参数非法bankBagNum(%i)." % ( bankBagNum ) )
			return
		kitbagNum = srcOrder / csdefine.KB_MAX_SPACE
		try:
			kitbag = self.kitbags[kitbagNum]
		except KeyError:
			ERROR_MSG( "包裹位置出错kitbagNum(%i)" % ( kitbagNum ) )
			return
		if kitbag.isFrozen():
			WARNING_MSG( "包裹被锁定。" )
			return
		item = self.getItem_( srcOrder )
		if item is None:
			ERROR_MSG( "物品位置出错srcOrder(%i)" % ( srcOrder ) )
			return
		if item.isFrozen():
			WARNING_MSG( "物品被锁定." )
			return
		if not item.canStore():
			self.statusMessage( csstatus.BANK_KITBAG_ITEM_UNSTOREABLE )
			return
		item.freeze()
		self.base.bank_storeItem2Bag( srcOrder, item.copy(), bankBagNum )

	def bank_storeItemSuccess01( self, dstOrder ):
		"""
		Define method.
		往钱庄空位存储一个物品成功，回cell解锁并删除物品
		给base的,背包往钱庄存储一个物品成功的回调函数
		"""
		item = self.getItem_( dstOrder )
		if self.deleteItem_( dstOrder, reason = csdefine.DELETE_ITEM_STOREITEM ):
			self.statusMessage( csstatus.CIB_MSG_STORE_ITEMS_TO_BANK,item.name(),item.amount )

	def bank_storeItemSuccess02( self, dstOrder, item ):
		"""
		Define method.
		叠加一个物品有剩余，或与钱庄目标格子交换物品，把剩余物品或交换的物品放回背包
		给base的,背包往钱庄存储一个物品成功的回调函数
		"""
		kitbagNum = dstOrder / csdefine.KB_MAX_SPACE
		item1 = self.getItem_( dstOrder )
		if self.deleteItem_( dstOrder, reason = csdefine.DELETE_ITEM_STOREITEM  ):
			addResult = self.addItemByOrder_( item, dstOrder, reason = csdefine.ADD_ITEM_STOREITEM )
			if addResult == csdefine.KITBAG_ADD_ITEM_SUCCESS:
				if item1.id == item.id:
					amount = item1.amount - item.amount
					if amount > 0:
						statusID = csstatus.CIB_MSG_STORE_ITEMS_TO_BANK
					else:
						amount = -amount
						statusID = csstatus.CIB_MSG_FETCH_ITEMS_FROM_BANK
					self.statusMessage( statusID, item1.name(), amount )
				else:
					self.statusMessage( csstatus.CIB_MSG_STORE_ITEMS_TO_BANK, item1.name(),item1.amount )
					self.statusMessage( csstatus.CIB_MSG_FETCH_ITEMS_FROM_BANK, item.name(),item.amount )
		else:
			# 按理说这里不应该会出错，如果出错了可能有BUG
			ERROR_MSG( "当向背包里增加一个道具时失败。kitTote = %i, kitName = %s, orderID = %i" % (kitbagNum, self.kitbags[kitbagNum].srcID, dstOrder) )

	#------------------------------------往钱庄里存物品 END------------------------------


	#------------------------------------物品从钱庄取出 BEGIN------------------------------
	def bank_fetchItem2Order( self, srcEntityID, srcOrder, dstOrder, entityID ):
		"""
		左键拖钱庄物品栏物品到确定的背包物品格

		param dstOrder:	格子号
		type dstOrder:	INT16
		param dstOrder:	格子号
		type dstOrder:	INT16
		param entityID:	钱庄npc的id
		type entityID:	OBJECT_ID
		"""
		if not self._bankOperateVerify( srcEntityID, entityID ):
			return
		if self.iskitbagsLocked():	# 背包上锁，by姜毅
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return

		kitbagNum = dstOrder / csdefine.KB_MAX_SPACE
		try:
			kitbag = self.kitbags[kitbagNum]
		except KeyError:
			ERROR_MSG( "包裹位置出错kitbagNum(%i)" % ( kitbagNum ) )
			return
		if kitbag.isFrozen():
			WARNING_MSG( "包裹被锁定。" )
			return
		item = self.getItem_(dstOrder)
		if item and not item.canStore():
			self.statusMessage( csstatus.BANK_KITBAG_ITEM_UNSTOREABLE )
			return

		self.base.bank_fetchItem2Order( srcOrder, dstOrder )

	def bank_fetchItem2OrderCB( self, dstOrder, item, srcOrder ):
		"""
		Define method.
		被base的bank_fetchItem2Order调用，把base发过来的物品放置到目标物品格
		"""
		if not self._addItem2Order( dstOrder, srcOrder, item ):	# 添加失败
			self.base.bank_fetchItemFailed( srcOrder )
			return

	def _addItem2Order( self, dstOrder, bankOrder, srcItem ):
		"""
		把一个物品放到指定包裹的格子中,被bank_fetchItem2OrderCB调用
		成功则返回true，否则返回false

		param kitbag:	包裹实例
		type kitbag:	KITBAG
		param dstOrder:	格子号
		type dstOrder:		INT16
		"""
		if self.addItemByOrder_( srcItem, dstOrder, reason = csdefine.ADD_ITEM_ADDITEM2ORDER ) == csdefine.KITBAG_ADD_ITEM_SUCCESS:
			self.base.bank_fetchItemSuccess01( bankOrder )
			return True

		dstItem = self.getItem_( dstOrder )
		if dstItem.isFrozen():
			WARNING_MSG( "error code: ", csstatus.CIB_MSG_FROZEN )
			return False
		if not dstItem.canStore():
			self.statusMessage( csstatus.BANK_KITBAG_ITEM_UNSTOREABLE )
			return False
		if dstItem.id == srcItem.id and dstItem.isBinded() != srcItem.isBinded() and dstItem.getAmount() < dstItem.getStackable():
			self.statusMessage( csstatus.BANK_BIND_TYPE_CANT_STACKABLE )
			return False
		if dstItem.id == srcItem.id and dstItem.getStackable() > dstItem.amount:	# 可叠加道具特殊处理
			overlapAmount = dstItem.getStackable()
			dstAmount = dstItem.amount
			srcAmount = srcItem.amount
			storeAmount = min( overlapAmount - dstAmount, srcAmount )
			dstItem.setAmount( dstAmount + storeAmount, self, csdefine.ADD_ITEM_ADDITEM2ORDER )
			try:
				self.questItemAmountChanged( dstItem, dstItem.getAmount() )
			except:
				ERROR_MSG( "玩家( %s )从帮会仓库取物品到背包触发任务检测出错。" % self.getName() )
			srcAmount = srcAmount - storeAmount
			srcItem.setAmount( srcAmount )
			if srcAmount:	# 在目标位置叠加后还有剩余，放回仓库
				self.base.bank_fetchItemSuccess02( bankOrder, srcItem )
				return True
			self.base.bank_fetchItemSuccess01( bankOrder )
			return True
		else:	# id相同的不可叠加物品 与 id不同的可叠加物品 是交换操作
			if self.deleteItem_( dstOrder, reason = csdefine.DELETE_ITEM_STOREITEM  ):
				if self.addItemByOrder_( srcItem, dstOrder, reason = csdefine.ADD_ITEM_ADDITEM2ORDER )== csdefine.KITBAG_ADD_ITEM_SUCCESS:
					self.base.bank_fetchItemSuccess02( bankOrder, dstItem )
					return True
		return False

	def bank_fetchItem2Kitbags( self, srcEntityID, srcOrder, entityID ):
		"""
		Exposed method.
		从钱庄里取出物品的接口，不指定包裹位与目标格子，在背包里查找第一个空位

		param dstOrder:	格子号
		type dstOrder:	INT16
		param entityID:	钱庄npc的id
		type entityID:	OBJECT_ID
		"""
		if not self._bankOperateVerify( srcEntityID, entityID ):
			return
		if self.iskitbagsLocked():	# 背包上锁，by姜毅
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return
		order = self.getNormalKitbagFreeOrder()
		if order == -1:
			DEBUG_MSG( "玩家(%s)背包无空位。" % ( self.getName() ) )
			return
		self.base.bank_fetchItem2Kitbags( srcOrder )

	def bank_fetchItem2KitbagsCB( self, srcOrder, srcItem ):
		"""
		Define method.
		被base的bank_fetchItem2Kitbags调用，把base发过来的物品放置到包裹中
		"""
		if srcItem.getStackable() > 1:	# 可叠加道具特殊处理
			if self.stackableItem( srcItem, reason = csdefine.ADD_ITEM_FETCHITEM2KITBAGS  ) == csdefine.KITBAG_STACK_ITEM_SUCCESS:
				self.base.bank_fetchItemSuccess01( srcOrder )
				try:
					self.questItemAmountChanged( srcItem, srcItem.getAmount() )
				except:
					ERROR_MSG( "玩家( %s )从帮会仓库取物品到背包触发任务检测出错。" % self.getName() )
				return
		order = self.getNormalKitbagFreeOrder()		# getNormalKitbagFreeOrder()定义在itemBagRole.py中，在背包中查找空位
		if order == -1:
			self.base.bank_fetchItemFailed( srcOrder )
			self.statusMessage( csstatus.CIB_MSG_BAG_HAS_FULL )
			return
		addResult = self.addItemByOrder_( srcItem, order, reason = csdefine.ADD_ITEM_FETCHITEM2KITBAGS )
		if addResult == csdefine.KITBAG_ADD_ITEM_SUCCESS:
			self.base.bank_fetchItemSuccess01( srcOrder )

	#------------------------------------物品从钱庄取出 END------------------------------
	def bank_destroyItem( self, srcEntityID, order, entityID ):
		"""
		Exposed method.
		销毁物品的接口

		param kitbagNum:钱庄包裹位号
		type kitbagNum:UINT8
		param order:	格子号
		type order:	INT16
		param entityID:	钱庄npc的id
		type entityID:	OBJECT_ID
		"""
		if not self._bankOperateVerify( srcEntityID, entityID ):
			return
		self.base.bank_destroyItem( order )

	def bank_moveItem( self, srcEntityID, srcOrder, dstOrder, entityID ):
		"""
		Exposed method.
		在同一个包裹中移动物品的接口

		param bankBagNum:钱庄包裹位号
		type bankBagNum:UINT8
		param dstOrder:	格子号
		type dstOrder:	INT16
		param srcOrder:	格子号
		type srcOrder:	INT16
		param entityID:	钱庄npc的id
		type entityID:	OBJECT_ID
		"""
		if not self._bankOperateVerify( srcEntityID, entityID ):
			return
		self.base.bank_moveItem( srcOrder, dstOrder )

	def bank_storeMoney( self, srcEntityID, money, entityID ):
		"""
		Exposed method.
		玩家往钱庄存储金钱的接口

		param money：玩家要往钱庄存的金钱数目
		type money：UINT32
		"""
		if not self._bankOperateVerify( srcEntityID, entityID ):
			return
		if int( money ) > int( self.money ):	# 注意,money是无符号数
			self.statusMessage( csstatus.BANK_MONEY_NOT_ENOUGH_TO_STORE )
			return
		if self.iskitbagsLocked():	# 背包上锁，by姜毅
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return

		if money + self.bankMoney > csconst.BANK_MONEY_LIMIT:
			if self.bankMoney >=csconst.BANK_MONEY_LIMIT:		#如果钱庄本的存款来就大于上限 那么直接退出
				return
			temp = csconst.BANK_MONEY_LIMIT - self.bankMoney
			self.payMoney( temp, csdefine.CHANGE_MONEY_STORE)
			self.bankMoney = csconst.BANK_MONEY_LIMIT
			self.statusMessage( csstatus.BANK_MONEY_LIMIT )
			return

		self.payMoney( money, csdefine.CHANGE_MONEY_STORE )
		self.bankMoney = self.bankMoney + money

	def bank_fetchMoney( self, srcEntityID, money, entityID ):
		"""
		Exposed method.
		玩家从钱庄取出金钱的接口

		param money：玩家要取出的金钱数目
		type money：UINT32
		"""
		if not self._bankOperateVerify( srcEntityID, entityID ):
			return

		if self.iskitbagsLocked():	# 背包上锁，by姜毅
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return

		addMax = self.testAddMoney( int( money ) )			#可以加的钱的上限
		if addMax > 0:		#服务器上再次判断玩家取到钱后 是否会超过上限
			if self.ifMoneyMax():	#如果玩家携带金钱量已满 那么返回
				return
			money = int( money ) + addMax	#计算出可以加的金钱

		if int( money ) > int( self.bankMoney ):
			if self.gainMoney( self.bankMoney, csdefine.CHANGE_MONEY_FETCH ):
				self.bankMoney = 0
				return
			return

		if self.gainMoney( money, csdefine.CHANGE_MONEY_FETCH ):
			self.bankMoney = self.bankMoney - money
			return
		return

	# ------------------------------------------钱庄密码锁功能 BEGIN----------------------------------------
	def	bank_setPassword( self, srcEntityID, srcPassword, password, entityID ):
		"""
		Exposed method.
		设置、修改钱庄密码都使用此接口。钱庄密码为空时，srcPassword值为"",修改密码时srcPassword值为 玩家的旧密码

		param srcPassword:	钱庄原密码,
		type srcPassword:	STRING
		param password:	玩家输入的密码
		type password:	STRING
		param entityID:	钱庄npc的id
		type entityID:	OBJECT_ID
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		npc = BigWorld.entities.get( entityID )
		if npc == None:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return

		# 判断是否在允许交易范围内
		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.BANK_TRADER_TOO_FAR )
			DEBUG_MSG( "too far from trade npc: %i. ( srcEntityID: %s )" % ( entityID, self.playerName ) )
			return

		# 会有统一的判断entityID的方式

		if not cmp( srcPassword, self.bankPassword ) == 0:
			DEBUG_MSG( "玩家输入的旧密码不正确。" )
			if self.bankUnlockLimitTime > 0 and int( time.time() ) - self.bankUnlockLimitTime > 0:
				self.bankUnlockLimitTime = 0		# 过了解锁限制期限，取消限制
				self.bankLockerStatus |= 0x10		# 把右边第5位设置为1，表示第一次输错密码
				self.client.bank_lockerNotify( 3, 0 )	# 旧密码输错，需要通知玩家
				return
			if self.bankUnlockLimitTime == 0:		# 玩家不在解锁限制期限内
				temp = self.bankLockerStatus >> 4
				temp += 1
				if temp == 3:						# 如果输错密码次数达到3次
					self.bankUnlockLimitTime = int( time.time() ) + csconst.BANK_CANT_UNLOCK_INTERVAL	# 设置限制解锁期限为csconst.BANK_CANT_UNLOCK_INTERVAL
					self.bankLockerStatus &= 0x03	# 把密码输错次数清0，以便下次重新计算次数
					return
				temp <<= 4
				self.bankLockerStatus &= 0x03		# 保持最右边2位不变，把其他位置清0
				self.bankLockerStatus |= temp		# 密码锁状态变化，记录玩家输错密码的次数
				self.client.bank_lockerNotify( 3, 0 )	# 旧密码输错，需要通知玩家
				return
			self.client.bank_lockerNotify( 3, 0 )		# 在解锁限制期限内旧密码输错，需要通知玩家
			return

		if self.bankPassword == "":
			self.bankLockerStatus |= 0x01
			self.client.bank_lockerNotify( 0, 0 )		# 设置密码成功，通知客户端
		else:
			self.client.bank_lockerNotify( 1, 0 )		# 修改密码成功的通知

		self.bankPassword = password

	def bank_lock( self, srcEntityID, entityID ):
		"""
		Exposed method.
		给钱庄上锁，在玩家设置了密码且还没有对钱庄上锁的前提下，才满足此接口的使用条件

		param entityID:	钱庄npc的id
		type entityID:	OBJECT_ID
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		npc = BigWorld.entities.get( entityID )
		if npc == None:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return

		# 判断是否在允许交易范围内
		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.BANK_TRADER_TOO_FAR )
			DEBUG_MSG( "too far from trade npc: %i. ( srcEntityID: %s )" % ( entityID, self.playerName ) )
			return

		# 会有统一的判断entityID的方式

		if not self._isBankSetPassword():
			HACK_MSG( "钱庄没有密码。" )
			return

		if self._isBankLocked():
			HACK_MSG( "钱庄已经处于锁定状态。" )
			return

		self.bankLockerStatus |= 0x02		# 设置钱庄状态为锁定状态
		self.client.bank_lockerNotify( 4, 0 )

	def bank_unlock( self, srcEntityID, srcPassword, entityID ):
		"""
		Exposed method.
		给钱庄解锁，在玩家设置了钱庄密码且给钱庄上锁的前提下，才满足此接口的使用条件。
		注意：解锁的操作如果在本次登陆期间失败3次，csconst.BANK_CANT_UNLOCK_INTERVAL内不允许钱庄解锁操作。

		param srcPassword:	钱庄原密码,
		type srcsrcPassword:STRING
		param entityID:	钱庄npc的id
		type entityID:	OBJECT_ID
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		npc = BigWorld.entities.get( entityID )
		if npc == None:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return

		# 判断是否在允许交易范围内
		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.BANK_TRADER_TOO_FAR )
			DEBUG_MSG( "too far from trade npc: %i. ( srcEntityID: %s )" % ( entityID, self.playerName ) )
			return

		# 会有统一的判断entityID的方式

		if not self._isBankSetPassword():
			HACK_MSG( "钱庄没有密码。" )
			return

		if not self._isBankLocked():
			HACK_MSG( "钱庄已经处于非锁定状态。" )
			return

		if self.bankUnlockLimitTime > 0:
			if not int( time.time() ) > self.bankUnlockLimitTime:	# 这个检查也在客户端做，界面检查如果在限制期内则由界面通知玩家，服务器不需要通知
				remainTime = int( self.bankUnlockLimitTime - int( time.time() ) )
				self.client.bank_lockerNotify( 6, remainTime )
				DEBUG_MSG( "玩家处于csconst.BANK_CANT_UNLOCK_INTERVAL不允许解锁期间。" )
				return
			self.bankUnlockLimitTime = 0

		if not cmp( srcPassword, self.bankPassword ) == 0:
			DEBUG_MSG( "玩家输入的密码不正确。" )
			temp = self.bankLockerStatus >> 4
			temp += 1
			if temp == 3:	# 如果输错密码次数达到3次
				self.bankUnlockLimitTime = int( time.time() ) + csconst.BANK_CANT_UNLOCK_INTERVAL
				self.bankLockerStatus &= 0x03			# 把密码输错次数清0，以便下次重新计算次数
				self.client.bank_lockerNotify( 2, 0 )		# 输错解锁密码的通知
				return
			temp <<= 4
			self.bankLockerStatus &= 0x03				# 保持最右边2位不变，把其他位置清0
			self.bankLockerStatus |= temp				# 密码锁状态变化，记录玩家输错密码的次数
			self.client.bank_lockerNotify( 2, 0 )			# 输错解锁密码的通知
			return

		self.bankLockerStatus &= 0x03					# 成功开锁后,把密码输错次数清0(如果连续3次输错密码，则锁定)
		self.bankLockerStatus &= 0xfd					# 把右边第2位置0，表示钱庄处于非锁定状态
		self.client.bank_lockerNotify( 5, 0 )				# 通知客户端
		self.__cancelForceUnlock()						# 成功解锁则撤销强制解锁

	def bank_onForceUnlock( self, srcEntityID ) :
		"""
		Exposed method
		玩家请求强制解除背包锁定并清空密码
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		if self.bankForceUnlockLimitTime > 0 :			# 在强制解除锁定期限内，不再重复响应请求
			self.statusMessage( csstatus.BANK_FORCE_UNLOCK_REPEAT )
			return
		if not self.bankLockerStatus & 0x02 :			# 背包未锁上，不允许申请强制解锁
			self.statusMessage( csstatus.BANK_FORCE_UNLOCK_FORBID )
			return
		self.bankForceUnlockLimitTime = int( time.time() ) + csconst.BANK_FORCE_UNLOCK_LIMIT_TIME
		self.__addForceUnlockTimer()

	def bank_clearPassword( self, srcEntityID, srcPassword, entityID ):
		"""
		Exposed method.
		给钱庄永久解锁，玩家已经给钱庄设置了密码的前提下，此接口清除玩家设置的密码，把钱庄密码置为空。
		注意：永久解锁的操作如果在本次登陆期间失败3次，csconst.BANK_CANT_UNLOCK_INTERVAL内不允许钱庄解锁操作。

		param srcPassword:	钱庄原密码,
		type srcsrcPassword:STRING
		param entityID:	钱庄npc的id
		type entityID:	OBJECT_ID
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		npc = BigWorld.entities.get( entityID )
		if npc == None:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return

		# 判断是否在允许交易范围内
		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.BANK_TRADER_TOO_FAR )
			DEBUG_MSG( "too far from trade npc: %i. ( srcEntityID: %s )" % ( entityID, self.playerName ) )
			return

		# 会有统一的判断entityID的方式

		if not self._isBankSetPassword():
			HACK_MSG( "钱庄没有密码。" )
			return

		if self.bankUnlockLimitTime > 0:
			if int( time.time() ) <= self.bankUnlockLimitTime:	# 这个检查也在客户端做，界面检查如果在限制期内则由界面通知玩家，服务器不需要通知
				remainTime = int( self.bankUnlockLimitTime - int( time.time() ) )
				self.client.bank_lockerNotify( 6, remainTime )
				DEBUG_MSG( "玩家处于csconst.BANK_CANT_UNLOCK_INTERVAL不允许解锁期间。" )
				return
			self.bankUnlockLimitTime = 0

		if not cmp( srcPassword, self.bankPassword ) == 0:
			DEBUG_MSG( "玩家输入的旧密码不正确。" )
			temp = self.bankLockerStatus >> 4
			temp += 1
			if temp == 3:	# 如果输错密码次数达到3次
				self.bankUnlockLimitTime = int( time.time() ) + csconst.BANK_CANT_UNLOCK_INTERVAL
				self.bankLockerStatus &= 0x03			# 把密码输错次数清0，以便下次重新计算次数
				self.client.bank_lockerNotify( 2, 0 )		# 输错解锁密码的通知
				return
			temp <<= 4
			self.bankLockerStatus &= 0x03				# 保持最右边2位不变，把其他位置清0
			self.bankLockerStatus |= temp				# 密码锁状态变化，记录玩家输错密码的次数
			self.client.bank_lockerNotify( 2, 0 )			# 输错解锁密码的通知
			return

		self.bankPassword = ""
		self.bankLockerStatus &= 0x00
		self.bankUnlockLimitTime = 0					# 密码没有了，所有的密码锁相关数据都清0
		self.client.bank_lockerNotify( 7, 0 )
		self.__cancelForceUnlock()						# 成功解锁则撤销强制解锁

	def onBankForceUnlockTimer( self ) :
		"""
		强制解除背包锁定的timer到达
		"""
		self.__forceUnlockKitbag()

	def __forceUnlockKitbag( self ) :
		"""
		强制解锁背包
		"""
		self.bankPassword = ""								# 密码清空
		self.bankLockerStatus &= 0x00						# 背包解锁
		self.bankUnlockLimitTime = 0						# 锁定时间清零
		self.bankForceUnlockLimitTime = 0					# 强制解锁时间清零
		self.removeTemp( "bk_forceUnlock_timerID" )
		self.statusMessage( csstatus.BANK_FORCE_UNLOCK_SUCCESS )
		mailMgr = BigWorld.globalData["MailMgr"]
		content = cschannel_msgs.FORCE_UNLOCK_MAIL_CONTENT % cschannel_msgs.GMMGR_CANG_KU
		title = cschannel_msgs.FORCE_UNLOCK_MAIL_TITLE % cschannel_msgs.GMMGR_CANG_KU
		mailMgr.send( None,
					self.getName(),
					csdefine.MAIL_TYPE_QUICK,
					csdefine.MAIL_SENDER_TYPE_NPC,
					cschannel_msgs.SHARE_SYSTEM,
					title, content, 0, []
					)

	def __cancelForceUnlock( self ) :
		"""
		撤销强制解锁
		"""
		bk_forceUnlock_timerID = self.queryTemp( "bk_forceUnlock_timerID", 0 )
		if bk_forceUnlock_timerID > 0 :
			self.cancel( bk_forceUnlock_timerID )
			self.removeTemp( "bk_forceUnlock_timerID" )
		self.bankForceUnlockLimitTime = 0

	def __addForceUnlockTimer( self ) :
		"""
		添加强制解锁的timer
		"""
		now = int( time.time() )
		leaveTime = self.bankForceUnlockLimitTime - now
		if leaveTime <= 0 : return								# 时间已超过
		bk_forceUnlock_timerID = self.queryTemp( "bk_forceUnlock_timerID", 0 )
		if bk_forceUnlock_timerID > 0 : return					# 已添加了一个timer，不允许重复添加
		bk_forceUnlock_timerID = self.delayCall( leaveTime, "onBankForceUnlockTimer" )
		self.setTemp( "bk_forceUnlock_timerID", bk_forceUnlock_timerID )
		leaveHours = leaveTime / 3600
		leaveMinutes = leaveTime % 3600 / 60
		leaveSeconds = leaveTime % 60
		leaveText = ""
		if leaveHours :
			leaveText += "%d%s" % ( leaveHours, ST.CHTIME_HOUR )
		if leaveMinutes :
			leaveText += "%d%s" % ( leaveMinutes, ST.CHTIME_MINUTE )
		if leaveSeconds :
			leaveText += "%d%s" % ( leaveSeconds, ST.CHTIME_SECOND )
		self.delayCall( 1, "statusMessage", csstatus.BANK_FORCE_UNLOCK_REMAIN, leaveText )


	# ------------------------------------------钱庄密码锁功能 END----------------------------------------

	# -----------------------------------------以下功能由于界面的变化已经不用------------------------------


	def bank_changeGoldToItem( self, goldValue ):
		"""
		Define method.
		银票替换为金元宝票物品
		"""
		tempItem = items.instance().createDynamicItem( GOLD_ITEM_ID )
		tempItem.set( 'goldYuanbao', goldValue )
		if not self.addItemAndNotify_( tempItem, csdefine.ADD_ITEM_CHANGEGOLDTOITEM ):
			self.statusMessage( csstatus.KITBAG_IS_FULL )
			self.base.bank_changeGoldToItemCB( goldValue, False )
		else:
			self.base.bank_changeGoldToItemCB( goldValue, True )
			INFO_MSG( "---->>>玩家( %s ) 兑换元宝票( 数额：%i )成功。" % ( self.getName(), goldValue ) )

	# -----------------------------------------------------------------------------------------------------
#
# $Log: not supported by cvs2svn $
# Revision 1.21  2008/07/10 07:21:23  songpeifang
# 修正租用钱庄包裹位的时间为半年时，金钱不够却不输入提示的bug
#
# Revision 1.20  2008/07/07 11:04:24  wangshufeng
# method modify:bank_kitbagsOffload2Bank,修正卸下包裹到钱庄的代码错误。
#
# Revision 1.19  2008/07/03 04:50:39  songpeifang
# 修正bug：从钱庄物品栏拖包裹到背包包裹栏，如果需要交换物品，交换后钱庄物品栏客户端不刷新
#
# Revision 1.18  2008/07/02 07:07:18  songpeifang
# 修正了把物品从钱庄包裹栏拖入钱庄物品栏时物品都变成幻法行囊的bug
#
# Revision 1.17  2008/07/02 05:40:00  songpeifang
# 加入了包裹的装备绑定功能
#
# Revision 1.16  2008/05/30 03:00:02  yangkai
# 备栏调整，导致仓库调整
#
# Revision 1.15  2008/05/13 06:05:51  wangshufeng
# method modify:bank_splitItem,去掉目标包裹和目标格子参数，查找背包第一个空位放置拆分后的物品。
#
# Revision 1.14  2008/05/07 02:57:54  yangkai
# query( "stackable" ) -> getStackable()
#
# Revision 1.13  2008/04/19 07:33:20  wangshufeng
# 修正第一个包裹位需要租用才能使用的bug
#
# Revision 1.12  2008/04/03 06:31:05  phw
# KitbagBase::find2All()改名为find()，并更改返回值从原来的( order, toteID, itemInstance )改为itemInstance
# KitbagBase::findAll2All()改名为findAll()，并更改返回值从原来的( order, toteID, itemInstance )改为itemInstance
# 根据以上的变化，调整相关使用到以上接口的代码
#
# Revision 1.11  2008/03/27 08:16:01  wangshufeng
# 修正了_isRentBagPlace返回值不正确的bug
#
# Revision 1.10  2008/02/03 03:30:11  wangshufeng
# no message
#
# Revision 1.9  2008/01/22 04:01:49  wangshufeng
# method modify：bank_lock,bank_unlock成功上锁、解锁后调用kitbags_lockerNotify通知client
#
# Revision 1.8  2008/01/18 06:28:19  zhangyuxing
# 加入物品和移除物品的方式做了调整
#
# Revision 1.7  2007/12/22 09:50:09  fangpengjun
# 修改了bank_swapBag接口
#
# Revision 1.6  2007/12/11 06:50:52  wangshufeng
# add interface:_setBagData,把源包裹的物品数据转移给目标包裹.
#
# Revision 1.5  2007/12/05 03:20:30  wangshufeng
# no message
#
# Revision 1.4  2007/11/27 07:59:52  yangkai
# CIST_KITBAG --> ITEM_WAREHOUSE_KITBAG
# CIST_CASKET --> ITEM_WAREHOUSE_CASKET
#
# Revision 1.3  2007/11/27 03:41:10  wangshufeng
# no message
#
# Revision 1.2  2007/11/26 02:12:27  wangshufeng
# interface modify:bank_requireItemData -> bank_requireData
# interface modify:bank_unlockBag -> bank_unfreezeBag
#
# 增加了钱庄密码锁功能
#
# Revision 1.1  2007/11/14 02:56:35  wangshufeng
# 添加了钱庄系统
#
#
#
#