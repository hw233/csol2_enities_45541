# -*- coding:gb18030 -*-

from Spell_MagicHomingChild import Spell_MagicHomingChild
import csconst
import random
import csstatus
import csdefine
from Function import newUID
from bwdebug import *

class Spell_FirstMagicHomingChild( Spell_MagicHomingChild ):
	"""
	����������һ���Ӽ���
	"""
	def __init__( self ):
		"""
		"""
		Spell_MagicHomingChild.__init__( self )

	def onMiss( self, damageType, caster, receiver ):
		"""
		����δ����
		"""
		Spell_MagicHomingChild.onMiss( self, damageType, caster, receiver )

class Spell_FixTargetFirstMagicHomingChild( Spell_FirstMagicHomingChild ):
	"""
	�̶�Ŀ�귨��������һ���Ӽ���
	"""

	def __init__( self ):
		"""
		"""
		Spell_FirstMagicHomingChild.__init__( self )
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