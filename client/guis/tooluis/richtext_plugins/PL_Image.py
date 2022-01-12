#
# -*- coding: gb18030 -*-
# $Id: PL_Image.py,v 1.3 2008-08-19 09:33:02 huangyongwei Exp $
#

"""
implement common line text class

2008.05.10: writen by huangyongwei
"""

import os
import GUI
from guis.UIFixer import hfUILoader
from guis.controls.RichText import BasePlugin
from share import defParser
from LinkImage import LinkImage

class PL_Image( BasePlugin ) :
	"""
	����ͼ���ʽ���������ʽΪ��@I{ p = ͼ������·��; t = ͼ��·��; m = �����ӱ��; s = ͼ���С( w, h ) }
	���� p ѡ���Ǳ���ģ���������ѡ���ѡ
	���������� m ѡ�������ֵ��Ϊ���ַ��������ͼ����Բ��������ӹ��ܣ��������ͼ��ʱ��RichText �� onComponentLClick ���¼����ᱻ������
	ע��p ��ֵ��ָͼ������·����������ͼ��;��������������չ��Ӧ���ǣ�*.gui
	"""
	esc_ = "@I"

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
		if formatText == "" : return None, leaveText						# ��ʽ��ʧ��
		strAttrs = defParser.getAttrInfos( formatText )
		attrs = {}
		path = strAttrs.get( "p", "" )
		texture = strAttrs.get( "t", "" )
		text = strAttrs.get( "text", "" )
		if path.endswith( ".gui" ) :
			try :
				image = GUI.load( path )
			except :
				image = hfUILoader.load( "guis/controls/richtext/deficon.gui" )
		else :
			image = hfUILoader.load( "guis/controls/richtext/deficon.gui" )
		if texture != "" :													# ʹ��ָ����ͼ
			image.textureName = texture
		attrs["image"] = image
		attrs["mark"] = strAttrs.get( "m", "" )
		strSize = strAttrs.get( "s", "" )
		attrs["size"] = defParser.tranTuple( strSize, 2 * [int], image.size )
		attrs["text"] = text
		color = defParser.tranColor( strAttrs.get( "c", "" ), None )
		if color : image.colour = color
		return attrs, leaveText

	def transform( self, pyRichText, imageInfo ) :
		"""
		ͨ����ʽ����Ϣ������ RichText �ṩ�� API���� RichText ��ճ���Զ���Ԫ��
		"""
		image = imageInfo['image']
		mark = imageInfo['mark']
		pyImage = LinkImage( image, mark )
		pyImage.text = imageInfo['text']
		pyImage.size = imageInfo['size']									# ���ô�С
		if not pyRichText.autoNewline :										# ������Զ�����
			pyRichText.addElement__( pyImage )								# ��ͼ��ŵ���ǰ����
			return

		space = pyRichText.getCurrLineSpace__()								# ��ǰ��ʣ����
		if pyImage.width <= space :											# �����ǰʣ���ȣ����Է���һ��ͼ��
			pyRichText.addElement__( pyImage )								# ��ͼ��ŵ���ǰ����
		elif pyImage.width > space and not pyRichText.isNewLine__() :		# �����ǰ��ʣ���Ȳ����Է���һ��ͼ��
			pyRichText.paintCurrLine__()									# ճ����ǰ��
			self.transform( pyRichText, imageInfo )							# ����ͼ��ŵ���һ���д���
		elif pyImage.width > space :										# ��� RichText ������ȶ������������ͼ��
			pyRichText.addElement__( pyImage )								# ��ͼ��ŵ���ǰ����
			pyRichText.paintCurrLine__()									# ճ����ǰ��

	# ----------------------------------------------------------------
	@classmethod
	def getSource( SELF, path = "", texture = "", lmark = "", size = None, color = None, text = "" ) :
		"""
		ͨ���ṩ��������Ϣ����ȡ����ͼ���ʽ���ı�
		@type				path  : str
		@param				path  : ͼ������·��
		@type				lmark : str
		@param				lmark : �����ӱ��
		@type				size  : tuple
		@param				size  : ͼ���С( ���� )
		@type				text  : str
		@param				text  : ��ͼƬ���ı���ʾ(��ʹ�����Լ�����)��
									����ΪRichText��viewText���֣��Է��������¼�ı���
		@return					  : RichText ��ʶ��ĸ�ʽ���ı�
		"""
		struct = "%s{%s}" % ( SELF.esc_, "%s" )
		strAttrs = []
		assert path != "" or texture != "", \
			"at least one of argument 'path' and 'texture' must't be empty string!"
		if path != "" : strAttrs.append( "p=%s" % path )
		if texture != "" : strAttrs.append( "t=%s" % texture )
		if lmark != "" : strAttrs.append( "m=%s" % lmark )
		if text != "" : strAttrs.append( "text=%s" % text )
		if size is not None : strAttrs.append( "s=%f,%f" % size )
		if color :
			if type( color ) is tuple and len( color ) == 3 :
				color += ( 255, )
			strAttrs.append( "c=%s" % str( color ) )
		return struct % ( ";".join( strAttrs ) )
