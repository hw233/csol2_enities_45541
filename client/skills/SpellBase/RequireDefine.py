# -*- coding: gb18030 -*-
#
# $Id: RequireDefine.py,v 1.8 2008-08-09 01:55:04 wangshufeng Exp $

"""
需求和消耗
"""

import BigWorld
import csstatus
import csdefine
import Language
import items
from bwdebug import *
from config.client.labels.skills import lbs_RequireDefine

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

	def getType( self ):
		"""
		获得需求类型
		"""
		return csdefine.SKILL_REQUIRE_TYPE_NONE

	def getDscription( self, skillInstance ):
		"""
		获取消耗描述
		"""
		return ""

	def validObject( self, sourceEntity, skillInstance ):
		"""
		校验对象是否满足需求。
		"""
		return csstatus.SKILL_UNKNOW

	def pay( self, sourceEntity ):
		"""
		支付消耗物
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

	def getDscription( self, skillInstance ):
		"""
		获取消耗描述
		"""
		return ""

	def validObject( self, sourceEntity, skillInstance ):
		"""
		校验对象是否满足需求。
		"""
		return csstatus.SKILL_GO_ON

	def pay( self, sourceEntity ):
		"""
		支付消耗物
		"""
		pass

class Mana( Require):
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

	def getType( self ):
		"""
		获得需求类型
		"""
		return csdefine.SKILL_REQUIRE_TYPE_MANA

	def getDscription( self, skillInstance ):
		"""
		获取消耗描述
		"""
		extraVal = skillInstance.calcExtraRequire( BigWorld.player() )
		val = ( self.mana + extraVal[0] ) * ( 1 + extraVal[1] )

		if val < 0:
			val = 0

		return lbs_RequireDefine[1] % val

	def validObject( self, sourceEntity, skillInstance ):
		"""
		校验对象是否满足需求。
		"""
		extraVal = skillInstance.calcExtraRequire( sourceEntity )
		val = ( self.mana + extraVal[0] ) * ( 1 + extraVal[1] )

		if val < 0:
			val = 0

		if sourceEntity.MP < val:
			return csstatus.SKILL_OUTOF_MANA

		return csstatus.SKILL_GO_ON

	def pay( self, sourceEntity ):
		"""
		支付消耗物
		"""
		pass

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

	def getDscription( self, skillInstance ):
		"""
		获取消耗描述
		"""
		return lbs_RequireDefine[2] % int( self.manaPercent * 100 )

	def validObject( self, caster, skillInstance ):
		"""
		校验对象是否满足需求。

		注：如果出现类似于“使用技能时，有$1%的几率‘增加’$2%的法力消耗”时，表现不一定正确，
		因为现在没有办法正确表现随机的“增加”
		"""
		extraVal = skillInstance.calcExtraRequire( caster )
		val = ( self.manaPercent * caster.MP_Max + extraVal[0] ) * ( 1 + extraVal[1] )
		if val < 0: val = 0
		if caster.MP < val:
			TRACE_MSG( "mana not enough" )
			return csstatus.SKILL_OUTOF_MANA

		return csstatus.SKILL_GO_ON
		
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

	def getType( self ):
		"""
		获得需求类型
		"""
		return csdefine.SKILL_REQUIRE_TYPE_ITEM

	def getDscription( self, skillInstance ):
		"""
		"""
		if self.itemAmount > 1:
			des = "%sx%s" %( items.instance().id2name( self.itemID ), self.itemAmount )
		else:
			des = items.instance().id2name( self.itemID )
		return des

	def validObject( self, caster, skillInstance ):
		"""
		校验对象是否满足需求。

		注：如果出现类似于“使用技能时，有$1%的几率‘增加’$2%的法力消耗”时，表现不一定正确，
		因为现在没有办法正确表现随机的“增加”
		"""
		if not caster.checkItemFromNKCK_( self.itemID, self.itemAmount ):
			return csstatus.SKILL_ITEM_NOT_EXIST
		return csstatus.SKILL_GO_ON

	def pay( self, caster ):
		"""
		支付消耗物
		"""
		pass

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

	def getDscription( self, skillInstance ):
		"""
		获取消耗描述
		"""
		val = self.combatCount
		if val < 0:
			val = 0

		return lbs_RequireDefine[3] % val

	def validObject( self, sourceEntity, skillInstance ):
		"""
		校验对象是否满足需求。
		"""
		val = self.combatCount
		if val < 0:
			val = 0
		if sourceEntity.combatCount < val:
			return csstatus.SKILL_OUTOF_CombatCount

		return csstatus.SKILL_GO_ON
	
class Vitality( Require):
	"""
	体力值消耗
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

	def getType( self ):
		"""
		获得需求类型
		"""
		return csdefine.SKILL_REQUIRE_TYPE_VITALITY

	def getDscription( self, skillInstance ):
		"""
		获取消耗描述
		"""
		extraVal = skillInstance.calcExtraRequire( BigWorld.player() )
		val = ( self.vitality + extraVal[0] ) * ( 1 + extraVal[1] )

		if val < 0:
			val = 0

		return val

	def validObject( self, sourceEntity, skillInstance ):
		"""
		校验对象是否满足需求。
		"""
		extraVal = skillInstance.calcExtraRequire( sourceEntity )
		val = ( self.vitality + extraVal[0] ) * ( 1 + extraVal[1] )

		if val < 0:
			val = 0

		if sourceEntity.energy < val:
			return csstatus.SKILL_OUTOF_VITALITY

		return csstatus.SKILL_GO_ON

	def pay( self, sourceEntity ):
		"""
		支付消耗物
		"""
		pass

class HP( Require):
	"""
	生命值消耗
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

	def getType( self ):
		"""
		获得需求类型
		"""
		return csdefine.SKILL_REQUIRE_TYPE_HP

	def getDscription( self, skillInstance ):
		"""
		获取消耗描述
		"""
		extraVal = skillInstance.calcExtraRequire( BigWorld.player() )
		val = ( self.hp + extraVal[0] ) * ( 1 + extraVal[1] )

		if val < 0:
			val = 0

		return val

	def validObject( self, sourceEntity, skillInstance ):
		"""
		校验对象是否满足需求。
		"""
		extraVal = skillInstance.calcExtraRequire( sourceEntity )
		val = ( self.hp + extraVal[0] ) * ( 1 + extraVal[1] )

		if val < 0:
			val = 0

		if sourceEntity.HP < val:
			return csstatus.SKILL_OUTOF_HP

		return csstatus.SKILL_GO_ON

	def pay( self, sourceEntity ):
		"""
		支付消耗物
		"""
		pass


class RequireDefine( Require ):

	def __init__( self ):
		"""
		构造函数。
		"""
		Require.__init__( self )
		self._requires = []

	def getDscription( self, skillInstance ):
		"""
		获取消耗描述列表
		"""
		dsps = ""
		for require in self._requires:
			msg = require.getDscription( skillInstance )
			if len( msg ) > 0 and len( self._requires ) > 1:
				dsps +=",%s"%msg
			else:
				dsps = msg
		return dsps

	def getRequireItemDscription( self, skillInstance ):
		"""
		获得消耗物品描述
		"""
		dsps = ""
		for require in self._requires:
			if require.getType() != csdefine.SKILL_REQUIRE_TYPE_ITEM:
				continue
			msg = require.getDscription( skillInstance )
			if len( msg ) > 0 and len( self._requires ) > 1:
				dsps +=",%s"%msg
			else:
				dsps = msg
		return dsps

	def getRequireItemList( self, skillInstance ):
		"""
		获得消耗物品描述
		"""
		dsps = []
		for require in self._requires:
			if require.getType() != csdefine.SKILL_REQUIRE_TYPE_ITEM:
				continue
			msg = require.getDscription()
			if require.validObject( BigWorld.player(), skillInstance ) == csstatus.SKILL_GO_ON:
				dsps.append( ( msg, 1 ) )
			else:
				dsps.append( ( msg, 0 ) )
		return dsps


	def getRequireManaDscription( self, skillInstance ):
		"""
		获得消耗魔法描述
		"""
		dsps = ""
		for require in self._requires:
			if require.getType() != csdefine.SKILL_REQUIRE_TYPE_MANA:
				continue
			msg = require.getDscription( skillInstance )
			if len( msg ) > 0 and len( self._requires ) > 1:
				dsps +=",%s"%msg
			else:
				dsps = msg
		return dsps

	def getRequireManaList( self, castEntity, skillInstance ):
		"""
		获得消耗魔法描述
		"""
		dsps = []
		for require in self._requires:
			if require.getType() != csdefine.SKILL_REQUIRE_TYPE_MANA:
				continue
			msg = require.getDscription( skillInstance )
			if require.validObject( castEntity, skillInstance ) == csstatus.SKILL_GO_ON:
				dsps.append( ( msg, 1 ) )
			else:
				dsps.append( ( msg, 0 ) )
		return dsps

	def getRequireVitality( self, skillInstance ):
		"""
		获得消耗体力
		"""
		vitality = 0
		for require in self._requires:
			if require.getType() != csdefine.SKILL_REQUIRE_TYPE_VITALITY:
				continue
			value = require.getDscription( skillInstance )
			vitality += value
		return int( vitality )

	def getRequireHP( self, skillInstance ):
		"""
		获得消耗生命值
		"""
		hp = 0
		for require in self._requires:
			if require.getType() != csdefine.SKILL_REQUIRE_TYPE_HP:
				continue
			value = require.getDscription( skillInstance )
			hp += value
		return int( hp )

	def load( self, listDat ):
		"""
		以字符串作为参数加载；

		@param listDat: python list data
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

		for datI in xrange( len( listDat ) ):
			dat = listDat[ datI ]
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

	def pay( self, caster ):
		"""
		支付消耗物
		"""
		for r in self._requires:
			r.pay( caster )

	def getRequires( self ):
		"""
		获得所有施法需求实例
		"""
		return self._requires

def newInstance( dict ):
	"""
	获取需求实例。
		以字符串作为参数加载；

		@param section: python dict data
	"""
	inst = RequireDefine()
	if dict:
		inst.load( dict )
	return inst
