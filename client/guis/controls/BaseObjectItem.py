# -*- coding: gb18030 -*-
#
# $Id: BaseObjectItem.py,v 1.11 2008-06-27 03:15:11 huangyongwei Exp $

"""
implement objectitem base class
it will be inherited by the item which specified object,

2007.03.17: writen by huangyongwei
"""
"""
composing :
	GUI.Window
		-- lbAmount: GUI.Text ( ��ʾ��Ʒ��������û�� )
"""

from guis import *
from Item import Item
from guis.controls.StaticText import StaticText

import Define
from guis.ItemsBrush import itemsBrush

class BaseObjectItem( Item ) :
	"""
	��Ʒ�����
	"""
	_particlePath = [
						"maps/particle_2d/guangxiao_lvguang/guangxiao_lvguang.texanim",
						"maps/particle_2d/guangxiao_languang/guangxiao_languang.texanim",
						"maps/particle_2d/guangxiao_hongguang/guangxiao_hongguang.texanim",
						"maps/particle_2d/guangxiao_ziguang/guangxiao_ziguang.texanim"
					]
	def __init__( self, item = None, pyBinder = None ) :
		self.pyLbAmount_ = StaticText()				# label for showing the number of obejct
		Item.__init__( self, item, pyBinder )
		self.__initialize( item )
		self.focus = True
		self.dragFocus = True
		self.__intensify_pName = "intensifyParticle"

	def subclass( self, item, pyBinder ) :
		Item.subclass( self, item, pyBinder )
		self.__initialize( item )
		return self

	def __del__( self ) :
		Item.__del__( self )
		itemsBrush.detach( self )								# �����߸��Ӵ���Ʒˢ��󣬷�������������Ʒ�����������ͷ�ʱ���Ƴ��������ڵ���
		if Debug.output_del_BaseObjectItem :
			INFO_MSG( str( self ) )

	def __initialize( self, item ) :
		if item is None : return
		if hasattr( item, "lbAmount" ) :
			self.pyLbAmount_.subclass( item.lbAmount )
		self.clear()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def clear( self ) :
		"""
		resume the object item to empty state
		"""
		self.amountText = ""
		Item.clear( self )


	def upDateParticle( self, intensifyLevel ):
		"""
		����ͼ���Ϲ���ǿ���ȼ���Ч��
		"""
		gui = self.getGui()
		if intensifyLevel < 6:
			if hasattr( gui, self.__intensify_pName ):
				for child in gui.children:
					if child[0] == self.__intensify_pName:
						child[1].visible = False
						return
			return
		assert intensifyLevel <= 9, "illegal, intensifyLevel is greater than 9"
		textureName = self._particlePath[ intensifyLevel - 6 ]
		if not hasattr( gui, self.__intensify_pName ):
			toolbox.itemParticle.addParticle( self , textureName, self.__intensify_pName )
		else:
			for child in gui.children:
				if child[0] == self.__intensify_pName:
					child[1].textureName = textureName
					child[1].visible = True
					return

	def hideParticle( self ):
		"""
		���������Ч��
		"""
		gui = self.getGui()
		if hasattr( gui, self.__intensify_pName ):
			for child in gui.children:
				if child[0] == self.__intensify_pName:
					child[1].visible = False
					return

	def update( self, itemInfo ) :
		Item.update( self, itemInfo )
		if itemInfo is not None :
			itemsBrush.attach( self )							# ���Խ����߸��Ӱ󶨵���Ʒˢ
			amount = itemInfo.amount
			self.amountText = amount > 1 and str( amount ) or ""
			self.upDateParticle( itemInfo.intensifyLevel )		# ����ǿ��6�Ǻ�ͼ���Ч����ʾ
			self.updateUseStatus( itemInfo.checkUseStatus() )	# ������Ʒ�Ŀ�ʹ��״̬
		else :
			itemsBrush.detach( self )							# �����߸��Ӵ���Ʒˢ���
			self.hideParticle()
			self.updateUseStatus( Define.ITEM_STATUS_NATURAL )

	def updateUseStatus( self, itemStatus ) :
		"""
		������Ʒ��ʹ��״̬�ı���
		"""
		self.color = Define.ITEM_STATUS_TO_COLOR[ itemStatus ]


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getAmount( self ) :
		if self.itemInfo is None :
			return 0
		return self.itemInfo.amount

	# -------------------------------------------------
	def _getAmountText( self ) :
		return self.pyLbAmount_.text

	def _setAmountText( self, strAmount ) :
		self.pyLbAmount_.text = strAmount

	def _getAmountColor( self ):
		return self.pyLbAmount_.color

	def _setAmountColor( self,color ):
		self.pyLbAmount_.color = color

	def _getFontSize( self ):
		return self.pyLbAmount_.fontSize

	def _setFontSize( self, fontSize ):
		self.pyLbAmount_.fontSize = fontSize

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	amount = property( _getAmount )
	amountText = property( _getAmountText, _setAmountText )				# get or set amount of the object
	amountColor = property( _getAmountColor, _setAmountColor )
	fontSize = property( _getFontSize, _setFontSize )