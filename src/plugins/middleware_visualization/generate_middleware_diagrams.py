"""Generate Mermaid diagrams for middleware hook combinations.

Binary naming scheme (5 bits):
- Bit 0: has_tools
- Bit 1: before_agent
- Bit 2: before_model
- Bit 3: after_model
- Bit 4: after_agent

Example: "10110" = tools, before_model, after_model
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from langchain_core.language_models.chat_models import SimpleChatModel
from langchain_core.tools import tool

from langchain.agents.factory import create_agent
from langchain.agents.middleware.types import AgentMiddleware, AgentState


class DemoModel(SimpleChatModel):
    """Demo model for generating diagrams."""

    def _call(self, messages, stop=None, run_manager=None, **kwargs):
        return "Demo response"

    @property
    def _llm_type(self) -> str:
        return "demo"


@tool
def demo_tool(query: str) -> str:
    """Demo tool for testing."""
    return f"Result for: {query}"


class BeforeModelMiddleware(AgentMiddleware):
    """Middleware with only before_model hook."""

    def before_model(self, state: AgentState, runtime) -> dict[str, Any] | None:
        return None


class AfterModelMiddleware(AgentMiddleware):
    """Middleware with only after_model hook."""

    def after_model(self, state: AgentState, runtime) -> dict[str, Any] | None:
        return None


class BeforeAgentMiddleware(AgentMiddleware):
    """Middleware with only before_agent hook."""

    def before_agent(self, state: AgentState, runtime) -> dict[str, Any] | None:
        return None


class AfterAgentMiddleware(AgentMiddleware):
    """Middleware with only after_agent hook."""

    def after_agent(self, state: AgentState, runtime) -> dict[str, Any] | None:
        return None


def binary_name(
    has_tools: bool,
    before_agent: bool,
    before_model: bool,
    after_model: bool,
    after_agent: bool,
) -> str:
    """Generate binary name for configuration.

    Bit positions:
    - Bit 0: has_tools
    - Bit 1: before_agent
    - Bit 2: before_model
    - Bit 3: after_model
    - Bit 4: after_agent
    """
    bits = [
        "1" if has_tools else "0",
        "1" if before_agent else "0",
        "1" if before_model else "0",
        "1" if after_model else "0",
        "1" if after_agent else "0",
    ]
    return "".join(bits)


def clean_mermaid_diagram(mermaid: str, language: str = "python") -> str:
    """Clean up Mermaid diagram by simplifying node names and improving styling.

    Args:
        mermaid: Raw Mermaid diagram from LangGraph.
        language: "python" for snake_case or "javascript" for camelCase naming.

    Returns:
        Cleaned Mermaid diagram with simplified node names.
    """
    import re

    # Replace middleware class names with simple hook names in node labels
    # Pattern matches: node_id(ClassName.hook_name) -> node_id(hook_name)
    if language == "javascript":
        replacements = [
            (r'\(BeforeAgentMiddleware\.before_agent\)', '(beforeAgent)'),
            (r'\(BeforeModelMiddleware\.before_model\)', '(beforeModel)'),
            (r'\(AfterModelMiddleware\.after_model\)', '(afterModel)'),
            (r'\(AfterAgentMiddleware\.after_agent\)', '(afterAgent)'),
            # Also update escaped versions in node IDs
            (r'BeforeAgentMiddleware\\2ebefore_agent', 'BeforeAgentMiddleware'),
            (r'BeforeModelMiddleware\\2ebefore_model', 'BeforeModelMiddleware'),
            (r'AfterModelMiddleware\\2eafter_model', 'AfterModelMiddleware'),
            (r'AfterAgentMiddleware\\2eafter_agent', 'AfterAgentMiddleware'),
        ]
    else:  # python
        replacements = [
            (r'\(BeforeAgentMiddleware\.before_agent\)', '(before_agent)'),
            (r'\(BeforeModelMiddleware\.before_model\)', '(before_model)'),
            (r'\(AfterModelMiddleware\.after_model\)', '(after_model)'),
            (r'\(AfterAgentMiddleware\.after_agent\)', '(after_agent)'),
        ]

    # Common replacements for both languages
    replacements.extend([
        # Remove <p> tags from start/end nodes to make them normal size
        (r'__start__\(\[<p>__start__</p>\]\)', '__start__([__start__])'),
        (r'__end__\(\[<p>__end__</p>\]\)', '__end__([__end__])'),
    ])

    for pattern, replacement in replacements:
        mermaid = re.sub(pattern, replacement, mermaid)

    # Add more compact layout configuration
    # Replace the config section to make diagrams more compact
    config_pattern = r'---\nconfig:\n  flowchart:\n    curve: linear\n---\n'
    compact_config = '''---
config:
  flowchart:
    curve: linear
    nodeSpacing: 30
    rankSpacing: 40
    padding: 10
---
'''
    mermaid = re.sub(config_pattern, compact_config, mermaid)

    return mermaid


def generate_all_diagrams(language: str = "python") -> dict[str, str]:
    """Generate Mermaid diagrams for all 32 possible hook combinations.

    Args:
        language: "python" for snake_case or "javascript" for camelCase naming.

    Returns:
        Dictionary mapping binary configuration names to Mermaid diagram strings.
    """
    model = DemoModel()
    diagrams = {}

    # Generate all 32 combinations (2^5)
    for i in range(32):
        # Extract bits
        has_tools = bool(i & 0b00001)
        before_agent = bool(i & 0b00010)
        before_model = bool(i & 0b00100)
        after_model = bool(i & 0b01000)
        after_agent = bool(i & 0b10000)

        # Build middleware list
        middleware = []
        if before_agent:
            middleware.append(BeforeAgentMiddleware())
        if before_model:
            middleware.append(BeforeModelMiddleware())
        if after_model:
            middleware.append(AfterModelMiddleware())
        if after_agent:
            middleware.append(AfterAgentMiddleware())

        # Generate binary name
        name = binary_name(
            has_tools,
            before_agent,
            before_model,
            after_model,
            after_agent,
        )

        # Create agent and generate diagram
        tools = [demo_tool] if has_tools else []
        agent = create_agent(model=model, tools=tools, middleware=middleware)

        mermaid = agent.get_graph().draw_mermaid()
        # Clean up node names
        mermaid = clean_mermaid_diagram(mermaid, language=language)
        diagrams[name] = mermaid

        print(f"Generated: {name} (tools={int(has_tools)}, "
              f"before_agent={int(before_agent)}, before_model={int(before_model)}, "
              f"after_model={int(after_model)}, after_agent={int(after_agent)})")

    return diagrams


def save_diagrams_to_inline_js(diagrams: dict[str, str], output_path: Path) -> None:
    """Save diagrams as an inline JavaScript constant file.

    This is needed because Mintlify's dev server doesn't serve JSON files.
    By converting to a JS file, the diagrams data can be loaded via <script src>.

    Args:
        diagrams: Dictionary mapping binary names to Mermaid diagrams.
        output_path: Path where the JS file should be saved.
    """
    # Minified JSON (no whitespace)
    json_str = json.dumps(diagrams, separators=(',', ':'))
    js_content = f'const diagrams = {json_str};'

    output_path.write_text(js_content)
    print(f"Saved inline JS version to {output_path}")


def main() -> None:
    """Generate all diagrams and save to both JSON and inline JS formats."""
    # Generate Python version (snake_case)
    print("\nGenerating Python diagrams (snake_case)...")
    python_diagrams = generate_all_diagrams(language="python")

    # Generate JavaScript version (camelCase)
    print("\nGenerating JavaScript diagrams (camelCase)...")
    js_diagrams = generate_all_diagrams(language="javascript")

    # Save to same directory as script
    output_dir = Path(__file__).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save as inline JS files (for Mintlify to serve)
    python_js_path = output_dir / "diagrams_python.js"
    save_diagrams_to_inline_js(python_diagrams, python_js_path)

    js_js_path = output_dir / "diagrams_js.js"
    save_diagrams_to_inline_js(js_diagrams, js_js_path)


if __name__ == "__main__":
    main()
