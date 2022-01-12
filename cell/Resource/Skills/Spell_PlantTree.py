# -*- coding: gb18030 -*-

import csstatus
import csconst
import csdefine
import random
from Spell_Item import Spell_Item
from bwdebug import *
import BigWorld
import Math

class Spell_PlantTree( Spell_Item ):
	"""
	种植果树
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )
		self.p1 = ""
		self.p2 = ""
		self.p3 = ""
		self.p4 = ""
		self.p5 = ""

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self.p1 = str( dict[ "param1" ] )					# 果树的模型编号
		self.p2 = int( dict[ "param2" ] )      				# 果树种子的ID
		if dict[ "param3" ]:
			self.p3 = str( dict[ "param3" ] )				# 果树种植位置限制
		if dict[ "param4" ]:
			self.p4 = float( dict[ "param4" ] )				# 果树种植范围限制
		if dict[ "param5" ]:
			self.p5 = str( dict[ "param5" ] ).split(";")	# 果树种植地图限制

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
		if caster.hasFlag( csdefine.ROLE_FLAG_SAFE_AREA ):
			return csstatus.FRUIT_PLANT_NOT_AREA

		if len( caster.entitiesInRangeExt( csconst.FRUIT_PLANT_DISTANCE, "FruitTree", caster.position ) ):
			return csstatus.FRUIT_PLANT_NEED_FAR

		if self.p5:
			if caster.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) not in self.p5:
				return csstatus.FRUIT_PLANT_WRONG_MAP

		if self.p3:
			posData = self.p3.split("|")
			posDatas = []
			for i in posData:
				j = eval(i)
				posDatas.append( j )
			canPlantTree = False
			for k in posDatas:
				if caster.position.distTo( k ) <= self.p4: canPlantTree = True
			if canPlantTree == False:
				return csstatus.FRUIT_PLANT_WRONG_POS
			else: return csstatus.SKILL_GO_ON

		if caster.state == csdefine.ENTITY_STATE_FIGHT:
			return csstatus.FRUIT_PLANT_WRONG
		return csstatus.SKILL_GO_ON

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达要做的事情
		这是对自己使用的物品技能，因此receiver肯定是real entity
		"""
		position = Math.Vector3( receiver.position )
		param = { "modelNumber" : self.p1, "fruitseedID" : self.p2, "planterDBID" : receiver.databaseID, "planterName" : receiver.getName() }
		receiver.createEntityNearPlanes( "FruitTree", position, ( 0, 0, 0 ), param )

