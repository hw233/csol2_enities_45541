# -*- coding: gb18030 -*-

from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus

from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_66012( Buff_Normal ):
	"""
	增加物理暴击率或是法术暴击率 
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self.phy = 0.0
		self.mag = 0.0
		self.magDoubleHit = 0.0
		self.phyDoubleHit = 0.0


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		Param1 格式：a;b;c;d
			a；物理攻击增加百分比
			b；法术攻击增加百分比
			c：物理暴击率增加百分比
			d：法术暴击率增加百分比
		0.0 =< a/b/c/d =< 1.0
		"""
		

		Buff_Normal.init( self, dict )
		self._p1 =  dict[ "Param1" ]
		if self._p1 != "" :
			tmp = self._p1.split( ";" ) # bug here
			self.phy = float( tmp[0] ) * csconst.FLOAT_ZIP_PERCENT
			self.mag = float( tmp[1] ) * csconst.FLOAT_ZIP_PERCENT
			self.phyDoubleHit = float( tmp[2] ) * csconst.FLOAT_ZIP_PERCENT
			self.magDoubleHit = float( tmp[3] ) * csconst.FLOAT_ZIP_PERCENT
			
		
	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果开始的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		
		#物理攻击
		receiver.damage_min_percent += self.phy
		receiver.damage_max_percent += self.phy
		receiver.calcDamageMin()
		receiver.calcDamageMax()
		
		#法术攻击
		receiver.magic_damage_percent += self.mag
		receiver.calcMagicDamage()
		
		#物理暴击率
		receiver.double_hit_probability_percent += self.phyDoubleHit
		receiver.calcDoubleHitProbability()
		
		#法术暴击率
		receiver.magic_double_hit_probability_percent += self.magDoubleHit
		receiver.calcMagicDoubleHitProbability()
		
	
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		
		#物理攻击
		receiver.damage_min_percent -= self.phy
		receiver.damage_max_percent -= self.phy
		receiver.calcDamageMin()
		receiver.calcDamageMax()
		
		#法术攻击
		receiver.magic_damage_percent -= self.mag
		receiver.calcMagicDamage()
		
		#物理暴击率
		receiver.double_hit_probability_percent -= self.phyDoubleHit
		receiver.calcDoubleHitProbability()
		
		#法术暴击率
		receiver.magic_double_hit_probability_percent -= self.magDoubleHit
		receiver.calcMagicDoubleHitProbability()
			
	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果重新加载的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )

		#物理攻击
		receiver.damage_min_percent += self.phy
		receiver.damage_max_percent += self.phy
		#法术攻击
		receiver.magic_damage_percent += self.mag
		#物理暴击率
		receiver.double_hit_probability_percent += self.phyDoubleHit
		#法术暴击率
		receiver.magic_double_hit_probability_percent += self.magDoubleHit
		
