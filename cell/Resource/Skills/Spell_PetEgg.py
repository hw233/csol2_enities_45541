# -*- coding: gb18030 -*-

import csstatus
import csconst
import csdefine
import random
from Love3 import g_objFactory
from Spell_Item import Spell_Item
from bwdebug import *

class Spell_PetEgg( Spell_Item ):
	"""
	宠物蛋技能
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )
		self.petClassID = 0
		self.petTypeDict = {}

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self.petClassID = ( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else "" )
		for sParam in ( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else "" ) .split( ";" ):
			petTypeList = sParam.split( ":" )
			self.petTypeDict[int( petTypeList[0] )] = float( petTypeList[1] ) / 100	# self.petTypeDict:{ 辈份1:概率1, ……}

	def getCatchPetType( self ):
		"""
		获得宠物的辈份
		"""
		rate = random.random()
		rateSect = 0.0
		for hierarchy, petRate in self.petTypeDict.iteritems():
			rateSect += petRate
			if rate < petRate:
				return hierarchy

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		能否使用技能的检查

		@param caster : 施展技能者
		@type caster : BigWorld.entity
		@param target : 施展对象
		@type target : 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		baseStatus = Spell_Item.useableCheck( self, caster, target )
		if baseStatus != csstatus.SKILL_GO_ON:
			return baseStatus

		if caster.pcg_isFull():
			return csstatus.SKILL_MISSING_FULL_PET
		petScriptObject = g_objFactory.getObject( self.petClassID )

		# 14:33 2009-10-22，wsf：此处检查宠物脚本是否存在是权宜之计，防止策划配错配置造成玩家不可挽回的损失。
		if petScriptObject is None:
			ERROR_MSG( "--->>>宠物脚本( %s )不存在!" % self.petClassID )
			caster.client.onStatusMessage( csstatus.PET_CONFIG_NOT_FIND, "" )
			return csstatus.PET_ADD_JOYANCY_FAIL_UNKNOW

		if caster.level < petScriptObject.takeLevel or petScriptObject.minLv - csconst.PET_CATCH_OVER_LEVEL > caster.level:
			return csstatus.PET_LEVEL_CANT_FIT
		return csstatus.SKILL_GO_ON

	def castValidityCheck( self, caster, receiver ):
		"""
		virtual method.
		校验技能是否可以施展。
		此接口仅仅用于当法术吟唱完后判断是否能对目标施展，
		如果需要判断一个法术是否能对目标使用，应该使用intonateValidityCheck()方法。
		此接口会被intonateValidityCheck()接口调用，如果重载时某些条件需要在吟唱结束后判断，
		则必须重载此接口并加入相关判断，否则只能重载intonateValidityCheck()接口。

		注：此接口是旧版中的validCast()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		state = Spell_Item.castValidityCheck( self, caster, receiver )
		if state != csstatus.SKILL_GO_ON:
			return state
		if caster.pcg_isFull():
			return csstatus.SKILL_MISSING_FULL_PET
		return state

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达要做的事情
		这是对自己使用的物品技能，因此receiver肯定是real entity
		"""
		monsterScriptObject = g_objFactory.getObject( self.petClassID )
		petID = monsterScriptObject.mapPetID
		level = random.randint( monsterScriptObject.minLv, monsterScriptObject.maxLv )
		defaultSkillIDs = g_objFactory.getObject( petID ).getDefSkillIDs( level )
		modelNumbers = monsterScriptObject.getEntityProperty( "modelNumber" )
		if len( modelNumbers ):
			modelNumber = modelNumbers[ random.randint( 0, len(modelNumbers) - 1 ) ]
		else:
			modelNumber = ""
		receiver.base.pcg_catchPet( self.petClassID, level, modelNumber, defaultSkillIDs, self.getCatchPetType(), caster.getByUid( caster.queryTemp( "item_using" ) ).isBinded(),False, False )