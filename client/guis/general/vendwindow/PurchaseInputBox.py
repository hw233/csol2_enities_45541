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

		self.__pyBtnMax = Button( wnd.btnMax )						# 最大值按钮
		self.__pyBtnMax.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnMax.onLClick.bind( self.__onMaxBtnClick )

		self.inputMode = InputMode.INTEGER							# 设置为只允许输入数值
		self.maxLength = 6											# 默认最多输入十位数
		self.__amountRng = None										# 默认可以输入任意大小的数值

		self.__pyUnitPrice = MoneyBar( wnd.inputBoxs_0, self )		# 单价输入框
		self.__pyUnitPrice.onTextChanged.bind( self.onTextChanged_ )
		self.__pyTotalPrice = MoneyBar( wnd.inputBoxs_1, self )		# 总价显示框
		self.__pyTotalPrice.readOnly = True							# 总价显示框只读

		self.__pyTitle = StaticText( wnd.lbTitle )
		self.__pySTUnitPrice = StaticText( wnd.st_unitPrice )
		self.__pySTItemAmount = StaticText( wnd.st_itemAmount )
		self.__pySTTotalPrice = StaticText( wnd.st_totalPrice )

		# ---------------------------------------------
		# 设置标签
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
		当最大值按钮被点击时调用
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
		当输入文本改变时被调用
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
		关闭窗口时被调用，在这里通过回调通知父体
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
		@param				callback : 回调
		@type				pyOwner	 : python ui
		@param				pyOwner	 : 所属的父窗口，如果传入该参数，则输入框将永远处于 pyOwner 的上面
		@type				rng		 : tuple of two element
		@param				rng		 : 允许的输入范围，缺省为可以输入任意范围( 如：( 1, 100 )，则包括 100 )
		@param				hintText : 输入字段提示
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

	unitPrice = property( _getUnitPrice, _setUnitPrice )								# 获得/设置单价
	unitPriceReadOnly = property( _getUnitPriceReadOnly, _setUnitPriceReadOnly )		# 单价是否可编辑
	amountRange = property( _getAmountRange, _setAmountRange )							# 数量范围
