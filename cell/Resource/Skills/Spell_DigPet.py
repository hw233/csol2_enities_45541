# -*- coding: gb18030 -*-
#
# $Id: Spell_DigPet.py,v 1.9 2008-08-02 09:24:52 songpeifang Exp $

"""
召唤玩家宠物
"""
import BigWorld

import csdefine
import csstatus
import csconst
from bwdebug import *

import Const
from SpellBase import *
from PetFormulas import formulas
import utils

class Spell_DigPet( Spell ):
	"""
	召唤玩家宠物
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )

	def use( self, caster, target ):
		"""
		virtual method.
		请求对 target/position 施展一个法术，任何法术的施法入口由此进。
		dstEntity和position是可选的，不用的参数用None代替，具体看法术本身是对目标还是位置，一般此方法都是由client调用统一接口后再转过来。
		默认啥都不做，直接返回。
		注：此接口即原来旧版中的cast()接口
		@param   caster: 施法者
		@type    caster: Entity

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		if caster.attrIntonateSkill and caster.attrIntonateSkill.getID() == self.getID() or\
			( caster.attrHomingSpell and caster.attrHomingSpell.getType() in Const.INTERRUPTED_BASE_TYPE ) :
			caster.interruptSpell( csstatus.SKILL_NO_MSG )
		Spell.use( self, caster, target )

	def useableCheck( self, caster, target ) :
		if caster.attrIntonateSkill and caster.attrIntonateSkill.getID() == self.getID() or\
			( caster.attrHomingSpell and caster.attrHomingSpell.getType() in Const.INTERRUPTED_BASE_TYPE ) :
			caster.interruptSpell( csstatus.SKILL_NO_MSG )
	
		#处理沉默等一类技能的施法判断
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB

		status = Spell.useableCheck( self, caster, target )
		if status == csstatus.SKILL_GO_ON :
			ownerLevel = caster.level
			dbid = caster.queryTemp( "pcg_conjuring_dbid" )
			if not caster.pcg_petDict.has_key( dbid ) :														# 要出征的宠物不存在
				status = csstatus.PET_CONJURE_FAIL_NOT_EXIST
			elif caster.pcg_isActPet( dbid ) :																# 要出征的宠物已经处于出征状态
				status = csstatus.PET_CONJURE_FAIL_CONJURED
			elif ownerLevel < caster.pcg_petDict.get( dbid ).takeLevel:										# 玩家低于宠物可挈带等级也不能召唤 by姜毅
				status = csstatus.SKILL_PET_NOT_TAKE_LEVEL
			elif ownerLevel < caster.pcg_petDict.get( dbid ).level - csconst.PET_CONJURE_OVER_LEVEL :		# hyw( 2008.05.23 )
				status = csstatus.PET_CONJURE_FAIL_LESS_LEVEL
		if status != csstatus.SKILL_GO_ON :
			caster.pcg_onConjureResult( 0, None )
			caster.statusMessage( status )																	# 输出召唤失败的原因
		# 防止其他原因导致的不可施法
		if caster.actionSign( csdefine.ACTION_FORBID_SPELL ):
			return csstatus.SKILL_CANT_CAST
		return status
		
	def cast( self, caster, target ):
		"""
		virtual method.
		正式向一个目标或位置施放（或叫发射）法术，此接口通常直接（或间接）由intonate()方法调用。

		注：此接口即原来旧版中的castSpell()接口

		@param     caster: 使用技能的实体
		@type      caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		# 引导技能检测
		caster.delHomingOnCast( self )
		self.setCooldownInIntonateOver( caster )
		# 处理消耗
		self.doRequire_( caster )
		#通知所有客户端播放动作/做其他事情
		caster.planesAllClients( "castSpell", ( self.getID(), target ) )
		
		# 法术施放完毕通知，不一定能打中人哦(是否能打中已经和施法没任何关系了)！
		# 如果是channel法术(未实现)，只有等法术结束后才能调用
		self.onSkillCastOver_( caster, target )
		
		#保证客户端和服务器端处理的受术者一致
		caster.addCastQueue( self, target, 2.0 )

	def onSpellInterrupted( self, caster ):
		"""
		当施法被打断时的通知；
		打断后需要做一些事情
		"""
		Spell.onSpellInterrupted( self, caster )
		caster.removeTemp( "pcg_conjuring_dbid" )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		dbid = receiver.queryTemp( "pcg_conjuring_dbid" )
		if dbid is None :
			ERROR_MSG( "conjure pet fail, can find pet" )
			return
		position = formulas.getPosition( caster.position, caster.yaw )
		# 宠物entity与地表做碰撞，确保可以放在地面上
		pos = utils.navpolyToGround( caster.spaceID, position, 5.0, 5.0 )
		receiver.base.pcg_conjurePet( dbid, pos, caster.direction )
