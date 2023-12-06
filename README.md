[FlapPyBird](https://sourabhv.github.io/FlapPyBird)
===============

This project consists of an AI agent to play Flappy Bird and was built over [FlapPyBird](https://github.com/sourabhv/FlapPyBird).


# Install
---------

To install this project you must have python 3.9 or 3.10.

If you use conda just create a new environment and activate it using

```bash
conda create --name flappy-ai python=3.10
conda activate flappy-ai
```

Navigate to this repo in your terminal and install the project and dependencies

```bash
pip install -e .
```

Finally, to run, just execute main.py

```bash
python main.py
```

# AI
-----

The AI model is a feed forward neural network with 5 inputs, 2 hidden layers (6 and 3 neurons respectively) and 1 output neuron.

https://github.com/phdomingues/FlapPyBird-AI/assets/30188500/04153d2e-1628-4add-8d40-a2ba92e17edc

## Inputs
----------

![Inputs](/readme_assets/inputs.png)

- **B<sub>y</sub>**: Bird height (distance in pixels from the top);
- **Tp<sub>x</sub>**: Horizontal distance from bird to the next top pipe;
- **Tp<sub>y</sub>**: Vertical distance from bird to the next top pipe;
- **Bp<sub>x</sub>**: Horizontal distance from bird to the next bottom pipe;
- **Bp<sub>y</sub>**: Vertical distance from bird to the next bottom pipe.

As noticeable in the previous Figure, inputs Tp<sub>x</sub> and Bp<sub>x</sub> have the same value. This was by design, envisioning that I or someone else could want to make the game harder by adding different speeds or offsets to the bottom and top pipes.

For the same reason, the neural network design is oversized, in case the game changes and it needs to learn more complex behaviors.

## Output

The output is a value normalized between 0-1 using a sigmoid activation function. Values greater or equal to 0.5 are interpreted as jump and values below as "do nothing".

## Training

https://github.com/phdomingues/FlapPyBird-AI/assets/30188500/5ac1f57a-ee05-47df-a8d8-adff3d304da0

Learning occurs by freezing all weights and training via a genetic algorithm, as described below.

Birds associated with a neural network are referred to as individuals.

1. N Neural Networks are created with random weights and bias;
2. All individuals then play the game until death;
3. If elitism is set to True, the best individual (highest in-game score) is copied to the next generation;
4. A new population, with the same size as the previous, is built by the following logic:
    1. Two individuals are selected to reproduce (the higher score an individual has, the higher its probability of being selected);
    2. The two individuals are encoded (encoded individuals are called chromosomes);
    3. Crossover is performed to generate a new chromosome;
    4. The new chromosome goes through mutation;
    5. The new chromosome is converted back into an individual (actual neural network) and added to the new population;
    6. If the new population size is the same size as the old one, stop reproducing and go to step 5. Otherwise, go back to step 4.1;
5. Delete the old population;
6. If any of the stop conditions are met, stop training and save the best individual. Otherwise, go back to step 2.

### Configuration File

A configs file is available at src/ai/config.yaml. It can be used to configure the following training parameters

1. population_size: Integer > 0;
2. mutation_probability: 0 < Float < 1. The probability of a mutation occurring in a single Gene in the chromosome;
3. mutation_standard_deviation: 0 < Float < 1. Standard deviation used to generate a random value to add or subtract from the mutated gene;
4. elitism: Bool. Turns elitism on or off (elitism = keep the best individual between generations);
5. stop_condition: Set of configurations related to automatic ways to stop training (all can be disabled by setting the value to .inf).
    - generations: Integer > 0. Maximum number of generations to evolve;
    - score: Integer > 0. Maximum score achieved by an individual before stopping;
    - time: Integer > 0. Maximum time (in seconds) to spend training.
6. save_best: Bool. Saves the best model upon closing the game or after finishing training.
7. enable_acceleration: Bool. The game gets faster over time.
8. load_previous_best: Bool. Load the best previous model, saved in a .pth file. 1 individual is set as an exact copy and all others are mutated variants.
9. hardstuck_gen: Integer > 0. The number of generations stuck at score 0 before completely resetting the population, in case the agent gets stuck.

### Chromosome

![Inputs](/readme_assets/chromosome.png)

A chromosome is an array containing 61 values (genes). It is created by sequentially flattening the weights and then the bias for each neuron of the network, from the first to the last layer, as shown in the Figure above.

### Crossover

Crossover consists of creating a mix of the first 30 genes from one parent chromosome and the last 31 from the other.

### Mutation

Mutation is performed using the following algorithm:

1. Iterate through all the genes;
2. Try to mutate (success chance defined in the configuration file);
3. If mutation succeded:
    1. Generate a random value from a normal distribution of mean 0 and standard deviation 0.3 (changeable using the configuration file). This ensures that the gene value can increase or decrease (both positive and negative values can be generated by the distribution) and that small mutations are more common, but large mutations are also possible;
    2. Add the value to the gene (remembering that it can be positive or negative);
4. If there are still more genes go to the next one and return to step 2.

### Visualizer
--------------

A visualizer built using matplotlib displays the neural network for the first individual alive in real-time.

The data is represented using the following logic:
- The first layer of neurons represents the inputs;
- Color on the hidden layers represents the activation of each one;
- Output neuron turns green for jump (activation > 0.5) and red for do nothing (activation < 0.5)
- For all neurons:
    - Green = positive values;
    - Red = negative values;
    - Less saturated colors (closer to white) = values closer to 0;
- Lines represent weights (bias is not shown in this visualization)
    - Green line = Positive weight / Red line = Negative weight;
    - Line width represents value intensity, thicker lines = greater absolute values.
