# -*- coding:gb18030 -*-
import math
from Spell_BuffNormal import Spell_BuffNormal
MAX_SPEED = 100.0

class Spell_Bounce( Spell_BuffNormal ):
	"""
	�����ﴴ��ʱ ��Ҫ����ҵ���
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )

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
		self.onArrive( caster, target )

	def onArrive( self, caster, target ):
		"""
		virtual method = 0.
		�����ִ�Ŀ��ͨ�档��Ĭ������£��˴�ִ�п�������Ա�Ļ�ȡ��Ȼ�����receive()�������ж�ÿ���������߽��д���
		ע���˽ӿ�Ϊ�ɰ��е�receiveSpell()

		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		# ��ȡ����������
		receivers = self.getReceivers( caster, target )
		for receiver in receivers:
			#��������ʱ������һЩ����
			self.receive( caster, receiver )
	
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if receiver.isDestroyed:
			return
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		self.receiveLinkBuff( caster, receiver )
		receiver.move_speed = MAX_SPEED
		receiver.receiveSpell( caster.id, self.getID(), 0, 0, 0 )
	
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
		s1 = caster.getBoundingBox().z / 2
		s2 = caster.getBoundingBox().x / 2
		radius = math.sqrt( s1*s1 + s2*s2 )
		return caster.entitiesInRangeExt( radius, "Role", caster.position )
