#
# -*- coding: gb18030 -*-
# $Id: PL_Space.py,v 1.3 2008-05-20 08:32:24 huangyongwei Exp $
#

"""
implement common line text class

2008.05.10: writen by huangyongwei
"""

from guis.controls.RichText import BasePlugin
from share import defParser
import reimpl_PL_Space

class PL_Space( BasePlugin ) :
	"""
	����ո�������ʽΪ��@S ���� @S{�����������}
	����Ϊ @S ��Ĭ�ϲ���һ���ո�
	"""
	esc_ = "@S"

	def __init__( self, owner ) :
		BasePlugin.__init__( self, owner )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def format( self, pyRichText, text ) :
		"""
		��ȡ������ĸ�ʽ���ı�
		"""
		formatText, leaveText = defParser.getFormatScope( text )
		if formatText == "" :											# û��ָ����ӵĿո�������Ĭ��һ��
			return None, " " + leaveText
		count = defParser.tranInt( formatText, 1 )
		count = max( 1, count )
		return None, " " * count + leaveText

	def transform( self, pyRichText, attrInfo ) :
		"""
		ͨ����ʽ����Ϣ������ RichText �ṩ�� API���� RichText ��ճ���Զ���Ԫ��
		"""
		pass

	# ----------------------------------------------------------------
	@classmethod
	@reimpl_PL_Space.deco_PL_Space_getSource
	def getSource( SELF, n ) :
		"""
		��ȡ����ո��ʽ���ı�
		@type					n : int
		@param					n : �ո���
		@rtype					  : str
		@return					  : RichText ��ʶ��ĸ�ʽ���ı�
		"""
		assert n > 0, "n moust great than 0."
		if n == 1 : return SELF.esc_
		return "%s{%d}" % ( SELF.esc_, n )
