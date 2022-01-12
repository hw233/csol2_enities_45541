# -*- coding:gb18030 -*-

import GUI
import utils
from bwdebug import *
from guis import uiFixer, UIState, InputMode
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.controls.CheckBox import CheckBoxEx
from guis.controls.StaticText import StaticText
from guis.controls.ODComboBox import ODComboBox, InputBox
from guis.controls.TextBox import TextBox
from guis.ScreenViewer import ScreenViewer
from LabelGather import labelGather
from fishing.FishingDataMgr import FishingDataMgr


class BulletShop(Window):

	def __init__(self):
		gui = GUI.load("guis/general/fishing/bulletshop.gui")
		uiFixer.firstLoadFix(gui)
		Window.__init__(self, gui)

		self._callback = None
		self.__initialize(gui)
		#self.loadBullets()

		# 添加清屏例外窗口
		ScreenViewer().addResistHiddenRoot(self)
		# 加入窗口管理器
		self.addToMgr()

	def __initialize(self, gui):
		class MyInputBox(InputBox):

			def onItemSelectChanged_( self, index ):
				"""选项改变时被调用"""
				pyCombo = self.pyComboBox
				default_text = labelGather.getText("fishing:BulletShop", "combotext")
				self.text = default_text if index < 0 else pyCombo.items[index]["name"]

		class MyComboBox(ODComboBox):

			def __init__(self, comboBox = None, clsBox = None, pyBinder = None):
				ODComboBox.__init__(self, comboBox, clsBox, pyBinder)
				# 添加清屏例外窗口
				ScreenViewer().addResistHiddenRoot(self.pyComboList_)

		self._pyBulletBox = MyComboBox(gui.combo_bullet, clsBox=MyInputBox)
		self._pyBulletBox.ownerDraw = True
		self._pyBulletBox.autoSelect = False
		self._pyBulletBox.onViewItemInitialized.bind(self._onBulletItemInitialized)
		self._pyBulletBox.onDrawItem.bind(self._onBulletItemDraw)
		self._pyBulletBox.onItemSelectChanged.bind(self._onBulletSelected)

		self._pyAutoBuyCheker = CheckBoxEx(gui.ckbox_autobuy)

		self._pyBuyBtn = Button(gui.btn_buy)
		self._pyBuyBtn.setStatesMapping(UIState.MODE_R4C1)
		self._pyBuyBtn.onLClick.bind(self._onBuyClicked)
		self.setOkButton(self._pyBuyBtn)

		self._pyBulletPrice = StaticText(gui.stext_bulletprice)
		self._pyBulletPrice.text = ""

		self._pyTotalCost = StaticText(gui.stext_totalcost)
		self._pyTotalCost.text = ""

		self._pyOwnMoney = StaticText(gui.stext_money)
		self._pyOwnMoney.text = ""

		self._pyOwnSilver = StaticText(gui.stext_silver)
		self._pyOwnSilver.text = ""

		self._pyBuyCount = TextBox(gui.input_buycount.box)
		self._pyBuyCount.inputMode = InputMode.INTEGER
		self._pyBuyCount.onTextChanged.bind(self._onCountChanged)

		# 设置文本
		labelGather.setLabel(gui.st_selectbullet, "fishing:BulletShop", "st_selectbullet")
		labelGather.setLabel(gui.st_bulletprice, "fishing:BulletShop", "st_bulletprice")
		labelGather.setLabel(gui.st_totalcost, "fishing:BulletShop", "st_totalcost")
		labelGather.setLabel(gui.st_buycount, "fishing:BulletShop", "st_buycount")
		labelGather.setLabel(gui.st_money, "fishing:BulletShop", "st_money")
		labelGather.setLabel(gui.st_silver, "fishing:BulletShop", "st_silver")
		labelGather.setPyLabel(self.pyLbTitle_, "fishing:BulletShop", "lbTitle")
		labelGather.setPyLabel(self._pyBulletBox.pyBox, "fishing:BulletShop", "combotext")
		labelGather.setPyLabel(self._pyAutoBuyCheker, "fishing:BulletShop", "autobuy")
		labelGather.setPyLabel(self._pyBuyBtn, "fishing:BulletShop", "buybtn")

	def loadBullets(self):
		""""""
		self._pyBulletBox.clearItems()
		bullets = FishingDataMgr.instance().getCannonballDatas()
		for b_level, b_data in bullets.iteritems():
			bullet = {
				"level" : b_level,
			    "price" : b_data["price"],
			    "name" : b_data["name"],
			}
			self._pyBulletBox.addItem(bullet)

	def _onBulletItemInitialized(self, pyViewItem):
		""""""
		pyText = StaticText()
		pyViewItem.addPyChild(pyText)
		pyText.pos = (0,0)
		pyViewItem.pyText = pyText

	def _onBulletItemDraw(self, pyViewItem):
		""""""
		pyViewItem.pyText.text = pyViewItem.listItem["name"]

	def _updateBuy(self):
		""""""
		selected_bullet = self._pyBulletBox.selItem
		if selected_bullet:
			buy_amount = self._pyBuyCount.text
			if buy_amount == "":
				buy_amount = 0
			else:
				buy_amount = int(buy_amount)

			price = FishingDataMgr.instance().getCannonballPriceByLevel(selected_bullet["level"])
			if price.type() == "coin":
				self._pyBulletPrice.text = utils.currencyToViewText(price.value, False)
				self._pyTotalCost.text = utils.currencyToViewText(price.value * buy_amount, False)
			elif price.type() == "ingot":
				self._pyBulletPrice.text = "%i%s" % (price.value, labelGather.getText("fishing:Datas", "currency_silver"))
				self._pyTotalCost.text = "%i%s" % (price.value * buy_amount, labelGather.getText("fishing:Datas", "currency_silver"))

			self._pyBuyBtn.enable = buy_amount > 0
		else:
			self._pyBuyBtn.enable = False

	def _onBulletSelected(self, index):
		""""""
		if index:
			bullet = self._pyBulletBox.items[index]
			print "Select bullet of level", bullet["level"]
		print "Select bullet of index", index
		self._updateBuy()

	def _onCountChanged(self):
		""""""
		print "Buy count", self._pyBuyCount.text
		self._updateBuy()

	def _onBuyClicked(self):
		""""""
		print "Buy %i bullet of level %i, set auto buy %s" % \
		      (int(self._pyBuyCount.text), self._pyBulletBox.selItem["level"], self._pyAutoBuyCheker.checked)
		if self._callback:
			callback = self._callback
			self._callback = None
			callback(self._pyBulletBox.selItem["level"], int(self._pyBuyCount.text), self._pyAutoBuyCheker.checked)
		self.hide()

	#----------------------------------------------------------
	# public
	#----------------------------------------------------------
	def popup(self, bulletLevel, autobuy, callback, pyOwner=None):
		""""""
		for bullet in self._pyBulletBox.items:
			if bullet["level"] == bulletLevel:
				self._pyBulletBox.selItem = bullet
		self._callback = callback
		self.show(pyOwner)
		self._pyAutoBuyCheker.checked = autobuy
		self._pyBuyCount.tabStop = True

	def updateOwnMoney(self, value):
		""""""
		self._pyOwnMoney.text = str(value)

	def updateOwnSilver(self, value):
		""""""
		self._pyOwnSilver.text = str(value)
