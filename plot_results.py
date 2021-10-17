import numpy as np
import sys
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation


def animate(time, r_data, R_data, r_line, R_line, rope_line):
    r_line.set_data(r_data[time, 0:2])
    r_line.set_3d_properties(r_data[time, 2])
    R_line.set_data(R_data[time, 0:2])
    R_line.set_3d_properties(R_data[time, 2])
    rope_line.set_data(
        [R_data[time, 0], r_data[time, 0]],
        [R_data[time, 1], r_data[time, 1]])
    rope_line.set_3d_properties(
        [R_data[time, 2], r_data[time, 2]])
    
    # rope_endpoint = r_data[time, :]-R_data[time, :]
    # rope_data = np.array([
    #     R_data[time, axis] + np.linspace(0,1,10)*rope_endpoint[axis]
    #     for axis in [0,1,2]
    # ])
    
    # rop_line.set_data(rope_data[0:2].T)
    # rope_line.set_3d_properties(rope_data[2])

def generate_animation(r, R, filename='animation.gif'):
    step = int(len(R[:, 0]) / 100)
    r_migrated=r[::step, :]
    R_migrated=R[::step, :]
    
    # Attaching 3D axis to the figure
    fig = plt.figure()
    ax = p3.Axes3D(fig)
    
    # NOTE: Can't pass empty arrays into 3d version of plot()
    R_line = ax.plot( R_migrated[0:1, 0], R_migrated[0:1, 1], R[0:1, 2], markersize=12, marker='.')[0]
    r_line = ax.plot( r_migrated[0:1, 0], r_migrated[0:1, 1], r[0:1, 2], markersize=12, marker='.' )[0]
    rope_line = ax.plot(
        [R_migrated[0, 0], r_migrated[0, 0]],
        [R_migrated[0, 1], r_migrated[0, 1]],
        [R_migrated[0, 2], r_migrated[0, 2]],
        linewidth=1.,
        color='black'
    )[0]
    
    # Setting the axes properties
    lim = max( [np.max(np.abs(array)) for array in [R_migrated, r_migrated]])
    
    ax.set_xlim3d([-lim, lim])
    ax.set_xlabel('X')

    ax.set_ylim3d([-lim, lim])
    ax.set_ylabel('Y')

    ax.set_zlim3d([-lim, lim])
    ax.set_zlabel('Z')

    ax.set_title('3D Test')
    
    # ax.set_axis_off()

    # Creating the Animation object
    line_ani = animation.FuncAnimation(fig, animate, len(R_migrated[:,0]),
                                       fargs=(r_migrated, R_migrated, r_line, R_line, rope_line),
                                       interval=10, blit=False)

    # Saving the animation as gif
    line_ani.save(filename, writer='imagemagick', fps=60)

R_raw = np.fromfile('results/R.dat', float)
r_raw = np.fromfile('results/r.dat', float)

R = R_raw.reshape(( int((len(R_raw))/3), 3))
r = r_raw.reshape(( int((len(r_raw))/3), 3))

generate_animation(r, R, 'test.gif')