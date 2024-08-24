from random import choice, randint

def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()

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
    return choice(['Take it to a publisher bro', 'Ion know what u mean', 'Idk how to answer dat lfmao',
                   'code not implemented for yo bs yet'])