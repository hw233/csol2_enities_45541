# -*- coding: gb18030 -*-

# ���ѡ��λ�����ɶ��AreaRestrictTransducer��entity(���幦��entity)

import BigWorld
import random
from utils import vector3TypeConvert
from SpellBase import *

class Spell_CastRandomTrap( Spell ):
	"""
	������������ͷ�ָ�����������弼��
	"""
	def __init__( self ):
		"""
		���캯��
		"""
		Spell.__init__( self )
		self.skillIDs = []				# ����IDs
		self.skillNum = 1				# �������
		self.probSkill = 1				# �и����ͷŵļ���
		self.activeRate = 0				# probSkill�ͷŵĸ���

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.skillIDs = str( dict["param1"] ).strip( ";" ).split( ";" )
		self.skillNum = int( dict["param2"] )
		self.probSkill = str( dict["param3"] ).strip( ";" ).split( ";" )[0]
		self.activeRate = float( str( dict["param3"] ).strip( ";" ).split( ";" )[1] )
		
	def getRandomSkill( self ):
		"""
		�������ͷż���
		"""
		if self.activeRate <= 0 or random.randint( 0, 100 ) > self.activeRate:			# probSkill�������ͷ�
			if self.skillNum > len( self.skillIDs ):
				ERROR_MSG( "Skill %i config error, its skillNum is larger than skill counts" % self.getID() )
				return []
			return random.sample( self.skillIDs, self.skillNum )
			
		if self.skillNum -1 > len( self.skillIDs ):
			ERROR_MSG( "Skill %i config error, its skillNum is larger than skill counts" % self.getID() )
			return []
		skills = []
		skills = random.sample( self.skillIDs, self.skillNum - 1 )
		skills.append( self.probSkill )
		return skills

	def cast( self, caster, target ):
		"""
		virtual method.
		����ʵ�ֵ�Ŀ��
		"""
		randList = self.getRandomSkill()
		for skill in randList:
			if caster:
				caster.spellTarget( int( skill ), caster.id )

class Spell_TrapSpecificPosition( Spell ):
	"""
	��ָ��λ������һ��AreaRestrictTransducer��entity(���幦��entity)
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		self.lifetime = 0				# ��������ʱ��
		self.isDisposable = 0			# �Ƿ�һ�������壨������һ�ξ����٣�
		self.radius = 0.0				# ����뾶
		self.enterSpell = 0				# ��������ʩ�ŵļ���
		self.leaveSpell = 0				# �뿪����ʩ�ŵļ���
		self.modelNumber =  ""			# �����Ӧ��ģ��(����Ч��)
		self.modelScale = 1.0			# ģ�����ű���
		self.position = None			# ����λ��

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		timeList = str( dict["param1"] ).strip( ";" ).split( ";" )
		self.lifetime = int( timeList[0] )
		if len( timeList ) >= 2:
			self.isDisposable = int( timeList[1])
			
		self.radius = float( dict[ "param2" ] )
		spellStr = str( dict["param3"] ).strip( ";" ).split( ";" )
		self.enterSpell = int( spellStr[0] )
		if len( spellStr ) >= 2:
			self.leaveSpell = int( spellStr[1] )
		
		modelStr = str( dict[ "param4"] ).strip( ";" ).split( ";" )
		self.modelNumber = str( modelStr[0] )
		if len( modelStr ) >= 2:
			self.modelScale = float( modelStr[1] )
		
		self.position = vector3TypeConvert( str( dict[ "param5" ] ) )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����ʵ�ֵ�Ŀ��
		"""
		dict = { "radius" : self.radius, "enterSpell" : self.enterSpell, "destroySpell" : self.leaveSpell,\
				"modelNumber" : self.modelNumber, "lifetime" : self.lifetime, "uname" : self.getName(),\
				 "isDisposable" : self.isDisposable, }
		trap = caster.createEntityNearPlanes( "AreaRestrictTransducer", self.position, (0, 0, 0), dict )
		trap.modelScale = self.modelScale				# ��������ģ�͵����ű���
