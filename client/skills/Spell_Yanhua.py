# -*- coding: gb18030 -*-
#
# $Id: Spell_311101.py,v 1.3 2008-03-10 01:01:25 kebiao Exp $

"""
Spell技能类。
"""
import BigWorld
from bwdebug import *
from SpellBase import *
import csstatus
import csdefine
import random
import Const
from Function import Functor
from gbref import rds
import Math

class Spell_Yanhua( Spell ):
	def __init__( self ):
		"""
		从python dict构造SkillBase
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type dict:				python dict
		"""
		Spell.init( self, dict )

	def useableCheck( self, caster, receiver ):
		"""
		virtual method.
		校验技能是否可以使用
		"""
		# 只能在自由状态下使用
		if caster.state != csdefine.ENTITY_STATE_FREE:
			return csstatus.SKILL_NEED_STATE_FREE
		return Spell.useableCheck( self, caster, receiver )

	def cast( self, caster, targetObject ):
		"""
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		#spell.cast( self, caster, targetObject )
		loadedFuc = Functor( self.__onEnptyModelEnd, caster )
		rds.effectMgr.addModelBGInPos( caster.getModel(), Const.YANHUA_START_HP, [Const.EMPTY_MODEL_PATH], loadedFuc )

	def __onEnptyModelEnd( self, caster, model ):
		"""
		空模型加载完毕
		"""
		if model is None: return
		if not model.inWorld: return
		if not caster.inWorld: return
		rds.effectMgr.createParticleBG( model, Const.YANHUA_END_HP, Const.YANHUA_SHE_PATH, type = caster.getParticleType() )

		homer = BigWorld.Homer()
		homer.speed = 10.0
		homer.proximity = 0.36
		homer.turnAxis = ( 0, 1, 0 )
		homer.turnRate = 314.159
		model.addMotor( homer )

		hight = random.random() * 10 + 5
		pos = ( caster.position.x, caster.position.y + hight, caster.position.z )
		matrix = Math.Matrix()
		matrix.setTranslate( pos )
		homer.target = matrix

		stopFunc = Functor( self.__onFlyEnd, caster, model )
		homer.proximityCallback = stopFunc

	def __onFlyEnd( self, caster, model ):
		"""
		"""
		if model is None: return
		if not model.inWorld: return
		if not caster.inWorld: return

		for p in model.node( Const.YANHUA_END_HP ).attachments:
			rds.effectMgr.fadeOutParticle( p )
		rds.effectMgr.createParticleBG( model, Const.YANHUA_END_HP, self._datas["param1"], type = caster.getParticleType() )

		deleteFunc = Functor( self.__delete, model )
		BigWorld.callback( 5.0, deleteFunc )

	def __delete( self, model ):
		"""
		"""
		player = BigWorld.player()
		if player is None: return

		if not player.inWorld: return

		listModels = list( player.models )

		if model in listModels:
			model.motors = ()
			player.delModel( model )
