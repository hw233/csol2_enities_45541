# -*- coding: gb18030 -*-

# $Id: AIActions.py,v 1.33 2008-09-05 01:41:26 zhangyuxing Exp $

import csstatus
import cschannel_msgs
import ShareTexts as ST
import csdefine
import csconst
import BigWorld
import csarithmetic
import random
import math
import time
import Math
import copy
from csdefine import *
from bwdebug import *
from Resource.AI.AIBase import *
import SkillTargetObjImpl
from Resource.SkillLoader import g_skills
from Resource.QuestLoader import QuestsFlyweight
from ObjectScripts.GameObjectFactory import g_objFactory
from Function import Functor
import ECBExtend
import Const
import items
import ObjectScripts.CopyTemplate as CopyTemplate
from csconst import g_maps_info
from NPCPotentialLoader import NPCPotentialLoader
from utils import vector3TypeConvert, checkAndMove, moveOut, followCheckAndMove
from interface.CombatUnit import CombatUnit
g_npcPotential = NPCPotentialLoader.instance()

questIns = QuestsFlyweight.instance()
g_items = items.instance()

from MsgLogger import g_logger
from Domain_Fight import g_fightMgr

#构成一个圆上的八个点
#groupsCirclePosition = {0: (0.0, 1.0), 1: (0.17364817473495014, 0.98480775352919525), 2: (0.34202013773034279, 0.93969262282244048), 3: (0.49999999226497954, 0.86602540825025476), 4: (0.64278760056383633, 0.76604445077383465), 5: (0.76604443355040708, 0.64278762108991794), 6: (0.86602539485280627, 0.5000000154700408), 7: (0.93969261365804591, 0.34202016290930942), 8: (0.98480774887631006, 0.17364820112277204), 9: (0.99999999999999967, 2.6794896585026611e-008), 10: (0.98480775818207977, -0.17364814834712822), 11: (0.93969263198683439, -0.34202011255137593), 12: (0.86602542164770269, -0.49999996905991789), 13: (0.76604446799726178, -0.64278758003775405), 14: (0.64278764161599922, -0.76604441632697884), 15: (0.50000003867510157, -0.86602538145535723), 16: (0.34202018808827572, -0.93969260449365066), 17: (0.17364822751059375, -0.9848077442234241), 18: (5.3589793170053202e-008, -0.99999999999999856), 19: (-0.17364812195930612, -0.98480776283496363), 20: (-0.34202008737240913, -0.93969264115122753), 21: (-0.49999994585485613, -0.86602543504514984), 22: (-0.64278755951167155, -0.76604448522068824), 23: (-0.76604439910355049, -0.64278766214207961), 24: (-0.86602536805790731, -0.50000006188016222), 25: (-0.93969259532925453, -0.34202021326724219), 26: (-0.98480773957053735, -0.17364825389841579), 27: (-0.99999999999999678, -8.038469019916896e-008), 28: (-0.98480776748784682, 0.17364809557148345), 29: (-0.93969265031562021, 0.34202006219344144), 30: (-0.86602544844259632, 0.49999992264979398), 31: (-0.76604450244411415, 0.6427875389855886), 32: (-0.64278768266816011, 0.76604438188012103), 33: (-0.50000008508522187, 0.86602535466045727), 34: (-0.34202023844620755, 0.93969258616485818), 35: (-0.17364828028623683, 0.98480773491765006)}


class AIAction1( AIAction ):
	"""
	战斗列表清空
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if len( entity.enemyList ) > 0:
			entity.resetEnemyList()

class AIAction2( AIAction ):
	"""
	伤害列表增加
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.addDamageList( entity.aiTargetID, 0 )

class AIAction3( AIAction ):
	"""
	伤害列表删减
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.removeEnemyDmgList( entity.aiTargetID )

class AIAction4( AIAction ):
	"""
	清空伤害列表
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.resetDamageList()

class AIAction5( AIAction ):
	"""
	治疗列表增加
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.addCureList( entity.aiTargetID, 0 )

class AIAction6( AIAction ):
	"""
	治疗列表删减
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.removeEnemyCureList( entity.aiTargetID )

class AIAction7( AIAction ):
	"""
	清空治疗列表
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.resetCureList()

class AIAction8( AIAction ):
	"""
	清空战斗列表中除当前AI选择目标外的所有单位
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if entity.aiTargetID in entity.enemyList:
			# 以下方法比循环更快
			enemyListID = entity.aiTargetID
			enemyListTime = entity.enemyList[ entity.aiTargetID ]
			damageListID = 0
			damageListVal = 0
			cureListID = 0
			cureListVal = 0
			if entity.aiTargetID in entity.damageList:
				damageListID = entity.aiTargetID
				damageListVal = entity.damageList[ entity.aiTargetID ]
			if entity.aiTargetID in entity.cureList:
				cureListID = entity.aiTargetID
				cureListVal = entity.cureList[ entity.aiTargetID ]
			entity.resetEnemyList()
			entity.enemyList[ entity.aiTargetID ] = enemyListTime
			if damageListID > 0:
				entity.damageList[ entity.aiTargetID ] = damageListVal
			if cureListID > 0:
				entity.cureList[ entity.aiTargetID ] = cureListVal
		else:
			ERROR_MSG( "aiTarget %i in enemyList not found, implEntity %i. " % ( entity.aiTargetID, entity.id ) )

class AIAction9( AIAction ):
	"""
	清空伤害列表中除当前目标外的所有单位
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if entity.aiTargetID in entity.damageList:
			# 以下方法比循环更快
			damageListVal = entity.damageList[ entity.aiTargetID ]
			entity.resetDamageList()
			entity.damageList[ entity.aiTargetID ] = damageListVal
		else:
			ERROR_MSG( "aiTarget %i in damageList not found, implEntity %i. " % ( entity.aiTargetID, entity.id ) )


class AIAction10( AIAction ):
	"""
	清空治疗列表中除当前目标外的所有单位
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if entity.aiTargetID in entity.cureList:
			# 以下方法比循环更快
			val = entity.cureList[ entity.aiTargetID ]
			entity.resetCureList()
			entity.cureList[ entity.aiTargetID ] = val
		else:
			ERROR_MSG( "aiTarget %i in cureList not found, implEntity %i. " % ( entity.aiTargetID, entity.id ) )


class AIAction11( AIAction ):
	"""
	将指定单位加入战斗己方单位列表
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.addFriendList( entity.aiTargetID )

class AIAction12( AIAction ):
	"""
	将指定单位移出战斗己方单位列表
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.removeAIFriend( entity.aiTargetID )

class AIAction13( AIAction ):
	"""
	将当前目标从己方单位列表中移出
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.removeAIFriend( entity.aiTargetID )

class AIAction14( AIAction ):
	"""
	进入战斗状态
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.changeAttackTarget( entity.aiTargetID )

class AIAction15( AIAction ):
	"""
	脱离战斗状态
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.changeState( csdefine.ENTITY_STATE_FREE )

class AIAction16( AIAction ):
	"""
	将伤害列表首位作为当前目标
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		eid = 0
		rval = 0
		for id, val in entity.damageList.iteritems():
			if val > rval:
				rval = val
				eid = id
		if eid > 0:
			entity.setAITargetID( eid )

class AIAction17( AIAction ):
	"""
	将治疗列表首位作为当前目标
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		eid = 0
		rval = 0
		for id, val in entity.cureList.iteritems():
			if val > rval:
				rval = val
				eid = id
		if eid > 0:
			entity.setAITargetID( eid )

class AIAction18( AIAction ):
	"""
	等级最低选择
	将战斗列表中等级最低的单位作为当前目标
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		eid = 0
		rval = 99999999
		for id in entity.enemyList:
			if BigWorld.entities.has_key( id ):
				e = BigWorld.entities[ id ]
				if e.level < rval:
					rval = e.level
					eid = id
		if eid > 0:
			entity.setAITargetID( eid )

class AIAction19( AIAction ):
	"""
	等级最高选择
	将战斗列表中等级最高的单位作为当前目标
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		eid = 0
		rval = 0
		for id in entity.enemyList:
			if BigWorld.entities.has_key( id ):
				e = BigWorld.entities[ id ]
				if e.level > rval:
					rval = e.level
					eid = id
		if eid > 0:
			entity.setAITargetID( eid )

class AIAction20( AIAction ):
	"""
	生命最低选择
	将战斗列表中生命最低的单位做为当前目标
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		eid = 0
		rval = 999999999
		for id in entity.enemyList:
			if BigWorld.entities.has_key( id ):
				e = BigWorld.entities[ id ]
				if e.HP < rval:
					rval = e.HP
					eid = id
		if eid > 0:
			entity.setAITargetID( eid )

class AIAction21( AIAction ):
	"""
	生命最高选择
	将战斗列表中生命最高的单位做为当前目标
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		eid = 0
		rval = 0
		for id in entity.enemyList:
			if BigWorld.entities.has_key( id ):
				e = BigWorld.entities[ id ]
				if e.HP > rval:
					rval = e.HP
					eid = id
		if eid > 0:
			entity.setAITargetID( eid )

class AIAction22( AIAction ):
	"""
	停止对当前目标的追击
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.stopMoving()
		entity.changeSubState( csdefine.M_SUB_STATE_NONE )

class AIAction23( AIAction ):
	"""
	复位
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.exitFight()

class AIAction24( AIAction ):
	"""
	完全恢复
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.full()
		entity.clearBuff( [csdefine.BUFF_INTERRUPT_ON_DIE] )					# 清除所有buff

class AIAction25( AIAction ):
	"""
	强制攻击目标
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.changeAttackTarget( entity.aiTargetID )

class AIAction26( AIAction ):
	"""
	使用技能
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt64( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		# 攻击判断
		try:
			enemy = BigWorld.entities[ entity.targetID ]
		except:
			return

		spell = g_skills[ self.param1 ]						# 获取配置的攻击技能
		range = spell.getRangeMax( entity )					# 获取技能的最大施法距离
		# 用于解决一堆怪物追击同一个目标时重叠在一起的问题。
		if checkAndMove( entity ):
			return
		state = entity.spellTarget( self.param1,  entity.targetID )

		# 有可能被反射致死
		if entity.state == csdefine.ENTITY_STATE_DEAD:
			return
		if state == csstatus.SKILL_GO_ON:						# 正常施展,,直接返回
			return
		elif state in [ csstatus.SKILL_NOT_HIT_TIME, csstatus.SKILL_NOT_READY, csstatus.SKILL_INTONATING ]:
			if entity.isMoving():
				entity.stopMoving()
		elif state == csstatus.SKILL_TOO_FAR:
			if entity.actionSign( csdefine.ACTION_FORBID_MOVE ):
				DEBUG_MSG( "im cannot the move!" )
				entity.stopMoving()
				return
			if enemy.isReal():
				if enemy.queryTemp( "AI_Trace_Position", None ) != None:
					entity.gotoPosition( random.choice( enemy.queryTemp( "AI_Trace_Position", None ) ) )
					return
			entity.chaseTarget( enemy, spell.getRangeMax( entity )*2/3 )# 距离过远,,追击目标（*2/3是为了追击更近一点）
		else:
			# 其它错误
			INFO_MSG( "%i: skill %i use state = %i." % ( entity.id, self.param1, state ) )

class AIAction27( AIAction ):
	"""
	逃跑
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.doFlee()

class AIAction28( AIAction ):
	"""
	停止逃跑
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.stopMoving()
		entity.changeSubState( csdefine.M_SUB_STATE_NONE )

class AIAction29( AIAction ):
	"""
	当前AI系统运行级别调整
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.setNextRunAILevel( self.param1 )

class AIAction30( AIAction ):
	"""
	默认AI系统运行级别调整
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.setDefaultAILevel( self.param1 )

class AIAction31( AIAction ):
	"""
	指定S级AI所对应的目标
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.setSAI( csdefine.AI_TYPE_SPECIAL, self.param1 )

class AIAction32( AIAction ):
	"""
	指定E级AI所对应的目标
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.addEAI( self.param1 )

class AIAction33( AIAction ):
	"""
	NPC发言
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if len( self.param1 ) > 0:
			entity.say( self.param1 )

class AIAction34( AIAction ):
	"""
	向指定一个或多个类型NPC发送AI命令
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = ""  # NPCID
		self.param2 = 0	  # cmd
		self.param3 = 0.0 # 搜索半径

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" ).split("|")
		self.param2 = section.readInt( "param2" )
		self.param3 = section.readFloat( "param3" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		es = entity.entitiesInRangeExt( self.param3, None, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in es:
			if e.className in self.param1 and e.className != "":
				entity.sendAICommand( e.id, self.param2 )

class AIAction35( AIAction ):
	"""
	清理不在视野范围类的敌人
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.onViewRange()

class AIAction36( AIAction ):
	"""
	检测当前攻击目标的有效性
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.checkAttackTarget( entity.targetID )					# 只检查当前攻击目标

class AIAction37( AIAction ):
	"""
	战斗列表增加
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		aiTarget = BigWorld.entities.get( entity.aiTargetID )
		if aiTarget:
			g_fightMgr.buildEnemyRelation( entity, aiTarget )

class AIAction38( AIAction ):
	"""
	将最先进入敌人列表的作为当前目标
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		eid = entity.findFirstEnemyByTime()
		if BigWorld.entities.has_key( eid ):
			entity.setAITargetID( eid )

class AIAction40( AIAction ):
	"""
	改变当前目标为最终作用对象
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if entity.hasEnemy( entity.aiTargetID ) and BigWorld.entities.has_key( entity.aiTargetID ) and entity.targetID != entity.aiTargetID:
			entity.changeAttackTarget( entity.aiTargetID )

class AIAction41( AIAction ):
	"""
	呼叫同伴
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		#因为AI总是有entity自身调用的 所以这样做是正确的
		if entity.queryTemp( "callSign", True ):
			return
		entity.setTemp( "callSign", True )
		escript = g_objFactory.getObject( entity.className )
		es = entity.entitiesInRangeExt( entity.callRange, None, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in es:
			if e.className in escript.callList:
				e.onFightCall( entity.targetID, entity.className )

class AIAction42( AIAction ):
	"""
	对目标使用自身等级的技能
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt64( "param1" ) * 1000

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		# 攻击判断
		try:
			enemy = BigWorld.entities[ entity.targetID ]
		except:
			return

		try:
			spell = g_skills[ self.param1 + entity.level ]						# 获取配置的攻击技能
		except:
			ERROR_MSG( "Use skill error, id is %i."%(self.param1 + entity.level) )
			return

		range = spell.getRangeMax( entity )					# 获取技能的最大施法距离
		# 用于解决一堆怪物追击同一个目标时重叠在一起的问题。
		if checkAndMove( entity ):
			return
		state = entity.spellTarget( self.param1 + entity.level,  entity.targetID )
		# 有可能被反射致死。残酷的现实：某些技能会导致entity销毁。
		if entity.isDestroyed or entity.state == csdefine.ENTITY_STATE_DEAD:
			return

		if state == csstatus.SKILL_GO_ON:						# 正常施展,,直接返回
			return
		elif state in [ csstatus.SKILL_NOT_HIT_TIME, csstatus.SKILL_NOT_READY, csstatus.SKILL_INTONATING ]:
			if entity.isMoving():
				entity.stopMoving()
		elif state == csstatus.SKILL_TOO_FAR:
			if entity.actionSign( csdefine.ACTION_FORBID_MOVE ):
				DEBUG_MSG( "im cannot the move!" )
				entity.stopMoving()
				return
			if entity.queryTemp( "AI_Trace_Position", None ) != None:
				entity.gotoPosition( random.choise( entity.queryTemp( "AI_Trace_Position", None ) ) )
			elif entity.chaseTarget( enemy, spell.getRangeMax( entity ) ):		# 距离过远,,追击目标
				return
		else:
			# 其它错误
			INFO_MSG( "%i: skill %i use state = %i." % ( entity.id, self.param1 + entity.level, state ) )

class AIAction43( AIAction ):
	"""
	对自身使用技能
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt64( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		# 攻击判断
		try:
			spell = g_skills[ self.param1 ]						# 获取配置的攻击技能
		except:
			ERROR_MSG( "Use skill error, id is %i."%self.param1 )
			return
		state = entity.spellTarget( self.param1,  entity.id )
		# 有可能被反射致死
		if entity.state == csdefine.ENTITY_STATE_DEAD:
			return

		if state == csstatus.SKILL_GO_ON:						# 正常施展,,直接返回
			return
		elif state in [ csstatus.SKILL_NOT_HIT_TIME, csstatus.SKILL_NOT_READY, csstatus.SKILL_INTONATING ]:
			if entity.isMoving():
				entity.stopMoving()
		else:
			# 其它错误
			INFO_MSG( "%i: skill %i use state = %i." % ( entity.id, self.param1, state ) )

class AIAction44( AIAction ):
	"""
	对自身使用自身等级的技能
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt64( "param1" ) * 1000

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		# 攻击判断
		state = entity.spellTarget( self.param1 + entity.level,  entity.id )
		# 有可能被反射致死
		if entity.state == csdefine.ENTITY_STATE_DEAD:
			return

		if state == csstatus.SKILL_GO_ON:						# 正常施展,,直接返回
			return
		elif state in [ csstatus.SKILL_NOT_HIT_TIME, csstatus.SKILL_NOT_READY, csstatus.SKILL_INTONATING ]:
			if entity.isMoving():
				entity.stopMoving()
		else:
			# 其它错误
			INFO_MSG( "%i: skill %i use state = %i." % ( entity.id, self.param1 + entity.level, state ) )

class AIAction45( AIAction ):
	"""
	将对我施放嘲讽技能的人做为最终作用对象
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		buffs = entity.findBuffsByBuffID( 199001 )
		if len( buffs ) <= 0:
			return

		casterID = entity.getBuff( buffs[0] )["caster"]
		if entity.targetID != casterID and BigWorld.entities.has_key( casterID ):
			entity.changeAttackTarget( casterID )

class AIAction46( AIAction ):
	"""
	停止巡逻
	停止巡逻, 具有巡逻功能的NPC才可以使用, 使改NPC处于停止巡逻状态
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.stopPatrol()

class AIAction47( AIAction ):
	"""
	开始巡逻
	开始巡逻, 具有巡逻功能的NPC才可以使用, 使该NPC处于巡逻状态，仅适用于巡逻路径在地面的npc

	如果配置了巡逻数据，那么使用巡逻数据进行巡逻，否则使用默认的巡逻数据。
	param1为patrolNode
	param2为路点id
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.patrolNode = ""
		self.graphID = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.patrolNode = section.readString( "param1" )
		self.graphID = section.readString( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if self.graphID == "":
			entity.doPatrol()
			return

		patrolList = BigWorld.PatrolPath( self.graphID )
		if not patrolList or not patrolList.isReady():
			ERROR_MSG( "Patrol(%s) unWorked. it's not ready or not have such graphID! Monster(%s,%s), spaceName:%s."% ( self.graphID, entity.getName(), entity.className, entity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) ) )
		else:
			lastPatrolNode = entity.queryTemp( "patrolPathNode", "" ) #上一次巡逻到达的点
			if lastPatrolNode != "" and patrolList.nodesTraversableFrom( lastPatrolNode ):
				# 上一个巡逻点不为空而且能找到下一个巡逻点
				entity.doPatrol( lastPatrolNode, patrolList  )
			else:
				patrolPathNode, position = patrolList.nearestNode( entity.position )
				entity.doPatrol( patrolPathNode, patrolList  )

class AIAction48( AIAction ):
	"""
	108星：NPC变成怪物
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.tolevel = section.readInt( "param1" )
		self.toTargetlevel = section.readInt( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if self.toTargetlevel <= 0:
			lv = self.tolevel
			if lv <= 0:
				lv = entity.level
			entity.changeToMonster( lv, 0 )
		else:
			target = BigWorld.entities.get( entity.targetID )
			if target:
				lv = target.level + self.toTargetlevel
				entity.changeToMonster( lv, 0 )
			elif entity.state == csdefine.ENTITY_STATE_FIGHT: # 如果找不到目标，变成怪物失败；但已经进入了战斗状态，则还原状态。
				entity.changeState( csdefine.ENTITY_STATE_FREE )

class AIAction49( AIAction ):
	"""
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.changeToNPC()
		if hasattr( entity, "littleMonsterIDs" ):
			for i in entity.littleMonsterIDs:
				monster = BigWorld.entities.get( i )
				if monster is not None:
					if monster.isReal():
						if entity.position.flatDistTo( monster.position ) < 30:
							if len( monster.enemyList ) > 0:
								entity.changeToMonster( entity.queryTemp("lastLevel"), 0 )
								g_fightMgr.buildGroupEnemyRelationByIDs( entity, monster.enemyList.keys() )
								entity.addTimer( 0.1, 0, ECBExtend.MONSTER_CHANGE_AI_TO_ONE_LEVEL_CBID )
								return

class AIAction50( AIAction ):
	"""
	NPC/MONSTER 自身销毁
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self._p1 = section.readFloat( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if self._p1 <= 0:
			entity.addTimer( csconst.MONSTER_CORPSE_DURATION, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )
		else:
			entity.addTimer( self._p1, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )
		#entity.destroy()

class AIAction51( AIAction ):
	"""
	NPC通知拥有者完成一个事件型任务
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0
		self.param2 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )
		self.param2 = section.readInt( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		ownerBase = entity.queryTemp( "npc_ownerBase", None )
		if ownerBase:
			ownerID = ownerBase.id
			if BigWorld.entities.has_key( ownerID ):
				owner = BigWorld.entities[ ownerID ]
				owner.questTaskIncreaseState( self.param1, self.param2 )
			else:
				ownerBase.cell.questTaskIncreaseState( self.param1, self.param2 )
		else:
			ERROR_MSG( "can not find the owner!" )

class AIAction52( AIAction ):
	"""
	记录当前的时间,,  到一个标签名中。
	主要用于一些时间查询等操作：
	如 一段时间内 NPC没有做什么就怎么样。

	要实现这个当然还需要配合一个相关条件：
	”某记录时间是否到达“   参数是和该标签名一样的
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if not entity.queryTemp( self.param1, None ):
			entity.setTemp( self.param1, BigWorld.time() )

class AIAction53( AIAction ):
	"""
	NPC停止移动
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.stopMoving()

class AIAction54( AIAction ):
	"""
	NPC跟随任务拥有者

	保持距离 既NPC始终与拥有者所保持的一段距离.
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		ownerBase = entity.queryTemp( "npc_ownerBase", None )
		entity.spawnPos = tuple( entity.position )
		if ownerBase:
			ownerID = ownerBase.id
			if BigWorld.entities.has_key( ownerID ):
				owner = BigWorld.entities[ ownerID ]
			else:
				return
			distance = csarithmetic.distancePP3( owner.position, entity.position )
			if int( distance ) <= self.param1:
				entity.stopMoving()
				return
			if entity.actionSign( csdefine.ACTION_FORBID_MOVE ):
				DEBUG_MSG( "im cannot the move!" )
				entity.stopMoving()
				return
			entity.chaseTarget( owner, self.param1 )
		else:
			ERROR_MSG( "can not find the owner!" )

class AIAction55( AIAction ):
	"""
	清除某记录时间
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.removeTemp( self.param1 )

class AIAction56( AIAction ):
	"""
	向任务拥有者发送一个系统信息
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

		# 注：section.readString( "param1" )参数必须填写，且必须是csstatus里存在的已定义的变量

		self.param1 = getattr( csstatus, section.readString( "param1" ) )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		ownerBase = entity.queryTemp( "npc_ownerBase", None )
		if ownerBase:
			ownerBase.client.onStatusMessage( self.param1, "" )
		else:
			ERROR_MSG( "can not find the owner!" )

class AIAction57( AIAction ):
	"""
	家族控制NPC持续给周围家族成员经验
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 15.0
		self.param2 = 1
		self.param3 = 2

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readFloat( "param1" )
		self.param2 = section.readInt( "param2" )
		self.param3 = section.readInt( "param3" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		spaceName = entity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		globalKey = "holdCity.%s" % spaceName
		if not BigWorld.globalData.has_key( globalKey ):	# 这个城市没有主人
			return
		masterTongDBID, msterTongName = BigWorld.globalData.has_key[globalKey]
		if not entity.queryTemp( "tongCityWarExpInfo", {} ):
			entity.setTemp( "tongCityWarExpInfo", {} )
		tongCityWarExpInfo = entity.queryTemp( "tongCityWarExpInfo" )

		today = time.localtime()[2]
		es = entity.entitiesInRangeExt( self.param1, None, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in es:
			if e.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				if e.tong_dbID == masterTongDBID:
					if tongCityWarExpInfo.has_key( e.databaseID ):
						expData = tongCityWarExpInfo[e.databaseID]
						if expData["day"] != today:		# 重置领取经验数据
							expData["day"] = today
							expData["count"] = 0
						else:
							if expData["count"] >= 60:	# 每天只能领60次，第60次的时候给个提示
								if expData["count"] == 60:
									e.client.onStatusMessage( csstatus.TONG_CITY_WAR_GET_NPC_EXP_OVER, "" )
									expData["count"] += 1
								continue
					else:
						tongCityWarExpInfo[e.databaseID] = {"day":today, "count":0}
					tongCityWarExpInfo[e.databaseID]["count"] += 1
					exp = int( 75 + 15 * pow( level, 1.2 ) ) * 8
					e.addExp( exp, csdefine.CHANGE_EXP_AIACTION )
					
					try:
						g_logger.actJoinLog( csdefine.ACTIVITY_NPC_GUA_JING_YAN, csdefine.ACTIVITY_JOIN_ROLE, e.databaseID, e.getName() )
					except:
						g_logger.logExceptLog( GET_ERROR_MSG()  )

class AIAction58( AIAction ):
	"""
	清除某EAI标记
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if not entity.isEAI( self.param1 ):
			return
		entity.eaiIDArray.remove( self.param1 )


class AIAction59( AIAction ):
	"""
	从属怪物攻击主人的敌人(需要主人进入战斗状态，否则出错)
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )



	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.spawnPos = tuple( entity.position )
		ownerID = entity.getOwnerID()
		if ownerID:
			if BigWorld.entities.has_key( ownerID ):
				owner = BigWorld.entities[ ownerID ]
				for id in owner.enemyList:
					enemyEntity = BigWorld.entities.get( id )
					if enemyEntity:
						if not enemyEntity.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ):
							g_fightMgr.buildEnemyRelation( entity, enemyEntity )
			else:
				return
		else:
			return


class AIAction60( AIAction ):
	"""
	从属怪物跟随主人
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		#if entity.getSubState() == csdefine.M_SUB_STATE_CHASE:
		#	return
		entity.spawnPos = tuple( entity.position )
		owner = BigWorld.entities.get( entity.getOwnerID() )

		if owner:
			if entity.actionSign( csdefine.ACTION_FORBID_MOVE ) or owner.actionSign( csdefine.ACTION_FORBID_MOVE ):
				return

			entity.chaseEntity( owner, 4 ) #镖车追到玩家距离4米的时候，停止移动


class AIAction61( AIAction ):
	"""
	发出飞到主人身边的请求（主要用于主人可能已经到了别的space的情况，也可以用于主人和自己不在一个cell时，请求飞到他身边）
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.flyToMasterSpace()


class AIAction62( AIAction ):
	"""
	飞到主人身边（用于和主人之间的距离比较远，需要飞到他旁边,也可以用于飞到不同的space）
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		ownerID = entity.getOwnerID()
		if ownerID:
			if BigWorld.entities.has_key( ownerID ):
				owner = BigWorld.entities[ ownerID ]
				entity.teleport( owner, owner.position + Math.Vector3( random.randint(-2,2), 0,random.randint(-2,2) ), owner.direction )
				if entity.isReal():
					entity.stopMoving()
			else:
				return
		else:
			return

class AIAction63( AIAction ):
	"""
	重新建立自身和主人的关联
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		target = BigWorld.entities.get( entity.aiTargetID )
		if not target:
			return
		if target.getName() == entity.ownerName:
			entity.setOwner( BigWorld.entities[entity.aiTargetID] )
			target.setTemp( 'dart_id', entity.id )
			g_fightMgr.breakEnemyRelation( entity, target )
			


class AIAction64( AIAction ):
	"""
	消失或变为NPC
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if hasattr( entity, "changeToNPC" ):
			entity.changeToNPC()
		entity.addTimer( csconst.MONSTER_CORPSE_DURATION, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )


class AIAction65( AIAction ):
	"""
	镖车招怪
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = ""


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		ct = entity.queryTemp( 'callMonstersTime', 0 )
		ctt = entity.queryTemp( 'callMonstersTimeTotal', 0 )
		memberIDDict = entity.queryTemp( "dartMembers", {} )
		g = BigWorld.entities.get
		if ct < ctt:
			# 召唤的次数callMonstersTime小于总的召唤次数callMonstersTimeTotal
			ct += 1
			entity.setTemp( 'callMonstersTime', ct )
			ownerID = entity.getOwnerID()
			owner = g(ownerID)
			for i in xrange( ctt ):
				# 召怪的个数callMonstersTotal
				monsterID = Const.DART_MONSTERSID[random.randint( 0,len ( Const.DART_MONSTERSID )-1 )]
				pos = entity.position + Math.Vector3( random.randint(3,6), 3,random.randint(3,6) )
				monster = entity.createObjectNearPlanes( str(monsterID), pos, entity.direction, {"spawnPos": tuple(entity.position), "level": entity.queryTemp('level',1)} )
				g_fightMgr.buildEnemyRelation( monster, entity )
				monster.setTemp( 'is_dart_banditti', True )
				monster.addCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_ANTAGONIZE_ID, ownerID )

			# 参与运镖者经验奖励
			if len( memberIDDict ) > 0:
				for mid in memberIDDict.iterkeys():
					member = g(mid)
					if memberIDDict[mid] == -1 or member is None:
						continue
					member.tongDartExpReward()
			if owner is not None:
				owner.tongDartExpReward()
			# 发通知 下镖车
			ownerBaseMailbox = entity.getOwner()
			if not hasattr( ownerBaseMailbox, "client" ):
				return
			ownerBaseMailbox.client.onStatusMessage( csstatus.ROLE_QUEST_DART_CALL_MONSTER, "" )
			entity.disMountEntity( ownerID, ownerID )


class AIAction66( AIAction ):
	"""
	镖车判断进入AOI的对象是不是自己的目标，如果是，则记录
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if BigWorld.entities.has_key( entity.aiTargetID ):
			if BigWorld.entities[entity.aiTargetID].className == entity.queryTemp( 'destNpcClassName' ):
				entity.setTemp( 'destEntityID', entity.aiTargetID )


class AIAction67( AIAction ):
	"""
	镖车检查是否到达目标,到达后，完成任务，自身消失
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if entity.controlledBy != None:
			return
		disEntityID = entity.queryTemp( 'destEntityID', 0 )
		questID = entity.queryTemp('questID')
		ownerID = entity.getOwnerID()
		if not (BigWorld.entities.has_key( disEntityID ) and BigWorld.entities.has_key( ownerID )):
			return
		g = BigWorld.entities.get
		disEntity = g( disEntityID )
		player = g(ownerID)
		distance = csarithmetic.distancePP3( disEntity.position, entity.position )
		if distance < 10 and disEntity.spaceID == entity.spaceID:		#镖车到达NPC的范围
			player.questTaskIncreaseState( questID, entity.queryTemp('eventIndex') )
			# 运镖完成后 在镖车消失后广播运镖完成 by姜毅
			if not entity.queryTemp( 'questFinish' ):
				self.dartMissionBrocad( questID, player )
			entity.setTemp( 'questFinish', True )

	def dartMissionBrocad( self, questID, player ):
		"""
		运镖或劫镖成功的广播 by姜毅14:10 2009-7-31
		@param missionType : 任务类型
		@param missonnType : UINT8
		"""
		#self.family_grade
		player.brocastMessageDart( questID )

class AIAction68( AIAction ):
	"""
	NPC向目标移动
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.chaseTarget( BigWorld.entities.get( entity.targetID ), 10.0 )


class AIAction70( AIAction ):
	"""
	镖车死亡通知玩家任务失败
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		playerName = entity.ownerName
		if BigWorld.entities.has_key( entity.getOwnerID() ):
			BigWorld.entities[entity.getOwnerID()].handleDartFailed()
		elif playerName != '':
			BigWorld.globalData['DartManager'].addDartMessage( playerName, csstatus.ROLE_QUEST_DART_NPC_DIE, True )


class AIAction69( AIAction ):
	"""
	向拥有者发送一个系统信息，并停下来
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 20.0


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		ownerBaseMailbox = entity.getOwner()
		entity.stopMoving()
		spaceName = entity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )

		if not hasattr( ownerBaseMailbox, "client" ):
			return

		if entity.queryTemp("lastSendTime", 0 ) == 0:
			ownerBaseMailbox.client.onStatusMessage( csstatus.ROLE_QUEST_CONVOY_OWNER_DISTANCE_FAR, "\'%s\',%d,%d" % ( g_maps_info[spaceName], int(entity.position[0]), int(entity.position[2]) ) )
			entity.setTemp("lastSendTime", time.time() )
		else:
			if time.time()- entity.queryTemp("lastSendTime", 0 ) > 20.0:
				ownerBaseMailbox.client.onStatusMessage( csstatus.ROLE_QUEST_CONVOY_OWNER_DISTANCE_FAR, "\'%s\',%d,%d" % ( g_maps_info[spaceName], int(entity.position[0]), int(entity.position[2]) ) )
				entity.setTemp("lastSendTime", time.time() )

class AIAction71( AIAction ):
	"""
	NPC通知拥有者一个事件型任务失败
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0
		self.param2 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )
		self.param2 = section.readInt( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		ownerBase = entity.queryTemp( "npc_ownerBase", None )
		if ownerBase:
			ownerID = ownerBase.id
			if BigWorld.entities.has_key( ownerID ):
				owner = BigWorld.entities[ ownerID ]
				owner.questTaskFailed( self.param1, self.param2 )
			else:
				ownerBase.cell.questTaskFailed( self.param1, self.param2 )
		else:
			ERROR_MSG( "can not find the owner!" )

class AIAction72( AIAction ):
	"""
	怪物脱离战斗后消失
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if not entity.getState() == csdefine.ENTITY_STATE_FIGHT:
			#entity.destroy()
			entity.addTimer( 0.1, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )


class AIAction73( AIAction ):
	"""
	水晶召唤怪物
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		monster = entity.createObjectNearPlanes( self.param1, entity.position, entity.direction, {"spawnPos": tuple(entity.position ), "level": entity.level, "spawnMB": entity.spawnMB })
		entity.resetEnemyList()
		entity.spawnMB = None
		entity.planesAllClients( "playCallMonsterEffect", () )
		entity.addTimer( 0.2, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )


class AIAction74( AIAction ):
	"""
	水晶释放技能
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt64( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		target = SkillTargetObjImpl.createTargetObjPosition( entity.position )	# 包装技能施展对象
		spell = g_skills[self.param1]
		spell.use( entity, target )										# 则，使用技能

class AIAction75( AIAction ):
	"""
	向特定的坐标移动
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

		position = section.readString( "param1" )
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param1 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.pos = pos

		try: #为了防止策划不填或默认填0的情况modify by wuxo
			self.backTo = bool( section.readInt( "param2" ) )# 是否背向移动
		except:
			self.backTo = False	# 是否背向移动

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if entity.actionSign( csdefine.ACTION_FORBID_MOVE ):	# 如果禁止移动
			entity.stopMoving()
		else:
			position = entity.queryTemp( "gotoPosition", None )
			if position:
				position = Math.Vector3( position[0], position[1], position[2] )
			if entity.isMoving() and position and self.pos and math.fabs( position.x - self.pos.x ) < 0.5 and math.fabs( position.z - self.pos.z ) < 0.5:
				return
			entity.gotoPosition( self.pos, not self.backTo )

class AIAction76( AIAction ):
	"""
	通知副本，我已到达指定位置
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		try:
			spaceBase = BigWorld.cellAppData["spaceID.%i" % entity.spaceID]
			spaceEntity = BigWorld.entities[ spaceBase.id ]
		except:
			DEBUG_MSG( "not find the spaceEntity!" )

		spaceEntity.getScript().onMonsterArrive( spaceEntity )		# 通知副本，我已到达指定位置

		#entity.destroy()	# 消失
		entity.addTimer( 1, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )	# 消失

class AIAction77( AIAction ):
	"""
	从战斗列表中随机选取一个，对其施放自身等级技能
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt64( "param1" ) * 1000

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if len( entity.enemyList ) > 0:
			targetID = random.choice( entity.enemyList.keys() )
			entity.spellTarget( self.param1 + entity.level,  targetID )

class AIAction78( AIAction ):
	"""
	召唤怪物
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0
		self.param2 = ""
		self.param3 = ""


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )	# 召唤怪物数量
		self.param2 = section.readString( "param2" )	# 召唤怪物className

		position = section.readString( "param3" )
		if position and position != '0':
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param3 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.param3 = pos

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		try:
			spaceBase = BigWorld.cellAppData["spaceID.%i" % entity.spaceID]
			spaceEntity = BigWorld.entities[ spaceBase.id ]		# 找到副本
		except:
			DEBUG_MSG( "not find the spaceEntity!" )
			return

		if self.param3 == "":
			position = entity.position
		else:
			position = self.param3

		for i in xrange( self.param1 ):

			if self.param3 == "":
				pos = position + Math.Vector3( random.randint(-2,2), 0,random.randint(-2,2) )
				monster = entity.createObjectNearPlanes( str(self.param2), pos, entity.direction, { "spawnPos": tuple(position), "level" : entity.level } )
			else:
				monster = entity.createObjectNearPlanes( str(self.param2), position, entity.direction, { "spawnPos": tuple(position), "level" : entity.level } )
			# 副本记录召唤出的怪物id
			tempCallMonsterIDs = spaceEntity.queryTemp( "tempCallMonsterIDs", [] )		# 取得副本记录召唤出的怪物id列表
			tempCallMonsterIDs.append( monster.id )
			spaceEntity.setTemp( "tempCallMonsterIDs", tempCallMonsterIDs )
			enemyList = entity.enemyList
			if len( enemyList ):
				ownerID = enemyList.keys()[0]
				monster.setTemp( "ownerID", ownerID )
			
			g_fightMgr.buildGroupEnemyRelationByIDs( monster, enemyList.keys() )

class AIAction79( AIAction ):
	"""
	NPC发言，并且记录发言时间
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if len( self.param1 ) > 0:
			entity.say( self.param1 )

		entity.setTemp( "tempSayTime", time.time() )	# 设置临时变量，存储NPC发言的时间
		entity.setTemp( "tempSayFlag", True )			# 设置临时变量，标记发言过

class AIAction80( AIAction ):
	"""
	寻找指定范围内特定类型目标，目标血量低于指定值，对其施放指定技能
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0.0
		self.param2 = ""
		self.param3 = 0
		self.param4 = 0.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readFloat( "param1" )			# 范围
		self.param2 = section.readString( "param2" )		# className
		self.param3 = section.readInt64( "param3" ) * 1000	# 技能编号
		self.param4 = section.readFloat( "param4" ) / 100	# 血量限制

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if entity.queryTemp( "onlyOneTime", False ):	# 只需要施放一次技能
			return
		target = None
		monsterList = entity.entitiesInRangeExt( self.param1, "Monster", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in monsterList:
			if e.className == self.param2:
				target = e
				break
		if target and float(target.HP)/ float(target.HP_Max)  <= self.param4:
			entity.spellTarget( self.param3 + entity.level, target.id )
			entity.setTemp( "onlyOneTime", True )	# 只需要施放一次技能

class AIAction81( AIAction ):
	"""
	随机选取战斗列表，作为当前目标
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if len( entity.enemyList ) > 0:
			targetID = random.choice( entity.enemyList.keys() )

			if targetID > 0:
				entity.setAITargetID( targetID )

class AIAction82( AIAction ):
	"""
	设置标记
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )			# 标记

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.setTemp( self.param1, True )						# 设置标记

class AIAction83( AIAction ):
	"""
	移除标记
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )			# 标记

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.removeTemp( self.param1 )		# 设置标记

class AIAction84( AIAction ):
	"""
	选取一定范围内特定类型的怪物，作为当前目标
	"""
	def __init__( self ):
		AIAction.__init__( self )

		self.param1 = 0.0
		self.param2 = ""
		self.param3 = "Monster"		# 默认为Monster

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

		self.param1 = section.readFloat( "param1" )							# 范围
		self.param2 = section.readString( "param2" )						# className
		self.param3 = section.readString( "param3" )						# EntityType

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		flag = False
		monsterList = entity.entitiesInRangeExt( self.param1, self.param3, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in monsterList:
			if e.className == self.param2:
				target = e
				flag = True
				break

		if not flag:	# 如果没有找到boss
			return

		#entity.setAITargetID( target.id )
		if entity.targetID != target.id:
			entity.changeAttackTarget( target.id )

class AIAction85( AIAction ):
	"""
	对自身使用随机的一个技能
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = []

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

		for e in (section.readString( "param1" )).split( ";" ):
			if e !=  "":	#add by wuxo 2011-12-20
				self.param1.append( int( e ) )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		# 攻击判断
		skillID = random.choice( self.param1 )
		spell = g_skills[ skillID ]								# 获取配置的攻击技能
		state = entity.spellTarget( skillID,  entity.id )
		# 有可能被反射致死
		if entity.state == csdefine.ENTITY_STATE_DEAD:
			return

		if state == csstatus.SKILL_GO_ON:						# 正常施展,,直接返回
			return
		elif state in [ csstatus.SKILL_NOT_HIT_TIME, csstatus.SKILL_NOT_READY, csstatus.SKILL_INTONATING ]:
			if entity.isMoving():
				entity.stopMoving()
		else:
			# 其它错误
			INFO_MSG( "%i: skill %i use state = %i." % ( entity.id, skillID, state ) )

class AIAction86( AIAction ):
	"""
	活动怪物头领死亡
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		# 攻击判断
		if entity.queryTemp('deadFlags', False):
			entity.addTimer( 0.1, 0, ECBExtend.ACTIVITY_MONSTER_DISAPPEAR_CBID )
			entity.removeTemp('deadFlags')

class AIAction87( AIAction ):
	"""
	骑宠传送
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.spaceName = section.readString( "param1" )

		position = section.readString( "param2" )
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param2 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.pos = pos

		direction = section.readString( "param3" )
		if direction:
			dir = vector3TypeConvert( direction )
			if dir is None:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param3" % ( self.getAIDataID(), self.getID(), direction ) )
			else:
				self.direction = dir

		self.patrolPathNode = section.readString( "param4" )
		self.patrolList = section.readString( "param5" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.setTemp( "teleportFly_data", ( self.patrolPathNode, self.patrolList, self.spaceName, self.pos, self.direction ) )
		indexs = entity.findBuffsByBuffID( 99010 )
		entity.getBuff( indexs[0] )["skill"].updateData( entity )

class AIAction88( AIAction ):
	"""
	传送当前地图某位置
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.spaceName = section.readString( "param1" )

		position = section.readString( "param2" )
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param2 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.pos = pos

		direction = section.readString( "param3" )
		if direction:
			dir = vector3TypeConvert( direction )
			if dir is None:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param3" % ( self.getAIDataID(), self.getID(), direction ) )
			else:
				self.direction = dir

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		#entity.gotoSpace( self.spaceName, self.pos, self.direction )
		entity.openVolatileInfo()	# 传送前开启volatile，为了表现正确，并不立即关闭，在enity停止移动后会触发关闭，就这个entity而言，就算不触发关闭也不会造成过度的消耗
		entity.position = self.pos
		entity.direction = self.direction

class AIAction89( AIAction ):
	"""
	飞翔传送动作与速度控制
	角色使用的AIAction
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.actionName = section.readString( "param1" )
		self.speed = section.readFloat( "param2" ) * csconst.FLOAT_ZIP_PERCENT

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		fly_model_add_speed = entity.queryTemp( "fly_model_add_speed", 0 )
		entity.move_speed_value -= fly_model_add_speed
		entity.move_speed_value += self.speed
		entity.setTemp( "fly_model_add_speed", self.speed )
		entity.calcMoveSpeed()
		entity.client.onTeleportVehicleModeActionChanged( self.actionName )

class AIAction90( AIAction ):
	"""
	飞翔传送结束
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.removeAllBuffByBuffID( 99010, [0] )
		entity.removeAllBuffByBuffID( 99027, [0] )
		fly_model_add_speed = entity.queryTemp( "fly_model_add_speed", 0 )
		if fly_model_add_speed > 0:
			entity.move_speed_value -= fly_model_add_speed
			entity.removeTemp( "fly_model_add_speed" )
			entity.calcMoveSpeed()

class AIAction91( AIAction ):
	"""
	骑宠传送 随机路径
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.patrolPathNode = section.readString( "param1" ).split( "|" )
		self.patrolList = section.readString( "param2" ).split( "|" )
		self.spaceName = section.readString( "param3" ).split( "|" )
		self.pos = [ eval( i ) for i in section.readString( "param4" ).split( "|" ) ]
		self.teleportData = [ ( x.split("&")[0], eval( x.split("&")[1] ) ) for x in section.readString( "param5" ).split("|") ]

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		index = random.randint( 0, len( self.spaceName ) - 1 )
		entity.setTemp( "teleportFly_data", ( self.patrolPathNode[ index ], self.patrolList[ index ], self.spaceName[ index ], self.pos[ index ], ( 0, 0, 0 ) ) )
		indexs = entity.findBuffsByBuffID( 99010 )
		entity.getBuff( indexs[0] )["skill"].updateData( entity )
		data = self.teleportData[ index ]
		entity.gotoSpace( data[ 0 ], data[ 1 ], ( 0, 0, 0 ) )

class AIAction92( AIAction ):
	"""
	寻找到PK值大于某数玩家则加入战斗列表
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self._radius = section.readFloat( "param1" ) # 搜索半径
		self._pkValue = section.readInt( "param2" ) # 搜索pk值在多少以上

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		es = entity.entitiesInRangeExt( self._radius, None, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in es:
			if e.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and \
				e.state != csdefine.ENTITY_STATE_DEAD and \
				e.state != csdefine.ENTITY_STATE_PENDING:
				if e.pkValue > self._pkValue:
					entity.changeAttackTarget( e.id )
					return

class AIAction93( AIAction ):
	"""
	记录自身朝向
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.setTemp( "figthDirection", entity.direction )

class AIAction94( AIAction ):
	"""
	改变自身朝向到记录的朝向
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.direction = entity.queryTemp( "figthDirection", ( 0, 0, 0 ) )


class AIAction95( AIAction ):
	"""
	用于混沌将领剩余10%血的时候，发言，并且限定唯一攻击目标为猰貐
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""

		if entity.HP_Max / entity.HP < 10:
			return

		if entity.queryTemp( "said", True ):
			roles = entity.entitiesInRangeExt( 30.0, "Role", entity.position )
			WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
			for role in roles:
				role.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.YA_YU_VOICE8, cschannel_msgs.QIAN_NIAN_DU_WA_VOICE_8, [] )
			entity.setTemp( "said", False )

		yayu = BigWorld.entities.get( entity.queryTemp( "enemyYayuID" ), None )
		if yayu is None:
			return

		if yayu.state == csdefine.ENTITY_STATE_DEAD:
			return

		if entity.targetID == yayu.id:
			return

		entity.changeAttackTarget( yayu.id )



class AIAction96( AIAction ):
	"""
	用于拯救猰貐爆烈红魔死亡，或者靠近猰貐使用自曝技能
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""

		#if entity.HP * 1.0 / entity.HP_Max < 0.8:
		#	entity.spellTarget( 122187001, entity.id )
		#	return
		yayu = BigWorld.entities[ entity.queryTemp( "enemyYayuID" ) ]
		#if entity.queryTemp( "useBaolie", False ):
		#	return
		if entity.position.x - yayu.position.x < 8.0 and entity.position.x - yayu.position.x > -8.0:
			if entity.position.z - yayu.position.z < 8.0 and entity.position.z - yayu.position.z > -8.0:
				#entity.setTemp( "useBaolie", True )
				entity.spellTarget( 122187001, entity.id )
				entity.addTimer( 0.2, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )			# 要死也不能立即死，保证技能放完再死
				# entity.destroy()
				return


class AIAction97( AIAction ):
	"""
	用于拯救猰貐硬甲蓝魔，这个怪物一直锁定不标，一直不变。
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""

		yayu = BigWorld.entities.get( entity.queryTemp( "enemyYayuID" ), None )
		if yayu is None:
			return

		if yayu.state == csdefine.ENTITY_STATE_DEAD:
			return

		if entity.targetID == yayu.id:
			return

		entity.changeAttackTarget( yayu.id )
		entity.spellTarget( 122188001, entity.id )
#


class AIAction98( AIAction ):
	"""
	把敌人加入到自己的仆从敌人列表中
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		lastTime = 0
		lastID = 0
		for eid, val in entity.enemyList.iteritems():
			if val > lastTime:
				lastTime = val
				lastID = eid
		lastEnemy = BigWorld.entities.get( lastID )
		if lastEnemy:
			g_fightMgr.buildGroupEnemyRelationByIDs( lastEnemy, entity.littleMonsterIDs )

class AIAction99( AIAction ):
	"""
	把敌人加入自己的主人敌人列表中
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		lastTime = 0
		lastID = 0

		masterID = entity.queryTemp("masterID",0)
		master = BigWorld.entities.get( masterID, None )
		if master:
			for eid, val in entity.enemyList.iteritems():
				if val > lastTime:
					lastTime = val
					lastID = eid
			lastEnemy = BigWorld.entities.get( lastID )
			if lastEnemy:			#有报错为lastID为0的情况。因此做一个判断，同时调整了流程，当没有master时不做循环。
				g_fightMgr.buildEnemyRelation( master, lastEnemy )

class AIAction100( AIAction ):
	"""
	（城战AI）选定最近的塔楼为攻击目标
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		items = entity.enemyList.items()
		if len( items ) <= 0:
			return

		distance = 100.0
		eid = items[0][0]

		for entityID, time in items:
			e = BigWorld.entities.get( entityID )
			if e and not e.state == csdefine.ENTITY_STATE_DEAD:
				distance1 = csarithmetic.distancePP3( e.position, entity.position )
				if distance > distance1:
					eid = entityID
					distance = distance1

		e = BigWorld.entities.get( eid )
		if e and not e.state == csdefine.ENTITY_STATE_DEAD and entity.targetID != eid:
			entity.setAITargetID( eid )
			entity.changeAttackTarget( eid )

class AIAction101( AIAction ):
	"""
	改变当前Entity状态到某状态
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.state = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if entity.state != self.state:
			entity.changeState( self.state )

class AIAction102( AIAction ):
	"""
	对自身周围目标施放技能最多X个受术者
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.skillID = section.readInt( "param1" )
		self.receiverCount = section.readInt( "param2" )
		self.radius = section.readFloat( "param3" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if entity.isMoving():
			entity.stopMoving()

		count = self.receiverCount
		es = entity.entitiesInRangeExt( self.radius, None, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in es:
			if entity.spellTarget( self.skillID, e.id ) == csstatus.SKILL_GO_ON:
				count = count - 1
				if count <= 0:
					return

class AIAction103( AIAction ):
	"""
	（城战AI）选定最近的塔楼并为塔楼加血
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.radius = section.readFloat( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		es = entity.entitiesInRangeExt( self.radius, "MonsterCityWar", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in es:
			if not e.isDestroyed and e.isTower() and not e.towerInBuilding:
				e.addHP( entity.HP )
				DEBUG_MSG( "addTowerHPSuccess selfName=%s, entity name = %s, type=%i" % ( entity.getName(), e.getName(), e.utype ) )
				entity.addTowerHPSuccess()

class AIAction104( AIAction ):
	"""
	NPC喊话（屏幕中央出现）
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.channel_msgs = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		es = entity.entitiesInRangeExt( csconst.CHAT_CHANNEL_SC_HINT_AREA, "Role", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in es:
			if e.spaceID == entity.spaceID:
				e.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", self.channel_msgs, [])

class AIAction105( AIAction ):
	"""
	向特定的坐标移动，坐标记录读取自身temp
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.temp = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if entity.actionSign( csdefine.ACTION_FORBID_MOVE ):	# 如果禁止移动
			entity.stopMoving()
		else:
			entity.gotoPosition( entity.queryTemp( self.temp, (0, 0, 0) ) )

class AIAction106( AIAction ):
	"""
	搜索友方生命，对生命少于50%的一个目标施放治疗术
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self._param1 = 0.0	#生命值（百分比）
		self._param2 = 0	# 技能id

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self._param1 = section.readFloat( "param1" )
		self._param2 = section.readInt( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		for eid in entity.friendList:
			if BigWorld.entities.has_key( eid ):
				e = BigWorld.entities[ eid ]
				if e.HP / float( e.HP_Max ) < self._param1:
					entity.spellTarget( self._param2, eid )
					break

class AIAction107( AIAction ):
	"""
	与一定范围内特定类型的怪物，互换位置
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AIAction.__init__( self )
		self.param1 = 0.0
		self.param2 = ""
		self.param3 = "Monster"		# 默认为Monster


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readFloat( "param1" )			# 范围
		self.param2 = section.readString( "param2" )		# className
		self.param3 = section.readString( "param3" )		# 怪物EntityType

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		monsterList = entity.entitiesInRangeExt( self.param1, self.param3, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in monsterList:
			if e.className == self.param2:
				position = copy.copy( entity.position )
				entity.position = e.position
				e.position = position
				return

class AIAction108( AIAction ):
	"""
	清除某些buff
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AIAction.__init__( self )
		self.buffs = []

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.buffs = section.readString( "param1" ).split("|")

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		for buff in self.buffs:
			entity.removeAllBuffByBuffID( int(buff), [csdefine.BUFF_INTERRUPT_NONE] )

class AIAction109( AIAction ):
	"""
	从战斗列表中随机选取一个，对其施放指定技能
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt64( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if len( entity.enemyList ) > 0:
			targetID = random.choice( entity.enemyList.keys() )
			entity.spellTarget( self.param1,  targetID )

class AIAction110( AIAction ):
	"""
	随机召唤带陷阱的怪物
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0
		self.param2 = ""
		self.radiusDict = {}					# 陷阱半径
		self.enterSpellDict = {}				# 进入陷阱施放的技能
		self.leaveSpellDict = {}				# 离开陷阱施放的技能


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )	# 召唤怪物数量
		self.classNameList = section.readString( "param2" ).split( ";" )	# 召唤怪物className(className1;className2;className3)
		self.radiusStr = section.readString( "param3" )						# 陷阱半径as like : className1:radius1;className2:radius2
		for e in self.radiusStr.split( ";" ):
			dict = e.split( ":" )
			self.radiusDict[ str(dict[0]) ] = int(dict[1])
		self.enterSpellStr = section.readString( "param4" )					# 进入陷阱施放的技能as like : className1:skill1;className2:skill2
		for e in self.enterSpellStr.split( ";" ):
			dict = e.split( ":" )
			self.enterSpellDict[ str(dict[0]) ] = int(dict[1])
		self.leaveSpellStr = section.readString( "param5" )					# 离开陷阱施放的技能as like : className1:skill1;className2:skill2
		for e in self.leaveSpellStr.split( ";" ):
			dict = e.split( ":" )
			self.leaveSpellDict[ str(dict[0]) ] = int(dict[1])

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		try:
			spaceBase = BigWorld.cellAppData["spaceID.%i" % entity.spaceID]
			spaceEntity = BigWorld.entities[ spaceBase.id ]		# 找到副本
		except:
			DEBUG_MSG( "not find the spaceEntity!" )

		for i in xrange( self.param1 ):
			className = str( random.choice( self.classNameList ) )
			pos = entity.position + Math.Vector3( random.randint(-2,2), 0,random.randint(-2,2) )
			newDict = { \
				"spawnPos": tuple(entity.position),
				"level" : entity.level,
				"radius": self.radiusDict[className],
				"enterSpell" : self.enterSpellDict[className],
				"leaveSpell" : self.leaveSpellDict[className]\
			}
			monster = entity.createObjectNearPlanes( className, pos, entity.direction, newDict )

			g_fightMgr.buildGroupEnemyRelationByIDs( monster, entity.enemyList.keys() )

class AIAction111( AIAction ):
	"""
	把周围若干米内玩家加入战斗列表
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )	# 搜索的半径

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		roleList = entity.entitiesInRangeExt( self.param1, "Role", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		g_fightMgr.buildGroupEnemyRelation( entity, roleList )

class AIAction112( AIAction ):
	"""
	找一定范围内特定类型的怪物，如果其有特定的buff，则都死亡。
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AIAction.__init__( self )
		self.param1 = 0.0
		self.param2 = ""
		self.param3 = "Monster"		# 默认为Monster
		self.param4 = 0


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readFloat( "param1" )			# 范围
		self.param2 = section.readString( "param2" )		# className
		self.param3 = section.readString( "param3" )		# 怪物EntityType
		self.param4 = section.readInt( "param4" )			# buff的id

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		monsterList = entity.entitiesInRangeExt( self.param1, self.param3, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in monsterList:
			if e.className == self.param2:
				if len( e.findBuffsByBuffID( self.param4 ) ) > 0:
					if ( entity.enemyList.keys() ) > 0:
						enemyID = entity.enemyList.keys()[0]
						entity.die( enemyID )
						e.die( enemyID )
				return

class AIAction113( AIAction ):
	"""
	将战斗列表中某className的怪物从敌人列表中删除
	"""
	def __init__( self ):
		"""
		初始化
		"""
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )			# className

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI  ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		removeEnemyList = []
		for enemyID in entity.enemyList:
			enemy = BigWorld.entities.get( enemyID )
			if enemy and hasattr( enemy, "className" ) and enemy.className == self.param1:
				removeEnemyList.append( enemyID )
		g_fightMgr.breakGroupEnemyRelationByIDs( entity, removeEnemyList )
		
class AIAction114( AIAction ):
	"""
	随机召唤怪物
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0
		self.param2 = ""


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )	# 召唤怪物数量
		self.classNameList = section.readString( "param2" ).split( ";" )	# 召唤怪物className(className1;className2;className3)

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		try:
			spaceBase = BigWorld.cellAppData["spaceID.%i" % entity.spaceID]
			spaceEntity = BigWorld.entities[ spaceBase.id ]		# 找到副本
		except:
			DEBUG_MSG( "not find the spaceEntity!" )
		
		for i in xrange( self.param1 ):
			className = str( random.choice( self.classNameList ) )
			pos = entity.position + Math.Vector3( random.randint(-2,2), 0,random.randint(-2,2) )
			newDict = { "spawnPos": tuple(entity.position), "level" : entity.level }
			monster = entity.createObjectNearPlanes( className, pos, entity.direction, newDict )
			g_fightMgr.buildGroupEnemyRelationByIDs( monster, entity.enemyList )

class AIAction115( AIAction ):
	"""
	关门
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )	# 门的className

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		spaceBase = entity.getCurrentSpaceBase()
		if spaceBase is None: return
		spaceBase.openDoor( { "entityName" : self.param1 } )		# 开启门

class AIAction116( AIAction ):
	"""
	选取一定范围内特定类型的有特定buff的entity，作为当前目标
	"""
	def __init__( self ):
		AIAction.__init__( self )

		self.param1 = 0.0
		self.param2 = 0
		self.param3 = "Monster"		# 默认为Monster

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

		self.param1 = section.readFloat( "param1" )							# 范围
		self.param2 = section.readInt( "param2" )							# buffID
		self.param3 = section.readString( "param3" )						# EntityType

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		flag = False
		entityList = entity.entitiesInRangeExt( self.param1, self.param3, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in entityList:
			buffs = e.findBuffsByBuffID( self.param2 )
			if len( buffs ) > 0:
				target = e
				flag = True
				break

		if not flag:	# 如果没有找到entity
			return

		if entity.targetID != target.id:
			entity.changeAttackTarget( target.id )

class AIAction117( AIAction ):
	"""
	城市管理员心跳 （检测新城市主人， 并设置名称）
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		spaceName = entity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		key = "holdCity.%s" % spaceName
		if BigWorld.globalData.has_key( key ):
			dbid, name = BigWorld.globalData[ key ]
			if entity.own_familyName != name:
			    entity.own_familyName = name

class AIAction118( AIAction ):
	"""
	AI发声
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		# 声音事件配置
		self.param1 = section.readString( "param1" )
		param2 = section.readString( "param2" )
		if param2 == "":
			self.param2 = 0
		else:
			self.param2 = int( param2 )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.planesAllClients( "onMakeASound", ( self.param1, self.param2 ) )



class AIAction119( AIAction ):
	"""
	把所有者设置为最高伤害的玩家
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		id = 0
		value = 0
		for iID,iValue in entity.damageList.iteritems():
			if value <= iValue:
				id = iID
		entity.bootyOwner = ( id, 0 )


class AIAction120( AIAction ):
	"""
	靠近则完成任务
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		# 声音事件配置
		self.__questID	 		= section.readInt( "param1" )
		self.__taskIndex	 	= section.readInt( "param2" )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.questTaskIncreaseState( self.__questID, self.__taskIndex )


class AIAction121( AIAction ):
	"""
	怪物攻城BOSS死亡喊话
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		id = 0
		value = 0
		for iID,iValue in entity.damageList.iteritems():
			if value <= iValue:
				id = iID
		player = BigWorld.entities.get( id, None )
		if player is None:
			return
		entity.say( cschannel_msgs.MONSTER_ATTACK_BOSS_DIE_SAY_01%player.playerName )


class AIAction122( AIAction ):
	"""
	进入战斗即记录开战时刻 by 姜毅
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		tick = int( time.time() )
		entity.setTemp( "fightStartTick", tick )


class AIAction123( AIAction ):
	"""
	释放一次技能即增加技能使用计数 by 姜毅
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		skillUseCount = entity.queryTemp( "uskCount", 0 ) + 1
		entity.setTemp( "uskCount", skillUseCount )


class AIAction124( AIAction ):
	"""
	同步相关者血条（夸父神殿），这个AI暂时只能用于副本
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.__classNames 		= section.readString( "param1" ).split("|")
		self.__range		 	= section.readInt( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		nextCount = entity.queryTemp( "nextSetHPCount", 1 )				#准备设置次数
		curCount = entity.queryTemp( "curSetHPCount", 0 )				#已经设置的次数
		if nextCount == curCount:										#如果相等，说明自己是被同步的对象，不需要同步他人
			entity.setTemp( "nextSetHPCount", nextCount + 1 )
			return
		entity.setTemp( "curSetHPCount", nextCount )
		entity.setTemp( "nextSetHPCount", nextCount + 1 )
		entityList = entity.entitiesInRangeExt( self.__range, "Monster", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for i in entityList:
			if i.className in self.__classNames:
				i.setTemp( "curSetHPCount", nextCount )
				i.HP = entity.HP

class AIAction125( AIAction ):
	"""
	改变指定怪物AI等级
	应用：这个意思是让某一个或多个怪物执行一个事情。
	实现方式是: 临时改变怪物的AI等级，让他们根据新配置的AI等级做具体的事情。事情完毕，AI等级恢复。
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.__classNames 		= section.readString( "param1" ).split("|")
		self.__range		 	= section.readInt( "param2" )
		self.__aiLevel		 	= section.readInt( "param3" )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entityList = entity.entitiesInRangeExt( self.__range, "Monster", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for i in entityList:
			if i.className in self.__classNames:
				i.setNextRunAILevel( self.__aiLevel )

class AIAction126( AIAction ):
	"""
	死亡
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if entity.state == csdefine.ENTITY_STATE_DEAD:
			return
		entity.die(0)


class AIAction127( AIAction ):
	"""
	把自身的攻击目标改为特定怪物的攻击目标
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.__className 		= section.readString( "param1" )
		self.__range		 	= section.readInt( "param2" )



	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entityList = entity.entitiesInRangeExt( self.__range, "Monster", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for i in entityList:
			if i.className == self.__className:
				if entity.targetID != i.targetID:
					entity.changeAttackTarget( i.targetID )
				return


class AIAction128( AIAction ):
	"""
	让怪物播放动作
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.__actionName = section.readString( "param1" )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.planesAllClients( "onPlayAction", ( self.__actionName, ) )


class AIAction129( AIAction ):
	"""
	怪物变为环境物件。
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.resetEnemyList()
		entity.state = csdefine.ENTITY_STATE_ENVIRONMENT_OBJECT
		entity.addFlag( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED )
		entity.actCounterInc( csdefine.ACTION_FORBID_ATTACK )


class AIAction130( AIAction ):
	"""
	环境物件（其实是怪物）变为怪物。
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.state = csdefine.ENTITY_STATE_FREE
		entity.removeFlag( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED )
		entity.actCounterDec( csdefine.ACTION_FORBID_ATTACK )


class AIAction131( AIAction ):
	"""
	记录当前血量
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.setTemp( "ai_save_HP_value", entity.HP )


class AIAction132( AIAction ):
	"""
	打断引导技能
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if entity.inHomingSpell():
			entity.delHomingSpell( csstatus.SKILL_INTERRUPTED_BY_SPELL_3 )



class AIAction133( AIAction ):
	"""
	对进入陷阱的玩家使用技能（小兔快跑使用）
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.skills = section.readString( "param1" ).split( "|" )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		target = BigWorld.entities.get( entity.aiTargetID )

		if target:
			skillID = int( random.choice( self.skills ) )
			entity.spellTarget( skillID, target.id )

class AIAction134( AIAction ):
	"""
	对entity所在位置使用技能
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt64( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		# 攻击判断
		try:
			enemy = BigWorld.entities[ entity.targetID ]
		except:
			return

		spell = g_skills[ self.param1 ]						# 获取配置的攻击技能
		range = spell.getRangeMax( entity )					# 获取技能的最大施法距离
		# 用于解决一堆怪物追击同一个目标时重叠在一起的问题。
		if checkAndMove( entity ):
			return

		state = entity.spellPosition( self.param1,  copy.copy( enemy.position ) )

		# 有可能被反射致死
		if entity.state == csdefine.ENTITY_STATE_DEAD:
			return

		if state == csstatus.SKILL_GO_ON:						# 正常施展,,直接返回
			return
		elif state in [ csstatus.SKILL_NOT_HIT_TIME, csstatus.SKILL_NOT_READY, csstatus.SKILL_INTONATING ]:
			if entity.isMoving():
				entity.stopMoving()
		elif state == csstatus.SKILL_TOO_FAR:
			if entity.actionSign( csdefine.ACTION_FORBID_MOVE ):
				DEBUG_MSG( "im cannot the move!" )
				entity.stopMoving()
				return
			if entity.queryTemp( "AI_Trace_Position", None ) != None:
				entity.gotoPosition( random.choise( entity.queryTemp( "AI_Trace_Position", None ) ) )
			elif entity.chaseTarget( enemy, spell.getRangeMax( entity ) ):		# 距离过远,,追击目标
				return
		else:
			# 其它错误
			INFO_MSG( "%i: skill %i use state = %i." % ( entity.id, self.param1, state ) )


class AIAction135( AIAction ):
	"""
	神树血量百分比，通知所在的space
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		spaceBase = entity.getCurrentSpaceBase()
		if spaceBase is None: return
		spaceBase.cell.remoteScriptCall( "onTreeHPChange", (int(entity.HP * 100 / entity.HP_Max),  ) )

class AIAction136( AIAction ):
	"""
	给所在的spacebase 发送事件
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		spaceBase = entity.getCurrentSpaceBase()
		if spaceBase is None: return 
		spaceBase.eventHandle( self.param1, {} )


class AIAction137( AIAction ):
	"""
	触发玩家身上的一个任务。
	找不到玩家，就不做任何动作 by mushuang
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""

		#param1: 任务ID
		#param2: 任务目标索引

		AIAction.init( self, section )
		self.questID = section.readInt( "param1" )
		self.taskIdx = section.readInt( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		player = None

		#获取玩家
		players = entity.entitiesInRangeExt( 60.0, "Role" )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		if players:
			player = players[0]

			# if 玩家身上有指定的任务:
			if player.hasTaskIndex( self.questID, self.taskIdx ):
				# 增加指定的QTTaskEventTrigger的状态
				player.questTaskIncreaseState( self.questID, self.taskIdx )

class AIAction138( AIAction ):
	"""
	NPC 移动到指定位置
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = None

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

		position = section.readString( "param1" )
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param1 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.param1 = pos								# 位置

		self.param2 = section.readFloat( "param2" )				#范围


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.doRandomRun( self.param1, self.param2 )

class AIAction139( AIAction ):
	"""
	触发客户端摄像头飞行路径
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )	# 触发的摄像头路径文件ID
		self.param2 = section.readInt( "param2" )		# 触发范围

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		roles = entity.entitiesInRangeExt( self.param2, "Role", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for role in roles:
			role.client.onCameraFly( self.param1 )

class AIAction140( AIAction ):
	"""
	对进入陷阱的目标使用自身等级的技能
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt64( "param1" ) * 1000

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		# 攻击判断
		try:
			enemy = BigWorld.entities[ entity.aiTargetID ]
		except:
			return

		try:
			spell = g_skills[ self.param1 + entity.level ]						# 获取配置的攻击技能
		except:
			ERROR_MSG( "Use skill error, id is %i."%(self.param1 + entity.level) )
			return

		range = spell.getRangeMax( entity )					# 获取技能的最大施法距离
		# 用于解决一堆怪物追击同一个目标时重叠在一起的问题。
		if checkAndMove( entity ):
			return
		entity.spellTarget( self.param1 + entity.level,  entity.aiTargetID )


class AIAction141( AIAction ):
	"""
	改变固定位置周围环境物件的模型（限于副本）
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.oldNumber = ""				#老的模型
		self.newNumber = ""				#新的模型
		self.range = 0					#范围
		self.position = ( 0, 0, 0 )		#位置

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.oldNumber = section.readString( "param1" )
		self.newNumber = section.readString( "param2" )
		self.range = section.readFloat( "param3" )

		position = section.readString( "param4" )
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param4 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.position = pos

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entityList = entity.entitiesInRangeExt( self.range, "EnvironmentObject", self.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for i in entityList:
			if i.modelNumber == self.oldNumber:
				i.modelNumber = self.newNumber



class AIAction142( AIAction ):
	"""
	对entity所在位置使用自身等级的技能
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt64( "param1" ) * 1000

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		# 攻击判断
		try:
			enemy = BigWorld.entities[ entity.targetID ]
		except:
			return

		spell = g_skills[ self.param1 + entity.level ]						# 获取配置的攻击技能
		range = spell.getRangeMax( entity )					# 获取技能的最大施法距离
		# 用于解决一堆怪物追击同一个目标时重叠在一起的问题。
		if checkAndMove( entity ):
			return

		state = entity.spellPosition( self.param1 + entity.level,  copy.copy( enemy.position ) )

		# 有可能被反射致死
		if entity.state == csdefine.ENTITY_STATE_DEAD:
			return

		if state == csstatus.SKILL_GO_ON:						# 正常施展,,直接返回
			return
		elif state in [ csstatus.SKILL_NOT_HIT_TIME, csstatus.SKILL_NOT_READY, csstatus.SKILL_INTONATING ]:
			if entity.isMoving():
				entity.stopMoving()
		elif state == csstatus.SKILL_TOO_FAR:
			if entity.actionSign( csdefine.ACTION_FORBID_MOVE ):
				DEBUG_MSG( "im cannot the move!" )
				entity.stopMoving()
				return
			if entity.queryTemp( "AI_Trace_Position", None ) != None:
				entity.gotoPosition( random.choise( entity.queryTemp( "AI_Trace_Position", None ) ) )
			elif entity.chaseTarget( enemy, spell.getRangeMax( entity ) ):		# 距离过远,,追击目标
				return
		else:
			# 其它错误
			INFO_MSG( "%i: skill %i use state = %i." % ( entity.id, self.param1, state ) )


class AIAction143( AIAction ):
	"""
	把自身的所有者分享给指定ID的怪物
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.range = 100
		self.className = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entityList = entity.entitiesInRangeExt( self.range, "Monster", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for i in entityList:
			if i.className == self.className:
				i.bootyOwner = entity.bootyOwner
				return


class AIAction144( AIAction ):
	"""
	移除怪物（NPC）一个标志位
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.removeFlag( self.param1 )


class AIAction145( AIAction ):
	"""
	镖车对复数运镖者发送标签数据（帮会运镖） by 姜毅
	镖车检查是否到达目标,到达后，完成任务，自身消失
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if entity.controlledBy != None:
			return
		disEntityID = entity.queryTemp( 'destEntityID', 0 )
		if not BigWorld.entities.has_key( disEntityID ):
			return
		g = BigWorld.entities.get
		disEntity = g(disEntityID)
		distance = csarithmetic.distancePP3( disEntity.position, entity.position )
		if distance < 10 and disEntity.spaceID == entity.spaceID :		#镖车到达NPC的范围
			ownerID = entity.getOwnerID()
			if not BigWorld.entities.has_key( ownerID ):
				return
			owner = g(ownerID)
			questID = entity.queryTemp('questID')
			memberIDDict = entity.queryTemp( "dartMembers", {} )
			tongDartMembers = 0
			if len(memberIDDict) > 0:
				# 取得成员运镖任务相关数据
				quest = questIns[questID]
				member_ql = []
				member_taskIndex = 1
				for qaf in quest.afterComplete_:
					if not hasattr( qaf, "_quests" ):
						continue
					_ql = getattr( qaf, "_quests" )
					member_ql = [int(qid[0]) for qid in _ql]
					member_taskIndex = qaf._eventIndex
					break
				for mid in memberIDDict.iterkeys():
					member = g(mid)
					if memberIDDict[mid] == -1 or member is None:
						continue

					tongDartMembers += 1

				# 发起者根据参与人数（自己以外）得到奖励
				for mid in memberIDDict.iterkeys():
					member = g(mid)
					if memberIDDict[mid] == -1 or member is None:
						continue

					for qID in member.questsTable.keys():		# 设置成员运镖任务finish
						if qID in member_ql:
							member.questTaskIncreaseState( qID, member_taskIndex )
							member.setTongDartJoinNum( questID, tongDartMembers )

			owner.setTongDartJoinNum( questID, tongDartMembers )
			owner.questTaskIncreaseState( questID, entity.queryTemp('eventIndex') )
			# 运镖完成后 在镖车消失后广播运镖完成 by姜毅
			if not entity.queryTemp( 'questFinish' ):
				self.dartMissionBrocad( questID, owner )
			entity.setTemp( 'questFinish', True )
			entity.removeTemp( "dartMembers" )

	def dartMissionBrocad( self, questID, player ):
		"""
		运镖或劫镖成功的广播 by姜毅14:10 2009-7-31
		@param missionType : 任务类型
		@param missonnType : UINT8
		"""
		#self.family_grade
		player.brocastMessageDart( questID )


class AIAction146( AIAction ):
	"""
	增加怪物（NPC）一个标志位
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.addFlag( self.param1 )


class AIAction147( AIAction ):
	"""
	清除一组EAI标记
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.eaiIDs = []

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		if section.readString( "param1" ):
			for i in section.readString( "param1" ).split( "|" ):
				if i == "": continue
				self.eaiIDs.append( int(i) )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		for i in self.eaiIDs:
			if not entity.isEAI( i ):
				continue
			entity.eaiIDArray.remove( i )


class AIAction148( AIAction ):
	"""
	向客户端发送一个剧情提示消息
	gjx 2010-12-24( merry christmas! )
	角色使用的AIAction
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.visible = False

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.msg = section.readString( "param1" )
		self.visible = section.readBool( "param2" )   # 如果未填写则默认返回为False

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if self.msg == "" :
			ERROR_MSG( "AI(%i)'s msg is blank!" % ai.getID() )
			return
		entity.client.chat_onScenarioMsg( self.msg, self.visible )


class AIAction149( AIAction ):
	"""
	显示/隐藏客户端的界面
	gjx 2010-12-24( merry christmas! )
	角色使用的AIAction
	"""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.visible = section.readBool( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.client.visibleRootUIs( self.visible )

class AIAction150( AIAction ):
	"""
	改变自身朝向
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.direction = ( 0.0, 0.0, 0.0 )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		direction = section.readString( "param1" )
		if direction:
			dir = vector3TypeConvert( direction )
			if dir is None:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param1" % ( self.getAIDataID(), self.getID(), direction ) )
			else:
				self.direction = dir

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.openVolatileInfo()
		entity.direction = self.direction

class AIAction151( AIAction ):
	"""
	小精灵飞到主人身边（用于和主人之间的距离比较远，需要飞到他旁边,也可以用于飞到不同的space）
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.gotoOwner()

class AIAction152( AIAction ):
	"""
	使在一定范围内的怪物战利品拥有者完成任务目标csdefine.QUEST_OBJECTIVE_EVOLUTION
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.range = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.range = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		bootyOwner = entity.getBootyOwner()
		if bootyOwner[1] != 0:
			players = entity.searchTeamMember( bootyOwner[1], self.range )
			for player in players:
				player.questMonsterEvoluted( entity.className )
				return
		bootyOwnerID = bootyOwner[0]
		if bootyOwnerID == 0:
			return
		try:
			ownerEntity = BigWorld.entities[bootyOwnerID]
		except KeyError:
			return
		else:
			if ownerEntity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and entity.position.distTo( ownerEntity.position ) < self.range:
				ownerEntity.questMonsterEvoluted( entity.className )

class AIAction153( AIAction ):
	"""
	将一定范围内的某类型的Entity加入战斗列表
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.range = 0
		self.enableType = []

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.range = section.readInt( "param1" )
		enableTypeStr = [  type  for type in section.readString( "param2" ).split("|")]
		for tstr in enableTypeStr:
			tval = getattr( csdefine, tstr, -1)
			if tval != -1:
				self.enableType.append( tval )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		rangeEntities = entity.entitiesInRangeExt( self.range, None, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in rangeEntities:
			if e.getEntityType() in self.enableType:
				g_fightMgr.buildEnemyRelation( entity, e )

class AIAction154( AIAction ):
	"""
	将一定范围内的某ID的Entity加入战斗列表
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.range = 0
		self.enableClassName = []

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.range = section.readInt( "param1" )
		self.enableClassName = [  cname  for cname in section.readString( "param2" ).split("|")]

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		rangeEntities = entity.entitiesInRangeExt( self.range, None, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in rangeEntities:
			if e.className in self.enableClassName:
				g_fightMgr.buildEnemyRelation( entity, e )

class AIAction155( AIAction ):
	"""
	重新指定怪物出生点
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.pos = None

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

		position = section.readString( "param1" )
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param1 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.pos = pos

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.spawnPos = self.pos


class AIAction156( AIAction ):
	"""
	设定当前位置未出生点
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.spawnPos = tuple( entity.position )


class AIAction157( AIAction ):
	"""
	更换怪物模型
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.modelNumber = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.modelNumber = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.setModelNumber( self.modelNumber )

class AIAction158( AIAction ):
	"""
	对怪物拥有者使用一个技能
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0
		self.param2 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt64( "param1" )
		param2 = section.readString( "param2" )
		if param2 != "":
			self.param2 = int( param2 )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if self.param1 == 0: return
		# 获取配置的攻击技能
		try:
			spell = g_skills[ self.param1 ]
		except:
			ERROR_MSG( "Use skill error, id is %i."%self.param1 )
			return
		ownerID = 0
		if self.param2:
			ownerBase = entity.queryTemp( "npc_ownerBase", None )
			if ownerBase:
				ownerID = ownerBase.id
		else:
			ownerID = entity.queryTemp( "ownerID", 0 )
		if ownerID == 0: return
		range = spell.getRangeMax( entity )					# 获取技能的最大施法距离
		state = entity.spellTarget( self.param1, ownerID )

		if checkAndMove( entity ):
			return

		# 有可能被反射致死
		if entity.state == csdefine.ENTITY_STATE_DEAD: return

		if state != csstatus.SKILL_GO_ON:
			# 其它错误
			INFO_MSG( "%i: skill %i use state = %i." % ( ownerID, self.param1, state ) )


class AIAction159( AIAction ):
	"""
	设置entity的若干个属性值，仅仅是赋值的方式，值只能是数值，配置此行为时必须咨询程序哪些属性可以设置。

	例如Monster的potential
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.propertiesDict = {}	# like as { "potential":50, "exp":40, ... }

	def init( self, section ):
		"""
		"""
		AIAction.init( self, section )
		self.propertiesDict = eval( section.readString( "param1" ) )

	def do( self, ai, entity ):
		"""
		"""
		for key, value in self.propertiesDict.iteritems():
			if not hasattr( entity, key ):
				ERROR_MSG( "entity( %s ) has not attribute %s" % ( entity.className, key ) )
				continue
			setattr( entity, key, value )
			DEBUG_MSG( "entity(id:%i, className:%s) setattr %s to %s" % ( entity.id, entity.className, key, str( value ) ) )

class AIAction160( AIAction ):
	"""
	修改entity所在地图是否允许飞行的标记
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.canFly = True

	def init( self, section ):
		"""
		"""
		AIAction.init( self, section )
		self.canFly = str( bool( section.readInt( "param1" ) ) )	# 飞行功能要求的格式

	def do( self, ai, entity ):
		"""
		"""
		BigWorld.setSpaceData( entity.spaceID, csconst.SPACE_SPACEDATA_CAN_FLY, self.canFly )

class AIAction161( AIAction ):
	"""
	使用新的潜能倍率刷新npc潜能值
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.potentialRate = 1	# 潜能倍率

	def init( self, section ):
		"""
		"""
		AIAction.init( self, section )
		self.potentialRate = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		"""
		entity.potential = int( g_npcPotential.get( entity.getLevel() ) * self.potentialRate )

class AIAction162( AIAction ):
	"""
	召唤怪物专用，复制主人的伤害列表
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		ownerEntity = BigWorld.entities.get( entity.owner.id )
		if not ( ownerEntity and ownerEntity.isReal() ):
			return

		entity.resetDamageList()
		for eid, damage in ownerEntity.damageList.iteritems():
			entity.addDamageList( eid, damage )


class AIAction163( AIAction ):
	"""
	选取一定范围内某些类型的怪物，以其中第一个作为当前目标
	"""
	def __init__( self ):
		AIAction.__init__( self )

		self.param1 = 0.0
		self.param2 = "Monster"

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

		self.param1 = section.readFloat( "param1" )							# 范围
		self.param2 = section.readString( "param2" ).split("|")				# EntityTypes

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		for iType in self.param2:
			monsterList = entity.entitiesInRangeExt( self.param1, iType, entity.position )
			WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
			amount = len( monsterList )
			while( amount ):
				targetEntity = monsterList[ len( monsterList ) - amount ]
				if entity.targetID != targetEntity.id and entity.queryRelation( targetEntity ) == csdefine.RELATION_ANTAGONIZE:
					entity.changeAttackTarget( targetEntity.id )
					break
				amount -= 1

class AIAction164( AIAction ):
	"""
	设置npc entity的名字
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.name = ""	# 要设置的名字

	def init( self, section ):
		"""
		"""
		AIAction.init( self, section )
		self.name = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		"""
		entity.setName( self.name )

class AIAction165( AIAction ):
	"""
	让从属怪物随便移动
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		"""
		owner = BigWorld.entities.get( entity.ownerID )
		if owner:
			followCheckAndMove( entity, owner )


class AIAction166( AIAction ):
	"""
	增加一个陷阱用于接受任务add by wuxo 2011-10-12
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.range   = 0
		self.questID =0

	def init( self, section ):
		"""
		初始化
		"""
		AIAction.init( self, section )
		rQuestID = section.readString( "param1" )
		rQuestIDL = rQuestID.split(";")
		if len(rQuestIDL) == 2:
			self.range = int(rQuestIDL[0])
			self.questID = int(rQuestIDL[1])

	def do( self, ai, entity ):
		"""
		执行
		"""
		members = entity.entitiesInRangeExt( self.range, "Role", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for p in members:
			quest = p.getQuest( self.questID )
			if quest:
				state = quest.query( entity )
				if state == csdefine.QUEST_STATE_NOT_HAVE:
					quest.gossipDetail( p, None )	#客户端弹出接取任务面板




class AIAction167( AIAction ):
	"""
	个人竞技宝箱一
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		"""
		try:
			player = BigWorld.entities[ entity.aiTargetID ]
		except:
			return
		if player.isEntityType(ENTITY_TYPE_ROLE):
			roles = player.entitiesInRangeExt( 100.0, "Role", player.position )
			roles.append( player )
			liveRoles = []
			for role in roles:
				if not role.queryTemp( "role_competition_die_teleport", False ):
					liveRoles.append(role)
			level = player.level/10 * 10 + 5
			exp = int( 7020 * ( 25 + 5 * level ** 1.2 )/ len( liveRoles ) )
			for i in liveRoles:
				i.addExp( exp, csdefine.REWARD_ROLECOMPETITION_BOX_EXP )
			#entity.destroy()



class AIAction168( AIAction ):
	"""
	个人竞技宝箱二
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		"""
		try:
			player = BigWorld.entities[ entity.aiTargetID ]
		except:
			return
		if player.isEntityType(ENTITY_TYPE_ROLE):
			roles = player.entitiesInRangeExt( 100.0, "Role", player.position )
			roles.append( player )
			liveRoles = []
			for role in roles:
				if not role.queryTemp( "role_competition_die_teleport", False ):
					liveRoles.append(role)
			level = player.level/10 * 10 + 5
			potential = int( ( 17550 * level ** 1.2 ) / len( liveRoles )  )
			for i in liveRoles:
				i.addPotential( potential, csdefine.ACTIVITY_GE_REN_JING_JI )
			#entity.destroy()



class AIAction169( AIAction ):
	"""
	个人竞技宝箱三
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		"""
		championID = entity.queryTemp( "champion" )
		try:
			player = BigWorld.entities[ entity.aiTargetID ]
		except:
			return
		item = g_items.createDynamicItem( self.param1 )
		dropItem = []
		dropItem.append(item)
		itemBox = entity.createEntityNearPlanes( "DroppedBox", player.position, player.direction, {} )
		itemBox.init( ( championID, 0 ), dropItem )
		#entity.destroy()


class AIAction170( AIAction ):
	"""
	潜能副本boss专用ai，给副本发送一个自己死亡的消息以便触发副本怪物死亡处理流程
	"""
	def do( self, ai, entity ):
		# 潜能副本已经存在的实现基础是这个空间中所有的entity互相之间都会是real entity
		try:
			spaceEntity = BigWorld.entities[ entity.getCurrentSpaceBase().id ]
		except:
			EXCEHOOK_MSG( "not find the spaceEntity!" )
			spaceEntity = None
		spaceEntity.getScript().onKillMonster( spaceEntity, True )	# 如果spaceEntity是None，那就让它出错

class AIAction171( AIAction ):
	"""
	组队竞技第一个箱子的奖励
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		"""
		try:
			player = BigWorld.entities[ entity.aiTargetID ]
		except:
			return
		if player:
			roles = player.entitiesInRangeExt( 100.0, "Role", player.position )
			roles.append( player )
			liveRoles = []
			for role in roles:
				if not role.queryTemp( "role_die",False ):
					liveRoles.append( role )
			level = player.level/10 * 10 + 5
			exp = int( 10530 * ( 25 + 5 * pow( level,1.2 ) / len( liveRoles ) ) )
			for i in liveRoles:
				i.addExp( exp, csdefine.REWARD_TEAMCOMPETITION_BOX_EXP )

class AIAction172( AIAction ):
	"""
	组队竞技第二个箱子的奖励
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		"""
		try:
			player = BigWorld.entities[ entity.aiTargetID ]
		except:
			return
		if player:
			roles = player.entitiesInRangeExt( 100.0, "Role", player.position )
			roles.append( player )
			liveRoles = []
			for role in roles:
				if not role.queryTemp( "role_die",False ):
					liveRoles.append( role )
			level = player.level/10 * 10 + 5
			addPotential = int( 26325 * pow( level, 1.2) / len( liveRoles ) )
			for i in liveRoles:
				i.addPotential( addPotential, csdefine.REWARD_TEAMCOMPETITION_POT )

class AIAction173( AIAction ):
	"""
	组队竞技第三个箱子的奖励
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		"""
		try:
			player = BigWorld.entities[ entity.aiTargetID ]
		except:
			return
		if player:
			roles = player.entitiesInRangeExt( 100.0, "Role", player.position )
			roles.append( player )
			item = g_items.createDynamicItem( self.param1 )
			itemsData = [item]
			for role in roles:
				if role.queryRoleRecord( "teamCompetitionWiner") != "1":
					continue
				boxOwner = ( role.id, 0 )
				itemBox = entity.createEntityNearPlanes( "DroppedBox", player.position, player.direction, {} )
				itemBox.init( boxOwner, itemsData )
				role.setRoleRecord( "teamCompetitionWiner", "0" )

class AIAction174( AIAction ):
	"""
	在entity所在的位置创建一个新的entity
	可以配置entity的className和位置，如果
	没有配位置，则使用entity的位置
	"""
	def __init__( self ) :
		AIAction.__init__( self )
		self.param1 = None					# 创建的Entity的className
		self.param2 = None					# 创建的Entity的位置
		self.param4 = None					# 创建的Entity的朝向

	def init( self, section ) :
		"""
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )

		position = section.readString( "param2" )
		if position and position != '0':
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param2 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.param2 = pos

		self.param3 = section.readInt( "param3" )

		direction = section.readString( "param4" )
		if direction and direction != '0':
			dir = vector3TypeConvert( direction )
			if dir is None:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param4" % ( self.getAIDataID(), self.getID(), direction ) )
			else:
				self.param4 = dir

	def do( self, ai, entity ) :
		"""
		"""
		dict = {}
		position = entity.position
		if self.param2 is not None :			# 如果配置有位置，则使用配置的位置
			position = self.param2

		dict[ "spawnPos" ] = tuple( position )

		if self.param3:
			dict[ "level" ] = entity.level

		direction = entity.direction
		if self.param4 is not None:
			direction = self.param4

		newEntity = entity.createObjectNearPlanes( self.param1, position, direction, dict )
		if newEntity is None :
			ERROR_MSG( "Create entity false in ai action171!" )


class AIAction175( AIAction ):
	"""
	帮会竞技第一个箱子的奖励
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		"""
		try:
			player = BigWorld.entities[ entity.aiTargetID ]
		except:
			return
		if player:
			roles = player.entitiesInRangeExt( 100.0, "Role", player.position )
			roles.append( player )
			liveRoles = []
			for role in roles:
				if not role.queryTemp( "role_die", False ):
					liveRoles.append( role )
			exp = int( ( csconst.TONG_COMPETITION_AWARD01 ) / len( liveRoles ) )
			for i in liveRoles:
					i.addExp( exp, csdefine.CHANGE_EXP_TONGCOMPETITION_BOX )

class AIAction176( AIAction ):
	"""
	帮会竞技第二个箱子的奖励
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		"""
		try:
			player = BigWorld.entities[ entity.aiTargetID ]
		except:
			return
		if player:
			roles = player.entitiesInRangeExt( 100.0, "Role", player.position )
			roles.append( player )
			liveRoles = []
			for role in roles:
				if not role.queryTemp( "role_die", False ):
					liveRoles.append( role )
			potential = int( ( csconst.TONG_COMPETITION_AWARD02 ) / len( liveRoles ) )
			for i in liveRoles:
					i.addPotential( potential, csdefine.ACTIVITY_BANG_HUI_JING_JI )

class AIAction177( AIAction ):
	"""
	帮会竞技第三个箱子的奖励
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		"""
		try:
			player = BigWorld.entities[ entity.aiTargetID ]
		except:
			return
		winnerList = entity.queryTemp( "winnerPlayerDBIDs", [] )
		if player:
			roles = player.entitiesInRangeExt( 100 )
			roles.append( player )
			item = g_items.createDynamicItem( self.param1 )
			dropItem = []
			dropItem.append(item)
			for role in roles:
				if role.id in winnerList:
					itemBox = entity.createEntityNearPlanes( "DroppedBox", player.position, player.direction, {} )
					itemBox.init( ( role.id, 0 ), dropItem )

class AIAction178( AIAction ):
	"""
	修改客户端陷阱的触发状态add by wuxo 2011-11-26
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.eventIDs = ""

	def init( self, section ):
		"""
		初始化
		"""
		AIAction.init( self, section )
		self.eventIDs = section.readString( "param1" )


	def do( self, ai, entity ):
		"""
		执行
		"""
		try:
			player = BigWorld.entities[ entity.targetID ]
		except:
			return
		if player.__class__.__name__ != "Role":
			return
		player.client.setCameraFlyState(self.eventIDs)


class AIAction179( AIAction ):
	"""
	销毁一定类型的entity by wuxo 2011-11-28
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.entityType = None
		self.className = None
		self.range = None

	def init( self, section ):
		"""
		初始化
		"""
		AIAction.init( self, section )
		self.entityType = section.readString( "param1" )
		self.className = section.readString( "param2" )
		self.range = section.readInt( "param3" )

	def do( self, ai, entity ):
		"""
		执行
		"""
		entities = entity.entitiesInRangeExt( self.range, self.entityType, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for i in entities:
			if i.className ==  self.className:
				#i.destroy()
				i.addTimer( 0.1, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )


class AIAction180( AIAction ) :
	"""
	地图脚本必须有定义方法：onConditionChange
	entity和副本交互，通知副本条件发生改变
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = ""								# 关键字
		self.param2 = ""								# 数值

	def init( self, section ) :
		"""
		初始化
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )
		self.param2 = section.readString( "param2" )

	def do( self, ai, entity ):
		"""
		通知副本情况有变
		"""
		try:
			spaceEntity = BigWorld.entities[ entity.getCurrentSpaceBase().id ]
		except:
			DEBUG_MSG( "can't get spaceEntity!" )
			return
		spaceEntity.onConditionChange( { self.param1 : self.param2 } )	# 如果spaceEntity是None，那就让它出错


class AIAction181( AIAction ) :
	"""
	将NPC的ID添加到所在副本中作为临时属性，以供
	副本交互之用
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = ""								# 关键字(配置AI时应与程序商定)

	def init( self, section ) :
		"""
		初始化
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )

	def do( self, ai, entity ) :
		"""
		将NPC的ID添加到副本中
		"""
		try:
			spaceEntity = BigWorld.entities[ entity.getCurrentSpaceBase().id ]
		except:
			return
		spaceEntity.setTemp( self.param1, entity.id )

class AIAction182( AIAction ):
	"""
	怪物掉落普通箱子
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" ).split("|")

	def do( self, ai, entity ):
		"""
		"""
		dropItem = []
		for className in self.param1:
			item = g_items.createDynamicItem( int( className ) )
			dropItem.append(item)
		try:
			target = BigWorld.entities[ entity.targetID ]
		except:
			return
		
		# 加入宠物的判断
		if target.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = target.getOwner()
			if owner.etype == "MAILBOX" :
				return
			target = owner.entity
		
		if target.utype != csdefine.ENTITY_TYPE_ROLE:
			return
			
		itemBox = entity.createEntityNearPlanes( "DroppedBox", entity.position, entity.direction, {} )
		itemBox.init( ( target.id, 0 ), dropItem )


class AIAction183( AIAction ) :
	"""
	将指定范围内的NPC设置为当前目标(不对目标发动攻击)
	"""
	def __init__( self ) :
		AIAction.__init__( self )
		self.param1 = 0.0										# 搜索半径
		self.param2 = ""										# NPC ID
		self.param3 = ""										# NPC 类型

	def init( self, section ) :
		"""
		"""
		AIAction.init( self, section )
		self.param1 = section.readFloat( "param1" )
		self.param2 = section.readString( "param2" )
		self.param3 = section.readString( "param3" )

	def do( self, ai, entity ) :
		"""
		"""
		es = entity.entitiesInRangeExt( self.param1, self.param3, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for ent in es:
			if ent.className == self.param2 :
				entity.targetID = ent.id
				break

class AIAction184( AIAction ):
	"""
	NPC喊话（屏幕中央出现），可限定喊话范围
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.channel_msgs = ""
		self.range = 0.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.channel_msgs = section.readString( "param1" )
		self.range = section.readFloat( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		es = entity.entitiesInRangeExt( self.range, "Role", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in es:
			if e.spaceID == entity.spaceID:
				e.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", self.channel_msgs, [])

class AIAction185( AIAction ):
	# 将自身的战利品拥有者作为当前目标
	def do( self, ai, entity ):
		bootyOwnerID = entity.bootyOwner[0]
		if bootyOwnerID:
			entity.setAITargetID( bootyOwnerID )

class AIAction186( AIAction ):
	"""
	给当前目标添加一个任务
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.questID = 0					# 任务ID
		self.timeDelay = 0					# 隔多长时间弹出任务界面

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.questID = section.readInt( "param1" )
		self.timeDelay = section.readInt( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		try:
			player = BigWorld.entities[ entity.targetID ]
		except:
			return
		if player.__class__.__name__ != "Role":
			return
		player.remoteCall( "onAIAddQuest",( self.questID, self.timeDelay, ) )

class AIAction187( AIAction ):
	"""
	改变朝向至指定范围内的指定entity edit by wuxo 2012-1-18
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self._className = 0		#指定的entity的className
		self._range = 0			#一定的范围
		self._type = None		#指定的entity的类型

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self._className = section.readString( "param1" )
		self._range = section.readInt( "param2" )
		self._type = section.readString( "param3" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai	: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai	:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		es = entity.entitiesInRangeExt( self._range, self._type, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in es:
			if hasattr(e,"className") and e.className == self._className :
				entity.openVolatileInfo()
				entity.direction = (0,0,(e.position-entity.position).yaw)
				break

class AIAction188( AIAction ):
	"""
	更改阵营名称
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self._battleCamp = 0	# 阵营名称默认为0，用数字表示

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		if section.readString( "param1" ) == "":
			self._battleCamp = 0
		else:
			self._battleCamp = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai	: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai	:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.battleCamp = self._battleCamp


class AIAction189( AIAction ):
	"""
	靠近攻击目标一定距离
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.distance = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		"""
		target = BigWorld.entities.get( entity.targetID, None )

		distanceBwTargetAndEntity = target.position.distTo( entity.position )

		if target:
			pos = calLinePosition( entity, target, self.distance - distanceBwTargetAndEntity )
			entity.gotoPosition( pos, False )


class AIAction190( AIAction ):
	"""
	远离攻击目标一定距离,通过参数选择采用后退的方式，或转身
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.distance = section.readInt( "param1" )
		self.backTo = bool( section.readString( "param2" ) )		# 是否背向移动


	def do( self, ai, entity ):
		"""
		"""
		target = BigWorld.entities.get( entity.targetID, None )
		if target:
			pos = calLinePosition( entity, target, self.distance )
			entity.gotoPosition( pos, not( self.backTo ) )


class AIAction191( AIAction ):
	"""
	水平朝向攻击目标
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def do( self, ai, entity ):
		"""
		"""
		target = BigWorld.entities.get( entity.targetID, None )
		if target:
			yaw = 0
			if target.position.x < entity.position.x:
				yaw = -1.57
			else:
				yaw = 1.57
			entity.direction = (0,0,yaw)
			entity.planesAllClients( "setFilterYaw", ( yaw, ) )


class AIAction192( AIAction ):
	"""
	与战斗目标保持一定距离走动
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def do( self, ai, entity ):
		"""
		"""
		target = BigWorld.entities.get( entity.targetID, None )
		if target:
			distance = 0.5 * random.randint(-3, 3 )

			pos = calLine2Position( entity, target, distance )
			entity.gotoPosition( pos, False )

class AIAction194( AIAction ):
	"""
	走到玩家周围距离玩家一定范围的某一位置。
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.distance = section.readFloat( "param1" )

	def do( self, ai, entity ):
		"""
		"""
		key = random.choice( groupsCirclePosition.keys() )

		target = BigWorld.entities.get( entity.targetID, None )
		if target:
			pos = None
			count = 0
			while pos is None and count < 50:
				count += 1
				x = target.position.x + groupsCirclePosition[key][0] * self.distance
				y = target.position.y
				z = target.position.z + groupsCirclePosition[key][1] * self.distance

				posList = BigWorld.collide( target.spaceID, ( x, y+10, z ), ( x, y-10, z ) )

				if posList:
					pos = entity.canNavigateTo( posList[0], self.distance )
					if not pos is None:
						if abs( entity.position.distTo( pos )) < self.distance or entity.position.distTo( target.position ) > self.distance * 1.5:
							entity.gotoPosition( pos, False )
							return
				key = random.choice( groupsCirclePosition.keys() )



class AIAction195( AIAction ):
	"""
	记录一下我要走到的位置。
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def do( self, ai, entity ):
		"""
		"""
		entity.setTemp( "AIGotoPosition", entity.queryTemp( "gotoPosition", None ) )


class AIAction196( AIAction ):
	"""
	继续我要到达的之前AI记录的位置。
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def do( self, ai, entity ):
		"""
		"""
		entity.setTemp( "AIGotoPosition", entity.queryTemp( "gotoPosition", None ) )

class AIAction197( AIAction ):
	"""
	给指定的怪物设定列队的编号
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self._startPos = None

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self._className = section.readString( "param1" )
		self._range = section.readFloat( "param2" )

		position = section.readString( "param3" )
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param3 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self._startPos = pos

		self._faceTo = section.readInt( "param4" )

	def do( self, ai, entity ):
		"""
		"""
		index = 0
		es = entity.entitiesInRangeExt( self._range, None, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in es:
			if hasattr(e,"className") and e.className == self._className:
				e.setTemp( "AIGroupInfo", ( index, self._faceTo, self._startPos ))
				index += 1


class AIAction198( AIAction ):
	"""
	走到列队的位置
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self._faceTo = 0				# 是否背向回跑

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self._lineWidth = section.readFloat( "param1" )
		self._lineCount = section.readInt( "param2" )
		if section.readString( "param3" ) == "" or int( section.readString( "param3" ) ) == 0:
			self._faceTo = 0
		else:
			self._faceTo = 1

	def do( self, ai, entity ):
		"""
		faceTo
		-1: 左向右
		1: 右向左
		"""
		info = entity.queryTemp( "AIGroupInfo" )

		startPos = info[2]
		index = info[0]
		faceTo = info[1]

		x = ( index%self._lineCount ) * self._lineWidth * faceTo + startPos[0]
		y = startPos[1]
		z = ( index/self._lineCount ) * self._lineWidth + startPos[2]

		posList = BigWorld.collide( entity.spaceID, ( x, y+10, z ), ( x, y-10, z ) )

		pos = None

		if posList:
			pos = posList[0]
		if pos:
			entity.gotoPosition( pos, self._faceTo )


class AIAction199( AIAction ):
	"""
	沿z轴向攻击目标移动
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.distance = section.readFloat( "param1" )

	def do( self, ai, entity ):
		"""
		"""
		target = BigWorld.entities.get( entity.targetID, None )

		d = self.distance * random.random()

		if target.position.z < entity.position.z:
			d *= -1

		if target:
				pos = ( entity.position.x , entity.position.y, target.position.z + d)
				#pos = entity.canNavigateTo( pos, 0.5 )
				#if not pos is None:
				entity.gotoPosition( pos, False )

class AIAction200( AIAction ):
	"""
	沿x轴向攻击目标移动
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.distance = section.readFloat( "param1" )

	def do( self, ai, entity ):
		"""
		"""
		target = BigWorld.entities.get( entity.targetID, None )

		d = self.distance * random.random()

		if target.position.x < entity.position.x:
			d *= -1


		k = ( target.position.x - entity.position.x )/2


		if target:
				if random.random() > 0.3:
					pos = ( target.position.x + d - k, entity.position.y, entity.position.z + random.choice([-1,1]) * ( 1.0 + random.random()*4.0 ) )
				else:
					pos = ( target.position.x + d, entity.position.y, entity.position.z )
				#pos = entity.canNavigateTo( pos, 0.5 )
				#if not pos is None:
				entity.gotoPosition( pos, False )


class AIAction201( AIAction ):
	"""
	把自己设定为队长
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.captainSign = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		"""
		entity.setTemp( self.captainSign, entity.id )
		print "我是队长:",entity.id


class AIAction202( AIAction ):
	"""
	把AI职责队长的ID分享给周围的怪物
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.captainSign = section.readString( "param1" )
		self.distance = section.readFloat( "param2" )
		self.className = section.readString( "param3" )

	def do( self, ai, entity ):
		"""
		"""
		id = entity.queryTemp( self.captainSign, 0 )

		entities = entity.entitiesInRangeExt( self.distance, "Monster", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for i in entities:
			if self.className == "" or self.className == i.className:
				i.setTemp( self.captainSign, entity.id )


class AIAction203( AIAction ):
	"""
	清理无效的战斗分队队员
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.distance = section.readFloat( "param1" )
		self.aiAttackDutyListSign = section.readString( "param2" )
		self.aiAttackDutySign = section.readString( "param3" )

	def do( self, ai, entity ):
		"""
		"""
		attackEntityIDs = entity.queryTemp( self.aiAttackDutyListSign, [] )
		removeAttackIDs = []

		for id in attackEntityIDs:
			if not BigWorld.entities.has_key( id ):
				removeAttackIDs.append( id )

		for id in removeAttackIDs:
			attackEntityIDs.remove( id )

		es = entity.entitiesInRangeExt( self.distance, 'Monster', entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in es:
			if e.id not in attackEntityIDs:
				e.removeTemp( self.aiAttackDutySign )


class AIAction204( AIAction ):
	"""
	攻击分队补充队员
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.distance = section.readFloat( "param1" )
		self.aiAttackDutyListSign = section.readString( "param2" )
		self.aiAttackDutySign = section.readString( "param3" )
		self.attackCount = section.readInt( "param4" )
		self.className = section.readString( "param5" )

	def do( self, ai, entity ):
		"""
		"""
		attackEntityIDs = entity.queryTemp( self.aiAttackDutyListSign, [] )
		if len( attackEntityIDs ) < self.attackCount:
			entities = entity.entitiesInRangeExt( self.distance, "Monster", entity.position )
			WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
			entities.append( entity )
			random.shuffle( entities )
			for i in entities:
				if i.targetID == entity.targetID and i.id not in attackEntityIDs and ( i.className == self.className or self.className == "" ):
					attackEntityIDs.append( i.id )
					BigWorld.entities[i.id].setTemp( self.aiAttackDutySign,True )
					entity.setTemp( self.aiAttackDutyListSign, attackEntityIDs )
					break;

class AIAction205( AIAction ):
	"""
	踢掉一个战斗分队队员
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.aiAttackDutyListSign = section.readString( "param1" )
		self.aiAttackDutySign = section.readString( "param2" )
		self.attackCount = section.readInt( "param3" )

	def do( self, ai, entity ):
		"""
		"""
		attackEntityIDs = entity.queryTemp( self.aiAttackDutyListSign, [] )
		if len(attackEntityIDs) > ( self.attackCount - 1 ):
			id = attackEntityIDs.pop( random.randint( 0, len(attackEntityIDs)-1 ) )
			entity1 = BigWorld.entities.get( id, None )
			if entity1:
				entity1.removeTemp( self.aiAttackDutySign )


class AIAction206( AIAction ):
	"""
	走到攻击目标的左边或右边
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.distance = section.readFloat( "param1" )


	def do( self, ai, entity ):
		"""
		"""
		target = BigWorld.entities.get( entity.targetID, None )

		if target:
			distance = self.distance * random.choice( [-1,1] )
			pos = ( target.position.x+distance + random.random(), target.position.y-10, target.position.z + random.random() )

			posList = BigWorld.collide( target.spaceID, ( pos[0], pos[1]-10, pos[2] ), ( pos[0], pos[1]+10, pos[2] ), )
			if posList:
				entity.gotoPosition( posList[0], False )


class AIAction207( AIAction ):
	"""
	NPC召唤一个战利品从属于对话玩家的怪物
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.ownerID = 0
		self.position = None
		self.className = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.className = section.readString( "param1" )				# 召唤怪物className

		position = section.readString( "param2" )					# 怪物刷新的位置
		if position and position != '0':
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param2 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.position = pos

	def do( self, ai, entity ):
		if self.position is None:
			position = entity.position + Math.Vector3( random.randint(-2,2), 0,random.randint(-2,2) )
		else:
			position = self.position

		self.ownerID = entity.queryTemp( "talkPlayerID", 0 )		# NPC记录的怪物拥有者ID
		if self.ownerID:
			monster = entity.createObjectNearPlanes( self.className, position, entity.direction, { "firstBruise":1,"bootyOwner":( self.ownerID, 0 ) } )
			monster.setTemp( "ownerID", self.ownerID )
			entity.removeTemp( "talkPlayerID" )
		else:
			DEBUG_MSG( "not find the owner!" )


class AIAction208( AIAction ):
	"""
	设置当前的目标添加为各种拥有者由参数决定是什么拥有者  edit by wuxo 2012-3-6
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		if section.readString( "param1" ) != "":
			self.param1 = section.readInt( "param1" )
		else:
			self.param1 = 1

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai	: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai	:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		tid = entity.targetID
		if tid == 0:
			return
		try:
			ownerEntity = BigWorld.entities[tid]
		except :
			return
		if ownerEntity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) :
			if self.param1 == 1:
				entity.setTemp( "ownerID", tid )
			elif self.param1 == 2:
				entity.bootyOwner = ( tid, 0 )
		elif ownerEntity.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = ownerEntity.getOwner()
			if owner.etype == "MAILBOX" : return
			p = owner.entity
			if self.param1 == 1:
				entity.setTemp( "ownerID", p.id )
			elif self.param1 == 2:
				entity.bootyOwner = ( p.id, 0 )

class AIAction209( AIAction ):
	# 把半径内的一定类型entity抓到自己身边( 短距离 )
	def __init__( self ):
		AIAction.__init__( self )
		self.radius = 0
		self.entityNames = []

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.radius = section.readInt( "param1" )
		self.entityNames = section.readString( "param2" ).split( ";" )

	def do( self, ai, entity ):
		catchEntities = []
		for entityName in self.entityNames:
			catchEntities.extend( entity.entitiesInRangeExt( self.radius, entityName, entity.position ) )
			for e in catchEntities:
				if entity.queryRelation( e ) == csdefine.RELATION_FRIEND:
					catchEntities.remove( e )
					break

		for catchEntity in catchEntities:
			catchEntity.position = entity.position

class AIAction210( AIAction ):
	"""
	NPC设置自己只对战利品拥有者可见
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai	: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai	:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if not entity.hasFlag( csdefine.ENTITY_FLAG_UNVISIBLE ):	# 如果没有不可见标记，则返回
			return 
		bootyOwner = entity.bootyOwner
		if bootyOwner[1] != 0:										# 有队伍
			bootyers = entity.searchTeamMember( bootyOwner[1], Const.TEAM_GAIN_EXP_RANGE )
			if len( bootyers ) == 0:
				return

			if not entity.queryCombatRelationIns( bootyOwner[1] ):
				entity.addCombatRelationIns( csdefine.RELATION_DYNAMIC_TEAM_ANTAGONIZE, bootyOwner[1] )
			entity.ownerVisibleInfos = bootyOwner
		elif bootyOwner[0] != 0:										# 没队伍
			if not BigWorld.entities.has_key( bootyOwner[0] ):			# 处理玩家可能掉线或者退出游戏的情况
				WARNING_MSG( "monster( className %s id %i )'s bootyOwner %i maybe die"  % ( entity.className, entity.id, bootyOwner[0]) )
				entity.ownerVisibleInfos = (0, 0)
				if entity.queryCombatRelationIns( bootyOwner[0] ):
					entity.removeCombatRelationIns(csdefine.RELATION_DYNAMIC_PRESONAL_ANTAGONIZE_ID, bootyOwner[0] )
				return
				
			if not entity.queryCombatRelationIns( bootyOwner[0] ):
				entity.addCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_ANTAGONIZE_ID, bootyOwner[0] )
			entity.ownerVisibleInfos = bootyOwner
		else:
			WARNING_MSG( "monster( className %s id %i ) not have bootyOwner" % ( entity.className, entity.id ) )

class AIAction211( AIAction ):
	"""
	NPC通知任务拥有者任务失败
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0
		self.param2 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )
		self.param2 = section.readInt( "param2" )

	def do( self, ai, entity ):
		bootyOwner = entity.getBootyOwner()
		if bootyOwner[1] != 0:
			bootyers = entity.searchTeamMember( bootyOwner[1], Const.TEAM_GAIN_EXP_RANGE )
			if len( bootyers ) == 0:
				return
			for teamMember in bootyers:
				teamMember.questTaskFailed( self.param1, self.param2 )
		elif bootyOwner[0] != 0:
			player = BigWorld.entities[ bootyOwner[0] ]
			player.questTaskFailed( self.param1, self.param2 )

class AIAction212( AIAction ):
	"""
	针对可控制的刷新点SpawnPointControl而做的AI控制
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		"""
		spaceBase = entity.getCurrentSpaceBase()
		if spaceBase is None: return
		spaceBase.destroySpawnPointControl()

class AIAction213( AIAction ):
	"""
	寻找指定范围内特定类型目标，目标血量低于指定值，对其施放指定技能，可以多次释放（区别于AIAction80）
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0.0
		self.param2 = ""
		self.param3 = 0
		self.param4 = 0.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readFloat( "param1" )			# 范围
		self.param2 = section.readString( "param2" )		# className
		self.param3 = section.readInt64( "param3" ) * 1000	# 技能编号
		self.param4 = section.readFloat( "param4" ) / 100	# 血量限制

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		target = None
		monsterList = entity.entitiesInRangeExt( self.param1, "Monster", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in monsterList:
			if e.className == self.param2:
				target = e
				break
		if target and float(target.HP)/ float(target.HP_Max)  <= self.param4:
			entity.spellTarget( self.param3 + entity.level, target.id )

class AIAction214( AIAction ):
	"""
	召唤怪物，被召唤的怪物和执行此AI的entity有同样的拥有者，且被召唤的怪物仅属于拥有者（们）可见
	"""
	def __init__( self ) :
		AIAction.__init__( self )
		self.className = None					# 创建的Entity的className
		self.position = None					# 创建的Entity的位置
		self.MonsNumber = None					# 创建的Entity的数量
		self.direction = None					# 创建的Entity的朝向

	def init( self, section ) :
		"""
		"""
		AIAction.init( self, section )
		self.className = section.readString( "param1" )
		self.MonsNumber = section.readInt( "param3" )

		position = section.readString( "param2" )
		if position and position != '0':
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param2 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.position = pos

		direction = section.readString( "param4" )
		if direction and direction != '0':
			dir = vector3TypeConvert( direction )
			if dir is None:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param4" % ( self.getAIDataID(), self.getID(), direction ) )
			else:
				self.direction = dir

	def do( self, ai, entity ) :
		"""
		"""
		if self.position is None:
			self.position = entity.position
		if self.direction is None:
			self.direction = entity.direction
			
		bootyOwner = entity.getBootyOwner()
		dict = {}
		dict[ "spawnPos" ] = tuple( self.position )
		dict[ "bootyOwner" ] = ( bootyOwner[0], bootyOwner[1] )

		for i in xrange( self.MonsNumber ):
			monster = entity.createObjectNearPlanes( self.className, self.position, self.direction, dict )
			monster.addFlag( csdefine.ENTITY_FLAG_UNVISIBLE )				# 添加不可见标签
			monster.firstBruise = 1

			if monster is None :
				ERROR_MSG( "Create entity false in ai action214!" )
				break

			tempEnemyID = []
			monster.setTemp( "ownerID", entity.queryTemp("ownerID", 0) )

			if bootyOwner != ( 0, 0 ):					# 有拥有者
				for enemyID in entity.enemyList:
					tempEnemyID.append( enemyID )
			else:
				ERROR_MSG( "monster %s not have bootyOwner"% entity.className )

			monster.setTemp( "enemyIDs", tempEnemyID )
			monster.ownerVisibleInfos = bootyOwner


class AIAction215( AIAction ):
	"""
	盘古守护，排兵布阵专用AI
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		ownerEntity = entity.getOwner()
		if hasattr( ownerEntity, "cell" ):
			return

		if entity.queryTemp( "ownerLastPos",0 ) == ownerEntity.position and entity.queryTemp( "ownerLastDir", 0 ) == ownerEntity.direction:
			return

		entity.setTemp( "ownerLastPos" , Math.Vector3( ownerEntity.position) )
		entity.setTemp( "ownerLastDir", Math.Vector3( ownerEntity.direction ) )
		pos = Math.Vector3( ownerEntity.position )
		onwerAngle = Math.Vector3( ownerEntity.direction).z / math.pi * 180
		angle = entity.toOwnerAngle + onwerAngle
		pos.x += math.sin( angle*math.pi/180 ) * entity.toOwnerDis + random.randint( -1, 1)
		pos.y = entity.position.y
		pos.z += math.cos( angle*math.pi/180 ) * entity.toOwnerDis + random.randint( -1, 1)
		if abs(pos.x - entity.position.x) > 0.5 or  abs(pos.z - entity.position.z) > 0.5:
			posList = BigWorld.collide( entity.spaceID, ( pos.x, pos.y+10, pos.z ), ( pos.x, pos.y-10, pos.z ) )
			if posList == None:
				pos = entity.position
			else:
				pos = posList[0]

			entity.gotoPosition( pos )


class AIAction216( AIAction ):
	"""
	配合214一起使用,使得召唤出来的怪物，会攻击适当的玩家
	"""
	def do( self, ai, entity ):
		"""
		"""
		entity.bootyOwner = entity.ownerVisibleInfos
		owner = BigWorld.entities.get( entity.bootyOwner[0], None )
		if owner:
			g_fightMgr.buildEnemyRelation( entity, owner )	# 让拥有者最先加入战斗列表
		g_fightMgr.buildGroupEnemyRelationByIDs( entity, entity.queryTemp("enemyIDs",[]) )


class AIAction217( AIAction ):
	"""
	把当前目标设置为自己的主人（限定于有主人的怪物使用）
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.entityType = "Role"

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		if section.readString( "param1" ) != "":
			self.entityType = section.readString( "param1" )						# EntityType

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai	: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai	:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		tid = entity.aiTargetID
		if tid == 0:
			return
		ownerEntity = BigWorld.entities.get( tid )
		if ownerEntity:
			if ownerEntity.__class__.__name__ == self.entityType :
				entity.setOwner( ownerEntity.base )


class AIAction218( AIAction ):
	"""
	根据排队指导人员的当前目标的位置，设置朝向
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.pos = None


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		position = section.readString( "param1" )
		if position:
			pos = vector3TypeConvert( position )
			if not pos:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param1 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.pos = pos

		self.className 	= section.readString( "param2" )
		self.range 		= section.readFloat( "param3" )
		self.width 		= section.readInt( "param4" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai	: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai	:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		targetPos = None
		es = entity.entitiesInRangeExt( self.range, "Monster", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for i in es:
			if i.className == self.className:
				target = BigWorld.entities.get(i.targetID)
				if target:
					targetPos = target.position
					break
		entity.openVolatileInfo()
		if targetPos:
			if targetPos[0] < self.pos[0]:
				if targetPos[2] < self.pos[2]:
					entity.direction = ( 0, 0, -2.35 )
				elif targetPos[2] > self.pos[2] + self.width:
					entity.direction = ( 0, 0, -0.785 )
				else:
					entity.direction = ( 0, 0, -1.57 )
			elif targetPos[0] > self.pos[0] + self.width:
				if targetPos[2] < self.pos[2]:
					entity.direction = ( 0, 0, 2.35 )
				elif targetPos[2] > self.pos[2] + self.width:
					entity.direction = ( 0, 0, 0.785 )
				else:
					entity.direction = ( 0, 0, 1.57 )
			else:
				if targetPos[2] < self.pos[2]:
					entity.direction = ( 0, 0, 3.14 )
				else:
					entity.direction = ( 0, 0, 0 )

class AIAction219( AIAction ):
	"""
	随机选取主人的敌人作为攻击目标（守护专用）
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		ownerEntity = entity.getOwner()
		if hasattr( ownerEntity, "cell" ):
			return

		enemyList = ownerEntity.enemyList
		if enemyList.has_key( 0 ):
			enemyList.pop( 0 )
		enemyAmount = len( enemyList )
		if not enemyAmount:
			return

		callPGDict = ownerEntity.queryTemp( "callPGDict", {} )
		callPGList = []
		for id in callPGDict.values():
			callPGList.extend( id )

		for index, id in enumerate( callPGList ):
			if entity.id == id:
				enemyID = enemyList.keys()[ index % enemyAmount ]
				if entity.targetID != enemyID:
					entity.setAITargetID( enemyID )
					entity.changeAttackTarget( enemyID )
				break

class AIAction220( AIAction ):
	"""
	改变自身朝向为主人朝向
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		ownerEntity = entity.getOwner()
		if hasattr( ownerEntity, "cell" ):
			return

		entity.openVolatileInfo()
		entity.direction = ownerEntity.direction

class AIAction221( AIAction ):
	"""
	NPC发言,仅聊天泡泡可见
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if len( self.param1 ) > 0:
			entity.sayBupple( self.param1 )

class AIAction222( AIAction ):
	"""
	怪物在周围一个给定半径的圆移动
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.range = section.readFloat( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if entity.actionSign( csdefine.ACTION_FORBID_MOVE ):
			DEBUG_MSG( "I cannot  move!" )
			return
		moveOut( entity, entity, self.range, self.range )

class AIAction223( AIAction ):
	"""
	英雄联盟NPC选择巡逻路线专用AI
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		spaceBase = entity.getCurrentSpaceBase()
		if spaceBase is None: return
		spaceEntity = BigWorld.entities.get( spaceBase.id )
		spaceEntity.monster_choosePatrolList( entity.id )

class AIAction224( AIAction ):
	"""
	传送点entity范围内的玩家传送到
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.position = None
		self.direction = None

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.range = section.readFloat( "param1" )				# 传送点范围
		self.spaceName = section.readString( "param2" )			# 传送至某个地图

		position = section.readString( "param3" )				# 传送至某个位置
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param3 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.position = pos

		self.lifeTime = section.readFloat( "param4" )			# 传送点销毁自身的时间
		direction = section.readString( "param5" )				# 传送位置朝向
		if direction and direction != '0':
			dir = vector3TypeConvert( direction )
			if dir is None:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param4" % ( self.getAIDataID(), self.getID(), direction ) )
			else:
				self.direction = dir

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if self.direction is None:
			self.direction = ( 0, 0, 0 )
		es = entity.entitiesInRangeExt( self.range, "Role", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in es:
			e.gotoSpace( self.spaceName, self.position, self.direction )
		entity.addTimer( self.lifeTime, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )

class AIAction225( AIAction ):
	"""
	通知星际副本多少秒后传送玩家出副本
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.leaveTime = 0.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.leaveTime = section.readFloat( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		spaceBase = entity.getCurrentSpaceBase()
		if spaceBase is None:	return
		spaceEntity = BigWorld.entities[ spaceBase.id ]
		spaceEntity.infoSpaceCopyStar( self.leaveTime )					# 通知星际副本调用函数

class AIAction226( AIAction ):
	"""
	寻找距离该怪物最近的巡逻点，并从那个点开始执行巡逻
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.graphID = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.graphID = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if self.graphID == "":
			entity.doPatrol()
			return
		patrolList = BigWorld.PatrolPath( self.graphID )
		if not patrolList or not patrolList.isReady():
			ERROR_MSG( "Patrol(%s) unWorked in %s. it's not ready or not have such graphID!"%(self.graphID, entity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )) )
		else:
			patrolPathNode, position = patrolList.nearestNode( entity.position )
			entity.doPatrol( patrolPathNode, patrolList  )


class AIAction227( AIAction ):
	"""
	怪物散开
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self._rangeMin = section.readFloat( "param1" )
		self._rangeMax = section.readFloat( "param2" )
		self._bodySize = section.readFloat( "param3" )
		self._moveMax  = section.readFloat( "param4" )

	def do( self, ai, entity ):
		"""
		"""
		dstEntity = BigWorld.entities.get( entity.targetID )
		if not dstEntity:
			return
			
		if entity.actionSign( csdefine.ACTION_FORBID_MOVE ):
			DEBUG_MSG( "I cannot  move!" )
			return
			
		if dstEntity.position.distTo( entity.position ) < self._rangeMin:
			if moveOut( entity, dstEntity, random.random() * (self._rangeMax - self._rangeMin) + self._rangeMin, self._moveMax ):
				return
			return

		es = entity.entitiesInRangeExt( self._bodySize, "Monster", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in es:
			if not e.isMoving() and isinstance( e, CombatUnit ):
				# 范围内有一些没有移动的entity，自己主动离开，随机移动到一个位置
				if moveOut( entity, dstEntity, random.random() * (self._rangeMax - self._rangeMin) + self._rangeMin, self._moveMax ):
					return


class AIAction228( AIAction ):
	"""
	增加副本Boss的击杀数量
	"""
	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		spaceBase = entity.getCurrentSpaceBase()
		if hasattr( spaceBase, "incBossesKilled" ) :
			spaceBase.incBossesKilled()
		else :
			ERROR_MSG( "current spacebase dosn't support recording boss killed. entity id: %i" % entity.id )

class AIAction229( AIAction ):
	"""
	设置副本Raid完成标记
	"""
	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		spaceBase = entity.getCurrentSpaceBase()
		if hasattr( spaceBase, "setRaidFinish" ) :
			spaceBase.setRaidFinish( True )
		else :
			ERROR_MSG( "current spacebase dosn't support recording raid finished. entity id: %i" % entity.id )

class AIAction230( AIAction ):
	"""
	选取伤害列表中某一类型的className的entity，以其中第一个作为当前目标(AI目标)
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.entityType = "Monster"
		self.className = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		if section.readString( "param1" ):
			self.entityType = section.readString( "param1" )
		self.className = section.readString( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		for id in entity.damageList:
			e = BigWorld.entities.get( id )
			if e and e.__class__.__name__ == self.entityType:
				if self.className and e.className != self.className:	# className为空则只需满足该Entity类型
					continue
				entity.setAITargetID( id )
				break 

class AIAction231( AIAction ) :
	"""
	地图脚本必须有定义方法：onYXLMCopyBossCreated
	entity和副本交互，通知副本某怪物已经刷出
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.signType = 1

	def init( self, section ) :
		"""
		初始化
		"""
		AIAction.init( self, section )
		if section.readInt( "param1" ):
			self.signType = section.readInt( "param1" )					# signType 显示在小地图的标志类型

	def do( self, ai, entity ):
		try:
			spaceEntity = BigWorld.entities[ entity.getCurrentSpaceBase().id ]
		except :
			return
		spaceEntity.onYXLMCopyBossCreated( entity.id, entity.className, entity.spawnPos, self.signType  )	# 如果spaceEntity是None，那就让它出错

class AIAction232( AIAction ) :
	"""
	地图脚本必须有定义方法：onYXLMCopyBossDied
	entity和副本交互，通知副本某怪物已经死亡，一般用在死亡事件里面
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ) :
		"""
		初始化
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ) :
		try:
			spaceEntity = BigWorld.entities[ entity.getCurrentSpaceBase().id ]
		except KeyError, errStr :
			EXCEHOOK_MSG( errStr )
			return
		spaceEntity.onYXLMCopyBossDied( entity.id, entity.className, entity.spawnPos, entity.position )

class AIAction233( AIAction ):
	"""
	在指定位置指定范围内召唤若干指定等级差的怪物，被召唤的怪物复制召唤者的战斗列表和战利品拥有者
	"""
	def __init__( self ) :
		AIAction.__init__( self )
		self.className = ""						# 创建的Entity的className
		self.amount = 1							# 创建的Entity的数量
		self.position = None					# 创建的Entity的位置
		self.range = 0							# 随机范围
		self.levelOffset = 0					# 等级差
		self.copyBootyOwner = 1					# 是否复制战利品拥有者
		self.copyEnemyList = 1					# 是否复制敌人列表
		self.maxHeightDiff = 3.0				# 刷怪位置与召唤者位置的高度差最大值，超过此值，取召唤者位置为刷怪位置 CSOL-230

	def init( self, section ) :
		"""
		"""
		AIAction.init( self, section )
		nameAndAmount = section.readString( "param1" ).split( "|" )
		self.className = nameAndAmount[0]
		if len( nameAndAmount ) == 2:
			self.amount = int( nameAndAmount[1] )
		self.range = section.readInt( "param3" )
		if section.readString( "param4" ):
			self.levelOffset = section.readInt( "param4")

		if section.readString( "param5" ):
			copyBootyAndEnemy =  section.readString( "param5" ).split( "|" )
			self.copyBootyOwner = int( copyBootyAndEnemy[0] )
			if len( copyBootyAndEnemy ) == 2:
				self.copyEnemyList = int( copyBootyAndEnemy[1] )
		
		position = section.readString( "param2" )
		if position and position != '0':
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param2 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.position = pos

	def do( self, ai, entity ) :
		"""
		"""
		try:
			spaceBase = BigWorld.cellAppData["spaceID.%i" % entity.spaceID]
			spaceEntity = BigWorld.entities[ spaceBase.id ]		# 找到副本
		except:
			DEBUG_MSG( "not find the spaceEntity!" )
			return
			
		pos = self.position
		if self.position is None:
			pos = tuple( entity.position )
		
		dict = {}
		dict[ "level" ] = entity.level + self.levelOffset
		
		for i in xrange( self.amount ):
			position = ( pos[0] + random.randint( -self.range, self.range ), pos[1], pos[2] + random.randint( -self.range, self.range ) )
			#位置增加碰撞
			collPos = csarithmetic.getCollidePoint( entity.spaceID, pos, Math.Vector3( position ) )
			endDstPos = csarithmetic.getCollidePoint( entity.spaceID, Math.Vector3( collPos[0],collPos[1] + 10,collPos[2]), Math.Vector3( collPos[0],collPos[1] - 10,collPos[2]) )
			if abs(endDstPos.y - entity.position.y) >  self.maxHeightDiff:
				endDstPos = tuple( entity.position )
			dict[ "spawnPos" ] =  tuple( endDstPos )
			monster = entity.createObjectNearPlanes( self.className, endDstPos, entity.direction, dict )
			if monster is None :
				ERROR_MSG( "Create entity false in AiAction233!" )
				break
			
			if self.copyBootyOwner:
				monster.firstBruise = 1
				monster.bootyOwner = entity.bootyOwner
			if self.copyEnemyList:
				g_fightMgr.buildGroupEnemyRelationByIDs( monster, entity.enemyList.keys() )


class AIAction234( AIAction ) :
	"""
	地图脚本必须有定义方法：updateYXLMCopyBossPos
	entity和副本交互，更新Boss在客户端的位置信息显示
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ) :
		"""
		初始化
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		spaceBase = entity.getCurrentSpaceBase()
		if spaceBase is None:
			return 
		spaceEntity = BigWorld.entities.get( spaceBase.id )
		spaceEntity.updateYXLMCopyBossPos( entity.id, entity.className, entity.position  )	# 如果spaceEntity是None，那就让它出错

class AIAction235( AIAction ):
	"""
	选取一定范围内特定类型的离自己最近的的怪物作为当前目标(AI目标)
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.entityType = "Monster"
		self.classNames = []
		self.range = 0.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		if section.readString( "param1" ):
			self.entityType = section.readString( "param1" )					# EntityType
		self.classNames = section.readString( "param2" ).split( "|" )			# className 列表
		self.range = section.readFloat( "param3" )								# 范围

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		eid = 0
		distance = 100.0
		monsterList = entity.entitiesInRangeExt( self.range, self.entityType, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in monsterList:													# 选择最近目标的ID
			if not self.classNames or ( self.classNames and  e.className in self.classNames ):
				dis = csarithmetic.distancePP3( e.position, entity.position )
				if distance > dis:
					eid = e.id
					distance = dis
		
		e = BigWorld.entities.get( eid )
		if e and e.state != csdefine.ENTITY_STATE_DEAD and entity.targetID != eid :
			entity.setAITargetID( eid )											# 改变AI目标为最近的目标
			
class AIAction236( AIAction ) :
	"""
	entity跟随玩家
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ) :
		"""
		初始化
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		dstEntity = BigWorld.entities.get( entity.targetID )
		if dstEntity is None:
			return
		entity.gotoPosition( dstEntity.position )
		entity.spawnPos = tuple( entity.position )

class AIAction237( AIAction ):
	"""
	对AI目标使用技能
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.skillID = section.readInt64( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		target = BigWorld.entities.get( entity.aiTargetID )		# 攻击判断
		if not target:
			ERROR_MSG( " AIData %i use skill %i error, can't get ( %i %s )'s aiTargetID %i" % ( self.getAIDataID(), self.skillID, entity.id, entity.className, entity.aiTargetID ) )
			return 

		try:
			spell = g_skills[ self.skillID ]					# 获取配置的攻击技能
		except:
			ERROR_MSG( "AIDAta %i get skill error, check whether %i is exist." %  ( self.getAIDataID(), self.skillID ) )
			return
			
		if checkAndMove( entity ):								# 用于解决一堆怪物追击同一个目标时重叠在一起的问题
			return
		state = entity.spellTarget( self.skillID,  entity.aiTargetID )

		if entity.state == csdefine.ENTITY_STATE_DEAD:			# 有可能被反射致死
			return

		if state != csstatus.SKILL_GO_ON:
			# 其它错误
			INFO_MSG( "%i: skill %i use state = %i." % ( entity.id, self.skillID, state ) )

class AIAction238( AIAction ):
	"""
	将自己的敌人列表复制给周围的某些NPC
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.range = section.readInt( "param1" )				# 搜索范围
		self.npcClassNameList = section.readString( "param2" ).split("|")			# npc className list

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		es = entity.entitiesInRangeExt( self.range, None, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in es:
			if e.className in self.npcClassNameList:
				g_fightMgr.buildGroupEnemyRelationByIDs( e, entity.enemyList.keys() )


class AIAction239( AIAction ):
	"""
	怪物移动到攻击目标周围一定范围内
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.range = 0.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.range = section.readFloat( "param1" )					# 与攻击目标的距离

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		try:
			target = BigWorld.entities[entity.targetID]
		except:
			ERROR_MSG( "AIData %i:( %i, %s )'s targetID %i is not exist!" % (  self.getAIDataID(), entity.id, entity.className, entity.targetID ))
			return 
			
		count = 10
		pos = None
		for tryNum in xrange( count ):
			a = self.range + ( entity.getBoundingBox().z + target.getBoundingBox().z ) / 3.0
			# 选取半圆周上的点
			yaw = ( entity.position - target.position ).yaw
			angle = random.uniform( yaw - math.pi/2, yaw + math.pi / 2 )
			direction = Math.Vector3( math.sin( angle ), 0.0, math.cos( angle ) )
			direction.normalise()					# 将向量单位化
			pos = Math.Vector3( target.position ) + a * direction

			posList = BigWorld.collide( entity.spaceID, ( pos.x, pos.y+10, pos.z ), ( pos.x, pos.y-10, pos.z ) )
			if not posList:
				continue
			pos = posList[0]
			entity.gotoPosition( pos )
			return 

class AIAction240( AIAction ):
	"""
	NPC跟随对话者

	保持距离 既NPC始终与拥有者所保持的一段距离.
	"""
	def __init__( self ):
		AIAction.__init__( self )
		
	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readFloat( "param1" )	# 距离

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		fid = entity.queryTemp( "talkFollowID", 0 )
		if fid:
			if BigWorld.entities.has_key( fid ):
				followEntity = BigWorld.entities[ fid ]
			else:
				entity.removeTemp( "talkFollowID" )
				entity.getScript().doGoBack( entity )
				return
			distance = csarithmetic.distancePP3( followEntity.position, entity.position )
			if int( distance ) > self.param1:
				entity.removeTemp( "talkFollowID" )
				entity.getScript().doGoBack( entity )
				return
			if entity.actionSign( csdefine.ACTION_FORBID_MOVE ):
				DEBUG_MSG( "im cannot the move!" )
				entity.stopMoving()
				return
			entity.chaseTarget( followEntity, True )
		else:
			ERROR_MSG( "can not find the follow target!" )

class AIAction241( AIAction ):
	"""
	移除NPC对话跟随标志
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.removeTemp( "talkFollowID" )

class AIAction242( AIAction ):
	"""
	靠近则完成任务
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.__questID	 		= section.readInt( "param1" )
		self.__taskIndex	 	= section.readInt( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		fid = entity.queryTemp( "talkFollowID", 0 )
		if BigWorld.entities.has_key( fid ):
			followEntity = BigWorld.entities[ fid ]
			followEntity.questTaskIncreaseState( self.__questID, self.__taskIndex )

class AIAction243( AIAction ) :
	"""
	entity和副本交互，通知副本某怪物已经刷出
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ) :
		"""
		初始化
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		spaceBase = entity.getCurrentSpaceBase()
		if BigWorld.entities.has_key( spaceBase.id ):
			BigWorld.entities[ spaceBase.id ].onAINotifySpaceCreated( entity.className, entity )
		else:
			spaceBase.cell.onAINotifySpaceCreated( entity.className, entity )

class AIAction244( AIAction ) :
	"""
	entity和副本交互，通知副本某怪物已经死亡，一般用在死亡事件里面
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ) :
		"""
		初始化
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ) :
		spaceBase = entity.getCurrentSpaceBase()
		if BigWorld.entities.has_key( spaceBase.id ):
			BigWorld.entities[ spaceBase.id ].onAINotifySpaceDied( entity.className, entity )
		else:
			spaceBase.cell.onAINotifySpaceDied( entity.className, entity )

class AIAction245( AIAction ):
	"""
	NPC/MONSTER让自己死亡
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.die( 0 )

class AIAction246( AIAction ):
	"""
	NPC喊话（屏幕中央出现），可限定喊话范围
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.channel_msgs = []
		self.range = 0.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		msg_string = section.readString( "param1" )
		for msgInf in msg_string.split( ";" ):
			r, msg, sound = msgInf.split( "|" )
			self.channel_msgs.append( ( int(r), msg, sound ) )
			
		self.range = section.readFloat( "param2" )

	def randomGetMsg( self ):
		for msgInf in self.channel_msgs:
			if msgInf[0] > random.randint( 1, 100 ):
				return msgInf[ 1:3 ]
		
		return self.channel_msgs[0][ 1:3 ]
	
	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		msg, soundID =self.randomGetMsg()
		entity.say( msg )
		entity.planesAllClients( "onMakeASound", ( soundID, 0 ) )
				
class AIAction247( AIAction ) :
	"""
	在副本中的几个给定点中随机选一个放陷阱
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.lifetime = 0				# 陷阱销毁时间
		self.repeattime = 0				# 循环伤害时间
		self.radius = 0.0				# 陷阱半径
		self.enterSpell = 0				
		self.leaveSpell = 0				
		self.destroySpell = 0			
		self.enter_Spell = 0				# 进入陷阱施放的技能
		self.leave_Spell = 0				# 离开陷阱施放的技能
		self.destroy_Spell = 0			# 陷阱死亡时释放的技能
		self.modelNumber =  ""			# 陷阱对应的模型(带光效的)
		self.isDisposable = False		# 是否一次性陷阱（即触发一次就销毁）
		self.position = None

	def init( self, section ) :
		"""
		初始化
		"""
		AIAction.init( self, section )
		timeStr = section.readString( "param1" )
		timeList = [int( t ) for t in timeStr.split(";") ]
		self.lifetime = timeList[0]
		if len( timeList ) >= 2:
			self.repeattime = timeList[1]
			
		param2 = section.readString( "param2" ).split(";")
		
		self.radius = float( param2[0] )
		self.modelNumber = section.readString( "param3" ).split(";")[0] 
		self.casterMaxDistanceLife = int( param2[1] )
		self.positionList = section.readString( "param4" ).split(";")

		if len( section.readString( "param5" ) ) > 0:
			self.enterSpell, self.leaveSpell, self.destroySpell, self.isDisposable = [ int(s) for s in section.readString( "param5" ).split(";") ]

	def do( self, ai, entity ):
		"""
		通知副本情况有变
		"""
		if self.enterSpell != 0 and self.enterSpell != 1:
			self.enter_Spell = self.enterSpell * 1000 + entity.getLevel()
		if self.leaveSpell != 0 and self.leaveSpell != 1:
			self.leave_Spell = self.leaveSpell * 1000 + entity.getLevel()
		if self.destroySpell != 0 and self.destroySpell != 1:
			self.destroy_Spell = self.destroySpell * 1000 + entity.getLevel()
		dict = { "radius" : self.radius, \
				"enterSpell" : self.enter_Spell, \
				"leaveSpell" : self.leave_Spell, \
				"destroySpell" : self.destroy_Spell, \
				"modelNumber" : self.modelNumber, \
				"casterMaxDistanceLife" : self.casterMaxDistanceLife, \
				"isDisposable" : self.isDisposable, \
				"lifetime" : self.lifetime, \
				"repeattime" : self.repeattime, \
				"casterID" : entity.id }
		positionIndex = random.randint( 0, len( self.positionList ) - 1 )
		position = self.positionList[ positionIndex ]
		if position and position != '0':
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param2 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.position = pos
		pos = self.position
		if self.position is None:
			pos = tuple( entity.position )

		entity.createEntityNearPlanes( "AreaRestrictTransducer", pos, (0, 0, 0), dict )

class AIAction248( AIAction ):
	"""
	npc_ownerBase完成任务
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.__questID	 		= section.readInt( "param1" )
		self.__taskIndex	 	= section.readInt( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		fid = entity.getOwner().id
		if BigWorld.entities.has_key( fid ):
			e = BigWorld.entities[ fid ]
			e.questTaskIncreaseState( self.__questID, self.__taskIndex )

class AIAction249( AIAction ):
	"""
	召唤怪物
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0
		self.param2 = ""
		self.param3 = 0.0


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )	# 召唤怪物数量
		self.param2 = section.readString( "param2" )	# 召唤怪物className
		self.param3 = section.readFloat( "param3" )		# entity面朝方向一定距离

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		try:
			spaceBase = BigWorld.cellAppData["spaceID.%i" % entity.spaceID]
			spaceEntity = BigWorld.entities[ spaceBase.id ]		# 找到副本
		except:
			DEBUG_MSG( "not find the spaceEntity!" )
			return

		if self.param3 == 0.0:
			position = entity.position + Math.Vector3( random.randint(-2,2), 0,random.randint(-2,2) )
		else:
			yaw = entity.yaw
			direction = Math.Vector3( math.sin(yaw), 0, math.cos(yaw) )
			position = self.param3 * direction + Math.Vector3( entity.position )
			posList = BigWorld.collide( entity.spaceID, ( position.x, position.y+10, position.z ), ( position.x, position.y-10, position.z ) )
			if posList != None:
				position = posList[0]
		
		newDict = { "spawnPos": tuple(position), "level" : entity.level }
		for i in xrange( self.param1 ):
			monster = entity.createObjectNearPlanes( str(self.param2), position, entity.direction, newDict )
			# 副本记录召唤出的怪物id
			tempCallMonsterIDs = spaceEntity.queryTemp( "tempCallMonsterIDs", [] )		# 取得副本记录召唤出的怪物id列表
			tempCallMonsterIDs.append( monster.id )
			spaceEntity.setTemp( "tempCallMonsterIDs", tempCallMonsterIDs )
			enemyList = entity.enemyList
			if len( enemyList ):
				ownerID = enemyList.keys()[0]
				monster.setTemp( "ownerID", ownerID )
			g_fightMgr.buildGroupEnemyRelationByIDs( monster, enemyList.keys() )

class AIAction250( AIAction ):
	"""
	播放入场动作
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.isFirstHide 		= section.readInt( "param1" )
		self.isMovedAction 		= section.readInt( "param2" )
		self.preActionTime 		= section.readFloat( "param3" )
		self.jumpPointType 		= section.readInt( "param4" )
		self.jumpPoint 			= section.readString( "param5" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if not self.isFirstHide or ( self.isFirstHide and entity.firstHide ):
			target_pos = entity.getDstPos( self.jumpPointType, self.jumpPoint )
			if target_pos:
				time = entity.doPreEvent( target_pos, self.isMovedAction, self.preActionTime )
				entity.addTimer( time, 0, ECBExtend.PRE_REMOVE_FLAG )

class AIAction251( AIAction ):
	"""
	NPC喊话（屏幕中央出现），可限定喊话范围, 支持给敌人和朋友发不同消息
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.channel_msgs_friend = ""
		self.channel_msgs_enemy = ""
		self.range = 0.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.channel_msgs_friend = section.readString( "param1" )
		self.channel_msgs_enemy = section.readString( "param2" )
		self.range = section.readFloat( "param3" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		es = entity.entitiesInRangeExt( self.range, "Role", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in es:
			if e.spaceID == entity.spaceID:
				if entity.queryRelation( e ) == csdefine.RELATION_FRIEND:
					e.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", self.channel_msgs_friend, [])
				else:
					e.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", self.channel_msgs_enemy, [])
					
class AIAction252( AIAction ):
	"""
	召唤怪物同时销毁自身，销毁前出生点置空
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		monster = entity.createObjectNearPlanes( self.param1, entity.position, entity.direction, {"spawnPos": tuple(entity.position ), "level": entity.level, "spawnMB": entity.spawnMB } )
		entity.resetEnemyList()
		entity.spawnMB = None
		entity.addTimer( 0.2, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )
		
class AIAction253( AIAction ) :
	"""
	地图脚本必须有定义方法：onYXLMMonsterGetDamage
	英雄联盟小地图防御塔、基地受到一定程度伤害时图标闪烁
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.flashTime = 0		#闪烁时间

	def init( self, section ) :
		"""
		初始化
		"""
		AIAction.init( self, section )
		if section.readInt( "param1" ):
			self.flashTime = section.readInt( "param1" )					# signType 显示在小地图的标志类型

	def do( self, ai, entity ) :
		spaceBase = entity.getCurrentSpaceBase()
		if spaceBase is None:
			return
		spaceEntity = BigWorld.entities[ spaceBase.id ]
		spaceEntity.onYXLMMonsterGetDamage( entity.id, self.flashTime )

class AIAction254( AIAction ) :
	"""
	下次AI行为在几秒后执行
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.thinkSpeed = 1.0		#闪烁时间

	def init( self, section ) :
		"""
		初始化
		"""
		AIAction.init( self, section )
		self.thinkSpeed = section.readFloat( "param1" )					# signType 显示在小地图的标志类型

	def do( self, ai, entity ) :
		entity.thinkSpeed = self.thinkSpeed


class AIAction255( AIAction ) :
	"""
	马上执行AI心跳
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def do( self, ai, entity ) :
		entity.think(0.1)

class AIAction256( AIAction ) :
	"""
	让副本内指定className entity插入一条sai
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.recvIDs = []
		self.aiType = 0
		self.sid = 0

	def init( self, section ) :
		"""
		初始化
		"""
		AIAction.init( self, section )
		self.recvIDs = section.readString( "param1" ).split( ";" )
		self.aiType = section.readInt( "param2" )
		self.sid = section.readInt( "param3" )

	def do( self, ai, entity ) :
		entity.sendSAICommand( self.recvIDs, self.aiType, self.sid )

class AIAction257( AIAction ) :
	"""
	走到发送SAI entity的位置
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def do( self, ai, entity ):
		mb = entity.queryTemp( "SEND_SAI_ENTITY", None )
		if mb and BigWorld.entities.has_key( mb.id ):
			entity.gotoPosition( BigWorld.entities[ mb.id ].position, False )

class AIAction258( AIAction ) :
	"""
	拷贝发送SAI entity的巡逻路线
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def do( self, ai, entity ):
		mb = entity.queryTemp( "SEND_SAI_ENTITY", None )
		if mb and BigWorld.entities.has_key( mb.id ):
			e = BigWorld.entities[ mb.id ]
			entity.patrolList = e.patrolList
		
class AIAction259( AIAction ) :
	"""
	绕AI目标一定角度前进
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.radian = 0
		self.distMin = 0			# 小于此距离，后退
		self.distMax = 0			# 大于此距离，不绕行，让其追击

	def init( self, section ) :
		"""
		初始化
		"""
		AIAction.init( self, section )
		self.radian = section.readFloat( "param1" )
		if section.readString( "param2" ):
			try:
				temp = ( section.readString( "param2" )).split( ":" )
				self.distMin = float( temp[0] )
				self.distMax = float( temp[1] )
			except:
				self.distMin = Const.ROUND_MIN_DIS
				self.distMax = Const.ROUND_MAX_DIS
				ERROR_MSG( "Type Error: ( AIData %i, id %i )." % ( self.getAIDataID(), self.getID() ) )

	def do( self, ai, entity ) :
		if not entity.isMoving() and not entity.actionSign( csdefine.ACTION_FORBID_MOVE ):
			try:
				target = BigWorld.entities[ entity.targetID ]
			except:
				ERROR_MSG( "AIData %i:( %i, %s )'s targetID %i is not exist!" % (  self.getAIDataID(), entity.id, entity.className, entity.targetID ))
				return
				
			distance = entity.distanceBB( target )
			if distance < self.distMin:
				entity.moveBack( entity.targetID, distance - self.distMin - 1 )		# 多退后一米，保证退到游荡范围内
			elif distance <= self.distMax:
				radian = random.uniform( self.radian *( -1 ), self.radian )
				entity.moveRadiFollow( entity.targetID, radian, ( self.distMin, self.distMax ) )
			else:
				entity.chaseTarget( target, self.distMax - 1 )


class AIAction260( AIAction ) :
	"""
	发送地图广播
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self._msg = ""

	def init( self, section ) :
		"""
		初始化
		"""
		AIAction.init( self, section )
		self._msg = section.readString( "param1" )

	def do( self, ai, entity ) :
		entity.getCurrentSpaceBase().onChatChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", self._msg, "" )
	
class AIAction261( AIAction ) :
	"""
	CollideMonster动作控制ai
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.isOpen = False

	def init( self, section ) :
		"""
		初始化
		"""
		AIAction.init( self, section )
		self.isOpen = section.readBool( "param1" )

	def do( self, ai, entity ) :
		entity.isOpen = self.isOpen
		
class AIAction262( AIAction ) :
	"""
	加了隔板的怪物无法寻路到，用此AI动作给怪物setTemp附近的一个坐标解决此问题，目前要配合 AIAction26 使用
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.positionList = []
		
	def init( self, section ) :
		"""
		初始化
		"""
		AIAction.init( self, section )
		positionList = section.readString( "param1" )
		if positionList and positionList != '0':
			for position in positionList.split( ";" ):
				pos = vector3TypeConvert( position )
				if pos is None:
					ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param1 " % ( self.getAIDataID(), self.getID(), position ) )
				else:
					self.positionList.append( pos )

	def do( self, ai, entity ) :
		if len( self.positionList ) > 0:
			entity.setTemp( "AI_Trace_Position", self.positionList )
			
class AIAction263( AIAction ) :
	"""
	让一定范围内的玩家显示界面提示信息
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.type = 0
		self.headTextureID = ""
		self.text = ""
		self.monsterName = ""
		self.radius = 0.0
		self.lastTime = 0.0

	def init( self, section ) :
		"""
		初始化
		"""
		AIAction.init( self, section )
		self.type = section.readInt( "param1" )
		self.headTextureID = section.readString( "param2" )
		param3 = section.readString( "param3" ).split(";")
		self.text = param3[0]
		if len(param3) > 1:
			self.monsterName = param3[1]
		self.radius = section.readFloat( "param4" )
		self.lastTime = section.readFloat( "param5" )


	def do( self, ai, entity ):
		"""
		通知玩家显示一个界面提示
		"""
		es = entity.entitiesInRangeExt( self.radius, "Role", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in es:
			e.client.showHeadPortraitAndText( self.type, self.monsterName, self.headTextureID, self.text, self.lastTime )
			if self.monsterName:
				e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, self.monsterName, self.text, [] )
			else:
				e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_MESSAGE, 0, e.getName(), self.text, [] )

class AIAction264( AIAction ) :
	"""
	打断吟唱
	"""
	def __init__( self ):
		AIAction.__init__( self )
		
	def do( self, ai, entity ):
		entity.interruptSpell( csstatus.SKILL_INTERRUPTED_BY_AI )

class AIAction265( AIAction ) :
	"""
	水晶副本第三关通知副本刷新水晶
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.monsterIDList = []			#水晶className列表
		self.monsterPosList = []		#水晶出生位置列表

	def init( self, section ) :
		"""
		初始化
		"""
		AIAction.init( self, section )
		self.monsterIDList = section.readString( "param1" ).split( ";" )
		self.monsterPosList = section.readString( "param2" ).split( ";" )

	def do( self, ai, entity ):
		"""
		通知副本刷新水晶
		"""
		try:
			spaceEntity = BigWorld.entities[ entity.getCurrentSpaceBase().id ]
		except:
			EXCEHOOK_MSG( "not find the spaceEntity!" )
			spaceEntity = None
		spaceEntity.getScript().spawnShuijing( spaceEntity, self.monsterIDList, self.monsterPosList )

class AIAction266( AIAction ) :
	"""
	给烽火连天副本先锋怪收集箱子增加积分用
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0.0
		self.param2 = ""
		self.integral = 0

	def init( self, section ) :
		"""
		初始化
		"""
		AIAction.init( self, section )
		self.param1 = section.readFloat( "param1" )			#搜索范围
		self.param2 = section.readString( "param2" )		#搜索的className
		self.param3 = section.readInt64( "param3" )			#释放的技能ID
		self.lifeTime = section.readFloat( "param4" )			#多久后销毁
		self.integral = section.readInt( "param5" )			#加积分的数值


	def do( self, ai, entity ):
		"""
		先锋怪收集箱子增加积分
		"""
		monsterList = entity.entitiesInRangeExt( self.param1, None, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in monsterList:
			if e.className == self.param2 and BigWorld.entities.has_key( e.id ):
				monster = BigWorld.entities[ e.id ]
				entity.spellTarget( self.param3, e.id )
				monster.addTimer( self.lifeTime, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )
				entity.addIntegral( self.integral )

class AIAction267( AIAction ):
	"""
	寻找距离该怪物最近的巡逻点，并寻路到最近的巡逻点
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.graphID = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.graphID = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if self.graphID == "":
			if entity.patrolList:
				patrolList = entity.patrolList
				patrolPathNode, position = patrolList.nearestNode( entity.position )
				entity.gotoPosition( position )
			else:
				ERROR_MSG("graphID is None!")
				return
		patrolList = BigWorld.PatrolPath( self.graphID )
		if not patrolList or not patrolList.isReady():
			ERROR_MSG( "Patrol(%s) unWorked. it's not ready or not have such graphID!"%self.graphID )
		else:
			patrolPathNode, position = patrolList.nearestNode( entity.position )
			entity.gotoPosition( position )

class AIAction268( AIAction ) :
	"""
	临时改变自己的nameColor值
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.tmpColor = 0

	def init( self, section ) :
		"""
		初始化
		"""
		AIAction.init( self, section )
		self.tmpColor = section.readInt( "param1" )
		
	def do( self, ai, entity ):
		"""
		通知改变nameColor
		"""
		if hasattr( entity, "nameColor" ):						#保存自己配置的nameColor
			nameColor = entity.nameColor
			entity.setTemp( "AI_old_nameColor", nameColor )
			entity.nameColor = self.tmpColor

class AIAction269( AIAction ) :
	"""
	重置nameColor属性值，与AIAction267配合使用
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ) :
		"""
		初始化
		"""
		AIAction.init( self, section )
		
	def do( self, ai, entity ):
		"""
		重置nameColor值
		"""
		if hasattr( entity, "nameColor" ):						#保存自己配置的nameColor
			oldColor = entity.queryTemp( "AI_old_nameColor", 0 )
			entity.nameColor = oldColor

class AIAction270( AIAction ):
	"""
	issue:CSOL-1708
	让范围内怪物目标设为主人敌人列表里的指定目标
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.callMonsterID = ""
		self.callRange = 0.0
		self.attackTargetIndex = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.callMonsterID = section.readString( "param1" )
		self.callRange = section.readFloat( "param2" )
		self.attackTargetIndex = section.readInt( "param3" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		targetID = entity.getEnemyByIndex( self.attackTargetIndex )
		if targetID:
			es = entity.entitiesInRangeExt( self.callRange, "Monster", entity.position )
			WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
			for e in es:
				if e.className == self.callMonsterID:
					e.targetID = targetID
	
class AIAction271( AIAction ):
	"""
	issue:CSOL-1709
	招唤怪物并把目标设为主人敌人列表里的指定目标
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.callMonsterID = ""
		self.rangeRandom = 1.0
		self.attackTargetIndex = 0
	
	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.callMonsterID = section.readString( "param1" )
		self.rangeRandom = section.readFloat( "param2" )
		self.attackTargetIndex = section.readInt( "param3" )
	
	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		pos = entity.position
		position = ( pos[0] + random.randint( -self.rangeRandom, self.rangeRandom ), pos[1], pos[2] + random.randint( -self.rangeRandom, self.rangeRandom ) )
		#位置增加碰撞
		collPos = csarithmetic.getCollidePoint( entity.spaceID, pos, Math.Vector3( position ) )
		
		e = entity.createObjectNearPlanes( self.callMonsterID, collPos, entity.direction, { "level" : entity.level } )
		g_fightMgr.buildGroupEnemyRelationByIDs( e, entity.enemyList.keys() )
		
		targetID = entity.getEnemyByIndex( self.attackTargetIndex )
		if targetID:
			e.targetID = targetID

class AIAction272( AIAction ):
	"""
	绕AI目标一定角度靠近
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.radian = 0				# 游荡最大角度
		self.distMin = 0			# 靠近游荡最小距离
		self.distMax = 0			# 靠近游荡最大距离
		self.move_speed_min = 0		# 靠近游荡最小移动速度
		self.move_speed_max = 0		# 靠近游荡最大移动速度
		self.aiCommandID = 0		# 发送AI指令ID

	def init( self, section ) :
		"""
		初始化
		"""
		AIAction.init( self, section )
		self.radian = section.readFloat( "param1" )
		if section.readString( "param2" ):
			try:
				temp = ( section.readString( "param2" )).split( ":" )
				self.distMin = float( temp[0] )
				self.distMax = float( temp[1] )
			except:
				self.distMin = Const.ROUND_MIN_DIS
				self.distMax = Const.ROUND_MAX_DIS
				ERROR_MSG( "Type Error: ( AIData %i, id %i )." % ( self.getAIDataID(), self.getID() ) )
		self.aiCommandID = section.readInt( "param3" )
		if section.readString( "param4" ):
			try:
				temp = ( section.readString( "param4" )).split( ":" )
				self.move_speed_min = float( temp[0] )
				self.move_speed_max = float( temp[1] )
			except:
				self.move_speed_min = Const.ROUND_SPEED[0]
				self.move_speed_max = Const.ROUND_SPEED[1]
				ERROR_MSG( "Type Error: ( AIData %i, id %i )." % ( self.getAIDataID(), self.getID() ) )

	def do( self, ai, entity ) :
		if not entity.isMoving() and not entity.actionSign( csdefine.ACTION_FORBID_MOVE ):
			try:
				target = BigWorld.entities[ entity.targetID ]
			except:
				ERROR_MSG( "AIData %i:( %i, %s )'s targetID %i is not exist!" % (  self.getAIDataID(), entity.id, entity.className, entity.targetID ))
				return
				
			if self.radian > Const.ROUND_NEAR_OR_FAR_MAX_ANGLE:
				self.radian = Const.ROUND_NEAR_OR_FAR_MAX_ANGLE
			entity.setTemp( "NearFollow_AICommandID", self.aiCommandID )
			radian = random.uniform( self.radian *( -1 ), self.radian )
			entity.moveTowardsNearOrFarRadiFollow( entity.targetID, radian, ( self.distMin, self.distMax ), ( self.move_speed_min, self.move_speed_max ), ECBExtend.MOVE_NEAR_RADI_FOLLOW_CBID )


class AIAction273( AIAction ):
	"""
	绕AI目标一定角度远离
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.radian = 0				# 游荡最大角度
		self.distMin = 0			# 远离游荡最小距离
		self.distMax = 0			# 远离游荡最大距离
		self.move_speed_min = 0		# 远离游荡最小移动速度
		self.move_speed_max = 0		# 远离游荡最大移动速度
		self.aiCommandID = 0		# 发送AI指令ID

	def init( self, section ) :
		"""
		初始化
		"""
		AIAction.init( self, section )
		self.radian = section.readFloat( "param1" )
		if section.readString( "param2" ):
			try:
				temp = ( section.readString( "param2" )).split( ":" )
				self.distMin = float( temp[0] )
				self.distMax = float( temp[1] )
			except:
				self.distMin = Const.ROUND_MIN_DIS
				self.distMax = Const.ROUND_MAX_DIS
				ERROR_MSG( "Type Error: ( AIData %i, id %i )." % ( self.getAIDataID(), self.getID() ) )
		self.aiCommandID = section.readInt( "param3" )
		if section.readString( "param4" ):
			try:
				temp = ( section.readString( "param4" )).split( ":" )
				self.move_speed_min = float( temp[0] )
				self.move_speed_max = float( temp[1] )
			except:
				self.move_speed_min = Const.ROUND_SPEED[0]
				self.move_speed_max = Const.ROUND_SPEED[1]
				ERROR_MSG( "Type Error: ( AIData %i, id %i )." % ( self.getAIDataID(), self.getID() ) )

	def do( self, ai, entity ) :
		if not entity.isMoving() and not entity.actionSign( csdefine.ACTION_FORBID_MOVE ):
			try:
				target = BigWorld.entities[ entity.targetID ]
			except:
				ERROR_MSG( "AIData %i:( %i, %s )'s targetID %i is not exist!" % (  self.getAIDataID(), entity.id, entity.className, entity.targetID ))
				return
				
			if self.radian > Const.ROUND_NEAR_OR_FAR_MAX_ANGLE:
				self.radian = Const.ROUND_NEAR_OR_FAR_MAX_ANGLE
			entity.setTemp( "FarFollow_AICommandID", self.aiCommandID )
			radian = random.uniform( self.radian *( -1 ), self.radian )
			entity.moveTowardsNearOrFarRadiFollow( entity.targetID, radian, ( self.distMin, self.distMax ), ( self.move_speed_min, self.move_speed_max ), ECBExtend.MOVE_FAR_RADI_FOLLOW_CBID )
			
class AIAction274( AIAction ):
	"""
	传送点entity范围内的玩家传送到( 同地图跳转,不会出现场景切换界面 )
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.position = None
		self.direction = None

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.range = section.readFloat( "param1" )				# 传送点范围
		position = section.readString( "param2" )				# 传送至某个位置
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param3 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.position = pos

		self.lifeTime = section.readFloat( "param3" )			# 传送点销毁自身的时间
		direction = section.readString( "param4" )				# 传送位置朝向
		if direction and direction != '0':
			dir = vector3TypeConvert( direction )
			if dir is None:
				ERROR_MSG( "Vector3 Type Error：( AIData %i, id %i ) Bad format '%s' in section param4" % ( self.getAIDataID(), self.getID(), direction ) )
			else:
				self.direction = dir

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if self.direction is None:
			self.direction = ( 0, 0, 0 )
		es = entity.entitiesInRangeExt( self.range, "Role", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in es:
			e.direction = self.direction
			e.position = self.position
		entity.addTimer( self.lifeTime, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )
		
class AIAction275( AIAction ):
	"""
	通知副本血量改变
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if entity.getCurrentSpaceBase():
			entity.getCurrentSpaceBase().cell.onZhainanHPChange( entity.HP, entity.HP_Max )

class AIAction276( AIAction ):
	"""
	通知副本进入/离开战斗状态
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if entity.getCurrentSpaceBase():
			if entity.state == csdefine.ENTITY_STATE_FIGHT:
				#显示怒气值界面
				entity.getCurrentSpaceBase().cell.onShowAnger()
			else:
				entity.getCurrentSpaceBase().cell.onHideAnger()


class AIAction277( AIAction ):
	"""
	清除当前目标的指定buff 
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		enemy = BigWorld.entities.get( entity.targetID, None )
		if enemy :
			enemy.removeAllBuffByBuffID( self.param1, [csdefine.BUFF_INTERRUPT_NONE] )

class AIAction278( AIAction ):
	"""
	给当前战斗列表中的玩家增加传送信息
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		for enemyID in entity.enemyList:
			enemy = BigWorld.entities.get( enemyID, None )
			if enemy and enemy.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				enemy.setTemp( "requestTeleport", self.param1 )

class AIAction279( AIAction ):
	"""
	触发附近一定范围内的且在自己伤害列表中的玩家身上的一个任务。
	"""
	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.questID = section.readInt( "param1" )
		self.taskIdx = section.readInt( "param2" )
		self.range = section.readInt( "param3" )
		
	def do( self, ai, entity ):
		es = entity.entitiesInRangeExt( self.range, "Role", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in es:
			if e.id in entity.damageList and e.hasTaskIndex( self.questID, self.taskIdx ):
				e.questTaskIncreaseState( self.questID, self.taskIdx )

class AIAction280( AIAction ):
	"""
	触发附近一定范围内的玩家身上的一个任务。
	"""
	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.questID = section.readInt( "param1" )		# param1: 任务ID
		self.taskIdx = section.readInt( "param2" )		# param2: 任务目标索引
		self.range = section.readInt( "param3" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		players = entity.entitiesInRangeExt( self.range, "Role", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in players:
			# if 玩家身上有指定的任务:
			if e.hasTaskIndex( self.questID, self.taskIdx ):
				# 增加指定的QTTaskEventTrigger的状态
				e.questTaskIncreaseState( self.questID, self.taskIdx )

class AIAction281( AIAction ):
	"""
	让地图中所有玩家使用一个系统技能（目前用于阵营活动给增益buff）
	"""
	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""

		#param1: 任务ID
		#param2: 任务目标索引

		AIAction.init( self, section )
		self.camp = section.readInt( "param1" )
		self.skillID = section.readInt( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		try:
			spell = g_skills[ self.skillID ]					# 获取配置的攻击技能
		except:
			ERROR_MSG( "AIDAta %i get skill error, check whether %i is exist." %  ( self.getAIDataID(), self.skillID ) )
			return
		spaceBase = entity.getCurrentSpaceBase()
		spaceBase.allPlayersRemoteCall( "camp_systemCastSpell", ( self.camp, self.skillID, ) )
		
class AIAction282( AIAction ):
	"""
	设置一个临时属性值
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = ""
		self.param2 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )
		self.param2 = section.readInt( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		try:
			spaceEntity = BigWorld.entities[ entity.getCurrentSpaceBase().id ]
		except:
			DEBUG_MSG( "can't get spaceEntity!" )
			return
		value = spaceEntity.queryTemp( self.param1, 0 )
		value = value + self.param2
		spaceEntity.setTemp( self.param1, value )

class AIAction283( AIAction ):
	"""
	更新NPC头顶任务标记(主要用于限时任务QTRInTime)
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		players = entity.entitiesInRangeExt( entity.attrDistance, "Role", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in players:
			entity.questStatus( e.id )

class AIAction284( AIAction ):
	"""
	全服通告（屏幕中央出现）
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.channel_msgs = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		BigWorld.globalData[ csconst.C_PREFIX_GBAE ].anonymityBroadcast(self.channel_msgs,[])
		
class AIAction285( AIAction ):
	"""
	六王墓专用
	param1填通告内容（%s玩家对BOSSXXX的伤害最高）
	param2填 1或2  1表示playerName，2表示tongName
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.channel_msgs = section.readString( "param1" )
		self.param2 = section.readInt( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if self.param2 == 1:
			name = entity.getMaxDamagePlayerName()
		elif self.param2 == 2:
			name = entity.getMaxDamageTongName()
		else:
			print "cehua's config is ERROR"
	
		if name:
			BigWorld.globalData[ csconst.C_PREFIX_GBAE ].anonymityBroadcast(self.channel_msgs %name,[])

class AIAction286( AIAction ):
	"""
	当前召唤怪物，并把自己设为怪物的主人
	没有主人的普通怪物不能用
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.className = ""
		self.num = ""
		self.pos = ( 0, 0, 0 )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.className = section.readString( "param1" )
		self.num = section.readInt( "param2" )
		pos = section.readString( "param3" )
		if pos:
			self.pos = vector3TypeConvert( pos )
		

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		for i in xrange( self.num ):
			e = entity.createObjectNearPlanes( self.className, entity.position + self.pos, entity.direction, { "level" : entity.level, "spawnPos" : tuple( entity.position ) } )
			e.setOwner( entity )
			if self.pos != ( 0, 0, 0 ):
				e.setToOwnerPos( self.pos )

class AIAction287( AIAction ):
	"""
	NPC 布阵
	只针对NPCFormation，其它怪物使用无效
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.formationType = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.formationType  = section.readInt( "param1" )
	
	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.remoteScriptCall( "setFormation", ( self.formationType, ) )

class AIAction288( AIAction ):
	"""
	被布阵NPC走到287设置的阵营位置
	NPCFormationServant专用
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
	
	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.gotoToOwnerPos()

class AIAction289( AIAction ):
	"""
	对某一阵营玩家发送通告
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.channel_msgs = ""
		self.campID = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.channel_msgs = section.readString( "param1" )	# 公告内容
		self.campID = section.readInt( "param2" )			# 公告阵营

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		BigWorld.globalData[ csconst.C_PREFIX_GBAE ].campChatLocal( self.campID, csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", self.channel_msgs, [] )
		
		
class AIAction290( AIAction ):
	"""
	六王墓专用
	六王墓boss死亡时，需要做的事
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.sendReward(1)
		playerName = ""
		tongName = ""
		if entity.getMaxDamagePlayerName():
			playerName = entity.getMaxDamagePlayerName()
		if entity.getMaxDamageTongName():
			tongName = entity.getMaxDamageTongName()
		BigWorld.globalData[ csconst.C_PREFIX_GBAE ].anonymityBroadcast(cschannel_msgs.LIUWANGMU_BOSS_KILLED %entity.uname ,[])
		BigWorld.globalData[ csconst.C_PREFIX_GBAE ].anonymityBroadcast(cschannel_msgs.BCT_LIUWANGMU_MAX_DAMAGE_PLAYER %playerName,[])
		if tongName:#有帮会才显示
			BigWorld.globalData[ csconst.C_PREFIX_GBAE ].anonymityBroadcast(cschannel_msgs.BCT_LIUWANGMU_MAX_DAMAGE_TONG %tongName,[])
		DEBUG_MSG("liuwangmu boss：%d is dead, and turn down the activity!"%entity.id)
		BigWorld.globalData["LiuWangMuMgr"].onBossDied()#通知管理器，boss死亡，提前结束副本
		entity.playerDamageList = {}

class AIAction291( AIAction ):
	"""
	AI发声（根据性别发出不同声音）
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		# 声音事件配置
		self.param1 = section.readString( "param1" )
		self.param2 = section.readString( "param2" )
		self.range = section.readFloat( "param3" )
		param4 = section.readString( "param4" )
		if param4 == "":
			self.param4 = 0
		else:
			self.param4 = int( param4 )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		players = entity.entitiesInRangeExt( self.range, "Role", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in players:
			if e.isReal() and hasattr( e, "getGender" ):
				if e.getGender() == csdefine.GENDER_MALE:
					e.client.playSoundFromGender( self.param1, entity.id, self.param4 )
				elif e.getGender() == csdefine.GENDER_FEMALE:
					e.client.playSoundFromGender( self.param2, entity.id, self.param4 )

class AIAction292( AIAction ):
	"""
	召唤怪物，并把自己设为怪物的主人( 没有主人的普通怪物不能用 )
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.className = ""
		self.pos = None

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.className = section.readString( "param1" )
		pos = section.readString( "param2" )
		if pos:
			self.pos = vector3TypeConvert( pos )
	
	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		pos = self.pos
		if not pos:
			pos = entity.position

		collide = BigWorld.collide( entity.spaceID, ( pos[0], pos[1] + 10, pos[2] ), ( pos[0], pos[1] - 10, pos[2] ) )
		if collide != None:
			pos = ( pos[0], collide[0].y, pos[2] )

		monster = entity.createObjectNearPlanes( self.className, pos, entity.direction, {"spawnPos": tuple( pos ), "level": entity.level, "spawnMB": entity.spawnMB })
		monster.setOwner( entity.id )

class AIAction293( AIAction ):
	"""
	通知空间增加积分（夺城战决赛专用）
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.integral = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.integral = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if not entity.belong: # 据点没有归属，则返回
			return
		
		spaceBase = entity.getCurrentSpaceBase()
		if not spaceBase:
			return
		spaceBase.cell.addIntegral( 0 , self.integral, entity.belong  )

class AIAction294( AIAction ):
	"""
	创建潜能副本传送门（仅限潜能副本用）
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		args = {}
		args[ "radius" ] = 4.0
		args[ "useRectangle" ] = 0
		args[ "volume" ] = ( 5.000000, 30.000000, 5.000000 )
		args[ "modelNumber" ] = "gw7208"
		args[ "modelScale" ] = 1.0
		args[ "destSpace" ] = "fu_ben_maps_xue_shan_0_1"
		args[ "description" ] = ""
		args[ "uname" ] = cschannel_msgs.POTENTIAL_QIAN_NENG_FU_BEN_CHUAN_SONG_DIAN
		args[ "destPosition" ] = ( -9.008, 91.878, -77.756 )
		args[ "destDirection" ] = ( -0.244, 74.997, 0.346 )
		args[ "ownerVisibleInfos" ] = entity.ownerVisibleInfos
		e = entity.createEntityNearPlanes( "PotentialDoor", entity.position, entity.direction, args )
		e.modelScale = 1.0

class AIAction295( AIAction ):
	"""
	飞行怪物对当前目标使用技能
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt64( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		entity.spellTarget( self.param1, entity.targetID )

class AIAction296( AIAction ):
	"""
	给当前战斗列表中的不同职业玩家增加传送信息
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.posInfoDatas = {}
		self.radius = 0.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		param1= section.readString( "param1" )			#职业和坐标信息,型如 profession|posInfo
		param2 = section.readString( "param2" )
		param3 = section.readString( "param3" )
		param4 = section.readString( "param4" )
		self.radius = section.readFloat( "param5" )		#检测半径
		
		for param in [param1, param2, param3, param4]:
			if len( param )> 0:
				profession = int( param.split("|")[0] )
				posInfo = param.split("|")[-1]
				self.posInfoDatas[profession] = posInfo

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		players = entity.entitiesInRangeExt( self.radius, "Role", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for player in players:
			if player.isReal() and hasattr( player, "raceclass" ):
				profession = player.raceclass & csdefine.RCMASK_CLASS
				posInfo = self.posInfoDatas.get( profession )
				if posInfo is None:return
				player.setTemp( "requestTeleport", posInfo )
				
class AIAction297( AIAction ):
	"""
	刷新副本进度坐标
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = ""
	
	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString("param1")  # 坐标
	
	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		BigWorld.setSpaceData( entity.spaceID, csconst.SPACE_SPACEDATA_PROGRESS, self.param1 )

class AIAction298( AIAction ):
	"""
	给AI对象播放声音
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		# 声音事件配置
		self.param1 = section.readString( "param1" )
		param2 = section.readString( "param2" )
		if param2 == "":
			self.param2 = 0
		else:
			self.param2 = int( param2 )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		target = BigWorld.entities.get( entity.aiTargetID, None )
		if target and target.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			target.client.onMakeASound( self.param1, self.param2 )


class AIAction299( AIAction ) :
	"""
	让AI对象（玩家）显示界面提示信息
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.type = 0
		self.headTextureID = ""
		self.text = ""
		self.monsterName = ""
		self.lastTime = 0.0

	def init( self, section ) :
		"""
		"""
		AIAction.init( self, section )
		self.type = section.readInt( "param1" )
		self.headTextureID = section.readString( "param2" )
		param3 = section.readString( "param3" ).split(";")
		self.text = param3[0]
		if len(param3) > 1:
			self.monsterName = param3[1]
		self.lastTime = section.readFloat( "param4" )


	def do( self, ai, entity ):
		"""
		"""
		target = BigWorld.entities.get( entity.aiTargetID, None )
		if target and target.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			target.client.showHeadPortraitAndText( self.type, self.monsterName, self.headTextureID, self.text, self.lastTime )
			if self.monsterName:
				target.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, self.monsterName, self.text, [] )
			else:
				target.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_MESSAGE, 0, target.getName(), self.text, [] )

class AIAction300( AIAction ):
	"""
	新副本模板怪物AI，每次怪物刷出后会从 n 条巡逻路线中不重复选择一条开始巡逻，要求刷出怪物总数量必须是 n 的整数倍。
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.graphIDs = []

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		graphIDs = section.readString( "param1" )
		self.graphIDs = graphIDs.split()

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AIAction的entity
		@type	entity	:	entity
		"""
		if self.graphIDs == [] :
			entity.doPatrol()
			return
		
		def doPatrolByGraphID( graphID ) :
			patrolList = BigWorld.PatrolPath( graphID )
			if not patrolList or not patrolList.isReady():
				ERROR_MSG( "Patrol(%s) unWorked in %s. it's not ready or not have such graphID!"%(graphID, entity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )) )
			else:
				patrolPathNode, position = patrolList.nearestNode( entity.position )
				entity.doPatrol( patrolPathNode, patrolList  )
		
		spaceBase = entity.getCurrentSpaceBase()
		if not spaceBase :
			return
		
		patrolGraphID = entity.queryTemp( "AIAction300_patrolGraphID" )
		if not patrolGraphID :
			spaceBase.cell.remoteScriptCall( "getNonRepeatedPatrolGraphID", ( self.graphIDs, entity.className, entity ) )
		else :
			doPatrolByGraphID( patrolGraphID )

def calLinePosition( entity, target, distance ):
	"""
	计算entity 与 target的位置所在的平面直线上的某个点。
	distance 是这个点与 entity所在位置之间的距离。
	符合公式：
	entity.position 与 某个点之间的距离 = entity.position 与 target.position 之间的距离 + distance

	直线公式
	y = ax + b
	a = (y1-y2)/(x1-x2)
	b = y1- a * x1
	"""
	x1 = target.position.x
	y1 = target.position.z

	x2 = entity.position.x
	y2 = entity.position.z

	if abs( y1 - y2 ) < 0.1:
		if x1 > x2:
			x3 = x2 - distance
		else:
			x3 = x2 + distance
		y3 = y1
	elif abs( x1 - x2 ) < 0.1:
		if y1 > y2:
			y3 = y2 - distance
		else:
			y3 = y2 + distance
		x3 = x1
	else:
		a = ( y1- y2 )/( x1-x2 )
		b = y1 - a * x1

		"""
		a*x3 + b = y3
		math.sqrt( (y3 - y1)**2 + ( x3 - x1 )**2 ) = math.sqrt( (y2 - y1)**2 + ( x2 - x1 )**2 ) + distance
		代入y3, 并且 L = ( math.sqrt( (y2 - y1)**2 + ( x2 - x1 )**2 ) + distance ) ** 2

		( a*x3 + b - y1 )**2 + ( x3 - x1 )**2 = L

		a**2*x3**2 + 2*a*(b-y1)*x3 + ( b - y1 )**2 + x3**2 - 2*x1*x3 + x1**2 - L = 0

		( a**2 + 1 ) * x3**2 + ( 2*a*(b-y1) - 2*x1 ) * x3 + ( b - y1 )**2 + x1**2 - L = 0


		A = ( a**2 + 1 )
		B = ( 2*a*(b-y1) - 2*x1 )
		C = ( b - y1 )**2 + x1**2 - L
		"""
		L = ( math.sqrt( (y2 - y1)**2 + ( x2 - x1 )**2 ) + distance ) ** 2
		A = ( a**2 + 1 )
		B = ( 2*a*( b - y1 ) - 2*x1 )
		C = ( b - y1 )**2 + x1**2 - L

		mm = myMath( A,B,C )
		x31,x32 = mm.mymath()

		y31 = a * x31 + b
		y32 = a * x32 + b

		if (y31 - y2)**2 + ( x31 - x2 )**2 - distance**2 < 0.1:
			y3 = y31
			x3 = x31
		else:
			y3 = y32
			x3 = x32

	pos = ( x3, entity.position.y, y3 )

	collide = BigWorld.collide( entity.spaceID, ( pos[0], pos[1] + 10, pos[2] ), ( pos[0], pos[1] - 10, pos[2] ) )
	if collide != None:
		pos = ( pos[0], collide[0].y, pos[2] )
	return pos



def calLine2Position( entity, target, distance ):
	"""
	"""
	x1 = target.position.x
	y1 = target.position.z

	x2 = entity.position.x
	y2 = entity.position.z

	L = ( y2-y1 )**2 + ( x2 - x1 )**2
	minL = 10000
	k = -1
	for i in groupsCirclePosition:
		x,y = groupsCirclePosition[i]
		curLen = ( y2 - y1 + y )**2 + ( x2 - x1 + x )**2
		if minL > abs(curLen - L):
			k = i
			minL = abs(curLen - L)
	x3 = entity.position.x + groupsCirclePosition[k][0] * distance
	y3 = entity.position.z + groupsCirclePosition[k][1] * distance

	pos = ( x3, entity.position.y, y3 )

	collide = BigWorld.collide( entity.spaceID, ( pos[0], pos[1] + 10, pos[2] ), ( pos[0], pos[1] - 10, pos[2] ) )
	if collide != None:
		pos = ( pos[0], collide[0].y, pos[2] )
	return pos



class myMath:
	def __init__(self,a,b,c):
		self.a=a
		self.b=b
		self.c=c

	def mymath(self):
		deta=self.b**2.0-4.0*self.a*self.c
		if deta<0:
			return( 0, 0 )
		else:
			x1=(-self.b+math.sqrt(deta))/(2.0*self.a)
			x2=(-self.b-math.sqrt(deta))/(2.0*self.a)

		return (x1,x2)


groupsCirclePosition = {0: (0.0, 1.0), 1: (0.017452406139607784, 0.99984769516158722), 2: (0.034899496107421553, 0.99939082703987636), 3: (0.052335955351004659, 0.99862953480131844), 4: (0.069756472556141938, 0.99756405034289619), 5: (0.087155741264717396, 0.99619469822148599), 6: (0.10452846149111271, 0.99452189555499526), 7: (0.12186934133663414, 0.99254615189530349), 8: (0.13917309860147606, 0.99026806907304843), 9: (0.15643446239373016, 0.98768834101430225), 10: (0.17364817473495014, 0.98480775352919525), 11: (0.19080899216178271, 0.98162718407255045), 12: (0.2079116873231775, 0.97814760147660196), 13: (0.22495105057268847, 0.97437006565587991), 14: (0.24192189155538293, 0.97029572728434987), 15: (0.25881904078887363, 0.96592582744490652), 16: (0.27563735123799338, 0.9612616972513276), 17: (0.2923716998826314, 0.95630475744280419), 18: (0.30901698927825522, 0.95105651795116919), 19: (0.32556814910864135, 0.94551857744095835), 20: (0.34202013773034279, 0.93969262282244048), 21: (0.3583679437084224, 0.93358042873776925), 22: (0.37460658734298424, 0.92718385702040951), 23: (0.39073112218603878, 0.92050485612800481), 24: (0.40673663654823855, 0.91354546054885855), 25: (0.42261825499502625, 0.90630779018220897), 26: (0.43837113983173925, 0.89879404969248755), 27: (0.45399049257721846, 0.89100652783775636), 28: (0.46947155542547181, 0.8829475967725311), 29: (0.48480961269494821, 0.87461971132519889), 30: (0.49999999226497954, 0.86602540825025476), 31: (0.51503806699895427, 0.85716730545558062), 32: (0.52991925615378765, 0.84804810120500618), 33: (0.54463902677526033, 0.83867057329639105), 34: (0.55919289507880032, 0.82903757821548096), 35: (0.57357642781528717, 0.81915205026579452), 36: (0.58778524362146245, 0.80901700067480542), 37: (0.60181501435453522, 0.7986355166766943), 38: (0.61566146641057673, 0.78801076057194697), 39: (0.62932038202630092, 0.77714596876408659), 40: (0.64278760056383633, 0.76604445077383465), 41: (0.65605901977809644, 0.75470958823099843), 42: (0.66913059706636346, 0.743144833844394), 43: (0.68199835069970383, 0.73135371035011765), 44: (0.694658361035842, 0.7193398094384863), 45: (0.70710677171312097, 0.70710679065997395), 46: (0.71933979082518695, 0.69465838031047766), 47: (0.73135369207604206, 0.68199837029625066), 48: (0.74314481591510861, 0.66913061697885212), 49: (0.75470957065196465, 0.65605904000046156), 50: (0.76604443355040708, 0.64278762108991794), 51: (0.7771459519015117, 0.62932040284984669), 52: (0.78801074407536131, 0.61566148752524341), 53: (0.79863550055112298, 0.60181503575389117), 54: (0.80901698492516028, 0.58778526529898911), 55: (0.81915203489687305, 0.57357644976438149), 56: (0.82903756323196487, 0.55919291729277631), 57: (0.83867055870284435, 0.5446390492473514), 58: (0.8480480870058742, 0.52991927887714863), 59: (0.85716729165518846, 0.51503808996666356), 60: (0.86602539485280627, 0.5000000154700408), 61: (0.87461969833477515, 0.48480963613029276), 62: (0.88294758419308894, 0.46947157908396125), 63: (0.89100651567312783, 0.45399051645164606), 64: (0.8987940379463778, 0.43837116391483277), 65: (0.90630777885819613, 0.42261827927944973), 66: (0.91354544965039208, 0.40673666102659456), 67: (0.9205048456584044, 0.39073114685087118), 68: (0.92718384698286438, 0.3746066121867796), 69: (0.93358041913533685, 0.35836796872361332), 70: (0.93969261365804591, 0.34202016290930942), 71: (0.94551856871739304, 0.32556817444371372), 72: (0.95105650967109057, 0.30901701476171617), 73: (0.95630474960873435, 0.29237172550671847), 74: (0.96126168986565297, 0.27563737699490104), 75: (0.96592582050987674, 0.25881906667075627), 76: (0.97029572080207749, 0.24192191755435666), 77: (0.97437005962833945, 0.22495107668083356), 78: (0.97814759590562939, 0.20791171353254134), 79: (0.98162717895984286, 0.1908090184643815), 80: (0.98480774887631006, 0.17364820112277204), 81: (0.98768833682265667, 0.1564344888587372), 82: (0.99026806534391931, 0.13917312513560651), 83: (0.99254614862982682, 0.12186936793180567), 84: (0.99452189275416558, 0.10452848813922397), 85: (0.99619469588615661, 0.087155767957651314), 86: (0.99756404847377833, 0.06975649928576759), 87: (0.99862953339898153, 0.052335982109179724), 88: (0.99939082610474761, 0.034899522885995453), 89: (0.99984769469395141, 0.017452432930423509), 90: (0.99999999999999967, 2.6794896585026611e-008), 91: (0.99984769562922227, -0.0174523793487921), 92: (0.99939082797500445, -0.034899469328847514), 93: (0.99862953620365458, -0.052335928592829505), 94: (0.99756405221201327, -0.069756445826516245), 95: (0.99619470055681481, -0.087155714571783477), 96: (0.99452189835582427, -0.10452843484300127), 97: (0.9925461551607796, -0.12186931474146247), 98: (0.99026807280217688, -0.1391730720673455), 99: (0.98768834520594717, -0.15643443592872308), 100: (0.98480775818207977, -0.17364814834712822), 101: (0.98162718918525727, -0.19080896585918375), 102: (0.97814760704757375, -0.20791166111381348), 103: (0.97437007168341971, -0.22495102446454326), 104: (0.97029573376662159, -0.24192186555640913), 105: (0.96592583437993562, -0.25881901490699077), 106: (0.96126170463700167, -0.27563732548108549), 107: (0.95630476527687336, -0.2923716742585441), 108: (0.95105652623124726, -0.30901696379479388), 109: (0.94551858616452289, -0.3255681237735687), 110: (0.93969263198683439, -0.34202011255137593), 111: (0.93358043834020088, -0.3583679186932312), 112: (0.92718386705795397, -0.3746065624991885), 113: (0.92050486659760455, -0.39073109752120611), 114: (0.91354547144732434, -0.40673661206988226), 115: (0.90630780150622103, -0.42261823071060267), 116: (0.89879406143859653, -0.43837111574864557), 117: (0.89100654000238433, -0.45399046870279053), 118: (0.88294760935197258, -0.46947153176698198), 119: (0.87461972431562218, -0.4848095892596031), 120: (0.86602542164770269, -0.49999996905991789), 121: (0.857167319255972, -0.51503804403124498), 122: (0.84804811540413749, -0.52991923343042624), 123: (0.8386705878899372, -0.54463900430316869), 124: (0.82903759319899661, -0.55919287286482378), 125: (0.81915206563471543, -0.5735764058661923), 126: (0.8090170164244499, -0.58778522194393545), 127: (0.79863553280226507, -0.60181499295517893), 128: (0.78801077706853206, -0.6156614452959096), 129: (0.77714598562666093, -0.6293203612027547), 130: (0.76604446799726178, -0.64278758003775405), 131: (0.75470960581003166, -0.65605899955573088), 132: (0.74314485177367884, -0.66913057715387425), 133: (0.73135372862419268, -0.68199833110315655), 134: (0.71933982805178498, -0.69465834176120589), 135: (0.7071068096068267, -0.70710675276626722), 136: (0.69465839958511255, -0.71933977221188738), 137: (0.68199838989279693, -0.73135367380196603), 138: (0.66913063689134045, -0.74314479798582267), 139: (0.65605906022282634, -0.75470955307293008), 140: (0.64278764161599922, -0.76604441632697884), 141: (0.62932042367339203, -0.77714593503893614), 142: (0.61566150863990954, -0.78801072757877522), 143: (0.60181505715324657, -0.79863548442555099), 144: (0.58778528697651533, -0.80901696917551458), 145: (0.57357647171347548, -0.81915201952795103), 146: (0.55919293950675208, -0.82903754824844811), 147: (0.54463907171944204, -0.83867054410929709), 148: (0.52991930160050926, -0.84804807280674166), 149: (0.51503811293437229, -0.85716727785479585), 150: (0.50000003867510157, -0.86602538145535723), 151: (0.48480965956563715, -0.87461968534435075), 152: (0.46947160274245053, -0.88294757161364612), 153: (0.45399054032607333, -0.89100650350849853), 154: (0.4383711879979259, -0.89879402620026749), 155: (0.42261830356387275, -0.90630776753418274), 156: (0.40673668550495046, -0.91354543875192495), 157: (0.39073117151570336, -0.92050483518880333), 158: (0.37460663703057479, -0.92718383694531858), 159: (0.35836799373880396, -0.93358040953290389), 160: (0.34202018808827572, -0.93969260449365066), 161: (0.32556819977878609, -0.94551855999382706), 162: (0.30901704024517712, -0.95105650139101128), 163: (0.29237175113080505, -0.95630474177466385), 164: (0.27563740275180848, -0.96126168247997767), 165: (0.25881909255263869, -0.9659258135748463), 166: (0.24192194355333008, -0.97029571431980433), 167: (0.22495110278897867, -0.9743700536007982), 168: (0.20791173974190474, -0.97814759033465626), 169: (0.19080904476698018, -0.9816271738471346), 170: (0.17364822751059375, -0.9848077442234241), 171: (0.156434515323744, -0.9876883326310103), 172: (0.13917315166973709, -0.99026806161478942), 173: (0.12186939452697726, -0.99254614536434926), 174: (0.10452851478733519, -0.99452188995333524), 175: (0.087155794650585136, -0.99619469355082646), 176: (0.069756526015393089, -0.9975640466046598), 177: (0.052336008867355004, -0.99862953199664395), 178: (0.034899549664569499, -0.99939082516961819), 179: (0.01745245972123886, -0.99984769422631492), 180: (5.3589793170053202e-008, -0.99999999999999856), 181: (-0.017452352557976489, -0.99984769609685664), 182: (-0.034899442550273621, -0.99939082891013176), 183: (-0.052335901834654114, -0.99862953760599005), 184: (-0.069756419096890371, -0.99756405408112969), 185: (-0.087155687878849461, -0.99619470289214274), 186: (-0.10452840819488982, -0.99452190115665251), 187: (-0.12186928814629083, -0.99254615842625493), 188: (-0.13917304553321463, -0.99026807653130466), 189: (-0.15643440946371573, -0.98768834939759131), 190: (-0.17364812195930612, -0.98480776283496363), 191: (-0.19080893955658465, -0.98162719429796341), 192: (-0.20791163490444942, -0.97814761261854488), 193: (-0.22495099835639767, -0.97437007771095885), 194: (-0.24192183955743496, -0.97029574024889276), 195: (-0.25881898902510803, -0.96592584131496395), 196: (-0.27563729972417744, -0.96126171202267485), 197: (-0.29237164863445675, -0.95630477311094175), 198: (-0.30901693831133253, -0.95105653451132444), 199: (-0.32556809843849566, -0.94551859488808676), 200: (-0.34202008737240913, -0.93969264115122753), 201: (-0.35836789367803978, -0.93358044794263184), 202: (-0.37460653765539254, -0.92718387709549765), 203: (-0.39073107285637326, -0.92050487706720352), 204: (-0.40673658759152548, -0.91354548234578958), 205: (-0.42261820642617831, -0.90630781283023276), 206: (-0.43837109166555144, -0.89879407318470494), 207: (-0.45399044482836226, -0.89100655216701174), 208: (-0.46947150810849192, -0.88294762193141341), 209: (-0.48480956582425788, -0.8746197373060447), 210: (-0.49999994585485613, -0.86602543504514984), 211: (-0.51503802106353502, -0.85716733305636283), 212: (-0.5299192107070646, -0.84804812960326825), 213: (-0.54463898183107684, -0.83867060248348269), 214: (-0.55919285065084701, -0.82903760818251149), 215: (-0.5735763839170972, -0.81915208100363557), 216: (-0.58778520026640757, -0.80901703217409404), 217: (-0.6018149715558222, -0.79863554892783528), 218: (-0.61566142418124215, -0.7880107935651165), 219: (-0.62932034037920814, -0.77714600248923471), 220: (-0.64278755951167155, -0.76604448522068824), 221: (-0.65605897933336454, -0.75470962338906478), 222: (-0.66913055724138448, -0.74314486970296323), 223: (-0.68199831150660872, -0.73135374689826715), 224: (-0.69465832248656934, -0.71933984666508322), 225: (-0.70710673381941314, -0.70710682855367879), 226: (-0.71933975359858682, -0.69465841885974744), 227: (-0.73135365552788945, -0.68199840948934276), 228: (-0.74314478005653617, -0.66913065680382822), 229: (-0.75470953549389519, -0.65605908044519057), 230: (-0.76604439910355049, -0.64278766214207961), 231: (-0.77714591817636047, -0.62932044449693636), 232: (-0.78801071108218845, -0.61566152975457522), 233: (-0.79863546829997856, -0.60181507855260152), 234: (-0.80901695342586832, -0.58778530865404122), 235: (-0.81915200415902856, -0.57357649366256891), 236: (-0.82903753326493079, -0.55919296172072719), 237: (-0.83867052951574894, -0.54463909419153267), 238: (-0.84804805860760823, -0.52991932432386979), 239: (-0.85716726405440236, -0.51503813590208103), 240: (-0.86602536805790731, -0.50000006188016222), 241: (-0.8746196723539259, -0.4848096830009806), 242: (-0.88294755903420297, -0.46947162640093881), 243: (-0.89100649134386867, -0.45399056420050027), 244: (-0.89879401445415652, -0.43837121208101876), 245: (-0.90630775621016868, -0.42261832784829551), 246: (-0.91354542785345716, -0.40673670998330586), 247: (-0.9205048247192017, -0.39073119618053509), 248: (-0.92718382690777201, -0.37460666187437008), 249: (-0.93358039993047004, -0.35836801875399477), 250: (-0.93969259532925453, -0.34202021326724219), 251: (-0.94551855127026063, -0.32556822511385758), 252: (-0.95105649311093143, -0.30901706572863719), 253: (-0.95630473394059268, -0.29237177675489162), 254: (-0.9612616750943016, -0.27563742850871575), 255: (-0.96592580663981509, -0.25881911843452088), 256: (-0.9702957078375305, -0.2419219695523033), 257: (-0.97437004757325629, -0.22495112889712343), 258: (-0.97814758476368224, -0.20791176595126862), 259: (-0.98162716873442546, -0.19080907106957917), 260: (-0.98480773957053735, -0.17364825389841579), 261: (-0.98768832843936327, -0.1564345417887511), 262: (-0.99026805788565886, -0.1391731782038669), 263: (-0.99254614209887115, -0.12186942112214809), 264: (-0.99452188715250411, -0.10452854143544635), 265: (-0.99619469121549564, -0.087155821343518902), 266: (-0.9975640447355405, -0.069756552745018519), 267: (-0.9986295305943057, -0.05233603562553002), 268: (-0.999390824234488, -0.034899576443143294), 269: (-0.99984769375867766, -0.017452486512054867), 270: (-0.99999999999999678, -8.038469019916896e-008), 271: (-0.99984769656449024, 0.017452325767160423), 272: (-0.99939082984525829, 0.034899415771700137), 273: (-0.99862953900832474, 0.052335875076479348), 274: (-0.99756405595024533, 0.069756392367265121), 275: (-0.99619470522747, 0.08715566118591539), 276: (-0.99452190395748008, 0.10452838154677829), 277: (-0.99254616169172949, 0.12186926155111912), 278: (-0.99026808026043167, 0.13917301899908388), 279: (-0.98768835358923479, 0.15643438299870849), 280: (-0.98480776748784682, 0.17364809557148345), 281: (-0.981627199410669, 0.190808913253985), 282: (-0.97814761818951534, 0.20791160869508479), 283: (-0.97437008373849709, 0.22495097224825256), 284: (-0.97029574673116292, 0.24192181355846129), 285: (-0.96592584824999173, 0.25881896314322494), 286: (-0.96126171940834748, 0.27563727396726917), 287: (-0.95630478094500948, 0.29237162301036912), 288: (-0.95105654279140106, 0.30901691282787092), 289: (-0.94551860361164997, 0.32556807310342256), 290: (-0.93969265031562021, 0.34202006219344144), 291: (-0.93358045754506236, 0.3583678686628477), 292: (-0.92718388713304101, 0.37460651281159585), 293: (-0.92050488753680204, 0.3907310481915397), 294: (-0.91354549324425383, 0.40673656311316903), 295: (-0.90630782415424338, 0.42261818214175445), 296: (-0.8987940849308127, 0.43837106758245703), 297: (-0.89100656433163838, 0.45399042095393366), 298: (-0.88294763451085367, 0.46947148445000153), 299: (-0.87461975029646655, 0.48480954238891227), 300: (-0.86602544844259632, 0.49999992264979398), 301: (-0.85716734685675322, 0.5150379980958244), 302: (-0.84804814380239868, 0.52991918798370208), 303: (-0.83867061707702784, 0.54463895935898421), 304: (-0.82903762316602614, 0.55919282843686946), 305: (-0.81915209637255493, 0.57357636196800199), 306: (-0.80901704792373719, 0.58778517858888002), 307: (-0.79863556505340494, 0.60181495015646513), 308: (-0.78801081006170037, 0.61566140306657424), 309: (-0.77714601935180783, 0.62932031955566115), 310: (-0.76604450244411415, 0.6427875389855886), 311: (-0.75470964096809701, 0.65605895911099799), 312: (-0.7431448876322474, 0.66913053732889405), 313: (-0.73135376517234141, 0.68199829191006023), 314: (-0.71933986527838112, 0.694658303211932), 315: (-0.70710684750052999, 0.70710671487255883), 316: (-0.69465843813438122, 0.71933973498528647), 317: (-0.68199842908588804, 0.73135363725381231), 318: (-0.66913067671631543, 0.74314476212724911), 319: (-0.65605910066755424, 0.75470951791485974), 320: (-0.64278768266816011, 0.76604438188012103), 321: (-0.62932046532048103, 0.77714590131378369), 322: (-0.6156615508692409, 0.78801069458560091), 323: (-0.60181509995195648, 0.79863545217440524), 324: (-0.58778533033156699, 0.80901693767622118), 325: (-0.57357651561166223, 0.81915198879010509), 326: (-0.55919298393470163, 0.82903751828141314), 327: (-0.54463911666362219, 0.83867051492220068), 328: (-0.52991934704722932, 0.84804804440847459), 329: (-0.51503815886978865, 0.85716725025400864), 330: (-0.50000008508522187, 0.86602535466045727), 331: (-0.48480970643632448, 0.87461965936350006), 332: (-0.46947165005942759, 0.8829475464547587), 333: (-0.45399058807492731, 0.89100647917923792), 334: (-0.43837123616411167, 0.89879400270804466), 335: (-0.42261835213271837, 0.90630774488615384), 336: (-0.40673673446166059, 0.91354541695498892), 337: (-0.39073122084536616, 0.92050481424959951), 338: (-0.37460668671816427, 0.92718381687022511), 339: (-0.35836804376918452, 0.93358039032803586), 340: (-0.34202023844620755, 0.93969258616485818), 341: (-0.32556825044892967, 0.94551854254669332), 342: (-0.30901709121209786, 0.95105648483085059), 343: (-0.29237180237897836, 0.95630472610652073), 344: (-0.27563745426562325, 0.96126166770862476), 345: (-0.25881914431640329, 0.96592579970478309), 346: (-0.2419219955512768, 0.97029570135525589), 347: (-0.22495115500526758, 0.97437004154571383), 348: (-0.20791179216063149, 0.97814757919270767), 349: (-0.19080909737217713, 0.98162716362171587), 350: (-0.17364828028623683, 0.98480773491765006), 351: (-0.15643456825375723, 0.98768832424771558), 352: (-0.13917320473799749, 0.99026805415652752), 353: (-0.12186944771731972, 0.99254613883339216), 354: (-0.10452856808355787, 0.99452188435167233), 355: (-0.087155848036453043, 0.99619468888016394), 356: (-0.069756579474644351, 0.99756404286642053), 357: (-0.052336062383705445, 0.99862952919196657), 358: (-0.034899603221716619, 0.99939082329935702), 359: (-0.017452513302869972, 0.99984769329103973)}

groupsLinePosition = {0: (-2.5, -6.0), 1: (-2.5, -5.0), 2: (-2.5, -4.0), 3: (-2.5, -3.0), 4: (-2.5, -2.0), 5: (-2.5, -1.0), 6: (-2.5, 0.0), 7: (-2.5, 1.0), 8: (-2.5, 2.0), 9: (-2.5, 3.0), 10: (-2.5, 4.0), 11: (-2.5, 5.0), 12: (-1.5, -6.0), 13: (-1.5, -5.0), 14: (-1.5, -4.0), 15: (-1.5, -3.0), 16: (-1.5, -2.0), 17: (-1.5, -1.0), 18: (-1.5, 0.0), 19: (-1.5, 1.0), 20: (-1.5, 2.0), 21: (-1.5, 3.0), 22: (-1.5, 4.0), 23: (-1.5, 5.0), 24: (1.5, -6.0), 25: (1.5, -5.0), 26: (1.5, -4.0), 27: (1.5, -3.0), 28: (1.5, -2.0), 29: (1.5, -1.0), 30: (1.5, 0.0), 31: (1.5, 1.0), 32: (1.5, 2.0), 33: (1.5, 3.0), 34: (1.5, 4.0), 35: (1.5, 5.0), 36: (2.5, -6.0), 37: (2.5, -5.0), 38: (2.5, -4.0), 39: (2.5, -3.0), 40: (2.5, -2.0), 41: (2.5, -1.0), 42: (2.5, 0.0), 43: (2.5, 1.0), 44: (2.5, 2.0), 45: (2.5, 3.0), 46: (2.5, 4.0), 47: (2.5, 5.0)}