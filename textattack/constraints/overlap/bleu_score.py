import nltk
from textattack.constraints import Constraint

class BLEU(Constraint):
    """ A constraint on BLEU score difference.
    """
    
    def __init__(self, max_bleu_score):
        if not isinstance(max_bleu_score, int):
            raise TypeError('max_bleu_score must be an int')
        self.max_bleu_score = max_bleu_score
        
    
    def __call__(self, x, x_adv, original_text=None):
        if not original_text:
            return True
        ref = original_text.words
        hyp = x_adv.words
        bleu_score = nltk.translate.bleu_score.sentence_bleu([ref], hyp)
        return bleu_score <= self.max_bleu_score
    
    def extra_repr_keys(self):
        return ['max_bleu_score']
