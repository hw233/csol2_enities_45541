# -*- coding: gb18030 -*-
#
from bwdebug import *
import BigWorld
import csconst
from Spell_ElemDamage import Spell_ElemDamage
import time
import csdefine

class Spell_312632( Spell_ElemDamage ):
	"""
	该技能可参考剑客的技能蜂尾321206/蜂杀311127，其中的蜂杀技能与此相似，不同之处在蜂杀是增加物理伤害，
	此技能是完全元素伤害，不计算角色的物理攻击力。
	此技能中所涉及的“心火焚烧”状态，见下面的技能“三昧真火”中的DEBUFF。
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_ElemDamage.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_ElemDamage.init( self, dict )

	def calcElemDamage( self, caster, receiver, attackdamage = 0 ):
		"""
		virtual method.
		计算元素伤害
		"""
		# 伤害x(1+DEBUFF已作用时间/DEBUFF总时间)
		damageMult = 1
		indexs = receiver.findBuffsByBuffID( 107017 )
		if len( indexs ):
			index = indexs[0]
			buff = receiver.getBuff( index )
			endTime = buff["persistent"]
			nowTime = time.time()
			skill = buff["skill"]
			totalTime = float( skill._persistent )
			damageMult = max( 1.0, 1 + ( ( totalTime - ( endTime - nowTime  ) ) / totalTime ) )
			receiver.removeAllBuffByBuffID( skill.getBuffID(), [ csdefine.BUFF_INTERRUPT_NONE ] )

		elemEffect = caster.queryTemp( "ELEM_ATTACK_EFFECT", "" )
		if elemEffect == "huo":		# 火元素攻击效果
			return [ self._huo_damage * damageMult + attackdamage, \
					self._xuan_damage * damageMult, \
					self._lei_damage * damageMult, \
					self._bing_damage * damageMult ]
		elif elemEffect == "xuan":	# 玄元素攻击效果
			return [ self._huo_damage * damageMult, \
					self._xuan_damage * damageMult + attackdamage, \
					self._lei_damage * damageMult, \
					self._bing_damage * damageMult ]
		elif elemEffect == "lei":	# 雷元素攻击效果
			return [ self._huo_damage * damageMult, \
					self._xuan_damage * damageMult, \
					self._lei_damage * damageMult + attackdamage, \
					self._bing_damage * damageMult ]
		elif elemEffect == "bing":	# 冰元素攻击效果
			return [ self._huo_damage * damageMult, \
					self._xuan_damage * damageMult, \
					self._lei_damage * damageMult, \
					self._bing_damage * damageMult + attackdamage ]
		else:
			return [ self._huo_damage * damageMult, \
					self._xuan_damage * damageMult, \
					self._lei_damage * damageMult, \
					self._bing_damage * damageMult ]
