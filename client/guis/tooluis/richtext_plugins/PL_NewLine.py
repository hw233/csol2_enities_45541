#
# -*- coding: gb18030 -*-
# $Id: PL_NewLine.py,v 1.3 2008-05-20 08:32:24 huangyongwei Exp $
#

"""
implement common line text class

2008.05.10: writen by huangyongwei
"""

from guis.controls.RichText import BasePlugin
from share import defParser

class PL_NewLine( BasePlugin ) :
	"""
	������в������ʽΪ��@B ���� @B{�����������}
	����Ϊ @B ��Ĭ�ϲ���һ������
	"""
	esc_ = "@B"

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
		if formatText == "" :											# û��ָ����ӵĿ���������Ĭ��һ��
			return 1, leaveText
		count = defParser.tranInt( formatText, 1 )
		count = max( 1, count )
		return count, leaveText

	def transform( self, pyRichText, count ) :
		"""
		ͨ����ʽ����Ϣ������ RichText �ṩ�� API���� RichText ��ճ���Զ���Ԫ��
		"""
		pyRichText.newLine__( count )

	# ----------------------------------------------------------------
	@classmethod
	def getSource( SELF, n = 1 ) :
		"""
		��ȡ���еĸ�ʽ���ı�
		@type					n : int
		@param					n : ������
		@rtype					  : str
		@return					  : RichText ��ʶ��ĸ�ʽ���ı�
		"""
		assert n > 0, "n moust great than 0."
		if n == 1 : return SELF.esc_
		return "%s{%d}" % ( SELF.esc_, n )

# --------------------------------------------------------------------
# Ϊ��ʡʱ���������Ϊȫ�ֱ���
# --------------------------------------------------------------------
g_newLine = PL_NewLine.getSource( )