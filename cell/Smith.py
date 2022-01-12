# -*- coding: gb18030 -*-
#
# $Id: Smith.py,v 1.3 2007-10-29 04:09:43 yangkai Exp $

"""
Smith
"""

from bwdebug import *
import NPC
import BigWorld

class Smith( NPC.NPC ):
	"""
	Smith
	"""
	def __init__( self ):
		"""
		初始化状态。要在Fight初始化之前
		"""
		NPC.NPC.__init__( self )

#
# $Log: not supported by cvs2svn $
# Revision 1.2  2007/06/14 00:38:49  kebiao
# 材料合成
#
# Revision 1.1  2007/05/05 08:23:33  panguankong
# 添加文件
#
#