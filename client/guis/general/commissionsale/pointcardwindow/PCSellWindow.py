# -*- coding: gb18030 -*-

# Implement point card buy window.
# By ganjinxing 2009-11-18

from guis import *
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.controls.TextBox import TextBox
from guis.controls.TabSwitcher import TabSwitcher
from guis.tooluis.CSRichText import CSRichText
from config.client.msgboxtexts import Datas as mbmsgs
from LabelGather import labelGather
import GUIFacade
import csconst

class PCSellWindow( Window ) :

	def __init__( self ) :
		wnd = GUI.load( "guis/general/commissionsale/pointcard/sellwnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )

		self.__pyMsgBox = None
		self.__trapID = None
		self.__trapNPCID = -1
		self.__initialize( wnd )
		self.__triggers = {}
		self.__registerTriggers()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_SHOW_POINT_CARD_SELL_WINDOW"] = self.__onShow

		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __initialize( self, wnd ) :
		self.__pyOKBtn = Button( wnd.okBtn )
		self.__pyOKBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyOKBtn.onLClick.bind( self.__onSell )
		self.__pyOKBtn.isOffsetText = True

		self.__pyCancelBtn = Button( wnd.cancelBtn )
		self.__pyCancelBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyCancelBtn.onLClick.bind( self.hide )
		self.__pyCancelBtn.isOffsetText = True

		self.__pyNumBox = TextBox( wnd.ipbox_number.iBox )
		self.__pyNumBox.maxLength = 20

		self.__pyPwdBox = TextBox( wnd.ipbox_pwd.iBox )
		self.__pyPwdBox.inputMode = InputMode.PASSWORD

		self.__pyGoldBox = TextBox( wnd.ipbox_gold.iBox )
		self.__pyGoldBox.inputMode = InputMode.INTEGER
		self.__pyGoldBox.onTabIn.bind( self.__onBoxTabIn )
		self.__pyGoldBox.filterChars = ['-', '+']

		self.__pySilverBox = TextBox( wnd.ipbox_silver.iBox )
		self.__pySilverBox.inputMode = InputMode.INTEGER
		self.__pySilverBox.onTabIn.bind( self.__onBoxTabIn )
		self.__pySilverBox.filterChars = ['-', '+']
		self.__pySilverBox.maxLength = 2

		self.__pyCoinBox = TextBox( wnd.ipbox_coin.iBox )
		self.__pyCoinBox.inputMode = InputMode.INTEGER
		self.__pyCoinBox.onTabIn.bind( self.__onBoxTabIn )
		self.__pyCoinBox.filterChars = ['-', '+']
		self.__pyCoinBox.maxLength = 2

		self.__tabSwt = TabSwitcher( [ self.__pyNumBox, self.__pyPwdBox,
										self.__pyGoldBox, self.__pySilverBox,
										self.__pyCoinBox,
									 ] )

		self.__pyExplanation = CSRichText( wnd.rtExp )
		self.__pyExplanation.text = labelGather.getText( "commissionsale:PCSellWindow", "explanation" )
		self.__pyPrompt = CSRichText( wnd.rtPrompt )
		self.__pyPrompt.text = labelGather.getText( "commissionsale:PCSellWindow", "prompt" )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyOKBtn, "commissionsale:PCSellWindow", "btnOK" )
		labelGather.setPyBgLabel( self.__pyCancelBtn, "commissionsale:PCSellWindow", "btnCancel" )
		labelGather.setLabel( wnd.lbTitle, "commissionsale:PCSellWindow", "lbTitle" )
		labelGather.setLabel( wnd.stCardNumber, "commissionsale:PCSellWindow", "stCardNo" )
		labelGather.setLabel( wnd.stCardPsw, "commissionsale:PCSellWindow", "stCardPsw" )
		labelGather.setLabel( wnd.stCardPrice, "commissionsale:PCSellWindow", "stCardPrice" )
		labelGather.setLabel( wnd.bg_panel.resumeTitle.lbText, "commissionsale:PCSellWindow", "stResume" )
		labelGather.setLabel( wnd.bg_panel.inputTitle.lbText, "commissionsale:PCSellWindow", "stInputTitle")

	def __onBoxTabIn( self, pyBox ) :
		pyBox.selectAll()

	def __onSell( self ) :
		if self.__checkCardNum() :
			cardNum = self.__pyNumBox.text.strip()
			password = self.__pyPwdBox.text.strip()
			if password == "" :
				# "密码不能为空！"
				self.__showMessage( mbmsgs[0x02e1] )
				return
			gold = self.__pyGoldBox.text.strip()
			silver = self.__pySilverBox.text.strip()
			coin = self.__pyCoinBox.text.strip()
			price = ( gold != "" and ( int( gold ), ) or ( 0, ) )[-1] * 10000
			price += ( silver != "" and ( int( silver ), ) or ( 0, ) )[-1] * 100
			price += ( coin != "" and ( int( coin ), ) or ( 0, ) )[-1]
			if price == 0 :
				# "点卡未定价！"
				self.__showMessage( mbmsgs[0x02e2] )
			else :
				BigWorld.player().cell.sellPointCard( cardNum,
													password,
													labelGather.getText( "commissionsale:PCSellWindow", "serverName" ),
													price )
		else :
			# "您输入的卡号不正确，请核实后再输入！"
			self.__showMessage( mbmsgs[0x02e3] )

	# -------------------------------------------------
	def __addTrap( self ) :
		self.__delTrap()
		player = BigWorld.player()
		distance = csconst.COMMUNICATE_DISTANCE
		if hasattr( self.trapNPC, "getRoleAndNpcSpeakDistance" ):
			distance = self.trapNPC.getRoleAndNpcSpeakDistance() + 0.5		# +0.5 避免陷阱大小和对话距离相等而导致在陷阱边缘对话时对话框会一闪消失的问题。
		self.__trapID = BigWorld.addPot(self.trapNPC.matrix,distance, self.__onEntitiesTrapThrough )	# 打开窗口后为玩家添加对话陷阱。

	def __delTrap( self ) :
		if self.__trapID is not None :
			BigWorld.delPot( self.__trapID )						# 删除玩家的对话陷阱
			self.__trapID = None

	def __onEntitiesTrapThrough( self, isEnter,handle ):
		if not isEnter:								# 如果NPC离开玩家对话陷阱
			self.hide()														# 隐藏当前与NPC对话窗口

	def __checkCardNum( self ):
		"""
		#处理简单的点卡规则判定
		简单规则：
			20个字母，前4个字母为haaa,第5个字母代表点卡面值，6-20随机生成
			字母代表的点卡面值为：
			E       10.0 光宇10元冲值卡(带矩阵)

			F       30.0 光宇30元冲值卡(带矩阵)

			B       10.0 光宇10元冲值卡

			D      30.0 光宇30元冲值卡

			P       10.0 声讯10元冲值卡

		@return  (bool， value)
			1.是否有效
			2.卡的数值
		"""
		valueDict = { 'e' 	: "10",
				'f'	: "30",
				'b'	: "10",
				'd'	: "30",
				'p'	: "10",
				}

		cardNum = self.__pyNumBox.text.strip().lower()

		if len( cardNum ) != 20:
			return False

		if cardNum[0:4]  != "haaa":
			return False

		if cardNum[4] not in "efbdp":
			return False

		return True

	def __resetText( self ) :
		self.__pyNumBox.text = ""
		self.__pyPwdBox.text = ""
		self.__pyGoldBox.text = ""
		self.__pySilverBox.text = ""
		self.__pyCoinBox.text = ""

	def __showMessage( self, msg ) :
		def query( res ) :
			self.__pyMsgBox = None
		if self.__pyMsgBox is None :
			self.__pyMsgBox = showMessage( msg, "", MB_OK, query, self, Define.GST_IN_WORLD )
		else :
			self.__pyMsgBox.show( msg, "", query, self, Define.GST_IN_WORLD )

	def __onShow( self ) :
		if not self.visible :
			self.__trapNPCID = GUIFacade.getGossipTargetID()
			self.__addTrap()
			self.show()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self ) :
		Window.show( self )
		self.__pyNumBox.tabStop = True

	def hide( self ) :
		self.__delTrap()
		self.__resetText()
		Window.hide( self )

	def onLeaveWorld( self ) :
		self.hide()

	def onEvent( self, evtMacro, *args ) :
		"""
		"""
		self.__triggers[evtMacro]( *args )


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getTrapNPC( self ) :
		return BigWorld.entities.get( self.__trapNPCID, None )

	trapNPC = property( _getTrapNPC )