# -*- coding: gb18030 -*-
#
# ��ұ���ϵͳ	2009-01-10 SongPeifang & LinQing
#

from bwdebug import *
import BigWorld
import csdefine
import csstatus
import Const
import csconst

class RoleChangeBody:
	"""
	��ұ���ϵͳ
	"""
	def __init__( self ):
		"""
		"""
		self.currentModelNumber = ""
		self.currentModelScale = 1.0

	def canChangeBody( self ):
		"""
		�������Ƿ��������
		"""
		if self.onFengQi: return False
		return True

	def begin_body_changing( self, modelNumber, modelScale ):
		"""
		Define method.
		��ұ���Ľӿ�
		"""
		if not self.canChangeBody():
			return
		# ���ñ���ģ�ͱ��
		self.currentModelNumber = modelNumber
		self.currentModelScale = modelScale
		if self.queryTemp( "BODY_CHANGE_NOT_CHANGE_STATE", False ):	# �в��ı�״̬���
			return
		self.changeState( csdefine.ENTITY_STATE_CHANGING )	# ���ñ���״̬

	def enterCopyBeforeNirvanaBodyChanging( self ):
		self.retractVehicle( self.id )
		self.currentModelNumber = Const.JUQING_MODELNUM_MAPS.get( self.getGender() | self.getClass(), "" )
		self.currentModelScale = csconst.MATCHING_DICT[self.getGender()][self.getClass()]

	def enterCopyYeZhanFengQiBodyChanging( self ):
		"""
		Define method.
		ҹս���ܱ���ģ��
		"""
		self.retractVehicle( self.id )	# �����
		if self.pcg_getActPet():		# �ջس���
			self.pcg_withdrawPet( self.id )
		self.currentModelNumber = Const.YEZHAN_MODELNUM_MAPS.get( self.getGender() | self.getClass(), "" )
		self.currentModelScale = csconst.MATCHING_DICT[self.getGender()][self.getClass()]

	def getCurrentBodyNumber( self ):
		"""
		��õ�ǰģ����
		"""
		return self.currentModelNumber

	def setCurrentBodyNumber( self, modelNumber ):
		"""
		���õ�ǰģ����
		"""
		self.currentModelNumber = modelNumber

	def end_body_changing( self, srcEntityID, bodyNumer ):
		"""
		Define method.
		���ȡ������Ľӿ�
		"""
		if srcEntityID != self.id:
			HACK_MSG( "�Ƿ�������." )
			return
		if not self.canChangeBody():
			return
		if self.attrIntonateSkill:		# ���������������Ҫȡ������
			reason = csstatus.SKILL_PLAYER_STOP_BODY_CHANGING
			if self.currentModelNumber == "fishing":
				reason = csstatus.SKILL_PLAYER_STOP_FISHING
			self.interruptSpell( reason )
		if self.queryTemp( "SAME_TYPE_BUFF_REPLACE", False ) and self.queryTemp( "ROLE_BODY_BUFF_END", False ):  # ͬ����buff�滻
			return
		self.currentModelNumber = bodyNumer
		
		if self.getState() == csdefine.ENTITY_STATE_CHANGING and not self.queryTemp( "BODY_CHANGE_NOT_CHANGE_STATE", False ): # û�в��ı�״̬���
			self.changeState( csdefine.ENTITY_STATE_FREE )

	def remove_bc_cards( self, cardIDList ):
		"""
		define method
		û��������ϵı���Ƭ
		"""
		for i in cardIDList:
			item = self.findItemFromNKCK_( int(i) )	# �ж��Ƿ��Ѿ���ֽ����
			if item != None:
				self.removeItem_( item.order, reason = csdefine.DELETE_ITEM_REMOVE_BC_CARDS )		# �Ƴ���������ϵ�ֽ��