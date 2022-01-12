# -*- coding: gb18030 -*-
#
# 召唤NPC技能

import copy
import math
import random
import Math
import ECBExtend
import csstatus
import csarithmetic
from bwdebug import *
import SkillTargetObjImpl
from Spell_BuffNormal import Spell_BuffNormal

class Spell_Summon( Spell_BuffNormal ):
	"""
	召唤
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_BuffNormal.__init__( self )
		self.npcs = []   #创建NPC信息
		self._target = None 
		self.level = 0	#创建的NPC等级 若不填或填0 为默认的施法者等级
		self.randomPosFlag = False  #是否要将施法者放入随机分配坐标点
		self.dis = 0   #随机距离
		self.maxHeightDiff = 0.0	#怪物刷新位置与招怪者位置高度不能超过此值，否则取施法者位置为刷怪位置 CSOL-230
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_BuffNormal.init( self, dict )
		if dict["param1"] != "" :
			self.npcs = eval(dict["param1"])
		else:
			self.npcs = []
			
		if dict["param2"] != "" :
			self.level = int(dict["param2"])
		else:
			self.level = 0
			
		if dict["param3"] != "" :
			self.dis = float(dict["param3"])
		else:
			self.dis = 0
			
		if dict["param4"] != "" :
			self.randomPosFlag = bool( int(dict["param4"]) )
		else:
			self.randomPosFlag = False
		
		if dict["param5"] != "" :
			self.maxHeightDiff = float(dict["param5"])
			
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
		# 检查技能cooldown
		if not self.isCooldown( caster ):
			return csstatus.SKILL_NOT_READY

		# 施法需求检查
		state = self.checkRequire_( caster )
		if state != csstatus.SKILL_GO_ON:
			return state

		# 施法者检查
		state = self.castValidityCheck( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		# 检查目标是否符合法术施展
		state = self.getCastObject().valid( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state
		
		if not target:
			dstPos = tuple( caster.position )
		else:
			dstPos = target.getObjectPosition()
		self._target = copy.deepcopy(SkillTargetObjImpl.createTargetObjPosition(dstPos))
		caster.setTemp( "SUMMON_CENTER_POS", dstPos )
		return csstatus.SKILL_GO_ON
	
	def onArrive( self, caster, target ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		# 开始放NPC
		level = 50
		if self.level > 0:
			level = self.level
		else:
			level = caster.level
		posList = [] #随机坐标集合
		entitiesL = [] #所有随机坐标的实体集合
		if self.dis:
			dstPos = caster.popTemp( "SUMMON_CENTER_POS",  tuple( caster.position ) )
			posList = calculatePos( caster.spaceID, caster.yaw, self.dis, dstPos )
		for info in self.npcs:
			for i in range( info[1] ):
				entity = caster.createObjectNearPlanes( info[0], tuple( caster.position ), caster.direction,{"level":level,"spawnPos":tuple( caster.position ) } )
				entitiesL.append( entity )
		if self.randomPosFlag:
			entitiesL.append( caster )
		for en in entitiesL:
			if len( posList ) != 0:
				pos = random.choice( posList )
				posList.remove( pos )
				if self.maxHeightDiff == 0.0 or abs(pos.y - en.position.y) <= self.maxHeightDiff:
					en.openVolatileInfo()
					en.position = pos
		
		self.receiveLinkBuff( caster, target.getObject() )	#支持buff
		Spell_BuffNormal.onArrive( self, caster, target )
		

def calculatePos( spaceID, yaw, dis, pos):
	"""
	计算8个点，角度yaw，距离dis
	"""
	posL = []
	for i in range(8):
		y = yaw + ( math.pi * 2 / 8 ) * i
		direction = Math.Vector3( math.sin(y), 0.0, math.cos(y) ) 
		direction.normalise()
		dstPos = pos + direction * dis
		collPos = csarithmetic.getCollidePoint( spaceID, pos, dstPos )
		endDstPos = csarithmetic.getCollidePoint( spaceID, Math.Vector3( collPos[0],collPos[1] + 10,collPos[2]), Math.Vector3( collPos[0],collPos[1] - 10,collPos[2]) )
		posL.append( endDstPos )
	return posL