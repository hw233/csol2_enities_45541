# -*- coding: gb18030 -*-
#
# $Id: Buff_199003.py,v 1.1 2008-08-05 06:50:12 kebiao Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_199003( Buff_Normal ):
	"""
	example:ս������
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )

#
# $Log: not supported by cvs2svn $
# Revision 1.1  2008/02/19 03:18:25  kebiao
# no message
#
#