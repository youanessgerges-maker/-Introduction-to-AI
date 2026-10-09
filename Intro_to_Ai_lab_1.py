import random

class VacuumEnv:
    def __init__(self, rooms=("A", "B"), dirty=("A", "B"), start="A",
                 p_dirty_again=0.0, p_suck_fail=0.0, seed=None):
        self.rooms = list(rooms)
        self.status = {r: ("Dirty" if r in dirty else "Clean") for r in self.rooms}
        self.loc = start
        self.p_dirty_again = p_dirty_again   # احتمال إن غرفة نضيفة تتوسخ تاني
        self.p_suck_fail = p_suck_fail       # احتمال إن Suck يفشل
        self.rng = random.Random(seed)

    def percept(self):
        return (self.loc, self.status[self.loc])

    def step(self, action):
        i = self.rooms.index(self.loc)
        move_cost = 0.0
        if action == "Suck":
            if self.rng.random() >= self.p_suck_fail:
                self.status[self.loc] = "Clean"
        elif action == "Right" and i < len(self.rooms) - 1:
            self.loc = self.rooms[i + 1]; move_cost = 0.5
        elif action == "Left" and i > 0:
            self.loc = self.rooms[i - 1]; move_cost = 0.5
        # NoOp: مفيش حاجة تحصل
        for r in self.rooms:
            if self.status[r] == "Clean" and self.rng.random() < self.p_dirty_again:
                self.status[r] = "Dirty"
        clean_rooms = sum(s == "Clean" for s in self.status.values())
        return clean_rooms - move_cost



def run(agent, env, steps=20, verbose=False):
    total = 0
    for t in range(steps):
        p = env.percept()
        a = agent(p)
        r = env.step(a)
        total += r
        if verbose:
            print(f"t={t:2d} percept={p!s:18} action={a:6} reward={r:4} status={env.status}")
    return total


# rooms = ("A", "B", "C")

def reflex_vacuum(percept):
    location, status = percept
    if status == "Dirty":
        return "Suck"
    elif location == "A":
        return "Right"
    else:
        return "Left"


class ModelBasedVacuum:
    def __init__(self, rooms=("A", "B")):
        self.rooms = list(rooms)
        self.known_clean = set()

    def __call__(self, percept):
        location, status = percept
        if status == "Dirty":
            self.known_clean.discard(location)
            return "Suck"
        self.known_clean.add(location)
        if len(self.known_clean) == len(self.rooms):
            return "NoOp"
        return "Right" if location == "A" else "Left"


print("=== Reflex ===")
print("score:", run(reflex_vacuum, VacuumEnv(), steps=10, verbose=True))
print("\n=== Model-based ===")
print("score:", run(ModelBasedVacuum(), VacuumEnv(), steps=10, verbose=True))

def evaluate(agent_factory, steps=50, runs=200, **env_kw):
    return sum(run(agent_factory(), VacuumEnv(seed=s, **env_kw), steps) for s in range(runs)) / runs

settings = {
    "Deterministic":                dict(),
    "Dirt comes back (p=0.10)":     dict(p_dirty_again=0.10),
    "Suck fails (p=0.30)":          dict(p_suck_fail=0.30),
}
print(f"{'environment':28}{'Reflex':>10}{'Model-based':>14}")
for name, kw in settings.items():
    r = evaluate(lambda: reflex_vacuum, **kw)
    m = evaluate(lambda: ModelBasedVacuum(), **kw)
    print(f"{name:28}{r:10.2f}{m:14.2f}")