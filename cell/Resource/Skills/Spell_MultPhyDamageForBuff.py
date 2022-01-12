# -*- coding:gb18030 -*-

from Spell_PhysSkill import Spell_PhysSkill

class Spell_MultPhyDamageForBuff( Spell_PhysSkill ):
	"""
	�౶�����˺����ܣ����������������ĳ��buff����ô�ᰴ�������������˺�
	"""
	def __init__( self ):
		"""
		"""
		Spell_PhysSkill.__init__( self )
		self.multParam = 1.0		# �����˺��ı���
		self.buffID = 0				# ��Ӱ���buff���
		
	def init( self, data ):
		"""
		"""
		Spell_PhysSkill.init( self, data )
		self.multParam = float( data["param1"] ) if len( data["param1"] ) else 1.0
		self.buffID = int( data["param2"] ) if len( data["param2"] ) else 0
		
	def receive( self, caster, receiver ):
		"""
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
			
		Spell_PhysSkill.receive( self, caster, receiver )
		
	def persentDamage( self, caster, receiver, damageType, damage ):
		"""
		"""
		if receiver.findBuffByBuffID( self.buffID ):
			damage *= self.multParam
		Spell_PhysSkill.persentDamage( self, caster, receiver, damageType, damage )
		