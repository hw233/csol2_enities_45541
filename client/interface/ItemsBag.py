# -*- coding: gb18030 -*-
#
# $Id: ItemsBag.py,v 1.136 2008-09-02 05:11:00 pengju Exp $

"""
@summary				:	����ģ��
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
	����һ�������� for role of client only

	@ivar kitbags: һ����Ʒ�б������洢��Ʒ
	@type kitbags: ITEMS

	kitbagsLockerStatus��ʾ����������״̬�����ݣ���������״̬���Է����ɴ����ݲ�ѯ�ó�������Ҫ��def��������������ݡ��������£�
	kitbagsLockerStatusλ��Ϊ8��ʹ�����ֽ�ģʽ�ұߵĵ�һλ����ʾ�����Ƿ����������״̬����λ�ֽ�ģʽΪ0ʱ��ʾ��������Ϊ1ʱ��ʾ������
	ʹ���ұߵڶ�λ����ʾ�����Ƿ�������״̬���ݣ�������Ϊ0������Ϊ1���ұߵ�������λ�����Ժ���չ��Ҫ��
	ʹ�����ұߵ��塢������λ����ʾ������������ʧ�ܴ������ݣ������Ա�ʾ7��ʧ�ܣ����ֽ�ģʽΪ111��kitbagsLockerStatus����4λ�������ɵò������ݣ�
	ÿʧ��һ�ο�����λ�����+1��10�������㡣

		����������״̬����kitbagsLockerStatus��״̬���£�����ʵ��ʱ�ɲο�����
		0000 0000:������״̬
		0000 0001:������״̬
		0000 0010:����״̬
		0111 0000:��������ʧ�ܴ���
	"""
	def __init__( self ):
		RoleVend.__init__( self )
		RoleSwapItem.__init__( self )		# wsf,��ʼ������ϵͳ
		RoleTradeWithNPC.__init__( self )
		RoleTradeWithMerchant.__init__( self )
		self.itemsBag = KitbagBase()		# ������Ʒ������������Ʒ�͵���( hyw -- 2008.06.10 )
		self.kitbags = {}					# ������{ order : item }���������б���( hyw -- 2008.06.10 )
		self.mySIItem = {}
		self.dstSIItem = {}
		self.pyBox = None					# ����ȷ�Ͽ�
		self.isCasketLocked = False			# ������������ by ����
		self.isRemoveCrystalSelected = False

		rds.shortcutMgr.setHandler( "ACTION_PICK_UP_ITEM", ItemsBag.__pickItem )

		# һ����װ��λ�������ж�Ӧ�� by jd
		self.suitPartDict = {
			ItemTypeEnum.CWT_HEAD :0, # ͷ     ���� ͷ��
			ItemTypeEnum.CWT_NECK :1, # ��     ���� ����
			ItemTypeEnum.CWT_BODY :2, # ����   ���� ���
			ItemTypeEnum.CWT_BREECH :3, # �β�   ���� ����
			ItemTypeEnum.CWT_VOLA :4, # ��     ���� ����
			ItemTypeEnum.CWT_HAUNCH :5, # ��     ���� ����
			ItemTypeEnum.CWT_CUFF :6, # ��     ���� ����
			ItemTypeEnum.CWT_LEFTHAND :7, # ����   ���� ����
			ItemTypeEnum.CWT_RIGHTHAND :8, # ����   ���� ����
			ItemTypeEnum.CWT_FEET :9, # ��     ���� Ь��
			ItemTypeEnum.CWT_LEFTFINGER :10, # ����ָ ���� ��ָ
			ItemTypeEnum.CWT_RIGHTFINGER :11, # ����ָ ���� ��ָ
			ItemTypeEnum.CWT_TALISMAN :12, # ����
			}


	# ----------------------------------------------------------------
	# private methods
	# ----------------------------------------------------------------
	def __useEquipItem( self, uid ):
		"""
		װ��/ж��װ��
		@param uid 			: ��Ʒ��ΨһID
		@type uid			: INT64
		"""

		item = self.getItemByUid_( uid )

		if item.getType() == ItemTypeEnum.ITEM_POTENTIAL_BOOK and item.isPotentialMax() and item.getOrder() != ItemTypeEnum.CEL_POTENTIAL_BOOK:
			self.__useSkillItem( uid )
			return
		# �Ҽ�װ��ʱ��������
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
				if ( not item2 ) and item1:	# ������ֿ� �� �����Ѿ�װ��
					dstOrderID = orders[1]
		self.moveItem( kitOrder, orderID, dstbagID, dstOrderID )

	def __useQuestItem( self, uid ):
		"""
		ʹ��������Ʒ
		@param uid 			: ��Ʒ��ΨһID
		@type uid			: INT64
		"""
		self.cell.selectQuestFromItem( uid )

	def __useSkillItem( self, uid ):
		"""
		ʹ�ü�����Ʒ
		@param uid 			: ��Ʒ��ΨһID
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
		if target:	# ���Ŀ�겻Ϊ�գ���Ŀ�겻���Լ�����ôҪ���Ŀ��ʹ��
			if target.id != self.id and not sk.isNotRotate:
				self.turnaround( target.matrix, None )
		state = item.use( self, target )
		if state != csstatus.SKILL_GO_ON:
			self.statusMessage( state )
			return
		if castType == csdefine.SKILL_CAST_OBJECT_TYPE_POSITION:return				#��λ��ʩ�����⴦��
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
				# ������輼���������Ƿ�����滻����һ�����ܣ�
				self.pyBox = showMessage( 0x00a1, "", MB_OK_CANCEL, query )
				return

		ECenter.fireEvent( "EVT_ON_ITEM_USE", item )
		if targetObj:
			self.cell.useItem( uid, targetObj )

	@reimpl_itemsBag.deco_itemsBagUseKitBagItem
	def __useKitBagItem( self, uid ):
		"""
		ʹ�ñ�����Ʒ
		@param uid 			: ��Ʒ��ΨһID
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
		ʹ����ͨ��Ʒ
		@param uid 			: ��Ʒ��ΨһID
		@type uid			: INT64
		"""
		targetObj = SkillTargetObjImpl.createTargetObjEntity( self )
		self.cell.useItem( uid, targetObj )

	def __useCasketItem( self, uid ):
		"""
		ʹ�����ϻ��Ʒ
		@param uid 			: ��Ʒ��ΨһID
		@type uid			: INT64
		"""
		item = self.getItemByUid_( uid )
		kitOrder = item.getKitID()
		orderID = item.getOrder()%csdefine.KB_MAX_SPACE
		self.moveKbItemToKitTote( kitOrder, orderID, csdefine.KB_CASKET_ID )

	def __useVehicleItem( self, uid ):
		"""
		ʹ�����
		@param uid 			: ��Ʒ��ΨһID
		@type uid			: INT64
		"""
		if len( self.vehicleDatas ) >= csconst.VEHICLE_AMOUNT_MAX:
			self.statusMessage( csstatus.VEHICLE_AMOUNT_MAX )
			return
		self.cell.useVehicleItem( uid )
		
	def __useTurnVehicleItem( self, uid ):
		"""
		ʹ��ת������Ʒ��������
		@param uid 			: ��Ʒ��ΨһID
		@type uid			: INT64
		"""
		if len( self.vehicleDatas ) >= csconst.VEHICLE_AMOUNT_MAX:
			self.statusMessage( csstatus.VEHICLE_AMOUNT_MAX )
			return
		self.cell.useTurnVehicleItem( uid )

	def __useTalismanStone( self, uid ):
		"""
		ʹ�����ʯ
		@param uid 			: ��Ʒ��ΨһID
		@type uid			: INT64
		"""
		# �ж���ҷ����Ƿ����
		order = ItemTypeEnum.CWT_TALISMAN
		talismanItem = self.getItem_( order )
		item = self.getItemByUid_( uid )
		if talismanItem is None:
			self.statusMessage( csstatus.TALISMAN_NO_WIELD )
			return
		# �ж��ǲ��Ƿ�������
		if talismanItem.getType() != ItemTypeEnum.ITEM_SYSTEM_TALISMAN:
			self.statusMessage( csstatus.TALISMAN_SHAN_ZHAI )
			return
		# ����ʹ�õ����ʯȷ���ܹ������Ʒ��
		useGrade = rds.talismanEffects.getAcGradeByItemID( item.id )
		if useGrade is None: return

		# �жϷ�����ǰ��Ʒ�������Ƿ����ø���Ʒ����
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

		# ��ʾû����Ҫ���������
		if newData is None:
			self.statusMessage( csstatus.TALISMAN_GRADE_NONEED )
			return

		self.cell.activateTalismanAttr( uid )

	def __isFrozenItemMsg( self ):
		"""
		����ϸ�ֶ�����Ʒ����ʾ
		"""
		if self.state == csdefine.ENTITY_STATE_VEND: #����������Ʒ�Ǵ��ڰ�̯״̬
			self.statusMessage( csstatus.SKILL_USE_ITEM_VEND_ISFROZEN )
		elif self.state == csdefine.TRADE_SWAP: #����������Ʒ�Ǵ��ڽ���״̬
			self.statusMessage( csstatus.ROLE_ITEM_ISFROZEN )
		else:
			self.statusMessage( csstatus.CIB_MSG_FROZEN )

	@staticmethod
	def __pickItem() :
		"""
		������Ʒ���� Tact ���ƶ����⣭��hyw��2008.12.29��
		ע��shortcuMgr �жԿ�ݼ����������������ã��������ʹ����ͨ����������;��ݼ����������ܻᶪ����
			���������þ�̬��������Ŀǰ����֪��ʲôԭ����Ϊ������ ItemsBag ���ﲻ��ʹ����ͨ����
		"""
		self = BigWorld.player()
		if self.currentItemBoxID != 0 and BigWorld.entities.has_key( self.currentItemBoxID ):
			# ����Ѿ��д򿪵����ӣ��ٰ���Z������ʰȡ��Ʒ
			box = BigWorld.entities[self.currentItemBoxID]
			box.pickUpAllItems()
			self.stopPickUp()
			return True
		if self.affectAfeard:
			return False
		if not self.isAlive():
			return False
		searchRange = 20.0									# ����������Ʒ�ķ�Χ����ʱд����
		space = 3.0											# ��ʰ����
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
		EntityCache�������
		"""
		if self.iskitbagsLocked() : # �������������������ʾ
			BigWorld.player().statusMessage( csstatus.CIB_REMIND_MSG_KITBAG_LOCKED )

	# ----------------------------------------------------------------
	# public for client
	# ----------------------------------------------------------------
	def useItem( self, uid ):
		"""
		�Ҽ������ͨ��Ʒ����ĳ����Ʒ
		@param 			kitOrder	  : ����λ��
		@type  			kitOrder	  : UINT8
		@param  		orderID		  : ��Ʒλ��
		@type   		orderID		  : UINT8
		@return						  : ��
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
		if item.getBindType() == ItemTypeEnum.CBT_EQUIP:	# �����װ����
			def query( rs_id ):
				if rs_id == RS_OK: self.useItemDependOnType( uid, item, i_type )
			if not self.pyBox is None:
				self.pyBox.visible = False
				self.pyBox = None
			# װ���󽫰󶨣��Ƿ�װ����
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
			# �����������·�����Ҫ���ķ���ʯ��ȷ��Ҫ����?
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
			# װ���󽫰󶨣��Ƿ�װ����
			self.pyBox = showMessage( 0x00a7, "", MB_OK_CANCEL, query )
			return
		self.useItemDependOnType( uid, item, i_type )

	def useItemDependOnType( self, uid, item, i_type ):
		"""
		������Ʒ����ѡ���Ӧ��ʹ�ýӿ� by����
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
		����һ����Ʒ

		@param uid: ����ΨһID
		@type  uid: INT64
		@return:        ������󱻷����򷵻�True�����򷵻�False
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
		@return:            ������󱻷����򷵻�True�����򷵻�False
		@rtype:             BOOL
		"""
		self.swapItem( srcKitTote, srcOrder, dstKitTote, dstOrder, False )

	def swapItem( self, srcKitTote, srcOrderID, dstKitTote, dstOrderID, isAskAgain = True ):
		"""
		����Ʒ����ǰ��ȷ�� modified by����
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

		if dstKitTote == csdefine.KB_EQUIP_ID:	# �������װ����
			if srcItem.query( "bindType" ) == ItemTypeEnum.CBT_EQUIP and isAskAgain:	# �����װ���� ���ҽ��뺯��·����ͨ��useEquipItem
				def query( rs_id ):
					if rs_id == RS_OK: self.swapItemFunc( srcKitTote, srcOrderID, dstKitTote, dstOrderID, srcItem, dstItem )
				if not self.pyBox is None:
					self.pyBox.visible = False
					self.pyBox = None
				# װ���󽫰󶨣��Ƿ�װ����
				self.pyBox = showMessage( 0x00a2, "", MB_OK_CANCEL, query )
			else:
				self.swapItemFunc( srcKitTote, srcOrderID, dstKitTote, dstOrderID, srcItem, dstItem )
		else:
			self.swapItemFunc( srcKitTote, srcOrderID, dstKitTote, dstOrderID, srcItem, dstItem )
	
	def swapItemFunc( self, srcKitTote, srcOrderID, dstKitTote, dstOrderID, srcItem, dstItem ):
		"""
		�����������ߵ�λ�á�

		��Ҫ����Դ������Ŀ�걳�����ͣ��п�����Ҫ���ݲ�ͬ����������ͬ�Ĳ���

		@param  srcKitTote: Դ����Ψһ��ʶ
		@type   srcKitTote: INT8
		@param  srcOrderID: Դ������Դ����
		@type   srcOrderID: INT8
		@param  dstKitTote: Ŀ�걳��Ψһ��ʶ
		@type   dstKitTote: INT8
		@param  dstOrderID: Ŀ�걳����Դ����
		@type   dstOrderID: INT8
		@return:            ������󱻷����򷵻�True�����򷵻�False
		@rtype:             BOOL
		"""
		DEBUG_MSG( "from %i, %i to %i, %i" % (srcKitTote, srcOrderID, dstKitTote, dstOrderID) )
		# Ϊ��ʹ�ýӿ����ܶ���ʹ�� ���������ظ����srcOrder dstOrder
		srcOrder = srcKitTote * csdefine.KB_MAX_SPACE + srcOrderID
		dstOrder = dstKitTote * csdefine.KB_MAX_SPACE + dstOrderID
		if ( srcItem is not None and srcItem.isFrozen() ) or ( dstItem is not None and dstItem.isFrozen() ):
			self.__isFrozenItemMsg()
			return False
		# �����Ʒ�Ǵ�װ���������ģ�����Ҫ����Ŀ����Ʒ�Ƿ��ܷ���װ����
		if srcKitTote == csdefine.KB_EQUIP_ID:
			if self.actionSign( csdefine.ACTION_FORBID_WIELD ):
				self.statusMessage( csstatus.KIT_EQUIP_CANT_STATE )
				return False
			if dstItem:
				state = self.canWieldEquip( srcOrder, dstItem )
				if state != csstatus.KIT_EQUIP_CAN_FIT_EQUIP:
					self.statusMessage( state )
					return False

		# �����ƷҪ�ŵ�װ�����ϣ�����Ҫ���Ǹ���Ʒ�Ƿ��ܷ���װ����
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
				# to normal kitbag ���������ͬ������һ��ﵽ�������ޣ�������λ�û���
				if dstItem is not None and \
					srcItem.id == dstItem.id and \
					srcItem.isBinded() == dstItem.isBinded() and \
					srcItem.getStackable() > 1 and \
					srcItem.getAmount() < srcItem.getStackable() and \
					dstItem.getAmount() < dstItem.getStackable():
						self.combineItem( srcKitTote, srcOrderID, dstKitTote, dstOrderID )
						return True
		#սʿ
		if self.getClass() == csdefine.CLASS_FIGHTER:    # ְҵΪսʿ
			l_item = self.itemsBag.getByOrder( ItemTypeEnum.CEL_LEFTHAND )
			r_item = self.itemsBag.getByOrder( ItemTypeEnum.CEL_RIGHTHAND )
			if l_item and r_item and dstItem and srcItem:
				if srcItem.getType() != dstItem.getType():
					orderIDs = self.getAllNormalKitbagFreeOrders()
					if len( orderIDs ) < 1 :
						self.statusMessage( csstatus.CIB_MSG_UNWIELD_ITEM )
						return False
		# ��cell��������
		self.cell.swapItem( srcOrder, dstOrder )
		return True

	def combineItem( self, srcKitTote, srcOrderID, dstKitTote, dstOrderID ):
		"""
		��һ���������ĳ������������һ��������ĵ��ߺϲ���
		���磺����A���С��ҩˮ��100��������B��С��ҩˮ��20����С��ҩˮ��������Ϊ200��
		�����ǿ���ʹ�ô˷����ѱ���B��С��ҩˮ���ڱ���A��Կճ�һ��λ�á�

		@param  srcKitTote: Դ����Ψһ��ʶ
		@type   srcKitTote: INT8
		@param  srcOrderID: Դ������Դ����
		@type   srcOrderID: INT8
		@param  dstKitTote: Ŀ�걳��Ψһ��ʶ
		@type   dstKitTote: INT8
		@param  dstOrderID: Ŀ�걳����Դ����
		@type   dstOrderID: INT8
		@return:            ������󱻷����򷵻�True�����򷵻�False
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

		# ������ͬ���߲��������
		if srcItem.id != dstItem.id:
			self.statusMessage( csstatus.CIB_MSG_CANNOT_STACKABLE )
			return False
		# �������ĸ��������ֻ��Ŀ���Ƿ��ܵ���
		stackable = dstItem.getStackable()
		if stackable <= 1:
			self.statusMessage( csstatus.CIB_MSG_CANNOT_STACKABLE )
			return False

		if stackable == dstItem.getAmount():
			return

		self.cell.combineItem( srcOrder, dstOrder )		# ��cell��������
		return True

	def splitItem( self, uid, amount ):
		"""
		�ֿ�һ���ɵ��ӵĵ��ߡ�

		��Ҫ����Դ������Ŀ�걳�����ͣ��п�����Ҫ���ݲ�ͬ����������ͬ�Ĳ���

		@param  uid: Դ������Դ���ߵ�ΨһID
		@type   uid: INT64
		@param      amount: ��ʾ��Դ��Ʒ����ֳ����ٸ���
		@type       amount: UINT16
		@return:            ������󱻷����򷵻�True�����򷵻�False
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
		���ϻˮ��ժ��ҳ��
		"""
		self.isRemoveCrystalSelected = isSelected


	# ----------------------------------------------------------------
	# ����cell server�Ľӿ�
	# ----------------------------------------------------------------
	def moveKbItemToKitTote( self, srcKitTote, srcOrder, dstKitTote ):
		"""
		ת��ĳ���������͵ĵ���Ϊ������
		client���������м�鶼ֻ��Ԥ��飬����������������Щ���еļ�顣

		@param  srcKitTote: ������λ�ã���ʾ���ĸ����������ñ������߳���,Define in csdefine.py
		@type   srcKitTote: INT8
		@param   srcOrder: ����λ��
		@type    srcOrder: INT16
		@param  dstKitTote: ������λ�ã���ʾ�µı����ŵ��ĸ�λ��
		@type   dstKitTote: INT8
		@return:            ������󱻷����򷵻�True�����򷵻�False
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
		# �������ͨ��Ʒ����ֱ�ӽ������
		if itemType not in ItemTypeEnum.KITBAG_LIST:
			#���������Ʒ��������ڵİ�����ֱ�ӷ���2008-07-25 spf
			if srcKitTote == dstKitTote:
				return False
			# �����Ʒ�ǿɵ�����Ʒ���ܹ����ӵ�Ŀ������ĵ�����Ʒ����ʹ��moveItemToKitTote�ӿ�
			if srcItem.getStackable() > 1 and self.canStackableInKit( srcItem.id, srcItem.isBinded(), itemAmount, dstKitTote ):	# �����Ʒ����Ŀ����������
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
		# ��������ϻ����ֻ�ܷ��ڵ�6������λ
		# CSOL-2151�����ϻҲ����ͨ���϶��ŵ�δ�򿪵İ���
		if itemType == ItemTypeEnum.ITEM_WAREHOUSE_CASKET and dstKitTote  != csdefine.KB_CASKET_ID:
			freeOrder = self.getFreeOrderFK( dstKitTote )
			if freeOrder == -1:
				return False
			self.cell.swapItem( order, freeOrder )
			return True
		# �������ͨ��������ֻ�ܷ��ڵ�2-5������λ
		if itemType == ItemTypeEnum.ITEM_WAREHOUSE_KITBAG:
			if ( dstKitTote <= csdefine.KB_COMMON_ID or dstKitTote >= csdefine.KB_CASKET_ID ):
				return False
		if self.kitbags.has_key( dstKitTote ):
			kitItem = self.kitbags[dstKitTote]
			if kitItem.isFrozen():
				self.__isFrozenItemMsg()
				return False

			# ���Ҫ�滻�İ�����������Ʒ�������滻 16:27 2008-5-19 yk
			#if self.getFreeOrderCountFK( dstKitTote ) != kitItem.getMaxSpace():
			#	self.statusMessage( csstatus.CIB_MSG_BAG_NOT_NULL )
			#	return False

			if itemType == ItemTypeEnum.ITEM_WAREHOUSE_CASKET:	# ��������У���������ж����Ͳ��ܻ�λ by ����
				if csdefine.KB_CASKET_ID in self.kitbags and self.getFreeOrderCountFK( csdefine.KB_CASKET_ID ) != self.kitbags[csdefine.KB_CASKET_ID].getMaxSpace():
					self.statusMessage( csstatus.CIB_MSG_BAG_NOT_NULL )
					return False
			elif kitItem.getMaxSpace() >= srcItem.getMaxSpace():	# ���Ŀ������ռ�����û��İ����ռ䣬�����滻��17:37 2008-10-30 wsf
				self.statusMessage( csstatus.CIB_PLACE_EXIST_BIGER_BAG )
				return False

		# ��cell��������
		self.cell.moveKbItemToKitTote( order, dstKitTote )
		return True

	def moveKitbagToKbItem( self, srcKitTote, dstKitTote, dstOrder ):
		"""
		ת��ĳ������Ϊ�������͵ĵ���
		@param  srcKitTote: ������λ����ʾ���ĸ�����λ�ѱ����ó���
		@type   srcKitTote: INT8
		@param  dstKitTote: Ŀ�걳����λ����ʾ�ñ����ó��������ĸ�����
		@type   dstKitTote: INT8
		@param  dstOrder: Ŀ�걳����������ʾ�ñ����ó��������ĸ��������ĸ�λ��
		@type   dstOrder: INT8
		@return:         ������󱻷����򷵻�True�����򷵻�False
		@rtype:          BOOL
		"""
		dOrder = dstKitTote * csdefine.KB_MAX_SPACE + dstOrder
		if len( self.getItems( srcKitTote ) ) != 0:
			# �����ǿգ������Ƴ�����Ϊ����
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
		��������������λ��
		@param  srcKitOrder: Դ������λ
		@type   srcKitOrder: INT8
		@param  dstKitOrder: Ŀ�걳����λ
		@type   dstKitOrder: INT8
		@return:         ������󱻷����򷵻�True�����򷵻�False
		@rtype:          BOOL
		"""
		if srcKitOrder == dstKitOrder: return False
		# �����Ľ����������ڵ�2-5λ����λ�Ľ���(��һλΪ�̶��ģ��ڰ�λΪ���ϻ)
		if srcKitOrder <= csdefine.KB_COMMON_ID or srcKitOrder >= csdefine.KB_CASKET_ID:
			self.statusMessage( csstatus.CIB_MSG_KITBAG_NOT_ALLOW )
			return False

		if dstKitOrder <= csdefine.KB_COMMON_ID or dstKitOrder >= csdefine.KB_CASKET_ID:
			self.statusMessage( csstatus.CIB_MSG_KITBAG_NOT_ALLOW )
			return False

		# �� Cell ������Ϣ
		self.cell.swapKitbag( srcKitOrder, dstKitOrder )

	# ------------------------------------------------------------------------------------
	# for cell �� callback ����
	# ------------------------------------------------------------------------------------
	# �����Ʒ
	# ------------------------------------------------------------------------------------
	def addItemCB( self, itemInstance ):
		"""
		Define method.
		ĳ��������ĳ��λ��������һ�����ߡ�
		���ǿ�����������Щ��������飬����ˢ�µ������ȡ�
		�ҵ�ԭ�������ŷ������������һ�С�����ʹ�Ǵ�ġ�
		����������Ҳ����жϲ�������ȷ�ԣ�
		�������Կ���ʹ��try���п��ܳ������Ϣpass���������ڲ�������������⡣

		@param itemInstance: �̳���CItemBase���Զ������͵���ʵ��
		@type  itemInstance: class instance
		@return:             ��
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
		rds.helper.courseHelper.addItem( itemInfo.itemType )	#�������̰���

	# ------------------------------------------------------------------------------------
	# �Ƴ���Ʒ
	# ------------------------------------------------------------------------------------
	def removeItemCB( self, order ):
		"""
		Define method.
		��cell�Ļص�������ɾ��ĳ�������ϵ�ĳ�����ߡ�
		���ǿ�����������Щ��������飬����ˢ�µ������ȡ�
		�ҵ�ԭ�������ŷ������������һ�С�����ʹ�Ǵ�ġ�
		����������Ҳ����жϲ�������ȷ�ԣ�
		�������Կ���ʹ��try���п��ܳ������Ϣpass���������ڲ�������������⡣

		@param   order: Դ������Դ����
		@type    order: INT16
		@return:        ��
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
	# ������Ʒ
	# ------------------------------------------------------------------------------------
	def swapItemCB( self, srcOrder, dstOrder ):
		"""
		Define method.
		�����������ߵ�λ�á�
		���ǿ�����������Щ��������飬����ˢ�µ������ȡ�
		�ҵ�ԭ�������ŷ������������һ�С�����ʹ�Ǵ�ġ�
		����������Ҳ����жϲ�������ȷ�ԣ�
		�������Կ���ʹ��try���п��ܳ������Ϣpass���������ڲ�������������⡣

		@param   srcOrder: Դ������Դ����
		@type    srcOrder: INT16
		@param   dstOrder: Ŀ�걳����Դ����
		@type    dstOrder: UINT8
		@return:           ��
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
				ECenter.fireEvent( "EVT_ON_UNWIELD_TO_KITBAG", dstKitTote, dstOrderID, ItemInfo( newDstItem ) )	#ж��װ����������
				ECenter.fireEvent( "EVT_ON_ITEM_EQUIPED", ItemInfo( oldDstItem ) )	# ֪ͨ����Ʒ��װ������ɫ����
			self.onUpdateNormalSkill()
			return
		if dstKitTote == csdefine.KB_EQUIP_ID:
			if oldDstItem is None:
				ECenter.fireEvent( "EVT_ON_WIELD_REMOVE_KITBAGITEM", ItemInfo( oldSrcItem ) )
				ECenter.fireEvent( "EVT_ON_EQUIPBAG_ADD_ITEM", ItemInfo( newDstItem ) )
			else:
				if oldDstItem.getType() == ItemTypeEnum.ITEM_SYSTEM_TALISMAN:
					ECenter.fireEvent( "EVT_ON_ROLE_ACTIVE_TALISNAM", None )
				ECenter.fireEvent( "EVT_ON_EQUIPBAG_SWAP_ITEM", ItemInfo( newDstItem ) )#����װ�����뱳���е���Ʒ��������
				ECenter.fireEvent( "EVT_ON_UNWIELD_TO_KITBAG", srcKitTote, srcOrderID, ItemInfo( newSrcItem ) )#ж��װ������������
			ECenter.fireEvent( "EVT_ON_ITEM_EQUIPED", ItemInfo( oldSrcItem ) )	# ֪ͨ����Ʒ��װ������ɫ����
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
		ɾ��ĳ��λ�õı���
		���ǿ�����������Щ��������飬����ˢ�µ������ȡ�
		�ҵ�ԭ�������ŷ������������һ�С�����ʹ�Ǵ�ġ�
		����������Ҳ����жϲ�������ȷ�ԣ�
		�������Կ���ʹ��try���п��ܳ������Ϣpass���������ڲ�������������⡣

		@param kitTote: Դ����
		@type  kitTote: INT8
		@param dstOrder: Ŀ��λ��
		@type  dstOrder: INT16
		@return:             ��
		"""
		del self.kitbags[kitTote]
		GUIFacade.removeKitbagCB( kitTote )

	def swapKitbagCB( self, srcKitOrder, dstKitOrder ):
		"""
		Define method.
		������������λ�ã�������������Ϣ
		@param srcKitOrder: Դ����λ
		@type  srcKitOrder: INT8
		@param dstKitOrder: Ŀ�걳��λ
		@type  dstKitOrder: INT8
		"""
		srcKitItem = self.kitbags.get( srcKitOrder )
		scrKitInfo = ItemInfo( srcKitItem )
		dstKitItem = self.kitbags.get(dstKitOrder)
		srcItemsList = self.getItems( srcKitOrder )
		swapItemData = {}	# ��¼��������
		srcOrderAmend = csdefine.KB_MAX_SPACE *( dstKitOrder - srcKitOrder )
		if dstKitItem is not None:
			dstKitInfo = ItemInfo( dstKitItem )
			dstItemsList = self.getItems( dstKitOrder )
			# Դ������Ŀ�걳�������ڣ���������
			for item in srcItemsList:
				swapItemData[item.order + srcOrderAmend] = item
				self.itemsBag.removeByOrder( item.order )
			dstOrderAmend = csdefine.KB_MAX_SPACE *( srcKitOrder - dstKitOrder )
			for item in dstItemsList:
				swapItemData[item.order + dstOrderAmend] = item
				self.itemsBag.removeByOrder( item.order )
			self.kitbags.update( { srcKitOrder : dstKitItem, dstKitOrder : srcKitItem } )
		else:
			# Դ�������ڣ�Ŀ�걳�������ڣ�������λ
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
		ĳ��λ�÷�һ������
		���ǿ�����������Щ��������飬����ˢ�µ������ȡ�
		�ҵ�ԭ�������ŷ������������һ�С�����ʹ�Ǵ�ġ�
		����������Ҳ����жϲ�������ȷ�ԣ�
		�������Կ���ʹ��try���п��ܳ������Ϣpass���������ڲ�������������⡣

		@param    kitTote: �¼ӵı��������ĸ�λ��
		@type     kitTote: INT8
		@param orderID: ת��Ϊ��������Ʒ
		@type  orderID: Int16
		@return:           ��
		"""
		self.kitbags[kitTote] = kitbagItem
		GUIFacade.addKitbagCB( kitTote, kitbagItem )

	# ------------------------------------------------------------------------------------
	# ��Ʒ���Ըı�֪ͨ
	# ------------------------------------------------------------------------------------
	def onItemAttrUpdated( self, orderID, attrIndex, stream ):
		"""
		Define method.
		��Ʒ���Ը���֪ͨ

		@param orderID: ����Ҫ������
		@type  orderID: UINT8
		@param    attrIndex: ���������� �� common/ItemAttrClass.py
		@type     attrIndex: UINT8
		@param  stream: ����ֵ����Ҫʹ��������Ե�createFromStream()������ȡ����ֵ
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
	# ��Ʒ��ʱ����(���������� see item.tmpExtra)�ı�֪ͨ
	# ------------------------------------------------------------------------------------
	def onItemTempAttrUpdated( self, orderID, attrIndex, stream ):
		"""
		Define method.
		��Ʒ���Ը���֪ͨ

		@param orderID: ����Ҫ������
		@type  orderID: UINT8
		@param    attrIndex: ����������
		@type     attrIndex: UINT8
		@param  stream: ����ֵ����Ҫʹ��������Ե�createFromStream()������ȡ����ֵ
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
	# ���ϻʹ�ô����ı�֪ͨ��15:15 2008-5-19 yk
	# ------------------------------------------------------------------------------------
	def onUpdateUseDegree( self, useDegree ):
		"""
		Define method.
		�������ϻʹ�ô���
		@param useDegree: ʣ��ʹ�ô���
		@type  useDegree: UINT8
		"""
		kitbagItem = self.kitbags[csdefine.KB_CASKET_ID]
		kitbagItem.set( "useDegree", useDegree )
		ECenter.fireEvent( "EVT_ON_CASKET_REMAIN_TIMES", useDegree )
		ECenter.fireEvent( "EVT_ON_UPDATE_PACK_ITEM", csdefine.KB_CASKET_ID, ItemInfo( kitbagItem ) )


	# ------------------------------------------------------------------------------------
	# ���ϻ��/���� by����
	# ------------------------------------------------------------------------------------
	def lockCasket( self ):
		"""
		֪ͨ���������
		"""
		self.isCasketLocked = True
		ECenter.fireEvent( "EVT_ON_LOCK_CASKET" )

	def unLockCasket( self ):
		"""
		defined method
		ʹ�ú���������ᱻ����������֪ͨ���������
		"""
		self.isCasketLocked = False
		ECenter.fireEvent( "EVT_ON_UNLOCK_CASKET" )

	# ------------------------------------------------------------------------------------
	# ��������������
	# ------------------------------------------------------------------------------------
	def kitbags_setPassword( self, srcPassword, password ):
		"""
		���á��޸ı������붼ʹ�ô˽ӿڡ���������Ϊ��ʱ��srcPasswordֵΪ"",�޸�����ʱsrcPasswordֵΪ ��ҵľ�����

		param srcPassword:		����ԭ����,
		type srcsrcPassword:	STRING
		param password:	������������
		type password:	STRING
		"""
		self.cell.kitbags_setPassword( srcPassword, password )

	def kitbags_lock( self ):
		"""
		����������������������������һ�û�жԱ���������ǰ���£�������˽ӿڵ�ʹ������
		"""
		self.cell.kitbags_lock()

	def kitbags_unlock( self, srcPassword ):
		"""
		����������������������˱��������Ҹ�����������ǰ���£�������˽ӿڵ�ʹ��������
		ע�⣺�����Ĳ�������ڱ��ε�½�ڼ�ʧ��3�Σ�24Сʱ�ڲ�����������������

		param srcPassword:		����ԭ����,
		type srcsrcPassword:	STRING
		"""
		self.cell.kitbags_unlock( srcPassword )


	def kitbags_clearPassword( self, srcPassword ):
		"""
		���������ý���������Ѿ������������������ǰ���£��˽ӿ����������õ����룬�ѱ���������Ϊ�ա�
		ע�⣺���ý����Ĳ�������ڱ��ε�½�ڼ�ʧ��3�Σ�24Сʱ�ڲ�����������������

		param srcPassword:		����ԭ����,
		type srcsrcPassword:	STRING
		"""
		self.cell.kitbags_clearPassword( srcPassword )

		# ---------------------notify UI--------------------------

		#����������״̬����kitbagsLockerStatus��״̬���£�����ʵ��ʱ�ɲο�����
		#0000 0000:������״̬
		#0000 0001:������״̬
		#0000 0010:����״̬
		#0111 0000:��������ʧ�ܴ���

	def set_kitbagsLockerStatus( self, oldValue ):
		"""
		����������״̬���º������Զ����º���
		"""
		ECenter.fireEvent( "EVT_ON_BAGLOCK_STATUAS_CHANGE", self.kitbagsLockerStatus )

		# ֪ͨ���棬wsf

	#def set_kitbagsUnlockLimitTime( self, oldValue ):
		"""
		������������ʱ����Զ�֪ͨ����
		"""
	#	printStackTrace()
	#	if self.kitbagsUnlockLimitTime > 0:
	#		# ֪ͨ���棬��Ϊ���kitbagsUnlockLimitTime > 0��˵��kitbagsUnlockLimitTime�ǵ�һ�����ã�
	#		# ��Ҫ֪ͨ���������Ϊ�����ˣ�wsf
	#		ECenter.fireEvent( "EVT_ON_BAGLOCK_TIME_CHANGE", self.kitbagsUnlockLimitTime )

	def kitbags_lockerNotify( self, flag ):
		"""
		Define method.
		����������֪ͨ����

		if flag == 0: ���ñ�������ɹ���֪ͨ
		if flag == 1: �������������ĳɹ���֪ͨ
		if flag == 2: ����������֪ͨ
		if flag == 3: ���������֪ͨ
		if flag == 4: �����������ɹ���֪ͨ
		if flag == 5: �����������ɹ���֪ͨ
		if flag == 6: �Ѿ������������
		type flag:	UINT8
		"""
		ECenter.fireEvent( "EVT_ON_BAGLOCK_FLAG_CHANGE", flag )

	def kitbags_onConfirmForceUnlock( self ) :
		"""
		Define method.
		ǿ�ƽ�������ȷ��
		"""
		def confirmUnlock( result ) :
			if result == RS_YES :
				self.cell.kitbags_onForceUnlock()
		# ǿ�ƽ���������Ҫ%s�����������뽫����գ���ȷ��Ҫ������
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
		��֤�����Ƿ�����
		"""
		return ( self.kitbagsLockerStatus >> 1 ) & 0x01 == 1	# ��ʾ�����Ƿ��������״̬λ�Ƿ�Ϊ1

	def autoStuffFC( self, orders ):
		"""
		Define Method
		�������Զ�������������Ϣ����
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
