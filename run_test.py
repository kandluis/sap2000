from main import Simulation

def test(times=50):
    sim = Simulation()
    path = sim.start(1)
    sim.run_simulation(50,outputfolder=path)
    return sim

if __name__ == '__main__':
    sim = test(50)
