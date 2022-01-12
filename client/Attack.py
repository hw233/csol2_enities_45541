# -*- coding: gb18030 -*-

"""
implement role's attack action.

18:10 2009-2-6 : written by wangshufeng
"""

import BigWorld
import Math
import csdefine
import csstatus
import csconst
import csstatus_msgs as StatusMsgs
from config.client.msgboxtexts import Datas as mbmsgs

from AbstractTemplates import MultiLngFuncDecorator
import skills as Skill
from skills.Spell_Item import Spell_Item
import SkillTargetObjImpl
import GUIFacade
import Const
import Define
import ResMgr
from skills.Spell_Item import Spell_Item

from bwdebug import *
from Function import Functor
from keys import *
import gbref
from gbref import rds
import event.EventCenter as ECenter
from DroppedBox import DroppedBox
from MessageBox import showMessage
from MessageBox import MB_OK_CANCEL
from MessageBox import RS_OK
from MessageBox import MB_OK
import PetEpitome
import ItemTypeEnum
from items.ItemDataList import ItemDataList
from config.client.labels import ChatFacade as lbs_ChatFacade

g_items = ItemDataList.instance()

AutoFightConfig = {	"AutoFightConfig"	:	{},
					"plusSkillTarget"		:	[],
					"autoPlusSkillList"	:	[]}		# 可供下线保存（关客户端不保存的自动战斗配置信息)
					

class languageDepart_AFEnter( MultiLngFuncDecorator ):
	"""
	多语言版本的内容区分 by 姜毅
	"""
	@staticmethod
	def locale_default( autoFight, owner ):
		"""
		简体版
		"""
		languageDepart_AFEnter.originalFunc( autoFight, owner )
		autoFight.persistentTimerID = BigWorld.callback( Const.AUTO_FIGHT_PERSISTENT_TIME, autoFight.cancel )

	@staticmethod
	def locale_big5( autoFight, owner ):
		"""
		繁体版
		"""
		languageDepart_AFEnter.originalFunc( autoFight, owner )
		if autoFight.owner.af_time_limit <= 0 and autoFight.owner.af_time_extra <= 0:
			autoFight.leave()
			autoFight.owner.statusMessage( csstatus.AUTO_FIGHT_TIME_LIMIT )
			return
		p_time = 0
		if autoFight.owner.af_time_extra > 0:
			p_time = autoFight.owner.af_time_extra
		else:
			p_time = autoFight.owner.af_time_limit
		autoFight.persistentTimerID = BigWorld.callback( p_time, autoFight.cancel )
		autoFight.owner.base.onEnterAutoFight()

class languageDepart_AFLeave( MultiLngFuncDecorator ):
	"""
	多语言版本的内容区分 by 姜毅
	"""
	@staticmethod
	def locale_big5( autoFight ):
		"""
		繁体版
		"""
		languageDepart_AFLeave.originalFunc( autoFight )
		autoFight.owner.base.onLeaveAutoFight()

class AutoRestore:
	"""
	自动恢复
	"""
	def __init__( self ):
		"""
		"""
		self.__cfgPath = ""
		sect = self.getConfigSect()
		self.hpPercent = sect.readFloat( "Role_HP" ) # 血量所剩比例低于这个值，则自动喝血
		self.mpPercent = sect.readFloat( "Role_MP" ) # 魔法值所剩比例低于此值，自动使用蓝药

	def restore( self, entity ):
		"""
		恢复entity
		"""

		# 加入玩家所在区域判断 by姜毅
		if entity.getCurrentSpaceType() in Const.SPACE_FORBIT_AUTO_DRUG: return

		try:	# 容错：除0错误
			hpPercent = float( entity.HP ) / float( entity.HP_Max )
			mpPercent = float( entity.MP ) / float( entity.MP_Max )
		except:
			return

		# 是否到补血的量，是否放置了物品，是否物品已无CD
		if hpPercent < self.hpPercent:
			entity.qb_autoRestoreHP()

		if mpPercent < self.mpPercent:
			entity.qb_autoRestoreMP()

	def setHpPercent( self, hpPercent ):
		"""
		"""
		self.hpPercent = hpPercent
		self.__cfgSect.save()

	def setMpPercent( self, mpPercent ):
		"""
		"""
		self.mpPercent = mpPercent
		self.__cfgSect.save()

	def getHpPercent( self ):
		"""
		"""
		return self.hpPercent

	def getMpPercent( self ):
		"""
		"""
		return self.mpPercent

	def getConfigSect( self ) :
		"""
		获取自动补血、补蓝的配置
		"""
		if self.__cfgPath != "" :
			ResMgr.purge( self.__cfgPath )
		accountName = rds.gameMgr.getCurrAccountInfo()["accountName"]
		roleName = rds.gameMgr.getCurrRoleHexName()
		self.__cfgPath = "account/%s/%s/auto_fight.xml" % ( accountName, roleName )
		self.__cfgSect = ResMgr.openSection( self.__cfgPath )
		if self.__cfgSect is None :
			self.__cfgSect = ResMgr.openSection( self.__cfgPath, True )
			self.__cfgSect.createSection( "Role_HP" )
			self.__cfgSect.createSection( "Role_MP" )
			self.__cfgSect.createSection( "Pet_HP" )
			self.__cfgSect.createSection( "Pet_MP" )
			self.__cfgSect.createSection( "isAutoConjure" )
			self.__cfgSect.createSection( "isAutoAddJoy" )
			self.__cfgSect.createSection( "isAutoPlus" )
			self.__cfgSect.createSection( "radius" )
			self.__cfgSect.createSection( "radiusAdd" )
			self.__cfgSect.createSection( "joyLess" )
			self.__cfgSect.createSection( "autoRepair" )
			self.__cfgSect.createSection( "autoReboin" )
			self.__cfgSect.createSection( "repairRate" )
			self.__cfgSect.createSection( "isAutoPickUp" )
			self.__cfgSect.createSection( "plusSkillTarget" )
			self.__cfgSect.createSection( "plusSkills" )
			self.__cfgSect.createSection( "isIgnorePickUp" )
			self.__cfgSect.createSection( "pickUpTypeList" )
			self.__cfgSect.createSection( "ignoredList" )
			self.__cfgSect.writeFloat( "Role_HP", 0.6 )
			self.__cfgSect.writeFloat( "Role_MP", 0.6 )
			self.__cfgSect.writeFloat( "Pet_HP", 0.6 )
			self.__cfgSect.writeFloat( "Pet_MP", 0.6 )
			self.__cfgSect.writeBool( "isAutoConjure", 0 )
			self.__cfgSect.writeBool( "isAutoAddJoy", 0 )
			self.__cfgSect.writeBool( "isAutoPlus", 0 )
			self.__cfgSect.writeInt( "radius", 0 )
			self.__cfgSect.writeInt( "radiusAdd", 15 )
			self.__cfgSect.writeInt( "joyLess", 0 )
			self.__cfgSect.writeBool( "autoRepair", 0 )
			self.__cfgSect.writeBool( "autoReboin", 0 )
			self.__cfgSect.writeInt( "repairRate", 0 )
			self.__cfgSect.writeBool( "isAutoPickUp", 0 )
			self.__cfgSect.writeVector3( "plusSkillTarget", (0, 0, 0) )
			self.__cfgSect.writeBool( "isIgnorePickUp", 1 )
			self.__cfgSect.writeString( "pickUpTypeList", "" )
			self.__cfgSect.writeString( "ignoredList", "" )
			self.__cfgSect.save()
		return self.__cfgSect
	
	def saveCfgSect( self ):
		"""
		保存配置
		"""
		self.__cfgSect.save()

class PetAutoRestore( AutoRestore ):
	"""
	宠物自动恢复
	"""
	def __init__( self ):
		"""
		"""
		AutoRestore.__init__( self )
		sect = AutoRestore().getConfigSect()
		self.hpPercent = sect.readFloat( "Pet_HP" )		# 血量所剩比例低于这个值，则自动喝血
		self.mpPercent = sect.readFloat( "Pet_MP" )		# 魔法值所剩比例低于此值，自动使用蓝药

	def restore( self, entity ):
		"""
		检测entity是否可以恢复

		@param entity : 宠物entity
		"""
		try:	# 容错：除0错误
			hpPercent = float( entity.HP ) / float( entity.HP_Max )
			mpPercent = float( entity.MP ) / float( entity.MP_Max )
		except:
			return
		player = BigWorld.player()
		if hpPercent < self.hpPercent:
			player.qb_autoRestorePetHP()

		if mpPercent < self.mpPercent:
			player.qb_autoRestorePetMP()


class AttackArgumentFactory:
	"""
	攻击状态参数封装工厂
	"""
	def __init__( self ):
		"""
		"""
		pass

	@staticmethod
	def getAttackArgument( state, arg ):
		"""
		"""
		if state == Const.ATTACK_STATE_ONCE:
			attackArgument = OnceAttackArg( state, arg )
		elif state == Const.ATTACK_STATE_AUTO_CONFIRM_SPELL:
			attackArgument = AttackConfirmSpellArg( state, arg )
		elif state == Const.ATTACK_STATE_AUTO_SPELL_CURSOR:
			attackArgument = AttackConfirmSpellArg( state, arg )
		elif state == Const.ATTACK_STATE_SPELL_AND_HOMING:
			attackArgument = AttackHomingSpellArg( state, arg )
		else:
			attackArgument = None

		return attackArgument


class OnceAttackArg:
	"""
	ATTACK_STATE_ONCE状态运行参数封装实例
	"""
	def __init__( self, state, arg ):
		"""
		@param state :	攻击状态
		@param arg :	进入此攻击状态需要的参数
		"""
		self.param = arg[ 0 ]


class AttackConfirmSpellArg:
	"""
	ATTACK_STATE_AUTO_CONFIRM_SPELL状态运行参数封装实例
	"""
	def __init__( self, state, arg ):
		"""
		@param state :	攻击状态
		@param arg :	进入此攻击状态需要的参数
		"""
		self.param = arg[ 0 ]

class AttackHomingSpellArg:
	"""
	ATTACK_STATE_HOMING_SPELL状态运行参数封装实例
	"""
	def __init__( self, state, arg ):
		"""
		@param state :	攻击状态
		@param arg :	进入此攻击状态需要的参数
		"""
		self.param = arg[ 0 ]

class AutoFightArg:
	"""
	ATTACK_STATE_AUTO_FIGHT状态运行参数封装实例
	"""
	def __init__( self, state, arg ):
		"""
		@param state :	攻击状态
		@param arg :	进入此攻击状态需要的参数
		"""
		self.param = None


class AttackBase:
	"""
	攻击实例基类
	"""
	def __init__( self, owner ):
		"""
		@param owner : 此实例的所有者，目前只会是角色。
		"""
		self.owner = owner

	def enter( self, attackArgument ):
		"""
		进入此状态后的初始化
		@param arg : 外部参数。
		"""
		pass

	def leave( self ):
		"""
		离开此状态时的清理工作
		"""
		pass

	def action( self ):
		"""
		进入此状态应该执行的行为
		"""
		pass

	def actionEnd( self ):
		"""
		行为执行结束后，接着……
		"""
		pass

	def canChangeState( self, oldState, attackArgument ):
		"""
		检查是否能进入该状态

		@param oldState : 转换过来的状态
		@type oldState : UINT8
		@param attackArgument : 封装参数
		@type attackArgument : see AttackArgumentFactory
		"""
		if BigWorld.player().isFollowing():	# 跟随状态不允许进入战斗
			return False
		return True

	def interruptAttack( self, reason ):
		"""
		打断攻击行为
		"""
		pass

	def onStateChanged( self, oldState, newState ):
		"""
		玩家的战斗状态改变
		"""
		if oldState == csdefine.ENTITY_STATE_FIGHT and newState != csdefine.ENTITY_STATE_FIGHT:
			self.owner.cancelAttackState()

	def onItemDrop( self, dropEntity ):
		"""
		有物品掉落
		"""
		pass

	def onReceiveSpell( self, casterID ):
		"""
		受到伤害

		@param casterID : 发出伤害的entity id
		"""
		pass

	def onSpellInterrupted( self, skillID, reason ):
		"""
		服务器打断释放技能
		"""
		pass


class NoAttack( AttackBase ):
	"""
	无攻击状态
	"""
	def __init__( self, owner ):
		"""
		"""
		AttackBase.__init__( self, owner )
		self.state = Const.ATTACK_STATE_NONE

	def canChangeState( self, oldState, attackArgument ):
		"""
		检查是否能进入该状态

		@param oldState : 转换过来的状态
		@type oldState : UINT8
		@param attackArgument : 封装参数
		@type attackArgument : see AttackArgumentFactory
		"""
		if self.owner.state == csdefine.ENTITY_STATE_DEAD: return False
		return True

	def enter( self, attackArgument ) :
		"""
		取消攻击状态
		"""
		self.owner.hideSpellingItemCover()

	def interruptAttack( self, reason ):
		"""
		如果玩家将要
		"""
		if self.owner.isChange2AutoSpell():
			self.owner.cancelAutoFight2AutoSpellTimer()

	def onReceiveSpell( self, casterID ):
		"""
		受到伤害

		@param casterID : 发出伤害的entity id
		"""
		enemyEntity = BigWorld.entities.get( casterID )
		if enemyEntity is None:
			return

		if self.owner.isMoving():
			return

		# fightControl和counter定义在entities\common\config\client\viewinfosetting.xml中，玩家是否自动反击的设置
		if rds.viewInfoMgr.getSetting( "fightControl", "counter" ):
			rds.targetMgr.bindTarget( enemyEntity )
			self.owner.changeAttackState( Const.ATTACK_STATE_NORMAL )

class OnceAttack( AttackBase ):
	"""
	使用技能攻击一次
	"""
	def __init__( self, owner ):
		"""
		"""
		AttackBase.__init__( self, owner )
		self.state = Const.ATTACK_STATE_ONCE
		self.skillID = 0

	def enter( self, attackArgument ):
		"""
		"""
		self.skillID = attackArgument.param
		self.action()

	def leave( self ):
		"""
		"""
		pass

	def canChangeState( self, oldState, attackArgument ):
		"""
		检查是否能进入该状态

		@param oldState : 转换过来的状态
		@type oldState : UINT8
		@param attackArgument : 封装参数
		@type attackArgument : see AttackArgumentFactory
		"""
		# 自动战斗状态下，不能进入该状态
		if oldState == Const.ATTACK_STATE_AUTO_FIGHT: return False
		# 玩家当前在吟唱，不能进入该状态。
		if self.owner.intonating(): return False
		# 指定技能不允许释放，不能进入该状态。
		skillID = attackArgument.param
		if hasattr( self.owner, "isInHomingSpell" ) and self.owner.isInHomingSpell and skillID / 1000 not in Const.HOMING_SPELL_CAN_USE_SKILL_LIST:return False
		skillInstance = Skill.getSkill( skillID )
		if not skillInstance.isCooldown( self.owner ) :
			self.owner.statusMessage( csstatus.SKILL_NOT_READY )
			self.owner.showInvalidItemCover( skillID )
			return False
		return AttackBase.canChangeState( self, oldState, attackArgument )

	def action( self ):
		"""
		"""
		self.owner.autoRestore()
		self.spellSkill()
		
	def actionEnd( self ):
		"""
		"""
		self.owner.cancelAttackState()

	def spellSkill( self ):
		"""
		释放技能攻击

		使用指定技能攻击目标：
		如果距离太远，那么接近到合法距离后攻击目标；
		如果满足条件，那么攻击目标；
		否则，退出此状态。
		"""
		skillInstance = Skill.getSkill( self.skillID )
		target = skillInstance.getCastObject().convertCastObject( self.owner, self.owner.targetEntity )	# 这个技能有可能只能对自己释放
		
		if target is None:
			self.owner.statusMessage( csstatus.SKILL_NO_TARGET )
			self.owner.cancelAttackState()
			return
		
		spellTarget = SkillTargetObjImpl.createTargetObjEntity( target )
		if skillInstance.getCastObjectType() == csdefine.SKILL_CAST_OBJECT_TYPE_NONE:
			skillInstance.spell( self.owner, spellTarget )
			self.actionEnd()
			return

		# 策划要求对一个目标判断是合法之后才允许向 距离过远的目标靠近 否则告之不可攻击相关信息
		state = skillInstance.useableCheck( self.owner, spellTarget )
		if state != csstatus.SKILL_GO_ON:
			if state != csstatus.SKILL_TOO_FAR:
				self.owner.showInvalidItemCover( self.skillID )
				if state is not None:
					self.owner.statusMessage( state )
				self.owner.cancelAttackState()
			else:	# 如果是距离太远，接近后攻击
				self.owner.showSpellingItemCover( self.skillID )
				spellRange = skillInstance.getRangeMax( self.owner )
				self.owner.pursueEntity( target, spellRange, self.pursueAttack )
		else:
			if self.owner.isMoving() and self.owner.isInSpellRange( target, skillInstance ):	# 原来的版本中停止移动0.1秒后再攻击
				self.owner.stopMove()
			skillInstance.spell( self.owner, spellTarget )
			self.actionEnd()

	def pursueAttack( self, owner, targetEntity, success ):
		"""
		追踪目标的回调
		"""
		if self.owner.attackState != self.state:
			return

		if targetEntity is None:
			owner.cancelAttackState()
			return

		if BigWorld.player().targetEntity != targetEntity :
			owner.cancelAttackState()
			return

		if not success:
			owner.cancelAttackState()
			return

		self.spellSkill()

	def onStateChanged( self, oldState, newState ):
		"""
		玩家的战斗状态改变
		"""
		if newState != csdefine.ENTITY_STATE_FIGHT:
			self.owner.cancelAttackState()

	def interruptAttack( self, reason ):
		"""
		攻击被打断，此状态攻击被打断则推出此状态
		"""
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		if self.owner.isPursueState( ) or ( self.owner.vehicle and self.owner.vehicle.isPursueState() ):
			return
		self.owner.cancelAttackState()

class AutoNormalAttack( AttackBase ):
	"""
	连续的普通物理攻击，例如：鼠标左键攻击目标
	"""
	def __init__( self, owner ):
		"""
		"""
		AttackBase.__init__( self, owner )
		self.state = Const.ATTACK_STATE_NORMAL
		self.timerID = 0

	def enter( self, attackArgument ):
		"""
		进入此状态后的初始化
		"""
		self.action()

	def action( self ):
		"""
		此状态行为开始
		"""
		self.owner.autoRestore()
		self.spellSkill()

	def leave( self ):
		"""
		离开此状态时的清理工作
		"""
		BigWorld.cancelCallback( self.timerID )

	def spellSkill( self ):
		"""
		释放技能攻击
		"""
		skillID = self.owner.getNormalAttackSkillID() 
		target = self.owner.targetEntity
		skillInstance = Skill.getSkill( skillID )

		if target is None:
			self.owner.statusMessage( csstatus.SKILL_NO_TARGET )
			self.owner.cancelAttackState()
			return

		# 策划要求对一个目标判断是合法之后才允许向 距离过远的目标靠近 否则告之不可攻击相关信息
		spellTarget = SkillTargetObjImpl.createTargetObjEntity( target )
		state = skillInstance.useableCheck( self.owner, spellTarget )
		# 恶性技能才进入pk提示判断
		if skillInstance.isMalignant():
			pkMessage = self.owner.pkStateMessage()
			if pkMessage is not None:
				self.owner.statusMessage( pkMessage )
		if state != csstatus.SKILL_GO_ON:
			if state != csstatus.SKILL_TOO_FAR:
				self.owner.showInvalidItemCover( skillID )
				if state is not None :
					self.owner.statusMessage( state )		# out put error message to system information panel( in RoleChat.py )
				self.owner.cancelAttackState()
			else:	# 如果是距离太远，接近后攻击
				spellRange = skillInstance.getRangeMax( self.owner )
				self.owner.pursueEntity( target, spellRange, self.pursueAttack )
		else:
			if self.owner.isMoving() and self.owner.isInSpellRange( target, skillInstance ):	# 原来的版本中停止移动0.1秒后再攻击
				self.owner.stopMove()
				DEBUG_MSG( "---------->>>stopMove" )
			skillInstance.spell( self.owner, spellTarget )
			self.actionEnd()

	def actionEnd( self ):
		"""
		成功执行一个行为后的处理，如果不成功，那么中途肯定退出了这个状态。
		"""
		if self.owner.pkStateMessage() is not None:
			return
		self.timerID = BigWorld.callback( self.owner.hit_speed + Const.AUTO_ATTACK_DELAY_AMEND, self.action )	# 重复这个行为的回调时间应该和攻击速度一致

	def interruptAttack( self, reason ):
		"""
		攻击被打断，此状态攻击被打断则推出此状态
		"""
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		if self.owner.isPursueState( ) or ( self.owner.vehicle and self.owner.vehicle.isPursueState() ):
			return
		self.owner.cancelAttackState()

	def pursueAttack( self, owner, targetEntity, success ):
		"""
		追踪目标的回调
		"""
		if self.owner.attackState != self.state:
			return
		if targetEntity is None:
			owner.cancelAttackState()	# 这个函数在被调用时玩家可能已经是默认攻击状态
			return
		if BigWorld.player().targetEntity != targetEntity :
			owner.cancelAttackState()
			return
		if not success:
			owner.cancelAttackState()
			return
		self.spellSkill()

	def canChangeState( self, oldState, attackArgument ):
		"""
		检查是否能进入该状态

		@param oldState : 转换过来的状态
		@type oldState : UINT8
		@param attackArgument : 封装参数
		@type attackArgument : see AttackArgumentFactory
		"""
		# 自动战斗状态下，不能进入该状态
		if oldState == Const.ATTACK_STATE_AUTO_FIGHT: return
		# 玩家当前在吟唱，不能进入该状态。
		if self.owner.intonating(): return False
		# 指定技能不允许释放，不能进入该状态。
		skillID = 0
		if attackArgument:
			skillID = attackArgument.param
		if hasattr( self.owner, "isInHomingSpell" ) and self.owner.isInHomingSpell and skillID / 1000 not in Const.HOMING_SPELL_CAN_USE_SKILL_LIST:return False
		return AttackBase.canChangeState( self, oldState, attackArgument )

	def onStateChanged( self, oldState, newState ):
		"""
		玩家的战斗状态改变
		"""
		if newState != csdefine.ENTITY_STATE_FIGHT:
			self.owner.cancelAttackState()

	def onSpellInterrupted( self, skillID, reason ):
		"""
		服务器打断释放技能
		"""
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		self.owner.cancelAttackState()


class AutoConfirmSpellAttack( AttackBase ):
	"""
	自动使用指定的技能攻击，指定的技能只使用一次，使用后接着使用普通物理攻击
	"""
	def __init__( self, owner ):
		"""
		"""
		AttackBase.__init__( self, owner )
		self.state = Const.ATTACK_STATE_AUTO_CONFIRM_SPELL
		self.timerID = 0
		self.skillID = 0
		self.skillHasUsed = False					# 指定技能是否被使用过

	def enter( self, attackArgument ):
		"""
		进入此状态后的初始化
		"""
		self.skillID = attackArgument.param		# 使用指定的技能
		self.action()

	def leave( self ):
		"""
		离开此状态时的清理工作
		"""
		self.skillID = 0
		self.skillHasUsed = False
		BigWorld.cancelCallback( self.timerID )

	def interruptAttack( self, reason ):
		"""
		攻击被打断，此状态攻击被打断则推出此状态
		"""
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		if self.owner.isPursueState( ) or ( self.owner.vehicle and self.owner.vehicle.isPursueState() ):
			return
		self.owner.cancelAttackState()

	def action( self ):
		"""
		此状态行为开始
		"""
		self.owner.autoRestore()
		if not self.canAction():
			self.timerID = BigWorld.callback( self.owner.hit_speed + Const.AUTO_ATTACK_DELAY_AMEND, self.action )	# 重复这个行为的回调时间应该和攻击速度一致
			return
		self.spellSkill()

	def canAction( self ):
		"""
		是否能开始行为
		"""
		if self.owner.intonating():
			return False
		if hasattr( self.owner, "isInHomingSpell" ) and self.owner.isInHomingSpell:return False
		return True

	def getSkillID( self ):
		"""
		获得使用技能
		"""
		if self.skillHasUsed:
			return self.owner.getNormalAttackSkillID()
		return self.skillID

	def spellSkill( self ):
		"""
		释放技能攻击

		使用指定技能攻击目标一次后，使用普通物理技能攻击目标，
		13:44 2009-5-31修改：如果技能冷却中，则本次攻击不成功；
		如果魔法不足，那么使用普通攻击目标；
		如果目标不在普通物理技能攻击范围内则callback检测；
		如果满足条件，那么攻击目标；
		否则，退出此状态。
		"""
		target = self.owner.targetEntity
		skillInstance = Skill.getSkill( self.getSkillID() )
		target = skillInstance.getCastObject().convertCastObject( self.owner, target )

		if target is None:
			self.owner.statusMessage( csstatus.SKILL_NO_TARGET )
			self.owner.cancelAttackState()
			return
		# 策划要求对一个目标判断是合法之后才允许向 距离过远的目标靠近 否则告之不可攻击相关信息
		spellTarget = SkillTargetObjImpl.createTargetObjEntity( target )
		state = skillInstance.useableCheck( self.owner, spellTarget )
		# 恶性技能才进入pk提示判断
		if skillInstance.isMalignant():
			pkMessage = self.owner.pkStateMessage()
			if pkMessage is not None:
				self.owner.statusMessage( pkMessage )
		if state != csstatus.SKILL_GO_ON:
			if state == csstatus.SKILL_OUTOF_MANA:	# 使用普通攻击技能攻击
				self.owner.showInvalidItemCover( self.skillID )
				skillInstance = Skill.getSkill( self.owner.getNormalAttackSkillID() )
				state2 = skillInstance.useableCheck( self.owner, spellTarget )
				if state2 == csstatus.SKILL_GO_ON:
					skillInstance.spell( self.owner, spellTarget )
					self.actionEnd()
				elif state2 == csstatus.SKILL_TOO_FAR:
					spellRange = skillInstance.getRangeMax( self.owner )
					self.owner.pursueEntity( target, spellRange, self.pursueAttack )
				else:
					if state is not None :
						self.owner.statusMessage( state )
					self.owner.cancelAttackState()
			elif state != csstatus.SKILL_TOO_FAR:
				if not self.skillHasUsed:	#为了解决普通攻击技能和当前技能的公共CD问题add by wuxo 2011-12-12
					self.owner.showInvalidItemCover( self.skillID )
					if state is not None:
						self.owner.statusMessage( state )
					self.owner.cancelAttackState()
				else:
					self.actionEnd()
			else:	# 如果是距离太远，接近后攻击
				if not self.skillHasUsed:
					self.owner.showSpellingItemCover( self.skillID )
					spellRange = skillInstance.getRangeMax( self.owner )
					self.owner.pursueEntity( target, spellRange, self.pursueAttack )
				else:
					self.actionEnd()
		else:
			if self.owner.isMoving() and self.owner.isInSpellRange( target, skillInstance ):	# 原来的版本中停止移动0.1秒后再攻击
				self.owner.stopMove()
			skillInstance.spell( self.owner, spellTarget )
			if not self.skillHasUsed:
				self.skillHasUsed = True					# 指定技能已经使用过了
				if not skillInstance.isMalignant() and ( self.owner.state != csdefine.ENTITY_STATE_FIGHT ):
					self.owner.cancelAttackState()
					return
			self.actionEnd()

	def actionEnd( self ):
		"""
		成功执行一个行为后的处理，如果不成功，那么中途肯定退出了这个状态。
		"""
		if self.owner.pkStateMessage() is not None:
			return
		self.timerID = BigWorld.callback( self.owner.hit_speed + Const.AUTO_ATTACK_DELAY_AMEND, self.action )	# 重复这个行为的回调时间应该和攻击速度一致

	def pursueAttack( self, owner, targetEntity, success ):
		"""
		追踪目标的回调
		"""
		if self.owner.attackState != self.state:
			return

		if targetEntity is None:
			owner.cancelAttackState()
			return

		if BigWorld.player().targetEntity != targetEntity :
			owner.cancelAttackState()
			return

		if not success:
			owner.cancelAttackState()
			return
		self.spellSkill()

	def canChangeState( self, oldState, attackArgument ):
		"""
		检查是否能进入该状态

		@param oldState : 转换过来的状态
		@type oldState : UINT8
		@param attackArgument : 封装参数
		@type attackArgument : see AttackArgumentFactory
		"""
		# 自动战斗状态下，不能进入该状态
		if oldState == Const.ATTACK_STATE_AUTO_FIGHT: return False
		# 玩家当前在吟唱，不能进入该状态。
		if self.owner.intonating(): return False
		# 指定技能不允许释放，不能进入该状态。
		skillID = attackArgument.param
		skillInstance = Skill.getSkill( skillID )
		if not skillInstance.isCooldown( self.owner ) :
			self.owner.statusMessage( csstatus.SKILL_NOT_READY )
			self.owner.showInvalidItemCover( skillID )
			return False
		return AttackBase.canChangeState( self, oldState, attackArgument )

	def onStateChanged( self, oldState, newState ):
		"""
		玩家的战斗状态改变
		"""
		if newState != csdefine.ENTITY_STATE_FIGHT:
			self.owner.cancelAttackState()

	def onSpellInterrupted( self, skillID, reason ):
		"""
		服务器打断释放技能
		"""
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		self.owner.cancelAttackState()

class AutoConfirmSpellAttackCursor( AttackBase ):
	"""
	自动使用指定的技能攻击，指定的技能只使用一次，使用后接着使用普通物理攻击
	"""
	def __init__( self, owner ):
		"""
		"""
		AttackBase.__init__( self, owner )
		self.state = Const.ATTACK_STATE_AUTO_SPELL_CURSOR
		self.timerID = 0
		self.skillID = 0
		self.attPos = Math.Vector3( (0, 0, 0) )
		self.skillHasUsed = False					# 指定技能是否被使用过
		
	def enter( self, attackArgument ):
		"""
		进入此状态后的初始化
		"""
		self.owner.stopMove()					# 停止移动，有可能在自动寻路中
		self.skillID = attackArgument.param		# 使用指定的技能
		cursorDropPoint = gbref.cursorToDropPoint()
		if cursorDropPoint:
			self.attPos = Math.Vector3( cursorDropPoint )
		self.action()

	def leave( self ):
		"""
		离开此状态时的清理工作
		"""
		self.skillID = 0
		self.skillHasUsed = False
		self.attPos = Math.Vector3( (0, 0, 0) )
		BigWorld.cancelCallback( self.timerID )

	def action( self ):
		"""
		此状态行为开始
		"""
		self.owner.autoRestore()
		if not self.canAction():
			self.timerID = BigWorld.callback( self.owner.hit_speed + Const.AUTO_ATTACK_DELAY_AMEND, self.action )	# 重复这个行为的回调时间应该和攻击速度一致
			return
		self.spellSkill()

	def actionEnd( self ):
		"""
		行为执行结束后，接着……
		"""
		if self.owner.pkStateMessage() is not None:
			return
		self.timerID = BigWorld.callback( self.owner.hit_speed + Const.AUTO_ATTACK_DELAY_AMEND, self.action )	# 重复这个行为的回调时间应该和攻击速度一致
	
	def canAction( self ):
		"""
		是否能开始行为
		"""
		if self.owner.intonating():
			return False
		if hasattr( self.owner, "isInHomingSpell" ) and self.owner.isInHomingSpell:return False
		return True
		
	def getSkillID( self ):
		"""
		获得使用技能
		"""
		if self.skillHasUsed:
			return self.owner.getNormalAttackSkillID()
		return self.skillID

	def canChangeState( self, oldState, attackArgument ):
		"""
		检查是否能进入该状态

		@param oldState : 转换过来的状态
		@type oldState : UINT8
		@param attackArgument : 封装参数
		@type attackArgument : see AttackArgumentFactory
		"""
		# 自动战斗状态下，不能进入该状态
		if oldState == Const.ATTACK_STATE_AUTO_FIGHT: return False
		# 玩家当前在吟唱，不能进入该状态。
		if self.owner.intonating(): return False
		# 指定技能不允许释放，不能进入该状态。
		skillID = attackArgument.param
		skillInstance = Skill.getSkill( skillID )
		if not skillInstance.isCooldown( self.owner ) :
			self.owner.statusMessage( csstatus.SKILL_NOT_READY )
			self.owner.showInvalidItemCover( skillID )
			return False
		return AttackBase.canChangeState( self, oldState, attackArgument )
	
	def onStateChanged( self, oldState, newState ):
		"""
		玩家的战斗状态改变
		"""
		if newState != csdefine.ENTITY_STATE_FIGHT:
			self.owner.cancelAttackState()

	def onSpellInterrupted( self, skillID, reason ):
		"""
		服务器打断释放技能
		"""
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		self.owner.cancelAttackState()
		
	def spellSkill( self ):
		"""
		释放技能攻击

		使用指定技能攻击目标一次后，使用普通物理技能攻击目标，
		13:44 2009-5-31修改：如果技能冷却中，则本次攻击不成功；
		如果魔法不足，那么使用普通攻击目标；
		如果目标不在普通物理技能攻击范围内则callback检测；
		如果满足条件，那么攻击目标；
		否则，退出此状态。
		"""
		if self.getSkillID() == 0 or self.getSkillID() == None:
			return
			
		skillInstance = Skill.getSkill( self.getSkillID() )
		cursorPos = self.attPos

		spellTarget = SkillTargetObjImpl.createTargetObjPosition( cursorPos )
		state = skillInstance.useableCheck( self.owner, spellTarget )
		# 恶性技能才进入pk提示判断
		if skillInstance.isMalignant():
			pkMessage = self.owner.pkStateMessage()
			if pkMessage is not None:
				self.owner.statusMessage( pkMessage )
		if state != csstatus.SKILL_GO_ON:
			if state == csstatus.SKILL_TOO_FAR:
				if not self.skillHasUsed:
					import math
					self.owner.showSpellingItemCover( self.skillID )
					spellRange = skillInstance.getRangeMax( self.owner )
					self.owner.pursuePosition( cursorPos, spellRange, self.onPursuePositionAttack )
				else:
					self.actionEnd()
			elif state == csstatus.SKILL_CANT_DIRECTION_ERR:
				matrix = Math.Matrix()
				matrix.setTranslate( cursorPos )
				self.owner.turnaround( matrix, self.onTurnaroundAttack )
			elif state == csstatus.SKILL_CANT_ARRIVAL:
				self.owner.statusMessage( csstatus.SKILL_CANT_ARRIVAL )
		else:
			if self.owner.isMoving() and self.owner.isInSpellDis( cursorPos, skillInstance ):	# 原来的版本中停止移动0.1秒后再攻击
				self.owner.stopMove()
			
			skillInstance.spell( self.owner, spellTarget )
			if not self.skillHasUsed:
				self.skillHasUsed = True					# 指定技能已经使用过了
				if not skillInstance.isMalignant() and ( self.owner.state != csdefine.ENTITY_STATE_FIGHT ):
					self.owner.cancelAttackState()
					return
			self.actionEnd()
	
	def onTurnaroundAttack( self, success):
		if not success and self.owner:
			self.owner.cancelAttackState()
			return
		
		self.spellSkill()
		
	def onPursuePositionAttack( self, owner, targetPos, success ):
		if not success and self.owner:
			self.owner.cancelAttackState()
			return
		
		self.spellSkill()

class AutoHomingSpellAttack( AttackBase ):
	"""
	自动使用引导技能攻击
	"""
	def __init__( self, owner ):
		"""
		"""
		AttackBase.__init__( self, owner )
		self.state = Const.ATTACK_STATE_HOMING_SPELL
		self.timerID = 0

	def enter( self, attackArgument ):
		"""
		进入此状态后的初始化
		@param arg : 外部参数。
		"""
		self.owner.autoRestore()
		self.tryUseSkill()

	def leave( self ):
		"""
		离开此状态时的清理工作
		"""
		BigWorld.cancelCallback( self.timerID )
		self.timerID = 0

	def canAction( self ):
		"""
		"""
		if self.owner.intonating(): return False
		if self.owner.isInHomingSpell: return False
		skillID = self.owner.getLastUseAutoSkillID()
		skillInstance = Skill.getSkill( skillID )
		if hasattr( self.owner, "isInHomingSpell" ) and self.owner.isInHomingSpell:return False
		if not skillInstance.isCooldown( self.owner ):return False
		return True

	def action( self ):
		if self.canAction():
			self.tryUseSkill()
		else:
			self.actionEnd()

	def tryUseSkill( self ):

		skillID = self.owner.getLastUseAutoSkillID()
		skillInstance = Skill.getSkill( skillID )
		target = self.owner.targetEntity
		target = skillInstance.getCastObject().convertCastObject( self.owner, target )
		if target is None:
			self.owner.cancelAttackState()
			return

		# 策划要求对一个目标判断是合法之后才允许向 距离过远的目标靠近 否则告之不可攻击相关信息
		spellTarget = SkillTargetObjImpl.createTargetObjEntity( target )
		state = skillInstance.useableCheck( self.owner, spellTarget )
		# 恶性技能才进入pk提示判断
		if skillInstance.isMalignant():
			pkMessage = self.owner.pkStateMessage()
			if pkMessage is not None:
				self.owner.statusMessage( pkMessage )
		if state == csstatus.SKILL_GO_ON:
			if self.owner.isMoving() and self.owner.isInSpellRange( target, skillInstance ):
				self.owner.stopMove()
			skillInstance.spell( self.owner, spellTarget )
			self.actionEnd()
		elif state == csstatus.SKILL_TOO_FAR:
			self.owner.showSpellingItemCover( skillID )
			spellRange = skillInstance.getRangeMax( self.owner )
			self.owner.pursueEntity( target, spellRange, self.pursueAttack )
		elif state == csstatus.SKILL_OUTOF_MANA:
			self.owner.showInvalidItemCover( skillID )
			self.owner.cancelAttackState()
		else:
			self.owner.showInvalidItemCover( skillID )
			if state is not None:
				self.owner.statusMessage( state )
			self.actionEnd()

	def actionEnd( self ):
		"""
		"""
		if self.owner.pkStateMessage() is not None:
			return
		self.timerID = BigWorld.callback( self.owner.hit_speed + Const.AUTO_ATTACK_DELAY_AMEND, self.action )

	def pursueAttack( self, owner, targetEntity, success ):
		"""
		追踪目标的回调
		"""
		if self.owner.attackState != self.state:
			return

		if targetEntity is None:
			owner.cancelAttackState()
			return

		if BigWorld.player().targetEntity != targetEntity :
			owner.cancelAttackState()
			return

		if not success:
			owner.cancelAttackState()
			return

		self.tryUseSkill()

	def canChangeState( self, oldState, attackArgument ):
		"""
		检查是否能进入该状态

		@param oldState : 转换过来的状态
		@type oldState : UINT8
		@param attackArgument : 封装参数
		@type attackArgument : see AttackArgumentFactory
		"""
		# 自动战斗状态下，不能进入该状态
		if oldState == Const.ATTACK_STATE_AUTO_FIGHT: return
		if oldState == self.state:return False
		return AttackBase.canChangeState( self, oldState, attackArgument )

	def interruptAttack( self, reason ):
		"""
		攻击被打断，此状态攻击被打断则推出此状态
		"""
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		if self.owner.isPursueState() or ( self.owner.vehicle and self.owner.vehicle.isPursueState() ):
			return
		self.owner.cancelAttackState()

	def onSpellInterrupted( self, skillID, reason ):
		"""
		服务器打断释放技能
		"""
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		self.owner.cancelAttackState()

	def onStateChanged( self, oldState, newState ):
		"""
		玩家的战斗状态改变
		"""
		if newState != csdefine.ENTITY_STATE_FIGHT:
			self.owner.cancelAttackState()

class SpellAutoHomingAttack( AttackBase ):
	"""
	使用非普通攻击技能攻击一次后再用引导技能攻击
	"""
	def __init__( self, owner ):
		"""
		"""
		AttackBase.__init__( self, owner )
		self.state = Const.ATTACK_STATE_SPELL_AND_HOMING
		self.skillID = 0
		self.timerID = 0
		self.isSkillUse = False

	def enter( self, attackArgument ):
		"""
		进入此状态后的初始化
		@param arg : 外部参数。
		"""
		self.owner.autoRestore()
		self.skillID = attackArgument.param
		self.tryUseSkill()

	def leave( self ):
		"""
		离开此状态时的清理工作
		"""
		BigWorld.cancelCallback( self.timerID )
		self.timerID = 0
		self.isSkillUse = False
		self.skillID = 0

	def getSkillID( self ):
		"""
		"""
		if self.isSkillUse: return self.owner.getLastUseAutoSkillID()
		return self.skillID

	def canAction( self ):
		"""
		是否能开始行为
		"""
		if self.owner.intonating(): return False
		if self.owner.isInHomingSpell: return False
		return True

	def action( self ):
		"""
		"""
		if not self.canAction():
			self.timerID = BigWorld.callback( self.owner.hit_speed + Const.AUTO_ATTACK_DELAY_AMEND, self.action )	# 重复这个行为的回调时间应该和攻击速度一致
			return
		self.tryUseSkill()

	def tryUseSkill( self ):
		"""
		尝试使用技能
		"""
		skillID = self.getSkillID()
		skillInstance = Skill.getSkill( skillID )
		target = self.owner.targetEntity
		target = skillInstance.getCastObject().convertCastObject( self.owner, target )
		if target is None:
			self.owner.statusMessage( csstatus.SKILL_NO_TARGET )
			self.owner.cancelAttackState()
			return
		# 策划要求对一个目标判断是合法之后才允许向 距离过远的目标靠近 否则告之不可攻击相关信息
		spellTarget = SkillTargetObjImpl.createTargetObjEntity( target )
		state = skillInstance.useableCheck( self.owner, spellTarget )
		# 恶性技能才进入pk提示判断
		if skillInstance.isMalignant():
			pkMessage = self.owner.pkStateMessage()
			if pkMessage is not None:
				self.owner.statusMessage( pkMessage )

		if state == csstatus.SKILL_GO_ON:
			if self.owner.isMoving() and self.owner.isInSpellRange( target, skillInstance ):
				self.owner.stopMove()
			skillInstance.spell( self.owner, spellTarget )
			if not self.isSkillUse:
				self.isSkillUse = True
				if not skillInstance.isMalignant() and ( self.owner.state != csdefine.ENTITY_STATE_FIGHT ):
					self.owner.cancelAttackState()
					return
			self.actionEnd()
		elif state == csstatus.SKILL_TOO_FAR:
			self.owner.showSpellingItemCover( skillID )
			spellRange = skillInstance.getRangeMax( self.owner )
			self.owner.pursueEntity( target, spellRange, self.pursueAttack )
		else:
			self.owner.showInvalidItemCover( skillID )
			self.actionEnd()

	def actionEnd( self ):
		"""
		成功执行一个行为后的处理，如果不成功，那么中途肯定退出了这个状态。
		"""
		if self.owner.pkStateMessage() is not None:
			return
		self.timerID = BigWorld.callback( self.owner.hit_speed + Const.AUTO_ATTACK_DELAY_AMEND, self.action )

	def pursueAttack( self, owner, targetEntity, success ):
		"""
		追踪目标的回调
		"""
		if self.owner.attackState != self.state:
			return

		if targetEntity is None:
			owner.cancelAttackState()
			return

		if BigWorld.player().targetEntity != targetEntity :
			owner.cancelAttackState()
			return

		if not success:
			owner.cancelAttackState()
			return

		self.tryUseSkill()

	def canChangeState( self, oldState, attackArgument ):
		"""
		检查是否能进入该状态

		@param oldState : 转换过来的状态
		@type oldState : UINT8
		@param attackArgument : 封装参数
		@type attackArgument : see AttackArgumentFactory
		"""
		# 自动战斗状态下，不能进入该状态
		if oldState == Const.ATTACK_STATE_AUTO_FIGHT: return
		# 玩家当前在吟唱，不能进入该状态。
		if self.owner.intonating(): return False
		# 指定技能不允许释放，不能进入该状态。
		skillID = attackArgument.param
		skillInstance = Skill.getSkill( skillID )
		if not skillInstance.isCooldown( self.owner ) :
			self.owner.statusMessage( csstatus.SKILL_NOT_READY )
			self.owner.showInvalidItemCover( skillID )
			return False
		return AttackBase.canChangeState( self, oldState, attackArgument )

	def interruptAttack( self, reason ):
		"""
		攻击被打断，此状态攻击被打断则推出此状态
		"""
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		if self.owner.isPursueState() or ( self.owner.vehicle and self.owner.vehicle.isPursueState() ):
			return
		self.owner.cancelAttackState()

	def onSpellInterrupted( self, skillID, reason ):
		"""
		服务器打断释放技能
		"""
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		self.owner.cancelAttackState()

	def onStateChanged( self, oldState, newState ):
		"""
		玩家的战斗状态改变
		"""
		if newState != csdefine.ENTITY_STATE_FIGHT:
			self.owner.cancelAttackState()

class AutoSpellAttack( AttackBase ):
	"""
	自动使用技能攻击，例如：右键攻击目标
	"""
	def __init__( self, owner ):
		"""
		"""
		AttackBase.__init__( self, owner )
		self.state = Const.ATTACK_STATE_AUTO_SPELL
		self.timerID = 0

	def enter( self, attackArgument ):
		"""
		进入此状态后的初始化
		"""
		self.owner.autoRestore()
		self.action()

	def leave( self ):
		"""
		离开此状态时的清理工作
		"""
		BigWorld.cancelCallback( self.timerID )

	def interruptAttack( self, reason ):
		"""
		攻击被打断，此状态攻击被打断则推出此状态
		"""
		if self.owner.isPursueState( ) or ( self.owner.vehicle and self.owner.vehicle.isPursueState() ):
			return
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		self.owner.cancelAttackState()

	def action( self ):
		"""
		此状态行为开始
		"""
		if not self.canAction():
			self.timerID = BigWorld.callback( self.owner.hit_speed + Const.AUTO_ATTACK_DELAY_AMEND, self.action )	# 重复这个行为的回调时间应该和攻击速度一致
			return
		self.spellSkill()

	def canAction( self ):
		"""
		是否能开始行为
		"""
		if self.owner.intonating() or self.owner.isInHomingSpell:
			return False
		return True

	def spellSkill( self ):
		"""
		释放技能攻击

		使用指定技能攻击目标：
		如果魔法不足或者技能没准备好，那么使用普通攻击目标；
		如果距离太远，那么接近到合法距离后攻击目标；
		如果满足条件，那么攻击目标；
		否则，退出此状态。
		"""
		skillInstance = Skill.getSkill( self.owner.getNormalAttackSkillID() )
		self.spellableCheck( skillInstance, self.owner.getNormalAttackSkillID() )

	def spellableCheck( self, skillInstance, skillID ):
		"""
		由于自动战斗使用规则的更改 使得右键战斗的技能选择结构也需更改 modified by姜毅
		"""
		target = self.owner.targetEntity
		if target is None:
			self.owner.cancelAttackState()
			return True
		# 策划要求对一个目标判断是合法之后才允许向 距离过远的目标靠近 否则告之不可攻击相关信息
		spellTarget = SkillTargetObjImpl.createTargetObjEntity( target )
		state = skillInstance.useableCheck( self.owner, spellTarget )
		if state != csstatus.SKILL_GO_ON:
			if state in [ csstatus.SKILL_NOT_READY, csstatus.SKILL_OUTOF_MANA ]:	# 使用普通攻击技能攻击
				self.owner.showInvalidItemCover( skillID )
				skillInstance = Skill.getSkill( self.owner.getNormalAttackSkillID() )
				state2 = skillInstance.useableCheck( self.owner, spellTarget )
				if state2 == csstatus.SKILL_GO_ON:
					skillInstance.spell( self.owner, spellTarget )
					self.actionEnd()
					return True
				elif state2 == csstatus.SKILL_TOO_FAR:
					spellRange = skillInstance.getRangeMax( self.owner )
					self.owner.pursueEntity( target, spellRange, self.pursueAttack )
					return True
				else:
					if state is not None:
						self.owner.statusMessage( state )
					self.owner.cancelAttackState()
					return False
			elif state != csstatus.SKILL_TOO_FAR:
				self.owner.showInvalidItemCover( skillID )
				if state is not None:
					self.owner.statusMessage( state )
				self.owner.cancelAttackState()
				return False
			else:	# 如果是距离太远，接近后攻击
				self.owner.showSpellingItemCover( skillID )
				spellRange = skillInstance.getRangeMax( self.owner )
				self.owner.pursueEntity( target, spellRange, self.pursueAttack )
				return True
		else:
			if self.owner.isMoving() and self.owner.isInSpellRange( target, skillInstance ):	# 原来的版本中停止移动0.1秒后再攻击
				self.owner.stopMove()
			skillInstance.spell( self.owner, spellTarget )
			self.actionEnd()
			return True

	def actionEnd( self ):
		"""
		成功执行一个行为后的处理，如果不成功，那么中途肯定退出了这个状态。
		"""
		if self.owner.pkStateMessage() is not None:
			return
		self.timerID = BigWorld.callback( self.owner.hit_speed + Const.AUTO_ATTACK_DELAY_AMEND, self.action )	# 重复这个行为的回调时间应该和攻击速度一致

	def pursueAttack( self, owner, targetEntity, success ):
		"""
		追踪目标的回调
		"""
		if self.owner.attackState != self.state:
			return

		if targetEntity is None:
			owner.cancelAttackState()
			return

		if BigWorld.player().targetEntity != targetEntity :
			owner.cancelAttackState()
			return

		if not success:
			owner.cancelAttackState()
			return

		self.spellSkill()

	def canChangeState( self, oldState, attackArgument ):
		"""
		检查是否能进入该状态

		@param oldState : 转换过来的状态
		@type oldState : UINT8
		@param attackArgument : 封装参数
		@type attackArgument : see AttackArgumentFactory
		"""
		if oldState == self.state: return False
		# 自动战斗状态下，不能进入该状态
		if oldState == Const.ATTACK_STATE_AUTO_FIGHT: return False
		return AttackBase.canChangeState( self, oldState, attackArgument )

	def onStateChanged( self, oldState, newState ):
		"""
		玩家的战斗状态改变
		"""
		if newState != csdefine.ENTITY_STATE_FIGHT:
			self.owner.cancelAttackState()

	def onSpellInterrupted( self, skillID, reason ):
		"""
		服务器打断释放技能
		"""
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		self.owner.cancelAttackState()

class SpellAndAutoHomingAttack( AttackBase ):
	"""
	指定技能与引导连续攻击技能交替使用状态
	"""
	def __init__( self, owner ):
		"""
		"""
		AttackBase.__init__( self, owner )
		self.state = Const.ATTACK_STATE_AUTO_SPELL_HOMING
		self.timerID = 0

	def enter( self, attackArgument ):
		"""
		进入此状态后的初始化
		"""
		self.owner.autoRestore()
		self.action()

	def leave( self ):
		"""
		离开此状态时的清理工作
		"""
		BigWorld.cancelCallback( self.timerID )

	def interruptAttack( self, reason ):
		"""
		攻击被打断，此状态攻击被打断则推出此状态
		"""
		if self.owner.isPursueState( ) or ( self.owner.vehicle and self.owner.vehicle.isPursueState() ):
			return
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		self.owner.cancelAttackState()

	def action( self ):
		"""
		此状态行为开始
		"""
		if not self.canAction():
			self.timerID = BigWorld.callback( self.owner.hit_speed + Const.AUTO_ATTACK_DELAY_AMEND, self.action )	# 重复这个行为的回调时间应该和攻击速度一致
			return
		self.tryUseSkill()

	def canAction( self ):
		"""
		是否能开始行为
		"""
		if self.owner.intonating():
			return False
		if hasattr( self.owner, "isInHomingSpell" ) and self.owner.isInHomingSpell:return False
		return True

	def tryUseSkill( self ):
		"""
		尝试使用技能
		据策划最新规则，自动战斗栏上的3个技能要根据CD情况播放
		"""
		# 目标不存在则直接退出该状态
		target = self.owner.targetEntity
		if target is None:
			self.owner.statusMessage( csstatus.SKILL_NO_TARGET )
			self.owner.cancelAttackState()
			return True
		spellTarget = SkillTargetObjImpl.createTargetObjEntity( target )

		skillIDList = self.owner.getAutoSkillIDList()
		# 如果没有摆放技能，则使用默认连续攻击技能
		if len( skillIDList ) == 0:
			lastUseAutoSkillID = self.owner.getLastUseAutoSkillID()
		else:
			# 技能使用成功则重新下一个tick检测
			for skillID in skillIDList:
				if self.useSkill( skillID, target ):
					return

			# 自动战斗栏摆放的技能都不能使用，则自动使用连续攻击技能
			lastUseAutoSkillID = self.owner.getLastUseAutoSkillID()
			self.useSkill( lastUseAutoSkillID, target )

	def useSkill( self, skillID, target ):
		"""
		使用一个技能，追击认为是使用成功。
		"""
		skillInstance = Skill.getSkill( skillID )
		spellTarget = SkillTargetObjImpl.createTargetObjEntity( target )
		state = skillInstance.useableCheck( self.owner, spellTarget )
		# 距离太远，接近后攻击
		if state == csstatus.SKILL_TOO_FAR:
			self.owner.showSpellingItemCover( skillID )
			spellRange = skillInstance.getRangeMax( self.owner )
			self.owner.pursueEntity( target, spellRange, self.pursueAttack )
		elif state == csstatus.SKILL_GO_ON:
			if self.owner.isMoving() and self.owner.isInSpellRange( target, skillInstance ):
				self.owner.stopMove()
			skillInstance.spell( self.owner, spellTarget )
			self.actionEnd()
		else:
			self.owner.showInvalidItemCover( skillID )
			return False
		return True

	def pursueAttack( self, owner, targetEntity, success ):
		"""
		追踪目标的回调
		"""
		if self.owner.attackState != self.state:
			return

		if targetEntity is None:
			owner.cancelAttackState()
			return

		if BigWorld.player().targetEntity != targetEntity :
			owner.cancelAttackState()
			return

		if not success:
			owner.cancelAttackState()
			return

		self.tryUseSkill()

	def actionEnd( self ):
		"""
		成功执行一个行为后的处理，如果不成功，那么中途肯定退出了这个状态。
		"""
		if self.owner.pkStateMessage() is not None:
			return
		self.timerID = BigWorld.callback( self.owner.hit_speed + Const.AUTO_ATTACK_DELAY_AMEND, self.tryUseSkill )	# 重复这个行为的回调时间应该和攻击速度一致

	def canChangeState( self, oldState, attackArgument ):
		"""
		检查是否能进入该状态

		@param oldState : 转换过来的状态
		@type oldState : UINT8
		@param attackArgument : 封装参数
		@type attackArgument : see AttackArgumentFactory
		"""
		if oldState == self.state: return False
		# 自动战斗状态下，不能进入该状态
		if oldState == Const.ATTACK_STATE_AUTO_FIGHT: return
		# 玩家当前在吟唱，不能进入该状态。
		if self.owner.intonating(): return False
		# 指定技能不允许释放，不能进入该状态。
		skillIDList = self.owner.getAutoSkillIDList()
		if len( skillIDList ) == 0: return False
		skillID = skillIDList[0]
		skillInstance = Skill.getSkill( skillID )
		if not skillInstance.isCooldown( self.owner ) :
			self.owner.statusMessage( csstatus.SKILL_NOT_READY )
			self.owner.showInvalidItemCover( skillID )
			return False
		return AttackBase.canChangeState( self, oldState, attackArgument )

	def onStateChanged( self, oldState, newState ):
		"""
		玩家的战斗状态改变
		"""
		if newState != csdefine.ENTITY_STATE_FIGHT:
			self.owner.cancelAttackState()

	def onSpellInterrupted( self, skillID, reason ):
		"""
		服务器打断释放技能
		"""
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		self.owner.cancelAttackState()

class AutoFightAttack( AttackBase ):
	"""
	自动战斗状态
	"""
	def __init__( self, owner ):
		"""
		"""
		AttackBase.__init__( self, owner )
		self.state = Const.ATTACK_STATE_AUTO_FIGHT
		self.timerID = 0
		self.startPosition = ( 0, 0, 0 )			# 自动战斗开始位置
		self.running = False						# 自动攻击行为是否正在执行
		self.pickUpList = []						# 拾取列表
		self.lastDropEntityID = 0				# 最后拾取的entityID，因为dropEntity销毁有延时，如果已经拾取过了，但是下一个拾取侦测过来还会找到此entity并播放拾取动作
		self.startPickUpDelayTimerID = 0		# 开始自动拾取延时的timerID
		self.persistentTimerID = 0				# 开始一次自动战斗持续时间的timer
		self.controlSkillID = -1				# 自动战斗允许手动使用技能，其用于记录该技能id，以-1清空 by 姜毅
		self.defaultSkillID = 0
		# 自动战斗新配置相关 by 姜毅
		self.actPetInfo = None					# 自动战斗用以记录出战宠物的简要数据
		self.AFconfig = {}
		self.onceMessageList = []					# 蛋疼的自动战斗一次性提示信息

	def cancel( self ):
		"""
		离开此状态
		"""
		self.owner.cancelAttackState()
		self.owner.statusMessage( csstatus.AUTO_FIGHT_TIME_OUT )

	@languageDepart_AFEnter
	def enter( self, attackArgument ):
		"""
		"""
		self.defaultSkillID = Define.SKILL_ID_TRIGGER_SKILLS.get( self.owner.getClass() )
		self.AFconfig = self.owner.getAutoFightConfig()
		self.startPosition = self.owner.position
		self.setAutoPet( False )
		self.owner.cell.enterAutoFight()
		ECenter.fireEvent( "EVT_ON_START_AUTOFIGHT" )
		self.timerID = BigWorld.callback( Const.AUTO_FIGHT_DETECT, self.autoFightDetect )
		self.pickUpAction()
		self.pyBox = None					# 二次确认框

	def autoFightDetect( self ):
		"""
		自动战斗开始后，每隔Const.AUTO_FIGHT_DETECT执行的一个侦测
		"""
		BigWorld.cancelCallback( self.timerID )
		self.timerID = BigWorld.callback( Const.AUTO_FIGHT_DETECT, self.autoFightDetect )
		self.owner.autoRestore()
		if not self.canAction():
			return
		self.action()

	def onStateChanged( self, oldState, newState ):
		"""
		角色状态改变
		"""
		if newState == csdefine.ENTITY_STATE_DEAD:
			if self.AFconfig["autoReboin"]:
				if self.actAutoReboin():
					return
			self.owner.cancelAttackState()

	@languageDepart_AFLeave
	def leave( self ):
		"""
		离开此状态
		"""
		ECenter.fireEvent( "EVT_ON_STOP_AUTOFIGHT" )
		ECenter.fireEvent( "EVT_ON_STOP_AUTO_SKILL", self.defaultSkillID )
		self.running = False
		self.startPosition = ( 0, 0, 0 )
		self.pickUpList = []
		self.onceMessageList = []
		self.owner.resetAutoFightList()
		self.owner.stopPickUp()
		self.lastDropEntityID = 0
		self.defaultSkillID = Define.SKILL_ID_TRIGGER_SKILLS.get( self.owner.getClass() )
		BigWorld.cancelCallback( self.timerID )
		BigWorld.cancelCallback( self.startPickUpDelayTimerID )
		BigWorld.cancelCallback( self.persistentTimerID )
		self.owner.cell.leaveAutoFight()
		self.setAutoPet( True )
		self.pyBox = None					# 二次确认框

	def action( self ):
		"""
		开始自动攻击
		"""
		self.running = True						# 自动攻击正在运行中
		self.AFconfig = self.owner.getAutoFightConfig()
		# 寻找目标
		target = self.__getTarget()
		if self.AFconfig["isAutoConjure"]: self.actPetAutoConj()	# 宠物召唤
		if self.AFconfig["isAutoAddJoy"]: self.actPetAutoJoyCharge( self.AFconfig["joyLess"] )	# 快乐度补充
		if self.AFconfig["autoRepair"]: self.actAutoRepair( self.AFconfig["repairRate"] )	#自动使用物品修理装备
		if target and not target.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and target.hasFlag( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED ):
			self.autoRangeCheck()	# 回归范围						# 此次自动攻击运行结束
			return
		if target and target != self.owner.targetEntity:
			rds.targetMgr.bindTarget( target )
		self.__attackTarget( target )
		self.autoRangeCheck()	# 回归范围

	def __attackTarget( self, target ):
		"""
		攻击目标
		@param target :	BigWorld entity
		"""
		if self.controlSkillID > 0:	# 如果此时玩家手动释放技能，则优先处理玩家手动释放的技能 by 姜毅
			skillInstance = Skill.getSkill( self.controlSkillID )
			# 手动释放技能检测不通过，则转为使用自动战斗栏的技能
			targetObject = skillInstance.getCastObject().convertCastObject( self.owner, target )
			spellTarget = SkillTargetObjImpl.createTargetObjEntity( targetObject )
			state = skillInstance.useableCheck( self.owner, spellTarget )
			if state != csstatus.SKILL_GO_ON and state != csstatus.SKILL_TOO_FAR:
				self.owner.statusMessage( state )
				skillInstance = self.__getAutoUseSkillInstance( target )
		else:						# 否则使用自动战斗栏的技能
			skillInstance = self.__getAutoUseSkillInstance( target )
		self.__useSkill( target, skillInstance )
		self.controlSkillID = -1	# 手动技能无论是否成功使用都清空

	def __getAutoUseSkillInstance( self, target ):
		"""
		"""
		skillInstance = Skill.getSkill( self.defaultSkillID )
		idList = self.owner.getAutoSkillIDList()		# 获得自动战斗栏的技能列
		for skillID in idList:
			skillInstance = self.__getAutoUseSpellAttack( target, skillID )      # 获得列表中可用技能
			if skillInstance is not Skill.getSkill( self.defaultSkillID ):break
		return skillInstance

	def __useSkill( self, target, skillInstance ):
		"""
		使用一个技能 攻击技能和增益技能通用
		"""
		target = skillInstance.getCastObject().convertCastObject( self.owner, target )
		spellTarget = SkillTargetObjImpl.createTargetObjEntity( target )
		state = skillInstance.useableCheck( self.owner, spellTarget )
		if state != csstatus.SKILL_GO_ON:
			if state == csstatus.SKILL_TOO_FAR:		# 如果是距离太远，接近后攻击
				self.owner.showSpellingItemCover( skillInstance.getID() )
				self.owner.pursueEntity( target, skillInstance.getRangeMax( self.owner ), self.pursueAttack )
		else:
			if self.owner.isMoving() and self.owner.isInSpellRange( target, skillInstance ):
				self.owner.stopMove()
			skillInstance.spell( self.owner, spellTarget )
			#self.__setDefaultSkill( skillInstance )

	def __setDefaultSkill( self, skillInstance ):
		"""
		设置默认的攻击技能，例如普通攻击
		"""
		homing = skillInstance.isHomingSkill()
		if skillInstance.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS_NORMAL or homing:
			#self.owner.isInHomingSpell = homing
			self.defaultSkillID = skillInstance.getID()
			ECenter.fireEvent( "EVT_ON_AUTO_NOR_SKILL_CHANGE", self.defaultSkillID )

	def canAction( self ):
		"""
		判断行为是否能够被执行。

		如果正在执行中，那么不执行。
		如果被打断了，那么执行。
		"""
		if self.running or self.owner.intonating():
			return False
		if hasattr( self.owner, "isInHomingSpell" ) and self.owner.isInHomingSpell:return False
		return True

	def actionEnd( self ):
		"""
		行为结束
		"""
		self.running = False

	def pursueAttack( self, owner, targetEntity, success ):
		"""
		接近后攻击
		"""
		if self.owner.attackState != self.state:
			return

		if targetEntity is None:
			self.actionEnd()
			return

		if BigWorld.player().targetEntity != targetEntity:
			self.actionEnd()
			return

		if not success:
			self.actionEnd()
			return

		self.__attackTarget( targetEntity )

	def __getAutoUseSpell( self, target ):
		"""
		@param target :	entity

		传一个target参数的原因是，明确说明技能实例的获得是和target参数有关的。
		"""
		skillInstance = Skill.getSkill( self.owner.getAutoSkillID() )
		target = skillInstance.getCastObject().convertCastObject( self.owner, target )
		target = SkillTargetObjImpl.createTargetObjEntity( target )
		state = skillInstance.useableCheck( self.owner, target )
		if skillInstance.getType() == csdefine.BASE_SKILL_TYPE_PASSIVE or state != csstatus.SKILL_GO_ON:
			skillInstance = Skill.getSkill( self.defaultSkillID )
		return skillInstance

	def __getAutoUseSpellAttack( self, target, skillID ):
		"""
		@param target :	entity
		因为自动战斗要增加技能数 获得自动战斗中攻击类技能 by姜毅
		"""
		skillInstance = Skill.getSkill( skillID )
		target = skillInstance.getCastObject().convertCastObject( self.owner, target )
		target = SkillTargetObjImpl.createTargetObjEntity( target )
		state = skillInstance.useableCheck( self.owner, target )
		if skillInstance.getType() != csdefine.BASE_SKILL_TYPE_PASSIVE and state == csstatus.SKILL_GO_ON:
			return skillInstance
		return Skill.getSkill( self.defaultSkillID )

		
	def __getTarget( self ):
		"""
		获得新的攻击目标
		"""
		target = self.owner.targetEntity
		if target is not None and self.AFconfig["radius"] > 0 and \
			( target.position.distTo( self.startPosition ) - target.getBoundingBox().z ) > self.AFconfig["radius"] :
				rds.targetMgr.unbindTarget()
				self.owner.statusMessage( csstatus.AUTO_FIGHT_TARGET_OUT_RANGE )
				target = None
		if not self.__targetCnd( target ):
			target = self.__getNearbyMonster()
		return target

	def __targetCnd( self, target ):
		"""
		"""
		player = BigWorld.player()
		
		if target is None or not ( ( target.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and self.owner.qieCuoTargetID == target.id ) or \
			( target.isEntityType( csdefine.ENTITY_TYPE_PET ) and self.owner.qieCuoTargetID == target.ownerID ) or target.utype in Const.ATTACK_MOSNTER_LIST ) or \
				not target.isAlive() or target.hasFlag( csdefine.ENTITY_FLAG_SPEAKER ) or self.owner.isQuestMonster( target ) or \
			 		( not target.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and target.hasFlag( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED ) ) or \
			 			target.hasFlag( csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE ) or target.hasFlag( csdefine.ENTITY_FLAG_FRIEND_ROLE ) or \
			 			target.hasFlag( csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE_2 ):
			 				return False
		if target.hasFlag( csdefine.ENTITY_FLAG_UNVISIBLE ):
			pid = target.ownerVisibleInfos[ 0 ]
			tid = target.ownerVisibleInfos[ 1 ]
			if pid == player.id or ( player.isInTeam() and tid == player.teamID ):
				return True
			return False
		return True

	def __getNearbyMonster( self, meter = Const.AUTO_ATTACK_RANGE ):
		"""
		获取离自己最近的一个怪物
		原名为：__getLatestMonster
		修改并重命名为：__getNearbyMonster（hyw -- 2008.11.08）
		"""
		autoFightList = self.owner.getAutoFightList()
		for index in xrange( len( autoFightList ) - 1, -1, -1 ):
			target = BigWorld.entities.get( autoFightList[ index ] )
			if target is None or not target.isAlive() or \
				( self.AFconfig["radius"] > 0 and ( target.position.distTo( self.startPosition ) - target.getBoundingBox().z ) > self.AFconfig["radius"] ):
				del autoFightList[ index ]
			else :
				if not self.__targetCnd( target ):
					continue
				return target

		monsters = self.owner.entitiesInRange( meter, cnd = self.attackVerifier )
		
		spaceType = self.owner.getCurrentSpaceType()
		if spaceType == csdefine.SPACE_TYPE_CITY_WAR:
			isRight = self.owner.tongInfos['right'].keys()[0] == self.owner.tong_dbID
			for monster in monsters:
				if not self.__targetCnd( monster ):
					continue
				if monster.isRight != isRight:
					return monster
		else:
			for monster in monsters:
				if not self.__targetCnd( monster ):
					continue
				return monster

		return None

	def attackVerifier( self, entity ) :
		"""
		是否是可攻击怪物( hyw -- 2008.11.08 )
		"""
		# 可选范围外的不可选择
		if self.AFconfig["radius"] > 0 and ( entity.position.distTo( self.startPosition ) - entity.getBoundingBox().z ) > self.AFconfig["radius"] :
			return False

		if self.AFconfig["isAutoPlus"] and entity.isEntityType( csdefine.ENTITY_TYPE_PET ):
			if self.owner.qieCuoTargetID == entity.ownerID:
				return True
			else:
				self.autoPlusSkillPet( entity )
		elif self.AFconfig["isAutoPlus"] and entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if self.owner.qieCuoTargetID == entity.id:
				return True
			else:
				self.autoPlusSkill( entity )

		if entity.isEntityType( csdefine.ENTITY_TYPE_TONG_NAGUAL ):
			# 上下两个不能and在一起
			if not self.owner.tong_dbID in entity.enemyTongDBIDList:
				return False
		elif not entity.utype in Const.ATTACK_MOSNTER_LIST:		# 必须是怪物
			if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and self.owner.qieCuoTargetID == entity.id:
				return True
			if entity.isEntityType( csdefine.ENTITY_TYPE_PET )  and self.owner.qieCuoTargetID == entity.ownerID:
				return True
 			return False

		if not hasattr( entity, "modelNumber" ):
			return False

		if entity.getState() != csdefine.ENTITY_STATE_FREE:								# 处于战斗状态下的一些特殊情况，也要返回为可自动战斗
			target = BigWorld.entities.get( entity.targetID, None )

			if target is None:															#1.怪物攻击的目标不在视野范围内
				return True

			if self.owner.id == target.id:												#2.怪物攻击的目标是自己
				return True

			pet = self.owner.pcg_getActPet()
			if pet is not None and pet.id == target.id:									#3.怪物攻击的目标是自己的宠物
				return True

			if self.owner.isTeamMember( target.id ):									#4.怪物攻击的目标是自己的队员
				return True

			if target.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ):				#5.怪物攻击的目标存在，且是自己的镖车
				if BigWorld.entities[entity.targetID].ownerID == self.owner.id:
					return True

			if not target.getEntityType() in [csdefine.ENTITY_TYPE_ROLE, csdefine.ENTITY_TYPE_PET, csdefine.ENTITY_TYPE_VEHICLE_DART]:				#6.怪物攻击的目标不是玩家，不是宠物，不是镖车，则可以被选中
				return True

		else:							#7.处于自由战斗状态的怪物，都可以被作为自动战斗目标
			return True

		return False

	def onItemDrop( self, dropEntity ):
		"""
		拾取通知
		"""
		self.pickUpAction()

	def pickUpAction( self ):
		"""
		拾取行为开始
		"""
		if not self.owner.getPickItemNeed():
			return

		self.pickUpList = self.getDropItemsNearBy()
		if len( self.pickUpList ) == 0:
			return

		# 过滤掉拾取过的箱子
		tempPickUpList = list( self.pickUpList )
		[ self.pickUpList.remove( tempDropEntity ) for tempDropEntity in tempPickUpList if tempDropEntity.isLooked == True ]
		if len( self.pickUpList ) == 0: # 过滤后该列表为空则返回
			return
		dropEntity = self.pickUpList.pop()
		if dropEntity.id == self.lastDropEntityID and len( self.pickUpList ) != 0:
			dropEntity = self.pickUpList.pop()

		self.lastDropEntityID = dropEntity.id
		dropEntity.isLooked = True
		self.owner.startPickUp( dropEntity )
		BigWorld.callback( Const.AUTO_PICK_UP_DELAY, Functor( self.__pickUpAllItem, dropEntity ) )

	def __pickUpAllItem( self, dropEntity ):
		"""
		捡取所有物品
		"""
		# 类型选择拾取
		isIPU = self.AFconfig["isIgnorePickUp"] #是否忽略拾取		
		if isIPU:
			igList = self.AFconfig["ignoredList"]#忽略列表
			if len( igList ) <= 0: #
				dropEntity.pickUpAllItems()
			else:
				indexs = []
				for k in dropEntity.boxItems:
					put = k["item"].getPickUpType()
					# 下面的k["item"].getQuality() - 1是因为策配置方面认定以0~4做品质范围，坚持使用20000作为白装，这边也只好配合了
					put = put + (k["item"].getQuality() - 1) if put in ItemTypeEnum.PICK_UP_TYPE_QUALITY_AREA else put
					if put in igList:
						continue
					indexs.append( k["order"] )
				if len( indexs ) > 0:
					dropEntity.cell.pickDropItems( indexs )
		else:
			pList = self.AFconfig["pickUpTypeList"]#拾取列表
			if len( pList ):
				indexs = []
				for k in dropEntity.boxItems:
					put = k["item"].getPickUpType()
					# 下面的k["item"].getQuality() - 1是因为策配置方面认定以0~4做品质范围，坚持使用20000作为白装，这边也只好配合了
					put = put + (k["item"].getQuality() - 1) if put in ItemTypeEnum.PICK_UP_TYPE_QUALITY_AREA else put
					if put in pList:
						indexs.append( k["order"] )
				if len( indexs ) > 0:
					dropEntity.cell.pickDropItems( indexs )
		self.owner.stopPickUp()
		if len( self.pickUpList ) == 0:
			return
		dropEntity = self.pickUpList.pop()
		self.lastDropEntityID = dropEntity.id
		self.owner.startPickUp( dropEntity )
		BigWorld.callback( Const.AUTO_PICK_UP_DELAY, Functor( self.__pickUpAllItem, dropEntity ) )

	def getDropItemsNearBy( self, range = Const.AUTO_PICK_UP_DISTANCE ):
		"""
		查找周围的物品
		"""
		return self.owner.entitiesInRange( range, cnd = lambda ent : ent.__class__ == DroppedBox and ent.canPickUp )

	def setControlSkillID( self, skillID ):
		"""
		设置自动战斗中途玩家手动使用的技能ID by 姜毅
		"""
		self.controlSkillID = skillID

	#------------------新增自动战斗配置功能 17:13 2009-12-4 by 姜毅------------------
	def actPetAutoConj( self ):
		"""
		处理召唤死亡宠物功能
		"""
		owner = self.owner
		if self.actPetInfo != None and owner.pcg_getActPet() is None:
			conjResult = self.actPetInfo.conjureForAutoFight( owner )
			if conjResult == 1 or conjResult == -1 or conjResult in self.onceMessageList:
				return
			else:
				owner.statusMessage( conjResult )
				self.onceMessageList.append( conjResult )

	def setAutoPet( self, reset ):
		"""
		设置自动宠物的简要数据
		@ param : reset 是否充值默认值
		@ param : reset BOOL
		"""
		if reset:
			self.actPetInfo = None
			return
		pet = self.owner.pcg_getActPet()
		if pet is None: return
		self.actPetInfo = self.owner.pcg_getPetEpitomes()[ pet.databaseID ]

	def actPetAutoJoyCharge( self, joyLess ):
		"""
		处理宠物快乐度功能
		@ param : joyLess 配置中的需补充最小快乐度
		@ param : joyLess INT8
		"""
		if self.actPetInfo is None: return
		owner = self.owner
		pet = owner.pcg_getActPet()
		if pet is None: return
		if pet.joyancy >= joyLess: return
		index = ( pet.level - 1 ) / 30
		itemID = csconst.pet_joyancy_items[index]
		if not self.actPetInfo.addJoyanceForAutoFight( owner ):
			if csstatus.SKILL_PET_JOYANCY_ITEM_NO_EXIST in self.onceMessageList:
				return
			owner.statusMessage( csstatus.SKILL_PET_JOYANCY_ITEM_NO_EXIST, g_items.id2name( itemID ) )
			self.onceMessageList.append( csstatus.SKILL_PET_JOYANCY_ITEM_NO_EXIST )
			
	def actAutoRepair( self, rate ):
		"""
		自动使用物品修理装备
		"""
		equips = self.owner.getItems( csdefine.KB_EQUIP_ID )
		needRep = False
		for equip in equips:
			hardMax = equip.getHardinessLimit()
			if hardMax == 0:
				continue
			hardNow = float(equip.getHardiness())
			if (hardNow/hardMax * 100) < rate:
				needRep = True
				break
		if needRep:
			repItems = self.owner.findItemsFromNKCK_( Const.AUTO_FIGHT_REPAIR_ITEM_ID )
			if len(repItems) <= 0:
				if csstatus.EQUIP_REPAIR_NO_REP_ITEM not in self.onceMessageList:
					self.owner.statusMessage( csstatus.EQUIP_REPAIR_NO_REP_ITEM )
					self.onceMessageList.append( csstatus.EQUIP_REPAIR_NO_REP_ITEM )
				return
			item = repItems[0]
			self.owner.useItemDependOnType( item.getUid(), item, item.getType() )
			
	def actAutoReboin( self ):
		"""
		自动复活
		"""
		p_state = self.owner.getState()
		if p_state == csdefine.ENTITY_STATE_DEAD:
			reboinItems = self.owner.findItemsFromNKCK_( Const.AUTO_FIGHT_REBOIN_ITEM_ID )
			if len(reboinItems) <= 0:
				if self.owner.level < 30:
					return False
				ECenter.fireEvent( "EVT_ON_HIDE_REVIVE_BOX" )
				def query( rs_id ):
					if rs_id == RS_OK:
						ECenter.fireEvent( "EVT_ON_TOGGLE_SPECIAL_SHOP" )
				if not self.pyBox is None:
					self.pyBox.visible = False
					self.pyBox = None
				self.pyBox = showMessage( mbmsgs[0x00c7], "", MB_OK_CANCEL, query )
				return False
			item = reboinItems[0]
			self.owner.cell.useItemRevive()
			#self.attackState = Const.ATTACK_STATE_AUTO_FIGHT
		return True

	def autoRangeCheck( self ):
		"""
		检测离原点距离，超距离的话就往回走，进入范围内就不跑了
		"""
		if self.AFconfig["radius"] == 0:
			self.actionEnd()
			return
		owner = self.owner
		if ( owner.position.distTo( self.startPosition ) - owner.getBoundingBox().z ) < self.AFconfig["radius"]:
			self.actionEnd()
			return
		owner.moveTo( self.startPosition )
		self.actionEnd()

	def autoPlusSkillPet( self, pet ):
		"""
		处理宠物自动增益技能的相关功能
		"""
		owner = self.owner
		plusInfo = owner.getAutoPlusInfo()
		if plusInfo[1] == 1:
			p = owner.pcg_getActPet()
			if p is not None and p.id == pet.id:
				skillID = self.checkPlusSkill( pet )
				if skillID <= 0: return
				skillInstance = Skill.getSkill( skillID )
				if skillInstance._datas["ReceiverCondition"]["conditions"] == "RECEIVER_CONDITION_ENTITY_ROLE":
					self.__useSkill( pet, skillInstance )
				return
		if plusInfo[2] == 1 and plusInfo[1] == 1:
			o = pet.getOwner()
			if o is not None and o.id != owner.id and o.id in owner.teamMember:
				skillID = self.checkPlusSkill( pet )
				if skillID <= 0: return
				skillInstance = Skill.getSkill( skillID )
				if skillInstance._datas["ReceiverCondition"]["conditions"] == "RECEIVER_CONDITION_ENTITY_ROLE":
					self.__useSkill( pet, skillInstance )

	def autoPlusSkill( self, role ):
		"""
		处理角色自动增益技能相关的功能
		"""
		owner = self.owner
		plusInfo = owner.getAutoPlusInfo()
		if plusInfo[0] == 1 and role.id == owner.id:
			skillID = self.checkPlusSkill( role )
			if skillID <= 0: return
			skillInstance = Skill.getSkill( skillID )
			self.__useSkill( role, skillInstance )
			return
		if plusInfo[2] == 1 and role.id != owner.id and role.id in owner.teamMember:
			skillID = self.checkPlusSkill( role )
			if skillID <= 0: return
			skillInstance = Skill.getSkill( skillID )
			if skillInstance._datas["ReceiverCondition"]["conditions"] == "RECEIVER_CONDITION_ENTITY_ROLE":
				self.__useSkill( role, skillInstance )

	def checkPlusSkill( self, entity ):
		"""
		初步检测增益技能的可用性
		注意，增益技能自动释放系统只对产生buff的技能有效，而增益技能都是能产生buff的技能
		因此，一般来说是不会有啥问题的
		如果增益技能列表里放了不能产生buff的技能，那么请节哀吧
		"""
		if entity is None: return 0
		skillIDs = self.owner.getAutoPlusSkillIDList()
		if len( skillIDs ) == 0: return 0
		buffSkillIDs = []
		for idx, buff in enumerate( entity.attrBuffs ):
			id = buff["skill"].getID()
			sk = Skill.getSkill( id )
			if sk.getType() == csdefine.BASE_SKILL_TYPE_BUFF:		# 对于buff技能，则要确实取得其源技能
				id = sk.getSourceSkillID()
			buffSkillIDs.append( int(id/1000) )

		for skillID in skillIDs:
			id = int(skillID/1000)
			if id not in buffSkillIDs:
				return skillID
		return 0

class Attack:
	"""
	"""
	def __init__( self ):
		"""
		"""
		self.attackState = Const.ATTACK_STATE_NONE
		self.autoSkillID = 0
		self.autoSkillIDList = []		# 自动战斗的多个技能ID列 by姜毅
		self.autoPlusSkillList = []		# 自动战斗的多个增益技能ID by姜毅
		self.castingSpell = 0			# 正在吟唱的技能。
		self.isInHomingSpell = False
		self.lastUseAutoSkillID = 0	# 最后一次使用的能自动连续攻击的技能（普通攻击技能/引导连续攻击技能）	
		self.attackInstanceDict = {}
		self.attackInstanceDict[ Const.ATTACK_STATE_NONE ]					= NoAttack( self )
		self.attackInstanceDict[ Const.ATTACK_STATE_ONCE ]					= OnceAttack( self )
		self.attackInstanceDict[ Const.ATTACK_STATE_NORMAL ]				= AutoNormalAttack( self )
		self.attackInstanceDict[ Const.ATTACK_STATE_AUTO_FIGHT ]			= AutoFightAttack( self )
		self.attackInstanceDict[ Const.ATTACK_STATE_AUTO_SPELL ]			= AutoSpellAttack( self )
		self.attackInstanceDict[ Const.ATTACK_STATE_AUTO_CONFIRM_SPELL ]	= AutoConfirmSpellAttack( self )
		self.attackInstanceDict[ Const.ATTACK_STATE_HOMING_SPELL ]			= AutoHomingSpellAttack( self )
		self.attackInstanceDict[ Const.ATTACK_STATE_SPELL_AND_HOMING ]		= SpellAutoHomingAttack( self )
		self.attackInstanceDict[ Const.ATTACK_STATE_AUTO_SPELL_HOMING ]		= SpellAndAutoHomingAttack( self )
		self.attackInstanceDict[ Const.ATTACK_STATE_AUTO_SPELL_CURSOR ]		= AutoConfirmSpellAttackCursor( self )
		# 自动战斗相关
		rds.shortcutMgr.setHandler( "COMBAT_AUTOFIGHT", self.__toggleAutoFight )
		self.__damageList = []
		self.roleAutoRestore = AutoRestore()		# 角色自动恢复
		self.petAutoRestore = PetAutoRestore()		# 宠物自动恢复

		# 自动拾取相关
		self.autoFight2AutoSpellTimerID = 0
		self.autoRestoreTimerID = 0
		cfgSect = self.roleAutoRestore.getConfigSect()

		# 自动战斗新配置相关 by 姜毅
		# 自动增益技能对象设置 [ 角色， 宠物， 队友 ]
		self.autoPlusInfo = [0, 0, 0]
		self.autoFightConfig = self.getAutoFightConfig()
		self.isAutoPickUp = self.getPickItemNeed()					# 是否自动拾取
		self.autoPlusInfo = self.getAutoPlusInfo()

	def autoRestoreDetect( self ):
		"""
		开始自动恢复
		"""
		if self.isAutoRestore():
			BigWorld.cancelCallback( self.autoRestoreTimerID )
		self.autoRestoreTimerID = BigWorld.callback( Const.AUTO_RESTORE_DETECT_INTERVAL, self.autoRestoreDetect )
		self.autoRestore()

	def isAutoRestore( self ):
		"""
		是否在自动恢复中
		"""
		return self.autoRestoreTimerID != 0

	def autoRestore( self ):
		"""
		自动恢复
		"""
		if self.intonating():
			return
		if self.actionSign( csdefine.ACTION_FORBID_USE_ITEM ):
			return
		self.roleAutoRestore.restore( self )			# 角色自动恢复
		activePet = self.pcg_getActPet()
		if activePet is not None:
			self.petAutoRestore.restore( activePet )	# 宠物自动恢复

	def stopAutoRestore( self ):
		"""
		停止自动恢复
		"""
		BigWorld.cancelCallback( self.autoRestoreTimerID )
		self.autoRestoreTimerID = 0

	def isChange2AutoSpell( self ):
		"""
		是否会切换到自动释放技能攻击状态
		"""
		return self.autoFight2AutoSpellTimerID != 0

	def cancelAutoFight2AutoSpellTimer( self ):
		"""
		退出自动战斗切换到自动释放技能攻击状态
		"""
		BigWorld.cancelCallback( self.autoFight2AutoSpellTimerID )
		self.autoFight2AutoSpellTimerID = 0

	def setPickItemNeed( self, need ):
		"""
		"""
		sect = self.roleAutoRestore.getConfigSect()
		sect.writeBool( "isAutoPickUp", need )
		self.isAutoPickUp = need
		self.autoFightConfig["isAutoPickUp"] = need
		self.roleAutoRestore.saveCfgSect()

	def getPickItemNeed( self ):
		"""
		"""
		return self.autoFightConfig["isAutoPickUp"]

	def setAutoPlusInfo( self, targetList ):
		"""
		设置自动增益技能对象
		"""
		sect = self.roleAutoRestore.getConfigSect()
		sect.writeVector3( "plusSkillTarget", tuple( targetList ) )
		self.autoPlusInfo = targetList
		self.autoFightConfig["plusSkillTarget"] = targetList
		AutoFightConfig["plusSkillTarget"] = self.autoPlusInfo
		self.roleAutoRestore.saveCfgSect()

	def getAutoPlusInfo( self ):
		"""
		"""
		targetList = self.autoFightConfig["plusSkillTarget"]
		for index, target in enumerate( list( targetList ) ):
			self.autoPlusInfo[index] = int( target )
		return self.autoPlusInfo

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		if self.qb_canAutoRestore() and not self.isAutoRestore():
			self.autoRestoreDetect()

	def leaveWorld( self ) :
		"""
		"""
		self.cancelAttackState()
		self.stopAutoRestore()
		BigWorld.cancelCallback( self.autoFight2AutoSpellTimerID )
		self.autoFight2AutoSpellTimerID = 0

	def getAtackState( self ):
		"""
		获得当前玩家的攻击状态
		"""
		return self.attackState

	def getAutoSkillID( self ):
		"""
		获得自动释放的技能
		"""
		if skillID == 0 :
			skillID = Define.SKILL_ID_TRIGGER_SKILLS.get( self.getClass() )
		return self.autoSkillID

	def setAutoSkillID( self, skillID = 0  ):
		"""
		设置自动释放技能id
		"""
		if skillID == 0 :
			skillID = Define.SKILL_ID_TRIGGER_SKILLS.get( self.getClass() )
		self.autoSkillID = skillID

	def getAutoSkillIDList( self ):
		"""
		获得自动释放的技能id list by姜毅
		传入的id list的元素一定要按照自动战斗栏的技能从左到右排列~
		"""
		return self.autoSkillIDList

	def setAutoSkillIDList( self, skillIDList = [] ):
		"""
		设置自动释放技能id list by姜毅
		"""
		self.autoSkillIDList = skillIDList

	def getAutoPlusSkillIDList( self ):
		"""
		获得自动释放的增益技能id list by姜毅
		传入的id list的元素一定要按照增益技能栏从上到下排列~
		"""
		cfgSect = self.roleAutoRestore.getConfigSect()
		if cfgSect.has_key( "plusSkills" ):
			skIDStr = cfgSect.readString( "plusSkills" )
			skIDs = skIDStr.split( "|" )
			for skId in skIDs:
				if skId == "" or int( skId ) in self.autoPlusSkillList:continue
				self.autoPlusSkillList.append( int( skId ) )
		return self.autoPlusSkillList

	def setAutoPlusSkillIDList( self, skillIDList = [] ):
		"""
		设置自动释放增益技能id list by姜毅
		"""
		self.autoPlusSkillList = skillIDList
		skIDStr = ""
		for skillID in skillIDList:
			skIDStr += "%s|"%str( skillID)
		cfgSect = self.roleAutoRestore.getConfigSect()
		if not cfgSect.has_key( "plusSkills" ):
			cfgSect.createSection( "plusSkills" )
		cfgSect.writeString( "plusSkills", skIDStr )
		AutoFightConfig["autoPlusSkillList"] = self.autoPlusSkillList
		self.roleAutoRestore.saveCfgSect()

	def getNormalAttackSkillID( self ):
		"""
		获得普通攻击技能id
		"""
		return Define.SKILL_ID_TRIGGER_SKILLS.get( self.getClass() )

	def setLastUseAutoSkillID( self, skillID ):
		"""
		设置最后一次使用的能连续攻击的技能ID（普通物理攻击/引导技能攻击）
		"""
		self.lastUseAutoSkillID = skillID

	def getLastUseAutoSkillID( self ):
		"""
		获得最后一次使用的能连续攻击的技能ID
		"""
		if self.lastUseAutoSkillID == 0 :
			self.lastUseAutoSkillID = Define.SKILL_ID_TRIGGER_SKILLS.get( self.getClass() )
		return self.lastUseAutoSkillID

	def changeAttackState( self, attackState, *arg ):
		"""
		攻击状态改变
		@param arg : 状态需要的外部参数。
		"""
		attackArgument = AttackArgumentFactory.getAttackArgument( attackState, arg )
		if self.attackState == Const.ATTACK_STATE_AUTO_FIGHT and attackArgument:
			self.attackInstanceDict[ self.attackState ].setControlSkillID( attackArgument.param )
			
		if self.attackInstanceDict[ attackState ].canChangeState( self.attackState, attackArgument ):
			DEBUG_MSG( "attackState change,%i-->>>%i." % ( self.attackState, attackState ) )
			self.attackInstanceDict[ self.attackState ].leave()
			self.attackState = attackState
			self.attackInstanceDict[ self.attackState ].enter( attackArgument )
			ECenter.fireEvent( "EVT_ON_ATTACK_STATE_CHANGTED", attackState )
		else:
			DEBUG_MSG( "Cannot change attackState,%i-->>>%i." % ( self.attackState, attackState ) )

	def cancelAttackState( self ):
		"""
		设置此接口的原因是为了区别于changeAttackState，changeAttackState是客户级请求，需要验证；
		而cancelAttackState是程序级请求，不需验证。某一个攻击状态运行结束后调用此接口退出。
		"""
		if self.attackState == Const.ATTACK_STATE_NONE:
			return
		DEBUG_MSG( "attackState change,%i-->>>%i." % ( self.attackState, Const.ATTACK_STATE_NONE ) )
		self.attackInstanceDict[ self.attackState ].leave()
		self.attackState = Const.ATTACK_STATE_NONE
		self.attackInstanceDict[ self.attackState ].enter( None )

	def isInSpellRange( self, target, spell ) :
		"""
		indicate the role whether in spell range now
		"""
		rng = self.distanceBB( target )
		if rng > spell.getRangeMax( self ) :
			return False
		return True
	
	def isInSpellDis( self, pos, spell):
		return True

	def interruptAttack( self, reason ):
		"""
		interrupt attacking
		不管玩家在什么状态，只要在吟唱过程中移动都会打断技能。
		@param	reason	: 打断的原因（一般在csstatus中定义）
		@type	reason	: int
		"""
		if self.intonating() or self.isInHomingSpell:
			self.cell.interruptSpellFC( reason )
			self.setCastingSpell( 0 )
			self.isInHomingSpell = False
		self.attackInstanceDict[ self.attackState ].interruptAttack( reason )

	def intonate( self, skillID, intonateTime, targetObject ):
		"""
		intonate
		@type		skillID	: INT
		@param	skillID	: skill id of intonate
		@return 			: None
		"""
		self.showSpellingItemCover( skillID )
		self.setCastingSpell( skillID )

	def castSpell( self, skillID, targetObject ):
		"""
		开始施法动作，重置吟唱技能id
		"""
		self.hideSpellingItemCover()
		self.setCastingSpell( 0 )
		if not hasattr( targetObject , "_entityID" ):
			return 
			
		targetID = targetObject._entityID
		skillInstance = Skill.getSkill( skillID )
		if targetID not in self.__damageList and targetID != self.id and skillInstance.isMalignant(): # 恶性技能才加入伤害列表
			self.__damageList.insert( -1, targetID )

	def intonating( self ):
		"""
		if player is in attacking state, it will return True
		"""
		return self.castingSpell != 0

	def setCastingSpell( self, skillID ):
		"""
		设置正在吟唱的技能id
		"""
		self.castingSpell = skillID

	def onStartHomingSpell( self ):
		"""
		define method.
		开始引导技能
		"""
		self.isInHomingSpell = True

	def onFiniHomingSpell( self ):
		"""
		结束引导技能
		"""
		self.isInHomingSpell = False

	def onSpellInterrupted( self, skillID, reason ):
		"""
		服务器中断吟唱的回调通知。
		attack interrupt has been accepted
		"""
		if reason != csstatus.SKILL_INTONATING:
			self.setCastingSpell( 0 )
			GUIFacade.onRoleSpellInterrupted()
		self.attackInstanceDict[ self.attackState ].onSpellInterrupted( skillID, reason )

	def onStateChanged( self, old, new ):
		"""
		when player's state is changed, it will be called
		"""
		self.attackInstanceDict[ self.attackState ].onStateChanged( old, new )
		if new == csdefine.ENTITY_STATE_DEAD:
			self.stopAutoRestore()

		if old == csdefine.ENTITY_STATE_DEAD:
			self.autoRestoreDetect()
		elif old == csdefine.ENTITY_STATE_FIGHT:
			self.resetAutoFightList()

	def onMoveChanged( self, isMoving ):
		"""
		change move state( from moving to standing or reverse )
		see also python_client.chm/Class list/getPhysics().isMovingNotifier
		@type		isMoving : bool
		@param		isMoving : indicate wether in moving state
		@return				 : None
		"""
		if isMoving:						# spelling is interupted when start moving
			if self.intonating() or self.isInHomingSpell:
				self.getPhysics().targetSource = None
				self.getPhysics().targetDest = None
				#self.flushAction()
			if not self.isInHomingSpell:
				self.interruptAttack( csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 )
		GUIFacade.onRoleMoved( isMoving )

	# --------------------------------- 自动战斗相关处理 -----------------------------------------
	def toggleAutoFight( self ):
		"""
		"""
		self.__toggleAutoFight()

	def onPetReceiveDamage( self, petTargetID ):
		if not self.isAutoFight(): return
		if petTargetID not in self.__damageList:
			self.__damageList.insert( -1, petTargetID )

	def onReceiveSpell( self, casterID, skillID, damageType, damage ):
		"""
		受到伤害
		"""
		if casterID not in self.__damageList:
			self.__damageList.insert( -1, casterID )
			try:
				target = BigWorld.entities[casterID]
			except KeyError:
				pass
			else:
				if target.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or target.isEntityType( csdefine.ENTITY_TYPE_PET ):
		 			spaceType = self.getCurrentSpaceType()
					if spaceType != csdefine.SPACE_TYPE_CITY_WAR:
						targetName = target.getName()
						if self.onFengQi:
							targetName = lbs_ChatFacade.masked
						self.statusMessage( csstatus.ATTACK_CAN_COUNTER, targetName )
		self.attackInstanceDict[ self.attackState ].onReceiveSpell( casterID )

	def getAutoFightList( self ):
		"""
		获得玩家的自动战斗目标id列表
		"""
		return self.__damageList

	def resetAutoFightList( self ):
		"""
		清空玩家自动战斗列表
		"""
		self.__damageList = []

	def inDamageList( self, entity ):
		"""
		entity是否在伤害列表里
		"""
		return entity.id in self.__damageList
	
	def getDamageLength( self ):
		"""
		获得伤害列表的长度
		"""
		return len( self.__damageList )

	def isAutoFight( self ):
		"""
		是否在自动战斗状态
		"""
		return self.attackState == Const.ATTACK_STATE_AUTO_FIGHT

	def __toggleAutoFight( self ):
		"""
		触发自动战斗
		"""
		if not self.hasAutoFight:
			if not self.pyBox is None:
				self.pyBox.visible = False
				self.pyBox = None
			self.pyBox = showMessage( mbmsgs[0x0ec6], "", MB_OK )
			return False
		if self.isAutoFight():
			self.stopAutoFight()
		else:
			self.changeAttackState( Const.ATTACK_STATE_AUTO_FIGHT )

	def change2AutoSpell( self ):
		"""
		转到自动使用技能攻击状态

		9:57 2009-2-16,新需求：退出自动战斗状态后则进入自动使用技能攻击状态。
		13:20 2009-3-20，规则更改为：退出自动战斗后如果处于战斗状态则进入自动使用技能攻击状态。
		"""
		self.changeAttackState( Const.ATTACK_STATE_NONE )

		if self.state == csdefine.ENTITY_STATE_FIGHT:
			# 延时hit_speed以后进入自动使用技能攻击状态，立即进入自动攻击状态的话有可能马上退出，
			# 因为普通物理攻击有可能刚刚使用正处于coolDown状态，使用技能使用不成功则会退出自动攻击状态。
			delay = self.hit_speed
			self.autoFight2AutoSpellTimerID = BigWorld.callback( delay, Functor( self.changeAttackState, Const.ATTACK_STATE_AUTO_SPELL ) )

	# ---------------------------------- 自动恢复 -------------------------------------
	def getRoleHpRestorePercent( self ):
		"""
		获得角色自动加血百分比值
		"""
		return self.roleAutoRestore.getHpPercent()

	def getRoleMpRestorePercent( self ):
		"""
		获得角色自动加蓝百分比值
		"""
		return self.roleAutoRestore.getMpPercent()

	def getPetHpRestorePercent( self ):
		"""
		获得宠物自动加血百分比值
		"""
		return self.petAutoRestore.getHpPercent()

	def getPetMpRestorePercent( self ):
		"""
		获得宠物自动加蓝百分比值
		"""
		return self.petAutoRestore.getMpPercent()

	def setRoleHpRestorePercent( self, percent ):
		"""
		设置角色自动加血百分比值
		"""
		sect = self.roleAutoRestore.getConfigSect()
		sect.writeFloat( "Role_HP", percent )
		self.roleAutoRestore.setHpPercent( percent )

	def setRoleMpRestorePercent( self, percent ):
		"""
		设置角色自动加蓝百分比值
		"""
		sect = self.roleAutoRestore.getConfigSect()
		sect.writeFloat( "Role_MP", percent )
		self.roleAutoRestore.setMpPercent( percent )

	def setPetHpRestorePercent( self, percent ):
		"""
		设置宠物自动加血百分比值
		"""
		sect = self.petAutoRestore.getConfigSect()
		sect.writeFloat( "Pet_HP", percent )
		self.petAutoRestore.setHpPercent( percent )

	def setPetMpRestorePercent( self, percent ):
		"""
		设置宠物自动加蓝百分比值
		"""
		sect = self.petAutoRestore.getConfigSect()
		sect.writeFloat( "Pet_MP", percent )
		self.petAutoRestore.setMpPercent( percent )

	# ---------------------自动战斗配置---------------------
	def stopAutoFight( self ):
		"""
		停止自动战斗
		"""
		self.change2AutoSpell()


	def setAutoFightConfig( self, config = {} ):
		"""
		设置自动战斗相关配置
		@ param : config 配置字典
		@ param : congig DICT
		"""
		if len( config ) == 0:
			self.autoFightConfig = {
									"isAutoPickUp":False,
									"isAutoConjure":True,
									"isAutoAddJoy":True,
									"isAutoPlus":False,
									"radius":0,
									"radiusAdd":15,
									"joyLess":0,
									"autoRepair":False,
									"autoReboin":False,
									"repairRate":0,
									"isIgnorePickUp":True,
									"pickUpTypeList":[],
									"ignoredList":[]
									}
		else:
			self.autoFightConfig = config
		cfgSect = self.roleAutoRestore.getConfigSect()
		for secKey, value in self.autoFightConfig.items():
			if not cfgSect.has_key( secKey ):
				cfgSect.createSection( secKey )
			if secKey in ["isAutoConjure", "isAutoAddJoy", "isAutoPlus", "autoRepair", "autoReboin", "isIgnorePickUp"]:
				cfgSect.writeBool( secKey, value )
			elif secKey in ["radius", "radiusAdd", "joyLess", "repairRate"]:
				cfgSect.writeInt( secKey, value )
		self.roleAutoRestore.saveCfgSect()
		AutoFightConfig["AutoFightConfig"] = self.autoFightConfig
		
	def setIgnorePickUp( self, value ):
		"""
		设置是否忽略自动拾取配置
		value is bool
		"""
		self.autoFightConfig["isIgnorePickUp"] = value
		cfgSect = self.roleAutoRestore.getConfigSect()
		if not cfgSect.has_key( "isIgnorePickUp" ):
			cfgSect.createSection( "isIgnorePickUp" )
		cfgSect.writeBool( "isIgnorePickUp", value )
		self.roleAutoRestore.saveCfgSect()
		
	def addPickType( self, itemType ):
		"""
		增加自动拾取类型
		"""
		ptl = self.autoFightConfig["pickUpTypeList"]
		if itemType in ptl:
			return
		ptl.append( itemType )
		
	def removePickType( self, itemType ):
		"""
		移除自动拾取类型
		"""
		ptl = self.autoFightConfig["pickUpTypeList"]
		if not itemType in ptl:
			return
		ptl.remove( itemType )
	
	def getPickUpTypes( self, isIgnored ):
		"""
		获取已设置自动拾取物品类型列表
		"""
		cfgSect = self.roleAutoRestore.getConfigSect()
		pickUpTypeList = []
		if not isIgnored: #拾取表
			if cfgSect.has_key( "pickUpTypeList" ):
				typesStr = cfgSect.readString( "pickUpTypeList" ).split( "|" )
				for typeStr in typesStr:
					if typeStr == "":continue
					pickUpTypeList.append( int( typeStr ) )
		else: #
			if cfgSect.has_key( "ignoredList" ):
				typesStr = cfgSect.readString( "ignoredList" ).split( "|" )
				for typeStr in typesStr:
					if typeStr == "":continue
					pickUpTypeList.append( int( typeStr ) )
		return pickUpTypeList
	
	def setPickUpTypes( self, isIgnored, itemTypes = [] ):
		"""
		设置自动拾取物品类型列表
		"""
		cfgSect = self.roleAutoRestore.getConfigSect()
		typesStr = ""
		for itemType in itemTypes:
			typesStr += "%s|"%str( itemType )
		if not isIgnored:
			if not cfgSect.has_key( "pickUpTypeList" ):
				cfgSect.createSection( "pickUpTypeList" )
			cfgSect.writeString( "pickUpTypeList", typesStr )
			self.autoFightConfig["pickUpTypeList"] = itemTypes
		else:
			if not cfgSect.has_key( "ignoredList" ):
				cfgSect.createSection( "ignoredList" )
			cfgSect.writeString( "ignoredList", typesStr )
			self.autoFightConfig["ignoredList"] = itemTypes
		self.roleAutoRestore.saveCfgSect()
		
	def setAutoRepair( self, value ):
		"""
		设置自动修理
		value is bool
		"""
		cfgSect = self.roleAutoRestore.getConfigSect()
		cfgSect.writeBool( "autoRepair", value )
		self.autoFightConfig["autoRepair"] = value
		AutoFightConfig["AutoFightConfig"] = self.autoFightConfig
		self.roleAutoRestore.saveCfgSect()
		
	def isAutoRepair( self ):
		"""
		是否自动修理状态
		"""
		return self.autoFightConfig["autoRepair"]
		
	def setAutoRepairRate( self, value ):
		"""
		设置自动修理百分比
		value is int
		"""
		cfgSect = self.roleAutoRestore.getConfigSect()
		cfgSect.writeInt( "repairRate", value )
		self.autoFightConfig["repairRate"] = value
		AutoFightConfig["AutoFightConfig"] = self.autoFightConfig
		self.roleAutoRestore.saveCfgSect()
		
	def getAutoRepairRate( self ):
		"""
		获得自动修理百分比
		"""
		return self.autoFightConfig["repairRate"]
		
	def setAutoReboin( self, value ):
		"""
		设置自动复活
		value is bool
		"""
		cfgSect = self.roleAutoRestore.getConfigSect()
		cfgSect.writeBool( "autoReboin", value )
		self.autoFightConfig["autoReboin"] = value
		AutoFightConfig["AutoFightConfig"] = self.autoFightConfig
		self.roleAutoRestore.saveCfgSect()
		
	def isAutoReboin( self ):
		"""
		是否自动复活状态
		"""
		return self.autoFightConfig["autoReboin"]

	def setAutoRange( self, r ):
		"""
		test interface
		"""
		cfgSect = self.roleAutoRestore.getConfigSect()
		cfgSect.writeInt( "radius", value )
		self.autoFightConfig["radius"] = r
		AutoFightConfig["AutoFightConfig"] = self.autoFightConfig
		self.roleAutoRestore.saveCfgSect()

	def getAutoFightConfig( self ):
		"""
		"""
		cfgSect = self.roleAutoRestore.getConfigSect()
		autoConfig = {
						"isAutoConjure":cfgSect.readBool("isAutoConjure"),
						"isAutoAddJoy":cfgSect.readBool("isAutoAddJoy"),
						"isAutoPlus":cfgSect.readBool("isAutoPlus"),
						"radius":cfgSect.readInt("radius"),
						"radiusAdd":cfgSect.readInt("radiusAdd"),
						"joyLess":cfgSect.readInt("joyLess"),
						"autoRepair":cfgSect.readBool("autoRepair"),
						"autoReboin":cfgSect.readBool("autoReboin"),
						"repairRate":cfgSect.readInt("repairRate"),
						"isAutoPickUp":cfgSect.readBool("isAutoPickUp"),
						"plusSkillTarget":cfgSect.readVector3("plusSkillTarget"),
						"isIgnorePickUp":cfgSect.readBool("isIgnorePickUp"),
						"pickUpTypeList":self.getPickUpTypes( False ),
						"ignoredList": self.getPickUpTypes( True )
					}
		return autoConfig

	def onRemoveSkill( self, skillID ):
		"""
		移除技能对战斗系统的影响 by 姜毅
		"""
		if skillID in self.autoPlusSkillList:
			self.autoPlusSkillList.remove(skillID)
		AutoFightConfig["autoPlusSkillList"] = self.autoPlusSkillList
		skIDStr = ""
		for skID in self.autoPlusSkillList:
			skIDStr += "%s|"%str( skID )
		cfgSect = self.roleAutoRestore.getConfigSect()
		cfgSect.writeString( "plusSkills", skIDStr )
		self.roleAutoRestore.saveCfgSect()

	# --------------------------------------------- 自动拾取 -----------------------------------------
	def onItemDrop( self, dropEntity ):
		"""
		有物品掉落的通知

		@param dropEntity :	掉落箱子entity
		@type dropEntity :		BigWorld entity
		"""
		self.attackInstanceDict[ self.attackState ].onItemDrop( dropEntity )

	def useSkill( self, skillID ):
		"""
		通过快捷键使用技能

		@param skillID:	技能ID
		@type skillID :	int64
		"""
		# 如果使用的是普通物理攻击三连击技能，则进入自动普通物理三连击连续攻击状态
		if skillID == Define.SKILL_ID_TRIGGER_SKILLS.get( self.getClass() ):
			self.setLastUseAutoSkillID( skillID )
			self.changeAttackState( Const.ATTACK_STATE_NORMAL )
			return
		# 如果使用的是引导连续攻击技能，则进入自动引导连续攻击状态
		sk = Skill.getSkill( skillID )
		isHomingSpell = sk.isHomingSkill()
		if isHomingSpell:
			if not sk.isNormalHomingSkill(): #如果是引导连续技能接普通攻击技能 add by wuxo 2011-12-12
				self.setLastUseAutoSkillID( skillID )
				self.changeAttackState( Const.ATTACK_STATE_HOMING_SPELL )
				return

		
		from skills import Spell_Cursor
		from skills import Spell_Position
		if isinstance( sk, Spell_Cursor.Spell_Cursor) or isinstance( sk, Spell_Position.Spell_Position)  :
			self.changeAttackState( Const.ATTACK_STATE_AUTO_SPELL_CURSOR, skillID )
			return

		# 如果使用的是良性技能，则进入技能攻击一次状态状态
		# 否则，根据最后一次使用的是普通物理攻击/引导连续攻击技能
		# 进入相对应的攻击状态
		lastUseSkillID = self.getLastUseAutoSkillID()
		self.changeAttackState( Const.ATTACK_STATE_ONCE, skillID )

	def onLClickTargt( self ):
		"""
		左键点击攻击目标
		"""
		
		lastUseSkillID = self.getLastUseAutoSkillID()
		if lastUseSkillID == Define.SKILL_ID_TRIGGER_SKILLS.get( self.getClass() ):
			self.changeAttackState( Const.ATTACK_STATE_ONCE,lastUseSkillID )
		else:
			self.changeAttackState( Const.ATTACK_STATE_HOMING_SPELL )

	def onRClickTargt( self ):
		"""
		右键点击攻击目标
		"""
		lastUseSkillID = self.getLastUseAutoSkillID()
		if lastUseSkillID == Define.SKILL_ID_TRIGGER_SKILLS.get( self.getClass() ):
			self.changeAttackState( Const.ATTACK_STATE_HOMING_SPELL )
		else:
			self.changeAttackState( Const.ATTACK_STATE_AUTO_SPELL_HOMING )
