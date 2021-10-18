import numpy as np
import sys
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation


def animate(time, r_data, R_data,
    r_line_3d, R_line_3d, rope_line_3d,
    r_line_x, R_line_x, rope_line_x,
    r_line_y, R_line_y, rope_line_y,
    r_line_z, R_line_z, rope_line_z):
    
    r_line_3d.set_data(r_data[time, 0:2])
    r_line_3d.set_3d_properties(r_data[time, 2])
    R_line_3d.set_data(R_data[time, 0:2])
    R_line_3d.set_3d_properties(R_data[time, 2])
    rope_line_3d.set_data(
        [R_data[time, 0], r_data[time, 0]],
        [R_data[time, 1], r_data[time, 1]])
    rope_line_3d.set_3d_properties(
        [R_data[time, 2], r_data[time, 2]])

    r_line_x.set_data(r_data[time, [1,2]])
    R_line_x.set_data(R_data[time, [1,2]])
    rope_line_x.set_data([r_data[time, 1], R_data[time, 1]], [r_data[time, 2], R_data[time, 2]])

    r_line_y.set_data(r_data[time, [0,2]])
    R_line_y.set_data(R_data[time, [0,2]])
    rope_line_y.set_data([r_data[time, 0], R_data[time, 0]], [r_data[time, 2], R_data[time, 2]])

    r_line_z.set_data(r_data[time, [0,1]])
    R_line_z.set_data(R_data[time, [0,1]])
    rope_line_z.set_data([r_data[time, 0], R_data[time, 0]], [r_data[time, 1], R_data[time, 1]])

def generate_animation(r, R, dt, fps=10, filename='results/animation.gif'):
    #step = int(len(R[:, 0]) / 100)
    step = int( 1/(fps*dt) )
    r_migrated=r[::step, :]
    R_migrated=R[::step, :]
    
    # Attaching 3D axis to the figure
    # fig = plt.figure()
    # ax = p3.Axes3D(fig)
    fig = plt.figure()
    ax3d = fig.add_subplot(2, 2, 1, projection='3d')
    ax2dx = fig.add_subplot(2, 2, 2)
    ax2dy = fig.add_subplot(2, 2, 3)
    ax2dz = fig.add_subplot(2, 2, 4)
    axes2d = [ax2dx, ax2dy, ax2dz] # list of all 2d axes

    # NOTE: Can't pass empty arrays into 3d version of plot()
    R_line_3d = ax3d.plot( R_migrated[0:1, 0], R_migrated[0:1, 1], R[0:1, 2], markersize=12, marker='.')[0]
    r_line_3d = ax3d.plot( r_migrated[0:1, 0], r_migrated[0:1, 1], r[0:1, 2], markersize=12, marker='.' )[0]
    rope_line_3d = ax3d.plot(
        [R_migrated[0, 0], r_migrated[0, 0]],
        [R_migrated[0, 1], r_migrated[0, 1]],
        [R_migrated[0, 2], r_migrated[0, 2]],
        linewidth=1.,
        color='black'
    )[0]

    R_line_x = ax2dx.plot( R_migrated[0:1, 1], R_migrated[0:1, 2], markersize=12, marker='.')[0]
    r_line_x = ax2dx.plot( r_migrated[0:1, 1], r_migrated[0:1, 2], markersize=12, marker='.' )[0]
    rope_line_x = ax2dx.plot(
        [R_migrated[0, 1], r_migrated[0, 1]],
        [R_migrated[0, 2], r_migrated[0, 2]],
        linewidth=1.,
        color='black'
    )[0]

    R_line_y = ax2dy.plot( R_migrated[0:1, 0], R_migrated[0:1, 2], markersize=12, marker='.')[0]
    r_line_y = ax2dy.plot( r_migrated[0:1, 0], r_migrated[0:1, 2], markersize=12, marker='.' )[0]
    rope_line_y = ax2dy.plot(
        [R_migrated[0, 0], r_migrated[0, 0]],
        [R_migrated[0, 2], r_migrated[0, 2]],
        linewidth=1.,
        color='black'
    )[0]

    R_line_z = ax2dz.plot( R_migrated[0:1, 0], R_migrated[0:1, 1], markersize=12, marker='.')[0]
    r_line_z = ax2dz.plot( r_migrated[0:1, 0], r_migrated[0:1, 1], markersize=12, marker='.' )[0]
    rope_line_z = ax2dz.plot(
        [R_migrated[0, 0], r_migrated[0, 0]],
        [R_migrated[0, 1], r_migrated[0, 1]],
        linewidth=1.,
        color='black'
    )[0]
    
    # Setting the axes properties
    lim = max( [np.max(np.abs(array)) for array in [R_migrated, r_migrated]])

    ax3d.set_xlim3d([-lim, lim])
    ax3d.set_ylim3d([-lim, lim])
    ax3d.set_zlim3d([-lim, lim])
    for ax2d in axes2d:
        ax2d.set_xlim(-lim, lim)
        ax2d.set_ylim(-lim, lim)

    # Creating the Animation object
    line_ani = animation.FuncAnimation(fig, animate, len(R_migrated[:,0]),
                                       fargs=(r_migrated, R_migrated,
                                       r_line_3d, R_line_3d, rope_line_3d,
                                       r_line_x, R_line_x, rope_line_x,
                                       r_line_y, R_line_y, rope_line_y,
                                       r_line_z, R_line_z, rope_line_z),
                                       interval=10, blit=False)

    # Saving the animation as gif
    line_ani.save(filename, writer='imagemagick', fps=fps)



if __name__=="__main__":

    # reading time configuration
    with open('results/cnfg.dat', 'r') as fdat_cnfg:
        print("Time configuration given by:")
        tmin = np.fromfile(fdat_cnfg, float, count=1)[0]
        print("tmin = "+str(tmin))
        tmax = np.fromfile(fdat_cnfg, float, count=1)[0]
        print("tmax = "+str(tmax))
        dt = np.fromfile(fdat_cnfg, float, count=1)[0]
        print("dt = "+str(dt))
        N = np.fromfile(fdat_cnfg, dtype='uint16', count=1)[0]
        print("N = "+str(N))
        

    # reading results from test
    R_raw = np.fromfile('results/R.dat', float)
    r_raw = np.fromfile('results/r.dat', float)
    R = R_raw.reshape(( int((len(R_raw))/3), 3))
    r = r_raw.reshape(( int((len(r_raw))/3), 3))
    
    print("Generating animation.gif")
    generate_animation(r, R, dt, fps=10, filename='results/animation.gif')