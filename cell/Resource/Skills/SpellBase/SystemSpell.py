# -*- coding: gb18030 -*-

# ϵͳ��ĳ��Ŀ��ʩ�ŵļ��ܣ�������Ϊû��ԴĿ�꣬Ҳ������ΪԴĿ�����ϵͳ��

from Spell import Spell
import csstatus
import csdefine


# --------------------------------------------------------------------
# ���Ǽ̳д���ļ��ܶ�����ϵͳʩ�ŵļ��ܣ����нӿ��е������ж϶������
# ʩ�������κι�ϵ��Ĭ��Ϊû��ʩ���ߡ�
# --------------------------------------------------------------------
class SystemSpell( Spell ) :

	def __init__( self ) :
		Spell.__init__( self )


	# ----------------------------------------------------------------
	# virtual methods
	# ----------------------------------------------------------------
	def useableCheck( self, caster, target ) :
		"""
		virtual method
		������ϵͳʩ�ŵļ��ܣ���˲����ʩ�������κ��ж�
		������Ϊϵͳ��ĳ��Ŀ��ʩ�ŵļ����ǲ��ɿ��ܵġ�
		"""
		return csstatus.SKILL_GO_ON

	def use( self, caster, target ) :
		"""
		virtual method
		û����������ȴ��Щ����
		"""
		self.cast( caster, target )

	def cast( self, caster, target ) :
		"""
		virtual method
		ϵͳʩ�ţ�û�������壬���Զ���˲��
		"""
		self.onArrive( caster, target )

	def onArrive( self, caster, target ) :
		"""
		virtual method
		��������󣬻�ȡ�����ߣ�ϵͳ������������Ŀ��ģ�
		���Ҫ��һЩ��Ҫ�ж�
		"""
		receivers = self.getReceivers( caster, target )
		for receiver in receivers:
			receiver.clearBuff( self._triggerBuffInterruptCode )
			self.receive( caster, receiver )

	def getReceivers( self, caster, target ) :
		"""
		virtual method
		Ĭ��ֻ������Ŀ��ʩ�š�
		"""
		receivers = []
		targetEntity = target.getObject()
		if not targetEntity.isDestroyed and ( \
		targetEntity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or \
		targetEntity.isEntityType( csdefine.ENTITY_TYPE_PET ) ):
			receivers.append( targetEntity )
		return receivers