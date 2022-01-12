# -*- coding: gb18030 -*-
#
# $Id: TongSpecialChapman.py



import BigWorld
from bwdebug import *
import csdefine
import csstatus
from NPC import NPC

class TongSpecialChapman( NPC ):
	"""
	帮会特殊商人 
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		NPC.__init__( self )
		
	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		根据给定的section，初始化（读取）entity属性。
		注：只有在createEntity()时需要把值自动对entity进行初始化时才有必要放到此函数初始化，
		也就是说，这里初始化的所有属性都必须是在相应的.def中声明过的。
		
		@param section: PyDataSection, 根据一定的格式存储了entity属性的section
		"""
		NPC.onLoadEntityProperties_( self, section )

# NPC.py
