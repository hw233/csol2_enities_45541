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
		self.__trapID = BigWorld.player().addTrapExt( csconst.COMMUNICATE_DISTANCE, self.__onEntitiesTrapThrough )#�򿪴��ں�Ϊ�����ӶԻ�����

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
		if len( text ) > 14 :	# ������ƺϷ��Լ��
			# "���ֳ��Ȳ��ܳ��� 14 ���ֽ�"
			showAutoHideMessage( 3.0, 0x0701, mbmsgs[0x0c22] )
			return False
		elif text == "" :
			# "������İ������Ч�����������롣"
			showAutoHideMessage( 3.0, 0x0702, mbmsgs[0x0c22] )
			return False
		elif not rds.wordsProfanity.isPureString( text ) :
			# "���Ʋ��Ϸ���"
			showAutoHideMessage( 3.0, 0x0703, mbmsgs[0x0c22] )
			return False
		elif self.__isHasDigit( text ):#��������
			# "�������ֻ���ɺ��ֺ���ĸ��ɣ�"
			showAutoHideMessage( 3.0, 0x0704, mbmsgs[0x0c22] )
			return False
		elif rds.wordsProfanity.searchNameProfanity( text ) is not None :
			# "����������н��ôʻ�!"
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
		ȡ����ť�����
		"""
		self.pressedOK_ = False
		self.hide()

	def show( self ):
		InputBox.show( self, labelGather.getText( "RelationShip:TongPanel", "nameChange" ), lambda a,b:None, None )
