import math

class AdaptiveEngine:
    def __init__(self):
        # Discrimination parameter - how well items separate different ability levels
        self.discrimination = 1.0
        self.learning_rate_base = 0.3  # How quickly abilities change

    def calculate_probability_correct(self, ability, item_difficulty):
        """
        Calculate probability of correct response using IRT 1PL model
        P(θ,b) = 1 / (1 + e^(-a(θ-b)))
        Where θ = ability, b = difficulty, a = discrimination
        """
        exponent = -self.discrimination * (ability - item_difficulty)
        probability = 1 / (1 + math.exp(exponent))
        return probability

    def update_ability_estimate(self, current_ability, item_difficulty, 
                              response_correct, num_responses):
        """
        Update ability estimate based on student's response to a question
        Uses a simplified maximum likelihood approach
        """
        # Calculate the expected probability of correct answer based on current ability
        prob_correct = self.calculate_probability_correct(current_ability, item_difficulty)
        
        # Actual outcome (1 for correct, 0 for incorrect)
        actual_outcome = int(response_correct)
        
        # Calculate how much to adjust ability based on difference between expected and actual
        # If student did better than expected, increase ability; if worse, decrease ability
        adjustment = actual_outcome - prob_correct
        
        # Learning rate decreases as student answers more questions (more confidence in estimate)
        learning_rate = self.learning_rate_base / (num_responses + 1)
        
        # Apply the adjustment to current ability
        new_ability = current_ability + learning_rate * adjustment
        
        # Keep ability within reasonable bounds [0.1, 0.9] to prevent extreme values
        return max(0.1, min(0.9, new_ability))

    def select_next_difficulty(self, current_ability, previous_response_correct):
        """
        Select the difficulty of the next question based on current ability and previous response
        This creates the adaptive loop: harder if correct, easier if incorrect
        """
        # Base the next difficulty on current ability for optimal challenge
        base_difficulty = current_ability
        
        # Adjust based on previous response to maintain engagement
        if previous_response_correct:
            # If student got previous question correct, make next question slightly harder
            next_difficulty = base_difficulty + 0.1
        else:
            # If student got previous question incorrect, make next question slightly easier
            next_difficulty = base_difficulty - 0.1
        
        # Keep difficulty within reasonable bounds [0.1, 0.9]
        return max(0.1, min(0.9, next_difficulty))

# Test the adaptive engine to demonstrate how it works
if __name__ == "__main__":
    print("=== Adaptive Engine Demonstration ===")
    
    # Create an instance of our adaptive engine
    engine = AdaptiveEngine()
    
    # Simulate a student starting with baseline ability (0.5)
    ability = 0.5
    print(f"Starting ability: {ability}")
    
    # Simulate responses: True = correct, False = incorrect
    responses = [True, True, False, True, False, True, True, True, False, True]
    
    print(f"\nSimulating 10 questions with responses: {responses}")
    print("-" * 60)
    
    for i, correct in enumerate(responses):
        print(f"Question {i+1:2d}: ", end="")
        
        # Show current state
        print(f"Ability={ability:.3f}", end=" → ")
        
        # Determine next question difficulty based on current ability and previous response
        prev_correct = correct if i > 0 else True  # For first question, assume baseline difficulty
        next_difficulty = engine.select_next_difficulty(ability, prev_correct)
        
        # Show what happens based on response
        print(f"Difficulty={next_difficulty:.3f}", end=" → ")
        print(f"Response={'CORRECT' if correct else 'INCORRECT'}", end=" → ")
        
        # Update ability based on response
        ability = engine.update_ability_estimate(ability, next_difficulty, correct, i+1)
        
        print(f"New Ability={ability:.3f}")
    
    print("-" * 60)
    print(f"Final ability estimate: {ability:.3f}")
    
    # Demonstrate difficulty selection logic
    print(f"\n=== Difficulty Selection Examples ===")
    test_abilities = [0.2, 0.5, 0.8]  # Low, Medium, High ability
    test_responses = [True, False]  # Correct, Incorrect
    
    for ability in test_abilities:
        print(f"\nFor student with ability {ability}:")
        for response in test_responses:
            next_diff = engine.select_next_difficulty(ability, response)
            print(f"  If previous answer was {'correct' if response else 'incorrect'}, "
                  f"next difficulty will be {next_diff:.2f}")