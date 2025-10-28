from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import traci
import uvicorn
import threading
import time

from agent import DQNAgent
from simulation import get_state

CONFIG_FILE = "cross3ltl.sumocfg"
lanes = ["1fi_0", "2fi_0", "3fi_0", "4fi_0"]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

agent = DQNAgent(state_size=5, action_size=2)
metrics = {"step": 0, "queue_lengths": [0, 0, 0, 0], "wait_time": 0}

MIN_GREEN = 10
MAX_GREEN = 30


def run_simulation():
    global metrics
    traci.start(["sumo-gui", "-c", CONFIG_FILE])

    # start phase = lane with most vehicles
    queue_lengths = [traci.lane.getLastStepHaltingNumber(l) for l in lanes]
    best_lane = queue_lengths.index(max(queue_lengths))
    current_phase = best_lane * 2
    traci.trafficlight.setPhase("0", current_phase)
    traci.trafficlight.setPhaseDuration("0", MIN_GREEN)
    time_in_phase = 0
    prev_wait = 0

    for step in range(200):
        traci.simulationStep()
        time_in_phase += 1

        state = get_state()
        action = agent.act(state)

        # queue info
        queue_lengths = [traci.lane.getLastStepHaltingNumber(l) for l in lanes]
        max_queue = max(queue_lengths)
        current_queue = queue_lengths[current_phase // 2]

        can_switch = False

        # ---- SWITCH LOGIC ----
        # 1. Never give green to empty lane if others waiting
        if current_queue == 0 and max_queue > 0:
            can_switch = True

        # 2. Force switch if max green reached
        elif time_in_phase >= MAX_GREEN:
            can_switch = True

        # 3. After min green, if another lane has more cars → switch
        elif time_in_phase >= MIN_GREEN and current_queue < max_queue:
            can_switch = True

        # ----------------------

        if can_switch:
            current_phase = (
                (current_phase + 2)
                % len(traci.trafficlight.getCompleteRedYellowGreenDefinition("0")[0].phases)
            )
            traci.trafficlight.setPhase("0", current_phase)
            traci.trafficlight.setPhaseDuration("0", MIN_GREEN)
            time_in_phase = 0

        # reward & training
        total_stopped = sum(traci.lane.getLastStepHaltingNumber(l) for l in lanes)
        reward = prev_wait - total_stopped
        prev_wait = total_stopped
        next_state = get_state()
        agent.train(state, action, reward, next_state, done=False)

        # update shared metrics
        metrics = {
            "step": step,
            "queue_lengths": queue_lengths,
            "wait_time": total_stopped,
            "phase": current_phase,
            "time_in_phase": time_in_phase,
        }

        time.sleep(0.5)

    traci.close()



@app.get("/metrics")
def get_metrics():
    return metrics


if __name__ == "__main__":
    sim_thread = threading.Thread(target=run_simulation, daemon=True)
    sim_thread.start()
    uvicorn.run(app, host="0.0.0.0", port=8000)
