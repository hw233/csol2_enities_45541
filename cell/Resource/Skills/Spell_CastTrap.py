# -*- coding: gb18030 -*-

# ϵͳ���ܣ�����һ��AreaRestrictTransducer��entity(���幦��entity)���ڹ�������ʱ��λ��

import BigWorld
import csdefine
import csstatus
from SpellBase import *

class Spell_CastTrap( Spell ):
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
		self.isDisposable = 0			# �Ƿ�һ�������壨������һ�ξ����٣�
		self.modelNumber =  ""			# �����Ӧ��ģ��(����Ч��)
		self._modelScale = 1.0			# ����ģ�����ű���

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.lifetime = int( dict[ "param1" ] )
		self.radius = float( dict[ "param2" ] )
		spellStr = str( dict["param3"] )
		self.enterSpell = int( spellStr.split(":")[0] )
		self.leaveSpell = int( spellStr.split(":")[1] )
		self.isDisposable = int( dict[ "param4" ] )
		spellStr_ = str( dict[ "param5" ] )
		self.modelNumber = str( spellStr_.split(":")[0] )
		self._modelScale = float( spellStr_.split(":")[1] )

	def cast( self, caster, target ):
		"""
		virtual method.
		����ʵ�ֵ�Ŀ��
		"""
		dict = { "radius" : self.radius, "enterSpell" : self.enterSpell, "destroySpell" : self.leaveSpell, "modelNumber" : self.modelNumber, "lifetime" : self.lifetime, "uname" : self.getName(),"isDisposable" : self.isDisposable }
		trap = caster.createEntityNearPlanes( "AreaRestrictTransducer", caster.position, (0, 0, 0), dict )
		trap.modelScale = self._modelScale		# ��������ģ�͵����ű���
