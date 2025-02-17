from datetime import datetime

from StarDiscGenerator import generate_star_disc

lat = 45.3003
long = -122.9761
# Set date and time for sky generation (midnight)
time = datetime(2024, 2, 1, 0, 0, 0)

# Generate current sky
disc_file = generate_star_disc(lat, long, time)