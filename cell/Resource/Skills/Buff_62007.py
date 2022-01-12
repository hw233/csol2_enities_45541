# -*- coding:gb18030 -*-


import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
from Function import newUID

class Buff_62007( Buff_Normal ):
	"""
	��������%������������%����������������%
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0		# ���ı���
		self._p4 = 0		# ����������������%
		self.NPCOldModelScale = 1.0
		
	def init( self, dict ):
		"""
		"""
		Buff_Normal.init( self, dict )
		self._p1 = float( dict[ "Param1" ] )
		self._p4 = ( int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )  / 100.0 ) * csconst.FLOAT_ZIP_PERCENT
		
	def doBegin( self, receiver, buffData ):
		"""
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.damage_min_percent += self._p4
		receiver.calcDamageMin()
		receiver.damage_max_percent += self._p4
		receiver.calcDamageMax()
		receiver.magic_damage_percent += self._p4
		receiver.calcMagicDamage()
		self.NPCOldModelScale = receiver.modelScale
		receiver.modelScale = self._p1

	def doReload( self, receiver, buffData ):
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.damage_min_percent += self._p4
		receiver.damage_max_percent += self._p4
		receiver.magic_damage_percent += self._p4
		self.NPCOldModelScale = receiver.modelScale
		receiver.modelScale = self._p1
		
	def doEnd( self, receiver, buffData ):
		"""
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.damage_min_percent -= self._p4
		receiver.calcDamageMin()
		receiver.damage_max_percent -= self._p4
		receiver.calcDamageMax()
		receiver.magic_damage_percent -= self._p4
		receiver.modelScale = self.NPCOldModelScale
		
	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{"id":self._id, "param":None}������ʾ�޶�̬���ݡ�

		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		"""
		return { "param" : self.NPCOldModelScale }
		
	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�

		@type data: dict
		"""
		obj = Buff_62007()
		obj.__dict__.update( self.__dict__ )

		obj.NPCOldModelScale = data["param"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj