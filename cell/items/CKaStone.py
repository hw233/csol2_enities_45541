# -*- coding: gb18030 -*-

# $Id: CKaStone.py,v 1.2 2008-02-21 06:10:53 kebiao Exp $

"""
魂魄石基础类
"""
from CEquip import *

class CKaStone( CEquip ):
	"""
	魂魄石基础类
	"""
	def __init__( self, srcData ):
		CEquip.__init__( self, srcData )
	
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
		if not self.isFull():
			owner.kaStone_SpellID = self.query( "spell" )
		return True

	def unWield( self, owner, update = True ):
		"""
		卸下装备

		@param  owner: 背包拥有者
		@type   owner: Entity
		@param update: 是否立即生效
		@type  update: bool
		@return:    无
		"""
		owner.kaStone_SpellID = 0
		CEquip.unWield( self, owner, update )
		
	def _checkHardiness( self ):
		"""
		检查当前耐久度

		@return: 大于0或不存在这个属性则返回True，否则返回False
		@rtype:  BOOL
		"""
		return True
		
	def isFull( self ):
		"""
		魂魄是否吸收满
		"""
		return self.query( "ka_count", 0 ) >= self.query( "ka_totalCount", 1 )
		
	def addKa( self, owner, kaVal ):
		"""
		添加魂魄
		"""
		self.set( "ka_count", self.query( "ka_count", 0 ) + kaVal, owner )
		self.onKaValueChanged( owner )
	
	def onKaValueChanged( self, owner ):
		"""
		魂魄值被改变了
		"""
		if self.isFull():
			owner.kaStone_SpellID = 0
			
#
# $Log: not supported by cvs2svn $
# Revision 1.1  2008/02/20 08:32:19  kebiao
# no message
#
#
