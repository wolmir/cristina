import random


symbol_list = ['a', 'b', 'c', 'd']


def generate_word(word_size):
    return [random.choice(symbol_list) for _ in range(word_size)]


class WordPopulation:
    def __init__(self, mutation_rate, population_size, word):
        self.mutation_rate = mutation_rate
        self.population_size = population_size
        self.word = word
        self.population = [(generate_word(len(word)), 0) for _ in range(population_size)]

    def finished(self):
        return self.population[0][0] == self.word


def main():
    word = generate_word(100)
    mutation_rate = 0.01
    population_size = 100
    word_population = WordPopulation(mutation_rate, population_size, word)
    generation_counter = 0
    while not word_population.finished():
        word_population.new_generation()
        generation_counter += 1
    print generation_counter


if __name__ == '__main__':
    main()