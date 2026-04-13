from dataclasses import dataclass
from agents.orchestractor import Orcherstrator, OrchestrationResults


@dataclass
class ReviewState:
    """
    Tracks the state of an actie feedback loop.
    Holds the latest result and iteration count.
    """
    result: OrchestrationResults
    iteration: int= 0
    done: bool= False
    message: str= ""


class ReviewCoordinator:
    """
    Manges the human-in-the-loop feedback cycle.

    Pattern:
    1. User reviews the agent output
    2. If satisfied: done
    3. If not: providec feedback, Orchestrator revises,
        loop back to step 1

    This continues until the user is statisfied or
    hits the max intration limit (prevents infinite loops)
    
    """

    MAX_ITERATION= 5 # prevents runaway revision loops

    def __init__(self, orchestrator: Orcherstrator):
        self.orchestrator= orchestrator

    def start(self, result: OrchestrationResults) -> ReviewState:
        """
        Begin a review cycle with an initial result.

        Args:
            result: the OrchestrationResults to review

        Returns:
            ReviewState with iteration=0
        """
        return ReviewState(
            result= result,
            iteration= 0,
            done= False,
            message= "Review the output above. Are you satisfied"
        )
    
    def handle(
            self,
            state: ReviewState,
            satisfied: bool,
            feedback: str= "",
    ) -> ReviewState:
        """
        Processes user satisfaction response.

        Args:
            state: current ReviewState
            satisfied: True if user is happy, False if they want changes
            feedback: revision instructions (required of mpt satisfied)
        
        Returns:
            Updated ReviewState
        """
        # User iteration reached - prevent infinte loops
        if state.iteration >= self.MAX_ITERATION:
            return ReviewState(
                result= self.state.result,
                iteration= state.iteration,
                done= True,
                message= (
                    f"Max revisions ({self.MAX_ITERATION}) reached."
                    "Using the latest version."
                ),
            )
        
        # Validate feedback is provided
        if not feedback or not feedback.strip():
            return ReviewState(
                result= state.result,
                iteration= state.iteration,
                done= False,
                message= "Please provide feedback so Quark AI knows what to improve."
            )
        
        # Run revision
        print(f"Revision {state.iteration + 1} of {self.MAX_ITERATION} ...")

        revised_result = self.orchestrator.revise(
            result= state.result,
            feedback= feedback.strip()
        )

        return ReviewState(
            result=revised_result,
            iteration= state.iteration + 1,
            done= False,
            message= f"Revised (iteration {state.iteration +1}). Review the updated output."
        )
