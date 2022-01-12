# -*- coding: gb18030 -*-

from bwdebug import *
import csdefine
from CEquip import CEquip

class CFashion( CEquip ):
	"""
	时装
	"""
	def __init__( self, srcData ):
		CEquip.__init__( self, srcData )

	def getFDict( self ):
		"""
		Virtual Method
		获取法宝效果类型自定义数据格式
		用于发送到客户端
		return INT32
		"""
		return self.model()

	def wield( self, owner, update = True ):
		"""
		装备时装

		@param  owner: 时装拥有者
		@type   owner: Entity
		@param update: 是否立即生效
		@type  update: bool
		@return:    True 装备成功，False 装备失败
		@return:    BOOL
		"""
		if not CEquip.wield( self, owner, update ):
			return False
		if update: owner.calcDynamicProperties()
		return True

	def unWield( self, owner, update = True ):
		"""
		卸下时装

		@param  owner: 时装拥有者
		@type   owner: Entity
		@param update: 是否立即生效
		@type  update: bool
		@return:    无
		"""
		# 如果没有装备效果则不用unwield
		if not self.isAlreadyWield(): return
		CEquip.unWield( self, owner, update )
		return True