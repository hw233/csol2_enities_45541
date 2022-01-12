# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.9 2008-03-25 01:59:31 zhangyuxing Exp $

"""
NPC的基类
"""
from bwdebug import *
from Monster import Monster
import csdefine

class NPC( Monster ):
	"""
	NPC的基类
	"""
	def __init__( self ):
		"""
		初始化
		"""
		Monster.__init__( self )
		
	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		根据给定的section，初始化（读取）entity属性。
		注：只有在createEntity()时需要把值自动对entity进行初始化时才有必要放到此函数初始化，
		也就是说，这里初始化的所有属性都必须是在相应的.def中声明过的。
		
		@param section: PyDataSection, 根据一定的格式存储了entity属性的section
		"""
		Monster.onLoadEntityProperties_( self, section )
		flags = self.getEntityProperty( "flags" )					#-----------------------------------------------
		flags &= ~( 1 << csdefine.ENTITY_FLAG_MONSTER_INITIATIVE ) 	#将NPC的ENTITY_FLAG_MONSTER_INITIATIVE标记屏蔽掉
		self.setEntityProperty( "flags", flags )					#-----------------------------------------------
		
	def _initDefaultAI( self, selfEntity ):
		"""
		初始化怪物默认的AI
		"""
		pass #NPC暂时没有默认AI
	
	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		初始化自己的entity的数据
		"""
		selfEntity.setLevel( selfEntity.level )
		self._initAI( selfEntity )
		selfEntity.setEntityType( csdefine.ENTITY_TYPE_NPC )

# NPC.py
