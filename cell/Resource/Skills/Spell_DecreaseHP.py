# -*- coding: gb18030 -*-
from SpellBase import *
import csstatus
import csdefine

class Spell_DecreaseHP( CombatSpell ):
	# ������Χָ������entity��Ѫ�����ٷֱȣ�
	def __init__( self ):
		"""
		���캯����
		"""
		CombatSpell.__init__( self )
		self.entityNames = []
		self.percentage = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		CombatSpell.init( self, dict )
		self.entityNames = dict[ "param1" ].split( ";" )
		self.percentage = int( dict[ "param2" ] )
	
	def getReceivers( self, caster, target ):
		receivers = CombatSpell.getReceivers( self, caster, target )
		for i, entity in enumerate( receivers ):
			if entity.__module__ not in self.entityNames:
				receivers.pop( i )
		
		return receivers
	
	def receive( self, caster, receiver ):
		# ����������Ҫ��������
		if receiver.isDestroyed:
			return
			
		finiDamage = int( receiver.HP_Max * self.percentage / 100 )
		#�������С��Ƶд�����ʵ�ʼ��� 
		reRate = self.calReduceDamage( caster, receiver )
		rm =  1 - reRate
		finiDamage *= rm
			
		self.persentDamage( caster, receiver, self._damageType, max( 1, int( finiDamage ) ) )
		self.receiveLinkBuff( caster, receiver )