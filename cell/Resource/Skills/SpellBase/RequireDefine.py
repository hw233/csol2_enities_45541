# -*- coding: gb18030 -*-
#
# $Id: RequireDefine.py,v 1.16 2008-08-21 03:53:49 kebiao Exp $

"""
需求和消耗
"""

import BigWorld
import Language
import csstatus
from bwdebug import *
import csdefine

class Require:
	def __init__( self ):
		"""
		构造函数。
		"""
		pass

	def load( self, args ):
		"""
		以字符串作为参数加载；

		@param args: 各字符串具体意义由各派生类自己定义
		@type  args: STRING
		"""
		pass

	def validObject( self, caster, skillInstance ):
		"""
		校验对象是否满足需求。

		@param caster: 施法者
		@type  caster: Entity
		@param skillInstance: 使用的技能实例
		@type  skillInstance: Skill
		"""
		return csstatus.SKILL_UNKNOW

	def pay( self, caster, skillInstance ):
		"""
		支付消耗物

		@param caster: 施法者
		@type  caster: Entity
		@param skillInstance: 使用的技能实例
		@type  skillInstance: Skill
		"""
		pass

class RequireNone:
	"""
	无要求
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		pass

	def load( self, args ):
		"""
		以字符串作为参数加载；

		@param args: do no thing
		@type  args: STRING
		"""
		pass

	def validObject( self, caster, skillInstance ):
		"""
		校验对象是否满足需求。
		"""
		return csstatus.SKILL_GO_ON

	def pay( self, caster, skillInstance ):
		"""
		支付消耗物
		"""
		pass

class Mana( Require ):

	def __init__( self ):
		"""
		构造函数。
		"""
		Require.__init__( self )
		self.mana = 0

	def load( self, args ):
		"""
		以字符串作为参数加载；

		@param args: format: int
		@type  args: STRING
		"""
		self.mana = int( args )

	def validObject( self, caster, skillInstance ):
		"""
		校验对象是否满足需求。

		注：如果出现类似于“使用技能时，有$1%的几率‘增加’$2%的法力消耗”时，表现不一定正确，
		因为现在没有办法正确表现随机的“增加”
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.mana + extraVal[0] ) * ( 1 + extraVal[1] )
		if val < 0: val = 0
		if caster.MP < val:
			TRACE_MSG( "mana not enough" )
			return csstatus.SKILL_OUTOF_MANA

		return csstatus.SKILL_GO_ON

	def pay( self, caster, skillInstance ):
		"""
		支付消耗物
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.mana + caster.popTemp( "changeMana_extra", 0 ) + extraVal[0] ) * ( 1 + caster.popTemp( "changeMana_perent", 0.0 ) + extraVal[1] ) + caster.popTemp( "changeMana_value", 0 )
		if val < 0: val = 0
		if caster.queryTemp( "NOT_NEED_MANA", False ): val = 0
		caster.setMP( caster.MP - val )

	def getPay( self, caster, skillInstance ):
		"""
		获取消耗物
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.mana + caster.popTemp( "changeMana_extra", 0 ) + extraVal[0] ) * ( 1 + caster.popTemp( "changeMana_perent", 0.0 ) + extraVal[1] ) + caster.popTemp( "changeMana_value", 0 )
		if val < 0: val = 0
		return val

class PercentMana( Require ):
	"""
	按最大魔法值一定比例消耗魔法
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Require.__init__( self )
		self.manaPercent = 0

	def load( self, args ):
		"""
		以字符串作为参数加载；

		@param args: format: int
		@type  args: STRING
		"""
		self.manaPercent = int( args ) / 100.0

	def validObject( self, caster, skillInstance ):
		"""
		校验对象是否满足需求。

		注：如果出现类似于“使用技能时，有$1%的几率‘增加’$2%的法力消耗”时，表现不一定正确，
		因为现在没有办法正确表现随机的“增加”
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.manaPercent * caster.MP_Max + extraVal[0] + caster.queryTemp( "changeMana_extra", 0 ) ) * ( 1 + extraVal[1] + caster.queryTemp( "changeMana_perent", 0.0 ) ) + caster.queryTemp( "changeMana_value", 0 )
		if val < 0: val = 0
		if caster.MP < val:
			TRACE_MSG( "mana not enough" )
			return csstatus.SKILL_OUTOF_MANA

		return csstatus.SKILL_GO_ON

	def pay( self, caster, skillInstance ):
		"""
		支付消耗物
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.manaPercent * caster.MP_Max + caster.queryTemp( "changeMana_extra", 0 ) + extraVal[0] ) * ( 1 + caster.queryTemp( "changeMana_perent", 0.0 ) + extraVal[1] ) + caster.queryTemp( "changeMana_value", 0 )
		if val < 0: val = 0
		if caster.queryTemp( "NOT_NEED_MANA", False ): val = 0
		caster.setMP( caster.MP - val )

	def getPay( self, caster, skillInstance ):
		"""
		获取消耗物
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.manaPercent * caster.MP_Max + caster.queryTemp( "changeMana_extra", 0 ) + extraVal[0] ) * ( 1 + caster.queryTemp( "changeMana_perent", 0.0 ) + extraVal[1] ) + caster.queryTemp( "changeMana_value", 0 )
		if val < 0: val = 0
		return val

class Item( Require ):

	def __init__( self ):
		"""
		构造函数。
		"""
		Require.__init__( self )
		self.itemID = 0
		self.itemAmount = 0

	def load( self, args ):
		"""
		以字符串作为参数加载；

		@param args: format: int
		@type  args: STRING
		"""
		if "'" in args:

			param = args.split( "'" )
			self.itemID = int( param[0] )
			self.itemAmount = int( param[1] )

	def validObject( self, caster, skillInstance ):
		"""
		校验对象是否满足需求。

		注：如果出现类似于“使用技能时，有$1%的几率‘增加’$2%的法力消耗”时，表现不一定正确，
		因为现在没有办法正确表现随机的“增加”
		"""
		if not caster.checkItemFromNKCK_( self.itemID, self.itemAmount ):
			return csstatus.SKILL_ITEM_NOT_EXIST
		return csstatus.SKILL_GO_ON

	def pay( self, caster, skillInstance ):
		"""
		支付消耗物
		"""
		amount = self.itemAmount
		caster.removeItemTotal( self.itemID, amount, csdefine.DELETE_ITEM_PAY )

	def getPay( self, caster, skillInstance ):
		"""
		获取消耗物
		"""
		return 0

class CombatCount( Require ):
	"""
	消耗格斗点数
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Require.__init__( self )
		self.combatCount = 0

	def load( self, args ):
		"""
		以字符串作为参数加载；

		@param args: format: int
		@type  args: STRING
		"""
		self.combatCount = int( args )

	def validObject( self, caster, skillInstance ):
		"""
		校验对象是否满足需求。
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.combatCount + extraVal[0] ) * ( 1 + extraVal[1] )
		if val < 0: val = 0
		if caster.combatCount < val:
			TRACE_MSG( "combatCount not enough" )
			return csstatus.SKILL_OUTOF_CombatCount

		return csstatus.SKILL_GO_ON

	def pay( self, caster, skillInstance ):
		"""
		支付消耗物
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.combatCount + extraVal[0] ) * ( 1 + extraVal[1] )
		if val < 0: val = 0
		caster.calCombatCount( -val )

	def getPay( self, caster, skillInstance ):
		"""
		获取消耗物
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.combatCount + extraVal[0] ) * ( 1 + extraVal[1] )
		if val < 0: val = 0
		return val
		
class Vitality( Require ):
	"""
	消耗体力值
	"""

	def __init__( self ):
		"""
		构造函数。
		"""
		Require.__init__( self )
		self.vitality = 0

	def load( self, args ):
		"""
		以字符串作为参数加载；

		@param args: format: int
		@type  args: STRING
		"""
		self.vitality = int( args )

	def validObject( self, caster, skillInstance ):
		"""
		校验对象是否满足需求。

		注：如果出现类似于“使用技能时，有$1%的几率‘增加’$2%的体力消耗”时，表现不一定正确，
		因为现在没有办法正确表现随机的“增加”
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.vitality + extraVal[0] ) * ( 1 + extraVal[1] )
		if val < 0: val = 0
		if caster.energy < val:
			TRACE_MSG( "vitality not enough" )
			return csstatus.SKILL_OUTOF_VITALITY

		return csstatus.SKILL_GO_ON

	def pay( self, caster, skillInstance ):
		"""
		支付消耗物
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.vitality + extraVal[0] ) * ( 1 + extraVal[1] )
		if val < 0: val = 0
		caster.calEnergy( -val )

	def getPay( self, caster, skillInstance ):
		"""
		获取消耗物
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.vitality + extraVal[0] ) * ( 1 + extraVal[1] )
		if val < 0: val = 0
		return val

class HP( Require ):
	"""
	消耗生命值
	"""

	def __init__( self ):
		"""
		构造函数。
		"""
		Require.__init__( self )
		self.hp = 0

	def load( self, args ):
		"""
		以字符串作为参数加载；

		@param args: format: int
		@type  args: STRING
		"""
		self.hp = int( args )

	def validObject( self, caster, skillInstance ):
		"""
		校验对象是否满足需求。

		注：如果出现类似于“使用技能时，有$1%的几率‘增加’$2%的生命消耗”时，表现不一定正确，
		因为现在没有办法正确表现随机的“增加”
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.hp + extraVal[0] ) * ( 1 + extraVal[1] )
		if val < 0: val = 0
		if caster.HP < val:
			TRACE_MSG( "HP not enough" )
			return csstatus.SKILL_OUTOF_HP

		return csstatus.SKILL_GO_ON

	def pay( self, caster, skillInstance ):
		"""
		支付消耗物
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.hp + extraVal[0] ) * ( 1 + extraVal[1] )
		if val < 0: val = 0
		caster.setHP( caster.HP - val )

	def getPay( self, caster, skillInstance ):
		"""
		获取消耗物
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.hp + extraVal[0] ) * ( 1 + extraVal[1] )
		if val < 0: val = 0
		return val

class RequireDefine( Require ):

	def __init__( self ):
		"""
		构造函数。
		"""
		Require.__init__( self )
		self._requires = []

	def load( self, pyDat ):
		"""
		以字符串作为参数加载；

		@param dictDat: python data
		"""
		reqs = \
		{
			0	     	:	Mana,
			1			:   Item,
			2			: 	PercentMana,
			3			:	CombatCount,
			4			:	Vitality,
			5			:	HP,
		}
		for i in xrange( len( pyDat ) ):
			dat = pyDat[ i ]
			instance = reqs[ dat[ "requireType" ] ]()
			instance.load( dat[ "value" ] )
			self._requires.append( instance )

	def validObject( self, caster, skillInstance ):
		"""
		校验对象是否满足需求。

		注：如果出现类似于“使用技能时，有$1%的几率‘增加’$2%的法力消耗”时，表现不一定正确，
		因为现在没有办法正确表现随机的“增加”
		"""
		for r in self._requires:
			state = r.validObject( caster, skillInstance )
			if state != csstatus.SKILL_GO_ON:
				return state
		return csstatus.SKILL_GO_ON

	def pay( self, caster, skillInstance ):
		"""
		支付消耗物
		"""
		for r in self._requires:
			r.pay( caster, skillInstance )

		for r in self._requires:
			if r.getPay( caster, skillInstance ) > 0:			
				# 不需要消耗魔法标记用一次就没了
				caster.detachNotNeedManaEffect()
				return

def newInstance( dictDat ):
	"""
	获取需求实例。
		以字符串作为参数加载；

		@param dictDat: python data
	"""
	inst = RequireDefine()
	if dictDat:
		inst.load( dictDat )
	return inst


