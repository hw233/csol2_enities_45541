# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
from guis import *
import csconst
from LabelGather import labelGather
from guis.tooluis.inputbox.InputBox import InputBox
from config.client.msgboxtexts import Datas as mbmsgs

class ChangeNameBox( InputBox ):
	"""
	"""
	def __init__( self, npcID ):
		"""
		"""
		InputBox.__init__( self )
		self.chatNPCID = npcID
		self.pyBtnOk_.onLClick.bind( self.__onOk )
		self.pyBtnCancel_.onLClick.bind( self.__onCancel )
		self.__trapID = BigWorld.player().addTrapExt( csconst.COMMUNICATE_DISTANCE, self.__onEntitiesTrapThrough )#打开窗口后为玩家添加对话陷阱

	def __onEntitiesTrapThrough( self, entitiesInTrap ):
		"""
		"""
		try:
			npcEntity = BigWorld.entities[self.chatNPCID]
		except KeyError:
			self.hide()
		else:
			if not npcEntity in entitiesInTrap:
				self.hide()

	def hide( self ):
		"""
		"""
		self.__delTrap()
		InputBox.hide( self )

	def __delTrap( self ):
		if self.__trapID :
			BigWorld.player().delTrap( self.__trapID )
			self.__trapID = 0

	def canChangeName( self ) :
		player = BigWorld.player()
		text = self.pyTextBox_.text
		if len( text ) > 14 :	# 帮会名称合法性检测
			# "名字长度不能超过 14 个字节"
			showAutoHideMessage( 3.0, 0x0701, mbmsgs[0x0c22] )
			return False
		elif text == "" :
			# "您输入的帮会名无效，请重新输入。"
			showAutoHideMessage( 3.0, 0x0702, mbmsgs[0x0c22] )
			return False
		elif not rds.wordsProfanity.isPureString( text ) :
			# "名称不合法！"
			showAutoHideMessage( 3.0, 0x0703, mbmsgs[0x0c22] )
			return False
		elif self.__isHasDigit( text ):#含有数字
			# "帮会名称只能由汉字和字母组成！"
			showAutoHideMessage( 3.0, 0x0704, mbmsgs[0x0c22] )
			return False
		elif rds.wordsProfanity.searchNameProfanity( text ) is not None :
			# "输入的名称有禁用词汇!"
			showAutoHideMessage( 3.0, 0x0705, mbmsgs[0x0c22] )
			return False
		self.pressedOK_ = True
		return True

	def __isHasDigit( self, text ):
		for letter in text:
			if letter.isdigit():
				return True
			else:
				continue
		return False

	def __onOk( self ):
		"""
		"""
		if self.canChangeName():
			BigWorld.player().cell.requestChangeTongName( self.pyTextBox_.text )
		self.pressedOK_ = True
		self.hide()

	def __onCancel( self ) :
		"""
		取消按钮被点击
		"""
		self.pressedOK_ = False
		self.hide()

	def show( self ):
		InputBox.show( self, labelGather.getText( "RelationShip:TongPanel", "nameChange" ), lambda a,b:None, None )
