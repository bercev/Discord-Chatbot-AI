from random import choice, randint
from aiTest import ask_chatAI, askQnA
from analyze_db import query, dump

# responses based on input
def get_response(user_input: str=None, deleted: bool=False) -> str:
    lowered: str = user_input.lower()

    if ('>>query' in lowered[0:7]):
        print("**SYSTEM** asking the RAG model...") # asking the model for an answer
        return query(lowered[7:])
    if '>>dump' in lowered[0:6]: # retrieve data
        return dump()
    if deleted:
        return lowered
    #if lowered =='':
    #    return 'Well, ur silent one aren\'t ya!'
    #if 'hello' in lowered:
    #    return 'Hello there!'
    #if 'how are you' in lowered:
    #    return 'Good, thanks!'
    #if 'bye' in lowered:
    #    return 'Bye!'
    if 'roll dice' in lowered:
        return f'You rolled: {randint(1,6)}'
    if len(lowered) > 2 and '>>' in lowered[0:2] and '?' in lowered[2:]: # checks if syntax is correct to call the AI model
        print("**[SYSTEM]** asking Llama AI...")
        if ('[' in lowered and ']' in lowered) and (lowered.index('[') < lowered.index(']')):
            try:
                num = int(lowered[lowered.index('[') +1: lowered.index(']')])
                return f"{num} word response:\n" + ask_chatAI(lowered)[0:num]
            except Exception as e:
                print(e)
        return ask_chatAI(lowered)[0:2000] # default max length
    
    return #choice(['Take it to a publisher bro', 'Ion know what u mean', 'Idk how to answer dat lfmao','code not implemented for yo bs yet'])
