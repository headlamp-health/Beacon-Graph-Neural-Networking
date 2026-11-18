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
            G.nodes[node_id]['subset'] = type_order.get(node_type, 3) 
        
            # Standard Pyvis formatting
            G.nodes[node_id]['label'] = str(node_id)
            G.nodes[node_id]['title'] = f"ID: {node_id}\nType: {node_type}"

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
    return (
        KG_COLOR_PALETTE,
        add_edges_from_list,
        apply_kg_colors,
        build_graph_from_node_list,
        find_all_paths_between,
        visualize_interactive_graph,
    )


@app.cell
def _():

    nodes = [
        {"id": "drug:brexpiprazole", "label": "Rexulti (brexpiprazole)", "type": "Drug", "synonyms": ["REXULTI", "brexpiprazole"]},
        {"id": "protein:HTR1A", "label": "5-HT1A receptor (HTR1A)", "type": "Protein"},
        {"id": "protein:HTR2A", "label": "5-HT2A receptor (HTR2A)", "type": "Protein"},
        {"id": "protein:HTR2B", "label": "5-HT2B receptor (HTR2B)", "type": "Protein"},
        {"id": "protein:HTR7",  "label": "5-HT7 receptor (HTR7)", "type": "Protein"},
        {"id": "protein:DRD2",  "label": "Dopamine D2 receptor (DRD2)", "type": "Protein"},
        {"id": "protein:DRD3",  "label": "Dopamine D3 receptor (DRD3)", "type": "Protein"},
        {"id": "protein:ADRA1A","label": "Adrenergic α1A receptor (ADRA1A)", "type": "Protein"},
        {"id": "protein:ADRA1B","label": "Adrenergic α1B receptor (ADRA1B)", "type": "Protein"},
        {"id": "protein:ADRA1D","label": "Adrenergic α1D receptor (ADRA1D)", "type": "Protein"},
        {"id": "protein:ADRA2C","label": "Adrenergic α2C receptor (ADRA2C)", "type": "Protein"},
        {"id": "protein:HRH1",  "label": "Histamine H1 receptor (HRH1)", "type": "Protein"},
        {"id": "protein:CHRM1", "label": "Muscarinic M1 receptor (CHRM1)", "type": "Protein"},
        {"id": "mf:gpcr_activity", "label": "G protein-coupled receptor activity", "type": "MolecularFunction"},
        {"id": "mf:dopamine_receptor_activity", "label": "Dopamine receptor activity", "type": "MolecularFunction"},
        {"id": "mf:serotonin_receptor_activity", "label": "Serotonin receptor activity", "type": "MolecularFunction"},
        {"id": "mf:adrenergic_receptor_activity", "label": "Adrenergic receptor activity", "type": "MolecularFunction"},
        {"id": "mf:alpha1_adrenergic_receptor_activity", "label": "Alpha-1 adrenergic receptor activity", "type": "MolecularFunction"},
        {"id": "mf:alpha2_adrenergic_receptor_activity", "label": "Alpha-2 adrenergic receptor activity", "type": "MolecularFunction"},
        {"id": "mf:histamine_receptor_activity", "label": "Histamine receptor activity", "type": "MolecularFunction"},
        {"id": "mf:muscarinic_acetylcholine_receptor_activity", "label": "Muscarinic acetylcholine receptor activity", "type": "MolecularFunction"},
         {"id": "cc:plasma_membrane", "label": "Plasma membrane", "type": "CellularComponent"},
        {"id": "cc:integral_membrane_component", "label": "Integral component of membrane", "type": "CellularComponent"},
        {"id": "cc:synapse", "label": "Synapse", "type": "CellularComponent"},
        {"id": "cc:postsynaptic_membrane", "label": "Postsynaptic membrane", "type": "CellularComponent"},
        {"id": "cc:presynaptic_membrane", "label": "Presynaptic membrane", "type": "CellularComponent"},
        {"id": "bp:dopamine_receptor_signaling", "label": "Dopamine receptor signaling", "type": "BiologicalProcess"},
        {"id": "bp:dopaminergic_synaptic_transmission", "label": "Dopaminergic synaptic transmission", "type": "BiologicalProcess"},

      # Serotonin / mood-related
        {"id": "bp:serotonin_receptor_signaling", "label": "Serotonin receptor signaling", "type": "BiologicalProcess"},
        {"id": "bp:serotonergic_synaptic_transmission", "label": "Serotonergic synaptic transmission", "type": "BiologicalProcess"},

      # Adrenergic / arousal-related
        {"id": "bp:adrenergic_receptor_signaling", "label": "Adrenergic receptor signaling", "type": "BiologicalProcess"},
        {"id": "bp:noradrenergic_synaptic_transmission", "label": "Noradrenergic synaptic transmission", "type": "BiologicalProcess"},

      # Histamine / sedation-weight gain (optional)
        {"id": "bp:histamine_receptor_signaling", "label": "Histamine receptor signaling", "type": "BiologicalProcess"},

      # Cholinergic / cognition (optional)
        {"id": "bp:cholinergic_receptor_signaling", "label": "Cholinergic receptor signaling", "type": "BiologicalProcess"},

      # Higher-level useful aggregator (optional)
        {"id": "bp:modulation_of_synaptic_transmission", "label": "Modulation of synaptic transmission", "type": "BiologicalProcess"},
        {"id": "bp:regulation_of_neuronal_excitation", "label": "Regulation of neuronal excitation", "type": "BiologicalProcess"}
    ]

    # Cellular Component nodes
    cc_nodes = [
      {"id": "cc:plasma_membrane", "label": "Plasma membrane", "type": "CellularComponent"},
      {"id": "cc:integral_membrane_component", "label": "Integral component of membrane", "type": "CellularComponent"},
      {"id": "cc:synapse", "label": "Synapse", "type": "CellularComponent"},
      {"id": "cc:postsynaptic_membrane", "label": "Postsynaptic membrane", "type": "CellularComponent"},
      {"id": "cc:presynaptic_membrane", "label": "Presynaptic membrane", "type": "CellularComponent"},
      {"id": "cc:cytoplasm", "label": "Cytoplasm", "type": "CellularComponent"},
    ]

    # Pathway nodes (simple, scalable set)
    pathway_nodes = [
      {"id": "pathway:gpcr_signaling", "label": "GPCR signaling", "type": "Pathway"},
      {"id": "pathway:gi_o_signaling", "label": "Gi/o-mediated GPCR signaling", "type": "Pathway"},
      {"id": "pathway:gq_signaling", "label": "Gq-mediated GPCR signaling", "type": "Pathway"},
      {"id": "pathway:gs_signaling", "label": "Gs-mediated GPCR signaling", "type": "Pathway"},
    ]

    circuit_nodes = [
      {"id": "circuit:mesolimbic_reward", "label": "Mesolimbic reward circuit (VTA→NAcc→PFC)", "type": "Circuit"},
      {"id": "circuit:mesocortical", "label": "Mesocortical circuit (VTA→PFC)", "type": "Circuit"},
      {"id": "circuit:nigrostriatal", "label": "Nigrostriatal circuit (SNc→Dorsal striatum)", "type": "Circuit"},
      {"id": "circuit:tuberoinfundibular", "label": "Tuberoinfundibular circuit (Hypothalamus→Pituitary)", "type": "Circuit"},

      {"id": "circuit:amygdala_pfc", "label": "Amygdala–PFC threat regulation circuit", "type": "Circuit"},
      {"id": "circuit:hippocampus_pfc", "label": "Hippocampus–PFC memory/context circuit", "type": "Circuit"},
      {"id": "circuit:thalamocortical", "label": "Thalamo-cortical cognitive integration circuit", "type": "Circuit"},

      {"id": "circuit:locus_coeruleus_arousal", "label": "Locus coeruleus–cortex arousal circuit", "type": "Circuit"},
      {"id": "circuit:frontostriatal", "label": "Frontostriatal control circuit (PFC↔Striatum)", "type": "Circuit"},

      {"id": "circuit:corticothalamic_sleep_wake", "label": "Cortico-thalamic sleep–wake regulation circuit", "type": "Circuit"}
    ]

    brainregion_nodes = [
      {"id": "brainregion:vta", "label": "Ventral Tegmental Area (VTA)", "type": "BrainRegion"},
      {"id": "brainregion:nacc", "label": "Nucleus Accumbens (NAcc)", "type": "BrainRegion"},
      {"id": "brainregion:pfc", "label": "Prefrontal Cortex (PFC)", "type": "BrainRegion"},
      {"id": "brainregion:snc", "label": "Substantia Nigra pars compacta (SNc)", "type": "BrainRegion"},
      {"id": "brainregion:dorsal_striatum", "label": "Dorsal Striatum", "type": "BrainRegion"},
      {"id": "brainregion:hypothalamus", "label": "Hypothalamus", "type": "BrainRegion"},
      {"id": "brainregion:pituitary", "label": "Pituitary", "type": "BrainRegion"},
      {"id": "brainregion:amygdala", "label": "Amygdala", "type": "BrainRegion"},
      {"id": "brainregion:hippocampus", "label": "Hippocampus", "type": "BrainRegion"},
      {"id": "brainregion:thalamus", "label": "Thalamus", "type": "BrainRegion"},
      {"id": "brainregion:cortex", "label": "Cerebral Cortex", "type": "BrainRegion"},
      {"id": "brainregion:locus_coeruleus", "label": "Locus Coeruleus (LC)", "type": "BrainRegion"}
    ]

    ntsystem_nodes = [
      {"id": "ntsystem:dopamine", "label": "Dopamine system", "type": "NeurotransmitterSystem"},
      {"id": "ntsystem:serotonin", "label": "Serotonin system", "type": "NeurotransmitterSystem"},
      {"id": "ntsystem:norepinephrine", "label": "Norepinephrine system", "type": "NeurotransmitterSystem"},
      {"id": "ntsystem:glutamate", "label": "Glutamate system", "type": "NeurotransmitterSystem"},
      {"id": "ntsystem:gaba", "label": "GABA system", "type": "NeurotransmitterSystem"},
      {"id": "ntsystem:histamine", "label": "Histamine system", "type": "NeurotransmitterSystem"},
      {"id": "ntsystem:acetylcholine", "label": "Acetylcholine system", "type": "NeurotransmitterSystem"},
    ]

    neurotransmitter_nodes = [
      {"id": "nt:dopamine", "label": "Dopamine", "type": "Neurotransmitter"},
      {"id": "nt:serotonin", "label": "Serotonin (5-HT)", "type": "Neurotransmitter"},
      {"id": "nt:norepinephrine", "label": "Norepinephrine (NE)", "type": "Neurotransmitter"},
      {"id": "nt:glutamate", "label": "Glutamate", "type": "Neurotransmitter"},
      {"id": "nt:gaba", "label": "GABA", "type": "Neurotransmitter"},
      {"id": "nt:histamine", "label": "Histamine", "type": "Neurotransmitter"},
      {"id": "nt:acetylcholine", "label": "Acetylcholine (ACh)", "type": "Neurotransmitter"},
    ]

    rdoc_nodes = [
      # Domains
      {"id": "rdoc_domain:negative_valence", "label": "RDoC Domain: Negative Valence Systems", "type": "RDoC_Domain"},
      {"id": "rdoc_domain:positive_valence", "label": "RDoC Domain: Positive Valence Systems", "type": "RDoC_Domain"},
      {"id": "rdoc_domain:cognitive", "label": "RDoC Domain: Cognitive Systems", "type": "RDoC_Domain"},
      {"id": "rdoc_domain:arousal_regulatory", "label": "RDoC Domain: Arousal / Regulatory Systems", "type": "RDoC_Domain"},
      {"id": "rdoc_domain:social_processes", "label": "RDoC Domain: Systems for Social Processes", "type": "RDoC_Domain"},

      # Constructs (Negative Valence)
      {"id": "rdoc_construct:acute_threat", "label": "RDoC Construct: Acute Threat (Fear)", "type": "RDoC_Construct"},
      {"id": "rdoc_construct:sustained_threat", "label": "RDoC Construct: Sustained Threat", "type": "RDoC_Construct"},

      # Constructs (Positive Valence)
      {"id": "rdoc_construct:reward_valuation", "label": "RDoC Construct: Reward Valuation", "type": "RDoC_Construct"},
      {"id": "rdoc_construct:reward_learning", "label": "RDoC Construct: Reward Learning", "type": "RDoC_Construct"},
      {"id": "rdoc_construct:reward_responsiveness", "label": "RDoC Construct: Reward Responsiveness", "type": "RDoC_Construct"},

      # Constructs (Cognitive)
      {"id": "rdoc_construct:cognitive_control", "label": "RDoC Construct: Cognitive Control", "type": "RDoC_Construct"},
      {"id": "rdoc_construct:working_memory", "label": "RDoC Construct: Working Memory", "type": "RDoC_Construct"},

      # Constructs (Arousal/Regulatory)
      {"id": "rdoc_construct:arousal", "label": "RDoC Construct: Arousal", "type": "RDoC_Construct"},
      {"id": "rdoc_construct:sleep_wake", "label": "RDoC Construct: Sleep–Wake", "type": "RDoC_Construct"},

      # Constructs (Social)
      {"id": "rdoc_construct:affiliation_attachment", "label": "RDoC Construct: Affiliation & Attachment", "type": "RDoC_Construct"},
    ]

    symptom_nodes = [
      {"id": "symptom:anxiety", "label": "Anxiety", "type": "Symptom"},
      {"id": "symptom:panic", "label": "Panic attacks", "type": "Symptom"},
      {"id": "symptom:hypervigilance", "label": "Hypervigilance", "type": "Symptom"},
      {"id": "symptom:avoidance", "label": "Avoidance", "type": "Symptom"},

      {"id": "symptom:anhedonia", "label": "Anhedonia (loss of pleasure)", "type": "Symptom"},
      {"id": "symptom:amotivation", "label": "Amotivation / low drive", "type": "Symptom"},
      {"id": "symptom:low_energy", "label": "Low energy / fatigue", "type": "Symptom"},

      {"id": "symptom:impulsivity", "label": "Impulsivity", "type": "Symptom"},
      {"id": "symptom:inattention", "label": "Inattention", "type": "Symptom"},
      {"id": "symptom:poor_working_memory", "label": "Poor working memory", "type": "Symptom"},
      {"id": "symptom:executive_dysfunction", "label": "Executive dysfunction", "type": "Symptom"},

      {"id": "symptom:insomnia", "label": "Insomnia", "type": "Symptom"},
      {"id": "symptom:hypersomnia", "label": "Hypersomnia", "type": "Symptom"},
      {"id": "symptom:irritability", "label": "Irritability", "type": "Symptom"},

      {"id": "symptom:social_withdrawal", "label": "Social withdrawal", "type": "Symptom"},
      {"id": "symptom:blunted_affect", "label": "Blunted affect", "type": "Symptom"},
    ]



    edges = [
        # Partial agonist edges
        {"source": "drug:brexpiprazole", "target": "protein:HTR1A", "relation": "partial_agonist_of", "Ki_nM": 0.12, "evidence": "FDA label (Revised 5/2025) Section 12.2"},
        {"source": "drug:brexpiprazole", "target": "protein:DRD2",  "relation": "partial_agonist_of", "Ki_nM": 0.30, "evidence": "FDA label (Revised 5/2025) Section 12.2"},
        {"source": "drug:brexpiprazole", "target": "protein:DRD3",  "relation": "partial_agonist_of", "Ki_nM": 1.10, "evidence": "FDA label (Revised 5/2025) Section 12.2"},
        # Antagonist edges
        {"source": "drug:brexpiprazole", "target": "protein:HTR2A",  "relation": "antagonist_of", "Ki_nM": 0.47, "evidence": "FDA label (Revised 5/2025) Section 12.2"},
        {"source": "drug:brexpiprazole", "target": "protein:HTR2B",  "relation": "antagonist_of", "Ki_nM": 1.90, "evidence": "FDA label (Revised 5/2025) Section 12.2"},
        {"source": "drug:brexpiprazole", "target": "protein:HTR7",   "relation": "antagonist_of", "Ki_nM": 3.70, "evidence": "FDA label (Revised 5/2025) Section 12.2"},
        {"source": "drug:brexpiprazole", "target": "protein:ADRA1A","relation": "antagonist_of", "Ki_nM": 3.80, "evidence": "FDA label (Revised 5/2025) Section 12.2"},
        {"source": "drug:brexpiprazole", "target": "protein:ADRA1B","relation": "antagonist_of", "Ki_nM": 0.17, "evidence": "FDA label (Revised 5/2025) Section 12.2"},
        {"source": "drug:brexpiprazole", "target": "protein:ADRA1D","relation": "antagonist_of", "Ki_nM": 2.60, "evidence": "FDA label (Revised 5/2025) Section 12.2"},
        {"source": "drug:brexpiprazole", "target": "protein:ADRA2C","relation": "antagonist_of", "Ki_nM": 0.59, "evidence": "FDA label (Revised 5/2025) Section 12.2"},
        # Other binding (affinity mentioned, action not specified in label excerpt)
        {"source": "drug:brexpiprazole", "target": "protein:HRH1",  "relation": "binds", "Ki_nM": 19.0, "evidence": "FDA label (Revised 5/2025) Section 12.2"},
        {"source": "drug:brexpiprazole", "target": "protein:CHRM1", "relation": "binds", "assay_note": "67% inhibition at 10 µM", "evidence": "FDA label (Revised 5/2025) Section 12.2"},
          {"source": "protein:DRD2", "target": "mf:gpcr_activity", "relation": "has_molecular_function"},
        {"source": "protein:DRD2", "target": "mf:dopamine_receptor_activity", "relation": "has_molecular_function"},
        {"source": "protein:DRD3", "target": "mf:gpcr_activity", "relation": "has_molecular_function"},
        {"source": "protein:DRD3", "target": "mf:dopamine_receptor_activity", "relation": "has_molecular_function"},

      # Serotonin receptors
        {"source": "protein:HTR1A", "target": "mf:gpcr_activity", "relation": "has_molecular_function"},
        {"source": "protein:HTR1A", "target": "mf:serotonin_receptor_activity", "relation": "has_molecular_function"},
        {"source": "protein:HTR2A", "target": "mf:gpcr_activity", "relation": "has_molecular_function"},
        {"source": "protein:HTR2A", "target": "mf:serotonin_receptor_activity", "relation": "has_molecular_function"},
        {"source": "protein:HTR2B", "target": "mf:gpcr_activity", "relation": "has_molecular_function"},
        {"source": "protein:HTR2B", "target": "mf:serotonin_receptor_activity", "relation": "has_molecular_function"},
        {"source": "protein:HTR7", "target": "mf:gpcr_activity", "relation": "has_molecular_function"},
        {"source": "protein:HTR7", "target": "mf:serotonin_receptor_activity", "relation": "has_molecular_function"},
      # Adrenergic receptors
        {"source": "protein:ADRA1A", "target": "mf:gpcr_activity", "relation": "has_molecular_function"},
        {"source": "protein:ADRA1A", "target": "mf:adrenergic_receptor_activity", "relation": "has_molecular_function"},
        {"source": "protein:ADRA1A", "target": "mf:alpha1_adrenergic_receptor_activity", "relation": "has_molecular_function"},
        {"source": "protein:ADRA1B", "target": "mf:gpcr_activity", "relation": "has_molecular_function"},
        {"source": "protein:ADRA1B", "target": "mf:adrenergic_receptor_activity", "relation": "has_molecular_function"},
        {"source": "protein:ADRA1B", "target": "mf:alpha1_adrenergic_receptor_activity", "relation": "has_molecular_function"},
        {"source": "protein:ADRA1D", "target": "mf:gpcr_activity", "relation": "has_molecular_function"},
        {"source": "protein:ADRA1D", "target": "mf:adrenergic_receptor_activity", "relation": "has_molecular_function"},
        {"source": "protein:ADRA1D", "target": "mf:alpha1_adrenergic_receptor_activity", "relation": "has_molecular_function"},
        {"source": "protein:ADRA2C", "target": "mf:gpcr_activity", "relation": "has_molecular_function"},
        {"source": "protein:ADRA2C", "target": "mf:adrenergic_receptor_activity", "relation": "has_molecular_function"},
        {"source": "protein:ADRA2C", "target": "mf:alpha2_adrenergic_receptor_activity", "relation": "has_molecular_function"},
      # Optional secondary targets
        {"source": "protein:HRH1", "target": "mf:gpcr_activity", "relation": "has_molecular_function"},
        {"source": "protein:HRH1", "target": "mf:histamine_receptor_activity", "relation": "has_molecular_function"},
        {"source": "protein:CHRM1", "target": "mf:gpcr_activity", "relation": "has_molecular_function"},
        {"source": "protein:CHRM1", "target": "mf:muscarinic_acetylcholine_receptor_activity", "relation": "has_molecular_function"},
          {"source": "protein:DRD2", "target": "cc:plasma_membrane", "relation": "located_in", "confidence": "high"},
      {"source": "protein:DRD2", "target": "cc:integral_membrane_component", "relation": "located_in", "confidence": "high"},
      {"source": "protein:DRD3", "target": "cc:plasma_membrane", "relation": "located_in", "confidence": "high"},
      {"source": "protein:DRD3", "target": "cc:integral_membrane_component", "relation": "located_in", "confidence": "high"},

      {"source": "protein:HTR1A", "target": "cc:plasma_membrane", "relation": "located_in", "confidence": "high"},
      {"source": "protein:HTR1A", "target": "cc:integral_membrane_component", "relation": "located_in", "confidence": "high"},
      {"source": "protein:HTR2A", "target": "cc:plasma_membrane", "relation": "located_in", "confidence": "high"},
      {"source": "protein:HTR2A", "target": "cc:integral_membrane_component", "relation": "located_in", "confidence": "high"},
      {"source": "protein:HTR2B", "target": "cc:plasma_membrane", "relation": "located_in", "confidence": "high"},
      {"source": "protein:HTR2B", "target": "cc:integral_membrane_component", "relation": "located_in", "confidence": "high"},
      {"source": "protein:HTR7", "target": "cc:plasma_membrane", "relation": "located_in", "confidence": "high"},
      {"source": "protein:HTR7", "target": "cc:integral_membrane_component", "relation": "located_in", "confidence": "high"},
      {"source": "protein:ADRA1A", "target": "cc:plasma_membrane", "relation": "located_in", "confidence": "high"},
      {"source": "protein:ADRA1A", "target": "cc:integral_membrane_component", "relation": "located_in", "confidence": "high"},
      {"source": "protein:ADRA1B", "target": "cc:plasma_membrane", "relation": "located_in", "confidence": "high"},
      {"source": "protein:ADRA1B", "target": "cc:integral_membrane_component", "relation": "located_in", "confidence": "high"},
      {"source": "protein:ADRA1D", "target": "cc:plasma_membrane", "relation": "located_in", "confidence": "high"},
      {"source": "protein:ADRA1D", "target": "cc:integral_membrane_component", "relation": "located_in", "confidence": "high"},
      {"source": "protein:ADRA2C", "target": "cc:plasma_membrane", "relation": "located_in", "confidence": "high"},
      {"source": "protein:ADRA2C", "target": "cc:integral_membrane_component", "relation": "located_in", "confidence": "high"},

      {"source": "protein:HRH1", "target": "cc:plasma_membrane", "relation": "located_in", "confidence": "high"},
      {"source": "protein:HRH1", "target": "cc:integral_membrane_component", "relation": "located_in", "confidence": "high"},
      {"source": "protein:CHRM1", "target": "cc:plasma_membrane", "relation": "located_in", "confidence": "high"},
      {"source": "protein:CHRM1", "target": "cc:integral_membrane_component", "relation": "located_in", "confidence": "high"},

      # Optional neuron-context (medium confidence, depends on brain region/cell type)
      {"source": "protein:DRD2", "target": "cc:synapse", "relation": "located_in", "confidence": "medium"},
      {"source": "protein:DRD3", "target": "cc:synapse", "relation": "located_in", "confidence": "medium"},
      {"source": "protein:HTR1A", "target": "cc:synapse", "relation": "located_in", "confidence": "medium"},
      {"source": "protein:HTR2A", "target": "cc:postsynaptic_membrane", "relation": "located_in", "confidence": "medium"},
      {"source": "protein:ADRA2C", "target": "cc:presynaptic_membrane", "relation": "located_in", "confidence": "medium"},
          {"source": "protein:DRD2", "target": "bp:dopamine_receptor_signaling", "relation": "involved_in"},
      {"source": "protein:DRD2", "target": "bp:dopaminergic_synaptic_transmission", "relation": "involved_in"},

      {"source": "protein:DRD3", "target": "bp:dopamine_receptor_signaling", "relation": "involved_in"},
      {"source": "protein:DRD3", "target": "bp:dopaminergic_synaptic_transmission", "relation": "involved_in"},

      # Serotonin receptors
      {"source": "protein:HTR1A", "target": "bp:serotonin_receptor_signaling", "relation": "involved_in"},
      {"source": "protein:HTR1A", "target": "bp:serotonergic_synaptic_transmission", "relation": "involved_in"},

      {"source": "protein:HTR2A", "target": "bp:serotonin_receptor_signaling", "relation": "involved_in"},
      {"source": "protein:HTR2A", "target": "bp:serotonergic_synaptic_transmission", "relation": "involved_in"},

      {"source": "protein:HTR2B", "target": "bp:serotonin_receptor_signaling", "relation": "involved_in"},
      {"source": "protein:HTR2B", "target": "bp:serotonergic_synaptic_transmission", "relation": "involved_in"},

      {"source": "protein:HTR7", "target": "bp:serotonin_receptor_signaling", "relation": "involved_in"},
      {"source": "protein:HTR7", "target": "bp:serotonergic_synaptic_transmission", "relation": "involved_in"},

      # Adrenergic receptors
      {"source": "protein:ADRA1A", "target": "bp:adrenergic_receptor_signaling", "relation": "involved_in"},
      {"source": "protein:ADRA1A", "target": "bp:noradrenergic_synaptic_transmission", "relation": "involved_in"},

      {"source": "protein:ADRA1B", "target": "bp:adrenergic_receptor_signaling", "relation": "involved_in"},
      {"source": "protein:ADRA1B", "target": "bp:noradrenergic_synaptic_transmission", "relation": "involved_in"},

      {"source": "protein:ADRA1D", "target": "bp:adrenergic_receptor_signaling", "relation": "involved_in"},
      {"source": "protein:ADRA1D", "target": "bp:noradrenergic_synaptic_transmission", "relation": "involved_in"},

      {"source": "protein:ADRA2C", "target": "bp:adrenergic_receptor_signaling", "relation": "involved_in"},
      {"source": "protein:ADRA2C", "target": "bp:noradrenergic_synaptic_transmission", "relation": "involved_in"},

      # Optional secondary targets
      {"source": "protein:HRH1", "target": "bp:histamine_receptor_signaling", "relation": "involved_in"},
      {"source": "protein:CHRM1", "target": "bp:cholinergic_receptor_signaling", "relation": "involved_in"},

      # Aggregator links (keep or drop depending on clutter)
      {"source": "protein:DRD2", "target": "bp:modulation_of_synaptic_transmission", "relation": "involved_in"},
      {"source": "protein:DRD3", "target": "bp:modulation_of_synaptic_transmission", "relation": "involved_in"},
      {"source": "protein:HTR1A", "target": "bp:modulation_of_synaptic_transmission", "relation": "involved_in"},
      {"source": "protein:HTR2A", "target": "bp:modulation_of_synaptic_transmission", "relation": "involved_in"},
      {"source": "protein:HTR7",  "target": "bp:modulation_of_synaptic_transmission", "relation": "involved_in"},
      {"source": "protein:ADRA2C","target": "bp:modulation_of_synaptic_transmission", "relation": "involved_in"},

      {"source": "protein:DRD2", "target": "bp:regulation_of_neuronal_excitation", "relation": "involved_in"},
      {"source": "protein:HTR1A", "target": "bp:regulation_of_neuronal_excitation", "relation": "involved_in"},
      {"source": "protein:HTR2A", "target": "bp:regulation_of_neuronal_excitation", "relation": "involved_in"},
      {"source": "protein:ADRA1A", "target": "bp:regulation_of_neuronal_excitation", "relation": "involved_in"},
      {"source": "protein:ADRA2C", "target": "bp:regulation_of_neuronal_excitation", "relation": "involved_in"}

    ]

    protein_to_cc_edges = [
      # High confidence for all these receptors (GPCRs): plasma membrane + integral membrane
      *[
        {"source": p, "target": "cc:plasma_membrane", "relation": "located_in", "confidence": "high"}
        for p in [
          "protein:DRD2","protein:DRD3","protein:HTR1A","protein:HTR2A","protein:HTR2B","protein:HTR7",
          "protein:ADRA1A","protein:ADRA1B","protein:ADRA1D","protein:ADRA2C","protein:HRH1","protein:CHRM1"
        ]
      ],
      *[
        {"source": p, "target": "cc:integral_membrane_component", "relation": "located_in", "confidence": "high"}
        for p in [
          "protein:DRD2","protein:DRD3","protein:HTR1A","protein:HTR2A","protein:HTR2B","protein:HTR7",
          "protein:ADRA1A","protein:ADRA1B","protein:ADRA1D","protein:ADRA2C","protein:HRH1","protein:CHRM1"
        ]
      ],

      # Optional neuron-context edges (medium confidence; depends on region/cell type)
      {"source": "protein:HTR2A", "target": "cc:postsynaptic_membrane", "relation": "located_in", "confidence": "medium"},
      {"source": "protein:ADRA2C", "target": "cc:presynaptic_membrane", "relation": "located_in", "confidence": "medium"},
      {"source": "protein:DRD2",  "target": "cc:synapse", "relation": "located_in", "confidence": "medium"},
      {"source": "protein:HTR1A", "target": "cc:synapse", "relation": "located_in", "confidence": "medium"},
    ]

    cc_to_bp_edges = [
      # Receptor signaling is primarily at the membrane (receptor is there)
      {"source": "cc:plasma_membrane", "target": "bp:dopamine_receptor_signaling",   "relation": "enables_context_for"},
      {"source": "cc:plasma_membrane", "target": "bp:serotonin_receptor_signaling",  "relation": "enables_context_for"},
      {"source": "cc:plasma_membrane", "target": "bp:adrenergic_receptor_signaling", "relation": "enables_context_for"},
      {"source": "cc:plasma_membrane", "target": "bp:histamine_receptor_signaling",  "relation": "enables_context_for"},
      {"source": "cc:plasma_membrane", "target": "bp:cholinergic_receptor_signaling","relation": "enables_context_for"},

      # Synaptic transmission conceptually occurs at synapses
      {"source": "cc:synapse", "target": "bp:dopaminergic_synaptic_transmission",    "relation": "occurs_in"},
      {"source": "cc:synapse", "target": "bp:serotonergic_synaptic_transmission",   "relation": "occurs_in"},
      {"source": "cc:synapse", "target": "bp:noradrenergic_synaptic_transmission",  "relation": "occurs_in"},

      # Many downstream signaling steps happen in cytoplasm (second messengers)
      {"source": "cc:cytoplasm", "target": "bp:regulation_of_neuronal_excitation",  "relation": "enables_context_for"},
      {"source": "cc:cytoplasm", "target": "bp:modulation_of_synaptic_transmission","relation": "enables_context_for"},
    ]

    mf_to_bp_edges = [
      {"source": "mf:dopamine_receptor_activity", "target": "bp:dopamine_receptor_signaling", "relation": "part_of"},
      {"source": "mf:serotonin_receptor_activity", "target": "bp:serotonin_receptor_signaling", "relation": "part_of"},
      {"source": "mf:adrenergic_receptor_activity", "target": "bp:adrenergic_receptor_signaling", "relation": "part_of"},
      {"source": "mf:histamine_receptor_activity", "target": "bp:histamine_receptor_signaling", "relation": "part_of"},
      {"source": "mf:muscarinic_acetylcholine_receptor_activity", "target": "bp:cholinergic_receptor_signaling", "relation": "part_of"},

      # Aggregators (optional)
      {"source": "mf:gpcr_activity", "target": "bp:modulation_of_synaptic_transmission", "relation": "contributes_to"},
      {"source": "mf:gpcr_activity", "target": "bp:regulation_of_neuronal_excitation", "relation": "contributes_to"},
    ]

    pathway_to_bp_edges = [
      # General GPCR signaling contributes broadly
      {"source": "pathway:gpcr_signaling", "target": "bp:modulation_of_synaptic_transmission", "relation": "contributes_to"},
      {"source": "pathway:gpcr_signaling", "target": "bp:regulation_of_neuronal_excitation", "relation": "contributes_to"},

      # Neurotransmitter receptor signaling BPs
      {"source": "pathway:gi_o_signaling", "target": "bp:dopamine_receptor_signaling", "relation": "contributes_to"},
      {"source": "pathway:gi_o_signaling", "target": "bp:serotonin_receptor_signaling", "relation": "contributes_to"},
      {"source": "pathway:gq_signaling",   "target": "bp:serotonin_receptor_signaling", "relation": "contributes_to"},
      {"source": "pathway:gq_signaling",   "target": "bp:adrenergic_receptor_signaling", "relation": "contributes_to"},
      {"source": "pathway:gs_signaling",   "target": "bp:serotonin_receptor_signaling", "relation": "contributes_to"},

      # Synaptic transmission (as downstream consequence)
      {"source": "pathway:gi_o_signaling", "target": "bp:dopaminergic_synaptic_transmission", "relation": "contributes_to"},
      {"source": "pathway:gi_o_signaling", "target": "bp:serotonergic_synaptic_transmission", "relation": "contributes_to"},
      {"source": "pathway:gq_signaling",   "target": "bp:noradrenergic_synaptic_transmission", "relation": "contributes_to"},
    ]

    bp_to_circuit_edges = [
      # Dopamine-related BPs → dopamine circuits
      {"source": "bp:dopamine_receptor_signaling", "target": "circuit:mesolimbic_reward", "relation": "modulates"},
      {"source": "bp:dopaminergic_synaptic_transmission", "target": "circuit:mesolimbic_reward", "relation": "modulates"},
      {"source": "bp:dopamine_receptor_signaling", "target": "circuit:mesocortical", "relation": "modulates"},
      {"source": "bp:dopaminergic_synaptic_transmission", "target": "circuit:mesocortical", "relation": "modulates"},
      {"source": "bp:dopamine_receptor_signaling", "target": "circuit:nigrostriatal", "relation": "modulates"},
      {"source": "bp:dopaminergic_synaptic_transmission", "target": "circuit:nigrostriatal", "relation": "modulates"},
      {"source": "bp:dopamine_receptor_signaling", "target": "circuit:tuberoinfundibular", "relation": "modulates"},

      # Serotonin-related BPs → mood/threat/context circuits (broad modulatory influence)
      {"source": "bp:serotonin_receptor_signaling", "target": "circuit:amygdala_pfc", "relation": "modulates"},
      {"source": "bp:serotonergic_synaptic_transmission", "target": "circuit:amygdala_pfc", "relation": "modulates"},
      {"source": "bp:serotonin_receptor_signaling", "target": "circuit:hippocampus_pfc", "relation": "modulates"},
      {"source": "bp:serotonergic_synaptic_transmission", "target": "circuit:hippocampus_pfc", "relation": "modulates"},
      {"source": "bp:serotonin_receptor_signaling", "target": "circuit:thalamocortical", "relation": "modulates"},

      # Adrenergic-related BPs → arousal + attention/control circuits
      {"source": "bp:adrenergic_receptor_signaling", "target": "circuit:locus_coeruleus_arousal", "relation": "modulates"},
      {"source": "bp:noradrenergic_synaptic_transmission", "target": "circuit:locus_coeruleus_arousal", "relation": "modulates"},
      {"source": "bp:adrenergic_receptor_signaling", "target": "circuit:frontostriatal", "relation": "modulates"},
      {"source": "bp:noradrenergic_synaptic_transmission", "target": "circuit:frontostriatal", "relation": "modulates"},

      # Histamine/cholinergic BPs → arousal/cognition/sleep-wake circuits (optional but useful)
      {"source": "bp:histamine_receptor_signaling", "target": "circuit:corticothalamic_sleep_wake", "relation": "modulates"},
      {"source": "bp:cholinergic_receptor_signaling", "target": "circuit:thalamocortical", "relation": "modulates"},

      # Aggregator BPs → many circuits
      {"source": "bp:modulation_of_synaptic_transmission", "target": "circuit:mesolimbic_reward", "relation": "modulates"},
      {"source": "bp:modulation_of_synaptic_transmission", "target": "circuit:amygdala_pfc", "relation": "modulates"},
      {"source": "bp:regulation_of_neuronal_excitation", "target": "circuit:amygdala_pfc", "relation": "modulates"},
      {"source": "bp:regulation_of_neuronal_excitation", "target": "circuit:frontostriatal", "relation": "modulates"}
    ]

    brainregion_to_circuit_edges = [

      # Mesolimbic reward circuit
      {"source": "brainregion:vta", "target": "circuit:mesolimbic_reward", "relation": "origin_of"},
      {"source": "brainregion:nacc", "target": "circuit:mesolimbic_reward", "relation": "terminus_of"},
      {"source": "brainregion:pfc", "target": "circuit:mesolimbic_reward", "relation": "terminus_of"},

      # Mesocortical circuit
      {"source": "brainregion:vta", "target": "circuit:mesocortical", "relation": "origin_of"},
      {"source": "brainregion:pfc", "target": "circuit:mesocortical", "relation": "terminus_of"},

      # Nigrostriatal circuit
      {"source": "brainregion:snc", "target": "circuit:nigrostriatal", "relation": "origin_of"},
      {"source": "brainregion:dorsal_striatum", "target": "circuit:nigrostriatal", "relation": "terminus_of"},

      # Tuberoinfundibular circuit
      {"source": "brainregion:hypothalamus", "target": "circuit:tuberoinfundibular", "relation": "origin_of"},
      {"source": "brainregion:pituitary", "target": "circuit:tuberoinfundibular", "relation": "terminus_of"},

      # Amygdala–PFC circuit (bidirectional)
      {"source": "brainregion:amygdala", "target": "circuit:amygdala_pfc", "relation": "origin_of"},
      {"source": "brainregion:pfc", "target": "circuit:amygdala_pfc", "relation": "terminus_of"},
      {"source": "brainregion:pfc", "target": "circuit:amygdala_pfc", "relation": "origin_of"},
      {"source": "brainregion:amygdala", "target": "circuit:amygdala_pfc", "relation": "terminus_of"},

      # Hippocampus–PFC circuit (bidirectional)
      {"source": "brainregion:hippocampus", "target": "circuit:hippocampus_pfc", "relation": "origin_of"},
      {"source": "brainregion:pfc", "target": "circuit:hippocampus_pfc", "relation": "terminus_of"},
      {"source": "brainregion:pfc", "target": "circuit:hippocampus_pfc", "relation": "origin_of"},
      {"source": "brainregion:hippocampus", "target": "circuit:hippocampus_pfc", "relation": "terminus_of"},

      # Thalamo-cortical circuit (bidirectional)
      {"source": "brainregion:thalamus", "target": "circuit:thalamocortical", "relation": "origin_of"},
      {"source": "brainregion:cortex", "target": "circuit:thalamocortical", "relation": "terminus_of"},
      {"source": "brainregion:cortex", "target": "circuit:thalamocortical", "relation": "origin_of"},
      {"source": "brainregion:thalamus", "target": "circuit:thalamocortical", "relation": "terminus_of"},

      # Locus coeruleus arousal circuit
      {"source": "brainregion:locus_coeruleus", "target": "circuit:locus_coeruleus_arousal", "relation": "origin_of"},
      {"source": "brainregion:cortex", "target": "circuit:locus_coeruleus_arousal", "relation": "terminus_of"}
    ]

    nt_edges = [
      # NTSystem uses neurotransmitter
      {"source": "ntsystem:dopamine", "target": "nt:dopamine", "relation": "uses_neurotransmitter"},
      {"source": "ntsystem:serotonin", "target": "nt:serotonin", "relation": "uses_neurotransmitter"},
      {"source": "ntsystem:norepinephrine", "target": "nt:norepinephrine", "relation": "uses_neurotransmitter"},
      {"source": "ntsystem:glutamate", "target": "nt:glutamate", "relation": "uses_neurotransmitter"},
      {"source": "ntsystem:gaba", "target": "nt:gaba", "relation": "uses_neurotransmitter"},
      {"source": "ntsystem:histamine", "target": "nt:histamine", "relation": "uses_neurotransmitter"},
      {"source": "ntsystem:acetylcholine", "target": "nt:acetylcholine", "relation": "uses_neurotransmitter"},

      # Circuit modulated_by NTSystem
      {"source": "circuit:mesolimbic_reward", "target": "ntsystem:dopamine", "relation": "modulated_by"},
      {"source": "circuit:mesocortical", "target": "ntsystem:dopamine", "relation": "modulated_by"},
      {"source": "circuit:nigrostriatal", "target": "ntsystem:dopamine", "relation": "modulated_by"},
      {"source": "circuit:tuberoinfundibular", "target": "ntsystem:dopamine", "relation": "modulated_by"},

      {"source": "circuit:amygdala_pfc", "target": "ntsystem:serotonin", "relation": "modulated_by"},
      {"source": "circuit:amygdala_pfc", "target": "ntsystem:norepinephrine", "relation": "modulated_by"},
      {"source": "circuit:amygdala_pfc", "target": "ntsystem:glutamate", "relation": "uses_fast_transmission"},
      {"source": "circuit:amygdala_pfc", "target": "ntsystem:gaba", "relation": "uses_fast_transmission"},

      {"source": "circuit:hippocampus_pfc", "target": "ntsystem:serotonin", "relation": "modulated_by"},
      {"source": "circuit:hippocampus_pfc", "target": "ntsystem:glutamate", "relation": "uses_fast_transmission"},
      {"source": "circuit:hippocampus_pfc", "target": "ntsystem:gaba", "relation": "uses_fast_transmission"},

      {"source": "circuit:thalamocortical", "target": "ntsystem:glutamate", "relation": "uses_fast_transmission"},
      {"source": "circuit:thalamocortical", "target": "ntsystem:gaba", "relation": "uses_fast_transmission"},
      {"source": "circuit:thalamocortical", "target": "ntsystem:acetylcholine", "relation": "modulated_by"},

      {"source": "circuit:locus_coeruleus_arousal", "target": "ntsystem:norepinephrine", "relation": "modulated_by"},
      {"source": "circuit:corticothalamic_sleep_wake", "target": "ntsystem:histamine", "relation": "modulated_by"},
      {"source": "circuit:corticothalamic_sleep_wake", "target": "ntsystem:acetylcholine", "relation": "modulated_by"},

      # NTSystem originates_in brain regions (optional but very useful)
      {"source": "ntsystem:dopamine", "target": "brainregion:vta", "relation": "originates_in"},
      {"source": "ntsystem:dopamine", "target": "brainregion:snc", "relation": "originates_in"},
      {"source": "ntsystem:dopamine", "target": "brainregion:hypothalamus", "relation": "originates_in"},  # tuberoinfundibular dopamine

      {"source": "ntsystem:serotonin", "target": "brainregion:raphe_nuclei", "relation": "originates_in"},
      {"source": "ntsystem:norepinephrine", "target": "brainregion:locus_coeruleus", "relation": "originates_in"},
      {"source": "ntsystem:histamine", "target": "brainregion:tuberomammillary_nucleus", "relation": "originates_in"},
      {"source": "ntsystem:acetylcholine", "target": "brainregion:basal_forebrain", "relation": "originates_in"},
    ]

    ntsystem_to_circuit_edges = [

      # Dopamine circuits
      {"source": "ntsystem:dopamine", "target": "circuit:mesolimbic_reward", "relation": "modulates"},
      {"source": "ntsystem:dopamine", "target": "circuit:mesocortical", "relation": "modulates"},
      {"source": "ntsystem:dopamine", "target": "circuit:nigrostriatal", "relation": "modulates"},
      {"source": "ntsystem:dopamine", "target": "circuit:tuberoinfundibular", "relation": "modulates"},

      # Threat / mood regulation circuits
      {"source": "ntsystem:serotonin", "target": "circuit:amygdala_pfc", "relation": "modulates"},
      {"source": "ntsystem:norepinephrine", "target": "circuit:amygdala_pfc", "relation": "modulates"},
      {"source": "ntsystem:dopamine", "target": "circuit:amygdala_pfc", "relation": "modulates"},

      {"source": "ntsystem:serotonin", "target": "circuit:hippocampus_pfc", "relation": "modulates"},
      {"source": "ntsystem:dopamine", "target": "circuit:hippocampus_pfc", "relation": "modulates"},

      # Cognitive / control circuits
      {"source": "ntsystem:dopamine", "target": "circuit:frontostriatal", "relation": "modulates"},
      {"source": "ntsystem:norepinephrine", "target": "circuit:frontostriatal", "relation": "modulates"},

      {"source": "ntsystem:acetylcholine", "target": "circuit:thalamocortical", "relation": "modulates"},
      {"source": "ntsystem:serotonin", "target": "circuit:thalamocortical", "relation": "modulates"},

      # Arousal / sleep circuits
      {"source": "ntsystem:norepinephrine", "target": "circuit:locus_coeruleus_arousal", "relation": "modulates"},
      {"source": "ntsystem:histamine", "target": "circuit:corticothalamic_sleep_wake", "relation": "modulates"},
      {"source": "ntsystem:acetylcholine", "target": "circuit:corticothalamic_sleep_wake", "relation": "modulates"},
    ]

    nt_system_to_nt_edges = [
        {"source": "ntsystem:dopamine", "target": "nt:dopamine", "relation": "uses_neurotransmitter"},
        {"source": "ntsystem:serotonin", "target": "nt:serotonin", "relation": "uses_neurotransmitter"},
        {"source": "ntsystem:norepinephrine", "target": "nt:norepinephrine", "relation": "uses_neurotransmitter"},
        {"source": "ntsystem:glutamate", "target": "nt:glutamate", "relation": "uses_neurotransmitter"},
        {"source": "ntsystem:gaba", "target": "nt:gaba", "relation": "uses_neurotransmitter"},
        {"source": "ntsystem:histamine", "target": "nt:histamine", "relation": "uses_neurotransmitter"},
        {"source": "ntsystem:acetylcholine", "target": "nt:acetylcholine", "relation": "uses_neurotransmitter"},
    ]

    rdoc_domain_to_construct_edges = [
      {"source": "rdoc_domain:negative_valence", "target": "rdoc_construct:acute_threat", "relation": "has_construct"},
      {"source": "rdoc_domain:negative_valence", "target": "rdoc_construct:sustained_threat", "relation": "has_construct"},

      {"source": "rdoc_domain:positive_valence", "target": "rdoc_construct:reward_valuation", "relation": "has_construct"},
      {"source": "rdoc_domain:positive_valence", "target": "rdoc_construct:reward_learning", "relation": "has_construct"},
      {"source": "rdoc_domain:positive_valence", "target": "rdoc_construct:reward_responsiveness", "relation": "has_construct"},

      {"source": "rdoc_domain:cognitive", "target": "rdoc_construct:cognitive_control", "relation": "has_construct"},
      {"source": "rdoc_domain:cognitive", "target": "rdoc_construct:working_memory", "relation": "has_construct"},

      {"source": "rdoc_domain:arousal_regulatory", "target": "rdoc_construct:arousal", "relation": "has_construct"},
      {"source": "rdoc_domain:arousal_regulatory", "target": "rdoc_construct:sleep_wake", "relation": "has_construct"},

      {"source": "rdoc_domain:social_processes", "target": "rdoc_construct:affiliation_attachment", "relation": "has_construct"},
    ]

    # -----------------------------
    # Circuit -> RDoC Construct edges
    # -----------------------------
    circuit_to_rdoc_construct_edges = [
      # Threat / fear regulation
      {"source": "circuit:amygdala_pfc", "target": "rdoc_construct:acute_threat", "relation": "underlies"},
      {"source": "circuit:amygdala_pfc", "target": "rdoc_construct:sustained_threat", "relation": "underlies"},

      # Reward / motivation
      {"source": "circuit:mesolimbic_reward", "target": "rdoc_construct:reward_valuation", "relation": "underlies"},
      {"source": "circuit:mesolimbic_reward", "target": "rdoc_construct:reward_responsiveness", "relation": "underlies"},
      {"source": "circuit:mesolimbic_reward", "target": "rdoc_construct:reward_learning", "relation": "underlies"},

      # Cognitive control & executive function
      {"source": "circuit:frontostriatal", "target": "rdoc_construct:cognitive_control", "relation": "underlies"},
      {"source": "circuit:mesocortical", "target": "rdoc_construct:working_memory", "relation": "underlies"},
      {"source": "circuit:thalamocortical", "target": "rdoc_construct:working_memory", "relation": "underlies"},

      # Memory/context regulation
      {"source": "circuit:hippocampus_pfc", "target": "rdoc_construct:cognitive_control", "relation": "underlies"},

      # Arousal / sleep-wake
      {"source": "circuit:locus_coeruleus_arousal", "target": "rdoc_construct:arousal", "relation": "underlies"},
      {"source": "circuit:corticothalamic_sleep_wake", "target": "rdoc_construct:sleep_wake", "relation": "underlies"},

      # Social (kept coarse; you can refine later)
      {"source": "circuit:amygdala_pfc", "target": "rdoc_construct:affiliation_attachment", "relation": "modulates"},
    ]

    rdoc_construct_to_symptom_edges = [
      # Negative valence (threat)
      {"source": "rdoc_construct:acute_threat", "target": "symptom:anxiety", "relation": "dysregulation_manifests_as"},
      {"source": "rdoc_construct:acute_threat", "target": "symptom:panic", "relation": "dysregulation_manifests_as"},
      {"source": "rdoc_construct:acute_threat", "target": "symptom:hypervigilance", "relation": "dysregulation_manifests_as"},
      {"source": "rdoc_construct:acute_threat", "target": "symptom:avoidance", "relation": "dysregulation_manifests_as"},

      {"source": "rdoc_construct:sustained_threat", "target": "symptom:anxiety", "relation": "dysregulation_manifests_as"},
      {"source": "rdoc_construct:sustained_threat", "target": "symptom:hypervigilance", "relation": "dysregulation_manifests_as"},
      {"source": "rdoc_construct:sustained_threat", "target": "symptom:irritability", "relation": "dysregulation_manifests_as"},
      {"source": "rdoc_construct:sustained_threat", "target": "symptom:insomnia", "relation": "dysregulation_manifests_as"},

      # Positive valence (reward)
      {"source": "rdoc_construct:reward_valuation", "target": "symptom:anhedonia", "relation": "dysregulation_manifests_as"},
      {"source": "rdoc_construct:reward_valuation", "target": "symptom:amotivation", "relation": "dysregulation_manifests_as"},

      {"source": "rdoc_construct:reward_responsiveness", "target": "symptom:anhedonia", "relation": "dysregulation_manifests_as"},
      {"source": "rdoc_construct:reward_responsiveness", "target": "symptom:low_energy", "relation": "dysregulation_manifests_as"},

      {"source": "rdoc_construct:reward_learning", "target": "symptom:amotivation", "relation": "dysregulation_manifests_as"},

      # Cognitive systems
      {"source": "rdoc_construct:cognitive_control", "target": "symptom:impulsivity", "relation": "dysregulation_manifests_as"},
      {"source": "rdoc_construct:cognitive_control", "target": "symptom:executive_dysfunction", "relation": "dysregulation_manifests_as"},
      {"source": "rdoc_construct:cognitive_control", "target": "symptom:inattention", "relation": "dysregulation_manifests_as"},

      {"source": "rdoc_construct:working_memory", "target": "symptom:poor_working_memory", "relation": "dysregulation_manifests_as"},
      {"source": "rdoc_construct:working_memory", "target": "symptom:inattention", "relation": "dysregulation_manifests_as"},

      # Arousal / regulatory
      {"source": "rdoc_construct:arousal", "target": "symptom:hypervigilance", "relation": "dysregulation_manifests_as"},
      {"source": "rdoc_construct:arousal", "target": "symptom:insomnia", "relation": "dysregulation_manifests_as"},
      {"source": "rdoc_construct:arousal", "target": "symptom:irritability", "relation": "dysregulation_manifests_as"},

      {"source": "rdoc_construct:sleep_wake", "target": "symptom:insomnia", "relation": "dysregulation_manifests_as"},
      {"source": "rdoc_construct:sleep_wake", "target": "symptom:hypersomnia", "relation": "dysregulation_manifests_as"},

      # Social processes
      {"source": "rdoc_construct:affiliation_attachment", "target": "symptom:social_withdrawal", "relation": "dysregulation_manifests_as"},
      {"source": "rdoc_construct:affiliation_attachment", "target": "symptom:blunted_affect", "relation": "dysregulation_manifests_as"},
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
        bp_to_circuit_edges,
        brainregion_nodes,
        brainregion_to_circuit_edges,
        cc_nodes,
        cc_to_bp_edges,
        circuit_nodes,
        circuit_to_rdoc_construct_edges,
        edges,
        format_neuro_paths,
        mf_to_bp_edges,
        neurotransmitter_nodes,
        nodes,
        nt_system_to_nt_edges,
        ntsystem_nodes,
        ntsystem_to_circuit_edges,
        pathway_nodes,
        pathway_to_bp_edges,
        protein_to_cc_edges,
        rdoc_construct_to_symptom_edges,
        rdoc_domain_to_construct_edges,
        rdoc_nodes,
        symptom_nodes,
    )


@app.cell
def _(
    bp_to_circuit_edges,
    brainregion_nodes,
    brainregion_to_circuit_edges,
    cc_nodes,
    cc_to_bp_edges,
    circuit_nodes,
    circuit_to_rdoc_construct_edges,
    edges,
    mf_to_bp_edges,
    neurotransmitter_nodes,
    nodes,
    nt_system_to_nt_edges,
    ntsystem_nodes,
    ntsystem_to_circuit_edges,
    pathway_nodes,
    pathway_to_bp_edges,
    protein_to_cc_edges,
    rdoc_construct_to_symptom_edges,
    rdoc_domain_to_construct_edges,
    rdoc_nodes,
    symptom_nodes,
):
    nodes.extend(cc_nodes)
    nodes.extend(pathway_nodes)
    nodes.extend(circuit_nodes)
    nodes.extend(brainregion_nodes)
    nodes.extend(ntsystem_nodes)
    nodes.extend(neurotransmitter_nodes)
    nodes.extend(brainregion_nodes)
    nodes.extend(rdoc_nodes)
    nodes.extend(symptom_nodes)

    edges.extend(protein_to_cc_edges)
    edges.extend(cc_to_bp_edges)
    edges.extend(mf_to_bp_edges)
    edges.extend(pathway_to_bp_edges)
    edges.extend(bp_to_circuit_edges)
    edges.extend(brainregion_to_circuit_edges)
    edges.extend(nt_system_to_nt_edges)
    edges.extend(ntsystem_to_circuit_edges)
    edges.extend(rdoc_domain_to_construct_edges)
    edges.extend(circuit_to_rdoc_construct_edges)
    edges.extend(rdoc_construct_to_symptom_edges)
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
    visualize_interactive_graph(graph_V3)
    return (graph_V3,)


@app.cell
def _(find_all_paths_between, format_neuro_paths, graph_V3):
    brexi_insomnia_paths = find_all_paths_between(graph_V3,'drug:brexpiprazole','symptom:insomnia',max_hops=9)
    all_paths = format_neuro_paths(brexi_insomnia_paths)
    return (all_paths,)


@app.cell
def _(all_paths):
    for i in all_paths:
        print(i)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
