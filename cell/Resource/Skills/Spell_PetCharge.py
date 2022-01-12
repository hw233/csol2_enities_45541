# -*- coding: gb18030 -*-

import BigWorld
import csdefine
from Spell_PhysSkill import Spell_PhysSkill2

class Spell_PetCharge( Spell_PhysSkill2 ):
	"""
	�����漼��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_PhysSkill2.__init__( self )

	def init( self, dict ):
		"""
		��ȡ����
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_PhysSkill2.init( self, dict )

	def cast( self, caster, target ):
		"""
		virtual method.
		��ʽ��һ��Ŀ���λ��ʩ�ţ���з��䣩�������˽ӿ�ͨ��ֱ�ӣ����ӣ���intonate()�������á�

		ע���˽ӿڼ�ԭ���ɰ��е�castSpell()�ӿ�

		@param     caster: ʹ�ü��ܵ�ʵ��
		@type      caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		#֪ͨ���пͻ��˲��Ŷ���/����������
		caster.planesAllClients( "castSpell", ( self.getID(), target ) )
		self.setCooldownInIntonateOver( caster )
		# ��������
		self.doRequire_( caster )
		#��֤�ͻ��˺ͷ������˴����������һ��
		delay = self.calcDelay( caster, target )
		# �ӳ�
		caster.addCastQueue( self, target, delay + 0.35 )
		# ����ʩ�����֪ͨ����һ���ܴ�����Ŷ(�Ƿ��ܴ����Ѿ���ʩ��û�κι�ϵ��)��
		# �����channel����(δʵ��)��ֻ�еȷ�����������ܵ���
		self.onSkillCastOver_( caster, target )
