# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_108002 import Buff_108002


"""
���Ի�˯
"""

class Buff_8002( Buff_108002 ):
	"""
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_108002.__init__( self )

		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_108002.init( self, dict )