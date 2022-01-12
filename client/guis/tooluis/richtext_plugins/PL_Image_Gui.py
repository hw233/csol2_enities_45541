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
from guis.controls.RichText import BasePlugin
from share import defParser
from guis.controls.Icon import Icon

class PL_Image_Gui( BasePlugin ) :
	"""
	�ò������������ĳ��GUI�����Ҹ�GUI����һͼ���Ƕ�̬�ɱ�ģ������ظ�ƴ�Ӷ��GUI
	����ͼ���ʽ���������ʽΪ: @II{ p = ͼ������·��;mp =ͼ���·��; m = �����ӱ��; s = ͼ���С( w, h ) }
	pΪgui������·������gui������һ����gui���ֽ�"Image" mpΪ�ɱ��ͼ���·��
	ע��p ��ֵ��ָͼ������·����������ͼ��;��������������չ��Ӧ���ǣ�*.gui
	"""
	esc_ = "@M"

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
		if formatText == "" : None, leaveText								# ��ʽ��ʧ��
		strAttrs = defParser.getAttrInfos( formatText )
		attrs = {}
		path = strAttrs.get( "p", "" )
		ext = os.path.splitext( path )[1]
		if ext == ".gui" :													# ��չ��Ϊ gui
			try :
				image = GUI.load( path )
			except ValueError :
				image = GUI.load( "guis/controls/richtext/deficon.gui" )
		else :																# ���������ļ�
			image = GUI.load( "guis/controls/richtext/deficon.gui" )
			if ext != "" : image.textureName = path							# ��չ��Ϊ��ͼ
		attrs["image"] = image
		attrs["mpath"] = strAttrs.get( "mp", "" )
		strSize = strAttrs.get( "s", "" )
		color = defParser.tranColor( strAttrs.get( "c", "" ), None )
		if color : image.colour = color
		return attrs, leaveText

	def transform( self, pyRichText, imageInfo ) :
		"""
		ͨ����ʽ����Ϣ������ RichText �ṩ�� API���� RichText ��ճ���Զ���Ԫ��
		"""
		image = imageInfo['image']
		mpath = imageInfo['mpath']
		image.image.textureName = mpath										# ����ͼ��
		pyIcon = Icon( image )
		if not pyRichText.autoNewline :										# ������Զ�����
			pyRichText.addElement__( pyIcon )								# ��ͼ��ŵ���ǰ����
			return

		space = pyRichText.getCurrLineSpace__()								# ��ǰ��ʣ����
		if pyIcon.width <= space :											# �����ǰʣ���ȣ����Է���һ��ͼ��
			pyRichText.addElement__( pyIcon )								# ��ͼ��ŵ���ǰ����
		elif pyIcon.width > space and not pyRichText.isNewLine__() :		# �����ǰ��ʣ���Ȳ����Է���һ��ͼ��
			pyRichText.paintCurrLine__()									# ճ����ǰ��
			self.transform( pyRichText, imageInfo )							# ����ͼ��ŵ���һ���д���
		elif pyIcon.width > space :										# ��� RichText ������ȶ������������ͼ��
			pyRichText.addElement__( pyIcon )								# ��ͼ��ŵ���ǰ����
			pyRichText.paintCurrLine__()									# ճ����ǰ��

	# ----------------------------------------------------------------
	@classmethod
	def getSource( SELF, path, mpath = "" ) :
		"""
		ͨ���ṩ��������Ϣ����ȡ����ͼ���ʽ���ı�
		@type				path  : str
		@param				path  : ͼ������·��
		@type				size  : tuple
		@param				size  : ͼ���С( ���� )
		@return					  : RichText ��ʶ��ĸ�ʽ���ı�
		"""
		struct = "%s{%s}" % ( SELF.esc_, "%s" )
		strAttrs = []
		strAttrs.append( "p=%s" % path )
		if mpath != "" : strAttrs.append( "mp=%s" % mpath)
		return struct % ( ";".join( strAttrs ) )
