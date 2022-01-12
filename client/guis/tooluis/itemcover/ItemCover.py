# -*- coding: gb18030 -*-
#
# $Id: ItemCover.py,v 1.4 2008-09-03 09:15:50 huangyongwei Exp $

"""
implement item cover class
"""
import BigWorld
from guis import *
from guis.controls.Control import Control
import ResMgr


# --------------------------------------------------------------------
# implement item cover class
# --------------------------------------------------------------------
class ItemCover( Control ) :
	__cc_textures = {}
	__cc_textures[(32, 32)] = BigWorld.PyTextureProvider( "guis/tooluis/itemcover/cover_32.dds" )					# 32 宽的 cover
	__cc_textures[(48, 48)] = BigWorld.PyTextureProvider( "guis/tooluis/itemcover/cover_48.dds" )					# 48 宽的 cover
	__cc_dummySection = ResMgr.openSection( "guis/tooluis/itemcover/itemcover.gui" )

	def __init__( self ) :
		cover = GUI.load( ItemCover.__cc_dummySection)
		Control.__init__( self, cover )
		self.resetMode( ( 48, 48 ) )
		self.visible = False

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_ItemCover :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def resetMode( self, size ) :
		"""
		根据 binder 设置 item 的规格
		"""
		mode = int( round( size[0] ) ), int( round( size[1] ) )
		if mode not in self.__cc_textures :
			self.texture = self.__cc_textures[(48, 48)]		# 有些技能并不在这两个尺寸内，像宠物交易界面的技能
			self.size = 48, 48								# 所以默认用48格式的贴图，再进行压缩显示
			util.setGuiState( self.getGui() )
			self.size = mode
			INFO_MSG( "itemcover '%s' is not exist!" % str( mode ) )
		else :
			self.texture = self.__cc_textures[mode]
			self.size = mode
			util.setGuiState( self.getGui() )


# --------------------------------------------------------------------
# implement item cover array
# --------------------------------------------------------------------
class ItemCoverArray :
	__c_cbid_vs_detect = 0
	__inst = None
	__cc_spellingTextures = {}
	__cc_spellingTextures[(32, 32)] = BigWorld.PyTextureProvider( "guis/tooluis/itemcover/spellingitem_32.dds" )
	__cc_spellingTextures[(48, 48)] = BigWorld.PyTextureProvider( "guis/tooluis/itemcover/spellingitem_48.dds" )
	__cc_invalidTextures = {}
	__cc_invalidTextures[(32, 32)] = BigWorld.PyTextureProvider( "guis/tooluis/itemcover/invaliditem_32.dds" )
	__cc_invalidTextures[(48, 48)] = BigWorld.PyTextureProvider( "guis/tooluis/itemcover/invaliditem_48.dds" )
	__instanceCount=10

	def __init__( self ) :
		assert self.__inst is None
		self.__inst = self
		self.__pyCover =ItemCover()
		self.instanceList=[]
		self.isi=False
		self.__pyCovers = {}
		self.instancePool()
		
	def instancePool(self):
		"""
		create a pool of ItemCover instances
		"""
		for i in xrange(ItemCoverArray.__instanceCount):
			self.instanceList.append(ItemCover())
			
	def getOneInstanceFromPool(self):
		"""
		if the instances pool has itemcover instance , get one from it ,
		else create an instance of itemcover
		"""
		if len(self.instanceList)!=0:
			return self.instanceList.pop()
		else:
			return ItemCover()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def highlightItem( self, pyItem ) :
		"""
		高亮显示一个物品格（一般用于鼠标进入某个物品格时，高亮显示该物品格）
		@type				pyItem : python ui
		@param				pyItem : 被覆盖的 UI
		@return					   : None
		"""
		parent = pyItem.getGui().parent
		if parent is None : return
		if pyItem.rvisible == False : # 如果物品格隐藏，则取消高亮
			self.normalizeItem()
			return
		self.__pyCover.resetMode( pyItem.size )
		parent.addChild( self.__pyCover.getGui() )
		self.__pyCover.pos = pyItem.pos
		self.__pyCover.posZ = pyItem.posZ - 0.001
		self.__pyCover.visible = True
		BigWorld.cancelCallback( ItemCoverArray.__c_cbid_vs_detect )
		ItemCoverArray.__c_cbid_vs_detect = BigWorld.callback( 1.0, Functor( self.highlightItem, pyItem ) ) # 1秒检测一次

	def normalizeItem( self ) :
		"""
		隐藏高亮膜
		@return					   : None
		"""
		self.__pyCover.visible = False
		BigWorld.cancelCallback( ItemCoverArray.__c_cbid_vs_detect )

	# -------------------------------------------------
	def showItemCover( self, pyItem ) :
		"""
		高亮显示多个物品格（一般用于拖动某个物品时，高亮显示装备中同类物品）
		@type				pyItem : python ui
		@param				pyItem : 被高亮显示的 UI
		@return					   : None
		"""
		if pyItem in self.__pyCovers : return
		parent = pyItem.getGui().parent
		if parent is None : return
		pyCover = self.getOneInstanceFromPool()
		pyCover.resetMode( pyItem.size )
		self.__pyCovers[pyItem] = pyCover
		parent.addChild( pyCover.getGui() )
		pyCover.pos = pyItem.pos
		pyCover.posZ = pyItem.posZ - 0.001
		pyCover.visible = True
		return pyCover
	def hideItemCover( self, pyItem ) :
		"""
		隐藏高亮膜组
		"""
		if pyItem in self.__pyCovers :
			itemCover=self.__pyCovers.pop( pyItem )
			itemCover.visible=False
			self.instanceList.append(itemCover)

	def showSpellingItemCover( self, pyItem ) :
		"""
		用绿色边框贴图覆盖正在施放的技能
		@type				pyItem : python ui
		@param				pyItem : 被覆盖的 UI
		@return					   : None
		"""
		pyCover = self.showItemCover( pyItem )
		if pyCover is not None :
			size = pyCover.size
			if ( int( size[0]), int( size[1]) ) == ( 32, 32 ) :
				pyCover.texture = self.__cc_spellingTextures[(32, 32)]
			else :
				pyCover.texture = self.__cc_spellingTextures[(48, 48)]
			pyCover.posZ = pyItem.posZ - 0.003
		return pyCover

	def showInvalidItemCover( self, pyItem ) :
		"""
		用红色边框贴图覆盖选中的不可用技能
		@type				pyItem : python ui
		@param				pyItem : 被覆盖的 UI
		@return					   : None
		"""
		pyCover = self.showItemCover( pyItem )
		if pyCover is not None :
			size = pyCover.size
			if ( int( size[0]), int( size[1]) ) == ( 32, 32 ) :
				pyCover.texture = self.__cc_invalidTextures[(32, 32)]
			else :
				pyCover.texture = self.__cc_invalidTextures[(48, 48)]
			pyCover.posZ = pyItem.posZ - 0.002
		return pyCover

