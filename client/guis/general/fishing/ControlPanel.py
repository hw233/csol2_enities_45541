# -*- coding:gb18030 -*-

import GUI
import BigWorld
import keys
import Define
from bwdebug import *
from guis.Toolbox import toolbox
from guis import uiFixer, UIState
from guis.common.RootGUI import RootGUI
from guis.common.GUIBaseObject import GUIBaseObject
from guis.controls.SelectableButton import SelectableButton
from guis.controls.SelectorGroup import SelectorGroup
from guis.controls.CheckBox import CheckBoxEx
from guis.controls.StaticText import StaticText
from guis.controls.Control import Control
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.ScreenViewer import ScreenViewer
from guis.ExtraEvents import LastKeyDownEvent
from event import EventCenter as ECenter
from LabelGather import labelGather
from MessageBox import *
from fishing.FishingDataMgr import FishingDataMgr
from Function import Functor
from ChatFacade import chatFacade
from BulletShop import BulletShop
from MessageBox import *


class ControlPanel(RootGUI):

	_instance = None

	def __init__(self):
		assert ControlPanel._instance is None, "You should invoke class method instance."
		ControlPanel._instance = self
		gui = GUI.load("guis/general/fishing/controlpanel.gui")
		uiFixer.firstLoadFix(gui)
		RootGUI.__init__(self, gui)
		self.focus = False
		self.movable_ = False
		self.escHide_ = False
		self.v_dockStyle = "BOTTOM"
		self.h_dockStyle = "CENTER"

		self._keyEventMap = {}

		self._cardFirstLeft = 0
		self._multipleCards = []

		self.__initialize(gui)

		self._triggers = {}
		self._triggers["EVT_FISHING_ON_UPDATE_BULLET"] = self._updateBulletAmount
		self._triggers["EVT_ON_ROLE_MONEY_CHANGED"] = self._onRoleMoneyChanged
		self._triggers["EVT_ON_ROLE_SILVER_CHANGED"] = self._onRoleSilverChanged
		self._triggers["EVT_FISHING_ON_GAIN_MULTIPLE_CARD"] = self._onAddedMultipleCard
		self._triggers["EVT_FISHING_ON_USE_MULTIPLE_CARD"] = self._onUsedMultipleCard
		self._triggers["EVT_FISHING_ON_BUY_BULLET"] = self._onPopupBulletShop
		self._triggers["EVT_ON_RESOLUTION_CHANGED"] = self._onResolutionChanged
		for evt in self._triggers:
			ECenter.registerEvent(evt, self)

		# 添加清屏例外窗口
		ScreenViewer().addResistHiddenRoot(self)
		# 加入窗口管理器
		self.addToMgr()

	def __initialize(self, gui):
		# 初始化炮弹类型选择按钮
		self._bulletSwitcher = SelectorGroup()
		self._bulletSwitcher.onSelectChanged.bind(self._onBulletSelected)
		for name, child in gui.itemsbar.children:
			index = int(name.split("_")[-1])
			if 0 < index < 8:
				pyBullet = Bullet(child.icon, index)
				pyBullet.onMouseEnter.bind(self._onMouseEnterBullet)
				pyBullet.onMouseLeave.bind(self._onHideInfoTip)
				key = eval("keys.KEY_%i" % index)
				self._keyEventMap[key] = Functor(self._changeBulletLevel, index)
				self._bulletSwitcher.addSelector(pyBullet)
			else:
				pyCard = Card(child.icon)
				pyCard.init(index - 7, 0)
				pyCard.locked = True
				pyCard.onMouseEnter.bind(self._onMouseEnterCard)
				pyCard.onMouseLeave.bind(self._onHideInfoTip)
				key = eval("keys.KEY_%i" % (index % 10))
				self._keyEventMap[key] = Functor(self._useCard, pyCard.type)
				pyCard.onLClick.bind(self._onCardClicked)
				self._multipleCards.append(pyCard)

		# 绑定按键事件
		LastKeyDownEvent.attach(self._onLastKeyDownEvent)

		self._pyAutoBuyChecker = CheckBoxEx(gui.cbox_autoBuy)		# 自动购买选择框
		self._pyAutoBuyChecker.onCheckChanged.bind(self._onAutoBuyChanged)
		self._pyAutoBuyChecker.onMouseEnter.bind(self._onMouseEnterAutoBuyChecker)
		self._pyAutoBuyChecker.onMouseLeave.bind(self._onHideInfoTip)
		self._pyAutoBuyChecker.crossFocus = True

		#self._pyBulletAmount = StaticText(gui.text_bullet)			# 子弹数量
		#self._pyBulletAmount.visible = False                        # 暂时隐藏

		self._pyMoney = StaticText(gui.mbox_coin.st_value)			# 游戏币数量
		self._pySilver = StaticText(gui.mbox_silver.st_value)		# 元宝数量
		self._pyMultipleClew = MultipleClew(gui.text_multiple)		# 加倍效果提示

		# 购买炮弹按钮
		self._pyBtnBuyBullet = HButtonEx(gui.btn_buy_bullet)
		self._pyBtnBuyBullet.setExStatesMapping(UIState.MODE_R4C1)
		self._pyBtnBuyBullet.onLClick.bind(self._onBuyBulletClicked)
		labelGather.setPyLabel(self._pyBtnBuyBullet, "fishing:Datas", "btn_buy_bullet")

		# 关闭按钮
		self._pyCloseBtnRoot = CloseButtonRoot()
		self._pyCloseBtnRoot.pyCloseBtn.onLClick.bind(self._onClickToQuit)

		# 炮弹商店
		self._pyBulletShop = BulletShop()

	def __del__(self):
		""""""
		print "---->>> %s delected." % self.__class__.__name__

	def dispose(self):
		RootGUI.dispose(self)
		self._pyCloseBtnRoot.dispose()
		self._pyBulletShop.dispose()

		for evt in self._triggers:
			ECenter.unregisterEvent(evt, self)

		self._keyEventMap.clear()

	def afterStatusChanged( self, oldStatus, newStatus ) :
		"""
		当游戏状态改变时被调用
		@param					onStatus  : 改变前的状态（在 Define.py 中定义）
		@param					newStatus : 改变后的状态（在 Define.py 中定义）
		"""
		if newStatus == Define.GST_IN_WORLD:
			startclew = labelGather.getText("fishing:Datas", "start_clew")
			ECenter.fireEvent("EVT_ON_SHOW_SCENARIO_TIPS", startclew, True)
			BigWorld.player().detectToEnterFishing()
			self._pyBulletShop.loadBullets()

	def layoutAndShow(self, style):
		""""""
		self._updateMoney(BigWorld.player().money)
		self._updateSilver(BigWorld.player().silver)
		self.show()
		self._pyCloseBtnRoot.show(self)
		self._changeBulletLevel(1)

	def layoutToLeftStyle(self):
		""""""
		self.h_dockStyle = "LEFT"
		self.left = 0

	def layoutToRightStyle(self):
		self.h_dockStyle = "RIGHT"
		self.right = BigWorld.screenWidth()

	def _onBulletSelected(self, pyBullet):
		""""""
		ECenter.fireEvent("EVT_FISHING_ON_PLAYER_CHANGE_CANNONBALL_LEVEL", pyBullet.level)

	def _changeBulletLevel(self, level):
		""""""
		for pyBullet in self._bulletSwitcher.pySelectors:
			if pyBullet.level == level:
				self._bulletSwitcher.pyCurrSelector = pyBullet

	def _onAutoBuyChanged(self, checked):
		""""""
		ECenter.fireEvent("EVT_FISHING_ON_PLAYER_CHANGE_AUTO_BUY", checked)

	def _onBuyBulletClicked(self):
		""""""
		self._onPopupBulletShop()

	def _onMouseEnterAutoBuyChecker(self):
		print "------>>> mouse enter"
		toolbox.infoTip.showToolTips(self, labelGather.getText("fishing:Datas", "autoBuyTip"), True)

	def _onHideInfoTip(self):
		print "------>>> mouse leave"
		toolbox.infoTip.hide()

	def _onMouseEnterBullet(self, pyBullet):
		""""""
		bullet_data = FishingDataMgr.instance().getCannonballDataByLevel(pyBullet.level)
		price = bullet_data["price"]
		if price.type() == "coin":
			currency = labelGather.getText("fishing:Datas", "currency_money")
		elif price.type() == "ingot":
			currency = labelGather.getText("fishing:Datas", "currency_silver")
		else:
			currency = "Unknow"
		format_str = labelGather.getText("fishing:Datas", "bullet_info_tip")
		toolbox.infoTip.showToolTips(self, format_str % (pyBullet.level, "", price.value, currency, currency), True)

	def _onMouseEnterCard(self, pyCard):
		""""""
		card_data = FishingDataMgr.instance().getMultipleCardDataByType(pyCard.type)
		format_str = labelGather.getText("fishing:Datas", "card_info_tip")
		multiple = card_data["multiple"]
		toolbox.infoTip.showToolTips(self, format_str % (multiple, card_data["persistent"], multiple, multiple), True)

	def _updateBulletAmount(self, amount):
		""""""
		self._bulletSwitcher.pyCurrSelector.setAmount(amount)

	def _onRoleMoneyChanged(self, oldValue, newValue):
		""""""
		self._pyBulletShop.updateOwnMoney(newValue)
		self._updateMoney(newValue)

	def _onRoleSilverChanged(self, oldValue, newValue):
		""""""
		self._pyBulletShop.updateOwnSilver(newValue)
		self._updateSilver(newValue)

	def _updateMoney(self, value):
		""""""
		self._pyMoney.text = str(value)

	def _updateSilver(self, value):
		""""""
		self._pySilver.text = str(value)

	def _onAddedMultipleCard(self, fisherID, type, fishUid):
		""""""
		if fisherID != BigWorld.player().id:
			return

		for pyCard in self._multipleCards:
			if pyCard.type == type:
				pyCard.increase()
				if pyCard.locked:
					pyCard.locked = False
				break
		else:
			ERROR_MSG("Can't find card of type %s" % type)

	def _onUsedMultipleCard(self, fisherID, type):
		""""""
		if fisherID != BigWorld.player().id:
			return

		for pyCard in self._multipleCards:
			if pyCard.type == type:
				pyCard.decrease()
				card_data = FishingDataMgr.instance().getMultipleCardDataByType(type)
				base_text = labelGather.getText("fishing:Datas", "text_multiple")
				self._pyMultipleClew.clew(base_text, card_data["multiple"], card_data["persistent"])
				if pyCard.amount == 0 and not pyCard.locked:
					pyCard.locked = True
				break

	def _onPopupBulletShop(self):
		"""子弹用光，提示购买子弹"""
		def inner_callback(bulletLevel, amount, autobuy):
			if autobuy != self._pyAutoBuyChecker.checked:
				self._pyAutoBuyChecker.checked = autobuy
			ECenter.fireEvent("EVT_FISHING_ON_PLAYER_BUYING_BULLET", bulletLevel, amount)

		self._pyBulletShop.popup(self._bulletSwitcher.pyCurrSelector.level,
		                         self._pyAutoBuyChecker.checked,
		                         inner_callback,
		                         self)

	def _locateCards(self):
		""""""
		for index, pyCard in enumerate(self._multipleCards):
			pyCard.left = self._cardFirstLeft + index * (pyCard.width + 3)

	def _onCardClicked(self, pyCard):
		""""""
		self._useCard(pyCard.type)

	def _useCard(self, type):
		""""""
		print "------>>> use card of type %i" % type
		BigWorld.player().base.fish_useItem(type)

	def _onClickToQuit(self):
		""""""
		def callback(res):
			if res == RS_OK:
				BigWorld.player().cell.fish_leaveFishing()

		py_msg = showMessage(0x10c0, "", MB_OK_CANCEL, callback, self)
		ScreenViewer().addResistHiddenRoot(py_msg)
		py_msg.visible = True

	def _onResolutionChanged(self, preReso):
		print "------>>> event notify resolution changed."

	def _onLastKeyDownEvent(self, key, mods):
		""""""
		if mods == 0:
			handler = self._keyEventMap.get(key)
			if handler:
				handler()
				return True
		return False

	@classmethod
	def instance(CLS):
		if ControlPanel._instance is None:
			ControlPanel._instance = ControlPanel()
		return ControlPanel._instance

	@classmethod
	def isInstanced(CLS):
		return ControlPanel._instance is not None

	@classmethod
	def release(CLS):
		if ControlPanel._instance is not None:
			ControlPanel._instance.dispose()
			ControlPanel._instance = None

	@classmethod
	def onEvent(CLS, evtMacro, *args ):
		""""""
		if evtMacro == "EVT_ON_ENTER_FISHING":
			ControlPanel.instance().layoutAndShow(*args)
		elif ControlPanel.isInstanced():
			if evtMacro == "EVT_ON_LEAVE_FISHING":
				ControlPanel.release()
			else:
				ControlPanel.instance()._triggers[evtMacro](*args)


class CloseButtonRoot(RootGUI):

	def __init__(self):
		gui = GUI.load("guis/general/fishing/closebutton.gui")
		uiFixer.firstLoadFix(gui)
		RootGUI.__init__(self, gui)
		self.movable_ = False
		self.escHide_ = False
		self.v_dockStyle = "TOP"
		self.h_dockStyle = "RIGHT"

		self._pyCloseBtn = Button(gui.sub_closebtn)
		self._pyCloseBtn.setStatesMapping(UIState.MODE_R2C2)
		# 添加清屏例外窗口
		ScreenViewer().addResistHiddenRoot(self)
		# 加入窗口管理器
		self.addToMgr()

	def __del__(self):
		print "%s delected..." % self.__class__


	pyCloseBtn = property(lambda self: self._pyCloseBtn)


# ---------------------------------------------------------------
# Item
# ---------------------------------------------------------------
class ItemBase(GUIBaseObject):

	def __init__(self, gui):
		GUIBaseObject.__init__(self, gui)
		self._scTag = None
		self._pyText = StaticText(gui.st_number)
		self._pyText.fontSize = 12

	def _updateText(self, text):
		""""""
		self._pyText.text = str(text)

	def _onShortcutTrigger(self):
		""""""
		return False

	def setIcon(self, texture="guis/empty.dds", color=(255,255,255)):
		""""""
		self.texture = texture
		self.color = color


# ---------------------------------------------------------------
# Bullet item
# ---------------------------------------------------------------
BULLET_SET = {
	1: (82,113,24),
	2: (82,150,24),
	3: (82,200,24),
	4: (150,150,0),
	5: (190,190,0),
	6: (220,220,0),
	7: (255,255,0),
}


class Bullet(SelectableButton, ItemBase):

	_cover_ui = None

	def __init__(self, gui, level):
		ItemBase.__init__(self, gui)
		SelectableButton.__init__(self, gui)
		self._level = level
		self._updateText("")

		#self.setIcon(color = BULLET_SET[level])
		#self.commonBackColor = BULLET_SET[level]
		#self.highlightBackColor = (255, 88, 33)
		#self.selectedBackColor = (33, 67, 214)

	def setStateView_(self, state):
		"""
		设置指定状态下的外观表现
		"""
		SelectableButton.setStateView_(self, state)
		if state == UIState.SELECTED:
			self._pyText.visible = True
			self.usingCover()
		else:
			self._pyText.visible = False

	def setAmount(self, amount):
		"""设置数量"""
		self._updateText(amount)

	def usingCover(self):
		"""设置正在使用的表现"""
		if Bullet._cover_ui is None:
			Bullet._cover_ui = GUI.load("guis/general/fishing/usingcover.gui")
		self.gui.addChild(Bullet._cover_ui)

	def _onShortcutTrigger(self):
		"""快捷键触发"""
		self.selected = True
		return True


	level = property(lambda self: self._level)


# ---------------------------------------------------------------
# Multiple card
# ---------------------------------------------------------------
CARD_SET = {
	1: (100,255,255),
	2: (255,100,255),
	3: (255,255,100),
}


class Card(Control, ItemBase):

	def __init__(self, gui):
		ItemBase.__init__(self, gui)
		Control.__init__(self, gui)
		self.focus = True
		self.crossFocus = True
		self._type = 0
		self._amount = 0
		self._locked = False

	def _getType(self):
		return self._type

	def _getLocked(self):
		return self._locked

	def _setLocked(self, locked):
		self._locked = locked
		if locked:
			self._pyText.materialFX = "COLOUR_EFF"
			self.materialFX = "COLOUR_EFF"
		else:
			self._pyText.materialFX = "BLEND"
			self.materialFX = "BLEND"

	def _updateAmount(self):
		""""""
		self._updateText(self._amount)

	def _onShortcutTrigger(self):
		"""快捷键触发"""
		if self._locked:
			return False
		else:
			self.onLClick()
			return True

	def onLClick_(self, mods):
		"""
		当鼠标左键点击时被调用
		"""
		if self._locked:
			return True
		else:
			return Control.onLClick_(self, mods)

	def init(self, type, amount):
		""""""
		self._type = type
		self._amount = amount
		self._updateAmount()

	def increase(self):
		"""数量增加"""
		self._amount += 1
		self._updateAmount()

	def decrease(self):
		"""数量减少"""
		self._amount -= 1
		self._updateAmount()

	def copyFrom(self, pyCard):
		"""复制其他卡片的信息"""
		self._type = pyCard.type
		self._amount = pyCard.amount
		self._updateAmount()
		self.setIcon(pyCard.texture, pyCard.color)

	def clear(self):
		"""清空信息"""
		self._type = 0
		self._amount = 0
		self._updateText("")
		self.setIcon("")


	type = property(_getType)
	amount = property(lambda self: self._amount)
	locked = property(_getLocked, _setLocked)


class MultipleClew(StaticText):

	def __init__(self, text_ui):
		StaticText.__init__(self, text_ui)
		self.text = ""
		self._base_text = ""
		self._multiple = 0
		self._persistent = 0
		self._countdown_cbid = 0

	def clew(self, base_text, multiple, persistent):
		""""""
		self._base_text = base_text
		self._multiple = multiple
		self._persistent = persistent
		self._start_count_down()

	def _start_count_down(self):
		""""""
		self._stop_count_down()
		self._count_down()

	def _stop_count_down(self):
		""""""
		if self._countdown_cbid:
			BigWorld.cancelCallback(self._countdown_cbid)
			self._countdown_cbid = 0

	def _count_down(self):
		""""""
		if self._persistent > 0:
			self.text = self._base_text % (self._multiple, self._persistent)
			self._persistent -= 1
			self._countdown_cbid = BigWorld.callback(1.0, self._count_down)
		else:
			self.text = ""


ECenter.registerEvent("EVT_ON_ENTER_FISHING", ControlPanel)
ECenter.registerEvent("EVT_ON_LEAVE_FISHING", ControlPanel)


def release():
	ECenter.unregisterEvent("EVT_ON_ENTER_FISHING", ControlPanel)
	ECenter.unregisterEvent("EVT_ON_LEAVE_FISHING", ControlPanel)
	ControlPanel.release()

def construct(style):
	ControlPanel.instance().layoutAndShow(style)
