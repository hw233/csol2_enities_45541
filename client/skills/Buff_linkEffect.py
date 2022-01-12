# -*- coding: gb18030 -*-

import BigWorld
import Const
import Define
import Math
from bwdebug import *
from SpellBase import *
from gbref import rds
from Function import Functor

class Buff_linkEffect( Buff ):
	"""
	连线光效Buff客户端脚本（只针对不动的实体）
	"""
	def __init__( self ):
		"""
		从sect构造SkillBase
		@param sect:			技能配置文件的XML Root Section
		@type sect:				DataSection
		"""
		Buff.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置字典数据
		@type dict:				Python dict
		"""
		Buff.init( self, dict )

	def playEffect( self, caster, target ):
		"""
		播放buff效果
		"""
		skillID = self.getEffectID() * 1000
		if hasattr( caster, "isLoadModel" ) and caster.isLoadModel:
			caster.delayCastEffects.append( Functor( self.playLinkEffects, caster, target, skillID ) )
		else:
			self.playLinkEffects( caster, target, skillID )

		# buff动作效果，一般体现在BUFF接受者身上
		self.pose.buffCast( target, skillID )

	def playLinkEffects( self, caster, target, skillID ):
		"""
		连线光效buff效果
		"""
		target.buffEffect[skillID] = {}
		# 光效
		weaponType = 0
		casterID = 0
		cModel = None
		tModel = None
		cType = Define.TYPE_PARTICLE_PLAYER
		tType = Define.TYPE_PARTICLE_PLAYER
		if caster:
			weaponType = caster.weaponType
			casterID = caster.id
		dict = rds.spellEffect.getCastEffect( skillID, casterID, weaponType )
		if dict:
			if caster:
				pyModel = BigWorld.Model( Const.EMPTY_MODEL_PATH_1 )	# 用BoundingBox较大的空模型替代原有的实体模型
				caster.addModel( pyModel )
				caster.linkEffectModel = pyModel
				pyModel.position = caster.position + Math.Vector3( 0, 1, 0 )
				pyModel.yaw = caster.yaw
				cModel = pyModel
				cType = caster.getParticleType()
			if target:
				tModel = target.getModel()
				tType = target.getParticleType()

			effect = rds.skillEffect.createEffect( dict, cModel, tModel, cType, tType )
			if effect:
				effect.start()
				target.buffEffect[skillID]["buff_effect"] = effect

			if effect.__class__.__name__ == "LinkEffect":
				caster.linkEffect.append( effect )
				target.linkEffect.append( effect )

		# 声音
		soundNames = rds.spellEffect.getSpellCastSound( skillID )
		target.buffEffect[skillID]["buff_sound"] = soundNames
		for name in soundNames:
			rds.skillEffect.playSound( target, name )

	def end( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		Buff.end( self, caster, target )
		caster.delModel( caster.linkEffectModel )
		caster.linkEffectModel = None
