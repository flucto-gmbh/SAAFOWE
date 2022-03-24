imu_accelerations = {
        'column_names' : ['acc_x', 'acc_y', 'acc_z'],
        'labels' : ['acceleration X', 'acceleration Y', 'acceleration Z'],
        'ylabel' : "Acceleration ($m \cdot s^{-2}$)",
        'xlabel' : "date time",
        'figure_filename' : "acceleration.png",
        'ylim' : [-1.5, 1.5],
        'title' : 'Acceleration',
    }

imu_rotations =  {
        'column_names' : ['rot_x', 'rot_y', 'rot_z'],
        'labels' : ['angular velocity X', 'angular velocity Y', 'angular velocity Z'],
        'ylabel' : "Angular velocity ($deg \cdot s^{-1}$)",
        'xlabel' : "date time",
        'figure_filename' : 'rotation.png',
        'title' : 'Rotation',
    }
imu_magfield = {
        'column_names' : ['mag_x', 'mag_y', 'mag_z'],
        'labels' : ['magnetic field X', 'magnetic field Y', 'magnetic field Z'],
        'ylabel' : "Magnetic field ($\mu T$)",
        'xlabel' : "date time",
        'figure_filename' : 'magfield.png',
        'title'  : 'Magnetic field',
    }
gps_position = {
        'column_names' : ['lat', 'lon'],
        'labels' : ['latitude', 'longitude'],
        'ylabel' : "latitude",
        'xlabel' : "longitude",
        'margin' : 0.1,
        'figure_filename' : "lat_lon.png",
        #'ylim' : [-1.5, 1.5],
        'title' : 'Latitude/Longitude',
}

gps_altitude = {
        'column_names' : ['alt',],
        'labels' : ['altitude',],
        'ylabel' : "altitude (m)",
        'xlabel' : "date time",
        'figure_filename' : "alt.png",
        #'ylim' : [-1.5, 1.5],
        'title' : 'Altitude',
}

GPS_SENSORS = {
    'position' : gps_position,
    'altitude' : gps_altitude,
}

IMU_SENSORS = {
    'accelerations' : imu_accelerations,
    'rotations' : imu_rotations,
    'magfield' : imu_magfield,
}

FIGURE_CONFIGURATION = {
    'figsize' : (16, 9),
    'dpi' : 300,
    'transparent' : False,
}

AVAILABLE_PLOT_CONFIGURATIONS = {
    'gps' : GPS_SENSORS,
    'imu' : IMU_SENSORS
}
