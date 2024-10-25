import sys
import random
import math
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QLabel, QPushButton, QFormLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from model import generate_locations, route_planning

class RouteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Vehicle Routing System')
        self.setGeometry(100, 100, 1920, 1080)
        
        widget = QWidget(self)
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)

        layout.addWidget(QLabel('Number of Vehicles'))
        self.vehicle_count = QLineEdit("0") # VEHICLE COUNT
        layout.addWidget(self.vehicle_count)
        self.vehicle_count.textChanged.connect(self.update_vehicle_inputs)

        # USER INPUT WIDGETS
        self.max_distance_label = QLabel('Max Distance per Vehicle (km)')
        self.max_distance = QLineEdit("200")
        self.max_deliveries_label = QLabel('Max Deliveries per Vehicle Run')
        self.max_deliveries = QLineEdit("20")

        self.distance_and_deliveries_layout = QVBoxLayout()
        layout.addLayout(self.distance_and_deliveries_layout)

        layout.addWidget(QLabel('Number of Locations'))
        self.num_locations = QLineEdit("200")
        layout.addWidget(self.num_locations)

        self.vehicle_settings_layout = QFormLayout()
        layout.addLayout(self.vehicle_settings_layout)

        calc_btn = QPushButton('Generate Routes')
        calc_btn.clicked.connect(self.calculate_routes)
        layout.addWidget(calc_btn)

        self.save_csv_btn = QPushButton('Save Route Data')
        self.save_csv_btn.clicked.connect(self.save_routes_to_csv)
        layout.addWidget(self.save_csv_btn)

        self.figure = plt.Figure(figsize=(10, 10))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)


    def update_vehicle_inputs(self):
        # VEHICLE COUNT UPDATE WITH DISTANCE AND DELIVERY INPUTS WIDGETS
        vehicle_count = int(self.vehicle_count.text() if self.vehicle_count.text().isdigit() else 0)

        #SHOW WIDGETS
        if vehicle_count > 0:
            if not self.max_distance_label.isVisible():
                self.distance_and_deliveries_layout.addWidget(self.max_distance_label)
                self.distance_and_deliveries_layout.addWidget(self.max_distance)
                self.distance_and_deliveries_layout.addWidget(self.max_deliveries_label)
                self.distance_and_deliveries_layout.addWidget(self.max_deliveries)
        else:
            # HIDE WIDGETS
            self.max_distance_label.hide()
            self.max_distance.hide()
            self.max_deliveries_label.hide()
            self.max_deliveries.hide()

        #CLEAR INPUTS
        while self.vehicle_settings_layout.count():
            child = self.vehicle_settings_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # ADDING INPUTS FOR THE VEHICLE
        self.max_distances = []
        self.deliveries_per_runs = []
        for i in range(vehicle_count):
            max_distance = QLineEdit("150")
            deliveries_per_run = QLineEdit("10")
            self.max_distances.append(max_distance)
            self.deliveries_per_runs.append(deliveries_per_run)
            self.vehicle_settings_layout.addRow(f'Vehicle {i+1} Max Distance (km):', max_distance)
            self.vehicle_settings_layout.addRow(f'Vehicle {i+1} Deliveries per Run:', deliveries_per_run)

    # CALCULATING ROUTES 
    def calculate_routes(self):
        num_vehicles = int(self.vehicle_count.text())
        max_distance = int(self.max_distance.text()) if self.max_distance else 200
        max_deliveries = int(self.max_deliveries.text()) if self.max_deliveries else 20
        num_locations = int(self.num_locations.text())

        locations = generate_locations(num_locations)
        routes = route_planning(locations, num_vehicles, max_distance, max_deliveries)
        self.routes = routes
        self.plot_routes(routes)

    # SAVING ROUTE FILE TO CSV.
    def save_routes_to_csv(self):
        import csv
        with open('route_data.csv', 'w', newline='') as file:

            writer = csv.writer(file, delimiter='\t')
            writer.writerow(['VehicleID', 'Run_No', 'Deliveries', 'Distance', 'Locations'])

            for vehicle_idx, vehicle_routes in self.routes.items():
                for run_idx, (route, dist) in enumerate(vehicle_routes):
                    # CALCULATE DELIVERIES
                    total_deliveries = sum(loc[3] for loc in route if loc[0] != 0)
                    
                    # CALCULATE VISISTED LOCATIONS WITHOUT DEPOT
                    visited_location_ids = ', '.join(str(loc[0]) for loc in route if loc[0] != 0)

                    row_data = [
                        vehicle_idx,
                        run_idx + 1,
                        total_deliveries,
                        f"{dist:.2f} km", 
                        visited_location_ids 
                    ]
                    writer.writerow(row_data)

        print("Route file written successfully.")


    def plot_routes(self, routes):
        ax = self.figure.add_subplot(111)
        ax.clear()  # CLEAR ROUTE
        depot = (50, 50)  # DEPOT CORDINATES
        ax.plot(depot[0], depot[1], 'ro')

        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']  # COLOR PALLETE FOR ROUTES

        for vehicle_idx, vehicle_routes, in routes.items():
            color = colors[(vehicle_idx - 1) % len(colors)]  # COLOR FOR EACH VEHICLE
            for run_idx, (route, dist) in enumerate(vehicle_routes):
                x_coords, y_coords = zip(*[(loc[1], loc[2]) for loc in route])
                ax.plot(x_coords, y_coords, marker='o', linestyle='-', color=color,
                        label=f'Vehicle {vehicle_idx} Run {run_idx + 1}: {dist:.2f} km')

                # PRINT DISTANCE BETWEEN LOCATIONS
                for i in range(1, len(route)):
                    start = route[i-1]
                    end = route[i]
                    distance = math.hypot(end[1] - start[1], end[2] - start[2])
                    mid_x = (start[1] + end[1]) / 2
                    mid_y = (start[2] + end[2]) / 2
                    ax.text(mid_x, mid_y, f'{distance:.2f} km - Deliv: {end[3]}', color=color, fontsize=5, ha='center') 

                # PRINT ID FOR EACH VEHICLE
                for loc in route:
                    ax.text(loc[1], loc[2] + 1.5, f'ID: {loc[0]}', color=color, fontsize=5, ha='center')

        #GRAPH METRICS
        ax.set_title('Vehicle Routes')
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')
        ax.legend()
        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RouteApp()
    ex.show()
    sys.exit(app.exec_())
