# -*- coding: gb18030 -*-

"""
������Ч��
"""
import copy

import BigWorld
import csdefine
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
from Function import newUID
from Domain_Fight import g_fightMgr

class Buff_21003( Buff_Normal ):
	"""
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._param = { "p1" : 0, "p2" : 1 } #p1������, p2�˺�����

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		param1 = dict[ "Param1" ].split( ";" )
		self._param[ "p1" ] = int( param1[0] ) # �˺�ֵ
		self._damageMultiple = float( param1[1] ) # �˺�����
		self._radius = float( dict[ "Param2" ] )
		self._maxCount = int( dict[ "Param3" ] )
		
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
		id = buffData["caster"]
		if BigWorld.entities.has_key( id ):
			caster = BigWorld.entities[ id ]
			p = self.initPhysicsDotDamage( caster, receiver, self._param[ "p1" ] ) # ת���ɼ��ܵ��˺�ֵ
			buffData[ "skill" ] = self.createFromDict( { "param":{ "p1":p } } )

			
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
		maxCount = self._maxCount
		entityList = receiver.entitiesInRangeExt( self._radius, None, receiver.position )	
		for e in entityList:
			if receiver.queryRelation( e ) == csdefine.RELATION_ANTAGONIZE:
				damage = self._damageMultiple * self.calcDotDamage( receiver, e, csdefine.DAMAGE_TYPE_MAGIC, int( self._param[ "p1" ] ) )
				
				g_fightMgr.buildEnemyRelation( e, receiver )
				e.receiveSpell( receiver.id, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage, 0 )
				e.receiveDamage( receiver.id, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage )
				maxCount -= 1
			
				if maxCount <= 0:
					break
					
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
		obj = Buff_21003()
		obj.__dict__.update( self.__dict__ )
		obj._param = data["param"]
		return obj
