# -*- coding:gb18030 -*-

from Spell_Magic import Spell_Magic
import csconst
import random

class Spell_MagicImprove( Spell_Magic ):
	"""
	可配置玩家法术、火、玄、雷、冰伤害比例的技能类
	param1配置法术、火、玄、雷、冰伤害比例，例如10;0;150;0;0，使用分号隔开，10表示10%，0表示没有提升比例。
	"""
	def __init__( self ):
		"""
		"""
		Spell_Magic.__init__( self )
		self.magicPercent = 0
		self.huoPercent = 0
		self.xuanPerent = 0
		self.leiPercent = 0
		self.bingPercent = 0
		
	def init( self, data ):
		"""
		"""
		Spell_Magic.init( self, data )
		percentParam = data["param1"] if len( data["param1"] ) > 0 else "0;0;0;0;0"
		percentList = [ int( param )/ 100.0 for param in percentParam.split( ";" ) ]
		self.magicPercent = percentList[0]
		self.huoPercent = percentList[1]
		self.xuanPerent = percentList[2]
		self.leiPercent = percentList[3]
		self.bingPercent = percentList[4]
		
	def calcElemDamage( self, caster, receiver, attackdamage = 0 ):
		"""
		virtual method.
		计算元素伤害
		"""
		elemEffect = caster.queryTemp( "ELEM_ATTACK_EFFECT", "" )
		if elemEffect == "huo":		# 火元素攻击效果
			return [ caster.elem_huo_damage * (1+self.huoPercent) + self._huo_damage + attackdamage, \
					caster.elem_xuan_damage * (1+self.xuanPerent) + self._xuan_damage, \
					caster.elem_lei_damage * (1+self.leiPercent) + self._lei_damage, \
					caster.elem_bing_damage * (1+self.bingPercent) + self._bing_damage ]
		elif elemEffect == "xuan":	# 玄元素攻击效果
			return [ caster.elem_huo_damage * (1+self.huoPercent) + self._huo_damage, \
					caster.elem_xuan_damage * (1+self.xuanPerent) + self._xuan_damage + attackdamage, \
					caster.elem_lei_damage * (1+self.leiPercent) + self._lei_damage, \
					caster.elem_bing_damage * (1+self.bingPercent) + self._bing_damage ]
		elif elemEffect == "lei":	# 雷元素攻击效果
			return [ caster.elem_huo_damage * (1+self.huoPercent) + self._huo_damage, \
					caster.elem_xuan_damage * (1+self.xuanPerent) + self._xuan_damage, \
					caster.elem_lei_damage * (1+self.leiPercent) + self._lei_damage + attackdamage, \
					caster.elem_bing_damage * (1+self.bingPercent) + self._bing_damage ]
		elif elemEffect == "bing":	# 冰元素攻击效果
			return [ caster.elem_huo_damage * (1+self.huoPercent) + self._huo_damage, \
					caster.elem_xuan_damage * (1+self.xuanPerent) + self._xuan_damage, \
					caster.elem_lei_damage * (1+self.leiPercent) + self._lei_damage, \
					caster.elem_bing_damage * (1+self.bingPercent) + self._bing_damage + attackdamage ]
		else:
			return [ caster.elem_huo_damage * (1+self.huoPercent) + self._huo_damage, \
					caster.elem_xuan_damage * (1+self.xuanPerent) + self._xuan_damage, \
					caster.elem_lei_damage * (1+self.leiPercent) + self._lei_damage, \
					caster.elem_bing_damage * (1+self.bingPercent) + self._bing_damage ]

	def calcSkillHitStrength( self, source,receiver, dynPercent, dynValue ):
		"""
		virtual method.
		计算技能攻击力
		基础法术攻击力(总公式中的基础值)=智力*0.14
		法术技能攻击力(总公式中的基础值)=(法术技能本身的攻击力+角色法术攻击力受2秒规则计算后的值)*(1+法术攻击力加成)+法术攻击力加值
		注意：法术技能攻击力这里稍稍有些不同，计算后的角色法术攻击力，对法术技能攻击力起效时，是处于附加值的位置。
		@param source:	攻击方
		@type  source:	entity
		@param dynPercent:	在本次攻击流程中可能会有外部其他技能导致额外的 技能攻击力加成
		@param  dynValue:	在本次攻击流程中可能会有外部其他技能导致额外的 技能攻击力加值
		"""
		base = random.randint( self._effect_min, self._effect_max )
		extra = self.calcTwoSecondRule( source, source.magic_damage * (1+self.magicPercent) )
		return self.calcProperty( base, extra * self._shareValPercent, dynPercent + source.magic_skill_extra_percent / csconst.FLOAT_ZIP_PERCENT, dynValue + source.magic_skill_extra_value / csconst.FLOAT_ZIP_PERCENT )
		