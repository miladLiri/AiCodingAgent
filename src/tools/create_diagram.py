from langchain.tools import tool
from langchain_openai import ChatOpenAI
from pathlib import Path
from src.config import *


@tool
def create_diagram(diagram_description: str) -> str:
    """Creates a diagram (.mmd file) from a text description.
    Input should be a natural language description of the diagram you want to create."""

    system_message = """You are a Mermaid diagram expert. Convert user descriptions into valid Mermaid syntax.

Rules:
- Output ONLY the Mermaid code, no explanations or markdown fences
- Use appropriate diagram type (flowchart, sequence, class, ER, etc.)
- Keep syntax clean and valid
- Use meaningful node IDs and labels
- For flowcharts use TB (top-bottom) or LR (left-right) direction
- When labels contain any of these, wrap them in quotes: parentheses () slashes / line breaks colons long descriptive text
- Use mermaid version v11.x
- Common patterns:
  * Flowchart: graph TD; A[Start] --> B[Process]
  * Sequence: sequenceDiagram; Alice->>Bob: Message
  * Class: classDiagram; Class1 --|> Class2
  * ER: erDiagram; CUSTOMER ||--o{ ORDER : places

Example input: "Create a flowchart showing user login process"
Example output:
graph TD
    A[User visits site] --> B{Logged in?}
    B -->|Yes| C[Show dashboard]
    B -->|No| D[Show login page]
    D --> E[Enter credentials]
    E --> F{Valid?}
    F -->|Yes| C
    F -->|No| D
"""

    llm = ChatOpenAI(model=MODEL_NAME, base_url=LLM_BASE_URL, api_key=LLM_API_KEY, temperature=0.1)

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": diagram_description}
    ]

    response = llm.invoke(messages)
    mermaid_code = response.content.strip()

    # Generate filename from description
    safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_'
    for c in diagram_description[:50])
    safe_name = "_".join(safe_name.split())
    filename = f"{safe_name}.mmd"

    # Save to current directory
    filepath = Path.cwd() / filename
    filepath.write_text(mermaid_code, encoding='utf-8')

    return f"Mermaid diagram saved to {filename}\n\nContent:\n{mermaid_code}"