# -*- coding: gb18030 -*-

import csstatus
import csdefine
import csconst
import BigWorld
import keys
import Timer
import utils
import skills as g_skills
from Time import Time
from bwdebug import *
from PetFormulas import formulas
from PetNavigate import PetNavigator, PetChaser
from SkillTargetObjImpl import createTargetObjEntity
from navigate import NavDataMgr


class PetAI:

	def __init__( self ):
		self.navigator = None
		self.hitDelay = 0.0
		self.__tmpSpellID = 0
		self.__forceChasing = False
		self.__autoAttackTimerID = 0
		self.__keepPosition = self.position
		self.__heartBeatTimer = None
		self.__clientControlled = False
		self.isCharging = False

#	# 总体控制 ------------------------------------------------------
	# ---------------------------------------------------------------
	def __onHeartBeat( self ):
		"""
		宠物心跳
		"""
		if not self.clientControlled():return
		elif self.__teleportDetect():return
		elif self.__fightingDetect():return
		elif self.__followDetect():return

	def __teleportDetect( self ):
		"""检测宠物是否需要传送到玩家身边"""
		# 获取主人
		owner = BigWorld.entities.get( self.ownerID, None )			# 获取所属角色
		if owner and owner.spaceID == self.spaceID and\
			self.__distTo(owner.position) >= (csconst.PET_FORCE_TELEPORT_RANGE - 2):
				self.teleportToOwner()
				return True
		return False

	def __fightingDetect( self ):
		"""
		战斗侦测
		"""
		if self.__forceChasing:
			return False
		elif self.tussleMode == csdefine.PET_TUSSLE_MODE_PASSIVE:
			self.stopAttacking()
			return False
		elif self.targetID != 0:
			if not self.isAttacking():
				self.__autoAttackCurrentTarget()
			return True
		elif self.tussleMode == csdefine.PET_TUSSLE_MODE_ACTIVE:
			enemy = self.__scentEnemy()
			if enemy:
				self.__autoAttackEnemy(enemy)
				return True
		return False

	def __followDetect( self ):
		"""
		普通跟随侦测
		"""
		if self.__forceChasing:
			return False
		elif self.actionMode == csdefine.PET_ACTION_MODE_KEEPING:	# 如果是停留状态
			return self.backToKeepPoint()							# 则回到停留点
		else:														# 如果没有跟随目标
			return self.followOwner()								# 则跟随主人

	def resumeHeartBeat( self ):
		"""唤醒心跳"""
		self.cancelHeartBeat()
		self.__heartBeatTimer = Timer.addTimer( 1.0, 1.0, self.__onHeartBeat )

	def cancelHeartBeat( self ):
		"""停止心跳"""
		if self.__heartBeatTimer is not None:
			Timer.cancel( self.__heartBeatTimer )
			self.__heartBeatTimer = None

#	# utils ----------------------------------------------------------
	# ----------------------------------------------------------------
	def __distTo( self, position ):
		"""
		到position的距离
		"""
		return self.position.distTo(position)

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

#	# fighting -------------------------------------------------------
	# ----------------------------------------------------------------
	def __castEnemyOrChase( self, skillID, enemy ):
		"""
		对敌人施展技能，如果因距离太远则追击目标，
		如果施展成功，下一次攻击将在onSkillCastOver
		设置
		"""
		state = self.__spellTargetCheck(skillID, enemy)				# 施展技能
		if state == csstatus.SKILL_TOO_FAR:
			if self.clientControlled():
				spell = g_skills.getSkill(skillID)
				if self.checkAndChase(enemy, spell.getRangeMax(self)-0.5, self.onHuntPursueOver):
					self.__tmpSpellID = skillID						# 设置使用的技能ID
					self.__forceChasing = True
				else:
					state = csstatus.PET_CAN_NOT_CHASE
			else:
				self.cell.attackTarget( enemy.id, skillID )
		elif state == csstatus.SKILL_GO_ON:
			self.cell.attackTarget( enemy.id, skillID )
			if self.clientControlled():
				self.setHitDelay(self.hit_speed)					# 记录攻击延时
		return state

	def __spellEnemy( self, skillID, enemy ):
		"""使用技能攻击敌人"""
		if self.isCharging: return False
		state = self.__castEnemyOrChase(skillID, enemy)
		return state == csstatus.SKILL_TOO_FAR or state == csstatus.SKILL_GO_ON

	def __autoSpellEnemy( self, enemy ):
		"""自动选用技能攻击敌人"""
		# 先尝试使用自动战斗栏中的技能
		for qbSkill in BigWorld.player().pcg_getQBItems():
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
		self.__autoSpellEnemy(enemy)
		self.__setMinAttackTimer()									# 成功对敌人施展攻击，设置一下次回调

	def __autoAttackCurrentTarget( self ):
		"""攻击当前的目标"""
		try:
			target = BigWorld.entities[self.targetID]				# 获取目标
		except KeyError:
			INFO_MSG("Pet(id:%i) client can't find target(id:%i),stop attacking target."\
				%(self.id, self.targetID))
			self.stopAttacking()
			return
		if self.__entityAttackable(target):							# 如果目标可攻击
			self.__autoAttackEnemy(target)
		else:
			self.stopAttacking()

	def __onAutoAttackCallback( self ):
		"""自动攻击回调到达"""
		if self.__forceChasing:										# 如果正在强迫跟随，则不进行攻击
			if self.targetID != 0:
				self.__setMinAttackTimer()
			elif self.isAttacking():
				self.__cancelAutoAttackTimer()
		else:
			self.__autoAttackCurrentTarget()

	def __spellTargetCheck( self, skillID, target ):
		"""根据skillID和攻击目标获取对应的技能实例和转换后的目标实例
		和施展状态"""
		spell = g_skills.getSkill(skillID)								# 获取相应技能
		tcobj = spell.getCastObject().convertCastObject( self, target )	# 这个技能有可能只能对自己释放
		tcobj = createTargetObjEntity( tcobj )							# 包装技能施展对象
		return spell.useableCheck(self, tcobj)

	# ------------------------------------------------
	# scant enemy
	# ------------------------------------------------
	def __scentClosestEnemy( self, position, range ):
		"""
		在position周围搜索最近的敌人
		"""
		entities = self.entitiesInRange( range, lambda e: self.__entityAttackable(e), position )
		#entities.sort( key = lambda e : e.position.distTo( position ) )	# 按怪物与角色的距离排序
		enemy = None
		distance = range + 10
		for entity in entities :
			d = entity.position.distTo(position)
			if d < distance:
				distance = d
				enemy = entity
		return enemy

	def __scentEnemy( self ) :
		"""
		嗅猎一个敌人
		"""
		basePos = BigWorld.player().position
		if self.actionMode == csdefine.PET_ACTION_MODE_KEEPING :
			basePos = self.__keepPosition
		return self.__scentClosestEnemy(basePos, csconst.PET_ENMITY_RANGE)

	# ------------------------------------------------
	# set attack timer
	# ------------------------------------------------
	def __setAutoAttackTimer( self, cbTime ) :
		"""
		启动自动攻击时钟
		"""
		self.__cancelAutoAttackTimer()
		self.__autoAttackTimerID = BigWorld.callback(cbTime, self.__onAutoAttackCallback)

	def __setNextAttackTimer( self, time ):
		"""
		设置下一次攻击的timer
		"""
		#if self.intonating() :										# 如果正在施法
		#	self.__setAutoAttackTimer(self.hit_speed)				# 则开启攻击时钟，等待下一个 tick
		#elif self.isMoving() :										# 如果正在移动
		#	self.__setAutoAttackTimer(self.hit_speed)				# 则开启攻击时钟，等待下一个 tick
		#else:
		self.__setAutoAttackTimer(time)								# 设置时间

	def __setMinAttackTimer( self ):
		"""
		设置对当前目标的下一次攻击timer
		"""
		try:
			target = BigWorld.entities[self.targetID]				# 获取目标
		except KeyError:
			INFO_MSG("Pet(id:%i) client can't find target(id:%i),stop attacking target."\
				%(self.id, self.targetID))
			self.__setNextAttackTimer(self.hit_speed)
			return
		self.__setNextAttackTimer(self.__minSpellInterval(target))

	def __minSpellInterval( self, enemy ) :
		"""
		获取下次可用技能的最小间隔
		"""
		skillID = csconst.PET_SKILL_ID_PHYSICS_MAPS.get( self.getPType(), 0 )
		normalSpell = g_skills.getSkill( skillID )					# 获取普通攻击的 spell
		minVal = normalSpell.getCooldownData( self )[1]				# 获取能使用普通攻击的时间
		if self.hitDelay > Time.time():								# 取大的，防止CD到了还有攻击延迟，技能同样无法施放
			minVal = max( minVal, self.hitDelay )

		for qbSkill in BigWorld.player().pcg_getQBItems():
			if not qbSkill["autoUse"] or not qbSkill["skillID"]:
				continue
			state = self.__spellTargetCheck(qbSkill["skillID"], enemy)
			if state != csstatus.SKILL_NOT_READY : continue			# 如果不是因为技能CD而无法施放的，无视
			spell = g_skills.getSkill(qbSkill["skillID"])
			timeVal = spell.getCooldownData(self)[1]				# 获取能使用该技能的时间
			if timeVal != 0 :
				minVal = min( minVal, timeVal )						# 获取较小的可用技能时间

		return max( minVal - Time.time(), 0.1 )

	def __cancelAutoAttackTimer( self ) :
		"""
		关闭自动攻击时钟
		"""
		if self.__autoAttackTimerID > 0 :
			BigWorld.cancelCallback( self.__autoAttackTimerID )
			self.__autoAttackTimerID = 0

	# ------------------------------------------------
	# public
	# ------------------------------------------------
	def attackTarget( self, enemy, skillID ) :
		"""
		命令宠物攻击目标的客户端开放接口
		"""
		owner = BigWorld.player()
		if enemy.id == self.targetID and\
			not self.hitDelayOver():								# 如果是针对同一个目标的攻击，则检查攻击延时，防止打破攻击速度规则
				return
		elif skillID not in csconst.SKILL_ID_PHYSICS_LIST and \
			skillID not in owner.pcg_getPetSkillList():				# 如果使用的技能不在宠物技能列表中
				HACK_MSG( "The pet(id:%i) dosen't has skill %i!" % (self.id, skillID))
				return

		if self.intonating() :										# 如果正在施法吟唱（不清楚为什么要在这里检查吟唱）
			self.statusMessage( csstatus.SKILL_INTONATING )			# 则，取消本次攻击命令
			return

		distance = owner.position.distTo(enemy.position)
		if distance >= csconst.PET_FORCE_TELEPORT_RANGE or\
			distance >= csconst.PET_FORCE_FOLLOW_RANGE:				# 如果攻击目标距离所属角色超出了宠物的强迫跟随距离或者强迫传送距离
			self.statusMessage( csstatus.PET_SPELL_TOOL_FAR )		# 则，拒绝攻击，因为离开了该距离，宠物始终要强迫回到所属角色身边的
		elif self.__entityAttackable(enemy):						# 如果是可攻击目标
			state = self.__castEnemyOrChase(skillID, enemy)
			if (state != csstatus.SKILL_GO_ON and state != csstatus.SKILL_TOO_FAR):
				if state == csstatus.SKILL_OUTOF_MANA:
					state = csstatus.SKILL_PET_OUTOF_MANA
				self.statusMessage( state )
		else:
			self.statusMessage( csstatus.SKILL_TARGET_CANT_FIGHT )

	def onTargetChanged( self, old ):
		"""
		攻击目标改变
		"""
		if self.clientControlled():
			if self.targetID != 0:
				if not self.__forceChasing:
					self.__autoAttackCurrentTarget()

	def isAttacking( self ) :
		"""
		是否正在战斗中
		"""
		return self.__autoAttackTimerID != 0

	def stopAttacking( self ):
		"""停止战斗"""
		self.__cancelAutoAttackTimer()

	def setHitDelay( self, delay ):
		"""
		记录攻击延迟
		"""
		self.hitDelay = Time.time() + delay

	def hitDelayOver( self ):
		"""
		攻击延时是否结束
		"""
		return Time.time() > self.hitDelay

#	# following ------------------------------------------------------
	# ----------------------------------------------------------------
	def initPhysics( self ):
		"""
		初始化physics，只有由客户端控制的entity才具有physics属性，
		BigWorld.controlEntity可以实现控制一个纯客户端entity
		有cell的entity需要设置cellEntity的controlledBy为baseMailbox
		"""
		if self.clientControlled():
			self.physics = keys.SIMPLE_PHYSICS
			self.physics.fall = True
			self.physics.collide = False
		else:
			TRACE_MSG( "Only controlled entities have a 'physics' attribute,maybe controlledBy hasnot init" )

	def followOwner( self ):
		"""
		跟随主人
		"""
		owner = BigWorld.player()
		if self.actionSign(csdefine.ACTION_FORBID_MOVE):
			return False
		elif self.position.distTo( owner.position ) <= csconst.PET_ROLE_KEEP_DISTANCE:
			return False
		else:
			# //无法通过寻路跟随玩家，直接传到玩家当前所在位置 csol-2080
			if not NavDataMgr.instance().canNavigateTo( self.position, owner.position ):
				self.navigator.teleportPosition( owner.position )
			elif not NavDataMgr.instance().canNavigateTo( owner.position, self.position ):
				self.navigator.teleportPosition( owner.position )
			elif not self.navigator.isFollowing():
				self.navigator.followEntity( owner, csconst.PET_ROLE_KEEP_DISTANCE, self.chaseSpeed() )
			return True

	def forcePursueOwner( self ):
		"""强制跟随主人"""
		owner = BigWorld.player()
		if self.isCharging: return
		if not self.actionSign(csdefine.ACTION_FORBID_MOVE):
			# //无法通过寻路跟随玩家，直接传到玩家当前所在位置 csol-2080
			if not NavDataMgr.instance().canNavigateTo( self.position, owner.position ):
				self.navigator.teleportPosition( owner.position )
			elif not NavDataMgr.instance().canNavigateTo( owner.position, self.position ):
				self.navigator.teleportPosition( owner.position )
			else:
				self.__forceChasing = True
				self.navigator.chaseEntity( owner, csconst.PET_ROLE_KEEP_DISTANCE, self.chaseSpeed(), self.onForcePursueOver )

	def cancelFollow( self ):
		"""
		停止跟随
		"""
		if self.navigator.isFollowing():
			self.navigator.stop()

	def teleportToOwner( self ):
		"""
		马上传送到主人身边
		"""
		if self.clientControlled():
			self.stopAttacking()
			self.stopMove()
			owner = BigWorld.player()
			dstPos = formulas.getPosition( owner.position, owner.yaw )
			dstPos = utils.posOnGround(owner.spaceID, dstPos, default=owner.position)
			self.navigator.teleportPosition(dstPos)

			self.setFilterYaw(owner.yaw)
			BigWorld.callback(0, self.restartFilterMoving)
			if self.actionMode == csdefine.PET_ACTION_MODE_KEEPING :	# 如果跳转前，宠物处于停留状态
				self.cell.setKeepPosition(dstPos)						# 通知服务器改变停留位置

	def backToKeepPoint( self ):
		"""
		回到停留点
		"""
		if not self.clientControlled():								# 不是由客户端来控制移动
			DEBUG_MSG( "I can not controlled by client! ID:%d" % self.id )
			return False
		elif self.actionSign( csdefine.ACTION_FORBID_MOVE ):
			DEBUG_MSG( "I can not move! ID:%d" % self.id )
			return False
		elif self.isCharging:
			DEBUG_MSG( "I am in charging! ID:%d" % self.id )
			return False
		else:
			self.stopMove()
			if self.__distTo(self.__keepPosition) > 1.0:
				self.navigator.chasePosition(self.__keepPosition, 1.0, self.chaseSpeed())
			return True

	def checkAndChase( self, entity, flatRange, callback = lambda o, t, r: None ):
		"""检查是否可以追踪目标，若可以，则追踪
		@param entity		: 追踪目标
		@param flatRange	: 在距离目标多远的范围内认为是到达了目的地
		"""
		if not self.clientControlled():								# 不是由客户端来控制移动
			DEBUG_MSG( "I can not controlled by client! ID:%d" % self.id )
			return False
		elif self.actionSign( csdefine.ACTION_FORBID_MOVE ):
			DEBUG_MSG( "I can not move! ID:%d" % self.id )
			return False
		elif self.__distTo(entity.position) > flatRange:
			self.pursueEntity( entity, flatRange, callback )
			return True
		else:
			return False

	def pursueEntity( self, entity, nearby, callback = lambda o, t, r: None ):
		"""
		pursue entity
		@type		entity			  : instance
		@param		entity			  : entity you want to pursue
		@type		nearby			  : float
		@param		nearby			  : move to the position nearby target
		@type		callback		  : 回调方法
		@param		callback		  : 带三个参数，一个是追踪者, 一个是追踪目标，一个是追踪结果
		@return						  : None
		"""
		self.navigator.chaseEntity( entity, nearby, self.chaseSpeed(), callback )

	def onHuntPursueOver( self, owner, target, success ):
		"""
		追猎一个目标结束
		"""
		self.__forceChasing = False
		if target and self.__tmpSpellID:
			if BigWorld.entities.has_key(target.id):						# 如果是在追击目标
				if self.__entityAttackable(target):
					self.__castEnemyOrChase(self.__tmpSpellID, target)		# 并且目标可攻击，则继续攻击目标
					self.__setMinAttackTimer()								# 设置攻击timer
				else:
					self.__setAutoAttackTimer(self.hit_speed)				# 设置攻击timer
			else:
				INFO_MSG("Pet(id:%i) client can't find target(id:%i),stop attacking target."\
					%(self.id, target.id))
				if self.isAttacking():
					self.stopAttacking()
		else:
			INFO_MSG("Pet(id:%i) client chase target(%s) over, with spell %s."\
				%(self.id, target.id if target else target, self.__tmpSpellID))

	def onForcePursueOver( self, owner, target, success ):
		"""强制跟随到达"""
		self.__forceChasing = False

	def isMoving( self ):
		"""是否正在移动"""
		return self.navigator.isMoving()

	def isForceChasing( self ):
		"""是否正在强迫追踪"""
		return self.__forceChasing

	def stopMove( self ) :
		"""
		停止移动
		"""
		self.__forceChasing = False
		self.navigator.stop()
		if self.isCharging:	# 结束冲锋
			self.onChargeOver()

	def onChargeOver( self ):
		"""
		冲锋结束
		"""
		self.isCharging = False
		self.updateChaseSpeed()		# 更新速度
		self.resumeHeartBeat()		# 冲锋结束，恢复心跳
		if self.tussleMode == csdefine.PET_TUSSLE_MODE_PASSIVE:
			self.stopAttacking()

	def chaseSpeed( self ):
		"""追踪速度"""
		if self.isAttacking():
			return self.move_speed
		else:
			return BigWorld.player().move_speed * 1.2

	def updateChaseSpeed( self ):
		"""更新追踪速度"""
		if self.isCharging: return	# 正在冲锋
		self.navigator.updateSpeed(self.chaseSpeed())

#	# others --------------------------------------------------------
	# ---------------------------------------------------------------
	def enterWorld( self ):
		"""
		"""
		if self.ownerID == BigWorld.player().id:
			self.navigator = PetChaser( self, PetNavigator(self) )
			if self.clientControlled():
				self.resumeHeartBeat()
			else:
				self.cell.onClientReady()
			self.onWaterPosToServer( self.position )

	def leaveWorld( self ):
		"""
		"""
		self.cancelHeartBeat()
		self.cancelFollow()
		self.stopMove()

	def onControlled( self, isControlled ):
		"""
		是否由客户端控制，由引擎调用
		（已不再使用）
		"""
		INFO_MSG("Pet(%i) is controlled by client: %s"%(self.id, isControlled))
		if isControlled:
			self.initPhysics()
			self.resumeHeartBeat()
		else:
			self.cancelHeartBeat()
			self.stopMove()

	def clientControlled( self ):
		"""
		是否由客户端控制移动
		"""
		#return hasattr(self, "physics")
		return self.__clientControlled

	def onClientControlled( self, isControlled ):
		"""
		服务器通知客户端进行控制
		<Defined method>
		"""
		INFO_MSG("Pet(%i) is controlled by client: %s"%(self.id, isControlled))
		self.__clientControlled = isControlled
		if isControlled:
			self.resumeHeartBeat()
		else:
			self.cancelHeartBeat()
			self.stopMove()

	def setActionMode( self, mode ):
		"""设置行为模式，这个是客户端的行为，未理会服务
		器端是否成功设置该行为模式，这样处理的前提是一旦
		成功向服务器发送修改请求，服务器必定会满足客户端
		的请求"""
		self.onSetActionMode(mode)

	def onSetActionMode( self, mode ):
		"""行为模式改变"""
		if self.clientControlled():
			if mode == csdefine.PET_ACTION_MODE_FOLLOW :
				self.forcePursueOwner()								# 强迫宠物回到主人身边
			elif mode == csdefine.PET_ACTION_MODE_KEEPING :
				self.backToKeepPoint()

	def onSetTussleMode( self, mode ):
		"""战斗模式改变"""
		if mode == csdefine.PET_TUSSLE_MODE_PASSIVE:
			if self.clientControlled():
				if self.actionMode == csdefine.PET_ACTION_MODE_KEEPING:
					self.backToKeepPoint()
				else:
					self.forcePursueOwner()

	def onSetKeepPosition( self, position ):
		"""
		<Defined method>
		设置停留位置
		"""
		DEBUG_MSG("Pet(%i) set keep point to %s" % (self.id, position))
		self.__keepPosition = position

	def onActWordChanged( self, old ):
		"""
		行为限制标识改变
		"""
		if self.actionSign(csdefine.ACTION_FORBID_MOVE):
			self.stopMove()

#	# client move -------------------------------------------------
	def syncPositionToServer( self, pos ):
		"""向服务器同步位置"""
		self.cell.synchronisePositionFromClient(pos)

	def onWaterPosToServer( self, position ):
		"""
		作水面碰撞，刷新位置
		"""
		pos = utils.posOnGround( self.spaceID, position, default=position )
		dstPos = BigWorld.toWater( pos )
		if dstPos is not None:
			pos = dstPos
		self.syncPositionToServer( pos )
