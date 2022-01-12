# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_108002 import Buff_108002


"""
良性昏睡
"""

class Buff_8002( Buff_108002 ):
	"""
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_108002.__init__( self )

		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_108002.init( self, dict )