
import numpy as np
import matplotlib.pyplot as plt

class Particle:
    def __init__(self, position):
        self.position = np.array(position, dtype='float64')
        self.velocity = np.random.rand(2) * 0.1  # Random initial velocity

    def update(self, particles, radius):
        # Find nearby particles within the specified radius
        nearby_velocities = []
        for other in particles:
            if other is not self:  # Exclude itself
                distance = np.linalg.norm(self.position - other.position)
                if distance < radius:
                    nearby_velocities.append(other.velocity)

        # Update velocity based on imitation of nearby particles
        if nearby_velocities:
            average_velocity = np.mean(nearby_velocities, axis=0)
            self.velocity = self.velocity + (average_velocity - self.velocity) * 0.5  # Imitation factor

        # Update position based on the new velocity
        self.position += self.velocity

def simulate(num_particles, num_iterations, radius):
    # Initialize particles
    particles = [Particle(position=np.random.rand(2)) for _ in range(num_particles)]

    # Prepare for plotting
    plt.ion()
    fig, ax = plt.subplots()
    
    for _ in range(num_iterations):
        ax.clear()
        positions = np.array([particle.position for particle in particles])
        ax.scatter(positions[:, 0], positions[:, 1])
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_title('Particle Swarm Dynamics')
        plt.pause(0.1)

        # Update each particle
        for particle in particles:
            particle.update(particles, radius)

    plt.ioff()
    plt.show()

# Parameters
num_particles = 100
num_iterations = 100
radius = 0.2

# Run the simulation
simulate(num_particles, num_iterations, radius)
