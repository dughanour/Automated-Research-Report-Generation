from pydantic import BaseModel, Field
from typing import Annotated, List
from langgraph.graph import MessagesState
from typing_extensions import TypedDict
import operator

# ============================================================
#                     DATA MODELS
# ============================================================
class Section(BaseModel):
    """A section of a document (e.g., "Market Analysis" section)."""
    title: str
    content: str


class Analyst(BaseModel):
    """An analyst."""
    affiliation: str = Field(..., description="The affiliation of the analyst.") # e.g., "Stanford University"
    name: str = Field(..., description="The name of the analyst.")               # e.g., "Dr. Sarah Chen"
    role: str = Field(..., description="Role of the analyst in the context of the topic.")               # e.g., "AI Ethics Researcher"
    description: str = Field(..., description="Description of the analyst's focus, concerns, and motives.") # e.g., "Focuses on bias in healthcare AI..."
    
    @property
    def persona(self) -> str:
        """The persona of the analyst."""
        return(
            f"Name: {self.name}\n"
            f"Role: {self.role}\n"
            f"Affiliation: {self.affiliation}\n"
            f"Description: {self.description}\n"
        )


class Perspectives(BaseModel):
    """A container for multiple analysts."""
    analysts: List[Analyst] =  Field(..., description="List of analysts with their roles and affiliations.")

class SearchQuery(BaseModel):
    """Output parser for the search queries."""
    search_query: str = Field(None, description="The search query to be used to find relevant documents.")

# ============================================================
#                     STATE CLASSES
# ============================================================

class GenerateAnalystsState(TypedDict):
    """State for analyst generation phase."""
    topic: str = Field(..., description="Research topic from user.")
    max_analysts: int = Field(3, description="Maximum number of analysts to generate.")
    human_analyst_feedback: str   # Feedback from human review
    analysts: List[Analyst]   # Generated analyst personas

class InterviewState(MessagesState):
    """State for the interview subgraph"""
    max_num_turns: int                              # Max interview turns allowed
    context: Annotated[list, operator.add]          # Search results (COMBINES from parallel searches)
    analyst: Analyst                                # Current analyst conducting interview
    interview: str                                  # Full interview transcript
    sections: list                                  # Generated sections from this interview

class ResearchGraphState(TypedDict):
    """Main state for the entire research workflow."""
    topic: str                                      # Research topic
    max_analysts: int                               # Number of analysts to create
    human_analyst_feedback: str                     # Human feedback on analysts
    analysts: List[Analyst]                         # All analyst personas
    sections: Annotated[list, operator.add]         # All sections (COMBINES from all interviews)
    introduction: str                               # Report introduction
    content: str                                    # Main report body
    conclusion: str                                 # Report conclusion
    final_report: str                               # Final compiled report










