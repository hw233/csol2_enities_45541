#
# -*- coding: gb18030 -*-
# $Id: PL_Align.py,v 1.4 2008-08-20 07:39:54 huangyongwei Exp $
#

"""
implement common line text class

2008.05.10: writen by huangyongwei
"""

from bwdebug import *
from guis.controls.RichText import BasePlugin
from share import defParser

class PL_Align( BasePlugin ) :
	"""
	�����ı����뷽ʽ�Ĳ���������ʽΪ: @A{�ı�ˮƽ���뷽ʽ}
	�����ı����뷽ʽ�У���L��( ��ʾ����� )����C��( ��ʾ���� )����R�� ( ��ʾ�Ҷ��� )
	"""
	esc_ = "@A"

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
		if formatText == "" : return None, text							# ��ʽ��ʧ��
		tmpAligns = formatText.strip().split( ';' )						# ���ͣ����ʽ
		aligns = []
		for align in tmpAligns :
			align = align.strip()
			if len( align ) != 1 : continue
			if align in "LCRTMB" :
				aligns.append( align )
		if len( aligns ) :
			return aligns, leaveText
		return None, leaveText											# ����ȥ����ʽ���ı���ת���ַ��ʹ������������ı�������ı�

	def transform( self, pyRichText, attrInfo ) :
		"""
		ͨ����ʽ����Ϣ������ RichText �ṩ�� API���� RichText ��ճ���Զ���Ԫ��
		"""
		for align in attrInfo :
			if align in "LCR" :
				pyRichText.setTmpAlign__( align )					# �����ı�ˮƽ���뷽ʽ
			elif align in "TMB" :
				pyRichText.setTmpLineFlat__( align )				# �����ı��ߵͶ��뷽ʽ

	# ----------------------------------------------------------------
	@classmethod
	def getStartAlign( SELF, text ) :
		"""
		��ȡĳ���ı�������ʼ���뷽ʽ
		"""
		if not text.startswith( SELF.esc_ ) : return ( None, None )
		text = text[len( SELF.esc_ ):]
		formatText, leaveText = defParser.getFormatScope( text )
		if formatText == "" : return ( "L", "T" )					# Ĭ��Ϊ�����Ͻ�
		aligns = [None, None]
		tmpAligns = formatText.strip().split( ';' )					# ���ͣ����ʽ
		for align in tmpAligns :
			align = align.strip()
			if len( align ) != 1 : continue
			if align in "LCR" :
				aligns[0] = align
			elif align in "TMB" :
				aligns[1] = align
		return tuple( aligns )

	@classmethod
	def getSource( SELF, align = None, lineFlat = None ) :
		"""
		ͨ���ṩ��������Ϣ����ȡ��ʽ���ı�
		@type			align	 : chr
		@param			align	 : �ı�ˮƽ���뷽ʽ: ������룺��L�������У���C�������Ҷ��롰R��
		@type			lineFlat : chr
		@param			lineFlat : ǰ�����θ߰���һ���ı��ĸߵͶ��뷽ʽ���������룺��T�����м���룺��M�����ײ����룺��B��
		@rtype					 : str
		@return					 : RichText ��ʶ��ĸ�ʽ���ı�
		"""
		if isDebuged :
			if align : assert len( align ) == 1 and align in "LCR", "align mode must be: 'L', 'C', 'R'"
			if lineFlat : assert len( lineFlat ) == 1 and lineFlat in "TMB", "lineflat mode must be: 'T', 'M', 'B'"
		if align and lineFlat :
			return "%s{%s;%s}" % ( SELF.esc_, align, lineFlat )
		elif align :
			return "%s{%s}" % ( SELF.esc_, align )
		elif lineFlat :
			return "%s{%s}" % ( SELF.esc_, lineFlat )
		return ""
