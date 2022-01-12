# -*- coding: gb18030 -*-
#
# $Id: ItemsBag.py,v 1.136 2008-09-02 05:11:00 pengju Exp $

"""
@summary				:	背包模块
"""

import copy
import csarithmetic
import csdefine
import csstatus
import csconst
import ItemTypeEnum
import ItemAttrClass
import skills
import items
import Const
import event.EventCenter as ECenter
import GUIFacade
import BigWorld
import ShareTexts
import reimpl_itemsBag

from bwdebug import *
from Function import Functor
from KitbagBase import KitbagBase
from ItemBagRole import ItemBagRole
from RoleSwapItem import RoleSwapItem
from RoleTradeWithNPC import RoleTradeWithNPC
from RoleTradeWithMerchant import RoleTradeWithMerchant
from gbref import rds
from love3 import *
from RoleVend import RoleVend
from ItemsFactory import ObjectItem as ItemInfo
from config.client.msgboxtexts import Datas as mbmsgs
from guis import *
from VehicleHelper import isVehicleEquipUseable
import SkillTargetObjImpl

crystals = [50101173,50101174,50101175,50101176,50101177]
class ItemsBag( ItemBagRole, RoleSwapItem, RoleTradeWithNPC, RoleVend, RoleTradeWithMerchant ):
	"""
	这是一个背包类 for role of client only

	@ivar kitbags: 一个物品列表，用来存储物品
	@type kitbags: ITEMS

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
	"""
	def __init__( self ):
		RoleVend.__init__( self )
		RoleSwapItem.__init__( self )		# wsf,初始化交易系统
		RoleTradeWithNPC.__init__( self )
		RoleTradeWithMerchant.__init__( self )
		self.itemsBag = KitbagBase()		# 背包物品，保存所有物品和道具( hyw -- 2008.06.10 )
		self.kitbags = {}					# 背包：{ order : item }，保存所有背包( hyw -- 2008.06.10 )
		self.mySIItem = {}
		self.dstSIItem = {}
		self.pyBox = None					# 二次确认框
		self.isCasketLocked = False			# 神机夹锁定标记 by 姜毅
		self.isRemoveCrystalSelected = False

		rds.shortcutMgr.setHandler( "ACTION_PICK_UP_ITEM", ItemsBag.__pickItem )

		# 一键换装部位、数据列对应表 by jd
		self.suitPartDict = {
			ItemTypeEnum.CWT_HEAD :0, # 头     —— 头盔
			ItemTypeEnum.CWT_NECK :1, # 颈     —— 项链
			ItemTypeEnum.CWT_BODY :2, # 身体   —— 身甲
			ItemTypeEnum.CWT_BREECH :3, # 臀部   —— 裤子
			ItemTypeEnum.CWT_VOLA :4, # 手     —— 手套
			ItemTypeEnum.CWT_HAUNCH :5, # 腰     —— 腰带
			ItemTypeEnum.CWT_CUFF :6, # 腕     —— 护腕
			ItemTypeEnum.CWT_LEFTHAND :7, # 左手   —— 盾牌
			ItemTypeEnum.CWT_RIGHTHAND :8, # 右手   —— 武器
			ItemTypeEnum.CWT_FEET :9, # 脚     —— 鞋子
			ItemTypeEnum.CWT_LEFTFINGER :10, # 左手指 —— 戒指
			ItemTypeEnum.CWT_RIGHTFINGER :11, # 右手指 —— 戒指
			ItemTypeEnum.CWT_TALISMAN :12, # 法宝
			}


	# ----------------------------------------------------------------
	# private methods
	# ----------------------------------------------------------------
	def __useEquipItem( self, uid ):
		"""
		装上/卸下装备
		@param uid 			: 物品的唯一ID
		@type uid			: INT64
		"""

		item = self.getItemByUid_( uid )

		if item.getType() == ItemTypeEnum.ITEM_POTENTIAL_BOOK and item.isPotentialMax() and item.getOrder() != ItemTypeEnum.CEL_POTENTIAL_BOOK:
			self.__useSkillItem( uid )
			return
		# 右键装备时发出声音
		sound = rds.iconsSound.getDragDownSound( item.icon() )
		rds.soundMgr.playUI( sound )

		kitOrder = item.getKitID()
		orderID = item.getOrder()%csdefine.KB_MAX_SPACE
		if kitOrder == csdefine.KB_EQUIP_ID:
			dstOrderID = self.getNormalKitbagFreeOrder()
			if dstOrderID == -1:
				self.statusMessage( csstatus.CIB_MSG_UNWIELD_ITEM )
				return
			dstbagID = dstOrderID/csdefine.KB_MAX_SPACE
			dstOrderID = dstOrderID%csdefine.KB_MAX_SPACE
		else :
			orders = item.getWieldOrders()
			if len( orders ) == 0: return
			dstbagID = csdefine.KB_EQUIP_ID
			dstOrderID = orders[0]
			if len( orders ) == 2:
				item1 = self.itemsBag.getByOrder( orders[0] )
				item2 = self.itemsBag.getByOrder( orders[1] )
				if ( not item2 ) and item1:	# 如果右手空 且 左手已经装备
					dstOrderID = orders[1]
		self.moveItem( kitOrder, orderID, dstbagID, dstOrderID )

	def __useQuestItem( self, uid ):
		"""
		使用任务物品
		@param uid 			: 物品的唯一ID
		@type uid			: INT64
		"""
		self.cell.selectQuestFromItem( uid )

	def __useSkillItem( self, uid ):
		"""
		使用技能物品
		@param uid 			: 物品的唯一ID
		@type uid			: INT64
		"""
		item = self.getItemByUid_( uid )
		if item.isFrozen():
			self.__isFrozenItemMsg()
			return
		target = self.targetEntity
		skillID = item.query("spell")
		sk = skills.getSkill( skillID )
		castType = sk.getCastObjectType()
		if castType == csdefine.SKILL_CAST_OBJECT_TYPE_POSITION:
			state = item.use( self, target )
			return
		if item.getType() == ItemTypeEnum.ITEM_POTENTIAL_BOOK:
			target = self
		target = sk.getCastObject().convertCastObject( self, target )
		targetObj = SkillTargetObjImpl.createTargetObjEntity( target )
		if target:	# 如果目标不为空，且目标不是自己，那么要面对目标使用
			if target.id != self.id and not sk.isNotRotate:
				self.turnaround( target.matrix, None )
		state = item.use( self, target )
		if state != csstatus.SKILL_GO_ON:
			self.statusMessage( state )
			return
		if castType == csdefine.SKILL_CAST_OBJECT_TYPE_POSITION:return				#对位置施法特殊处理
		player = BigWorld.player()
		if player.intonating():
			player.cell.interruptSpellFC( csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1 )

		if item.getType() == ItemTypeEnum.ITEM_VEHICLE_BOOK:
			vehicleSkills = player.getVehicleSkills( player.vehicleDBID )
			if len( vehicleSkills ) >= csconst.VEHICLE_SKILLS_TOTAL:
				def query( rs_id ):
					if rs_id == RS_OK and targetObj: self.cell.useItem( uid, targetObj )
				if not self.pyBox is None:
					self.pyBox.visible = False
					self.pyBox = None
				# 您的骑宠技能已满，是否随机替换其中一个技能？
				self.pyBox = showMessage( 0x00a1, "", MB_OK_CANCEL, query )
				return

		ECenter.fireEvent( "EVT_ON_ITEM_USE", item )
		if targetObj:
			self.cell.useItem( uid, targetObj )

	@reimpl_itemsBag.deco_itemsBagUseKitBagItem
	def __useKitBagItem( self, uid ):
		"""
		使用背包物品
		@param uid 			: 物品的唯一ID
		@type uid			: INT64
		"""
		item = self.getItemByUid_( uid )
		kitOrder = item.getKitID()
		orderID = item.getOrder()%csdefine.KB_MAX_SPACE
		for i in xrange( csdefine.KB_EXCONE_ID , csdefine.KB_EXCTHREE_ID + 1 ):
			if i not in self.kitbags:
				self.moveKbItemToKitTote( kitOrder, orderID, i )
				break

	def __useNormalItem( self, uid ):
		"""
		使用普通物品
		@param uid 			: 物品的唯一ID
		@type uid			: INT64
		"""
		targetObj = SkillTargetObjImpl.createTargetObjEntity( self )
		self.cell.useItem( uid, targetObj )

	def __useCasketItem( self, uid ):
		"""
		使用神机匣物品
		@param uid 			: 物品的唯一ID
		@type uid			: INT64
		"""
		item = self.getItemByUid_( uid )
		kitOrder = item.getKitID()
		orderID = item.getOrder()%csdefine.KB_MAX_SPACE
		self.moveKbItemToKitTote( kitOrder, orderID, csdefine.KB_CASKET_ID )

	def __useVehicleItem( self, uid ):
		"""
		使用骑宠
		@param uid 			: 物品的唯一ID
		@type uid			: INT64
		"""
		if len( self.vehicleDatas ) >= csconst.VEHICLE_AMOUNT_MAX:
			self.statusMessage( csstatus.VEHICLE_AMOUNT_MAX )
			return
		self.cell.useVehicleItem( uid )
		
	def __useTurnVehicleItem( self, uid ):
		"""
		使用转换成物品的骑宠道具
		@param uid 			: 物品的唯一ID
		@type uid			: INT64
		"""
		if len( self.vehicleDatas ) >= csconst.VEHICLE_AMOUNT_MAX:
			self.statusMessage( csstatus.VEHICLE_AMOUNT_MAX )
			return
		self.cell.useTurnVehicleItem( uid )

	def __useTalismanStone( self, uid ):
		"""
		使用天罡石
		@param uid 			: 物品的唯一ID
		@type uid			: INT64
		"""
		# 判断玩家法宝是否存在
		order = ItemTypeEnum.CWT_TALISMAN
		talismanItem = self.getItem_( order )
		item = self.getItemByUid_( uid )
		if talismanItem is None:
			self.statusMessage( csstatus.TALISMAN_NO_WIELD )
			return
		# 判断是不是法宝类型
		if talismanItem.getType() != ItemTypeEnum.ITEM_SYSTEM_TALISMAN:
			self.statusMessage( csstatus.TALISMAN_SHAN_ZHAI )
			return
		# 根据使用的天罡石确定能够激活的品级
		useGrade = rds.talismanEffects.getAcGradeByItemID( item.id )
		if useGrade is None: return

		# 判断法宝当前的品级属性是否能用该物品激活
		grade = talismanItem.getGrade()
		if useGrade > grade:
			self.statusMessage( csstatus.TALISMAN_GRADE_LESS )
			return

		effect = []
		if useGrade == ItemTypeEnum.TALISMAN_COMMON:
			effect = list( talismanItem.getCommonEffect() )
		elif useGrade == ItemTypeEnum.TALISMAN_IMMORTAL:
			effect = list( talismanItem.getImmortalEffect() )
		elif useGrade == ItemTypeEnum.TALISMAN_DEITY:
			effect = list( talismanItem.getDeityEffect() )
		if len( effect ) == 0: return

		newData = None
		for index, data in enumerate( effect ):
			key, state = data
			if state: continue
			newData = ( key, True )
			break

		# 表示没有需要激活的属性
		if newData is None:
			self.statusMessage( csstatus.TALISMAN_GRADE_NONEED )
			return

		self.cell.activateTalismanAttr( uid )

	def __isFrozenItemMsg( self ):
		"""
		用来细分冻结物品的提示
		"""
		if self.state == csdefine.ENTITY_STATE_VEND: #如果冻结的物品是处于摆摊状态
			self.statusMessage( csstatus.SKILL_USE_ITEM_VEND_ISFROZEN )
		elif self.state == csdefine.TRADE_SWAP: #如果冻结的物品是处于交易状态
			self.statusMessage( csstatus.ROLE_ITEM_ISFROZEN )
		else:
			self.statusMessage( csstatus.CIB_MSG_FROZEN )

	@staticmethod
	def __pickItem() :
		"""
		捡起物品（从 Tact 中移动到这－－hyw：2008.12.29）
		注：shortcuMgr 中对快捷键处理函数采用弱引用，如果这里使用普通方法，则，中途快捷键处理函数可能会丢掉。
			因此这里采用静态方法－－目前还不知道什么原因，因为仅仅是 ItemsBag 这里不能使用普通方法
		"""
		self = BigWorld.player()
		if self.currentItemBoxID != 0 and BigWorld.entities.has_key( self.currentItemBoxID ):
			# 如果已经有打开的箱子，再按下Z键则是拾取物品
			box = BigWorld.entities[self.currentItemBoxID]
			box.pickUpAllItems()
			self.stopPickUp()
			return True
		if self.affectAfeard:
			return False
		if not self.isAlive():
			return False
		searchRange = 20.0									# 搜索掉落物品的范围（暂时写死）
		space = 3.0											# 捡拾距离
		def verifier( ent ) :
			return ( ent.isEntityType( csdefine.ENTITY_TYPE_DROPPED_ITEM ) or ent.isEntityType( csdefine.ENTITY_TYPE_DROPPED_BOX ) ) and ent.canPickUp
		items = self.entitiesInRange( searchRange, cnd = verifier )
		if len( items ) == 0:
			return True
		item = items[0]
		if self.position.distTo( item.position ) >= space:
			pos = csarithmetic.getSeparatePoint3( item.position, self.position, space )
			def pickup( item, success ) :
				if not success : return
				rds.targetMgr.bindTarget( item )
				self.startPickUp( item )
			self.moveTo( pos, Functor( pickup, item ) )
		else :
			rds.targetMgr.bindTarget( item )
			self.startPickUp( item )
		return True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		if self.iskitbagsLocked() : # 如果背包已上锁，则提示
			BigWorld.player().statusMessage( csstatus.CIB_REMIND_MSG_KITBAG_LOCKED )

	# ----------------------------------------------------------------
	# public for client
	# ----------------------------------------------------------------
	def useItem( self, uid ):
		"""
		右键点击普通物品栏的某个物品
		@param 			kitOrder	  : 背包位置
		@type  			kitOrder	  : UINT8
		@param  		orderID		  : 物品位置
		@type   		orderID		  : UINT8
		@return						  : 无
		"""
		item = self.getItemByUid_( uid )
		if item is None : return
		if item.isFrozen():
			self.__isFrozenItemMsg()
			return
		i_type = item.getType()

		player = BigWorld.player()
		if player.isDeadWatcher() or player.isGMWatcher():
			player.statusMessage( csstatus.CIB_MSG_ITEM_NOT_IN_POSTURE )
			return

		if item.isEquip() and item.isAlreadyWield() or \
		i_type == ItemTypeEnum.ITEM_POTENTIAL_BOOK and not item.isPotentialMax():
			self.useItemDependOnType( uid, item, i_type )
			return
		if item.getBindType() == ItemTypeEnum.CBT_EQUIP:	# 如果是装备绑定
			def query( rs_id ):
				if rs_id == RS_OK: self.useItemDependOnType( uid, item, i_type )
			if not self.pyBox is None:
				self.pyBox.visible = False
				self.pyBox = None
			# 装备后将绑定，是否装备？
			self.pyBox = showMessage( 0x00a2, "", MB_OK_CANCEL, query )
			return
		if item.id in Const.SECOND_QUEST_ITEM_AND_INFO:
			info = Const.SECOND_QUEST_ITEM_AND_INFO[item.id]
			if item.id == 110103046 and self.af_time_extra > 0:
				info = Const.INFO_AF_TIME_PLUS2
			def query( rs_id ):
				if rs_id == RS_OK: self.useItemDependOnType( uid, item, i_type )
			if not self.pyBox is None:
				self.pyBox.visible = False
				self.pyBox = None
			self.pyBox = showMessage( info, "", MB_OK_CANCEL, query )
			return
		if i_type == ItemTypeEnum.ITEM_SYSTEM_VEHICLE:
			def query( rs_id ):
				if rs_id == RS_OK: self.useItemDependOnType( uid, item, i_type )
			if not self.pyBox is None:
				self.pyBox.visible = False
				self.pyBox = None
			# 孵化后若重新封灵需要消耗符文石，确定要孵化?
			self.pyBox = showMessage( 0x00a6, "", MB_OK_CANCEL, query )
			if item.id == 60501079:
				rds.ruisMgr.okCancelBox = self.pyBox
				rds.opIndicator.fireRegIdtsOfTrigger( ( "gui_visible","okCancelBox" ) )
			
			return
		if i_type == ItemTypeEnum.ITEM_VEHICLE_TURN:
			def query( rs_id ):
				if rs_id == RS_OK: self.useItemDependOnType( uid, item, i_type )
			if not self.pyBox is None:
				self.pyBox.visible = False
				self.pyBox = None
			# 装备后将绑定，是否装备？
			self.pyBox = showMessage( 0x00a7, "", MB_OK_CANCEL, query )
			return
		self.useItemDependOnType( uid, item, i_type )

	def useItemDependOnType( self, uid, item, i_type ):
		"""
		基于物品类型选择对应的使用接口 by姜毅
		"""
		if i_type == ItemTypeEnum.ITEM_SYSTEM_VEHICLE:
			self.__useVehicleItem( uid )
		elif i_type == ItemTypeEnum.ITEM_VEHICLE_TURN:
			self.__useTurnVehicleItem( uid )
		elif i_type == ItemTypeEnum.ITEM_SYSTEM_GODSTONE:
			self.__useTalismanStone( uid )
		elif i_type in ItemTypeEnum.VEHICLE_EQUIP_LIST:
			self.__useVehicleEquip( uid )
		elif item.getQuestID() > 0 :
			self.__useQuestItem( uid )
		elif i_type in ItemTypeEnum.EQUIP_TYPE_SET:
			self.__useEquipItem( uid )
		elif item.getSpell() != None:
			self.__useSkillItem( uid )
		elif i_type == ItemTypeEnum.ITEM_WAREHOUSE_KITBAG:
			self.__useKitBagItem( uid )
		elif i_type == ItemTypeEnum.ITEM_WAREHOUSE_CASKET:
			self.__useCasketItem( uid )
		else:
			self.__useNormalItem( uid )

	def destroyItem( self, uid ):
		"""
		销毁一个物品

		@param uid: 道具唯一ID
		@type  uid: INT64
		@return:        如果请求被发送则返回True，否则返回False
		@rtype:         BOOL
		"""
		item = self.itemsBag.getByUid( uid )
		if item is None:
			self.statusMessage( csstatus.CIB_MSG_SRCPOS_NOT_ITEM, orderID )
			return False

		if item.isFrozen():
			self.__isFrozenItemMsg()
			return False

		if not item.canDestroy():
			self.statusMessage( csstatus.CIB_MSG_CANNOT_DESTROY )
			return False

		self.cell.destroyItem( uid )
		return True

	def moveItem( self, srcKitTote, srcOrder, dstKitTote, dstOrder ):
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
		@return:            如果请求被发送则返回True，否则返回False
		@rtype:             BOOL
		"""
		self.swapItem( srcKitTote, srcOrder, dstKitTote, dstOrder, False )

	def swapItem( self, srcKitTote, srcOrderID, dstKitTote, dstOrderID, isAskAgain = True ):
		"""
		在物品交换前作确认 modified by姜毅
		"""
		srcOrder = srcKitTote * csdefine.KB_MAX_SPACE + srcOrderID
		dstOrder = dstKitTote * csdefine.KB_MAX_SPACE + dstOrderID

		kitItem = self.kitbags.get( dstKitTote )
		if kitItem is None:
			self.statusMessage( csstatus.CIB_MSG_INVALID_KITBAG, dstKitTote )
			return False

		srcItem = self.itemsBag.getByOrder( srcOrder )
		dstItem = self.itemsBag.getByOrder( dstOrder )

		if srcItem is None:
			self.statusMessage( csstatus.CIB_MSG_SRCPOS_NOT_ITEM, srcOrderID )
			return False

		if dstKitTote == csdefine.KB_EQUIP_ID:	# 如果放入装备栏
			if srcItem.query( "bindType" ) == ItemTypeEnum.CBT_EQUIP and isAskAgain:	# 如果是装备绑定 而且进入函数路径不通过useEquipItem
				def query( rs_id ):
					if rs_id == RS_OK: self.swapItemFunc( srcKitTote, srcOrderID, dstKitTote, dstOrderID, srcItem, dstItem )
				if not self.pyBox is None:
					self.pyBox.visible = False
					self.pyBox = None
				# 装备后将绑定，是否装备？
				self.pyBox = showMessage( 0x00a2, "", MB_OK_CANCEL, query )
			else:
				self.swapItemFunc( srcKitTote, srcOrderID, dstKitTote, dstOrderID, srcItem, dstItem )
		else:
			self.swapItemFunc( srcKitTote, srcOrderID, dstKitTote, dstOrderID, srcItem, dstItem )
	
	def swapItemFunc( self, srcKitTote, srcOrderID, dstKitTote, dstOrderID, srcItem, dstItem ):
		"""
		交换两个道具的位置。

		需要考虑源背包和目标背包类型，有可能需要根据不同类型做出不同的操作

		@param  srcKitTote: 源背包唯一标识
		@type   srcKitTote: INT8
		@param  srcOrderID: 源背包的源道具
		@type   srcOrderID: INT8
		@param  dstKitTote: 目标背包唯一标识
		@type   dstKitTote: INT8
		@param  dstOrderID: 目标背包的源道具
		@type   dstOrderID: INT8
		@return:            如果请求被发送则返回True，否则返回False
		@rtype:             BOOL
		"""
		DEBUG_MSG( "from %i, %i to %i, %i" % (srcKitTote, srcOrderID, dstKitTote, dstOrderID) )
		# 为了使该接口能能独立使用 所以这里重复获得srcOrder dstOrder
		srcOrder = srcKitTote * csdefine.KB_MAX_SPACE + srcOrderID
		dstOrder = dstKitTote * csdefine.KB_MAX_SPACE + dstOrderID
		if ( srcItem is not None and srcItem.isFrozen() ) or ( dstItem is not None and dstItem.isFrozen() ):
			self.__isFrozenItemMsg()
			return False
		# 如果物品是从装备栏出来的，则需要考虑目标物品是否能放入装备栏
		if srcKitTote == csdefine.KB_EQUIP_ID:
			if self.actionSign( csdefine.ACTION_FORBID_WIELD ):
				self.statusMessage( csstatus.KIT_EQUIP_CANT_STATE )
				return False
			if dstItem:
				state = self.canWieldEquip( srcOrder, dstItem )
				if state != csstatus.KIT_EQUIP_CAN_FIT_EQUIP:
					self.statusMessage( state )
					return False

		# 如果物品要放到装备栏上，则需要考虑该物品是否能放入装备栏
		if dstKitTote == csdefine.KB_EQUIP_ID:
			if self.actionSign( csdefine.ACTION_FORBID_WIELD ):
				self.statusMessage( csstatus.KIT_EQUIP_CANT_STATE )
				return False
			state = self.canWieldEquip( dstOrder, srcItem )
			if state != csstatus.KIT_EQUIP_CAN_FIT_EQUIP:
				self.statusMessage( state )
				return False

		if srcKitTote in xrange( csdefine.KB_COMMON_ID, csdefine.KB_CASKET_ID + 1 ):
			# from normal kitbag
			if dstKitTote in xrange( csdefine.KB_COMMON_ID, csdefine.KB_CASKET_ID ):
				# to normal kitbag 两组道具相同，至少一组达到叠加上限，则两组位置互换
				if dstItem is not None and \
					srcItem.id == dstItem.id and \
					srcItem.isBinded() == dstItem.isBinded() and \
					srcItem.getStackable() > 1 and \
					srcItem.getAmount() < srcItem.getStackable() and \
					dstItem.getAmount() < dstItem.getStackable():
						self.combineItem( srcKitTote, srcOrderID, dstKitTote, dstOrderID )
						return True
		#战士
		if self.getClass() == csdefine.CLASS_FIGHTER:    # 职业为战士
			l_item = self.itemsBag.getByOrder( ItemTypeEnum.CEL_LEFTHAND )
			r_item = self.itemsBag.getByOrder( ItemTypeEnum.CEL_RIGHTHAND )
			if l_item and r_item and dstItem and srcItem:
				if srcItem.getType() != dstItem.getType():
					orderIDs = self.getAllNormalKitbagFreeOrders()
					if len( orderIDs ) < 1 :
						self.statusMessage( csstatus.CIB_MSG_UNWIELD_ITEM )
						return False
		# 向cell发送请求
		self.cell.swapItem( srcOrder, dstOrder )
		return True

	def combineItem( self, srcKitTote, srcOrderID, dstKitTote, dstOrderID ):
		"""
		把一个背包里的某个道具与另外一个背包里的道具合并。
		例如：背包A里的小红药水有100个，背包B的小红药水有20个，小红药水最大叠加数为200，
		那我们可以使用此方法把背包B的小红药水放在背包A里，以空出一个位置。

		@param  srcKitTote: 源背包唯一标识
		@type   srcKitTote: INT8
		@param  srcOrderID: 源背包的源道具
		@type   srcOrderID: INT8
		@param  dstKitTote: 目标背包唯一标识
		@type   dstKitTote: INT8
		@param  dstOrderID: 目标背包的源道具
		@type   dstOrderID: INT8
		@return:            如果请求被发送则返回True，否则返回False
		@rtype:             BOOL
		"""
		srcOrder = srcKitTote * csdefine.KB_MAX_SPACE + srcOrderID
		dstOrder = dstKitTote * csdefine.KB_MAX_SPACE + dstOrderID

		srcItem = self.itemsBag.getByOrder( srcOrder )
		dstItem = self.itemsBag.getByOrder( dstOrder )
		if ( srcItem is None ) or ( dstItem is None ):
			self.statusMessage( csstatus.CIB_MSG_SRC_DES_NOT_EXIST, srcOrderID, dstOrderID )
			return False

		if srcItem.isFrozen() or dstItem.isFrozen():
			self.__isFrozenItemMsg()
			return False

		# 不是相同道具不允许叠加
		if srcItem.id != dstItem.id:
			self.statusMessage( csstatus.CIB_MSG_CANNOT_STACKABLE )
			return False
		# 不管在哪个道具栏里，只看目标是否能叠加
		stackable = dstItem.getStackable()
		if stackable <= 1:
			self.statusMessage( csstatus.CIB_MSG_CANNOT_STACKABLE )
			return False

		if stackable == dstItem.getAmount():
			return

		self.cell.combineItem( srcOrder, dstOrder )		# 向cell发送请求
		return True

	def splitItem( self, uid, amount ):
		"""
		分开一个可叠加的道具。

		需要考虑源背包和目标背包类型，有可能需要根据不同类型做出不同的操作

		@param  uid: 源背包的源道具的唯一ID
		@type   uid: INT64
		@param      amount: 表示从源物品里面分出多少个来
		@type       amount: UINT16
		@return:            如果请求被发送则返回True，否则返回False
		@rtype:             BOOL
		"""
		srcItem = self.itemsBag.getByUid( uid )
		freeID = self.getNormalKitbagFreeOrder()
		if srcItem is None:
			self.statusMessage( csstatus.CIB_MSG_SRCPOS_NOT_ITEM, srcItem.orderID )
			return False

		if srcItem.getStackable() <= 1:
			self.statusMessage( csstatus.CIB_MSG_CANNOT_STACKABLE )
			return False

		if amount < 1:
			self.statusMessage( csstatus.CIB_MSG_AMOUNT_CANT_BE_ZERO )
			return False

		if srcItem.getAmount() - amount < 1:
			self.statusMessage( csstatus.CIB_MSG_AMOUNT_TOO_BIG )
			return False

		if freeID == -1:
			self.statusMessage( csstatus.CIB_MSG_CANNOT_SPLIT )
			return False

		self.cell.splitItem( uid, amount )
		return True

	def checkRemoveCryStal( self ,isSelected ):
		"""
		神机匣水晶摘除页面
		"""
		self.isRemoveCrystalSelected = isSelected


	# ----------------------------------------------------------------
	# 调用cell server的接口
	# ----------------------------------------------------------------
	def moveKbItemToKitTote( self, srcKitTote, srcOrder, dstKitTote ):
		"""
		转换某个背包类型的道具为背包。
		client所做的所有检查都只是预检查，服务器必须重现这些所有的检查。

		@param  srcKitTote: 道具栏位置，表示从哪个道具栏里拿背包道具出来,Define in csdefine.py
		@type   srcKitTote: INT8
		@param   srcOrder: 道具位置
		@type    srcOrder: INT16
		@param  dstKitTote: 道具栏位置，表示新的背包放到哪个位置
		@type   dstKitTote: INT8
		@return:            如果请求被发送则返回True，否则返回False
		@rtype:             BOOL
		"""
		order = srcKitTote * csdefine.KB_MAX_SPACE + srcOrder
		srcItem = self.itemsBag.getByOrder( order )
		if srcItem is None:
			self.statusMessage( csstatus.CIB_MSG_ITEM_NOT_EXIST )
			return False

		if srcItem.isFrozen():
			self.__isFrozenItemMsg()
			return False

		itemType = srcItem.getType()
		itemAmount = srcItem.getAmount()
		# 如果是普通物品，则直接进入包裹
		if itemType not in ItemTypeEnum.KITBAG_LIST:
			#如果拖入物品本身就所在的包裹，直接返回2008-07-25 spf
			if srcKitTote == dstKitTote:
				return False
			# 如果物品是可叠加物品且能够叠加到目标包裹的叠加物品上则使用moveItemToKitTote接口
			if srcItem.getStackable() > 1 and self.canStackableInKit( srcItem.id, srcItem.isBinded(), itemAmount, dstKitTote ):	# 如果物品能在目标包裹里叠加
				self.cell.moveItemToKitTote( order, dstKitTote )
				return True
			freeOrder = self.getFreeOrderFK( dstKitTote )
			if dstKitTote == csdefine.KB_CASKET_ID and self.isRemoveCrystalSelected:
				if srcItem.isEquip():
					freeOrder = csdefine.KB_MAX_SPACE * dstKitTote + csdefine.KB_CASKET_SPACE
				elif srcItem.id in crystals:
					freeOrder = csdefine.KB_MAX_SPACE * dstKitTote +csdefine.KB_CASKET_SPACE + 1
				else:
					self.pyBox = showMessage( mbmsgs[0x03e6],"",MB_OK, None )
					return
			if freeOrder == -1:
				return False
			self.cell.swapItem( order, freeOrder )
			return True
		# 如果是神机匣，则只能放在第6个包裹位
		# CSOL-2151：神机匣也可以通过拖动放到未打开的包裹
		if itemType == ItemTypeEnum.ITEM_WAREHOUSE_CASKET and dstKitTote  != csdefine.KB_CASKET_ID:
			freeOrder = self.getFreeOrderFK( dstKitTote )
			if freeOrder == -1:
				return False
			self.cell.swapItem( order, freeOrder )
			return True
		# 如果是普通背包，则只能放在第2-5个包裹位
		if itemType == ItemTypeEnum.ITEM_WAREHOUSE_KITBAG:
			if ( dstKitTote <= csdefine.KB_COMMON_ID or dstKitTote >= csdefine.KB_CASKET_ID ):
				return False
		if self.kitbags.has_key( dstKitTote ):
			kitItem = self.kitbags[dstKitTote]
			if kitItem.isFrozen():
				self.__isFrozenItemMsg()
				return False

			# 如果要替换的包包里面有物品，则不能替换 16:27 2008-5-19 yk
			#if self.getFreeOrderCountFK( dstKitTote ) != kitItem.getMaxSpace():
			#	self.statusMessage( csstatus.CIB_MSG_BAG_NOT_NULL )
			#	return False

			if itemType == ItemTypeEnum.ITEM_WAREHOUSE_CASKET:	# 对于神机夹，如果里面有东西就不能换位 by 姜毅
				if csdefine.KB_CASKET_ID in self.kitbags and self.getFreeOrderCountFK( csdefine.KB_CASKET_ID ) != self.kitbags[csdefine.KB_CASKET_ID].getMaxSpace():
					self.statusMessage( csstatus.CIB_MSG_BAG_NOT_NULL )
					return False
			elif kitItem.getMaxSpace() >= srcItem.getMaxSpace():	# 如果目标包裹空间大于置换的包裹空间，不能替换．17:37 2008-10-30 wsf
				self.statusMessage( csstatus.CIB_PLACE_EXIST_BIGER_BAG )
				return False

		# 向cell发送请求
		self.cell.moveKbItemToKitTote( order, dstKitTote )
		return True

	def moveKitbagToKbItem( self, srcKitTote, dstKitTote, dstOrder ):
		"""
		转换某个背包为背包类型的道具
		@param  srcKitTote: 背包栏位，表示从哪个背包位把背包拿出来
		@type   srcKitTote: INT8
		@param  dstKitTote: 目标背包栏位，表示该背包拿出来放在哪个包裹
		@type   dstKitTote: INT8
		@param  dstOrder: 目标背包索引，表示该背包拿出来放在哪个包裹的哪个位置
		@type   dstOrder: INT8
		@return:         如果请求被发送则返回True，否则返回False
		@rtype:          BOOL
		"""
		dOrder = dstKitTote * csdefine.KB_MAX_SPACE + dstOrder
		if len( self.getItems( srcKitTote ) ) != 0:
			# 包裹非空，不能移出来作为道具
			self.statusMessage( csstatus.CIB_MSG_BAG_NOT_NULL )
			return False

		if srcKitTote == dstKitTote:
			self.statusMessage( csstatus.CIB_MSG_KITBAG_NOT_ALLOW )
			return False

		item = self.kitbags.get( srcKitTote )

		if item is None:
			self.statusMessage( csstatus.CIB_MSG_INVALID_KITBAG, srcKitTote )
			return False

		if item.isFrozen():
			self.__isFrozenItemMsg()
			return False

		dstItem = self.itemsBag.getByOrder( dOrder )
		if dstItem is not None and dstItem.getType() == ItemTypeEnum.ITEM_WAREHOUSE_KITBAG:
			self.cell.moveKbItemToKitTote( dOrder, srcKitTote )
			return True

		self.cell.moveKitbagToKbItem( srcKitTote, dOrder )
		return True

	def swapKitbag( self, srcKitOrder, dstKitOrder ):
		"""
		交换两个背包的位置
		@param  srcKitOrder: 源背包栏位
		@type   srcKitOrder: INT8
		@param  dstKitOrder: 目标背包栏位
		@type   dstKitOrder: INT8
		@return:         如果请求被发送则返回True，否则返回False
		@rtype:          BOOL
		"""
		if srcKitOrder == dstKitOrder: return False
		# 背包的交换仅仅限于第2-5位背包位的交换(第一位为固定的，第八位为神机匣)
		if srcKitOrder <= csdefine.KB_COMMON_ID or srcKitOrder >= csdefine.KB_CASKET_ID:
			self.statusMessage( csstatus.CIB_MSG_KITBAG_NOT_ALLOW )
			return False

		if dstKitOrder <= csdefine.KB_COMMON_ID or dstKitOrder >= csdefine.KB_CASKET_ID:
			self.statusMessage( csstatus.CIB_MSG_KITBAG_NOT_ALLOW )
			return False

		# 向 Cell 发送消息
		self.cell.swapKitbag( srcKitOrder, dstKitOrder )

	# ------------------------------------------------------------------------------------
	# for cell 的 callback 函数
	# ------------------------------------------------------------------------------------
	# 添加物品
	# ------------------------------------------------------------------------------------
	def addItemCB( self, itemInstance ):
		"""
		Define method.
		某个背包的某个位置上新增一个道具。
		我们可以在这里做些额外的事情，例如刷新道具栏等。
		我的原则是相信服务器告诉你的一切——即使是错的。
		因此在这里我并不判断参数的正确性，
		将来可以考虑使用try把有可能出错的消息pass掉，但现在并不考虑这个问题。

		@param itemInstance: 继承于CItemBase的自定义类型道具实例
		@type  itemInstance: class instance
		@return:             无
		"""
		#DEBUG_MSG( "receive new item: kitTote = %i, orderID = %i, keyname = %s" % (kitTote, orderID, itemInstance) )
		orderID = itemInstance.getOrder()
		srcKitID = itemInstance.getKitID()
		if not self.itemsBag.add( orderID, itemInstance ):
			raise AssertionError, "repeat receive new item: srcKitID = %i, uid = %i, orderID = %i, keyname = %s" % (srcKitID, itemInstance.uid, orderID, itemInstance)
		itemInfo = ItemInfo( itemInstance )

		if srcKitID == csdefine.KB_EQUIP_ID :
			self.onUpdateNormalSkill()
			ECenter.fireEvent( "EVT_ON_EQUIPBAG_ADD_ITEM", itemInfo )
		else:
			ECenter.fireEvent( "EVT_ON_KITBAG_ADD_ITEM", itemInfo )
			rds.opIndicator.onPlayerAddedItem( itemInfo.id )
		rds.helper.courseHelper.addItem( itemInfo.itemType )	#触发过程帮助

	# ------------------------------------------------------------------------------------
	# 移除物品
	# ------------------------------------------------------------------------------------
	def removeItemCB( self, order ):
		"""
		Define method.
		给cell的回调方法，删除某个背包上的某个道具。
		我们可以在这里做些额外的事情，例如刷新道具栏等。
		我的原则是相信服务器告诉你的一切——即使是错的。
		因此在这里我并不判断参数的正确性，
		将来可以考虑使用try把有可能出错的消息pass掉，但现在并不考虑这个问题。

		@param   order: 源背包的源道具
		@type    order: INT16
		@return:        无
		"""
		item = self.itemsBag.getByOrder( order )
		if item is None : return
		kitID = item.getKitID()
		itemCopy = copy.copy( item )
		self.itemsBag.removeByOrder( order )
		itemInfo = ItemInfo( itemCopy )
		if kitID == csdefine.KB_EQUIP_ID :
			self.onUpdateNormalSkill()
			ECenter.fireEvent( "EVT_ON_EQUIPBAG_REMOVE_ITEM", itemInfo )
		else:
			ECenter.fireEvent( "EVT_ON_KITBAG_REMOVE_ITEM", itemInfo )

	# ------------------------------------------------------------------------------------
	# 交换物品
	# ------------------------------------------------------------------------------------
	def swapItemCB( self, srcOrder, dstOrder ):
		"""
		Define method.
		交换两个道具的位置。
		我们可以在这里做些额外的事情，例如刷新道具栏等。
		我的原则是相信服务器告诉你的一切——即使是错的。
		因此在这里我并不判断参数的正确性，
		将来可以考虑使用try把有可能出错的消息pass掉，但现在并不考虑这个问题。

		@param   srcOrder: 源背包的源道具
		@type    srcOrder: INT16
		@param   dstOrder: 目标背包的源道具
		@type    dstOrder: UINT8
		@return:           无
		"""
		oldSrcItem = copy.copy( self.itemsBag.getByOrder( srcOrder ) )
		oldDstItem = copy.copy( self.itemsBag.getByOrder( dstOrder ) )
		srcKitTote = srcOrder/csdefine.KB_MAX_SPACE
		dstKitTote = dstOrder/csdefine.KB_MAX_SPACE
		self.itemsBag.swapOrder( srcOrder, dstOrder )

		newSrcItem = self.itemsBag.getByOrder( srcOrder )
		newDstItem = self.itemsBag.getByOrder( dstOrder )

		srcOrderID = srcOrder%csdefine.KB_MAX_SPACE
		dstOrderID = dstOrder%csdefine.KB_MAX_SPACE
		if srcKitTote == csdefine.KB_EQUIP_ID:
			if oldSrcItem.getType() == ItemTypeEnum.ITEM_SYSTEM_TALISMAN:
				ECenter.fireEvent( "EVT_ON_ROLE_ACTIVE_TALISNAM", None )
			if oldDstItem is None:
				ECenter.fireEvent( "EVT_ON_EQUIPBAG_REMOVE_ITEM", ItemInfo( oldSrcItem ) )
				ECenter.fireEvent( "EVT_ON_UNWIELD_ADD_KITBAGITEM", ItemInfo( newDstItem ) )
			else:
				ECenter.fireEvent( "EVT_ON_EQUIPBAG_UPDATE_ITEM", ItemInfo( newSrcItem ) )
				ECenter.fireEvent( "EVT_ON_UNWIELD_TO_KITBAG", dstKitTote, dstOrderID, ItemInfo( newDstItem ) )	#卸下装备到背包中
				ECenter.fireEvent( "EVT_ON_ITEM_EQUIPED", ItemInfo( oldDstItem ) )	# 通知该物品被装备到角色身上
			self.onUpdateNormalSkill()
			return
		if dstKitTote == csdefine.KB_EQUIP_ID:
			if oldDstItem is None:
				ECenter.fireEvent( "EVT_ON_WIELD_REMOVE_KITBAGITEM", ItemInfo( oldSrcItem ) )
				ECenter.fireEvent( "EVT_ON_EQUIPBAG_ADD_ITEM", ItemInfo( newDstItem ) )
			else:
				if oldDstItem.getType() == ItemTypeEnum.ITEM_SYSTEM_TALISMAN:
					ECenter.fireEvent( "EVT_ON_ROLE_ACTIVE_TALISNAM", None )
				ECenter.fireEvent( "EVT_ON_EQUIPBAG_SWAP_ITEM", ItemInfo( newDstItem ) )#提醒装备栏与背包中的物品交换属性
				ECenter.fireEvent( "EVT_ON_UNWIELD_TO_KITBAG", srcKitTote, srcOrderID, ItemInfo( newSrcItem ) )#卸下装备备到背包中
			ECenter.fireEvent( "EVT_ON_ITEM_EQUIPED", ItemInfo( oldSrcItem ) )	# 通知该物品被装备到角色身上
			self.onUpdateNormalSkill()
			return

		if newSrcItem is None: newSrcItemInfo = None
		else: newSrcItemInfo = ItemInfo( newSrcItem )
		if newDstItem is None: newDstItemInfo = None
		else: newDstItemInfo = ItemInfo( newDstItem )

		ECenter.fireEvent( "EVT_ON_KITBAG_SWAP_ITEM", srcKitTote, srcOrderID, newSrcItemInfo, dstKitTote, dstOrderID, newDstItemInfo )

	def removeKitbagCB( self, kitTote ):
		"""
		Define method.
		删除某个位置的背包
		我们可以在这里做些额外的事情，例如刷新道具栏等。
		我的原则是相信服务器告诉你的一切——即使是错的。
		因此在这里我并不判断参数的正确性，
		将来可以考虑使用try把有可能出错的消息pass掉，但现在并不考虑这个问题。

		@param kitTote: 源背包
		@type  kitTote: INT8
		@param dstOrder: 目标位置
		@type  dstOrder: INT16
		@return:             无
		"""
		del self.kitbags[kitTote]
		GUIFacade.removeKitbagCB( kitTote )

	def swapKitbagCB( self, srcKitOrder, dstKitOrder ):
		"""
		Define method.
		交换两背包的位置，服务器返回信息
		@param srcKitOrder: 源背包位
		@type  srcKitOrder: INT8
		@param dstKitOrder: 目标背包位
		@type  dstKitOrder: INT8
		"""
		srcKitItem = self.kitbags.get( srcKitOrder )
		scrKitInfo = ItemInfo( srcKitItem )
		dstKitItem = self.kitbags.get(dstKitOrder)
		srcItemsList = self.getItems( srcKitOrder )
		swapItemData = {}	# 记录交换数据
		srcOrderAmend = csdefine.KB_MAX_SPACE *( dstKitOrder - srcKitOrder )
		if dstKitItem is not None:
			dstKitInfo = ItemInfo( dstKitItem )
			dstItemsList = self.getItems( dstKitOrder )
			# 源背包和目标背包都存在，包裹互换
			for item in srcItemsList:
				swapItemData[item.order + srcOrderAmend] = item
				self.itemsBag.removeByOrder( item.order )
			dstOrderAmend = csdefine.KB_MAX_SPACE *( srcKitOrder - dstKitOrder )
			for item in dstItemsList:
				swapItemData[item.order + dstOrderAmend] = item
				self.itemsBag.removeByOrder( item.order )
			self.kitbags.update( { srcKitOrder : dstKitItem, dstKitOrder : srcKitItem } )
		else:
			# 源背包存在，目标背包不存在，包裹移位
			dstKitInfo = None
			for item in srcItemsList:
				swapItemData[item.order + srcOrderAmend] = item
				self.itemsBag.removeByOrder( item.order )
			self.kitbags[dstKitOrder] = self.kitbags.pop( srcKitOrder )

		for order, itemData in swapItemData.iteritems():
			self.itemsBag.add( order, itemData )

		ECenter.fireEvent( "EVT_ON_SWRAP_PACK_ITEMS", srcKitOrder, dstKitInfo, dstKitOrder, scrKitInfo )

	def addKitbagCB( self, kitTote, kitbagItem ):
		"""
		Define method.
		某个位置放一个背包
		我们可以在这里做些额外的事情，例如刷新道具栏等。
		我的原则是相信服务器告诉你的一切——即使是错的。
		因此在这里我并不判断参数的正确性，
		将来可以考虑使用try把有可能出错的消息pass掉，但现在并不考虑这个问题。

		@param    kitTote: 新加的背包放在哪个位置
		@type     kitTote: INT8
		@param orderID: 转换为背包的物品
		@type  orderID: Int16
		@return:           无
		"""
		self.kitbags[kitTote] = kitbagItem
		GUIFacade.addKitbagCB( kitTote, kitbagItem )

	# ------------------------------------------------------------------------------------
	# 物品属性改变通知
	# ------------------------------------------------------------------------------------
	def onItemAttrUpdated( self, orderID, attrIndex, stream ):
		"""
		Define method.
		物品属性更改通知

		@param orderID: 道具要放在哪
		@type  orderID: UINT8
		@param    attrIndex: 属性名索引 见 common/ItemAttrClass.py
		@type     attrIndex: UINT8
		@param  stream: 属性值，需要使用相关属性的createFromStream()方法获取真正值
		@type   stream: STRING
		"""
		kitTote = orderID/csdefine.KB_MAX_SPACE
		item = self.itemsBag.getByOrder( orderID )
		if item is None:
			ERROR_MSG( "item not found in kitbag order %i." %  orderID )
			return
		name = ItemAttrClass.m_itemAttrSendMap[ attrIndex ]
		value = ItemAttrClass.m_itemAttrMap[name].createFromStream( stream )
		if name == "amount":
			item.setAmount( value )
		else:
			item.set( name, value )

		itemInfo = ItemInfo( item )
		if itemInfo.kitbagID == csdefine.KB_EQUIP_ID:
			ECenter.fireEvent( "EVT_ON_EQUIPBAG_UPDATE_ITEM", itemInfo )
		else:
			ECenter.fireEvent( "EVT_ON_KITBAG_UPDATE_ITEM", itemInfo )

	# ------------------------------------------------------------------------------------
	# 物品临时属性(不保存属性 see item.tmpExtra)改变通知
	# ------------------------------------------------------------------------------------
	def onItemTempAttrUpdated( self, orderID, attrIndex, stream ):
		"""
		Define method.
		物品属性更改通知

		@param orderID: 道具要放在哪
		@type  orderID: UINT8
		@param    attrIndex: 属性名索引
		@type     attrIndex: UINT8
		@param  stream: 属性值，需要使用相关属性的createFromStream()方法获取真正值
		@type   stream: STRING
		"""
		kitTote = orderID/csdefine.KB_MAX_SPACE
		item = self.itemsBag.getByOrder( orderID )
		name = ItemAttrClass.m_itemAttrSendMap[attrIndex]
		value = ItemAttrClass.m_itemAttrMap[name].createFromStream( stream )
		item.setTemp( name, value )
		itemInfo = ItemInfo( item )
		if itemInfo.kitbagID == csdefine.KB_EQUIP_ID:
			ECenter.fireEvent( "EVT_ON_EQUIPBAG_UPDATE_ITEM", itemInfo )
		else:
			ECenter.fireEvent( "EVT_ON_KITBAG_UPDATE_ITEM", itemInfo )

	# ------------------------------------------------------------------------------------
	# 神机匣使用次数改变通知，15:15 2008-5-19 yk
	# ------------------------------------------------------------------------------------
	def onUpdateUseDegree( self, useDegree ):
		"""
		Define method.
		更新神机匣使用次数
		@param useDegree: 剩余使用次数
		@type  useDegree: UINT8
		"""
		kitbagItem = self.kitbags[csdefine.KB_CASKET_ID]
		kitbagItem.set( "useDegree", useDegree )
		ECenter.fireEvent( "EVT_ON_CASKET_REMAIN_TIMES", useDegree )
		ECenter.fireEvent( "EVT_ON_UPDATE_PACK_ITEM", csdefine.KB_CASKET_ID, ItemInfo( kitbagItem ) )


	# ------------------------------------------------------------------------------------
	# 神机匣锁/解锁 by姜毅
	# ------------------------------------------------------------------------------------
	def lockCasket( self ):
		"""
		通知神机夹上锁
		"""
		self.isCasketLocked = True
		ECenter.fireEvent( "EVT_ON_LOCK_CASKET" )

	def unLockCasket( self ):
		"""
		defined method
		使用后神机夹面板会被上锁，这里通知解锁神机夹
		"""
		self.isCasketLocked = False
		ECenter.fireEvent( "EVT_ON_UNLOCK_CASKET" )

	# ------------------------------------------------------------------------------------
	# 背包密码锁功能
	# ------------------------------------------------------------------------------------
	def kitbags_setPassword( self, srcPassword, password ):
		"""
		设置、修改背包密码都使用此接口。背包密码为空时，srcPassword值为"",修改密码时srcPassword值为 玩家的旧密码

		param srcPassword:		背包原密码,
		type srcsrcPassword:	STRING
		param password:	玩家输入的密码
		type password:	STRING
		"""
		self.cell.kitbags_setPassword( srcPassword, password )

	def kitbags_lock( self ):
		"""
		给背包上锁，在玩家设置了密码且还没有对背包上锁的前提下，才满足此接口的使用条件
		"""
		self.cell.kitbags_lock()

	def kitbags_unlock( self, srcPassword ):
		"""
		给背包解锁，在玩家设置了背包密码且给背包上锁的前提下，才满足此接口的使用条件。
		注意：解锁的操作如果在本次登陆期间失败3次，24小时内不允许背包解锁操作。

		param srcPassword:		背包原密码,
		type srcsrcPassword:	STRING
		"""
		self.cell.kitbags_unlock( srcPassword )


	def kitbags_clearPassword( self, srcPassword ):
		"""
		给背包永久解锁，玩家已经给背包设置了密码的前提下，此接口清除玩家设置的密码，把背包密码置为空。
		注意：永久解锁的操作如果在本次登陆期间失败3次，24小时内不允许背包解锁操作。

		param srcPassword:		背包原密码,
		type srcsrcPassword:	STRING
		"""
		self.cell.kitbags_clearPassword( srcPassword )

		# ---------------------notify UI--------------------------

		#背包密码锁状态数据kitbagsLockerStatus的状态如下（界面实现时可参考）：
		#0000 0000:无密码状态
		#0000 0001:有密码状态
		#0000 0010:锁定状态
		#0111 0000:背包解锁失败次数

	def set_kitbagsLockerStatus( self, oldValue ):
		"""
		背包密码锁状态更新函数的自动更新函数
		"""
		ECenter.fireEvent( "EVT_ON_BAGLOCK_STATUAS_CHANGE", self.kitbagsLockerStatus )

		# 通知界面，wsf

	#def set_kitbagsUnlockLimitTime( self, oldValue ):
		"""
		背包解锁限制时间的自动通知函数
		"""
	#	printStackTrace()
	#	if self.kitbagsUnlockLimitTime > 0:
	#		# 通知界面，因为如果kitbagsUnlockLimitTime > 0，说明kitbagsUnlockLimitTime是第一次设置，
	#		# 需要通知玩家他的行为受限了，wsf
	#		ECenter.fireEvent( "EVT_ON_BAGLOCK_TIME_CHANGE", self.kitbagsUnlockLimitTime )

	def kitbags_lockerNotify( self, flag ):
		"""
		Define method.
		背包密码锁通知函数

		if flag == 0: 设置背包密码成功的通知
		if flag == 1: 背包密码锁更改成功的通知
		if flag == 2: 输错解锁密码通知
		if flag == 3: 输错旧密码的通知
		if flag == 4: 给背包上锁成功的通知
		if flag == 5: 给背包解锁成功的通知
		if flag == 6: 已经输错三次密码
		type flag:	UINT8
		"""
		ECenter.fireEvent( "EVT_ON_BAGLOCK_FLAG_CHANGE", flag )

	def kitbags_onConfirmForceUnlock( self ) :
		"""
		Define method.
		强制解锁背包确认
		"""
		def confirmUnlock( result ) :
			if result == RS_YES :
				self.cell.kitbags_onForceUnlock()
		# 强制解锁背包需要%s，解锁后密码将被清空，你确定要申请吗？
		needTime = csconst.KITBAG_FORCE_UNLOCK_LIMIT_TIME
		needHours = needTime / 3600
		needMinutes = needTime % 3600 / 60
		needSeconds = needTime % 60
		needTimeText = ""
		if needHours :
			needTimeText += "%d%s" % ( needHours, ShareTexts.CHTIME_HOUR )
		if needMinutes :
			needTimeText += "%d%s" % ( needMinutes, ShareTexts.CHTIME_MINUTE )
		if needSeconds :
			needTimeText += "%d%s" % ( needSeconds, ShareTexts.CHTIME_SECOND )
		msg = mbmsgs[0x00a3] % needTimeText
		if self.pyBox is not None:
			self.pyBox.visible = False
			self.pyBox = None
		self.pyBox = showMessage( msg, "", MB_YES_NO, confirmUnlock )

	def iskitbagsLocked( self ):
		"""
		验证背包是否被锁定
		"""
		return ( self.kitbagsLockerStatus >> 1 ) & 0x01 == 1	# 表示背包是否被锁定与否状态位是否为1

	def autoStuffFC( self, orders ):
		"""
		Define Method
		服务器自动放入打造材料消息发来
		@return 			: None
		"""
		ECenter.fireEvent( "EVT_ON_GET_AUTO_STUFF", orders )
	def clearVendSignBoard( self ):
		RoleVend.vend_onLeaveWorld( self )

	def playIconNotify( self, itemInstance ):
		"""
		Define method.
		"""
		itemInfo = ItemInfo( itemInstance )
		ECenter.fireEvent( "EVT_ON_ICON_PLAY", itemInfo )

# ItemsBag.py
