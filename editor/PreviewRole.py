# -*- coding: utf_8 -*-

# $Id: PreviewRole.py,v 1.3 2008-04-30 04:13:06 phw Exp $


"""
-- 2007/08/31: written by hyw
"""

class PreviewRole :
	def modelName( self, props ) :
		if len( props["modelName"] ):
			return props["modelName"]
		return "avatar/nanjianke/model/all_1000.model"