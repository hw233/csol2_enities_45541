# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
NPC基类
"""

import BigWorld
from bwdebug import *
import csdefine
import csstatus
from NPC import NPC

class TongJunShi( NPC ):
	"""
	帮会军师
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		NPC.__init__( self )
		
	def lock( self ):
		"""
		define method.
		NPC被锁住， 帮会成员无法和他交互
		"""
		self.locked = True

	def unlock( self ):
		"""
		define method.
		NPC被开锁， 帮会成员恢复和他交互
		"""
		self.locked = False
	
	def openFete( self ):
		"""
		define method.
		开放祭祀活动
		"""
		self.feteOpen = True
	
	def closeFete( self ):
		"""
		define method.
		关闭祭祀活动
		"""
		self.feteOpen = False
# NPC.py
