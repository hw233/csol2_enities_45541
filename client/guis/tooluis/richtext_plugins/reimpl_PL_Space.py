# -*- coding: gb18030 -*-

"""
2010.10.18: writen by pengju
"""

from AbstractTemplates import MultiLngFuncDecorator

class deco_PL_Space_getSource( MultiLngFuncDecorator ) :
	@staticmethod
	def locale_big5( SELF, n ) :
		"""
		��ȡ����ո��ʽ���ı�
		@type					n : int
		@param					n : �ո���
		@rtype					  : str
		@return					  : RichText ��ʶ��ĸ�ʽ���ı�
		"""
		assert n > 0, "n moust great than 0."
		if n == 1 :
			return "%s{%d}" % ( SELF.esc_, 2 )
		return "%s{%d}" % ( SELF.esc_, 2*n )
