# -*- coding: gb18030 -*-
#
from bwdebug import *
from Buff_Normal import Buff_Normal
import csdefine
from config.server.FlawMonster import Datas as g_flawMonster
import random

class Buff_170005( Buff_Normal ):
	"""
	破绽演化BUFF
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self.param1 = 0
		self.param2 = 0
		self.param3 = 0
		self.param4 = 0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self.param1 = int( dict["Param1"] )			# 触发技能ID
		self.param2 = int( dict["Param2"] )			# 演化技能ID

		oddsList = dict["Param3"].split(",")
		if len( oddsList ) == 2:
			self.param3 = int( oddsList[0] )		# 触发概率
			self.param4 = int( oddsList[1] )		# 演化概率

	def receive( self, caster, receiver ):
		"""
		用于给目标施加一个buff，所有的buff的接收都必须通过此接口，
		此接口必须判断接收者是否为realEntity，
		如果否则必须要通过receiver.receiveOnReal()接口处理。

		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者，None表示不存在
		@type  receiver: Entity
		"""
		if caster is None: return
		if not receiver.isEntityType( csdefine.ENTITY_TYPE_MONSTER ): return
		if receiver.className not in g_flawMonster: return

		buffIndex = receiver.getBuffIndexByType( csdefine.BUFF_TYPE_FLAW )
		if buffIndex == -1:
			odds = self.param3
			skillID = self.getSourceSkillID()/1000
			odds += caster.skillBuffOdds.getOdds( skillID ) * 100
			if random.randint( 1, 100 ) <= odds:
				caster.spellTarget( self.param1, receiver.id )
		else:
			if random.randint( 1, 100 ) <= self.param4:
				caster.spellTarget( self.param2, receiver.id )
