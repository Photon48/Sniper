grid_size = 3
total_grid_size = grid_size * grid_size  # 9 for a 9x9 grid

best_option1 = 6  # Which subgrid
best_option2 = 4  # Position within that subgrid

# Determine subgrid's top-left corner in the 9x9 grid
subgrid_row = (best_option1 - 1) // grid_size
subgrid_col = (best_option1 - 1) % grid_size
subgrid_start = (subgrid_row * grid_size * total_grid_size) + (subgrid_col * grid_size) + 1

# Determine exact position within the subgrid
position_row = (best_option2 - 1) // grid_size
position_col = (best_option2 - 1) % grid_size
final_node = subgrid_start + (position_row * total_grid_size) + position_col

print(f"Final Node: {final_node}")