"""
Robert D. Bates, PhD

Polynomial Class 

After writing x=Poly([0,1]), x can now be used to make polynomails. Like, 
f = (x-1)+x**6
Has many attached functions like, f.roots(), f.derivative(), 
f.convex_hull(), etc.
"""

import numpy as np
from itertools import zip_longest

def prod(iterable,start=1):
    for i in iterable:
        start*=i
    return start

def positive_dot(a,b):
    if (a.conjugate()*b).imag>=0:
        return np.arccos((a.real*b.real+a.imag*b.imag)/np.abs(a*b))
    return 2*np.pi-np.arccos((a.real*b.real+a.imag*b.imag)/np.abs(a*b))

def random_root():
    r = np.random.rand()
    t = 2*np.pi*np.random.rand()
    return r*np.e**(t*1j)

def root_coor(roots):
    return [(r.real,r.imag) for r in roots]

class Poly:
    def __init__(self,polylist,listtype='coefficients'):
        self.round = 2
        while polylist[-1]==0 and len(polylist)>1: 
            polylist.pop(-1)
        for n,i in enumerate(polylist):
            if i.imag==0:
                polylist[n] = [i.real,int(i.real)][i.real==int(i.real)]
            else:
                polylist[n] = [i.real,int(i.real)][i.real==int(i.real)] + [i.imag,int(i.imag)][i.imag==int(i.imag)]*1j
        if listtype=='coefficients':
            self.coefficients = polylist
    def __repr__(self): 
        exp = dict(zip('0123456789','⁰¹²³⁴⁵⁶⁷⁸⁹'))
        exponents = ['','x']+['x'+''.join(exp[i] for i in str(n)) for n in range(2,len(self.coefficients)+1)]
        terms=[]
        for c,e in zip(self.coefficients,exponents):
            c = complex(round(c.real,self.round),round(c.imag,self.round))
            if c==0 and len(self.coefficients)!=1:
                pass
            elif c==0 and len(self.coefficients)==1:
                terms+=['0']
            elif c==1:
                terms+=[[e,'1'][e=='']]
            elif c==-1 and len(terms)>0:
                terms+=['\b-'+e]
            elif abs(c)==-c and len(terms)>0:
                terms+=['\b{}{}'.format(c,e)]
            else:
                terms+=['{}{}'.format(c,e)]
        return '+'.join(terms)
    def __add__(self,other):
        if type(other)!=Poly:
            return Poly([self.coefficients[0]+other]+self.coefficients[1:])
        else:
            return Poly([x+y for x,y in zip_longest(self.coefficients,other.coefficients,fillvalue=0)])
    def __mul__(self,other):
        if type(other)!=Poly:
            return Poly([x*other for x in self.coefficients])
        elif other.coefficients==[0,1]:
            return Poly([0]+self.coefficients)
        else:
            terms = [prod(i*[Poly([0,1])],self)*y for i,y in enumerate(other.coefficients)]
            return sum(terms,Poly([0]))
    def __neg__(self):
        return Poly([-x for x in self.coefficients])
    def __pow__(self,other):
        return prod(other*[self],Poly([1]))
    def __eq__(self,other):
        return (self-other).coefficients == [0]
    def __sub__(self,other):
        return self+(-other)
    def __radd__(self,other):
        return self+other
    def __rsub__(self,other):
        return (-self)+other
    def __rmul__(self,other):
        return self*other
    def roots(self):
        return np.roots(list(reversed(self.coefficients)))
    def evaluate(self,value):
        return self.coefficients[0]+sum(c*value**i for i,c in list(enumerate(self.coefficients))[1:])
    def derivative(self):
        return sum(c*i*Poly([0,1])**(i-1) for i,c in list(enumerate(self.coefficients))[1:])
    def convex_hull(self):
        roots = sorted(self.roots(),key=lambda r: (np.angle(r),-np.abs(r)))
        if len(set(roots)) in [0,1,2]:
            return list(set(roots))
        hull = [roots[0],roots[-1]]
        for i in range(2*len(set(roots))):
            sort = lambda r: positive_dot(hull[-1]-hull[-2],r-hull[-1]) 
            hull+= [sorted([r for r in roots if r not in hull[-2:]],key=sort)[0]]
        start = [n for n,r in list(enumerate(reversed(hull)))[1:] if r==hull[-1]][0]
        return hull[len(hull)-start:]

x = Poly([0,1])


