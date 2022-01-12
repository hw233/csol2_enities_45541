# -*- coding: gb18030 -*-
#
# $Id: Buff_7001.py,v 1.6 2008-08-14 04:00:15 songpeifang Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_7001( Buff_Normal ):
	"""
	example:����ҩЧ	ÿ��ָ�����ֵ13�㡣
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._param = 0 #ÿ��ָ�����ֵ13�㡣 ��������ֵ104 ��Ҫ��

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._param = int( int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  / ( self._persistent / self._loopSpeed ) )	

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
		if not receiver.HP == receiver.HP_Max:
			m_addHp = receiver.addHP( self._param )	#�ȼ�����ϵĵ���  �ٷ��ͼ��ϵ���Ϣ hd
			SkillMessage.buff_CureHP( buffData, receiver, m_addHp )
			casterID = buffData["caster"]
			caster = BigWorld.entities.get( casterID )
			if caster:
				caster.doCasterOnCure( receiver, m_addHp )	#����Ŀ��ʱ����
				receiver.doReceiverOnCure( caster, m_addHp )   #������ʱ����
		return Buff_Normal.doLoop( self, receiver, buffData )

#
# $Log: not supported by cvs2svn $
# Revision 1.5  2008/02/13 08:45:54  kebiao
# ��������ʾ��Ϣ
#
# Revision 1.4  2008/01/31 07:06:53  kebiao
# ����������Ϣ
#
# Revision 1.3  2007/12/12 01:38:54  kebiao
# �޸�ƽ����ֵ������
#
# Revision 1.2  2007/12/03 02:46:00  kebiao
# �޸����Ʒ�ʽ ֱ��ʹ�ü���������
#
# Revision 1.1  2007/11/30 07:11:50  kebiao
# no message
#
#
#