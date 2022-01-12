# -*- coding: gb18030 -*-
"""
怪物掉落物品排列方式列表。
使用方式：
	>>> import LostItemDistr
	>>> print LostItemDistr.instance[10]
	[(0, 0), (0, 2), (0, -2), (2, 0), (-2, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

@var  instance: LostDistrBase的默认实例，外面可以通过这个实例直接获取数据
@type instance: LostDistrBase
"""
# $Id: LostItemDistr.py,v 1.4 2006-01-24 02:32:57 phw Exp $

class LostDistrBase:
	"""
	当怪物死亡时掉落的物品的排列方式，不用担心计算量问题，它只有在第一次模块被import时才会执行，以后使用的时候都是结果
	使用文式：
		>>> instance = LostDistrBase()
		>>> lostItemDistr = instance[level] -> return: [(x,z), (x1, z1), ...]
		
	"""
	
	x = z = 0		# 偏移初始值
	dist = 1
	distrDict = {}

	# 2006-01-07, 根据新的掉落规则,只需要一个掉落分布即可
	DefaultItemDistr = [
						(x, z),
						(x, z - dist),
						(x - dist, z - dist),
						(x - dist, z),
						(x - dist, z + dist),
						(x, z + dist),
						(x + dist, z + dist),
						(x + dist, z),
						(x + dist, z - dist),
						(x, z - dist * 2),
						(x - dist * 2, z),
						(x, z + dist * 2),
						(x + dist * 2, z),
						(x + dist * 2, z - dist * 2),
						(x - dist * 2, z - dist * 2),
						(x - dist * 2, z + dist * 2),
						(x + dist * 2, z + dist * 2),
					]
	
	# 以下的分布不再使用
	distrDict[1] = [
						(x, z), 
						(x, z + dist * 2),
						(x, z - dist * 2),
						(x + dist * 2, z),
						(x - dist * 2, z),
						(x + dist, z + dist),
						(x + dist, z - dist),
						(x - dist, z + dist),
						(x - dist, z - dist),
					]
	distrDict[21] = [
						(x, z),
						(x, z + dist * 2),
						(x, z - dist * 2),
						(x + dist * 2, z),
						(x - dist * 2, z),
						(x + dist, z + dist),
						(x + dist, z - dist),
						(x - dist, z + dist),
						(x - dist, z - dist),
						
						(x, z + dist),
						(x, z - dist),
						(x + dist, z),
						(x - dist, z),
					]
	distrDict[41] = [
						(x, z),
						(x, z + dist),
						(x, z - dist),
						(x + dist, z),
						(x - dist, z),
						
						(x, z + dist * 3),
						(x, z - dist * 3),
						(x + dist * 3, z),
						(x - dist * 3, z),
						(x + dist, z + dist * 2),
						(x + dist, z - dist * 2),
						(x + dist * 2, z + dist),
						(x + dist * 2, z - dist),
						(x - dist, z + dist * 2),
						(x - dist, z - dist * 2),
						(x - dist * 2, z + dist),
						(x - dist * 2, z - dist),
					]
	distrDict[71] = [
						(x, z),
						(x, z + dist),
						(x, z - dist),
						(x + dist, z),
						(x - dist, z),

						(x, z + dist * 2),
						(x, z - dist * 2),
						(x + dist * 2, z),
						(x - dist * 2, z),
						(x + dist, z + dist),
						(x + dist, z - dist),
						(x - dist, z + dist),
						(x - dist, z - dist),

						(x, z + dist * 3),
						(x, z - dist * 3),
						(x + dist * 3, z),
						(x - dist * 3, z),
						(x + dist, z + dist * 2),
						(x + dist, z - dist * 2),
						(x + dist * 2, z + dist),
						(x + dist * 2, z - dist),
						(x - dist, z + dist * 2),
						(x - dist, z - dist * 2),
						(x - dist * 2, z + dist),
						(x - dist * 2, z - dist),
					]

	distrDict[100] = [
						(x, z),
						(x, z + dist),
						(x, z - dist),
						(x + dist, z),
						(x - dist, z),

						(x, z + dist * 2),
						(x, z - dist * 2),
						(x + dist * 2, z),
						(x - dist * 2, z),
						(x + dist, z + dist),
						(x + dist, z - dist),
						(x - dist, z + dist),
						(x - dist, z - dist),

						(x, z + dist * 3),
						(x, z - dist * 3),
						(x + dist * 3, z),
						(x - dist * 3, z),
						(x + dist, z + dist * 2),
						(x + dist, z - dist * 2),
						(x + dist * 2, z + dist),
						(x + dist * 2, z - dist),
						(x - dist, z + dist * 2),
						(x - dist, z - dist * 2),
						(x - dist * 2, z + dist),
						(x - dist * 2, z - dist),

						(x, z + dist * 4),
						(x, z - dist * 4),
						(x + dist * 4, z),
						(x - dist * 4, z),
						(x + dist, z + dist * 3),
						(x + dist, z - dist * 3),
						(x + dist * 2, z + dist * 2),
						(x + dist * 2, z - dist * 2),
						(x + dist * 3, z + dist),
						(x + dist * 3, z - dist),
						(x - dist, z + dist * 3),
						(x - dist, z - dist * 3),
						(x - dist * 2, z + dist * 2),
						(x - dist * 2, z - dist * 2),
						(x - dist * 3, z + dist),
						(x - dist * 3, z - dist),
					]
	# init list
	distrList = distrDict.keys()
	distrList.sort()
	distrList.reverse()
	
	def __getitem__( self, level ):
		"""
		取得某个等级的怪物的爆物品分部列表
		
		@param lv: 表示是哪个等级的
		@type  lv: int
		@return: 包含(x, z)偏移值的tuple的list -> [ (x1, z1), (x2, z2), ... ]，每组tuple表示一个位置的偏移
		"""
		for e in LostDistrBase.distrList:
			if level >= e:
				return LostDistrBase.distrDict[e][:]	# 切片返回，以确保原有的list数量不会改变
		return None		# 如果返回这个，调用者就得检查自己的lv参数是否小于或等于0
		
### end of class LostDistrBase() ###

# 默认实例
# 使用时只要：distrList = instance[level]即可得到分布列表
instance = LostDistrBase()


# $Log: not supported by cvs2svn $
# Revision 1.3  2005/08/31 10:19:05  phw
# no message
#
# Revision 1.2  2005/03/29 09:20:22  phw
# 修改了注释，使其符合epydoc的要求
#"
