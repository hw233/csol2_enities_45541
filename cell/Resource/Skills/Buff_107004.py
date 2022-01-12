# -*- coding: gb18030 -*-
#
# $Id: Buff_107004.py,v 1.7 2008-08-11 07:55:59 kebiao Exp $

"""
������Ч��
"""

import BigWorld
import csdefine
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_107004( Buff_Normal ):
	"""
	example:ʧȥ����ֵA	DEBUFF	��������ʧ����	��һ����ֵ����ʧȥ������
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0 # ������hPֵ 

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  / ( self._persistent / self._loopSpeed ) )	
			
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
		damage = self.calcDotDamage( receiver, receiver, csdefine.DAMAGE_TYPE_VOID, int( self._p1 ) )
		receiver.receiveDamage( buffData["caster"], self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_VOID, damage )
		receiver.receiveSpell( buffData["caster"], self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_VOID, damage, 0 ) 
		return Buff_Normal.doLoop( self, receiver, buffData )

#
# $Log: not supported by cvs2svn $
# Revision 1.6  2008/04/10 04:09:08  kebiao
# ��Ϊ�ڽ����˺�֮ǰ֪ͨ�ͻ��˽��ܼ��ܴ���
#
# Revision 1.5  2008/04/10 03:25:50  kebiao
# modify to receiveSpell pertinent.
#
# Revision 1.4  2008/03/31 09:04:02  kebiao
# �޸�receiveDamage��֪ͨ�ͻ��˽���ĳ���ܽ���ֿ�
# ����ͨ��receiveSpell֪ͨ�ͻ���ȥ���֣�֧�ָ����ܲ�ͬ�ı���
#
# Revision 1.3  2007/12/21 08:43:14  kebiao
# no message
#
# Revision 1.2  2007/12/21 07:28:00  kebiao
# no message
#
# Revision 1.1  2007/11/30 07:11:50  kebiao
# no message
#
# 
#