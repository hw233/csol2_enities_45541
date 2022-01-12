# -*- coding: gb18030 -*-
#
# $Id: Buff_1003.py,v 1.2 2007-12-13 04:59:55 huangyongwei Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_22007( Buff_Normal ):
	"""
	�չ�ԡbuff�����ϲ��ϼ������Ѫֵ����Ȼ����ѭһ�����ɣ�
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._p1 = "lv*2"
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = ( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else "" ) .replace(" ","")			# ���ÿ��Ҫ������Ѫ�ļ��㹫ʽ
		self._hpVal = int( self._p1[ 3:len( self._p1 ) ] )
		self._hpOpt = self._p1[ 2:3 ]
	
	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч����ʼ�Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.setTemp( "forbid_revert_hp", False )	# ������������ӽ�ֹ��Ѫ�ı��
	
	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�����¼��صĴ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.setTemp( "forbid_revert_hp", False )	# ������������ӽ�ֹ��Ѫ�ı��
	
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.removeTemp( "forbid_revert_hp" )	# �����������Ͻ�ֹ��Ѫ�ı��
	
	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		����buff����ʾbuff��ÿһ������ʱӦ����ʲô��

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL�������������򷵻�True�����򷵻�False
		@rtype:  BOOL
		"""
		decreaseHP = 0
		
		if receiver.queryTemp( "has_suntan_oil", 0 ) != 1:	# ������û��Ϳ��ɹ˪
			decreaseHP = self.getDecHP( receiver.level, self._hpOpt, self._hpVal )
			
			if receiver.queryTemp( "jthl_hp_rate", 0.0 ) > 0:	# �����ɫ�о��κ���buff
				# ���κ��˿۳���Ѫ��Ϊ����ֵ��jthl_hp_rate��
				decreaseHP += decreaseHP * receiver.queryTemp( "jthl_hp_rate", 0.0 )
		
		if decreaseHP > 0:	# �����ɫ��Ѫ��
			receiver.addHP ( 0 - decreaseHP )
			self.onPlayerAddHP( receiver, decreaseHP )
			
		return Buff_Normal.doLoop( self, receiver, buffData )
		
	def onPlayerAddHP( self, player, decreaseHP ):
		"""
		�ͻ��˱��ּ�Ѫ�����ж�����Ƿ�����
		"""
		player.receiveSpell( 0, self.getID(), csdefine.DAMAGE_TYPE_VOID, decreaseHP, 0 )
		if player.HP <= 0:
			player.onInSunBathingDead()
	
	def getDecHP( self, level, opration, value ):
		"""
		���ݹ�ʽ��ü��ٵ�Ѫ��
		"""
		return level * value