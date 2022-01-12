# -*- coding: gb18030 -*-
#
# $Id: Buff_22001.py,v 1.2 2008-05-19 08:01:12 kebiao Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Function import newUID
from Buff_Normal import Buff_Normal
import time
import math

class Buff_22119( Buff_Normal ):
	"""
	example: �౶���齱�� ɱ��ʱ�������������õľ�����Ǳ�����һ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )
		self.isCharge = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )

	def getPercent( self ):
		"""
		��ȡ����
		"""
		return self._p1

	def updatePercent( self, val ):
		self._p1 = val

	def setRoleExpRecord( self, role ):
		"""
		���ý�ɫ�����¼
		"""
		DEBUG_MSG( "query rewardExpHour:%i" % role.queryTemp( "rewardExpHour", 0 ) )

		hour = role.popTemp( "rewardExpHour", 0 )
		if hour > 0 and self.isCharge == 0:
			role.takeExpRecord[ "week" ] = time.localtime()[6]
			role.takeExpRecord[ "remainTime" ] = role.takeExpRecord[ "remainTime" ] - hour
			role.takeExpRecord[ "lastTime" ] = time.time()

	def receive( self, caster, receiver ):
		"""
		���ڸ�Ŀ��ʩ��һ��buff�����е�buff�Ľ��ն�����ͨ���˽ӿڣ�
		�˽ӿڱ����жϽ������Ƿ�ΪrealEntity��
		����������Ҫͨ��receiver.receiveOnReal()�ӿڴ���

		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ��ߣ�None��ʾ������
		@type  receiver: Entity
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( casterID, self )
			return

		buffs = receiver.findBuffsByBuffID( self._buffID )

		#�ж��Ƿ�����ͬ��buff
		if len( buffs ) > 0:
			# �Ѵ�����ͬ���͵�buff
			self.doAppend( receiver, buffs[0] )
		else:
			sexp = str( self.getPercent() ) + "%"
			receiver.statusMessage( csstatus.TAKE_EXP_SUCCESS1, receiver.queryTemp( "rewardExpHour", 0 ), sexp )
			self.setRoleExpRecord( receiver )
			receiver.addBuff( self.getNewBuffData( caster, receiver ) )

	def doAppend( self, receiver, buffIndex ):
		"""
		Virtual method.
		��һ�������Ѿ����ڵ�ͬ����BUFF����׷�Ӳ���
		�����BUFF����׷��ʲô�ɼ̳��߾���
		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffs: �������ͬ���͵�BUFF����attrbuffs��λ��,BUFFDAT ����ͨ�� receiver.getBuff( buffIndex ) ��ȡ
		"""
		buffdata = receiver.getBuff( buffIndex )
		sk = buffdata["skill"]
		sexp = str( self.getPercent() ) + "%"
		sexp1 = str( sk.getPercent() ) + "%"
		isappend = 0

		if sk.getPercent() == self.getPercent():
			# ��ѵ������շѵ���ֻ����һ��
			if sk.isCharge != self.isCharge:
				if self.isCharge:
					receiver.statusMessage( csstatus.TAKE_EXP_BUFF_ITEM_NOUSE, sexp1 )
				else:
					receiver.statusMessage( csstatus.TAKE_EXP_BUFF_EXIST1, sexp1 )
				return
			buffdata["persistent"] += self._persistent
		elif sk.getPercent() < self.getPercent():
			# �����ǰҪ��ӵĸ߱���BUFF����ѵģ� ���ϵĵױ������շѵ��ߣ� ��������
			if sk.isCharge and not self.isCharge:
				receiver.statusMessage( csstatus.TAKE_EXP_BUFF_ITEM_NOUSE1, sexp1 )
				return

			#�߱���ʱ�� + �ͱ���ʱ��*�ͱ��ʱ���/�߱��ʱ���
			sk_persistent = int( ( buffdata["persistent"] ) - time.time() )
			val = self._persistent + sk_persistent * sk.getPercent() / self.getPercent()
			isappend = val
			buffdata["persistent"] = ( val + time.time() )
			val = self.getPercent() / 100.0
			receiver.multExp = val
			receiver.potential_percent = val
			buffdata["skill"].isCharge = self.isCharge
			buffdata["skill"].updatePercent( self.getPercent() )
		else:
			if self.isCharge:
				receiver.statusMessage( csstatus.TAKE_EXP_BUFF_ITEM_NOUSE, sexp1 )
			else:
				receiver.statusMessage( csstatus.TAKE_EXP_BUFF_EXIST1, sexp1 )
			return

		if isappend == 0:
			receiver.statusMessage( csstatus.TAKE_EXP_SUCCESS1, receiver.queryTemp( "rewardExpHour", 0 ), sexp )
		else:
			receiver.statusMessage( csstatus.TAKE_EXP_SUCCESS3, math.ceil( isappend / 60.0 ), sexp )
		self.setRoleExpRecord( receiver )
		receiver.client.onUpdateBuffData( buffIndex, buffdata )

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
		buffData[ "skill" ] = self.createFromDict( { "param": { "p1" : self.getPercent(), "isCharge" : self.isCharge } } )
		val = self.getPercent() / 100.0
		receiver.vehicle_multExp += val

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
		val = buffData[ "skill" ].getPercent() / 100.0
		receiver.vehicle_multExp += val

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		val = self.getPercent() / 100.0
		receiver.vehicle_multExp -= val
		Buff_Normal.doEnd( self, receiver, buffData )

	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{ "param": None }������ʾ�޶�̬���ݡ�

		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		"""
		return { "param": { "p1" : self.getPercent(), "isCharge" : self.isCharge } }

	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�

		@type data: dict
		"""
		obj = Buff_22119()
		obj.__dict__.update( self.__dict__ )
		obj.updatePercent( data[ "param" ][ "p1" ] )
		obj.isCharge = data[ "param" ][ "isCharge" ]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj