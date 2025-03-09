import numpy as np

def analyze_predecessors(matrix, target_states, state_labels=None, threshold=0.01):
    """
    Analyze the immediate predecessors of target states.
    
    Args:
        matrix: Transition probability matrix
        target_states: List of target states to analyze
        state_labels: Optional dictionary mapping state IDs to readable labels
        threshold: Minimum transition probability to consider a state as a predecessor
        
    Returns:
        predecessors: Dictionary mapping target states to lists of predecessor states
    """
    predecessors = {}
    
    print("\nPredecessor Analysis for Target States:")
    print("======================================")
    
    for target in target_states:
        target_label = state_labels.get(target, f"State {target}") if state_labels else f"State {target}"
        print(f"\nTarget: {target_label} (State {target})")
        print("-" * (len(f"Target: {target_label} (State {target})")))
        
        # Find states that have a direct transition to this target
        target_predecessors = []
        
        for source in range(matrix.shape[0]):
            if matrix[source, target] >= threshold:
                source_label = state_labels.get(source, f"State {source}") if state_labels else f"State {source}"
                target_predecessors.append((source, source_label, matrix[source, target]))
        
        # Sort by transition probability (highest first)
        target_predecessors.sort(key=lambda x: x[2], reverse=True)
        
        # Store the predecessors
        predecessors[target] = [(s, p) for s, _, p in target_predecessors]
        
        # Print information about each predecessor
        if target_predecessors:
            print(f"Found {len(target_predecessors)} predecessors with probability >= {threshold}:")
            for source, source_label, prob in target_predecessors:
                print(f"  • {source_label} → {target_label} with probability {prob:.4f}")
                
            # Calculate total incoming probability
            total_prob = sum(prob for _, _, prob in target_predecessors)
            print(f"\n  Total incoming probability: {total_prob:.4f}")
            
            # Identify the primary path(s) to this target
            # (predecessors that contribute at least 20% of the incoming probability)
            primary_paths = [(s, l, p) for s, l, p in target_predecessors if p >= 0.2 * total_prob]
            if primary_paths:
                print("\n  Primary incoming paths:")
                for source, source_label, prob in primary_paths:
                    percentage = (prob / total_prob) * 100
                    print(f"  • {source_label} → {target_label}: {prob:.4f} ({percentage:.1f}% of incoming)")
        else:
            print("No direct predecessors found with probability >= {threshold}")
    
    return predecessors

def plot_with_predecessors(time_series, cumulative_series, matrix, source, target_states, 
                          predecessors, max_steps, state_labels=None):
    """
    Plot cumulative probabilities for target states and their key predecessors.
    
    Args:
        time_series: Step-by-step probabilities from original calculation
        cumulative_series: Cumulative probabilities from original calculation
        matrix: Transition probability matrix
        source: Source state
        target_states: List of target states
        predecessors: Dictionary mapping targets to predecessor lists
        max_steps: Maximum number of steps to compute
        state_labels: Optional dictionary of state labels
    """
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    
    # Create subplots
    fig = make_subplots(rows=2, cols=1, 
                        subplot_titles=("Step-by-Step Probability", "Cumulative Probability"),
                        vertical_spacing=0.15)
    
    # Create a color scale for targets
    colors = px.colors.qualitative.Plotly
    target_colors = {target: colors[i % len(colors)] for i, target in enumerate(target_states)}
    
    # Add step-by-step traces
    for i, state in enumerate(target_states):
        label = state_labels.get(state, f"State {state}") if state_labels else f"State {state}"
        
        fig.add_trace(
            go.Scatter(
                x=list(range(len(time_series[state]))),
                y=time_series[state],
                mode='lines',
                name=label,
                line=dict(color=target_colors[state], width=2)
            ),
            row=1, col=1
        )
    
    # Add cumulative traces for target states
    for state in target_states:
        label = state_labels.get(state, f"State {state}") if state_labels else f"State {state}"
        
        fig.add_trace(
            go.Scatter(
                x=list(range(len(cumulative_series[state]))),
                y=cumulative_series[state],
                mode='lines',
                name=f"{label} (Cum.)",
                line=dict(color=target_colors[state], width=2),
                legendgroup=f"group_{state}",
                showlegend=False
            ),
            row=2, col=1
        )
    
    # Get top predecessors for each target (limit to avoid cluttering)
    top_predecessors = {}
    for target in target_states:
        # Get top 3 predecessors, or fewer if there aren't 3
        top_predecessors[target] = predecessors[target][:min(3, len(predecessors[target]))]
    
    # Compute cumulative probabilities for predecessor states
    # Initialize step-by-step probabilities for each state
    all_states = list(set([pred for target in target_states 
                          for pred, _ in top_predecessors[target]]))
    
    # Filter out targets that are already in our analysis
    pred_states = [state for state in all_states if state not in target_states]
    
    if pred_states:
        # Compute cumulative probabilities for predecessors using the original function
        pred_cumulative_series = compute_cumulative_probabilities(matrix, source, pred_states, max_steps)
        
        # Add predecessor traces to the cumulative plot
        for target in target_states:
            target_label = state_labels.get(target, f"State {target}") if state_labels else f"State {target}"
            color = target_colors[target]
            
            for i, (pred, prob) in enumerate(top_predecessors[target]):
                if pred in target_states:
                    continue  # Skip if it's already a target state
                    
                pred_label = state_labels.get(pred, f"State {pred}") if state_labels else f"State {pred}"
                
                # Use lighter shade of the target color
                lightness = 0.7 - (i * 0.2)
                
                # Extract RGB components from hex color
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                
                # Lighten the color
                r = int(r + (255 - r) * lightness)
                g = int(g + (255 - g) * lightness)
                b = int(b + (255 - b) * lightness)
                
                pred_color = f"#{r:02x}{g:02x}{b:02x}"
                
                fig.add_trace(
                    go.Scatter(
                        x=list(range(len(pred_cumulative_series[pred]))),
                        y=pred_cumulative_series[pred],
                        mode='lines',
                        name=f"{pred_label} → {target_label} (p={prob:.2f})",
                        line=dict(color=pred_color, width=1.5, dash='dot'),
                        legendgroup=f"group_{target}"
                    ),
                    row=2, col=1
                )
    
    # Update layout
    fig.update_layout(
        title="Probability Analysis for Target States and Their Predecessors",
        xaxis_title="Number of Steps",
        xaxis2_title="Number of Steps",
        yaxis_title="Probability",
        yaxis2_title="Cumulative Probability",
        legend_title="States",
        hovermode="x unified",
        template="plotly_white",
        height=800
    )
    
    # Add grid and improve readability
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    
    # Save to HTML
    fig.write_html("predecessor_analysis.html")
    print("\nProbability plot with predecessors saved to 'predecessor_analysis.html'")
    
    return fig

# Reuse the cumulative probability function from before
def compute_cumulative_probabilities(matrix, source, target_states, max_steps):
    """
    Compute the cumulative probability of reaching each target state from the source.
    
    Args:
        matrix: Transition probability matrix
        source: Source state (typically 0)
        target_states: List of target states to analyze
        max_steps: Maximum number of steps to compute
        
    Returns:
        cumulative_series: Dictionary with state IDs as keys and cumulative probability arrays as values
    """
    n_states = matrix.shape[0]
    
    # Initialize cumulative series for each target state
    cumulative_series = {state: np.zeros(max_steps + 1) for state in target_states}
    
    # Initial state probability
    initial_dist = np.zeros(n_states)
    initial_dist[source] = 1.0
    
    # Distribution of probability that hasn't yet reached any target
    active_dist = initial_dist.copy()
    
    # Record initial state
    for state in target_states:
        if state == source:
            cumulative_series[state][0] = 1.0
    
    # For each step
    for step in range(1, max_steps + 1):
        # Copy previous cumulative probabilities
        for state in target_states:
            cumulative_series[state][step] = cumulative_series[state][step-1]
        
        # Move active distribution forward one step
        next_dist = np.dot(active_dist, matrix)
        
        # For each target state, add newly arrived probability
        for state in target_states:
            # Add new probability to cumulative
            new_arrival = next_dist[state]
            cumulative_series[state][step] += new_arrival
            
            # Remove this probability from active distribution to avoid counting it again
            next_dist[state] = 0
        
        # Update active distribution for next iteration
        active_dist = next_dist
    
    return cumulative_series

# First compute step-by-step and cumulative probabilities for targets
print("Computing probabilities for target states...")

# Step-by-step probabilities
def compute_step_by_step_probabilities(matrix, source, target_states, max_steps):
    n_states = matrix.shape[0]
    time_series = {state: np.zeros(max_steps + 1) for state in target_states}
    initial_dist = np.zeros(n_states)
    initial_dist[source] = 1.0
    for state in target_states:
        time_series[state][0] = initial_dist[state]
    current_dist = initial_dist.copy()
    for step in range(1, max_steps + 1):
        current_dist = np.dot(current_dist, matrix)
        for state in target_states:
            time_series[state][step] = current_dist[state]
    return time_series
