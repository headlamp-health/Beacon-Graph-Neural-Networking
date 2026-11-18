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
        'drug': '#007bff',# Blue
        'gene': '#6610f2', # Indigo
        'protein': '#ffb300',      # Cyan
        'molecular_function': '#28a745',   # Green
        'pathways':'#a4ac86', # Olive Green
        'biological_process': '#6f42c1',     # Purple
        'RDOC_construct':'#b69dd6',         # Olive Green
        'RDOC_domain':'#20c997', #Teal
        'circuit': '#dc3545', # Red
        'brain_region':'#703332', #Brown
        'clinical_outcome':'#080707', #Black
        #'NeurotransmitterSystem':'#ffc107', # Amber
        #'Neurotransmitter':'#ffb300', #Slight amber
        #'Symptom':'#6c204d',
        # 'Target': '#adb5bd',   # Light Grey
        # 'Pathway': '#6610f2', # Indigo     
        # 'NDCPackage': '#fd7e14',     # Orange
        # 'biological_process': '#e83e8c',      # Pink
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
        type_order = {'drug': 0, 'gene':1, 'protein': 2, 'molecular_function': 3, 
                      'pathways':4, 'biological_process':5, 'RDOC_construct':6, 'RDOC_domain':8, 
                      'circuit':9, 'brain_region':10, 'clinical_outcome':11
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
def _():
    # j = []

    # for i in nodes_data_master: 
    #     #print(i)
    #     if i['category'] not in j: 
    #         j.append(i['category'])

    # for i in j: 
    #     print(i)
    #     print('-------')
    # #print(j)
    return


@app.cell
def _():
    # for i_2 in nodes_data_master: 
    #     print(i_2)
    #     print(i_2['_layer'])
    #     print(True if i_2['_layer'] == 0 else False)
    #     print('--------------------------------------------------')
    return


@app.cell
def _():
    # for i_3 in edges_data_master: 
    #     if i_3['subject'] in []:
    #         print(i_3)
    #         print('----------')
    return


@app.cell
def _():
    # for i_5 in nodes_data_master:
    #     if i_5['id'] in : 
    #         print(i_5)
    #         i_5['Type'] = "drug"
    #         i_5['_layer'] = -1
    return


@app.cell
def _(nodes_data_master):
    layer_neg_1 = []
    layer_0 = []
    #layer_1 = []
    layer_2 = []
    layer_3 = []
    layer_4 = []
    layer_5 = []
    layer_6 = []
    layer_7 = []
    layer_8 = []
    layer_9 = []

    for i_1 in nodes_data_master: 
        if i_1['_layer'] == -1: 
            i_1['Type'] = 'drug'
            layer_neg_1.append(i_1)
        elif i_1['_layer'] == 0: 
            i_1['Type'] = 'gene'
            layer_0.append(i_1)
        # elif i_1['_layer'] == 1:
        #     i_1['Type'] = 'protein'
        #     layer_1.append(i_1)
        elif i_1['_layer'] == 2: 
            i_1['Type'] = 'molecular_function'
            layer_2.append(i_1)
        elif i_1['_layer'] == 3: 
            i_1['Type'] = 'pathways'
            layer_3.append(i_1)
        elif i_1['_layer'] == 4 and i_1['id'] in ["GO:0060078", "GO:0040017", "GO:0098664", 
    "GO:0048167", "GO:0060124", "GO:0014062", "GO:0007186", "GO:0007264", "GO:0007626", "GO:0042428", "GO:0060160", "GO:0007208", 
    "GO:0048149", "GO:0007210", "GO:0033685", "GO:0060134" ,"GO:0060158", "GO:0007193", "GO:0001963", "GO:0051586", "GO:0014059"]: 
            i_1['Type'] = 'biological_process'
            layer_4.append(i_1)
        elif i_1['_layer'] == 5: 
            i_1['Type'] = 'RDOC_construct'
            layer_5.append(i_1)
        elif i_1['_layer'] == 6: 
            i_1['Type'] = 'RDOC_domain'
            layer_6.append(i_1)
        elif i_1['_layer'] == 7: 
            i_1['Type'] = 'circuit'
            layer_7.append(i_1)
        elif i_1['_layer'] == 8: 
            i_1['Type'] = 'brain_region'
            layer_8.append(i_1)
        elif i_1['_layer'] == 9: 
            i_1['Type'] = 'clinical_outcome'
            layer_9.append(i_1)

    print(layer_neg_1)
    print(layer_0)
    #print(layer_1)
    print(layer_2)
    print(layer_3)
    print(layer_4)
    print(layer_5)
    print(layer_6)
    print(layer_7)
    print(layer_8)
    print(layer_9)
    return (
        layer_0,
        layer_2,
        layer_3,
        layer_4,
        layer_5,
        layer_6,
        layer_7,
        layer_8,
        layer_9,
        layer_neg_1,
    )


@app.cell
def _(
    layer_0,
    layer_2,
    layer_3,
    layer_4,
    layer_5,
    layer_6,
    layer_7,
    layer_8,
    layer_9,
    layer_neg_1,
):
    layer_neg_ids = [i['id'] for i in layer_neg_1]
    layer_0_ids = [i['id'] for i in layer_0]
    #layer_1_ids = [i['id'] for i in layer_1]
    layer_2_ids = [i['id'] for i in layer_2]
    layer_3_ids = [i['id'] for i in layer_3]
    layer_4_ids = [i['id'] for i in layer_4]
    layer_5_ids = [i['id'] for i in layer_5]
    layer_6_ids = [i['id'] for i in layer_6]
    layer_7_ids = [i['id'] for i in layer_7]
    layer_8_ids = [i['id'] for i in layer_8]
    layer_9_ids = [i['id'] for i in layer_9]
    return layer_0_ids, layer_neg_ids


@app.cell
def _(edges_data_master, layer_0_ids, layer_neg_ids):
    # for i_6 in edges_data_master: 
    #     if i_6['subject'] in layer_8_ids and i_6['object'] in layer_9_ids:
    #         #print(i_6)
    #         #print(i_6["object"])
    #         #x.append(i_6["object"])
    #         print(f'{{"source": "{i_6["subject"]}", "target": "{i_6["object"]}", "relation": "", "weight": 1}},')




    for i_6 in edges_data_master: 
        #if i_4['subject'] in brain_region_ids and i_4['object'] in rdoc_construct_ids:
        if i_6['subject'] in layer_neg_ids and i_6['object'] in layer_0_ids:
            #print(i_6)
            print(f'{{"source": "{i_6["subject"]}", "target": "{i_6["object"]}", "relation": "", "weight": 1}},')
    #list(set(sorted(x)))
    return


@app.cell
def _():
    ## Edges

    ################################################# Layer neg to Layer 0: Drug to gene ###############################################
    ## 1. Drug --> Receptor (Using Hill Equation at 6nM)
    # Result of: Scaling * (6 / (6 + Ki))
    weight_drug_protien_DRD2 = 0.71 * (6/(6+2.5))
    weight_drug_protien_HTR2A = 0.38 * (6/(6+10))
    weight_drug_protien_HTR1A = 0.43 * (6/(6+8))

    drug_to_gene_edges = [
        {"source": "drug:aripiprazole", "target": "HGNC:3023", "relation": "", "weight":weight_drug_protien_DRD2},
        {"source": "drug:aripiprazole", "target": "HGNC:5293", "relation": "", "weight":weight_drug_protien_HTR2A},
        {"source": "drug:aripiprazole", "target": "HGNC:5286", "relation": "", "weight":weight_drug_protien_HTR1A} 
    ]

    ############################################## Layer 0 to Layer 1: Gene --> Protein ###########################################
    #gene_to_protein = [
    #    {"source":"HGNC:3023","target":"UniProtKB:P14416","relation":"Synthetic has_gene_product edge from UniProt","weight":1}
    #]

    ####################################### Layer 1 to layer 2: Protein --> Molecular Function ###########################################

    # Source 1 - Burris et al. (2002) - Aripiprazole, a Novel Antipsychotic, is a High-Affinity Partial Agonist at Human Dopamine D2 Receptors
    # Source 2 - Shapiro et al. (2003) - Aripiprazole, A Novel Atypical Antipsychotic Drug with a Unique and Robust Pharmacology
    # Source 3 - IUPHAR Database - Aripiprazole Ligand Page
    # Source 4 - Yokoi et al. (2002) - Dopamine D2 and D3 receptor occupancy in normal humans treated with aripiprazole


    protein_to_MF = [
        #HGNC:3023 DRD2
        # G protein-coupled receptor activity
        {'source': 'HGNC:3023', 'target': 'GO:0004930', 'relation': 'Partial_agonist', 'weight': 0.5},
        # dopamine neurotransmitter receptor activity, coupled via Gi/Go
        {'source': 'HGNC:3023', 'target': 'GO:0001591', 'relation': 'Partial_agonist', 'weight': 0.5},
        # G-protein alpha-subunit binding
        {'source': 'HGNC:3023', 'target': 'GO:0001965', 'relation': 'Partial_agonist', 'weight': 0.5},
        # dopamine neurotransmitter receptor activity 
        {'source': 'HGNC:3023', 'target': 'GO:0004952', 'relation': 'Partial_agonist', 'weight': 0.5},
        # signaling receptor binding
        {'source': 'HGNC:3023', 'target': 'GO:0005102', 'relation': 'Partial_agonist', 'weight': 0.5},
        # potassium channel regulator activity
        {'source': 'HGNC:3023', 'target': 'GO:0015459', 'relation': 'Partial_agonist', 'weight': 0.5}, 
        # heterotrimeric G-protein binding
        {'source': 'HGNC:3023', 'target': 'GO:0032795', 'relation': 'Partial_agonist', 'weight': 0.5},
        # dopamine binding (Blocks endogenous dopamine)
        {'source': 'HGNC:3023', 'target': 'GO:0035240', 'relation': 'Antagonist', 'weight': 0.0},
        # ionotropic glutamate receptor binding (Inhibitory role)
        {'source': 'HGNC:3023', 'target': 'GO:0035255', 'relation': 'Antagonist', 'weight': 0.0},
        # identical protein binding
        {'source': 'HGNC:3023', 'target': 'GO:0042802', 'relation': 'Partial_agonist', 'weight': 0.5},
        # protein-containing complex binding
        {'source': 'HGNC:3023', 'target': 'GO:0044877', 'relation': 'Partial_agonist', 'weight': 0.5},

        # HGNC:5293 HTR2A
        # neurotransmitter receptor activity
        {'source': 'HGNC:5293', 'target': 'GO:0030594', 'relation': 'Antagonist', 'weight': 0.0},
        # G protein-coupled serotonin receptor activity
        {'source': 'HGNC:5293', 'target': 'GO:0004993', 'relation': 'Antagonist', 'weight': 0.0},
        # Gq/11-coupled serotonin receptor activity
        {'source': 'HGNC:5293', 'target': 'GO:0001587', 'relation': 'Antagonist', 'weight': 0.0},
        # virus receptor activity
        {'source': 'HGNC:5293', 'target': 'GO:0001618', 'relation': 'Antagonist', 'weight': 0.0},
        # G protein-coupled receptor activity
        {'source': 'HGNC:5293', 'target': 'GO:0004930', 'relation': 'Antagonist', 'weight': 0.0},
        # protein tyrosine kinase activator activity
        {'source': 'HGNC:5293', 'target': 'GO:0030296', 'relation': 'Antagonist', 'weight': 0.0},
        # identical protein binding
        {'source': 'HGNC:5293', 'target': 'GO:0042802', 'relation': 'Antagonist', 'weight': 0.0},
        # protein-containing complex binding
        {'source': 'HGNC:5293', 'target': 'GO:0044877', 'relation': 'Antagonist', 'weight': 0.0},
        # serotonin binding
        {'source': 'HGNC:5293', 'target': 'GO:0051378', 'relation': 'Antagonist', 'weight': 0.0},
        # 1-(4-iodo-2,5-dimethoxyphenyl)propan-2-amine binding
        {'source': 'HGNC:5293', 'target': 'GO:0071886', 'relation': 'Antagonist', 'weight': 0.0},
        # serotonin receptor activity
        {'source': 'HGNC:5293', 'target': 'GO:0099589', 'relation': 'Antagonist', 'weight': 0.0},

        # HGNC:5286 HTR1A
        # # neurotransmitter receptor activity
        {'source': 'HGNC:5286', 'target': 'GO:0030594', 'relation': 'Partial_agonist', 'weight': 0.5},
        # G protein-coupled serotonin receptor activity
        {'source': 'HGNC:5286', 'target': 'GO:0004993', 'relation': 'Partial_agonist', 'weight': 0.5},
        # serotonin binding (Blocks endogenous serotonin)
        {'source': 'HGNC:5286', 'target': 'GO:0051378', 'relation': 'Antagonist', 'weight': 0.0},
        # Gi/o-coupled serotonin receptor activity
        {'source': 'HGNC:5286', 'target': 'GO:0001586', 'relation': 'Partial_agonist', 'weight': 0.5}, 
        # G protein-coupled receptor activity
        {'source': 'HGNC:5286', 'target': 'GO:0004930', 'relation': 'Partial_agonist', 'weight': 0.5}, 
        # receptor-receptor interaction
        {'source': 'HGNC:5286', 'target': 'GO:0090722', 'relation': 'Partial_agonist', 'weight': 0.5},
        # serotonin receptor activity
        {'source': 'HGNC:5286', 'target': 'GO:0099589', 'relation': 'Partial_agonist', 'weight': 0.5}
    ]

    ######################################## Layer 2 to Layer 3: MF --> Pathway #########################################
    MF_to_pathway = [
        {"source": "GO:0004930", "target": "KEGG:hsa04540", "relation": "", "weight": 1},
        {"source": "GO:0042802", "target": "KEGG:hsa04540", "relation": "", "weight": 1},
        {"source": "GO:0035240", "target": "KEGG:hsa04540", "relation": "", "weight": 1},
        {"source": "GO:0035255", "target": "KEGG:hsa04540", "relation": "", "weight": 1},
        {"source": "GO:0044877", "target": "KEGG:hsa04540", "relation": "", "weight": 1},
        {"source": "GO:0032795", "target": "KEGG:hsa04540", "relation": "", "weight": 1},
        {"source": "GO:0004952", "target": "KEGG:hsa04540", "relation": "", "weight": 1},
        {"source": "GO:0001965", "target": "KEGG:hsa04540", "relation": "", "weight": 1},
        {"source": "GO:0005102", "target": "KEGG:hsa04540", "relation": "", "weight": 1},
        {"source": "GO:0015459", "target": "KEGG:hsa04540", "relation": "", "weight": 1},
        {"source": "GO:0001591", "target": "KEGG:hsa04540", "relation": "", "weight": 1},
        {"source": "GO:0004930", "target": "KEGG:hsa04024", "relation": "", "weight": 1},
        {"source": "GO:0042802", "target": "KEGG:hsa04024", "relation": "", "weight": 1},
        {"source": "GO:0035240", "target": "KEGG:hsa04024", "relation": "", "weight": 1},
        {"source": "GO:0035255", "target": "KEGG:hsa04024", "relation": "", "weight": 1},
        {"source": "GO:0044877", "target": "KEGG:hsa04024", "relation": "", "weight": 1},
        {"source": "GO:0032795", "target": "KEGG:hsa04024", "relation": "", "weight": 1},
        {"source": "GO:0004952", "target": "KEGG:hsa04024", "relation": "", "weight": 1},
        {"source": "GO:0001965", "target": "KEGG:hsa04024", "relation": "", "weight": 1},
        {"source": "GO:0005102", "target": "KEGG:hsa04024", "relation": "", "weight": 1},
        {"source": "GO:0015459", "target": "KEGG:hsa04024", "relation": "", "weight": 1},
        {"source": "GO:0001591", "target": "KEGG:hsa04024", "relation": "", "weight": 1},
        {"source": "GO:0004930", "target": "KEGG:hsa04728", "relation": "", "weight": 1},
        {"source": "GO:0042802", "target": "KEGG:hsa04728", "relation": "", "weight": 1},
        {"source": "GO:0035240", "target": "KEGG:hsa04728", "relation": "", "weight": 1},
        {"source": "GO:0035255", "target": "KEGG:hsa04728", "relation": "", "weight": 1},
        {"source": "GO:0044877", "target": "KEGG:hsa04728", "relation": "", "weight": 1},
        {"source": "GO:0032795", "target": "KEGG:hsa04728", "relation": "", "weight": 1},
        {"source": "GO:0004952", "target": "KEGG:hsa04728", "relation": "", "weight": 1},
        {"source": "GO:0001965", "target": "KEGG:hsa04728", "relation": "", "weight": 1},
        {"source": "GO:0005102", "target": "KEGG:hsa04728", "relation": "", "weight": 1},
        {"source": "GO:0015459", "target": "KEGG:hsa04728", "relation": "", "weight": 1},
        {"source": "GO:0001591", "target": "KEGG:hsa04728", "relation": "", "weight": 1},
        {"source": "GO:0004930", "target": "Reactome:R-HSA-390651", "relation": "", "weight": 1},
        {"source": "GO:0042802", "target": "Reactome:R-HSA-390651", "relation": "", "weight": 1},
        {"source": "GO:0035240", "target": "Reactome:R-HSA-390651", "relation": "", "weight": 1},
        {"source": "GO:0035255", "target": "Reactome:R-HSA-390651", "relation": "", "weight": 1},
        {"source": "GO:0044877", "target": "Reactome:R-HSA-390651", "relation": "", "weight": 1},
        {"source": "GO:0032795", "target": "Reactome:R-HSA-390651", "relation": "", "weight": 1},
        {"source": "GO:0004952", "target": "Reactome:R-HSA-390651", "relation": "", "weight": 1},
        {"source": "GO:0001965", "target": "Reactome:R-HSA-390651", "relation": "", "weight": 1},
        {"source": "GO:0005102", "target": "Reactome:R-HSA-390651", "relation": "", "weight": 1},
        {"source": "GO:0015459", "target": "Reactome:R-HSA-390651", "relation": "", "weight": 1},
        {"source": "GO:0001591", "target": "Reactome:R-HSA-390651", "relation": "", "weight": 1},
        {"source": "GO:0004930", "target": "KEGG:hsa04082", "relation": "", "weight": 1},
        {"source": "GO:0042802", "target": "KEGG:hsa04082", "relation": "", "weight": 1},
        {"source": "GO:0035240", "target": "KEGG:hsa04082", "relation": "", "weight": 1},
        {"source": "GO:0035255", "target": "KEGG:hsa04082", "relation": "", "weight": 1},
        {"source": "GO:0044877", "target": "KEGG:hsa04082", "relation": "", "weight": 1},
        {"source": "GO:0032795", "target": "KEGG:hsa04082", "relation": "", "weight": 1},
        {"source": "GO:0004952", "target": "KEGG:hsa04082", "relation": "", "weight": 1},
        {"source": "GO:0001965", "target": "KEGG:hsa04082", "relation": "", "weight": 1},
        {"source": "GO:0005102", "target": "KEGG:hsa04082", "relation": "", "weight": 1},
        {"source": "GO:0015459", "target": "KEGG:hsa04082", "relation": "", "weight": 1},
        {"source": "GO:0001591", "target": "KEGG:hsa04082", "relation": "", "weight": 1},
        {"source": "GO:0004930", "target": "KEGG:hsa04015", "relation": "", "weight": 1},
        {"source": "GO:0042802", "target": "KEGG:hsa04015", "relation": "", "weight": 1},
        {"source": "GO:0035240", "target": "KEGG:hsa04015", "relation": "", "weight": 1},
        {"source": "GO:0035255", "target": "KEGG:hsa04015", "relation": "", "weight": 1},
        {"source": "GO:0044877", "target": "KEGG:hsa04015", "relation": "", "weight": 1},
        {"source": "GO:0032795", "target": "KEGG:hsa04015", "relation": "", "weight": 1},
        {"source": "GO:0004952", "target": "KEGG:hsa04015", "relation": "", "weight": 1},
        {"source": "GO:0001965", "target": "KEGG:hsa04015", "relation": "", "weight": 1},
        {"source": "GO:0005102", "target": "KEGG:hsa04015", "relation": "", "weight": 1},
        {"source": "GO:0015459", "target": "KEGG:hsa04015", "relation": "", "weight": 1},
        {"source": "GO:0001591", "target": "KEGG:hsa04015", "relation": "", "weight": 1},
        {"source": "GO:0004930", "target": "KEGG:hsa04081", "relation": "", "weight": 1},
        {"source": "GO:0042802", "target": "KEGG:hsa04081", "relation": "", "weight": 1},
        {"source": "GO:0035240", "target": "KEGG:hsa04081", "relation": "", "weight": 1},
        {"source": "GO:0035255", "target": "KEGG:hsa04081", "relation": "", "weight": 1},
        {"source": "GO:0044877", "target": "KEGG:hsa04081", "relation": "", "weight": 1},
        {"source": "GO:0032795", "target": "KEGG:hsa04081", "relation": "", "weight": 1},
        {"source": "GO:0004952", "target": "KEGG:hsa04081", "relation": "", "weight": 1},
        {"source": "GO:0001965", "target": "KEGG:hsa04081", "relation": "", "weight": 1},
        {"source": "GO:0005102", "target": "KEGG:hsa04081", "relation": "", "weight": 1},
        {"source": "GO:0015459", "target": "KEGG:hsa04081", "relation": "", "weight": 1},
        {"source": "GO:0001591", "target": "KEGG:hsa04081", "relation": "", "weight": 1},
        {"source": "GO:0004930", "target": "KEGG:hsa04080", "relation": "", "weight": 1},
        {"source": "GO:0042802", "target": "KEGG:hsa04080", "relation": "", "weight": 1},
        {"source": "GO:0035240", "target": "KEGG:hsa04080", "relation": "", "weight": 1},
        {"source": "GO:0035255", "target": "KEGG:hsa04080", "relation": "", "weight": 1},
        {"source": "GO:0044877", "target": "KEGG:hsa04080", "relation": "", "weight": 1},
        {"source": "GO:0032795", "target": "KEGG:hsa04080", "relation": "", "weight": 1},
        {"source": "GO:0004952", "target": "KEGG:hsa04080", "relation": "", "weight": 1},
        {"source": "GO:0001965", "target": "KEGG:hsa04080", "relation": "", "weight": 1},
        {"source": "GO:0005102", "target": "KEGG:hsa04080", "relation": "", "weight": 1},
        {"source": "GO:0015459", "target": "KEGG:hsa04080", "relation": "", "weight": 1},
        {"source": "GO:0001591", "target": "KEGG:hsa04080", "relation": "", "weight": 1},
        {"source": "GO:0030594", "target": "Reactome:R-HSA-416476", "relation": "", "weight": 1},
        {"source": "GO:0099589", "target": "Reactome:R-HSA-416476", "relation": "", "weight": 1},
        {"source": "GO:0051378", "target": "Reactome:R-HSA-416476", "relation": "", "weight": 1},
        {"source": "GO:0042802", "target": "Reactome:R-HSA-416476", "relation": "", "weight": 1},
        {"source": "GO:0030296", "target": "Reactome:R-HSA-416476", "relation": "", "weight": 1},
        {"source": "GO:0004930", "target": "Reactome:R-HSA-416476", "relation": "", "weight": 1},
        {"source": "GO:0044877", "target": "Reactome:R-HSA-416476", "relation": "", "weight": 1},
        {"source": "GO:0001618", "target": "Reactome:R-HSA-416476", "relation": "", "weight": 1},
        {"source": "GO:0001587", "target": "Reactome:R-HSA-416476", "relation": "", "weight": 1},
        {"source": "GO:0071886", "target": "Reactome:R-HSA-416476", "relation": "", "weight": 1},
        {"source": "GO:0004993", "target": "Reactome:R-HSA-416476", "relation": "", "weight": 1},
        {"source": "GO:0030594", "target": "Reactome:R-HSA-390666", "relation": "", "weight": 1},
        {"source": "GO:0099589", "target": "Reactome:R-HSA-390666", "relation": "", "weight": 1},
        {"source": "GO:0051378", "target": "Reactome:R-HSA-390666", "relation": "", "weight": 1},
        {"source": "GO:0042802", "target": "Reactome:R-HSA-390666", "relation": "", "weight": 1},
        {"source": "GO:0030296", "target": "Reactome:R-HSA-390666", "relation": "", "weight": 1},
        {"source": "GO:0004930", "target": "Reactome:R-HSA-390666", "relation": "", "weight": 1},
        {"source": "GO:0044877", "target": "Reactome:R-HSA-390666", "relation": "", "weight": 1},
        {"source": "GO:0001618", "target": "Reactome:R-HSA-390666", "relation": "", "weight": 1},
        {"source": "GO:0001587", "target": "Reactome:R-HSA-390666", "relation": "", "weight": 1},
        {"source": "GO:0071886", "target": "Reactome:R-HSA-390666", "relation": "", "weight": 1},
        {"source": "GO:0004993", "target": "Reactome:R-HSA-390666", "relation": "", "weight": 1},
        {"source": "GO:0090722", "target": "Reactome:R-HSA-390666", "relation": "", "weight": 1},
        {"source": "GO:0001586", "target": "Reactome:R-HSA-390666", "relation": "", "weight": 1}
    ]

    ################################## Layer 3 to Layer 4: Pathway --> Biological Process ########################################
    pathway_to_BP = [
        {"source": "KEGG:hsa04728", "target": "GO:0001963", "relation": "", "weight": 1},
        {"source": "KEGG:hsa04015", "target": "GO:0007264", "relation": "", "weight": 1},
        {"source": "KEGG:hsa04024", "target": "GO:0007193", "relation": "", "weight": 1},
        {"source": "KEGG:hsa04728", "target": "GO:0007626", "relation": "", "weight": 1},
        {"source": "KEGG:hsa04728", "target": "GO:0014059", "relation": "", "weight": 1},
        {"source": "KEGG:hsa04728", "target": "GO:0060134", "relation": "", "weight": 1},
        {"source": "KEGG:hsa04728", "target": "GO:0048167", "relation": "", "weight": 1},
        {"source": "KEGG:hsa04024", "target": "GO:0048167", "relation": "", "weight": 1},
        {"source": "KEGG:hsa04728", "target": "GO:0033685", "relation": "", "weight": 1},
        {"source": "KEGG:hsa04728", "target": "GO:0048149", "relation": "", "weight": 1},
        {"source": "KEGG:hsa04728", "target": "GO:0040017", "relation": "", "weight": 1},
        {"source": "KEGG:hsa04728", "target": "GO:0060078", "relation": "", "weight": 1},
        {"source": "Reactome:R-HSA-390651", "target": "GO:0060160", "relation": "", "weight": 1},
        {"source": "Reactome:R-HSA-390651", "target": "GO:0060158", "relation": "", "weight": 1},
        {"source": "Reactome:R-HSA-390651", "target": "GO:0051586", "relation": "", "weight": 1},
        {"source": "KEGG:hsa04081", "target": "GO:0060124", "relation": "", "weight": 1},
        {"source": "KEGG:hsa04081", "target": "GO:0033685", "relation": "", "weight": 1},
        {"source": "KEGG:hsa04080", "target": "GO:0060160", "relation": "", "weight": 1},
        {"source": "KEGG:hsa04080", "target": "GO:0007186", "relation": "", "weight": 1},
        {"source": "KEGG:hsa04080", "target": "GO:0060158", "relation": "", "weight": 1},
        {"source": "Reactome:R-HSA-390666", "target": "GO:0098664", "relation": "", "weight": 1},
        {"source": "Reactome:R-HSA-390666", "target": "GO:0007210", "relation": "", "weight": 1},
        {"source": "Reactome:R-HSA-390666", "target": "GO:0007208", "relation": "", "weight": 1},
        {"source": "Reactome:R-HSA-390666", "target": "GO:0042428", "relation": "", "weight": 1},
        {"source": "Reactome:R-HSA-390666", "target": "GO:0014062", "relation": "", "weight": 1}
    ]

    ######################################## Layer 4 to Layer 5: BP --> RDOC Construct ############################################
    BP_to_RDOC_Construct = [
        {"source": "GO:0001963", "target": "RDOC_CONSTRUCT:reward_responsiveness", "relation": "", "weight": 1},
        {"source": "GO:0001963", "target": "RDOC_CONSTRUCT:reward_learning", "relation": "", "weight": 1},
        {"source": "GO:0001963", "target": "RDOC_CONSTRUCT:effort_valuation", "relation": "", "weight": 1},
        {"source": "GO:0001963", "target": "RDOC_CONSTRUCT:expectancy", "relation": "", "weight": 1},
        {"source": "GO:0001963", "target": "RDOC_CONSTRUCT:habit", "relation": "", "weight": 1},
        {"source": "GO:0007626", "target": "RDOC_CONSTRUCT:motor_actions", "relation": "", "weight": 1},
        {"source": "GO:0007626", "target": "RDOC_CONSTRUCT:innate_motor_patterns", "relation": "", "weight": 1},
        {"source": "GO:0014059", "target": "RDOC_CONSTRUCT:arousal", "relation": "", "weight": 1},
        {"source": "GO:0040017", "target": "RDOC_CONSTRUCT:motor_actions", "relation": "", "weight": 1},
        {"source": "GO:0048149", "target": "RDOC_CONSTRUCT:initial_responsiveness", "relation": "", "weight": 1},
        {"source": "GO:0060134", "target": "RDOC_CONSTRUCT:innate_motor_patterns", "relation": "", "weight": 1}
    ]

    ################################# Layer 5 to Layer 6: RDOC Construct --> RDOC Domain ##################################

    RDOC_Construct_to_RDOC_Domain = [
        {"source": "RDOC_CONSTRUCT:arousal", "target": "RDOC_DOMAIN:rdoc_domain:arousal_regulatory", "relation": "", "weight": 1},
        {"source": "RDOC_CONSTRUCT:attention", "target": "RDOC_DOMAIN:rdoc_domain:cognitive", "relation": "", "weight": 1},
        {"source": "RDOC_CONSTRUCT:cognitive_control", "target": "RDOC_DOMAIN:rdoc_domain:cognitive", "relation": "", "weight": 1},
        {"source": "RDOC_CONSTRUCT:declarative_memory", "target": "RDOC_DOMAIN:rdoc_domain:cognitive", "relation": "", "weight": 1},
        {"source": "RDOC_CONSTRUCT:effort_valuation", "target": "RDOC_DOMAIN:rdoc_domain:positive_valence", "relation": "", "weight": 1},
        {"source": "RDOC_CONSTRUCT:expectancy", "target": "RDOC_DOMAIN:rdoc_domain:positive_valence", "relation": "", "weight": 1},
        {"source": "RDOC_CONSTRUCT:habit", "target": "RDOC_DOMAIN:rdoc_domain:sensorimotor", "relation": "", "weight": 1},
        {"source": "RDOC_CONSTRUCT:initial_responsiveness", "target": "RDOC_DOMAIN:rdoc_domain:positive_valence", "relation": "", "weight": 1},
        {"source": "RDOC_CONSTRUCT:innate_motor_patterns", "target": "RDOC_DOMAIN:rdoc_domain:sensorimotor", "relation": "", "weight": 1},
        {"source": "RDOC_CONSTRUCT:motor_actions", "target": "RDOC_DOMAIN:rdoc_domain:sensorimotor", "relation": "", "weight": 1},
        {"source": "RDOC_CONSTRUCT:reward_learning", "target": "RDOC_DOMAIN:rdoc_domain:positive_valence", "relation": "", "weight": 1},
        {"source": "RDOC_CONSTRUCT:reward_responsiveness", "target": "RDOC_DOMAIN:rdoc_domain:positive_valence", "relation": "", "weight": 1},
        {"source": "RDOC_CONSTRUCT:reward_valuation", "target": "RDOC_DOMAIN:rdoc_domain:positive_valence", "relation": "", "weight": 1},
        {"source": "RDOC_CONSTRUCT:working_memory", "target": "RDOC_DOMAIN:rdoc_domain:cognitive", "relation": "", "weight": 1}    
    ]

    ################################## Layer 6 to Layer 7: RDOC Domain --> Circuit #########################################
    RDOC_Domain_to_circuit = [
        {"source": "RDOC_DOMAIN:rdoc_domain:positive_valence", "target": "CIRCUIT:mesolimbic", "relation": "", "weight": 1},
        {"source": "RDOC_DOMAIN:rdoc_domain:positive_valence", "target": "CIRCUIT:mesocortical", "relation": "", "weight": 1},
        {"source": "RDOC_DOMAIN:rdoc_domain:cognitive", "target": "CIRCUIT:mesocortical", "relation": "", "weight": 1},
        {"source": "RDOC_DOMAIN:rdoc_domain:sensorimotor", "target": "CIRCUIT:nigrostriatal", "relation": "", "weight": 1}
    ]

    ################################## Layer 7 to Layer 8: Circuit --> brain_region #########################################
    circuit_to_brain_region = [
        {"source": "CIRCUIT:mesolimbic", "target": "UBERON:0002691", "relation": "", "weight": 1},
        {"source": "CIRCUIT:mesolimbic", "target": "UBERON:0001882", "relation": "", "weight": 1},
        {"source": "CIRCUIT:mesolimbic", "target": "UBERON:0002421", "relation": "", "weight": 1},
        {"source": "CIRCUIT:mesolimbic", "target": "UBERON:0001876", "relation": "", "weight": 1},
        {"source": "CIRCUIT:mesocortical", "target": "UBERON:0002691", "relation": "", "weight": 1},
        {"source": "CIRCUIT:mesocortical", "target": "UBERON:0001870", "relation": "", "weight": 1},
        {"source": "CIRCUIT:mesocortical", "target": "UBERON:0000451", "relation": "", "weight": 1},
        {"source": "CIRCUIT:nigrostriatal", "target": "UBERON:0002038", "relation": "", "weight": 1},
        {"source": "CIRCUIT:nigrostriatal", "target": "UBERON:0002435", "relation": "", "weight": 1},
        {"source": "CIRCUIT:nigrostriatal", "target": "UBERON:0001873", "relation": "", "weight": 1},
        {"source": "CIRCUIT:nigrostriatal", "target": "UBERON:0001874", "relation": "", "weight": 1},
        {"source": "CIRCUIT:nigrostriatal", "target": "UBERON:0002477", "relation": "", "weight": 1},
        {"source": "CIRCUIT:nigrostriatal", "target": "UBERON:0002476", "relation": "", "weight": 1},
        {"source": "CIRCUIT:nigrostriatal", "target": "UBERON:0001897", "relation": "", "weight": 1},
        {"source": "CIRCUIT:tuberoinfundibular", "target": "UBERON:0001898", "relation": "", "weight": 1},
        {"source": "CIRCUIT:tuberoinfundibular", "target": "UBERON:0000007", "relation": "", "weight": 1},
        {"source": "CIRCUIT:raphe_prefrontal", "target": "UBERON:0002043", "relation": "", "weight": 1},
        {"source": "CIRCUIT:raphe_prefrontal", "target": "UBERON:0001870", "relation": "", "weight": 1},
        {"source": "CIRCUIT:raphe_limbic", "target": "UBERON:0002043", "relation": "", "weight": 1},
        {"source": "CIRCUIT:raphe_limbic", "target": "UBERON:0001876", "relation": "", "weight": 1},
        {"source": "CIRCUIT:raphe_limbic", "target": "UBERON:0002421", "relation": "", "weight": 1},
        {"source": "CIRCUIT:raphe_striatal", "target": "UBERON:0002043", "relation": "", "weight": 1},
        {"source": "CIRCUIT:raphe_striatal", "target": "UBERON:0002435", "relation": "", "weight": 1}
    ]

    ################################## Layer 8 to Layer 9: brain_region --> clinical outcome ################################
    brain_region_to_clinical_outcome = [
        {"source": "UBERON:0002691", "target": "MONDO:0005090", "relation": "", "weight": 1},
        {"source": "UBERON:0001882", "target": "MONDO:0005090", "relation": "", "weight": 1},
        {"source": "UBERON:0002421", "target": "MONDO:0005090", "relation": "", "weight": 1},
        {"source": "UBERON:0001876", "target": "MONDO:0005090", "relation": "", "weight": 1},
        {"source": "UBERON:0002691", "target": "MONDO:0002491", "relation": "", "weight": 1},
        {"source": "UBERON:0001882", "target": "MONDO:0002491", "relation": "", "weight": 1},
        {"source": "UBERON:0002421", "target": "MONDO:0002491", "relation": "", "weight": 1},
        {"source": "UBERON:0001876", "target": "MONDO:0002491", "relation": "", "weight": 1},
        {"source": "UBERON:0002691", "target": "MONDO:0007079", "relation": "", "weight": 1},
        {"source": "UBERON:0001882", "target": "MONDO:0007079", "relation": "", "weight": 1},
        {"source": "UBERON:0002421", "target": "MONDO:0007079", "relation": "", "weight": 1},
        {"source": "UBERON:0001876", "target": "MONDO:0007079", "relation": "", "weight": 1},
        {"source": "UBERON:0002691", "target": "MONDO:0004985", "relation": "", "weight": 1},
        {"source": "UBERON:0001882", "target": "MONDO:0004985", "relation": "", "weight": 1},
        {"source": "UBERON:0002421", "target": "MONDO:0004985", "relation": "", "weight": 1},
        {"source": "UBERON:0001876", "target": "MONDO:0004985", "relation": "", "weight": 1},
        {"source": "UBERON:0002691", "target": "MONDO:0007743", "relation": "", "weight": 1},
        {"source": "UBERON:0001882", "target": "MONDO:0007743", "relation": "", "weight": 1},
        {"source": "UBERON:0002421", "target": "MONDO:0007743", "relation": "", "weight": 1},
        {"source": "UBERON:0001876", "target": "MONDO:0007743", "relation": "", "weight": 1},
        {"source": "UBERON:0002691", "target": "MONDO:0002050", "relation": "", "weight": 1},
        {"source": "UBERON:0001882", "target": "MONDO:0002050", "relation": "", "weight": 1},
        {"source": "UBERON:0002421", "target": "MONDO:0002050", "relation": "", "weight": 1},
        {"source": "UBERON:0001876", "target": "MONDO:0002050", "relation": "", "weight": 1},
        {"source": "UBERON:0001870", "target": "MONDO:0005090", "relation": "", "weight": 1},
        {"source": "UBERON:0000451", "target": "MONDO:0005090", "relation": "", "weight": 1},
        {"source": "UBERON:0001870", "target": "MONDO:0007743", "relation": "", "weight": 1},
        {"source": "UBERON:0000451", "target": "MONDO:0007743", "relation": "", "weight": 1},
        {"source": "UBERON:0001870", "target": "MONDO:0002050", "relation": "", "weight": 1},
        {"source": "UBERON:0000451", "target": "MONDO:0002050", "relation": "", "weight": 1},
        {"source": "UBERON:0002038", "target": "MONDO:0005180", "relation": "", "weight": 1},
        {"source": "UBERON:0002435", "target": "MONDO:0005180", "relation": "", "weight": 1},
        {"source": "UBERON:0001873", "target": "MONDO:0005180", "relation": "", "weight": 1},
        {"source": "UBERON:0001874", "target": "MONDO:0005180", "relation": "", "weight": 1},
        {"source": "UBERON:0002477", "target": "MONDO:0005180", "relation": "", "weight": 1},
        {"source": "UBERON:0002476", "target": "MONDO:0005180", "relation": "", "weight": 1},
        {"source": "UBERON:0001897", "target": "MONDO:0005180", "relation": "", "weight": 1},
        {"source": "UBERON:0002038", "target": "MONDO:0001609", "relation": "", "weight": 1},
        {"source": "UBERON:0002435", "target": "MONDO:0001609", "relation": "", "weight": 1},
        {"source": "UBERON:0001873", "target": "MONDO:0001609", "relation": "", "weight": 1},
        {"source": "UBERON:0001874", "target": "MONDO:0001609", "relation": "", "weight": 1},
        {"source": "UBERON:0002477", "target": "MONDO:0001609", "relation": "", "weight": 1},
        {"source": "UBERON:0002476", "target": "MONDO:0001609", "relation": "", "weight": 1},
        {"source": "UBERON:0001897", "target": "MONDO:0001609", "relation": "", "weight": 1},
        {"source": "UBERON:0002038", "target": "MONDO:0000903", "relation": "", "weight": 1},
        {"source": "UBERON:0002435", "target": "MONDO:0000903", "relation": "", "weight": 1},
        {"source": "UBERON:0001873", "target": "MONDO:0000903", "relation": "", "weight": 1},
        {"source": "UBERON:0001874", "target": "MONDO:0000903", "relation": "", "weight": 1},
        {"source": "UBERON:0002477", "target": "MONDO:0000903", "relation": "", "weight": 1},
        {"source": "UBERON:0002476", "target": "MONDO:0000903", "relation": "", "weight": 1},
        {"source": "UBERON:0001897", "target": "MONDO:0000903", "relation": "", "weight": 1},
        {"source": "UBERON:0002038", "target": "MONDO:0005391", "relation": "", "weight": 1},
        {"source": "UBERON:0002435", "target": "MONDO:0005391", "relation": "", "weight": 1},
        {"source": "UBERON:0001873", "target": "MONDO:0005391", "relation": "", "weight": 1},
        {"source": "UBERON:0001874", "target": "MONDO:0005391", "relation": "", "weight": 1},
        {"source": "UBERON:0002477", "target": "MONDO:0005391", "relation": "", "weight": 1},
        {"source": "UBERON:0002476", "target": "MONDO:0005391", "relation": "", "weight": 1},
        {"source": "UBERON:0001897", "target": "MONDO:0005391", "relation": "", "weight": 1},
        {"source": "UBERON:0002038", "target": "MONDO:0007661", "relation": "", "weight": 1},
        {"source": "UBERON:0002435", "target": "MONDO:0007661", "relation": "", "weight": 1},
        {"source": "UBERON:0001873", "target": "MONDO:0007661", "relation": "", "weight": 1},
        {"source": "UBERON:0001874", "target": "MONDO:0007661", "relation": "", "weight": 1},
        {"source": "UBERON:0002477", "target": "MONDO:0007661", "relation": "", "weight": 1},
        {"source": "UBERON:0002476", "target": "MONDO:0007661", "relation": "", "weight": 1},
        {"source": "UBERON:0001897", "target": "MONDO:0007661", "relation": "", "weight": 1},
        {"source": "UBERON:0001898", "target": "MONDO:0001981", "relation": "", "weight": 1},
        {"source": "UBERON:0000007", "target": "MONDO:0001981", "relation": "", "weight": 1},
        {"source": "UBERON:0002043", "target": "MONDO:0005618", "relation": "", "weight": 1},
        {"source": "UBERON:0001870", "target": "MONDO:0005618", "relation": "", "weight": 1},
        {"source": "UBERON:0001876", "target": "MONDO:0005618", "relation": "", "weight": 1},
        {"source": "UBERON:0002421", "target": "MONDO:0005618", "relation": "", "weight": 1},
        {"source": "UBERON:0002043", "target": "MONDO:0005277", "relation": "", "weight": 1},
        {"source": "UBERON:0001876", "target": "MONDO:0005277", "relation": "", "weight": 1},
        {"source": "UBERON:0002421", "target": "MONDO:0005277", "relation": "", "weight": 1},
        {"source": "UBERON:0002043", "target": "MONDO:0008114", "relation": "", "weight": 1},
        {"source": "UBERON:0002435", "target": "MONDO:0008114", "relation": "", "weight": 1}    
    ]
    return drug_to_gene_edges, protein_to_MF


@app.cell
def _():
    layer_names = ["layer_neg_1","layer_0", #"layer_1", 
                   "layer_2", "layer_3", "layer_4", "layer_5", "layer_6", "layer_7", "layer_8", "layer_9"]

    layer_acutals = ["drug","Gene", "Protein", "MF", "pathway", "BP", 
                   "RDOC_Construct", "RDOC_Domain", "circuit", "brain_region", "clinical_outcome"]

    print("-------------------------# of Nodes of each type--------------------------")
    for name, condition in zip(layer_names, layer_acutals):
        data = globals()[name] 
        print(f"{name} ({condition}): {len(data)}")
    return


@app.cell
def _(nodes_data_master, protein_to_MF):
    # #matching_edges = [edge for edge in edges_data_master if edge['source'] in protein_ids]
    # for i_4 in edges_data_master: 
    #     #if i_4['subject'] in brain_region_ids and i_4['object'] in rdoc_construct_ids:
    #     if i_4['subject'] in layer_neg_ids and i_4['object'] in layer_0_ids:
    #         print(f'{{"source": "{i_4["subject"]}", "target": "{i_4["object"]}", "relation": "", "weight": 1}},')
    lookup_map = {node['id']: node['name'] for node in nodes_data_master}

    for i_4 in protein_to_MF: 
        print(i_4)
        source_id = i_4['source']
        target_id = i_4['target']

        source_name = lookup_map.get(source_id)
        target_name = lookup_map.get(target_id)

        print(f"Source: {source_name} ({source_id})")
        print(f"Target: {target_name} ({target_id})")
        print('----------')



        # 2. Run your original loop with fast lookups
    # for i_4 in protein_to_MF:
    #     # Use .get() to safely retrieve names from the lookup map
    #     source_name = lookup_map.get(i_4['source'], "Unknown Source")
    #     target_name = lookup_map.get(i_4['target'], "Unknown Target")
    
    #     print(f"Source: {source_name} (ID: {i_4['source']})")
    #     print(f"Target: {target_name} (ID: {i_4['target']})")
    #     print('----------')
    return


@app.cell
def _(drug_to_gene_edges, layer_0, layer_2, layer_neg_1, protein_to_MF):
    nodes_for_graph = []
    nodes_for_graph.extend(layer_neg_1)
    nodes_for_graph.extend(layer_0)
    #nodes_for_graph.extend(layer_1)
    nodes_for_graph.extend(layer_2)
    #nodes_for_graph.extend(layer_3)
    #nodes_for_graph.extend(layer_4)
    #nodes_for_graph.extend(layer_5)
    #nodes_for_graph.extend(layer_6)
    #nodes_for_graph.extend(layer_7)
    #nodes_for_graph.extend(layer_8)
    #nodes_for_graph.extend(layer_9)



    edges_for_graph = []
    edges_for_graph.extend(drug_to_gene_edges)
    #edges_for_graph.extend(gene_to_protein)
    edges_for_graph.extend(protein_to_MF)
    #edges_for_graph.extend(MF_to_pathway)
    #edges_for_graph.extend(pathway_to_BP)
    #edges_for_graph.extend(BP_to_RDOC_Construct)
    #edges_for_graph.extend(RDOC_Construct_to_RDOC_Domain)
    #edges_for_graph.extend(RDOC_Domain_to_circuit)
    #edges_for_graph.extend(circuit_to_brain_region)
    #edges_for_graph.extend(brain_region_to_clinical_outcome)
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
