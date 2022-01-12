# -*- coding: gb18030 -*-

from bwdebug import *
from CEquip import CEquip
import csdefine
import csstatus
import csconst
import ItemTypeEnum

class CPotentialBook( CEquip ):
	"""
	潜能书 by 姜毅
	"""
	def __init__( self, srcData ):
		"""
		"""
		CEquip.__init__( self, srcData )
		
	def getPotential( self ):
		"""
		获得书上潜能
		"""
		temp = self.query( "param2" )
		if temp is None:
			return 0
		return int( temp )
		
	def getPotentialMax( self ):
		"""
		获得书上最大潜能
		"""
		return int( self.queryTemp( "param1", 0 ) )
		
	def getPotentialRate( self ):
		"""
		获得潜能附加率
		"""
		return float( self.queryTemp( "param3", 0 ) )
		
	def isPotentialMax( self ):
		"""
		潜能书是否满了
		"""
		return self.getPotential() >= self.getPotentialMax()
		
	def use( self, owner, target ):
		"""
		使用潜能天书
		"""
		if self.getLevel() > target.getLevel():
			return csstatus.KIT_EQUIP_CANT_POTENTIAL_BOOK
		pot = self.getPotential()
		if target.potential + pot > csconst.ROLE_POTENTIAL_UPPER:
			return csstatus.KIT_EQUIP_POTENTIAL_BOOK_LIM
		target.addPotential( pot )
		owner.removeItem_( self.getOrder(), reason = csdefine.DELETE_ITEM_POTENTIAL_BOOK )
		target.statusMessage( csstatus.KIT_EQUIP_POTENTIAL_BOOK_USED, pot )
		return csstatus.SKILL_GO_ON
		
	def addPotential( self, value, owner ):
		"""
		增加书本潜能点
		"""
		if self.isPotentialMax():
			return
		pot = self.getPotential()
		potMax = self.getPotentialMax()
		rate = self.getPotentialRate()
		value *= rate
		if ( pot + value ) > potMax:
			value = potMax - pot
		pot += value
		self.setPotential( pot, owner )
		
	def setPotential( self, value, owner ):
		"""
		设置书本潜能点
		"""
		self.set( "param2", value, owner )
		
	def getFDict( self ):
		"""
		Virtual Method
		获取法宝效果类型自定义数据格式
		用于发送到客户端
		return INT32
		"""
		return 0
		
	def wield( self, owner, update = True ):
		"""
		装备道具

		@param  owner: 背包拥有者
		@type   owner: Entity
		@param update: 是否立即生效
		@type  update: bool
		@return:    True 装备成功，False 装备失败
		@return:    BOOL
		"""
		if not CEquip.wield( self, owner, update ):
			return False

	def unWield( self, owner, update = True ):
		"""
		卸下装备

		@param  owner: 背包拥有者
		@type   owner: Entity
		@param update: 是否立即生效
		@type  update: bool
		@return:    无
		"""
		CEquip.unWield( self, owner, update )