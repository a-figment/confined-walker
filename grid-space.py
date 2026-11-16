import matplotlib.pyplot as plt
import matplotlib.patches as patches

class EvolvingDomain:
    def __init__(self, W=1, L=1):
        """
        Initializes the domain.
        Args:
            W: Width of a single block (x-dimension)
            L: Length of a single block (y-dimension)
        """
        # Physical dimensions of a single block
        self.W = W
        self.L = L
        
        # We use a set of tuples to store the (x, y) grid INDICES of active cells.
        # Initial state: A single block at grid index (0, 0)
        self.active_cells = {(0, 0)}
        
        # Directions mapping for easier logic handling
        self.directions = {
            'right': (1, 0),
            'left': (-1, 0),
            'up': (0, 1),
            'down': (0, -1)
        }

    def get_boundary_candidates(self):
        """
        Identifies the 'grey blocks' (walls).
        These are cells that are NOT active but are adjacent to an active cell.
        """
        candidates = set()
        for x, y in self.active_cells:
            for dx, dy in self.directions.values():
                neighbor = (x + dx, y + dy)
                if neighbor not in self.active_cells:
                    candidates.add(neighbor)
        return candidates

    def erode_wall(self, target_cell_index, direction):
        """
        Rule 1: Remove a wall (expand the domain).
        
        Args:
            target_cell_index: tuple (x_idx, y_idx) of the cell initiating expansion
            direction: string 'right', 'left', 'up', or 'down'
        """
        if target_cell_index not in self.active_cells:
            print(f"Error: Cell index {target_cell_index} does not exist in domain.")
            return

        dx, dy = self.directions[direction]
        new_cell = (target_cell_index[0] + dx, target_cell_index[1] + dy)
        
        # Add the new cell to the active domain
        self.active_cells.add(new_cell)
        print(f"Expanded {direction} from {target_cell_index}. New cell added at {new_cell}")
    def get_boundary_polygons(self):
            """
            Converts active grid cells into a list of polygonal vertex chains.
            Vertices are ordered Counter-Clockwise (CCW).
            Returns:
                list of lists: [[(x,y), (x,y), ...], ...] 
                (A list containing one or more loops of vertices)
            """
            # 1. Collect all directed edges that form the boundary.
            # We enforce the "Left Hand Rule": The interior must be on the left of the vector.
            # Dictionary format: start_node -> end_node
            # Note: In complex pinch-cases (checkerboards), a node might have 2 outgoing edges.
            # This simple dict approach assumes manifold boundaries (no pinch points).
            edges = {}
    
            for x, y in self.active_cells:
                # Check Right Neighbor (x+1, y)
                # If empty, this wall goes UP: (x+1, y) -> (x+1, y+1)
                if (x + 1, y) not in self.active_cells:
                    edges[(x + 1, y)] = (x + 1, y + 1)
    
                # Check Top Neighbor (x, y+1)
                # If empty, this wall goes LEFT: (x+1, y+1) -> (x, y+1)
                if (x, y + 1) not in self.active_cells:
                    edges[(x + 1, y + 1)] = (x, y + 1)
    
                # Check Left Neighbor (x-1, y)
                # If empty, this wall goes DOWN: (x, y+1) -> (x, y)
                if (x - 1, y) not in self.active_cells:
                    edges[(x, y + 1)] = (x, y)
    
                # Check Bottom Neighbor (x, y-1)
                # If empty, this wall goes RIGHT: (x, y) -> (x+1, y)
                if (x, y - 1) not in self.active_cells:
                    edges[(x, y)] = (x + 1, y)
    
            # 2. Chain edges together to form polygons
            polygons = []
            
            while edges:
                # Pick an arbitrary start from the remaining edges
                start_vertex = next(iter(edges))
                current_vertex = start_vertex
                current_poly = []
    
                while True:
                    # Add current vertex scaled by physical dimensions
                    phys_pt = (current_vertex[0] * self.W, current_vertex[1] * self.L)
                    current_poly.append(phys_pt)
    
                    # Get the next vertex and remove the edge from the set
                    next_vertex = edges.pop(current_vertex, None)
                    
                    if next_vertex is None:
                        # This shouldn't happen in a closed loop geometry
                        break
                    
                    # If we closed the loop, stop
                    if next_vertex == start_vertex:
                        break
                    
                    current_vertex = next_vertex
                
                polygons.append(current_poly)
    
            return polygons


    def plot_grid(self, title="Current Domain State"):
        """
        Visualizes the active domain (white) and potential expansion blocks (grey).
        Uses self.W and self.L to scale the drawing.
        """
        fig, ax = plt.subplots(figsize=(6, 6))
        
        # Helper to calculate physical coordinates from grid indices
        def get_physical_rect(ix, iy, color, alpha=1.0, label=None):
            # Bottom-left corner is (ix * W, iy * L)
            rect = patches.Rectangle((ix * self.W, iy * self.L), 
                                     self.W, self.L, 
                                     linewidth=1 if color=='lightgrey' else 2, 
                                     edgecolor='gray' if color=='lightgrey' else 'black', 
                                     facecolor=color, 
                                     alpha=alpha)
            return rect

        # 1. Plot the "Potential/Wall" blocks (Grey)
        boundary_blocks = self.get_boundary_candidates()
        for ix, iy in boundary_blocks:
            rect = get_physical_rect(ix, iy, 'lightgrey', alpha=0.5)
            ax.add_patch(rect)
            
        # 2. Plot the "Active" blocks (White)
        for ix, iy in self.active_cells:
            rect = get_physical_rect(ix, iy, 'white')
            ax.add_patch(rect)
            # Add text to identify grid indices
            center_x = (ix * self.W) + (self.W / 2)
            center_y = (iy * self.L) + (self.L / 2)
            ax.text(center_x, center_y, f"{ix},{iy}", 
                    ha='center', va='center', fontsize=8, color='black')

        # Adjust plot limits dynamically based on physical dimensions
        all_indices = self.active_cells | boundary_blocks
        all_x_phys = [c[0] * self.W for c in all_indices]
        all_y_phys = [c[1] * self.L for c in all_indices]
        
        # Add some padding equal to one block size
        ax.set_xlim(min(all_x_phys) - self.W, max(all_x_phys) + 2*self.W)
        ax.set_ylim(min(all_y_phys) - self.L, max(all_y_phys) + 2*self.L)
        
        ax.set_aspect('equal')
        ax.grid(True, linestyle='--', alpha=0.3)
        plt.title(title)
        plt.show()

# --- Simulation ---

# 1. Initialize with W=1, L=1
domain = EvolvingDomain(W=1, L=1)

# 2. Visualize Initial State
# Should see White (0,0) surrounded by Grey blocks
domain.plot_grid("Step 1: Initial State [0,W]x[0,L]")

# 3. Apply Rule 1: Erode the "right" wall of (0,0)
# The domain physically becomes [0, 2W] x [0, L]
domain.erode_wall((0, 0), 'right')
domain.plot_grid("Step 2: After expanding Right")
print(domain.active_cells)
# 4. Apply Rule 1 again: Erode the "up" wall of the NEW cell (1,0)
domain.erode_wall((1, 0), 'up')
domain.plot_grid("Step 3: After expanding Up from (1,0)")
# ... (After your previous simulation code) ...

# 5. Extract the polygon vertices
loops = domain.get_boundary_polygons()

print(f"Found {len(loops)} closed boundary loop(s).")
for i, poly in enumerate(loops):
    print(f"Loop {i} vertices: {poly}")

# 6. Plotting the Polygon overlay to verify
fig, ax = plt.subplots(figsize=(6, 6))

# Re-plot the grid blocks for context
for ix, iy in domain.active_cells:
    # Quick re-plot of white squares
    rect = patches.Rectangle((ix * domain.W, iy * domain.L), 
                             domain.W, domain.L, 
                             linewidth=1, edgecolor='lightgray', facecolor='white')
    ax.add_patch(rect)

# Plot the polygon lines
for poly in loops:
    # Unpack x and y lists
    xs, ys = zip(*poly)
    # Append the first point to the end to close the visual loop line
    xs = xs + (xs[0],)
    ys = ys + (ys[0],)
    
    ax.plot(xs, ys, color='red', linewidth=3, marker='o', label='Boundary Polygon')

# Set limits
all_indices = domain.active_cells
all_x = [c[0] * domain.W for c in all_indices]
all_y = [c[1] * domain.L for c in all_indices]
ax.set_xlim(min(all_x) - 1, max(all_x) + 2)
ax.set_ylim(min(all_y) - 1, max(all_y) + 2)
ax.set_aspect('equal')
plt.title("Polygon Extraction Verification")
plt.show()

