# -*- coding: gb18030 -*-
from config.item.EquipDefenceLevelConfig import Datas as equipDefenceData

"""
战斗系统相关公式 
"""

class CombatExp:	
	def __init__( self, attacker, target ):
		self.__assertValid( attacker, target )
		self.__attacker = attacker
		self.__target = target
		
		self.__initialize()
		
	def __initialize( self ):
		"""
		初始化并计算必要数据 所有基本数据计算应该在这里完成，公共方法只返回公式
		"""
		
		self.defenceLevelArg1 = equipDefenceData[ self.__target.level ][1]
		self.defenceLevelArg2 = equipDefenceData[ self.__target.level ][2]
		self.defenceLevelArg3 = equipDefenceData[ self.__target.level ][3]
		
	def __assertValid( self, attacker, target ):
		pass
	
	def getPhysicsDamageReductionRate( self ):
		"""
		物理防御减伤公式
		"""
		# 物理防御减伤百分比  = 物理防御值 / [ 物理防御值 + (参数_1 * 攻击方等级 + 参数_2 ) * 参数_3^( 0.1 * 攻击方等级-1) ]
		return self.__target.armor / ( self.__target.armor + ( self.defenceLevelArg1 * self.__attacker.level + self.defenceLevelArg2 ) * self.defenceLevelArg3 ** ( 0.1 * self.__attacker.level - 1 ) )
		
	
	def getMagicDamageReductionRate( self ):
		"""
		法术防御减伤公式
		"""
		# 法术防御减伤百分比  = 法术防御值 / [ 法术防御值 + (参数_1 * 攻击方等级 + 参数_2 ) * 参数_3^( 0.1 * 攻击方等级-1) ]
		return self.__target.magic_armor / ( self.__target.magic_armor + ( self.defenceLevelArg1 * self.__attacker.level + self.defenceLevelArg2 ) * self.defenceLevelArg3 ** ( 0.1 * self.__attacker.level - 1 ) )
		