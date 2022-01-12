# -*- coding:gb18030 -*-

from SpellBase import *
from bwdebug import *
import BigWorld
import csdefine
from bwdebug import *
from Buff_Normal import Buff_Normal

class Buff_22126( Buff_Normal ):
	"""
	每分钟获得当前若干点经验
	例如：总经验=角色当前等级*2^1.5*500；buff名称为师徒共勉，持续30分钟
	"""
	def init( self, dict ):
		"""
		"""
		Buff_Normal.init( self, dict )
		# 经验计算参数，玩家每分钟获得的经验是：角色当前等级*  2^1.5*修正参数  / 持续时间
		self.minExpParam = pow( 2, 1.5 ) * int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 ) / self._persistent * 60
		
	def doReload( self, receiver, buffData ):
		"""
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.addExp( receiver.level*self.minExpParam, csdefine.CHANGE_EXP_TEACH_BUFF )
		
	def doLoop( self, receiver, buffData ):
		"""
		"""
		receiver.addExp( receiver.level*self.minExpParam, csdefine.CHANGE_EXP_TEACH_BUFF )
		return Buff_Normal.doLoop( self, receiver, buffData )
		
	def doEnd( self, receiver, buffData ):
		"""
		"""
		receiver.addExp( receiver.level*self.minExpParam, csdefine.CHANGE_EXP_TEACH_BUFF )
		Buff_Normal.doEnd( self, receiver, buffData )
		