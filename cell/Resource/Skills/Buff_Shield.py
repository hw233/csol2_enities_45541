# -*- coding: gb18030 -*-
#
# $Id: Buff_Shield.py,v 1.9 2007-11-30 07:10:38 kebiao Exp $

"""
������Ч��
"""

import BigWorld
import csdefine
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_Shield( Buff_Normal ):
	"""
	���ܻ���
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._shieldType = csdefine.SHIELD_TYPE_VOID
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )

	def getShieldType( self ):
		"""
		virtual method.
		��ȡ���ܵ�����
		"""
		return self._shieldType
	
	def isDisabled( self, receiver ):
		"""
		virtual method.
		�����Ƿ�ʧЧ
		@param receiver: ������
		"""
		return True
		
	def doShield( self, receiver, damageType, damage ):
		"""
		virtual method.
		ִ�л���������  �磺������ת���˺�ΪMP 
		ע��: �˽ӿڲ����ֶ�ɾ���û���
		@param receiver: ������
		@param damageType: �˺�����
		@param damage : �����˺�ֵ
		@rtype: ���ر���������˺�ֵ
		"""
		if self.isDisabled( receiver ):
			return damage
		return 0
#
# $Log: not supported by cvs2svn $
# 
#