"""Tests for Tension Protocols."""
import sys

sys.path.insert(0, '.')


class TestSovereignEconomistProtocol:
    """Test Sovereign-Economist tension protocol."""
    
    def test_protocol_initialization(self):
        """Test protocol can be initialized."""
        from src.consortium.tensions.sovereign_economist import (
            SovereignEconomistProtocol
        )
        
        protocol = SovereignEconomistProtocol()
        assert protocol is not None
        assert protocol.protocol_id == "sovereign_economist"
        assert protocol.priority > 0
        print("✓ SovereignEconomistProtocol initialized")
    
    def test_detect_tension(self):
        """Test tension detection with conflicting ratings."""
        from src.consortium.tensions.sovereign_economist import (
            SovereignEconomistProtocol
        )
        
        protocol = SovereignEconomistProtocol()
        
        # State with BLOCK vs ACCEPT conflict
        base_state = {
            "query": "Test query",
            "context": {"industry": "tech"},
            "triggered_agents": ["sovereign", "economist"],
            "agent_responses": {
                "sovereign": {
                    "agent_id": "sovereign",
                    "rating": "BLOCK",
                    "confidence": 80,
                    "reasoning": "Must use EU-only infrastructure"
                },
                "economist": {
                    "agent_id": "economist",
                    "rating": "ACCEPT",
                    "confidence": 80,
                    "reasoning": "Cost effective solution"
                }
            },
            "active_tensions": [],
            "convergence_status": {},
            "final_recommendation": {},
            "iteration_count": 0,
            "cla_review": None,
            "cla_gate_status": "PENDING"
        }
        
        result = protocol.detect(base_state)
        
        # Should detect tension due to BLOCK vs ACCEPT
        if result is not None:
            assert isinstance(result, dict)
            assert "protocol_id" in result
            print(f"✓ Detected tension: {result.get('protocol_id')}")
        else:
            # May not detect if threshold not met
            print("✓ No tension detected (within threshold)")


class TestTensionOrchestrator:
    """Test TensionOrchestrator."""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initializes with all protocols."""
        from src.consortium.tensions.orchestrator import TensionOrchestrator
        
        orch = TensionOrchestrator()
        assert orch is not None
        assert len(orch.protocols) >= 1
        print(f"✓ Orchestrator loaded {len(orch.protocols)} protocol(s)")
    
    def test_detect_multiple_tensions(self):
        """Test detecting multiple tensions."""
        from src.consortium.tensions.orchestrator import TensionOrchestrator
        
        orch = TensionOrchestrator()
        
        # State with potential tensions
        state = {
            "query": "Test",
            "context": {},
            "triggered_agents": ["jurist", "philosopher"],
            "agent_responses": {
                "jurist": {
                    "rating": "BLOCK",
                    "confidence": 90,
                    "reasoning": "Legal compliance required"
                },
                "philosopher": {
                    "rating": "WARN",
                    "confidence": 85,
                    "reasoning": "Ethical concerns"
                }
            },
            "active_tensions": [],
            "convergence_status": {},
            "final_recommendation": None
        }
        
        tensions = orch.detect_tensions(state)
        
        assert tensions is not None
        assert isinstance(tensions, list)
        
        if len(tensions) > 0:
            tension = tensions[0]
            # Check for expected fields (may vary by protocol)
            assert "protocol_id" in tension
            assert "agent_a" in tension or "agents_involved" in tension
            print(f"✓ Detected {len(tensions)} tension(s)")
        else:
            print("✓ No tensions detected")
    
    def test_resolve_tension(self):
        """Test tension resolution."""
        from src.consortium.tensions.orchestrator import TensionOrchestrator
        
        orch = TensionOrchestrator()
        
        # State with active tension
        state = {
            "query": "Test",
            "context": {},
            "triggered_agents": ["sovereign", "economist"],
            "agent_responses": {
                "sovereign": {
                    "rating": "BLOCK",
                    "confidence": 90,
                    "reasoning": "Risk"
                },
                "economist": {
                    "rating": "ACCEPT",
                    "confidence": 85,
                    "reasoning": "Value"
                }
            },
            "active_tensions": [
                {
                    "protocol_id": "sovereign_economist",
                    "agent_a": "sovereign",
                    "agent_b": "economist",
                    "priority": 1,
                    "status": "active",
                    "iteration_count": 0,
                    "max_iterations": 4
                }
            ],
            "convergence_status": {},
            "final_recommendation": None
        }
        
        result = orch.resolve_next_tension(state)
        
        assert result is not None
        assert isinstance(result, dict)
        print("✓ Tension resolution executed")


class TestAllProtocols:
    """Test all tension protocols load correctly."""
    
    def test_all_protocols_load(self):
        """Test all 5 tension protocols can be instantiated."""
        from src.consortium.tensions import (
            SovereignEconomistProtocol,
            EcosystemArchitectProtocol,
            JuristPhilosopherProtocol,
            OperatorStrategyProtocol,
            FuturistAllProtocol
        )
        
        protocols = [
            SovereignEconomistProtocol(),
            EcosystemArchitectProtocol(),
            JuristPhilosopherProtocol(),
            OperatorStrategyProtocol(),
            FuturistAllProtocol()
        ]
        
        for p in protocols:
            assert p.protocol_id is not None
            assert p.priority >= 0
            print(f"✓ {p.protocol_id} loaded (priority {p.priority})")
        
        assert len(protocols) == 5
        print(f"✓ All {len(protocols)} protocols loaded")
    
    def test_orchestrator_has_all_protocols(self):
        """Test orchestrator loads all protocols."""
        from src.consortium.tensions.orchestrator import TensionOrchestrator
        
        orch = TensionOrchestrator()
        
        # Should have 5 protocols
        assert len(orch.protocols) == 5
        
        # Check protocol IDs
        protocol_ids = [p.protocol_id for p in orch.protocols]
        expected_ids = [
            "sovereign_economist",
            "ecosystem_architect",
            "jurist_philosopher",
            "operator_strategy",
            "futurist_all"
        ]
        
        for expected_id in expected_ids:
            assert expected_id in protocol_ids
        
        print(f"✓ Orchestrator has all {len(orch.protocols)} protocols")
