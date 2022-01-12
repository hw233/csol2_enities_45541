# -*- coding: gb18030 -*-
#


"""
������Ч��
"""
import random
import Math
import BigWorld
import time
import csstatus
import csdefine
import csconst
from bwdebug import *
from Function import newUID

import Const
from SpellBase import *
from Buff_Normal import Buff_Normal



class Buff_22135( Buff_Normal ):
	"""
	��������buff
	(Lv^1.5 * 3.5 + 9) * param1  #ÿ���ӻ�þ��飻
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
		self.param1 = float( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0.0 )

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
		exp = ( pow(receiver.level, 1.5) * 3.5 + 9 ) * self.param1  #ÿ���ӻ�þ���
		receiver.addExp( exp, csdefine.CHANGE_EXP_DANCEKING_BUFF )
		DEBUG_MSG("Buff_22135 doLoop add exp:%f to playerName:%s"%(exp, receiver.playerName))
		return Buff_Normal.doLoop( self, receiver, buffData )

	def receive( self, caster, receiver ):
		if receiver.findBuffByBuffID(csconst.DancingBuffID):   #��������buff�Ļ����ϲż�����buff
			Buff_Normal.receive( self, caster, receiver )

	def getNewBuffData( self, caster, receiver ):
		newBuffData = {}
		newBuffData[ "skill" ] = self
		newBuffData[ "persistent" ] = self.calculateTime( receiver )
		newBuffData[ "currTick" ] = 0
		newBuffData[ "caster" ] = self._casterID
		newBuffData[ "state" ] = 0
		newBuffData[ "index" ] = 0
		newBuffData[ "sourceType" ] = self.getSourceType()
		newBuffData[ "isNotIcon" ] = self.isNotIcon()
		return newBuffData

	def calculateTime( self, receiver ):
		"""
		"""
		return receiver.findBuffByBuffID(csconst.DancingBuffID)["persistent"]

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
		exp = ( pow(receiver.level, 1.5) * 3.5 + 9 ) * self.param1  #ÿ���ӻ�þ���
		DEBUG_MSG("Buff_22135 doReload add exp:%f to playerName:%s"%(exp, receiver.playerName))
		receiver.addExp( exp, csdefine.CHANGE_EXP_DANCEKING_BUFF )
		
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		exp = ( pow(receiver.level, 1.5) * 3.5 + 9 ) * self.param1  #ÿ���ӻ�þ���
		receiver.addExp( exp, csdefine.CHANGE_EXP_DANCEKING_BUFF )
		DEBUG_MSG("Buff_22135 doEnd add exp:%f to playerName:%s"%(exp, receiver.playerName))
		if csconst.DancingKingBuffID in [skillData["skill"].getBuffID() for skillData in receiver.attrBuffs]:  #������buffʱ�䵽��ʱ��ҲҪȥ������buff
			receiver.removeBuffByID( DancingKingBuffID,  [csdefine.BUFF_INTERRUPT_NONE] )   #buffʱ�䵽�ˣ��Զ�ȥ������buff	
		Buff_Normal.doEnd( self, receiver, buffData )

	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�
		
		@type data: dict
		"""
		obj = Buff_22135()
		obj.__dict__.update( self.__dict__ )
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )		
		else:
			obj.setUID( data[ "uid" ] )		
		return obj

#
# $Log: not supported by cvs2svn $
#
# 
#