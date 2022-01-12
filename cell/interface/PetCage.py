# -*- coding: gb18030 -*-
#
# $Id: PetCage.py,v 1.59 2008-09-05 01:39:19 zhangyuxing Exp $

"""
This module implements the pet entity.

2007/07/01: writen by huangyongwei
2007/10/24: according to new version documents, it is rewriten by huangyongwei
"""

import time
import random
import BigWorld
import csdefine
import csconst
import csstatus
import ECBExtend
import items
from bwdebug import *
from PetFormulas import formulas
from ChatProfanity import chatProfanity
from PetTrainer import PetTrainer
from PetStorage import PetStorage
from PetFoster import PetFoster
from SkillTargetObjImpl import createTargetObjEntity
from ObjectScripts.GameObjectFactory import g_objFactory
from Love3 import g_skills
from VehicleHelper import  getCurrVehicleSkillIDs, isFlying
from Domain_Fight import g_fightMgr
import Language
import utils

# --------------------------------------------------------------------
# implement active pet
# --------------------------------------------------------------------
class _ActivePet( object ) :
	__slots__ = ( "dbid", "etype", "entity" )

	def __init__( self, dbid, mbBase ) :
		self.dbid = dbid
		entity = BigWorld.entities.get( mbBase.id )
		if entity is None :
			self.etype = "MAILBOX"
			self.entity = mbBase.cell
		elif entity.isReal() :
			self.etype = "REAL"
			self.entity = entity
		else :
			self.etype = "GHOST"
			self.entity = entity


# --------------------------------------------------------------------
# implement pet cage class
# --------------------------------------------------------------------
class PetCage( PetTrainer, PetStorage, PetFoster ) :
	def __init__( self ) :
		PetTrainer.__init__( self )						# 代练
		PetStorage.__init__( self )						# 仓库
		PetFoster.__init__( self )						# 繁殖
		self.pcg_releaseOperating_()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def pcg_lockOperation_( self ) :
		"""
		锁定操作，该锁定操作是为了防止某个操作还没从 base 或别的 cell 返回时，另一个操作又出现
		这样将会造成某些物品或金钱的数量本来只允许操作一次的，但两次操作都通过了
		"""
		if self.__operateTime + 5.0 > time.time() :
			self.statusMessage( csstatus.GB_OPERATE_FREQUENTLY )
			return False
		self.__operateTime = time.time()
		return True

	def pcg_releaseOperating_( self ) :
		"""
		取消当前的繁忙状态
		"""
		self.__operateTime = 0.0

	def pcg_isTradingPet_( self, dbid ) :
		"""
		判断某个宠物当前是否处于交易状态
		"""
		if self.isPetInSwap( dbid ):
			self.statusMessage( csstatus.PET_OPERATE_REFUSE_IN_TRADING )
			return True
		return False


	# ----------------------------------------------------------------
	# 由 base 返回的调用
	# ----------------------------------------------------------------
	def pcg_onAddPet( self, epitome ) :
		"""
		defined method
		当增加了一个宠物的时候被调用
		@type				epitome : common.CellPetEpitome
		@param				epitome : 宠物在 cell 部分的虚拟影像
		"""
		self.pcg_petDict.add( epitome.databaseID, epitome, self )
		self.questPetAmountChange( 1 )
		self.questPetAmountAdd( epitome.mapMonster, epitome.databaseID )

	def pcg_onRemovePet( self, dbid ) :
		"""
		defined method
		当一个宠物被删除的时候被调用
		@type				dbid : INT64
		@param				dbid : 被删除的宠物的数据库 ID
		"""
		if self.pcg_petDict.has_key( dbid ) :
			petData = self.pcg_petDict.get( dbid )
			self.questPetAmountSub( petData.mapMonster, petData.databaseID )
			self.pcg_petDict.remove( dbid, self )
			self.questPetAmountChange( -1 )
			if self.pcg_actPetDBID == dbid:
				self.pcg_actPetDBID = 0

	# -------------------------------------------------
	def pcg_onConjureResult( self, petDBID, basePet ) :
		"""
		defined method
		宠物出征请求的返回
		@type					petDBID : INT64
		@param					petDBID : 出征宠物的数据库 ID
		@type					basePet : MAILBOX
		@param					basePet : 出征宠物的 base mailbox
		"""
		if petDBID > 0 :
			self.pcg_actPetDBID = petDBID
			self.pcg_mbBaseActPet = basePet
			self.client.pcg_onPetConjured( petDBID )
			actPet = self.pcg_getActPet()
			pet = actPet.entity
			pet.planesID = self.planesID
			self.onPetConjureNotifyTeam( pet.id, pet.uname, pet.name, pet.modelNumber, pet.species )

			self.questPetActChanged()								# 触发“召唤宠物任务”标记该任务完成 2009-07-15	15:00 SPF
			for i, v in self.enemyList.iteritems():
				enemy = BigWorld.entities.get( i )
				if enemy:
					g_fightMgr.buildEnemyRelation( pet, enemy )
		self.removeTemp( "pcg_conjuring_dbid" )						# 清除出征宠物 DBID 的临时数据
		self.pcg_releaseOperating_()								# 在向 base 请求出征的时候，操作曾经被锁定，在这里解锁

	def pcg_onWithdrawResult( self, epitome, result ) :
		"""
		defined method
		宠物回收时被调用
		@type					result : MACRO DEFINATION
		@param					result : 回收结果，在 common.csstatus 中定义
		"""
		if result == csstatus.PET_WITHDRAW_SUCCESS_FREE :			# 如果回收是因为放生而回收的话
			self.questPetActChanged()								# 放生宠物将“召唤宠物任务”设置为未完成 2009-07-15	15:00 SPF
		elif result != csstatus.PET_WITHDRAW_SUCCESS_CONJURE :		# 如果不是放生回收，也不是出战回收
			self.statusMessage( result )							# 则，向客户端输出回收结果信息（否则，不发送回收结果信息）
			self.pcg_releaseOperating_()							# 并解锁操作
		if result != csstatus.PET_WITHDRAW_FAIL_NOT_OUT :			# 如果回收成功
			self.pcg_petDict.update( epitome.databaseID, epitome, self )# 更新非出战宠物的属性
			self.client.pcg_onPetWithdrawed()
			self.pcg_actPetDBID = 0									# 则，将出征宠物信息清空
			self.questPetActChanged()								# 回收宠物将“召唤宠物任务”设置为未完成 2009-07-15	15:00 SPF
			self.onPetWithdrawNotifyTeam()					# 收回宠物通知队友

	def pcg_onFreeResult( self, result ) :
		"""
		defined method
		当宠物放生时被调用
		@type					result : MACRO DEFINATION
		@param					result : 放生结果，在 scstatus 中定义
		"""
		self.statusMessage( result )
		self.pcg_releaseOperating_()
		self.onPetWithdrawNotifyTeam()

	# -------------------------------------------------
	def pcg_onRenameResult( self, result ) :
		"""
		defined method
		宠物改名后被 base 调用
		@type					result : MACRO DEFINATION
		@param					result : 重命名返回结果，在 csstatus 中定义
		"""
		self.pcg_releaseOperating_()								# 释放操作锁定

	# -------------------------------------------------
	def pcg_onCombineResult( self, result, args ) :
		"""
		defined method
		宠物合成时，base 的返回结果
		@type					result : MACRO DEFINATION
		@param					result : 合成返回结果，在 csstatus 中定义
		"""
		self.client.onStatusMessage( result, args )
		self.unfreezeMoney()										# 解锁金钱（因为合成时需要用到金钱）
		self.pcg_releaseOperating_()								# 解锁操作
		if result in [csstatus.PET_COMBINE_SUCCESS,csstatus.PET_COMBINE_SUCCESS_UP] :
			self.questPetEvent( "combine" )

	def pcg_onAddLifeResult( self, result ) :
		"""
		defined method
		增加寿命值时的返回结果
		@type					result : MACRO DEFINATION
		@param					result : 增加寿命的返回结果，在 csstatus 中定义
		"""
		if result == csstatus.PET_ADD_LIFE_SUCCESS :
			itemSeat0 = self.queryTemp( "pcg_add_life_item_seat", None )	# 删除延寿丹
			if itemSeat0:
				self.removeItem_( itemSeat0, 1 , csdefine.DELETE_ITEM_PET_ADDLIFE )			# 删除延寿丹
		else :
			self.statusMessage( result )
		self.removeTemp( "pcg_add_life_item_seat" )
		self.pcg_releaseOperating_()										# 解除操作锁定

	def pcg_onAddJoyancyResult( self, result ) :
		"""
		defined method
		增加快乐度时的返回结果
		@type					result : MACRO DEFINATION
		@param					result : 增加快乐度的返回结果，在 csstatus 中定义
		"""
		if result == csstatus.PET_ADD_JOYANCY_SUCCESS :
			itemSeat0 = self.queryTemp( "pcg_add_joyancy_item_seat", None )	# 溜溜球 或 布娃娃
			self.questPetEvent( "joyancy" )
			if itemSeat0:
				self.removeItem_( itemSeat0, 1, csdefine.DELETE_ITEM_PET_ADDJOYANCY )				# 删除一个溜溜球或布娃娃
		else :
			self.statusMessage( result )
		self.removeTemp( "pcg_add_joyancy_item_seat" )
		self.pcg_releaseOperating_()										# 解除操作锁定

	def pcg_onUpdatePetEpitomeAttr( self, databaseID, attrName, value ):
		"""
		Define method.
		pet未出战情况下属性改变，更新到cell

		@param databaseID : 属性改变的petDBID
		@type databaseID : DATABASE_ID
		@param attrName : 属性名字
		@type attrName : STRING
		@param value : 属性值
		@type value : PYTHON
		"""
		self.pcg_petDict.get( databaseID ).update( attrName, value, self )

	# ----------------------------------------------------------------
	# methods called by active pet
	# ----------------------------------------------------------------
	def pcg_teleportPet( self ) :
		"""
		<Define method>
		将宠物跳转到身边
		注意：不可以将返回的 ActivePet 保存下来以供长期使用。
		@type			mbBasePet : MAILBOX
		@param			mbBasePet : 宠物的 base mailbox
		"""
		actPet = self.pcg_getActPet()												# 这里不需要判断是否有出征宠物，因此，如果不确定是否有出征宠物，
																					# 在调用该方法之前，先判断是否有出征宠物
		pos = formulas.getPosition( self.position, self.yaw )						# 根据玩家位置获取宠物出征时的位置
		pos = utils.navpolyToGround(self.spaceID, pos, 5.0, 5.0)					# 取地面上的点
		actPet.entity.teleportToEntity( self.spaceID, self, pos, self.direction )


	# ----------------------------------------------------------------
	# public methods ：与 NPC 对话时调用
	# ----------------------------------------------------------------
	def pcg_dlgCanCombinePet( self ) :
		"""
		判断释放可以合成
		"""
		return self.pcg_hasActPet()

	def pcg_dlgCombinePet( self, npcEntity ) :
		"""
		显示与 NPC 对话要合成宠物对话框
		"""
		if self.pcg_hasActPet() :
			self.client.pcg_onShowCombineDialog()
		else :
			self.statusMessage( csstatus.PET_COMBINE_FAIL_NOT_OUT )


	# ----------------------------------------------------------------
	# public methods
	# ----------------------------------------------------------------
	def pcg_onCellPetChange( self ):
		"""
		for real & ghost
		宠物数据改变，基于bw的通信机制，必须触发"="操作才会把pcg_petDict数据广播出去
		该方法在 common/CellPetDict:CellPetEpitome 中调用
		"""
		self.pcg_petDict = self.pcg_petDict

	# -------------------------------------------------
	def pcg_getPetCount( self ) :
		"""
		for real & ghost
		获取当前携带宠物的数量
		"""
		return self.pcg_petDict.count()

	def pcg_getKeepingCount( self ) :
		"""
		for real & ghost
		获取当前可以携带宠物的最大数量
		"""
		return formulas.getKeepingCount( self.pcg_reinBible )

	def pcg_isFull( self ) :
		"""
		for real & ghost
		判断当前携带的宠物是否已经达到上限
		"""
		return self.pcg_getPetCount() >= self.pcg_getKeepingCount()

	def pcg_isOverbrim( self, count ) :
		"""
		for real & ghost
		判断增加 count 个宠物后，是否会达到携带上限
		@type				count : int
		@param				count : 要增加的携带宠物数量
		"""
		return self.pcg_getPetCount() + count > self.pcg_getKeepingCount()

	# ---------------------------------------
	def pcg_hasActPet( self ) :
		"""
		for real & ghost
		是否有出征宠物
		"""
		return self.pcg_actPetDBID > 0

	def pcg_isActPet( self, dbid ) :
		"""
		for real & ghost
		判断指定的宠物是否是出征宠物
		"""
		if dbid == 0 : return False
		return self.pcg_actPetDBID == dbid

	def pcg_isPetBinded( self, dbid ):
		"""
		宠物是否被绑定
		"""
		return self.pcg_petDict.get( dbid ).isBinded

	def pcg_getActPet( self ) :
		"""
		for real & ghost
		获取出征宠物 ActivePet( 本模块顶部定义 )
		@rtype					: _ActivePet
		@return					: 出征宠物的，如果，没有出征宠物，则返回 None
		"""
		if self.pcg_actPetDBID == 0 : return None
		return _ActivePet( self.pcg_actPetDBID, self.pcg_mbBaseActPet )

	def pcg_isConjuring( self, dbid ):
		"""
		for real
		宠物是否正在被召唤中
		"""
		return self.queryTemp( "pcg_conjuring_dbid", 0 ) == dbid

	# -------------------------------------------------
	def pcg_catchPet( self, monsterClassName, level, modelNumber, catchType, isCatch, needResetLevel = False ) :
		"""
		for real
		捕捉一个怪物作为宠物
		@type			monsterClassName : str
		@param			monsterClassName : 怪物的 ID
		@type			level			 : UINT8
		@param			level			 : 怪物等级
		@type			modelNumber		 : str
		@param			modelNumber		 : 怪物模型号
		@type			needResetLevel	:BOOL
		@param			needResetLevel	:是否强制设置等级为1
		@return							 : None
		"""
		className = g_objFactory.getObject( monsterClassName ).mapPetID
		vpet = g_objFactory.getObject( className )
		if self.pcg_isFull() :
			self.statusMessage( csstatus.PET_CATCH_FAIL_OVERRUN )
		else :
			defSkillIDs = vpet.getDefSkillIDs( level  )				# 技能前缀
			self.base.pcg_catchPet( monsterClassName, level, modelNumber, defSkillIDs, catchType, False, needResetLevel,isCatch )

	def pcg_onEnhanceResult( self, *args ) :
		"""
		for real
		宠物强化时，base 的返回结果
		@type					result : MACRO DEFINATION
		@param					result : 强化返回结果，在 csstatus 中定义
		"""
		result = args[0]
		if result == csstatus.PET_ENHANCE_SUCCESS :							# 强化成功时
			itemSeat0 = self.queryTemp( "pcg_enhance_item_seat", None )		# 清除强化需要的物品
			itemSeat1 = self.queryTemp( "pcg_enhance_item_seat1", None )	# 精炼符、点化符
			itemSeat2 = self.queryTemp( "pcg_enhance_item_seat2", None )
			for order in [itemSeat0, itemSeat1, itemSeat2]:
				if order:
					self.removeItem_( order, 1, reason = csdefine.DELETE_ITEM_PET_ENHANCE )
			# remove item
			self.questPetEvent( "enhance" )
		self.statusMessage( *args )
		self.removeTemp( "pcg_enhance_item_seat" )
		self.removeTemp( "pcg_enhance_item_seat1" )
		self.removeTemp( "pcg_enhance_item_seat2" )
		self.pcg_releaseOperating_()										# 解锁操作


	# ----------------------------------------------------------------
	# exposed methods
	# ----------------------------------------------------------------
	def pcg_renamePet( self, srcEntityID, dbid, newName ) :
		"""
		<Exposed/>
		重命名宠物
		@type				dbid		: INT64
		@param				dbid		: 宠物数据库 ID
		@type				newName		: STRING
		@param				newName		: 新名字
		"""
		if not self.hackVerify_( srcEntityID ) : return									# 验证是否是欺骗的客户端
		if self.pcg_isTradingPet_( dbid ) : return										# 判断要命名的宠物是否处于交易状态
		if self.pcg_isActPet( dbid ): return											# 出战状态不允许改名

		illegalWord = chatProfanity.searchNameProfanity( newName )						# 验证名字是否合法
		if illegalWord is not None :
			self.statusMessage( csstatus.PET_RENAME_FAIL_ILLEGAL_WORD, illegalWord )
		elif len( newName.decode( Language.DECODE_NAME ) ) > csconst.PET_NAME_MAX_LENGTH :			# 名字是否超出限定长度
			self.statusMessage( csstatus.PET_RENAME_FAIL_OVERLONG )
		elif self.pcg_lockOperation_() :												# 锁定操作（注：意调用结束的地方必须回调：pcg_onRenameResult）
			self.base.pcg_renamePet( dbid, newName )

	def pcg_conjurePet( self, srcEntityID, dbid ) :
		"""
		<Exposed/>
		让宠物出征
		@type				dbid : INT64
		@param				dbid : 要出征宠物的数据库 ID
		"""
		if not self.hackVerify_( srcEntityID ) : return									# 验证是否是欺骗的客户端
		if self.actionSign( csdefine.ACTION_FORBID_CALL_PET ) or isFlying( self ) or self.onFengQi:
			# 处于不允许出征状态
			self.statusMessage( csstatus.PET_CAN_NOT_CONJURED )
			return

		if self.pcg_isTradingPet_( dbid ) : return										# 判断要命名的宠物是否处于交易状态
		if self.pft_procreating( dbid ) :												# 是否选择用于繁殖
			self.statusMessage( csstatus.PET_PROCREATING_CANT_CONJURED )
			return
		if self.isSunBathing(): return													# 判断是否是在日光浴中，是则不能召唤
		if self.actionSign( csdefine.ACTION_ALLOW_DANCE ):								# 判断角色是否在舞厅中
			self.statusMessage( csstatus.JING_WU_SHI_KE_RESTRICT_CONJURE_PET )
			return
		if self.effect_state & csdefine.EFFECT_STATE_WATCHER:							# 观察者状态下不允许召唤宠物
			self.statusMessage( csstatus.PET_CONJURE_FAIL_WATCHER )
			return
		if self.effect_state & csdefine.EFFECT_STATE_PROWL:								# 潜行状态下不允许召唤宠物
			self.statusMessage( csstatus.PET_CONJURE_FAIL_SNAKE )
			return

		spaceKey = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		spaceScript = g_objFactory.getObject( spaceKey )
		if not spaceScript.canConjurePet:
			self.statusMessage( csstatus.PET_CONJURE_FAIL_NOT_SPECIAL_MAP)				# canConjurePet配置为0的副本禁止召唤宠物
			return

		if not self.pcg_lockOperation_() : return										# 锁定操作（注：意调用结束的地方必须回调：pcg_onConjureResult）
		self.setTemp( "pcg_conjuring_dbid", dbid )										# 记录下要出征宠物的数据库 ID
		state = self.spellTarget( csdefine.SKILL_ID_CONJURE_PET, self.id )				# 使用出征技能
		if state != csstatus.SKILL_GO_ON :												# 使用出征技能失败
			self.statusMessage( state )

	def pcg_withdrawPet( self, srcEntityID ) :
		"""
		<Exposed/>
		回收宠物
		"""
		if not self.hackVerify_( srcEntityID ) : return									# 验证是否是欺骗的客户端
		actPet = self.pcg_getActPet()													# 获取出征宠物
		if actPet is None :																# 如果没有出征宠物
			self.statusMessage( csstatus.PET_WITHDRAW_FAIL_NOT_OUT )
		elif self.pcg_lockOperation_() :												# 锁定操作（注：意调用结束的地方必须回调：pcg_onWithdrawResult）
			actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON ) 						# 如果没有宠物出战

	def pcg_freePet( self, srcEntityID, dbid ) :
		"""
		<Exposed/>
		放生宠物
		@type					dbid : INT64
		@param					dbid : 要放生的宠物数据库 ID
		"""
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return

		if self.vend_isVendedPet( dbid ) : return										# 判断宠物是否正在摆摊中
		if self.pcg_isTradingPet_( dbid ) : return										# 判断要命名的宠物是否处于交易状态
		if not self.hackVerify_( srcEntityID ) : return									# 验证是否是欺骗的客户端
		if not self.pcg_lockOperation_() : return										# 锁定操作（注：意调用结束的地方必须回调：pcg_onFreeResult）
		actPet = self.pcg_getActPet()
		if actPet and actPet.dbid == dbid :												# 如果放生的宠物处于出征状态
			actPet.entity.free()
		else :
			self.base.pcg_freePet( dbid )												# 通知 base 放生

	# -------------------------------------------------
	def pcg_combinePets( self, srcEntityID, dbid ) :
		"""
		<Exposed/>
		合成宠物
		@type					dbid : INT64
		@param					dbid : 要合成宠物的材料宠的数据库 ID
		"""
		if not self.hackVerify_( srcEntityID ) : return									# 验证是否是欺骗的客户端
		if self.pcg_isTradingPet_( dbid ) : return										# 判断要命名的宠物是否处于交易状态
		actPet = self.pcg_getActPet()
		if actPet is None :																# 当前没有出征宠物
			self.statusMessage( csstatus.PET_COMBINE_FAIL_NOT_OUT )						# 则不允许合成
		elif actPet.dbid == dbid :														# 如果材料宠是出征宠
			self.statusMessage( csstatus.PET_COMBINE_FAIL_SELF_MATERIAL )				# 则不允许合成
		elif self.pcg_lockOperation_() :												# 锁定操作（注：意调用结束的地方必须回调：pcg_onCombineResult）
			actPet.entity.combine( dbid )

	# -------------------------------------------------
	def pcg_enhancePet( self, srcEntityID, etype, attrName, isCurse, stoneItemUid, symbolItemUid ) :
		"""
		强化宠物
		@type					etype			 : MACRO DEFINATION
		@param					etype			 : 强化类型
		@type					attrName 		 : str
		@param					attrName 		 : 要强化的属性名称
		@type					isCurse			 : bool
		@param					isCurse			 : 是否使用点化符
		@param					stoneItemUid	 : 魂魄石uid
		@type					stoneItemUid 	 : uid
		@param					symbolItemUid    : 点化符uid
		@type					symbolItemUid 	 : uid
		"""
		if not self.hackVerify_( srcEntityID ) : return										# 验证是否是欺骗的客户端
		actPet = self.pcg_getActPet()
		if actPet is None :																	# 没有出战宠物，不能强化
			self.statusMessage( csstatus.PET_ENHANCE_FAIL_NOT_OUT )
			return

		if not self.pcg_lockOperation_() : return											# 锁定操作（注：意调用结束的地方必须回调：pcg_onEnhanceResult）

		#加多少属性值
		if etype == csdefine.PET_ENHANCE_COMMON:
			count = getattr( actPet.entity, "ec_" + attrName )
		else:
			count =  actPet.entity.ec_free
		minValue,maxValue = formulas.getEnhanceValue( actPet.entity.species, etype, attrName, count + 1  )
		value = random.randint( minValue, maxValue )
		if isCurse:
			for itemID in csconst.PET_SMELT_ITEMS:
				itemInfo = self.findItemFromNKCK_( itemID )									# 精炼符
				if itemInfo and not itemInfo.isFrozen():
					self.setTemp( "pcg_enhance_item_seat", itemInfo.order )
					value = maxValue
					break

		if etype == csdefine.PET_ENHANCE_FREE:												# 如果是自由强化
			findItem = None
#			for itemID in csconst.PET_DIRECT_ITEMS:
#				itemInfo = self.findItemFromNKCK_( itemID )									# 则，寻找点化符
#				if itemInfo and not itemInfo.isFrozen():
#					findItem = itemInfo
#					break
			itemInfo = self.getItemByUid_( symbolItemUid )									# 则，寻找点化符
			if itemInfo and not itemInfo.isFrozen():
				findItem = itemInfo
			if findItem:
				self.setTemp( "pcg_enhance_item_seat1", findItem.order )
			else:
				self.pcg_onEnhanceResult( csstatus.PET_ENHANCE_CURSE_NOT_FOUND )
				return

		def getStoneInfo( attrName ):
			"""
			获个强化属性对应魂魄石信息
			"""
			hasItem = False
			stoneItem = None
			maxQuality = -1
			itemlist = csconst.pet_enhance_stones.get( attrName, () )
			for itemID in itemlist :
				items = self.findItemsByIDFromNKCK( itemID )
				for item in items :
					hasItem = True
					if not item.isFull() :
						continue
					if item.isFrozen():
						continue
					quality = item.getQuality()
					if quality > maxQuality :										# 查找最高品质的
						stoneItem = item
						maxQuality = quality
			return hasItem, stoneItem

		stoneItem = self.getItemByUid_( stoneItemUid )
		if stoneItem :
			self.setTemp( "pcg_enhance_item_seat2", stoneItem.order )				# 找到了相关魂魄石
			actPet.entity.enhance( etype, attrName, value )							# 强化成功
		else :
			self.pcg_onEnhanceResult( csstatus.PET_ENHANCE_KA_STONE_NOT_FOUND )		# 没找到对应的魂魄石

	def pcg_addLife( self, srcEntityID, dbid ) :
		"""
		增加宠物寿命
		@type					dbid : INT64
		@param					dbid : 要增加寿命的数据库 ID
		"""
		if not self.hackVerify_( srcEntityID ) : return								# 验证是否是欺骗的客户端
		if self.pcg_isTradingPet_( dbid ) : return									# 验证是否处于交易状态

		item = None
		for itemID in csconst.PET_ADD_LIFE_ITEMS:
			findItem = self.findItemFromNKCK_( itemID )								# 寻找延寿丹
			if findItem:
				item = findItem
				break
		if item is None:															# 如果没有延寿丹则返回
			self.statusMessage( csstatus.PET_ADD_LIFE_FAIL_NO_STUFF )
			return

		if not self.pcg_lockOperation_() : return									# 锁定操作（注：意调用结束的地方必须回调：pcg_onAddLifeResult）
		self.setTemp( "pcg_add_life_item_seat", item.order )						# 记录延寿丹的位置
		value = item.query( "pet_life", 0 )
		actPet = self.pcg_getActPet()
		if actPet and actPet.dbid == dbid :											# 对出征宠物延寿
			actPet.entity.lifeup( value )
		else :
			self.base.pcg_addLife( dbid, value )									# 则转到 base 中添加寿命

	def pcg_addJoyancy( self, srcEntityID, dbid ) :
		"""
		增加快乐度
		@type					dbid : INT64
		@param					dbid : 要增加快乐度的宠物数据库 ID
		"""
		if not self.hackVerify_( srcEntityID ) : return								# 验证是否是欺骗的客户端
		if self.pcg_isTradingPet_( dbid ) : return									# 验证是否处于交易状态
		if not self.pcg_petDict.has_key( dbid ) : return							# 宠物已经不存在（不需要输出提示！？）
		if not self.pcg_lockOperation_() : return									# 锁定操作（注：意调用结束的地方必须回调：pcg_onAddJoyancyResult）

		def getItemValue( level ) :
			"""
			获取适合等级驯养物品的快乐值
			"""
			index = level / 30															# 计算宠物应该使用哪类布娃娃 分为5类,每30级为一类 如 60级 属于2类(索引为1)
			if level % 30 == 0:															# 计算过程为 60/30 = 2 由于60能被30整除 表明他没有超出2类 所以 2-1 得出 60为 1类
				index -= 1
			item = self.findItemFromNKCK_( csconst.pet_joyancy_items[index] )				# 布娃娃或溜溜球
			if item is None : return -1, -1
			if item.isFrozen(): return -1, -1
			return item.order, item.query( "joyancy", 0 )

		actPet = self.pcg_getActPet()
		if actPet and actPet.dbid == dbid :												# 要驯养的宠物是否处于出征状态
			if actPet.etype == "MAILBOX" :												# 暂时找不到出征的宠物
				self.pcg_onAddJoyancyResult( csstatus.PET_ADD_JOYANCY_FAIL_NOT_EXIST )
			else :
				order, value = getItemValue( actPet.entity.level )
				if value < 0 :															# 驯养物品不存在
					self.pcg_onAddJoyancyResult( csstatus.PET_ADD_JOYANCY_FAIL_NO_STUFF )
				else :
					self.setTemp( "pcg_add_joyancy_item_seat", order )					# 保存材料的位置
					actPet.entity.domesticate( value )									# 注：这里必须回调：pcg_onAddJoyancyResult
		else :
			order, value = getItemValue( self.pcg_petDict.get( dbid ).level )
			if value < 0 :																# 驯养物品不存在
				self.pcg_onAddJoyancyResult( csstatus.PET_ADD_JOYANCY_FAIL_NO_STUFF )
			else :
				self.setTemp( "pcg_add_joyancy_item_seat", order )						# 保存材料的位置
				self.base.pcg_addJoyancy( dbid, value )									# 注：这里必须回调：pcg_onAddJoyancyResult


	# ----------------------------------------------------------------
	# callback methods
	# ----------------------------------------------------------------
	def onGetPetCell( self, petMailbox ):
		"""
		Define method.
		宠物cell部分创建完毕的通知

		@param petMailbox : 宠物的cell mailbox
		@type petMailbox : MAILBOX
		"""
		pass

	def onDie( self ) :
		"""
		当玩家死亡时被调用
		"""
		actPet = self.pcg_getActPet()
		if actPet :
			actPet.entity.withdraw( csdefine.PET_WITHDRAW_OWNER_DEATH )			# 则首先回收宠物

	def onDestroy( self ) :
		"""
		角色销毁时被调用
		"""
		# 如果玩家先于宠物销毁
		actPet = self.pcg_getActPet()
		if actPet:
			actPet.entity.baseOwner = None
		
		self.pcg_actPetDBID = 0													# 清除出战宠物
		self.pcg_mbBaseActPet = None

