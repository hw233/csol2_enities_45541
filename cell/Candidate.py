# -*- coding: gb18030 -*-

import BigWorld

# $Id: Candidate.py,v 1.1 2006-04-21 09:06:17 wanhaipeng Exp $

#
# 登陆是候选的角色，不会生成Cell Entity
#

class Candidate( BigWorld.Entity ):
	def __init__( self ):
		BigWorld.Entity.__init__( self )


#
# $Log: not supported by cvs2svn $
#