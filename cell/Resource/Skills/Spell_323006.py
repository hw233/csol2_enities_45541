# -*- coding: gb18030 -*-
#
# $Id:  Exp $


from SpellBase import *
import random
import csdefine
import csstatus
from bwdebug import *
from SpellBase.HomingSpell import ActiveHomingSpell
from Function import newUID
import Math
import VehicleHelper

class Spell_323006( ActiveHomingSpell ):
	"""
	剑客连击2
	"""
	def __init__( self ):
		"""
		"""
		ActiveHomingSpell.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		ActiveHomingSpell.init( self, dict )
		self._casterActions = dict["param4"].split(",")
		self._targetActions = dict["param5"].split(",")

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		targetEntity = target.getObject()
		if targetEntity is None: return csstatus.SKILL_UNKNOW
		if targetEntity.findBuffByBuffID( 299021 ):
			return csstatus.SKILL_RECEIVE_OBJECT_NOT_MONSTER

		return ActiveHomingSpell.useableCheck( self, caster, target )

	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTypeImpl；
		此接口默认返回：{ "param": None }，即表示无动态数据。

		@return: 返回一个SKILL类型的字典。SKILL类型详细定义请参照defs/alias.xml文件
		"""
		return { "param" : {	"endTime" : self._endTime,
								"tickInterval" : self._tickInterval,
								"target" : self._target,
								"childSpellIDs": list( self._childSpellIDs ),
								"castActions" : list( self._casterActions ),
								"targetActions" : list( self._targetActions ) } }

	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。

		@type data: dict
		"""
		obj = self.__class__()
		obj.__dict__.update( self.__dict__ )

		obj._endTime = data["param"][ "endTime" ]
		obj._tickIntervalCopy = list( data["param"][ "tickInterval" ] )
		obj._target = data["param"][ "target" ]
		obj._childSpellIDsCopy = data["param"][ "childSpellIDs" ]
		obj._casterActions = data["param"][ "castActions" ]
		obj._targetActions = data["param"][ "targetActions" ]

		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj

