import collections
import re

import textattack
from textattack.goal_functions import *

from .utils import get_logger

logger = get_logger()

# A list of goal functions and the corresponding available models.
MODELS_BY_GOAL_FUNCTIONS = {
    (TargetedClassification, UntargetedClassification): [
            r'^textattack.models.classification.*',
            r'^textattack.models.entailment.*',
        ],
    (NonOverlappingOutput, ): [ # @todo add TargetedKeywordsOutput
            r'^textattack.models.translation.*',
            r'^textattack.models.summarization.*',
        ],
    
}

# Unroll the `MODELS_BY_GOAL_FUNCTIONS` dictionary into a dictionary that has
# a key for each goal function. (Note the plurality here that distinguishes
# the two variables from one another.)
MODELS_BY_GOAL_FUNCTION = {}
for goal_functions, matching_model_globs in MODELS_BY_GOAL_FUNCTIONS.items():
    for goal_function in goal_functions:
        MODELS_BY_GOAL_FUNCTION[goal_function] = matching_model_globs

def validate_model_goal_function_compatibility(goal_function_class, model_class):
    """
        Determines if `model` is task-compatible with `goal_function`. 
        
        For example, a text-generative model like one intended for translation
            or summarization would not be compatible with a goal function
            that requires probability scores, like the UntargetedGoalFunction.
    """
    # Verify that this is a valid goal function.
    try:
        matching_model_globs = MODELS_BY_GOAL_FUNCTION[goal_function_class]
    except KeyError:
        raise ValueError(f'No entry found for goal function {goal_function_class}.')
    # Get options for this goal function.
    model_module = model_class.__module__
    # Ensure the model matches one of these options.
    for glob in matching_model_globs:
        if re.match(glob, model_module):
            logger.info(f'Goal function {goal_function_class} matches model {model_class.__name__}.')
            return True
    # If we got here, the model does not match the intended goal function.
    for goal_functions, globs in MODELS_BY_GOAL_FUNCTIONS.items():
        for glob in globs:
            if re.match(glob, model_module):
                raise ValueError(f'Model {model_class.__name__} does not match provided goal function {goal_function_class}.'
                    ' Found match with other goal functions: {goal_functions}.')
    # If it matches another goal function, throw an error.
    
    # Otherwise, this is an unknown model–perhaps user-provided, or we forgot to
    # update the corresponding dictionary. Warn user and return.
    logger.warn(f'Unknown if model {model} compatible with goal function {goal_function}.')
    return True
    
def validate_model_gradient_word_swap_compatibility(model):
    """
        Determines if `model` is task-compatible with `GradientBasedWordSwap`. 
        
        We can only take the gradient with respect to an individual word if the
            model uses a word-based tokenizer.
    """
    if isinstance(model, textattack.models.helpers.LSTMForClassification):
        return True
    else:
        raise ValueError(f'Cannot perform GradientBasedWordSwap on model {model}.')