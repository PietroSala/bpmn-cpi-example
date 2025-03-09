import networkx as nx

def generate_completion_state_labels(dot_file_path):
    """
    Generates a dictionary mapping state IDs to descriptive labels for completion states.
    Translates "Completed True/False priority" to "On Time/Late priority Priority"
    
    Args:
        dot_file_path (str): Path to the DOT file containing the MDP
        
    Returns:
        dict: Dictionary mapping state IDs to descriptive labels
    """
    # Read the DOT file and create a directed graph
    G = nx.DiGraph(nx.nx_pydot.read_dot(dot_file_path))
    
    # Initialize the state labels dictionary
    state_labels = {}
    
    # Find all completion states
    for node, attrs in G.nodes(data=True):
        label = attrs.get('label', '').strip('"')
        
        # Check if this is a completion state
        if label.startswith('Completed'):
            # Format is typically: "Completed True medium" or "Completed False high"
            parts = label.split()
            if len(parts) >= 3:
                # Extract success/failure indicator and priority
                success = parts[1] == "True"
                priority = parts[2] if len(parts) >= 3 else "unknown"
                
                # Create descriptive label: "On Time/Late priority Priority"
                descriptive_label = f"{'On Time' if success else 'Late'} {priority.capitalize()} Priority"
                
                # Extract state ID number (remove the 's' prefix)
                state_id = node.lstrip('s')
                
                # Add to state labels dictionary
                state_labels[state_id] = descriptive_label
    
    return state_labels