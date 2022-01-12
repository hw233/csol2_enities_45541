# -*- coding: gb18030 -*-
#
# written by wangshufeng

import BigWorld
import csconst
import Const
from bwdebug import *


class RelationMgr( BigWorld.Base ):
	"""
	��ҹ�ϵuid����
	
	��ҹ�ϵ����ƣ�
	�Զ���һ��db��custom_Relation���洢��������ҵĹ�ϵ������ÿһ����¼��ʾ������ҹ�ϵ��
	��¼����һ���ֶ�relationStatus��ʾ��2����ҵĹ�ϵ״̬��relationStatus��һ��uint32���ݣ�
	����ǰ2���ֽڱ�ʾsm_playerDBID1����ҹ�ϵ״̬����2�ֽڱ�ʾsm_playerDBID2�Ĺ�ϵ״̬��
	����˫����Ҷ��п���ͬʱд������¼�п������ǰ�߱����ǣ�����ڸ��¹�ϵ״̬ʱʹ�ý�����relationStatus�е�ĳһ��λ�ķ�ʽ��
	��˾���˫��ͬʱ���´����ݺ���Ҳ���Ḳ�ǵ�ǰ�ߵĸ��ġ�
	ÿһ����¼����Ψһ��һ��uid(int32)����Ҹ��¹�ϵ״̬ʱ������uid����λ��ϵ���ݡ�uid�����ɹ������£�
	uid��uidFactory���䣬��1��ʼ������baseAppÿ�η���100��uid��Դ��ÿ��baseApp��uid��Դ����10��ʱ����uidFactory�ٴ����롣
	ÿ�η�������������ѯcustom_Relation���ҳ�����uid���Դ���Ϊuid�������ʼ��š�ÿ��baseAppû����uid�����ٴ����룬
	�����uid��Դ�����࣬����������ࡣ
	"""
	def __init__( self ):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.maxUID = 0			# ��ǰ����uid
		self.intializeFinish = False	# �Ƿ��ʼ�����
		self.registerGlobally( "RelationMgr", self.registerGloballyCB )
		self.createTable()
		
	def registerGloballyCB( self, succeeded ):
		"""
		ע��ȫ��ʵ���Ļص�
		"""
		if not succeeded:
			self.registerGlobally( "RelationMgr", self.registerGloballyCB )
			
	def createTable( self ):
		"""
		����custom_Relation��
		
		`sm_playerDBID1` ���1��databaseID
		`sm_playerDBID2` ���2��databaseID
		`sm_relationStatus` ���1�����2�Ĺ�ϵ״̬
		`sm_friendlyValue` ���1�����2���Ѻö�
		`sm_uid` ÿ����ϵ��Ψһid
		`sm_param` ��ϵ������չ�ֶΣ����ô��ֶε�ԭ���ǽ��ϵͳ��Ҫ�洢��ݳƺţ��д��ֶ�Ҳ���Դ洢������ϵ��������ݡ�
		
		sm_relationStatus��һ��UINT32���ݡ����ң�ǰ16λ��λģʽ��ʾplayerDBID1�Ĺ�ϵ״̬
		��16λ��λģʽ��ʾplayerDBID2�Ĺ�ϵ״̬
		"""
		# ��ҹ�ϵ���
		sqlSentence = """CREATE TABLE IF NOT EXISTS `custom_Relation` (
						`id` bigint(20) NOT NULL AUTO_INCREMENT,
						`sm_playerDBID1` BIGINT(20) UNSIGNED NOT NULL,
						`sm_playerDBID2` BIGINT(20) UNSIGNED NOT NULL,
						`sm_relationStatus` int(32) unsigned NOT NULL,
						`sm_friendlyValue` int(32) unsigned NOT NULL default 0,
						`sm_uid` int(32) unsigned NOT NULL,
						`sm_param` text,
						PRIMARY KEY (`id`),
						key (sm_uid),
						key `sm_playerDBID1Index` (sm_playerDBID1),
						key `sm_playerDBID2Index` (sm_playerDBID2)
						)ENGINE=InnoDB;
						"""
		BigWorld.executeRawDatabaseCommand( sqlSentence, self._createTableCB )
		
	def _createTableCB( self, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "create custom_Relation error:%s." % errstr )
			return
		BigWorld.executeRawDatabaseCommand( "select max(sm_uid) from custom_Relation;", self.initializeCB )
		
	def initializeCB( self, result, rows, errstr ):
		if errstr:
			ERROR_MSG( "RelationMgr initialize:%s." % errstr )
			return
		DEBUG_MSG( result )
		if result[0][0] is not None:	# һ��ʼ�ǿձ�
			self.maxUID = int( result[0][0] )
		self.intializeFinish = True
		# ��ѭһ��BigWorld.globalBases�Բ������е���ע���base entity����relationUID
		for k, baseEntityMB in BigWorld.globalBases.items():
			if not isinstance( k, str ) or not k.startswith( csconst.C_PREFIX_GBAE ):
				continue
			self.requestRelationUID( baseEntityMB )
			
	def requestRelationUID( self, baseEntityMB ):
		"""
		Define method.
		baseEntity����uid.
		��ʱ�п���UIDFactory�ոճ�ʼ���ò��Ѿ���baseEntity������UID�������ٷ���
		
		@param baseEntityMB : baseEntityMB��mailbox
		"""
		if not self.intializeFinish:		# ��û��ʼ���ã����󲻳ɹ�����ʼ����ɺ�����������е�baseApp entity����relationUID
			return
		minUID = self.maxUID + 1
		self.maxUID += Const.RELATION_UID_SAND_MAX_COUNT
		baseEntityMB.receiveRelationUID( minUID )
		
		