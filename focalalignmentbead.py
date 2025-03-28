import numpy as np
import matplotlib.pyplot as plt

def plot3vec(sRec, marker='.', ax=None):
    """Plot 3D vector positions."""
    if len(sRec.shape) == 1:
        sRec = sRec.reshape(-1, 1)

    if marker == 'b+':  # Blue with plus markers
        color, symbol = 'b', '+'
    elif marker == 'ro':  # Red with circle markers
        color, symbol = 'r', 'o'
    else:
        color, symbol = 'k', '.'  # Default to black dots if unknown

    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

    ax.scatter(sRec[0, :], sRec[2, :], sRec[1, :], c=color, marker=symbol)
    ax.set_xlabel('x (mm)')
    ax.set_ylabel('z (mm)')
    ax.set_zlabel('y (mm)')
    ax.invert_zaxis()

import numpy as np
import matplotlib.pyplot as plt


def plot3vec(sRec, marker='b+', ax=None):
    """Plot 3D vector positions."""
    if len(sRec.shape) == 1:
        sRec = sRec.reshape(-1, 1)

    color, symbol = parse_marker(marker)

    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

    ax.scatter(sRec[0, :], sRec[2, :], sRec[1, :], c=color, marker=symbol)
    ax.set_xlabel('x (mm)')
    ax.set_ylabel('z (mm)')
    ax.set_zlabel('y (mm)')
    ax.invert_zaxis()


def plot2vec(sRec, marker='b+'):
    """Plot 2D vector positions."""
    if len(sRec.shape) == 1:
        sRec = sRec.reshape(-1, 1)

    color, symbol = parse_marker(marker)
    plt.scatter(sRec[0, :], sRec[1, :], c=color, marker=symbol)


def parse_marker(marker):
    """Parse MATLAB-like marker format to matplotlib format."""
    if marker == 'b+':  # Blue with plus markers
        return 'b', '+'
    elif marker == 'ro':  # Red with circle markers
        return 'r', 'o'
    elif marker == 'bo':  # Blue with circles
        return 'b', 'o'
    elif marker == 'r+':  # Red with plus markers
        return 'r', '+'
    else:
        # Default: black dots if unknown marker
        return 'k', '.'
    
# ---------------------
# Main script
# ---------------------

# Set the focal spot position relative to detector center
fs_xyz_mm = np.array([-5, 0, -3])

# Source-to-detector distance
sd_mm = 341

N_beads = 9  # Number of beads along one axis (2*N-1 beads per plane)
# Bead spacing
bead_sp_mm = 2
# Separation between bead planes
bead_plane_sep_y_mm = 50
# Distance from lower plane to detector surface
s_lower_plane_to_det_mm = 15

# Bead positions along x and z axis
bead_pos_xz_ax_mm = np.arange(0, bead_sp_mm * N_beads, bead_sp_mm)
bead_pos_xz_ax_mm = bead_pos_xz_ax_mm - np.mean(bead_pos_xz_ax_mm) # Center the beads

# Lower and upper bead plane distances
bead_plane_lower_y_mm = sd_mm - s_lower_plane_to_det_mm # float
bead_plane_upper_y_mm = bead_plane_lower_y_mm - bead_plane_sep_y_mm # float

# Magnifications
mag_upper = sd_mm / bead_plane_upper_y_mm # float >1
mag_lower = sd_mm / bead_plane_lower_y_mm # float >1

# Bead positions at upper plane
bead_pos_xz_plane1_mm = np.vstack([
    np.concatenate([bead_pos_xz_ax_mm, np.zeros(N_beads)]),
    bead_plane_upper_y_mm * np.ones(2 * N_beads),
    np.concatenate([np.zeros(N_beads), bead_pos_xz_ax_mm / mag_upper * mag_lower])
])

# Bead positions at lower plane (magnified spacing)
bead_pos_xz_plane2_mm = np.vstack([
    np.concatenate([bead_pos_xz_ax_mm / mag_lower * mag_upper, np.zeros(N_beads)]),
    bead_plane_lower_y_mm * np.ones(2 * N_beads),
    np.concatenate([np.zeros(N_beads), bead_pos_xz_ax_mm])
])

# Projection lines
p0 = fs_xyz_mm[:, np.newaxis]  # Focal spot position as 3x1
p1 = np.hstack([bead_pos_xz_plane1_mm, bead_pos_xz_plane2_mm])  # Bead positions

# Vector direction from source to beads
v = p1 - p0
lambda_vals = (sd_mm - p0[1, :]) / v[1, :]

# Compute projections onto the detector
proj = p0 + v * lambda_vals

# ---------------------
# Plotting Bead Positions
# ---------------------

# Plot bead positions in 3D
fig = plt.figure(1)
plt.clf()
ax = fig.add_subplot(111, projection='3d')
plot3vec(bead_pos_xz_plane1_mm[[0, 2, 1], :], 'b+', ax)
plot3vec(bead_pos_xz_plane2_mm[[0, 2, 1], :], 'ro', ax)
plt.show(block=False)

# ---------------------
# Plotting Projection
# ---------------------

plt.figure(2)
plt.clf()
plot2vec(proj[[0, 2], :2 * N_beads], 'bo')
plot2vec(proj[[0, 2], 2 * N_beads:], 'r+')
plt.xlabel('x (mm)')
plt.ylabel('z (mm)')
plt.title(f'Projection of beads on detector focal spot at ({fs_xyz_mm[0]}, {fs_xyz_mm[2]})')
plt.show()
