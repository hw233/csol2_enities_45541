# -*- coding: gb18030 -*-
#
# $Id: PetAI.py,v 1.43 2008-08-29 07:09:42 qilan Exp $

"""
This module implements the pet entity.

2007/12/11 : wirten by huangyongwei
"""

import BigWorld
import Math
import csarithmetic
import csdefine
import csconst
import csstatus
import Const
import ECBExtend
import time
import utils
from bwdebug import *
from Function import Functor
from PetFormulas import formulas
from CombatUnit import CombatUnit
from AmbulantObject import AmbulantObject
from SkillTargetObjImpl import createTargetObjEntity
from Resource.SkillLoader import g_skills
from Domain_Fight import g_fightMgr


CONTROL_BORN		= 0												# 控制权状态，宠物刚创建
CONTROL_GIVE_OUT	= 1												# 控制权状态，已经给出控制权
CONTROL_TAKE_BACK	= 2												# 控制权状态，已经收回控制权

class PetAI( CombatUnit, AmbulantObject ) :
	def __init__( self ) :
		self.resist_yuanli_base += 500
		self.resist_lingli_base += 500
		self.resist_tipo_base += 500
		AmbulantObject.__init__( self )
		CombatUnit.__init__( self )
		# 如果没有技能快捷栏，则初始化快捷栏
		for idx in xrange( csconst.QB_PET_ITEM_COUNT - len( self.__qbItems ) ) :
			defItem = { "skillID" : 0 , "autoUse" : 0 }				# 默认的快捷格信息
			self.__qbItems.append( defItem )					 	# 初始化快捷格为指定个数
		self.__isForceFollow = False								# 临时标记是否强迫跟随
		self.__autoAttackTimerID = 0								# 自动攻击 timer ID
		self.__isAutoAttack = False									# 自动攻击标记
		self.__chaseEntityID = 0									# 记录chaseEntity失败并且doRandomRun成功时，追踪的目标ID
		self.__chaseFlatRange = 0.0									# 记录chaseEntity失败并且doRandomRun成功时，距离追踪目标多远时认为到达，CELL_PRIVATE
		self.__controlPowerStatus = CONTROL_GIVE_OUT				# 记录控制权的状态

#	# 总体控制 ------------------------------------------------------
	# ----------------------------------------------------------------
	def actionThinking_( self ) :
		"""
		宠物行为控制函数（由 Pet 中的心跳调用）
		"""
		if self.isDead(): return								# 如果已经死亡，则不进行任何动作
		if self.__teleportDetect(): return						# 是否需要传送
		if self.__forceFollowDetect(): return					# 是否超出了强迫跟随范围
		if self.__fightingDetect(): return						# 战斗侦测
		if self.__normalFollowDetect(): return					# 普通状态侦测

	def __teleportDetect( self ):
		"""检测宠物是否需要传送到玩家身边"""
		# 正在传送中
		if self.queryTemp("owner_controlled_before_teleport"):
			return True
		# 隔一段时间才进行跳转侦测
		if self.tickCount % Const.PET_TELEPORT_DETECT_CONTROL != 0:
			return False
		# 获取主人
		owner = BigWorld.entities.get( self.ownerID, None )			# 获取所属角色
		if owner is None :											# 如果所属角色已经不在 entities 中
			self.notifyDefOwner_( "pcg_teleportPet" )				# 则，跳转
			return True												# 返回 True 截获 tick
		# 所在地图检测
		if owner.spaceID != self.spaceID :							# 如果宠物与所属角色不同在一个 space
			self.teleportToOwner()
			return True
		# 距离检测
		if self.__distTo(owner.position) >= csconst.PET_FORCE_TELEPORT_RANGE:
			self.teleportToOwner()
			return True
		return False

	def __forceFollowDetect( self ):
		"""检测是否需要强制跟随主人"""
		if not self.selfControlled():								# @<FOR_CLIENT_CONTROL>
			return False
		if self.tickCount % Const.PET_FOLLOW_DETECT_CONTROL != 0:	# 隔一段时间才进行强迫跟随侦测
			return False
		if self.actionMode == csdefine.PET_ACTION_MODE_KEEPING:		# 如果是停留状态，则不进行强制跟随
			return False
		try:
			owner = BigWorld.entities[self.ownerID]					# 获取主人
		except KeyError:
			INFO_MSG("May be pet(id:%i) stays different cellapp from owner(id:%i)"%(self.id, self.ownerID))
			return False
		if self.__distTo(owner.position) > csconst.PET_FORCE_FOLLOW_RANGE:
			self.__forceFollowEntity(owner, csconst.PET_ROLE_KEEP_DISTANCE-1.0)	# 超出强迫跟随距离，宠物将会强迫跟随角色
			return True
		else:
			return False

	def __fightingDetect( self ):
		"""
		战斗检测
		"""
		if self.isAttacking(): 										# 如果当前正在战斗，则返回 True，忽略本 tick
			if not self.selfControlled():							# @<FOR_CLIENT_CONTROL>
				target = BigWorld.entities.get(self.targetID)
				if not self.__enemyIsValid(target):
					self.setTargetID(0)
			return True
		elif self.tussleMode == csdefine.PET_TUSSLE_MODE_PASSIVE:	# 被动状态不执行攻击
			if self.enemyList:
				self.__findAndCleanEnemy()							# 清理无效敌人
			return False
		else:
			enemy = self.__findNextEnemy()							# 攻击下一个目标
			if enemy:
				if self.selfControlled():							# @<FOR_CLIENT_CONTROL>
					self.__autoAttackEnemy(enemy)
				else:
					self.setTargetID(enemy.id)						# @<FOR_CLIENT_CONTROL>
				return True
			else:
				return False

	def __normalFollowDetect( self ):
		"""
		普通跟随检测
		"""
		if not self.selfControlled():								# @<FOR_CLIENT_CONTROL>
			return False
		elif self.actionMode == csdefine.PET_ACTION_MODE_KEEPING:	# 如果是停留状态
			return self.__backToKeepPoint()							# 则回到停留点
		elif self.chaseEntityID == 0:								# 如果没有跟随目标
			return self.__forceFollowOwner()						# 则强制跟随主人
		else:
			return False

#	# utils ----------------------------------------------------------
	# ----------------------------------------------------------------
	def __distTo( self, position ):
		"""
		到position的距离
		"""
		return self.position.distTo(position)

	def __enemyIsValid( self, enemy ):
		"""
		敌人有效性检查，即敌人是否可作为一个
		有效的攻击对象，例如死亡的目标就是无效的
		"""
		if enemy is None :
			return False
		elif enemy.spaceID != self.spaceID :
			return False
		elif self.__distTo(enemy.position) > csconst.ROLE_AOI_RADIUS :
			return False
		elif enemy.state == csdefine.ENTITY_STATE_DEAD :
			return False
		return True

	def __entityAttackable( self, entity ):
		"""
		entity 是否可以攻击，例如加了无敌buff
		的目标就是不能攻击的，但是依然可以是有效
		的敌人，当无敌buff去掉了，就又可以攻击了
		"""
		if getattr(entity, "state", csdefine.ENTITY_STATE_DEAD) == csdefine.ENTITY_STATE_DEAD:
			# 死亡的，对于没有state属性的entity，视为不可攻击
			return False
		elif entity.hasFlag( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED ) and\
			entity.getEntityType() != csdefine.ENTITY_TYPE_ROLE:		# 应该考虑将这些标记加到queryRelation判断中
				return False
		elif entity.hasFlag( csdefine.ENTITY_FLAG_UNVISIBLE ):			# 应该考虑将这些标记加到queryRelation判断中
			pid, tid = entity.ownerVisibleInfos							# ownerVisibleInfos属性指定看得见的玩家或者队伍
			if pid != self.ownerID:										# 对主人不可见
				teamMailbox = self.getTeamMailbox()
				if teamMailbox is None or tid != teamMailbox.id:		# 对所在的队伍也不可见
					return False										# 则不能攻击
		return self.queryRelation(entity) == csdefine.RELATION_ANTAGONIZE

	def __clearEnemyList( self ):
		"""
		清空敌人列表
		"""
		g_fightMgr.breakGroupEnemyRelationByIDs( self, self.enemyList.keys() )


	def __setAutoAttack( self, auto ):
		"""
		设置自动攻击标记
		"""
		if self.__isAutoAttack != auto:
			self.__isAutoAttack = auto

#	# fighting -------------------------------------------------------
	# ----------------------------------------------------------------
	def addEnemyCheck( self, entityID ):
		"""
		extend method.
		"""
		if not CombatUnit.addEnemyCheck( self, entityID ):
			return False

		if entityID == self.ownerID :
			return False

		return True


	def onAddEnemy( self, entityID ):
		"""
		extend method.
		"""
		CombatUnit.onAddEnemy( self, entityID )

		if entityID == 0:												# entityID是0的情况，是防止同一个tick多次进入、退出战斗的特殊处理，详细请看CombatSpell.py
			return

		if not self.selfControlled():							# 如果当前不处于攻击状态，也不处于强迫跟随主人状态 @<FOR_CLIENT_CONTROL>
			return

		if self.isAttacking():
			return

		if self.__isForceFollow:
			return

		if self.tussleMode == csdefine.PET_TUSSLE_MODE_PASSIVE :
			return

		enemy = BigWorld.entities.get(entityID, None)
		if not enemy:
			INFO_MSG("May be pet(id:%i) stays different cellapp from enemy(id:%i)."%(self.id, entityID))
			return

		self.__autoAttackEnemy( enemy )							# 则，对新加敌人发动攻击


	def __findAndCleanEnemy( self ) :
		"""
		顺序遍历列表，找到第一个有效且可攻击的敌人，
		并将期间遍历到的无效敌人移除
		"""
		for enemyID, atime in self.enemyList.items() :
			enemy = BigWorld.entities.get( enemyID, None )
			if self.__enemyIsValid(enemy):
				if self.__entityAttackable(enemy):
					return enemy
			elif enemy is None:
				g_fightMgr.removeEnemyByID(self, enemyID)
			else:
				g_fightMgr.breakEnemyRelation(self, enemy)
		return None

	def __scentClosestEnemy( self, position, range ):
		"""
		在position周围搜索最近的敌人
		"""
		entities = self.entitiesInRangeExt( range, None, position )
		entities.sort( key = lambda e : e.position.distTo( position ) )	# 按怪物与角色的距离排序
		for entity in entities :
			if self.__entityAttackable(entity):
				return entity
		return None

	def __scentEnemy( self ) :
		"""
		嗅猎一个敌人
		"""
		try:
			owner = BigWorld.entities[self.ownerID]
		except KeyError:
			INFO_MSG("May be pet(id:%i) stays different cellapp from owner(id:%i),stop scenting."\
				%(self.id, self.ownerID))
			return None
		basePos = owner.position
		if self.actionMode == csdefine.PET_ACTION_MODE_KEEPING :
			basePos = self.__keepPosition
		return self.__scentClosestEnemy(basePos, csconst.PET_ENMITY_RANGE)

	def __findNextEnemy( self ):
		"""
		获取下一个攻击目标
		"""
		enemy = self.__findAndCleanEnemy()							# 优先选取敌人列表里的敌人
		if enemy is not None:
			return enemy
		elif self.selfControlled() and\
			self.tussleMode == csdefine.PET_TUSSLE_MODE_ACTIVE:		# 否则如果是主动模式		@<FOR_CLIENT_CONTROL>
				return self.__scentEnemy()							# 则，自动寻找周围的敌人
		else:
			return None

	def __castEnemyOrChase( self, skillID, enemy ):
		"""
		对敌人施展技能，如果因距离太远则追击目标，
		如果施展成功，下一次攻击将在onSkillCastOver
		设置
		"""
		self.setTargetID(enemy.id)									# 设置攻击目标
		state = self.spellTarget(skillID, enemy.id)					# 施展技能
		if state == csstatus.SKILL_TOO_FAR:
			if self.selfControlled():								# 如果是服务器控制		@<FOR_CLIENT_CONTROL>
				spell = g_skills[skillID]
				if self.checkAndChase(enemy, spell.getRangeMax(self)):
					self.__tmpSpellID = skillID						# 设置使用的技能ID
				else:
					state = csstatus.PET_CAN_NOT_CHASE
		elif state == csstatus.SKILL_GO_ON:
			if enemy.state != csdefine.ENTITY_STATE_DEAD:			# 如果怪物没有被秒杀
				self.changeState( csdefine.ENTITY_STATE_FIGHT )		# 设置为进入战斗状态
		else:
			self.setTargetID(0)										# 攻击失败，移除目标
		return state

	def __spellEnemy( self, skillID, enemy ):
		"""使用技能攻击敌人"""
		state = self.__castEnemyOrChase(skillID, enemy)
		return state == csstatus.SKILL_TOO_FAR or state == csstatus.SKILL_GO_ON

	def __autoSpellEnemy( self, enemy ):
		"""自动选用技能攻击敌人"""
		# 先尝试使用自动战斗栏中的技能
		for qbSkill in self.__qbItems:
			if not qbSkill["autoUse"] or not qbSkill["skillID"]:
				continue
			if self.__spellEnemy(qbSkill["skillID"], enemy):
				return True
		# 尝试使用普通物理攻击
		skillID = csconst.PET_SKILL_ID_PHYSICS_MAPS.get( self.getPType(), 0 )
		return self.__spellEnemy(skillID, enemy)

	def __autoAttackEnemy( self, enemy ) :
		"""
		启动自动攻击，强迫跟随和攻击是互斥的，如果
		命令宠物攻击，就会取消强迫跟随，如果正在强
		迫跟随，就不能进行攻击
		"""
		if self.__isForceFollow : return							# 如果正在强迫跟随，则不进行攻击
		self.__setAutoAttack(True)									# 开启自动攻击标记
		if not self.__autoSpellEnemy(enemy):						# 如果攻击失败
			self.__setNextAttackTimer(self.hit_speed)				# 敌人不可攻击，则放慢攻击回调

	def __autoAttackCurrentTarget( self ):
		"""攻击当前的目标"""
		try:
			target = BigWorld.entities[self.targetID]				# 获取目标
		except KeyError:
			INFO_MSG("May be pet(id:%i) stays different cellapp from target(id:%i),stop attacking target."\
				%(self.id, self.targetID))
			self.setTargetID(0)										# 设置为当前没有攻击目标，等待下一个tick
			return
		if self.__entityAttackable(target):							# 如果目标可攻击
			if self.selfControlled():								# @<FOR_CLIENT_CONTROL>
				self.__autoAttackEnemy(target)
		else:
			self.setTargetID(0)										# 设置为当前没有攻击目标，等待下一个tick

	def __setAutoAttackTimer( self, cbTime ) :
		"""
		启动自动攻击时钟
		"""
		# 以下Timer的回调方法是onPetAttackTimer
		self.__cancelAutoAttackTimer()
		self.__autoAttackTimerID = self.addTimer( cbTime, 0, ECBExtend.PET_ATTACK_CBID )

	def __setNextAttackTimer( self, time ):
		"""
		设置下一次攻击的timer
		"""
		if self.intonating() :										# 如果正在施法
			self.__setAutoAttackTimer(self.hit_speed)				# 则开启攻击时钟，等待下一个 tick
		elif self.isMoving() :										# 如果正在移动
			self.__setAutoAttackTimer(self.hit_speed)				# 则开启攻击时钟，等待下一个 tick
		else:
			self.__setAutoAttackTimer(time)							# 设置时间

	def __setMinAttackTimer( self ):
		"""
		设置对当前目标的下一次攻击timer
		"""
		try:
			target = BigWorld.entities[self.targetID]				# 获取目标
		except KeyError:
			INFO_MSG("May be pet(id:%i) stays different cellapp from target(id:%i),stop attacking target."\
				%(self.id, self.targetID))
			DEBUG_MSG("attacking: %s, has enemy: %s, callbacking: %s, force following: %s, moving: %s"%\
				(self.isAttacking(), len(self.enemyList), self.__autoAttackTimerID != 0, self.__isForceFollow,\
				self.isMoving()))
			self.__setNextAttackTimer(self.hit_speed)
			return
		self.__setNextAttackTimer(self.__minSpellInterval(target))

	def __minSpellInterval( self, enemy ) :
		"""
		获取下次可用技能的最小间隔
		"""
		skillID = csconst.PET_SKILL_ID_PHYSICS_MAPS.get( self.getPType(), 0 )
		normalSpell = g_skills[skillID]								# 获取普通攻击的 spell
		minVal = normalSpell.getMaxCooldown( self )					# 获取能使用普通攻击的时间
		hitDelay = self.hitDelay - BigWorld.time()					# 获取攻击延迟
		if hitDelay > 0 :											# 取大的，防止CD到了还有攻击延迟，技能同样无法施放
			minVal = max( minVal, time.time() + hitDelay )

		for qbSkill in self.__qbItems:
			if not qbSkill["autoUse"] or not qbSkill["skillID"]:
				continue
			state = self.__spellTargetCheck(qbSkill["skillID"], enemy)
			if state != csstatus.SKILL_NOT_READY : continue			# 如果不是因为技能CD而无法施放的，无视
			timeVal = g_skills[qbSkill["skillID"]].getMaxCooldown( self )	# 获取能使用该技能的时间
			if timeVal != 0 :
				minVal = min( minVal, timeVal )						# 获取较小的可用技能时间

		return max( minVal - time.time(), 0.1 )

	def __cancelAutoAttackTimer( self ) :
		"""
		关闭自动攻击时钟
		"""
		if self.__autoAttackTimerID > 0 :
			self.cancel( self.__autoAttackTimerID )
			self.__autoAttackTimerID = 0

	def __spellTargetCheck( self, skillID, target ):
		"""根据skillID和攻击目标获取对应的技能实例和转换后的目标实例
		和施展状态"""
		spell = g_skills[skillID]										# 获取相应技能
		tcobj = spell.getCastObject().convertCastObject( self, target )	# 这个技能有可能只能对自己释放
		tcobj = createTargetObjEntity( tcobj )							# 包装技能施展对象
		if self.intonating():
			return csstatus.SKILL_INTONATING
		if self.inHomingSpell():
			return csstatus.SKILL_CANT_CAST
		return spell.useableCheck(self, tcobj)

#	# following ------------------------------------------------------
	# ----------------------------------------------------------------
	def __forceFollowOwner( self ) :
		"""
		强迫跟随主人
		"""
		try:
			owner = BigWorld.entities[self.ownerID]					# 获取主人
		except KeyError:
			INFO_MSG("May be pet(id:%i) stays different cellapp from owner(id:%i),stop force follow."\
				%(self.id, self.ownerID))
			return False
		keepDistance = csconst.PET_ROLE_KEEP_DISTANCE
		if self.__distTo(owner.position) > keepDistance :
			return self.__forceFollowEntity( owner, keepDistance-1.0 )
		else:
			return True

	def __forceFollowEntity( self, entity, flatRange ):
		"""
		强制跟随指定的目标
		@param entity : 跟随的目标
		@param flatRange : 距离追踪目标多远时认为到达
		"""
		if self.chaseEntityID == entity.id:
			return True												# 如果当前已经正在跟随中，则返回
		self.stopMoving()											# 否则，强行停止当前移动行为
		self.stopAttacking()										# 强行停止当前攻击行为
		if self.checkAndChase( entity, flatRange ):					# 追随目标
			self.__isForceFollow = True
			return True
		else:
			return False

	def __backToKeepPoint( self ):
		"""
		回到停留点
		"""
		self.stopMoving()											# 先停止移动
		if self.__distTo(self.__keepPosition) <= 0.1:
			return False
		elif self.actionSign( csdefine.ACTION_FORBID_MOVE ):
			return False
		else:
			self.gotoPosition( self.__keepPosition )
			return True

	def __setKeepPosition( self, position ):
		"""
		设置停留位置，并通知客户端
		"""
		if self.__keepPosition != position:
			self.__keepPosition = position
			self.notifyMyClient_("onSetKeepPosition", position)		# @<FOR_CLIENT_CONTROL>

#	# public ---------------------------------------------------------
	# -------------------------------------------------
	# 追踪跟随
	# -------------------------------------------------
	def chaseTarget( self, entity, flatRange ):
		"""
		追踪一个entity
		注意: AmbulantObject层的chaseEntity在petAI层不可直接使用，pet追击一个目标应该使用本接口
		@param   entity: 被追赶的目标
		@type    entity: Entity
		@param flatRange: 离目标entity多远的距离停下来
		@type  flatRange: FLOAT
		@return: 返回此次接口调用是否成功
		@rtype:  BOOL
		"""
		if self.chaseEntity( entity, flatRange ):					# 先尝试追踪
			self.__chaseEntityID = 0
			self.__chaseFlatRange = 0.0
			return True
		elif self.doRandomRun( entity.position, flatRange ):		# 再尝试走到目标点附近随机位置
			DEBUG_MSG("Can't chase entity(id:%i), doRandomRun."%entity.id)
			self.__chaseEntityID = entity.id
			self.__chaseFlatRange = flatRange
			return True
		else:
			DEBUG_MSG("Can't chase entity(id:%i), also not doRandomRun."%entity.id)
			return False

	def checkAndChase( self, entity, flatRange ):
		"""检查是否可以追踪目标，若可以，则追踪
		@param entity		: 追踪目标
		@param flatRange	: 在距离目标多远的范围内认为是到达了目的地
		"""
		if self.actionSign( csdefine.ACTION_FORBID_MOVE ):
			DEBUG_MSG( "I can not move! ID:%d" % self.id )
			return False
		elif not self.selfControlled():								# @<FOR_CLIENT_CONTROL>
			DEBUG_MSG( "I(id:%d) am not self controlled." % self.id )
			return False
		else:
			return self.chaseTarget( entity, flatRange )

	def stopMoving( self ):
		"""
		Overwrited from AmbulantObject
		停止移动，调用该方法将不会触发onChaseOver
		"""
		AmbulantObject.stopMoving(self)
		self.__isForceFollow = False
		if not self.selfControlled():								# @<FOR_CLIENT_CONTROL>
			self.openVolatileInfo()									# @<FOR_CLIENT_CONTROL>

	def onMovedOver( self, success ) :
		"""
		gotoPosition 的回调，当前的策略是如果chaseEntity失败，
		则启动doRandomRun移动到目标点附近，成功后再继续追踪
		目标
		"""
		if self.__chaseEntityID != 0:
			try:
				en = BigWorld.entities[self.__chaseEntityID]
				self.checkAndChase( en, self.__chaseFlatRange )		# go on chasing Target
			except:
				self.__chaseEntityID = 0

	def onChaseOver( self, entity, success ) :
		"""
		chaseEntity 的回调
		需要考虑到在追踪过程或者战斗过程中，追击目标
		状态发生改变导致无法被攻击或者由无法攻击变为
		可以攻击的情况
		"""
		AmbulantObject.onChaseOver( self, entity, success )
		if entity and self.__tmpSpellID:							# 如果是在追击目标
			if self.__entityAttackable(entity):
				self.__castEnemyOrChase(self.__tmpSpellID, entity)	# 并且目标可攻击，则继续攻击目标
			else:
				self.setTargetID(0)									# 否则设置为没有攻击目标，等待下一个tick
		else:
			if self.isAttacking():
				self.stopAttacking()								# 如果追踪失败或者没有攻击技能，则停止攻击
			if self.selfControlled():								# @<FOR_CLIENT_CONTROL>
				if self.actionMode == csdefine.PET_ACTION_MODE_KEEPING:
					self.__backToKeepPoint()
				elif not self.__forceFollowOwner():					# 如果不是停留状态，则强制跟随主人
					self.teleportToOwner()							# 如果强制跟随主人失败，则传送到主人处

	def teleportToOwner( self ):
		"""传送到主人身边"""
		try:
			owner = BigWorld.entities[self.ownerID]					# 获取所属角色
		except KeyError:
			INFO_MSG("May be pet(id:%i) stays different cellapp from owner(id:%i)"%(self.id, self.ownerID))
			self.notifyDefOwner_( "pcg_teleportPet" )				# 则，跳转
			return
		pos = formulas.getPosition( owner.position, owner.yaw )		# 计算宠物的位置
		if self.spaceID == owner.spaceID:							# 目标点检测，防止宠物传到地底下
			properPos = self.canNavigateTo(pos)
			if properPos:
				pos = properPos
		pos = utils.navpolyToGround(owner.spaceID, pos, 5.0, 5.0)	# 取地面上的点
		self.teleportToEntity(owner.spaceID, owner, pos, owner.direction)	# 注意，如果宠物是一个ghost，这里就是远程调用

	def teleportToEntity( self, spaceID, entityMB, position, direction ):
		"""
		<Defined method>
		传送到entity所在空间
		"""
		if self.isAttacking() : self.stopAttacking()				# 停止攻击
		self.stopMoving()											# 停止任何移动
		if self.actionMode == csdefine.PET_ACTION_MODE_KEEPING :	# 如果跳转前，宠物处于停留状态
			self.__setKeepPosition(position)
		self.onBeforeTeleport( spaceID, position )					# 通知回调
		if self.spaceID == spaceID:
			self._teleport(spaceID, None, position, direction)		# 同地图跳转到角色身边
		else:
			self._teleport(spaceID, entityMB, position, direction)	# 不同地图跳转到角色身边

	def _teleport( self, spaceID, entityMB, position, direction ):
		"""
		传送
		"""
		if self.selfControlled():
			self.teleport( entityMB, position, direction )
			self.teleportOver()
		else:
			prev_tid = self.queryTemp("teleport_timerID")			# 关闭上次的传送
			if prev_tid:
				self.cancel(prev_tid)
			self.takeBackControlPower()
			self.setTemp("owner_controlled_before_teleport", True)
			self.setTemp("teleport_args", (entityMB, position, direction))
			tid = self.addTimer(1.0, 0.0, ECBExtend.PET_TELEPORT_CBID)			# 回调方法：onTeleportTimer
			self.setTemp("teleport_timerID", tid)

	def onTeleportTimer( self, timerID, userData ):
		"""
		传送timer到达
		"""
		tid = self.popTemp("teleport_timerID")
		if tid != timerID:
			ERROR_MSG("Unknown timerID %s callback, expected %s"%(timerID, tid))
		else:
			# BIGWORD_ERROR:根据测试结果，发现引擎在timer回调时传送entity的话，回调会再触发一次
			# 为防止出现不可预料的情况，在回调后，传送之前，先手动取消timer
			self.cancel(tid)
		args = self.popTemp("teleport_args")
		if args is None:
			ERROR_MSG("Got invalid teleport args of %s" % args)
			self.removeTemp("owner_controlled_before_teleport")
		else:
			self.teleport(*args)
			self.teleportOver()

	def teleportOver( self ):
		"""
		<Defined method>
		传送完成回调
		"""
		if self.popTemp("owner_controlled_before_teleport", False):
			self.giveControlToOwner()
		else:
			self.openVolatileInfo()

	def setKeepPosition( self, srcEntityID, position ):
		"""
		<Exposed method>
		客户端设置停留位置
		"""
		if self.hackVerify_(srcEntityID):
			if self.selfControlled():
				INFO_MSG("Pet(%i) is self controlled currently, client(%i) sets keep position is not allowed."\
					%(self.id, srcEntityID))
			else:
				self.__setKeepPosition(position)
		else:
			WARNING_MSG("Client cheat detected! id is %s" % srcEntityID)

	# ------------------------------------------------
	# 攻击
	# ------------------------------------------------
	def attackTarget( self, srcEntityID, enemyID, skillID ) :
		"""
		<Exposed method>
		命令宠物攻击目标的客户端开放接口
		"""
		if not self.hackVerify_( srcEntityID ) : return				# 如果不是所属角色发出的命令

		if skillID in csconst.SKILL_ID_PHYSICS_LIST:
			if enemyID == self.targetID and\
				not self.hitDelayOver():							# 如果是针对同一个目标的攻击，则检查攻击延时，防止打破攻击速度规则
					return
		elif skillID not in self.attrSkillBox:						# 如果使用的技能不在宠物技能列表中
			HACK_MSG( "The pet(id:%i) dosen't has skill %i!" % (self.id, skillID))
			return

		if self.intonating() :										# 如果正在施法吟唱（不清楚为什么要在这里检查吟唱）
			self.statusMessage( csstatus.SKILL_INTONATING )			# 则，取消本次攻击命令
			return

		enemy = BigWorld.entities.get( enemyID, None )
		if enemy is None or enemy.spaceID != self.spaceID :			# 如果目标不存在，或与宠物不同一个 space
			self.statusMessage( csstatus.SKILL_TARGET_NOT_EXIST )
			return

		try:
			owner = BigWorld.entities[self.ownerID]
		except KeyError:
			INFO_MSG("May be pet(id:%i) stays different cellapp from owner(id:%i),stop attacking."\
				%(self.id, self.ownerID))
			return

		distance = owner.position.distTo(enemy.position)
		if distance >= csconst.PET_FORCE_TELEPORT_RANGE or\
			distance >= csconst.PET_FORCE_FOLLOW_RANGE:				# 如果攻击目标距离所属角色超出了宠物的强迫跟随距离或者强迫传送距离
			self.statusMessage( csstatus.PET_SPELL_TOOL_FAR )		# 则，拒绝攻击，因为离开了该距离，宠物始终要强迫回到所属角色身边的
		elif self.__entityAttackable(enemy):						# 如果是可攻击目标
			self.__setAutoAttack(True)								# 开启宠物自动战斗，设计为不打断正在进行的攻击循环，以防一旦本次攻击失败，宠物就不再进行攻击
			state = self.__castEnemyOrChase(skillID, enemy)
			if (state != csstatus.SKILL_GO_ON and state != csstatus.SKILL_TOO_FAR):
				if state == csstatus.SKILL_OUTOF_MANA:
					state = csstatus.SKILL_PET_OUTOF_MANA
				self.statusMessage( state )
			self.setTargetID(enemyID)								# 强制将攻击目标设置为该目标
		else:
			self.statusMessage( csstatus.SKILL_TARGET_CANT_FIGHT )


	def onRemoveEnemy( self, entityID ):
		"""
		"""
		if len( self.enemyList ) == 0:
			self.enterFreeState()

	def setTargetID( self, targetID ):
		"""设置宠物的目标"""
		if self.targetID != targetID:
			self.targetID = targetID

	def isAttacking( self ) :
		"""
		是否正在战斗中
		"""
		return self.targetID != 0

	def isAutoAttacking( self ) :
		"""
		是否处于自动攻击中
		"""
		return self.__isAutoAttack

	def stopAttacking( self ) :
		"""
		停止当前战斗
		"""
		if self.attrIntonateSkill :									# 如果正在施法
			self.interruptSpell( csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 )# 则停止施法
		self.setTargetID(0)											# 清除攻击目标
		self.__setAutoAttack(False)									# 关闭自动攻击标志
		self.__cancelAutoAttackTimer()								# 关闭自动攻击时钟
		self.__tmpSpellID = 0										# 清除技能

	def enterFreeState( self ):
		"""
		进入自由状态
		"""
		self.stopAttacking()										# 停止当前战斗
		self.__clearEnemyList()										# 清空敌人列表
		if self.state != csdefine.ENTITY_STATE_DEAD and\
			self.state != csdefine.ENTITY_STATE_PENDING:			# 如果宠物还没死亡并且没在未决状态
				self.changeState( csdefine.ENTITY_STATE_FREE )		# 则，改为自由状态

	def onPetAttackTimer( self, timerID, cbid ) :
		"""
		自动攻击 timer
		"""
		self.__autoAttackCurrentTarget()

	def receiveDamage( self, casterID, skillID, damageType, damage ):
		"""
		Define and virtual method.
		接受伤害。
		@param			casterID   : 施法者ID
		@type			casterID   : OBJECT_ID
		@param			skillID	   : 技能ID
		@type			skillID	   : INT
		@param			damageType : 伤害类型；see also csdefine.py/DAMAGE_TYPE_*
		@type			damageType : INT
		@param			damage	   : 伤害数值
		@type			damage	   : INT
		"""
		CombatUnit.receiveDamage( self, casterID, skillID, damageType, damage )
		try : caster = BigWorld.entities[casterID]
		except : caster = None

		if caster and caster.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = caster.getOwner()
			if owner.etype !="MAILBOX" :
				caster = owner.entity

		if caster and not caster.state == csdefine.ENTITY_STATE_DEAD:
			if not self.state == csdefine.ENTITY_STATE_DEAD and (damageType & csdefine.DAMAGE_TYPE_FLAG_BUFF == csdefine.DAMAGE_TYPE_FLAG_BUFF):
				return
			self.addDamageList( casterID, damage )

	def onSkillCastOver( self, spellInstance, target ) :
		"""
		virtual method.
		释放技能完成。

		@param  spellInstance: 技能实例
		@type   spellInstance: SPELL
		@param  target: 技能目标
		@type   target: SkillImplTargetObj
		"""
		CombatUnit.onSkillCastOver( self, spellInstance, target )
		if self.selfControlled():									#@<FOR_CLIENT_CONTROL>
			if self.isAutoAttacking() :								# 如果正在自动攻击
				self.__setMinAttackTimer()
		else:
			self.__setNextAttackTimer(self.hit_speed)				#@<FOR_CLIENT_CONTROL>

	def onSpellInterrupted( self ):
		"""
		避免技能被打断中断自动战斗timer
		"""
		CombatUnit.onSpellInterrupted( self )
		self.__setNextAttackTimer( 1.5 )

	def onSkillArriveReceiver( self, spellInstance, receiver ):
		"""
		virtual method.
		技能效果已经到达某个目标

		@param  spellInstance: 技能实例
		@type   spellInstance: SPELL
		@param  receiver: 受到这个技能影响的entity
		@type   receiver: entity
		"""
		CombatUnit.onSkillArriveReceiver( self, spellInstance, receiver )

		if not receiver.isDestroyed:
			if receiver.isEntityType( csdefine.ENTITY_TYPE_PET ):
				targetID = receiver.getOwner().entity.id
			elif receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				targetID = receiver.id
			elif receiver.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ):
				targetID = receiver.getOwnerID()
			else:
				return

			state = spellInstance.isMalignant()
			self.getOwner().entity.pkAttackStateCheck( targetID, state )

			#在这里检测是不是结束切磋
			if receiver.popTemp( "QIECUO_END", False ):
				qiecuoTarget = BigWorld.entities.get( receiver.id )
				if qiecuoTarget:
					g_fightMgr.breakEnemyRelation( self, qiecuoTarget )
				receiver.loseQieCuo()
				self.setActionMode( self.ownerID, csdefine.PET_ACTION_MODE_FOLLOW )

	# ------------------------------------------------
	# 技能快捷栏
	# ------------------------------------------------
	def requestQBItems( self, srcEntityID ) :
		"""
		<Exposed/>
		请求技能快捷栏
		"""
		self.notifyClient_( "pcg_onInitPetQBItems", self.__qbItems )

	def updateQBItem( self, srcEntityID, index, qbItem ) :
		"""
		<Exposed/>
		更新快捷栏
		"""
		if not self.hackVerify_( srcEntityID ) : return
		skillID = qbItem["skillID"]
		if skillID and skillID not in self.attrSkillBox :
			HACK_MSG( "pet dosen't contain skill: %i!" )
		else :
			try :
				self.__qbItems[index] = qbItem
				self.notifyClient_( "pcg_onUpdatePetQBItem", index, qbItem )
			except IndexError :
				HACK_MSG( "index '%i' out of quick items' max range '%i'" % ( index, len( self.__qbItems ) ) )

	def autoAddQBItem( self, skillID ):
		"""
		新加技能，自动触发放置到快捷栏中
		"""
		for e in self.__qbItems:
			if e["skillID"] == 0:	# 如果找到空的，则放置到这个快捷栏格子中
				e["skillID"] = skillID
				e["autoUse"] = 1
				self.notifyClient_( "pcg_onInitPetQBItems", self.__qbItems )		# 更新客户端快捷栏
				break

	def removeSkill( self, skillID ):
		"""
		移出一个技能，删除相关的快捷栏数据
		"""
		for qbItem in self.__qbItems:
			if qbItem["skillID"] == skillID:
				qbItem["skillID"] = 0
				qbItem["autoUse"] = 0
				return

	def onUpdateSkill( self, oldSkillID, newSkillID ) :
		"""
		当技能更新时被调用
		"""
		for qbItem in self.__qbItems :
			if oldSkillID == qbItem["skillID"] :						# 如果旧的技能 ID 在快捷列表中
				qbItem["skillID"] = newSkillID							# 则，意味着技能升级, 因此将旧技能更新为新等级的技能
		self.notifyClient_( "pcg_onInitPetQBItems", self.__qbItems )	# 更新客户端快捷栏

	# -------------------------------------------------
	# 模式设置
	# -------------------------------------------------
	def setActionMode( self, srcEntityID, mode ) :
		"""
		<Exposed/>
		设置行为模式
		"""
		if not self.hackVerify_( srcEntityID ) : return
		if mode not in [ \
			csdefine.PET_ACTION_MODE_FOLLOW, \
			csdefine.PET_ACTION_MODE_KEEPING] :
				HACK_MSG( "error motion! from %i" % srcEntityID )
				return
		if mode == csdefine.PET_ACTION_MODE_FOLLOW :
			self.__forceFollowOwner()								# 强迫宠物回到角色身边
		elif mode == csdefine.PET_ACTION_MODE_KEEPING :
			self.__setKeepPosition(Math.Vector3(self.position))
			if self.isMoving():
				self.stopMoving()
			if self.isAttacking():
				self.stopAttacking()
		self.actionMode = mode
		self.baseOwner.pcg_setActionMode( mode )

	def setTussleMode( self, srcEntityID, mode ) :
		"""
		<Exposed/>
		设置战斗模式
		"""
		if not self.hackVerify_( srcEntityID ) : return
		self.removeTemp("Snake_buff")
		if mode not in [ \
			csdefine.PET_TUSSLE_MODE_ACTIVE, \
			csdefine.PET_TUSSLE_MODE_PASSIVE, \
			csdefine.PET_TUSSLE_MODE_GUARD] :
				HACK_MSG( "error tussle! from %i" % srcEntityID )
				return
		self.tussleMode = mode
		self.baseOwner.pcg_setTussleMode( mode )
		if mode == csdefine.PET_TUSSLE_MODE_PASSIVE:
			if self.isAttacking():
				self.stopAttacking()
			if self.selfControlled():								#@<FOR_CLIENT_CONTROL>
				if self.actionMode == csdefine.PET_ACTION_MODE_KEEPING:
					self.__backToKeepPoint()
				else:
					self.__forceFollowOwner()

	# ------------------------------------------------
	# others
	# ------------------------------------------------
	def onDestroy( self ) :
		"""
		当销毁的时候做点事情
		"""
		self.enterFreeState()
		self.stopMoving()
		self.takeBackControlPower()		# controlledBy不为None时，客户端不会销毁宠物

	def getDaoheng( self ):
		# 获取自身道行值
		return self.wuxue / 2.0

	def onStateChanged( self, old, new ):
		"""
		状态切换。
		@param			old : 更改以前的状态
		@type			old : integer
		@param			new : 更改以后的状态
		@type			new : integer
		"""
		CombatUnit.onStateChanged( self, old, new )
		# 逻辑上说，宠物应该是因为停止了战斗才能进入自由状态，
		# 而不是因为进入了自由状态所以就要停止战斗，这里还做
		# 检测是为了容错处理
		if new == csdefine.ENTITY_STATE_DEAD :
			if self.isMoving():
				self.stopMoving()
			if self.isAttacking():
				self.enterFreeState()
		elif new == csdefine.ENTITY_STATE_FREE :
			if self.isAttacking():
				self.stopAttacking()

	def effectStateChanged( self, estate, disabled ):
		"""
		效果改变.
		@param estate		:	效果标识(非组合)
		@type estate		:	integer
		@param disabled		:	效果是否生效
		@param disabled		:	bool
		"""
		if self.effect_state & csdefine.EFFECT_STATE_PROWL :		# 隐身时 若是主动则进入防御状态
			if self.tussleMode == csdefine.PET_TUSSLE_MODE_ACTIVE:
				self.setTemp( "Snake_buff", csdefine.PET_TUSSLE_MODE_ACTIVE )
				self.tussleMode = csdefine.PET_TUSSLE_MODE_GUARD

#	# client control -------------------------------------------------
	def selfControlled( self ):
		"""
		宠物行为是否由自己在控制
		"""
		#return self.controlledBy == None
		return self.__controlPowerStatus != CONTROL_GIVE_OUT

	def onClientReady( self, srcEntityID ):
		"""
		<Exposed method>
		客户端准备好了
		"""
		if self.hackVerify_(srcEntityID):
			if self.__controlPowerStatus != CONTROL_TAKE_BACK:
				self.giveControlToOwner()
			else:
				INFO_MSG("Control powner is taken back currently")
		else:
			WARNING_MSG("Client cheat detected! id is %s" % srcEntityID)

	def giveControlToOwner( self ):
		"""
		将控制权交给主人
		"""
		self.openVolatileInfo()
		# 防止异步情况下，已经设置过controlledBy但是客户端没有收到，
		# 接着客户端再次申请控制权，而服务器因已经设置过，所以再次
		# 设置无效的情况，所以先设置为None，再重新设置控制权
		#self.controlledBy = None
		#self.controlledBy = self.baseOwner
		self.notifyMyClient_("onClientControlled", True)
		self.__controlPowerStatus = CONTROL_GIVE_OUT

	def takeBackControlPower( self ):
		"""
		取回控制权
		"""
		if not self.selfControlled():
			#self.controlledBy = None
			self.notifyMyClient_("onClientControlled", False)
			self.__controlPowerStatus = CONTROL_TAKE_BACK

#	# synchronise position ---------------------------------
	def synchronisePositionFromClient( self, srcEntityID, position ):
		"""
		<Exposed method>
		"""
		if not self.hackVerify_(srcEntityID):
			return
		if not self.selfControlled():
			self.rotateToPos(position)
			self.position = position
