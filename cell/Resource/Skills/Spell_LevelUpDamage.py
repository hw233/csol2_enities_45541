# -*- coding: gb18030 -*-

import BigWorld
import csstatus
import csdefine
import math
from SpellBase import *
from VehicleHelper import getCurrVehicleID

class Spell_LevelUpDamage( CombatSpell ):
	"""
	����������Χ�˺�����ר�ýű�
	"""
	def __init__( self ):
		"""
		���캯��
		"""
		CombatSpell.__init__( self )
		self._damageType = csdefine.DAMAGE_TYPE_VOID	# �˺������ݶ�Ϊ������
		self._damage = 0								# �����˺�

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		CombatSpell.init( self, dict )
		self._damage = int( dict["param1"] ) if len( dict["param1"] ) > 0 else 0

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ��
		return type:int
		"""
		if getCurrVehicleID( caster ):	# ���״̬���޷�����
			return csstatus.SKILL_NO_MSG

		return csstatus.SKILL_GO_ON

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		if receiver.isDestroyed:
			return
		
		finiDamage = self._damage
		#�������С��Ƶд�����ʵ�ʼ��� 
		reRate = self.calReduceDamage( caster, receiver )
		rm =  1 - reRate
		finiDamage *= rm
			
		self.persentDamage( caster, receiver, self._damageType, max( 1, int( finiDamage ) ) )
		self.receiveLinkBuff( caster, receiver )