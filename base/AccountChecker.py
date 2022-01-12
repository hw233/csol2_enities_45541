# -*- coding: gb18030 -*-
#
"""
账号检测器模块:
	账号检测器模块分为账号检测管理器(Checker)和账号检测器组件(BaseChecker......),添加新的组件时,需要继承检测器组件基础类BaseChecker
	并重写其提供的模块。新的组件需要增加到组件列表中（checkers）中，该列表是有序的。按照检查的先后顺序进行排列。
"""


import BigWorld
import Const
import time
import random
import weakref
from bwdebug import *
import csstatus

class Checker:
	"""
	账号检测器
	"""
	_instance = None
	def __init__( self, accountID ):
		"""
		初始化
		"""
		self.checkers = []												# 所有的检测器列表
		self.accountID = accountID								# 账号实例
		self.currentChecker = -1										# 当前使用的检测器索引
		for checker in checkers:										# 初始化所有的检测模块
			self.checkers.append( checker( self.accountID ))

	def checkAccount( self ):
		"""
		检测账号是否能够登录
		"""
		self.clear()
		self.checkAlong()

	def account( self ):
		"""
		获取玩家的账号
		"""
		try:
			return BigWorld.entities[self.accountID]
		except:
			ERROR_MSG( "account is not exist, id = %s" % self.accountID )
			return None

	def checkAlong( self ):
		"""
		检测账号
		"""
		if not self.account():										# 如果账号已经不存在了,那么直接退出。
			self.clear()
			return
		self.currentChecker += 1									# 检测器索引指向下一个检测检测器(初始为-1.+1后即从第一个开始检测)
		if self.currentChecker < 0:									# 索引不正确的情况,这种情况理论上永远不会出现
			self.clear()
			ERROR_MSG( "get a error checker index = %s" % self.currentChecker )
			return
		elif self.currentChecker < len( self.checkers ):			# 索引正确的情况
			self.checkers[self.currentChecker].onCheck()			# 将检测权交给检测器组件
		else:														# 检测完毕或者没有检测器的情况
			self.account().onBeginLogAccount()						# 可以登录
			self.clear()											# 恢复检测器数据

	def getCurrentChecker( self ):
		"""
		获取当前的checker
		"""
		try:
			return self.checkers[self.currentChecker]
		except:
			return None

	def clear( self ):
		"""
		恢复数据,以便当有人挤客户端的时候重新检测
		"""
		self.currentChecker = -1
		for checker in self.checkers:				# 恢复检测器组件的数据
			checker.clear()


class BaseChecker:
	"""
	检测器组件的基础模块
	"""
	def __init__( self, accountID ):
		"""
		初始化
		"""
		self.accountID = accountID		# 存储玩家账号 entity ID

	def onCheck( self ):
		"""
		检测玩家是否被封号,必须被重写
		"""
		pass

	def clear( self ):
		"""
		还原checker数据， 必须被重写
		"""
		pass

	def account( self ):
		"""
		获取玩家的账号
		"""
		try:
			return BigWorld.entities[self.accountID]
		except:
			ERROR_MSG( "account is not exist, id = %s" % self.accountID )
			return None



class BlockChecker( BaseChecker ):
	"""
	账号封存检测组件
	"""
	def __init__( self, accountID ):
		"""
		初始化
		"""
		BaseChecker.__init__( self, accountID )

	def onCheck( self ):
		"""
		检测玩家是否被封号
		"""
		if self.checkBlock():							# 账号被封存
			self.checkFailed()							# 通知客户端断开连接
		else:											# 通过检测
			self.account().getChecker().checkAlong()		# 把控制权交还给 Checker

	def checkBlock( self ):
		"""
		检查是否被封号
		@param accountIns : 账号的实例
		@type  accountIns : Account
		"""
		if self.account().block_state:
			now = time.time()
			if now <= self.account().block_end_time or self.account().block_end_time == -1:
				return True
			else:
				self.account().block_state = 0
				self.account().block_end_time = 0
				return False
		return False

	def checkFailed( self ):
		"""
		检查失败 通知账号
		@param accountIns : 账号的实例
		@type  accountIns : Account
		"""
		self.account().onAccountlockedNotify( self.account().block_end_time )		#通知客户端锁住了
		self.account().getChecker().clear()											#释放数据



class PasswdProtect_Matrix( BaseChecker ):
	"""
	密码保护检测组件

	注: 密报卡状态分为三种:
		1- 未绑定
		2- 已绑定
		3- 挂失封停
	"""
	COORDINATENUM = 6	# 要玩家比对的坐标位数( 6代表3个坐标 如 11 21 31 )
	def __init__(  self, accountID  ):
		"""
		初始化
		"""
		BaseChecker.__init__( self, accountID )
		self.passwdPro_state = "" 	# 矩阵卡状态
		self.matrix_value = []		# 矩阵卡的值
		self.answer       = []		# 此次登陆的矩阵卡的答案
		self.position     = 0		# 此次登陆的矩阵卡的坐标
		self.inputTimes   = 0		# 客户端输入矩阵卡值得次数

	def init( self ):
		"""
		读取矩阵卡数据
		"""
		self.passwdPro_state   =  self.account().customData.query( "passwdPro_state")		# 记录当前矩阵卡状态
		matrix_value = self.account().customData.query( "matrix_value")						# 记录当前矩阵卡值

		if not self.passwdPro_state or not matrix_value:
			return

		self.passwdPro_state = int( self.passwdPro_state)
		if matrix_value.find(',') >= 0:
			self.matrix_value = matrix_value.split(',')
		else:
			for i in range( 0, len(matrix_value), 2):
				self.matrix_value.append( matrix_value[i:i+2] )

	def onCheck( self ):
		"""
		数据库中获取相应的数据,并检测矩阵卡状态，通知客户端数据矩阵卡值
		"""
		self.init()								# 读取矩阵卡数据
		if not self.passwdPro_state:
		# 如果没有查找到数据，说明没有绑定密保卡
		# (注：今后可能修改为查看玩家是否有开通密保卡服务,目前开通密保卡服务功能北京方面没有给出是否要做的答复)
			self.account().getChecker().checkAlong()
		elif self.passwdPro_state == 1:
		# 未绑定矩阵卡 让其通过
			self.account().getChecker().checkAlong()
		elif self.passwdPro_state == 2:
		# 开通了矩阵卡 需要通知客户端输入矩阵卡值
			self.position,self.answer = self.random_checkValues()
			self.account().client.input_passwdPro_matrix( self.position, self.inputTimes )	# 发送信息让客户端输入答案
		elif self.passwdPro_state == 3:
		# 挂失封停状态，挂失封停的封停状态有时间限制,如果超过时间,是可以正常登陆的,到达这里说明已经检测过是否封号,
		# 所以这里一定是挂失且封停时间超过的状态，让其登陆。
			self.account().getChecker().checkAlong()


	def random_checkValues( self ):
		"""
		随机矩阵卡的值和矩阵卡值坐标
		"""
		keys   = 0
		values = []
		for i in xrange( 0, self.COORDINATENUM, 2 ):
			cs = random.randint(1,9)
			ip = random.randint(1,9)
			baseValue = 10 ** i
			keys += ( cs * 10 + ip ) * baseValue
			values.insert( 0, self.get_checkValue( cs, ip ) )
		return ( keys,  ",".join( values ) )
		#注: 这里直接返回整型值,当values第一个字符值为0时会被丢弃,但是客户端传输时仍然用此方法转换成整型值，对答案的大小不构成影响

	def get_checkValue( self, cs, ip ):
		"""
		获取相应坐标的check值
		@type  pos : string
		@param pos : 卡值的位置 比如 11
		"""
		#-----计算位置的方式是行数+列数  cs-1  ip-1 是位置的下标
		line = 9 * (cs-1)
		index   = line + (ip - 1)
		return self.matrix_value[ index]

	def check_passwdProMatrixValue( self, value ):
		"""
		检测玩家输入的答案,将结果返回给客户端
		@type  value : STRING
		@param value : 客户端传来的矩阵卡答案
		"""
		if self.ifRightAnswert( value ):
			self.account().client.input_passwdPro_matrix(  self.position, 255 )				# 告诉客户端通过矩阵卡密保检测 255代表通过检测
			self.account().getChecker().checkAlong()											# 把控制权交还给账号检测器
		else:
			self.inputTimes += 1															# 增加数据次数
			self.account().client.input_passwdPro_matrix(  self.position, self.inputTimes  )	# 通知客户端输入错误，返回输入的坐标和次数

	def ifRightAnswert( self, value ):
		"""
		检测客户端到达的数据数否是密保卡的答案
		@type  value : UINT32
		@param value : 客户端传来的矩阵卡答案
		"""
		return (self.answer == value) and (self.answer )

	def clear( self ):
		"""
		恢复部分数据
		"""
		self.answer       = []		# 此次登陆的矩阵卡的答案
		self.position     = 0		# 此次登陆的矩阵卡的坐标
		self.inputTimes   = 0		# 客户端输入矩阵卡值得次数

	def reCheck( self ):
		"""
		再次检测矩阵卡密保
		"""
		self.clear()				# 恢复数据
		self.position,self.answer = self.random_checkValues()
		self.account().client.input_passwdPro_matrix( self.position, self.inputTimes )	# 发送信息让客户端输入答案

class checkBaseSectionMD5( BaseChecker ):
	"""
	Account数据库字段MD5检测器 by 姜毅
	"""
	def __init__( self, accountID ):
		"""
		初始化
		"""
		BaseChecker.__init__( self, accountID )

	def onCheck( self ):
		"""
		Account表的部分字段的MD5检测
		"""
		accountEntity = self.account()
		if accountEntity.checkPropertyMD5():
			INFO_MSG( "%s account md5 check passed"%( accountEntity.playerName ) )
			accountEntity.getChecker().checkAlong()		# 把控制权交还给 Checker
		else:
			ERROR_MSG( "%s account md5 check failed"%( accountEntity.playerName ) )
			accountEntity.statusMessage( csstatus.ACCOUNT_MD5_CHECK_FAILED, "" )
			accountEntity.getChecker().clear()											#释放数据
			accountEntity.logoff()

	def clear( self ):
		"""
		"""
		pass

#---------------checker模块列表---------------
checkers = [									# 注 该列表是有序的，需要按照先后顺序检测。
				BlockChecker,
				PasswdProtect_Matrix,
				checkBaseSectionMD5,
			]