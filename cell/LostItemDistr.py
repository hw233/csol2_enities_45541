# -*- coding: gb18030 -*-
"""
���������Ʒ���з�ʽ�б�
ʹ�÷�ʽ��
	>>> import LostItemDistr
	>>> print LostItemDistr.instance[10]
	[(0, 0), (0, 2), (0, -2), (2, 0), (-2, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

@var  instance: LostDistrBase��Ĭ��ʵ�����������ͨ�����ʵ��ֱ�ӻ�ȡ����
@type instance: LostDistrBase
"""
# $Id: LostItemDistr.py,v 1.4 2006-01-24 02:32:57 phw Exp $

class LostDistrBase:
	"""
	����������ʱ�������Ʒ�����з�ʽ�����õ��ļ��������⣬��ֻ���ڵ�һ��ģ�鱻importʱ�Ż�ִ�У��Ժ�ʹ�õ�ʱ���ǽ��
	ʹ����ʽ��
		>>> instance = LostDistrBase()
		>>> lostItemDistr = instance[level] -> return: [(x,z), (x1, z1), ...]
		
	"""
	
	x = z = 0		# ƫ�Ƴ�ʼֵ
	dist = 1
	distrDict = {}

	# 2006-01-07, �����µĵ������,ֻ��Ҫһ������ֲ�����
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
	
	# ���µķֲ�����ʹ��
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
		ȡ��ĳ���ȼ��Ĺ���ı���Ʒ�ֲ��б�
		
		@param lv: ��ʾ���ĸ��ȼ���
		@type  lv: int
		@return: ����(x, z)ƫ��ֵ��tuple��list -> [ (x1, z1), (x2, z2), ... ]��ÿ��tuple��ʾһ��λ�õ�ƫ��
		"""
		for e in LostDistrBase.distrList:
			if level >= e:
				return LostDistrBase.distrDict[e][:]	# ��Ƭ���أ���ȷ��ԭ�е�list��������ı�
		return None		# �����������������߾͵ü���Լ���lv�����Ƿ�С�ڻ����0
		
### end of class LostDistrBase() ###

# Ĭ��ʵ��
# ʹ��ʱֻҪ��distrList = instance[level]���ɵõ��ֲ��б�
instance = LostDistrBase()


# $Log: not supported by cvs2svn $
# Revision 1.3  2005/08/31 10:19:05  phw
# no message
#
# Revision 1.2  2005/03/29 09:20:22  phw
# �޸���ע�ͣ�ʹ�����epydoc��Ҫ��
#"
