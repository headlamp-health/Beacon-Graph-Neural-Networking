import marimo

__generated_with = "0.19.7"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(r"""
    ## Predicting missing links between seed node & adverse events
    """)
    return


@app.cell
def _():
    import os
    os.getcwd()
    os.chdir("/Users/naveendeevi/Python Projects/Beacon Graph Neural Networking")
    return


@app.cell
def _():
    import networkx as nx
    import marimo as mo
    from pyvis.network import Network
    import numpy as np
    import json
    import pandas as pd
    return Network, json, mo, np, nx, pd


@app.cell
def _(mo):
    # Update the runtime limit directly in a cell
    # This sets it to ~100MB (adjust as needed)
    mo._runtime.context.get_context().marimo_config["runtime"]["output_max_bytes"] = 100_000_000
    return


@app.cell
def _(Network, json, mo, nx):
    ## Functions

    def build_graph_from_node_list(graph, nodes_list):
        """
        Takes a list of node dictionaries, uses 'id' as the node key, 
        stores the remaining data as attributes, and prints the graph status.
        """
        G = graph

        # Process each dictionary in the list
        processed_nodes = []
        for node_dict in nodes_list:
            # Create a copy so we don't destroy the original source data
            attrs = node_dict.copy()

            # Pop the 'id' to use as the primary key
            node_id = attrs.pop('id')

            # Format as (id, attribute_dict) for NetworkX
            processed_nodes.append((node_id, attrs))

        # Add all nodes to the graph at once
        G.add_nodes_from(processed_nodes)

        # Print the result as requested
        #print(f"Nodes in Graph: {list(G.nodes(data=True))}")
        print(f"--- Nodes Implementation Complete ---")
        print(f"Total Nodes Added: {len(processed_nodes)}")

        return G

    # Color the nodes
    # A professional, high-contrast biomedical palette
    # Extended Palette for Medical Knowledge Graphs
    KG_COLOR_PALETTE = {
        'Drug': '#007bff',           # Blue
        'Brandname': '#17a2b8',      # Cyan
        'Manufacturer': '#adb5bd',   # Light Grey
        'Drugclass': '#e83e8c',      # Pink
        'Target': '#28a745',         # Green
        'Condition': '#dc3545',      # Red
        'FDAApplication': '#6610f2', # Indigo
        'FDAProduct': '#6f42c1',     # Purple
        'Formulation': '#20c997',    # Teal
        'NDCPackage': '#fd7e14',     # Orange
        'AdverseEffect': '#ffc107',  # Amber
        'Enzyme': '#a4ac86',         # Olive Green
        'unknown': '#6c757d'         # Dark Grey
    }

    def apply_kg_colors(G, palette=KG_COLOR_PALETTE):
        """
        Applies colors and sets specific node sizes based on node importance.
        """
        for node_id, data in G.nodes(data=True):
            # 1. Get type and convert to lowercase for matching
            raw_type = data.get('node_type', 'unknown')
            n_type = str(raw_type).replace(" ", "")

            # 2. Assign Color
            color = palette.get(n_type, palette['unknown'])
            G.nodes[node_id]['color'] = color

            # 3. Size Logic (Central nodes are larger)
            if n_type in ['drug', 'target', 'condition']:
                G.nodes[node_id]['size'] = 35
            else:
                G.nodes[node_id]['size'] = 20

        print("Color coding and sizing applied successfully.")
        return G

    # Usage:
    # G = apply_kg_colors(G)

    # Apply to your graph
    #G = apply_default_colors(G)

    def add_edges_from_list(G, edges_list):
        """
        Input: List of dicts with keys: 'id', 'source_id', 'target_id', 'edge_type'
        Output: NetworkX DiGraph with relational attributes
        """
        processed_edges = []

        # These keys are reserved by NetworkX/Pyvis and will cause TypeErrors 
        # if passed inside the attribute dictionary.
        reserved_keys = {'source', 'target', 'to', 'from', 'self'}

        for edge_dict in edges_list:
            u = edge_dict['source_id']
            v = edge_dict['target_id']

            # Create a copy so we don't mutate the original data list
            attrs = edge_dict.copy()

            # 1. Sanitize keys: Rename anything in reserved_keys
            # We use list(attrs.keys()) to avoid 'dictionary changed size' error
            for key in list(attrs.keys()):
                if key.lower() in reserved_keys:
                    attrs[f"data_{key}"] = attrs.pop(key)

            # 2. Add Visualization standard keys
            rel = attrs.get('edge_type', 'interacts')
            attrs['label'] = rel  # Visible text on edge

            # 3. Create a clean tooltip (title)
            tooltip = f"Relation: {rel}"
            if 'weight' in attrs:
                tooltip += f"<br>Weight: {attrs['weight']}"
            if 'ki_nm' in attrs:
                tooltip += f"<br>Ki: {attrs['ki_nm']} nm"
            attrs['title'] = tooltip 

            processed_edges.append((u, v, attrs))

        G.add_edges_from(processed_edges)

        print(f"--- Edge Implementation Complete ---")
        print(f"Total Edges Added: {G.number_of_edges()}")
        return G

    # Visualize the graph 
    # def visualize_interactive_graph(G, filename="drug_graph.html"):
    #     # Initialize Pyvis
    #     net = Network(height="700px", width="100%", notebook=True, directed=True, cdn_resources='remote')

    #     # Import NetworkX graph
    #     net.from_nx(G)

    #     # Physics makes it easy to see clusters of "Drug Classes"
    #     net.toggle_physics(True)

    #     # Save and show
    #     return net.show(filename)



    def visualize_interactive_graph(G, filename="drug_graph.html"):
        # 1. Update node metadata
        for node_id in G.nodes():
            G.nodes[node_id]['label'] = str(node_id)
            node_type = G.nodes[node_id].get('node_type', 'Unknown')
            G.nodes[node_id]['title'] = f"ID: {node_id}\nType: {node_type}"

        # 2. Initialize Pyvis (notebook=False is critical here)
        net = Network(height="700px", width="100%", notebook=False, directed=True, cdn_resources='remote')

        # 3. Load the NetworkX graph
        net.from_nx(G)
        net.toggle_physics(True)

        # 4. Generate the HTML string directly instead of saving/showing
        html_string = net.generate_html()

        # 5. Wrap in an iframe to prevent CSS/JS conflicts with Marimo
        return mo.Html(
            f'<iframe srcdoc="{html_string.replace('"', '&quot;')}" '
            f'width="100%" height="750px" style="border:none;"></iframe>'
        )


    def filter_graph_by_type(G, target_types):
        """
        Returns a subgraph containing only the nodes of the specified types.
        target_types: list of strings, e.g., ['Drug', 'Enzyme']
        """
        # Convert target types to lowercase for robust matching
        target_types = [t.lower() for t in target_types]

        # Identify nodes that match the criteria
        nodes_to_keep = [
            node_id for node_id, data in G.nodes(data=True) 
            if str(data.get('node_type', '')).lower() in target_types
        ]

        # Create the subgraph
        filtered_G = G.subgraph(nodes_to_keep).copy()

        print(f"Filtered Graph: {filtered_G.number_of_nodes()} nodes, {filtered_G.number_of_edges()} edges.")
        return filtered_G


    def filter_graph_by_edge_type(G, target_edge_types):
        """
        Filters the graph using the 'edge_type' attribute.
        """
        targets = [t.lower().strip() for t in target_edge_types]

        # Identify edges to keep
        edges_to_keep = [
            (u, v) for u, v, data in G.edges(data=True)
            if str(data.get('edge_type', '')).lower().strip() in targets
        ]

        if not edges_to_keep:
            print("⚠️ No matching edges found. Visualization will be empty.")
            return G.__class__()

        # Create the edge-induced subgraph
        filtered_G = G.edge_subgraph(edges_to_keep).copy()

        # Remove nodes that no longer have edges
        orphans = [n for n, deg in dict(filtered_G.degree()).items() if deg == 0]
        filtered_G.remove_nodes_from(orphans)

        print(f"✅ Filtered Graph: {filtered_G.number_of_nodes()} nodes, {filtered_G.number_of_edges()} edges.")
        return filtered_G


    def filter_graph_refined(G, target_node_types, target_edge_types):
        """
        Filters graph by both node types and edge types in a single pass.
        """
        # Normalize everything for matching
        node_targets = [n.lower().strip() for n in target_node_types]
        edge_targets = [e.lower().strip() for e in target_edge_types]

        # Create the new graph
        filtered_G = G.__class__()

        # 1. Identify valid nodes based on type
        valid_nodes = {
            node_id for node_id, data in G.nodes(data=True)
            if str(data.get('node_type', '')).lower().strip() in node_targets
        }

        # 2. Add these nodes to the new graph
        # We use a subset of the original nodes to ensure attributes carry over
        filtered_G.add_nodes_from((n, G.nodes[n]) for n in valid_nodes)

        # 3. Add edges ONLY if they connect valid nodes AND match the edge type
        edges_added = 0

        # Handle both MultiGraph and standard Graph
        if G.is_multigraph():
            for u, v, k, data in G.edges(data=True, keys=True):
                if u in valid_nodes and v in valid_nodes:
                    etype = str(data.get('edge_type', '')).lower().strip()
                    if etype in edge_targets:
                        filtered_G.add_edge(u, v, key=k, **data)
                        edges_added += 1
        else:
            for u, v, data in G.edges(data=True):
                if u in valid_nodes and v in valid_nodes:
                    etype = str(data.get('edge_type', '')).lower().strip()
                    if etype in edge_targets:
                        filtered_G.add_edge(u, v, **data)
                        edges_added += 1

        # 4. Final Cleanup: Remove nodes that ended up with no edges after edge filtering
        orphans = [n for n, degree in dict(filtered_G.degree()).items() if degree == 0]
        filtered_G.remove_nodes_from(orphans)

        print(f"--- Filter Results ---")
        print(f"Nodes kept: {filtered_G.number_of_nodes()}")
        print(f"Edges kept: {filtered_G.number_of_edges()}")

        return filtered_G


    def filter_graph_by_hops(G, source_node_id, num_hops=1):
        """
        Extracts a subgraph centered around source_node_id up to n hops away.

        Inputs:
        - G: The complete NetworkX graph.
        - source_node_id: The exact ID of the starting node (e.g., 'drug:aripiprazole').
        - num_hops: Number of steps to branch out (radius).
        """
        if source_node_id not in G:
            print(f"❌ Error: Node ID '{source_node_id}' not found in the graph.")
            return None

        # nx.ego_graph captures the node and all nodes within 'num_hops' distance.
        # undirected=False follows directed edges only. 
        # Set undirected=True if you want to follow edges 'backwards' too.
        sub_G = nx.ego_graph(G, source_node_id, radius=num_hops, undirected=False)

        print(f"✅ Extracted {num_hops}-hop neighborhood.")
        print(f"Nodes: {sub_G.number_of_nodes()} | Edges: {sub_G.number_of_edges()}")

        return sub_G.copy()


    def load_and_merge(file_list):
        with open(file_list[0], 'r') as f:
            base_data = json.load(f)

        #with open(file_list[1], 'r') as f:
            # extend() modifies base_data in-place, avoiding a third list allocation
        #    base_data.extend(json.load(f))

        return base_data


    def prune_direct_id_prefix_edges(G, seed_id, prefix):
        """
        Removes direct edges from seed_id to any node whose ID 
        starts with a specific prefix (e.g., 'adverse:').
        """
        if seed_id not in G:
            print(f"❌ Seed ID {seed_id} not found.")
            return G

        # Identify edges where the neighbor's ID starts with the prefix
        # We check successors (Drug -> Adverse)
        edges_to_remove = [
            (seed_id, neighbor) 
            for neighbor in G.successors(seed_id) 
            if str(neighbor).startswith(prefix)
        ]

        # Create copy and remove
        new_G = G.copy()
        new_G.remove_edges_from(edges_to_remove)

        print(f"--- Prefix Pruning Report ---")
        print(f"Seed: {seed_id}")
        print(f"Prefix: '{prefix}'")
        print(f"Edges identified & removed: {len(edges_to_remove)}")

        return new_G


    def find_all_paths_between(G, source_name, target_name, max_hops=7):
        """
        Finds all unique directed paths between two nodes within a hop limit.

        Inputs:
        - G: The NetworkX DiGraph.
        - source_name: The name or ID of the start node (e.g., 'Aripiprazole').
        - target_name: The name or ID of the end node (e.g., 'Schizophrenia').
        - max_hops: Maximum path length to search (prevents infinite search).
        """
        # 1. Helper to handle Name vs ID search
        def get_id(name):
            matches = [n for n, d in G.nodes(data=True) 
                       if name.lower() in str(d.get('node_name', n)).lower()]
            return matches[0] if matches else None

        s_id = get_id(source_name)
        t_id = get_id(target_name)

        if not s_id or not t_id:
            print(f"❌ Could not find source '{source_name}' or target '{target_name}'")
            return []

        # 2. Compute simple paths
        # Simple paths avoid cycles (A -> B -> A)
        paths = list(nx.all_simple_paths(G, source=s_id, target=t_id, cutoff=max_hops))

        print(f"✅ Found {len(paths)} paths within {max_hops} hops.")
        return paths



    def show_immediate_neighbors(G, seed_id):
        """
        Identifies and prints all nodes directly connected to the seed.
        Distinguishes between 'pointing to' (successors) and 'pointed by' (predecessors).
        """
        if seed_id not in G:
            print(f"❌ Seed ID '{seed_id}' not found in the graph.")
            return []

        # In a DiGraph, neighbors usually means nodes the drug points TO (out-edges)
        outgoing = list(G.successors(seed_id))
        # Predecessors are nodes pointing TO the drug (in-edges)
        incoming = list(G.predecessors(seed_id))

        print(f"--- Neighborhood Report for: {seed_id} ---")
        print(f"Total Outgoing Neighbors (Successors): {len(outgoing)}")
        print(f"Total Incoming Neighbors (Predecessors): {len(incoming)}")
        print("-" * 40)

        # Display breakdown by type for clarity
        for neighbor in outgoing:
            n_type = G.nodes[neighbor].get('node_type', 'Unknown')
            # Using the ID since we know yours have prefixes like 'adverse:'
            print(f" -> [{n_type:10}] ID: {neighbor}")

        return outgoing + incoming
    return (
        KG_COLOR_PALETTE,
        add_edges_from_list,
        apply_kg_colors,
        build_graph_from_node_list,
        filter_graph_by_edge_type,
        filter_graph_by_hops,
        filter_graph_by_type,
        load_and_merge,
        prune_direct_id_prefix_edges,
        show_immediate_neighbors,
        visualize_interactive_graph,
    )


@app.cell
def _(load_and_merge):
    # Read nodes JSON


    # Replace 'your_data.json' with your actual file path
    # Define file pairs to process
    files = {
        'nodes': ['merged_graph_v6_nodes.json'],
        'edges': ['merged_graph_v6_edges_weighted_brex_trimmed.json']
    }

    nodes_data_master = load_and_merge(files['nodes'])
    edges_data_master = load_and_merge(files['edges'])
    return edges_data_master, nodes_data_master


@app.cell
def _(edges_data_master):
    for i_1 in edges_data_master:
        if i_1['source_id'] == 'drug:aripiprazole' and i_1['target_id'].startswith('condition:'):
            print(i_1)
    return


@app.cell
def _(
    KG_COLOR_PALETTE,
    add_edges_from_list,
    apply_kg_colors,
    build_graph_from_node_list,
    edges_data_master,
    nodes_data_master,
    nx,
    visualize_interactive_graph,
):
    # Shows the complete graph
    # Step 1: Initialize graph
    graph_V0 = nx.DiGraph() 

    # Step 2: Add nodes to the graph 
    graph_V1 = build_graph_from_node_list(graph_V0,nodes_data_master)

    # Step 3: Add edges to the graph
    graph_V2 = add_edges_from_list(graph_V1,edges_data_master)

    #Step 4: Visualize the graph
    graph_V3 = apply_kg_colors(graph_V2,KG_COLOR_PALETTE)
    visualize_interactive_graph(graph_V3)
    return (graph_V3,)


@app.cell
def _():
    #list(dict.fromkeys(x['edge_type'] for x in edges_data_master))
    return


@app.cell
def _(
    filter_graph_by_edge_type,
    filter_graph_by_type,
    graph_V3,
    visualize_interactive_graph,
):
    # --- Usage ---
    # The unneccessary nodes like Manufactured, etc.,. will be removed in this graph. 
    # 1. Choose your types
    my_targets = ['Drug','Gene','Pathway','BrainRegion','BiologicalProcess','MolecularFunction',
                  'CellularComponent','Condition','Symptom','Circuit','Neurotransmitter','NTSystem',
                  'RDoCDomain','RDoCConstruct','Target','DrugClass','AdverseEffect','Enzyme']

    my_targets_edges = ["TARGETS","PARTICIPATES_IN","EXPRESSED_IN","INTERACTS_WITH","INVOLVED_IN","HAS_FUNCTION","LOCATED_IN",
                        "ASSOCIATED_WITH","HAS_SYMPTOM","COMORBID_WITH","ASSOCIATED_WITH_GENE","HAS_CHILD","HAS_ORIGIN",
                        "HAS_TERMINUS","MODULATES","UNDERLIES","PRIMARY_NT","PART_OF","HAS_CONSTRUCT","DYSFUNCTION_CAUSES",
                        "ENCODES","BELONGS_TO_CLASS","INDICATED_FOR","CONTRAINDICATED_FOR","CAUSES","METABOLIZED_BY",
                        "CONTAINS_INGREDIENT","HAS_FORMULATION","HAS_NDC_PACKAGE"]

    # Step 1: Filter by edge type first. 
    # This ensures we only look at the RELATIONSHIPS you care about.
    graph_V4 = filter_graph_by_edge_type(graph_V3, my_targets_edges)

    # Step 2: Now filter that result by the NODE types.
    # This prunes the graph down to the specific entities (Drug, Gene, etc.)
    graph_V5 = filter_graph_by_type(graph_V4, my_targets)

    # Step 3: Visualize
    visualize_interactive_graph(graph_V5, filename="filtered_drug_enzyme.html")
    return (graph_V5,)


@app.cell
def _(graph_V5, prune_direct_id_prefix_edges, visualize_interactive_graph):
    # Remove the direct links between Aripiprazole & all the adverse 
    graph_V6 = prune_direct_id_prefix_edges(graph_V5, "drug:aripiprazole", "adverse:")
    visualize_interactive_graph(graph_V6)
    return (graph_V6,)


@app.cell
def _(graph_V6, show_immediate_neighbors):
    show_immediate_neighbors(graph_V6,"circuit:mesolimbic")
    return


@app.cell
def _():
    # Validates the neighbors fo Aripirazole, to make sure no edges to 'Adverse reactions'
    #show_immediate_neighbors(graph_V6,'drug:aripiprazole')
    return


@app.cell
def _(graph_V6, nx):
    # Find and show Aripiprazole, Brexpiprazole. 

    # Search for the node ID
    target_node = [n for n in graph_V6.nodes() if 'drug:aripiprazole' in str(n).lower()]

    if target_node:
        node_id = target_node[0]
        print(f"Found Node ID: {node_id}")

        # 2. View the Node Attributes
        print("\n--- Node Attributes ---")
        print(graph_V6.nodes[node_id])

        # 3. View the Connections (Edges)
        print("\n--- Outgoing Connections (Edges) ---")
        for neighbor in graph_V6.neighbors(node_id):
            edge_data = graph_V6.get_edge_data(node_id, neighbor)
            #print(f"Connected to: {neighbor} | Relation: {edge_data.get('label', 'N/A')}")
    else:
        print("Node not found. Check if the name is exact or if it was filtered out.")

    if target_node:
        # Create a subgraph of Aripiprazole and everything it connects to
        # radius=1 means direct neighbors, radius=2 includes neighbors of neighbors
        ego_G = nx.ego_graph(graph_V6, target_node[0], radius=7)

        # Render just this small portion
        #print(type(graph_V6))
        #print(type(ego_G))
        print(ego_G)
        #visualize_interactive_graph(ego_G, filename="aripirazole_neighbors.html")
    return


@app.cell
def _(graph_V6):
    # Assuming your node attribute key is 'node_type'
    condition_nodes = [n for n, d in graph_V6.nodes(data=True) 
                       if d.get('node_type') == 'Condition']

    print(f"Found {len(condition_nodes)} Condition nodes.")
    print("Nodes:", condition_nodes[:])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Implement Random Walk with Restart - Unidirectional & no weights to the edges.
    """)
    return


@app.cell
def _(np, nx):

    #Function to filter the graph for only outward edges. 
    def get_outward_subgraph(G, seed_name, hops=7):
        # 1. Find the exact ID
        matches = [n for n, d in G.nodes(data=True) 
                   if seed_name.lower() in str(d.get('node_name', n)).lower()]

        if not matches:
            return None, None

        seed_id = matches[0]

        # 2. Extract the ego graph (discovery phase)
        sub_g = nx.ego_graph(G, seed_id, radius=hops, undirected=True).copy()

        # 3. PRUNING PHASE: Remove edges pointing back to the seed
        # We look for any edge where the 'target' (v) is our seed_id
        back_edges = [(u, v) for u, v in sub_g.edges() if v == seed_id]
        sub_g.remove_edges_from(back_edges)

        # 4. Optional: Remove "Lateral" edges if you want a pure hierarchy
        # (Only keep edges where the target is further from the seed than the source)

        print(f"Removed {len(back_edges)} back-pointing edges to {seed_name}.")
        return sub_g, seed_id

    # Function for RWR. 
    def run_robust_rwr(G, seed_id, alpha=0.15):
        nodes = list(G.nodes())
        node_to_idx = {node: i for i, node in enumerate(nodes)}
        n = len(nodes)

        # 1. Get Adjacency Matrix
        A = nx.to_numpy_array(G, nodelist=nodes, weight=None)

        # 2. Fix Dead Ends (Sinks)
        # If a node has no outgoing edges, make it point back to the seed
        # This prevents signal loss.
        out_degrees = np.sum(A, axis=0)
        for i in range(n):
            if out_degrees[i] == 0:
                A[node_to_idx[seed_id], i] = 1 

        # 3. Simple Column Normalization (Safer than Symmetric for small subgraphs)
        # W = A / col_sums
        col_sums = A.sum(axis=0)
        W = A / col_sums

        # 4. Seed Vector
        p0 = np.zeros(n)
        p0[node_to_idx[seed_id]] = 1.0

        # 5. Iteration
        pk = p0.copy()
        for i in range(200): # Increased iterations
            pk_next = (1 - alpha) * np.dot(W, pk) + alpha * p0

            # Check for convergence
            diff = np.linalg.norm(pk_next - pk, ord=1)
            if diff < 1e-12:
                print(f"Converged at iteration {i}")
                break
            pk = pk_next

        return {nodes[i]: pk[i] for i in range(n)}

    # Function that conserves the RWR

    def run_conserving_rwr(G, seed_id, alpha=0.15, max_iter=100):
        nodes = list(G.nodes())
        node_to_idx = {node: i for i, node in enumerate(nodes)}
        n = len(nodes)
        seed_idx = node_to_idx[seed_id]

        # 1. Create Adjacency Matrix
        # We want A[i, j] = 1 if there is an edge from j to i (Transition Matrix)
        A = nx.to_numpy_array(G, nodelist=nodes).T 

        # 2. Handle Sinks (Dead Ends)
        # If a column (source node) sums to 0, it's a dead end. 
        # We force dead ends to point back to the seed node.
        col_sums = A.sum(axis=0)
        for j in range(n):
            if col_sums[j] == 0:
                A[seed_idx, j] = 1.0  # Sink nodes 'teleport' back to seed

        # 3. Final Normalization
        W = A / A.sum(axis=0)

        # 4. Iterative Propagation
        p0 = np.zeros(n)
        p0[seed_idx] = 1.0
        pk = p0.copy()

        for i in range(max_iter):
            pk_next = (1 - alpha) * np.dot(W, pk) + alpha * p0

            # Monitor Total Fluid (Should always be 1.0)
            total_fluid = np.sum(pk_next)

            if np.linalg.norm(pk_next - pk, ord=1) < 1e-10:
                print(f"✅ Converged at iteration {i}. Total system fluid: {total_fluid:.2f}")
                break
            pk = pk_next

        return {nodes[i]: pk[i] for i in range(n)}

    # Debug the RWR
    def debug_rwr(G, seed_id, alpha=0.15):
        nodes = list(G.nodes())
        node_to_idx = {node: i for i, node in enumerate(nodes)}
        n = len(nodes)

        if seed_id not in node_to_idx:
            return f"❌ Error: seed_id '{seed_id}' is not in the graph nodes!"

        # 1. Create Adjacency Matrix
        # Ensure we are pulling the structural edges
        A = nx.to_numpy_array(G, nodelist=nodes, weight=None)

        # --- DIAGNOSTIC CHECK ---
        seed_idx = node_to_idx[seed_id]
        # Outgoing edges are rows in a column-normalized setup (A[target, source])
        # But nx.to_numpy_array usually returns A[source, target]
        # Let's check how many connections the seed has in the matrix:
        seed_out_edges = np.sum(A[seed_idx, :]) 
        print(f"DEBUG: Seed node '{seed_id}' has {seed_out_edges} outgoing edges in the Matrix.")

        if seed_out_edges == 0:
            print("❌ CRITICAL: The Matrix thinks the seed has NO neighbors. Propagation is impossible.")
            return None

        # 2. Normalize (Column-Stochastic)
        # Transpose A if necessary so flow is Source -> Target
        # Standard: W[i, j] is probability of moving from j to i
        W = A.T 
        sums = W.sum(axis=0)
        sums[sums == 0] = 1
        W = W / sums

        # 3. Initial Vector
        p0 = np.zeros(n)
        p0[seed_idx] = 1.0

        # 4. ONE STEP TEST
        p1 = (1 - alpha) * np.dot(W, p0) + alpha * p0
        moved_fluid = np.sum(p1) - p1[seed_idx]
        print(f"DEBUG: After 1 step, {moved_fluid:.6f} fluid moved away from the seed.")

        # 5. Full Loop
        pk = p0.copy()
        for i in range(100):
            pk_next = (1 - alpha) * np.dot(W, pk) + alpha * p0
            if np.linalg.norm(pk_next - pk, ord=1) < 1e-9:
                break
            pk = pk_next

        return {nodes[i]: pk[i] for i in range(n)}
    return get_outward_subgraph, run_conserving_rwr


@app.cell
def _():
    # Check if any edges still point to the seed
    #incoming_to_seed = [u for u, v in sub_graph.edges() if v == arip_id]
    #print(f"Nodes pointing back to seed: {incoming_to_seed}") # Should be an empty list []
    return


@app.cell
def _(get_outward_subgraph, graph_V6, nx, run_conserving_rwr_V2):
    # Step 1: Extract outward neighborhood
    sub_graph_V1, arip_id = get_outward_subgraph(graph_V6, "drug:aripiprazole", hops=7)

    #debug_rwr(sub_graph, arip_id)

    # Step 2: Run Random Walk with Restart with popular nodes normalized and score is significant enough
    #rwr_scores = run_conserving_rwr(sub_graph, arip_id)
    rwr_scores = run_conserving_rwr_V2(sub_graph_V1, arip_id)

    # Check reachability
    reachable_nodes = nx.descendants(sub_graph_V1, arip_id)
    print(f"Total nodes reachable from {arip_id}: {len(reachable_nodes)}")

    if len(reachable_nodes) == 0:
        print("❌ Critical Error: No nodes are reachable from the seed. Check edge directions!")

    # Step 3: Sort nodes by score descending
    sorted_hits = sorted(rwr_scores.items(), key=lambda x: x[1], reverse=True)

    # Step 4: Keep the top 50 nodes
    top_50_nodes = [node_id for node_id, score in sorted_hits[:50]]

    # Step 5: Extract the final high-confidence subgraph
    final_g = sub_graph_V1.subgraph(top_50_nodes).copy()
    return sorted_hits, sub_graph_V1


@app.cell
def _(sub_graph_V1, visualize_interactive_graph):
    visualize_interactive_graph(sub_graph_V1, filename="aripirazole_neighbors.html")
    return


@app.cell
def _(sub_graph_V1):
    for i in sub_graph_V1.edges(): 
        #print(i)
        #print(i[1])
        if i[1].startswith('Pathway:'):
            print(i)
            #sg = filter_graph_by_hops(graph_V6,'gene:DRD2',num_hops=1)

    return


@app.cell
def _(np, nx, pd, tqdm):

    def generate_all_paths_report(G, seed_id, prefix, max_hops=4):
        """
        Finds ALL simple paths up to max_hops from seed to target nodes.
        Returns detailed statistics on path lengths.
        """
        if seed_id not in G:
            print(f"❌ Seed ID '{seed_id}' not found.")
            return None

        target_nodes = [n for n in G.nodes() if str(n).startswith(prefix)]

        all_path_lengths = []
        per_node_stats = []

        print(f"🔍 Analyzing all paths (max {max_hops} hops) for {len(target_nodes)} targets...")

        for target in tqdm(target_nodes, desc="Processing Targets"):
            # Find all simple paths (no cycles) up to the cutoff
            paths = list(nx.all_simple_paths(G, source=seed_id, target=target, cutoff=max_hops))

            if paths:
                lengths = [len(p) - 1 for p in paths] # -1 because length is number of edges
                all_path_lengths.extend(lengths)

                per_node_stats.append({
                    "Node": target,
                    "Path_Count": len(paths),
                    "Min_Dist": np.min(lengths),
                    "Max_Dist": np.max(lengths),
                    "Mean_Dist": np.mean(lengths),
                    "Median_Dist": np.median(lengths)
                })

        if not all_path_lengths:
            print(f"⚠️ No paths found within {max_hops} hops.")
            return None

        # Global Statistics
        global_stats = {
            "Global Min Path": np.min(all_path_lengths),
            "Global Max Path": np.max(all_path_lengths),
            "Global Mean Path": np.mean(all_path_lengths),
            "Global Median Path": np.median(all_path_lengths)
        }

        global_mean_of_stats = np.mean(list(global_stats.values()))

        # Print Report
        print(f"\n📊 ALL-PATHS REPORT (Cutoff: {max_hops} hops)")
        print(f"Seed: {seed_id} | Total Paths Found: {len(all_path_lengths)}")
        print("-" * 50)
        for key, val in global_stats.items():
            print(f"{key:25}: {val:.4f}")
        print(f"{'Global Proximity Index':25}: {global_mean_of_stats:.4f}")
        print("-" * 50)

        return pd.DataFrame(per_node_stats)


    def list_all_paths_dataframe(G, seed_id, prefix, max_hops=3):
        """
        Enumerates every path between the seed and target nodes.
        Returns a pandas DataFrame where each row is a unique path.
        """
        if seed_id not in G:
            print(f"❌ Seed ID '{seed_id}' not found.")
            return pd.DataFrame()

        target_nodes = [n for n in G.nodes() if str(n).startswith(prefix)]

        all_paths_data = []

        print(f"🛤️ Enumerating paths up to {max_hops} hops...")

        for target in tqdm(target_nodes, desc="Tracing Paths"):
            # find_all_simple_paths prevents infinite loops in cycles
            paths = list(nx.all_simple_paths(G, source=seed_id, target=target, cutoff=max_hops))

            for p in paths:
                all_paths_data.append({
                    "Target_Node": target,
                    "Hops": len(p) - 1,
                    "Path_Sequence": " -> ".join(p),
                    "Nodes_In_Path": p,
                    "Contains_Proteins": any("gene" in node.lower() or "protein" in node.lower() for node in p)
                })

        df = pd.DataFrame(all_paths_data)

        if not df.empty:
            print(f"✅ Success: Found {len(df)} unique paths.")
            # Sort by hops so the most direct mechanisms are at the top
            return df.sort_values(by=["Target_Node", "Hops"])
        else:
            print("⚠️ No paths found.")
            return pd.DataFrame()

    # Example Usage:
    # df_paths = list_all_paths_dataframe(sub_graph_V2, arip_id_V2, "adverse:", max_hops=3)
    return generate_all_paths_report, list_all_paths_dataframe


@app.cell
def _(generate_all_paths_report, nodes_data_master, sub_graph_V1):
    ct = 0 
    for i_3 in nodes_data_master:
        if i_3['node_type'] == 'Gene' and ct < 3:
            print(i_3['id'])
            x = generate_all_paths_report(sub_graph_V1,i_3['id'],'circuit:',max_hops=9)
            print('result:%s'%x)
            ct = ct + 1 
    return


@app.cell
def _(generate_all_paths_report, sub_graph_V1):
    generate_all_paths_report(sub_graph_V1,'gene:DRD2','circuit:',max_hops=20)
    return


@app.cell
def _(list_all_paths_dataframe, sub_graph_V1):
    all_paths_df = list_all_paths_dataframe(sub_graph_V1,'symptom:obsessive_compulsive_behavior','pathway:',max_hops=7)
    return (all_paths_df,)


@app.cell
def _(all_paths_df):
    all_paths_df
    return


@app.cell
def _(all_paths_df):
    all_paths_df.to_csv('all_paths_from_aripiprazole_V3.csv')
    return


@app.cell
def _(all_paths_df):
    all_paths_df[all_paths_df['Target_Node'] == 'symptom:depressivity']
    return


@app.cell
def _(filter_graph_by_hops, graph_V6):
    sg = filter_graph_by_hops(graph_V6,'gene:DRD2',num_hops=1)
    #visualize_interactive_graph(sg, filename="adverse:agitation.html")
    print(sg.nodes())
    return


@app.cell
def _(sorted_hits):
    for node, score in sorted_hits:
        if score > 0.00:
        #and node.startswith('symptom:'):
            print(f"Node: {node:<20} | Score: {score:.10f}")
    return (node,)


@app.cell
def _():
    # All the paths between two nodes

    #import networkx as nx
    #paths_1 = find_all_paths_between(final_g,'drug:aripiprazole','adverse:akathisia')

    #print(len(paths_1))
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Z Scores of the node score.
    1. Calculates the node original score using 'run_conserving_rwr'
    2. Then shuffles the edges, shuffling the biology but preserving the degrees. Uses the function 'Randomizer'
    3. The main function triggers all the above function
    4. Runs 'run_conserving_rwr' function and calculate the score.
    5. Generates 100 random graphs using 'Randomizer' function.
    6. Stores all the results and calcualte the mean & std.
    7. Finally creates the Z score.
    """)
    return


@app.cell
def _(np, nx, run_conserving_rwr):
    #import numpy as np
    #import networkx as nx
    import random
    from tqdm import tqdm # For progress tracking

    # --- LAYER 1: THE WORKER ---
    def run_conserving_rwr_V2(G, seed_id, alpha=0.15):
        """Calculates steady-state scores ensuring no signal is lost at sinks."""
        nodes = list(G.nodes())
        node_to_idx = {node: i for i, node in enumerate(nodes)}
        n = len(nodes)
        seed_idx = node_to_idx[seed_id]

        # Build Transition Matrix (Transpose of Adjacency)
        A = nx.to_numpy_array(G, nodelist=nodes).T 

        # Handle Sinks: Force dead-ends to teleport back to seed
        col_sums = A.sum(axis=0)
        for j in range(n):
            if col_sums[j] == 0:
                A[seed_idx, j] = 1.0

        # Normalize columns
        W = A / A.sum(axis=0)

        # Power Iteration
        p0 = np.zeros(n)
        p0[seed_idx] = 1.0
        pk = p0.copy()

        for _ in range(100):
            pk_next = (1 - alpha) * np.dot(W, pk) + alpha * p0
            if np.linalg.norm(pk_next - pk, ord=1) < 1e-9:
                break
            pk = pk_next

        return {nodes[i]: pk[i] for i in range(n)}

    # --- LAYER 2: THE RANDOMIZER ---
    def get_randomized_null_graph_safe(G, swaps_per_edge=1):
        """
        Shuffles edges but won't crash if the graph is too dense to 
        achieve the 'perfect' number of swaps.
        """
        R = G.copy()
        n_edges = R.number_of_edges()

        # We lower swaps_per_edge to 1 for large 7-hop graphs to save time
        try:
            nx.directed_edge_swap(
                R, 
                nswap=n_edges * swaps_per_edge, 
                max_tries=n_edges * 20, 
                seed=None
            )
        except nx.NetworkXAlgorithmError:
            # If it hits the limit, we just accept the partially shuffled graph
            pass
        return R

    # --- LAYER 3: THE ORCHESTRATOR ---
    def calculate_network_z_scores(G, seed_id, iterations=50):
        """Main function to calculate Z-scores using a permutation null model."""
        print(f"🚀 Starting Z-score calculation for {seed_id}...")

        # 1. Get the 'Observed' scores from the real graph
        obs_scores_dict = run_conserving_rwr_V2(G, seed_id)
        nodes = list(G.nodes())

        # 2. Setup storage for null scores
        # A matrix where rows = nodes and columns = iterations
        null_matrix = np.zeros((len(nodes), iterations))

        # 3. The Permutation Loop
        for i in tqdm(range(iterations), desc="Randomizing & Running RWR"):
            # Create a shuffled version of the graph
            G_null = get_randomized_null_graph_safe(G)

            # Run RWR on the shuffled graph
            null_scores = run_conserving_rwr_V2(G_null, seed_id)

            # Store scores in our matrix
            for idx, node in enumerate(nodes):
                null_matrix[idx, i] = null_scores[node]

        # 4. Statistical Calculation (The Z-Scale)
        z_scores = {}
        for idx, node in enumerate(nodes):
            obs = obs_scores_dict[node]
            mu = np.mean(null_matrix[idx, :])
            sigma = np.std(null_matrix[idx, :])

            # Avoid division by zero for isolated nodes
            if sigma > 0:
                z_scores[node] = (obs - mu) / sigma
            else:
                z_scores[node] = 0.0

        print("✅ Z-score calculation complete.")
        return z_scores

    # ---- Layer 3 (alternative): Orchestrator that changes the target_seed so instead of 'Aripiprazole' to new seed. 
    def calculate_z_scores_via_random_seeds(G, target_seed_id, iterations=50):
        """
        Calculates Z-scores by comparing the target drug to 
        randomly selected seed nodes in the same graph.
        """
        nodes = list(G.nodes())
        node_to_idx = {node: i for i, node in enumerate(nodes)}

        # 1. Observed Scores (Aripiprazole)
        print(f"Calculating observed scores for {target_seed_id}...")
        obs_scores_dict = run_conserving_rwr(G, target_seed_id)

        # 2. Null Model (Random Seeds)
        # We pick random nodes from the graph to act as the 'fake' seeds
        all_nodes = list(G.nodes())
        null_matrix = np.zeros((len(nodes), iterations))

        for i in tqdm(range(iterations), desc="Running Null Model Seeds"):
            # Pick a random node that isn't our target seed
            random_seed = random.choice(all_nodes)

            # Run RWR from that random location
            null_scores = run_conserving_rwr(G, random_seed)

            for idx, node in enumerate(nodes):
                null_matrix[idx, i] = null_scores[node]

        # 3. Final Z-Score Calculation
        z_scores = {}
        for idx, node in enumerate(nodes):
            obs = obs_scores_dict[node]
            mu = np.mean(null_matrix[idx, :])
            sigma = np.std(null_matrix[idx, :])

            if sigma > 0:
                z_scores[node] = (obs - mu) / sigma
            else:
                # If the node always gets the same score (or 0), Z is 0
                z_scores[node] = 0.0

        return z_scores
    return calculate_z_scores_via_random_seeds, run_conserving_rwr_V2, tqdm


@app.cell
def _(calculate_z_scores_via_random_seeds, get_outward_subgraph, graph_V6):
    sub_graph_V2, arip_id_V2 = get_outward_subgraph(graph_V6, "drug:aripiprazole", hops=7)

    # print(f"Nodes: {sub_graph_V2.number_of_nodes()}")
    # print(f"Edges: {sub_graph_V2.number_of_edges()}")
    # # Density: 0 is empty, 1 is every node connected to every other node
    # print(f"Density: {nx.density(sub_graph_V2):.4f}")

    # 1. Run the Orchestrator
    # Use your neighborhood subgraph to keep it fast
    #final_z_results = calculate_network_z_scores(sub_graph_V2, arip_id_V2, iterations=20)
    final_z_results = calculate_z_scores_via_random_seeds(sub_graph_V2, arip_id_V2, iterations=100)

    # 2. Filter for the 'Gold' hits (Z-score > 3.0)
    top_hits = sorted(final_z_results.items(), key=lambda x: x[1], reverse=True)

    print("\n--- TOP SIGNIFICANT HITS (Z > 3) ---")
    for node_id_v2, z in top_hits:
        if z > 3: 
            # Extract node type for context if available
            n_type = sub_graph_V2.nodes[node_id_v2].get('node_type', 'Unknown')
            print(f"Z={z:.2f} | [{n_type}] {node_id_v2}")

    # 3. Update your graph for Marimo Visualization
    # for node_id_v2 in sub_graph.nodes():
    #     z = final_z_results.get(node_id_v2, 0)
    #     # Scale node size based on Z-score
    #     sub_graph.nodes[node_id_v2]['value'] = max(z * 5, 1) 
    #     sub_graph.nodes[node_id_v2]['title'] = f"Z-Score: {z:.2f}"

    #     # Color-code by significance
    #     if z > 3.0:
    #         sub_graph.nodes[node_id_v2]['color'] = '#FF4500' # Orange-Red for High Sig
    #     elif z > 1.96:
    #         sub_graph.nodes[node_id_v2]['color'] = '#FFD700' # Gold for Sig
    return arip_id_V2, sub_graph_V2


@app.cell
def _(arip_id_V2, nx, run_conserving_rwr, sub_graph, sub_graph_V2):
    rwr_scores_V2 = run_conserving_rwr(sub_graph_V2, arip_id_V2)

    # Check reachability
    reachable_nodes_V2 = nx.descendants(sub_graph_V2, arip_id_V2)
    print(f"Total nodes reachable from {arip_id_V2}: {len(reachable_nodes_V2)}")

    if len(reachable_nodes_V2) == 0:
        print("❌ Critical Error: No nodes are reachable from the seed. Check edge directions!")

    # Step 3: Sort nodes by score descending
    sorted_hits_V2 = sorted(rwr_scores_V2.items(), key=lambda x: x[1], reverse=True)

    # Step 4: Keep the top 50 nodes
    top_50_nodes_V2 = [node_id for node_id, score in sorted_hits_V2[:50]]

    # Step 5: Extract the final high-confidence subgraph
    final_g_V2 = sub_graph.subgraph(top_50_nodes_V2).copy()
    return (sorted_hits_V2,)


@app.cell
def _(node, sorted_hits_V2):
    for node_V2, score_V2 in sorted_hits_V2:
        if 'adverse:akathesia' in node:
            print(f"Node: {node_V2:<20} | Score: {score_V2:.10f}")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
