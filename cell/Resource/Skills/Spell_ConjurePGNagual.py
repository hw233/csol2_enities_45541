# -*- coding: gb18030 -*-

# common and global
import BigWorld
import random
import Math
from bwdebug import *
import csconst
import csdefine
# cell
import Const
from SpellBase import Spell

# config
import csstatus

class Spell_Conjure( Spell ):
	"""
	����ٻ��̹��ػ�����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		self.className = ""				# �̹��ػ�className
		self.attackType = 1				# ��������

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.className = dict[ "param1" ] if dict["param1"] else ""
		self.attackType = int( dict["param3"] ) if dict["param3"] else 1 

	def receive( self, caster, receiver ):
		"""
		virtual method = 0
		���ÿһ�������߽�����������������˺����ı����Եȵȡ�ͨ������´˽ӿ�����onArrive()���ã�
		�������п�����SpellUnit::receiveOnreal()�������ã����ڴ���һЩ��Ҫ�������ߵ�real entity�����������顣
		�������Ƿ���Ҫ��real entity���Ͻ��գ��ɼ����������receive()�������жϣ������ṩ��ػ��ơ�
		ע���˽ӿ�Ϊ�ɰ��е�onReceive()

		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		pos = Math.Vector3( receiver.position )
		dir = receiver.direction
		dic = [ -5, -4, -3, 3, 4, 5 ]
		randomVal = dic[ random.randint( 0, 5 ) ]
		
		pos.x = receiver.position.x + randomVal
		pos.z = receiver.position.z + randomVal
		
		# �ٻ������ʱ��Ե��������ײ����������������
		collide = BigWorld.collide( receiver.spaceID, ( pos.x, pos.y + 10, pos.z ), ( pos.x, pos.y - 10, pos.z ) )
		if collide != None:
			pos.y = collide[0].y
				
		dict ={}
		dict[ "spawnPos" ] = tuple( pos )
		dict["attackType"] = self.attackType
		dict["level"] = self.getLevel()

		newEntity = receiver.createObjectNearPlanes( self.className, pos, dir, dict )
		newEntity.setOwner( caster.base )

class Spell_ConjurePGNagual( Spell_Conjure ):
	"""
	����ٻ��̹��ػ�����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Conjure.__init__( self )
		self.reqAccum = 0				# ��������

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Conjure.init( self, dict )
		self.reqAccum = int( dict["param2"] ) if dict["param2"] else 0 

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		targetEntity = target.getObject()
		if not targetEntity:
			ERROR_MSG( "Can't find target entity!" )
			return
			
		spaceScript = targetEntity.getCurrentSpaceScript()
		if not spaceScript.canGetAccum:														# ָ����ͼ
			return csstatus.SKILL_SPELL_NOT_SPECIAL_SPACE
			
		callPGDict = caster.queryTemp( "callPGDict", {} )
		npcIDs = []
		for id in callPGDict.values():
			npcIDs.extend( id )
		if len( npcIDs ) >= caster.queryTemp( "ROLE_CALL_PGNAGUAL_LIMIT", csconst.ROLE_CALL_PGNAGUAL_LIMIT ):	# ���ٻ������ж�
			return csstatus.SKILL_SPELL_CALL_PGNAGUAL_ENOUGH
		
		if caster.getAccum() < self.reqAccum:												# ����ֵ�ж�
			return csstatus.SKILL_SPELL_NOT_ENOUGH_ACCUM 
		
		return Spell_Conjure.useableCheck( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method = 0
		���ÿһ�������߽�����������������˺����ı����Եȵȡ�ͨ������´˽ӿ�����onArrive()���ã�
		�������п�����SpellUnit::receiveOnreal()�������ã����ڴ���һЩ��Ҫ�������ߵ�real entity�����������顣
		�������Ƿ���Ҫ��real entity���Ͻ��գ��ɼ����������receive()�������жϣ������ṩ��ػ��ơ�
		ע���˽ӿ�Ϊ�ɰ��е�onReceive()

		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		Spell_Conjure.receive( self, caster, receiver )
		caster.addAccumPoint( - self.reqAccum )