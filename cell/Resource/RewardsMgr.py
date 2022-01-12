# -*- coding: utf_8 -*-
#

"""
"""
from bwdebug import *
import random
import time
import Language
import csdefine
import ItemTypeEnum
from CrondScheme import Scheme

from items.ItemDataList import ItemDataList
g_items = ItemDataList.instance()

class Awarder( object ):
	"""
	授奖者，所有奖励都会被提取(fetch())到这个类的实例里面，
	然后各个有奖励需要的地方再根据自己实际情况决定怎么使用。
	"""
	def __init__( self ):
		"""
		"""
		self.items = []
		self.money = 0
		self.tongContribute = 0
		self.exp = 0
		self.potential = 0

	def addItem( self, itemInstance ):
		"""
		"""
		self.items.append( itemInstance )

	def addMoney( self, amount ):
		"""
		"""
		self.money += amount

	def addTongContribute( self, amount ):
		"""
		"""
		self.tongContribute += amount
		
	def addExp( self, exp ):
		"""
		"""
		self.exp += exp
		
	def addPotential( self, amount ):
		"""
		"""
		self.potential += amount

	def combineItem( self ):
		"""
		把所有物品奖励合并
		理论上，这个接口不应该存在，我们也用不上它
		"""
		result = []
		combineD = {}
		for item in self.items:
			# 我们不合并不可叠加或已绑定的物品
			stackable = item.getStackable()
			if stackable <= 1 or item.isBinded():
				result.append( item )

			if item.id not in combineD:
				combineD[item.id] = item
			else:
				it = combineD[item.id]
				remnant = it.getAmount() + item.getAmount() - stackable

				if remnant >= 0:
					# 可以撑满，叠满后放入result表中，并从combineD表中移除
					it.setAmount( stackable )
					result.append( it )
					del combineD[item.id]
					if remnant > 0:
						# 有多了，把item的数量设成剩余数量，并放到combineD表中
						item.setAmount( remnant )
						combineD[item.id] = item
				else:
					# 撑不满，直接加进去
					it.setAmount( it.getAmount() + item.getAmount() )

		self.items = result
		
		
	def award( self, awardee, reason ):
		"""
		直接给奖励

		@param awardee: player entity
		@param reason: 给予的原因（awardee是因为什么原因而获得这个奖励）
		@return result of award : BOOL
		"""
		for item in self.items:
			if not awardee.addItemAndNotify_( item, reason ):		# 添加失败
				return False
		if self.money != 0:
			awardee.addMoney( self.money, reason )
			
		if self.exp != 0:
			awardee.addExp( self.exp, reason )
			
		if self.tongContribute != 0:
			awardee.tong_addContribute( self.tongContribute )
			
		if self.potential != 0:
			awardee.addPotential( self.potential )
			
		return True
		
		
	def awardReturnExceedItems( self, awardee, reason ):
		"""
		给奖励,同时以list形式返回不能正确给与玩家的奖励

		@param awardee: player entity
		@param reason: 给予的原因（awardee是因为什么原因而获得这个奖励）
		@return result of award : LIST of items
		"""
		exceedItems = []
		for item in self.items:
			addState = awardee.addItem_( item, reason )
			if addState != csdefine.KITBAG_ADD_ITEM_SUCCESS:	# 添加失败
				exceedItems.append( item )
		if self.money != 0:
			awardee.addMoney( self.money, reason )
			
		return exceedItems

# ------------------------------------------------------------------------
"""
reward_obj ::= RewardEmpty | RewardItem | RewardGroup | RewardRandom | RewardLevel
RewardEmpty ::= no reward

RewardItem ::= itemID amount
itemID ::= digit*
amount ::= digit*
digit ::= "0"..."9"

RewardGroup ::= reward_obj*
odds ::= digit*

RewardRandom ::= (odds reward_obj)*

RewardLevel ::= (level reward_obj)*
"""
class Reward( object ):
	"""
	基类
	"""
	def __init__( self, rewardDict ):
		"""
		@param dataSection: instance of resmgr.DataSection
		"""
		self.uid = int(rewardDict["uid"])		# 用于标识其唯一性的uid


	def fetch( self, awarder, awardee ):
		"""
		提取奖品到awarder

		@param awarder: Awarder实例（授奖者）
		@param awardee: 奖品的获得者（受奖者）
		"""
		assert False

class RewardEmpty( Reward ):
	"""
	空奖励，什么都不奖励，用于做占位符，
	以实现例如在随机奖励下一定机率不掉东西的需求。
	<reward_obj>
		<uid></uid>
		<type>RewardEmpty</type>
	<reward_obj/>
	"""
	def fetch( self, awarder, awardee ):
		"""
		提取奖品到awarder

		@param awarder: Awarder实例（授奖者）
		@param awardee: 奖品的获得者（受奖者）
		"""
		return

class RewardCombo( Reward ):
	"""
	组合型奖励，通过奖励ID去获得另一个奖励
	<reward_obj>
		<uid></uid>
		<type>RewardCombo</type>
		<itemID>comboRewardID</itemID>
	<reward_obj/>
	"""
	def __init__( self, rewardDict ):
		Reward.__init__( self, rewardDict )
		self.comboRewardIDs_ = []
		# init instance of Reward
		INFO_MSG(str(rewardDict))
		for sonRewardDict in rewardDict["itemList"]:
		    self.comboRewardIDs_.append(int(sonRewardDict['rewardID']))

	def fetch( self, awarder, awardee ):
		"""
		"""
		from Love3 import g_rewards
		for rewardID in self.comboRewardIDs_:
			
			aw = g_rewards._datas.get(rewardID)
			if aw is None:
				ERROR_MSG( "Reward Combo,reward data %d not exist."%rewardID )
				continue
			aw.fetch( awarder, awardee )

class RewardMoney( Reward ):
	"""
	金钱奖励
	<reward_obj>
		<uid></uid>
		<type>RewardMoney</type>
		<amount>20</amount>
	<reward_obj/>
	"""
	def __init__( self, rewardDict ):
		Reward.__init__( self, rewardDict )
		self._amount = int(rewardDict["amount"])

	def fetch( self, awarder, awardee ):
		"""
		"""
		awarder.addMoney( self._amount )

class RewardEquip( Reward ):
	"""
	单个装备物品奖励
	<reward_obj>
		<uid></uid>
		<type>RewardEquip</type>
		<itemID></itemID>
	<reward_obj/>
	"""
	def __init__( self, rewardDict ):
		Reward.__init__( self, rewardDict )
		self.itemID_ = int( rewardDict["itemID"] )

	def fetch( self, awarder, awardee ):
		"""
		"""
		#这个接口可能要修改
		item = g_items.createDynamicItem( self.itemID_, 1)
		if item is not None:
			awarder.addItem( item )
			
class RewardPotential( Reward ):
	"""
	潜能奖励
	<reward_obj>
		<uid></uid>
		<type>RewardPotential</type>
		<amount></amount>
	<reward_obj/>
	"""
	def __init__( self, rewardDict ):
		Reward.__init__( self, rewardDict )
		self.amount_ = int(rewardDict["amount"])

	def fetch( self, awarder, awardee ):
		"""
		"""
		awarder.addPotential( self.amount_ )#这个接口可能要修改

class RewardExperience( Reward ):
	"""
	经验奖励
	<reward_obj>
		<uid></uid>
		<type>RewardExperience</type>
		<amount></amount>
	<reward_obj/>
	"""
	def __init__( self, rewardDict ):
		Reward.__init__( self, rewardDict )
		self.amount_ = int(rewardDict["amount"])

	def fetch( self, awarder, awardee ):
		"""
		"""
		awarder.addExp( self.amount_ )#这个接口可能要修改

class RewardTongContribute( Reward ):
	"""
	帮贡奖励
	
	<reward_obj>
		<uid></uid>
		<type>RewardTongContribute</type>
		<amount></amount>
	<reward_obj/>
	"""
	def __init__( self, rewardDict ):
		Reward.__init__( self, rewardDict )
		self.amount_ = int(rewardDict["amount"])

	def fetch( self, awarder, awardee ):
		"""
		"""
		awarder.addTongContribute( self.amount_ )

class RewardItem( Reward ):
	"""
	单个物品奖励
	<reward_obj>
		<uid></uid>
		<type>RewardItem</type>
		<itemID></itemID>
		<amount></amount>
	<reward_obj/>
	"""
	def __init__( self, rewardDict ):
		Reward.__init__( self, rewardDict )
		self.itemID_ = int(rewardDict["itemID"])
		self.amount_ = int(rewardDict["amount"])
		if rewardDict.has_key("needBind") and int(rewardDict["needBind"]) == 0:
			self.needBind = False
		else:
			self.needBind = True

	def fetch( self, awarder, awardee ):
		"""
		"""
		if g_items.getStacCount( self.itemID_ ) > 1:
			item = g_items.createDynamicItem( self.itemID_, self.amount_ )
			if self.needBind:
				item.setBindType( ItemTypeEnum.CBT_PICKUP,awardee )		# 根据奖励工程里的物品配置决定是否无条件绑定该物品
			if item is not None:
				awarder.addItem( item )
		else:
			for i in xrange( self.amount_ ):
				item = g_items.createDynamicItem( self.itemID_ )
				if self.needBind:
					item.setBindType( ItemTypeEnum.CBT_PICKUP,awardee )
				if item is not None:
					awarder.addItem( item )

class RewardItemFitLevel( Reward ):
	"""
	在奖励时才能确定物品级别的单个物品奖励
	如果self.level_ == -1那么物品级别为awardee.getLevel()，否则为配置的级别
	
	<reward_obj>
		<uid></uid>
		<type>RewardItem</type>
		<itemID></itemID>
		<amount></amount>
		<itemLevel></itemLevel>
	<reward_obj/>
	"""
	def __init__( self, rewardDict ):
		Reward.__init__( self, rewardDict )
		self.itemID_ = int(rewardDict["itemID"])
		self.amount_ = int(rewardDict["amount"])
		self.level_ = int(rewardDict["itemLevel"])
		if rewardDict.has_key("needBind") and int(rewardDict["needBind"]) == 0:
			self.needBind = False
		else:
			self.needBind = True
		
	def fetch( self, awarder, awardee ):
		"""
		"""
		level = self.level_
		if level <= 0:
			level = awardee.getLevel()
		if g_items.getStacCount( self.itemID_ ) > 1:
			item = g_items.createDynamicItem( self.itemID_, self.amount_ )
			if self.needBind:
				item.setBindType( ItemTypeEnum.CBT_PICKUP,awardee )		# 根据奖励工程里的物品配置决定是否无条件绑定该物品
			if item is not None:
				item.setLevel( level )
				awarder.addItem( item )
		else:
			for i in xrange( self.amount_ ):
				item = g_items.createDynamicItem( self.itemID_ )
				if self.needBind:
					item.setBindType( ItemTypeEnum.CBT_PICKUP,awardee )
				if item is not None:
					item.setLevel( level )
					awarder.addItem( item )

class RewardItemInHour( Reward ):
	"""
	在限定时间（Hour）内单个物品奖励
	stratHour 开始钟点
	lastHour  持续小时
	<reward_obj>
		<uid></uid>
		<type>RewardItemInHour</type>
		<startHour></startHour>
		<lastHour></lastHour>
		<itemID></itemID>
		<amount></amount>
	<reward_obj/>
	"""
	def __init__( self, rewardDict ):
		Reward.__init__( self, rewardDict )
		self.startHour_ = int(rewardDict["startHour"])
		self.lastHour_ = int(rewardDict["lastHour"])
		self.itemID_ = int(rewardDict["itemID"])
		self.amount_ = int(rewardDict["amount"])
		if rewardDict.has_key("needBind") and int(rewardDict["needBind"]) == 0:
			self.needBind = False
		else:
			self.needBind = True

	def timeCheck( self ):
		"""
		根据时间检测奖励合法性
		"""
		nowHour = time.localtime()[3]	# 当前钟点
		endHour = self.startHour_ + self.lastHour_
		intervalTime = endHour%24
		if intervalTime == 0:
			if nowHour in xrange( self.startHour_, endHour ):
				return True
		else:
			if nowHour in xrange( self.startHour_, 24 ) or nowHour in xrange( 0, intervalTime ):
				return True
		return False

	def fetch( self, awarder, awardee ):
		"""
		"""
		if not self.timeCheck(): return
		if g_items.getStacCount( self.itemID_ ) > 1:
			item = g_items.createDynamicItem( self.itemID_, self.amount_ )
			if self.needBind:
				item.setBindType( ItemTypeEnum.CBT_PICKUP,awardee )		# 根据奖励工程里的物品配置决定是否无条件绑定该物品
			if item is not None:
				awarder.addItem( item )
		else:
			for i in xrange( self.amount_ ):
				item = g_items.createDynamicItem( self.itemID_ )
				if self.needBind:
					item.setBindType( ItemTypeEnum.CBT_PICKUP,awardee )
				if item is not None:
					awarder.addItem( item )

class RewardRandomEquip( Reward ):
	"""
	随机属性装备
	<reward_obj>
		<uid></uid>
		<type>RewardRandomEquip</type>
		<itemID></itemID>
		<quality></quality>
		<prefix></prefix>
	<reward_obj/>

	"""
	def __init__( self, rewardDict ):
		Reward.__init__( self, rewardDict )

		# 初始化随机属性
		self.itemID_ = int(rewardDict["itemID"])
		self.quality_ = int(rewardDict["quality"])
		self.prefix_ = int(rewardDict["prefix"])
		if rewardDict.has_key("needBind") and int(rewardDict["needBind"]) == 0:
			self.needBind = False
		else:
			self.needBind = True


	def fetch( self, awarder, awardee ):
		"""
		"""
		item = g_items.createDynamicItem( self.itemID_, 1 )
		if self.needBind:
			item.setBindType( ItemTypeEnum.CBT_PICKUP,awardee )		# 根据奖励工程里的物品配置决定是否无条件绑定该物品
		if item is not None:
			if self.quality_ > 0 and self.prefix_ > 0:
				item.setQuality( self.quality_ )
				item.setPrefix( self.prefix_ )
				if not item.createRandomEffect():
					ERROR_MSG( "getDropItem createRandomEffect failed, item %s, quality %s, prefix %s " % ( self.itemID_, self.prefix_, self.prefix_ ) )
			awarder.addItem( item )

class RewardGroup( Reward ):
	"""
	一次奖励一批
	element是配合DICT中的LIST结构的层标签，该标签并不在DICT中以key的形式表现
	<reward_obj>
		<uid></uid>
		<type>RewardGroup</type>
		<name></name>
		<itemList>
			<element>
				<item>
					<reward_obj>
						<uid></uid>
						<type></type>
						<other param.../>
					</reward_obj>
				</item>
			</element>
			<element>
				<item>
					<reward_obj>
						<uid></uid>
						<type></type>
						<other param.../>
					</reward_obj>
				</item>
			</element>
		</itemList>
	<reward_obj/>
	"""
	def __init__( self, rewardDict ):
		Reward.__init__( self, rewardDict )
		self._rewards = []		# list of Reward

		from Love3 import g_rewards
		# init instance of Reward
		for sonRewardDict in rewardDict["itemList"]:
			sonReward = newReward(sonRewardDict['item'])
			self._rewards.append(sonReward)
			
			if not g_rewards._datas.get( sonReward.uid ) and sonRewardDict['item'].has_key('name'):
				g_rewards._datas[sonReward.uid] = sonReward
		
	def fetch( self, awarder, awardee ):
		"""
		"""
		for r in self._rewards:
			r.fetch( awarder, awardee )

class RewardTongFete( RewardGroup ):
	"""
	帮会祭祀奖励
	
	<reward_obj>
		<uid></uid>
		<type>RewardTongFete</type>
		<name></name>
		<itemList>
			<element>
				<item>
					<level></level>
					<quality></quality>
					<reward_obj>
						<uid></uid>
						<type></type>
						<other param.../>
					</reward_obj>
				</item>
			</element>
			<element>
				<item>
					<level></level>
					<quality></quality>
					<reward_obj>
						<uid></uid>
						<type></type>
						<other param.../>
					</reward_obj>
				</item>
			</element>
		</itemList>
	<reward_obj/>
	"""
	def __init__( self, rewardDict ):
		Reward.__init__( self, rewardDict )
		self._rewards = {}		# list of Reward
		
		from Love3 import g_rewards
		for level1RewardDict in rewardDict["itemList"]:
			quality = int(level1RewardDict["quality"])
			level = int(level1RewardDict["level"])
			reward = newReward( level1RewardDict["item"] )
			self._rewards[(level, quality)] = reward
			
			if not g_rewards._datas.get( reward.uid )and level1RewardDict["item"].has_key('name'):
				g_rewards._datas[reward.uid] = reward
			
	def fetch( self, awarder, awardee ):
		"""
		"""
		order = awardee.queryTemp( "FeteRewardGiveItemOrder", -1 )
		if order == -1:
			return
		item = awardee.getItem_( order )
		if item is None or item.isFrozen():
			ERROR_MSG( "仙灵换物奖励提交的物品(order:%i)不存在或被冻结。" % order )
			return
		mapLevel = item.getLevel() / 10 * 10	# 去掉个位数，获得装备的等级段
		self._rewards[(mapLevel, item.getQuality())].fetch( awarder, awardee )
		
class RewardSpecialTime( RewardGroup ):
	"""
	特定时间一次奖励一批
	
	element是配合DICT中的LIST结构的层标签，该标签并不在DICT中以key的形式表现
	<reward_obj>
		<uid></uid>
		<type>RewardGroup</type>
		<name></name>
		<startTime></startTime>
		<persistentTime></persistentTime>
		<itemList>
			<element>
				<item>
					<reward_obj>
						<uid></uid>
						<type></type>
						<other param.../>
					</reward_obj>
				</item>
			</element>
			<element>
				<item>
					<reward_obj>
						<uid></uid>
						<type></type>
						<other param.../>
					</reward_obj>
				</item>
			</element>
		</itemList>
	<reward_obj/>
	"""
	def __init__( self, rewardDict ):
		"""
		"""
		RewardGroup.__init__( self, rewardDict )
		self.startScheme = Scheme( rewardDict["startTime"] )
		self.persistentTime = int( rewardDict["persistentTime"] ) * 60
		
	def fetch( self, awarder, awardee ):
		"""
		"""
		now = time.time()
		# 由于使用开始时间来判定是否处于特定时间内，那么需要把开始时间往前推一个持续时间，否则如果过了开始时间但处于可以给奖励的持续时间内，那么也不会给奖励
		year, month, day, hour, minute = time.localtime( now - self.persistentTime )[0:5]
		nextTime = self.startScheme.calculateNext( year, month, day, hour, minute )
		if nextTime < now:	# 还在特定时间内
			RewardGroup.fetch( self, awarder, awardee )
			
class RewardRandom( Reward ):
	"""
	随机奖励
	element是配合DICT中的LIST结构的层标签，该标签并不在DICT中以key的形式表现
	<reward_obj>
		<uid></uid>
		<type>RewardRandom</type>
		<amount>2</amount>
		<name></name>
		<itemList>
			<element>
				<odds>10</odds>
				<item>
					<reward_obj>
						<uid></uid>
						<type></type>
						<other param.../>
					</reward_obj>
				</item>
			</element>
			<element>
				<odds>20</odds>
				<item>
					<reward_obj>
						<uid></uid>
						<type></type>
						<other param.../>
					</reward_obj>
				</item>
			</element>
		</itemList>
	<reward_obj/>
	"""
	def __init__( self, rewardDict ):
		Reward.__init__( self, rewardDict )

		self._amount = 0		# 随机奖励数量
		self._oddsTotle = 0		# 机率总值，即所有奖励的机率总和
		# list of tuple like as [(odds, Reward), ...]
		# 一个以odds为排序依据升序排列的列表。
		self._rewards = []

		# init instance of Reward
		self._amount = int(rewardDict["amount"])
		assert self._amount > 0, "uid %s" % self.uid
		
		from Love3 import g_rewards
		for sonRewardDict in rewardDict["itemList"]:
			odds = int(sonRewardDict["odds"])
			self._oddsTotle += odds
			reward = newReward(sonRewardDict['item'])
			self._rewards.append( (self._oddsTotle, reward) )
			
			if not g_rewards._datas.get( reward.uid )and sonRewardDict['item'].has_key('name'):
				g_rewards._datas[reward.uid] = reward

	def fetch( self, awarder, awardee ):
		"""
		"""
		for e in xrange( self._amount ):
			odds = random.randint( 1, self._oddsTotle )
			for r, reward in self._rewards:
				if odds <= r:
					reward.fetch( awarder, awardee )
					break

class RewardRandom2( Reward ):
	"""
	随机奖励2
	element是配合DICT中的LIST结构的层标签，该标签并不在DICT中以key的形式表现
	这个与RewardRandom的差别在于：
		·RewardRandom在一堆奖励中随机抽取一个
		·RewardRandom2是对每一个奖励进行一次命中判断，
		　如果命中了就对该奖励进行奖励提取。
		　而且，此方案可以使用RewardRandom与RewardEmpty组合达成相同的效果，
		　提供此类型，仅仅是为了方便配置时减少层次。
	<reward_obj>
		<uid></uid>
		<type>RewardRandom2</type>
		<amount>2</amount>
		<name></name>
		<itemList>
			<element>
				<odds>10</odds>
				<oddsRange>100</oddsRange>
				<item>
					<reward_obj>
						<uid></uid>
						<type></type>
						<other param.../>
					</reward_obj>
				</item>
			</element>
			<element>
				<odds>20</odds>
				<oddsRange>100</oddsRange>
				<item>
					<reward_obj>
						<uid></uid>
						<type></type>
						<other param.../>
					</reward_obj>
				</item>
			</element>
		</itemList>
	<reward_obj/>
	"""
	def __init__( self, rewardDict ):
		Reward.__init__( self, rewardDict )

		self._amount = 0		# 随机奖励数量
		self._rewards = []		# list of tuple like as [(odds, oddsRange, Reward), ...]

		# init instance of Reward
		self._amount = int(rewardDict["amount"])
		assert self._amount > 0, "uid %s" % self.uid

		from Love3 import g_rewards
		for sonRewardDict in rewardDict["itemList"]:
			# 产生新的奖励实例
			reward = newReward(sonRewardDict['item'])
			if reward is None:
				continue

			# 获取机率
			# 机率(x%) = odds / oddsRange
			odds = int(sonRewardDict["odds"])				# 命中机率
			oddsRange = int(sonRewardDict["oddsRange"])		# 随机值取值范围
			assert oddsRange > odds, "uid %s" % self.uid

			self._rewards.append( (odds, oddsRange, reward) )
			
			if not g_rewards._datas.get( reward.uid )and sonRewardDict['item'].has_key('name'):
				g_rewards._datas[reward.uid] = reward

	def fetch( self, awarder, awardee ):
		"""
		"""
		for e in xrange( self._amount ):
			for odds, oddsRange, reward in self._rewards:
				if random.randint( 1, oddsRange ) <= odds:
					reward.fetch( awarder, awardee )

class RewardLevel( Reward ):
	"""
	按等级决定奖励
	element是配合DICT中的LIST结构的层标签，该标签并不在DICT中以key的形式表现
	<reward_obj>
		<uid></uid>
		<type>RewardLevel</type>
		<name></name>
		<itemList>
			<element>
				<level>10</level>
				<item>
					<reward_obj>
						<uid></uid>
						<type></type>
						<other param.../>
					</reward_obj>
				</item>
			</element>
			<element>
				<level>11</level>
				<item>
					<reward_obj>
						<uid></uid>
						<type></type>
						<other param.../>
					</reward_obj>
				</item>
			</element>
		</itemList>
	<reward_obj/>
	"""
	def __init__( self, rewardDict ):
		Reward.__init__( self, rewardDict )
		self._rewards = []		# list of Reward; index is level - 1 and value is Reward

		# init instance of Reward
		lvs = [int( e["level"] ) for e in rewardDict["itemList"]]
		maxLv = max( lvs )
		assert maxLv < 500
		self._rewards =  [ None, ] * maxLv	# 用最大等级铺开成列表
		
		from Love3 import g_rewards
		for section in rewardDict["itemList"]:
			lv = int(section["level"])
			reward = newReward( section["item"] )
			self._rewards[lv-1] = reward
			
			if not g_rewards._datas.get( reward.uid )and section["item"].has_key('name'):
				g_rewards._datas[reward.uid] = reward

	def fetch( self, awarder, awardee ):
		"""
		"""
		lv = awardee.level - 1
		try:
			value = self._rewards[lv]
		except IndexError:
			return

		if value is not None:
			value.fetch( awarder, awardee )

class RewardGroupByGenderClassic( Reward ):
	"""
	基于性别和职业一批物品奖励 by 姜毅
	element是配合DICT中的LIST结构的层标签，该标签并不在DICT中以key的形式表现
	<reward_obj>
		<uid></uid>
		<type>RewardGroupByGenderClassic</type>
		<name></name>
		<itemList>
			<element>
				<gender>0</gender>
				<classic>16</classic>
				<item>
					<reward_obj>
						<uid></uid>
						<type></type>
						<other param.../>
					</reward_obj>
				</item>
			</element>
			<element>
				<gender>0</gender>
				<classic>16</classic>
				<item>
					<reward_obj>
						<uid></uid>
						<type></type>
						<other param.../>
					</reward_obj>
				</item>
			</element>
		</itemList>
	<reward_obj/>
	"""
	def __init__( self, rewardDict ):

		Reward.__init__( self, rewardDict )
		self._rewards = {}		# dict of Reward; index is gender-classic and value is Reward
		
		from Love3 import g_rewards
		for sonRewardDict in rewardDict["itemList"]:
			#if section.name != "item":
			#	continue
			gender = int(sonRewardDict["gender"])
			classic = int(sonRewardDict["classic"])
			if not self._rewards.has_key( gender ):
				self._rewards[gender] = {}
			if not self._rewards[gender].has_key( classic ):
				self._rewards[gender][classic] = []
			reward = newReward(sonRewardDict['item'] )
			self._rewards[gender][classic].append(reward)
			
			if not g_rewards._datas.get( reward.uid )and sonRewardDict['item'].has_key('name'):
				g_rewards._datas[reward.uid] = reward

	def fetch( self, awarder, awardee ):
		"""
		"""
		if awarder is None: return
		gender = awardee.getGender()
		classic = awardee.getClass()
		value = []
		try:
			value = self._rewards[gender][classic]
		except IndexError:
			return

		if len( value ) <= 0: return
		for rew in value:
			rew.fetch( awarder, awardee )

class RewardInHour( Reward ):
	"""
	在限定时间（Hour）内的一批奖励
	stratHour 开始钟点
	lastHour  持续小时
	<reward_obj>
		<uid></uid>
		<type>RewardInHour</type>
		<startHour></startHour>
		<lastHour></lastHour>
		<itemList>
			<element>
				<gender>0</gender>
				<classic>16</classic>
				<item>
					<reward_obj>
						<uid></uid>
						<type></type>
						<other param.../>
					</reward_obj>
				</item>
			</element>
			<element>
				<gender>0</gender>
				<classic>16</classic>
				<item>
					<reward_obj>
						<uid></uid>
						<type></type>
						<other param.../>
					</reward_obj>
				</item>
			</element>
		</itemList>
	<reward_obj/>
	"""
	def __init__( self, rewardDict ):
		Reward.__init__( self, rewardDict )
		self.startHour_ = int(rewardDict["startHour"])
		self.lastHour_ = int(rewardDict["lastHour"])
		self._rewards = []
		
		from Love3 import g_rewards
		for childReward in rewardDict["itemList"]:
			reward = newReward(childReward["item"])
			self._rewards.append( reward )
			
			if not g_rewards._datas.get( reward.uid )and childReward["item"].has_key('name'):
				g_rewards._datas[reward.uid] = reward

	def timeCheck( self ):
		"""
		根据时间检测奖励合法性
		"""
		nowHour = time.localtime()[3]	# 当前钟点
		endHour = self.startHour_ + self.lastHour_
		intervalTime = endHour%24
		if intervalTime == 0:
			if nowHour in xrange( self.startHour_, endHour ):
				return True
		else:
			if nowHour in xrange( self.startHour_, 24 ) or nowHour in xrange( 0, intervalTime ):
				return True
		return False

	def fetch( self, awarder, awardee ):
		"""
		"""
		if not self.timeCheck(): return
		for reward in self._rewards:
			reward.fetch( awarder, awardee )

class RewardByMonster( Reward ):
	"""
	根据怪物(className)来给与一批奖励 by 姜毅
	<reward_obj>
		<uid></uid>
		<type>RewardByMonster</type>
		<monster> monsterClassName </monster>
		<itemList>
			<element>
				<gender>0</gender>
				<classic>16</classic>
				<item>
					<reward_obj>
						<uid></uid>
						<type></type>
						<other param.../>
					</reward_obj>
				</item>
			</element>
			<element>
				<gender>0</gender>
				<classic>16</classic>
				<item>
					<reward_obj>
						<uid></uid>
						<type></type>
						<other param.../>
					</reward_obj>
				</item>
			</element>
		</itemList>
	</reward_obj>
	"""
	def __init__( self, rewardDict ):
		Reward.__init__( self, rewardDict )
		self._monsterCN = rewardDict["monsterClassName"]	# monster class name
		self._rewards = []
		
		from Love3 import g_rewards
		for childReward in rewardDict["itemList"]:
			reward = newReward(childReward["item"])
			self._rewards.append( reward )
			
			if not g_rewards._datas.get( reward.uid )and childReward["item"].has_key('name'):
				g_rewards._datas[reward.uid] = reward
			
	def fetch( self, awarder, awardee ):
		"""
		"""
		if awardee.className == self._monsterCN:
			for reward in self._rewards:
				reward.fetch( awarder, awardee )

class ShareSonReward( Reward ):
	"""
	共用表格
	<reward_obj>
		<uid></uid>
		<amount></amount>
		<type></type>
		<ref_name></ref_name>
		<ref_type></ref_type>
		<ref_uid></ref_uid>
	</reward_obj>
	"""
	def __init__( self, rewardDict ):
		Reward.__init__( self, rewardDict )
		self._amount = 0
		if rewardDict["amount"]:
			self._amount = int( rewardDict["amount"] )
		
		self.ref_uid = None
		self.ref_uid = int( rewardDict["ref_uid"] )
		assert self.ref_uid is not None, "uid %s" % self.uid
		
		self._rewards = None
		
	def fetch( self, awarder, awardee ):
		
		from Love3 import g_rewards
		self._rewards = g_rewards._datas.get( self.ref_uid )
		if not self._rewards:
			ERROR_MSG( "refers reward project config: %s not exist."%self.ref_uid )
			return
		if hasattr( self._rewards, "_amount"):
			amount = self._rewards._amount
			self._rewards._amount = self._amount
			self._rewards.fetch( awarder,awardee )
			self._rewards._amount = amount
		else:
			self._rewards.fetch( awarder,awardee )
# ------------------------------------------------------------------------
class RewardsMgr( object ):
	"""
	配置加载器
	"""
	_instance = None
	def __init__( self ):
		"""
		"""
		self._datas = {}	# key == Reward.uid, value == instance of Reward
		self.rewardSecs = Language.openConfigSection("config/server/rewards")
		
	@classmethod
	def instance( SELF ):
		"""
		"""
		if SELF._instance is None:
			SELF._instance = RewardsMgr()
		return SELF._instance
		
	def addRewardProj( self, projectFileName ):
		"""
		读取奖励配置工程以加载奖励工程
		"""
		p = "entities/%s/config/server/rewards/%s"%( Language._LANG_CONFIG_STRING_MAPPING[Language.LANG], projectFileName )
		o = open(p, 'r')
		s = o.read()
		s = s.replace( '\r', '' )
		t = compile(s,'','exec')
		exec t
		f_modulenames = RewardProjDict["rewardFile"].itervalues()
		o.close()
		for modulename in f_modulenames:
			modulename = modulename.replace('./', '')
			modulename = modulename.replace('.py', '')
			if self.rewardSecs.has_key( modulename + ".py" ) or self.rewardSecs.has_key( modulename + ".pyc" ):
				modulename = "config/server/rewards/%s" % modulename
				mod = __import__( modulename )
				self.addConfig( mod.rewardConfigDict )
			else:
				ERROR_MSG( "reward project config %s not exist."%modulename )

	def addConfig( self, rewardDict ):
		"""
		初始化配置
		"""
		if rewardDict is None:
			ERROR_MSG( "open '%s' fault" % rewardDict )
			return
		award = newReward( rewardDict )
		self._datas[award.uid] = award

	def fetch( self, awardID, awardee ):
		"""
		提取奖品到awarder

		@param awardID: 奖品配置的uid
		@param awardee: 奖品的获得者（受奖者）
		@return: instance of Awarder
		"""
		if awardID not in self._datas:
			ERROR_MSG( "I has no such award -- '%s'" % awardID )
			return None

		awarder = Awarder()
		awardInstance = self._datas[awardID]
		awardInstance.fetch( awarder, awardee )
		return awarder

# ------------------------------------------------------------------------
__g_type = {
		"RewardEmpty"		: RewardEmpty,
		"RewardCombo"	: RewardCombo,
		"RewardItem"		: RewardItem,
		"RewardGroup"		: RewardGroup,
		"RewardRandom"		: RewardRandom,
		"RewardLevel"		: RewardLevel,
		"RewardRandomEquip"	: RewardRandomEquip,
		"RewardEquip"		:RewardEquip,
		"RewardPotential"	:RewardPotential,
		"RewardExperience"	:RewardExperience,
		"RewardMoney"		:RewardMoney,
		"RewardItemInHour"	:RewardItemInHour,
		"RewardRandom2"		:RewardRandom2,
		"RewardGroupByGenderClassic":RewardGroupByGenderClassic,
		"RewardTongFete":RewardTongFete,
		"RewardTongContribute":RewardTongContribute,
		"RewardInHour":RewardInHour,
		"RewardByMonster":RewardByMonster,
		"RewardSpecialTime":RewardSpecialTime,
		"RewardItemFitLevel":RewardItemFitLevel,
		"ShareSonReward":ShareSonReward,
	}

def newReward( rewardDict ):
	"""
	"""
	try:
		c = __g_type[rewardDict["type"]]
	except KeyError, errstr:
		ERROR_MSG( "invalid reward type '%s'." % errstr )
		return None

	return c( rewardDict )

# Rewards.py