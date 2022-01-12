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
	ս����ʼ��X����
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return time.time() - entity.fightStartTime <= self._param1

class AICnd2( AICondition ):
	"""
	ս����ʼ��X���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return time.time() - entity.fightStartTime > self._param1

class AICnd3( AICondition ):
	"""
	ս����ʼ��ÿ��X��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		
		t = int(time.time() - entity.fightStartTime )
		
		return entity.fightStartTime > 0 and t > 0 and t % self._param1 == 0

class AICnd4( AICondition ):
	"""
	ս���б��еĵ�λ�����ﵽĳ��ֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return len( entity.enemyList ) >= self._param1

class AICnd5( AICondition ):
	"""
	ս���б�Ϊ��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return len( entity.enemyList ) <= 0

class AICnd6( AICondition ):
	"""
	�˺��б��еĵ�λ�����ﵽĳ��ֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return len( entity.damageList ) >= self._param1

class AICnd7( AICondition ):
	"""
	�˺��б�Ϊ��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return len( entity.damageList ) <= 0

class AICnd8( AICondition ):
	"""
	�����б��еĵ�λ�����ﵽĳ��ֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return len( entity.cureList ) >= self._param1

class AICnd9( AICondition ):
	"""
	�����б�Ϊ��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return len( entity.cureList ) <= 0

class AICnd10( AICondition ):
	"""
	�����б���ĳ����λ��������������ĳֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		eid = entity.findEnemyByMaxCure()
		if eid <= 0:
			return False
		return entity.cureList[ eid ] > self._param1

class AICnd11( AICondition ):
	"""
	ս���б��е�ĳ��ְҵ����������ĳ��ֵ
	# ְҵ
	CLASS_UNKNOWN							= 0x00		# δ֪
	CLASS_FIGHTER							= 0x10		# սʿ
	CLASS_SWORDMAN							= 0x20		# ����
	CLASS_ARCHER							= 0x30		# ����
	CLASS_MAGE								= 0x40		# ��ʦ
	CLASS_PALADIN							= 0x50		# ǿ����սʿ��NPCר�ã�
	CLASS_WARLOCK							= 0x60		# ��ʦ( ��ȥ�� )
	CLASS_PRIEST							= 0x70		# ��ʦ( ��ȥ�� )
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0 #ְҵ
		self._param2 = 0 #����

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = eval( section.readString( "param1" ) )
		self._param2 = section.readInt( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	�˺��б���ĳ����λ���˺���������ĳֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		eid = entity.findEnemyByMaxDamage()
		if eid <= 0:
			return False
		return entity.damageList[ eid ] > self._param1

class AICnd13( AICondition ):
	"""
	���ڷ�ս��״̬
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return entity.getState() != csdefine.ENTITY_STATE_FIGHT

class AICnd14( AICondition ):
	"""
	����ս��״̬
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return entity.getState() == csdefine.ENTITY_STATE_FIGHT

class AICnd15( AICondition ):
	"""
	��������״̬
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return entity.getSubState() == csdefine.M_SUB_STATE_FLEE

class AICnd16( AICondition ):
	"""
	����׷��״̬
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return entity.getSubState() == csdefine.M_SUB_STATE_CHASE

class AICnd17( AICondition ):
	"""
	���ڸ�λ״̬
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return entity.getSubState() == csdefine.M_SUB_STATE_GOBACK

class AICnd18( AICondition ):
	"""
	����׷��״̬
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return entity.getOldSubState() == csdefine.M_SUB_STATE_CHASE and entity.getSubState() != csdefine.M_SUB_STATE_CHASE

class AICnd19( AICondition ):
	"""
	��������״̬
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return entity.getOldSubState() == csdefine.M_SUB_STATE_FLEE and entity.getSubState() != csdefine.M_SUB_STATE_FLEE

class AICnd20( AICondition ):
	"""
	��������״̬
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return entity.getState() == csdefine.ENTITY_STATE_DEAD

class AICnd21( AICondition ):
	"""
	������������ĳ���ٷֱ�ֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return entity.HP / float( entity.HP_Max ) > self._param1 / 100.0

class AICnd22( AICondition ):
	"""
	��������ֵ����ĳ���ٷֱ�ֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return entity.HP / float( entity.HP_Max ) < self._param1 / 100.0

class AICnd23( AICondition ):
	"""
	�������ĳBUFF/DEBUFFʱ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0 #buffID
		self._param2 = 0 #BuffLevel

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )
		self._param2 = section.readInt( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	��������ĳBUFF/DEBUFFʱ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0 #buffID
		self._param2 = 0 #BuffLevel

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )
		self._param2 = section.readInt( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	��һ��ʹ�õļ�����ĳ����
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0 #buffID list

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return entity.queryTemp( "last_use_spell", -1 ) == self._param1

class AICnd26( AICondition ):
	"""
	��һ����Χ��û��ս���б��еĵ�λʱ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0 #��Χ�뾶���ף�

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readFloat( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		for eid in entity.enemyList:
			if BigWorld.entities.has_key( eid ):
				if entity.distanceBB( BigWorld.entities[ eid ] ) <= self._param1:
					return False
		return len( entity.enemyList ) > 0

class AICnd27( AICondition ):
	"""
	��ǰĿ�괦��һ����Χ��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0 #��Χ�뾶���ף�

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readFloat( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		if BigWorld.entities.has_key( entity.targetID ):
			if entity.distanceBB( BigWorld.entities[ entity.targetID ] ) <= self._param1:
				return True
		return False

class AICnd28( AICondition ):
	"""
	��ǰĿ�괦��һ����Χ֮��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0 #��Χ�뾶���ף�

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readFloat( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		if BigWorld.entities.has_key( entity.targetID ):
			if entity.distanceBB( BigWorld.entities[ entity.targetID ] ) > self._param1:
				return True
		return False

class AICnd29( AICondition ):
	"""
	һ����Χ�ڵļ�����λ��������ĳֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0 #��Χ�뾶���ף�
		self._param2 = 0 #������λ����

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readFloat( "param1" )
		self._param2 = section.readInt( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	һ����Χ�ڵļ�����λ����С��ĳֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0 #��Χ�뾶���ף�
		self._param2 = 0 #������λ����

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readFloat( "param1" )
		self._param2 = section.readInt( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	һ����Χ�ڵ�ս���б��еĵ�λ��������ĳֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0 #��Χ�뾶���ף�
		self._param2 = 0 #������λ����

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readFloat( "param1" )
		self._param2 = section.readInt( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	һ����Χ�ڵ�ս���б��еĵ�λ����С��ĳֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0 #��Χ�뾶���ף�
		self._param2 = 0 #������λ����

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readFloat( "param1" )
		self._param2 = section.readInt( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	����ս����ĳһָ��������λ��������ĳֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = "" #NPCID
		self._param2 = 0 #����ֵ���ٷֱȣ�int

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readString( "param1" )
		self._param2 = section.readInt( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	����ս�������⼺����λ����ֵ����ĳֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0 #����ֵ���ٷֱȣ�int

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	��ǰĿ������ֵ����ĳ��ֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0.0 #����ֵ���ٷֱȣ�

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readFloat( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		if BigWorld.entities.has_key( entity.targetID ):
			e = BigWorld.entities[ entity.targetID ]
			if e.HP / float( e.HP_Max ) < self._param1:
				return True
		return False

class AICnd36( AICondition ):
	"""
	Ŀ��ȼ�����ĳֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0 #level

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		if BigWorld.entities.has_key( entity.targetID ):
			e = BigWorld.entities[ entity.targetID ]
			if e.level < self._param1:
				return True
		return False

class AICnd37( AICondition ):
	"""
	Ŀ��ȼ�����ĳֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0 #level

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		if BigWorld.entities.has_key( entity.targetID ):
			e = BigWorld.entities[ entity.targetID ]
			if e.level > self._param1:
				return True
		return False

class AICnd38( AICondition ):
	"""
	��ǰĿ��Ϊĳְҵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0 #race

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		if BigWorld.entities.has_key( entity.targetID ):
			e = BigWorld.entities[ entity.targetID ]
			if e.getClass() == self._param1:
				return True
		return False

class AICnd39( AICondition ):
	"""
	��ǰĿ�����ĳBUFF/DEBUFFʱ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0 #buffID
		self._param2 = 0 #BuffLevel

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )
		self._param2 = section.readInt( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	��ǰĿ�겻����ĳBUFF/DEBUFFʱ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0 #buffID
		self._param2 = 0 #BuffLevel

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )
		self._param2 = section.readInt( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	��ǰĿ�겻��ĳְҵʱ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0 #race

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		if BigWorld.entities.has_key( entity.targetID ):
			e = BigWorld.entities[ entity.targetID ]
			if e.getClass() != self._param1:
				return True
		return False

class AICnd42( AICondition ):
	"""
	��ǰĿ����������һ������ʱ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		if BigWorld.entities.has_key( entity.targetID ):
			e = BigWorld.entities[ entity.targetID ]
			if e.intonating():
				return True
		return False

class AICnd43( AICondition ):
	"""
	��ǰĿ������ֵ����ĳ��ֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0.0 #����ֵ���ٷֱȣ�

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readFloat( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		if BigWorld.entities.has_key( entity.targetID ):
			e = BigWorld.entities[ entity.targetID ]
			if e.HP / float( e.HP_Max ) > self._param1:
				return True
		return False

class AICnd44( AICondition ):
	"""
	AI�����Ƿ�Ϸ�
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = [] 	 # NPCID�б�[ npcclass, npclass...]
		self._param2 = []	 # AI�����б�[uint16,...]

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		cmdInfo = entity.queryTemp( "AICommand", 0 )
		if cmdInfo == 0:
			return False
		npcID, className, cmd = cmdInfo
		if cmd not in self._param2:
			return False
		if not self._param1:	# ���û��ָ������������Ӧ���з����ߵ�����
			return True
		if className in self._param1:
			return True
		return False

class AICnd45( AICondition ):
	"""
	ս���б����ӣ��¼���ս���б����ı䣩
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return entity.aiTargetID in entity.enemyList

class AICnd46( AICondition ):
	"""
	��ǰ���ö���Ϊĳ����
	1		# ��ɫ
	2		# NPC
	3		# ����
	4		# ����
	6		# ������Ʒ
	7		# ������
	8		# ������
	9		# ���͵�
	10	# ����ʦ
	11	# ����ϵͳ
	12	# ��������
	13	# ��
	14	# �������û��������Ҫ�жϵ����Ͷ���Ϊ���ࣩ

	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0 #����ֵ���ٷֱȣ�

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		if not BigWorld.entities.has_key( entity.targetID ):
			ERROR_MSG( "targetID %i is error." % entity.targetID )
			return
		return BigWorld.entities[ entity.targetID ].isEntityType( self._param1 )

class AICnd47( AICondition ):
	"""
	��ǰĿ��Ϊĳ��
	1		# ��ɫ
	2		# NPC
	3		# ����
	4		# ����
	6		# ������Ʒ
	7		# ������
	8		# ������
	9		# ���͵�
	10	# ����ʦ
	11	# ����ϵͳ
	12	# ��������
	13	# ��
	14	# �������û��������Ҫ�жϵ����Ͷ���Ϊ���ࣩ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0 #����ֵ���ٷֱȣ�

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section.readInt( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		if not BigWorld.entities.has_key( entity.aiTargetID ):
			WARNING_MSG( "aiTargetID is error." )
			return False
		return BigWorld.entities[ entity.aiTargetID ].isEntityType( self._param1 )

class AICnd48( AICondition ):
	"""
	�˺��б����ӣ��¼���ս���б����ı䣩
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return entity.aiTargetID in entity.damageList

class AICnd49( AICondition ):
	"""
	ָ�����ܿɶԵ�ǰĿ��ʹ��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt64( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		# �����ж�
		try:
			enemy = BigWorld.entities[ entity.targetID ]
		except:
			return False
		target = SkillTargetObjImpl.createTargetObjEntity( enemy )
		try:
			spell = g_skills[ self.param1 ]						# ��ȡ���õĹ�������
		except:
			ERROR_MSG( "Entity classname %s use skill error, id is %i."%( entity.className ,self.param1 ))
			return False

		state = spell.useableCheck( entity,  target )
		if state != csstatus.SKILL_GO_ON and state != csstatus.SKILL_TOO_FAR:
			return False
		return True

class AICnd50( AICondition ):
	"""
	ָ������ȼ����ܿɶԵ�ǰĿ��ʹ��
	�����еļ���ָδչ���ļ���ID����Ҫ���ϸ�NPC�ĵȼ���Ϊչ����ļ���ID��
	�磺NPC�ȼ�Ϊ32������IDΪ123456����Ҫ�жϵļ���IDӦΪ123456032
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt64( "param1" ) * 1000

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		# �����ж�
		try:
			enemy = BigWorld.entities[ entity.targetID ]
		except:
			return False
		target = SkillTargetObjImpl.createTargetObjEntity( enemy )
		try:
			spell = g_skills[ self.param1 + entity.level ]						# ��ȡ���õĹ�������
		except:
			ERROR_MSG( "Use skill error, id is %i. className: %s."%(self.param1 + entity.level, entity.className ) )
			return False
		state = spell.useableCheck( entity,  target )
		if state != csstatus.SKILL_GO_ON and state != csstatus.SKILL_TOO_FAR:
			return False
		return True


class AICnd51( AICondition ):
	"""
	��⳰��ʩ������Ч��
	������ʹ�ó����ܵ�Ŀ�� ��ǰ����Ч�ԣ��ɷ���乥����
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		buffs = entity.findBuffsByBuffID( 199001 )
		if len( buffs ) <= 0:
			return False

		casterID = entity.getBuff( buffs[0] )["caster"]
		return BigWorld.entities.has_key( casterID )

class AICnd52( AICondition ):
	"""
	�������״̬
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return entity.getOldSubState() == csdefine.M_SUB_STATE_GOBACK and entity.getSubState() != csdefine.M_SUB_STATE_GOBACK

class AICnd53( AICondition ):
	"""
	ĳ��¼ʱ���Ƿ񵽴�
	��Ҫ����һЩʱ���ѯ�Ȳ�����
	�� һ��ʱ���� NPCû����ʲô����ô����

	Ҫʵ�������Ȼ����Ҫ���һ����ض�����
	����¼��ǰʱ�䡰   �����Ǻ͸ñ�ǩ��һ����
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 1
		self.param2 = 1 # һ��ʱ���  �磺30��

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readString( "param1" )
		self.param2 = section.readInt( "param2" )
		self.param3 = section.readInt( "param3" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		signTime = entity.queryTemp( self.param1, -1.0 )
		return signTime != -1 and BigWorld.time() - signTime >= self.param2


class AICnd54( AICondition ):
	"""
	����ӵ������NPC֮������Ƿ�С����ĳֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" ) # �뾶��С  ��������Ϊ����

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		ownerBase = entity.queryTemp( "npc_ownerBase", None )
		if ownerBase:
			ownerID = ownerBase.id
			if BigWorld.entities.has_key( ownerID ):
				owner = BigWorld.entities[ ownerID ]
				# �����Ƿ�Ҫ��
				if owner.isMyOwnerFollowNPC( entity.id ):
					distance = csarithmetic.distancePP3( owner.position, entity.position )
					return distance <= self.param1
		else:
			pass
			#ERROR_MSG( "can not find the owner!" )
		# �Ҳ������������
		return False

class AICnd55( AICondition ):
	"""
	����ӵ������NPC֮������Ƿ����ĳֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" ) # �뾶��С  ��������Ϊ����

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		ownerBase = entity.queryTemp( "npc_ownerBase", None )
		if ownerBase:
			ownerID = ownerBase.id
			if BigWorld.entities.has_key( ownerID ):
				owner = BigWorld.entities[ ownerID ]
				# �����Ƿ�Ҫ��
				if owner.isMyOwnerFollowNPC( entity.id ):
					distance = csarithmetic.distancePP3( owner.position, entity.position )
					return distance >= self.param1
		else:
			pass
			#ERROR_MSG( "can not find the owner!" )
		# �Ҳ������������
		return True

class AICnd56( AICondition ):
	"""
	NPC�Ƿ񵽴�ָ����Χ��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = (0,0,0)
		self.param2 = 2
		self.param3 = "fengming"

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

		position = section.readString( "param1" )				# ����
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param1" % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.param1 = pos

		self.param2 = section.readFloat( "param2" ) # �뾶��С
		self.param3 = section.readString( "param3" ) # map

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		map = entity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		if map != self.param3:
			return False
		distance = csarithmetic.distancePP3( self.param1, entity.position )
		return distance <= self.param2

class AICnd57( AICondition ):
	"""
	NPC�Ƿ�δ����ָ����Χ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = (0,0,0)
		self.param2 = 2
		self.param3 = "fengming"

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

		position = section.readString( "param1" )				# ����
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error��( AIData %i, id %i ) Bad format '%s' in section param1" % ( self.getAIDataID(), self.getID(), position ) )
			else:
				self.param1 = pos

		self.param2 = section.readFloat( "param2" ) # �뾶��С
		self.param3 = section.readString( "param3" ) # map

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		map = entity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		if map != self.param3:
			return False
		distance = csarithmetic.distancePP3( self.param1, entity.position )
		return distance > self.param2

class AICnd58( AICondition ):
	"""
	���NPC�Ƿ���Ա��Monster
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return entity.queryTemp( "state_npc_speaker", True )


class AICnd59( AICondition ):
	"""
	������������˼����ĳһ����
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 3.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" ) #����
		if self.param1 < 0.1:
			self.param1 = 30.0



	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	������������˼�С��ĳһ����
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 20.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" ) #����


	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	���������Ҳ�������
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )


	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	��������״̬
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return entity.getState() == csdefine.ENTITY_STATE_FREE


class AICnd63( AICondition ):
	"""
	������������˲���һ���ռ���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )


	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		ownerID = entity.getOwnerID()
		if BigWorld.entities.has_key( ownerID ):
			return BigWorld.entities[ownerID].spaceID != entity.spaceID

		return True


class AICnd64( AICondition ):
	"""
	���˽���ս��״̬
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )


	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	�����˶�ʧ��ϵʱ������趨ʱ��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" ) #ʱ��


	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	�������
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )


	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return entity.queryTemp( 'questFinish', False )

class AICnd67( AICondition ):
	"""
	ս��ͳ˧��NPC�жϽ�����Ұ������Ƿ�Ϊ�ж԰��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )


	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
				#  ����ǹ���
				return not p.isRight
		else:
			if p.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				return p.tong_dbID in BigWorld.globalData[ "CityWarRightTongDBID" ]
			else:
				#  ����ǹ���
				return p.isRight

		return p.tong_dbID in BigWorld.globalData[ "CityWarRightTongDBID" ]


class AICnd68( AICondition ):
	"""
	�̶�ʱ�����ĳʱ��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = section['param1'].asString			#key (���磺 'start_time' ��
		self._param2 = section['param2'].asFloat			#ʱ���

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		startTime = entity.queryTemp( self._param1, 0.0 )
		if self._param2 < BigWorld.time() - startTime:
			entity.setTemp( self._param1, BigWorld.time() )
			return True
		return False

class AICnd69( AICondition ):
	"""
	�ڳ��Ҳ��������ߣ������̫Զ��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" ) # �뾶��С  ��������Ϊ����
		if self.param1 < 20.0:
			self.param1 = 20.0

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	NPCӵ���ߵ�ĳ�����ĳTASK�Ƿ�δ���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 0
		self.param2 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt( "param1" )
		self.param2 = section.readInt( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		ownerBase = entity.queryTemp( "npc_ownerBase", None )
		if ownerBase:
			ownerID = ownerBase.id
			if BigWorld.entities.has_key( ownerID ):
				owner = BigWorld.entities[ ownerID ]
				# �����Ƿ�Ҫ��
				if owner.isMyOwnerFollowNPC( entity.id ):
					return not owner.taskIsCompleted( self.param1, self.param2 )
			else:
				if ownerBase.cell.isMyOwnerFollowNPC( entity.id ):
					return not ownerBase.cell.taskIsCompleted( self.param1, self.param2 )
		# �Ҳ��������,����δ���
		return True

class AICnd71( AICondition ):
	"""
	NPC��ӵ�����Ƿ�ɱ���˻���������
	�����ӵ����ָ����ӵ�й�������Ȩ����ң�����ʵ�ִ�NPC�������������Ȩӵ����Ҳ�����˽����˴洢
	Ŀǰֻ����Ա������֡��������Ȳر�ͼϵͳ�еĹ���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		ownerID = entity.getOwnerID()
		if ownerID:
			if BigWorld.entities.has_key( ownerID ):
				owner = BigWorld.entities[ ownerID ]
				if owner.getState() == csdefine.ENTITY_STATE_DEAD:
					# �����ɫ����
					return True
				else:
					# �����ɫ����
					return False
			else:
				return True
		return True

class AICnd72( AICondition ):
	"""
	����ȼ���ָ����Χ��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 0
		self.param2 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt( "param1" )
		self.param2 = section.readInt( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return entity.level >= self.param1 and entity.level <= self.param2

class AICnd73( AICondition ):
	"""
	�Ƿ���ĳ״̬�´ﵽһ��ʱ��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 0	# �Ƿ���ĳ״̬
		self.param2 = 0	# �Ƿ�ﵽһ��ʱ��

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt( "param1" )	# �Ƿ���ĳ״̬
		self.param2 = section.readInt( "param2" )	# �Ƿ�ﵽһ��ʱ��

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	���ʱ�����ָ��ֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt( "param1" )	# �Ƿ���ĳ״̬

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		if entity.queryTemp('spawnTime', 0 ) == 0:
			entity.setTemp( 'spawnTime', time.time() )
		return time.time() - entity.queryTemp('spawnTime') > self.param1


class AICnd75( AICondition ):
	"""
	����Ѫ������ָ���ٷֱ�
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 0


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return float(entity.HP)/ float(entity.HP_Max)  < self.param1

class AICnd76( AICondition ):
	"""
	�Ƿ����NPC���Ժ�һ��ʱ��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 0


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		if entity.queryTemp( "tempSayFlag", False ) and time.time() - entity.queryTemp( "tempSayTime", 0 ) >= self.param1:
			entity.setTemp( "tempSayFlag", False )	# ���ñ��
			return True
		return False

class AICnd77( AICondition ):
	"""
	�Ƿ����ĳ���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readString( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return entity.queryTemp( self.param1 )

class AICnd78( AICondition ):
	"""
	һ����Χ���Ƿ����ض����͵Ĺ���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 0.0
		self.classNames = []
		self.param3 = "Monster"		# Ĭ��ΪMonster


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" )			# ��Χ
		self.classNames = section.readString( "param2" ).split("|")		# className
		self.param3 = section.readString( "param3" )		# ����EntityType

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	һ����Χ���ض����͵Ĺ��Ѫ���Ƿ����ض���Χ��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 0.0
		self.param2 = ""
		self.param3 = []
		self.param4 = "Monster"

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" )							# ��Χ
		self.param2 = section.readString( "param2" )						# className
		self.param3 = (section.readString( "param3" )).split( ":" )			# Ѫ����Χֵ��such as : 10:60
		self.param4 = section.readString( "param4" )						# ����EntityType

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	ָ����Χ���Ƿ���pkֵ����ĳ�������
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._radius = section.readFloat( "param1" ) # �����뾶
		self._pkValue = section.readInt( "param2" ) # ����pkֵ�ڶ�������

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	ָ�����ܿɶ�����ʹ��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt64( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		target = SkillTargetObjImpl.createTargetObjEntity( entity )

		try:
			spell = g_skills[ self.param1 ]						# ��ȡ���õĹ�������
		except:
			ERROR_MSG( "Entity classname %s use skill error, id is %i."%( entity.className ,self.param1 ))
			return False
		state = spell.useableCheck( entity,  target )
		if state != csstatus.SKILL_GO_ON and state != csstatus.SKILL_TOO_FAR:
			return False
		return True


class AICnd82( AICondition ):
	"""
	ָ������ȼ����ܿɶ�����ʹ��
	�����еļ���ָδչ���ļ���ID����Ҫ���ϸ�NPC�ĵȼ���Ϊչ����ļ���ID��
	�磺NPC�ȼ�Ϊ32������IDΪ123456����Ҫ�жϵļ���IDӦΪ123456032
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt64( "param1" ) * 1000

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		# �����ж�
		target = SkillTargetObjImpl.createTargetObjEntity( entity )
		spell = g_skills[ self.param1 + entity.level ]						# ��ȡ���õĹ�������
		state = spell.useableCheck( entity,  target )
		if state != csstatus.SKILL_GO_ON and state != csstatus.SKILL_TOO_FAR:
			return False
		return True

class AICnd83( AICondition ):
	"""
	�Ƿ񲻴���ĳ���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 0


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readString( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return not entity.queryTemp( self.param1 )

class AICnd84( AICondition ):
	"""
	����սAI��������Ұ��entity�Ƿ�Ϊս����¥
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		e = BigWorld.entities.get( entity.aiTargetID )
		return e and e.isEntityType( csdefine.ENTITY_TYPE_TONG_CITYWAR_MONSTER ) and e.cw_flag == csdefine.TONG_CW_FLAG_TOWER

class AICnd85( AICondition ):
	"""
	��Χ���Ƿ���ĳ���͵Ĺ���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 0.0
		self.param2 = "Monster"		# Ĭ��ΪMonster


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" )			# ��Χ
		self.param2 = section.readString( "param2" )		# ����EntityType

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	��Χ���Ƿ�û��ĳ���͵Ĺ���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 0.0
		self.param2 = "Monster"		# Ĭ��ΪMonster


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" )			# ��Χ
		self.param2 = section.readString( "param2" )		# ����EntityType

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	һ����Χ��û���ض����͵Ĺ���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 0.0
		self.param2 = ""
		self.param3 = "Monster"		# Ĭ��ΪMonster


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" )			# ��Χ
		self.param2 = section.readString( "param2" ).split("|")		# className
		self.param3 = section.readString( "param3" )		# ����EntityType

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	ս���б�����ĳclassName�Ĺ���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readString( "param1" )			# className

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		for enemyID in entity.enemyList:
			enemy = BigWorld.entities.get( enemyID )
			if enemy and hasattr( enemy, "className" ) and enemy.className == self.param1:
				return True
		return False

class AICnd89( AICondition ):
	"""
	һ����Χ���Ƿ����ض����͵����ض�buff��entity
	"""
	def __init__( self ):
		AICondition.__init__( self )

		self.param1 = 0.0
		self.param2 = 0
		self.param3 = "Monster"		# Ĭ��ΪMonster

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

		self.param1 = section.readFloat( "param1" )							# ��Χ
		self.param2 = section.readInt( "param2" )							# buffID
		self.param3 = section.readString( "param3" )						# EntityType

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	һ����Χ���Ƿ�û���ض����͵����ض�buff��entity
	"""
	def __init__( self ):
		AICondition.__init__( self )

		self.param1 = 0.0
		self.param2 = 0
		self.param3 = "Monster"		# Ĭ��ΪMonster

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

		self.param1 = section.readFloat( "param1" )							# ��Χ
		self.param2 = section.readInt( "param2" )							# buffID
		self.param3 = section.readString( "param3" )						# EntityType

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	һ����Χ���Ƿ����ض����͵�entity
	"""
	def __init__( self ):
		AICondition.__init__( self )

		self.param1 = 0.0
		self.param2 = "Monster"		# Ĭ��ΪMonster

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

		self.param1 = section.readFloat( "param1" )							# ��Χ
		self.param2 = section.readString( "param2" )						# EntityType

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	һ����Χ���Ƿ�û���ض����͵�entity
	"""
	def __init__( self ):
		AICondition.__init__( self )

		self.param1 = 0.0
		self.param2 = "Monster"		# Ĭ��ΪMonster

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

		self.param1 = section.readFloat( "param1" )							# ��Χ
		self.param2 = section.readString( "param2" )						# EntityType

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	һ����Χ�����ض����͵��ض�className�����ض�buff��entity
	"""
	def __init__( self ):
		AICondition.__init__( self )

		self.param1 = 0.0
		self.param2 = 0
		self.param3 = "Monster"		# Ĭ��ΪMonster

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

		self.param1 = section.readFloat( "param1" )							# ��Χ
		self.param2 = section.readInt( "param2" )							# buffID
		self.param3 = section.readString( "param3" )						# EntityType
		self.param4 = section.readString( "param4" )						# className

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	һ����Χ��û���ض����͵��ض�className�����ض�buff��entity
	"""
	def __init__( self ):
		AICondition.__init__( self )

		self.param1 = 0.0
		self.param2 = 0
		self.param3 = "Monster"		# Ĭ��ΪMonster

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

		self.param1 = section.readFloat( "param1" )							# ��Χ
		self.param2 = section.readInt( "param2" )							# buffID
		self.param3 = section.readString( "param3" )						# EntityType
		self.param4 = section.readString( "param4" )						# className

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	Ѫ���仯ֵ��֮ǰ��¼��һ����ʼֵ��
	"""
	def __init__( self ):
		AICondition.__init__( self )

		self.param1 = 0


	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt( "param1" )							# �仯ֵ


	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		saveHp = entity.queryTemp( "ai_save_HP_value", 0 )

		if saveHp == 0 or saveHp - entity.HP > int( self.param1 * 0.01 * entity.HP_Max ):
			return True

		return False


class AICnd96( AICondition ):
	"""
	�Է��Ƿ�������
	"""
	def __init__( self ):
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		target = BigWorld.entities.get( entity.aiTargetID )
		if target and target.isReal():
			if target.findBuffByID( csconst.RABBIT_RUN_CATCH_RABBIT_RABBIT_BUFF_ID ) is not None:
				return True
		return False



class AICnd97( AICondition ):
	"""
	ָ�����ﲻ��������״̬
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" )							# ��Χ
		self.param2 = section.readString( "param2" )						# EntityType
		self.param3 = section.readString( "param3" )						# className

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	�����Ƿ񲻾���ĳ����־λ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt( "param1" )							# ��־λ


	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return not entity.hasFlag( self.param1 )


class AICnd99( AICondition ):
	"""
	��ĳ״̬�л����ض�״̬
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt( "param1" )							# ��״̬
		self.param2 = section.readInt( "param2" )							# ��״̬


	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		return entity.lastState == self.param1 and entity.state == self.param2

class AICnd100( AICondition ):
	"""
	�ڳ����Ҹ��������ߣ�������ڣ� by ����
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" ) # �뾶��С  ��������Ϊ��������
		self.param2 = section.readInt( "param2" )	# �����뿪�ڳ����ʱ�䣬��λ ��

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
				memberIDDict[mid] = -1	# ����ʧ��
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

					for qID in member.questsTable.keys():		# ���ó�Ա��������failure
						if qID in member_ql:
							member.questTaskFailed( qID, member_taskIndex )

				continue
			dis = (csarithmetic.distancePP3( member.position, entity.position ) - self.param1) if member is not None else 0
			memberIDDict[mid] = t if dis >= 0 and mt == 0 else mt
		return True

class AICnd101( AICondition ):
	# �������ս��Ʒӵ����
	def check( self, ai, entity ):
		return entity.bootyOwner != ( 0, 0 )

class AICnd102( AICondition ):
	"""
	entity�Ƿ�λ��ĳЩ��ͼ
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
	������������˼����ĳһ����( �Ҳ������˷���True )
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 3.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" ) #����
		if self.param1 < 0.1:
			self.param1 = 30.0

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	��һ����Χ�����ض�������û���ض�BUFF��entity(ֻҪ��һ������ ) add by wuxo 2011-12-7
	"""
	def __init__( self ):
		AICondition.__init__( self )

		self.param1 = 0.0
		self.param2 = 0
		self.param3 = "Monster"		# Ĭ��ΪMonster

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

		self.param1 = section.readFloat( "param1" ) #��Χ							# ��Χ
		self.param2 = section.readInt( "param2" )	#bufferID							# buffID
		self.param3 = section.readString( "param3" )# ����				# EntityType

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	����͹���Ŀ��ľ����ǲ��Ǵ���ָ��ֵ
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
	����͹���Ŀ��ľ����ǲ���С��ָ��ֵ
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
	�ж�һ����Χ���ض�className�Ĺ��������Ƿ������ض���������ϵ
	"""
	def __init__( self ):
		AICondition.__init__( self )
		self.param1 = 0.0
		self.param2 = ""
		self.param3 = 0				# entity����
		self.param4 = 0				# �жϷ���
		self.param5 = "Monster"		# Ĭ��ΪMonster

	def init( self, section ):
		"""
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" ) 	# ��Χ
		self.param2 = section.readString( "param2" )	# className
		self.param3 = section.readInt( "param3" )		# entity����
		self.param4 = section.readInt( "param4")		# ������ϵ���ţ�0����=����1����<����2����>��
		self.param5 = section.readString( "param5")		# entityType

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
			# ������㡰=���ض�entity����
			return True
		if self.param4 == 1 and len( monstersList ) < self.param3:
			# ������㡰<���ض�entity����
			return True
		if self.param4 == 2 and len( monstersList ) > self.param3:
			# ������㡰>���ض�entity����
			return True
		return False


class AICnd108( AICondition ):
	"""
	�Ƿ�û�е���AIҪȥ��λ�õ�һ����Χ
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
	�Ƿ�ﵽ�͹���Ŀ����x�����һ�������λ��
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
	�Ƿ�ﵽ�͹���Ŀ����z�����һ�������λ��
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
	�ӳ��Ƿ񲻴���
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
	���������Ƕӳ�
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
	�Ƿ��ڹ���Ŀ�������һ����Χ��
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
	�ж�NPC��ӵ���ߵ�״̬��ʹ���������NPC�� added by dqh
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 0				# Ĭ��Ϊ����״̬

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt( "param1" ) # ��ɫ��״̬

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	�жϵ�ǰѲ��·���Ƿ��Ѿ�׼����
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.patrolNode = ""
		self.graphID = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.patrolNode = section.readString( "param1" )
		self.graphID = section.readString( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		patrolList = BigWorld.PatrolPath( self.graphID )
		if not patrolList or not patrolList.isReady() or len(self.patrolNode) <= 0:
			return False
		else:
			return True

class AICnd116( AICondition ):
	"""
	�ж�NPC��ս��Ʒӵ���ߵ�״̬(ʹ���ڷ�ConvoyMonster���͵������NPC)
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 0				# Ĭ��Ϊ����״̬

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt( "param1" ) # ��ɫ��״̬

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	�ж���һ��ͬclassname���Ҿ�����ͬ��ս��Ʒӵ���ߵĹ����Ƿ�ȫ������
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 50				# ��Χ
		self.param2 = ""				# className

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt( "param1" ) 		# ��Χ
		self.param2 = section.readString( "param2" )	# className

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		bootyOwner = entity.getBootyOwner()
		monsterList = entity.entitiesInRangeExt( self.param1, "Monster", entity.position )
		WARNING_MSG( "start search entities around of monster(class:%s|id:%i)!" % ( entity.className, entity.id ) )
		if len( monsterList ) == 0:
			return True
		else:
			for e in monsterList:
				if e.className == self.param2 and e.getBootyOwner() == bootyOwner and not e.isDead():		#ֻҪ����һ������className�����Һ�entity��ӵ����һ��
					return False
		return True

class AICnd118( AICondition ):
	"""
	�ж�ӵ���ߣ����ˣ��Ƿ�Ϊĳ״̬�����������˵Ĺ���ʹ�ã�
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.param1 = 0				# Ĭ��Ϊ����״̬

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readInt( "param1" ) 				# ��ɫ��״̬

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	�ж��Ƿ���ӵ���ߣ��޶��������˵Ĺ���ʹ�ã�
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	�ж���Χ����ĳһ�ض���Ӫ��battleCamp��NPC�������Ƿ�С��ĳֵ
	"""
	def __init__( self ):
		AICondition.__init__( self )
		self.range = 0.0			# ��Χ
		self.batCamp = 0			# ��Ӫ
		self.amount = 0				# entity����

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.range = section.readFloat( "param1" ) 	# ��Χ
		self.batCamp = section.readInt( "param2" )	# battleCamp
		self.amount = section.readInt( "param3" )	# entity����

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	�ж���Χ����ĳһ�ض���Ӫ��battleCamp��NPC�������Ƿ����ĳֵ
	"""
	def __init__( self ):
		AICondition.__init__( self )
		self.range = 0.0			# ��Χ
		self.batCamp = 0			# ��Ӫ
		self.amount = 0				# entity����

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.range = section.readFloat( "param1" ) 	# ��Χ
		self.batCamp = section.readInt( "param2" )	# battleCamp
		self.amount = section.readInt( "param3" )	# entity����

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	�˺��б����Ƿ����ض����͵�className��entity
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.entityType = ""
		self.className = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.entityType = section.readString( "param1" )
		self.className = section.readString( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		for id in entity.damageList:
			e = BigWorld.entities.get( id )
			if e and e.__class__.__name__ == self.entityType:
				if self.className and e.className != self.className:		# classNameΪ����ֻ�������Entity����
					continue
				return True
		return False


class AICnd123( AICondition ):
	"""
	�жϵ�ǰ���ڿռ�Ĵ���ʱ���Ƿ���ڵ���ָ��ֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.upperLimit = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.upperLimit = section.readFloat( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	�жϵ�ǰ���ڿռ�Ĵ���ʱ���Ƿ�С��ָ��ֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self.lowerLimit = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.lowerLimit = section.readFloat( "param1" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		spaceEntity = BigWorld.entities.get( entity.getCurrentSpaceBase().id )
		if spaceEntity is None : return False
		return spaceEntity.timeFromCreated() < self.lowerLimit

class AICnd125( AICondition ):
	"""
	�жϵ�ǰ�Ƿ��жԻ�������
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		if entity.queryTemp( "talkFollowID", 0 ):
			return True
		
		return False

class AICnd126( AICondition ):
	"""
	����Ƿ񵽴�ĳ��Ѳ��·�����������λ�������Ѳ�ߵ��XZƽ��һ����Χ��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.graphID = section.readString( "param1" )
		self.range = section.readFloat( "param2" )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	aiĿ���Ƿ���pkֵ����ĳ�������
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._pkValue = section.readInt( "param1" ) # ����pkֵ�ڶ�������

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	һ����Χ�ڣ��Ƿ���������ͬclassName�Ĺ��ﵱǰ��Ŀ��������Ŀ��һ�¡� 
	"""
	def __init__( self ):
		AICondition.__init__( self )
		self.param1 = 0.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" )						# className

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	һ����Χ�ڣ���ͬclassName�Ĺ���,�Ƿ�ֻ���ҵ�Ŀ��(targetID)�����entitiy(�������) �� 
	"""
	def __init__( self ):
		AICondition.__init__( self )
		self.param1 = 0.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readFloat( "param1" )						# className

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	��ѯ�����ĳ����ʱ�����Ƿ����ĳ��ֵ 
	"""
	def __init__( self ):
		AICondition.__init__( self )
		self.param1 = ""
		self.param2 = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = section.readString( "param1" )						# �������ʱ����
		self.param2 = section.readInt( "param2" )							# ��ʱ���Ե�ֵ�Ƿ����ĳ��ֵ

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	�Ƿ�������Ӧ����Ӫ� 
	"""
	def __init__( self ):
		AICondition.__init__( self )
		self.param1 = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = [ int( i ) for i in section.readString( "param1" ).split(";") ]						# ��Ӫ�����

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	�Ƿ�û�п�����Ӧ����Ӫ� 
	"""
	def __init__( self ):
		AICondition.__init__( self )
		self.param1 = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self.param1 = [ int( i ) for i in section.readString( "param1" ).split(";") ]						# ��Ӫ�����

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
	�Ƿ���ָ��ʱ����
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._cmd = ""			# scheme �ַ��� �磺" * * 3 * *" (�μ� CrondScheme.py)
		self._lastTime = 1		# ��λ��
		self.scheme = Scheme()

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._cmd = section.readString( "param1" )
		self._lastTime = section.readInt( "param2" )
		self.scheme.init( self._cmd )

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		year, month, day, hour, minute = time.localtime( time.time() - self._lastTime )[:5]
		nextTime = self.scheme.calculateNext( year, month, day, hour, minute )
		if nextTime < time.time():
			return True
		return False

class AICnd134( AICondition ):
	"""
	aiĿ���Ƿ���ĳ��Ӫ�б���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._param1 = [] #camp list

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		AICondition.init( self, section )
		self._param1 = [int(i) for i in section.readString( "param1" ).split( ";" )]

	def check( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		if BigWorld.entities.has_key( entity.aiTargetID ):
			e = BigWorld.entities[entity.aiTargetID]
			if e.getCamp() in self._param1:
				return True
		return False

class AICnd135( AICondition ):
	"""
	AI������ң���ĳ����Ľ���״̬�Ƿ���ָ��������״̬�б���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		AICondition.__init__( self )
		self._questID = 0		# ����ID
		self._questStates = []	# ����״̬�б�

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
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
		@param	ai		: 	ӵ�д�������AI  ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
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
