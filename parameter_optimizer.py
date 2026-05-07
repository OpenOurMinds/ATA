"""
Parameter Optimizer
Machine learning-based parameter tuning for self-sustaining ATA system
Uses Bayesian optimization and genetic algorithms for parameter evolution
"""

import random
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class OptimizationMethod(Enum):
    """Methods for parameter optimization"""
    BAYESIAN = "bayesian"
    GENETIC = "genetic"
    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"


@dataclass
class ParameterSpace:
    """Defines the search space for parameters"""
    name: str
    min_value: float
    max_value: float
    current_value: float
    type: str  # "continuous" or "discrete"
    step: Optional[float] = None
    
    def sample(self) -> float:
        """Sample a value from the parameter space"""
        if self.type == "continuous":
            return random.uniform(self.min_value, self.max_value)
        else:
            if self.step:
                steps = int((self.max_value - self.min_value) / self.step)
                step_index = random.randint(0, steps)
                return self.min_value + step_index * self.step
            return random.choice([self.min_value, self.max_value])


@dataclass
class OptimizationResult:
    """Result of parameter optimization"""
    iteration: int
    parameters: Dict[str, float]
    objective_value: float
    timestamp: str
    method: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


class BayesianOptimizer:
    """Bayesian optimization for parameter tuning"""
    
    def __init__(self, parameter_spaces: List[ParameterSpace]):
        self.parameter_spaces = parameter_spaces
        self.history: List[OptimizationResult] = []
        self.best_result: Optional[OptimizationResult] = None
    
    def suggest_parameters(self) -> Dict[str, float]:
        """Suggest next parameters to try based on history"""
        if not self.history:
            # Random initialization
            return {ps.name: ps.sample() for ps in self.parameter_spaces}
        
        # Simple Thompson sampling for exploration/exploitation
        parameters = {}
        for ps in self.parameter_spaces:
            # Weighted sampling around best parameters
            if self.best_result:
                best_val = self.best_result.parameters.get(ps.name, ps.current_value)
                # Explore around best value with some noise
                noise = random.gauss(0, (ps.max_value - ps.min_value) * 0.1)
                suggested = max(ps.min_value, min(ps.max_value, best_val + noise))
                parameters[ps.name] = suggested
            else:
                parameters[ps.name] = ps.sample()
        
        return parameters
    
    def observe(self, parameters: Dict[str, float], objective_value: float):
        """Observe the result of a parameter set"""
        result = OptimizationResult(
            iteration=len(self.history) + 1,
            parameters=parameters,
            objective_value=objective_value,
            timestamp=datetime.now().isoformat(),
            method="bayesian"
        )
        
        self.history.append(result)
        
        if self.best_result is None or objective_value > self.best_result.objective_value:
            self.best_result = result
    
    def get_best_parameters(self) -> Dict[str, float]:
        """Get the best parameters found so far"""
        if self.best_result:
            return self.best_result.parameters
        return {ps.name: ps.current_value for ps in self.parameter_spaces}


class GeneticOptimizer:
    """Genetic algorithm for parameter evolution"""
    
    def __init__(self, parameter_spaces: List[ParameterSpace], population_size: int = 20):
        self.parameter_spaces = parameter_spaces
        self.population_size = population_size
        self.population: List[Dict[str, float]] = []
        self.fitness_scores: List[float] = []
        self.generation = 0
        self.best_individual: Optional[Dict[str, float]] = None
        self.best_fitness: float = float('-inf')
    
    def initialize_population(self):
        """Initialize random population"""
        self.population = []
        for _ in range(self.population_size):
            individual = {ps.name: ps.sample() for ps in self.parameter_spaces}
            self.population.append(individual)
        self.generation = 0
    
    def evaluate(self, fitness_function):
        """Evaluate fitness of population"""
        self.fitness_scores = []
        for individual in self.population:
            fitness = fitness_function(individual)
            self.fitness_scores.append(fitness)
            
            if fitness > self.best_fitness:
                self.best_fitness = fitness
                self.best_individual = individual.copy()
    
    def selection(self, tournament_size: int = 3) -> Dict[str, float]:
        """Tournament selection"""
        tournament = random.sample(list(zip(self.population, self.fitness_scores)), 
                                  min(tournament_size, len(self.population)))
        return max(tournament, key=lambda x: x[1])[0]
    
    def crossover(self, parent1: Dict[str, float], parent2: Dict[str, float]) -> Dict[str, float]:
        """Uniform crossover"""
        child = {}
        for ps in self.parameter_spaces:
            if random.random() < 0.5:
                child[ps.name] = parent1[ps.name]
            else:
                child[ps.name] = parent2[ps.name]
        return child
    
    def mutate(self, individual: Dict[str, float], mutation_rate: float = 0.1) -> Dict[str, float]:
        """Mutation operator"""
        mutated = individual.copy()
        for ps in self.parameter_spaces:
            if random.random() < mutation_rate:
                mutated[ps.name] = ps.sample()
        return mutated
    
    def evolve(self, fitness_function, generations: int = 10):
        """Run genetic algorithm for specified generations"""
        if not self.population:
            self.initialize_population()
        
        for gen in range(generations):
            self.evaluate(fitness_function)
            
            # Create new population
            new_population = []
            
            # Elitism: keep best individual
            if self.best_individual:
                new_population.append(self.best_individual.copy())
            
            # Generate offspring
            while len(new_population) < self.population_size:
                parent1 = self.selection()
                parent2 = self.selection()
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                new_population.append(child)
            
            self.population = new_population
            self.generation += 1
        
        return self.best_individual, self.best_fitness


class ParameterOptimizer:
    """Main parameter optimizer for ATA system"""
    
    def __init__(self):
        self.parameter_spaces = self._define_default_spaces()
        self.optimizer = BayesianOptimizer(self.parameter_spaces)
        self.genetic_optimizer = None
        self.optimization_history: List[OptimizationResult] = []
        self.current_parameters = {ps.name: ps.current_value for ps in self.parameter_spaces}
    
    def _define_default_spaces(self) -> List[ParameterSpace]:
        """Define default parameter spaces for ATA system"""
        return [
            ParameterSpace("soul_count", 10, 1000, 50, "discrete", 10),
            ParameterSpace("workflow_count", 5, 100, 10, "discrete", 5),
            ParameterSpace("activity_count", 5, 50, 10, "discrete", 5),
            ParameterSpace("trust_weight", 0.0, 1.0, 0.3, "continuous", 0.05),
            ParameterSpace("altruism_weight", 0.0, 1.0, 0.25, "continuous", 0.05),
            ParameterSpace("ambition_weight", 0.0, 1.0, 0.2, "continuous", 0.05),
            ParameterSpace("curiosity_weight", 0.0, 1.0, 0.15, "continuous", 0.05),
            ParameterSpace("fear_weight", 0.0, 1.0, 0.1, "continuous", 0.05),
            ParameterSpace("learning_rate", 0.001, 0.1, 0.01, "continuous", 0.001),
            ParameterSpace("exploration_rate", 0.0, 1.0, 0.3, "continuous", 0.05)
        ]
    
    def optimize_for_democratic_index(self, simulation_function, 
                                     method: OptimizationMethod = OptimizationMethod.BAYESIAN,
                                     iterations: int = 10) -> Dict[str, float]:
        """Optimize parameters to maximize democratic index"""
        
        def objective_function(parameters: Dict[str, float]) -> float:
            """Run simulation with parameters and return democratic index"""
            try:
                result = simulation_function(parameters)
                # Extract democratic index from result
                if isinstance(result, dict):
                    return result.get('democratic_index', 0.5)
                return float(result)
            except Exception:
                return 0.0
        
        if method == OptimizationMethod.BAYESIAN:
            for i in range(iterations):
                parameters = self.optimizer.suggest_parameters()
                objective_value = objective_function(parameters)
                self.optimizer.observe(parameters, objective_value)
                
                result = OptimizationResult(
                    iteration=i + 1,
                    parameters=parameters,
                    objective_value=objective_value,
                    timestamp=datetime.now().isoformat(),
                    method="bayesian"
                )
                self.optimization_history.append(result)
            
            best_params = self.optimizer.get_best_parameters()
        
        elif method == OptimizationMethod.GENETIC:
            self.genetic_optimizer = GeneticOptimizer(self.parameter_spaces)
            best_params, best_fitness = self.genetic_optimizer.evolve(
                objective_function, generations=iterations
            )
            
            result = OptimizationResult(
                iteration=iterations,
                parameters=best_params,
                objective_value=best_fitness,
                timestamp=datetime.now().isoformat(),
                method="genetic"
            )
            self.optimization_history.append(result)
        
        else:
            # Random search
            best_value = float('-inf')
            best_params = {}
            
            for i in range(iterations):
                parameters = {ps.name: ps.sample() for ps in self.parameter_spaces}
                objective_value = objective_function(parameters)
                
                if objective_value > best_value:
                    best_value = objective_value
                    best_params = parameters
                
                result = OptimizationResult(
                    iteration=i + 1,
                    parameters=parameters,
                    objective_value=objective_value,
                    timestamp=datetime.now().isoformat(),
                    method="random_search"
                )
                self.optimization_history.append(result)
        
        # Update current parameters
        self.current_parameters = best_params
        return best_params
    
    def optimize_for_economic_health(self, simulation_function, 
                                     iterations: int = 10) -> Dict[str, float]:
        """Optimize parameters to maximize economic health"""
        
        def objective_function(parameters: Dict[str, float]) -> float:
            try:
                result = simulation_function(parameters)
                if isinstance(result, dict):
                    return result.get('economic_health', 0.5)
                return float(result)
            except Exception:
                return 0.0
        
        best_value = float('-inf')
        best_params = {}
        
        for i in range(iterations):
            parameters = {ps.name: ps.sample() for ps in self.parameter_spaces}
            objective_value = objective_function(parameters)
            
            if objective_value > best_value:
                best_value = objective_value
                best_params = parameters
            
            result = OptimizationResult(
                iteration=i + 1,
                parameters=parameters,
                objective_value=objective_value,
                timestamp=datetime.now().isoformat(),
                method="economic_optimization"
            )
            self.optimization_history.append(result)
        
        self.current_parameters = best_params
        return best_params
    
    def get_current_parameters(self) -> Dict[str, float]:
        """Get current optimized parameters"""
        return self.current_parameters
    
    def get_optimization_history(self) -> List[Dict]:
        """Get optimization history"""
        return [r.to_dict() for r in self.optimization_history]
    
    def export_history(self, filename: str = "optimization_history.json"):
        """Export optimization history to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.get_optimization_history(), f, indent=2)
    
    def load_parameters(self, filename: str):
        """Load parameters from file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self.current_parameters = data
                elif isinstance(data, list) and data:
                    # Load best parameters from history
                    best = max(data, key=lambda x: x.get('objective_value', 0))
                    self.current_parameters = best.get('parameters', {})
        except Exception:
            pass
    
    def reset(self):
        """Reset optimizer to initial state"""
        self.optimizer = BayesianOptimizer(self.parameter_spaces)
        self.optimization_history = []
        self.current_parameters = {ps.name: ps.current_value for ps in self.parameter_spaces}


def main():
    """Test the parameter optimizer"""
    print("🔧 Parameter Optimizer Test")
    print("=" * 50)
    
    optimizer = ParameterOptimizer()
    
    # Define a simple test simulation function
    def test_simulation(parameters: Dict[str, float]) -> Dict[str, float]:
        """Test simulation that returns democratic index based on parameters"""
        # Simple formula: democratic index increases with trust and altruism weights
        democratic_index = (
            parameters.get('trust_weight', 0.3) * 0.4 +
            parameters.get('altruism_weight', 0.25) * 0.3 +
            parameters.get('ambition_weight', 0.2) * 0.2 +
            parameters.get('curiosity_weight', 0.15) * 0.1
        )
        
        economic_health = (
            parameters.get('ambition_weight', 0.2) * 0.5 +
            parameters.get('curiosity_weight', 0.15) * 0.3 +
            parameters.get('trust_weight', 0.3) * 0.2
        )
        
        return {
            'democratic_index': democratic_index,
            'economic_health': economic_health
        }
    
    print("\n📊 Optimizing for Democratic Index...")
    best_params = optimizer.optimize_for_democratic_index(
        test_simulation, 
        method=OptimizationMethod.BAYESIAN,
        iterations=5
    )
    
    print(f"\n✅ Best Parameters Found:")
    for key, value in best_params.items():
        print(f"   {key}: {value:.4f}")
    
    print(f"\n📈 Optimization History: {len(optimizer.optimization_history)} iterations")
    
    # Export history
    optimizer.export_history()
    print(f"\n💾 Optimization history exported to optimization_history.json")


if __name__ == "__main__":
    main()
