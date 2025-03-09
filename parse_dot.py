import re
import numpy as np
import pandas as pd


def filter_dot_file(input_file, target_states):
    """
    Filter a DOT file to only include lines related to target states and their predecessors.
    Keeps the original formatting of the DOT file intact.
    
    Args:
        input_file: Path to the original DOT file
        target_states: List of target state IDs to include
        
    Returns:
        filtered_dot: String containing the filtered DOT content
    """
    # Read the original DOT file
    with open(input_file, 'r') as f:
        content = f.readlines()
    
    # First pass: identify predecessors of target states
    predecessors = set()
    target_set = set(target_states)
    
    for line in content:
        if "->" in line:  # This is an edge line
            # Extract source and target
            edge_match = re.search(r's(\d+)\s+->\s+s(\d+)', line)
            if edge_match:
                source = int(edge_match.group(1))
                target = int(edge_match.group(2))
                
                # If this edge leads to a target state, the source is a predecessor
                if target in target_set:
                    predecessors.add(source)
    
    # Combine targets and predecessors
    nodes_to_keep = target_set.union(predecessors)
    
    # Second pass: keep relevant lines
    filtered_lines = []
    
    # Always keep the header line
    filtered_lines.append("digraph filtered_mdp {\n")
    
    for line in content:
        line = line.strip()
        
        # Skip digraph opening and closing lines
        if line.startswith("digraph") or line == "{" or line == "}":
            continue
            
        # Check if this is a node definition
        if "->" not in line and "[label=" in line:
            node_match = re.search(r's(\d+)', line)
            if node_match and int(node_match.group(1)) in nodes_to_keep:
                filtered_lines.append(line + "\n")
                
        # Check if this is an edge definition
        elif "->" in line:
            edge_match = re.search(r's(\d+)\s+->\s+s(\d+)', line)
            if edge_match:
                source = int(edge_match.group(1))
                target = int(edge_match.group(2))
                
                # Keep edges between nodes we're interested in
                if source in nodes_to_keep and target in nodes_to_keep:
                    filtered_lines.append(line + "\n")
    
    # Add closing bracket
    filtered_lines.append("}\n")
    
    return "".join(filtered_lines)

def parse_dot_file(file_path):
    """
    Parse a DOT file containing a Markov Decision Process and extract nodes and transitions.
    
    Args:
        file_path: Path to the DOT file
        
    Returns:
        nodes: Dictionary mapping node IDs to labels
        transitions: List of tuples (source, target, probability)
    """
    # Read the file content
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Process the DOT file line by line to properly distinguish nodes from edges
    lines = content.split(';')
    
    nodes = {}
    transitions = []
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Check if this is a node definition (doesn't contain "->")
        if "->" not in line and "label=" in line:
            # Extract node ID and label
            node_match = re.search(r's(\d+)\s+\[label="([^"]*)"\]', line)
            if node_match:
                node_id = int(node_match.group(1))
                label = node_match.group(2)
                nodes[node_id] = label
        
        # Check if this is an edge definition (contains "->")
        elif "->" in line and "label=" in line:
            # Extract source, target, and probability
            edge_match = re.search(r's(\d+)\s+->\s+s(\d+)\s+\[label="run:([0-9.]+)"\]', line)
            if edge_match:
                source = int(edge_match.group(1))
                target = int(edge_match.group(2))
                probability = float(edge_match.group(3))
                transitions.append((source, target, probability))
    
    return nodes, transitions

def create_transition_matrix(nodes, transitions):
    """
    Create a transition probability matrix from nodes and transitions.
    
    Args:
        nodes: Dictionary mapping node IDs to labels
        transitions: List of tuples (source, target, probability)
        
    Returns:
        matrix: NumPy array representing the transition probability matrix
        node_ids: List of node IDs in the order they appear in the matrix
    """
    # Get the maximum node ID
    max_node_id = max(nodes.keys())
    
    # Initialize the transition matrix with zeros
    matrix = np.zeros((max_node_id + 1, max_node_id + 1))
    
    # Fill in the transition probabilities
    for source, target, probability in transitions:
        matrix[source, target] = probability
    
    # Create list of node IDs in order
    node_ids = list(range(max_node_id + 1))
    
    return matrix, node_ids

def save_matrix_to_csv(matrix, output_file):
    """
    Save the transition matrix to a CSV file.
    
    Args:
        matrix: NumPy array representing the transition probability matrix
        output_file: Path to save the CSV file
    """
    # Create a DataFrame from the matrix
    df = pd.DataFrame(matrix)
    
    # Save to CSV
    df.to_csv(output_file)
    print(f"Transition matrix saved to {output_file}")

def save_node_labels(nodes, output_file):
    """
    Save the node labels to a text file.
    
    Args:
        nodes: Dictionary mapping node IDs to labels
        output_file: Path to save the labels file
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for node_id in sorted(nodes.keys()):
            f.write(f"Node {node_id}: {nodes[node_id]}\n")
    
    print(f"Node labels saved to {output_file}")
