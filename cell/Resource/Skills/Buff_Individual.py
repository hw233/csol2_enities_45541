# -*- coding: gb18030 -*-
"""
Ŀǰ�����ǵ�buff��������д����������⣺ 

�����Buff_1234�ű��д������´��룺 
def doBegin( self, receiver, buffData ): 
   self.playerID = receiver.id 
��ô������ 
1������5687����buff 1234 
1����player1��id = 1��ʩ��5678������buff 1234 
2���������player2��id = 2��Ҳʩ��5678�����Ҳ������buff 1234 

��ôcell��player1.attrBuffs[buff 1234 idx]["skill"].playerID == player2.id

����֮������buff 1234���ԣ�self.playerID��һ�ָ��Ի����ݣ������ǺͲ�ͬ�����صģ�����ͬһ���ܵ�buff 1234��ʵ��ȫ��ֻ��һ������˲��������ݸ��ǵ����⡣

����������������Ѿã����������ȡ�˴���һ�µĴ����ʩ�����ڣ� 
doBegin( self, receiver, buffData )����Ϊ�����������μ�buff:15003�� 

���Դ����ȶ��Կ��ǣ�������������е���������Եײ�������κ��޸ġ�

���ǣ���doBegin()�и�������Ľ���취��Ȼ��һ�����⡪������������ӵ�д�����ͬ��addToDict/createFromDict������������࣬����Ϊ�˽��
�������⣬���Ҽ򻯰����С���Ҹ��Ի����ݡ�buff��ʵ�֡����ĳ��buff��Ҫ������Ҹ��Ի����ݣ���̳�����ࡣ

ʹ�ø�Ҫ��
1) �̳������
2) ������Ҫ�������ĸ��¼��г�ʼ�����Ի����ݣ�_onDoBegin�� _onDoEnd, _onDoReload, _onDoLoop����ʼ�����֮��ʹ��_packIndividualData���������ݴ����
Ȼ��һ�и��Ի����ݵ�Ǩ�����⽻�����ദ���ɣ������в���Ҫ���κεĶ��⴦����һ��ʹ�ô˻��Ƶ������ǣ�Buff_Vehicle��

ע�����
1��һ���̳�������࣬�Ͳ���ҪҲ��Ӧ������createFromDict/addToDict
2��ֻ�������ĸ�������_onDoBegin�� _onDoEnd, _onDoReload, _onDoLoop��ʹ��_packIndividualData������������ݣ������������Դ�
3��ǿ�ҽ���ֻͨ��_packIndividualData������������ݣ������ƹ���ȫ��顣
4��_packIndividualData�����������ʱ��Ҫһ��������ֵ�ԣ��������ֱ����Ǵ���ʵ���е��������������������Դ�(��ô����ԭ����ο���Ӧ�����е�ע��)��
5�����Ի����ݵ�ֵ����_packIndividualData�������ʱȷ��������֮��һ���޸����κθ��Ի����ݣ���Ӧ�õ���_packIndividualData�����Դ����ݽ��д��������ͻ��������Ǩ�ƺ�һ�µ������
6����������һ���׻��ƣ������cell�ϼ̳�������࣬��ô�������Ҫ�����ݴ������ͻ��˵�������£�ҲӦ����client�ϼ̳���Ӧ��ͬ���ࡣ
7�������������в����û����receive������˻���ʧЧ��

2011-1-14 16:38
by mushuang
"""



import BigWorld
from bwdebug import *
from Buff_Normal import Buff_Normal
from Function import newUID

class Buff_Individual ( Buff_Normal ):
	"""
	��Ҹ�����ص�buff�����ĳ��buff����Ҫ����һЩ���ÿ����ҵĸ��Ի����ݣ���ô��̳д�buff
	���̳д�buff��Ҳ����ȡ������ʩ��ֱ�Ӵ�����Ҹ��Ի����ݻ��������ʵ�������⣬�����CSOL-10239
	by mushuang
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._packedIndividualData = {}
		self.__canPackData = False # �˱�־������֤�������ͬ��Ҷ��������ݵ�ʱ���Ƿ���ȷ���ڲ���ȷ��ʱ������Լ�������ͬ���޷����⡰��ʵ��������
		
	def _packIndividualData( self, key, val ):
		"""
		@addIndividualData:��ÿ�������ص����ݴ��
		@key: �����ݵ�����ʵ���е�ʵ����
		@val: �����ݵ�ֵ
		"""
		# ȷ���Ƿ�Ӧ���ڴ�ʱ�������ͬ��Ҷ��������ݣ��ڲ���ȷ��ʱ������Լ�������ͬ���޷����⡰��ʵ��������
		assert self.__canPackData, "You can't pack individual data now!"
		
		# ��֧��˽�����ԣ�__��ͷ�����ԣ������ֶ����û����һЩ����Ĵ��룬���Ǳ������ԣ�_��ͷ�����ԣ��ǿ���ʹ�õ�
		assert not key.startswith( "__" ), "Private attribute is not supported!"
		
		# �����ʵ���б�������ԡ�key��Ϊ�������ԣ��������Ϊ��������������Ҳ��������������ǣ��ϸ��޶������ڼ���
		# bug��������һ��������޶���������ɴ�����������һ�£����������Ӵ���ĸ��Ӷȣ�����һ��������cell�Ͻ�_hp����
		# client��ȴ��_healthPercent�������Կ����������һ��Ǿ������������޶���
		assert hasattr( self, key ), "Attribute: %s must exist in this object"%key
		
		self._packedIndividualData[ key ] = val
		

	def receive( self, caster, receiver ):
		"""
		���ڸ�Ŀ��ʩ��һ��buff�����е�buff�Ľ��ն�����ͨ���˽ӿڣ�
		�˽ӿڱ����жϽ������Ƿ�ΪrealEntity��
		����������Ҫͨ��receiver.receiveOnReal()�ӿڴ���

		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		# ��Ϊ�ȵ��û��࣬����receiver��ghost��������ڻ������Ѿ�����
		Buff_Normal.receive( self, caster, receiver )
		
		# �滻�Ѿ����ص�buff���ݵ��е�buffʵ����������ʵ��:ÿ��������ϼ��ص��ǲ�ͬ��buffʵ��
		buffData = receiver.findBuffByID( self.getID() )
		assert buffData, "Can't find buffData!"
		
		# �������������Ӷ���֤������ÿ��������ϵ�buff���Ƕ�����
		buffData["skill"] = self.__clone()
		
	def _onDoBegin( self, receiver, buffData ):
		"""
		�˷�����Buff_Individual��doBegin���ã����ڸ��¡���Ҹ��Ի����ݡ����������������и�����ĳ�����Ի����ݣ���ʹ�ã�
		_packIndividualData�����ݴ�������������޷���ȷǨ�ơ�
		"""
		pass
		
	def _onDoEnd( self, receiver, buffData ):
		"""
		�˷�����Buff_Individual��doEnd���ã����ڸ��¡���Ҹ��Ի����ݡ����������������и�����ĳ�����Ի����ݣ���ʹ�ã�
		_packIndividualData�����ݴ�������������޷���ȷǨ�ơ�
		"""
		pass
	
	def _onDoLoop( self, receiver, buffData ):
		"""
		�˷�����Buff_Individual��doLoop���ã����ڸ��¡���Ҹ��Ի����ݡ����������������и�����ĳ�����Ի����ݣ���ʹ�ã�
		_packIndividualData�����ݴ�������������޷���ȷǨ�ơ�
		"""
	
	def _onDoReload( self, receiver, buffData ):
		"""
		�˷�����Buff_Individual��doReload���ã����ڸ��¡���Ҹ��Ի����ݡ����������������и�����ĳ�����Ի����ݣ���ʹ�ã�
		_packIndividualData�����ݴ�������������޷���ȷǨ�ơ�
		"""

	
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
		# ������receive�п�¡���Լ��������������ʵ���Ϸ�����ÿ����Ҹ��Ե�buffʵ����
		
		Buff_Normal.doBegin( self, receiver, buffData )
		
		self.__canPackData = True
		self._onDoBegin( receiver, buffData )
		self.__canPackData = False
		
	
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
		
		self.__canPackData = True
		self._onDoLoop( receiver, buffData )
		self.__canPackData = False
		
		return Buff_Normal.doLoop( self, receive, buffData )
		
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
		
		# doReload����ʲô���⴦����buffReloadʱ�������ݿ��з����л������Ķ����Ѿ���ÿ����Ҳ�ͬ����
		# �ο���SkillTypeImpl.py
		
		self.__canPackData = True
		self._onDoReload( receiver, buffData )
		self.__canPackData = False
	
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		
		# ��������������õ��Ѿ���ÿ��������ϲ�ͬ��buffʵ�������Բ����κ����⴦��
		
		self.__canPackData = True
		self._onDoEnd( receiver, buffData )
		self.__canPackData = False
		
	def __clone( self ):
		"""
		��¡����
		"""
		obj = self.__class__()
		obj.__dict__.update( self.__dict__ )
		return obj
		
	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{"id":self._id, "param":None}������ʾ�޶�̬���ݡ�
		
		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		
		
		ע��:�����̳��ˡ�Buff_Individual���࣬һ����Ҫ�������������
		
		"""
		DEBUG_MSG( "Adding individual data to dict:%s"%str( { "param" : self._packedIndividualData } ) )
		return { "param" : self._packedIndividualData }
		
	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�
		
		ע��:�����̳��ˡ�Buff_Individual���࣬һ����Ҫ�������������
		
		@type data: dict
		"""
		obj = self.__clone()
		
		obj._packedIndividualData = data[ "param" ]
		
		# ����������������߱���ģ����Ե���һ��Ӧ�ô�ģ���еĴ���ָ�ʱ����Ȼ��None��
		# ����Ϊ֮ǰ��ͨ��Skill.addToDict�е�Ĭ�ϻ��Ʊ���ģ��� ��������ͻ���
		# _packIndividualData() ʱ�����쳣��2011-1-25 10:01 by mushuang
		if obj._packedIndividualData is None:
			WARNING_MSG( "Deprecated data of \"param\" found, resetting _packedIndividualData to {}" )
			obj._packedIndividualData = {}
			
		DEBUG_MSG( "Restore individual Data to _packedIndividualData: %s"%data[ "param" ] )
		
		# ���������ġ���ͬ���������ݡ���ȷ���õ������ֶ���ȥ
		for key,val in self._packedIndividualData.iteritems():
			assert hasattr( obj, key ),"Can't find attribute: %s in this object!"%key
			setattr( obj, key, val )
		
		# _uidĿǰ��û��ʹ�ã����ǰ�ȫ�������Ϊ�˱�֤���Ƶ������ԣ����ǰ����Ͱ�ش�������
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj
	

	