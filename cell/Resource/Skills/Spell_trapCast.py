# -*- coding: gb18030 -*-

# ϵͳ���ܣ�����һ��AreaRestrictTransducer��entity(���幦��entity)����ʩ����λ��

import BigWorld
import csdefine
import csstatus
from SpellBase import *

class Spell_trapCast( Spell ):
	"""
	ϵͳ����
	����һ��AreaRestrictTransducer��entity(���幦��entity)
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		self.lifetime = 0				# ��������ʱ��
		self.radius = 0.0				# ����뾶
		self.enterSpell = 0				# ��������ʩ�ŵļ���
		self.leaveSpell = 0				# �뿪����ʩ�ŵļ���
		self.modelNumber =  ""			# �����Ӧ��ģ��(����Ч��)

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.lifetime = int( dict[ "param1" ] )
		self.radius = float( dict[ "param2" ] )
		self.enterSpell = int( dict[ "param3" ] )
		self.leaveSpell = int( dict[ "param4" ] )
		self.modelNumber = str( dict[ "param5" ] )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����ʵ�ֵ�Ŀ��
		"""
		if receiver.isReal():
			dict = { "radius" : self.radius, "enterSpell" : self.enterSpell, "leaveSpell" : self.leaveSpell, "destroySpell" : self.leaveSpell, "modelNumber" : self.modelNumber, "lifetime" : self.lifetime, "uname" : self.getName(), "casterID" : caster.id }
			caster.createEntityNearPlanes( "SkillTrap", caster.position, (0, 0, 0), dict )
		else:	# �����ghost��֧�֡�17:31 2009-1-16��wsf
			receiver.receiveOnReal( caster.id, self )
