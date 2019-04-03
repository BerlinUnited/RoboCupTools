#!/usr/bin/python

import numpy as np
#from PIL import Image

import math
from scipy.spatial import cKDTree as KDTree

'''
def loadImage(path):
  img = Image.open(path)
  ycbcr = img.convert('YCbCr')
  
  global imWidth
  global imHeight

  width = ycbcr.size[0]
  height = ycbcr.size[1]
  size = (height, width)
  
  # separate chanels
  img_y = np.array(list(ycbcr.getdata(band=0)))
  img_u = np.array(list(ycbcr.getdata(band=1)))
  img_v = np.array(list(ycbcr.getdata(band=2)))

  img_y = np.reshape(img_y, size)
  img_u = np.reshape(img_u, size)
  img_v = np.reshape(img_v, size)
		
  return (img, img_y, img_u, img_v)
'''
 
def make_field_points(step=200.0):

  width = 6000.0
  length = 9000.0
  circle_radius = 750.0
  penalty_area_width=600.0
  penalty_area_length=2200.0
  penalty_mark_distance=1300.0
  feld = []
  
  # side lines
  for x in np.arange(-length/2.0, length/2.0+step,step):
    feld += [[x, -width/2.0]]
    feld += [[x, width/2.0]]
  
  # goal lines and the center line
  for y in np.arange(-width/2.0, width/2.0+step,step):
    feld += [[-length/2.0, y]]
    feld += [[length/2.0, y]]
    feld += [[0.0, y]]
    
  # penalty area long lines
  for y in np.arange(-penalty_area_length/2.0, penalty_area_length/2.0+step,step):
    feld += [[-length/2.0+penalty_area_width, y]]
    feld += [[length/2.0-penalty_area_width, y]]
    
  # penalty area short lines
  for x in np.arange(0.0, penalty_area_width, step):
    feld += [[-length/2.0+x, -penalty_area_length/2.0]]
    feld += [[-length/2.0+x,  penalty_area_length/2.0]]
    feld += [[ length/2.0-x, -penalty_area_length/2.0]]
    feld += [[ length/2.0-x,  penalty_area_length/2.0]]

  # penalty mark
  #feld += [[length/2.0-penalty_mark_distance, 0.0]]
  #feld += [[-length/2.0+penalty_mark_distance, 0.0]]

  # middle circle
  number_of_steps = (2.0*np.pi*circle_radius) / step
  for a in np.arange(-np.pi,np.pi,2.0*np.pi/number_of_steps):
    feld += [[circle_radius*np.sin(a), circle_radius*np.cos(a)]]
    
  
  
  feld = np.array(feld).astype(float)
  feld = feld[:,[1,0]] # vertausche x und y
  return feld
  
def make_field_points_HU(step=200.0):
  feld = np.load("HU_Modell.npy")
  feld = feld[:,[1,0]] # vertausche x und y
  return feld[::int(step/10)]*1000.0

  
def projectPoints(points, pose):
  
  # stelle sicher, dass die Punkte im richtigen Format sind
  assert(points.shape[1] == 2)
  
  # rotation
  ax, ay, az = np.radians(pose[0:3])
  
  Rx = np.array([[1, 0, 0],[0, math.cos(ax), math.sin(ax)],[0, -math.sin(ax), math.cos(ax)]])
  Ry = np.array([[math.cos(ay), 0, -math.sin(ay)],[0, 1, 0],[math.sin(ay), 0, math.cos(ay)]])
  Rz = np.array([[math.cos(az), math.sin(az), 0],[-math.sin(az), math.cos(az), 0],[0, 0, 1]])
  
  R = np.dot(Rx,np.dot(Ry,Rz))
  
  # translation: x,y,z
  t = pose[3:6]
  
  # NOTE: calculated for GoPro Session with Matlab
  f = 820.0
  
  # NOTIZ:
  # skallierungsfaktor fuer die Pixel: Pixel scheinen nicht quadratisch zu sein
  # Das kann daran liegen, dass die Aufloesung 1920 x 1080 nicht der nativen Aufloesung des Chips der Kamera entspricht.
  # ACHTUNG: aktueller Faktor ist manuell ermittelt (!)
  
  projected_points = np.zeros((points.shape[0],3))
  
  # verschiebe alle Punkte
  projected_points[:,0] = 1.0
  projected_points[:,1] = ( - points[:,1]) / f
  projected_points[:,2] = ( - points[:,0]) / f
  
  # rotiere alle Punkte: vgl. project()
  # v = np.dot(R , np.array([f, x0, y0]))
  v = np.dot(R, projected_points.transpose()).transpose()
  
  # projiziere ale Punkte: vgl. project()
  # v[0:2]*(t[2]/(-v[2])) + t[0:2]
  result = np.multiply(v[:,0:2], np.tile(np.divide(-t[2], v[:,2]), (2,1)).transpose()) + np.tile(t[0:2], (v.shape[0],1))
  
  return result
   

def find_closest_points(model, data):
  result = []
  error = 0.0
  
  if data.shape[0] == 0:
    return result, error
  
  tree = KDTree(model)
  ordered_errors, ordered_neighbors = tree.query(data, k=1)
  for idx, e in zip(ordered_neighbors, ordered_errors):
    result += [idx]
    error += e*e
  
  return result, error / float(data.shape[0])

  
def calculateOutliers(model, data, max_error):
  inlier_idx = []
  outlier_idx = []
  
  c_idx, _ = find_closest_points(model, data)
  for i_data, i_model in enumerate(c_idx):
    if i_data < data.shape[0] and i_model < model.shape[0]:
      v = data[i_data,:] - model[i_model,:]
      if np.hypot(v[0],v[1]) <= max_error:
        inlier_idx += [i_data]
      else:
        outlier_idx += [i_data]
        
  return inlier_idx, outlier_idx
  
