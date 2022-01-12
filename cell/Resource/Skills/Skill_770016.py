# -*- coding: gb18030 -*-
#

import BigWorld
import csconst
import csdefine
import csstatus
from bwdebug import *

from SpellBase import *
from Skill_Normal import Skill_Normal


class Skill_770016( Skill_Normal ):
	"""
	骑宠技能 固本培元:主人及主人的出战宠物，获得5%的基础体质加成。
	"""
	def __init__( self ):
		"""
		"""
		Skill_Normal.__init__( self )
		self.param = 0


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Skill_Normal.init( self, dict )
		self.param = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 )  * 100.0


	def attach( self, ownerEntity ):
		"""
		virtual method
		为目标附上一个效果，通常被附上的效果是实例自身，它可以通过detach()去掉这个效果。具体效果由各派生类自行决定。

		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		ownerEntity.affectPropValue( "corporeity_percent", self.param * ownerEntity.queryTemp( "vehicleJoyancyEffect", 0.0 ), "calcDynamicProperties" )


	def detach( self, ownerEntity ):
		"""
		virtual method = 0;
		执行与attach()的反向操作

		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		ownerEntity.affectPropValue( "corporeity_percent", -self.param * ownerEntity.queryTemp( "vehicleJoyancyEffect", 0.0 ), "calcDynamicProperties" )

