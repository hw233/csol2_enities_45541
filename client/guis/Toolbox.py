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
	全局工具箱
	"""
	def __init__( self ) :
		self.__itemCover = None							# 高亮显示物品格
		self.__infoTip = None							# 工具提示
		self.__itemParticle = None						# 给某个物品的图标增加一个贴图


	# ----------------------------------------------------------------
	# tools
	# ----------------------------------------------------------------
	@property
	def itemCover( self ) :
		"""
		高亮显示物品格的盖膜
		"""
		if self.__itemCover is None :
			ItemCover = __import__( "guis/tooluis/itemcover/ItemCover" )
			self.__itemCover = ItemCover.ItemCoverArray()
		return self.__itemCover

	@property
	def itemParticle( self ):
		"""
		给某一个图标增加一个贴图
		"""
		if self.__itemParticle is None :
			ItemParticle = __import__( "guis/tooluis/itemcover/ItemParticle" )
			self.__itemParticle = ItemParticle.ItemParticleArray()
		return self.__itemParticle

	@property
	def infoTip( self ) :
		"""
		工具提示
		"""
		if self.__infoTip is None :
			InfoTip = __import__( "guis/tooluis/infotip/InfoTip" )
			self.__infoTip = InfoTip.InfoTip()
		return self.__infoTip


# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
toolbox = Toolbox()