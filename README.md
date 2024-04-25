<div align="center">
  <br />
  <!-- <img src="" alt="FlowVisorLogo" width="30%"/> -->
  <h1>FlowVisor</h1>
  <p>
    Visualize the flow of your python code.
  </p>
</div>

<!-- Badges -->
<div align="center">
   <!-- <a href="https://github.com/cophilot/FlowVisor/releases">
       <img src="https://img.shields.io/github/v/release/cophilot/FlowVisor?display_name=tag" alt="current realease" />
   </a> -->
   <a href="https://github.com/cophilot/FlowVisor/blob/master/LICENSE">
       <img src="https://img.shields.io/github/license/cophilot/FlowVisor" alt="license" />
   </a>
   <a href="https://github.com/cophilot/FlowVisor/stargazers">
       <img src="https://img.shields.io/github/stars/cophilot/FlowVisor" alt="stars" />
   </a>
   <a href="https://github.com/cophilot/FlowVisor/commits/master">
       <img src="https://img.shields.io/github/last-commit/cophilot/FlowVisor" alt="last commit" />
   </a>
</div>

---

![FlowVisor-Example](https://raw.githubusercontent.com/cophilot/FlowVisor/main/assets/example.png)

---

-   [Installation](#installation)
-   [Usage](#usage)
-   [CLI](#cli)
    -   [add-vis](#add-vis)
    -   [remove-vis](#remove-vis)
    -   [vis-file](#vis-file)
-   [Overhead](#overhead)
-   [Development](#development)
-   [Example](#example)

---

## Installation

```bash
pip install FlowVisor
```

---

## Usage

```python
from FlowVisor import FlowVisor, vis

@vis # This will visualize the function in the flow
def my_function():
    print("Hello World")

@vis
def my_other_function():
    my_function()

my_other_function()
FlowVisor.CONFIG.output_file = "example_graph" # You can add some configureation with the CONFIG object
FlowVisor.graph() # Generate the graph
FlowVisor.export("example_flow", "json") # Save the flow as json

```

---

## CLI

### add-vis

Adds the vis decorator to all functions in all python files in a directory.

```bash
add-vis -p <path-to-dir>
```

### remove-vis

Removes the vis decorator from all functions in all python files in a directory.

```bash
remove-vis -p <path-to-dir>
```

### vis-file

Generate a graph from a exported flow file.

```bash
vis-file -f <path-to-flow-file>
```

---

## Overhead

The overhead of the FlowVisor is tried to be kept as low as possible. The overhead is mainly caused by the decorator. Therefore the time for running the logic of the Flowvisor is excluded from the profiling.

You can even descrease the overhead by the `advanced_ovhead_reduction`:

```python
FlowVisor.enable_advanced_overhead_reduction()
```

---

## Development

```bash
git clone https://github.com/cophilot/FlowVisor
cd FlowVisor
pip install -r requirements.txt
```

---

## Example

Run the example:

```python
pip install -r requirements.txt
python example.py
```

---

<!-- ## Bugs

-   _no known bugs_

---

## [Release Notes](https://github.com/cophilot/FlowVisor/blob/master/CHANGELOG.md)

### [v0.0.1](https://github.com/cophilot/FlowVisor/tree/0.0.1)

-   _Initial release_
 -->

by [Philipp B.](https://github.com/cophilot)
