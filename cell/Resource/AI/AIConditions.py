# -*- coding: gb18030 -*-

# $Id: AIConditions.py,v 1.22 2008-09-02 03:31:03 kebiao Exp $
import BigWorld
import csdefine
import csstatus
import csconst
import Const
import time
import csarithmetic
import SkillTargetObjImpl
from Resource.AI.AIBase import *
from bwdebug import *
from csdefine import *
from Resource.SkillLoader import g_skills
from utils import vector3TypeConvert
from CrondScheme import *

class AICnd1( AICondition ):
	"""
	战斗开始后X秒内
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return time.time() - entity.fightStartTime <= self._param1

class AICnd2( AICondition ):
	"""
	战斗开始后X秒后
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return time.time() - entity.fightStartTime > self._param1

class AICnd3( AICondition ):
	"""
	战斗开始后每隔X秒
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		
		t = int(time.time() - entity.fightStartTime )
		
		return entity.fightStartTime > 0 and t > 0 and t % self._param1 == 0

class AICnd4( AICondition ):
	"""
	战斗列表中的单位数量达到某个值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return len( entity.enemyList ) >= self._param1

class AICnd5( AICondition ):
	"""
	战斗列表为空
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return len( entity.enemyList ) <= 0

class AICnd6( AICondition ):
	"""
	伤害列表中的单位数量达到某个值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return len( entity.damageList ) >= self._param1

class AICnd7( AICondition ):
	"""
	伤害列表为空
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return len( entity.damageList ) <= 0

class AICnd8( AICondition ):
	"""
	治疗列表中的单位数量达到某个值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return len( entity.cureList ) >= self._param1

class AICnd9( AICondition ):
	"""
	治疗列表为空
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return len( entity.cureList ) <= 0

class AICnd10( AICondition ):
	"""
	治疗列表中某个单位的治疗总量超过某值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		eid = entity.findEnemyByMaxCure()
		if eid <= 0:
			return False
		return entity.cureList[ eid ] > self._param1

class AICnd11( AICondition ):
	"""
	战斗列表中的某类职业的数量超过某个值
	# 职业
	CLASS_UNKNOWN							= 0x00		# 未知
	CLASS_FIGHTER							= 0x10		# 战士
	CLASS_SWORDMAN							= 0x20		# 剑客
	CLASS_ARCHER							= 0x30		# 射手
	CLASS_MAGE								= 0x40		# 法师
	CLASS_PALADIN							= 0x50		# 强防型战士（NPC专用）
	CLASS_WARLOCK							= 0x60		# 巫师( 已去掉 )
	CLASS_PRIEST							= 0x70		# 祭师( 已去掉 )
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0 #职业
		self._param2 = 0 #数量

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = eval( section.readString( "param1" ) )
		self._param2 = section.readInt( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		race = 0
		for eid in entity.enemyList:
			if not BigWorld.entities.has_key( eid ):
				continue
			if BigWorld.entities[ eid ].getClass() == self._param1:
				race += 1
		return race > self._param2

class AICnd12( AICondition ):
	"""
	伤害列表中某个单位的伤害总量超过某值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		eid = entity.findEnemyByMaxDamage()
		if eid <= 0:
			return False
		return entity.damageList[ eid ] > self._param1

class AICnd13( AICondition ):
	"""
	处于非战斗状态
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return entity.getState() != csdefine.ENTITY_STATE_FIGHT

class AICnd14( AICondition ):
	"""
	处于战斗状态
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return entity.getState() == csdefine.ENTITY_STATE_FIGHT

class AICnd15( AICondition ):
	"""
	处于逃跑状态
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return entity.getSubState() == csdefine.M_SUB_STATE_FLEE

class AICnd16( AICondition ):
	"""
	处于追击状态
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return entity.getSubState() == csdefine.M_SUB_STATE_CHASE

class AICnd17( AICondition ):
	"""
	处于复位状态
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return entity.getSubState() == csdefine.M_SUB_STATE_GOBACK

class AICnd18( AICondition ):
	"""
	脱离追击状态
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return entity.getOldSubState() == csdefine.M_SUB_STATE_CHASE and entity.getSubState() != csdefine.M_SUB_STATE_CHASE

class AICnd19( AICondition ):
	"""
	脱离逃跑状态
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return entity.getOldSubState() == csdefine.M_SUB_STATE_FLEE and entity.getSubState() != csdefine.M_SUB_STATE_FLEE

class AICnd20( AICondition ):
	"""
	处于死亡状态
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return entity.getState() == csdefine.ENTITY_STATE_DEAD

class AICnd21( AICondition ):
	"""
	自身生命高于某个百分比值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return entity.HP / float( entity.HP_Max ) > self._param1 / 100.0

class AICnd22( AICondition ):
	"""
	自身生命值低于某个百分比值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return entity.HP / float( entity.HP_Max ) < self._param1 / 100.0

class AICnd23( AICondition ):
	"""
	自身存在某BUFF/DEBUFF时
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0 #buffID
		self._param2 = 0 #BuffLevel

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )
		self._param2 = section.readInt( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		buffs = entity.findBuffsByBuffID( self._param1 )
		if self._param2 <= 0:
			return len( buffs ) > 0
		for b in buffs:
			if entity.getBuff( b )["skill"].getLevel() == self._param2:
				return True
		return False

class AICnd24( AICondition ):
	"""
	自身不存在某BUFF/DEBUFF时
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0 #buffID
		self._param2 = 0 #BuffLevel

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )
		self._param2 = section.readInt( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		buffs = entity.findBuffsByBuffID( self._param1 )
		if self._param2 <= 0:
			return len( buffs ) <= 0
		for b in buffs:
			if entity.getBuff( b )["skill"].getLevel() == self._param2:
				return False
		return True

class AICnd25( AICondition ):
	"""
	上一个使用的技能是某技能
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0 #buffID list

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return entity.queryTemp( "last_use_spell", -1 ) == self._param1

class AICnd26( AICondition ):
	"""
	在一定范围内没有战斗列表中的单位时
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0 #范围半径（米）

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readFloat( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		for eid in entity.enemyList:
			if BigWorld.entities.has_key( eid ):
				if entity.distanceBB( BigWorld.entities[ eid ] ) <= self._param1:
					return False
		return len( entity.enemyList ) > 0

class AICnd27( AICondition ):
	"""
	当前目标处于一定范围内
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0 #范围半径（米）

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readFloat( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		if BigWorld.entities.has_key( entity.targetID ):
			if entity.distanceBB( BigWorld.entities[ entity.targetID ] ) <= self._param1:
				return True
		return False

class AICnd28( AICondition ):
	"""
	当前目标处于一定范围之外
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0 #范围半径（米）

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readFloat( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		if BigWorld.entities.has_key( entity.targetID ):
			if entity.distanceBB( BigWorld.entities[ entity.targetID ] ) > self._param1:
				return True
		return False

class AICnd29( AICondition ):
	"""
	一定范围内的己方单位数量大于某值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0 #范围半径（米）
		self._param2 = 0 #己方单位数量

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readFloat( "param1" )
		self._param2 = section.readInt( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		n = 0
		for eid in entity.friendList:
			if BigWorld.entities.has_key( eid ):
				if entity.distanceBB( BigWorld.entities[ eid ] ) <= self._param1:
					n += 1
		return n > self._param2

class AICnd30( AICondition ):
	"""
	一定范围内的己方单位数量小于某值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0 #范围半径（米）
		self._param2 = 0 #己方单位数量

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readFloat( "param1" )
		self._param2 = section.readInt( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		n = 0
		for eid in entity.friendList:
			if BigWorld.entities.has_key( eid ):
				if entity.distanceBB( BigWorld.entities[ eid ] ) <= self._param1:
					n += 1
		return n < self._param2

class AICnd31( AICondition ):
	"""
	一定范围内的战斗列表中的单位数量大于某值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0 #范围半径（米）
		self._param2 = 0 #己方单位数量

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readFloat( "param1" )
		self._param2 = section.readInt( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		n = 0
		for eid in entity.enemyList:
			if BigWorld.entities.has_key( eid ):
				if entity.distanceBB( BigWorld.entities[ eid ] ) <= self._param1:
					n += 1
		return n > self._param2

class AICnd32( AICondition ):
	"""
	一定范围内的战斗列表中的单位数量小于某值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0 #范围半径（米）
		self._param2 = 0 #己方单位数量

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readFloat( "param1" )
		self._param2 = section.readInt( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		n = 0
		for eid in entity.enemyList:
			if BigWorld.entities.has_key( eid ):
				if entity.distanceBB( BigWorld.entities[ eid ] ) <= self._param1:
					n += 1
		return n < self._param2

class AICnd33( AICondition ):
	"""
	参与战斗的某一指定己方单位生命低于某值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = "" #NPCID
		self._param2 = 0 #生命值（百分比）int

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readString( "param1" )
		self._param2 = section.readInt( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		for eid in entity.friendList:
			if BigWorld.entities.has_key( eid ):
				e = BigWorld.entities[ eid ]
				if e.className == self._param1:
					if e.HP < self._param2:
						return True
		return False

class AICnd34( AICondition ):
	"""
	参与战斗的任意己方单位生命值低于某值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0 #生命值（百分比）int

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		for eid in entity.friendList:
			if BigWorld.entities.has_key( eid ):
				e = BigWorld.entities[ eid ]
				if e.HP < self._param1:
					return True
		return False

class AICnd35( AICondition ):
	"""
	当前目标生命值低于某个值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0.0 #生命值（百分比）

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readFloat( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		if BigWorld.entities.has_key( entity.targetID ):
			e = BigWorld.entities[ entity.targetID ]
			if e.HP / float( e.HP_Max ) < self._param1:
				return True
		return False

class AICnd36( AICondition ):
	"""
	目标等级低于某值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0 #level

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		if BigWorld.entities.has_key( entity.targetID ):
			e = BigWorld.entities[ entity.targetID ]
			if e.level < self._param1:
				return True
		return False

class AICnd37( AICondition ):
	"""
	目标等级高于某值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0 #level

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		if BigWorld.entities.has_key( entity.targetID ):
			e = BigWorld.entities[ entity.targetID ]
			if e.level > self._param1:
				return True
		return False

class AICnd38( AICondition ):
	"""
	当前目标为某职业
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0 #race

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		if BigWorld.entities.has_key( entity.targetID ):
			e = BigWorld.entities[ entity.targetID ]
			if e.getClass() == self._param1:
				return True
		return False

class AICnd39( AICondition ):
	"""
	当前目标存在某BUFF/DEBUFF时
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0 #buffID
		self._param2 = 0 #BuffLevel

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )
		self._param2 = section.readInt( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		if BigWorld.entities.has_key( entity.targetID ):
			e = BigWorld.entities[ entity.targetID ]
			for index, buff in enumerate( e.attrBuffs ):
				if buff["skill"].getBuffID() == self._param1:
					if self._param2 <= 0:
						return True
					else:
						if buff["skill"].getLevel() == self._param2:
							return True
		return False

class AICnd40( AICondition ):
	"""
	当前目标不存在某BUFF/DEBUFF时
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0 #buffID
		self._param2 = 0 #BuffLevel

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )
		self._param2 = section.readInt( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		if BigWorld.entities.has_key( entity.targetID ):
			e = BigWorld.entities[ entity.targetID ]
			for index, buff in enumerate( e.attrBuffs ):
				if buff["skill"].getBuffID() == self._param1:
					if self._param2 <= 0:
						return False
					else:
						if buff["skill"].getLevel() == self._param2:
							return False
		return True

class AICnd41( AICondition ):
	"""
	当前目标不是某职业时
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0 #race

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		if BigWorld.entities.has_key( entity.targetID ):
			e = BigWorld.entities[ entity.targetID ]
			if e.getClass() != self._param1:
				return True
		return False

class AICnd42( AICondition ):
	"""
	当前目标正在吟唱一个法术时
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		if BigWorld.entities.has_key( entity.targetID ):
			e = BigWorld.entities[ entity.targetID ]
			if e.intonating():
				return True
		return False

class AICnd43( AICondition ):
	"""
	当前目标生命值高于某个值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0.0 #生命值（百分比）

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readFloat( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		if BigWorld.entities.has_key( entity.targetID ):
			e = BigWorld.entities[ entity.targetID ]
			if e.HP / float( e.HP_Max ) > self._param1:
				return True
		return False

class AICnd44( AICondition ):
	"""
	AI命令是否合法
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = [] 	 # NPCID列表[ npcclass, npclass...]
		self._param2 = []	 # AI命令列表[uint16,...]

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		param1 = section.readString( "param1" )
		if param1:
			self._param1 = param1.split( "," )
		self._param2 = [ int( e ) for e in section.readString( "param2" ).split(",") ]

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		cmdInfo = entity.queryTemp( "AICommand", 0 )
		if cmdInfo == 0:
			return False
		npcID, className, cmd = cmdInfo
		if cmd not in self._param2:
			return False
		if not self._param1:	# 如果没有指定发布者则响应所有发布者的命令
			return True
		if className in self._param1:
			return True
		return False

class AICnd45( AICondition ):
	"""
	战斗列表增加（事件：战斗列表被被改变）
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return entity.aiTargetID in entity.enemyList

class AICnd46( AICondition ):
	"""
	当前作用对象为某类型
	1		# 角色
	2		# NPC
	3		# 怪物
	4		# 宠物
	6		# 掉下物品
	7		# 出生点
	8		# 传送门
	9		# 传送点
	10	# 传送师
	11	# 天气系统
	12	# 任务箱子
	13	# ？
	14	# 杂物（其它没有特殊需要判断的类型都归为此类）

	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0 #生命值（百分比）

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		if not BigWorld.entities.has_key( entity.targetID ):
			ERROR_MSG( "targetID %i is error." % entity.targetID )
			return
		return BigWorld.entities[ entity.targetID ].isEntityType( self._param1 )

class AICnd47( AICondition ):
	"""
	当前目标为某类
	1		# 角色
	2		# NPC
	3		# 怪物
	4		# 宠物
	6		# 掉下物品
	7		# 出生点
	8		# 传送门
	9		# 传送点
	10	# 传送师
	11	# 天气系统
	12	# 任务箱子
	13	# ？
	14	# 杂物（其它没有特殊需要判断的类型都归为此类）
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0 #生命值（百分比）

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		if not BigWorld.entities.has_key( entity.aiTargetID ):
			WARNING_MSG( "aiTargetID is error." )
			return False
		return BigWorld.entities[ entity.aiTargetID ].isEntityType( self._param1 )

class AICnd48( AICondition ):
	"""
	伤害列表增加（事件：战斗列表被被改变）
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return entity.aiTargetID in entity.damageList

class AICnd49( AICondition ):
	"""
	指定技能可对当前目标使用
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt64( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		# 攻击判断
		try:
			enemy = BigWorld.entities[ entity.targetID ]
		except:
			return False
		target = SkillTargetObjImpl.createTargetObjEntity( enemy )
		try:
			spell = g_skills[ self.param1 ]						# 获取配置的攻击技能
		except:
			ERROR_MSG( "Entity classname %s use skill error, id is %i."%( entity.className ,self.param1 ))
			return False

		state = spell.useableCheck( entity,  target )
		if state != csstatus.SKILL_GO_ON and state != csstatus.SKILL_TOO_FAR:
			return False
		return True

class AICnd50( AICondition ):
	"""
	指定自身等级技能可对当前目标使用
	参数中的技能指未展开的技能ID，需要配上该NPC的等级成为展开后的技能ID。
	如：NPC等级为32，技能ID为123456，需要判断的技能ID应为123456032
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt64( "param1" ) * 1000

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		# 攻击判断
		try:
			enemy = BigWorld.entities[ entity.targetID ]
		except:
			return False
		target = SkillTargetObjImpl.createTargetObjEntity( enemy )
		try:
			spell = g_skills[ self.param1 + entity.level ]						# 获取配置的攻击技能
		except:
			ERROR_MSG( "Use skill error, id is %i. className: %s."%(self.param1 + entity.level, entity.className ) )
			return False
		state = spell.useableCheck( entity,  target )
		if state != csstatus.SKILL_GO_ON and state != csstatus.SKILL_TOO_FAR:
			return False
		return True


class AICnd51( AICondition ):
	"""
	检测嘲讽施放者有效性
	检查对我使用嘲讽技能的目标 当前的有效性（可否对其攻击）
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		buffs = entity.findBuffsByBuffID( 199001 )
		if len( buffs ) <= 0:
			return False

		casterID = entity.getBuff( buffs[0] )["caster"]
		return BigWorld.entities.has_key( casterID )

class AICnd52( AICondition ):
	"""
	脱离回走状态
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return entity.getOldSubState() == csdefine.M_SUB_STATE_GOBACK and entity.getSubState() != csdefine.M_SUB_STATE_GOBACK

class AICnd53( AICondition ):
	"""
	某记录时间是否到达
	主要用于一些时间查询等操作：
	如 一段时间内 NPC没有做什么就怎么样。

	要实现这个当然还需要配合一个相关动作：
	”记录当前时间“   参数是和该标签名一样的
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 1
		self.param2 = 1 # 一个时间段  如：30秒

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readString( "param1" )
		self.param2 = section.readInt( "param2" )
		self.param3 = section.readInt( "param3" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		signTime = entity.queryTemp( self.param1, -1.0 )
		return signTime != -1 and BigWorld.time() - signTime >= self.param2


class AICnd54( AICondition ):
	"""
	任务拥有者与NPC之间距离是否小等于某值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" ) # 半径大小  可用来作为距离

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		ownerBase = entity.queryTemp( "npc_ownerBase", None )
		if ownerBase:
			ownerID = ownerBase.id
			if BigWorld.entities.has_key( ownerID ):
				owner = BigWorld.entities[ ownerID ]
				# 主人是否还要我
				if owner.isMyOwnerFollowNPC( entity.id ):
					distance = csarithmetic.distancePP3( owner.position, entity.position )
					return distance <= self.param1
		else:
			pass
			#ERROR_MSG( "can not find the owner!" )
		# 找不到算距离无限
		return False

class AICnd55( AICondition ):
	"""
	任务拥有者与NPC之间距离是否大于某值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" ) # 半径大小  可用来作为距离

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		ownerBase = entity.queryTemp( "npc_ownerBase", None )
		if ownerBase:
			ownerID = ownerBase.id
			if BigWorld.entities.has_key( ownerID ):
				owner = BigWorld.entities[ ownerID ]
				# 主人是否还要我
				if owner.isMyOwnerFollowNPC( entity.id ):
					distance = csarithmetic.distancePP3( owner.position, entity.position )
					return distance >= self.param1
		else:
			pass
			#ERROR_MSG( "can not find the owner!" )
		# 找不到算距离无限
		return True

class AICnd56( AICondition ):
	"""
	NPC是否到达指定范围内
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = (0,0,0)
		self.param2 = 2
		self.param3 = "fengming"

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

		position = section.readString( "param1" )				# 坐标
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param1" % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.param1 = pos

		self.param2 = section.readFloat( "param2" ) # 半径大小
		self.param3 = section.readString( "param3" ) # map

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		map = entity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		if map != self.param3:
			return False
		distance = csarithmetic.distancePP3( self.param1, entity.position )
		return distance <= self.param2

class AICnd57( AICondition ):
	"""
	NPC是否未到达指定范围
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = (0,0,0)
		self.param2 = 2
		self.param3 = "fengming"

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

		position = section.readString( "param1" )				# 坐标
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param1" % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.param1 = pos

		self.param2 = section.readFloat( "param2" ) # 半径大小
		self.param3 = section.readString( "param3" ) # map

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		map = entity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		if map != self.param3:
			return False
		distance = csarithmetic.distancePP3( self.param1, entity.position )
		return distance > self.param2

class AICnd58( AICondition ):
	"""
	检测NPC是否可以变成Monster
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return entity.queryTemp( "state_npc_speaker", True )


class AICnd59( AICondition ):
	"""
	从属怪物和主人间大于某一距离
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 3.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" ) #距离
		if self.param1 < 0.1:
			self.param1 = 30.0



	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		ownerID = entity.getOwnerID()
		if ownerID:
			if BigWorld.entities.has_key( ownerID ):
				owner = BigWorld.entities[ ownerID ]
			else:
				return False
		else:
			return False
		distance = csarithmetic.distancePP3( owner.position, entity.position )
		return distance >= self.param1


class AICnd60( AICondition ):
	"""
	从属怪物和主人间小于某一距离
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 20.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" ) #距离


	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		ownerID = entity.getOwnerID()
		if ownerID:
			if BigWorld.entities.has_key( ownerID ):
				owner = BigWorld.entities[ ownerID ]
			else:
				return False
		else:
			return False
		distance = csarithmetic.distancePP3( owner.position, entity.position )
		return distance <= self.param1



class AICnd61( AICondition ):
	"""
	从属怪物找不到主人
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )


	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		ownerID = entity.getOwnerID()
		if ownerID:
			if not BigWorld.entities.has_key( ownerID ):
				return True
			else:
				return False
		else:
			return False


class AICnd62( AICondition ):
	"""
	处于休闲状态
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return entity.getState() == csdefine.ENTITY_STATE_FREE


class AICnd63( AICondition ):
	"""
	从属怪物和主人不在一个空间中
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )


	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		ownerID = entity.getOwnerID()
		if BigWorld.entities.has_key( ownerID ):
			return BigWorld.entities[ownerID].spaceID != entity.spaceID

		return True


class AICnd64( AICondition ):
	"""
	主人进入战斗状态
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )


	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		ownerID = entity.getOwnerID()
		if ownerID:
			if BigWorld.entities.has_key( ownerID ):
				owner = BigWorld.entities[ ownerID ]
			else:
				return False
		else:
			return False
		return owner.getState() == csdefine.ENTITY_STATE_FIGHT

class AICnd65( AICondition ):
	"""
	和主人丢失联系时间大于设定时间
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" ) #时间


	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		ownerID = entity.getOwnerID()
		if ownerID:
			if BigWorld.entities.has_key( ownerID ):
				entity.setTemp( 'connectTimer', time.time() )
				return False
		lastTime = entity.queryTemp( 'connectTimer', 0 )
		return lastTime != 0 and time.time() - lastTime > self.param1


class AICnd66( AICondition ):
	"""
	任务完成
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )


	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return entity.queryTemp( 'questFinish', False )

class AICnd67( AICondition ):
	"""
	战场统帅等NPC判断进入视野的玩家是否为敌对帮会
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )


	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		if not BigWorld.entities.has_key( entity.aiTargetID ):
			return False

		isRight = entity.isRight
		p = BigWorld.entities[ entity.aiTargetID ]
		if p.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = p.getOwner()
			if owner.etype == "MAILBOX" : return False
			p = owner.entity
		if isRight:
			if p.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				return not p.tong_dbID in BigWorld.globalData[ "CityWarRightTongDBID" ]
			else:
				#  如果是怪物
				return not p.isRight
		else:
			if p.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				return p.tong_dbID in BigWorld.globalData[ "CityWarRightTongDBID" ]
			else:
				#  如果是怪物
				return p.isRight

		return p.tong_dbID in BigWorld.globalData[ "CityWarRightTongDBID" ]


class AICnd68( AICondition ):
	"""
	固定时间段做某时间
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section['param1'].asString			#key (例如： 'start_time' ）
		self._param2 = section['param2'].asFloat			#时间段

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		startTime = entity.queryTemp( self._param1, 0.0 )
		if self._param2 < BigWorld.time() - startTime:
			entity.setTemp( self._param1, BigWorld.time() )
			return True
		return False

class AICnd69( AICondition ):
	"""
	镖车找不到运镖者（如距离太远）
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" ) # 半径大小  可用来作为距离
		if self.param1 < 20.0:
			self.param1 = 20.0

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		owner = entity.getOwnerID()
		if not owner:
			return True
		if BigWorld.entities.has_key( owner ):
			owner = BigWorld.entities[ owner ]
		else:
			return True
		distance = csarithmetic.distancePP3( owner.position, entity.position )
		return distance >= self.param1

class AICnd70( AICondition ):
	"""
	NPC拥有者的某任务的某TASK是否未完成
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 0
		self.param2 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt( "param1" )
		self.param2 = section.readInt( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		ownerBase = entity.queryTemp( "npc_ownerBase", None )
		if ownerBase:
			ownerID = ownerBase.id
			if BigWorld.entities.has_key( ownerID ):
				owner = BigWorld.entities[ ownerID ]
				# 主人是否还要我
				if owner.isMyOwnerFollowNPC( entity.id ):
					return not owner.taskIsCompleted( self.param1, self.param2 )
			else:
				if ownerBase.cell.isMyOwnerFollowNPC( entity.id ):
					return not ownerBase.cell.taskIsCompleted( self.param1, self.param2 )
		# 找不到等情况,均算未完成
		return True

class AICnd71( AICondition ):
	"""
	NPC的拥有者是否被杀死了或者下线了
	这里的拥有者指的是拥有怪物所有权的玩家，但是实现此NPC的类里对其所有权拥有者也设置了进行了存储
	目前只能针对宝藏猎手、盗宝贼等藏宝图系统中的怪物
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		ownerID = entity.getOwnerID()
		if ownerID:
			if BigWorld.entities.has_key( ownerID ):
				owner = BigWorld.entities[ ownerID ]
				if owner.getState() == csdefine.ENTITY_STATE_DEAD:
					# 如果角色死亡
					return True
				else:
					# 如果角色下线
					return False
			else:
				return True
		return True

class AICnd72( AICondition ):
	"""
	自身等级在指定范围内
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 0
		self.param2 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt( "param1" )
		self.param2 = section.readInt( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return entity.level >= self.param1 and entity.level <= self.param2

class AICnd73( AICondition ):
	"""
	是否处于某状态下达到一定时间
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 0	# 是否处于某状态
		self.param2 = 0	# 是否达到一定时间

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt( "param1" )	# 是否处于某状态
		self.param2 = section.readInt( "param2" )	# 是否达到一定时间

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		if self.param1 != entity.getState():
			return False

		lastTime = entity.queryTemp( "time_in_state", 0 )
		if lastTime != 0 and int( time.time() - lastTime ) < self.param2 and entity.queryTemp( "count_in_state", 0 ) < self.param2:
			entity.setTemp( "time_in_state", time.time() )
			entity.setTemp( "count_in_state", entity.queryTemp( "count_in_state", 0 ) + 1 )
		elif entity.queryTemp( "count_in_state", 0 ) >= self.param2:
			return True
		else:
			entity.setTemp( "time_in_state", time.time() )
			entity.setTemp( "count_in_state", 0 )
		return False

class AICnd74( AICondition ):
	"""
	存活时间大于指定值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt( "param1" )	# 是否处于某状态

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		if entity.queryTemp('spawnTime', 0 ) == 0:
			entity.setTemp( 'spawnTime', time.time() )
		return time.time() - entity.queryTemp('spawnTime') > self.param1


class AICnd75( AICondition ):
	"""
	怪物血量少于指定百分比
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 0


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return float(entity.HP)/ float(entity.HP_Max)  < self.param1

class AICnd76( AICondition ):
	"""
	是否大于NPC发言后一定时间
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 0


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		if entity.queryTemp( "tempSayFlag", False ) and time.time() - entity.queryTemp( "tempSayTime", 0 ) >= self.param1:
			entity.setTemp( "tempSayFlag", False )	# 重置标记
			return True
		return False

class AICnd77( AICondition ):
	"""
	是否存在某标记
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readString( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return entity.queryTemp( self.param1 )

class AICnd78( AICondition ):
	"""
	一定范围内是否有特定类型的怪物
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 0.0
		self.classNames = []
		self.param3 = "Monster"		# 默认为Monster


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" )			# 范围
		self.classNames = section.readString( "param2" ).split("|")		# className
		self.param3 = section.readString( "param3" )		# 怪物EntityType

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		monsterList = entity.entitiesInRangeExt( self.param1, self.param3, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in monsterList:
			if e.className in self.classNames and not e.isDead():
				return True
		return False

class AICnd79( AICondition ):
	"""
	一定范围内特定类型的怪物，血量是否在特定范围内
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 0.0
		self.param2 = ""
		self.param3 = []
		self.param4 = "Monster"

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" )							# 范围
		self.param2 = section.readString( "param2" )						# className
		self.param3 = (section.readString( "param3" )).split( ":" )			# 血量范围值，such as : 10:60
		self.param4 = section.readString( "param4" )						# 怪物EntityType

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		flag = False
		monsterList = entity.entitiesInRangeExt( self.param1, self.param4, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in monsterList:
			if e.className == self.param2:
				target = e
				flag = True
				break

		if not flag:
			return False

		hpPercent = float(target.HP)/ float(target.HP_Max) * 100.0

		if float(self.param3[0]) <= hpPercent and hpPercent <= float(self.param3[1]):
			return True

		return False

class AICnd80( AICondition ):
	"""
	指定范围内是否有pk值大于某数的玩家
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._radius = section.readFloat( "param1" ) # 搜索半径
		self._pkValue = section.readInt( "param2" ) # 搜索pk值在多少以上

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		es = entity.entitiesInRangeExt( self._radius, "Role", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in es:
			if e.state != csdefine.ENTITY_STATE_DEAD and \
				e.state != csdefine.ENTITY_STATE_PENDING:
				if e.pkValue > self._pkValue:
					return True
		return False


class AICnd81( AICondition ):
	"""
	指定技能可对自身使用
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt64( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		target = SkillTargetObjImpl.createTargetObjEntity( entity )

		try:
			spell = g_skills[ self.param1 ]						# 获取配置的攻击技能
		except:
			ERROR_MSG( "Entity classname %s use skill error, id is %i."%( entity.className ,self.param1 ))
			return False
		state = spell.useableCheck( entity,  target )
		if state != csstatus.SKILL_GO_ON and state != csstatus.SKILL_TOO_FAR:
			return False
		return True


class AICnd82( AICondition ):
	"""
	指定自身等级技能可对自身使用
	参数中的技能指未展开的技能ID，需要配上该NPC的等级成为展开后的技能ID。
	如：NPC等级为32，技能ID为123456，需要判断的技能ID应为123456032
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt64( "param1" ) * 1000

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		# 攻击判断
		target = SkillTargetObjImpl.createTargetObjEntity( entity )
		spell = g_skills[ self.param1 + entity.level ]						# 获取配置的攻击技能
		state = spell.useableCheck( entity,  target )
		if state != csstatus.SKILL_GO_ON and state != csstatus.SKILL_TOO_FAR:
			return False
		return True

class AICnd83( AICondition ):
	"""
	是否不存在某标记
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 0


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readString( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return not entity.queryTemp( self.param1 )

class AICnd84( AICondition ):
	"""
	（城战AI）进入视野的entity是否为战场塔楼
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		e = BigWorld.entities.get( entity.aiTargetID )
		return e and e.isEntityType( csdefine.ENTITY_TYPE_TONG_CITYWAR_MONSTER ) and e.cw_flag == csdefine.TONG_CW_FLAG_TOWER

class AICnd85( AICondition ):
	"""
	范围内是否有某类型的怪物
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 0.0
		self.param2 = "Monster"		# 默认为Monster


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" )			# 范围
		self.param2 = section.readString( "param2" )		# 怪物EntityType

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		monsterList = entity.entitiesInRangeExt( self.param1, self.param2, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in monsterList:
			if not e.isDead():
				return True
		return False

class AICnd86( AICondition ):
	"""
	范围内是否没有某类型的怪物
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 0.0
		self.param2 = "Monster"		# 默认为Monster


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" )			# 范围
		self.param2 = section.readString( "param2" )		# 怪物EntityType

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		monsterList = entity.entitiesInRangeExt( self.param1, self.param2, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		if len( monsterList ) > 0:
			for i in monsterList:
				if not i.isDead():
					return False
			return True
		return True

class AICnd87( AICondition ):
	"""
	一定范围内没有特定类型的怪物
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 0.0
		self.param2 = ""
		self.param3 = "Monster"		# 默认为Monster


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" )			# 范围
		self.param2 = section.readString( "param2" ).split("|")		# className
		self.param3 = section.readString( "param3" )		# 怪物EntityType

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		monsterList = entity.entitiesInRangeExt( self.param1, self.param3, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		if len( monsterList ) > 0:
			for i in monsterList:
				if not i.isDead() and i.className in self.param2:
					return False
		return True

class AICnd88( AICondition ):
	"""
	战斗列表中有某className的怪物
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readString( "param1" )			# className

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		for enemyID in entity.enemyList:
			enemy = BigWorld.entities.get( enemyID )
			if enemy and hasattr( enemy, "className" ) and enemy.className == self.param1:
				return True
		return False

class AICnd89( AICondition ):
	"""
	一定范围内是否有特定类型的有特定buff的entity
	"""
	def __init__( self ):
		AICondition.__init__( self )

		self.param1 = 0.0
		self.param2 = 0
		self.param3 = "Monster"		# 默认为Monster

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

		self.param1 = section.readFloat( "param1" )							# 范围
		self.param2 = section.readInt( "param2" )							# buffID
		self.param3 = section.readString( "param3" )						# EntityType

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		entityList = entity.entitiesInRangeExt( self.param1, self.param3, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in entityList:
			if not e.isDead():
				buffs = e.findBuffsByBuffID( self.param2 )
				if len( buffs ) > 0:
					return True
		return False

class AICnd90( AICondition ):
	"""
	一定范围内是否没有特定类型的有特定buff的entity
	"""
	def __init__( self ):
		AICondition.__init__( self )

		self.param1 = 0.0
		self.param2 = 0
		self.param3 = "Monster"		# 默认为Monster

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

		self.param1 = section.readFloat( "param1" )							# 范围
		self.param2 = section.readInt( "param2" )							# buffID
		self.param3 = section.readString( "param3" )						# EntityType

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		entityList = entity.entitiesInRangeExt( self.param1, self.param3, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in entityList:
			if not e.isDead():
				buffs = e.findBuffsByBuffID( self.param2 )
				if len( buffs ) > 0:
					return False
		return True

class AICnd91( AICondition ):
	"""
	一定范围内是否有特定类型的entity
	"""
	def __init__( self ):
		AICondition.__init__( self )

		self.param1 = 0.0
		self.param2 = "Monster"		# 默认为Monster

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

		self.param1 = section.readFloat( "param1" )							# 范围
		self.param2 = section.readString( "param2" )						# EntityType

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		entityList = entity.entitiesInRangeExt( self.param1, self.param2, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in entityList:
			if not e.isDead():
				return True
		return False

class AICnd92( AICondition ):
	"""
	一定范围内是否没有特定类型的entity
	"""
	def __init__( self ):
		AICondition.__init__( self )

		self.param1 = 0.0
		self.param2 = "Monster"		# 默认为Monster

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

		self.param1 = section.readFloat( "param1" )							# 范围
		self.param2 = section.readString( "param2" )						# EntityType

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		entityList = entity.entitiesInRangeExt( self.param1, self.param2, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in entityList:
			if getattr( e, "isDead") and not e.isDead():
				return False
		return True

class AICnd93( AICondition ):
	"""
	一定范围内有特定类型的特定className的有特定buff的entity
	"""
	def __init__( self ):
		AICondition.__init__( self )

		self.param1 = 0.0
		self.param2 = 0
		self.param3 = "Monster"		# 默认为Monster

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

		self.param1 = section.readFloat( "param1" )							# 范围
		self.param2 = section.readInt( "param2" )							# buffID
		self.param3 = section.readString( "param3" )						# EntityType
		self.param4 = section.readString( "param4" )						# className

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		entityList = entity.entitiesInRangeExt( self.param1, self.param3, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in entityList:
			if hasattr( e, "className" ) and e.className == self.param4 and not e.isDead():
				buffs = e.findBuffsByBuffID( self.param2 )
				if len( buffs ) > 0:
					return True
		return False

class AICnd94( AICondition ):
	"""
	一定范围内没有特定类型的特定className的有特定buff的entity
	"""
	def __init__( self ):
		AICondition.__init__( self )

		self.param1 = 0.0
		self.param2 = 0
		self.param3 = "Monster"		# 默认为Monster

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

		self.param1 = section.readFloat( "param1" )							# 范围
		self.param2 = section.readInt( "param2" )							# buffID
		self.param3 = section.readString( "param3" )						# EntityType
		self.param4 = section.readString( "param4" )						# className

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		entityList = entity.entitiesInRangeExt( self.param1, self.param3, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in entityList:
			if hasattr( e, "className" ) and e.className == self.param4 and not e.isDead():
				buffs = e.findBuffsByBuffID( self.param2 )
				if len( buffs ) > 0:
					return False
		return True



class AICnd95( AICondition ):
	"""
	血量变化值（之前记录了一个初始值）
	"""
	def __init__( self ):
		AICondition.__init__( self )

		self.param1 = 0


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt( "param1" )							# 变化值


	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		saveHp = entity.queryTemp( "ai_save_HP_value", 0 )

		if saveHp == 0 or saveHp - entity.HP > int( self.param1 * 0.01 * entity.HP_Max ):
			return True

		return False


class AICnd96( AICondition ):
	"""
	对方是否是兔子
	"""
	def __init__( self ):
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		target = BigWorld.entities.get( entity.aiTargetID )
		if target and target.isReal():
			if target.findBuffByID( csconst.RABBIT_RUN_CATCH_RABBIT_RABBIT_BUFF_ID ) is not None:
				return True
		return False



class AICnd97( AICondition ):
	"""
	指定怪物不处于死亡状态
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" )							# 范围
		self.param2 = section.readString( "param2" )						# EntityType
		self.param3 = section.readString( "param3" )						# className

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		entityList = entity.entitiesInRangeExt( self.param1, self.param2, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		monster = None
		for e in entityList:
			if hasattr( e, "className" ) and e.className == self.param3:
				monster = e
				break
		return monster and monster.getState() != csdefine.ENTITY_STATE_DEAD


class AICnd98( AICondition ):
	"""
	怪物是否不具有某个标志位
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt( "param1" )							# 标志位


	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return not entity.hasFlag( self.param1 )


class AICnd99( AICondition ):
	"""
	由某状态切换到特定状态
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt( "param1" )							# 旧状态
		self.param2 = section.readInt( "param2" )							# 新状态


	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		return entity.lastState == self.param1 and entity.state == self.param2

class AICnd100( AICondition ):
	"""
	镖车查找复数运镖者（帮会运镖） by 姜毅
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" ) # 半径大小  可用来作为搜索距离
		self.param2 = section.readInt( "param2" )	# 允许离开镖车的最长时间，单位 秒

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		ownerID = entity.getOwnerID()
		if not ownerID:
			return True
		g = BigWorld.entities.get
		if BigWorld.entities.has_key( ownerID ):
			owner = g(ownerID)
		else:
			return True
		questID = entity.queryTemp('questID')
		memberIDDict = entity.queryTemp( "dartMembers", {} )
		t = int(time.time())
		for mid in memberIDDict.iterkeys():
			mt = memberIDDict[mid]
			member = g(mid)
			if mt > 0 and t - mt > self.param2:
				memberIDDict[mid] = -1	# 宣告失败
				if  member is not None:
					#member.questTaskFailed( questID, 1 )
					from Love3 import g_taskData as g_questDict
					questObj = g_questDict[questID]
					questAfterCList = questObj.afterComplete_
					member_ql = []
					member_taskIndex = 1
					for qaf in questAfterCList:
						if hasattr( qaf, "_quests" ):
							_ql = getattr( qaf, "_quests" )
							member_ql = [int(qid[0]) for qid in _ql]
							member_taskIndex = qaf._eventIndex
							break

					for qID in member.questsTable.keys():		# 设置成员运镖任务failure
						if qID in member_ql:
							member.questTaskFailed( qID, member_taskIndex )

				continue
			dis = (csarithmetic.distancePP3( member.position, entity.position ) - self.param1) if member is not None else 0
			memberIDDict[mid] = t if dis >= 0 and mt == 0 else mt
		return True

class AICnd101( AICondition ):
	# 自身存在战利品拥有者
	def check( self, ai, entity ):
		return entity.bootyOwner != ( 0, 0 )

class AICnd102( AICondition ):
	"""
	entity是否位于某些地图
	"""
	def __init__( self ):
		AICondition.__init__( self )
		self.spaceNameList = None

	def init( self, section ):
		"""
		"""
		AICondition.init( self, section )
		self.spaceNameList = section.readString( "param1" ).split( ";" )

	def check( self, ai, entity ):
		"""
		"""
		return entity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) in self.spaceNameList

class AICnd103( AICondition ):
	"""
	从属怪物和主人间大于某一距离( 找不到主人返回True )
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 3.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" ) #距离
		if self.param1 < 0.1:
			self.param1 = 30.0

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		ownerID = entity.getOwnerID()
		if ownerID:
			if BigWorld.entities.has_key( ownerID ):
				owner = BigWorld.entities[ ownerID ]
			else:
				return True
		else:
			return False
		distance = csarithmetic.distancePP3( owner.position, entity.position )
		return distance >= self.param1

class AICnd104( AICondition ):
	"""
	在一定范围内有特定类型且没有特定BUFF的entity(只要有一个就行 ) add by wuxo 2011-12-7
	"""
	def __init__( self ):
		AICondition.__init__( self )

		self.param1 = 0.0
		self.param2 = 0
		self.param3 = "Monster"		# 默认为Monster

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

		self.param1 = section.readFloat( "param1" ) #范围							# 范围
		self.param2 = section.readInt( "param2" )	#bufferID							# buffID
		self.param3 = section.readString( "param3" )# 类型				# EntityType

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		entityList = entity.entitiesInRangeExt( self.param1, self.param3, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in entityList:
			if not e.isDead():
				buffs = e.findBuffsByBuffID( self.param2 )
				if len( buffs ) == 0:
					return True

		return False


class AICnd105( AICondition ):
	"""
	怪物和攻击目标的距离是不是大于指定值
	"""
	def __init__( self ):
		AICondition.__init__( self )

	def init( self, section ):
		"""
		"""
		AICondition.init( self, section )
		self.distance = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		"""
		target = BigWorld.entities.get( entity.targetID, None )
		if target:
			return self.distance < csarithmetic.distancePP3( target.position, entity.position )
		return False


class AICnd106( AICondition ):
	"""
	怪物和攻击目标的距离是不是小于指定值
	"""
	def __init__( self ):
		AICondition.__init__( self )

	def init( self, section ):
		"""
		"""
		AICondition.init( self, section )
		self.distance = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		"""
		target = BigWorld.entities.get( entity.targetID, None )
		if target:
			return self.distance > csarithmetic.distancePP3( target.position, entity.position )
		return False

class AICnd107( AICondition ):
	"""
	判断一定范围内特定className的怪物数量是否满足特定的数量关系
	"""
	def __init__( self ):
		AICondition.__init__( self )
		self.param1 = 0.0
		self.param2 = ""
		self.param3 = 0				# entity数量
		self.param4 = 0				# 判断符号
		self.param5 = "Monster"		# 默认为Monster

	def init( self, section ):
		"""
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" ) 	# 范围
		self.param2 = section.readString( "param2" )	# className
		self.param3 = section.readInt( "param3" )		# entity数量
		self.param4 = section.readInt( "param4")		# 数量关系符号：0代表“=”，1代表“<”，2代表“>”
		self.param5 = section.readString( "param5")		# entityType

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		monstersList = []
		entityList = entity.entitiesInRangeExt( self.param1, self.param5, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in entityList:
			if e.className == self.param2 and not e.isDead():
				monstersList.append( e.className )
		#if len( monstersList ) == 0:
			#return True
		if self.param4 == 0 and len( monstersList ) == self.param3:
			# 如果满足“=”特定entity数量
			return True
		if self.param4 == 1 and len( monstersList ) < self.param3:
			# 如果满足“<”特定entity数量
			return True
		if self.param4 == 2 and len( monstersList ) > self.param3:
			# 如果满足“>”特定entity数量
			return True
		return False


class AICnd108( AICondition ):
	"""
	是否没有到达AI要去的位置的一定范围
	"""
	def __init__( self ):
		AICondition.__init__( self )

	def init( self, section ):
		"""
		"""
		AICondition.init( self, section )
		self.distance = section.readFloat( "param1" )

	def check( self, ai, entity ):
		"""
		"""
		pos = entity.queryTemp( "AIGotoPosition", None )
		if pos:
			return self.distance > csarithmetic.distancePP3( entity.position, pos )
		return False



class AICnd109( AICondition ):
	"""
	是否达到和攻击目标在x轴大于一定距离的位置
	"""
	def __init__( self ):
		AICondition.__init__( self )

	def init( self, section ):
		"""
		"""
		AICondition.init( self, section )
		self.distance = section.readFloat( "param1" )

	def check( self, ai, entity ):
		"""
		"""
		target = BigWorld.entities.get( entity.targetID, None )
		if target:
			return abs( entity.position.x - target.position.x ) > self.distance


class AICnd110( AICondition ):
	"""
	是否达到和攻击目标在z轴大于一定距离的位置
	"""
	def __init__( self ):
		AICondition.__init__( self )

	def init( self, section ):
		"""
		"""
		AICondition.init( self, section )
		self.distance = section.readFloat( "param1" )

	def check( self, ai, entity ):
		"""
		"""
		target = BigWorld.entities.get( entity.targetID, None )
		if target:
			return abs( entity.position.z - target.position.z ) > self.distance

class AICnd111( AICondition ):
	"""
	队长是否不存在
	"""
	def __init__( self ):
		AICondition.__init__( self )

	def init( self, section ):
		"""
		"""
		AICondition.init( self, section )
		self.distance = section.readFloat( "param1" )
		self.captainSign = section.readString( "param2" )

	def check( self, ai, entity ):
		"""
		"""
		id = entity.queryTemp( self.captainSign, 0 )
		captain = BigWorld.entities.get( id, None )
		if captain and captain.targetID == entity.targetID:
			return False
		return True

class AICnd112( AICondition ):
	"""
	怪物自身是队长
	"""
	def __init__( self ):
		AICondition.__init__( self )

	def init( self, section ):
		"""
		"""
		AICondition.init( self, section )
		self.captainSign = section.readString( "param1" )

	def check( self, ai, entity ):
		"""
		"""
		return entity.id == entity.queryTemp( self.captainSign, 0 )

class AICnd113( AICondition ):
	"""
	是否在攻击目标的左右一定范围外
	"""
	def __init__( self ):
		AICondition.__init__( self )

	def init( self, section ):
		"""
		"""
		AICondition.init( self, section )
		self.Xdistance = section.readFloat( "param1" )
		self.range = section.readFloat( "param2" )

	def check( self, ai, entity ):
		"""
		"""
		target = BigWorld.entities.get( entity.targetID, None )
		if target:
			distance1 = entity.position.distTo( ( target.position.x + self.Xdistance, target.position.y, target.position.z ) )
			distance2 = entity.position.distTo( ( target.position.x - self.Xdistance, target.position.y, target.position.z ) )

			return not ( distance1 < self.range or distance2 < self.range )

class AICnd114( AICondition ):
	"""
	判断NPC的拥有者的状态（使用于任务怪NPC） added by dqh
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 0				# 默认为自由状态

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt( "param1" ) # 角色的状态

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		ownerID = entity.queryTemp( "ownerID", 0 )
		if ownerID == 0:
			return False
		try:
			owner = BigWorld.entities.get( ownerID )
			return owner.state  == self.param1
		except:
			ERROR_MSG( "AICnd114:can not find the owner!" )

class AICnd115( AICondition ):
	"""
	判断当前巡逻路线是否已经准备好
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.patrolNode = ""
		self.graphID = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.patrolNode = section.readString( "param1" )
		self.graphID = section.readString( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		patrolList = BigWorld.PatrolPath( self.graphID )
		if not patrolList or not patrolList.isReady() or len(self.patrolNode) <= 0:
			return False
		else:
			return True

class AICnd116( AICondition ):
	"""
	判断NPC的战利品拥有者的状态(使用于非ConvoyMonster类型的任务怪NPC)
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 0				# 默认为自由状态

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt( "param1" ) # 角色的状态

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		bootyOwner = entity.getBootyOwner()
		if bootyOwner[1] != 0:
			bootyers = entity.searchTeamMember( bootyOwner[1], Const.TEAM_GAIN_EXP_RANGE )
			if len( bootyers ) == 0:
				return False
			for teamMember in bootyers:
				if teamMember.state != self.param1:
					return False
			return True
		elif bootyOwner[0] != 0:
			try:
				player = BigWorld.entities[ bootyOwner[0] ]
				return player.state == self.param1
			except:
				ERROR_MSG( "AICnd115:can not find the bootyOwner!" )

class AICnd117( AICondition ):
	"""
	判断上一拨同classname并且具有相同的战利品拥有者的怪物是否全部死亡
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 50				# 范围
		self.param2 = ""				# className

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt( "param1" ) 		# 范围
		self.param2 = section.readString( "param2" )	# className

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		bootyOwner = entity.getBootyOwner()
		monsterList = entity.entitiesInRangeExt( self.param1, "Monster", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		if len( monsterList ) == 0:
			return True
		else:
			for e in monsterList:
				if e.className == self.param2 and e.getBootyOwner() == bootyOwner and not e.isDead():		#只要还有一个怪是className，而且和entity的拥有者一样
					return False
		return True

class AICnd118( AICondition ):
	"""
	判断拥有者（主人）是否为某状态（限于有主人的怪物使用）
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.param1 = 0				# 默认为自由状态

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt( "param1" ) 				# 角色的状态

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		ownerID = entity.getOwnerID()
		if ownerID != 0:
			owner = BigWorld.entities.get( ownerID )
			if owner:
				return owner.state  == self.param1
			else:
				ERROR_MSG( "AICnd118:can not find the owner!" )
		return False

class AICnd119( AICondition ):
	"""
	判断是否有拥有者（限定于有主人的怪物使用）
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		ownerID = entity.getOwnerID()
		if ownerID != 0:
			owner = BigWorld.entities.get( ownerID )
			if owner:
				return True
		return False

class AICnd120( AICondition ):
	"""
	判断周围属于某一特定阵营（battleCamp）NPC的数量是否小于某值
	"""
	def __init__( self ):
		AICondition.__init__( self )
		self.range = 0.0			# 范围
		self.batCamp = 0			# 阵营
		self.amount = 0				# entity数量

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.range = section.readFloat( "param1" ) 	# 范围
		self.batCamp = section.readInt( "param2" )	# battleCamp
		self.amount = section.readInt( "param3" )	# entity数量

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		monsterList = []
		entityList = entity.entitiesInRangeExt( self.range, None, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in entityList:
			if hasattr( e, "battleCamp") and e.battleCamp == self.batCamp and not e.isDead():
				monsterList.append( e.id )

		if len( monsterList ) < self.amount:
			return True

		return False

class AICnd121( AICondition ):
	"""
	判断周围属于某一特定阵营（battleCamp）NPC的数量是否大于某值
	"""
	def __init__( self ):
		AICondition.__init__( self )
		self.range = 0.0			# 范围
		self.batCamp = 0			# 阵营
		self.amount = 0				# entity数量

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.range = section.readFloat( "param1" ) 	# 范围
		self.batCamp = section.readInt( "param2" )	# battleCamp
		self.amount = section.readInt( "param3" )	# entity数量

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		monsterList = []
		entityList = entity.entitiesInRangeExt( self.range, None, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in entityList:
			if hasattr( e, "battleCamp") and e.battleCamp == self.batCamp and not e.isDead():
				monsterList.append( e.id )

		if len( monsterList ) > self.amount:
			return True

		return False

class AICnd122( AICondition ):
	"""
	伤害列表中是否有特定类型的className的entity
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.entityType = ""
		self.className = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.entityType = section.readString( "param1" )
		self.className = section.readString( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		for id in entity.damageList:
			e = BigWorld.entities.get( id )
			if e and e.__class__.__name__ == self.entityType:
				if self.className and e.className != self.className:		# className为空则只需满足该Entity类型
					continue
				return True
		return False


class AICnd123( AICondition ):
	"""
	判断当前所在空间的创建时间是否大于等于指定值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.upperLimit = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.upperLimit = section.readFloat( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		spaceBase = entity.getCurrentSpaceBase()
		if spaceBase is None:
			return False
		spaceEntity = BigWorld.entities.get( spaceBase.id )
		if spaceEntity is None : return False
		return spaceEntity.timeFromCreated() >= self.upperLimit

class AICnd124( AICondition ):
	"""
	判断当前所在空间的创建时间是否小于指定值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self.lowerLimit = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.lowerLimit = section.readFloat( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		spaceEntity = BigWorld.entities.get( entity.getCurrentSpaceBase().id )
		if spaceEntity is None : return False
		return spaceEntity.timeFromCreated() < self.lowerLimit

class AICnd125( AICondition ):
	"""
	判断当前是否有对话跟随者
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		if entity.queryTemp( "talkFollowID", 0 ):
			return True
		
		return False

class AICnd126( AICondition ):
	"""
	检查是否到达某条巡逻路线离怪物自身位置最近的巡逻点的XZ平面一定范围内
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.graphID = section.readString( "param1" )
		self.range = section.readFloat( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		if self.graphID == "":
			if entity.patrolList:
				patrolList = entity.patrolList
				patrolPathNode, position = patrolList.nearestNode( entity.position )
				dx = pow( position[0] - entity.position[0], 2 )
				dz = pow( position[2] - entity.position[2], 2 )
				if pow( dx + dz, 0.5 ) < self.range:
					return True
				else:
					return False
			else:
				ERROR_MSG("graphID is None!")
				return False
		patrolList = BigWorld.PatrolPath( self.graphID )
		if not patrolList or not patrolList.isReady():
			ERROR_MSG( "Patrol(%s) unWorked. it's not ready or not have such graphID!"%self.graphID )
			return False
		else:
			patrolPathNode, position = patrolList.nearestNode( entity.position )
			dx = pow( position[0] - entity.position[0], 2 )
			dz = pow( position[2] - entity.position[2], 2 )
			if pow( dx + dz, 0.5 ) < self.range:
				return True
			else:
				return False

class AICnd127( AICondition ):
	"""
	ai目标是否是pk值大于某数的玩家
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._pkValue = section.readInt( "param1" ) # 搜索pk值在多少以上

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		e = BigWorld.entities.get( entity.aiTargetID)
		if e and e.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if e.state != csdefine.ENTITY_STATE_DEAD and \
				e.state != csdefine.ENTITY_STATE_PENDING:
				if e.pkValue > self._pkValue:
					return True
		return False

class AICnd128( AICondition ):
	"""
	一定范围内，是否有其他相同className的怪物当前的目标和自身的目标一致。 
	"""
	def __init__( self ):
		AICondition.__init__( self )
		self.param1 = 0.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" )						# className

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		entityList = entity.entitiesInRangeExt( self.param1, entity.__class__.__name__, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in entityList:
			if hasattr( e, "className" ) and e.className == entity.className and not e.isDead():
				if e.targetID == entity.targetID:
					return True
		return False
	
class AICnd129( AICondition ):
	"""
	一定范围内，相同className的怪物,是否只有我的目标(targetID)是这个entitiy(或者玩家) 。 
	"""
	def __init__( self ):
		AICondition.__init__( self )
		self.param1 = 0.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" )						# className

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		entityList = entity.entitiesInRangeExt( self.param1, entity.__class__.__name__, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in entityList:
			if hasattr( e, "className" ) and e.className == entity.className and not e.isDead():
				if e.targetID == entity.targetID:
					return False
		return True

class AICnd130( AICondition ):
	"""
	查询怪物的某个临时属性是否等于某个值 
	"""
	def __init__( self ):
		AICondition.__init__( self )
		self.param1 = ""
		self.param2 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readString( "param1" )						# 怪物的临时属性
		self.param2 = section.readInt( "param2" )							# 临时属性的值是否大于某个值

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		try:
			spaceEntity = BigWorld.entities[ entity.getCurrentSpaceBase().id ]
		except:
			DEBUG_MSG( "can't get spaceEntity!" )
			return False
		value = spaceEntity.queryTemp( self.param1, 0 )
		if value == self.param2:
			return True
		return False
		
class AICnd131( AICondition ):
	"""
	是否开启了相应的阵营活动 
	"""
	def __init__( self ):
		AICondition.__init__( self )
		self.param1 = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = [ int( i ) for i in section.readString( "param1" ).split(";") ]						# 阵营活动类型

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		try:
			spaceEntity = BigWorld.entities[ entity.getCurrentSpaceBase().id ]
		except:
			DEBUG_MSG( "can't get spaceEntity!" )
			return False
			
		if BigWorld.globalData.has_key( "CampActivityCondition" ):
			temp = BigWorld.globalData["CampActivityCondition"]
			if spaceEntity.className in temp[0] and temp[1] in self.param1:
				return True
		return False
		
class AICnd132( AICondition ):
	"""
	是否没有开启相应的阵营活动 
	"""
	def __init__( self ):
		AICondition.__init__( self )
		self.param1 = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = [ int( i ) for i in section.readString( "param1" ).split(";") ]						# 阵营活动类型

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		try:
			spaceEntity = BigWorld.entities[ entity.getCurrentSpaceBase().id ]
		except:
			DEBUG_MSG( "can't get spaceEntity!" )
			return False
			
		if BigWorld.globalData.has_key( "CampActivityCondition" ):
			temp = BigWorld.globalData["CampActivityCondition"]
			if spaceEntity.className in temp[0] and temp[1] in self.param1:
				return False
		return True

class AICnd133( AICondition ):
	"""
	是否在指定时间内
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._cmd = ""			# scheme 字符串 如：" * * 3 * *" (参见 CrondScheme.py)
		self._lastTime = 1		# 单位秒
		self.scheme = Scheme()

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._cmd = section.readString( "param1" )
		self._lastTime = section.readInt( "param2" )
		self.scheme.init( self._cmd )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		year, month, day, hour, minute = time.localtime( time.time() - self._lastTime )[:5]
		nextTime = self.scheme.calculateNext( year, month, day, hour, minute )
		if nextTime < time.time():
			return True
		return False

class AICnd134( AICondition ):
	"""
	ai目标是否在某阵营列表中
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._param1 = [] #camp list

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = [int(i) for i in section.readString( "param1" ).split( ";" )]

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		if BigWorld.entities.has_key( entity.aiTargetID ):
			e = BigWorld.entities[entity.aiTargetID]
			if e.getCamp() in self._param1:
				return True
		return False

class AICnd135( AICondition ):
	"""
	AI对象（玩家）对某任务的进行状态是否处于指定的任务状态列表中
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AICondition.__init__( self )
		self._questID = 0		# 任务ID
		self._questStates = []	# 任务状态列表

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._questID = section.readInt( "param1" )
		if section.readString( "param2" ) == "":
			self._questStates = [ csdefine.QUEST_STATE_NOT_FINISH, csdefine.QUEST_STATE_FINISH ]
		else:
			self._questStates = [int( i ) for i in section.readString( "param2" ).split( ";" )]
		

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		target = BigWorld.entities.get( entity.aiTargetID, None )
		if target and target.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			quest = target.getQuest( self._questID )
			if quest and quest.query( target ) in self._questStates:
				return True
		return False

# AIConditions.py
##
