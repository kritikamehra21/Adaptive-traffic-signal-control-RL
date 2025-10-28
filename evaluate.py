import traci
from agent import DQNAgent
from simulation import get_state, CONFIG_FILE, lanes

def run_eval(use_rl=True, steps=200):
    agent = DQNAgent(state_size=5, action_size=2)
    agent.model.load_weights("trained_model.h5")
    traci.start(["sumo-gui", "-c", CONFIG_FILE])

    total_waits = []
    for step in range(steps):
        traci.simulationStep()
        state = get_state()

        if use_rl:
            action = agent.act(state)
            if action == 1:
                current_phase = traci.trafficlight.getPhase("0")
                phases = traci.trafficlight.getCompleteRedYellowGreenDefinition("0")[0].phases
                traci.trafficlight.setPhase("0", (current_phase + 1) % len(phases))
        else:
            if step % 20 == 0:  # naive fixed controller
                current_phase = traci.trafficlight.getPhase("0")
                traci.trafficlight.setPhase("0", (current_phase + 1) % 2)

        total_wait = sum(traci.lane.getLastStepHaltingNumber(l) for l in lanes)
        total_waits.append(total_wait)

    traci.close()
    return sum(total_waits) / steps

if __name__ == "__main__":
    print("Avg wait (RL):", run_eval(use_rl=True))
    print("Avg wait (Fixed):", run_eval(use_rl=False))
