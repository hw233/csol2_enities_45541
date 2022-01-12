# -*- coding: gb18030 -*-

"""
2010.10.18: writen by pengju
"""

from AbstractTemplates import MultiLngFuncDecorator

class deco_PL_Space_getSource( MultiLngFuncDecorator ) :
	@staticmethod
	def locale_big5( SELF, n ) :
		"""
		获取插入空格格式化文本
		@type					n : int
		@param					n : 空格数
		@rtype					  : str
		@return					  : RichText 可识别的格式化文本
		"""
		assert n > 0, "n moust great than 0."
		if n == 1 :
			return "%s{%d}" % ( SELF.esc_, 2 )
		return "%s{%d}" % ( SELF.esc_, 2*n )
