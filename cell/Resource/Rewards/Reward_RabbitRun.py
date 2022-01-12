# -*- coding: gb18030 -*-

from Reward import Reward
import Language
import csdefine
import csstatus
import items
g_items = items.instance()



class Reward_RabbitRun( Reward ):
	"""
	小兔快跑奖励
	"""
	def __init__( self ):
		"""
		只通过公式计算，没有表格
		"""
		self.type = csdefine.REWARD_RACE_HORSE
		Reward.__init__( self )


	def do( self, playerEntity ):
		"""
		1。经验奖励=角色等级*(30-名次)^2.8
		2。金钱奖励=角色等级*(30-名次)^2.8（和经验奖励公式一样，因为单位是铜币，所以奖励的并不算多）
		"""
		pass

		place = playerEntity.query( "rabbit_run_place", 0 )
		if place == 0:
			return
		
		if place <= 30:
			value = playerEntity.level*( 31 - place )**2.8
		else:
			value = playerEntity.level

		exp 	= value
		money 	= value

		playerEntity.gainMoney( money, csdefine.CHANGE_MONEY_RABBIT_RUN )
		playerEntity.addExp( exp, csdefine.CHANGE_EXP_RABBITRUN )
		playerEntity.remove( "rabbit_run_place" )

g_RR = Reward_RabbitRun()

