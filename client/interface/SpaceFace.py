# -*- coding: gb18030 -*-
#
# $Id: SpaceFace.py,v 1.5 2008-07-24 02:04:03 kebiao Exp $

"""
Player Client for SPACE Face
"""

import BigWorld
from bwdebug import *

class SpaceFace:
	"""
	player client
	"""
	def __init__( self ):
		#self.duplicateSpaceID
		pass

	def spaceMessage( self, state ):
		"""
		״̬
		"""
		INFO_MSG( "===== Space State:", state )
		self.onStatusMessage( state, "" )
	
		
# $Log: not supported by cvs2svn $
# Revision 1.4  2007/05/14 07:03:40  phw
# ɾ�����õ�ģ������
#
# Revision 1.3  2007/05/04 03:18:05  panguankong
# �����spaceface�ӿ�
#
# Revision 1.2  2006/12/04 07:08:45  panguankong
# no message
#
# Revision 1.1  2006/11/03 00:34:23  panguankong
# ��ӿռ������
#
# 
