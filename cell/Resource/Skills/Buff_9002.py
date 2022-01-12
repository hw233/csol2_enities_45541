# -*- coding: gb18030 -*-
#
# $Id: Buff_9002.py,v 1.3 2008-05-28 05:59:25 kebiao Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import csdefine
from bwdebug import *
from SpellBase import *
from Function import newUID
from Buff_Normal import Buff_Normal

class Buff_9002( Buff_Normal ):
	"""
	example:
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._param = { "p1" : 3 }#������

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
		receiver.say( "BUFF3---(%d)" % self._param[ "p1" ] )
		return Buff_Normal.doLoop( self, receiver, buffData )

	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{"id":self._id, "param":None}������ʾ�޶�̬���ݡ�

		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		"""
		return { "param" : self._param }

	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�

		@type data: dict
		"""
		obj = Buff_9002()
		obj.__dict__.update( self.__dict__ )
		obj._param = data["param"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj
#
# $Log: not supported by cvs2svn $
# Revision 1.2  2007/11/30 08:45:13  kebiao
# csstatus.BUFF_INTERRUPT
# TO��
# csdefine.BUFF_INTERRUPT
#
# Revision 1.1  2007/11/30 07:11:50  kebiao
# no message
#
#
#