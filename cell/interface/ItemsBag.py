# -*- coding: gb18030 -*-
#
# $Id: ItemsBag.py,v 1.133 2008-09-02 00:54:37 songpeifang Exp $

"""
@summary				:	背包模块
"""

import time			# wsf
import cschannel_msgs
import ShareTexts as ST
import BigWorld
import Language
import csdefine
import csconst
import csstatus
import ChatObjParser
import ECBExtend
import items
import ItemTypeEnum
from bwdebug import *
from MsgLogger import g_logger
from ItemBagRole import ItemBagRole
from RoleSwapItem import RoleSwapItem
from RoleTradeWithNPC import RoleTradeWithNPC
from RoleTradeWithMerchant import RoleTradeWithMerchant
from RoleVend import RoleVend
import Math
from items.CueItemsLoader import CueItemsLoader
import sys
import Const
import csstatus_msgs
g_cueItem = CueItemsLoader.instance()

g_items = items.instance()


class ItemsBag( ItemBagRole, RoleSwapItem, RoleTradeWithNPC, RoleTradeWithMerchant, RoleVend ):
	"""
	这是一个背包类 for role of cell only。

	该类在初始化时会自动检查背包，并传手动传输给client。

	@ivar kitbags: 一个物品列表，用来存储物品
	@type kitbags: ITEMS
	@ivar mySIState:	1111 1111 -> 左4位表示目标, 右4位表示自己
						- 0	没有交易
						- 1	交易请求期,表示发起方已确认,等待确认目标
						- 2	交易中,正式开始交易
						- 3	确认
						- 4	再次确认
						- 5	确认锁定，当为此值时将不再接受取消交易要求
	@type mySIState: UINT8


	kitbagsLockerStatus表示背包密码锁状态的数据，密码锁的状态可以方便由此数据查询得出，不需要再def中声明过多的数据。规则如下：
	kitbagsLockerStatus位长为8，使用其字节模式右边的第一位来表示背包是否设置密码的状态，当位字节模式为0时表示不锁定，为1时表示锁定；
	使用右边第二位来表示背包是否锁定的状态数据，设置则为0，否则为1。右边第三、四位考虑以后扩展需要。
	使用其右边第五、六、七位来表示背包解锁密码失败次数数据，最多可以表示7次失败，即字节模式为111，kitbagsLockerStatus右移4位操作即可得操作数据，
	每失败一次可在移位后进行+1的10进制运算。

	背包密码锁状态数据kitbagsLockerStatus的状态如下（界面实现时可参考）：
	0000 0000:无密码状态
	0000 0001:有密码状态
	0000 0010:锁定状态
	0111 0000:背包解锁失败次数
	
	kitbags :包裹（这里的包裹是一个物品）集：包括装备栏（14个格子）、原始包裹（42个格子）、3个小包（格子不定）
	kitbag  :包裹：可以是装备栏、原始包裹、小包。kitbags是由kitbag组成的,是一个容器
	kbItem  :包裹类型的物品
	itemsBag:物品集（泛指背包）：所有包裹（这里的包裹是一个物品容器）的物品集合
	kitTote :包裹位：原始背包下面的3个包裹位
	item    :泛指背包中的物品
	"""
	def __init__( self ):
		"""
		"""
		RoleVend.__init__( self )

		#self.kitbagsPassword			# 背包的密码数据，定义在def文件中
		#self.kitbagsUnlockLimitTime	# 限制背包解锁行为时间，定义在def文件中

		# 初始化密码锁数据状态
		if self.kitbagsPassword:		# 如果背包设置了密码
			self.kitbagsLockerStatus |= 0x03	# 把字节模式设置为00000011

		if self.kitbagsForceUnlockLimitTime > 0 :	# 如果玩家申请了强制解锁
			now = int( time.time() )
			forceUnlockLeaveTime = self.kitbagsForceUnlockLimitTime - now
			if forceUnlockLeaveTime <= 0 : 			# 如果强制解锁时间已到
				self.__forceUnlockKitbag()			# 强制解锁背包
			else :
				self.__addForceUnlockTimer()		# 否则添加强制解锁的Timer

	def onDestroy( self ):
		"""
		当销毁的时候做点事情
		"""
		pass

	# -----------------------------------------------------------------------------------------------------
	# 基本操作
	# -----------------------------------------------------------------------------------------------------
	def __addItem( self, orderID, itemInstance, reason ):
		"""
		往背包加物品
		"""
		if self.itemsBag.add( orderID, itemInstance ):
			try:
				uid = itemInstance.uid
				fullName = itemInstance.fullName()
				id = itemInstance.id
				amount = itemInstance.getAmount()
				g_logger.itemAddLog( self.databaseID, self.getName(), self.grade, reason, uid, fullName + "(%s)"%id, amount, self.getLevel() )	#加入物品
			except:
				g_logger.logExceptLog( GET_ERROR_MSG()  )
			return True
		else:
			return False
	
	def __removeItem( self, orderID, itemInstance, reason ):
		"""
		删除某物品
		"""
		if self.itemsBag.removeByOrder( orderID ):
			uid = itemInstance.uid
			fullName = itemInstance.fullName()
			id = itemInstance.id
			amount = itemInstance.getAmount()
			try:
				g_logger.itemDelLog( self.databaseID, self.getName(), self.grade, reason, uid, fullName + "(%s)"%id, amount )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG()  )
					
			return True
		else:
			return  False

	# -----------------------------------------------------------------------------------------------------
	# 添加物品
	# -----------------------------------------------------------------------------------------------------
	def requestItems( self ) :
		"""
		请求发送物品到客户端( hyw -- 2008.06.10 )
		"""
		self.setTemp( "itemsbag_init_item_order", 0 )
		self.addTimer( 0.0, csconst.ROLE_INIT_INTERVAL, ECBExtend.UPDATE_CLIENT_ITEMS_CBID )

	def onTimer_updateClientItems( self, timerID, cbid ) :
		"""
		分包发送物品( hyw -- 2008.06.10 )
		"""
		items = self.itemsBag.getDatas()
		count = len( items )
		startOrder = self.queryTempInt( "itemsbag_init_item_order" )
		endOrder = min( count, startOrder + 5 )							# 每次发 5 个
		for order in xrange( startOrder, endOrder ) :					# 一次发一小组物品
			item = items[order]
			if cschannel_msgs.ROLE_INFO_12 in item.name():									# 判断是否有带血商品
				self.showBloodItemFlag()								# 如果有带血商品则对玩家进行处理
			if item.id == 50201256 :									# 生命蘑菇,玩家头顶需要显示蘑菇标记
				self.tong_showFungusFlag()
			self.client.addItemCB( item )
		if endOrder < count :											# 如果还有剩余物品
			self.addTempInt( "itemsbag_init_item_order", 5 )			# 则索引指针下跳 5 格
		else :															# 如果没有剩余物品
			self.cancel( timerID )										# 删除更新 timer
			self.removeTemp( "itemsbag_init_item_order" )				# 删除临时索引指针
			self.client.onInitialized( csdefine.ROLE_INIT_ITEMS )		# 发送结束命令到客户端

	def requestKitbags( self ) :
		"""
		请求发送背包物品到客户端( hyw -- 2008.06.10 )
		"""
		for order, item in self.kitbags.iteritems() :
			self.client.addKitbagCB( order, item )
		self.client.onInitialized( csdefine.ROLE_INIT_KITBAGS )

	# -------------------------------------------------
	def addItem( self, itemInstance, reason ):
		"""
		Define method.
		给自己增加一个道具，如果失败则道具掉在地上。

		@param itemInstance: 被CItemProp类型解释的自定义类型道具实例
		@type  itemInstance: instance
		@return:             被声明的方法，没有返回值
		"""
		self.addItemAndNotify_( itemInstance, reason )
		# 失败则往地上扔
		#itemInstance.createEntity( self.spaceID, Math.Vector3( self.position ), self.direction )

	def addItem_( self, itemInstance, reason ):
		"""
		description: 加入某个道具实例,但不提示得到xx物品，要想顺便提示，请使用addItemAndNotify_
		@param itemInstance	: 继承于CItemBase的自定义道具实例
		@type  itemInstance	: CItemBase
		@return				: 成功则返回成功状态码，如果成功，则会自动通知client，失败则返回原因
		@rtype				: INT8
		"""
		if itemInstance is None: return csdefine.KITBAG_ADD_ITEM_FAILURE
		# phw: 加入物品uid重复的日志，以便于日后过滤异常日志时容易发现
		# 所以这里不用if来判断，而用assert
		# 事实证明，这里确实截获了不少uid相同的物品放入背包，
		# 因此，我们有理由相信某些代码还是存在问题。
		try:
			assert not self.itemsBag.hasUid( itemInstance.uid ), \
				"%s(%i): item uid duplicate. itemUID %s, srcItemID %s, dstItemID %s" % (
				self.getName(), self.id, itemInstance.uid, self.itemsBag.getByUid( itemInstance.uid ).id, itemInstance.id )
		except:
			EXCEHOOK_MSG()
			return csdefine.KITBAG_ADD_ITEM_FAILURE

		# 加入物品之前如果是拾取绑定或任务绑定则临时改变其绑定状态，以便正确的加入背包，如果加入失败，则需要取消绑定。9:40 2009-2-25，wsf
		bindType = itemInstance.getBindType()
		needCancelBindType = False
		if not itemInstance.isBinded() and bindType in [ ItemTypeEnum.CBT_PICKUP, ItemTypeEnum.CBT_QUEST ]:
			itemInstance.setBindType( bindType )
			needCancelBindType = True

		# 判断是否道具可叠加
		if itemInstance.getStackable() > 1:
			if self.stackableItem( itemInstance, reason ) == csdefine.KITBAG_STACK_ITEM_SUCCESS:
				self.questItemAmountChanged( itemInstance, itemInstance.getAmount() )
				return csdefine.KITBAG_ADD_ITEM_BY_STACK_SUCCESS

		# 接着取一个空位置
		orderID = self.getNormalKitbagFreeOrder()
		if orderID == -1:
			if needCancelBindType:
				itemInstance.cancelBindType()
			return csdefine.KITBAG_NO_MORE_SPACE

		# 最后交给addItemByOrder_处理
		addState = self.addItemByOrder_( itemInstance, orderID, reason )
		if addState != csdefine.KITBAG_ADD_ITEM_SUCCESS:
			if needCancelBindType:
				itemInstance.cancelBindType()
		return addState

	def addItemAndNotify_( self, itemInstance, reason ):
		"""
		description:添加物品，并给个提示信息
		"""
		addResut = self.addItem_( itemInstance, reason )
		if addResut in csconst.KITBAG_ADD_ITEM_SUCCESS_RESULTS:
			self.notifyPickupInfo( itemInstance, reason )
			self.client.playIconNotify( itemInstance )
			return True
		return False

	def addItemByOrder_( self, itemInstance, orderID, reason ):
		"""
		description: 往指定位置加入某个道具实例
		@param itemInstance: 继承于CItemBase的自定义道具实例
		@type  itemInstance: CItemBase
		@param orderID: 道具在背包里的位置
		@type  orderID: INT16
		@return:             成功则返回成功的状态码，如果成功，则会自动通知client，失败则返回底层返回的状态码
		@rtype:              INT8
		"""
		# 检查物品数量限制
		if not self.checkItemLimit( [itemInstance] ):
			return csdefine.KITBAG_ITEM_COUNT_LIMIT

		# 对于要加入的位置是背包 则对背包的剩余时间做判断 过期则不能加入 by姜毅
		dstKitID = orderID/csdefine.KB_MAX_SPACE
		kitItem = self.kitbags.get( dstKitID )

		# 判断背包使用期限 过期背包只能扔
		if kitItem.isActiveLifeTime():
			if time.time() > kitItem.getDeadTime():
				self.statusMessage( csstatus.CIB_MSG_TIME_OUT, kitItem.name() )
				return csdefine.KITBAG_ADD_ITEM_FAILURE

		# 此函数用做将物品实例加进包裹
		addResult = self.__addItem( orderID, itemInstance, reason )
		# 返回底层的状态，暂时由于底层只返回0或1，所以才这么做
		if not addResult:
			return csdefine.KITBAG_ADD_ITEM_FAILURE
		self.questItemAmountChanged( itemInstance, itemInstance.getAmount() )
		self.client.addItemCB( itemInstance )
		# 物品进入玩家包裹处理
		itemInstance.onAdd( self )
		self.kitbags_saveLater()
		return csdefine.KITBAG_ADD_ITEM_SUCCESS

	def addItemByOrderAndNotify_( self, itemInstance, orderID, reason ):
		"""
		description:在指定位置添加物品，并给个提示信息
		如果需要给出自己的提示，请直接调用addItemByOrder_
		"""
		addResut = self.addItemByOrder_( itemInstance, orderID, reason )
		if addResut == csdefine.KITBAG_ADD_ITEM_SUCCESS:
			self.notifyPickupInfo( itemInstance, reason )
			return True
		return False

	def addItemAndRadio( self, itemInstance, itemAddType = ItemTypeEnum.ITEM_GET_GM,  itemFromSpace = "", itemFromOwner = "", stuffItemName = "", insLevel = "", reason = csdefine.ITEM_NORMAL ):
		"""
		添加一个物品触发广播
		@param itemInstance	: 继承于CItemBase的自定义道具实例
		@type  itemInstance	: CItemBase
		@param itemAddType	: 物品的获得方式
		@type  itemAddType	: UINT8
		@param itemFromSpace: 物品的产出地
		@type  itemFromSpace: STRING
		@param itemFromOwner: 物品的产出者
		@type  itemFromOwner: STRING
		"""
		#装备强化使用其它添加方式 这个添加方式不适合 by姜毅
		if not itemAddType in [ ItemTypeEnum.ITEM_GET_EQUIP_INSTENSIFY, ItemTypeEnum.ITEM_GET_STUD ]:
			if not self.addItemAndNotify_( itemInstance, reason ): return False
			# 过了上面，都返回True
			if itemAddType == ItemTypeEnum.ITEM_GET_GM: return True
			if not g_cueItem.hasCueFlag( itemInstance.id, itemAddType ): return True
		else:
			if itemAddType == ItemTypeEnum.ITEM_GET_GM: return True
		msg = g_cueItem.getCueMsg( itemAddType )
		if msg is None: return True
		roleName = self.getName()
		itemName = itemInstance.fullName()
		# 处理物品名字颜色的改变
		itemName = csconst.ITEM_BROAD_COLOR_FOR_QUALITY[ itemInstance.getQuality() ] % itemName
		itemAmount = itemInstance.getAmount()
		i_Count = msg.count( "_t" ) + msg.count( "_i" )
		link_items = []
		if i_Count > 0:
			d_item = ChatObjParser.dumpItem( itemInstance )	# 用于物品消息链接
			for i in xrange( 0, i_Count ):
				link_items.append( d_item )
		msg = g_cueItem.getCueMsgString( _keyMsg = msg, _p = roleName, _a = itemFromSpace, _m = itemFromOwner, _i = "${o0}", _n = str( itemAmount ), _t = "${o0}", _s = stuffItemName, _q = insLevel )
		self.base.chat_handleMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, "", msg, link_items )
		return True

	def stackableItem( self , itemInstance, reason, kitTote =-1  ):
		"""
		description:物品进背包前进行的操作：看其能否与背包中的某个物品叠加。
					kitTote ==-1：表示在所有背包中找相同物品叠加
					kitTote !=-1：表示在指定背包中找相同物品叠加
		@param itemInstance: 继承于CItemBase的自定义道具实例
		@type  itemInstance: CItemBase
		@param kitTote: 背包的编号
		@type  kitTote: INT8
		@return: 叠加结果
		@rtype:  INT8
		"""
		# 检查物品数量限制
		if not self.checkItemLimit( [itemInstance] ):
			return csdefine.KITBAG_ITEM_COUNT_LIMIT

		itemList = []
		# 获得总数
		currtotal = 0
		# 单个叠加上限
		stackable = itemInstance.getStackable()
		itemAmount = itemInstance.getAmount()
		itemID = itemInstance.id
		# 是否绑定
		isBinded = itemInstance.isBinded()
		# 判断是否能叠加

		if kitTote != -1:
			if not self.canStackableInKit( itemID, isBinded, itemAmount, kitTote ):
				return csdefine.KITBAG_ADD_ITEM_FAILURE
			# 根据指定ID、包裹位、绑定类型获取物品实例列表
			itemList = self.getItemsFKWithBind( itemID, kitTote, isBinded )
		else:
			if not self.canStackable( itemID, isBinded, itemAmount ):
				return csdefine.KITBAG_ADD_ITEM_FAILURE
			# 根据指定ID、包裹位、绑定类型获取物品实例列表
			itemList = self.findItemsByIDWithBindFromNKCK( itemID, isBinded )
		# 计数
		currtotal = sum( [ k.getAmount() for k in itemList if not k.isFrozen() ] )

		if len( itemList ) == 0:
			return csdefine.KITBAG_STACK_ITEM_NO_SAME_ITEM

		val = len( itemList ) * stackable - currtotal		# 获取还可以叠加的数量
		val1 = itemInstance.getAmount()				# 获取这个物品的数量
		if val < val1:
			return csdefine.KITBAG_STACK_ITEM_NO_MORE
		for item in itemList:
			if item.isFrozen(): continue
			if val1 <= 0:break
			amount = stackable - item.getAmount()
			if amount > 0:
				if amount >= val1:
					item.setAmount( item.getAmount() + val1, self, reason )
					break
				else:
					item.setAmount( stackable , self, reason )
					val1 -= amount
		return csdefine.KITBAG_STACK_ITEM_SUCCESS


	def addItemByItemIDWithAmount( self, itemDict, bindType, reason ):
		"""
		通过物品ID为索引的相关列表数据（例如数量）来添加（一系列）物品 by 姜毅
		传入前先要按照参数格式封装好物品信息
		对于不能加入背包（例如空间已满）的物品则处理后返回
		@param itemDict : { itemID:Amount, ... }
		@type  itemDict : DICT
		@param isAllBinded : 绑定类型
		@type : INT8
		"""
		if type( itemDict ) is not dict: return
		if len( itemDict ) <= 0: return
		itemList = []
		for idt in itemDict:
			item = g_items.createDynamicItem( idt )
			if item is None: continue
			item.setAmount( itemDict[idt] )
			item.setBindType( bindType )
			itemList.append( item )

		checkRes = self.checkItemsPlaceIntoNK_( itemList )
		if checkRes != csdefine.KITBAG_CAN_HOLD: return itemList
		for item in itemList: self.addItem( item, reason )
		return None

	# -----------------------------------------------------------------------------------------------------
	# 移除物品
	# -----------------------------------------------------------------------------------------------------
	def removeItem_( self, orderID, amount = -1, reason = csdefine.DELETE_ITEM_NORMAL ):
		"""
		移去某道具

		@param orderID: 道具在背包里的位置
		@type  orderID: INT16
		@param amount: 需要删除的道具的数量
		@type  amount: INT16
		@param reason: 删除道具的原因
		@type  reason: INT16
		@return:        如果物品被删除则返回True,否则返回False
		@rtype:         BOOL
		"""
		item = self.itemsBag.getByOrder( orderID )
		if item is None: return False
		deleteAmount = self.deleteItem_( orderID, amount, True, reason )
		if deleteAmount:
			d_item = ChatObjParser.dumpItem( item )
			msg = csstatus_msgs.getStatusInfo( csstatus.CIB_MSG_LOST_ITEMS, "${o0}", deleteAmount ).msg
			self.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSTEM, 0, "", msg, [d_item] )
		item = None # 释放掉item

	def deleteItem_( self, orderID, amount = -1, questItemAmountChanged = True, reason = csdefine.DELETE_ITEM_NORMAL ):
		"""
		description: 删除某道具,没有提示消息
		@param orderID: 道具在背包里的位置
		@type  orderID: INT16
		@param amount: 需要删除的道具的数量，默认为-1，当数量为负数时，即把该位置道具全部删除，为0时不作为
		@type  amount: INT16
		@param questItemAmountChanged: 对任务的影响，话说不怎么觉得放这里合适。。。
		@type  questItemAmountChanged: BOOL
		@param reason: 删除道具的原因
		@type  reason: INT16
		@return:        如果物品被删除则返回删除的数量,否则返回False
		@rtype:         INT8
		"""
		if amount == 0: return False
		itemInstance = self.itemsBag.getByOrder( orderID )
		if itemInstance is None: return False
		itemAmount = itemInstance.getAmount()
		if amount < 0:
			amount = itemAmount
		remain = itemAmount - amount

		if remain < 0:
			return False
		if remain == 0:
			result = self.__removeItem( orderID, itemInstance, reason )
			if not result :
				return False
				
			itemInstance.onDelete( self )
			self.client.removeItemCB( orderID )
		else:
			itemInstance.setAmount( remain, self, reason )

		if questItemAmountChanged:
			self.questItemAmountChanged( itemInstance, -amount )
			
		self.kitbags_saveLater()
		return amount

	def removeItemByUid_( self, uid, amount = -1, reason = csdefine.DELETE_ITEM_NORMAL ):
		"""
		移去某背包上的某道具

		@param  uid: 道具在玩家身上的唯一标识
		@type   uid: INT64
		@return:        如果物品被删除则返回True,否则返回False
		@rtype:         BOOL
		"""
		orderID = self.itemsBag.getOrderID( uid )
		if orderID < 0: return
		return self.removeItem_( orderID, amount, reason )

	def removeItemTotal( self, itemKeyName, amount, reason ):
		"""
		移去与itemKeyName相同的物品amount个；

		@param itemKeyName: 表示每一类道具的唯一的道具类型
		@type  itemKeyName: str
		@param      amount: 欲删除的数量
		@type       amount: UINT16
		@return: 如果有这么多可以删除且被删除则返回True，否则返回False
		@return: True
		"""
		if not self.checkItemFromNKCK_( itemKeyName, amount ): return False
		rm = amount
		for item in self.findItemsFromNKCK_( itemKeyName ):
			im = item.getAmount()
			if im <= rm:
				rm -= im
				item.setAmount( 0, self, reason )
				if rm == 0:
					self.questItemAmountChanged( item, -amount )
					msg = csstatus_msgs.getStatusInfo( csstatus.CIB_MSG_LOST_ITEMS, "${o0}", amount ).msg
					self.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSTEM, 0, "", msg, [ChatObjParser.dumpItem( item )] )
					return True
			else:
				item.setAmount( item.getAmount() - rm, self, reason )
				self.questItemAmountChanged( item, -amount )
				msg = csstatus_msgs.getStatusInfo( csstatus.CIB_MSG_LOST_ITEMS, "${o0}", amount ).msg
				self.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSTEM, 0, "", msg, [ChatObjParser.dumpItem( item )] )
				return True
		return False

	def removeItemTotalWithNoBind( self, itemKeyName, amount, reason ):
		"""
		移去与itemKeyName相同的且未绑定的物品amount个；

		@param itemKeyName: 表示每一类道具的唯一的道具类型
		@type  itemKeyName: str
		@param      amount: 欲删除的数量
		@type       amount: UINT16
		@return: 如果有这么多可以删除且被删除则返回True，否则返回False
		@return: True
		"""
		if self.countItemTotalWithBinded_( itemKeyName, False ) < amount: return False
		rm = amount
		for item in self.findItemsEx_( csconst.KB_SEARCH_COMMON_AND_CASKET, itemKeyName ):
			if item.isBinded():
				continue

			im = item.getAmount()
			if im <= rm:
				rm -= im
				item.setAmount( 0, self, reason )
				if rm == 0:
					self.questItemAmountChanged( item, -amount )
					self.statusMessage( csstatus.CIB_MSG_LOST_ITEMS,  item.name(), amount )
					return True
			else:
				item.setAmount( item.getAmount() - rm, self, reason )
				self.questItemAmountChanged( item, -amount )
				self.statusMessage( csstatus.CIB_MSG_LOST_ITEMS,  item.name(), amount )
				return True
		return False


	# -----------------------------------------------------------------------------------------------------
	# client call method
	# ---------------------------------------------------------------------------------------------
	# 使用物品
	# ---------------------------------------------------------------------------------------------
	def useItem(self, srcEntityID, uid, targetObj ):
		"""
		Exposed method.
		对某人使用某道具

		@param srcEntityID: 使用者，必须与self.id一致
		@type  srcEntityID: int32
		@param  srcKitTote: 道具栏位置
		@type   srcKitTote: UINT8
		@param      uid: 道具唯一标识符
		@type       uid: INT64
		@param dstEntityID: 目标
		@type  dstEntityID: int32
		@return:            被声明的方法，没有返回值
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return False

		if self.iskitbagsLocked():
			DEBUG_MSG( "背包被上锁了。" )
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return False
		dstEntity = targetObj.getObject()
		if targetObj.type != csdefine.SKILL_TARGET_OBJECT_POSITION:
			if dstEntity is None:
				self.statusMessage( csstatus.CIB_MSG_INVALID_TARGET )
				return False
			if dstEntity.isDestroyed:
				self.statusMessage( csstatus.CIB_MSG_INVALID_TARGET )
				return False
		dstItem = self.itemsBag.getByUid( uid )
		if dstItem is None:
			self.statusMessage( csstatus.CIB_MSG_ITEM_NOT_EXIST )
			return False

		if dstItem.isFrozen():
			WARNING_MSG( "error code: ", csstatus.CIB_MSG_FROZEN )
			return False
		useResult = dstItem.use( self, dstEntity )
		if useResult != csstatus.SKILL_GO_ON and useResult is not None:
			self.statusMessage( useResult )
			return False
		return True

	def destroyItem( self, srcEntityID, uid ):
		"""
		Exposed method.
		销毁一个物品

		@param srcEntityID: 调用实体的ID号
		@type  srcEntityID: int32
		@param      uid: 道具唯一标识符
		@type       uid: INT64
		@return:            被声明的方法，没有返回值
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return

		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return False
		item = self.itemsBag.getByUid( uid )
		if item is None:
			self.statusMessage( csstatus.CIB_MSG_ITEM_NOT_EXIST )
			return False

		if item.isFrozen():
			self.statusMessage( csstatus.CIB_MSG_FROZEN )
			return False

		if not item.canDestroy():
			self.statusMessage( csstatus.CIB_MSG_CANNOT_DESTROY )
			return

		self.removeItemByUid_( uid, reason = csdefine.DELETE_ITEM_DESTROYITEM )
		return True

	def swapItem( self, srcEntityID, srcOrderID, dstOrderID ):
		"""
		Exposed method.
		交换两个道具的位置。

		需要考虑源背包和目标背包类型，有可能需要根据不同类型做出不同的操作

		@param srcEntityID: 调用实体的ID号
		@type  srcEntityID: int32
		@param  srcOrderID: 源背包的源道具
		@type   srcOrderID: INT8
		@param  dstOrderID: 目标背包的源道具
		@type   dstOrderID: INT8
		@return:            被声明的方法，没有返回值
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		self.swapItemAC( srcOrderID, dstOrderID )

	def swapItemAC( self, srcOrderID, dstOrderID ):
		"""
		交换两个道具的位置。
		"""
		if self.iskitbagsLocked():
			DEBUG_MSG( "背包被上锁了。" )
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return False
		srcKitID = srcOrderID/csdefine.KB_MAX_SPACE
		dstKitID = dstOrderID/csdefine.KB_MAX_SPACE
		kitItem = self.kitbags.get( dstKitID )

		# 判断背包使用期限 过期背包只能扔
		if kitItem.isActiveLifeTime():
			if time.time() > kitItem.getDeadTime():
				self.statusMessage( csstatus.CIB_MSG_TIME_OUT, kitItem.name() )
				return False

		if kitItem is None:
			self.statusMessage( csstatus.CIB_MSG_INVALID_KITBAG, dstKitID )
			return False

		srcItem = self.itemsBag.getByOrder( srcOrderID )
		dstItem = self.itemsBag.getByOrder( dstOrderID )
		# 防止两次连续点击时出现bug
		if srcItem is None:

			return False
		if (srcItem is not None and srcItem.isFrozen()) or (dstItem is not None and dstItem.isFrozen()):
			WARNING_MSG( "error code: ", csstatus.CIB_MSG_FROZEN )
			return False
		
		# 如果物品是从装备栏出来的，则需要考虑目标物品是否能放入装备栏
		if srcKitID == csdefine.KB_EQUIP_ID:
			if self.actionSign( csdefine.ACTION_FORBID_WIELD ):
				self.statusMessage( csstatus.KIT_EQUIP_CANT_STATE )
				return False
			if dstItem:
				state = self.canWieldEquip( srcOrderID, dstItem )
				if state != csstatus.KIT_EQUIP_CAN_FIT_EQUIP:
					self.statusMessage( state )
					return False

		# 如果物品要放到装备栏上，则需要考虑该物品是否能放入装备栏
		if dstKitID == csdefine.KB_EQUIP_ID:
			if self.actionSign( csdefine.ACTION_FORBID_WIELD ):
				self.statusMessage( csstatus.KIT_EQUIP_CANT_STATE )
				return False
			state = self.canWieldEquip( dstOrderID, srcItem )
			if state != csstatus.KIT_EQUIP_CAN_FIT_EQUIP:
				self.statusMessage( state )
				return False
		
		weaponOrders = [ ItemTypeEnum.CEL_LEFTHAND, ItemTypeEnum.CEL_RIGHTHAND ]
		if self.getClass() == csdefine.CLASS_FIGHTER and ( srcOrderID in weaponOrders or dstOrderID in weaponOrders ):
			l_item = self.itemsBag.getByOrder( ItemTypeEnum.CEL_LEFTHAND )
			r_item = self.itemsBag.getByOrder( ItemTypeEnum.CEL_RIGHTHAND )
			orderIDs = self.getAllNormalKitbagFreeOrders()
			
			if srcKitID == csdefine.KB_EQUIP_ID : #如果物品是从装备栏出来的
				if dstItem: #目标格子装备存在
					if srcItem.getType() != dstItem.getType(): #目标格子装备和源格子装备类型不一致
						if srcOrderID == ItemTypeEnum.CEL_LEFTHAND: #源格子装备来自左手
							self.statusMessage( csstatus.KIT_EQUIP_CANT_APP_ORDER )
							return False
						else: #源格子装备来自右手
							if l_item: #左手有盾
								if len( orderIDs ) < 1 :
									self.statusMessage( csstatus.CIB_MSG_UNWIELD_ITEM )
									return False
								else:
									flag1 = self.swapItemACBack( srcOrderID, dstOrderID )
									flag2 = self.swapItemACBack( ItemTypeEnum.CEL_LEFTHAND, orderIDs[0] )
									return flag1 and flag2
			
			if dstKitID == csdefine.KB_EQUIP_ID: #物品要放到装备栏上
				if dstItem: #目标格子装备存在
					if srcItem.getType() != dstItem.getType(): #目标格子装备和源格子装备类型不一致
						if dstOrderID == ItemTypeEnum.CEL_LEFTHAND: #目标格子是左手
							self.statusMessage( csstatus.KIT_EQUIP_CANT_APP_ORDER )
							return False
						else: #目标格子是右手
							if l_item: #左手有盾
								if len( orderIDs ) < 1 :
									self.statusMessage( csstatus.CIB_MSG_UNWIELD_ITEM )
									return False
								else:
									flag1 = self.swapItemACBack( srcOrderID, dstOrderID )
									flag2 = self.swapItemACBack( ItemTypeEnum.CEL_LEFTHAND, orderIDs[0] )
									return flag1 and flag2
				else:
					if l_item: #左手有盾
						if srcItem.getType() == ItemTypeEnum.ITEM_WEAPON_SPEAR2: #想装备枪
							flag1 = self.swapItemACBack( srcOrderID, dstOrderID )
							flag2 = self.swapItemACBack( ItemTypeEnum.CEL_LEFTHAND, srcOrderID )
							return flag1 and flag2
					else: #左手无盾
						if srcItem.getType() == ItemTypeEnum.ITEM_WEAPON_SHIELD and r_item and r_item.getType() == ItemTypeEnum.ITEM_WEAPON_SPEAR2: #目标格子是左手,并且右手为枪
							flag1 = self.swapItemACBack( srcOrderID, dstOrderID )
							flag2 = self.swapItemACBack( ItemTypeEnum.CEL_RIGHTHAND, srcOrderID )
							return flag1 and flag2	
		
		return self.swapItemACBack( srcOrderID, dstOrderID )
	
	def swapItemACBack( self, srcOrderID, dstOrderID ):
		"""
		交换两个道具的位置。
		"""
		srcKitID = srcOrderID/csdefine.KB_MAX_SPACE
		dstKitID = dstOrderID/csdefine.KB_MAX_SPACE
		srcItem = self.itemsBag.getByOrder( srcOrderID )
		dstItem = self.itemsBag.getByOrder( dstOrderID )
		
		if self.itemsBag.swapOrder( srcOrderID, dstOrderID ):
			self.client.swapItemCB( srcOrderID, dstOrderID )
			# 如果是相同背包移位，到此功能就结束了
			if srcKitID == dstKitID: return True
			# 移位成功才进行装备，通知客户端更换装备模型
			newEquip = None
			if srcKitID == csdefine.KB_EQUIP_ID:
				if srcItem: srcItem.unWield( self, update = False )
				if dstItem is not None:
					dstItem.wield( self, update = False )
					newEquip = dstItem
				self.resetEquipModel( srcOrderID, newEquip )
			if dstKitID == csdefine.KB_EQUIP_ID:
				if dstItem: dstItem.unWield( self, update = False )
				if srcItem is not None:
					srcItem.wield( self, update = False )
					newEquip = srcItem
				self.resetEquipModel( dstOrderID, newEquip )
			# 最后才计算属性
			self.calcDynamicProperties()
			return True
		else:
			WARNING_MSG( "error code: ", csstatus.CIB_MSG_KITBAG_NOT_ALLOW )
			return False

	def splitItem( self, srcEntityID, uid, amount ):
		"""
		Exposed method.
		分开一个可叠加的道具。

		需要考虑源背包和目标背包类型，有可能需要根据不同类型做出不同的操作

		@param srcEntityID: 调用实体的ID号
		@type  srcEntityID: int32
		@param         uid: 源背包的源道具的唯一ID
		@type          uid: INT64
		@param      amount: 表示从源物品里面分出多少个来
		@type       amount: UINT16
		@return:             被声明的方法，没有返回值
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return False

		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return False

		srcItem = self.itemsBag.getByUid( uid )
		if srcItem is None:
			self.statusMessage( csstatus.CIB_MSG_ITEM_NOT_EXIST )
			return False

		if srcItem.isFrozen():
			self.statusMessage( csstatus.CIB_MSG_FROZEN )
			return False

		if amount < 1:
			self.statusMessage( csstatus.CIB_MSG_AMOUNT_CANT_BE_ZERO )
			return False

		if srcItem.getAmount() - amount < 1:
			self.statusMessage( csstatus.CIB_MSG_AMOUNT_TOO_BIG )
			return False

		if srcItem.getStackable() <= 1:
			self.statusMessage( csstatus.CIB_MSG_CANNOT_STACKABLE )
			return False

		freeOrder = self.getNormalKitbagFreeOrder()
		if freeOrder == -1:
			self.statusMessage( csstatus.CIB_MSG_ORDER_NOT_NULL )
			return False
		dstItem = srcItem.new()
		dstItem.setAmount( amount )
		srcItem.setAmount( srcItem.getAmount() - amount, self, csdefine.DELETE_ITEM_SPLITITEM )
		if self.__addItem( freeOrder, dstItem, csdefine.ADD_ITEM_SPLITITEM ):
			self.client.addItemCB( dstItem )
		return True

	def combineItem( self, srcEntityID, srcOrder, dstOrder ):
		"""
		Exposed method.
		把一个背包里的某个道具与另外一个背包里的道具合并。
		例如：背包A里的小红药水有100个，背包B的小红药水有20个，小红药水最大叠加数为200，
		那我们可以使用此方法把背包B的小红药水放在背包A里，以空出一个位置。

		@param srcEntityID: 调用实体的ID号
		@type  srcEntityID: int32
		@param    srcOrder: 源背包的源道具
		@type     srcOrder: UINT8
		@param    dstOrder: 目标背包的源道具
		@type     dstOrder: UINT8
		@return:            被声明的方法，没有返回值
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return False

		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return False

		srcItem = self.itemsBag.getByOrder( srcOrder )
		dstItem = self.itemsBag.getByOrder( dstOrder )
		if ( srcItem is None ) or ( dstItem is None ):
			self.statusMessage( csstatus.CIB_MSG_SRC_DES_NOT_EXIST, srcOrder, dstOrder )
			return False

		if srcItem.isFrozen() or dstItem.isFrozen():
			self.statusMessage( csstatus.CIB_MSG_FROZEN )
			return False

		# 不是相同道具不允许叠加
		if srcItem.id != dstItem.id:
			self.statusMessage( csstatus.CIB_MSG_CANNOT_STACKABLE )
			return False

		if srcItem.isBinded() != dstItem.isBinded():	# 区分物品是否绑定。18:49 2009-2-16，wsf
			self.statusMessage( csstatus.BANK_BIND_TYPE_CANT_STACKABLE )
			return False

		stackable = dstItem.getStackable()
		# 不管在哪个道具栏里，只看目标是否能叠加
		if stackable <= 1:
			self.statusMessage( csstatus.CIB_MSG_CANNOT_STACKABLE )
			return False
		dAmount = dstItem.getAmount()
		# 如果目标达到可叠加最大数量，什么也不做,也不用通知客户端
		if dAmount == stackable:
			return False

		sAmount = srcItem.getAmount()
		# 算出目标道具可叠加数量
		stackAmount = stackable - dAmount
		if stackAmount >= sAmount:
			newDstAmount = dAmount + sAmount
			newSrcAmount = 0
			srcItem.setAmount( newSrcAmount, self, csdefine.DELETE_ITEM_COMBINEITEM )
			dstItem.setAmount( newDstAmount, self, csdefine.ADD_ITEM_COMBINEITEM )
		else:
			newDstAmount = stackable
			newSrcAmount = sAmount - stackAmount
			srcItem.setAmount( newSrcAmount, self, csdefine.DELETE_ITEM_COMBINEITEM )
			dstItem.setAmount( newDstAmount, self, csdefine.ADD_ITEM_COMBINEITEM )

		return True

	def moveItemToKitTote( self, srcEntityID, srcOrder, dstKitTote ):	# wsf add，15:10 2008-6-10
		"""
		Exposed method.
		把一个物品拖到包裹位的包裹上的处理。目前暂时只处理拖一个可叠加物品且可叠加到包裹中的情况。
		param srcOrder:	格子号
		type srcOrder:	INT16
		param dstKitTote:背包包裹位号
		type dstKitTote:UINT8
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return

		kitItem = self.kitbags.get( dstKitTote )
		if kitItem is None:
			self.statusMessage( csstatus.CIB_MSG_INVALID_KITBAG, dstKitTote )
			return False

		srcItem = self.itemsBag.getByOrder( srcOrder )
		if srcItem is None:
			self.statusMessage( csstatus.CIB_MSG_ITEM_NOT_EXIST )
			return

		if srcItem.isFrozen():
			self.statusMessage( csstatus.CIB_MSG_FROZEN )
			return

		if dstKitTote < csdefine.KB_COMMON_ID or dstKitTote > csdefine.KB_CASKET_ID:
			HACK_MSG( "dstKitTote( %i ) not in kitbag id list." % dstKitTote )
			return

		if srcItem.getStackable() > 1:	# 如果是可叠加物品
			if self.stackableItem( srcItem, csdefine.ADD_ITEM_STACK, dstKitTote ) == csdefine.KITBAG_STACK_ITEM_SUCCESS:	# 叠加成功
				self.deleteItem_( srcOrder, questItemAmountChanged = False, reason = csdefine.DELETE_ITEM_STACK  )
				return
		else:	# 对于不可叠加的物品，客户端目前并不使用此接口，而是使用swapOrder接口。
			pass

	# ---------------------------------------------------------------------------------------------
	# 物品锁定
	# ---------------------------------------------------------------------------------------------
	def freezeItem_( self, order ):
		"""
		锁定一个物品

		@return: BOOL
		"""
		item = self.itemsBag.getByOrder( order )
		if item is None: return False
		return item.freeze( self )

	def unfreezeItem_( self, order ):
		"""
		解锁一个物品

		@return: 无
		"""
		item = self.itemsBag.getByOrder( order )
		if item is None: return False
		item.unfreeze( self )

	def freezeItemByUid_( self, uid ):
		"""
		锁定一个物品

		@return: BOOL
		"""
		orderID = self.itemsBag.getOrderID( uid )
		return self.freezeItem_( orderID )

	def unfreezeItemByUid_( self, uid ):
		"""
		解锁一个物品

		@return: 无
		"""
		orderID = self.itemsBag.getOrderID( uid )
		return self.unfreezeItem_( orderID )

	def notifyPickupInfo( self, itemInstance, reason ):
		"""
		向客户端发送获得物品消息
		"""
		#chat_onChannelMessage( self.id, speaker.id, speaker.playerName, msg, blobArgs )

		d_item = ChatObjParser.dumpItem( itemInstance )

		if reason == csdefine.ADD_ITEM_LUCKYBOXZHAOCAI:
			msg = csstatus_msgs.getStatusInfo( csstatus.CIB_ZHAOCAI_ADD_REWARD, "${o0}" ).msg + "x%i"%( itemInstance.amount )
			self.statusMessage( csstatus.CIB_ZHAOCAI_ADD_REWARD, "[%s]" % itemInstance.fullName() )
		elif reason == csdefine.ADD_ITEM_LUCKYBOXJINBAO:
			msg = csstatus_msgs.getStatusInfo( csstatus.CIB_JINBAO_ADD_REWARD, "${o0}" ).msg + "x%i"%( itemInstance.amount )
			self.statusMessage( csstatus.CIB_JINBAO_ADD_REWARD, "[%s]" % itemInstance.fullName() )
		else:
			msg = csstatus_msgs.getStatusInfo( csstatus.CIB_MSG_GAIN_ITEMS, "${o0}", itemInstance.amount ).msg

		self.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSTEM, 0, "", msg, [d_item] )

	# ---------------------------------------------------------------------------------------------
	# 背包道具相关
	# ---------------------------------------------------------------------------------------------
	def moveKbItemToKitTote( self, srcEntityID, srcOrderID, dstKitTote ):
		"""
		Exposed method
		转换某个背包类型的道具为背包
		@param srcEntityID: 使用者，必须与self.id一致
		@type  srcEntityID: int32
		@param   srcOrderID: 道具位置
		@type    srcOrderID: INT16
		@param  dstKitTote: 道具栏位置，表示新的背包放到哪个位置
		@type   dstKitTote: INT8
		@return:            被声明的方法，没有返回值
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		self.__itemToKitbag( srcOrderID, dstKitTote )
		
	def __itemToKitbag( self, srcOrderID, dstKitTote ):
		"""
		转换某个背包类型的道具为背包
		@param   srcOrderID: 道具位置
		@type    srcOrderID: INT16
		@param  dstKitTote: 道具栏位置，表示新的背包放到哪个位置
		@type   dstKitTote: INT8
		"""
		if self.iskitbagsLocked():
			DEBUG_MSG( "背包被上锁了。" )
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return False

		srcItem = self.itemsBag.getByOrder( srcOrderID )
		if srcItem is None:
			self.statusMessage( csstatus.CIB_MSG_ITEM_NOT_EXIST )
			return False

		# 判断背包是否过期 过期背包不可装备 by姜毅
		if srcItem.isActiveLifeTime():
			if time.time() > srcItem.getDeadTime():
				self.statusMessage( csstatus.CIB_ITEM_CANT_EQUIP_OVERTIME )
				return
		else:
			srcItem.activaLifeTime()

		if srcItem.isFrozen():
			self.statusMessage( csstatus.CIB_MSG_FROZEN )
			return

		itemType = srcItem.getType()
		if itemType not in ItemTypeEnum.KITBAG_LIST:
			freeOrder = self.getFreeOrderFK( dstKitTote )
			if freeOrder == -1:
				return False
			self.swapItemAC( srcItem.order, freeOrder )
			return True
		# 如果是神机匣，则只能放在第6个包裹位
		if itemType == ItemTypeEnum.ITEM_WAREHOUSE_CASKET and dstKitTote  != csdefine.KB_CASKET_ID:
			return False
		# 如果是普通背包，则只能放在第2-5个包裹位
		if itemType == ItemTypeEnum.ITEM_WAREHOUSE_KITBAG \
			and ( dstKitTote <= csdefine.KB_COMMON_ID or dstKitTote >= csdefine.KB_CASKET_ID ):
			return False

		sOrder = srcItem.order
		kitItem = None
		if self.kitbags.has_key( dstKitTote ):
			# 检查背包是否被冻结
			kitItem = self.kitbags[dstKitTote]
			if kitItem.isFrozen():
				self.statusMessage( csstatus.CIB_MSG_FROZEN )
				return

			if itemType == ItemTypeEnum.ITEM_WAREHOUSE_CASKET:	# 对于神机夹，如果里面有东西就不能换位 by 姜毅
				if csdefine.KB_CASKET_ID in self.kitbags and self.getFreeOrderCountFK( csdefine.KB_CASKET_ID ) != self.kitbags[csdefine.KB_CASKET_ID].getMaxSpace():
					return False
			elif kitItem.getMaxSpace() >= srcItem.getMaxSpace():	# 如果目标包裹空间大于置换的包裹空间，不能替换．17:37 2008-10-30 wsf
				self.statusMessage( csstatus.CIB_PLACE_EXIST_BIGER_BAG )
				return

		if self.__removeItem( sOrder, srcItem, csdefine.DELETE_ITEM_TO_KITBAG ):
			self.kitbags[dstKitTote] = srcItem
			srcItem.onWield( self )
			self.client.removeItemCB( sOrder )
			self.client.addKitbagCB( dstKitTote, srcItem )		# 通知client
			if kitItem:
				self.__addItem( sOrder, kitItem, csdefine.ADD_ITEM_TO_KITBAG )
				self.client.addItemCB( kitItem )
			return True
		return False

	
	def moveKitbagToKbItem( self, srcEntityID, srcKitTote, dstOrder ):
		"""
		Exposed method
		转换某个背包为背包类型的道具
		@param srcEntityID: 使用者，必须与self.id一致
		@type  srcEntityID: int32
		@param  srcKitTote: 包裹栏位置，表示从哪个包裹栏里拿出来的
		@type   srcKitTote: INT8
		@param    dstOrder: 放到背包哪个位置
		@type     dstOrder: UINT8
		@return:            被声明的方法，没有返回值
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		self.__kitbagToItem( srcKitTote, dstOrder )
	
	def __kitbagToItem( self, srcKitTote, dstOrder ):
		"""
		@param  srcKitTote: 道具栏位置，表示从哪个道具栏里拿出来
		@type   srcKitTote: INT8
		@param    dstOrder: 放到背包哪个位置
		@type     dstOrder: UINT8
		"""
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return False

		if srcKitTote == dstOrder/csdefine.KB_MAX_SPACE:
			self.statusMessage( csstatus.CIB_MSG_KITBAG_NOT_ALLOW )
			return False

		if srcKitTote in [ csdefine.KB_EQUIP_ID, csdefine.KB_COMMON_ID ]:
			# 装备栏和第一物品栏不可变
			self.statusMessage( csstatus.CIB_MSG_KITBAG_NOT_ALLOW )
			return False

		kitItem = self.kitbags.get( srcKitTote )
		if kitItem is None:
			self.statusMessage( csstatus.CIB_MSG_INVALID_KITBAG, srcKitTote )
			return False

		if kitItem.isFrozen():
			self.statusMessage( csstatus.CIB_MSG_FROZEN )
			return False

		if len( self.getItems( srcKitTote ) ) != 0:
			# 包裹非空，不能移出来作为道具
			self.statusMessage( csstatus.CIB_MSG_BAG_NOT_NULL )
			return False

		dstItem = self.itemsBag.getByOrder( dstOrder )
		if dstItem is not None:
			self.statusMessage( csstatus.CIB_MSG_KITBAG_NOT_ALLOW )
			return False

		if self.__addItem( dstOrder, kitItem, csdefine.ADD_ITEM_KITBAG_TO_ITEM ):
			del self.kitbags[srcKitTote]
			self.client.addItemCB( kitItem )
			self.client.removeKitbagCB( srcKitTote )

	def swapKitbag( self, srcEntityID, srcKitOrder, dstKitOrder ):
		"""
		Exposed method
		交换两个背包的位置
		@param  srcKitOrder: 源背包栏位
		@type   srcKitOrder: INT8
		@param  dstKitOrder: 目标背包栏位
		@type   dstKitOrder: INT8
		@return:         如果请求被发送则返回True，否则返回False
		@rtype:          BOOL
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return

		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return False

		# 判断源背包位置是否合法
		if srcKitOrder <= csdefine.KB_COMMON_ID or srcKitOrder >= csdefine.KB_CASKET_ID:
			self.statusMessage( csstatus.CIB_MSG_KITBAG_NOT_ALLOW )
			return False
		# 判断目标背包位置是否合法
		if dstKitOrder <= csdefine.KB_COMMON_ID or dstKitOrder >= csdefine.KB_CASKET_ID:
			self.statusMessage( csstatus.CIB_MSG_KITBAG_NOT_ALLOW )
			return False

		srckitItem = self.kitbags.get( srcKitOrder )
		if srckitItem is None:
			self.statusMessage( csstatus.CIB_MSG_INVALID_KITBAG, srcKitOrder )
			return False
		# 判断源背包中是否有被锁定物品
		srcItemsList = self.getItems( srcKitOrder )
		for tempItem in srcItemsList:
			if tempItem.isFrozen():
				self.statusMessage( csstatus.CIB_MSG_FROZEN )
				return False

		dstkitItem = self.kitbags.get( dstKitOrder )
		swapItemData = {}	# 记录交换数据
		orderAmend = csdefine.KB_MAX_SPACE *( dstKitOrder - srcKitOrder )
		if dstkitItem is not None:
			# 判断目标背包中是否有被锁定物品
			dstItemsList = self.getItems( dstKitOrder )
			for tempItem in dstItemsList:
				if tempItem.isFrozen():
					self.statusMessage( csstatus.CIB_MSG_FROZEN )
					return False
			# 源背包和目标背包都存在，包裹互换
			for item in srcItemsList:
				swapItemData[item.order + orderAmend] = item
				self.__removeItem( item.order, item, csdefine.DELETE_ITEM_SWAP_KITBAG )
				
			for item in dstItemsList:
				swapItemData[item.order - orderAmend] = item
				self.__removeItem( item.order, item, csdefine.DELETE_ITEM_SWAP_KITBAG )
				
			self.kitbags.update( { srcKitOrder : dstkitItem, dstKitOrder : srckitItem } )
		else:
			# 源背包存在，目标背包不存在，包裹移位
			for item in srcItemsList:
				swapItemData[item.order + orderAmend] = item
				self.__removeItem( item.order, item, csdefine.DELETE_ITEM_SWAP_KITBAG )
				
			self.kitbags[dstKitOrder] = self.kitbags.pop( srcKitOrder )

		for order, itemData in swapItemData.iteritems():
			self.__addItem( order, itemData, csdefine.ADD_ITEM_SWAP_KITBAG )
				
		self.client.swapKitbagCB( srcKitOrder, dstKitOrder )

	# ------------------------------------------背包密码锁功能 BEGIN----------------------------------------
	def _iskitbagsSetPassword( self ):
		"""
		验证是否设置了背包密码
		"""
		return self.kitbagsPassword != ""	# 表示密码存在与否状态的位是否为1


	def iskitbagsLocked( self ):
		"""
		验证背包是否被锁定
		"""
		return ( self.kitbagsLockerStatus >> 1 ) & 0x01 == 1	# 表示背包是否被锁定与否状态位是否为1


	def kitbags_setPassword( self, srcEntityID, srcPassword, password ):
		"""
		Exposed method.
		设置、修改背包密码都使用此接口。背包密码为空时，srcPassword值为"",修改密码时srcPassword值为 玩家的旧密码

		param srcPassword:	背包原密码,
		type srcPassword:	STRING
		param password:	玩家输入的密码
		type password:	STRING
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return

		if not cmp( srcPassword, self.kitbagsPassword ) == 0:
			DEBUG_MSG( "玩家输入的旧密码不正确。" )
			if self.kitbagsUnlockLimitTime > 0 and int( time.time() ) - self.kitbagsUnlockLimitTime > 0:
				self.kitbagsUnlockLimitTime = 0			# 过了解锁限制期限，取消限制
				self.kitbagsLockerStatus |= 0x10		# 把右边第5位设置为1，表示第一次输错密码
				self.client.kitbags_lockerNotify( 3 )	# 旧密码输错，需要通知玩家
				return
			if self.kitbagsUnlockLimitTime == 0:		# 玩家不在解锁限制期限内
				temp = self.kitbagsLockerStatus >> 4
				temp += 1
				if temp == 3:							# 如果输错密码次数达到3次
					self.kitbagsUnlockLimitTime = int( time.time() ) + csconst.KITBAG_CANT_UNLOCK_INTERVAL	# 设置限制解锁期限
					self.kitbagsLockerStatus &= 0x03	# 把密码输错次数清0，以便下次重新计算次数
					return
				temp <<= 4
				self.kitbagsLockerStatus &= 0x03		# 保持最右边2位不变，把其他位置清0
				self.kitbagsLockerStatus |= temp		# 密码锁状态变化，记录玩家输错密码的次数
				self.client.kitbags_lockerNotify( 3 )	# 旧密码输错，需要通知玩家
				return
			self.client.kitbags_lockerNotify( 3 )		# 在解锁限制期限内旧密码输错，需要通知玩家
			return

		if self.kitbagsPassword == "":
			self.kitbagsLockerStatus |= 0x01
			self.client.kitbags_lockerNotify( 0 )		# 设置密码成功，通知客户端
		else:
			self.client.kitbags_lockerNotify( 1 )		# 修改密码成功的通知

		self.kitbagsPassword = password


	def kitbags_lock( self, srcEntityID ):
		"""
		Exposed method.
		给背包上锁，在玩家设置了密码且还没有对背包上锁的前提下，才满足此接口的使用条件

		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return

		if not self._iskitbagsSetPassword():
			HACK_MSG( "背包没有密码。" )
			return

		if self.iskitbagsLocked():
			HACK_MSG( "背包已经处于锁定状态。" )
			return
		#处于交易状态时上锁会导致交易取消
		if self.si_myState != csdefine.TRADE_SWAP_DEFAULT:
			self.__cancelTradeForLock()

		self.kitbagsLockerStatus |= 0x02		# 设置背包状态为锁定状态
		self.client.kitbags_lockerNotify( 4 )

		if self._isVend():						# 如果正在摆摊，那么取消摆摊
			self.vend_endVend( self.id, True )

	def __cancelTradeForLock( self ):
		tradeTarget = BigWorld.entities.get( self.si_targetID )
		if tradeTarget :
			self.si_tradeCancelFC( self.id )
			self.si_resetData()
			tradeTarget.client.onStatusMessage( csstatus.CIB_MSG_CANCEL_TRADE_FOR_LOCK, "" )	#为防止交易对象是ghost时会出错，把tradeTarget.statusMessage方法改成这个。
			self.statusMessage( csstatus.CIB_MSG_CANCEL_TRADE )

	def kitbags_unlock( self, srcEntityID, srcPassword ):
		"""
		Exposed method.
		给背包解锁，在玩家设置了背包密码且给背包上锁的前提下，才满足此接口的使用条件。
		注意：解锁的操作如果在本次登陆期间连续失败3次，KITBAG_CANT_UNLOCK_INTERVAL不允许背包解锁操作。

		param srcPassword:	背包原密码,
		type srcsrcPassword:STRING
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return

		if not self._iskitbagsSetPassword():
			HACK_MSG( "背包没有密码。" )
			return

		if not self.iskitbagsLocked():
			HACK_MSG( "背包已经处于非锁定状态。" )
			return

		if self.kitbagsUnlockLimitTime > 0:
			if not int( time.time() ) > self.kitbagsUnlockLimitTime:	# 这个检查也在客户端做，界面检查如果在限制期内则由界面通知玩家，服务器不需要通知
				self.client.kitbags_lockerNotify( 6 )
				DEBUG_MSG( "玩家处于不允许解锁期间。" )
				return
			self.kitbagsUnlockLimitTime = 0

		if not cmp( srcPassword, self.kitbagsPassword ) == 0:
			DEBUG_MSG( "玩家输入的密码不正确。" )
			temp = self.kitbagsLockerStatus >> 4
			temp += 1
			if temp == 3:	# 如果输错密码次数达到3次
				self.kitbagsUnlockLimitTime = int( time.time() ) + csconst.KITBAG_CANT_UNLOCK_INTERVAL
				self.kitbagsLockerStatus &= 0x03			# 把密码输错次数清0，以便下次重新计算次数
				self.client.kitbags_lockerNotify( 2 )		# 输错解锁密码的通知
				return
			temp <<= 4
			self.kitbagsLockerStatus &= 0x03				# 保持最右边2位不变，把其他位置清0
			self.kitbagsLockerStatus |= temp				# 密码锁状态变化，记录玩家输错密码的次数
			self.client.kitbags_lockerNotify( 2 )			# 输错解锁密码的通知
			return

		self.kitbagsLockerStatus &= 0x03					# 成功开锁后,把密码输错次数清0(如果连续3次输错密码，则锁定)
		self.kitbagsLockerStatus &= 0xfd					# 把右边第2位置0，表示背包处于非锁定状态
		self.client.kitbags_lockerNotify( 5 )
		self.__cancelForceUnlock()							# 成功解锁则撤销强制解锁

	def kitbags_onForceUnlock( self, srcEntityID ) :
		"""
		Exposed method
		玩家请求强制解除背包锁定并清空密码
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		if self.kitbagsForceUnlockLimitTime > 0 :			# 在强制解除锁定期限内，不再重复响应请求
			self.statusMessage( csstatus.CIB_MSG_KITBAG_FORCE_UNLOCK_REPEAT )
			return
		if not self.kitbagsLockerStatus & 0x02 :			# 背包未锁上，不允许申请强制解锁
			self.statusMessage( csstatus.CIB_MSG_KITBAG_FORCE_UNLOCK_FORBID )
			return
		self.kitbagsForceUnlockLimitTime = int( time.time() ) + csconst.KITBAG_FORCE_UNLOCK_LIMIT_TIME
		self.__addForceUnlockTimer()

	def kitbags_clearPassword( self, srcEntityID, srcPassword ):
		"""
		给背包永久解锁，玩家已经给背包设置了密码的前提下，此接口清除玩家设置的密码，把背包密码置为空。
		注意：永久解锁的操作如果在本次登陆期间失败3次，KITBAG_CANT_UNLOCK_INTERVAL内不允许背包解锁操作。

		param srcPassword:	背包原密码,
		type srcsrcPassword:STRING
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return

		if not self._iskitbagsSetPassword():
			HACK_MSG( "背包没有密码。" )
			return

		if self.kitbagsUnlockLimitTime > 0:
			if int( time.time() ) <= self.kitbagsUnlockLimitTime:	# 这个检查也在客户端做，界面检查如果在限制期内则由界面通知玩家，服务器不需要通知
				self.client.kitbags_lockerNotify( 6 )
				DEBUG_MSG( "玩家处于不允许解锁期间。" )
				return
			self.kitbagsUnlockLimitTime = 0

		if not cmp( srcPassword, self.kitbagsPassword ) == 0:
			DEBUG_MSG( "玩家输入的旧密码不正确。" )
			temp = self.kitbagsLockerStatus >> 4
			temp += 1
			if temp == 3:	# 如果输错密码次数达到3次
				self.kitbagsUnlockLimitTime = int( time.time() ) + csconst.KITBAG_CANT_UNLOCK_INTERVAL
				self.kitbagsLockerStatus &= 0x03			# 把密码输错次数清0，以便下次重新计算次数
				self.client.kitbags_lockerNotify( 2 )		# 输错解锁密码的通知
				return
			temp <<= 4
			self.kitbagsLockerStatus &= 0x03				# 保持最右边2位不变，把其他位置清0
			self.kitbagsLockerStatus |= temp				# 密码锁状态变化，记录玩家输错密码的次数
			self.client.kitbags_lockerNotify( 2 )			# 输错解锁密码的通知
			return

		self.kitbagsPassword = ""
		self.kitbagsLockerStatus &= 0x00
		self.kitbagsUnlockLimitTime = 0						# 密码没有了，所有的密码锁相关数据都清0
		self.client.kitbags_lockerNotify( 7 )
		self.__cancelForceUnlock()							# 成功解锁则撤销强制解锁
	# ------------------------------------------背包密码锁功能 END----------------------------------------


	def combineAppItem( self, itemID ):
		"""
		合并指定的物品
		@param    srcOrder: 源背包的源道具
		@type     srcOrder: UINT8
		@param    dstOrder: 目标背包的源道具
		@type     dstOrder: UINT8
		"""
		if self.iskitbagsLocked(): return

		self.combineItems( self.findItemsByIDWithBindFromNKCK( itemID, True ) )
		self.combineItems( self.findItemsByIDWithBindFromNKCK( itemID, False ) )

	def combineItems( self, items ):
		"""
		合并一堆物品
		"""
		# 小于2个物品就没必要合并了
		if len( items ) < 2: return False
		uItem = items[0]
		# 判断该物品是否能合并
		stackable = uItem.getStackable()
		if stackable <= 1: return False
		# 判断是否锁住了
		for item in items:
			if item.isFrozen(): return False

		allAmount = sum( [item.amount for item in items] )
		group = allAmount / stackable
		keepAmount = allAmount % stackable

		i = 0
		for item in items:
			if i < group:
				item.setAmount( stackable, self, csdefine.ADD_ITEM_COMBINEITEM )
			elif i == group:
				item.setAmount( keepAmount, self, csdefine.DELETE_ITEM_COMBINEITEM )
			else:
				item.setAmount( 0, self, csdefine.DELETE_ITEM_COMBINEITEM )
			i += 1

		return True

	def autoInStuffs( self, srcEntityID, itemIDs, needAmounts ):
		"""
		Exposed Method
		装备打造中，自动合并并拆分需求的材料
		对指定的物品ID，合并并留下 needAmount 的数量。
		一个很诡异的方法.
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return

		if self.iskitbagsLocked(): return False

		# 要进行拆分合并的所有物品中，只要有一个物品处于锁定状态，则不允许拆分
		for itemID in itemIDs:
			items = self.findItemsByIDFromNKCK( itemID )
			for item in items:
				if item.isFrozen():
					self.statusMessage( csstatus.AUTO_STUFF_ITEM_FROZEN )
					return False

		# 背包空位检查
		needCount = len( itemIDs )
		freeOrderCount = self.getNormalKitbagFreeOrderCount()
		if freeOrderCount < needCount:
			self.statusMessage( csstatus.AUTO_STUFF_NO_FREEORDER, needCount )
			return

		needOrder = []

		for itemID, amount in zip( itemIDs, needAmounts ):
			self.combineAppItem( itemID )
			items = self.findItemsByIDFromNKCK( itemID )
			if len( items ) == 0: return False
			orders = [ item.order for item in items if item.amount == amount ]
			if len( orders )  > 0:
				needOrder.append( orders[0] )
			else:
				newAmount = amount
				for item in items:
					itemAmount = item.amount
					if itemAmount > newAmount:
						newItem = item.new()
						newItem.setAmount( newAmount )
						freeOrder = self.getNormalKitbagFreeOrder()
						if self.__addItem( freeOrder, newItem, csdefine.ADD_ITEM_AUTOINSTUFFS ):
							self.questItemAmountChanged( newItem, newAmount )
							self.client.addItemCB( newItem )
							item.setAmount( itemAmount - newAmount, self, csdefine.DELETE_ITEM_AUTOINSTUFFS )
							needOrder.append( freeOrder )
						break
					else:
						needOrder.append( item.order )
						newAmount -= itemAmount

		self.client.autoStuffFC( needOrder )

	def getByUid( self, uid ):
		"""
		根据UID 获取背包中的物品
		@type  uid : UINT32
		@param uid : 物品的UID
		@return 物品的实例，没有返回None
		"""
		return self.itemsBag.getByUid( uid )


	def onMoneyChanged( self, value, reason ):
		"""
		玩家给钱
		"""
		RoleSwapItem.onMoneyChanged( self, value, reason )

	# -------------------------------------------------
	# 背包强制解锁相关
	# -------------------------------------------------
	def onKitbagForceUnlockTimer( self ) :
		"""
		强制解除背包锁定的timer到达
		"""
		self.__forceUnlockKitbag()

	def __forceUnlockKitbag( self ) :
		"""
		强制解锁背包
		"""
		self.kitbagsPassword = ""								# 密码清空
		self.kitbagsLockerStatus &= 0x00						# 背包解锁
		self.kitbagsUnlockLimitTime = 0							# 锁定时间清零
		self.kitbagsForceUnlockLimitTime = 0					# 强制解锁时间清零
		self.removeTemp( "kb_forceUnlock_timerID" )
		self.statusMessage( csstatus.CIB_MSG_KITBAG_FORCE_UNLOCK_SUCCESS )
		mailMgr = BigWorld.globalData["MailMgr"]
		content = cschannel_msgs.FORCE_UNLOCK_MAIL_CONTENT % cschannel_msgs.GMMGR_BEI_BAO
		title = cschannel_msgs.FORCE_UNLOCK_MAIL_TITLE % cschannel_msgs.GMMGR_BEI_BAO
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
		kb_forceUnlock_timerID = self.queryTemp( "kb_forceUnlock_timerID", 0 )
		if kb_forceUnlock_timerID > 0 :
			self.cancel( kb_forceUnlock_timerID )
			self.removeTemp( "kb_forceUnlock_timerID" )
		self.kitbagsForceUnlockLimitTime = 0

	def __addForceUnlockTimer( self ) :
		"""
		添加强制解锁的timer
		"""
		now = int( time.time() )
		leaveTime = self.kitbagsForceUnlockLimitTime - now
		if leaveTime <= 0 : return								# 时间已超过
		kb_forceUnlock_timerID = self.queryTemp( "kb_forceUnlock_timerID", 0 )
		if kb_forceUnlock_timerID > 0 : return					# 已添加了一个timer，不允许重复添加
		kb_forceUnlock_timerID = self.delayCall( leaveTime, "onKitbagForceUnlockTimer" )
		self.setTemp( "kb_forceUnlock_timerID", kb_forceUnlock_timerID )
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
		self.delayCall( 1, "statusMessage", csstatus.CIB_MSG_KITBAG_FORCE_UNLOCK_REMAIN, leaveText )
	
	def kitbags_saveLater( self ):
		"""
		操作延迟存储
		"""
		if self.kitbags_saveTimerID:
			return
			
		self.kitbags_saveTimerID = self.addTimer( 60.0, 0, ECBExtend.ROLE_ITEM_BAG_SAVE_LATER )
	
	def kitbags_onSaveLaterTimer( self, timerID, cbid ):
		"""
		执行延迟存储操作
		"""
		self.kitbags_saveTimerID = 0
		self.writeToDB()

	