import os
import sys

import matplotlib.pyplot as plt
import numpy as np

import point_registration
import tools


def correct_superview(points, cx, cy):
    s = 4.0 / 3.0
    a = 5.0 / 4.0

    x = np.abs(points[:, 0] - cx)
    y = np.abs(points[:, 1] - cy)

    ox = a
    fx = ox + (1.0 / cx) * np.multiply(x, s - ox)
    x = np.multiply(x, fx)
    points[:, 0] = cx + np.multiply(x, np.sign(points[:, 0] - cx))

    oy = a
    fy = oy + (1.0 / cy) * np.multiply(y, 1 - oy)
    y = np.multiply(y, fy)
    points[:, 1] = cy + np.multiply(y, np.sign(points[:, 1] - cy))

    return points


def correct_distortion(points, cx, cy, k1, k2, k3, f):
    r2 = (points[:, 0] - cx) ** 2 + (points[:, 1] - cy) ** 2
    r2 = r2 * (1.0 / (f * f))
    r4 = np.multiply(r2, r2)
    cr = 1 + k1 * r2 + k2 * r4 + k3 * r2 * r4
    pr = np.array([cx + np.multiply(points[:, 0] - cx, cr), cy + np.multiply(points[:, 1] - cy, cr)])
    return pr.transpose()


def align_camera(points):
    cx = 1080 / 2
    cy = 1920 / 2

    f, (ax1, ax2) = plt.subplots(2, 1)
    ax1.set_aspect('equal')
    ax2.set_aspect('equal')
    ax1.plot(points[:, 1], -points[:, 0], '.')

    points = correct_superview(points, cx, cy)

    ax1.plot(points[:, 1], -points[:, 0], '.')

    # this was determined manually
    k1 = 0.18
    k2 = 0.15
    k3 = 0.1
    f = 920.0
    points = correct_distortion(points, cx, cy, k1, k2, k3, f)
    ax1.plot(points[:, 1], -points[:, 0], '.')

    # the model for the RC19 field lines
    field_model_fkt = tools.make_field_points_rc
    # the model for the NaoTH lab
    #field_model_fkt = tools.make_field_points_bu

    model_points = field_model_fkt(50.0)
    ax2.plot(model_points[:, 1], model_points[:, 0], '.', label='field lines')

    # initial guess for the position of the camera at the RC19
    t0 = np.array([0, -35, 0, -3500, 0, 1800])
    # initial guess for the position of the camera in the lab NaoCam 2
    #t0 = np.array([0,-90, 6, -400, -300, 2400])

    # all coordinates relative to the center for convenience in the projection
    points[:, 0] -= cx
    points[:, 1] -= cy

    # project the points with the initial transform t0
    tpoints = tools.projectPoints(points, t0)
    ax2.plot(tpoints[:, 1], tpoints[:, 0], '.', label='after initial transformation')

    # ignore the 'worst outliers', i.e., more than 3m away
    inlier_idx, outlier_idx = tools.calculateOutliers(model_points, tpoints, 3000)
    points = points[inlier_idx, :]

    # optimize the alignment
    t, err, points, model_points = point_registration.finde_transformation(points, t0,
                                                                           point_registration.registration_fast,
                                                                           field_model_fkt)
    
    # project the points with the final transformation
    tpoints = tools.projectPoints(points, t)
    ax2.plot(tpoints[:, 1], tpoints[:, 0], '.', label='final projection')
    ax2.legend(loc='lower center', bbox_to_anchor=(0.5, 1.05), fancybox=True, shadow=True)
    plt.show()


if __name__ == "__main__":

    if len(sys.argv) == 1:
        file = './data/rc18-htwk-naoth-h1-combined.txt'
    else:
      file = sys.argv[1]

    print("reading: {}".format(file))

    # construct the path for the target file to save the points to
    name = os.path.splitext(os.path.basename(file))[0]
    dir = os.path.dirname(file)
    target_file = os.path.join(dir, name + '.txt')

    points = np.loadtxt(file)

    align_camera(points)
