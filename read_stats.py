import pickle
import matplotlib.pyplot as plt

# charge les statistiques d'entrainement et les affiche
with open("stats.pkl", "rb") as f:
    stats = pickle.load(f)

    print(type(stats))

    generation = range(len(stats.most_fit_genomes))
    best_fitness = [c.fitness for c in stats.most_fit_genomes]

    plt.plot(generation, best_fitness)
    plt.show()
