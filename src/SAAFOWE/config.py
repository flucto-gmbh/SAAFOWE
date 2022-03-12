IMU_SENSORS = {
    'acceleration' : {
        'column_names' : ['acc_x', 'acc_y', 'acc_z'],
        'labels' : ['acceleration X', 'acceleration Y', 'acceleration Z'],
        'ylabel' : "Acceleration ($m \cdot s^{-2}$)",
        'xlabel' : "date time",
        'figure_filename' : "acceleration.png",
        'ylim' : [-1.5, 1.5],
        'title' : 'Acceleration',
    },
    'rotation' : {
        'column_names' : ['rot_x', 'rot_y', 'rot_z'],
        'labels' : ['angular velocity X', 'angular velocity Y', 'angular velocity Z'],
        'ylabel' : "Angular velocity ($deg \cdot s^{-1}$)",
        'xlabel' : "date time",
        'figure_filename' : 'rotation.png',
        'title' : 'Rotation',
    },
    'magfield' : {
        'column_names' : ['mag_x', 'mag_y', 'mag_z'],
        'labels' : ['magnetic field X', 'magnetic field Y', 'magnetic field Z'],
        'ylabel' : "Magnetic field ($\mu T$)",
        'xlabel' : "date time",
        'figure_filename' : 'magfield.png',
        'title'  : 'Magnetic field',
    },
}

PLOT_PARAMETERS = {
    'figsize' : (16, 9),
    'dpi' : 300,
}