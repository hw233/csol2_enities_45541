# -*- coding: gb18030 -*-
#
# $Id: Spell_HP.py,v 1.1 2008-08-30 10:01:12 wangshufeng Exp $

from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus
import random
from SpellBase import *
from Spell_Magic import Spell_Magic


class Spell_112034( Spell_Magic ):
	"""
	城战 龙炮技能：只能攻击塔楼,造成固定伤害,与防御无关.
	"""
	def __init__( self ):
		"""
		"""
		Spell_Magic.__init__( self )
		self._p1 = 0
		
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )
		self._p1 = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ) 	
		self._p2 = int( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else 0 ) 	
		
	def calcDamageScissor( self, caster, receiver, damage ):
		"""
		virtual method.
		计算被攻击方物理伤害削减
		伤害=物理伤害x (1 – 被攻击方物理伤害减免率) 
		– 被攻击方物理伤害减免值
		伤害下限为0。
		注：伤害为DOT型持续伤害则对其伤害总值削减后再分次作用。
		其中，物理伤害减免率及物理伤害减免值参考公式文档，公式如下：
		角色基础物理伤害减免点数（总公式中的基础值）=0
		角色基础物理伤害减免值（总公式中的基础值）=0
		@param target: 被攻击方
		@type  target: entity
		@param  damage: 经过招架判断后的伤害
		@type   damage: INT
		@return: INT32
		"""
		return damage
		
#$Log: not supported by cvs2svn $
#
#