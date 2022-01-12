# -*- coding: gb18030 -*-
#
# $Id: QuickBar.py,v 1.58 2008-07-21 02:48:21 huangyongwei Exp $

"""
implement quickbar base class，referrence document:‘AB\客户端设计\QuickBar.mdl’。

2005/12/23 : writen by wanhaipeng
2006/09/17 : rewriten by huangyongwei ( begin from version 1.29 )
"""

import BigWorld
import csdefine
import csconst
import ItemTypeEnum
import event.EventCenter as ECenter
import skills as Skill
from bwdebug import *
from keys import *
from ItemsFactory import QuickBarItem
from gbref import rds


class QuickBar :
	def __init__( self ) :
		self.__itemInfos = {}
		self.__triggers = {}
		self.__recordRedMedication = None
		self.__recordBlueMedication = None
		self.__recordPetRedMedication = None
		self.__recordPetBlueMedication = None

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		if not self.isPlayer() : return
		self.__triggers["EVT_ON_KITBAG_ADD_ITEM"] = self.__onKitbagUpdateItem
		self.__triggers["EVT_ON_KITBAG_UPDATE_ITEM"] = self.__onKitbagUpdateItem
		self.__triggers["EVT_ON_KITBAG_REMOVE_ITEM"] = self.__onKitbagRemoveItem
		self.__triggers["EVT_ON_PLAYERROLE_UPDATE_SKILL"] = self.__onSkillUpdate
		self.__triggers["EVT_ON_PLAYERROLE_REMOVE_SKILL"] = self.__onSkillRemove
		self.__triggers["EVT_ON_PLAYERROLE_UPDATE_NORMAL_SKILL"] = self.__onNormalSkillUpdate
		self.__triggers["EVT_ON_PLAYER_FREE_VEHICLE"] = self.__onVehicleFree			# 放生骑宠后 刷新格子 by姜毅
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )

	# -------------------------------------------------
	def __onKitbagUpdateItem( self, objItemInfo ) :
		for index, info in self.__itemInfos.iteritems() :
			if info.qbType != csdefine.QB_ITEM_KITBAG : continue
			if info.id != objItemInfo.id : continue
			nextItem = BigWorld.player().findItemFromNKCK_( objItemInfo.id )
			if nextItem is None :									# not match item
				self.qb_removeItem( index )
			self.qb_updateItem( index, info.qbType, nextItem )
			ECenter.fireEvent( "EVT_ON_QUICKBAR_UPDATE_ITEM", index, info )

	def __onKitbagRemoveItem( self, objItemInfo ) :
		# find out all iteminfos that their id is the same as objItemInfo
		mapInfos = []
		for info in self.__itemInfos.itervalues() :
			if info.qbType != csdefine.QB_ITEM_KITBAG : continue
			if info.id == objItemInfo.id :
				mapInfos.append( info )
		if len( mapInfos ) == 0 : return

		# find next item which its id is the same as objItemInfo
		nextItem = BigWorld.player().findItemFromNKCK_( objItemInfo.id )

		# update all items
		for info in mapInfos :
			index = info.index
			if nextItem is None :									# not match item
				self.qb_removeItem( index )
			elif info.baseItem.uid == objItemInfo.uid :		# info is just the mapping of the deleted object item
				self.qb_updateItem( index, info.qbType, nextItem )
			else :													# other same id items ( only updte its amount )
				ECenter.fireEvent( "EVT_ON_QUICKBAR_UPDATE_ITEM", index, info )

	def __onVehicleFree( self, vehicleDBID ):
		mapInfos = []
		for info in self.__itemInfos.itervalues() :
			if info.qbType == csdefine.QB_ITEM_VEHICLE:
				if info.dbid == vehicleDBID:
					mapInfos.append( info )
		for info in mapInfos:
			index = info.index
			self.qb_onRemoveItem( index )

	# ---------------------------------------
	def __onSkillUpdate( self, oldSkillID, skItemInfo ) :
		for index, info in self.__itemInfos.iteritems() :
			if info.qbType == csdefine.QB_ITEM_SKILL and \
				info.id == oldSkillID :
					self.qb_updateItem( index, info.qbType, skItemInfo.baseItem )

	def __onSkillRemove( self, skInfo ) :
		for index, info in self.__itemInfos.items() :
			if info.qbType != csdefine.QB_ITEM_SKILL : continue
			if info.id != skInfo.id : continue
			self.qb_removeItem( index )

	def __onNormalSkillUpdate( self, skillID, baseItem ) :
		"""
		更新普通物理攻击技能
		"""
		for index, info in self.__itemInfos.iteritems() :
			if info.id == skillID :
				self.qb_updateItem( index, info.qbType, baseItem )


	# ----------------------------------------------------------------
	# called by server
	# ----------------------------------------------------------------
	def qb_onRemoveItem( self, index ) :
		"""
		notify to remove an quickbar item ( but now it just called by client, because we trust it )
		@type			index  : int
		@param			index  : index of the item will be removed
		@return				   : None
		"""
		if self.__itemInfos.has_key( index ) :
			ECenter.fireEvent( "EVT_ON_QUICKBAR_UPDATE_ITEM", index, None )
			self.__itemInfos.pop( index )
			if not self.qb_canAutoRestore(): 	# 如果放置有药品，那么开始自动恢复的timer
				self.stopAutoRestore()

	def qb_onUpdateItem( self, index, qbType, narg1, sarg2 ) :
		"""
		notify to update a quickbar item( but now it just called by client, because we trust it )
		@type			index  : int
		@param			index  : item index
		@rtype			qbType : type of quickbar item
		@param			qbType : item type ( QB_ITEM_SKILL, QB_ITEM_KITBAG, QB_ITEM_TACT )
		@rtype			narg1  : int
		@param			narg1  : index of item in its own type
		@type			sarg2  : str
		@param			sarg2  : item ID
		@return				   : None
		"""
		itemInfo = self.__itemInfos.get( index, None )
		if itemInfo is not None and itemInfo.qbType == qbType :
			baseItem = QBItemInfoFactory.getBaseItem( qbType, narg1, sarg2 )
			if baseItem is None : return
			itemInfo.update( baseItem )
		else :
			itemInfo = QBItemInfoFactory.createItemInfo( qbType, narg1, sarg2 )
			if itemInfo is None : return
			itemInfo.index = index
			self.__itemInfos[index] = itemInfo
		ECenter.fireEvent( "EVT_ON_QUICKBAR_UPDATE_ITEM", index, itemInfo )	# 在宠物快捷栏ui脚本中要做判断，如果不是出战宠物那么不更新
		if self.qb_canAutoRestore() and not self.isAutoRestore(): 	# 如果放置有药品，那么开始自动恢复的timer
			self.autoRestoreDetect()

	def qb_onExchangeItem( self, srcIndex, dstIndex ) :
		"""
		exchange quickbar item
		@type				srcIndex : int
		@param				srcIndex : source item index
		@type				srcIndex : int
		@param				srcIndex : destination item index
		@return						 : None
		"""
		srcInfo = self.__itemInfos[srcIndex]
		dstInfo = self.__itemInfos.get( dstIndex, None )
		self.__itemInfos[dstIndex] = srcInfo
		srcInfo.index = dstIndex
		if dstInfo is None :
			self.__itemInfos.pop( srcIndex )
		else :
			self.__itemInfos[srcIndex] = dstInfo
			dstInfo.index = srcIndex
		ECenter.fireEvent( "EVT_ON_QUICKBAR_UPDATE_ITEM", srcIndex, dstInfo )
		ECenter.fireEvent( "EVT_ON_QUICKBAR_UPDATE_ITEM", dstIndex, srcInfo )


	# ----------------------------------------------------------------
	# called by client base
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	# ---------------------------------------
	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		self.__registerTriggers()

	def leaveWorld( self ) :
		self.__itemInfos.clear()
		self.__deregisterTriggers()


	# ----------------------------------------------------------------
	# called by ui
	# ----------------------------------------------------------------
	def qb_removeItem( self, index ) :
		"""
		notify base to remove a quick bar item
		@rtype			index : int
		@param			index : index of the item will be removed
		@return				  : None
		"""
		self.base.qb_removeItem( index )
		self.qb_onRemoveItem( index )	# no feedback form server, so we trust it

	def qb_updateItem( self, index, qbType, baseItem ) :
		"""
		notify base update quickbar item
		@type			index	 : int
		@param			index	 : index of the item will be updated
		@type			qbType	 : int
		@param			qbType	 : defined in: common/csdefine.py
		@type			baseItem : instance of skill/kitbag/…… base item
		@param			baseItem : the item you want to update
		@return					 : None
		"""
		narg1, sarg2 = QBItemInfoFactory.getArguments( qbType, baseItem )
		self.base.qb_updateItem( index, qbType, narg1, sarg2 )
		self.qb_onUpdateItem( index, qbType, narg1, sarg2 )			# don't wait for feedback form server, we trust it

	def qb_exchangeItem( self, srcIndex, dstIndex ) :
		"""
		exchange quick bar item
		@type			srcIndex : int
		@param			srcIndex : the source item index
		@type			dstIndex : int
		@param			dstIndex : the distance item index
		@return					 : None
		"""
		self.base.qb_exchangeItem( srcIndex, dstIndex )
		self.qb_onExchangeItem( srcIndex, dstIndex )

	# -------------------------------------------------
	def qb_getItems( self ) :
		"""
		get all quick items
		@rtype			: dict
		@return			: { index : instnace of QuickbarItemInfo, …… }
		"""
		return self.__itemInfos

	# -------------------------------------------------
	def qb_setRecordRedMedication( self, medication ):
		"""
		"""
		self.__recordRedMedication = medication

	def qb_getRecordRedMedication( self ):
		return self.__recordRedMedication

	def qb_setRecordBlueMedication( self, medication ):
		"""
		"""
		self.__recordBlueMedication = medication

	def qb_getRecordBlueMedication( self ):
		return self.__recordBlueMedication

	def qb_setPetRecordRedMedication( self, medication ):
		"""
		"""
		self.__recordPetRedMedication = medication

	def qb_getPetRecordRedMedication( self ):
		return self.__recordPetRedMedication

	def qb_setPetRecordBlueMedication( self, medication ):
		"""
		"""
		self.__recordPetBlueMedication = medication

	def qb_getPetRecordBlueMedication( self ):
		return self.__recordPetBlueMedication

	def qb_canAutoRestore( self ):
		"""
		快捷栏中是否有自动恢复药品
		"""
		return ( self.__recordRedMedication or self.__recordBlueMedication or \
				self.__recordPetRedMedication or self.__recordPetBlueMedication ) and \
				self.state != csdefine.ENTITY_STATE_DEAD

	def qb_autoRestoreHP( self ):
		"""
		使用红药物品恢复
		"""
		itemInfo = self.qb_getRecordRedMedication()
		if itemInfo:
			if not itemInfo.getCooldownInfo() == ( 0, 0 ):
				return
			if itemInfo.reqLevel > self.level:
				return
			if itemInfo.itemType == ItemTypeEnum.ITEM_SUPER_DRUG_HP or self.hasFlag( csdefine.ROLE_FLAG_ICHOR ):
				itemInfo.spell()

	def qb_autoRestoreMP( self ):
		"""
		使用蓝药物品恢复
		"""
		itemInfo = self.qb_getRecordBlueMedication()
		if itemInfo:
			if not itemInfo.getCooldownInfo() == ( 0, 0 ):
				return
			if itemInfo.reqLevel > self.level:
				return
			if itemInfo.itemType == ItemTypeEnum.ITEM_SUPER_DRUG_MP or self.hasFlag( csdefine.ROLE_FLAG_ICHOR ):
				itemInfo.spell()

	def qb_autoRestorePetHP( self ):
		"""
		使用宠物红药物品恢复
		"""
		actPet = self.pcg_getActPet()
		if actPet is None:
			return
		itemInfo = self.qb_getPetRecordRedMedication()
		if itemInfo:
			if itemInfo.reqLevel > actPet.level:
				return
			if not itemInfo.getCooldownInfo() == ( 0, 0 ):
				return

			if itemInfo.itemType == ItemTypeEnum.ITEM_PET_SUPER_DRUG_HP or self.hasFlag( csdefine.ROLE_FLAG_ICHOR ):
				itemInfo.spell()

	def qb_autoRestorePetMP( self ):
		"""
		使用宠物蓝药物品恢复
		"""
		actPet = self.pcg_getActPet()
		if actPet is None:
			return
		itemInfo = self.qb_getPetRecordBlueMedication()
		if itemInfo:
			if itemInfo.reqLevel > actPet.level:
				return
			if not itemInfo.getCooldownInfo() == ( 0, 0 ):
				return
			if itemInfo.itemType == ItemTypeEnum.ITEM_PET_SUPER_DRUG_MP or self.hasFlag( csdefine.ROLE_FLAG_ICHOR ):
				itemInfo.spell()

	# ------------------------------------------------
	def showSpellingItemCover( self, skillID ) :
		"""
		高亮显示正在施放的技能
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_SPELLING_COVER", skillID )

	def hideSpellingItemCover( self ) :
		"""
		隐藏技能的高亮显示状态
		"""
		ECenter.fireEvent( "EVT_ON_HIDE_SPELLING_COVER" )

	def showInvalidItemCover( self, skillID ) :
		"""
		点击不可用技能时用红色边框显示
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_INVALID_COVER", skillID )

	def showPetInvalidItemCover( self, skillID ) :
		"""
		点击宠物当前不可用技能时显示红色边框
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_PET_INVALID_COVER", skillID )

# --------------------------------------------------------------------
# implement quickbar iteminfo factory
# --------------------------------------------------------------------
class QBItemInfoFactory :
	__instance = None

	def __init__( self ) :
		assert self.__instance is None

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@classmethod
	def __getInstance( SELF ) :
		if SELF.__instance is None :
			SELF.__instance = QBItemInfoFactory()
		return SELF.__instance

	# -------------------------------------------------
	def __getKitbagItem( self, kitbagID, itemIndex ) :
		player = BigWorld.player()
		item = player.getItem_( int( itemIndex ) )
		return item

	def __getSkillItem( self, narg1, skillName ) :
		skillList = BigWorld.player().getSkillList()
		skillList += csconst.SKILL_ID_ACTIONS
		for id in skillList :
			skill = Skill.getSkill( id )
			if skill.getName() == skillName :
				return skill
		return None

	def __getTactItem( self, narg1, tactName ) :
		tactItem = rds.tactFactory.getTact( tactName )
		if tactItem is None : return None
		return tactItem

	def __getVehicleData( self, narg1, vehicleID ):
		player = BigWorld.player()
		vehicleID = int( vehicleID )
		if player.vehicleDatas.has_key( vehicleID ):
			vehicleData = player.vehicleDatas[vehicleID]
			return vehicleData
		return None

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@classmethod
	def getArguments( SELF, qbType, baseItem ) :
		if qbType == csdefine.QB_ITEM_KITBAG :
			return baseItem.getKitID(), str( baseItem.getOrder() )
		elif qbType == csdefine.QB_ITEM_EQUIP :
			return baseItem.getKitID(), str( baseItem.getOrder() )
		elif qbType == csdefine.QB_ITEM_SKILL :
			return 0, baseItem.getName()
		elif qbType == csdefine.QB_ITEM_TACT :
			return 0, baseItem.getClassName()
		elif qbType == csdefine.QB_ITEM_VEHICLE:
			return 0, str( baseItem["id"] )
		return 0, ""

	@classmethod
	def getBaseItem( SELF, qbType, narg1, sarg2 ) :
		self = SELF.__getInstance()
		generators = {}
		generators[csdefine.QB_ITEM_KITBAG]	= self.__getKitbagItem
		generators[csdefine.QB_ITEM_EQUIP]	= self.__getKitbagItem
		generators[csdefine.QB_ITEM_SKILL]	= self.__getSkillItem
		generators[csdefine.QB_ITEM_TACT]	= self.__getTactItem
		generators[csdefine.QB_ITEM_VEHICLE] = self.__getVehicleData
		if qbType not in generators :
			ERROR_MSG( "unrecognize qucik bar item type: %i" % qbType )
		else :
			return generators[qbType]( narg1, sarg2 )

	@classmethod
	def createItemInfo( SELF, qbType, narg1, sarg2 ) :
		self = SELF.__getInstance()
		baseItem = SELF.getBaseItem( qbType, narg1, sarg2 )
		if baseItem is None : return None
		classes = {}
		classes[csdefine.QB_ITEM_KITBAG] = QBKitbagItem
		classes[csdefine.QB_ITEM_EQUIP]	= QBKitbagItem
		classes[csdefine.QB_ITEM_SKILL]	= QBSkillItem
		classes[csdefine.QB_ITEM_TACT]	= QBTactItem
		classes[csdefine.QB_ITEM_VEHICLE] = QBVehicle
		return classes[qbType]( baseItem )


# --------------------------------------------------------------------
# quick bar item specifies kitbag item
# --------------------------------------------------------------------
from ItemsFactory import ObjectItem

class QBKitbagItem( QuickBarItem, ObjectItem ) :
	def __init__( self, baseItem ) :
		QuickBarItem.__init__( self, baseItem )
		ObjectItem.__init__( self, baseItem )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isCooldownType( self, cooldownType ) :
		"""
		when cooldown message had been sended, indidate whether the item is allow to show cooldown
		"""
		item = self.baseItem
		if item is None : return False
		return item.isCooldownType( cooldownType )

	def getSpell( self ) :
		return ObjectItem.getSpell( self )

	def spell( self ) :
		"""
		use kitbagItem to targetEntity later.
		"""
		ObjectItem.spell( self )
	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def qbType( self ) :
		"""
		get type of quick item
		"""
		return csdefine.QB_ITEM_KITBAG

	# -------------------------------------------------
	@property
	def amount( self ) :
		"""
		if the item is countable, it will return the number of item
		"""
		if self.isEquip : return 1
		return BigWorld.player().countItemTotal_( self.id )

# --------------------------------------------------------------------
# quick bar item specifies skill
# --------------------------------------------------------------------
from ItemsFactory import SkillItem

class QBSkillItem( QuickBarItem, SkillItem ) :
	def __init__( self, baseItem ) :
		QuickBarItem.__init__( self, baseItem )
		SkillItem.__init__( self, baseItem )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isCooldownType( self, cooldownType ) :
		"""
		indicate whether show cooldown
		"""
		skill = self.baseItem
		if skill.getType() not in csconst.BASE_SKILL_TYPE_SPELL_LIST : return False
		return skill.isCooldownType( cooldownType )

	def getSpell( self ) :
		return SkillItem.getSpell( self )

	def spell( self ) :
		"""
		use skill
		"""
		SkillItem.spell( self )


	# ----------------------------------------------------------------
	# proeprties
	# ----------------------------------------------------------------
	@property
	def qbType( self ) :
		"""
		get type of quick item
		"""
		return csdefine.QB_ITEM_SKILL

# ------------------------------------------------------------
from ItemsFactory import PetSkillItem

class QBPetSkillItem(  QuickBarItem, PetSkillItem ):
	def __init__( self, petQBitem ):
		skillID = petQBitem["skillID"]
		baseItem = Skill.getSkill( skillID )
		QuickBarItem.__init__( self, baseItem )
		PetSkillItem.__init__( self, baseItem )
		self.__autoUse = petQBitem["autoUse"]


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getID( self ) :
		"""
		get pet skill id
		"""
		return self.baseItem.getID()

	# -------------------------------------------------
	def isCooldownType( self, cooldownType ) :
		"""
		indicate whether show cooldown
		"""
		skill = self.baseItem
		if skill.getType() not in csconst.BASE_SKILL_TYPE_SPELL_LIST : return False
		return skill.isCooldownType( cooldownType )

	def getSpell( self ) :
		return PetSkillItem.getSpell( self )

	def spell( self ) :
		"""
		use skill
		"""
		PetSkillItem.spell( self )

	# ----------------------------------------------------------------
	# proeprty methods
	# ----------------------------------------------------------------
	@property
	def qbType( self ) :
		return csdefine.QB_ITEM_PET_SKILL

	@property
	def autoUse( self ) :
		return self.__autoUse


# --------------------------------------------------------------------
# quick bar item specifies tact item
# --------------------------------------------------------------------
class QBTactItem( QuickBarItem ) :
	def __init__( self, baseItem ) :
		QuickBarItem.__init__( self, baseItem )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def spell( self ) :
		return self.baseItem.spell()


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def qbType( self ) :
		"""
		get quick bar item's mapping item type
		"""
		return csdefine.QB_ITEM_TACT

	# -------------------------------------------------
	@property
	def icon( self ) :
		"""
		get item's icon
		"""
		icon = self.baseItem.getIcon()
		if type( icon ) is str :
			icon = ( icon, None )
		return icon

	@property
	def description( self ) :
		"""
		get mapping item's description
		"""
		return self.baseItem.getFormatedDescription()

	# -------------------------------------------------
	@property
	def countable( self ) :
		"""
		indicate  whether the mapping item is countable
		"""
		return False

# --------------------------------------------------------------------
# quick bar item specifies tact item
# --------------------------------------------------------------------
from ItemsFactory import VehicleItem

class QBVehicle( QuickBarItem, VehicleItem ) :
	def __init__( self, vehicleData ) :
		QuickBarItem.__init__( self, vehicleData )
		VehicleItem.__init__( self, vehicleData )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def spell( self ) :
		VehicleItem.spell( self )

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def qbType( self ) :
		"""
		get quick bar item's mapping item type
		"""
		return csdefine.QB_ITEM_VEHICLE