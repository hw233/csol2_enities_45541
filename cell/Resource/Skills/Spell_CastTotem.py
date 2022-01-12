# -*- coding: gb18030 -*-

# ϵͳ���ܣ�����һ��AreaRestrictTransducer��entity(���幦��entity)����ʩ����λ��

import BigWorld
import csdefine
import csstatus
import utils
from SpellBase import *

class Spell_CastTotem( Spell ):
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
		self.repeattime = 0				# ѭ���˺�ʱ��
		self.radius = 0.0				# ����뾶
		self.enterSpell = 0				# ��������ʩ�ŵļ���
		self.leaveSpell = 0				# �뿪����ʩ�ŵļ���
		self.destroySpell = 0			# ��������ʱ�ͷŵļ���
		self.modelNumber =  ""			# �����Ӧ��ģ��(����Ч��)
		self.isDisposable = False		# �Ƿ�һ�������壨������һ�ξ����٣�

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		timeStr = dict[ "param1" ]
		timeList = [int( t ) for t in timeStr.split(",") ]
		self.lifetime = timeList[0]
		if len( timeList ) >= 2:
			self.repeattime = timeList[1]
			
		self.radius = float( dict[ "param2" ] )
		self.modelNumber = str( dict[ "param3" ]).split(";")[0] 
		self.casterMaxDistanceLife = int( dict[ "param4" ] )

		if len( dict[ "param5" ] ) > 0:
			self.enterSpell, self.leaveSpell, self.destroySpell, self.isDisposable = [ int(s) for s in dict[ "param5" ].split(",") ]
	
	def _getDict( self, caster, target ):
		dict = { "radius" : self.radius, \
			"enterSpell" : self.enterSpell, \
			"leaveSpell" : self.leaveSpell, \
			"destroySpell" : self.destroySpell, \
			"originSkill" : self.getID(), \
			"modelNumber" : self.modelNumber, \
			"casterMaxDistanceLife" : self.casterMaxDistanceLife, \
			"isDisposable" : self.isDisposable, \
			"lifetime" : self.lifetime, \
			"repeattime" : self.repeattime, \
			"casterID" : caster.id, \
			"uname" : self.getName() }
			
		return dict
		
	def onArrive( self, caster, target ):
		caster.createEntityNearPlanes( "SkillTrap", target.getObjectPosition(), (0, 0, 0), self._getDict( caster, target ) )
		Spell.onArrive( self, caster, target )


class Spell_CastTotemNotCaster( SystemSpell ):
	#Ŀ����entity
	def __init__( self ):
		"""
		���캯����
		"""
		SystemSpell.__init__( self )
		self.lifetime = 0				# ��������ʱ��
		self.repeattime = 0				# ѭ���˺�ʱ��
		self.radius = 0.0				# ����뾶
		self.enterSpell = 0				# ��������ʩ�ŵļ���
		self.leaveSpell = 0				# �뿪����ʩ�ŵļ���
		self.destroySpell = 0			# ��������ʱ�ͷŵļ���
		self.modelNumber =  ""			# �����Ӧ��ģ��(����Ч��)
		self.isDisposable = False		# �Ƿ�һ�������壨������һ�ξ����٣�

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		SystemSpell.init( self, dict )
		timeStr = dict[ "param1" ]
		timeList = [int( t ) for t in timeStr.split(",") ]
		self.lifetime = timeList[0]
		if len( timeList ) >= 2:
			self.repeattime = timeList[1]
			
		self.radius = float( dict[ "param2" ] )
		self.modelNumber = str( dict[ "param3" ]).split(";")[0] 
		self.casterMaxDistanceLife = int( dict[ "param4" ] )

		if len( dict[ "param5" ] ) > 0:
			self.enterSpell, self.leaveSpell, self.destroySpell, self.isDisposable = [ int(s) for s in dict[ "param5" ].split(",") ]
			
	def _getDict( self, caster, target ):
		dict = { "radius" : self.radius, \
			"enterSpell" : self.enterSpell, \
			"leaveSpell" : self.leaveSpell, \
			"destroySpell" : self.destroySpell, \
			"originSkill" : self.getID(), \
			"modelNumber" : self.modelNumber, \
			"casterMaxDistanceLife" : self.casterMaxDistanceLife, \
			"isDisposable" : self.isDisposable, \
			"lifetime" : self.lifetime, \
			"repeattime" : self.repeattime, \
			"casterID" : 0, \
			"uname" : self.getName() }
			
		return dict
	
	def onArrive( self, caster, target ):
		targetEntity = target.getObject()
		targetEntity.createEntityNearPlanes( "SkillTrap", utils.navpolyToGround( targetEntity.spaceID, target.getObjectPosition(), 0.2, 20.0 ), (0, 0, 0), self._getDict( caster, target ) )
		SystemSpell.onArrive( self, caster, target )