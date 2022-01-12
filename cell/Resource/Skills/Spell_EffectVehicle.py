# -*- coding: gb18030 -*-
#
# $Id: Spell_EffectVehicle.py,v 1.1 2008-09-04 06:43:35 yangkai Exp $

"""
"""
from SpellBase import Spell
import csstatus

class Spell_EffectVehicle( Spell ):
	"""
	对骑宠起效果的技能,包括骑宠装备buff
	因骑宠召唤有异步性，所有分开了召唤技能和起效果的技能
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
		# 给玩家加一个骑宠专用buff
		self.receiveLinkBuff( caster, receiver )

# $Log: not supported by cvs2svn $
