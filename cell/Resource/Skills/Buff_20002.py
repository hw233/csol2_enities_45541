# -*- coding: gb18030 -*-

import BigWorld
import csconst
import csdefine
import csstatus
from bwdebug import *
from Buff_Normal import Buff_Normal

class Buff_20002( Buff_Normal ):
	"""
	潜行buff
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = ( int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  / 100.0 ) * csconst.FLOAT_ZIP_PERCENT
		self._p2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )

	def springOnUseMaligSkill( self, caster, skill ):
		"""
		使用恶性技能被触发
		"""
		buffID = self.getBuffID()
		caster.removeAllBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )

	def springOnDamage( self, caster, skill ):
		"""
		接收伤害后
		"""
		buffID = self.getBuffID()
		caster.removeAllBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )

	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果开始的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		# 使用恶性技能后触发（伤害计算后）
		receiver.appendOnUseMaligSkill( buffData[ "skill" ] )
		# 被命中后
		receiver.appendVictimHit( buffData[ "skill" ] )
		#CSOL-1239这里由于策划要求被删掉，暂时注释防止以后要改回来
		## 根据接收者不同有不同的效果，策划认为宠物不受暴击的影响
		#if not receiver.isEntityType( csdefine.ENTITY_TYPE_PET ) and receiver.getClass() == csdefine.CLASS_SWORDMAN:
		#	# 暴击100%
		#	receiver.double_hit_probability_value += csconst.FLOAT_ZIP_PERCENT
		#	receiver.calcDoubleHitProbability()
		#	receiver.magic_double_hit_probability_value += csconst.FLOAT_ZIP_PERCENT
		#	receiver.calcMagicDoubleHitProbability()
		#	# 被暴击100%
		#	receiver.be_double_hit_probability += csconst.FLOAT_ZIP_PERCENT
		#	receiver.be_magic_double_hit_probability += csconst.FLOAT_ZIP_PERCENT
		# 移动速度-50%
		receiver.move_speed_percent -= self._p1
		receiver.calcMoveSpeed()
		# 潜行等级值修正
		receiver.sneakLevelAmend += self._p2
		# 隐匿标志
		receiver.effectStateInc( csdefine.EFFECT_STATE_PROWL )

	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果重新加载的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		# 使用恶性技能后触发（伤害计算后）
		receiver.appendOnUseMaligSkill( buffData[ "skill" ] )
		# 被命中后
		receiver.appendVictimHit( buffData[ "skill" ] )
		
		## 根据接收者不同有不同的效果，策划认为宠物不受暴击的影响
		#if not receiver.isEntityType( csdefine.ENTITY_TYPE_PET ) and receiver.getClass() == csdefine.CLASS_SWORDMAN:
		#	# 暴击100%
		#	receiver.double_hit_probability_value += csconst.FLOAT_ZIP_PERCENT
		#	receiver.calcDoubleHitProbability()
		#	receiver.magic_double_hit_probability_value += csconst.FLOAT_ZIP_PERCENT
		#	receiver.calcMagicDoubleHitProbability()
		#	# 被暴击100%
		#	receiver.be_double_hit_probability += csconst.FLOAT_ZIP_PERCENT
		#	receiver.be_magic_double_hit_probability += csconst.FLOAT_ZIP_PERCENT
		# 移动速度-50%
		receiver.move_speed_percent -= self._p1
		# 潜行等级值修正
		receiver.sneakLevelAmend += self._p2
		# 隐匿标志
		receiver.effectStateInc( csdefine.EFFECT_STATE_PROWL )

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		# 使用恶性技能后触发（伤害计算后）
		receiver.removeOnUseMaligSkill( buffData[ "skill" ].getUID() )
		# 被命中后
		receiver.removeVictimHit( buffData[ "skill" ].getUID() )
		## 根据接收者不同有不同的效果，策划认为宠物应该不受暴击的影响
		#
		#if not receiver.isEntityType( csdefine.ENTITY_TYPE_PET ) and receiver.getClass() == csdefine.CLASS_SWORDMAN:
		#	# 暴击100%
		#	receiver.double_hit_probability_value -= csconst.FLOAT_ZIP_PERCENT
		#	receiver.calcDoubleHitProbability()
		#	receiver.magic_double_hit_probability_value -= csconst.FLOAT_ZIP_PERCENT
		#	receiver.calcMagicDoubleHitProbability()
		#	# 被暴击100%
		#	receiver.be_double_hit_probability -= csconst.FLOAT_ZIP_PERCENT
		#	receiver.be_magic_double_hit_probability -= csconst.FLOAT_ZIP_PERCENT
		# 移动速度50%
		receiver.move_speed_percent += self._p1
		receiver.calcMoveSpeed()
		# 潜行等级值修正
		receiver.sneakLevelAmend -= self._p2
		# 隐匿标志
		receiver.effectStateDec( csdefine.EFFECT_STATE_PROWL )

		buffID = self.getBuffID()
		if receiver.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = receiver.getOwner()
			if owner.etype == "REAL":
				owner.entity.removeAllBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )
			else:
				owner.entity.remoteCall( "removeAllBuffByBuffID",( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] ))
			#如果之前是主动状态，破隐后还原
			mode = receiver.queryTemp("Snake_buff", -1)
			if mode != -1:
				receiver.tussleMode = mode
			receiver.removeTemp("Snake_buff")
		elif receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			
			#解除潜行Buff后触发附近陷阱  by 陈晓鸣 2010-09-28
			receiver.onRemoveBuffProwl()
		
			actPet = receiver.pcg_getActPet()
			if actPet:
				if actPet.etype == "REAL":
					actPet.entity.removeAllBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )
				else:
					actPet.entity.remoteCall( "removeAllBuffByBuffID", ( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] ) )
			