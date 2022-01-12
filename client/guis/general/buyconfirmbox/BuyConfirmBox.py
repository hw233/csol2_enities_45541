# -*- coding: gb18030 -*-

# implement BuyConfirmBox class
# This box will be visible when the player buy
# something cost more than one gold from the chapman,
# for attaining the confirmation from the player
# that he/she surely want to buy these goods or not.

import csconst
from guis import *
from guis.common.Window import Window
from guis.controls.CheckBox import CheckBoxEx
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ButtonEx import HButtonEx
from AbstractTemplates import Singleton
from LabelGather import labelGather

class BuyConfirmBox( Singleton, Window ) :
	__instance=None
	__persistent=True						# 是否每次购买时都显示确认框
	__triggers = {}

	def __init__( self ) :
		BuyConfirmBox.__instance=self
		wnd = GUI.load( "guis/general/buyconfirmbox/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L2
		self.__callback = None				# 购买回调
		self.__chapman = None				# 当前交易的商人NPC
		self.__trapID = None
		self.__triggers = {}

		self.__initialize( wnd )

	def __del__( self ) :
		Window.__del__( self )
		if Debug.output_del_BuyConfirmBox :
			INFO_MSG( str( self ) )

	def dispose( self ) :
		Window.dispose( self )
		self.__class__.releaseInst()

	@staticmethod
	def instance():
		"""
		get the exclusive instance of BuyConfirmBox
		"""
		if BuyConfirmBox.__instance is None:
			BuyConfirmBox.__instance=BuyConfirmBox()
		return BuyConfirmBox.__instance

	@staticmethod
	def getInstance():
		"""
		return None or the instance of BuyConfirmBox
		"""
		return BuyConfirmBox.__instance

	def __initialize( self, wnd ) :
		self.__pyCKBox = CheckBoxEx( wnd.ckBox )
		self.__pyCKBox.checked = False

		self.__pyYesBtn = HButtonEx( wnd.yesBtn )
		self.__pyYesBtn.onLClick.bind( self.__onOK )
		self.__pyYesBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.setOkButton( self.__pyYesBtn )

		self.__pyNoBtn = HButtonEx( wnd.noBtn )
		self.__pyNoBtn.onLClick.bind( self.__onCancel )
		self.__pyNoBtn.setExStatesMapping( UIState.MODE_R4C1 )

		self.__pyMsg = CSRichText( wnd.textPanel )
		self.__pyMsg.text = ""

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyCKBox, "BuyConfirmBox:main", "cbNotify" )
		labelGather.setPyBgLabel( self.__pyYesBtn, "BuyConfirmBox:main", "btnYes" )
		labelGather.setPyBgLabel( self.__pyNoBtn, "BuyConfirmBox:main", "btnNo" )


	def __onOK( self ) :
		BuyConfirmBox.__persistent = not self.__pyCKBox.checked
		self.__callback( True )
		self.hide()

	def __onCancel( self ) :
		self.__callback( False )
		self.hide()

	def __addTrap( self ) :
		self.__delTrap()														# 把旧陷阱去掉
		distance = csconst.COMMUNICATE_DISTANCE
		if hasattr( self.__chapman, "getRoleAndNpcSpeakDistance" ):
			distance = self.__chapman.getRoleAndNpcSpeakDistance()
		self.__trapID = BigWorld.addPot( self.__chapman.matrix,distance, self.__onEntitiesTrapThrough )

	def __delTrap( self ) :
		if self.__trapID is not None:
			BigWorld.delPot( self.__trapID )
			self.__trapID = None

	def __onEntitiesTrapThrough( self, enteredTrap, handle  ) :
		if not  enteredTrap:
			self.__onCancel()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def showConfirmBox( self, text, chapman, callback = lambda result : type( result ) is bool ) :
		"""
		@param	text		: 界面上的提示消息
		@type	text		: str
		@param	chapman		: 当前交易的商人NPC
		@type	chapman		: entity
		@param	callback	: 回调方法，带一个bool型参数
		@type	callback	: callable method
		"""
		if not BuyConfirmBox.__persistent : 						# 如果选择了不再提示
			callback( True )							# 则默认为确认购买物品
			return
		self.__chapman = chapman
		self.__addTrap()
		self.__callback = callback
		self.__pyMsg.text = text
		self.__pyMsg.center = self.width / 2
		self.__pyMsg.middle = 73
		self.__pyCKBox.checked = False
		self.center = BigWorld.screenSize()[0] / 2		# 每次弹出窗口都放在屏幕中间
		self.middle = BigWorld.screenSize()[1] / 2
		self.show()
		self.addToMgr()

	def hide( self ) :
		self.__callback = None
		BuyConfirmBox.__instance=None
		self.__delTrap()
		Window.hide( self )
		self.dispose()

	def __del__(self):
		"""
		just for testing memory leak
		"""
		pass

	@classmethod
	def __onLeaveWorld( SELF, role ) :
		if role != BigWorld.player():
			return
		SELF.__persistent = True						# 下线后重置
		if SELF.insted :
			SELF.inst.hide()

	@classmethod
	def onEvent( SELF, evtMacro, *args) :
		SELF.__triggers[ evtMacro ]( *args )

	@classmethod
	def registerEvents( SELF ) :
		SELF.__triggers[ "EVT_ON_ROLE_LEAVE_WORLD" ] = SELF.__onLeaveWorld
		for key in SELF.__triggers :
			ECenter.registerEvent( key, SELF )

BuyConfirmBox.registerEvents()