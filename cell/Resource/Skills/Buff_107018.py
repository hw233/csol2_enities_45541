# -*- coding: gb18030 -*-
#
# $Id: $

"""
������Ч��
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
from Function import newUID
import csdefine
from Domain_Fight import g_fightMgr


class Buff_107018( Buff_Normal ):
	"""
	example:ʹĿ��ÿ2��һ��ֱ���˺�185(30��)/439(60��)�㣬����10�롣���Ŀ���ڴ˹�����������������Χ5�����10��Ŀ�����ÿ��494/1171��ֱ���˺���
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
		value = dict[ "Param1" ].split(",")
		self._p1 = int( value[0] )
		self._p2 = int( value[1] )
		
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
			p = self.initMagicDotDamage( caster, receiver, self._p1 )
			
			buff = self.createFromDict( { "param":{ "p1":p, "rid" : receiver.id, "casterID" : id } } )
			buffData[ "skill" ] = buff
			
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
		damage = self.calcDotDamage( receiver, receiver, csdefine.DAMAGE_TYPE_MAGIC, self._p1 )
		receiver.receiveSpell( buffData["caster"], self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage, 0 )
		receiver.receiveDamage( buffData["caster"], self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage )
		return Buff_Normal.doLoop( self, receiver, buffData )

	def cancelBuff( self, reasons ):
		"""
		virtual method.
		ȡ��һ��BUFF
		@param reasons: ȡ����ԭ��
		@rtype  : bool
		"""
		if not Buff_Normal.cancelBuff( self, reasons ):
			return False
		
		if csdefine.BUFF_INTERRUPT_ON_DIE in reasons:
			maxCount = self._maxCount
			receiver = BigWorld.entities.get( self._param[ "rid" ] )			
			casterID = self._param[ "casterID" ]			
			# ����Ѱ��һ��ʩ���ߣ�����Ҳ����Ͳ���ִ��AOE�˺� by mushuang
			caster = BigWorld.entities.get( casterID )
			if not caster: return True
			entityList = receiver.entitiesInRangeExt( self._radius, receiver.__class__.__name__, receiver.position )	
			for e in entityList:
				if caster.queryRelation( e ) != csdefine.RELATION_ANTAGONIZE: continue
				if e.effect_state & csdefine.EFFECT_STATE_INVINCIBILITY > 0: continue
				damage = self.calcDotDamage( receiver, e, csdefine.DAMAGE_TYPE_MAGIC, self._p2 )
				g_fightMgr.buildEnemyRelation( e, caster )
				e.receiveSpell( casterID, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage, 0 )
				e.receiveDamage( casterID, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_MAGIC, damage )
					
				maxCount -= 1
			
				if maxCount <= 0:
					break
						
		return True
		
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
		obj = Buff_107018()
		obj.__dict__.update( self.__dict__ )
		obj._param = data["param"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )		
		else:
			obj.setUID( data[ "uid" ] )		
		return obj
		
#
# $Log: not supported by cvs2svn $
#