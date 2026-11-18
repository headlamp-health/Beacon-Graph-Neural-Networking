import marimo

__generated_with = "0.19.7"
app = marimo.App(width="medium")


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
    import math
    return Network, json, math, mo, nx


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
        'Protein_V1': '#fd7e14',    # Orange
        'MolecularFunction': '#28a745',   # Green
        'CellularComponent': '#e83e8c',      # Pink
        'BP': '#6f42c1',     # Purple
        'vNode':'#a4ac86',         # Olive Green
        'Pathway':'#a4ac86', # Olive Green
        'Circuit':'#dc3545', # Red
        'Brain_Region':'#20c997', #Teal
        'NeurotransmitterSystem':'#ffc107', # Amber
        'Neurotransmitter':'#ffb300', #Slight amber
        'Rdoc_domain':'#d5b8dc', #
        'Rdoc_construct':'#b69dd6',
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
            raw_type = data.get('Type', 'unknown')
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
                      'CellularComponent':3, 'Protein_V1':4, 'Pathway':4, 'BP':5,
                      'vNode':6,'Neurotransmitter':7,'NeurotransmitterSystem': 8, 'Circuit':9, 
                      'Brain_Region': 10, 'Rdoc_domain': 12, 
                      'Rdoc_construct':11, 'Symptom':13
                     }

        for node_id, data in G.nodes(data=True):
            # Assign the 'subset' for the layout logic
            node_type = data.get('Type', 'Unknown')
            node_label = data.get('name','Unknown')
            G.nodes[node_id]['subset'] = type_order.get(node_type, 3) 

            # Standard Pyvis formatting
            G.nodes[node_id]['name'] = str(node_id)
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
    return (
        KG_COLOR_PALETTE,
        add_edges_from_list,
        apply_kg_colors,
        build_graph_from_node_list,
        visualize_interactive_graph,
    )


@app.cell
def _(json):
    # Read nodes JSON
    # Replace 'your_data.json' with your actual file path
    # Define file pairs to process

    files = {
        'nodes': ['Arpiprazole_merged_graph_V8_nodes.json'],
        'edges': ['Arpiprazole_merged_graph_V7_edges.json']
    }

    def load_and_merge(file_list):
        with open(file_list[0], 'r') as f:
            base_data = json.load(f)

        #with open(file_list[1], 'r') as f:
            # extend() modifies base_data in-place, avoiding a third list allocation
        #    base_data.extend(json.load(f))

        return base_data

    nodes_data_master = load_and_merge(files['nodes'])
    edges_data_master = load_and_merge(files['edges'])
    return edges_data_master, nodes_data_master


@app.cell
def _(nodes_data_master):
    len(nodes_data_master)
    return


@app.cell
def _(nodes_data_master):
    j = []

    for i in nodes_data_master: 
        #print(i)
        if i['category'] not in j: 
            j.append(i['category'])

    for i in j: 
        print(i)
        print('-------')
    #print(j)
    return


@app.cell
def _(edges_data_master):
    for i_10 in edges_data_master: 
        if i_10['subject'] in ['GO:0060160','GO:0060158','GO:0051586','GO:0098664','GO:0007210','GO:0007208','GO:0042428','GO:0014062']:
            print(i_10)
            print('----------')
    return


@app.cell
def _(nodes_data_master):
    protein = []
    protein_V1 = []
    drug = []
    pathway = []
    BP = []

    circuit = []
    brain_region = []
    rdoc_construct = []
    rdoc_domain = []
    symptoms = []

    for i_1 in nodes_data_master: 
        if 'biolink:Gene' in i_1['category']: 
            #drug = i_1
            #print(i_1)
            i_1['Type'] = 'Protein'
            protein.append(i_1)
        elif 'biolink:Protein' in i_1['category']:
            i_1['Type'] = 'Protein_V1'
            protein_V1.append(i_1)
        elif 'biolink:drug' in i_1['category']: 
            i_1['Type'] = 'Drug'
            drug.append(i_1)
        elif 'biolink:Pathway' in i_1['category'] and i_1['id'] in ['Reactome:R-HSA-390651','Reactome:R-HSA-390666','Reactome:R-HSA-416476']: 
            i_1['Type'] = 'Pathway'
            pathway.append(i_1)
        elif 'biolink:BiologicalProcess' in i_1['category'] and i_1['id'] in ["GO:0004930","GO:0001591","GO:0001965","GO:0004952","GO:0005102","GO:0015459","GO:0032795","GO:0035240","GO:0035255","GO:0042802"
    ,"GO:0044877","GO:0060160","GO:0060158","GO:0051586","GO:0098664","GO:0007210","GO:0007208","GO:0042428","GO:0014062"]: 
            i_1['Type'] = 'BP'
            BP.append(i_1)
        elif i_1['id'].startswith('CIRCUIT:'):
            i_1['Type'] = 'Circuit'
            circuit.append(i_1)
        elif i_1['id'].startswith('UBERON:') and i_1['id'] in ['UBERON:0002043','UBERON:0001870','UBERON:0001876','UBERON:0002421','UBERON:0002435']:
            i_1['Type'] = 'Brain_Region'
            brain_region.append(i_1)
        elif i_1['id'].startswith('RDOC_CONSTRUCT:'): 
            i_1['Type'] = 'Rdoc_construct'
            rdoc_construct.append(i_1)
        elif i_1['id'].startswith('RDOC_DOMAIN:'): 
            i_1['Type'] = 'Rdoc_domain'
            rdoc_domain.append(i_1)
        elif i_1['id'].startswith('MONDO:'): 
            i_1['Type'] = 'Symptom'
            symptoms.append(i_1)



    print(drug)
    print(protein)
    print(protein_V1)
    print(pathway)
    print(BP)
    print(circuit)
    print(brain_region)
    print(rdoc_construct)
    print(rdoc_domain)
    print(symptoms)
    return (
        BP,
        brain_region,
        circuit,
        drug,
        pathway,
        protein,
        protein_V1,
        rdoc_construct,
        rdoc_domain,
        symptoms,
    )


@app.cell
def _(
    BP,
    brain_region,
    circuit,
    edges_data_master,
    pathway,
    protein,
    protein_V1,
    rdoc_construct,
    rdoc_domain,
    symptoms,
):
    protein_ids = [i['id'] for i in protein]
    protein_V1_ids = [i['id'] for i in protein_V1]
    pathway_ids = [i['id'] for i in pathway]
    bp_ids = [i['id'] for i in BP]
    circuit_ids = [i['id'] for i in circuit]
    brain_region_ids = [i['id'] for i in brain_region]
    rdoc_construct_ids = [i['id'] for i in rdoc_construct]
    rdoc_domain_ids = [i['id'] for i in rdoc_domain]
    symptom_ids = [i['id'] for i in symptoms]

    #matching_edges = [edge for edge in edges_data_master if edge['source'] in protein_ids]

    for i_4 in edges_data_master: 
        #if i_4['subject'] in brain_region_ids and i_4['object'] in rdoc_construct_ids:
        if i_4['subject'] in ['KEGG:hsa04082']:
            print(i_4)
    return


@app.cell
def _(nodes_data_master):
    for i_8 in nodes_data_master: 
        if i_8['id'] == 'KEGG:hsa04082': 
            print(i_8)
    return


@app.cell
def _(nodes_data_master):
    for i_16 in nodes_data_master: 
        if i_16['id'] == 'GO:0060160': 
            print(i_16)
    return


@app.cell
def _():
    ## Edges

    ##################################################### Layer 1 ##########################################################
    ## 1. Drug --> Receptor (Using Hill Equation at 6nM)
    # Result of: Scaling * (6 / (6 + Ki))
    weight_drug_protien_DRD2 = 0.71 * (6/(6+2.5))
    weight_drug_protien_HTR2A = 0.38 * (6/(6+10))
    weight_drug_protien_HTR1A = 0.43 * (6/(6+8))


    drug_to_protein_edges = [
        {"source": "drug:aripiprazole", "target": "HGNC:5293", "relation": "antagonist", "weight":weight_drug_protien_HTR2A},
        {"source": "drug:aripiprazole", "target": "HGNC:5286", "relation": "partial_agonist_of", "weight":weight_drug_protien_HTR1A}, 
        {"source": "drug:aripiprazole", "target": "HGNC:3023", "relation": "partial_agonist_of", "weight":weight_drug_protien_DRD2}
    ]

    ############################################## Layer 2: Receptor --> Pathway ###########################################
    Agonist = 1
    Partial_agonist = 0.5
    Antagonist = 0.0
    inverse_antagonist = -0.5

    # Intrensic Activity * Coupling Efficiency
    weight_drd2_to_dopamine_recpt = Partial_agonist * 0.80
    weight_htr2a_to_serotonin_recpt = Antagonist * 0.85
    weight_htr2a_to_g_alpha_signal_recpt = Partial_agonist * 0.85
    weight_htr1a_to_serotonin_recpt = Partial_agonist * 0.85

    receptor_to_pathway = [
        {"source": "HGNC:3023", "target": "Reactome:R-HSA-390651", "relation": "Transduction", "weight":weight_drd2_to_dopamine_recpt},
        {"source": "HGNC:5293", "target": "Reactome:R-HSA-390666", "relation": "Transduction", "weight":weight_htr2a_to_serotonin_recpt}, 
        {"source": "HGNC:5293", "target": "Reactome:R-HSA-416476", "relation": "Transduction", "weight":weight_htr2a_to_g_alpha_signal_recpt}, 
        {"source": "HGNC:5286", "target": "Reactome:R-HSA-390666", "relation": "Transduction", "weight":weight_htr1a_to_serotonin_recpt} 
    ]

    ############################################## Layer 2_1: Receptor --> Protein V1 ###########################################

    receptor_to_protein_v1 = [{"source": "HGNC:3023","target": "UniProtKB:P14416", "relation":"has gene product","weight":1}]


    ################################################### Layer 3: Pathway --> Biological Process #########################################
    weight_dopamine_to_bp_0060160 = 3.0 #Source:Gemini #Paper: 
    weight_dopamine_to_bp_0060158 = 2.5 #Source:Gemini
    weight_dopamine_to_bp_0051586 = 1.5 #Source:Gemini
    weight_serotonin_to_bp_0098664 = 2.0 #Source:Gemini
    weight_serotonin_to_bp_0007210 = 4.5 #Source:Gemini
    weight_serotonin_to_bp_0007208 = 4.5 #Source:Gemini
    weight_serotonin_to_bp_0042428 = 1.1 #Source:Gemini
    weight_serotonin_to_bp_0014062 = 3.5 #Source:Gemini


    pathway_to_bp = [
        {"source":"Reactome:R-HSA-390651","target":"GO:0060160","relation":"","weight":weight_dopamine_to_bp_0060160},
        {"source":"Reactome:R-HSA-390651","target":"GO:0060158","relation":"","weight":weight_dopamine_to_bp_0060158}, 
        {"source":"Reactome:R-HSA-390651","target":"GO:0051586","relation":"","weight":weight_dopamine_to_bp_0051586},
        {"source":"Reactome:R-HSA-390666","target":"GO:0098664","relation":"","weight":weight_serotonin_to_bp_0098664},
        {"source":"Reactome:R-HSA-390666","target":"GO:0007210","relation":"","weight":weight_serotonin_to_bp_0007210},
        {"source":"Reactome:R-HSA-390666","target":"GO:0007208","relation":"","weight":weight_serotonin_to_bp_0007208},
        {"source":"Reactome:R-HSA-390666","target":"GO:0042428","relation":"","weight":weight_serotonin_to_bp_0042428},
        {"source":"Reactome:R-HSA-390666","target":"GO:0014062","relation":"","weight":weight_serotonin_to_bp_0014062}    
    ]


    ############################################### Layer 3_1: Protein_V1 --> Biological Process ########################################

    protein_V1_to_BP = [
        {"source":"UniProtKB:P14416","target":"GO:0004930","relation":"","weight":1},
        {"source":"UniProtKB:P14416","target":"GO:0001591","relation":"","weight":1}, 
        {"source":"UniProtKB:P14416","target":"GO:0001965","relation":"","weight":1}, 
        {"source":"UniProtKB:P14416","target":"GO:0004952","relation":"","weight":1}, 
        {"source":"UniProtKB:P14416","target":"GO:0005102","relation":"","weight":1}, 
        {"source":"UniProtKB:P14416","target":"GO:0015459","relation":"","weight":1}, 
        {"source":"UniProtKB:P14416","target":"GO:0032795","relation":"","weight":1}, 
        {"source":"UniProtKB:P14416","target":"GO:0035240","relation":"","weight":1}, 
        {"source":"UniProtKB:P14416","target":"GO:0035255","relation":"","weight":1}, 
        {"source":"UniProtKB:P14416","target":"GO:0042802","relation":"","weight":1}, 
        {"source":"UniProtKB:P14416","target":"GO:0044877","relation":"","weight":1}    
    ]

    ["GO:0004930","GO:0001591","GO:0001965","GO:0004952","GO:0005102","GO:0015459","GO:0032795","GO:0035240","GO:0035255","GO:0042802"
    ,"GO:0044877","GO:0060160","GO:0060158","GO:0051586","GO:0098664","GO:0007210","GO:0007208","GO:0042428"]

    ##################################################### Layer 4: Virtual Nodes ############################################

    ## Virtual Nodes (vNodes) 
    # These represent the functional integration points in the brain
    virtual_circuit_nodes = [
        {"id": "vCIRCUIT:raphe_prefrontal","name":"Raphe-prefrontal serotonergic pathway virtual node","description":"Serotonergic projection from dorsal raphe nucleus to prefrontal cortex. Modulates mood, impulse control, and cognitive flexibility.","Type":"vNode"},
        {"id": "vCIRCUIT:raphe_limbic","name":"Raphe-limbic serotonergic pathway","description":"Serotonergic projection from raphe nuclei to amygdala, hippocampus, and other limbic structures. Modulates anxiety, fear, and emotional memory.","Type":"vNode"},
        {"id": "vCIRCUIT:raphe_striatal","name":"Raphe-striatal serotonergic pathway","description":"Serotonergic projection from dorsal raphe to basal ganglia. Modulates motor activity and opposes dopaminergic transmission in the striatum.","Type":"vNode"}
    ]


    bp_to_virtual_circuit_nodes = [
        {"source": "GO:0007210", "target": "vCIRCUIT:raphe_prefrontal", "relation": "contributes_to","weight":1.0,"modulation":"sigmoid"},
        {"source": "GO:0007210", "target": "vCIRCUIT:raphe_limbic", "relation": "contributes_to","weight":1.0,"modulation":"sigmoid"},
        {"source": "GO:0007210", "target": "vCIRCUIT:raphe_striatal", "relation": "contributes_to","weight":1.0, "modulation":"sigmoid"}
    ]

    ################################################# Layer 5: Circuit nodes #########################################

    ## Layer 5: Virtual Node --> Circuit
    # The weight of 1.0 means the Circuit carries the full integrated signal.
    # The 'modulation' key tells your propagator to apply sigmoid() here.

    virtaul_circuit_node_to_circuit_edges = [
        {"source": "vCIRCUIT:raphe_prefrontal", "target": "CIRCUIT:raphe_prefrontal", "relation": "biolink:occurs_in", "weight": 1.0},
        {"source": "vCIRCUIT:raphe_limbic", "target": "CIRCUIT:raphe_limbic", "relation": "biolink:occurs_in", "weight": 1.0},
        {"source": "vCIRCUIT:raphe_striatal", "target": "CIRCUIT:raphe_striatal", "relation": "biolink:occurs_in", "weight": 1.0}
    ]

    ############################################### Layer 6: Brain Region nodes #########################################

    # --- Regional Sensitivity Constants (Lambda) ---
    # Lambda(λ) represents how much a specific region "cares" about the signal coming from that circuit

    LAMBDA_CONFIG = {
        "UBERON:0001870": 0.75,  # Frontal Cortex (Executive/Cognitive)
        "UBERON:0001876": 0.80,  # Amygdala (Emotional/Fear)
        "UBERON:0002421": 0.80,  # Hippocampal Formation (Memory/Context)
        "UBERON:0002435": 0.65,  # Striatum (Motor/Habit)
        "UBERON:0002043": 0.95   # Dorsal Raphe Nucleus (Autoregulation/Feedback)
    }

    ## Layer 6: Circuit --> Brain Region
    circuit_to_anatomy_edges = [
        {"source": "CIRCUIT:raphe_prefrontal", "target": "UBERON:0001870", "relation": "biolink:has_part", 
         "weight": LAMBDA_CONFIG["UBERON:0001870"]},
        {"source": "CIRCUIT:raphe_prefrontal", "target": "UBERON:0002043", "relation": "biolink:has_part", 
         "weight": LAMBDA_CONFIG["UBERON:0002043"]},
        {"source": "CIRCUIT:raphe_limbic", "target": "UBERON:0001876", "relation": "biolink:has_part", 
         "weight": LAMBDA_CONFIG["UBERON:0001876"]},
        {"source": "CIRCUIT:raphe_limbic", "target": "UBERON:0002421", "relation": "biolink:has_part", 
         "weight": LAMBDA_CONFIG["UBERON:0002421"]},
        {"source": "CIRCUIT:raphe_limbic", "target": "UBERON:0002043", "relation": "biolink:has_part", 
         "weight": LAMBDA_CONFIG["UBERON:0002043"]},
        {"source": "CIRCUIT:raphe_striatal", "target": "UBERON:0002435", "relation": "biolink:has_part", 
         "weight": LAMBDA_CONFIG["UBERON:0002435"]},
        {"source": "CIRCUIT:raphe_striatal", "target": "UBERON:0002043", "relation": "biolink:has_part", 
         "weight": LAMBDA_CONFIG["UBERON:0002043"]}
    ]

    ## Layer 7 & 8: Rdoc_Domain to Rdoc_Construct

    rdoc_construct_to_domain_edges = [
        # Arousal and Regulatory Systems
        {"source": "RDOC_CONSTRUCT:arousal", "target": "RDOC_DOMAIN:rdoc_domain:arousal_regulatory", "relation": "biolink:subclass_of", "weight": 1.0},
        # Cognitive Systems
        {"source": "RDOC_CONSTRUCT:attention", "target": "RDOC_DOMAIN:rdoc_domain:cognitive", "relation": "biolink:subclass_of", "weight": 1.0},
        {"source": "RDOC_CONSTRUCT:cognitive_control", "target": "RDOC_DOMAIN:rdoc_domain:cognitive", "relation": "biolink:subclass_of", "weight": 1.0},
        {"source": "RDOC_CONSTRUCT:declarative_memory", "target": "RDOC_DOMAIN:rdoc_domain:cognitive", "relation": "biolink:subclass_of", "weight": 1.0},
        {"source": "RDOC_CONSTRUCT:working_memory", "target": "RDOC_DOMAIN:rdoc_domain:cognitive", "relation": "biolink:subclass_of", "weight": 1.0},
        # Positive Valence Systems
        {"source": "RDOC_CONSTRUCT:effort_valuation", "target": "RDOC_DOMAIN:rdoc_domain:positive_valence", "relation": "biolink:subclass_of", "weight": 1.0},
        {"source": "RDOC_CONSTRUCT:expectancy", "target": "RDOC_DOMAIN:rdoc_domain:positive_valence", "relation": "biolink:subclass_of", "weight": 1.0},
        {"source": "RDOC_CONSTRUCT:initial_responsiveness", "target": "RDOC_DOMAIN:rdoc_domain:positive_valence", "relation": "biolink:subclass_of", "weight": 1.0},
        {"source": "RDOC_CONSTRUCT:reward_learning", "target": "RDOC_DOMAIN:rdoc_domain:positive_valence", "relation": "biolink:subclass_of", "weight": 1.0},
        {"source": "RDOC_CONSTRUCT:reward_responsiveness", "target": "RDOC_DOMAIN:rdoc_domain:positive_valence", "relation": "biolink:subclass_of", "weight": 1.0},
        {"source": "RDOC_CONSTRUCT:reward_valuation", "target": "RDOC_DOMAIN:rdoc_domain:positive_valence", "relation": "biolink:subclass_of", "weight": 1.0},
        # Sensorimotor Systems
        {"source": "RDOC_CONSTRUCT:habit", "target": "RDOC_DOMAIN:rdoc_domain:sensorimotor", "relation": "biolink:subclass_of", "weight": 1.0},
        {"source": "RDOC_CONSTRUCT:innate_motor_patterns", "target": "RDOC_DOMAIN:rdoc_domain:sensorimotor", "relation": "biolink:subclass_of", "weight": 1.0},
        {"source": "RDOC_CONSTRUCT:motor_actions", "target": "RDOC_DOMAIN:rdoc_domain:sensorimotor", "relation": "biolink:subclass_of", "weight": 1.0}
    ]

    ## Layer 10: Brain Region to Symptom
    # These define the clinical impact based on regional functional states.
    ## Layer 9: Brain Region --> Clinical Outcome (MONDO)
    # Initial Pass: Weights set to 1.0 to monitor direct flow propagation.
    region_to_disease_edges = [
        # Schizophrenia (MONDO:0005090)
        {"source": "UBERON:0002421", "target": "MONDO:0005090", "relation": "biolink:associated_with", "weight": 1.0},
        {"source": "UBERON:0001876", "target": "MONDO:0005090", "relation": "biolink:associated_with", "weight": 1.0},
        {"source": "UBERON:0001870", "target": "MONDO:0005090", "relation": "biolink:associated_with", "weight": 1.0},
        # Bipolar Disorder (MONDO:0004985)
        {"source": "UBERON:0002421", "target": "MONDO:0004985", "relation": "biolink:associated_with", "weight": 1.0},
        {"source": "UBERON:0001876", "target": "MONDO:0004985", "relation": "biolink:associated_with", "weight": 1.0},
        # Depressive Disorder (MONDO:0002050)
        {"source": "UBERON:0002421", "target": "MONDO:0002050", "relation": "biolink:associated_with", "weight": 1.0},
        {"source": "UBERON:0001876", "target": "MONDO:0002050", "relation": "biolink:associated_with", "weight": 1.0},
        {"source": "UBERON:0001870", "target": "MONDO:0002050", "relation": "biolink:associated_with", "weight": 1.0},
        # ADHD (MONDO:0007743)
        {"source": "UBERON:0001870", "target": "MONDO:0007743", "relation": "biolink:associated_with", "weight": 1.0},
        # Motor/Striatal Disorders (Nigrostriatal Circuit)
        {"source": "UBERON:0002435", "target": "MONDO:0005180", "relation": "biolink:associated_with", "weight": 1.0}, # Parkinson
        {"source": "UBERON:0002435", "target": "MONDO:0001609", "relation": "biolink:associated_with", "weight": 1.0}, # Tardive Dyskinesia
        # Anxiety Disorders (MONDO:0005618)
        {"source": "UBERON:0002043", "target": "MONDO:0005618", "relation": "biolink:associated_with", "weight": 1.0},
        {"source": "UBERON:0001876", "target": "MONDO:0005618", "relation": "biolink:associated_with", "weight": 1.0}
    ]
    return (
        bp_to_virtual_circuit_nodes,
        circuit_to_anatomy_edges,
        drug_to_protein_edges,
        pathway_to_bp,
        receptor_to_pathway,
        region_to_disease_edges,
        virtaul_circuit_node_to_circuit_edges,
        virtual_circuit_nodes,
    )


@app.cell
def _(BP):
    [i['id'] for i in BP]
    return


@app.cell
def _(BP, edges_data_master):
    for i_9 in edges_data_master: 
        if i_9['subject'] in [i['id'] for i in BP]:
       #if i_9['object'] in symptom_ids and i_9['subject'] in #['UBERON:0002043','UBERON:0001870','UBERON:0001876','UBERON:0002421','UBERON:0002435']:
            print(i_9)
    return


@app.cell
def _(
    BP,
    bp_to_virtual_circuit_nodes,
    brain_region,
    circuit,
    circuit_to_anatomy_edges,
    drug,
    drug_to_protein_edges,
    pathway,
    pathway_to_bp,
    protein,
    receptor_to_pathway,
    region_to_disease_edges,
    symptoms,
    virtaul_circuit_node_to_circuit_edges,
    virtual_circuit_nodes,
):
    nodes_for_graph = []
    nodes_for_graph.extend(drug)
    nodes_for_graph.extend(protein)
    #nodes_for_graph.extend(protein_V1) # Added the protein V1 actually the above protein is gene. 
    nodes_for_graph.extend(pathway)
    nodes_for_graph.extend(BP)
    nodes_for_graph.extend(virtual_circuit_nodes)
    nodes_for_graph.extend(circuit)
    nodes_for_graph.extend(brain_region)
    #nodes_for_graph.extend(rdoc_domain)
    #nodes_for_graph.extend(rdoc_construct)
    nodes_for_graph.extend(symptoms)


    edges_for_graph = []
    edges_for_graph.extend(drug_to_protein_edges)
    #edges_for_graph.extend(receptor_to_protein_v1) # Added new protein provided the above protein are actually gene. 
    #edges_for_graph.extend(protein_V1_to_BP) # Added a new proteint provided the above protein are actually genes. 
    edges_for_graph.extend(receptor_to_pathway)
    edges_for_graph.extend(pathway_to_bp)
    edges_for_graph.extend(bp_to_virtual_circuit_nodes)
    edges_for_graph.extend(virtaul_circuit_node_to_circuit_edges)
    edges_for_graph.extend(circuit_to_anatomy_edges)
    #edges_for_graph.extend(rdoc_construct_to_domain_edges)
    edges_for_graph.extend(region_to_disease_edges)
    return edges_for_graph, nodes_for_graph


@app.cell
def _(nx):
    class BioGraphSystem:
        def __init__(self):
            self.G = nx.DiGraph()
            # Define the global weights for relationship types
            self.weight_rules = {
                "drug_to_receptor": 1.00,
                "receptor_to_pathway": 1.00,
                "pathway_to_process": 1.00
            }

        def build_layer(self, source_list, target_list, rel_type):
            """
            Connects two entire layers based on a relationship type.
            You can pass filtered lists here.
            """
            weight = self.weight_rules.get(rel_type, 1.0)

            for s in source_list:
                for t in target_list:
                    # In a real scenario, you'd check a condition here 
                    # e.g., if s interacts with t
                    self.G.add_edge(s, t, type=rel_type, weight=weight)

        def update_weight(self, rel_type, new_weight):
            """Update weights for a specific relationship type across the graph."""
            self.weight_rules[rel_type] = new_weight
            for u, v, d in self.G.edges(data=True):
                if d['type'] == rel_type:
                    self.G[u][v]['weight'] = new_weight
    return


@app.cell
def _(
    KG_COLOR_PALETTE,
    add_edges_from_list,
    apply_kg_colors,
    build_graph_from_node_list,
    edges_for_graph,
    nodes_for_graph,
    nx,
    visualize_interactive_graph,
):
    # Shows the complete graph
    # Step 1: Initialize graph
    graph_V0 = nx.DiGraph()

    # Step 2: Add nodes to the graph 
    graph_V1 = build_graph_from_node_list(graph_V0,nodes_for_graph)

    # Step 3: Add edges to the graph
    graph_V2 = add_edges_from_list(graph_V1,edges_for_graph)

    #Step 4: Visualize the graph
    graph_V3 = apply_kg_colors(graph_V2,KG_COLOR_PALETTE)
    visualize_interactive_graph(graph_V3,filename="complete_graph_V2.html")
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Flow Logic
    """)
    return


@app.cell
def _(math):
    def propagate_fluid_to_proteins(input_volume, edges):
        protein_signals = {}
    
        for edge in edges:
            target = edge["target"]
            # The engine simply GRABS the weight you already calculated
            edge_weight = edge["weight"] 
        
            # Calculation: Fluid Volume * Pre-set Valve Size
            protein_signals[target] = input_volume * edge_weight
        
        return protein_signals

    def validate_edge_flow(source, target, weight, input_vol):
        flow_reached = input_vol * weight
        return {
            "path": f"{source} -> {target}",
            "precalculated_weight": round(weight, 4),
            "actual_flow_reached": round(flow_reached, 4),
            "check": "VALID" if flow_reached == weight else "ERROR: Flow calculation mismatch"
        }

    def get_node_name(node_id, node_master):
        """Looks up the ID in the master list and returns the human-readable name."""
        for node in node_master:
            if node["id"] == node_id:
                return node["name"]
        return node_id # Fallback to ID if name not found

    def propagate_with_names(input_volume, edges, node_master):
        flow_report = []
    
        for edge in edges:
            # 1. Get the Names for the report
            source_name = get_node_name(edge["source"], node_master)
            target_name = get_node_name(edge["target"], node_master)
        
            # 2. Perform the Logic
            weight = edge["weight"]
            actual_flow = input_volume * weight
        
            # 3. Store the result in a readable format
            flow_report.append({
                "from": source_name,
                "to": target_name,
                "id_path": f"{edge['source']} -> {edge['target']}",
                "weight": round(weight, 4),
                "flow_received": round(actual_flow, 4)
            })
        return flow_report

    def validate_named_flow(report):
        print(f"{'PATH':<30} | {'WEIGHT':<10} | {'RESULT':<10}")
        print("-" * 55)
        for entry in report:
            path_str = f"{entry['from']} -> {entry['to']}"
            print(f"{path_str:<30} | {entry['weight']:<10} | {entry['flow_received']:<10}")

    def propagate_generic_layer(input_state, edges, node_master):
        """
        input_state: {node_id: fluid_volume}
        edges: list of edge dicts
        node_master: list of node dicts for naming
        """
        new_state = {}
        detailed_report = []

        for edge in edges:
            source_id = edge["source"]
            target_id = edge["target"]
            weight = edge["weight"]

            # 1. Get fluid from source
            incoming = input_state.get(source_id, 0)
        
            # 2. Logic: Fluid * Valve (Weight)
            flow_out = incoming * weight

            # 3. Accumulate math state
            new_state[target_id] = new_state.get(target_id, 0) + flow_out

            # 4. Generate human-readable names for the report
            source_name = next((n['name'] for n in node_master if n['id'] == source_id), source_id)
            target_name = next((n['name'] for n in node_master if n['id'] == target_id), target_id)

            # 5. Log the transaction
            detailed_report.append({
                "from": source_name,
                "to": target_name,
                "weight": round(weight, 4),
                "input": round(incoming, 4),
                "output": round(flow_out, 4)
            })
            
        return new_state, detailed_report

    def validate_l2_flow(report):
        print(f"{'PROTEIN (Source)':<15} | {'PATHWAY (Target)':<25} | {'HANDSHAKE':<10} | {'RESULT'}")
        print("-" * 75)
        for entry in report:
            print(f"{entry['from']:<15} | {entry['to']:<25} | {entry['handshake_weight']:<10} | {entry['output_to_pathway']}")

    ## Propagate to Virtual Circuit Nodes, sigmoid modulation
    def sigmoid(x, k=1.0, x0=0.0):
        """The Sigmoid 'Safety Valve' function."""
        return 1 / (1 + math.exp(-k * (x - x0)))

    def propagate_to_vCN(bp_results, bp_to_vcn_edges, node_master):
        """
        bp_results: {'BP_ID': 2.45}
        bp_to_vcn_edges: list of edges
        node_master: lookup table
        """
        new_state = {}
        detailed_report = []

        # 1. First, calculate the Raw Sums for each vCN (to apply Sigmoid correctly)
        raw_sums = {}
        for edge in bp_to_vcn_edges:
            source_id = edge["source"]
            target_id = edge["target"]
            weight = edge["weight"]
            incoming = bp_results.get(source_id, 0)
            raw_sums[target_id] = raw_sums.get(target_id, 0) + (incoming * weight)

        # 2. Now, generate the report with the standardized keys
        for edge in bp_to_vcn_edges:
            source_id = edge["source"]
            target_id = edge["target"]
            weight = edge["weight"]
        
            # Get Names
            source_name = next((n['name'] for n in node_master if n['id'] == source_id), source_id)
            target_name = next((n['name'] for n in node_master if n['id'] == target_id), target_id)
        
            # Get the input from the BP
            incoming_fluid = bp_results.get(source_id, 0)
        
            # The 'Output' here is the FINAL state of the vCN after modulation
            # We use the raw_sum for that specific target vCN
            final_modulated_output = sigmoid(raw_sums[target_id], k=1.5, x0=0.5)
        
            # Add to the final state dictionary (The Math Engine)
            new_state[target_id] = final_modulated_output

            # The Standardized Report
            detailed_report.append({
                "from": source_name,
                "to": target_name,
                "weight": round(weight, 4),
                "input": round(incoming_fluid, 4),
                "output": round(final_modulated_output, 4) # The 'Result' of the handshake
            })
            
        return new_state, detailed_report
    ## End of sigmoid modulation
    return (
        propagate_generic_layer,
        propagate_to_vCN,
        propagate_with_names,
        validate_named_flow,
    )


@app.cell
def _(
    bp_to_virtual_circuit_nodes,
    circuit_to_anatomy_edges,
    drug_to_protein_edges,
    nodes_data_master,
    pathway_to_bp,
    propagate_generic_layer,
    propagate_to_vCN,
    propagate_with_names,
    protein,
    receptor_to_pathway,
    region_to_disease_edges,
    validate_named_flow,
    virtaul_circuit_node_to_circuit_edges,
):
    ############################################### Step 1: Drug to Protein #####################################################
    input_unit = 1.0
    current_flow = propagate_with_names(input_unit, drug_to_protein_edges, nodes_data_master)
    # Show the results
    report_l1 = validate_named_flow(current_flow)
    #print(report_l1)

    print('------------------------------------------------------------------------------------------')

    ################################################ Step 2: Protein to Pathway ################################################
    # --- EXECUTION ---
    # Using the results from our previous Layer 1 (0.501 reached DRD2)
    # 1. Create a quick lookup for protein names to IDs
    name_to_id = {p['name']: p['id'] for p in protein}

    # 2. Map the flow directly using the lookup
    layer_1_results = {
        name_to_id[flow['to']]: flow['flow_received'] 
        for flow in current_flow 
        if flow['to'] in name_to_id
    }

    layer_2_results, report_l2 = propagate_generic_layer(layer_1_results, receptor_to_pathway, nodes_data_master)

    print(f"{'FROM':<15} | {'TO':<35} | {'WEIGHT':<10} | {'OUT'}")
    print("-" * 75)
    for entry in report_l2:
        print(f"{entry['from']:<15} | {entry['to']:<35} | {entry['weight']:<10} | {entry['output']}")

    #print(layer_2_results)
    print('------------------------------------------------------------------------------------------')

    ############################################## Step 3: Pathway to Biological Process #######################################

    layer_3_results, report_l3 = propagate_generic_layer(layer_2_results, pathway_to_bp, nodes_data_master)

    print(f"{'FROM':<20} | {'TO':<75} | {'WEIGHT':<15} | {'OUT'}")
    print("-" * 75)
    for entry in report_l3:
        print(f"{entry['from']:<20} | {entry['to']:<75} | {entry['weight']:<15} | {entry['output']}")

    #print(report_l3)
    print('------------------------------------------------------------------------------------------')

    ######################################### Step 4: Biological Process to Virtual Circuit #######################################

    layer_4_results, report_l4 = propagate_to_vCN(layer_3_results, bp_to_virtual_circuit_nodes, nodes_data_master)

    print(f"{'FROM':<35} | {'TO':<30} | {'WEIGHT':<15} | {'OUT'}")
    print("-" * 75)
    for entry in report_l4:
        print(f"{entry['from']:<35} | {entry['to']:<30} | {entry['weight']:<15} | {entry['output']}")

    #print(report_l4)
    print('------------------------------------------------------------------------------------------')

    ######################################### Step 5: Virtual Circuit to Actual Circuit node #######################################

    layer_5_results, report_l5 = propagate_generic_layer(layer_4_results, virtaul_circuit_node_to_circuit_edges, nodes_data_master)

    print(f"{'FROM':<35} | {'TO':<40} | {'WEIGHT':<15} | {'OUT'}")
    print("-" * 75)
    for entry in report_l5:
        print(f"{entry['from']:<35} | {entry['to']:<40} | {entry['weight']:<15} | {entry['output']}")

    #print(report_l5)
    print('------------------------------------------------------------------------------------------')

    ######################################### Step 6: Circuit to Brain Region #######################################

    layer_6_results, report_l6 = propagate_generic_layer(layer_5_results, circuit_to_anatomy_edges, nodes_data_master)

    print(f"{'FROM':<40} | {'TO':<40} | {'WEIGHT':<15} | {'OUT'}")
    print("-" * 75)
    for entry in report_l6:
        print(f"{entry['from']:<40} | {entry['to']:<40} | {entry['weight']:<15} | {entry['output']}")

    #print(report_l6)
    print('------------------------------------------------------------------------------------------')

    ######################################### Step 7: Brain Region to Symptom #######################################

    layer_7_results, report_l7 = propagate_generic_layer(layer_6_results, region_to_disease_edges, nodes_data_master)

    print(f"{'FROM':<40} | {'TO':<40} | {'WEIGHT':<15} | {'OUT'}")
    print("-" * 75)
    for entry in report_l7:
        print(f"{entry['from']:<40} | {entry['to']:<40} | {entry['weight']:<15} | {entry['output']}")

    #print(report_l7)
    print('------------------------------------------------------------------------------------------')


    return (layer_7_results,)


@app.cell
def _(layer_7_results, symptoms):
    symptom_name_id = {s['name']:s['id']  for s in symptoms}
    reverse_map = {v: k for k,v in symptom_name_id.items()}
    {reverse_map.get(k,k): v for k, v in layer_7_results.items()}
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
