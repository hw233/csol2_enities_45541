# -*- coding: gb18030 -*-


from bwdebug import *
from Skill_Normal import Skill_Normal
import BigWorld
import csconst
import csstatus
import csdefine
import random


class Skill_Damage( Skill_Normal ):
	"""
	被动技能 产生伤害类
	
	目前还不完善,仅加入了目前为止确定的一些行为以适应装备附加属性技能的需求,
	以后需要对被动技能结构进行总体规划.11:14 2008-10-24,wsf
	"""
	def __init__( self ):
		"""
		"""
		Skill_Normal.__init__( self )
		
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Skill_Normal.init( self, dict )
		
		
	def calcProperty( self, baseVal, extraVal, percentVal, value ):
		"""
		创世基础计算总公式
		计算值=（基础值+附加值）*（1+加成）+加值
		@param baseVal: 基础值
		@param extraVal: 附加值
		@param percentVal: 加成
		@param value: 加值
		"""
		return ( baseVal + extraVal ) * ( 1 + percentVal ) + value
		
		
	def calcHitProbability( self, source, target ):
		"""
		virtual method.
		计算命中率
		
		
		基础物理命中率（总公式中的基础值）=95% -（被攻击方等级-攻击方等级）^1.61*3%
		
		如果（被攻击方等级-攻击方等级）<0，则（被攻击方等级-攻击方等级）=0项计为0。
		如果95% -（被攻击方等级-攻击方等级）^1.61*3%<1%。则此项取1%。
		@param source:	攻击方
		@type  source:	entity
		@param target:	被攻击方
		@type  target:	entity
		return type:	Float
		"""
		ERROR_MSG( "This is virtual method." )
		
		
	def calcVictimResist( self, source, target ):
		"""
		virtual method.
		计算被攻击方物理防御减伤
		角色基础物理防御值（总公式中的基础值）=0
		物理防御减伤（总公式中的基础值）=物理防御值/（物理防御值+45*攻击方等级+350）
		在攻防的计算中，防御值会先换算成防御减伤，然后再和攻击力进行换算。
		@param source:	攻击方
		@type  source:	entity
		@param target:	被攻击方
		@type  target:	entity
		@return: FLOAT
		"""
		ERROR_MSG( "This is virtual method." )
		
		
	def calcDamageScissor( self, caster, receiver, damage ):
		"""
		virtual method.
		计算被攻击方物理伤害削减
		伤害=物理伤害x (1 – 被攻击方物理伤害减免率) 
		– 被攻击方物理伤害减免值
		伤害下限为0。
		注：伤害为DOT型持续伤害则对其伤害总值削减后再分次作用。
		其中，物理伤害减免率及物理伤害减免值参考公式文档，公式如下：
		角色基础物理伤害减免点数（总公式中的基础值）=0
		角色基础物理伤害减免值（总公式中的基础值）=0
		@param target: 被攻击方
		@type  target: entity
		@param  damage: 经过招架判断后的伤害
		@type   damage: INT
		@return: INT32
		"""
		return caster.calcDamageScissor( receiver, damage )
		
		
	def calcDoubleMultiple( self, caster ):
		"""
		virtual method.
		计算暴击伤害加倍
		@param caster: 被攻击方
		@type  caster: entity
		@return type:计算后得到的暴击倍数
		"""
		ERROR_MSG( "This is virtual method." )
		return 1.0
		
	def isDoubleHit( self, caster, receiver ):
		"""
		virtual method.
		判断攻击者是否爆击
		return type:bool
		"""
		ERROR_MSG( "This is virtual method." )
		
		
	def calcSkillHitStrength( self, source, receiver,dynPercent, dynValue ):
		"""
		virtual method.
		计算技能攻击力
		方式1：技能攻击力（总公式中的基础值）=技能本身的攻击力+角色的物理攻击力
		带入总公式中就是：（技能本身的攻击力+角色物理攻击力）*（1+物理攻击力加成）+物理攻击力加值
		@param source:	攻击方
		@type  source:	entity
		@param dynPercent:	在本次攻击流程中可能会有外部其他技能导致额外的 技能攻击力加成
		@param  dynValue:	在本次攻击流程中可能会有外部其他技能导致额外的 技能攻击力加值
		"""
		return random.randint( self._effect_min, self._effect_max )
		