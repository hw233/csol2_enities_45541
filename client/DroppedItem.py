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
	# ʰȡ��Ʒ�����Χ
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
			if rng <= self.__cc_valid_range :					# �жϾ��� �������ֱ�ӽ�����ʾ��ͼ ������ʾ��ͼ
				rds.ccursor.set( "pickup" )						# modified by hyw( 2008.09.12 )
			else:
				rds.ccursor.set( "pickup", True )				# modified by hd( 2008.09.16 )

	# Quitting as target
	def onTargetBlur( self ):
		rds.ccursor.set( "normal" )

	def tryPickup( self, player, position ):
		if self.itemProp.isType( ItemTypeEnum.ITEM_MONEY ):
			if player.testAddMoney( self.itemProp.amount ) > 0:			#�鿴�˴β����Ƿ��ʹ��Ǯ�ﵽ����
				player.statusMessage( csstatus.CIB_MSG_MONEY_OVERFLOW )
				if player.ifMoneyMax():									#�����ҵĽ�Ǯ�Ѿ���������
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
		ȡ��entity����
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
	ͨ��ģ�ͺŻ��ģ���ļ���

	@param modelID: ģ��ID��
	@type  modelID: UINT32
	@return: ����ҵ����򷵻���Ӧ��ģ���ļ���,�Ҳ����򷵻ؿ��ַ���""
	@rtype:  String
	"""
	if g_preloads.has_key( modelID ):
		return g_preloads[modelID]
	return rds.itemModel.getDropModelByID( modelID )

def getMoneyModelFile( moneyAmount ):
	"""
	���ݽ�Ǯ������ȡ��ģ���ļ�
	"""
	# ��ʱʹ��Ĭ�Ͻ�Ǯ��������ģ��
	if len( g_preloadMoney ) == 0:
		return rds.itemModel.getDropModelByID( "99-98-0001")

	for amount, fileName in g_preloadMoney:
		if moneyAmount >= amount:
			return fileName


# DroppedItem.py
