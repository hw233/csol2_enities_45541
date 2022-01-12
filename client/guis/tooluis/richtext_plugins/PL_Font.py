#
# -*- coding: gb18030 -*-
# $Id: PL_Font.py,v 1.2 2008-05-19 04:52:17 huangyongwei Exp $
#

"""
implement common line text class

2008.05.10: writen by huangyongwei
"""

from bwdebug import *
from guis.controls.RichText import BasePlugin
from share import defParser

class PL_Font( BasePlugin ) :
	"""
	�������Բ���������ʽΪ��
	@F{ n = ��������; fc = ǰ��ɫ; bc = ����ɫ; fa = ǰ��ɫ alpha ֵ; ba = ����ɫ alpha ֵ;
	    fs = �����С; cs = �ּ��; bl = 1 �� 0����ʾ�����Ƿ�Ϊ���壩; il = 1 �� 0����ʾ�����Ƿ�Ϊб�壩; ul = 1 �� 0����ʾ�Ƿ����»��ߣ�; so = 0 �� 1���Ƿ���ɾ���ߣ�}
	����ÿ�����Զ��ǿ�ѡ�ġ����� @F{ n = �������� } �� @F{ fc = ǰ��ɫ } ���ǺϷ��ģ����Ƿֱ��ʾֻ���������ֻ����ǰ��ɫ
	ע��һ����ʽ���󣬸��ڸø�ʽ������������ı���׷��ø�ʽ�����֣�Ҫ�ָ�ԭ���ı��֣�Ҫ���¸�ʽ������
	"""
	esc_ = "@F"

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
		if formatText == "" : return None, leaveText							# ��ʽ��ʧ��
		strAttrs = defParser.getAttrInfos( formatText )
		attrInfos = {}
		tmpOuter = pyRichText.tmpOuter__
		attrInfos["font"] = strAttrs.get( 'n', tmpOuter.font )
		fcolor = strAttrs.get( 'fc', "" )
		bcolor = strAttrs.get( 'bc', "" )
		falpha = strAttrs.get( 'fa', "" )
		balpha = strAttrs.get( 'ba', "" )
		attrInfos["fcolor"] = defParser.tranColor( fcolor, tmpOuter.fcolor )
		attrInfos["bcolor"] = defParser.tranColor( fcolor, tmpOuter.bcolor )
		attrInfos["falpha"] = defParser.tranInt( falpha, tmpOuter.fcolor[3] )
		attrInfos["balpha"] = defParser.tranInt( balpha, tmpOuter.bcolor[3] )

		size = strAttrs.get( "fs", None )
		chSpace = strAttrs.get( "cs", None )
		bold = strAttrs.get( "bl", None )
		italic = strAttrs.get( "il", None )
		underline = strAttrs.get( "ul", None )
		strikeOut = strAttrs.get( "so", None )
		if size : attrInfos["fs"] = defParser.tranInt( size, tmpOuter.fontSize )
		if chSpace : attrInfos["cs"] = defParser.tranFloat( chSpace, tmpOuter.charSpace )
		if bold : attrInfos["bl"] = defParser.tranInt( bold, tmpOuter.bold )
		if italic : attrInfos["il"] = defParser.tranInt( italic, tmpOuter.italic )
		if underline : attrInfos["ul"] = defParser.tranInt( underline, tmpOuter.underline )
		if strikeOut : attrInfos["so"] = defParser.tranInt( strikeOut, tmpOuter.strikeOut )

		return attrInfos, leaveText

	def transform( self, pyRichText, attrInfos ) :
		"""
		ͨ����ʽ����Ϣ������ RichText �ṩ�� API���� RichText ��ճ���Զ���Ԫ��
		"""
		fr, fg, fb = attrInfos['fcolor'][:3]
		br, bg, bb = attrInfos['bcolor'][:3]
		fa = attrInfos["falpha"]
		ba = attrInfos["balpha"]
		tmpOuter = pyRichText.tmpOuter__
		tmpOuter.font = attrInfos["font"]
		tmpOuter.fcolor = fr, fg, fb, fa
		tmpOuter.bcolor = br, bg, bb, ba

		size = attrInfos.get( "fs", None )
		chSpace = attrInfos.get( "cs", None )
		bold = attrInfos.get( "bl", None )
		italic = attrInfos.get( "il", None )
		underline = attrInfos.get( "ul", None )
		strikeOut = attrInfos.get( "so", None )
		tmpOuter.font = attrInfos['font']
		if size is not None : tmpOuter.fontSize = size
		if chSpace is not None : tmpOuter.charSpace = chSpace
		if bold is not None : tmpOuter.bold = bold
		if italic is not None : tmpOuter.italic = italic
		if underline is not None : tmpOuter.underline = underline
		if strikeOut is not None : tmpOuter.strikeOut = strikeOut

	# ----------------------------------------------------------------
	@classmethod
	def getSource( SELF, text = "", **attrInfos ) :
		"""
		ͨ���ṩ��������Ϣ����ȡ��ʽ���ı�
		@type			text	  : str
		@param			text	  : Ҫ��ʽ�����ı��������ֵ��Ϊ�գ����ڸ�ʽ������ַ������Զ����������ɫ�ָ�Ϊ RichText Ĭ�ϵ���ɫ��
									�����ʽ����һֱ���쵽��һ�� @F Ϊֹ
		@type			attrInfos : dict
		@param			attrInfos : �����ʽ������:
									{ n = ��������( ���Բ��� .font ��չ��); fc = ǰ��ɫ; bc = ����ɫ; fa = ǰ��ɫ alpha ֵ; ba = ����ɫ alpha ֵ;
									  fs = �����С; cs = �ּ��; bl = 1 �� 0���Ƿ�Ϊ���壩; il = 1 �� 0���Ƿ�Ϊб�壩; ul = 1 �� 0���Ƿ����»��ߣ�; so = 1 �� 0���Ƿ���ɾ���ߣ�}
		@rtype					  : str
		@return					  : RichText ��ʶ��ĸ�ʽ���ı�
		"""
		struct = "%s{%s}" % ( SELF.esc_, "%s" )
		strAttrs = []
		for key, value in attrInfos.iteritems() :
			if isDebuged :
				assert key in ( "n", "fc", "bc", "fa", "ba", \
					"fs", "bl", "il", "ul", "so" ), \
					"%s is not the keyword of the PL_Font plugin for RichText!" % key
			strAttrs.append( "%s=%s" % ( key, str( value ) ) )
		if len( strAttrs ) == 0 : return text
		return struct % ( ";".join( strAttrs ) ) + text + "@D"
