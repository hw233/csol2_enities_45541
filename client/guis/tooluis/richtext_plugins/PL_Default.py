#
# -*- coding: gb18030 -*-
# $Id: PL_Default.py,v 1.2 2008-05-19 04:52:17 huangyongwei Exp $
#

"""
implement common line text class

2008.05.10: writen by huangyongwei
"""


from guis.controls.RichText import TmpOuter, BasePlugin
from share import defParser

class PL_Default( BasePlugin ) :
	"""
	���ý��ŵ��ı����塢ǰ��ɫ��ɫ������ɫΪĬ��ֵ
	"""
	esc_ = "@D"

	def __init__( self, owner ) :
		BasePlugin.__init__( self, owner )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def format( self, pyRichText, text ) :
		"""
		��ȡ������ĸ�ʽ���ı�
		"""
		return self.esc, text

	def transform( self, pyRichText, attrInfo ) :
		"""
		ͨ����ʽ����Ϣ������ RichText �ṩ�� API���� RichText ��ճ���Զ���Ԫ��
		"""
		pyRichText.tmpOuter__ = TmpOuter( pyRichText )

	# ----------------------------------------------------------------
	@classmethod
	def getSource( SELF ) :
		"""
		ͨ���ṩ��������Ϣ����ȡ��ʽ���ı�
		@return				  : RichText ��ʶ��ĸ�ʽ���ı�
		"""
		return SELF.esc_
