import marimo

__generated_with = "0.19.7"
app = marimo.App(width="medium")


@app.cell
def _():
    ## The virgin path of Brexiprazole/Rexulty
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
    from collections import Counter
    return Network, mo, nx


@app.cell
def _(Network, mo, nx):
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

    KG_COLOR_PALETTE = {
        'Drug': '#007bff',           # Blue
        'Protein': '#17a2b8',      # Cyan
        'MolecularFunction': '#28a745',   # Green
        'CellularComponent': '#e83e8c',      # Pink
        'BiologicalProcess': '#6f42c1',     # Purple
        'Pathway':'#a4ac86', # Olive Green
        'Circuit':'#dc3545', # Red
        'BrainRegion':'#20c997', #Teal
        'NeurotransmitterSystem':'#ffc107', # Amber
        'Neurotransmitter':'#ffb300', #Slight amber
        'RDoC_Domain':'#d5b8dc', #
        'RDoC_Construct':'#b69dd6',
        'Symptom':'#6c204d',
        # 'Target': '#adb5bd',   # Light Grey
        # 'Pathway': '#6610f2', # Indigo     
        # 'NDCPackage': '#fd7e14',     # Orange
        # 'Enzyme': '#a4ac86',         # Olive Green
        'unknown': '#6c757d'         # Dark Grey
    }

    def apply_kg_colors(G, palette=KG_COLOR_PALETTE):
        """
        Applies colors and sets specific node sizes based on node importance.
        """
        for node_id, data in G.nodes(data=True):
            # 1. Get type and convert to lowercase for matching
            raw_type = data.get('type', 'unknown')
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


    def add_edges_from_list(G, edges_list):
        """
        Input: List of dicts with keys: 'id', 'source', 'target', 'edge_type'
        Output: NetworkX DiGraph with relational attributes
        """
        processed_edges = []

        # These keys are reserved by NetworkX/Pyvis and will cause TypeErrors 
        # if passed inside the attribute dictionary.
        reserved_keys = {'source', 'target', 'to', 'from', 'self'}

        for edge_dict in edges_list:
            u = edge_dict['source']
            v = edge_dict['target']

            # Create a copy so we don't mutate the original data list
            attrs = edge_dict.copy()

            # 1. Sanitize keys: Rename anything in reserved_keys
            # We use list(attrs.keys()) to avoid 'dictionary changed size' error
            for key in list(attrs.keys()):
                if key.lower() in reserved_keys:
                    attrs[f"data_{key}"] = attrs.pop(key)

            # 2. Add Visualization standard keys
            rel = attrs.get('relation', 'interacts')
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

    def visualize_interactive_graph(G, filename="drug_graph.html"):
        # 1. Define the order of types
        # Replace these with your actual node types in the order you want (left to right)
        type_order = {'Drug': 0, 'Protein': 1, 'MolecularFunction': 2, 
                      'CellularComponent':3, 'Pathway':4, 'BiologicalProcess':5,
                      'Neurotransmitter':6,'NeurotransmitterSystem': 7, 
                      'BrainRegion': 8, 'Circuit':9, 'RDoC_Domain': 10, 
                      'RDoC_Construct':11, 'Symptom':12
                     }

        for node_id, data in G.nodes(data=True):
            # Assign the 'subset' for the layout logic
            node_type = data.get('type', 'Unknown')
            node_label = data.get('label','Unknown')
            G.nodes[node_id]['subset'] = type_order.get(node_type, 3) 

            # Standard Pyvis formatting
            G.nodes[node_id]['label'] = str(node_id)
            G.nodes[node_id]['title'] = f"ID: {node_label}\nType: {node_type}"

        # 2. Calculate positions using NetworkX
        # This creates a dict of {node: [x, y]}
        pos = nx.multipartite_layout(G, subset_key="subset")

        # 3. Initialize Pyvis
        net = Network(height="700px", width="100%", notebook=False, directed=True, cdn_resources='remote')

        # 4. Load the graph
        net.from_nx(G)

        # 5. Apply the calculated positions to Pyvis nodes
        for node in net.nodes:
            node_id = node['id']
            if node_id in pos:
                # Scale up the positions (NetworkX uses small floats like 0.1, 1.0)
                node['x'] = pos[node_id][0] * 1000
                node['y'] = pos[node_id][1] * 1000

        # 6. CRITICAL: Disable physics so nodes stay in their columns
        net.toggle_physics(False)

        html_string = net.generate_html()
        return mo.Html(
            f'<iframe srcdoc="{html_string.replace('"', '&quot;')}" '
            f'width="100%" height="750px" style="border:none;"></iframe>'
        )


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


    def find_all_paths_to_type_ids(G, source_name, target_type):
        """
        Finds all unique directed paths from a source to any node of target_type.
        Returns a list of paths, where each path is a list of node IDs.
        """
        # Find Source ID
        s_id = None
        for n, d in G.nodes(data=True):
            if source_name.lower() in [str(n).lower(), str(d.get('label', '')).lower()]:
                s_id = n
                break

        if s_id is None:
            print(f"❌ Source '{source_name}' not found.")
            return []

        # Find Target IDs by type
        target_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == target_type]

        all_paths = []
        for t_id in target_nodes:
            try:
                paths = list(nx.all_simple_paths(G, source=s_id, target=t_id))
                all_paths.extend(paths)
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                continue

        return all_paths


    def map_path_ids_to_labels(nodes_list, paths):
        """
        Translates a list of paths (IDs) into a list of paths (formatted labels).
        Output format: "[Type] Label"
        """
        # 1. Create a fast lookup: {id: "[Type] Label"}
        id_to_formatted_label = {}
        for node in nodes_list:
            if 'id' in node:
                n_type = node.get('type', 'Unknown')
                n_label = node.get('label') or node.get('node_name') or node['id']
                # Create the combined string
                id_to_formatted_label[node['id']] = f"[{n_type}] {n_label}"

        labeled_results = []

        # 2. Process each path
        for path in paths:
            if not isinstance(path, (list, tuple)):
                continue

            translated_path = []
            for node_id in path:
                # Look up formatted label, fallback to node_id if not found
                formatted = id_to_formatted_label.get(str(node_id), str(node_id))
                translated_path.append(formatted)

            labeled_results.append(translated_path)

        return labeled_results
    return (
        KG_COLOR_PALETTE,
        add_edges_from_list,
        apply_kg_colors,
        build_graph_from_node_list,
        find_all_paths_to_type_ids,
        map_path_ids_to_labels,
        visualize_interactive_graph,
    )


@app.cell
def _():

    nodes = [
        {"id": "drug:aripiprazole", "label": "abilify (aripiprazole)", "type": "Drug", "synonyms": ["Abilify", "aripiprazole"]},
        {"id": "protein:DRD2", "label": "Dopamine D2 receptor (DRD2)", "type": "Protein"},
        {"id": "protein:DRD3", "label": "Dopamine D3 receptor (DRD3)", "type": "Protein"},
        {"id": "protein:HTR1A", "label": "5-HT1A receptor (HTR1A)", "type": "Protein"},
        {"id": "protein:HTR2A", "label": "5-HT2A receptor (HTR2A)", "type": "Protein"},
        {"id": "protein:HTR2B", "label": "5-HT2B receptor (HTR2B)", "type": "Protein"},
        {"id": "protein:HTR7", "label": "5-HT7 receptor (HTR7)", "type": "Protein"},
        {"id": "protein:ADRA1A", "label": "Alpha-1A adrenergic receptor (ADRA1A)", "type": "Protein"},
        {"id": "protein:HRH1", "label": "Histamine H1 receptor (HRH1)", "type": "Protein"}

    ]

    ## Cellular Component Nodes
    molecular_function = [
        {"id": "go:0004930", "label": "G protein-coupled receptor activity", "type": "MolecularFunction"},
        {"id": "go:0001591", "label": "Dopamine neurotransmitter receptor activity, coupled via Gi/Go", "type": "MolecularFunction"},
        {"id": "go:0035240", "label": "Dopamine binding", "type": "MolecularFunction"},
        {"id": "go:0004993", "label": "Serotonin receptor activity", "type": "MolecularFunction"},
        {"id": "go:0031663", "label": "G protein-coupled serotonin receptor activity", "type": "MolecularFunction"},
        {"id": "go:0001592", "label": "Serotonin neurotransmitter receptor activity, coupled via Gi/Go", "type": "MolecularFunction"},
        {"id": "go:0001590", "label": "Serotonin neurotransmitter receptor activity, coupled via Gq/G11", "type": "MolecularFunction"},
        {"id": "go:0048018", "label": "Receptor tyrosine kinase binding", "type": "MolecularFunction"},
        {"id": "go:0005515", "label": "Protein binding", "type": "MolecularFunction"},
        {"id": "go:0032795", "label": "Heterotrimeric G-protein binding", "type": "MolecularFunction"},
        {"id": "go:0042802", "label": "Identical protein binding (Dimerization)", "type": "MolecularFunction"}, 
        {"id": "go:0001593", "label": "Serotonin neurotransmitter receptor activity, coupled via Gs", "type": "MolecularFunction"},
        {"id": "go:0004935", "label": "Alpha-1 adrenergic receptor activity", "type": "MolecularFunction"},
        {"id": "go:0001580", "label": "Epinephrine binding", "type": "MolecularFunction"},
        {"id": "go:0051379", "label": "Norepinephrine binding", "type": "MolecularFunction"}, 
        {"id": "go:0004970", "label": "Histamine H1 receptor activity", "type": "MolecularFunction"},
        {"id": "go:0001590", "label": "G protein-coupled receptor activity, coupled via Gq", "type": "MolecularFunction"}
    ]


    # # Cellular Component nodes
    cc_nodes = [
        {"id": "go:0005886", "label": "Plasma membrane", "type": "CellularComponent"},
        {"id": "go:0045211", "label": "Postsynaptic membrane", "type": "CellularComponent"},
        {"id": "go:0042734", "label": "Presynaptic membrane", "type": "CellularComponent"},
        {"id": "go:0005794", "label": "Golgi apparatus", "type": "CellularComponent"},
        {"id": "go:0014069", "label": "Postsynaptic density", "type": "CellularComponent"},
        {"id": "go:0005813", "label": "Endosome", "type": "CellularComponent"},
        {"id": "go:0005829", "label": "Cytosol", "type": "CellularComponent"}, 
        {"id": "go:0044306", "label": "Neuron projection terminus", "type": "CellularComponent"},
        {"id": "go:0036477", "label": "Somatodendritic compartment", "type": "CellularComponent"},
        {"id": "go:0043197", "label": "Dendritic spine", "type": "CellularComponent"},
        {"id": "go:0098978", "label": "Glutamatergic synapse", "type": "CellularComponent"}, 
        {"id": "go:0005901", "label": "Caveola", "type": "CellularComponent"},
        {"id": "go:0016528", "label": "Sarcoplasmic reticulum", "type": "CellularComponent"},
        {"id": "go:0045121", "label": "Extracellular matrix", "type": "CellularComponent"},
        {"id": "go:0044309", "label": "Neuron-to-neuron synapse", "type": "CellularComponent"},
        {"id": "go:0031253", "label": "Cell projection membrane", "type": "CellularComponent"}, 
        {"id": "go:0043005", "label": "Neuron projection", "type": "CellularComponent"},
        {"id": "go:0098984", "label": "Dendritic membrane", "type": "CellularComponent"},
        {"id": "go:0005737", "label": "Cytoplasm (Calcium signaling pool)", "type": "CellularComponent"}   
    ]

    ## Pathway nodes
    pathway = [
        {"id": "pathway:hsa04728", "label": "Dopaminergic synapse", "type": "Pathway"},
        {"id": "pathway:hsa04024", "label": "cAMP signaling pathway", "type": "Pathway"},
        {"id": "pathway:hsa04010", "label": "MAPK signaling pathway", "type": "Pathway"},
        {"id": "pathway:hsa04725", "label": "Serotonergic synapse", "type": "Pathway"},
        {"id": "pathway:hsa04933", "label": "AGE-RAGE signaling pathway in diabetic complications", "type": "Pathway"},
        {"id": "pathway:hsa05030", "label": "Cocaine addiction", "type": "Pathway"}, 
        {"id": "pathway:hsa04726", "label": "Serotonergic synapse", "type": "Pathway"},
        {"id": "pathway:hsa04080", "label": "Neuroactive ligand-receptor interaction", "type": "Pathway"}, 
        {"id": "pathway:hsa04020", "label": "Calcium signaling pathway", "type": "Pathway"},    
        {"id": "pathway:hsa04071", "label": "Phospholipase D signaling pathway", "type": "Pathway"},
        {"id": "pathway:hsa04724", "label": "Glutamatergic synapse", "type": "Pathway"}, 
        {"id": "pathway:hsa04270", "label": "Vascular smooth muscle contraction", "type": "Pathway"},
        {"id": "pathway:hsa04022", "label": "cGMP-PKG signaling pathway", "type": "Pathway"}, 
        {"id": "pathway:hsa04710", "label": "Circadian rhythm", "type": "Pathway"},
        {"id": "pathway:hsa04724", "label": "Glutamatergic synapse signaling", "type": "Pathway"}, 
        {"id": "pathway:hsa04261", "label": "Adrenergic signaling in cardiomyocytes", "type": "Pathway"},
        {"id": "pathway:hsa04726", "label": "Serotonergic synapse (Regulatory overlap)", "type": "Pathway"}, 
        {"id": "pathway:hsa04920", "label": "Adipocytokine signaling pathway", "type": "Pathway"},
        {"id": "pathway:hsa04152", "label": "AMPK signaling pathway", "type": "Pathway"},
        {"id": "pathway:hsa04977", "label": "Vitamin digestion and absorption (Metabolic integration)", "type": "Pathway"}   
    ]

    ##Bioloigcal Process
    biological_process = [
        {"id": "bp:0007212", "label": "Dopamine receptor signaling pathway (BP)", "type": "BiologicalProcess"},
        {"id": "bp:0007268", "label": "Chemical synaptic transmission (BP)", "type": "BiologicalProcess"},
        {"id": "bp:0045892", "label": "Negative regulation of adenylate cyclase activity (BP)", "type": "BiologicalProcess"},
        {"id": "bp:0051580", "label": "Regulation of dopamine secretion (BP)", "type": "BiologicalProcess"},
        {"id": "bp:0007626", "label": "Locomotory behavior (BP)", "type": "BiologicalProcess"},
        {"id": "bp:0002027", "label": "Regulation of hormone secretion (BP)", "type": "BiologicalProcess"},
        {"id": "bp:0007186", "label": "G protein-coupled receptor signaling pathway (BP)", "type": "BiologicalProcess"},
        {"id": "bp:0008277", "label": "Regulation of G protein-coupled receptor signaling (BP)", "type": "BiologicalProcess"}, 
        {"id": "bp:0045006", "label": "Maintenance of dopamine gastrointestinal homeostasis", "type": "BiologicalProcess"},
        {"id": "bp:0060007", "label": "Drug-seeking behavior", "type": "BiologicalProcess"},
        {"id": "bp:0048265", "label": "Response to morphine", "type": "BiologicalProcess"},
        {"id": "bp:0007628", "label": "Adult walking behavior", "type": "BiologicalProcess"},
        {"id": "bp:0035094", "label": "Positive regulation of dopamine uptake", "type": "BiologicalProcess"}, 
        {"id": "bp:0045648", "label": "Positive regulation of erythrocyte differentiation", "type": "BiologicalProcess"},
        {"id": "bp:0031100", "label": "Animal organ regeneration", "type": "BiologicalProcess"},
        {"id": "bp:0007631", "label": "Feeding behavior", "type": "BiologicalProcess"}, 
        {"id": "bp:0007611", "label": "Learning or memory", "type": "BiologicalProcess"},
        {"id": "bp:0031645", "label": "Negative regulation of neurological system process", "type": "BiologicalProcess"},
        {"id": "bp:0001659", "label": "Temperature homeostasis", "type": "BiologicalProcess"},
        {"id": "bp:0008217", "label": "Regulation of blood pressure", "type": "BiologicalProcess"},
        {"id": "bp:0051482", "label": "Negative regulation of cytosolic calcium ion concentration", "type": "BiologicalProcess"},
        {"id": "bp:0007600", "label": "Sensory perception", "type": "BiologicalProcess"},
        {"id": "bp:0045747", "label": "Positive regulation of Notch signaling pathway", "type": "BiologicalProcess"},
        {"id": "bp:0050854", "label": "Regulation of synaptogenesis", "type": "BiologicalProcess"},
        {"id": "bp:0014057", "label": "Regulation of NMDA receptor activity", "type": "BiologicalProcess"},
        {"id": "bp:0007605", "label": "Sensory perception of sound", "type": "BiologicalProcess"}, 
        {"id": "bp:0045907", "label": "Positive regulation of vasoconstriction", "type": "BiologicalProcess"},
        {"id": "bp:0042127", "label": "Regulation of cell proliferation", "type": "BiologicalProcess"},
        {"id": "bp:0014031", "label": "Mesenchymal cell proliferation", "type": "BiologicalProcess"},
        {"id": "bp:0003013", "label": "Circulatory system process", "type": "BiologicalProcess"}, 
        {"id": "bp:0007623", "label": "Circadian sleep/wake cycle", "type": "BiologicalProcess"},
        {"id": "bp:0043518", "label": "Negative regulation of DNA-templated transcription, rhythmic", "type": "BiologicalProcess"},
        {"id": "bp:0050848", "label": "Regulation of synaptic plasticity", "type": "BiologicalProcess"},
        {"id": "bp:0007610", "label": "Behavior", "type": "BiologicalProcess"}, 
        {"id": "bp:0031644", "label": "Regulation of neurological system process", "type": "BiologicalProcess"},
        {"id": "bp:0050890", "label": "Cognition", "type": "BiologicalProcess"}, 
        {"id": "bp:0010893", "label": "Positive regulation of appetite", "type": "BiologicalProcess"},
        {"id": "bp:0006006", "label": "Glucose metabolic process", "type": "BiologicalProcess"},
        {"id": "bp:0042730", "label": "Analysis of external stimulus", "type": "BiologicalProcess"},
        {"id": "bp:0007622", "label": "Cessation of feeding", "type": "BiologicalProcess"}   
    ]

    circuit = [
        {"id": "circuit:mesolimbic_pathway", "label": "Mesolimbic Pathway", "type": "Circuit"},
        {"id": "circuit:mesocortical_pathway", "label": "Mesocortical Pathway", "type": "Circuit"},
        {"id": "circuit:nigrostriatal_pathway", "label": "Nigrostriatal Pathway", "type": "Circuit"},
        {"id": "circuit:tuberoinfundibular_pathway", "label": "Tuberoinfundibular Pathway", "type": "Circuit"},
        {"id": "circuit:cortico_striatal_loop", "label": "Cortico-Striatal Loop", "type": "Circuit"},
        {"id": "circuit:amygdala_pfc_circuit", "label": "Amygdala-PFC Circuit", "type": "Circuit"},
        {"id": "circuit:hippocampal_circuit", "label": "Hippocampal Circuit", "type": "Circuit"}, 
        {"id": "circuit:habenula_circuit", "label": "Lateral Habenula Circuit", "type": "Circuit"},
        {"id": "circuit:thalamocortical_relay", "label": "Thalamocortical Relay", "type": "Circuit"},
        {"id": "circuit:hypothalamic_pituitary_axis", "label": "Hypothalamic-Pituitary Axis", "type": "Circuit"},
        {"id": "circuit:enteric_nervous_system", "label": "Enteric Nervous System (ENS)", "type": "Circuit"},
        {"id": "circuit:vascular_network", "label": "Peripheral Vascular Network", "type": "Circuit"},
        {"id": "circuit:cardiac_valvular_circuit", "label": "Cardiac Valvular Tissue Circuit", "type": "Circuit"}, 
        {"id": "circuit:suprachiasmatic_nucleus", "label": "Suprachiasmatic Nucleus (SCN)", "type": "Circuit"},
        {"id": "circuit:thalamocortical_relay", "label": "Thalamocortical Relay Circuit", "type": "Circuit"}, 
        {"id": "circuit:locus_coeruleus_projection", "label": "Locus Coeruleus-Noradrenergic Projection", "type": "Circuit"},
        {"id": "circuit:baroreceptor_reflex_arc", "label": "Baroreceptor Reflex Arc", "type": "Circuit"},
        {"id": "circuit:reticular_activating_system", "label": "Reticular Activating System (RAS)", "type": "Circuit"}, 
        {"id": "circuit:tuberomammillary_nucleus", "label": "Tuberomammillary Nucleus (TMN)", "type": "Circuit"},
        {"id": "circuit:ventromedial_hypothalamus", "label": "Ventromedial Hypothalamus (VMH)", "type": "Circuit"},
        {"id": "circuit:lateral_hypothalamus", "label": "Lateral Hypothalamus (LH)", "type": "Circuit"}   
    ]


    Rdoc_construct = [
        {"id": "rdoc:acute_threat", "label": "Acute Threat (Fear)", "type": "RDocConstruct"},
        {"id": "rdoc:potential_threat", "label": "Potential Threat (Anxiety)", "type": "RDocConstruct"},
        {"id": "rdoc:sustained_threat", "label": "Sustained Threat", "type": "RDocConstruct"},
        {"id": "rdoc:frustrative_nonreward", "label": "Frustrative Nonreward", "type": "RDocConstruct"},
        {"id": "rdoc:loss", "label": "Loss", "type": "RDocConstruct"}, 
        {"id": "rdoc:reward_responsiveness", "label": "Reward Responsiveness", "type": "RDocConstruct"},
        {"id": "rdoc:reward_learning", "label": "Reward Learning", "type": "RDocConstruct"},
        {"id": "rdoc:reward_valuation", "label": "Reward Valuation", "type": "RDocConstruct"}, 
        {"id": "rdoc:attention", "label": "Attention", "type": "RDocConstruct"},
        {"id": "rdoc:perception", "label": "Perception", "type": "RDocConstruct"},
        {"id": "rdoc:working_memory", "label": "Working Memory", "type": "RDocConstruct"},
        {"id": "rdoc:declarative_memory", "label": "Declarative Memory", "type": "RDocConstruct"},
        {"id": "rdoc:cognitive_control", "label": "Cognitive Control", "type": "RDocConstruct"}, 
        {"id": "rdoc:affiliation_attachment", "label": "Affiliation and Attachment", "type": "RDocConstruct"},
        {"id": "rdoc:social_communication", "label": "Social Communication", "type": "RDocConstruct"},
        {"id": "rdoc:perception_self", "label": "Perception of Self", "type": "RDocConstruct"},
        {"id": "rdoc:perception_others", "label": "Perception of Others", "type": "RDocConstruct"}, 
        {"id": "rdoc:arousal", "label": "Arousal", "type": "RDocConstruct"},
        {"id": "rdoc:circadian_rhythms", "label": "Circadian Rhythms", "type": "RDocConstruct"},
        {"id": "rdoc:sleep_wake", "label": "Sleep and Wakefulness", "type": "RDocConstruct"}, 
        {"id": "rdoc:motor_actions", "label": "Motor Actions", "type": "RDocConstruct"},
        {"id": "rdoc:agency_ownership", "label": "Agency and Ownership", "type": "RDocConstruct"},
        {"id": "rdoc:habit", "label": "Habit", "type": "RDocConstruct"},
        {"id": "rdoc:innate_motor", "label": "Innate Motor Programs", "type": "RDocConstruct"}, 
        {"id": "rdoc:perception", "label": "Perception (Auditory/Visual)", "type": "RDocConstruct"},
        {"id": "rdoc:sensorimotor_behavior", "label": "Sensorimotor Behavior", "type": "RDocConstruct"}, 
        {"id": "rdoc:visceral_perception", "label": "Visceral Perception (Interoception)", "type": "RDocConstruct"},
        {"id": "rdoc:homeostatic_regulation", "label": "Homeostatic Regulation", "type": "RDocConstruct"},
        {"id": "rdoc:autonomic_arousal", "label": "Autonomic Arousal", "type": "RDocConstruct"}, 
        {"id": "rdoc:sleep_wake", "label": "Sleep-Wakefulness", "type": "RDocConstruct"}, 
        {"id": "rdoc:sleep_wakefulness", "label": "Sleep-Wakefulness", "type": "RDocConstruct"}, 
        {"id": "rdoc:energy_homeostasis", "label": "Energy Homeostasis", "type": "RDocConstruct"}    
    ]

    symptom = [
            {"id": "symp:anhedonia", "label": "Anhedonia (Loss of pleasure)", "type": "Symptom"},
            {"id": "symp:avolition", "label": "Avolition (Lack of motivation)", "type": "Symptom"},
            {"id": "symp:apathy", "label": "Apathy", "type": "Symptom"},
            {"id": "symp:asociality", "label": "Asociality (Social withdrawal)", "type": "Symptom"}, 
            {"id": "symp:hallucinations", "label": "Auditory/Visual Hallucinations", "type": "Symptom"},
            {"id": "symp:delusions", "label": "Delusions", "type": "Symptom"},
            {"id": "symp:thought_disorder", "label": "Disorganized Thinking", "type": "Symptom"},
            {"id": "symp:distractibility", "label": "Inattention/Distractibility", "type": "Symptom"},
            {"id": "symp:impulsivity", "label": "Impulsive Behavior", "type": "Symptom"}, 
            {"id": "symp:anxiety", "label": "Generalized Anxiety", "type": "Symptom"},
            {"id": "symp:agitation", "label": "Psychomotor Agitation", "type": "Symptom"},
            {"id": "symp:paranoia", "label": "Paranoia", "type": "Symptom"},
            {"id": "symp:irritability", "label": "Irritability", "type": "Symptom"}, 
            {"id": "symp:tremor", "label": "Resting Tremor (Parkinsonian)", "type": "Symptom"},
            {"id": "symp:rigidity", "label": "Muscle Rigidity", "type": "Symptom"},
            {"id": "symp:akathisia", "label": "Akathisia (Inner restlessness)", "type": "Symptom"},
            {"id": "symp:dystonia", "label": "Acute Dystonia (Muscle spasms)", "type": "Symptom"},
            {"id": "symp:tardive_dyskinesia", "label": "Tardive Dyskinesia", "type": "Symptom"}, 
            {"id": "symp:insomnia", "label": "Insomnia", "type": "Symptom"},
            {"id": "symp:somnolence", "label": "Sedation/Somnolence", "type": "Symptom"},
            {"id": "symp:hyperprolactinemia", "label": "Galactorrhea/Hormonal Dysfunction", "type": "Symptom"}, 
            {"id": "symp:impulse_control_disorder", "label": "Impulse Control Disorder (e.g., Gambling, Binge Eating)", "type":"Symptom"},
            {"id": "symp:compulsive_behavior", "label": "Compulsive Behavior", "type": "Symptom"},
            {"id": "symp:cognitive_blunting", "label": "Cognitive Blunting", "type": "Symptom"},
            {"id": "symp:weight_gain", "label": "Weight Gain / Increased Appetite", "type": "Symptom"},
            {"id": "symp:nausea", "label": "Gastrointestinal Nausea", "type": "Symptom"}, 
            {"id": "symp:social_anxiety", "label": "Social Anxiety / Avoidance", "type": "Symptom"},
            {"id": "symp:generalized_anxiety", "label": "Generalized Anxiety / Worry", "type": "Symptom"},
            {"id": "symp:cognitive_impairment", "label": "Cognitive Impairment / Brain Fog", "type": "Symptom"},
            {"id": "symp:depressive_mood", "label": "Depressive Mood / Sadness", "type": "Symptom"}, 
            {"id": "symp:hallucinations", "label": "Hallucinations (Auditory/Visual)", "type": "Symptom"},
            {"id": "symp:eps_prevention", "label": "Reduced Extrapyramidal Symptoms (EPS)", "type": "Symptom"},
            {"id": "symp:sleep_continuity", "label": "Improved Sleep Continuity", "type": "Symptom"},
            {"id": "symp:aggression", "label": "Irritability and Aggression", "type": "Symptom"}, 
            {"id": "symp:gi_distress", "label": "Gastrointestinal Distress (Nausea/Cramping)", "type": "Symptom"},
            {"id": "symp:valvular_fibrosis_risk", "label": "Risk of Cardiac Valvulopathy", "type": "Symptom"},
            {"id": "symp:orthostatic_instability", "label": "Orthostatic Blood Pressure Changes", "type": "Symptom"},
            {"id": "symp:somatic_anxiety", "label": "Somatic Manifestations of Anxiety", "type": "Symptom"}, 
            {"id": "symp:circadian_dysregulation", "label": "Diurnal Mood Variation", "type": "Symptom"},
            {"id": "symp:insomnia", "label": "Insomnia / Sleep Fragmentation", "type": "Symptom"},
            {"id": "symp:cognitive_fog", "label": "Cognitive 'Fog' and Sensory Overload", "type": "Symptom"},
            {"id": "symp:depressive_rumination", "label": "Depressive Rumination", "type": "Symptom"}, 
            {"id": "symp:orthostatic_hypotension", "label": "Orthostatic Hypotension (Dizziness upon standing)", "type": "Symptom"},
            {"id": "symp:sedation", "label": "Sedation / Somnolence", "type": "Symptom"},
            {"id": "symp:nasal_congestion", "label": "Nasal Congestion", "type": "Symptom"},
            {"id": "symp:tachycardia_reflex", "label": "Reflex Tachycardia", "type": "Symptom"}, 
            {"id": "symp:weight_gain", "label": "Weight Gain / Increased BMI", "type": "Symptom"},
            {"id": "symp:hyperphagia", "label": "Hyperphagia (Increased Appetite)", "type": "Symptom"},
            {"id": "symp:metabolic_syndrome_risk", "label": "Risk of Metabolic Syndrome", "type": "Symptom"},
            {"id": "symp:somnolence", "label": "Somnolence (Daytime Sleepiness)", "type": "Symptom"}   
    ]


    #####################################################################################################################
    #########################################     EDGES      ############################################################
    #####################################################################################################################


    edges = [
        {"source": "drug:aripiprazole", "target": "protein:DRD2", "relation": "partial_agonist_of"},
        {"source": "drug:aripiprazole", "target": "protein:DRD3", "relation": "partial_agonist_of"},
        {"source": "drug:aripiprazole", "target": "protein:HTR1A", "relation": "partial_agonist_of"},
        {"source": "drug:aripiprazole", "target": "protein:HTR2A", "relation": "antagonist_of"},
        {"source": "drug:aripiprazole", "target": "protein:HTR2B", "relation": "inverse_agonist_of"},
        {"source": "drug:aripiprazole", "target": "protein:HTR7", "relation": "antagonist_of"},
        {"source": "drug:aripiprazole", "target": "protein:ADRA1A", "relation": "antagonist_of"},
        {"source": "drug:aripiprazole", "target": "protein:HRH1", "relation": "antagonist_of"}
    ]


    ## Protien to Molecular Function edges
    protien_to_mf_edges = [
        {"source": "protein:DRD2", "target": "go:0004930", "relation": "enables"},
        {"source": "protein:DRD2", "target": "go:0001591", "relation": "enables"},
        {"source": "protein:DRD2", "target": "go:0005515", "relation": "enables"},
        {"source": "protein:DRD2", "target": "go:0032795", "relation": "enables"},
        {"source": "protein:DRD2", "target": "go:0035240", "relation": "enables"},
        {"source": "protein:DRD2", "target": "go:0042802", "relation": "enables"},
    
        {"source": "protein:DRD3", "target": "go:0004930", "relation": "enables"},
        {"source": "protein:DRD3", "target": "go:0001591", "relation": "enables"},
        {"source": "protein:DRD3", "target": "go:0005515", "relation": "enables"},
        {"source": "protein:DRD3", "target": "go:0032795", "relation": "enables"},
        {"source": "protein:DRD3", "target": "go:0035240", "relation": "enables"},

        {"source": "protein:HTR1A", "target": "go:0004993", "relation": "enables"},
        {"source": "protein:HTR1A", "target": "go:0001592", "relation": "enables"},
        {"source": "protein:HTR1A", "target": "go:0005515", "relation": "enables"},
        {"source": "protein:HTR1A", "target": "go:0032795", "relation": "enables"},
        {"source": "protein:HTR1A", "target": "go:0042802", "relation": "enables"},
        {"source": "protein:HTR1A", "target": "go:0031663", "relation": "enables"},

        {"source": "protein:HTR2A", "target": "go:0004993", "relation": "enables"}, 
        {"source": "protein:HTR2A", "target": "go:0031663", "relation": "enables"},
        {"source": "protein:HTR2A", "target": "go:0001590", "relation": "enables"},
        {"source": "protein:HTR2A", "target": "go:0005515", "relation": "enables"},
        {"source": "protein:HTR2A", "target": "go:0042802", "relation": "enables"},
        {"source": "protein:HTR2A", "target": "go:0032795", "relation": "enables"},

        {"source": "protein:HTR2B", "target": "go:0004993", "relation": "enables"},
        {"source": "protein:HTR2B", "target": "go:0031663", "relation": "enables"},
        {"source": "protein:HTR2B", "target": "go:0001590", "relation": "enables"},
        {"source": "protein:HTR2B", "target": "go:0048018", "relation": "enables"},
        {"source": "protein:HTR2B", "target": "go:0004930", "relation": "enables"},
        {"source": "protein:HTR2B", "target": "go:0005515", "relation": "enables"},
        {"source": "protein:HTR2B", "target": "go:0032795", "relation": "enables"}, 

        {"source": "protein:HTR7", "target": "go:0004993", "relation": "enables"},
        {"source": "protein:HTR7", "target": "go:0031663", "relation": "enables"},
        {"source": "protein:HTR7", "target": "go:0001593", "relation": "enables"},
        {"source": "protein:HTR7", "target": "go:0004930", "relation": "enables"},
        {"source": "protein:HTR7", "target": "go:0005515", "relation": "enables"},
        {"source": "protein:HTR7", "target": "go:0032795", "relation": "enables"}, 

        {"source": "protein:ADRA1A", "target": "go:0004935", "relation": "enables"},    
        {"source": "protein:ADRA1A", "target": "go:0001580", "relation": "enables"},
        {"source": "protein:ADRA1A", "target": "go:0051379", "relation": "enables"},
        {"source": "protein:ADRA1A", "target": "go:0004930", "relation": "enables"},
        {"source": "protein:ADRA1A", "target": "go:0032795", "relation": "enables"},
        {"source": "protein:ADRA1A", "target": "go:0005515", "relation": "enables"}, 

        {"source": "protein:HRH1", "target": "go:0004970", "relation": "enables"},
        {"source": "protein:HRH1", "target": "go:0001590", "relation": "enables"},
        {"source": "protein:HRH1", "target": "go:0032795", "relation": "enables"},
        {"source": "protein:HRH1", "target": "go:0004930", "relation": "enables"},
        {"source": "protein:HRH1", "target": "go:0005515", "relation": "enables"}   
    ]

    ## Protein to Cellular Component edges
    mf_to_cc_edges = [
        {"source": "go:0004930", "target": "go:0005886", "relation": "occurs_at"},
        {"source": "go:0031663", "target": "go:0005886", "relation": "occurs_at"},
        {"source": "go:0001590", "target": "go:0005886", "relation": "occurs_at"},
        {"source": "go:0005515", "target": "go:0005829", "relation": "occurs_at"},

        {"source": "go:0001591", "target": "go:0045211", "relation": "occurs_at"},
        {"source": "go:0001591", "target": "go:0042734", "relation": "occurs_at"},
        {"source": "go:0035240", "target": "go:0045211", "relation": "occurs_at"},
        {"source": "go:0035240", "target": "go:0042734", "relation": "occurs_at"},
        {"source": "go:0035240", "target": "go:0014069", "relation": "occurs_at"},

        {"source": "go:0001592", "target": "go:0005886", "relation": "occurs_at"},
        {"source": "go:0004993", "target": "go:0036477", "relation": "occurs_at"}, 
        {"source": "go:0031663", "target": "go:0045211", "relation": "occurs_at"},
        {"source": "go:0031663", "target": "go:0042734", "relation": "occurs_at"},
        {"source": "go:0001592", "target": "go:0014069", "relation": "occurs_at"},

        {"source": "go:0001590", "target": "go:0043197", "relation": "occurs_at"}, 
        {"source": "go:0001590", "target": "go:0014069", "relation": "occurs_at"}, 
        {"source": "go:0004993", "target": "go:0098978", "relation": "occurs_at"}, 

        {"source": "go:0001590", "target": "go:0005901", "relation": "occurs_at"}, 
        {"source": "go:0032795", "target": "go:0016528", "relation": "modulates_calcium_at"}, 
        {"source": "go:0048018", "target": "go:0045121", "relation": "influences_structure_via"}, 

        {"source": "go:0032795", "target": "go:0014069", "relation": "occurs_at"},
        {"source": "go:0032795", "target": "go:0005886", "relation": "occurs_at"},
        {"source": "go:0032795", "target": "go:0036477", "relation": "occurs_at"},
        {"source": "go:0005515", "target": "go:0014069", "relation": "occurs_at"}, 

        {"source": "go:0004930", "target": "go:0005886", "relation": "occurs_at"},
        {"source": "go:0031663", "target": "go:0005886", "relation": "occurs_at"},
        {"source": "go:0001590", "target": "go:0005901", "relation": "localizes_to"}, 

        {"source": "go:0001593", "target": "go:0005886", "relation": "occurs_at"},
        {"source": "go:0001593", "target": "go:0045211", "relation": "localizes_to"}, 

        {"source": "go:0004935", "target": "go:0005886", "relation": "occurs_at"},
        {"source": "go:0004935", "target": "go:0044309", "relation": "localizes_to"},
        {"source": "go:0051379", "target": "go:0044309", "relation": "occurs_at"},
        {"source": "go:0032795", "target": "go:0016528", "relation": "modulates_activity_at"}, 

        {"source": "go:0004970", "target": "go:0005886", "relation": "occurs_at"},
        {"source": "go:0004970", "target": "go:0098984", "relation": "localizes_to"},
        {"source": "go:0001590", "target": "go:0005737", "relation": "results_in_flux_at"},
        {"source": "go:0004970", "target": "go:0043005", "relation": "operates_on"}    
    ]

    ##cc to pathway
    cc_to_pathway = [
        {"source": "go:0045211", "target": "pathway:hsa04728", "relation": "enables_pathway"},
        {"source": "go:0042734", "target": "pathway:hsa04728", "relation": "enables_pathway"},
        {"source": "go:0014069", "target": "pathway:hsa04024", "relation": "localizes_pathway"},
        {"source": "go:0014069", "target": "pathway:hsa04010", "relation": "localizes_pathway"},
        {"source": "go:0005886", "target": "pathway:hsa04024", "relation": "enables_pathway"},
        {"source": "go:0005886", "target": "pathway:hsa04728", "relation": "enables_pathway"},
        {"source": "go:0005794", "target": "pathway:hsa04728", "relation": "prepares_components_for"},
        {"source": "go:0045211", "target": "pathway:hsa04725", "relation": "enables_pathway"}, 
        {"source": "go:0005886", "target": "pathway:hsa05030", "relation": "enables_pathway"}, 
        {"source": "go:0036477", "target": "pathway:hsa04726", "relation": "enables_pathway"},
        {"source": "go:0045211", "target": "pathway:hsa04726", "relation": "enables_pathway"},
        {"source": "go:0005886", "target": "pathway:hsa04080", "relation": "enables_pathway"},
        {"source": "go:0042734", "target": "pathway:hsa04726", "relation": "enables_pathway"}, 
        {"source": "go:0043197", "target": "pathway:hsa04020", "relation": "enables_pathway"},
        {"source": "go:0043197", "target": "pathway:hsa04724", "relation": "modulates_pathway"},
        {"source": "go:0014069", "target": "pathway:hsa04071", "relation": "localizes_pathway"},
        {"source": "go:0005886", "target": "pathway:hsa04726", "relation": "enables_pathway"}, 
        {"source": "go:0005886", "target": "pathway:hsa04270", "relation": "initiates_pathway"},
        {"source": "go:0005901", "target": "pathway:hsa04270", "relation": "localizes_pathway"},
        {"source": "go:0016528", "target": "pathway:hsa04020", "relation": "mediates_flux_in"},
        {"source": "go:0045121", "target": "pathway:hsa04010", "relation": "triggers_cascade_in"}, 
        {"source": "go:0005886", "target": "pathway:hsa04024", "relation": "initiates_pathway"},
        {"source": "go:0014069", "target": "pathway:hsa04724", "relation": "modulates_activity_in"},
        {"source": "go:0005886", "target": "pathway:hsa04710", "relation": "contributes_to_rhythmicity"},
        {"source": "go:0045211", "target": "pathway:hsa04024", "relation": "localizes_cAMP_production"}, 
        {"source": "go:0005886", "target": "pathway:hsa04261", "relation": "initiates_pathway"},
        {"source": "go:0005886", "target": "pathway:hsa04270", "relation": "localizes_pathway"},
        {"source": "go:0044309", "target": "pathway:hsa04020", "relation": "modulates_activity_in"},
        {"source": "go:0044309", "target": "pathway:hsa04726", "relation": "contributes_to_network"}, 
        {"source": "go:0005886", "target": "pathway:hsa04152", "relation": "initiates_pathway"},
        {"source": "go:0098984", "target": "pathway:hsa04920", "relation": "modulates_activity_in"},
        {"source": "go:0005737", "target": "pathway:hsa04152", "relation": "supports_signaling_flux"},
        {"source": "go:0005886", "target": "pathway:hsa04020", "relation": "localizes_cascade"}
    
    ]

    ##Protein to BP
    pathway_to_BP = [
        {"source": "pathway:hsa04728", "target": "bp:0007268", "relation": "executes_process"},
        {"source": "pathway:hsa04728", "target": "bp:0007626", "relation": "results_in_behavior"},
        {"source": "pathway:hsa04728", "target": "bp:0051580", "relation": "controls_feedback_loop"},
        {"source": "pathway:hsa04024", "target": "bp:0045892", "relation": "mediates_regulation"},
        {"source": "pathway:hsa04024", "target": "bp:0007212", "relation": "is_core_mechanism_of"},
        {"source": "pathway:hsa04010", "target": "bp:0002027", "relation": "contributes_to_regulation"},
        {"source": "pathway:hsa04024", "target": "bp:0007186", "relation": "is_part_of"},
        {"source": "pathway:hsa04024", "target": "bp:0008277", "relation": "contributes_to_signaling_balance"}, 
        {"source": "pathway:hsa04728", "target": "bp:0007212", "relation": "executes_process"},
        {"source": "pathway:hsa04728", "target": "bp:0035094", "relation": "results_in"},
        {"source": "pathway:hsa04728", "target": "bp:0007628", "relation": "modulates_behavior"},
        {"source": "pathway:hsa05030", "target": "bp:0060007", "relation": "mediates_process"},
        {"source": "pathway:hsa05030", "target": "bp:0048265", "relation": "cross_talks_with"},
        {"source": "pathway:hsa04010", "target": "bp:0045648", "relation": "regulates_process"},
        {"source": "pathway:hsa04010", "target": "bp:0031100", "relation": "contributes_to"},
        {"source": "pathway:hsa04728", "target": "bp:0007631", "relation": "modulates_behavior"}, 
        {"source": "pathway:hsa04726", "target": "bp:0031645", "relation": "mediates_process"},
        {"source": "pathway:hsa04726", "target": "bp:0007611", "relation": "results_in"},
        {"source": "pathway:hsa04726", "target": "bp:0001659", "relation": "controls"},
        {"source": "pathway:hsa04024", "target": "bp:0051482", "relation": "mediates_regulation"},
        {"source": "pathway:hsa04010", "target": "bp:0007611", "relation": "supports_plasticity"},
        {"source": "pathway:hsa04080", "target": "bp:0007631", "relation": "modulates_behavior"},
        {"source": "pathway:hsa04080", "target": "bp:0008217", "relation": "influences_physiology"}, 
        {"source": "pathway:hsa04020", "target": "bp:0007600", "relation": "mediates_process"},
        {"source": "pathway:hsa04020", "target": "bp:0014057", "relation": "results_in"},
        {"source": "pathway:hsa04726", "target": "bp:0007605", "relation": "modulates_process"},
        {"source": "pathway:hsa04010", "target": "bp:0050854", "relation": "regulates_process"},
        {"source": "pathway:hsa04071", "target": "bp:0045747", "relation": "supports_signaling"}, 
        {"source": "pathway:hsa04270", "target": "bp:0045907", "relation": "mediates_process"},
        {"source": "pathway:hsa04270", "target": "bp:0008217", "relation": "influences_process"},
        {"source": "pathway:hsa04010", "target": "bp:0042127", "relation": "regulates_process"},
        {"source": "pathway:hsa04010", "target": "bp:0014031", "relation": "results_in"},
        {"source": "pathway:hsa04020", "target": "bp:0003013", "relation": "supports_process"},
        {"source": "pathway:hsa04022", "target": "bp:0003013", "relation": "modulates_process"}, 
        {"source": "pathway:hsa04710", "target": "bp:0007623", "relation": "mediates_process"},
        {"source": "pathway:hsa04710", "target": "bp:0043518", "relation": "results_in"},
        {"source": "pathway:hsa04724", "target": "bp:0014057", "relation": "modulates_process"},
        {"source": "pathway:hsa04724", "target": "bp:0050848", "relation": "influences_process"},
        {"source": "pathway:hsa04024", "target": "bp:0007610", "relation": "regulates_process"},
        {"source": "pathway:hsa04024", "target": "bp:0050848", "relation": "supports_process"}, 
        {"source": "pathway:hsa04261", "target": "bp:0003013", "relation": "supports_process"},
        {"source": "pathway:hsa04020", "target": "bp:0031644", "relation": "regulates_process"},
        {"source": "pathway:hsa04020", "target": "bp:0050890", "relation": "modulates_process"}, 
        {"source": "pathway:hsa04152", "target": "bp:0007631", "relation": "regulates_process"},
        {"source": "pathway:hsa04152", "target": "bp:0010893", "relation": "mediates_flux_in"},
        {"source": "pathway:hsa04152", "target": "bp:0006006", "relation": "supports_process"},
        {"source": "pathway:hsa04920", "target": "bp:0007622", "relation": "triggers_process"},
        {"source": "pathway:hsa04020", "target": "bp:0042730", "relation": "enables_process"},
        {"source": "pathway:hsa04020", "target": "bp:0007610", "relation": "modulates_process"}
    ]

    BP_to_circuit = [
        {"source": "bp:0007212", "target": "circuit:mesolimbic_pathway", "relation": "operates_in"},
        {"source": "bp:0007212", "target": "circuit:nigrostriatal_pathway", "relation": "operates_in"},
        {"source": "bp:0007268", "target": "circuit:cortico_striatal_loop", "relation": "enables_transmission_in"},
        {"source": "bp:0007186", "target": "circuit:mesocortical_pathway", "relation": "mediates_signaling_in"},
        {"source": "bp:0007626", "target": "circuit:nigrostriatal_pathway", "relation": "executes_via"},
        {"source": "bp:0007628", "target": "circuit:cortico_striatal_loop", "relation": "executes_via"},
        {"source": "bp:0051580", "target": "circuit:nigrostriatal_pathway", "relation": "regulates_output_of"},
        {"source": "bp:0060007", "target": "circuit:mesolimbic_pathway", "relation": "localizes_to"},
        {"source": "bp:0048265", "target": "circuit:mesolimbic_pathway", "relation": "modulates_activity_in"},
        {"source": "bp:0035094", "target": "circuit:mesolimbic_pathway", "relation": "regulates_tonus_in"},
        {"source": "bp:0007611", "target": "circuit:hippocampal_circuit", "relation": "occurs_in"},
        {"source": "bp:0050854", "target": "circuit:mesocortical_pathway", "relation": "supports_plasticity_in"},
        {"source": "bp:0014057", "target": "circuit:mesocortical_pathway", "relation": "modulates_excitation_in"},
        {"source": "bp:0031645", "target": "circuit:amygdala_pfc_circuit", "relation": "stabilizes_activity"},
        {"source": "bp:0051482", "target": "circuit:amygdala_pfc_circuit", "relation": "regulates_excitability_in"},
        {"source": "bp:0002027", "target": "circuit:tuberoinfundibular_pathway", "relation": "controls_output_of"},
        {"source": "bp:0001659", "target": "circuit:tuberoinfundibular_pathway", "relation": "localized_regulation"},
        {"source": "bp:0008217", "target": "circuit:tuberoinfundibular_pathway", "relation": "autonomic_integration"},
        {"source": "bp:0007600", "target": "circuit:mesocortical_pathway", "relation": "influences_interpretation"},
        {"source": "bp:0007605", "target": "circuit:mesocortical_pathway", "relation": "influences_interpretation"}, 
        {"source": "bp:0045907", "target": "circuit:vascular_network", "relation": "operates_in"},
        {"source": "bp:0008217", "target": "circuit:vascular_network", "relation": "regulates_tonus_of"},
        {"source": "bp:0003013", "target": "circuit:vascular_network", "relation": "localizes_to"},
        {"source": "bp:0042127", "target": "circuit:cardiac_valvular_circuit", "relation": "modulates_structure_of"},
        {"source": "bp:0014031", "target": "circuit:cardiac_valvular_circuit", "relation": "occurs_in"},
        {"source": "bp:0007631", "target": "circuit:enteric_nervous_system", "relation": "modulates_motility_via"},
        {"source": "bp:0045006", "target": "circuit:enteric_nervous_system", "relation": "supports_homeostasis_in"}, 
        {"source": "bp:0007623", "target": "circuit:suprachiasmatic_nucleus", "relation": "localized_in"},
        {"source": "bp:0043518", "target": "circuit:suprachiasmatic_nucleus", "relation": "operates_in"},
        {"source": "bp:0014057", "target": "circuit:thalamocortical_relay", "relation": "modulates_activity_of"},
        {"source": "bp:0050848", "target": "circuit:thalamocortical_relay", "relation": "supports_function_of"},
        {"source": "bp:0007610", "target": "circuit:cortico_striatal_loop", "relation": "influences_output_of"}, 
        {"source": "bp:0031644", "target": "circuit:reticular_activating_system", "relation": "modulates_activity_of"},
        {"source": "bp:0050890", "target": "circuit:locus_coeruleus_projection", "relation": "supported_by"},
        {"source": "bp:0045907", "target": "circuit:vascular_network", "relation": "occurs_in"},
        {"source": "bp:0008217", "target": "circuit:baroreceptor_reflex_arc", "relation": "regulates_feedback_in"},
        {"source": "bp:0003013", "target": "circuit:vascular_network", "relation": "localized_in"}, 
        {"source": "bp:0042730", "target": "circuit:tuberomammillary_nucleus", "relation": "originates_in"},
        {"source": "bp:0007623", "target": "circuit:tuberomammillary_nucleus", "relation": "is_regulated_by"},
        {"source": "bp:0010893", "target": "circuit:ventromedial_hypothalamus", "relation": "occurs_in"},
        {"source": "bp:0007631", "target": "circuit:lateral_hypothalamus", "relation": "is_mediated_by"},
        {"source": "bp:0007622", "target": "circuit:ventromedial_hypothalamus", "relation": "is_localized_to"},
        {"source": "bp:0006006", "target": "circuit:ventromedial_hypothalamus", "relation": "is_monitored_by"}   
    ]

    circuit_to_rdoc = [
        {"source": "circuit:mesolimbic_pathway", "target": "rdoc:reward_valuation", "relation": "mediates_construct"},
        {"source": "circuit:mesolimbic_pathway", "target": "rdoc:reward_learning", "relation": "mediates_construct"},
        {"source": "circuit:mesolimbic_pathway", "target": "rdoc:reward_responsiveness", "relation": "mediates_construct"},
        {"source": "circuit:nigrostriatal_pathway", "target": "rdoc:motor_actions", "relation": "mediates_construct"},
        {"source": "circuit:nigrostriatal_pathway", "target": "rdoc:sensorimotor_behavior", "relation": "mediates_construct"},
        {"source": "circuit:cortico_striatal_loop", "target": "rdoc:habit", "relation": "mediates_construct"},
        {"source": "circuit:cortico_striatal_loop", "target": "rdoc:innate_motor", "relation": "mediates_construct"},
        {"source": "circuit:mesocortical_pathway", "target": "rdoc:cognitive_control", "relation": "supports_construct"},
        {"source": "circuit:mesocortical_pathway", "target": "rdoc:working_memory", "relation": "supports_construct"},
        {"source": "circuit:mesocortical_pathway", "target": "rdoc:attention", "relation": "supports_construct"},
        {"source": "circuit:mesocortical_pathway", "target": "rdoc:perception", "relation": "influences_construct"},
        {"source": "circuit:amygdala_pfc_circuit", "target": "rdoc:acute_threat", "relation": "mediates_construct"},
        {"source": "circuit:amygdala_pfc_circuit", "target": "rdoc:potential_threat", "relation": "mediates_construct"},
        {"source": "circuit:amygdala_pfc_circuit", "target": "rdoc:sustained_threat", "relation": "mediates_construct"},
        {"source": "circuit:hippocampal_circuit", "target": "rdoc:declarative_memory", "relation": "mediates_construct"},
        {"source": "circuit:hippocampal_circuit", "target": "rdoc:working_memory", "relation": "supports_construct"},
        {"source": "circuit:tuberoinfundibular_pathway", "target": "rdoc:arousal", "relation": "modulates_construct"},
        {"source": "circuit:tuberoinfundibular_pathway", "target": "rdoc:circadian_rhythms", "relation": "modulates_construct"}, 
        {"source": "circuit:habenula_circuit", "target": "rdoc:frustrative_nonreward", "relation": "mediates_construct"},
        {"source": "circuit:habenula_circuit", "target": "rdoc:loss", "relation": "mediates_construct"},
        {"source": "circuit:thalamocortical_relay", "target": "rdoc:perception", "relation": "mediates_construct"},
        {"source": "circuit:thalamocortical_relay", "target": "rdoc:attention", "relation": "supports_construct"},
        {"source": "circuit:hypothalamic_pituitary_axis", "target": "rdoc:arousal", "relation": "mediates_construct"},
        {"source": "circuit:hypothalamic_pituitary_axis", "target": "rdoc:affiliation_attachment", "relation": "influences_construct"}, 
        {"source": "circuit:enteric_nervous_system", "target": "rdoc:visceral_perception", "relation": "provides_sensory_input_for"},
        {"source": "circuit:vascular_network", "target": "rdoc:autonomic_arousal", "relation": "mediates_physiological_state"},
        {"source": "circuit:cardiac_valvular_circuit", "target": "rdoc:homeostatic_regulation", "relation": "is_monitored_by"},
        {"source": "rdoc:visceral_perception", "target": "rdoc:ARS", "relation": "is_part_of_domain"},
        {"source": "rdoc:homeostatic_regulation", "target": "rdoc:ARS", "relation": "is_part_of_domain"},
        {"source": "rdoc:autonomic_arousal", "target": "rdoc:ARS", "relation": "is_part_of_domain"}, 
        {"source": "circuit:suprachiasmatic_nucleus", "target": "rdoc:circadian_rhythms", "relation": "mediates_construct"},
        {"source": "circuit:suprachiasmatic_nucleus", "target": "rdoc:sleep_wake", "relation": "mediates_construct"},
        {"source": "circuit:thalamocortical_relay", "target": "rdoc:perception", "relation": "gates_sensory_input_for"},
        {"source": "circuit:thalamocortical_relay", "target": "rdoc:cognitive_control", "relation": "facilitates_construct"},
        {"source": "circuit:suprachiasmatic_nucleus", "target": "rdoc:arousal", "relation": "modulates_construct"}, 
        {"source": "circuit:reticular_activating_system", "target": "rdoc:arousal", "relation": "maintains_tonic_level_of"},
        {"source": "circuit:locus_coeruleus_projection", "target": "rdoc:sleep_wakefulness", "relation": "modulates_transition_in"},
        {"source": "circuit:baroreceptor_reflex_arc", "target": "rdoc:homeostatic_regulation", "relation": "executes_autonomic_balance_for"},
        {"source": "rdoc:arousal", "target": "rdoc:ARS", "relation": "is_part_of_domain"},
        {"source": "rdoc:sleep_wakefulness", "target": "rdoc:ARS", "relation": "is_part_of_domain"}, 
        {"source": "circuit:tuberomammillary_nucleus", "target": "rdoc:arousal", "relation": "mediates_tonic_state"},
        {"source": "circuit:tuberomammillary_nucleus", "target": "rdoc:sleep_wakefulness", "relation": "maintains_alertness_construct"},
        {"source": "circuit:ventromedial_hypothalamus", "target": "rdoc:energy_homeostasis", "relation": "regulates_satiety_balance"},
        {"source": "circuit:lateral_hypothalamus", "target": "rdoc:energy_homeostasis", "relation": "modulates_feeding_drive"},
        {"source": "rdoc:energy_homeostasis", "target": "rdoc:arousal", "relation": "interacts_with"}   
    ]

    Rdoc_construct_to_symptom = [
        {"source": "rdoc:reward_responsiveness", "target": "symp:anhedonia", "relation": "explains_symptom"},
        {"source": "rdoc:reward_responsiveness", "target": "symp:avolition", "relation": "explains_symptom"},
        {"source": "rdoc:perception", "target": "symp:hallucinations", "relation": "explains_symptom"},
        {"source": "rdoc:perception", "target": "symp:delusions", "relation": "explains_symptom"},
        {"source": "rdoc:cognitive_control", "target": "symp:impulsivity", "relation": "explains_symptom"},
        {"source": "rdoc:motor_actions", "target": "symp:tremor", "relation": "explains_symptom"},
        {"source": "rdoc:motor_actions", "target": "symp:rigidity", "relation": "explains_symptom"},
        {"source": "rdoc:motor_actions", "target": "symp:akathisia", "relation": "explains_symptom"},
        {"source": "rdoc:potential_threat", "target": "symp:anxiety", "relation": "explains_symptom"},
        {"source": "rdoc:potential_threat", "target": "symp:paranoia", "relation": "explains_symptom"}, 
        {"source": "rdoc:habit", "target": "symp:compulsive_behavior", "relation": "explains_symptom"},
        {"source": "rdoc:reward_learning", "target": "symp:impulse_control_disorder", "relation": "explains_symptom"},
        {"source": "rdoc:reward_valuation", "target": "symp:weight_gain", "relation": "explains_symptom"},
        {"source": "rdoc:cognitive_control", "target": "symp:cognitive_blunting", "relation": "explains_symptom"},
        {"source": "rdoc:arousal", "target": "symp:nausea", "relation": "explains_symptom"}, 
        {"source": "rdoc:potential_threat", "target": "symp:generalized_anxiety", "relation": "explains_symptom"},
        {"source": "rdoc:acute_threat", "target": "symp:social_anxiety", "relation": "explains_symptom"},
        {"source": "rdoc:working_memory", "target": "symp:cognitive_impairment", "relation": "influences_symptom"},
        {"source": "rdoc:declarative_memory", "target": "symp:cognitive_impairment", "relation": "influences_symptom"},
        {"source": "rdoc:reward_responsiveness", "target": "symp:depressive_mood", "relation": "modulates_symptom"},
        {"source": "rdoc:arousal", "target": "symp:insomnia", "relation": "affects_symptom"}, 
        {"source": "rdoc:sensorimotor_behavior", "target": "symp:eps_prevention", "relation": "modulates_side_effect_profile"},
        {"source": "rdoc:potential_threat", "target": "symp:aggression", "relation": "underlies_symptom"},
        {"source": "rdoc:arousal", "target": "symp:sleep_continuity", "relation": "affects_symptom"}, 
        {"source": "rdoc:visceral_perception", "target": "symp:gi_distress", "relation": "manifests_as"},
        {"source": "rdoc:homeostatic_regulation", "target": "symp:valvular_fibrosis_risk", "relation": "prevents_via_antagonism"},
        {"source": "rdoc:autonomic_arousal", "target": "symp:orthostatic_instability", "relation": "influences"},
        {"source": "rdoc:autonomic_arousal", "target": "symp:somatic_anxiety", "relation": "drives_physical_symptoms"}, 
        {"source": "rdoc:circadian_rhythms", "target": "symp:circadian_dysregulation", "relation": "manifests_as"},
        {"source": "rdoc:sleep_wake", "target": "symp:insomnia", "relation": "manifests_as"},
        {"source": "rdoc:perception", "target": "symp:cognitive_fog", "relation": "results_in_excess_noise"},
        {"source": "rdoc:attention", "target": "symp:cognitive_fog", "relation": "mitigates_via_stabilization"},
        {"source": "rdoc:cognitive_control", "target": "symp:depressive_rumination", "relation": "inhibits_pathological_loop"},
        {"source": "rdoc:arousal", "target": "symp:insomnia", "relation": "drives_hyperarousal_state"}, 
        {"source": "rdoc:homeostatic_regulation", "target": "symp:orthostatic_hypotension", "relation": "leads_to_dysfunction_in"},
        {"source": "rdoc:homeostatic_regulation", "target": "symp:tachycardia_reflex", "relation": "triggers_compensatory_state"},
        {"source": "rdoc:arousal", "target": "symp:sedation", "relation": "manifests_as_low_state"},
        {"source": "rdoc:sleep_wakefulness", "target": "symp:sedation", "relation": "disrupts_daytime_vigilance"},
        {"source": "rdoc:autonomic_arousal", "target": "symp:nasal_congestion", "relation": "results_in_vasodilation"}, 
        {"source": "rdoc:energy_homeostasis", "target": "symp:hyperphagia", "relation": "leads_to_dysfunction_in"},
        {"source": "rdoc:energy_homeostasis", "target": "symp:weight_gain", "relation": "results_in"},
        {"source": "rdoc:energy_homeostasis", "target": "symp:metabolic_syndrome_risk", "relation": "increases_vulnerability_to"},
        {"source": "rdoc:arousal", "target": "symp:somnolence", "relation": "manifests_as_deficiency_in"},
        {"source": "rdoc:sleep_wakefulness", "target": "symp:somnolence", "relation": "manifests_as"},
        {"source": "symp:hyperphagia", "target": "symp:somnolence", "relation": "exacerbates"}    
    ]


    # -----------------------------
    # JSON Path to actual path
    # -----------------------------
    def format_neuro_paths(json_data):
        """
        Converts a list of lists into a list of arrow-separated strings.
        """
        # Join each sub-list with the ' --> ' separator
        return [" --> ".join(path) for path in json_data]
    return (
        BP_to_circuit,
        Rdoc_construct,
        Rdoc_construct_to_symptom,
        biological_process,
        cc_nodes,
        cc_to_pathway,
        circuit,
        circuit_to_rdoc,
        edges,
        mf_to_cc_edges,
        molecular_function,
        nodes,
        pathway,
        pathway_to_BP,
        protien_to_mf_edges,
        symptom,
    )


@app.cell
def _(
    BP_to_circuit,
    Rdoc_construct,
    Rdoc_construct_to_symptom,
    biological_process,
    cc_nodes,
    cc_to_pathway,
    circuit,
    circuit_to_rdoc,
    edges,
    mf_to_cc_edges,
    molecular_function,
    nodes,
    pathway,
    pathway_to_BP,
    protien_to_mf_edges,
    symptom,
):

    nodes.extend(molecular_function)
    nodes.extend(cc_nodes)
    nodes.extend(pathway)
    nodes.extend(biological_process)
    nodes.extend(circuit)
    nodes.extend(Rdoc_construct)
    nodes.extend(symptom)

    edges.extend(protien_to_mf_edges)
    edges.extend(mf_to_cc_edges)
    edges.extend(cc_to_pathway)
    edges.extend(pathway_to_BP)
    edges.extend(BP_to_circuit)
    edges.extend(circuit_to_rdoc)
    edges.extend(Rdoc_construct_to_symptom)
    return


@app.cell
def _(
    KG_COLOR_PALETTE,
    add_edges_from_list,
    apply_kg_colors,
    build_graph_from_node_list,
    edges,
    nodes,
    nx,
    visualize_interactive_graph,
):
    # Shows the complete graph
    # Step 1: Initialize graph
    graph_V0 = nx.DiGraph()

    # Step 2: Add nodes to the graph 
    graph_V1 = build_graph_from_node_list(graph_V0,nodes)

    # Step 3: Add edges to the graph
    graph_V2 = add_edges_from_list(graph_V1,edges)

    #Step 4: Visualize the graph
    graph_V3 = apply_kg_colors(graph_V2,KG_COLOR_PALETTE)
    visualize_interactive_graph(graph_V3,filename="complete_graph_V2.html")
    return (graph_V3,)


@app.cell
def _(find_all_paths_to_type_ids, graph_V3, map_path_ids_to_labels, nodes):
    # 1. Get the raw IDs
    raw_paths = find_all_paths_to_type_ids(graph_V3, "drug:aripiprazole", "Symptom")

    # 2. Map them to Labels
    readable_paths = map_path_ids_to_labels(nodes, raw_paths)

    # 3. Print the results
    all_paths = []
    for path in readable_paths:
        print(" ➔ ".join(path))
        all_paths.append(" ➔ ".join(path))
    #print(i)
    #sorted(all_paths)
    return (all_paths,)


@app.cell
def _(all_paths):
    for i in (sorted(all_paths)): 
        if 'HRH1' in i: 
            print(i)
    return


@app.cell
def _(all_paths):
    len(all_paths)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
