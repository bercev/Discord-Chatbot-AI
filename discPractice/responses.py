from random import choice, randint
from aiTest import ask_chat

# responses based on input
def get_response(user_input: str, deleted: bool=False) -> str:
    lowered: str = user_input.lower()

    if deleted:
        return lowered
    if lowered =='':
        return 'Well, ur silent one aren\'t ya!'
    if 'hello' in lowered:
        return 'Hello there!'
    if 'how are you' in lowered:
        return 'Good, thanks!'
    if 'bye' in lowered:
        return 'cya'
    if 'roll dice' in lowered:
        return f'You rolled: {randint(1,6)}'
    if len(lowered) > 2 and '>>' in lowered[0:2] and '?' in lowered[2:]: # checks if syntax is correct to call the AI model
        return ask_chat(lowered)
    return choice(['Take it to a publisher bro', 'Ion know what u mean', 'Idk how to answer dat lfmao','code not implemented for yo bs yet'])
