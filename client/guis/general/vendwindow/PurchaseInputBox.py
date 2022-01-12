#-*- coding: gb18030 -*-
#
# written by ganjinxing 2010-01-28

from guis import *
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.tooluis.inputbox.InputBox import InputBox
from guis.tooluis.inputbox.MoneyInputBox import MoneyBar
from LabelGather import labelGather


class PurchaseInputBox( InputBox ) :

	def __init__( self ) :
		wnd = GUI.load( "guis/general/vendwindow/inputwnd.gui" )
		uiFixer.firstLoadFix( wnd )
		InputBox.__init__( self, wnd )
		self.pyTextBox_.onTextChanged.bind( self.onTextChanged_ )
		self.pyBtnOk_.enable = False

		self.__pyBtnMax = Button( wnd.btnMax )						# ���ֵ��ť
		self.__pyBtnMax.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnMax.onLClick.bind( self.__onMaxBtnClick )

		self.inputMode = InputMode.INTEGER							# ����Ϊֻ����������ֵ
		self.maxLength = 6											# Ĭ���������ʮλ��
		self.__amountRng = None										# Ĭ�Ͽ������������С����ֵ

		self.__pyUnitPrice = MoneyBar( wnd.inputBoxs_0, self )		# ���������
		self.__pyUnitPrice.onTextChanged.bind( self.onTextChanged_ )
		self.__pyTotalPrice = MoneyBar( wnd.inputBoxs_1, self )		# �ܼ���ʾ��
		self.__pyTotalPrice.readOnly = True							# �ܼ���ʾ��ֻ��

		self.__pyTitle = StaticText( wnd.lbTitle )
		self.__pySTUnitPrice = StaticText( wnd.st_unitPrice )
		self.__pySTItemAmount = StaticText( wnd.st_itemAmount )
		self.__pySTTotalPrice = StaticText( wnd.st_totalPrice )

		# ---------------------------------------------
		# ���ñ�ǩ
		# ---------------------------------------------
		labelGather.setLabel( wnd.st_itemAmount, "vendwindow:PurchaseInputBox", "st_itemAmount" )
		labelGather.setLabel( wnd.st_totalPrice, "vendwindow:PurchaseInputBox", "st_totalPrice" )
		labelGather.setLabel( wnd.st_unitPrice, "vendwindow:PurchaseInputBox", "st_unitPrice" )
		labelGather.setLabel( wnd.btnCancel.lbText, "vendwindow:PurchaseInputBox", "btnCancel" )
		labelGather.setLabel( wnd.btnOk.lbText, "vendwindow:PurchaseInputBox", "btnOk" )
		labelGather.setLabel( wnd.lbTitle, "vendwindow:PurchaseInputBox", "lbTitle" )

	def __del__( self ) :
		InputBox.__del__( self )
		if Debug.output_del_InputBox :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onMaxBtnClick( self ) :
		"""
		�����ֵ��ť�����ʱ����
		"""
		if self.__amountRng is None :
			if self.maxLength > 0 :
				self.text = '9' * self.maxLength
		else :
			self.text = str( self.__amountRng[1] )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onTextChanged_( self ) :
		"""
		�������ı��ı�ʱ������
		"""
		amount = self.text.strip()
		amount = ( amount != "" and ( int( amount ), ) or ( 0, ) )[0]
		unitPrice = self.__pyUnitPrice.money
		totalPrice = amount * unitPrice
		self.__pyTotalPrice.money = totalPrice
		if totalPrice <= 0 :
			self.pyBtnOk_.enable = False
		elif self.__amountRng is not None :
			self.pyBtnOk_.enable = amount >= self.__amountRng[0] and amount <= self.__amountRng[1]
		else :
			self.pyBtnOk_.enable = True

	def notify_( self, res ) :
		"""
		�رմ���ʱ�����ã�������ͨ���ص�֪ͨ����
		"""
		text = self.text.replace( ' ', '' )
		if not text.isdigit() : return False
		unitPrice = self.__pyUnitPrice.money
		if unitPrice <= 0 : return False
		amount = int( text )
		try :
			self.callback_( res, amount, unitPrice )
		except :
			EXCEHOOK_MSG()
		self.pressedOK_ = False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, callback, title = "", pyOwner = None, hintText = [] ) :
		"""
		@type				callback : functor
		@param				callback : �ص�
		@type				pyOwner	 : python ui
		@param				pyOwner	 : �����ĸ����ڣ��������ò��������������Զ���� pyOwner ������
		@type				rng		 : tuple of two element
		@param				rng		 : ��������뷶Χ��ȱʡΪ�����������ⷶΧ( �磺( 1, 100 )������� 100 )
		@param				hintText : �����ֶ���ʾ
		@type				hintText : list of string
		@return						 : None
		"""
		InputBox.show( self, "", callback, pyOwner )
		self.__pyTitle.text = title
		self.__pyUnitPrice.tabStop = True
		if self.__amountRng is not None :
			self.text = str( self.__amountRng[0] )
		if len( hintText ) == 3 :
			self.__pySTUnitPrice.text = hintText[0]
			self.__pySTItemAmount.text = hintText[1]
			self.__pySTTotalPrice.text = hintText[2]


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getUnitPrice( self ) :
		return self.__pyUnitPrice.money

	def _setUnitPrice( self, price ) :
		self.__pyUnitPrice.money = price

	def _getUnitPriceReadOnly( self ) :
		return self.__pyUnitPrice.readOnly

	def _setUnitPriceReadOnly( self, readOnly ) :
		self.__pyUnitPrice.readOnly = readOnly

	def _getAmountRange( self ) :
		return self.__amountRng

	def _setAmountRange( self, rng ) :
		self.__amountRng = rng
		self.pyBtnOk_.enable = rng is not None
		if rng is not None :
			self.text = str( rng[0] )
			unitGoldLength = self.__pyUnitPrice.maxGoldLength
			totalMaxValue = int( "9" * ( unitGoldLength + 4 ) ) * rng[1]
			self.__pyTotalPrice.maxGoldLength = len( str( totalMaxValue / 10000 ) )

	unitPrice = property( _getUnitPrice, _setUnitPrice )								# ���/���õ���
	unitPriceReadOnly = property( _getUnitPriceReadOnly, _setUnitPriceReadOnly )		# �����Ƿ�ɱ༭
	amountRange = property( _getAmountRange, _setAmountRange )							# ������Χ
