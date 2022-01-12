# -*- coding: gb18030 -*-
#
# $Id: Buff_199005.py,v 1.1 2008-02-19 03:18:25 kebiao Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_299005( Buff_Normal ):
	"""
	example:反省
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )

#
# $Log: not supported by cvs2svn $
#