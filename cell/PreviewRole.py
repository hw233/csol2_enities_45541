# -*- coding: gb18030 -*-

# $Id: PreviewRole.py,v 1.1 2007-10-07 09:57:04 huangyongwei Exp $


"""
candidate role, model only exists in client
-- 2007/09/25: wirten by huangyongwei
"""

from interface.GameObject import GameObject

class PreviewRole( GameObject ) :
	def __init__( self ) :
		GameObject.__init__( self )
