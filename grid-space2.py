import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random

class EvolvingDomain:
    def __init__(self, W=1, L=1):
        self.W = W
        self.L = L
        self.active_cells = {(0, 0)}
        self.boundary_blocks = {}
        self.directions = {
            'right': (1, 0), 'left': (-1, 0),
            'up': (0, 1), 'down': (0, -1)
        }
        # Initialize neighbors for the start
        self._update_boundary_neighbors((0, 0))

    def _update_boundary_neighbors(self, cell_idx):
        cx, cy = cell_idx
        for dx, dy in self.directions.values():
            neighbor = (cx + dx, cy + dy)
            if neighbor not in self.active_cells and neighbor not in self.boundary_blocks:
                # Random assignment for this demo
                self.boundary_blocks[neighbor] = random.choice(['blue', 'red'])

    def erode_wall(self, active_cell_idx, direction):
        """ Rule 1: Expand Domain (Blue Wall) """
        if active_cell_idx not in self.active_cells: return
        dx, dy = self.directions[direction]
        target = (active_cell_idx[0] + dx, active_cell_idx[1] + dy)
        
        if target in self.boundary_blocks and self.boundary_blocks[target] == 'blue':
            print(f"ACTION: Eroding Blue wall at {direction}. Domain grows.")
            del self.boundary_blocks[target]
            self.active_cells.add(target)
            self._update_boundary_neighbors(target)

    def grow_wall(self, active_cell_idx, direction):
        """ Rule 2: Shrink Domain (Red Wall attacks) """
        if active_cell_idx not in self.active_cells: return
        dx, dy = self.directions[direction]
        attacker = (active_cell_idx[0] + dx, active_cell_idx[1] + dy)

        if attacker in self.boundary_blocks and self.boundary_blocks[attacker] == 'red':
            print(f"ACTION: Red wall at {direction} grows into {active_cell_idx}.")
            
            # 1. Kill the active cell
            self.active_cells.remove(active_cell_idx)
            
            # 2. Cleanup: The cell is no longer active, so it doesn't need neighbors calculated
            # However, strictly speaking, the 'attacker' is still there. 
            # We don't need to do complex logic here for the skeleton, just removing 
            # the active cell is enough to change the polygon.
            if not self.active_cells:
                print("!!! TERMINATION: Domain annihilated. !!!")

    def get_boundary_polygons(self):
        """ Calculates CCW ordered vertices for the boundary. """
        if not self.active_cells: return []
        
        edges = {}
        for x, y in self.active_cells:
            # Logic: If neighbor is empty, that edge is part of the boundary
            if (x + 1, y) not in self.active_cells: edges[(x + 1, y)] = (x + 1, y + 1) # Right
            if (x, y + 1) not in self.active_cells: edges[(x + 1, y + 1)] = (x, y + 1) # Top
            if (x - 1, y) not in self.active_cells: edges[(x, y + 1)] = (x, y)         # Left
            if (x, y - 1) not in self.active_cells: edges[(x, y)] = (x + 1, y)         # Bottom

        polygons = []
        while edges:
            curr = next(iter(edges))
            start = curr
            poly = []
            while True:
                # Scale grid coordinates to physical dimensions here
                poly.append((curr[0] * self.W, curr[1] * self.L))
                curr = edges.pop(curr, None)
                if curr is None or curr == start: break
            polygons.append(poly)
        return polygons
    def identify_islands(self):
            """
            Scans the active_cells and groups them into connected components (Islands).
            Returns:
                List of sets: [{ (x,y), ... }, { (x,y), ... }]
            """
            unvisited = self.active_cells.copy()
            islands = []
    
            while unvisited:
                # Start a new island from an arbitrary unvisited cell
                start_node = next(iter(unvisited))
                current_island = set()
                queue = [start_node]
                
                # Mark start as visited immediately so we don't re-queue it
                unvisited.remove(start_node)
                current_island.add(start_node)
    
                # BFS / Flood Fill
                while queue:
                    cx, cy = queue.pop(0)
                    
                    # Check 4 neighbors
                    for dx, dy in self.directions.values():
                        neighbor = (cx + dx, cy + dy)
                        
                        # If neighbor is active and we haven't processed it yet
                        if neighbor in unvisited:
                            unvisited.remove(neighbor)
                            current_island.add(neighbor)
                            queue.append(neighbor)
                
                islands.append(current_island)
                
            return islands

    def plot_grid(self, title="Current Domain State"):
            fig, ax = plt.subplots(figsize=(6, 6))
            
            # Helper for rectangles
            def get_rect(ix, iy, color, hatch=None, alpha=1.0):
                return patches.Rectangle((ix * self.W, iy * self.L), self.W, self.L, 
                                         linewidth=0.5, edgecolor='gray', facecolor=color, 
                                         hatch=hatch, alpha=alpha)
    
            # 1. Plot Walls (Blue/Red)
            for (ix, iy), b_type in self.boundary_blocks.items():
                c = 'cornflowerblue' if b_type == 'blue' else 'salmon'
                h = '//' if b_type == 'red' else None
                ax.add_patch(get_rect(ix, iy, c, hatch=h, alpha=0.4))
    
            # 2. Plot Active Cells (Distinct Colors per Island)
            islands = self.identify_islands()
            # Define a palette of pastel colors for different islands
            island_colors = ['white', '#FFEB99', '#C2F0C2', '#E6E6FA', '#FFCCCC'] 
            
            for i, island in enumerate(islands):
                # Cycle through colors if we have many islands
                color = island_colors[i % len(island_colors)]
                
                for ix, iy in island:
                    ax.add_patch(get_rect(ix, iy, color, alpha=1.0))
                    # Label with Island ID to make it obvious
                    ax.text((ix+0.5)*self.W, (iy+0.5)*self.L, f"{ix},{iy}", 
                            ha='center', va='center', fontsize=7, color='black')
    
            # 3. OVERLAY: Boundary Polygons
            loops = self.get_boundary_polygons()
            for poly in loops:
                xs, ys = zip(*poly)
                xs = xs + (xs[0],)
                ys = ys + (ys[0],)
                ax.plot(xs, ys, color='black', linewidth=3, marker='o', markersize=4)
    
            # 4. Viewport
            all_coords = list(self.active_cells) + list(self.boundary_blocks.keys())
            if all_coords:
                xs = [c[0] for c in all_coords]
                ys = [c[1] for c in all_coords]
                ax.set_xlim((min(xs)-1)*self.W, (max(xs)+2)*self.W)
                ax.set_ylim((min(ys)-1)*self.L, (max(ys)+2)*self.L)
            else:
                ax.set_xlim(-2, 2); ax.set_ylim(-2, 2)
    
            ax.set_aspect('equal')
            plt.title(f"{title}\n(Islands Detected: {len(islands)})")
            plt.grid(True, linestyle='--', alpha=0.2)
            plt.show()

# --- 7-STEP SIMULATION ---

# Insert the updated class methods above first...

def run_island_simulation():
    random.seed(42)
    domain = EvolvingDomain(W=1, L=1)
    
    print("--- STARTING ISLAND SEPARATION TEST ---")

    # A. Construct a 3-block line: (0,0) - (1,0) - (2,0)
    # This requires expanding Right twice.
    # Note: We must ensure the walls we want to erode are Blue. 
    # For this demo script, we force them.
    
    # 1. Expand Right from (0,0) -> creates (1,0)
    domain.boundary_blocks[(1,0)] = 'blue' # Force Blue
    domain.erode_wall((0,0), 'right')
    
    # 2. Expand Right from (1,0) -> creates (2,0)
    domain.boundary_blocks[(2,0)] = 'blue' # Force Blue
    domain.erode_wall((1,0), 'right')
    
    domain.plot_grid("Step 1: The 'Dumbbell' (One Connected Component)")

    # B. The Split
    # We want to destroy the middle block (1,0).
    # We need a RED wall adjacent to (1,0) to attack it.
    # Let's say the wall 'up' from (1,0) is Red.
    attacker_pos = (1, 1)
    domain.boundary_blocks[attacker_pos] = 'red'
    
    print("\nAttempting to cut the domain in half...")
    domain.grow_wall((1,0), 'up') # (1,0) is attacked from Up
    
    domain.plot_grid("Step 2: The Split (Two Independent Islands)")

    # C. Independent Evolution
    # Now we have Island A at (0,0) and Island B at (2,0).
    # Let's grow Island A UP, and Island B DOWN.
    
    # 1. Expand Island A (0,0) UP
    domain.boundary_blocks[(0,1)] = 'blue'
    domain.erode_wall((0,0), 'up')
    
    # 2. Expand Island B (2,0) DOWN
    domain.boundary_blocks[(2,-1)] = 'blue'
    domain.erode_wall((2,0), 'down')

    domain.plot_grid("Step 3: Independent Evolution")

if __name__ == "__main__":
    run_island_simulation()
