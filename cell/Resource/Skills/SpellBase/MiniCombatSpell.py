# -*- coding: gb18030 -*-

import csdefine
import csstatus
from CombatSpell import CombatSpell
import time

class MiniCombatSpell( CombatSpell ):
	def useableCheck( self, caster, target ):
		"""
		"""
		# ʩ���߼��
		if caster.getState() == csdefine.ENTITY_STATE_DEAD:
			return csstatus.SKILL_IN_DEAD

		if self.getRangeMax( self ) + caster.getBoundingBox().z / 2 + target.getObject().getBoundingBox().z / 2  \
			< caster.getGroundPosition().distTo( target.getObject().getGroundPosition() ):  # ����׷����ʱ��ʹ�õ��ǵ�����������жϣ��������Ҳ���õ�������
			return csstatus.SKILL_TOO_FAR
		return csstatus.SKILL_GO_ON

	def persentDamage( self, caster, receiver, damageType, finiDamage ):
		"""
		virtual method.
		"""
		receiver.receiveSpell( caster.id, self.getID(), damageType, finiDamage, 0 )
		receiver.receiveDamage( caster.id, self.getID(), damageType, finiDamage )

	def use( self, caster, target ):
		"""
		"""
		if not self.isNotRotate:
			caster.rotateToSpellTarget( target )					# ת��
		self.cast( caster, target )

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
		caster.planesAllClients( "castSpell", ( self.getID(), target ) )
		caster.addCastQueue( self, target, 0.1 )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if receiver.isDestroyed:
			return
		finiDamage = 20
		
		#�������С��Ƶд�����ʵ�ʼ��� 
		reRate = self.calReduceDamage( caster, receiver )
		rm =  1 - reRate
		finiDamage *= rm
		
		self.persentDamage( caster, receiver, self._damageType, finiDamage )

