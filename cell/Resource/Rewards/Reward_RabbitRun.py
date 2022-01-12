# -*- coding: gb18030 -*-

from Reward import Reward
import Language
import csdefine
import csstatus
import items
g_items = items.instance()



class Reward_RabbitRun( Reward ):
	"""
	С�ÿ��ܽ���
	"""
	def __init__( self ):
		"""
		ֻͨ����ʽ���㣬û�б��
		"""
		self.type = csdefine.REWARD_RACE_HORSE
		Reward.__init__( self )


	def do( self, playerEntity ):
		"""
		1�����齱��=��ɫ�ȼ�*(30-����)^2.8
		2����Ǯ����=��ɫ�ȼ�*(30-����)^2.8���;��齱����ʽһ������Ϊ��λ��ͭ�ң����Խ����Ĳ�����ࣩ
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

