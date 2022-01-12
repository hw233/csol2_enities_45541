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

#����һ��Բ�ϵİ˸���
#groupsCirclePosition = {0: (0.0, 1.0), 1: (0.17364817473495014, 0.98480775352919525), 2: (0.34202013773034279, 0.93969262282244048), 3: (0.49999999226497954, 0.86602540825025476), 4: (0.64278760056383633, 0.76604445077383465), 5: (0.76604443355040708, 0.64278762108991794), 6: (0.86602539485280627, 0.5000000154700408), 7: (0.93969261365804591, 0.34202016290930942), 8: (0.98480774887631006, 0.17364820112277204), 9: (0.99999999999999967, 2.6794896585026611e-008), 10: (0.98480775818207977, -0.17364814834712822), 11: (0.93969263198683439, -0.34202011255137593), 12: (0.86602542164770269, -0.49999996905991789), 13: (0.76604446799726178, -0.64278758003775405), 14: (0.64278764161599922, -0.76604441632697884), 15: (0.50000003867510157, -0.86602538145535723), 16: (0.34202018808827572, -0.93969260449365066), 17: (0.17364822751059375, -0.9848077442234241), 18: (5.3589793170053202e-008, -0.99999999999999856), 19: (-0.17364812195930612, -0.98480776283496363), 20: (-0.34202008737240913, -0.93969264115122753), 21: (-0.49999994585485613, -0.86602543504514984), 22: (-0.64278755951167155, -0.76604448522068824), 23: (-0.76604439910355049, -0.64278766214207961), 24: (-0.86602536805790731, -0.50000006188016222), 25: (-0.93969259532925453, -0.34202021326724219), 26: (-0.98480773957053735, -0.17364825389841579), 27: (-0.99999999999999678, -8.038469019916896e-008), 28: (-0.98480776748784682, 0.17364809557148345), 29: (-0.93969265031562021, 0.34202006219344144), 30: (-0.86602544844259632, 0.49999992264979398), 31: (-0.76604450244411415, 0.6427875389855886), 32: (-0.64278768266816011, 0.76604438188012103), 33: (-0.50000008508522187, 0.86602535466045727), 34: (-0.34202023844620755, 0.93969258616485818), 35: (-0.17364828028623683, 0.98480773491765006)}


class AIAction1( AIAction ):
	"""
	ս���б����
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if len( entity.enemyList ) > 0:
			entity.resetEnemyList()

class AIAction2( AIAction ):
	"""
	�˺��б�����
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.addDamageList( entity.aiTargetID, 0 )

class AIAction3( AIAction ):
	"""
	�˺��б�ɾ��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.removeEnemyDmgList( entity.aiTargetID )

class AIAction4( AIAction ):
	"""
	����˺��б�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.resetDamageList()

class AIAction5( AIAction ):
	"""
	�����б�����
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.addCureList( entity.aiTargetID, 0 )

class AIAction6( AIAction ):
	"""
	�����б�ɾ��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.removeEnemyCureList( entity.aiTargetID )

class AIAction7( AIAction ):
	"""
	��������б�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.resetCureList()

class AIAction8( AIAction ):
	"""
	���ս���б��г���ǰAIѡ��Ŀ��������е�λ
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if entity.aiTargetID in entity.enemyList:
			# ���·�����ѭ������
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
	����˺��б��г���ǰĿ��������е�λ
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if entity.aiTargetID in entity.damageList:
			# ���·�����ѭ������
			damageListVal = entity.damageList[ entity.aiTargetID ]
			entity.resetDamageList()
			entity.damageList[ entity.aiTargetID ] = damageListVal
		else:
			ERROR_MSG( "aiTarget %i in damageList not found, implEntity %i. " % ( entity.aiTargetID, entity.id ) )


class AIAction10( AIAction ):
	"""
	��������б��г���ǰĿ��������е�λ
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if entity.aiTargetID in entity.cureList:
			# ���·�����ѭ������
			val = entity.cureList[ entity.aiTargetID ]
			entity.resetCureList()
			entity.cureList[ entity.aiTargetID ] = val
		else:
			ERROR_MSG( "aiTarget %i in cureList not found, implEntity %i. " % ( entity.aiTargetID, entity.id ) )


class AIAction11( AIAction ):
	"""
	��ָ����λ����ս��������λ�б�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.addFriendList( entity.aiTargetID )

class AIAction12( AIAction ):
	"""
	��ָ����λ�Ƴ�ս��������λ�б�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.removeAIFriend( entity.aiTargetID )

class AIAction13( AIAction ):
	"""
	����ǰĿ��Ӽ�����λ�б����Ƴ�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.removeAIFriend( entity.aiTargetID )

class AIAction14( AIAction ):
	"""
	����ս��״̬
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.changeAttackTarget( entity.aiTargetID )

class AIAction15( AIAction ):
	"""
	����ս��״̬
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.changeState( csdefine.ENTITY_STATE_FREE )

class AIAction16( AIAction ):
	"""
	���˺��б���λ��Ϊ��ǰĿ��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	�������б���λ��Ϊ��ǰĿ��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	�ȼ����ѡ��
	��ս���б��еȼ���͵ĵ�λ��Ϊ��ǰĿ��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	�ȼ����ѡ��
	��ս���б��еȼ���ߵĵ�λ��Ϊ��ǰĿ��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	�������ѡ��
	��ս���б���������͵ĵ�λ��Ϊ��ǰĿ��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	�������ѡ��
	��ս���б���������ߵĵ�λ��Ϊ��ǰĿ��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	ֹͣ�Ե�ǰĿ���׷��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.stopMoving()
		entity.changeSubState( csdefine.M_SUB_STATE_NONE )

class AIAction23( AIAction ):
	"""
	��λ
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.exitFight()

class AIAction24( AIAction ):
	"""
	��ȫ�ָ�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.full()
		entity.clearBuff( [csdefine.BUFF_INTERRUPT_ON_DIE] )					# �������buff

class AIAction25( AIAction ):
	"""
	ǿ�ƹ���Ŀ��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.changeAttackTarget( entity.aiTargetID )

class AIAction26( AIAction ):
	"""
	ʹ�ü���
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt64( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		# �����ж�
		try:
			enemy = BigWorld.entities[ entity.targetID ]
		except:
			return

		spell = g_skills[ self.param1 ]						# ��ȡ���õĹ�������
		range = spell.getRangeMax( entity )					# ��ȡ���ܵ����ʩ������
		# ���ڽ��һ�ѹ���׷��ͬһ��Ŀ��ʱ�ص���һ������⡣
		if checkAndMove( entity ):
			return
		state = entity.spellTarget( self.param1,  entity.targetID )

		# �п��ܱ���������
		if entity.state == csdefine.ENTITY_STATE_DEAD:
			return
		if state == csstatus.SKILL_GO_ON:						# ����ʩչ,,ֱ�ӷ���
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
			entity.chaseTarget( enemy, spell.getRangeMax( entity )*2/3 )# �����Զ,,׷��Ŀ�꣨*2/3��Ϊ��׷������һ�㣩
		else:
			# ��������
			INFO_MSG( "%i: skill %i use state = %i." % ( entity.id, self.param1, state ) )

class AIAction27( AIAction ):
	"""
	����
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.doFlee()

class AIAction28( AIAction ):
	"""
	ֹͣ����
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.stopMoving()
		entity.changeSubState( csdefine.M_SUB_STATE_NONE )

class AIAction29( AIAction ):
	"""
	��ǰAIϵͳ���м������
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.setNextRunAILevel( self.param1 )

class AIAction30( AIAction ):
	"""
	Ĭ��AIϵͳ���м������
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.setDefaultAILevel( self.param1 )

class AIAction31( AIAction ):
	"""
	ָ��S��AI����Ӧ��Ŀ��
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.setSAI( csdefine.AI_TYPE_SPECIAL, self.param1 )

class AIAction32( AIAction ):
	"""
	ָ��E��AI����Ӧ��Ŀ��
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.addEAI( self.param1 )

class AIAction33( AIAction ):
	"""
	NPC����
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if len( self.param1 ) > 0:
			entity.say( self.param1 )

class AIAction34( AIAction ):
	"""
	��ָ��һ����������NPC����AI����
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = ""  # NPCID
		self.param2 = 0	  # cmd
		self.param3 = 0.0 # �����뾶

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" ).split("|")
		self.param2 = section.readInt( "param2" )
		self.param3 = section.readFloat( "param3" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		es = entity.entitiesInRangeExt( self.param3, None, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in es:
			if e.className in self.param1 and e.className != "":
				entity.sendAICommand( e.id, self.param2 )

class AIAction35( AIAction ):
	"""
	��������Ұ��Χ��ĵ���
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.onViewRange()

class AIAction36( AIAction ):
	"""
	��⵱ǰ����Ŀ�����Ч��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.checkAttackTarget( entity.targetID )					# ֻ��鵱ǰ����Ŀ��

class AIAction37( AIAction ):
	"""
	ս���б�����
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		aiTarget = BigWorld.entities.get( entity.aiTargetID )
		if aiTarget:
			g_fightMgr.buildEnemyRelation( entity, aiTarget )

class AIAction38( AIAction ):
	"""
	�����Ƚ�������б����Ϊ��ǰĿ��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		eid = entity.findFirstEnemyByTime()
		if BigWorld.entities.has_key( eid ):
			entity.setAITargetID( eid )

class AIAction40( AIAction ):
	"""
	�ı䵱ǰĿ��Ϊ�������ö���
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if entity.hasEnemy( entity.aiTargetID ) and BigWorld.entities.has_key( entity.aiTargetID ) and entity.targetID != entity.aiTargetID:
			entity.changeAttackTarget( entity.aiTargetID )

class AIAction41( AIAction ):
	"""
	����ͬ��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		#��ΪAI������entity������õ� ��������������ȷ��
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
	��Ŀ��ʹ������ȼ��ļ���
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt64( "param1" ) * 1000

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		# �����ж�
		try:
			enemy = BigWorld.entities[ entity.targetID ]
		except:
			return

		try:
			spell = g_skills[ self.param1 + entity.level ]						# ��ȡ���õĹ�������
		except:
			ERROR_MSG( "Use skill error, id is %i."%(self.param1 + entity.level) )
			return

		range = spell.getRangeMax( entity )					# ��ȡ���ܵ����ʩ������
		# ���ڽ��һ�ѹ���׷��ͬһ��Ŀ��ʱ�ص���һ������⡣
		if checkAndMove( entity ):
			return
		state = entity.spellTarget( self.param1 + entity.level,  entity.targetID )
		# �п��ܱ������������п����ʵ��ĳЩ���ܻᵼ��entity���١�
		if entity.isDestroyed or entity.state == csdefine.ENTITY_STATE_DEAD:
			return

		if state == csstatus.SKILL_GO_ON:						# ����ʩչ,,ֱ�ӷ���
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
			elif entity.chaseTarget( enemy, spell.getRangeMax( entity ) ):		# �����Զ,,׷��Ŀ��
				return
		else:
			# ��������
			INFO_MSG( "%i: skill %i use state = %i." % ( entity.id, self.param1 + entity.level, state ) )

class AIAction43( AIAction ):
	"""
	������ʹ�ü���
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt64( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		# �����ж�
		try:
			spell = g_skills[ self.param1 ]						# ��ȡ���õĹ�������
		except:
			ERROR_MSG( "Use skill error, id is %i."%self.param1 )
			return
		state = entity.spellTarget( self.param1,  entity.id )
		# �п��ܱ���������
		if entity.state == csdefine.ENTITY_STATE_DEAD:
			return

		if state == csstatus.SKILL_GO_ON:						# ����ʩչ,,ֱ�ӷ���
			return
		elif state in [ csstatus.SKILL_NOT_HIT_TIME, csstatus.SKILL_NOT_READY, csstatus.SKILL_INTONATING ]:
			if entity.isMoving():
				entity.stopMoving()
		else:
			# ��������
			INFO_MSG( "%i: skill %i use state = %i." % ( entity.id, self.param1, state ) )

class AIAction44( AIAction ):
	"""
	������ʹ������ȼ��ļ���
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt64( "param1" ) * 1000

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		# �����ж�
		state = entity.spellTarget( self.param1 + entity.level,  entity.id )
		# �п��ܱ���������
		if entity.state == csdefine.ENTITY_STATE_DEAD:
			return

		if state == csstatus.SKILL_GO_ON:						# ����ʩչ,,ֱ�ӷ���
			return
		elif state in [ csstatus.SKILL_NOT_HIT_TIME, csstatus.SKILL_NOT_READY, csstatus.SKILL_INTONATING ]:
			if entity.isMoving():
				entity.stopMoving()
		else:
			# ��������
			INFO_MSG( "%i: skill %i use state = %i." % ( entity.id, self.param1 + entity.level, state ) )

class AIAction45( AIAction ):
	"""
	������ʩ�ų����ܵ�����Ϊ�������ö���
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	ֹͣѲ��
	ֹͣѲ��, ����Ѳ�߹��ܵ�NPC�ſ���ʹ��, ʹ��NPC����ֹͣѲ��״̬
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.stopPatrol()

class AIAction47( AIAction ):
	"""
	��ʼѲ��
	��ʼѲ��, ����Ѳ�߹��ܵ�NPC�ſ���ʹ��, ʹ��NPC����Ѳ��״̬����������Ѳ��·���ڵ����npc

	���������Ѳ�����ݣ���ôʹ��Ѳ�����ݽ���Ѳ�ߣ�����ʹ��Ĭ�ϵ�Ѳ�����ݡ�
	param1ΪpatrolNode
	param2Ϊ·��id
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.patrolNode = ""
		self.graphID = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.patrolNode = section.readString( "param1" )
		self.graphID = section.readString( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if self.graphID == "":
			entity.doPatrol()
			return

		patrolList = BigWorld.PatrolPath( self.graphID )
		if not patrolList or not patrolList.isReady():
			ERROR_MSG( "Patrol(%s) unWorked. it's not ready or not have such graphID! Monster(%s,%s), spaceName:%s."% ( self.graphID, entity.getName(), entity.className, entity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) ) )
		else:
			lastPatrolNode = entity.queryTemp( "patrolPathNode", "" ) #��һ��Ѳ�ߵ���ĵ�
			if lastPatrolNode != "" and patrolList.nodesTraversableFrom( lastPatrolNode ):
				# ��һ��Ѳ�ߵ㲻Ϊ�ն������ҵ���һ��Ѳ�ߵ�
				entity.doPatrol( lastPatrolNode, patrolList  )
			else:
				patrolPathNode, position = patrolList.nearestNode( entity.position )
				entity.doPatrol( patrolPathNode, patrolList  )

class AIAction48( AIAction ):
	"""
	108�ǣ�NPC��ɹ���
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.tolevel = section.readInt( "param1" )
		self.toTargetlevel = section.readInt( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
			elif entity.state == csdefine.ENTITY_STATE_FIGHT: # ����Ҳ���Ŀ�꣬��ɹ���ʧ�ܣ����Ѿ�������ս��״̬����ԭ״̬��
				entity.changeState( csdefine.ENTITY_STATE_FREE )

class AIAction49( AIAction ):
	"""
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	NPC/MONSTER ��������
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self._p1 = section.readFloat( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if self._p1 <= 0:
			entity.addTimer( csconst.MONSTER_CORPSE_DURATION, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )
		else:
			entity.addTimer( self._p1, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )
		#entity.destroy()

class AIAction51( AIAction ):
	"""
	NPC֪ͨӵ�������һ���¼�������
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0
		self.param2 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )
		self.param2 = section.readInt( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	��¼��ǰ��ʱ��,,  ��һ����ǩ���С�
	��Ҫ����һЩʱ���ѯ�Ȳ�����
	�� һ��ʱ���� NPCû����ʲô����ô����

	Ҫʵ�������Ȼ����Ҫ���һ�����������
	��ĳ��¼ʱ���Ƿ񵽴   �����Ǻ͸ñ�ǩ��һ����
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if not entity.queryTemp( self.param1, None ):
			entity.setTemp( self.param1, BigWorld.time() )

class AIAction53( AIAction ):
	"""
	NPCֹͣ�ƶ�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.stopMoving()

class AIAction54( AIAction ):
	"""
	NPC��������ӵ����

	���־��� ��NPCʼ����ӵ���������ֵ�һ�ξ���.
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	���ĳ��¼ʱ��
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.removeTemp( self.param1 )

class AIAction56( AIAction ):
	"""
	������ӵ���߷���һ��ϵͳ��Ϣ
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

		# ע��section.readString( "param1" )����������д���ұ�����csstatus����ڵ��Ѷ���ı���

		self.param1 = getattr( csstatus, section.readString( "param1" ) )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		ownerBase = entity.queryTemp( "npc_ownerBase", None )
		if ownerBase:
			ownerBase.client.onStatusMessage( self.param1, "" )
		else:
			ERROR_MSG( "can not find the owner!" )

class AIAction57( AIAction ):
	"""
	�������NPC��������Χ�����Ա����
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 15.0
		self.param2 = 1
		self.param3 = 2

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readFloat( "param1" )
		self.param2 = section.readInt( "param2" )
		self.param3 = section.readInt( "param3" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		spaceName = entity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		globalKey = "holdCity.%s" % spaceName
		if not BigWorld.globalData.has_key( globalKey ):	# �������û������
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
						if expData["day"] != today:		# ������ȡ��������
							expData["day"] = today
							expData["count"] = 0
						else:
							if expData["count"] >= 60:	# ÿ��ֻ����60�Σ���60�ε�ʱ�������ʾ
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
	���ĳEAI���
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if not entity.isEAI( self.param1 ):
			return
		entity.eaiIDArray.remove( self.param1 )


class AIAction59( AIAction ):
	"""
	�������﹥�����˵ĵ���(��Ҫ���˽���ս��״̬���������)
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )



	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	���������������
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		#if entity.getSubState() == csdefine.M_SUB_STATE_CHASE:
		#	return
		entity.spawnPos = tuple( entity.position )
		owner = BigWorld.entities.get( entity.getOwnerID() )

		if owner:
			if entity.actionSign( csdefine.ACTION_FORBID_MOVE ) or owner.actionSign( csdefine.ACTION_FORBID_MOVE ):
				return

			entity.chaseEntity( owner, 4 ) #�ڳ�׷����Ҿ���4�׵�ʱ��ֹͣ�ƶ�


class AIAction61( AIAction ):
	"""
	�����ɵ�������ߵ�������Ҫ�������˿����Ѿ����˱��space�������Ҳ�����������˺��Լ�����һ��cellʱ������ɵ�����ߣ�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.flyToMasterSpace()


class AIAction62( AIAction ):
	"""
	�ɵ�������ߣ����ں�����֮��ľ���Ƚ�Զ����Ҫ�ɵ����Ա�,Ҳ�������ڷɵ���ͬ��space��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	���½�����������˵Ĺ���
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	��ʧ���ΪNPC
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if hasattr( entity, "changeToNPC" ):
			entity.changeToNPC()
		entity.addTimer( csconst.MONSTER_CORPSE_DURATION, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )


class AIAction65( AIAction ):
	"""
	�ڳ��й�
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = ""


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		ct = entity.queryTemp( 'callMonstersTime', 0 )
		ctt = entity.queryTemp( 'callMonstersTimeTotal', 0 )
		memberIDDict = entity.queryTemp( "dartMembers", {} )
		g = BigWorld.entities.get
		if ct < ctt:
			# �ٻ��Ĵ���callMonstersTimeС���ܵ��ٻ�����callMonstersTimeTotal
			ct += 1
			entity.setTemp( 'callMonstersTime', ct )
			ownerID = entity.getOwnerID()
			owner = g(ownerID)
			for i in xrange( ctt ):
				# �ٹֵĸ���callMonstersTotal
				monsterID = Const.DART_MONSTERSID[random.randint( 0,len ( Const.DART_MONSTERSID )-1 )]
				pos = entity.position + Math.Vector3( random.randint(3,6), 3,random.randint(3,6) )
				monster = entity.createObjectNearPlanes( str(monsterID), pos, entity.direction, {"spawnPos": tuple(entity.position), "level": entity.queryTemp('level',1)} )
				g_fightMgr.buildEnemyRelation( monster, entity )
				monster.setTemp( 'is_dart_banditti', True )
				monster.addCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_ANTAGONIZE_ID, ownerID )

			# ���������߾��齱��
			if len( memberIDDict ) > 0:
				for mid in memberIDDict.iterkeys():
					member = g(mid)
					if memberIDDict[mid] == -1 or member is None:
						continue
					member.tongDartExpReward()
			if owner is not None:
				owner.tongDartExpReward()
			# ��֪ͨ ���ڳ�
			ownerBaseMailbox = entity.getOwner()
			if not hasattr( ownerBaseMailbox, "client" ):
				return
			ownerBaseMailbox.client.onStatusMessage( csstatus.ROLE_QUEST_DART_CALL_MONSTER, "" )
			entity.disMountEntity( ownerID, ownerID )


class AIAction66( AIAction ):
	"""
	�ڳ��жϽ���AOI�Ķ����ǲ����Լ���Ŀ�꣬����ǣ����¼
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if BigWorld.entities.has_key( entity.aiTargetID ):
			if BigWorld.entities[entity.aiTargetID].className == entity.queryTemp( 'destNpcClassName' ):
				entity.setTemp( 'destEntityID', entity.aiTargetID )


class AIAction67( AIAction ):
	"""
	�ڳ�����Ƿ񵽴�Ŀ��,������������������ʧ
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
		if distance < 10 and disEntity.spaceID == entity.spaceID:		#�ڳ�����NPC�ķ�Χ
			player.questTaskIncreaseState( questID, entity.queryTemp('eventIndex') )
			# ������ɺ� ���ڳ���ʧ��㲥������� by����
			if not entity.queryTemp( 'questFinish' ):
				self.dartMissionBrocad( questID, player )
			entity.setTemp( 'questFinish', True )

	def dartMissionBrocad( self, questID, player ):
		"""
		���ڻ���ڳɹ��Ĺ㲥 by����14:10 2009-7-31
		@param missionType : ��������
		@param missonnType : UINT8
		"""
		#self.family_grade
		player.brocastMessageDart( questID )

class AIAction68( AIAction ):
	"""
	NPC��Ŀ���ƶ�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.chaseTarget( BigWorld.entities.get( entity.targetID ), 10.0 )


class AIAction70( AIAction ):
	"""
	�ڳ�����֪ͨ�������ʧ��
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		playerName = entity.ownerName
		if BigWorld.entities.has_key( entity.getOwnerID() ):
			BigWorld.entities[entity.getOwnerID()].handleDartFailed()
		elif playerName != '':
			BigWorld.globalData['DartManager'].addDartMessage( playerName, csstatus.ROLE_QUEST_DART_NPC_DIE, True )


class AIAction69( AIAction ):
	"""
	��ӵ���߷���һ��ϵͳ��Ϣ����ͣ����
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 20.0


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	NPC֪ͨӵ����һ���¼�������ʧ��
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0
		self.param2 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )
		self.param2 = section.readInt( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	��������ս������ʧ
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if not entity.getState() == csdefine.ENTITY_STATE_FIGHT:
			#entity.destroy()
			entity.addTimer( 0.1, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )


class AIAction73( AIAction ):
	"""
	ˮ���ٻ�����
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		monster = entity.createObjectNearPlanes( self.param1, entity.position, entity.direction, {"spawnPos": tuple(entity.position ), "level": entity.level, "spawnMB": entity.spawnMB })
		entity.resetEnemyList()
		entity.spawnMB = None
		entity.planesAllClients( "playCallMonsterEffect", () )
		entity.addTimer( 0.2, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )


class AIAction74( AIAction ):
	"""
	ˮ���ͷż���
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt64( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		target = SkillTargetObjImpl.createTargetObjPosition( entity.position )	# ��װ����ʩչ����
		spell = g_skills[self.param1]
		spell.use( entity, target )										# ��ʹ�ü���

class AIAction75( AIAction ):
	"""
	���ض��������ƶ�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

		position = section.readString( "param1" )
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param1 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.pos = pos

		try: #Ϊ�˷�ֹ�߻������Ĭ����0�����modify by wuxo
			self.backTo = bool( section.readInt( "param2" ) )# �Ƿ����ƶ�
		except:
			self.backTo = False	# �Ƿ����ƶ�

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if entity.actionSign( csdefine.ACTION_FORBID_MOVE ):	# �����ֹ�ƶ�
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
	֪ͨ���������ѵ���ָ��λ��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		try:
			spaceBase = BigWorld.cellAppData["spaceID.%i" % entity.spaceID]
			spaceEntity = BigWorld.entities[ spaceBase.id ]
		except:
			DEBUG_MSG( "not find the spaceEntity!" )

		spaceEntity.getScript().onMonsterArrive( spaceEntity )		# ֪ͨ���������ѵ���ָ��λ��

		#entity.destroy()	# ��ʧ
		entity.addTimer( 1, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )	# ��ʧ

class AIAction77( AIAction ):
	"""
	��ս���б������ѡȡһ��������ʩ������ȼ�����
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt64( "param1" ) * 1000

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if len( entity.enemyList ) > 0:
			targetID = random.choice( entity.enemyList.keys() )
			entity.spellTarget( self.param1 + entity.level,  targetID )

class AIAction78( AIAction ):
	"""
	�ٻ�����
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0
		self.param2 = ""
		self.param3 = ""


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )	# �ٻ���������
		self.param2 = section.readString( "param2" )	# �ٻ�����className

		position = section.readString( "param3" )
		if position and position != '0':
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param3 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.param3 = pos

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		try:
			spaceBase = BigWorld.cellAppData["spaceID.%i" % entity.spaceID]
			spaceEntity = BigWorld.entities[ spaceBase.id ]		# �ҵ�����
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
			# ������¼�ٻ����Ĺ���id
			tempCallMonsterIDs = spaceEntity.queryTemp( "tempCallMonsterIDs", [] )		# ȡ�ø�����¼�ٻ����Ĺ���id�б�
			tempCallMonsterIDs.append( monster.id )
			spaceEntity.setTemp( "tempCallMonsterIDs", tempCallMonsterIDs )
			enemyList = entity.enemyList
			if len( enemyList ):
				ownerID = enemyList.keys()[0]
				monster.setTemp( "ownerID", ownerID )
			
			g_fightMgr.buildGroupEnemyRelationByIDs( monster, enemyList.keys() )

class AIAction79( AIAction ):
	"""
	NPC���ԣ����Ҽ�¼����ʱ��
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if len( self.param1 ) > 0:
			entity.say( self.param1 )

		entity.setTemp( "tempSayTime", time.time() )	# ������ʱ�������洢NPC���Ե�ʱ��
		entity.setTemp( "tempSayFlag", True )			# ������ʱ��������Ƿ��Թ�

class AIAction80( AIAction ):
	"""
	Ѱ��ָ����Χ���ض�����Ŀ�꣬Ŀ��Ѫ������ָ��ֵ������ʩ��ָ������
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
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readFloat( "param1" )			# ��Χ
		self.param2 = section.readString( "param2" )		# className
		self.param3 = section.readInt64( "param3" ) * 1000	# ���ܱ��
		self.param4 = section.readFloat( "param4" ) / 100	# Ѫ������

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if entity.queryTemp( "onlyOneTime", False ):	# ֻ��Ҫʩ��һ�μ���
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
			entity.setTemp( "onlyOneTime", True )	# ֻ��Ҫʩ��һ�μ���

class AIAction81( AIAction ):
	"""
	���ѡȡս���б���Ϊ��ǰĿ��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if len( entity.enemyList ) > 0:
			targetID = random.choice( entity.enemyList.keys() )

			if targetID > 0:
				entity.setAITargetID( targetID )

class AIAction82( AIAction ):
	"""
	���ñ��
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )			# ���

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.setTemp( self.param1, True )						# ���ñ��

class AIAction83( AIAction ):
	"""
	�Ƴ����
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )			# ���

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.removeTemp( self.param1 )		# ���ñ��

class AIAction84( AIAction ):
	"""
	ѡȡһ����Χ���ض����͵Ĺ����Ϊ��ǰĿ��
	"""
	def __init__( self ):
		AIAction.__init__( self )

		self.param1 = 0.0
		self.param2 = ""
		self.param3 = "Monster"		# Ĭ��ΪMonster

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

		self.param1 = section.readFloat( "param1" )							# ��Χ
		self.param2 = section.readString( "param2" )						# className
		self.param3 = section.readString( "param3" )						# EntityType

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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

		if not flag:	# ���û���ҵ�boss
			return

		#entity.setAITargetID( target.id )
		if entity.targetID != target.id:
			entity.changeAttackTarget( target.id )

class AIAction85( AIAction ):
	"""
	������ʹ�������һ������
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = []

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

		for e in (section.readString( "param1" )).split( ";" ):
			if e !=  "":	#add by wuxo 2011-12-20
				self.param1.append( int( e ) )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		# �����ж�
		skillID = random.choice( self.param1 )
		spell = g_skills[ skillID ]								# ��ȡ���õĹ�������
		state = entity.spellTarget( skillID,  entity.id )
		# �п��ܱ���������
		if entity.state == csdefine.ENTITY_STATE_DEAD:
			return

		if state == csstatus.SKILL_GO_ON:						# ����ʩչ,,ֱ�ӷ���
			return
		elif state in [ csstatus.SKILL_NOT_HIT_TIME, csstatus.SKILL_NOT_READY, csstatus.SKILL_INTONATING ]:
			if entity.isMoving():
				entity.stopMoving()
		else:
			# ��������
			INFO_MSG( "%i: skill %i use state = %i." % ( entity.id, skillID, state ) )

class AIAction86( AIAction ):
	"""
	�����ͷ������
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		# �����ж�
		if entity.queryTemp('deadFlags', False):
			entity.addTimer( 0.1, 0, ECBExtend.ACTIVITY_MONSTER_DISAPPEAR_CBID )
			entity.removeTemp('deadFlags')

class AIAction87( AIAction ):
	"""
	��贫��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.spaceName = section.readString( "param1" )

		position = section.readString( "param2" )
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param2 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.pos = pos

		direction = section.readString( "param3" )
		if direction:
			dir = vector3TypeConvert( direction )
			if dir is None:
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param3" % ( self.getAIDataID(), self.getID(), direction ) )
			else:
				self.direction = dir

		self.patrolPathNode = section.readString( "param4" )
		self.patrolList = section.readString( "param5" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.setTemp( "teleportFly_data", ( self.patrolPathNode, self.patrolList, self.spaceName, self.pos, self.direction ) )
		indexs = entity.findBuffsByBuffID( 99010 )
		entity.getBuff( indexs[0] )["skill"].updateData( entity )

class AIAction88( AIAction ):
	"""
	���͵�ǰ��ͼĳλ��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.spaceName = section.readString( "param1" )

		position = section.readString( "param2" )
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param2 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.pos = pos

		direction = section.readString( "param3" )
		if direction:
			dir = vector3TypeConvert( direction )
			if dir is None:
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param3" % ( self.getAIDataID(), self.getID(), direction ) )
			else:
				self.direction = dir

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		#entity.gotoSpace( self.spaceName, self.pos, self.direction )
		entity.openVolatileInfo()	# ����ǰ����volatile��Ϊ�˱�����ȷ�����������رգ���enityֹͣ�ƶ���ᴥ���رգ������entity���ԣ����㲻�����ر�Ҳ������ɹ��ȵ�����
		entity.position = self.pos
		entity.direction = self.direction

class AIAction89( AIAction ):
	"""
	���贫�Ͷ������ٶȿ���
	��ɫʹ�õ�AIAction
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.actionName = section.readString( "param1" )
		self.speed = section.readFloat( "param2" ) * csconst.FLOAT_ZIP_PERCENT

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	���贫�ͽ���
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	��贫�� ���·��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	Ѱ�ҵ�PKֵ����ĳ����������ս���б�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self._radius = section.readFloat( "param1" ) # �����뾶
		self._pkValue = section.readInt( "param2" ) # ����pkֵ�ڶ�������

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	��¼������
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.setTemp( "figthDirection", entity.direction )

class AIAction94( AIAction ):
	"""
	�ı������򵽼�¼�ĳ���
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.direction = entity.queryTemp( "figthDirection", ( 0, 0, 0 ) )


class AIAction95( AIAction ):
	"""
	���ڻ��罫��ʣ��10%Ѫ��ʱ�򣬷��ԣ������޶�Ψһ����Ŀ��Ϊ�m؅
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	�������Ȫm؅���Һ�ħ���������߿����m؅ʹ�����ؼ���
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
				entity.addTimer( 0.2, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )			# Ҫ��Ҳ��������������֤���ܷ�������
				# entity.destroy()
				return


class AIAction97( AIAction ):
	"""
	�������Ȫm؅Ӳ����ħ���������һֱ�������꣬һֱ���䡣
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	�ѵ��˼��뵽�Լ����ʹӵ����б���
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	�ѵ��˼����Լ������˵����б���
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
			if lastEnemy:			#�б���ΪlastIDΪ0������������һ���жϣ�ͬʱ���������̣���û��masterʱ����ѭ����
				g_fightMgr.buildEnemyRelation( master, lastEnemy )

class AIAction100( AIAction ):
	"""
	����սAI��ѡ���������¥Ϊ����Ŀ��
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	�ı䵱ǰEntity״̬��ĳ״̬
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.state = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if entity.state != self.state:
			entity.changeState( self.state )

class AIAction102( AIAction ):
	"""
	��������ΧĿ��ʩ�ż������X��������
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.skillID = section.readInt( "param1" )
		self.receiverCount = section.readInt( "param2" )
		self.radius = section.readFloat( "param3" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	����սAI��ѡ���������¥��Ϊ��¥��Ѫ
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.radius = section.readFloat( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	NPC��������Ļ������֣�
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.channel_msgs = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		es = entity.entitiesInRangeExt( csconst.CHAT_CHANNEL_SC_HINT_AREA, "Role", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in es:
			if e.spaceID == entity.spaceID:
				e.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", self.channel_msgs, [])

class AIAction105( AIAction ):
	"""
	���ض��������ƶ��������¼��ȡ����temp
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.temp = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if entity.actionSign( csdefine.ACTION_FORBID_MOVE ):	# �����ֹ�ƶ�
			entity.stopMoving()
		else:
			entity.gotoPosition( entity.queryTemp( self.temp, (0, 0, 0) ) )

class AIAction106( AIAction ):
	"""
	�����ѷ�����������������50%��һ��Ŀ��ʩ��������
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self._param1 = 0.0	#����ֵ���ٷֱȣ�
		self._param2 = 0	# ����id

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self._param1 = section.readFloat( "param1" )
		self._param2 = section.readInt( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	��һ����Χ���ض����͵Ĺ������λ��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AIAction.__init__( self )
		self.param1 = 0.0
		self.param2 = ""
		self.param3 = "Monster"		# Ĭ��ΪMonster


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readFloat( "param1" )			# ��Χ
		self.param2 = section.readString( "param2" )		# className
		self.param3 = section.readString( "param3" )		# ����EntityType

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	���ĳЩbuff
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AIAction.__init__( self )
		self.buffs = []

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.buffs = section.readString( "param1" ).split("|")

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		for buff in self.buffs:
			entity.removeAllBuffByBuffID( int(buff), [csdefine.BUFF_INTERRUPT_NONE] )

class AIAction109( AIAction ):
	"""
	��ս���б������ѡȡһ��������ʩ��ָ������
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt64( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if len( entity.enemyList ) > 0:
			targetID = random.choice( entity.enemyList.keys() )
			entity.spellTarget( self.param1,  targetID )

class AIAction110( AIAction ):
	"""
	����ٻ�������Ĺ���
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0
		self.param2 = ""
		self.radiusDict = {}					# ����뾶
		self.enterSpellDict = {}				# ��������ʩ�ŵļ���
		self.leaveSpellDict = {}				# �뿪����ʩ�ŵļ���


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )	# �ٻ���������
		self.classNameList = section.readString( "param2" ).split( ";" )	# �ٻ�����className(className1;className2;className3)
		self.radiusStr = section.readString( "param3" )						# ����뾶as like : className1:radius1;className2:radius2
		for e in self.radiusStr.split( ";" ):
			dict = e.split( ":" )
			self.radiusDict[ str(dict[0]) ] = int(dict[1])
		self.enterSpellStr = section.readString( "param4" )					# ��������ʩ�ŵļ���as like : className1:skill1;className2:skill2
		for e in self.enterSpellStr.split( ";" ):
			dict = e.split( ":" )
			self.enterSpellDict[ str(dict[0]) ] = int(dict[1])
		self.leaveSpellStr = section.readString( "param5" )					# �뿪����ʩ�ŵļ���as like : className1:skill1;className2:skill2
		for e in self.leaveSpellStr.split( ";" ):
			dict = e.split( ":" )
			self.leaveSpellDict[ str(dict[0]) ] = int(dict[1])

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		try:
			spaceBase = BigWorld.cellAppData["spaceID.%i" % entity.spaceID]
			spaceEntity = BigWorld.entities[ spaceBase.id ]		# �ҵ�����
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
	����Χ����������Ҽ���ս���б�
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )	# �����İ뾶

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		roleList = entity.entitiesInRangeExt( self.param1, "Role", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		g_fightMgr.buildGroupEnemyRelation( entity, roleList )

class AIAction112( AIAction ):
	"""
	��һ����Χ���ض����͵Ĺ����������ض���buff����������
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AIAction.__init__( self )
		self.param1 = 0.0
		self.param2 = ""
		self.param3 = "Monster"		# Ĭ��ΪMonster
		self.param4 = 0


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readFloat( "param1" )			# ��Χ
		self.param2 = section.readString( "param2" )		# className
		self.param3 = section.readString( "param3" )		# ����EntityType
		self.param4 = section.readInt( "param4" )			# buff��id

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	��ս���б���ĳclassName�Ĺ���ӵ����б���ɾ��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )			# className

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	����ٻ�����
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0
		self.param2 = ""


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )	# �ٻ���������
		self.classNameList = section.readString( "param2" ).split( ";" )	# �ٻ�����className(className1;className2;className3)

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		try:
			spaceBase = BigWorld.cellAppData["spaceID.%i" % entity.spaceID]
			spaceEntity = BigWorld.entities[ spaceBase.id ]		# �ҵ�����
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
	����
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )	# �ŵ�className

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		spaceBase = entity.getCurrentSpaceBase()
		if spaceBase is None: return
		spaceBase.openDoor( { "entityName" : self.param1 } )		# ������

class AIAction116( AIAction ):
	"""
	ѡȡһ����Χ���ض����͵����ض�buff��entity����Ϊ��ǰĿ��
	"""
	def __init__( self ):
		AIAction.__init__( self )

		self.param1 = 0.0
		self.param2 = 0
		self.param3 = "Monster"		# Ĭ��ΪMonster

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

		self.param1 = section.readFloat( "param1" )							# ��Χ
		self.param2 = section.readInt( "param2" )							# buffID
		self.param3 = section.readString( "param3" )						# EntityType

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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

		if not flag:	# ���û���ҵ�entity
			return

		if entity.targetID != target.id:
			entity.changeAttackTarget( target.id )

class AIAction117( AIAction ):
	"""
	���й���Ա���� ������³������ˣ� ���������ƣ�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	AI����
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		# �����¼�����
		self.param1 = section.readString( "param1" )
		param2 = section.readString( "param2" )
		if param2 == "":
			self.param2 = 0
		else:
			self.param2 = int( param2 )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.planesAllClients( "onMakeASound", ( self.param1, self.param2 ) )



class AIAction119( AIAction ):
	"""
	������������Ϊ����˺������
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	�������������
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		# �����¼�����
		self.__questID	 		= section.readInt( "param1" )
		self.__taskIndex	 	= section.readInt( "param2" )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.questTaskIncreaseState( self.__questID, self.__taskIndex )


class AIAction121( AIAction ):
	"""
	���﹥��BOSS��������
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	����ս������¼��սʱ�� by ����
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		tick = int( time.time() )
		entity.setTemp( "fightStartTick", tick )


class AIAction123( AIAction ):
	"""
	�ͷ�һ�μ��ܼ����Ӽ���ʹ�ü��� by ����
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		skillUseCount = entity.queryTemp( "uskCount", 0 ) + 1
		entity.setTemp( "uskCount", skillUseCount )


class AIAction124( AIAction ):
	"""
	ͬ�������Ѫ�����丸�������AI��ʱֻ�����ڸ���
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.__classNames 		= section.readString( "param1" ).split("|")
		self.__range		 	= section.readInt( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		nextCount = entity.queryTemp( "nextSetHPCount", 1 )				#׼�����ô���
		curCount = entity.queryTemp( "curSetHPCount", 0 )				#�Ѿ����õĴ���
		if nextCount == curCount:										#�����ȣ�˵���Լ��Ǳ�ͬ���Ķ��󣬲���Ҫͬ������
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
	�ı�ָ������AI�ȼ�
	Ӧ�ã������˼����ĳһ����������ִ��һ�����顣
	ʵ�ַ�ʽ��: ��ʱ�ı�����AI�ȼ��������Ǹ��������õ�AI�ȼ�����������顣������ϣ�AI�ȼ��ָ���
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.__classNames 		= section.readString( "param1" ).split("|")
		self.__range		 	= section.readInt( "param2" )
		self.__aiLevel		 	= section.readInt( "param3" )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entityList = entity.entitiesInRangeExt( self.__range, "Monster", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for i in entityList:
			if i.className in self.__classNames:
				i.setNextRunAILevel( self.__aiLevel )

class AIAction126( AIAction ):
	"""
	����
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if entity.state == csdefine.ENTITY_STATE_DEAD:
			return
		entity.die(0)


class AIAction127( AIAction ):
	"""
	������Ĺ���Ŀ���Ϊ�ض�����Ĺ���Ŀ��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.__className 		= section.readString( "param1" )
		self.__range		 	= section.readInt( "param2" )



	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	�ù��ﲥ�Ŷ���
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.__actionName = section.readString( "param1" )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.planesAllClients( "onPlayAction", ( self.__actionName, ) )


class AIAction129( AIAction ):
	"""
	�����Ϊ���������
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.resetEnemyList()
		entity.state = csdefine.ENTITY_STATE_ENVIRONMENT_OBJECT
		entity.addFlag( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED )
		entity.actCounterInc( csdefine.ACTION_FORBID_ATTACK )


class AIAction130( AIAction ):
	"""
	�����������ʵ�ǹ����Ϊ���
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.state = csdefine.ENTITY_STATE_FREE
		entity.removeFlag( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED )
		entity.actCounterDec( csdefine.ACTION_FORBID_ATTACK )


class AIAction131( AIAction ):
	"""
	��¼��ǰѪ��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.setTemp( "ai_save_HP_value", entity.HP )


class AIAction132( AIAction ):
	"""
	�����������
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if entity.inHomingSpell():
			entity.delHomingSpell( csstatus.SKILL_INTERRUPTED_BY_SPELL_3 )



class AIAction133( AIAction ):
	"""
	�Խ�����������ʹ�ü��ܣ�С�ÿ���ʹ�ã�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.skills = section.readString( "param1" ).split( "|" )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		target = BigWorld.entities.get( entity.aiTargetID )

		if target:
			skillID = int( random.choice( self.skills ) )
			entity.spellTarget( skillID, target.id )

class AIAction134( AIAction ):
	"""
	��entity����λ��ʹ�ü���
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt64( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		# �����ж�
		try:
			enemy = BigWorld.entities[ entity.targetID ]
		except:
			return

		spell = g_skills[ self.param1 ]						# ��ȡ���õĹ�������
		range = spell.getRangeMax( entity )					# ��ȡ���ܵ����ʩ������
		# ���ڽ��һ�ѹ���׷��ͬһ��Ŀ��ʱ�ص���һ������⡣
		if checkAndMove( entity ):
			return

		state = entity.spellPosition( self.param1,  copy.copy( enemy.position ) )

		# �п��ܱ���������
		if entity.state == csdefine.ENTITY_STATE_DEAD:
			return

		if state == csstatus.SKILL_GO_ON:						# ����ʩչ,,ֱ�ӷ���
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
			elif entity.chaseTarget( enemy, spell.getRangeMax( entity ) ):		# �����Զ,,׷��Ŀ��
				return
		else:
			# ��������
			INFO_MSG( "%i: skill %i use state = %i." % ( entity.id, self.param1, state ) )


class AIAction135( AIAction ):
	"""
	����Ѫ���ٷֱȣ�֪ͨ���ڵ�space
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		spaceBase = entity.getCurrentSpaceBase()
		if spaceBase is None: return
		spaceBase.cell.remoteScriptCall( "onTreeHPChange", (int(entity.HP * 100 / entity.HP_Max),  ) )

class AIAction136( AIAction ):
	"""
	�����ڵ�spacebase �����¼�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		spaceBase = entity.getCurrentSpaceBase()
		if spaceBase is None: return 
		spaceBase.eventHandle( self.param1, {} )


class AIAction137( AIAction ):
	"""
	����������ϵ�һ������
	�Ҳ�����ң��Ͳ����κζ��� by mushuang
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""

		#param1: ����ID
		#param2: ����Ŀ������

		AIAction.init( self, section )
		self.questID = section.readInt( "param1" )
		self.taskIdx = section.readInt( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		player = None

		#��ȡ���
		players = entity.entitiesInRangeExt( 60.0, "Role" )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		if players:
			player = players[0]

			# if ���������ָ��������:
			if player.hasTaskIndex( self.questID, self.taskIdx ):
				# ����ָ����QTTaskEventTrigger��״̬
				player.questTaskIncreaseState( self.questID, self.taskIdx )

class AIAction138( AIAction ):
	"""
	NPC �ƶ���ָ��λ��
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = None

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

		position = section.readString( "param1" )
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param1 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.param1 = pos								# λ��

		self.param2 = section.readFloat( "param2" )				#��Χ


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.doRandomRun( self.param1, self.param2 )

class AIAction139( AIAction ):
	"""
	�����ͻ�������ͷ����·��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )	# ����������ͷ·���ļ�ID
		self.param2 = section.readInt( "param2" )		# ������Χ

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		roles = entity.entitiesInRangeExt( self.param2, "Role", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for role in roles:
			role.client.onCameraFly( self.param1 )

class AIAction140( AIAction ):
	"""
	�Խ��������Ŀ��ʹ������ȼ��ļ���
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt64( "param1" ) * 1000

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		# �����ж�
		try:
			enemy = BigWorld.entities[ entity.aiTargetID ]
		except:
			return

		try:
			spell = g_skills[ self.param1 + entity.level ]						# ��ȡ���õĹ�������
		except:
			ERROR_MSG( "Use skill error, id is %i."%(self.param1 + entity.level) )
			return

		range = spell.getRangeMax( entity )					# ��ȡ���ܵ����ʩ������
		# ���ڽ��һ�ѹ���׷��ͬһ��Ŀ��ʱ�ص���һ������⡣
		if checkAndMove( entity ):
			return
		entity.spellTarget( self.param1 + entity.level,  entity.aiTargetID )


class AIAction141( AIAction ):
	"""
	�ı�̶�λ����Χ���������ģ�ͣ����ڸ�����
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.oldNumber = ""				#�ϵ�ģ��
		self.newNumber = ""				#�µ�ģ��
		self.range = 0					#��Χ
		self.position = ( 0, 0, 0 )		#λ��

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param4 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.position = pos

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entityList = entity.entitiesInRangeExt( self.range, "EnvironmentObject", self.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for i in entityList:
			if i.modelNumber == self.oldNumber:
				i.modelNumber = self.newNumber



class AIAction142( AIAction ):
	"""
	��entity����λ��ʹ������ȼ��ļ���
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt64( "param1" ) * 1000

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		# �����ж�
		try:
			enemy = BigWorld.entities[ entity.targetID ]
		except:
			return

		spell = g_skills[ self.param1 + entity.level ]						# ��ȡ���õĹ�������
		range = spell.getRangeMax( entity )					# ��ȡ���ܵ����ʩ������
		# ���ڽ��һ�ѹ���׷��ͬһ��Ŀ��ʱ�ص���һ������⡣
		if checkAndMove( entity ):
			return

		state = entity.spellPosition( self.param1 + entity.level,  copy.copy( enemy.position ) )

		# �п��ܱ���������
		if entity.state == csdefine.ENTITY_STATE_DEAD:
			return

		if state == csstatus.SKILL_GO_ON:						# ����ʩչ,,ֱ�ӷ���
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
			elif entity.chaseTarget( enemy, spell.getRangeMax( entity ) ):		# �����Զ,,׷��Ŀ��
				return
		else:
			# ��������
			INFO_MSG( "%i: skill %i use state = %i." % ( entity.id, self.param1, state ) )


class AIAction143( AIAction ):
	"""
	������������߷����ָ��ID�Ĺ���
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.range = 100
		self.className = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	�Ƴ����NPC��һ����־λ
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.removeFlag( self.param1 )


class AIAction145( AIAction ):
	"""
	�ڳ��Ը��������߷��ͱ�ǩ���ݣ�������ڣ� by ����
	�ڳ�����Ƿ񵽴�Ŀ��,������������������ʧ
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
		if distance < 10 and disEntity.spaceID == entity.spaceID :		#�ڳ�����NPC�ķ�Χ
			ownerID = entity.getOwnerID()
			if not BigWorld.entities.has_key( ownerID ):
				return
			owner = g(ownerID)
			questID = entity.queryTemp('questID')
			memberIDDict = entity.queryTemp( "dartMembers", {} )
			tongDartMembers = 0
			if len(memberIDDict) > 0:
				# ȡ�ó�Ա���������������
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

				# �����߸��ݲ����������Լ����⣩�õ�����
				for mid in memberIDDict.iterkeys():
					member = g(mid)
					if memberIDDict[mid] == -1 or member is None:
						continue

					for qID in member.questsTable.keys():		# ���ó�Ա��������finish
						if qID in member_ql:
							member.questTaskIncreaseState( qID, member_taskIndex )
							member.setTongDartJoinNum( questID, tongDartMembers )

			owner.setTongDartJoinNum( questID, tongDartMembers )
			owner.questTaskIncreaseState( questID, entity.queryTemp('eventIndex') )
			# ������ɺ� ���ڳ���ʧ��㲥������� by����
			if not entity.queryTemp( 'questFinish' ):
				self.dartMissionBrocad( questID, owner )
			entity.setTemp( 'questFinish', True )
			entity.removeTemp( "dartMembers" )

	def dartMissionBrocad( self, questID, player ):
		"""
		���ڻ���ڳɹ��Ĺ㲥 by����14:10 2009-7-31
		@param missionType : ��������
		@param missonnType : UINT8
		"""
		#self.family_grade
		player.brocastMessageDart( questID )


class AIAction146( AIAction ):
	"""
	���ӹ��NPC��һ����־λ
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.addFlag( self.param1 )


class AIAction147( AIAction ):
	"""
	���һ��EAI���
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.eaiIDs = []

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		for i in self.eaiIDs:
			if not entity.isEAI( i ):
				continue
			entity.eaiIDArray.remove( i )


class AIAction148( AIAction ):
	"""
	��ͻ��˷���һ��������ʾ��Ϣ
	gjx 2010-12-24( merry christmas! )
	��ɫʹ�õ�AIAction
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.visible = False

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.msg = section.readString( "param1" )
		self.visible = section.readBool( "param2" )   # ���δ��д��Ĭ�Ϸ���ΪFalse

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if self.msg == "" :
			ERROR_MSG( "AI(%i)'s msg is blank!" % ai.getID() )
			return
		entity.client.chat_onScenarioMsg( self.msg, self.visible )


class AIAction149( AIAction ):
	"""
	��ʾ/���ؿͻ��˵Ľ���
	gjx 2010-12-24( merry christmas! )
	��ɫʹ�õ�AIAction
	"""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.visible = section.readBool( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.client.visibleRootUIs( self.visible )

class AIAction150( AIAction ):
	"""
	�ı�������
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.direction = ( 0.0, 0.0, 0.0 )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		direction = section.readString( "param1" )
		if direction:
			dir = vector3TypeConvert( direction )
			if dir is None:
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param1" % ( self.getAIDataID(), self.getID(), direction ) )
			else:
				self.direction = dir

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.openVolatileInfo()
		entity.direction = self.direction

class AIAction151( AIAction ):
	"""
	С����ɵ�������ߣ����ں�����֮��ľ���Ƚ�Զ����Ҫ�ɵ����Ա�,Ҳ�������ڷɵ���ͬ��space��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.gotoOwner()

class AIAction152( AIAction ):
	"""
	ʹ��һ����Χ�ڵĹ���ս��Ʒӵ�����������Ŀ��csdefine.QUEST_OBJECTIVE_EVOLUTION
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.range = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.range = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	��һ����Χ�ڵ�ĳ���͵�Entity����ս���б�
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.range = 0
		self.enableType = []

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		rangeEntities = entity.entitiesInRangeExt( self.range, None, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in rangeEntities:
			if e.getEntityType() in self.enableType:
				g_fightMgr.buildEnemyRelation( entity, e )

class AIAction154( AIAction ):
	"""
	��һ����Χ�ڵ�ĳID��Entity����ս���б�
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.range = 0
		self.enableClassName = []

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.range = section.readInt( "param1" )
		self.enableClassName = [  cname  for cname in section.readString( "param2" ).split("|")]

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		rangeEntities = entity.entitiesInRangeExt( self.range, None, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in rangeEntities:
			if e.className in self.enableClassName:
				g_fightMgr.buildEnemyRelation( entity, e )

class AIAction155( AIAction ):
	"""
	����ָ�����������
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.pos = None

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

		position = section.readString( "param1" )
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param1 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.pos = pos

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.spawnPos = self.pos


class AIAction156( AIAction ):
	"""
	�趨��ǰλ��δ������
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )


	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.spawnPos = tuple( entity.position )


class AIAction157( AIAction ):
	"""
	��������ģ��
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.modelNumber = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.modelNumber = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.setModelNumber( self.modelNumber )

class AIAction158( AIAction ):
	"""
	�Թ���ӵ����ʹ��һ������
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0
		self.param2 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if self.param1 == 0: return
		# ��ȡ���õĹ�������
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
		range = spell.getRangeMax( entity )					# ��ȡ���ܵ����ʩ������
		state = entity.spellTarget( self.param1, ownerID )

		if checkAndMove( entity ):
			return

		# �п��ܱ���������
		if entity.state == csdefine.ENTITY_STATE_DEAD: return

		if state != csstatus.SKILL_GO_ON:
			# ��������
			INFO_MSG( "%i: skill %i use state = %i." % ( ownerID, self.param1, state ) )


class AIAction159( AIAction ):
	"""
	����entity�����ɸ�����ֵ�������Ǹ�ֵ�ķ�ʽ��ֵֻ������ֵ�����ô���Ϊʱ������ѯ������Щ���Կ������á�

	����Monster��potential
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
	�޸�entity���ڵ�ͼ�Ƿ�������еı��
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.canFly = True

	def init( self, section ):
		"""
		"""
		AIAction.init( self, section )
		self.canFly = str( bool( section.readInt( "param1" ) ) )	# ���й���Ҫ��ĸ�ʽ

	def do( self, ai, entity ):
		"""
		"""
		BigWorld.setSpaceData( entity.spaceID, csconst.SPACE_SPACEDATA_CAN_FLY, self.canFly )

class AIAction161( AIAction ):
	"""
	ʹ���µ�Ǳ�ܱ���ˢ��npcǱ��ֵ
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.potentialRate = 1	# Ǳ�ܱ���

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
	�ٻ�����ר�ã��������˵��˺��б�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	ѡȡһ����Χ��ĳЩ���͵Ĺ�������е�һ����Ϊ��ǰĿ��
	"""
	def __init__( self ):
		AIAction.__init__( self )

		self.param1 = 0.0
		self.param2 = "Monster"

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

		self.param1 = section.readFloat( "param1" )							# ��Χ
		self.param2 = section.readString( "param2" ).split("|")				# EntityTypes

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	����npc entity������
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.name = ""	# Ҫ���õ�����

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
	�ô�����������ƶ�
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
	����һ���������ڽ�������add by wuxo 2011-10-12
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.range   = 0
		self.questID =0

	def init( self, section ):
		"""
		��ʼ��
		"""
		AIAction.init( self, section )
		rQuestID = section.readString( "param1" )
		rQuestIDL = rQuestID.split(";")
		if len(rQuestIDL) == 2:
			self.range = int(rQuestIDL[0])
			self.questID = int(rQuestIDL[1])

	def do( self, ai, entity ):
		"""
		ִ��
		"""
		members = entity.entitiesInRangeExt( self.range, "Role", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for p in members:
			quest = p.getQuest( self.questID )
			if quest:
				state = quest.query( entity )
				if state == csdefine.QUEST_STATE_NOT_HAVE:
					quest.gossipDetail( p, None )	#�ͻ��˵�����ȡ�������




class AIAction167( AIAction ):
	"""
	���˾�������һ
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
	���˾��������
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
	���˾���������
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
	Ǳ�ܸ���bossר��ai������������һ���Լ���������Ϣ�Ա㴥����������������������
	"""
	def do( self, ai, entity ):
		# Ǳ�ܸ����Ѿ����ڵ�ʵ�ֻ���������ռ������е�entity����֮�䶼����real entity
		try:
			spaceEntity = BigWorld.entities[ entity.getCurrentSpaceBase().id ]
		except:
			EXCEHOOK_MSG( "not find the spaceEntity!" )
			spaceEntity = None
		spaceEntity.getScript().onKillMonster( spaceEntity, True )	# ���spaceEntity��None���Ǿ���������

class AIAction171( AIAction ):
	"""
	��Ӿ�����һ�����ӵĽ���
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
	��Ӿ����ڶ������ӵĽ���
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
	��Ӿ������������ӵĽ���
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
	��entity���ڵ�λ�ô���һ���µ�entity
	��������entity��className��λ�ã����
	û����λ�ã���ʹ��entity��λ��
	"""
	def __init__( self ) :
		AIAction.__init__( self )
		self.param1 = None					# ������Entity��className
		self.param2 = None					# ������Entity��λ��
		self.param4 = None					# ������Entity�ĳ���

	def init( self, section ) :
		"""
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )

		position = section.readString( "param2" )
		if position and position != '0':
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param2 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.param2 = pos

		self.param3 = section.readInt( "param3" )

		direction = section.readString( "param4" )
		if direction and direction != '0':
			dir = vector3TypeConvert( direction )
			if dir is None:
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param4" % ( self.getAIDataID(), self.getID(), direction ) )
			else:
				self.param4 = dir

	def do( self, ai, entity ) :
		"""
		"""
		dict = {}
		position = entity.position
		if self.param2 is not None :			# ���������λ�ã���ʹ�����õ�λ��
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
	��Ὰ����һ�����ӵĽ���
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
	��Ὰ���ڶ������ӵĽ���
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
	��Ὰ�����������ӵĽ���
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
	�޸Ŀͻ�������Ĵ���״̬add by wuxo 2011-11-26
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.eventIDs = ""

	def init( self, section ):
		"""
		��ʼ��
		"""
		AIAction.init( self, section )
		self.eventIDs = section.readString( "param1" )


	def do( self, ai, entity ):
		"""
		ִ��
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
	����һ�����͵�entity by wuxo 2011-11-28
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.entityType = None
		self.className = None
		self.range = None

	def init( self, section ):
		"""
		��ʼ��
		"""
		AIAction.init( self, section )
		self.entityType = section.readString( "param1" )
		self.className = section.readString( "param2" )
		self.range = section.readInt( "param3" )

	def do( self, ai, entity ):
		"""
		ִ��
		"""
		entities = entity.entitiesInRangeExt( self.range, self.entityType, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for i in entities:
			if i.className ==  self.className:
				#i.destroy()
				i.addTimer( 0.1, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )


class AIAction180( AIAction ) :
	"""
	��ͼ�ű������ж��巽����onConditionChange
	entity�͸���������֪ͨ�������������ı�
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = ""								# �ؼ���
		self.param2 = ""								# ��ֵ

	def init( self, section ) :
		"""
		��ʼ��
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )
		self.param2 = section.readString( "param2" )

	def do( self, ai, entity ):
		"""
		֪ͨ��������б�
		"""
		try:
			spaceEntity = BigWorld.entities[ entity.getCurrentSpaceBase().id ]
		except:
			DEBUG_MSG( "can't get spaceEntity!" )
			return
		spaceEntity.onConditionChange( { self.param1 : self.param2 } )	# ���spaceEntity��None���Ǿ���������


class AIAction181( AIAction ) :
	"""
	��NPC��ID��ӵ����ڸ�������Ϊ��ʱ���ԣ��Թ�
	��������֮��
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = ""								# �ؼ���(����AIʱӦ������̶�)

	def init( self, section ) :
		"""
		��ʼ��
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )

	def do( self, ai, entity ) :
		"""
		��NPC��ID��ӵ�������
		"""
		try:
			spaceEntity = BigWorld.entities[ entity.getCurrentSpaceBase().id ]
		except:
			return
		spaceEntity.setTemp( self.param1, entity.id )

class AIAction182( AIAction ):
	"""
	���������ͨ����
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
		
		# ���������ж�
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
	��ָ����Χ�ڵ�NPC����Ϊ��ǰĿ��(����Ŀ�귢������)
	"""
	def __init__( self ) :
		AIAction.__init__( self )
		self.param1 = 0.0										# �����뾶
		self.param2 = ""										# NPC ID
		self.param3 = ""										# NPC ����

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
	NPC��������Ļ������֣������޶�������Χ
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.channel_msgs = ""
		self.range = 0.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.channel_msgs = section.readString( "param1" )
		self.range = section.readFloat( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		es = entity.entitiesInRangeExt( self.range, "Role", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in es:
			if e.spaceID == entity.spaceID:
				e.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", self.channel_msgs, [])

class AIAction185( AIAction ):
	# �������ս��Ʒӵ������Ϊ��ǰĿ��
	def do( self, ai, entity ):
		bootyOwnerID = entity.bootyOwner[0]
		if bootyOwnerID:
			entity.setAITargetID( bootyOwnerID )

class AIAction186( AIAction ):
	"""
	����ǰĿ�����һ������
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.questID = 0					# ����ID
		self.timeDelay = 0					# ���೤ʱ�䵯���������

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.questID = section.readInt( "param1" )
		self.timeDelay = section.readInt( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	�ı䳯����ָ����Χ�ڵ�ָ��entity edit by wuxo 2012-1-18
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self._className = 0		#ָ����entity��className
		self._range = 0			#һ���ķ�Χ
		self._type = None		#ָ����entity������

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self._className = section.readString( "param1" )
		self._range = section.readInt( "param2" )
		self._type = section.readString( "param3" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai	: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai	:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	������Ӫ����
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self._battleCamp = 0	# ��Ӫ����Ĭ��Ϊ0�������ֱ�ʾ

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
		@param	ai	: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai	:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.battleCamp = self._battleCamp


class AIAction189( AIAction ):
	"""
	��������Ŀ��һ������
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
	Զ�빥��Ŀ��һ������,ͨ������ѡ����ú��˵ķ�ʽ����ת��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.distance = section.readInt( "param1" )
		self.backTo = bool( section.readString( "param2" ) )		# �Ƿ����ƶ�


	def do( self, ai, entity ):
		"""
		"""
		target = BigWorld.entities.get( entity.targetID, None )
		if target:
			pos = calLinePosition( entity, target, self.distance )
			entity.gotoPosition( pos, not( self.backTo ) )


class AIAction191( AIAction ):
	"""
	ˮƽ���򹥻�Ŀ��
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
	��ս��Ŀ�걣��һ�������߶�
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
	�ߵ������Χ�������һ����Χ��ĳһλ�á�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
	��¼һ����Ҫ�ߵ���λ�á�
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def do( self, ai, entity ):
		"""
		"""
		entity.setTemp( "AIGotoPosition", entity.queryTemp( "gotoPosition", None ) )


class AIAction196( AIAction ):
	"""
	������Ҫ�����֮ǰAI��¼��λ�á�
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def do( self, ai, entity ):
		"""
		"""
		entity.setTemp( "AIGotoPosition", entity.queryTemp( "gotoPosition", None ) )

class AIAction197( AIAction ):
	"""
	��ָ���Ĺ����趨�жӵı��
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self._startPos = None

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self._className = section.readString( "param1" )
		self._range = section.readFloat( "param2" )

		position = section.readString( "param3" )
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param3 " % ( self.getAIDataID(), self.getID(), position ) )
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
	�ߵ��жӵ�λ��
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self._faceTo = 0				# �Ƿ������

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
		-1: ������
		1: ������
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
	��z���򹥻�Ŀ���ƶ�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
	��x���򹥻�Ŀ���ƶ�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
	���Լ��趨Ϊ�ӳ�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.captainSign = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		"""
		entity.setTemp( self.captainSign, entity.id )
		print "���Ƕӳ�:",entity.id


class AIAction202( AIAction ):
	"""
	��AIְ��ӳ���ID�������Χ�Ĺ���
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
	������Ч��ս���ֶӶ�Ա
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
	�����ֶӲ����Ա
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
	�ߵ�һ��ս���ֶӶ�Ա
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
	�ߵ�����Ŀ�����߻��ұ�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
	NPC�ٻ�һ��ս��Ʒ�����ڶԻ���ҵĹ���
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.ownerID = 0
		self.position = None
		self.className = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.className = section.readString( "param1" )				# �ٻ�����className

		position = section.readString( "param2" )					# ����ˢ�µ�λ��
		if position and position != '0':
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param2 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.position = pos

	def do( self, ai, entity ):
		if self.position is None:
			position = entity.position + Math.Vector3( random.randint(-2,2), 0,random.randint(-2,2) )
		else:
			position = self.position

		self.ownerID = entity.queryTemp( "talkPlayerID", 0 )		# NPC��¼�Ĺ���ӵ����ID
		if self.ownerID:
			monster = entity.createObjectNearPlanes( self.className, position, entity.direction, { "firstBruise":1,"bootyOwner":( self.ownerID, 0 ) } )
			monster.setTemp( "ownerID", self.ownerID )
			entity.removeTemp( "talkPlayerID" )
		else:
			DEBUG_MSG( "not find the owner!" )


class AIAction208( AIAction ):
	"""
	���õ�ǰ��Ŀ�����Ϊ����ӵ�����ɲ���������ʲôӵ����  edit by wuxo 2012-3-6
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
		@param	ai	: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai	:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	# �Ѱ뾶�ڵ�һ������entityץ���Լ����( �̾��� )
	def __init__( self ):
		AIAction.__init__( self )
		self.radius = 0
		self.entityNames = []

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
	NPC�����Լ�ֻ��ս��Ʒӵ���߿ɼ�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai	: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai	:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if not entity.hasFlag( csdefine.ENTITY_FLAG_UNVISIBLE ):	# ���û�в��ɼ���ǣ��򷵻�
			return 
		bootyOwner = entity.bootyOwner
		if bootyOwner[1] != 0:										# �ж���
			bootyers = entity.searchTeamMember( bootyOwner[1], Const.TEAM_GAIN_EXP_RANGE )
			if len( bootyers ) == 0:
				return

			if not entity.queryCombatRelationIns( bootyOwner[1] ):
				entity.addCombatRelationIns( csdefine.RELATION_DYNAMIC_TEAM_ANTAGONIZE, bootyOwner[1] )
			entity.ownerVisibleInfos = bootyOwner
		elif bootyOwner[0] != 0:										# û����
			if not BigWorld.entities.has_key( bootyOwner[0] ):			# ������ҿ��ܵ��߻����˳���Ϸ�����
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
	NPC֪ͨ����ӵ��������ʧ��
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0
		self.param2 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
	��Կɿ��Ƶ�ˢ�µ�SpawnPointControl������AI����
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
	Ѱ��ָ����Χ���ض�����Ŀ�꣬Ŀ��Ѫ������ָ��ֵ������ʩ��ָ�����ܣ����Զ���ͷţ�������AIAction80��
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
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readFloat( "param1" )			# ��Χ
		self.param2 = section.readString( "param2" )		# className
		self.param3 = section.readInt64( "param3" ) * 1000	# ���ܱ��
		self.param4 = section.readFloat( "param4" ) / 100	# Ѫ������

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	�ٻ�������ٻ��Ĺ����ִ�д�AI��entity��ͬ����ӵ���ߣ��ұ��ٻ��Ĺ��������ӵ���ߣ��ǣ��ɼ�
	"""
	def __init__( self ) :
		AIAction.__init__( self )
		self.className = None					# ������Entity��className
		self.position = None					# ������Entity��λ��
		self.MonsNumber = None					# ������Entity������
		self.direction = None					# ������Entity�ĳ���

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
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param2 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.position = pos

		direction = section.readString( "param4" )
		if direction and direction != '0':
			dir = vector3TypeConvert( direction )
			if dir is None:
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param4" % ( self.getAIDataID(), self.getID(), direction ) )
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
			monster.addFlag( csdefine.ENTITY_FLAG_UNVISIBLE )				# ��Ӳ��ɼ���ǩ
			monster.firstBruise = 1

			if monster is None :
				ERROR_MSG( "Create entity false in ai action214!" )
				break

			tempEnemyID = []
			monster.setTemp( "ownerID", entity.queryTemp("ownerID", 0) )

			if bootyOwner != ( 0, 0 ):					# ��ӵ����
				for enemyID in entity.enemyList:
					tempEnemyID.append( enemyID )
			else:
				ERROR_MSG( "monster %s not have bootyOwner"% entity.className )

			monster.setTemp( "enemyIDs", tempEnemyID )
			monster.ownerVisibleInfos = bootyOwner


class AIAction215( AIAction ):
	"""
	�̹��ػ����ű�����ר��AI
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	���214һ��ʹ��,ʹ���ٻ������Ĺ���ṥ���ʵ������
	"""
	def do( self, ai, entity ):
		"""
		"""
		entity.bootyOwner = entity.ownerVisibleInfos
		owner = BigWorld.entities.get( entity.bootyOwner[0], None )
		if owner:
			g_fightMgr.buildEnemyRelation( entity, owner )	# ��ӵ�������ȼ���ս���б�
		g_fightMgr.buildGroupEnemyRelationByIDs( entity, entity.queryTemp("enemyIDs",[]) )


class AIAction217( AIAction ):
	"""
	�ѵ�ǰĿ������Ϊ�Լ������ˣ��޶��������˵Ĺ���ʹ�ã�
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.entityType = "Role"

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		if section.readString( "param1" ) != "":
			self.entityType = section.readString( "param1" )						# EntityType

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai	: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai	:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	�����Ŷ�ָ����Ա�ĵ�ǰĿ���λ�ã����ó���
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.pos = None


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		position = section.readString( "param1" )
		if position:
			pos = vector3TypeConvert( position )
			if not pos:
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param1 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.pos = pos

		self.className 	= section.readString( "param2" )
		self.range 		= section.readFloat( "param3" )
		self.width 		= section.readInt( "param4" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai	: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai	:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	���ѡȡ���˵ĵ�����Ϊ����Ŀ�꣨�ػ�ר�ã�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	�ı�������Ϊ���˳���
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		ownerEntity = entity.getOwner()
		if hasattr( ownerEntity, "cell" ):
			return

		entity.openVolatileInfo()
		entity.direction = ownerEntity.direction

class AIAction221( AIAction ):
	"""
	NPC����,���������ݿɼ�
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if len( self.param1 ) > 0:
			entity.sayBupple( self.param1 )

class AIAction222( AIAction ):
	"""
	��������Χһ�������뾶��Բ�ƶ�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.range = section.readFloat( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if entity.actionSign( csdefine.ACTION_FORBID_MOVE ):
			DEBUG_MSG( "I cannot  move!" )
			return
		moveOut( entity, entity, self.range, self.range )

class AIAction223( AIAction ):
	"""
	Ӣ������NPCѡ��Ѳ��·��ר��AI
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		spaceBase = entity.getCurrentSpaceBase()
		if spaceBase is None: return
		spaceEntity = BigWorld.entities.get( spaceBase.id )
		spaceEntity.monster_choosePatrolList( entity.id )

class AIAction224( AIAction ):
	"""
	���͵�entity��Χ�ڵ���Ҵ��͵�
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.position = None
		self.direction = None

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.range = section.readFloat( "param1" )				# ���͵㷶Χ
		self.spaceName = section.readString( "param2" )			# ������ĳ����ͼ

		position = section.readString( "param3" )				# ������ĳ��λ��
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param3 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.position = pos

		self.lifeTime = section.readFloat( "param4" )			# ���͵����������ʱ��
		direction = section.readString( "param5" )				# ����λ�ó���
		if direction and direction != '0':
			dir = vector3TypeConvert( direction )
			if dir is None:
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param4" % ( self.getAIDataID(), self.getID(), direction ) )
			else:
				self.direction = dir

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	֪ͨ�Ǽʸ��������������ҳ�����
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.leaveTime = 0.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.leaveTime = section.readFloat( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		spaceBase = entity.getCurrentSpaceBase()
		if spaceBase is None:	return
		spaceEntity = BigWorld.entities[ spaceBase.id ]
		spaceEntity.infoSpaceCopyStar( self.leaveTime )					# ֪ͨ�Ǽʸ������ú���

class AIAction226( AIAction ):
	"""
	Ѱ�Ҿ���ù��������Ѳ�ߵ㣬�����Ǹ��㿪ʼִ��Ѳ��
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.graphID = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.graphID = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	����ɢ��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
				# ��Χ����һЩû���ƶ���entity���Լ������뿪������ƶ���һ��λ��
				if moveOut( entity, dstEntity, random.random() * (self._rangeMax - self._rangeMin) + self._rangeMin, self._moveMax ):
					return


class AIAction228( AIAction ):
	"""
	���Ӹ���Boss�Ļ�ɱ����
	"""
	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		spaceBase = entity.getCurrentSpaceBase()
		if hasattr( spaceBase, "incBossesKilled" ) :
			spaceBase.incBossesKilled()
		else :
			ERROR_MSG( "current spacebase dosn't support recording boss killed. entity id: %i" % entity.id )

class AIAction229( AIAction ):
	"""
	���ø���Raid��ɱ��
	"""
	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		spaceBase = entity.getCurrentSpaceBase()
		if hasattr( spaceBase, "setRaidFinish" ) :
			spaceBase.setRaidFinish( True )
		else :
			ERROR_MSG( "current spacebase dosn't support recording raid finished. entity id: %i" % entity.id )

class AIAction230( AIAction ):
	"""
	ѡȡ�˺��б���ĳһ���͵�className��entity�������е�һ����Ϊ��ǰĿ��(AIĿ��)
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.entityType = "Monster"
		self.className = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		if section.readString( "param1" ):
			self.entityType = section.readString( "param1" )
		self.className = section.readString( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		for id in entity.damageList:
			e = BigWorld.entities.get( id )
			if e and e.__class__.__name__ == self.entityType:
				if self.className and e.className != self.className:	# classNameΪ����ֻ�������Entity����
					continue
				entity.setAITargetID( id )
				break 

class AIAction231( AIAction ) :
	"""
	��ͼ�ű������ж��巽����onYXLMCopyBossCreated
	entity�͸���������֪ͨ����ĳ�����Ѿ�ˢ��
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.signType = 1

	def init( self, section ) :
		"""
		��ʼ��
		"""
		AIAction.init( self, section )
		if section.readInt( "param1" ):
			self.signType = section.readInt( "param1" )					# signType ��ʾ��С��ͼ�ı�־����

	def do( self, ai, entity ):
		try:
			spaceEntity = BigWorld.entities[ entity.getCurrentSpaceBase().id ]
		except :
			return
		spaceEntity.onYXLMCopyBossCreated( entity.id, entity.className, entity.spawnPos, self.signType  )	# ���spaceEntity��None���Ǿ���������

class AIAction232( AIAction ) :
	"""
	��ͼ�ű������ж��巽����onYXLMCopyBossDied
	entity�͸���������֪ͨ����ĳ�����Ѿ�������һ�����������¼�����
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ) :
		"""
		��ʼ��
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
	��ָ��λ��ָ����Χ���ٻ�����ָ���ȼ���Ĺ�����ٻ��Ĺ��︴���ٻ��ߵ�ս���б��ս��Ʒӵ����
	"""
	def __init__( self ) :
		AIAction.__init__( self )
		self.className = ""						# ������Entity��className
		self.amount = 1							# ������Entity������
		self.position = None					# ������Entity��λ��
		self.range = 0							# �����Χ
		self.levelOffset = 0					# �ȼ���
		self.copyBootyOwner = 1					# �Ƿ���ս��Ʒӵ����
		self.copyEnemyList = 1					# �Ƿ��Ƶ����б�
		self.maxHeightDiff = 3.0				# ˢ��λ�����ٻ���λ�õĸ߶Ȳ����ֵ��������ֵ��ȡ�ٻ���λ��Ϊˢ��λ�� CSOL-230

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
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param2 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.position = pos

	def do( self, ai, entity ) :
		"""
		"""
		try:
			spaceBase = BigWorld.cellAppData["spaceID.%i" % entity.spaceID]
			spaceEntity = BigWorld.entities[ spaceBase.id ]		# �ҵ�����
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
			#λ��������ײ
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
	��ͼ�ű������ж��巽����updateYXLMCopyBossPos
	entity�͸�������������Boss�ڿͻ��˵�λ����Ϣ��ʾ
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ) :
		"""
		��ʼ��
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		spaceBase = entity.getCurrentSpaceBase()
		if spaceBase is None:
			return 
		spaceEntity = BigWorld.entities.get( spaceBase.id )
		spaceEntity.updateYXLMCopyBossPos( entity.id, entity.className, entity.position  )	# ���spaceEntity��None���Ǿ���������

class AIAction235( AIAction ):
	"""
	ѡȡһ����Χ���ض����͵����Լ�����ĵĹ�����Ϊ��ǰĿ��(AIĿ��)
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.entityType = "Monster"
		self.classNames = []
		self.range = 0.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		if section.readString( "param1" ):
			self.entityType = section.readString( "param1" )					# EntityType
		self.classNames = section.readString( "param2" ).split( "|" )			# className �б�
		self.range = section.readFloat( "param3" )								# ��Χ

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		eid = 0
		distance = 100.0
		monsterList = entity.entitiesInRangeExt( self.range, self.entityType, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in monsterList:													# ѡ�����Ŀ���ID
			if not self.classNames or ( self.classNames and  e.className in self.classNames ):
				dis = csarithmetic.distancePP3( e.position, entity.position )
				if distance > dis:
					eid = e.id
					distance = dis
		
		e = BigWorld.entities.get( eid )
		if e and e.state != csdefine.ENTITY_STATE_DEAD and entity.targetID != eid :
			entity.setAITargetID( eid )											# �ı�AIĿ��Ϊ�����Ŀ��
			
class AIAction236( AIAction ) :
	"""
	entity�������
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ) :
		"""
		��ʼ��
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		dstEntity = BigWorld.entities.get( entity.targetID )
		if dstEntity is None:
			return
		entity.gotoPosition( dstEntity.position )
		entity.spawnPos = tuple( entity.position )

class AIAction237( AIAction ):
	"""
	��AIĿ��ʹ�ü���
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.skillID = section.readInt64( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		target = BigWorld.entities.get( entity.aiTargetID )		# �����ж�
		if not target:
			ERROR_MSG( " AIData %i use skill %i error, can't get ( %i %s )'s aiTargetID %i" % ( self.getAIDataID(), self.skillID, entity.id, entity.className, entity.aiTargetID ) )
			return 

		try:
			spell = g_skills[ self.skillID ]					# ��ȡ���õĹ�������
		except:
			ERROR_MSG( "AIDAta %i get skill error, check whether %i is exist." %  ( self.getAIDataID(), self.skillID ) )
			return
			
		if checkAndMove( entity ):								# ���ڽ��һ�ѹ���׷��ͬһ��Ŀ��ʱ�ص���һ�������
			return
		state = entity.spellTarget( self.skillID,  entity.aiTargetID )

		if entity.state == csdefine.ENTITY_STATE_DEAD:			# �п��ܱ���������
			return

		if state != csstatus.SKILL_GO_ON:
			# ��������
			INFO_MSG( "%i: skill %i use state = %i." % ( entity.id, self.skillID, state ) )

class AIAction238( AIAction ):
	"""
	���Լ��ĵ����б��Ƹ���Χ��ĳЩNPC
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.range = section.readInt( "param1" )				# ������Χ
		self.npcClassNameList = section.readString( "param2" ).split("|")			# npc className list

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		es = entity.entitiesInRangeExt( self.range, None, entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in es:
			if e.className in self.npcClassNameList:
				g_fightMgr.buildGroupEnemyRelationByIDs( e, entity.enemyList.keys() )


class AIAction239( AIAction ):
	"""
	�����ƶ�������Ŀ����Χһ����Χ��
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.range = 0.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.range = section.readFloat( "param1" )					# �빥��Ŀ��ľ���

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
			# ѡȡ��Բ���ϵĵ�
			yaw = ( entity.position - target.position ).yaw
			angle = random.uniform( yaw - math.pi/2, yaw + math.pi / 2 )
			direction = Math.Vector3( math.sin( angle ), 0.0, math.cos( angle ) )
			direction.normalise()					# ��������λ��
			pos = Math.Vector3( target.position ) + a * direction

			posList = BigWorld.collide( entity.spaceID, ( pos.x, pos.y+10, pos.z ), ( pos.x, pos.y-10, pos.z ) )
			if not posList:
				continue
			pos = posList[0]
			entity.gotoPosition( pos )
			return 

class AIAction240( AIAction ):
	"""
	NPC����Ի���

	���־��� ��NPCʼ����ӵ���������ֵ�һ�ξ���.
	"""
	def __init__( self ):
		AIAction.__init__( self )
		
	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readFloat( "param1" )	# ����

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	�Ƴ�NPC�Ի������־
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.removeTemp( "talkFollowID" )

class AIAction242( AIAction ):
	"""
	�������������
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.__questID	 		= section.readInt( "param1" )
		self.__taskIndex	 	= section.readInt( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		fid = entity.queryTemp( "talkFollowID", 0 )
		if BigWorld.entities.has_key( fid ):
			followEntity = BigWorld.entities[ fid ]
			followEntity.questTaskIncreaseState( self.__questID, self.__taskIndex )

class AIAction243( AIAction ) :
	"""
	entity�͸���������֪ͨ����ĳ�����Ѿ�ˢ��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ) :
		"""
		��ʼ��
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
	entity�͸���������֪ͨ����ĳ�����Ѿ�������һ�����������¼�����
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ) :
		"""
		��ʼ��
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
	NPC/MONSTER���Լ�����
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.die( 0 )

class AIAction246( AIAction ):
	"""
	NPC��������Ļ������֣������޶�������Χ
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.channel_msgs = []
		self.range = 0.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		msg, soundID =self.randomGetMsg()
		entity.say( msg )
		entity.planesAllClients( "onMakeASound", ( soundID, 0 ) )
				
class AIAction247( AIAction ) :
	"""
	�ڸ����еļ��������������ѡһ��������
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.lifetime = 0				# ��������ʱ��
		self.repeattime = 0				# ѭ���˺�ʱ��
		self.radius = 0.0				# ����뾶
		self.enterSpell = 0				
		self.leaveSpell = 0				
		self.destroySpell = 0			
		self.enter_Spell = 0				# ��������ʩ�ŵļ���
		self.leave_Spell = 0				# �뿪����ʩ�ŵļ���
		self.destroy_Spell = 0			# ��������ʱ�ͷŵļ���
		self.modelNumber =  ""			# �����Ӧ��ģ��(����Ч��)
		self.isDisposable = False		# �Ƿ�һ�������壨������һ�ξ����٣�
		self.position = None

	def init( self, section ) :
		"""
		��ʼ��
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
		֪ͨ��������б�
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
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param2 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.position = pos
		pos = self.position
		if self.position is None:
			pos = tuple( entity.position )

		entity.createEntityNearPlanes( "AreaRestrictTransducer", pos, (0, 0, 0), dict )

class AIAction248( AIAction ):
	"""
	npc_ownerBase�������
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.__questID	 		= section.readInt( "param1" )
		self.__taskIndex	 	= section.readInt( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		fid = entity.getOwner().id
		if BigWorld.entities.has_key( fid ):
			e = BigWorld.entities[ fid ]
			e.questTaskIncreaseState( self.__questID, self.__taskIndex )

class AIAction249( AIAction ):
	"""
	�ٻ�����
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0
		self.param2 = ""
		self.param3 = 0.0


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )	# �ٻ���������
		self.param2 = section.readString( "param2" )	# �ٻ�����className
		self.param3 = section.readFloat( "param3" )		# entity�泯����һ������

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		try:
			spaceBase = BigWorld.cellAppData["spaceID.%i" % entity.spaceID]
			spaceEntity = BigWorld.entities[ spaceBase.id ]		# �ҵ�����
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
			# ������¼�ٻ����Ĺ���id
			tempCallMonsterIDs = spaceEntity.queryTemp( "tempCallMonsterIDs", [] )		# ȡ�ø�����¼�ٻ����Ĺ���id�б�
			tempCallMonsterIDs.append( monster.id )
			spaceEntity.setTemp( "tempCallMonsterIDs", tempCallMonsterIDs )
			enemyList = entity.enemyList
			if len( enemyList ):
				ownerID = enemyList.keys()[0]
				monster.setTemp( "ownerID", ownerID )
			g_fightMgr.buildGroupEnemyRelationByIDs( monster, enemyList.keys() )

class AIAction250( AIAction ):
	"""
	�����볡����
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if not self.isFirstHide or ( self.isFirstHide and entity.firstHide ):
			target_pos = entity.getDstPos( self.jumpPointType, self.jumpPoint )
			if target_pos:
				time = entity.doPreEvent( target_pos, self.isMovedAction, self.preActionTime )
				entity.addTimer( time, 0, ECBExtend.PRE_REMOVE_FLAG )

class AIAction251( AIAction ):
	"""
	NPC��������Ļ������֣������޶�������Χ, ֧�ָ����˺����ѷ���ͬ��Ϣ
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.channel_msgs_friend = ""
		self.channel_msgs_enemy = ""
		self.range = 0.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.channel_msgs_friend = section.readString( "param1" )
		self.channel_msgs_enemy = section.readString( "param2" )
		self.range = section.readFloat( "param3" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	�ٻ�����ͬʱ������������ǰ�������ÿ�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		monster = entity.createObjectNearPlanes( self.param1, entity.position, entity.direction, {"spawnPos": tuple(entity.position ), "level": entity.level, "spawnMB": entity.spawnMB } )
		entity.resetEnemyList()
		entity.spawnMB = None
		entity.addTimer( 0.2, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )
		
class AIAction253( AIAction ) :
	"""
	��ͼ�ű������ж��巽����onYXLMMonsterGetDamage
	Ӣ������С��ͼ�������������ܵ�һ���̶��˺�ʱͼ����˸
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.flashTime = 0		#��˸ʱ��

	def init( self, section ) :
		"""
		��ʼ��
		"""
		AIAction.init( self, section )
		if section.readInt( "param1" ):
			self.flashTime = section.readInt( "param1" )					# signType ��ʾ��С��ͼ�ı�־����

	def do( self, ai, entity ) :
		spaceBase = entity.getCurrentSpaceBase()
		if spaceBase is None:
			return
		spaceEntity = BigWorld.entities[ spaceBase.id ]
		spaceEntity.onYXLMMonsterGetDamage( entity.id, self.flashTime )

class AIAction254( AIAction ) :
	"""
	�´�AI��Ϊ�ڼ����ִ��
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.thinkSpeed = 1.0		#��˸ʱ��

	def init( self, section ) :
		"""
		��ʼ��
		"""
		AIAction.init( self, section )
		self.thinkSpeed = section.readFloat( "param1" )					# signType ��ʾ��С��ͼ�ı�־����

	def do( self, ai, entity ) :
		entity.thinkSpeed = self.thinkSpeed


class AIAction255( AIAction ) :
	"""
	����ִ��AI����
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def do( self, ai, entity ) :
		entity.think(0.1)

class AIAction256( AIAction ) :
	"""
	�ø�����ָ��className entity����һ��sai
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.recvIDs = []
		self.aiType = 0
		self.sid = 0

	def init( self, section ) :
		"""
		��ʼ��
		"""
		AIAction.init( self, section )
		self.recvIDs = section.readString( "param1" ).split( ";" )
		self.aiType = section.readInt( "param2" )
		self.sid = section.readInt( "param3" )

	def do( self, ai, entity ) :
		entity.sendSAICommand( self.recvIDs, self.aiType, self.sid )

class AIAction257( AIAction ) :
	"""
	�ߵ�����SAI entity��λ��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def do( self, ai, entity ):
		mb = entity.queryTemp( "SEND_SAI_ENTITY", None )
		if mb and BigWorld.entities.has_key( mb.id ):
			entity.gotoPosition( BigWorld.entities[ mb.id ].position, False )

class AIAction258( AIAction ) :
	"""
	��������SAI entity��Ѳ��·��
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
	��AIĿ��һ���Ƕ�ǰ��
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.radian = 0
		self.distMin = 0			# С�ڴ˾��룬����
		self.distMax = 0			# ���ڴ˾��룬�����У�����׷��

	def init( self, section ) :
		"""
		��ʼ��
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
				entity.moveBack( entity.targetID, distance - self.distMin - 1 )		# ���˺�һ�ף���֤�˵��ε���Χ��
			elif distance <= self.distMax:
				radian = random.uniform( self.radian *( -1 ), self.radian )
				entity.moveRadiFollow( entity.targetID, radian, ( self.distMin, self.distMax ) )
			else:
				entity.chaseTarget( target, self.distMax - 1 )


class AIAction260( AIAction ) :
	"""
	���͵�ͼ�㲥
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self._msg = ""

	def init( self, section ) :
		"""
		��ʼ��
		"""
		AIAction.init( self, section )
		self._msg = section.readString( "param1" )

	def do( self, ai, entity ) :
		entity.getCurrentSpaceBase().onChatChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", self._msg, "" )
	
class AIAction261( AIAction ) :
	"""
	CollideMonster��������ai
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.isOpen = False

	def init( self, section ) :
		"""
		��ʼ��
		"""
		AIAction.init( self, section )
		self.isOpen = section.readBool( "param1" )

	def do( self, ai, entity ) :
		entity.isOpen = self.isOpen
		
class AIAction262( AIAction ) :
	"""
	���˸���Ĺ����޷�Ѱ·�����ô�AI����������setTemp������һ�������������⣬ĿǰҪ��� AIAction26 ʹ��
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.positionList = []
		
	def init( self, section ) :
		"""
		��ʼ��
		"""
		AIAction.init( self, section )
		positionList = section.readString( "param1" )
		if positionList and positionList != '0':
			for position in positionList.split( ";" ):
				pos = vector3TypeConvert( position )
				if pos is None:
					ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param1 " % ( self.getAIDataID(), self.getID(), position ) )
				else:
					self.positionList.append( pos )

	def do( self, ai, entity ) :
		if len( self.positionList ) > 0:
			entity.setTemp( "AI_Trace_Position", self.positionList )
			
class AIAction263( AIAction ) :
	"""
	��һ����Χ�ڵ������ʾ������ʾ��Ϣ
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
		��ʼ��
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
		֪ͨ�����ʾһ��������ʾ
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
	�������
	"""
	def __init__( self ):
		AIAction.__init__( self )
		
	def do( self, ai, entity ):
		entity.interruptSpell( csstatus.SKILL_INTERRUPTED_BY_AI )

class AIAction265( AIAction ) :
	"""
	ˮ������������֪ͨ����ˢ��ˮ��
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.monsterIDList = []			#ˮ��className�б�
		self.monsterPosList = []		#ˮ������λ���б�

	def init( self, section ) :
		"""
		��ʼ��
		"""
		AIAction.init( self, section )
		self.monsterIDList = section.readString( "param1" ).split( ";" )
		self.monsterPosList = section.readString( "param2" ).split( ";" )

	def do( self, ai, entity ):
		"""
		֪ͨ����ˢ��ˮ��
		"""
		try:
			spaceEntity = BigWorld.entities[ entity.getCurrentSpaceBase().id ]
		except:
			EXCEHOOK_MSG( "not find the spaceEntity!" )
			spaceEntity = None
		spaceEntity.getScript().spawnShuijing( spaceEntity, self.monsterIDList, self.monsterPosList )

class AIAction266( AIAction ) :
	"""
	��������츱���ȷ���ռ��������ӻ�����
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0.0
		self.param2 = ""
		self.integral = 0

	def init( self, section ) :
		"""
		��ʼ��
		"""
		AIAction.init( self, section )
		self.param1 = section.readFloat( "param1" )			#������Χ
		self.param2 = section.readString( "param2" )		#������className
		self.param3 = section.readInt64( "param3" )			#�ͷŵļ���ID
		self.lifeTime = section.readFloat( "param4" )			#��ú�����
		self.integral = section.readInt( "param5" )			#�ӻ��ֵ���ֵ


	def do( self, ai, entity ):
		"""
		�ȷ���ռ��������ӻ���
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
	Ѱ�Ҿ���ù��������Ѳ�ߵ㣬��Ѱ·�������Ѳ�ߵ�
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.graphID = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.graphID = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	��ʱ�ı��Լ���nameColorֵ
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.tmpColor = 0

	def init( self, section ) :
		"""
		��ʼ��
		"""
		AIAction.init( self, section )
		self.tmpColor = section.readInt( "param1" )
		
	def do( self, ai, entity ):
		"""
		֪ͨ�ı�nameColor
		"""
		if hasattr( entity, "nameColor" ):						#�����Լ����õ�nameColor
			nameColor = entity.nameColor
			entity.setTemp( "AI_old_nameColor", nameColor )
			entity.nameColor = self.tmpColor

class AIAction269( AIAction ) :
	"""
	����nameColor����ֵ����AIAction267���ʹ��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ) :
		"""
		��ʼ��
		"""
		AIAction.init( self, section )
		
	def do( self, ai, entity ):
		"""
		����nameColorֵ
		"""
		if hasattr( entity, "nameColor" ):						#�����Լ����õ�nameColor
			oldColor = entity.queryTemp( "AI_old_nameColor", 0 )
			entity.nameColor = oldColor

class AIAction270( AIAction ):
	"""
	issue:CSOL-1708
	�÷�Χ�ڹ���Ŀ����Ϊ���˵����б����ָ��Ŀ��
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.callMonsterID = ""
		self.callRange = 0.0
		self.attackTargetIndex = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.callMonsterID = section.readString( "param1" )
		self.callRange = section.readFloat( "param2" )
		self.attackTargetIndex = section.readInt( "param3" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	�л����ﲢ��Ŀ����Ϊ���˵����б����ָ��Ŀ��
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.callMonsterID = ""
		self.rangeRandom = 1.0
		self.attackTargetIndex = 0
	
	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.callMonsterID = section.readString( "param1" )
		self.rangeRandom = section.readFloat( "param2" )
		self.attackTargetIndex = section.readInt( "param3" )
	
	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		pos = entity.position
		position = ( pos[0] + random.randint( -self.rangeRandom, self.rangeRandom ), pos[1], pos[2] + random.randint( -self.rangeRandom, self.rangeRandom ) )
		#λ��������ײ
		collPos = csarithmetic.getCollidePoint( entity.spaceID, pos, Math.Vector3( position ) )
		
		e = entity.createObjectNearPlanes( self.callMonsterID, collPos, entity.direction, { "level" : entity.level } )
		g_fightMgr.buildGroupEnemyRelationByIDs( e, entity.enemyList.keys() )
		
		targetID = entity.getEnemyByIndex( self.attackTargetIndex )
		if targetID:
			e.targetID = targetID

class AIAction272( AIAction ):
	"""
	��AIĿ��һ���Ƕȿ���
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.radian = 0				# �ε����Ƕ�
		self.distMin = 0			# �����ε���С����
		self.distMax = 0			# �����ε�������
		self.move_speed_min = 0		# �����ε���С�ƶ��ٶ�
		self.move_speed_max = 0		# �����ε�����ƶ��ٶ�
		self.aiCommandID = 0		# ����AIָ��ID

	def init( self, section ) :
		"""
		��ʼ��
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
	��AIĿ��һ���Ƕ�Զ��
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.radian = 0				# �ε����Ƕ�
		self.distMin = 0			# Զ���ε���С����
		self.distMax = 0			# Զ���ε�������
		self.move_speed_min = 0		# Զ���ε���С�ƶ��ٶ�
		self.move_speed_max = 0		# Զ���ε�����ƶ��ٶ�
		self.aiCommandID = 0		# ����AIָ��ID

	def init( self, section ) :
		"""
		��ʼ��
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
	���͵�entity��Χ�ڵ���Ҵ��͵�( ͬ��ͼ��ת,������ֳ����л����� )
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.position = None
		self.direction = None

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.range = section.readFloat( "param1" )				# ���͵㷶Χ
		position = section.readString( "param2" )				# ������ĳ��λ��
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param3 " % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.position = pos

		self.lifeTime = section.readFloat( "param3" )			# ���͵����������ʱ��
		direction = section.readString( "param4" )				# ����λ�ó���
		if direction and direction != '0':
			dir = vector3TypeConvert( direction )
			if dir is None:
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param4" % ( self.getAIDataID(), self.getID(), direction ) )
			else:
				self.direction = dir

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	֪ͨ����Ѫ���ı�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if entity.getCurrentSpaceBase():
			entity.getCurrentSpaceBase().cell.onZhainanHPChange( entity.HP, entity.HP_Max )

class AIAction276( AIAction ):
	"""
	֪ͨ��������/�뿪ս��״̬
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if entity.getCurrentSpaceBase():
			if entity.state == csdefine.ENTITY_STATE_FIGHT:
				#��ʾŭ��ֵ����
				entity.getCurrentSpaceBase().cell.onShowAnger()
			else:
				entity.getCurrentSpaceBase().cell.onHideAnger()


class AIAction277( AIAction ):
	"""
	�����ǰĿ���ָ��buff 
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		enemy = BigWorld.entities.get( entity.targetID, None )
		if enemy :
			enemy.removeAllBuffByBuffID( self.param1, [csdefine.BUFF_INTERRUPT_NONE] )

class AIAction278( AIAction ):
	"""
	����ǰս���б��е�������Ӵ�����Ϣ
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		for enemyID in entity.enemyList:
			enemy = BigWorld.entities.get( enemyID, None )
			if enemy and enemy.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				enemy.setTemp( "requestTeleport", self.param1 )

class AIAction279( AIAction ):
	"""
	��������һ����Χ�ڵ������Լ��˺��б��е�������ϵ�һ������
	"""
	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
	��������һ����Χ�ڵ�������ϵ�һ������
	"""
	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.questID = section.readInt( "param1" )		# param1: ����ID
		self.taskIdx = section.readInt( "param2" )		# param2: ����Ŀ������
		self.range = section.readInt( "param3" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		players = entity.entitiesInRangeExt( self.range, "Role", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in players:
			# if ���������ָ��������:
			if e.hasTaskIndex( self.questID, self.taskIdx ):
				# ����ָ����QTTaskEventTrigger��״̬
				e.questTaskIncreaseState( self.questID, self.taskIdx )

class AIAction281( AIAction ):
	"""
	�õ�ͼ���������ʹ��һ��ϵͳ���ܣ�Ŀǰ������Ӫ�������buff��
	"""
	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""

		#param1: ����ID
		#param2: ����Ŀ������

		AIAction.init( self, section )
		self.camp = section.readInt( "param1" )
		self.skillID = section.readInt( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		try:
			spell = g_skills[ self.skillID ]					# ��ȡ���õĹ�������
		except:
			ERROR_MSG( "AIDAta %i get skill error, check whether %i is exist." %  ( self.getAIDataID(), self.skillID ) )
			return
		spaceBase = entity.getCurrentSpaceBase()
		spaceBase.allPlayersRemoteCall( "camp_systemCastSpell", ( self.camp, self.skillID, ) )
		
class AIAction282( AIAction ):
	"""
	����һ����ʱ����ֵ
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = ""
		self.param2 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString( "param1" )
		self.param2 = section.readInt( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	����NPCͷ��������(��Ҫ������ʱ����QTRInTime)
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		players = entity.entitiesInRangeExt( entity.attrDistance, "Role", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		for e in players:
			entity.questStatus( e.id )

class AIAction284( AIAction ):
	"""
	ȫ��ͨ�棨��Ļ������֣�
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.channel_msgs = section.readString( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		BigWorld.globalData[ csconst.C_PREFIX_GBAE ].anonymityBroadcast(self.channel_msgs,[])
		
class AIAction285( AIAction ):
	"""
	����Ĺר��
	param1��ͨ�����ݣ�%s��Ҷ�BOSSXXX���˺���ߣ�
	param2�� 1��2  1��ʾplayerName��2��ʾtongName
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.channel_msgs = section.readString( "param1" )
		self.param2 = section.readInt( "param2" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	��ǰ�ٻ���������Լ���Ϊ���������
	û�����˵���ͨ���ﲻ����
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.className = ""
		self.num = ""
		self.pos = ( 0, 0, 0 )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		for i in xrange( self.num ):
			e = entity.createObjectNearPlanes( self.className, entity.position + self.pos, entity.direction, { "level" : entity.level, "spawnPos" : tuple( entity.position ) } )
			e.setOwner( entity )
			if self.pos != ( 0, 0, 0 ):
				e.setToOwnerPos( self.pos )

class AIAction287( AIAction ):
	"""
	NPC ����
	ֻ���NPCFormation����������ʹ����Ч
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.formationType = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.formationType  = section.readInt( "param1" )
	
	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.remoteScriptCall( "setFormation", ( self.formationType, ) )

class AIAction288( AIAction ):
	"""
	������NPC�ߵ�287���õ���Ӫλ��
	NPCFormationServantר��
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
	
	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.gotoToOwnerPos()

class AIAction289( AIAction ):
	"""
	��ĳһ��Ӫ��ҷ���ͨ��
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.channel_msgs = ""
		self.campID = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.channel_msgs = section.readString( "param1" )	# ��������
		self.campID = section.readInt( "param2" )			# ������Ӫ

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		BigWorld.globalData[ csconst.C_PREFIX_GBAE ].campChatLocal( self.campID, csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", self.channel_msgs, [] )
		
		
class AIAction290( AIAction ):
	"""
	����Ĺר��
	����Ĺboss����ʱ����Ҫ������
	"""
	def __init__( self ):
		AIAction.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
		if tongName:#�а�����ʾ
			BigWorld.globalData[ csconst.C_PREFIX_GBAE ].anonymityBroadcast(cschannel_msgs.BCT_LIUWANGMU_MAX_DAMAGE_TONG %tongName,[])
		DEBUG_MSG("liuwangmu boss��%d is dead, and turn down the activity!"%entity.id)
		BigWorld.globalData["LiuWangMuMgr"].onBossDied()#֪ͨ��������boss��������ǰ��������
		entity.playerDamageList = {}

class AIAction291( AIAction ):
	"""
	AI�����������Ա𷢳���ͬ������
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		# �����¼�����
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
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	�ٻ���������Լ���Ϊ���������( û�����˵���ͨ���ﲻ���� )
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.className = ""
		self.pos = None

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	֪ͨ�ռ����ӻ��֣����ս����ר�ã�
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.integral = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.integral = section.readInt( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		if not entity.belong: # �ݵ�û�й������򷵻�
			return
		
		spaceBase = entity.getCurrentSpaceBase()
		if not spaceBase:
			return
		spaceBase.cell.addIntegral( 0 , self.integral, entity.belong  )

class AIAction294( AIAction ):
	"""
	����Ǳ�ܸ��������ţ�����Ǳ�ܸ����ã�
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	���й���Ե�ǰĿ��ʹ�ü���
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readInt64( "param1" )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		entity.spellTarget( self.param1, entity.targetID )

class AIAction296( AIAction ):
	"""
	����ǰս���б��еĲ�ְͬҵ������Ӵ�����Ϣ
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.posInfoDatas = {}
		self.radius = 0.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		param1= section.readString( "param1" )			#ְҵ��������Ϣ,���� profession|posInfo
		param2 = section.readString( "param2" )
		param3 = section.readString( "param3" )
		param4 = section.readString( "param4" )
		self.radius = section.readFloat( "param5" )		#���뾶
		
		for param in [param1, param2, param3, param4]:
			if len( param )> 0:
				profession = int( param.split("|")[0] )
				posInfo = param.split("|")[-1]
				self.posInfoDatas[profession] = posInfo

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	ˢ�¸�����������
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.param1 = ""
	
	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		self.param1 = section.readString("param1")  # ����
	
	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		BigWorld.setSpaceData( entity.spaceID, csconst.SPACE_SPACEDATA_PROGRESS, self.param1 )

class AIAction298( AIAction ):
	"""
	��AI���󲥷�����
	"""
	def __init__( self ):
		AIAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		# �����¼�����
		self.param1 = section.readString( "param1" )
		param2 = section.readString( "param2" )
		if param2 == "":
			self.param2 = 0
		else:
			self.param2 = int( param2 )

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
		@type	entity	:	entity
		"""
		target = BigWorld.entities.get( entity.aiTargetID, None )
		if target and target.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			target.client.onMakeASound( self.param1, self.param2 )


class AIAction299( AIAction ) :
	"""
	��AI������ң���ʾ������ʾ��Ϣ
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
	�¸���ģ�����AI��ÿ�ι���ˢ������ n ��Ѳ��·���в��ظ�ѡ��һ����ʼѲ�ߣ�Ҫ��ˢ������������������ n ����������
	"""
	def __init__( self ):
		AIAction.__init__( self )
		self.graphIDs = []

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AIAction.init( self, section )
		graphIDs = section.readString( "param1" )
		self.graphIDs = graphIDs.split()

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AIAction��entity
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
	����entity �� target��λ�����ڵ�ƽ��ֱ���ϵ�ĳ���㡣
	distance ��������� entity����λ��֮��ľ��롣
	���Ϲ�ʽ��
	entity.position �� ĳ����֮��ľ��� = entity.position �� target.position ֮��ľ��� + distance

	ֱ�߹�ʽ
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
		����y3, ���� L = ( math.sqrt( (y2 - y1)**2 + ( x2 - x1 )**2 ) + distance ) ** 2

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