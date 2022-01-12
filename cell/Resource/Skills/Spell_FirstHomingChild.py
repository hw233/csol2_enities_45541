# -*- coding:gb18030 -*-

from SpellBase.Spell import Spell
from Spell_HomingChild import Spell_HomingChild,Spell_TargetChangeHomingChild,Spell_HomingChild_Distance
import csconst
import csdefine
import random
import Math
import csstatus
from Function import newUID
import SkillTargetObjImpl
from bwdebug import *

class Spell_FirstHomingChild( Spell_HomingChild ):
	"""
	����������һ���Ӽ���
	"""
	def __init__( self ):
		"""
		"""
		Spell_HomingChild.__init__( self )

	def onMiss( self, damageType, caster, receiver ):
		"""
		����δ����
		"""
		Spell_HomingChild.onMiss( self, damageType, caster, receiver )

class Spell_FixTargetFirstHomingChild( Spell_FirstHomingChild ):
	"""
	�̶�Ŀ������������һ���Ӽ���
	"""

	def __init__( self ):
		"""
		"""
		Spell_FirstHomingChild.__init__( self )
		self._receivers = []

	def onUse( self, caster, target, receivers ) :
		"""
		"""
		self._receivers = receivers
		data = self.addToDict()
		nSkill = self.createFromDict( data )
		nSkill.cast( caster, target )

	def getReceivers( self, caster, target ):
		"""
		virtual method
		ȡ�����еķ���������������Entity�б�
		���е�onArrive()������Ӧ�õ��ô˷�������ȡ��Ч��entity��
		@return: array of Entity

		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@rtype: list of Entity
		"""
		return self._receivers

	def valid( self, target ):
		"""
		���Ŀ���Ƿ�������
		"""
		spellTarget = target.getObject()
		try:
			if spellTarget.state == csdefine.ENTITY_STATE_DEAD:
				return csstatus.SKILL_CHANGE_TARGET
			return csstatus.SKILL_GO_ON
		except AttributeError, errstr:
			# ֻ������󣬵���Ȼ��Ч���õ�Ҫ�󲻷��ϵĽ��
			# ԭ�������������Ʒ��һ���entity�ǲ����У�����������û�У�isDead()������
			INFO_MSG( errstr )
		return csstatus.SKILL_CHANGE_TARGET

	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{ "param": None }������ʾ�޶�̬���ݡ�

		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		"""
		return { "param" : { "receivers" : self._receivers } }

	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�

		@type data: dict
		"""
		obj = self.__class__()
		obj.__dict__.update( self.__dict__ )

		obj._receivers = data["param"]["receivers"]

		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj

class Spell_FirstTargetChangeHomingChild( Spell_TargetChangeHomingChild ):
	"""
	������һ���Ӽ���-Ŀ�����Լ�
	"""
	def __init__( self ):
		"""
		"""
		Spell_TargetChangeHomingChild.__init__( self )

	def onMiss( self, damageType, caster, receiver ):
		"""
		����δ����
		"""
		# ���㿪�˲���������û���㣬��˳�����п��ܴ��ڵģ���Ҫ֪ͨ�ܵ�0���˺�
		receiver.receiveSpell( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0, 0 )
		receiver.receiveDamage( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0 )
		caster.doAttackerOnDodge( receiver, damageType )
		receiver.doVictimOnDodge( caster, damageType )


class Spell_FirstHomingChild2( Spell ):
	"""
	�����ƶ���ָ��λ��
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )

		# ʩ����λ������
		self.moveTime = 0.0

	def init( self, data ):
		"""
		"""
		Spell.init( self, data )
		self.moveTime = float( data["param2"] )

	def cast( self, caster, target ) :
		Spell.cast( self, caster, target )
		dist = caster.position.distTo( target.getObjectPosition() )
		moveSpeed = dist / self.moveTime
		caster.moveToPosFC( Math.Vector3( target.getObjectPosition() ), moveSpeed, True )

class Spell_FirstHomingChild3( Spell ):
	"""
	ֱ��λ�Ƶ�ĳλ��
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )

		# ʩ����λ������
		self.maxDist = 0.0

	def init( self, data ):
		"""
		"""
		Spell.init( self, data )

	def cast( self, caster, target ) :
		Spell.cast( self, caster, target )
		caster.position = target.getObjectPosition()

class Spell_FirstHomingChild4( Spell_HomingChild_Distance ):
	"""
	����嵽��ҵ�λ��
	"""
	def __init__( self ):
		"""
		"""
		Spell_HomingChild_Distance.__init__( self )

	def onMiss( self, damageType, caster, receiver ):
		"""
		����δ����
		"""
		Spell_HomingChild_Distance.onMiss( self, damageType, caster, receiver )
