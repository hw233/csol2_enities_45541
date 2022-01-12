# -*- coding: gb18030 -*-

#

import BigWorld
import csdefine
import csstatus
import random
from SpellBase import *

class Spell_322448( Spell ):
	"""
	系统技能
	"该技能同时存在对目标的DEBUFF和对自身的BUFF，普通BUFF技能不能满足要求。同时，必须判断首先对目标的DEBUFF施放成功（目标获得此DEBUFF），才能产生对自身的BUFF
此处降低法防的DEBUFF104006和提高自身物防的BUFF004005都是已有的BUFF。"

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

	def receive( self, caster, receiver ):
		"""
		virtual method = 0.
		针对每一个受术者进行受术处理，如计算伤害、改变属性等等。通常情况下此接口是由onArrive()调用，
		但它亦有可能由SpellUnit::receiveOnreal()方法调用，用于处理一些需要在受术者的real entity身上作的事情。
		但对于是否需要在real entity身上接收，由技能设计者在receive()中自行判断，并不提供相关机制。
		注：此接口为旧版中的onReceive()

		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		self.receiveLinkBuff( caster, receiver )

	def receiveLinkBuff( self, caster, receiver ):
		"""
		给entity附加buff的效果
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 施展对象
		@type  receiver: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		buff = self._buffLink[0]
		# 有产生机率则判断机率
		if not self.canLinkBuff( caster, receiver, buff ): return

		buff.getBuff().receive( caster, receiver )
		self._buffLink[1].getBuff().receive( caster, caster )