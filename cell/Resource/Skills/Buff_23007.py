# -*- coding: gb18030 -*-
#

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
from Buff_Shield import Buff_Shield
from Function import newUID
"""
"""

class Buff_23007( Buff_Shield ):
	"""
	"������Buff_23007������ʹ�����е���ͨBUFF�ű���
	��ɫ���ڴ�DEBUFFʱ�����ܵ����κ��˺�������һ���ٷֱ�A������ʣ�ಿ�ֵ�һ���ٷֱ�B�˺�ת��ʩ���ߡ�ʩ�������ܵ����˺�Ҳ�ή�Ͱٷֱ�A��������ת��ʣ�ಿ�֣������յ�����ת����˺����پ����ٷֱ�A��������
	��Ѱ��ʩ����ʱ��ָ���ķ�Χ��Ѱ�ң���Ѱ�Ҳ���ʩ���ߣ��ٷֱ�B���˺���ת����"
	"""
	def __init__( self ):
		"""
		"""
		Buff_Shield.__init__( self )
		self._p1 = 0
		self._p2 = 0
		self._damage = 0
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Shield.init( self, dict )
		self._p1 = int( dict[ "Param1" ] ) / 100.0
		self._p2 = int( dict[ "Param2" ] ) / 100.0
		self._radius = float( dict[ "Param3" ] )
		
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
		val = damage * self._p1
		dval = ( damage - val ) * self._p2
		self._damage += dval
		return dval
		
	def isDisabled( self, receiver ):
		"""
		virtual method.
		�����Ƿ�ʧЧ
		@param receiver: ������
		"""
		return False
		
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
		self._damage = 0
		buffData[ "skill" ] = self.createFromDict( self.addToDict() )
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
		if self._damage > 0:
			caster = BigWorld.entities.get( buffData[ "caster" ] )
			if caster and caster != receiver and caster.position.flatDistTo( receiver.position ) <= self._radius:
				caster.receiveSpell( 0, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF, self._damage, 0 )
				caster.receiveDamage( 0, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF, self._damage )
			else:
				receiver.receiveSpell( 0, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF, self._damage, 0 )
				receiver.receiveDamage( 0, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF, self._damage )
				
			self._damage = 0
		return Buff_Normal.doLoop( self, receiver, buffData )
		
	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{"id":self._id, "param":None}������ʾ�޶�̬���ݡ�

		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		"""
		return { "param" : self._damage }

	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�

		@type data: dict
		"""
		obj = Buff_23007()
		obj.__dict__.update( self.__dict__ )

		obj._damage = data["param"]

		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj