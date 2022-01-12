#
# -*- coding: gb18030 -*-
# $Id: PL_Link.py,v 1.3 2008-08-19 09:33:02 huangyongwei Exp $
#

"""
implement common line text class

2008.05.10: writen by huangyongwei
"""

import csstring
from guis import *
from guis.controls.RichText import BasePlugin
from share import defParser
from LinkLabel import LinkLabel
from csstring import g_interpunctions

class PL_Link( BasePlugin ) :
	"""
	���볬���Ӳ������ʽΪ��@L{ t = '�������ı�'; m = �����ӱ��;
		cfc = ��ͨ״̬��ǰ��ɫ; cbc = ��ͨ״̬�±���ɫ; hfc = ������״̬��ǰ��ɫ; hbc = ������״̬�±���ɫ; ul = 0 �� 1 ��ʾ�Ƿ����»���; }
	���� t �� m ѡ���Ǳ�ѡ�ģ�������ѡ
	"""
	esc_ = "@L"

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
		if formatText == "" : return None, leaveText								# ��ʽ��ʧ��
		attrs = {}
		tmpOuter = pyRichText.tmpOuter__
		strAttrs = defParser.getAttrInfos( formatText )
		attrs["text"] = strAttrs.get( "t", "" )
		attrs["mark"] = strAttrs.get( "m", "" )
		if attrs["text"] == "" : attrs["text"] = "<error link label: no link text>"
		elif attrs["mark"] == "" : attrs["text"] += "<error link label: no link mark>"

		cfc = strAttrs.get( "cfc", "" )
		cbc = strAttrs.get( "cbc", "" )
		hfc = strAttrs.get( "hfc", cfc )											# ���û�����ø�����ǰ��ɫ����ʹ������״̬�µ�ǰ��ɫ
		hbc = strAttrs.get( "hbc", cbc )											# ���û�����ø����ı���ɫ����ʹ������״̬�µı���ɫ
		attrs["cfc"] = defParser.tranColor( cfc, tmpOuter.fcolor )
		attrs["cbc"] = defParser.tranColor( cbc, tmpOuter.bcolor )
		attrs["hfc"] = defParser.tranColor( hfc, tmpOuter.fcolor )
		attrs["hbc"] = defParser.tranColor( hbc, tmpOuter.bcolor )

		attrs["ul"] = strAttrs.get( "ul", "0" )										# �»���

		return attrs, leaveText

	def transform( self, pyRichText, linkInfo, pyForeLabel = None ) :
		"""
		ͨ����ʽ����Ϣ������ RichText �ṩ�� API���� RichText ��ճ���Զ���Ԫ��
		"""
		pyLabel = LinkLabel( linkInfo['mark'] )							# ����һ�����ӱ�ǩ
		pyLabel.pyForeLabel = pyForeLabel								# ��������ǰ�ñ�ǩ
		if pyForeLabel : pyForeLabel.pyNextLabel = pyLabel				# ���������ñ�ǩ��ǰ�ñ�ǩ
		pyLabel.commonForeColor = cfcolor = linkInfo["cfc"]				# ���ӱ�ǩ��ͨ״̬�µ�ǰ��ɫ
		pyLabel.commonBackColor = linkInfo["cbc"]						# ���ӱ�ǩ��ͨ״̬�µı���ɫ
		pyLabel.highlightForeColor = linkInfo["hfc"]					# ���ӱ�ǩ����״̬�µ�ǰ��ɫ
		pyLabel.highlightBackColor = linkInfo["hbc"]					# ���ӱ�ǩ����״̬�µı���ɫ

		tmpOuter = pyRichText.tmpOuter__
		pyLabel.charSpace = tmpOuter.charSpace							# �ּ��
		pyLabel.setFontInfo( {
			"font" : tmpOuter.font,										# ����
			"size" : tmpOuter.fontSize,									# �����С
			"bold" : tmpOuter.bold,										# �Ƿ�ʹ�ô���
			"italic" : tmpOuter.italic,									# �Ƿ�ʹ��б��
			"underline" : linkInfo["ul"] != "0",						# �Ƿ����»���
			} )

		text = linkInfo["text"]											# �����ı�
		ltext, rtext = text, ""											# Ĭ�ϲ����Զ�����
		if pyRichText.autoNewline :										# ����Զ�����
			space = pyRichText.getCurrLineSpace__()						# ��ȡ��ǰ��ʣ����
			ltext, rtext, lwtext, rwtext = pyLabel.splitText( space, "CUT", text )	# ��ʣ���ȷ�Χ�ڲ���ַ���
			if len( rwtext ) :
				fchr = csstring.toString( rwtext[0] )
				if fchr in g_interpunctions :							# ���۶ϱ�����
					ltext += fchr
					rtext = csstring.toString( rwtext[1:] )
		if rtext == "" :												# ���û���۶��ı�����˵��ʣ���ȿ��Է��������ַ���
			pyLabel.text = ltext
			pyRichText.addElement__( pyLabel )							# �ŵ���ǰ����
		elif ltext == "" and not pyRichText.isNewLine__() :				# ���ʣ��Ŀ�Ȳ����Է���һ������
			pyRichText.paintCurrLine__()								# ճ����ǰ��
			self.transform( pyRichText, linkInfo )						# ת����һ����ճ��
		elif ltext == "" :												# ��������̫С����һ����Ҳ�Ų���
			wtext = csstring.toWideString( text )
			pyLabel.text = csstring.toString( wtext[0] )				# ��ֻ��һ����
			pyRichText.addElement__( pyLabel )							# ��ӵ���ǰ��
			pyRichText.paintCurrLine__()								# ճ����ǰ��
			linkInfo['text'] = csstring.toString( wtext[1:] )			# ��ȡʣ���ı�
			self.transform( pyRichText, linkInfo, pyLabel )				# ת����һ����ճ��ʣ���ı�
		else :															# ����ı����۶ϳ�����
			pyLabel.text = ltext
			pyRichText.addElement__( pyLabel )							# ���۶ϵ�����ı��ŵ���ǰ��
			pyRichText.paintCurrLine__()								# ճ����ǰ��
			linkInfo['text'] = rtext									# ��ȡʣ���ı�
			self.transform( pyRichText, linkInfo, pyLabel )				# ת����һ����ճ��ʣ���ı�

	# ----------------------------------------------------------------
	@classmethod
	def getSource( SELF, text, mark, **dspMode ) :
		"""
		ͨ���ṩ�ĳ�������Ϣ���ȡ��ʽ���ı�
		@type				text	: str
		@param				text	: �������ı�
		@type				mark	: str
		@param				mark	: �����ӱ��
		@type				dspMode : dict
		@param				dspMode : �����ӱ�����ʽ��
									  { cfc = ��ͨǰ��ɫ; cbc = ��ͨ����ɫ; hfc = ����ǰ��ɫ; hbc = ��������ɫ;
										bl = 1 �� 0����ʾ�Ƿ��Ǵ��壩; il = 1 �� 0����ʾ�Ƿ���б�壩; ul = 1 �� 0����ʾ�Ƿ����»��ߣ�}
		@rtype						: str
		@return						: RichText ��ʶ��ĸ�ʽ���ı�
		"""
		struct = "%s{%s}" % ( SELF.esc_, "%s" )
		attrStrs = []
		attrStrs.append( "t=%s" % text )
		attrStrs.append( "m=%s" % mark )
		for key, value in dspMode.iteritems() :
			if isDebuged :
				assert key in ( "cfc", "cbc", "hfc", "hbc", "ul" ), \
					"%s is not the keyword of the link plugin for RichText!" % key
			attrStrs.append( "%s=%s" % ( key, value ) )
		return struct % ( ";".join( attrStrs ) )
