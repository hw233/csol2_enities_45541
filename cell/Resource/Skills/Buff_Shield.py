# -*- coding: gb18030 -*-
#
# $Id: Buff_Shield.py,v 1.9 2007-11-30 07:10:38 kebiao Exp $

"""
持续性效果
"""

import BigWorld
import csdefine
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_Shield( Buff_Normal ):
	"""
	护盾基础
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._shieldType = csdefine.SHIELD_TYPE_VOID
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )

	def getShieldType( self ):
		"""
		virtual method.
		获取护盾的类型
		"""
		return self._shieldType
	
	def isDisabled( self, receiver ):
		"""
		virtual method.
		护盾是否失效
		@param receiver: 受术者
		"""
		return True
		
	def doShield( self, receiver, damageType, damage ):
		"""
		virtual method.
		执行护盾自身功能  如：法术形转化伤害为MP 
		注意: 此接口不可手动删除该护盾
		@param receiver: 受术者
		@param damageType: 伤害类型
		@param damage : 本次伤害值
		@rtype: 返回被消减后的伤害值
		"""
		if self.isDisabled( receiver ):
			return damage
		return 0
#
# $Log: not supported by cvs2svn $
# 
#