from random import *
from math import *
from time import sleep
import sys
import subprocess

# genome encoding: [x, y]

def create_base():
	return random()*10 - 5

def initialize_population(size):
	population = []
	for individual in range(size):
		x = create_base()
		y = create_base()
		population.append([x, y])
	return population

def display(population):
	global mutation_rate
	print('Mutation Rate: ' + str(mutation_rate) + '\n')
	for rank in range(POP_SIZE):
		print('{:2d})\t({: 5.3f}, {: 5.3f})\tCost: {: 6.4f}'.format(\
			rank+1, population[rank][0], population[rank][1], cost(population[rank])))

def get_coordinates(genome):
	return genome[0], genome[1]

def cost(genome):
	# minimize Rastrigin Function
	x, y = get_coordinates(genome)
	cost = 20 + x**2 - 10*cos(2*pi*x) + y**2 - 10*cos(2*pi*y)
	return cost

def rank(population):
	population.sort(key = cost) #sort coordinates by f(x,y) = cost from min to max

def breed(population):
	new_population = []
	# elitism for top 10%
	for elite in range(POP_SIZE//10):
		new_population.append(population[elite])
	#population_spread = cost(population[POP_SIZE]) - cost(population[0])
	for elite_parent_index in range(POP_SIZE//10):
		for num_children in range(1,10):
			baby = cross(population[elite_parent_index], population[elite_parent_index+num_children])
			new_population.append(baby)

	return new_population

def cross(genome_1, genome_2):
	cross_point = randint(0,GENOME_LENGTH)
	new_genome = genome_1[0:cross_point] + genome_2[cross_point:]
	new_genome = mutate(new_genome)
	return new_genome

def mutate(genome):
	global convergence
	global mutation_rate
	# ~80% mutation rate at threshold, ~20% baseline, see plot in Mathematica
	mutation_rate = sigmoid(convergence[1]-CONVERGENCE_THRESHOLD)**(1/3)
	for base_num in range(len(genome)):
		coin_flip = random()
		if coin_flip <= mutation_rate: genome[base_num] = create_base()
	return genome

def sigmoid(x):
	return 1/(1+e**(-x))

def update_convergence(cost, generation):
	global convergence
	if abs(convergence[0] - cost) <= CHANGE_IN_COST_THRESHOLD: convergence[1] += 1
	else: convergence[1] = 0; convergence[0] = cost

# CONSTANTS
GENOME_LENGTH = 2
POP_SIZE = 100 # divisible by 10
GENERATIONS = 20
CHANGE_IN_COST_THRESHOLD = 0.1
CONVERGENCE_THRESHOLD = 5

def main():	


	theproc = subprocess.Popen([sys.executable, "run_test.py"])
  theproc.communicate()


	global convergence
	global mutation_rate
	convergence = [] #[cost, num_generations], if num_generations is high, local/global min has been reached

	population = initialize_population(POP_SIZE)
	rank(population)
	convergence = [cost(population[0]), 0]
	mutation_rate = 0
	print('GENERATION 0:\n')
	display(population)

	for generation in range(GENERATIONS):
		if generation%100 == 0: sleep(1)
		population = breed(population)
		rank(population)
		update_convergence(cost(population[0]), generation)
		print('\nGENERATION '+str(generation+1) + ':\n')
		display(population)

	print('\nNatural Selection picks ' + str(population[0]) + ' as most fit with cost ' + str(cost(population[0]))+'\n')

if __name__== '__main__': main()