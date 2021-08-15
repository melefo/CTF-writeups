#!/usr/bin/python3

from pwn import *
from itertools import permutations

chal, port = "None", None
#context.log_level = 'debug'

re = lambda : io.recvline()
ru = lambda a: io.recvuntil(a)
s  = lambda a: io.sendline(a)
distance = lambda a, b: abs(a[0]-b[0])+abs(a[1]-b[1])
direction = lambda a, b: (b-a)//abs(b-a) if a-b else 1
prompt = b"Enter move in the format 'current-x-cord,current-y-cord,to-x-cord,to-y-cord ' : "

class blk:
	def __init__(self, i, a, b, sz):
		self.name = i
		self.sz = sz
		self.cur_pos = a
		self.end_pos = b
		self.dist = distance(a, b)
		self.steps = gen_steps(a, b)
		assert len(self.steps[0]) == self.dist

	def update(self, i):
		val = self.steps[i]
		self.steps = {0: val[1:]}
		self.dist -= 1
		self.cur_pos = val[0][2:]

	def __repr__(self):
		return f"\n\nName: {self.name}\nCurrent Position: {self.cur_pos}\nEnd Position: {self.end_pos}\nDistance: {self.dist}\nSteps: {self.steps}\n\n"

def gen_steps(a, b):
	dist = distance(a, b)
	base = [1]*abs(a[0]-b[0])+[0]*abs(a[1]-b[1])
	steps, tmp = {}, a[:]
	for ctr, i in enumerate(set(permutations(base))):
		steps[ctr], a = [], tmp[:]
		for j in range(dist):
			if i[j]:
				shift = [a[0]+direction(a[0], b[0]), a[1]]
				steps[ctr] += [a+shift]
				a = shift
			else:
				shift = [a[0], a[1]+direction(a[1], b[1])]
				steps[ctr] += [a+shift]
				a = shift
	return steps

def find_index(arr):
	ret={}
	for i in range(len(arr)):
		for j in range(len(arr)):
			if '0' != arr[i][j] and 0!=arr[i][j]:
				ret[arr[i][j]]=[i,j]
	return ret

def parse(lvl, sol):
	idxl = find_index(lvl)
	idxs = find_index(sol)
	lst  = [blk(i, idxl[i], idxs[i], len(idxl)) for i in idxl.keys()]
	return sorted( lst, key=lambda a: a.dist, reverse=True)	

def get_info(io):
    x = io.recvuntil(b':').decode()
    moves=int(io.recvline().decode().strip().split()[0])
    x = io.recvuntil(b'moves').decode()
    lev = []
    sol = []
    for i in x.split('\n'):
        if('|' in i):
            y = i.replace('\t', '').replace(' ', '').split('|')
            while '' in y:
                y.remove('')
            lev.append(y[:len(y)//2])
            sol.append(y[len(y)//2:])
    return moves,lev,sol

def find_route(lst):
	for ctr in range(len(lst)):
		if not lst[ctr].dist: continue
		for i,j in lst[ctr].steps.items():
			if all([all([item[2:]!=obj.cur_pos for obj in lst]) for item in j]):
				lst[ctr].update(i)
				return j[0]
	path = [0, 1, 0, -1]
	for obj in lst:
		if not obj.dist: continue
		a = obj.cur_pos[:]
		for i in range(4):
			item_pos = [a[0]+path[i], a[1]+path[(i+1)%4]]
			if any([ctr not in range(obj.sz) for ctr in item_pos]): continue
			ndist = distance(obj.end_pos, item_pos)
			if all([item_pos!=obj.cur_pos for obj in lst]) and ((obj.dist+1)<=ndist):
				tmp = obj.cur_pos[:]
				obj.cur_pos = item_pos
				obj.dist = ndist
				obj.steps = gen_steps(item_pos, obj.end_pos)
				return tmp+item_pos
	return -1

def main(io):
	moves, lvl, sol = get_info(io)
	print(f"[*] Attempting Level: {len(lvl)-1}")
	lst = parse(lvl, sol)
	for i in range(moves):
		if b'Congrats' in re().strip():
			return 1
		ru(prompt)
		ret = find_route(lst)
		if ret==-1:
			print('oops :(')
			return 0
		s(','.join(map(str, ret)).encode())

if __name__ == '__main__':
	io = remote("misc.challenge.bi0s.in",1337)
	[io.recvuntil(b': ') for _ in range(2)]
	io.sendline(b'y')
	for i in range(9):
		if not main(io):
			exit(0)
	print(io.recvline().decode())
	io.close()
