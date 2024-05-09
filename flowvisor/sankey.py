from typing import List
import plotly.graph_objects as go

from flowvisor.function_node import FunctionNode

source_list = []
target_list = []
value_list = []

def get_index_for_node(node: FunctionNode, all_nodes: List[FunctionNode], get_start = True):
    """
    Get the index for the node
    """
    i =  all_nodes.index(node)
    i *= 2
    if not get_start:
        i += 1
    return i

def add_connection(source: FunctionNode, target: FunctionNode, value: int, all_nodes: List[FunctionNode]):
    """
    Add a connection between two nodes
    """
    source_list.append(get_index_for_node(source, all_nodes))
    target_list.append(get_index_for_node(target, all_nodes))
    value_list.append(value)

def draw_node(node: FunctionNode, all_nodes: List[FunctionNode], parent = None):
    source_item = get_index_for_node(node, all_nodes)
    if parent is not None:
        source_item = get_index_for_node(parent, all_nodes, False)
        
    source_list.append(source_item)
    
    target_list.append(get_index_for_node(node, all_nodes, False))
    value_list.append(node.time)

def handle_node(node: FunctionNode, all_nodes: List[FunctionNode], parent = None):
    """
    Handle the node
    """
    draw_node(node, all_nodes, parent)
    for child in node.children:
        handle_node(child, all_nodes, node)

def get_labels(all_nodes: List[FunctionNode]):
    """
    Get the labels for the nodes
    """
    labels = []
    for node in all_nodes:
        labels.append(node.name + ":start")
        labels.append(node.name + ":end")
    return labels

def make_sankey_diagram(roots: List[FunctionNode], all_nodes: List[FunctionNode]):

    for node in roots:
      handle_node(node, all_nodes)

    fig = go.Figure(data=[go.Sankey(
        node = dict(
          label = get_labels(all_nodes),
          color = "blue",
          align = "left",
        ),
        link = dict(
            arrowlen=15,
            source = source_list,
            target = target_list,
            value = value_list
      ))])

    fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
    fig.show()
    # save the figure
    fig.write_image("sankey_diagram.png")

