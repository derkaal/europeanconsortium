"""Convergence test node - checks if agents have converged.

Implements cumulative convergence criteria with tier-based gates.

Changes from original:
- Tier-1 BLOCKs cannot be averaged away (require waiver or redesign)
- Tier-2 BLOCKs require explicit tradeoff documentation
- Tier-3 BLOCKs are advisory only
- Philosopher BLOCKs trigger Values Escalation Report
"""

import logging
from typing import Dict, Any

from ..state import ConsortiumState

logger = logging.getLogger(__name__)


def convergence_test_node(state: ConsortiumState) -> Dict[str, Any]:
    """Test if agent responses have converged.
    
    Convergence Criteria (ALL must be met):
    1. Zero BLOCK ratings
    2. Max 2 WARN ratings with mitigations
    3. Combined confidence >70%
    4. ≥60% agents rate ACCEPT/ENDORSE
    
    FORCED CONVERGENCE: After 5 iterations, force convergence to prevent
    infinite loops, even if criteria not met.
    
    LANGGRAPH PATTERN: Return partial state update with convergence_status.
    
    Args:
        state: Current consortium state
        
    Returns:
        Partial state update with convergence_status and iteration_count
    """
    responses = state.get("agent_responses", {})
    iteration_count = state.get("iteration_count", 0)
    
    # Increment iteration counter
    new_iteration_count = iteration_count + 1
    
    if not responses:
        logger.warning("No agent responses to test for convergence")
        return {
            "convergence_status": {
                "converged": False,
                "reason": "No agent responses yet"
            },
            "iteration_count": new_iteration_count
        }
    
    logger.info(
        f"Testing convergence for {len(responses)} agent responses "
        f"(iteration {new_iteration_count})"
    )
    
    # FORCED CONVERGENCE: After 3 iterations, stop regardless
    MAX_ITERATIONS = 3
    if new_iteration_count >= MAX_ITERATIONS:
        logger.warning(
            f"⚠ FORCED CONVERGENCE after {new_iteration_count} iterations"
        )
        return {
            "convergence_status": {
                "converged": True,
                "reason": (
                    f"Forced convergence after {new_iteration_count} "
                    f"iterations (max: {MAX_ITERATIONS})"
                ),
                "forced": True,
                "iteration_count": new_iteration_count
            },
            "iteration_count": new_iteration_count
        }
    
    # Check 1: Convergence Gates (Tier-based BLOCK handling)
    # Load and check convergence gates
    try:
        from .convergence_gates import ConvergenceGates, load_convergence_config

        config = load_convergence_config()
        gates = ConvergenceGates(config)

        can_proceed, gate_status = gates.check_convergence_gates(
            responses,
            state.get("context", {})
        )

        if not can_proceed:
            logger.info(
                f"Convergence blocked by gates: {gate_status['gate_decision']} "
                f"(iteration {new_iteration_count}/{MAX_ITERATIONS})"
            )
            return {
                "convergence_status": {
                    "converged": False,
                    "reason": gate_status["message"],
                    "gate_status": gate_status,
                    "iteration_count": new_iteration_count
                },
                "iteration_count": new_iteration_count
            }

        # If gates passed but there were BLOCKs with waivers, include in status
        if gate_status.get("waivers_applied"):
            logger.info(
                f"Convergence gates passed with {len(gate_status['waivers_applied'])} waiver(s) applied"
            )

    except Exception as e:
        logger.warning(f"Convergence gates check failed, falling back to legacy logic: {e}")
        # Fallback to legacy logic
        blocks = [
            aid for aid, r in responses.items()
            if r.get("rating") == "BLOCK"
        ]
        if blocks:
            logger.info(
                f"Convergence failed: {len(blocks)} BLOCK ratings "
                f"(iteration {new_iteration_count}/{MAX_ITERATIONS})"
            )
            return {
                "convergence_status": {
                    "converged": False,
                    "reason": f"Blocking concerns from: {', '.join(blocks)}",
                    "blocking_agents": blocks,
                    "iteration_count": new_iteration_count
                },
                "iteration_count": new_iteration_count
            }
        gate_status = None  # No gate status if using legacy logic
    
    # Check 2: Max 2 WARN ratings
    warns = [
        aid for aid, r in responses.items()
        if r.get("rating") == "WARN"
    ]
    if len(warns) > 2:
        logger.info(f"Convergence failed: {len(warns)} WARN ratings")
        return {
            "convergence_status": {
                "converged": False,
                "reason": (
                    f"Too many warnings ({len(warns)} > 2): "
                    f"{', '.join(warns)}"
                ),
                "iteration_count": new_iteration_count
            },
            "iteration_count": new_iteration_count
        }
    
    # Check 3: Combined confidence >70%
    confidences = [
        r.get("confidence", 0.0) for r in responses.values()
    ]
    avg_confidence = (
        sum(confidences) / len(confidences) if confidences else 0
    )
    # Convert to percentage
    avg_confidence_pct = avg_confidence * 100
    
    if avg_confidence_pct <= 70:
        logger.info(
            f"Convergence failed: Low confidence "
            f"({avg_confidence_pct:.1f}%)"
        )
        return {
            "convergence_status": {
                "converged": False,
                "reason": (
                    f"Insufficient confidence "
                    f"({avg_confidence_pct:.1f}% ≤ 70%)"
                ),
                "avg_confidence": avg_confidence_pct,
                "iteration_count": new_iteration_count
            },
            "iteration_count": new_iteration_count
        }
    
    # Check 4: ≥60% ACCEPT/ENDORSE
    positive = [
        aid for aid, r in responses.items()
        if r.get("rating") in ["ACCEPT", "ENDORSE"]
    ]
    positive_pct = (
        (len(positive) / len(responses)) * 100 if responses else 0
    )
    
    if positive_pct < 60:
        logger.info(
            f"Convergence failed: Low agreement ({positive_pct:.0f}%)"
        )
        return {
            "convergence_status": {
                "converged": False,
                "reason": (
                    f"Insufficient agreement ({positive_pct:.0f}% < 60%)"
                ),
                "positive_percentage": positive_pct,
                "iteration_count": new_iteration_count
            },
            "iteration_count": new_iteration_count
        }
    
    # All checks passed!
    logger.info(
        f"✓ CONVERGENCE ACHIEVED "
        f"(confidence: {avg_confidence_pct:.1f}%, "
        f"agreement: {positive_pct:.0f}%)"
    )

    convergence_status = {
        "converged": True,
        "reason": "All convergence criteria met",
        "avg_confidence": avg_confidence_pct,
        "positive_percentage": positive_pct,
        "positive_ratings": len(positive),
        "warn_ratings": len(warns),
        "iteration_count": new_iteration_count
    }

    # Include gate status if available
    if gate_status:
        convergence_status["gate_status"] = gate_status

    return {
        "convergence_status": convergence_status,
        "iteration_count": new_iteration_count
    }
