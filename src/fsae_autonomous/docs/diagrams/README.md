# Rendered diagrams

SVG copies of the Mermaid charts, so the docs show diagrams in any Markdown viewer
(VS Code's built-in preview does not draw Mermaid). The Mermaid source stays in each doc,
inside a collapsed "Mermaid source" block, and is the copy to edit.

| Image | Source |
|---|---|
| `architecture_1_pipeline.svg` | `docs/ARCHITECTURE.md`, diagram 1 |
| `architecture_2_node_topic_graph.svg` | `docs/ARCHITECTURE.md`, diagram 2 |
| `architecture_3_launch_tree.svg` | `docs/ARCHITECTURE.md`, diagram 3 |
| `nmpc_controller_io.svg` | `control/fsae_control/fsae_control/mpc/MPC_NODE_DOCS.md`, inputs and outputs chart |

After editing a chart, re-render it with the Mermaid CLI (needs Node.js):

```bash
# save the chart's Mermaid text (without the ``` fences) as chart.mmd, then:
npx -p @mermaid-js/mermaid-cli@11.4.2 mmdc -b white -i chart.mmd -o docs/diagrams/<name>.svg
```

`mmdc` uses a headless Chrome; set `PUPPETEER_EXECUTABLE_PATH` to an installed Chrome or
Edge if it cannot download one. Keep `flowchart.htmlLabels` false (`-c` with
`{"flowchart":{"htmlLabels":false}}`) so the SVG draws text without HTML, which some
viewers drop.
