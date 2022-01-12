# -*- coding: gb18030 -*-

"""
心旷神怡
"""

from Buff_Normal import Buff_Normal

class Buff_22111( Buff_Normal ):
	"""
	心旷神怡buff，不断增加潜能（当然，指的是有效时间内，数值相当该玩家没加任何状态下获得经验量）
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = ( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else "" ) 					# 增加潜能的公式--和经验值配置相同
		self._p2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 ) 					# 每天最多可以晒多长时间（ 单位是秒 ）--和经验值配置相同
		self._hpVal = int( self._p1[ 3:len( self._p1 ) ] )		# 增加的经验值
		self._hpOpt = self._p1[ 2:3 ]					# 操作符

	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		用于buff，表示buff在每一次心跳时应该做什么。
		"""
		# 判断是否在日光浴合法时间中
		if receiver.isSunBathing() and receiver.sunBathDailyRecord.sunBathCount < self._p2:
			increasePotential = self.getIncreasePotential( receiver.level, self._hpOpt, self._hpVal )
			receiver.addPotential ( increasePotential )
			
		return Buff_Normal.doLoop( self, receiver, buffData )
		
	def getIncreasePotential( self, level, opration, value ):
		"""
		根据公式获得减少的血量
		"""
		return level + value