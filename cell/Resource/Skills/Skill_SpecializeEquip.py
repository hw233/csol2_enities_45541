# -*- coding: gb18030 -*-
#
# $Id: Skill_SpecializeEquip.py,v 1.4 2007-08-15 03:28:35 kebiao Exp $

"""
"""

from SpellBase import *
from Skill_Normal import Skill_Normal
import ItemTypeEnum

class Skill_SpecializeEquip( Skill_Normal ):
	"""
	精通装备（矛、盾等）
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Skill_Normal.__init__( self )
		self._itemType = 0		# 装备类型
	
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Skill_Normal.init( self, dict )
		self._itemType = eval( ( dict["NeedEquip"] if len( dict["NeedEquip"] ) > 0 else "" ) .strip(), None, ItemTypeEnum.__dict__ )	
		
	def attach( self, ownerEntity ):
		"""
		virtual method = 0;
		为目标附上一个效果，通常被附上的效果是实例自身，它可以通过detach()去掉这个效果。具体效果由各派生类自行决定。
		
		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		item = ownerEntity.findEquipsByType( self._itemType )
		for it in item:
			it.unWield( ownerEntity )
		
		key = "specialize" + str( self._itemType )
		ownerEntity.setTemp( key, self._id )
		
		for it in item:
			it.wield( ownerEntity )

	def detach( self, ownerEntity ):
		"""
		virtual method = 0;
		执行与attach()的反向操作

		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		item = ownerEntity.findEquipsByType( self._itemType )
		for it in item:
			it.unWield( ownerEntity, update = False )
		
		key = "specialize" + str( self._itemType )
		ownerEntity.setTemp( key, 0 )
		
		for it in item:
			it.wield( ownerEntity, update = False )

		ownerEntity.calcDynamicProperties()
		
	def do( self, owner ):
		"""
		精通系列的统一接口
		
		@return: BOOL
		"""
		return True
		
	def undo( self, owner ):
		"""
		精通系列的统一接口
		"""
		pass
			
#
# $Log: not supported by cvs2svn $
# 
#