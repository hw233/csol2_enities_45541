# -*- coding: gb18030 -*-
from config.item.EquipDefenceLevelConfig import Datas as equipDefenceData

"""
ս��ϵͳ��ع�ʽ 
"""

class CombatExp:	
	def __init__( self, attacker, target ):
		self.__assertValid( attacker, target )
		self.__attacker = attacker
		self.__target = target
		
		self.__initialize()
		
	def __initialize( self ):
		"""
		��ʼ���������Ҫ���� ���л������ݼ���Ӧ����������ɣ���������ֻ���ع�ʽ
		"""
		
		self.defenceLevelArg1 = equipDefenceData[ self.__target.level ][1]
		self.defenceLevelArg2 = equipDefenceData[ self.__target.level ][2]
		self.defenceLevelArg3 = equipDefenceData[ self.__target.level ][3]
		
	def __assertValid( self, attacker, target ):
		pass
	
	def getPhysicsDamageReductionRate( self ):
		"""
		����������˹�ʽ
		"""
		# ����������˰ٷֱ�  = �������ֵ / [ �������ֵ + (����_1 * �������ȼ� + ����_2 ) * ����_3^( 0.1 * �������ȼ�-1) ]
		return self.__target.armor / ( self.__target.armor + ( self.defenceLevelArg1 * self.__attacker.level + self.defenceLevelArg2 ) * self.defenceLevelArg3 ** ( 0.1 * self.__attacker.level - 1 ) )
		
	
	def getMagicDamageReductionRate( self ):
		"""
		�����������˹�ʽ
		"""
		# �����������˰ٷֱ�  = ��������ֵ / [ ��������ֵ + (����_1 * �������ȼ� + ����_2 ) * ����_3^( 0.1 * �������ȼ�-1) ]
		return self.__target.magic_armor / ( self.__target.magic_armor + ( self.defenceLevelArg1 * self.__attacker.level + self.defenceLevelArg2 ) * self.defenceLevelArg3 ** ( 0.1 * self.__attacker.level - 1 ) )
		