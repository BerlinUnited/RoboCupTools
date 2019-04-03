#!/usr/bin/python
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
  
import tools

# skaliere die Rohdaten auf die groesse des Modells
# faktor wird aus der mitleren Abweichung der in x und y richtung bestimmt
# Punkte auserhalb des Feldes verfaelschen vermutlich die berechnung
def rezise_to_Model(model, points):
	p = points - (np.sum(points, axis=0) / points.shape[0])
	m = np.amax(model, axis=0)
	d = np.amax(p, axis=0)
	x = m[0] / d[0]
	y = m[1] / d[1]
	s = (x+y)/2
	return points*s

  
def mask_to_Pointlist(img):
	#img = img[770:] #oberes ende abschneiden um Fehler zu reduzieren
	#~ img = np.flip(img, 0) #spiegeln an x-Achse
	#~ img = np.flip(img, 1) #spiegeln an y-Achse
	return (np.array(np.where( img > 0 )).T).astype(float)

  
def error(model, points, t):
	points = tools.projectPoints(points, t)
	_, e = tools.find_closest_points(model, points)

	print("Error: {0}mm".format(np.sqrt(e)))
	return e
  
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html#scipy.optimize.minimize
# finde eine transformation, die den error zwischen dem model und den Daten minimiert
def registration_simple(model, points, t0):

  f = lambda x: error(model, points, x)
  
  t = np.array(t0)
  bnds = ((-360,360),(-360,360),(-360,360),(None, None),(None, None),(None, None))
  result = optimize.minimize(f, t, method='SLSQP', bounds=bnds)

  if result.success:
    return result.x, np.sqrt(result.fun)
  else:
    print result
    raise("[ERROR] could not solve")
  

  
  
def errorMeanSquare(model, points, t):
  
  tpoints = tools.projectPoints(points, t)
  assert(model.shape == tpoints.shape)
  
  # calculate error
  e = model - tpoints
  e = np.multiply(e, e) 
  e = np.sum(np.sum(e,axis=0)) / float(points.shape[0])

  return e  

def registration_fast(model, points, t0, iterationen = 10):
  
  t = t0
  
  for k in range(0,iterationen):
    print "Iteration {0}".format(k)
    
    # make the assignement only once
    tpoints = tools.projectPoints(points, t)
    c_idx, et = tools.find_closest_points(model, tpoints)
    model_selection = model[c_idx,:]
    
    # loese das problem
    f = lambda x: errorMeanSquare(model_selection, points, x)
    bnds = ((-360,360),(-360,360),(-360,360),(None, None),(None, None),(None, None))
    result = optimize.minimize(f, t, method='SLSQP', bounds=bnds)
    
    t = result.x
    e = np.sqrt(result.fun)
    print("Error: {0}mm".format(e))
  
  if result.success:
    return result.x, np.sqrt(result.fun)
  else:
    print result
    raise("[ERROR] could not solve")
  
# suche nach den Eckpnkten des Feldes
def extrahiere_eckpunkte(points):
  points = np.around(points)

  p = np.zeros((4,2))
  y, x = np.split(points,2, axis=1)

  pmin = np.argmin(x.T)
  pmax = np.argmax(x.T)

  for i in range(0,int(x[pmax][0]+1),5):
    h = np.where(x == i)
    if h[0].size == 0:
      continue
    hp = []
    for j in h[0]:
      hp.append(y[j][0])
    if np.max(hp) > (p[0][0]-50):
      p[0] = np.array([np.max(hp), i])
    if np.min(hp) < (p[1][0]+50):
      p[1] = np.array([np.min(hp), i])

  for i in range(0,abs(int(x[pmin][0]-1)),5):
    h = np.where(x == -i)
    if h[0].size == 0:
      continue
    hp = []
    for j in h[0]:
      hp.append(y[j][0])
    if np.max(hp) > (p[2][0]-50):
      p[2] = np.array([np.max(hp), -i])
    if np.min(hp) < (p[3][0]+50):
      p[3] = np.array([np.min(hp), -i])
  return p
  
def finde_transformation(points, t0, registration_function = registration_fast, modelfkt = tools.make_field_points):

  # erstelle das Model
  model = modelfkt(200.0)

  # berechne den initialen Fehler
  e_initial = np.sqrt(error(model, points, t0))
  print("Initial Error: {0}mm".format(e_initial))
  
  t, err = registration_function(model, points, t0)
  
  return t, err, points, model
  
  
# ein zweistufiges verfahren 
def finde_transformation_zwei_stufen(points, registration_function = registration_fast, modelfkt = tools.make_field_points, t0 = None):
  
  # startwert
  #~ t0, _, _ = finde_initiale_transformation(points)
  if t0 is None:
    t0 = finde_initiale_transformation(points)
  
  ###############################
  # STUFE 1
  
  # erzeuge ein grobes modell
  model = modelfkt(200.0)
  
  # berechne den initialen Fehler
  e_initial = np.sqrt(error(model, points, t0))
  print("Initial Error: {0}mm".format(e_initial))
  
  
  # minimiere den Fehler
  t1, e1 = registration_function(model, points, t0)
  
  print("Intermediate Error: {0}mm".format(e1))
  
  # finde die Ausreisser
  tpoints = tools.projectPoints(points, t1)
  inlier_idx, outlier_idx = tools.calculateOutliers(model, tpoints, e1*2)
  
  
  ###############################
  # STUFE 2 
  
  # erzeuge ein feineres modell
  model = modelfkt(50.0)
  
  # verfeinere die optimierung nur auf daten ohne Ausreisser
  inlier_points = points[inlier_idx, :]
  t2, e2 = registration_function(model, inlier_points, t1)
  
  return t2, e2, points, model
  
  
# Zeichne die Daten und Ausreissern
def show_data(model, points, t, err = float("inf")):

  tpoints = tools.projectPoints(points, t)
  inlier_idx, outlier_idx = tools.calculateOutliers(model, tpoints, err*2)
  tinlier_points = tpoints[inlier_idx,:]
  
  f, ax = plt.subplots()
  ax.plot(model[:,1], model[:,0], 'g.')
  ax.plot(tpoints[inlier_idx,1], tpoints[inlier_idx,0], 'k.')
  ax.plot(tpoints[outlier_idx,1], tpoints[outlier_idx,0], 'r.')
  
  # plot the zuordnung
  c_idx, _ = tools.find_closest_points(model, tinlier_points)
  for i_points, i_model in enumerate(c_idx):
    if i_points < tinlier_points.shape[0] and i_model < model.shape[0]:
      ax.plot([tinlier_points[i_points,1], model[i_model,1]], [tinlier_points[i_points,0], model[i_model,0]], 'b')
  
  plt.show()
  
  

if __name__ == "__main__":
	
  # lade die Daten
  img = np.load("intrinready.npy")
  plt.imshow(img)
  plt.show()
  img[0:770,:] = 0 #oberes ende abschneiden um Fehler zu reduzieren
  
  points = mask_to_Pointlist(img)
  # subsampling: nur jeden 10ten Punkt
  points = points[range(0,points.shape[0],10),:]
  
  # teste die initiale Schatzung
  #------------------------------
  t = np.array([0,50,0, -3000,1,1700])
  # das ist nur fuer die anzeige
  model = tools.make_field_points(200.0)
  err = 0
  
  # teste das einfache verfahren
  #------------------------------
  #t, err, points, model = finde_transformation(points, registration_fast)
  #t, err, points, model = finde_transformation(points, registration_simple)
  
  # teste das zweistufige verfahren
  #------------------------------
  #t, err, points, model = finde_transformation_zwei_stufen(points, registration_fast)
  t, err, points, model = finde_transformation_zwei_stufen(points, registration_simple)
  
  
  print("Final Error: {0}mm".format(err))
  print("ax: {0:.2f}, ay: {1:.2f}, az: {2:.2f} x: {3:.0f}, y: {4:.0f}, z: {5:.0f}".format(t[0],t[1],t[2],t[3],t[4],t[5]))
  
  show_data(model, points, t, err)
  
  
