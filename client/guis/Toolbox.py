# -*- coding: gb18030 -*-
#
#$Id: Toolbox.py,v 1.3 2008-08-19 09:27:21 huangyongwei Exp $
#

"""
implement global tool ui

2008/05/07: writen by huangyongwei
"""

from AbstractTemplates import Singleton

class Toolbox( Singleton ) :
	"""
	ȫ�ֹ�����
	"""
	def __init__( self ) :
		self.__itemCover = None							# ������ʾ��Ʒ��
		self.__infoTip = None							# ������ʾ
		self.__itemParticle = None						# ��ĳ����Ʒ��ͼ������һ����ͼ


	# ----------------------------------------------------------------
	# tools
	# ----------------------------------------------------------------
	@property
	def itemCover( self ) :
		"""
		������ʾ��Ʒ��ĸ�Ĥ
		"""
		if self.__itemCover is None :
			ItemCover = __import__( "guis/tooluis/itemcover/ItemCover" )
			self.__itemCover = ItemCover.ItemCoverArray()
		return self.__itemCover

	@property
	def itemParticle( self ):
		"""
		��ĳһ��ͼ������һ����ͼ
		"""
		if self.__itemParticle is None :
			ItemParticle = __import__( "guis/tooluis/itemcover/ItemParticle" )
			self.__itemParticle = ItemParticle.ItemParticleArray()
		return self.__itemParticle

	@property
	def infoTip( self ) :
		"""
		������ʾ
		"""
		if self.__infoTip is None :
			InfoTip = __import__( "guis/tooluis/infotip/InfoTip" )
			self.__infoTip = InfoTip.InfoTip()
		return self.__infoTip


# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
toolbox = Toolbox()