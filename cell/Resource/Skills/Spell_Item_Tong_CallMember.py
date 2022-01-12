# -*- coding: gb18030 -*-


import BigWorld
import Math
import random
import math
import csstatus
import csconst

from Spell_Item import Spell_Item
from bwdebug import *

class Spell_Item_Tong_CallMember( Spell_Item ):
	"""
	�ٻ����ߣ�������Ա���͹���
	"""
	def init( self, dict ):
		"""
		��ʼ��
		"""
		Spell_Item.init( self, dict )
		self.limitLevel = int( dict["param1"] )				# ֻ��ʹ����ҵȼ�����x���İ���Ա�����յ���ʾ
		self.showMessage = int( dict["param2"] )				# ��ʾ�������1Ϊ�������ݣ�2Ϊ������ݣ�3Ϊ...
		
		
	def useableCheck( self, caster, target ):
		"""
		У�鼼���Ƿ���ʹ��
		"""
		if caster.tong_dbID == 0:
			caster.statusMessage( csstatus.SKILL_ITEM_ADD_NOT_TONG_ATTRIBUTE )
			return False
		
		return Spell_Item.useableCheck( self, caster, target )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		userDBID = receiver.databaseID
		tongOnlineMember = receiver.getTongOnlineMember()							# ��ȡ������߳�Ա
		spaceName = receiver.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )	# ��ȡʩ�������ڵĵ�ͼ��
		if len( tongOnlineMember ) == 0:				# ������û�����߳�Ա
			return
		lineNumber = receiver.getCurrentSpaceLineNumber()
		tong = receiver.tong_getTongEntity( receiver.tong_dbID )
		if tong:
			tong.infoCallMember( userDBID, lineNumber, spaceName, receiver.position, receiver.direction, self.limitLevel, self.showMessage )
	#	Spell_Item.receive( self, caster, receiver )
