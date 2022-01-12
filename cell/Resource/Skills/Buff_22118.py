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
from Function import newUID
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_22118( Buff_Normal ):
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
		self._p1 = float( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0.0 )

	def getPercent( self ):
		"""
		��ȡ����
		"""
		return self._p1

	def updatePercent( self, val ):
		self._p1 = val

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

		if receiver.getState() == csdefine.ENTITY_STATE_DEAD:
			return

		buffs = receiver.findBuffsByBuffID( self._buffID )
		#�ж��Ƿ�����ͬ��buff
		if len( buffs ) > 0:
			# �Ѵ�����ͬ���͵�buff
			self.doAppend( receiver, buffs[0] )
		else:
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
		if sk.getPercent() == self.getPercent():
			buffdata["persistent"] += self._persistent
		elif sk.getPercent() < self.getPercent():
			buffdata["skill"].updatePercent( self.getPercent() )
			#�߱���ʱ�� + �ͱ���ʱ��*�ͱ��ʱ���/�߱��ʱ���
			sk_persistent = int( buffdata["persistent"] - time.time() )
			val = self._persistent + sk_persistent * sk.getPercent() / self.getPercent()
			buffdata["persistent"] = val + time.time()
			receiver.multExp = self.getPercent()
			receiver.potential_percent = self.getPercent()
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
		buffData[ "skill" ] = self.createFromDict( { "param": self.getPercent() } )
		receiver.multExp += self.getPercent()
		receiver.potential_percent += self.getPercent()

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
		val = buffData[ "skill" ].getPercent()
		receiver.multExp += val
		receiver.potential_percent += val

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		receiver.multExp -= self.getPercent()
		receiver.potential_percent -= self.getPercent()
		Buff_Normal.doEnd( self, receiver, buffData )

	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{ "param": None }������ʾ�޶�̬���ݡ�

		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		"""
		return {  "param" : self.getPercent() }

	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�

		@type data: dict
		"""
		obj = Buff_22118()
		obj.__dict__.update( self.__dict__ )
		obj.updatePercent( data["param"] )
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj