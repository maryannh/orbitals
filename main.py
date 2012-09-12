#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# orbitals. andershoff.net
# inspired by complexification.net
#
# master

import os,sys,cairo,Image
from math import log, sin, cos, pi, atan2, sqrt
from random import random
from operator import itemgetter
from time import time
import numpy as np
from matplotlib import pylab as plt

PI     = pi
PII    = PI*2.

NUM    = 300    # nodes
MAXFS  = 40     # max friendships pr node
NEARL  = 0.07   # comfort zone
FARL   = 0.1    # ignore nodes beyond this distance

N      = 1000   # size of png image
N2     = N/2         
GRAINS = 4      # number of grains in sand painting connections
BACK   = 1.     # background color 
OUT    = 'img'  # resulting image name

RAD    = 0.1    # radius of starting circle

STP    = 0.0009 # scale motion in each iteration by this
steps  = 1000   # iterations

def ctxInit():
  sur = cairo.ImageSurface(cairo.FORMAT_ARGB32,N,N)
  ctx = cairo.Context(sur)
  ctx.scale(N,N)
  ctx.set_source_rgb(BACK,BACK,BACK)
  ctx.rectangle(0,0,1,1)
  ctx.fill()
  return sur,ctx

def pInit(X,Y):
  for i in xrange(0,NUM):
    the = random()*PII
    x = RAD * sin(the)
    y = RAD * cos(the)
    X[i] = 0.5+x
    Y[i] = 0.5+y
  return

def showP(ctx,X,Y):
  ctx.set_source_rgba(1,0,0,0.5)
  for i in xrange(0,NUM):
    ctx.move_to(X[i],Y[i])
    ctx.arc(X[i],Y[i],2./N,0,PII)
  ctx.close_path()
  ctx.fill()
  return

def setDistances(X,Y,R,A):
  for i in xrange(0,NUM):
    dx = X[i] - X
    dy = Y[i] - Y
    a  = np.arctan2(dy,dx)
    d  = np.sqrt(dx*dx+dy*dy)
    R[i] = d
    A[i] = a
  return

def makeFriends(i,R,F):
  if sum(F[i]) > MAXFS:
    return

  r = []
  for j in xrange(0,NUM):
    if i != j and sum(F[j]) < MAXFS\
      and not F[j][i]:
        r.append([R[i][j][0],j])
  if not len(r):
    return
  r = sorted(r, key=itemgetter(0))

  index = len(r)-1
  for k in xrange(0,len(r)):
    if random() < 0.1:
      index = k
      break
 
  F[i][r[index][1]] = True
  F[r[index][1]][i] = True
  return

def getConnectionPoints(ctx,X,Y,R,A,F,POINTS):
  for i in xrange(0,NUM):
    for j in xrange(i+1,NUM):
      if not F[i][j]:
        continue

      a = A[i][j]
      sx = cos(a)
      sy = sin(a)
      
      d = R[i][j]
      scale = random()*d/GRAINS
      if random()<0.5:
        q = i
      else:
        q = j
        scale *= -1

      xp = X[q][0]
      yp = Y[q][0]
      
      ij = NUM*i + j
      for q in xrange(0,GRAINS):
        xp -= sx*scale
        yp -= sy*scale
        POINTS.extend([ij,xp,yp])

  return

def paintIt(ctx,POINTS,colors,opa=0.2):
  n = len(POINTS)/3
  ncolors = len(colors)
  for k in xrange(0,n):
    k3 = k*3
    ij = POINTS[k3]
    rgb = colors[ij % ncolors]
    ctx.set_source_rgba(rgb[0],rgb[1],rgb[2],opa)
    ctx.rectangle(POINTS[k3+1],POINTS[k3+2],1./N,1./N)
    ctx.fill()

  return

def run(ctx,X,Y,SX,SY,R,A,F,NEARL,FARL):
  t = []
  t.append(time())
  setDistances(X,Y,R,A)
  t.append(time())
  
  SX[:] = 0.
  SY[:] = 0.
  
  t.append(time())

  for i in xrange(0,NUM):
    xF        = np.logical_not(F[i])
    d         = R[i]
    a         = A[i]
    near      = d > NEARL
    near[xF]  = False
    far       = d < FARL
    far[near] = False
    near[i]   = False
    far[i]    = False
    speed     = FARL - d[far]

    SX[near] += np.cos(a[near])
    SY[near] += np.sin(a[near])
    SX[far]  -= speed*np.cos(a[far])
    SY[far]  -= speed*np.sin(a[far])

  t.append(time())
  X  += SX*STP
  Y  += SY*STP
  t.append(time())
  makeFriends(int(random()*NUM),R,F)
  t.append(time())
  
  #for ti in xrange(0,len(t)-1):
    #print '{:.9f}'\
      #.format(t[ti+1] - t[ti]),
  #print 

def plotIt(X,Y,F):
  #plt.ion() ; plt.figure() # need to run this once on first run.
  plt.clf()
  plt.plot(X,Y,'ro')
  for k,ff in enumerate(F):
    for fi in xrange(0,NUM):
      if ff[fi] and fi > k:
        plt.plot([X[k],X[fi]],[Y[k],Y[fi]],'k-')

  plt.axis([0,1,0,1])
  ax = plt.gca()
  ax.set_autoscale_on(False)
  plt.draw()

def getColors(f):
  scale = 255.
  im = Image.open(f)
  w,h = im.size
  rgbim = im.convert('RGB')
  res = {}
  for i in xrange(0,w):
    for j in xrange(0,h):
      r,g,b = rgbim.getpixel((i,j))
      key = '{:03d}{:03d}{:03d}'\
        .format(r,g,b)
      res[key] = [r/scale,g/scale,b/scale]
  res = [value for key,value in res.iteritems()]
  return res

def main():
  POINTS = []

  #colors = getColors('colors.gif')
  colors = [[0,0,0]]

  farmult =  0.05
  nearmult = 0.02
  g = 3
  h = 3
  FARL = float(farmult) * float(g)
  NEARL = float(nearmult) * float(h)
  X       = np.zeros((NUM,1))
  Y       = np.zeros((NUM,1))
  SX      = np.zeros((NUM,1))
  SY      = np.zeros((NUM,1))
  R       = [np.zeros((NUM,1),dtype=np.bool) for i in xrange(0,NUM)]
  A       = [np.zeros((NUM,1),dtype=np.bool) for i in xrange(0,NUM)]
  F       = [np.zeros((NUM,1),dtype=np.bool) for i in xrange(0,NUM)]
  sur,ctx = ctxInit()
  pInit(X,Y)
  
  ctx.set_line_width(1./N)
 
  for i in xrange(0,steps):
    if not i%10:
      print i
    run(ctx,X,Y,SX,SY,R,A,F,NEARL,FARL)
    getConnectionPoints(ctx,X,Y,R,A,F,POINTS)
  print

  paintIt(ctx,POINTS,colors,opa=0.2)
  sur.write_to_png('./'+OUT+str(NEARL)+'x'+str(FARL)+'.png')

  return

if __name__ == '__main__' : main()

