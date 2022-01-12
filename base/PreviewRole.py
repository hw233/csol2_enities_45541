# -*- coding: gb18030 -*-

# $Id: PreviewRole.py,v 1.3 2008-05-31 01:42:45 phw Exp $


"""
candidate role, model only exists in client
-- 2007/09/25: wirten by huangyongwei
"""

from BigWorld import Base
from interface.GameObject import GameObject

class PreviewRole( Base, GameObject ) :
	def __init__( self ) :
		Base.__init__( self )
		GameObject.__init__( self )
