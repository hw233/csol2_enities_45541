# -*- coding: gb18030 -*-
#
# $Id: DroppedItem.py,v 1.62 2008-08-29 02:38:41 huangyongwei Exp $

import BigWorld
import Pixie
import GUI
import csol
import csstatus
import ItemTypeEnum
import event.EventCenter as ECenter
from bwdebug import *
from utils import *
import csdefine
import Define
from gbref import rds
from interface.GameObject import GameObject

C_DEFAULT_MODEL_FILE = "dlwp/Model/dlwp_sub_dm_qt_0000shape1.model"

class DroppedItem( GameObject ):
	# 拾取物品的最大范围
	__cc_valid_range	= 3

	def __init__( self ):
		GameObject.__init__( self )
		self.gx = Pixie.create( "particles/tong_tong/diaoluowupin.xml" )
		self.model = None
		self.setSelectable( True )
		self.selectable = True

	def enterWorld( self ):
		if (self.model == None):
			if self.itemProp.isType( ItemTypeEnum.ITEM_MONEY ):
				mf = getMoneyModelFile( self.itemProp.amount )
			else:
				mf = getModelFile( self.itemProp.model() )
			if mf is None or len(mf) == 0:
				WARNING_MSG( "no model found, use default model.(%s)" % self.itemProp.model() )
				mf = C_DEFAULT_MODEL_FILE

			self.model = BigWorld.Model( mf )
		self.model.node("HP_root").attach( self.gx )
		self.model.play()
		ECenter.fireEvent( "EVT_ON_ENTITY_ENTER_WORLD", self )
		nameText = ""
		if self.itemProp.amount > 1:
			nameText = "%s(%i)" % ( self.getName(), self.itemProp.amount )
		else:
			nameText = self.getName()
		ECenter.fireEvent( "EVT_ON_ENTITY_NAME_CHANGED", self.id, nameText )

	def prerequisites( self ):
		"""
		This method will be called before EnterWorld method
		"""
		nNames = []
		nNames.append( getModelFile( self.itemProp.model() ) )
		return nNames

	# Becoming a target
	def onTargetFocus( self ):
		if ( self.inWorld ):
			if self.itemProp.amount > 1:
				new_text = "%s(%i)" % ( self.getName(), self.itemProp.amount )
			rng = self.distanceBB( BigWorld.player() )
			if rng <= self.__cc_valid_range :					# 判断距离 如果可以直接交互显示亮图 否则显示灰图
				rds.ccursor.set( "pickup" )						# modified by hyw( 2008.09.12 )
			else:
				rds.ccursor.set( "pickup", True )				# modified by hd( 2008.09.16 )

	# Quitting as target
	def onTargetBlur( self ):
		rds.ccursor.set( "normal" )

	def tryPickup( self, player, position ):
		if self.itemProp.isType( ItemTypeEnum.ITEM_MONEY ):
			if player.testAddMoney( self.itemProp.amount ) > 0:			#查看此次操作是否会使金钱达到上限
				player.statusMessage( csstatus.CIB_MSG_MONEY_OVERFLOW )
				if player.ifMoneyMax():									#如果玩家的金钱已经超出上限
					return
			self.cell.pickup()
		else:
			if player.checkItemsPlaceIntoNK_( [ self.itemProp ] ) == csdefine.KITBAG_CAN_HOLD:
				self.cell.pickup()
			elif player.checkItemsPlaceIntoNK_( [ self.itemProp ] ) == csdefine.KITBAG_NO_MORE_SPACE:
				#DEBUG_MSG( "I can't pickup it" )
				player.statusMessage( csstatus.CIB_MSG_BAG_HAS_FULL )
			elif player.checkItemsPlaceIntoNK_( [ self.itemProp ] ) == csdefine.KITBAG_ITEM_COUNT_LIMIT:
				player.statusMessage( csstatus.CIB_MSG_BAG_ITEM_LIMIT, self.getName() )

		return Define.TARGET_PURSUE_SUCCESS

	def onTargetClick( self, player ):
		pass

	def getName( self ):
		"""
		取得entity名称
		"""
		return self.itemProp.name()

	def getHP( self ):
		"""
		@return: INT
		"""
		return 0

	def getHPMax( self ):
		"""
		@return: INT
		"""
		return 0

	def getMP( self ):
		"""
		@return: INT
		"""
		return 0

	def getMPMax( self ):
		"""
		@return: INT
		"""
		return 0

	def getHeadTexture( self ):
		"""
		@return: ???
		"""
		return None

	def getLevel( self ):
		"""
		@return: INT
		"""
		return 0

# ----------------->
# function
# ----------------->
g_preloads = {}
g_preloadMoney = []		# [ (amount, file), ... ]

def getModelFile( modelID ):
	"""
	通过模型号获得模型文件名

	@param modelID: 模型ID号
	@type  modelID: UINT32
	@return: 如果找到了则返回相应的模型文件名,找不到则返回空字符串""
	@rtype:  String
	"""
	if g_preloads.has_key( modelID ):
		return g_preloads[modelID]
	return rds.itemModel.getDropModelByID( modelID )

def getMoneyModelFile( moneyAmount ):
	"""
	根据金钱的数量取得模型文件
	"""
	# 暂时使用默认金钱数量掉落模型
	if len( g_preloadMoney ) == 0:
		return rds.itemModel.getDropModelByID( "99-98-0001")

	for amount, fileName in g_preloadMoney:
		if moneyAmount >= amount:
			return fileName


# DroppedItem.py
