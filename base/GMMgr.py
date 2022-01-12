# -*- coding: gb18030 -*-
#

import Love3
import Language
import cschannel_msgs
import ShareTexts as ST
import Function
import BigWorld
import csdefine
from bwdebug import *
import time
import csconst
from Function import Functor
import csstatus


QUERY_STATE 	= 1
SEND_INFO_STATE = 2


class Action:
	"""
	��Ϣ������Ϊ������
	"""
	def __init__( self, demanderMB, dstBaseMB, args, params ):
		"""
		"""
		self.queryerMB = demanderMB
		self.dstMB = dstBaseMB
		self.args = args
		self.params = params

	def do( self ):
		"""
		������Ϣ
		"""
		pass


class QueryMoneyAction( Action ):
	"""
	��ѯ��ҽ�Ǯ
	"""
	def do( self ):
		"""
		"""
		self.dstMB.cell.queryMoneyInfo( self.queryerMB, self.params  )


class QueryPosAction( Action ):
	"""
	��ѯ���λ��
	"""
	def do( self ):
		"""
		"""
		self.dstMB.cell.queryPosInfo( self.queryerMB, self.params  )


class QueryStateAction( Action ):
	"""
	��ѯ��ҽ�Ǯ
	"""
	def do( self ):
		"""
		"""
		self.dstMB.cell.queryStateInfo( self.queryerMB, self.params  )



class QueryBankAction( Action ):
	"""
	��ѯ�ֿ���Ϣ
	"""
	def do( self ):
		"""
		"""
		self.dstMB.queryBankInfo( self.queryerMB, self.params )
		self.dstMB.cell.queryBankInfo( self.queryerMB, self.params  )



class QueryBagAction( Action ):
	"""
	��ѯ������Ϣ
	"""
	def do( self ):
		"""
		"""
		self.dstMB.cell.queryBagInfo( self.queryerMB, self.params  )


class QuerySkillAction( Action ):
	"""
	��ѯ������Ϣ
	"""
	def do( self ):
		"""
		"""
		self.dstMB.cell.querySkillInfo( self.queryerMB, self.params  )


class QueryLoginAction( Action ):
	"""
	��ѯ��½��Ϣ
	"""
	def do( self ):
		"""
		"""
		self.dstMB.queryLoginInfo( self.queryerMB, self.params  )


class QueryLastLoginAction( Action ):
	"""
	��ѯ�ϴε�½��Ϣ
	"""
	def do( self ):
		"""
		"""
		self.dstMB.queryLastLoginInfo( self.queryerMB, self.params  )


class QueryAccountAction( Action ):
	"""
	��ѯ�ϴε�½��Ϣ
	"""
	def do( self ):
		"""
		"""
		self.dstMB.queryAccountInfo( self.queryerMB, self.params  )


class CatchAction( Action ):
	"""
	��׽��ɫ
	"""
	def do( self ):
		"""
		"""
		self.dstMB.cell.catchAction( self.queryerMB, self.params )


class CometoAction( Action ):
	"""
	�����ɫ��λ��
	"""
	def do( self ):
		"""
		"""
		self.dstMB.cell.cometoAction( self.queryerMB, self.params )

class QueryIPAction( Action ):
	"""
	��ѯIP
	"""
	def do( self ):
		"""
		"""
		self.dstMB.queryIPAction( self.queryerMB, self.params )


class KickAction( Action ):
	"""
	�߽�ɫ
	"""
	def do( self ):
		"""
		"""
		self.dstMB.kickAction( self.queryerMB, self.params )


class QueryPlayerAmountAction( Action ):
	"""
	�������������Ŀ
	"""
	def do( self ):
		"""
		"""
		self.dstMB.queryPlayerAmountAction( self.queryerMB, self.params )

class QueryPlayerNameAction( Action ):
	"""
	�鿴�����������
	"""
	def do( self ):
		"""
		"""
		self.dstMB.queryPlayerNameAction( self.queryerMB, self.params )


class BlockAccountAction( Action ):
	"""
	�����ʺ�
	"""
	def do( self ):
		"""
		such as:
		self.args = cschannel_msgs.GMMGR_ABC_FENG_SUO_ZHANG_HAO_3600
		"""
		#self.dstMB.blockAccountAction( self.queryerMB, self.params )

		msg = self.args.split()
		"""
		self.beginDate = time.time()
		self.endDate = time.time() + int(msg[2])
		self.reason_persist = msg[3]
		self.reason_variable = "No"
		self.author = self.params['name']
		self.dbid = self.dstMB.databaseID
		"""
		self.dstMB.blockPlayerAccount( {
										"endDate":time.time() + int(msg[2]),
										} )
		self.queryerMB.client.onStatusMessage( csstatus.GM_LOCK_ACCOUNT, str(( int(msg[2]), )) )


class SetRespawnRateAction( Action ):
	"""
	���ù���ˢ���ٶȡ�
	"""
	def do( self ):
		"""
		"""
		args = self.args.split()
		for key in BigWorld.globalData.keys():
			if type(key) == type("cellApp_") and "cellApp_" in key:
				BigWorld.executeRemoteScript( "BigWorld.cellAppData['%s'].setRespawnRate( '%s', %s )"%( key + "_actions", args[0], args[1] ), BigWorld.globalData[key] )


class QueryPetNimbus( Action ):
	"""
	�鿴��������
	"""
	def do( self ):
		"""
		"""
		self.dstMB.cell.queryPetNimbus( self.queryerMB, self.params )



class QueryPetLife( Action ):
	"""
	�鿴��������ֵ
	"""
	def do( self ):
		"""
		"""
		self.dstMB.cell.queryPetLife( self.queryerMB, self.params )


class QueryPetJoyancy( Action ):
	"""
	�鿴������ֶ�
	"""
	def do( self ):
		"""
		"""
		self.dstMB.cell.queryPetJoyancy( self.queryerMB, self.params )


class QueryPetPropagate( Action ):
	"""
	�鿴���ﷱֳ���
	"""
	def do( self ):
		"""
		"""
		self.dstMB.cell.queryPetPropagate( self.queryerMB, self.params )

attribute_Dict = {	cschannel_msgs.GMMGR_ZHUANG_TAI			:		QueryStateAction,
					cschannel_msgs.GMMGR_WEI_ZHI			:		QueryPosAction,
					cschannel_msgs.GMMGR_JIN_QIAN			:		QueryMoneyAction,
					"IP"			:		QueryIPAction,
					cschannel_msgs.GMMGR_CANG_KU			:		QueryBankAction,
					cschannel_msgs.GMMGR_BEI_BAO			:		QueryBagAction,
					cschannel_msgs.GMMGR_JI_NENG			:		QuerySkillAction,
					cschannel_msgs.GMMGR_DENG_LU			:		QueryLoginAction,
					cschannel_msgs.GMMGR_SHANG_CI_DENG_LU		:		QueryLastLoginAction,
					cschannel_msgs.GMMGR_ZHANG_HAO			:		QueryAccountAction,
					cschannel_msgs.GMMGR_BO_ZHUO			:		CatchAction,
					cschannel_msgs.GMMGR_DAO_DA			:		CometoAction,
					cschannel_msgs.GMMGR_TI_REN			:		KickAction,
					cschannel_msgs.GMMGR_ZAI_XIAN_REN_SHU		:	 	QueryPlayerAmountAction,
					cschannel_msgs.GMMGR_FENG_SUO_ZHANG_HAO		: 		BlockAccountAction,
					cschannel_msgs.GMMGR_ZAI_XIAN_MING_ZI		: 		QueryPlayerNameAction,
					cschannel_msgs.GMMGR_SHUA_GUAI_SU_DU		: 		SetRespawnRateAction,

					cschannel_msgs.GMMGR_CHONG_WU_LING_XING_ZHI 	:		QueryPetNimbus,
					cschannel_msgs.GMMGR_CHONG_WU_SHOU_MING		:		QueryPetLife,
					cschannel_msgs.GMMGR_CHONG_WU_KUAI_LE_DU	:		QueryPetJoyancy,
					cschannel_msgs.GMMGR_CHONG_WU_FAN_ZHI		:		QueryPetPropagate,
					}


class GMMgr( BigWorld.Base ):
	"""
	"""
	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		# ���Լ�ע��ΪglobalDataȫ��ʵ��
		self.registerGlobally( "GMMgr", self._onRegisterManager )
		self.actionDict = {} 				#{ demanderMB : [ Info1 ], ... }
		self.currentAction = None			#��ǰ����Ϣ��������

	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register GMMgr Fail!" )
			# again
			self.registerGlobally( "GMMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["GMMgr"] = self
			INFO_MSG("GMMgr Create Complete!")


	def query_Info( self, demanderMB, args, params ):
		"""
		define method
		��ѯ��Ϣ
		"""
		msg = args.split()

		if len( msg ) < 2:
			demanderMB.client.onStatusMessage( csstatus.GM_QUERY_INFO_HELP, "" )
			demanderMB.client.onStatusMessage( csstatus.GM_QUERY_INFO_HELP_01, "" )
			return
		for i in msg[1:]:
			if i not in attribute_Dict:
				demanderMB.client.onStatusMessage( csstatus.GM_QUERY_INFO_HELP_01, "" )
				return
		Love3.g_baseApp.lookupRoleBaseByName( msg[0], Function.Functor( self.lookResult, demanderMB, args, params ) )


	def query_Pet_Info( self, demanderMB, dstMB, args ):
		"""
		define method
		��ѯ��Ϣ
		"""
		if args.split()[0] not in attribute_Dict:
			return
		self.addQueryDict( demanderMB, dstMB, args.split()[0], args, {} )


	def lookResult( self, demanderMB, args, params, dstBaseMB ) :
		"""
		"""
		if hasattr( dstBaseMB, "cell" ):					# �������
			self.addQueryDict( demanderMB, dstBaseMB,args.split()[1], args, params )
		else:											# ���Ŀ������Ѿ�����
			demanderMB.client.onStatusMessage( csstatus.GM_NOT_HAVE_PLAYER, "" )

	def addQueryDict( self, demanderMB, dstBaseMB, key, args, params ) :
		"""
		����һ����ѯ��¼
		"""
		if not self.actionDict.has_key( demanderMB.id ):
			self.actionDict[demanderMB.id] = []

		self.actionDict[demanderMB.id].append( attribute_Dict[key]( demanderMB, dstBaseMB, args, params ) )

		self.addTimer( 0.1, 0, QUERY_STATE )

	def onTimer( self, id, userArg ):
		"""
		"""
		if userArg == QUERY_STATE:
			key = self.actionDict.keys()[0]
			self.currentAction = self.actionDict[key].pop(0)

			self.currentAction.do()

			if len( self.actionDict[key] ) == 0:
				del self.actionDict[key]


	def catch( self, demanderMB, args, params ):
		"""
		define method
		ץ��
		"""
		msg = args.split()

		if len( msg ) < 1:
			return

		Love3.g_baseApp.lookupRoleBaseByName( msg[0], Function.Functor( self.lookResult, demanderMB, args + " " + cschannel_msgs.GMMGR_BO_ZHUO, params ) )


	def cometo( self, demanderMB, args, params ):
		"""
		define method
		����
		"""
		msg = args.split()

		if len( msg ) < 1:
			return

		Love3.g_baseApp.lookupRoleBaseByName( msg[0], Function.Functor( self.lookResult, demanderMB, args + " " + cschannel_msgs.GMMGR_DAO_DA, params ) )


	def kick( self, demanderMB, args, params ):
		"""
		define method
		����
		"""
		msg = args.split()

		if len( msg ) < 1:
			return
		Love3.g_baseApp.lookupRoleBaseByName( msg[0], Function.Functor( self.lookResult, demanderMB, args + " " + cschannel_msgs.GMMGR_TI_REN, params ) )


	def queryPlayerAmount( self, demanderMB, args, params ):
		"""
		define method
		��ѯ����
		"""
		self.addQueryDict( demanderMB, demanderMB, cschannel_msgs.GMMGR_ZAI_XIAN_REN_SHU, args, params )


	def block_account( self, demanderMB, args, params ):
		"""
		define method
		�����ʺ�
		/block_account kkk 3600 ����
		"""
		msg = args.split()

		if len( msg ) < 2:
			return
		newArgs = msg[0] + " " + cschannel_msgs.GMMGR_FENG_SUO_ZHANG_HAO + " " + msg[1]
		Love3.g_baseApp.lookupRoleBaseByName( msg[0], Function.Functor( self.lookResult, demanderMB, newArgs, params ) )


	def unBlock_account( self, demanderMB, args, params ):
		"""
		"""
		accountName = args.split()[0]
		query = "update tbl_Account set sm_block_end_time = %i, sm_block_state = %i  where sm_playerName = \'%s\' "% ( 0, 0, BigWorld.escape_string( accountName ) )
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onUnBlockCB, demanderMB) )#��¼�����ݿ�

	def __onUnBlockCB( self, demanderMB, resultSet, rows, errstr ):
		"""
		"""
		if errstr:
			demanderMB.client.onStatusMessage( csstatus.GM_NOT_HAVE_ACCOUNT, "" )
		else:
			demanderMB.client.onStatusMessage( csstatus.GM_UNLOCK_ACCOUNT, "" )


	def queryPlayersName( self, demanderMB, args, params ):
		"""
		define method
		��ѯ����
		"""
		self.addQueryDict( demanderMB, demanderMB, cschannel_msgs.GMMGR_ZAI_XIAN_MING_ZI, args, params )


	def setRespawnRate( self, demanderMB, args, params ):
		"""
		define method
		ˢ���ٶ�
		"""
		self.addQueryDict( demanderMB, demanderMB, cschannel_msgs.GMMGR_SHUA_GUAI_SU_DU, args, params )


	def shutdown( self, delay ):
		"""
		define method
		�رշ�����
		"""
		Love3.g_baseApp.shutdownAll( delay )
