# -*- coding: gb18030 -*-
#
# $Id: Buff_23002.py,v 1.2 2008-02-28 08:25:56 kebiao Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Function import newUID
from Buff_Shield import Buff_Shield

class Buff_23002( Buff_Shield ):
	"""
	example:���ܵ��ķ����˺�����x%�ı��ʣ��۳�����ֵ�����ת��y���˺���ת����󣬻�����ʧ
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Shield.__init__( self )
		self._p1 = 0 # ��x%�ı���
		self._p2 = 0 # ���ת��y���˺�
		self._param = 0
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Shield.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  / 100.0	
		self._p2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 ) 	
		
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
		if damageType != csdefine.DAMAGE_TYPE_MAGIC:
			return damage
			
		if self.isDisabled( receiver ):
			return damage
			
		val = damage * self._p1

		if receiver.MP < val or self._param["p2"] < val:
			self._param["disabled"] = True
			return damage

		# ��������ж�real ������ܻᱻ����2�Σ� ���忴shieldConsume����
		if receiver.isReal():	
			self._param["p2"] -= val
			receiver.setMP( int( receiver.MP - val ) )

		return 0

	def isDisabled( self, receiver ):
		"""
		virtual method.
		�����Ƿ�ʧЧ
		@param receiver: ������
		"""
		return self._param.has_key( "disabled" )#���ڻ����Ǳ���̬���������� ��˿����ж���������
		
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
		Buff_Shield.doBegin( self, receiver, buffData )
		#����createFromDict�����˸�������Զ�p1�ǲ��ᱻ ����ʵ�����ı�� ��˲���Ҫ���p1
		buffData[ "skill" ] = self.createFromDict( { "param":{ "p2":self._p2 } } )
		receiver.appendShield( buffData[ "skill" ] )
		
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
		Buff_Shield.doReload( self, receiver, buffData )
		buffData[ "skill" ] = self.createFromDict( { "param":{ "p2":self._p2 } } )
		receiver.appendShield( buffData[ "skill" ] )
		
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Shield.doEnd( self, receiver, buffData )
		receiver.removeShield( buffData[ "skill" ].getUID() )

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
		obj = Buff_23002()
		obj.__dict__.update( self.__dict__ )
		obj._param = data["param"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )		
		else:
			obj.setUID( data[ "uid" ] )		
		return obj

#
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/12/20 03:07:54  kebiao
# no message
#
# 
#