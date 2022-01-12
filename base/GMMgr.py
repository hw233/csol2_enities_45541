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
	信息查找行为基础类
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
		查找信息
		"""
		pass


class QueryMoneyAction( Action ):
	"""
	查询玩家金钱
	"""
	def do( self ):
		"""
		"""
		self.dstMB.cell.queryMoneyInfo( self.queryerMB, self.params  )


class QueryPosAction( Action ):
	"""
	查询玩家位置
	"""
	def do( self ):
		"""
		"""
		self.dstMB.cell.queryPosInfo( self.queryerMB, self.params  )


class QueryStateAction( Action ):
	"""
	查询玩家金钱
	"""
	def do( self ):
		"""
		"""
		self.dstMB.cell.queryStateInfo( self.queryerMB, self.params  )



class QueryBankAction( Action ):
	"""
	查询仓库信息
	"""
	def do( self ):
		"""
		"""
		self.dstMB.queryBankInfo( self.queryerMB, self.params )
		self.dstMB.cell.queryBankInfo( self.queryerMB, self.params  )



class QueryBagAction( Action ):
	"""
	查询背包信息
	"""
	def do( self ):
		"""
		"""
		self.dstMB.cell.queryBagInfo( self.queryerMB, self.params  )


class QuerySkillAction( Action ):
	"""
	查询技能信息
	"""
	def do( self ):
		"""
		"""
		self.dstMB.cell.querySkillInfo( self.queryerMB, self.params  )


class QueryLoginAction( Action ):
	"""
	查询登陆信息
	"""
	def do( self ):
		"""
		"""
		self.dstMB.queryLoginInfo( self.queryerMB, self.params  )


class QueryLastLoginAction( Action ):
	"""
	查询上次登陆信息
	"""
	def do( self ):
		"""
		"""
		self.dstMB.queryLastLoginInfo( self.queryerMB, self.params  )


class QueryAccountAction( Action ):
	"""
	查询上次登陆信息
	"""
	def do( self ):
		"""
		"""
		self.dstMB.queryAccountInfo( self.queryerMB, self.params  )


class CatchAction( Action ):
	"""
	捕捉角色
	"""
	def do( self ):
		"""
		"""
		self.dstMB.cell.catchAction( self.queryerMB, self.params )


class CometoAction( Action ):
	"""
	到达角色的位置
	"""
	def do( self ):
		"""
		"""
		self.dstMB.cell.cometoAction( self.queryerMB, self.params )

class QueryIPAction( Action ):
	"""
	查询IP
	"""
	def do( self ):
		"""
		"""
		self.dstMB.queryIPAction( self.queryerMB, self.params )


class KickAction( Action ):
	"""
	踢角色
	"""
	def do( self ):
		"""
		"""
		self.dstMB.kickAction( self.queryerMB, self.params )


class QueryPlayerAmountAction( Action ):
	"""
	查找在线玩家数目
	"""
	def do( self ):
		"""
		"""
		self.dstMB.queryPlayerAmountAction( self.queryerMB, self.params )

class QueryPlayerNameAction( Action ):
	"""
	查看在线玩家名字
	"""
	def do( self ):
		"""
		"""
		self.dstMB.queryPlayerNameAction( self.queryerMB, self.params )


class BlockAccountAction( Action ):
	"""
	封锁帐号
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
	设置怪物刷新速度。
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
	查看宠物灵性
	"""
	def do( self ):
		"""
		"""
		self.dstMB.cell.queryPetNimbus( self.queryerMB, self.params )



class QueryPetLife( Action ):
	"""
	查看宠物生命值
	"""
	def do( self ):
		"""
		"""
		self.dstMB.cell.queryPetLife( self.queryerMB, self.params )


class QueryPetJoyancy( Action ):
	"""
	查看宠物快乐度
	"""
	def do( self ):
		"""
		"""
		self.dstMB.cell.queryPetJoyancy( self.queryerMB, self.params )


class QueryPetPropagate( Action ):
	"""
	查看宠物繁殖情况
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
		# 把自己注册为globalData全局实体
		self.registerGlobally( "GMMgr", self._onRegisterManager )
		self.actionDict = {} 				#{ demanderMB : [ Info1 ], ... }
		self.currentAction = None			#当前的信息查找任务

	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
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
		查询信息
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
		查询信息
		"""
		if args.split()[0] not in attribute_Dict:
			return
		self.addQueryDict( demanderMB, dstMB, args.split()[0], args, {} )


	def lookResult( self, demanderMB, args, params, dstBaseMB ) :
		"""
		"""
		if hasattr( dstBaseMB, "cell" ):					# 玩家在线
			self.addQueryDict( demanderMB, dstBaseMB,args.split()[1], args, params )
		else:											# 如果目标玩家已经下线
			demanderMB.client.onStatusMessage( csstatus.GM_NOT_HAVE_PLAYER, "" )

	def addQueryDict( self, demanderMB, dstBaseMB, key, args, params ) :
		"""
		增加一个查询记录
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
		抓人
		"""
		msg = args.split()

		if len( msg ) < 1:
			return

		Love3.g_baseApp.lookupRoleBaseByName( msg[0], Function.Functor( self.lookResult, demanderMB, args + " " + cschannel_msgs.GMMGR_BO_ZHUO, params ) )


	def cometo( self, demanderMB, args, params ):
		"""
		define method
		到达
		"""
		msg = args.split()

		if len( msg ) < 1:
			return

		Love3.g_baseApp.lookupRoleBaseByName( msg[0], Function.Functor( self.lookResult, demanderMB, args + " " + cschannel_msgs.GMMGR_DAO_DA, params ) )


	def kick( self, demanderMB, args, params ):
		"""
		define method
		踢人
		"""
		msg = args.split()

		if len( msg ) < 1:
			return
		Love3.g_baseApp.lookupRoleBaseByName( msg[0], Function.Functor( self.lookResult, demanderMB, args + " " + cschannel_msgs.GMMGR_TI_REN, params ) )


	def queryPlayerAmount( self, demanderMB, args, params ):
		"""
		define method
		查询人数
		"""
		self.addQueryDict( demanderMB, demanderMB, cschannel_msgs.GMMGR_ZAI_XIAN_REN_SHU, args, params )


	def block_account( self, demanderMB, args, params ):
		"""
		define method
		封锁帐号
		/block_account kkk 3600 坏人
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
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onUnBlockCB, demanderMB) )#记录到数据库

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
		查询人数
		"""
		self.addQueryDict( demanderMB, demanderMB, cschannel_msgs.GMMGR_ZAI_XIAN_MING_ZI, args, params )


	def setRespawnRate( self, demanderMB, args, params ):
		"""
		define method
		刷怪速度
		"""
		self.addQueryDict( demanderMB, demanderMB, cschannel_msgs.GMMGR_SHUA_GUAI_SU_DU, args, params )


	def shutdown( self, delay ):
		"""
		define method
		关闭服务器
		"""
		Love3.g_baseApp.shutdownAll( delay )
