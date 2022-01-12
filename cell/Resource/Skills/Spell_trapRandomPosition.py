# -*- coding: gb18030 -*-

# ϵͳ���ܣ�����һ��AreaRestrictTransducer��entity(���幦��entity)����һ����Χ�������һ��

import BigWorld
import csdefine
import csstatus
from SpellBase import *
import random

class Spell_trapRandomPosition( Spell ):
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
		self.randomRadius = 0			# ��������������Χ�뾶
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
		spellStr = str( dict["param3"] )
		self.enterSpell = int( spellStr.split(";")[0] )
		self.leaveSpell = int( spellStr.split(";")[1] )
		self.randomRadius = int( dict[ "param4" ] )
		self.modelNumber = str( dict[ "param5" ] )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����ʵ�ֵ�Ŀ��
		"""
		if receiver.isReal():
			dict = { \
				"radius" : self.radius,
				"enterSpell" : self.enterSpell,
				"leaveSpell" : self.leaveSpell,
				"destroySpell" : self.leaveSpell,
				"modelNumber" : self.modelNumber,
				"lifetime" : self.lifetime,
				"uname" : self.getName()\
			}
			pos = caster.position + ( random.randint(-self.randomRadius, self.randomRadius), 0, random.randint(-self.randomRadius, self.randomRadius) )
			trap = receiver.createEntityNearPlanes( "SkillTrap", pos, (0, 0, 0), dict )
		else:	# �����ghost��֧�֡�17:31 2009-1-16��wsf
			receiver.receiveOnReal( caster.id, self )
