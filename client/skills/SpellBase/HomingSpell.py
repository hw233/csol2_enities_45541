# -*- coding: gb18030 -*-
#
# $Id: Spell.py,v 1.00 14:08 2010-3-18 jiangyi Exp $

"""
HomingSpell技能类。
"""
from Spell import Spell
import skills
from gbref import rds
import BigWorld
import ItemTypeEnum
from bwdebug import *
import csdefine
import Define
import csstatus
import math
import Math
from config.skill.Skill.SkillDataMgr import Datas as SKILL_DATA

class HomingSpell( Spell ):
	"""
	引导技能模块
	"""
	def __init__( self ):
		"""
		构造SkillBase
		"""
		Spell.__init__( self )
		self.childSkill = None

	def isHomingSkill( self ):
		"""
		判断是否引导技能 	by 姜毅
		@return: BOOL
		"""
		return True
	
	def isNormalHomingSkill( self ):
		"""
		判断是否引导普通攻击技能 by wuxo
		@return: BOOL
		"""
		return False

	def interrupt( self, caster, reason ):
		"""
		中止施放技能。
		@param caster:			施放者Entity
		@type caster:			Entity
		"""
		if reason in [csstatus.SKILL_NOT_READY,csstatus.SKILL_CANT_CAST]:return
		if reason == csstatus.SKILL_INTERRUPTED_BY_TIME_OVER :return
		Spell.interrupt( self, caster, reason )
		rds.skillEffect.stopHomingEffects( caster )
		model = caster.getModel()
		if model is None:return
		for name in model.queue:
			rds.actionMgr.stopAction( caster.getModel(), name )

	def rotate( self, caster, receiver ):
		"""
		转动方向
		"""
		if caster.id == receiver.id:
			return
		#中了昏睡、眩晕、定身等效果时不能自动转向
		EffectState_list = csdefine.EFFECT_STATE_FIX | csdefine.EFFECT_STATE_VERTIGO | csdefine.EFFECT_STATE_SLEEP | csdefine.EFFECT_STATE_BE_HOMING
		if caster.effect_state & EffectState_list != 0: return
		
		new_yaw = (receiver.position - caster.position).yaw
		BigWorld.player().am.turnModelToEntity = 0
		BigWorld.player().model.yaw = new_yaw
		BigWorld.dcursor().yaw = new_yaw
		BigWorld.player().am.turnModelToEntity = 1
	
	def cast( self, caster, targetObject ):
		"""
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		if caster.id == BigWorld.player().id:
			target = targetObject.getObject()
			skillID = self.getID()
			childID = int( SKILL_DATA.__getitem__( skillID )["param2"].split(",")[0] )
			param4 = SKILL_DATA.__getitem__( childID )["param4"].split(";")
			attackTargetDis = 0.0
			attackTrackDis = 6.0
			if len( param4 ) >= 2:
				attackTargetDis = float( param4[0] )
				attackTrackDis = float( param4[1] )
			caster.setPhysicsHoming( attackTargetDis, attackTrackDis, target )
		Spell.cast( self, caster, targetObject )
		

class NormalHomingSpell( HomingSpell ):
	"""
	引导普通攻击技能模块by wuxo
	"""
	def isNormalHomingSkill( self ):
		"""
		判断是否引导普通攻击技能 
		@return: BOOL
		"""
		return True
	
	def __idConvert( self, skillID ):
		"""
		转换技能ID为系列ID
		如：311120001 -> 311120
		程序自定义技能ID无需转换
		"""
		# 技能ID小于1000为程序自用，不需转换
		if skillID < csdefine.SKILL_ID_LIMIT:
			return skillID
		return skillID/1000

	def getIcon( self ):
		"""
		三连击技能图标使用武器图标图标
		"""
		id = self.__idConvert( self.getID() )
		if not id in Define.TRIGGER_SKILL_IDS: 
			return Spell.getIcon( self )
		pl = BigWorld.player()
		try:
			if pl.primaryHandEmpty():
				return Spell.getIcon( self )
			else:
				item = pl.getItem_( ItemTypeEnum.CWT_RIGHTHAND )
				return item.icon()
		except AttributeError, errstr:
			WARNING_MSG( errstr )
			return Spell.getIcon( self )