from random import choice, randint
from aiTest import ask_chatAI, askQnA
from collections import defaultdict

# responses based on input
def get_response(user_input: str=None, deleted: bool=False, allMessages: defaultdict=None) -> str:
    lowered: str = user_input.lower()

    if '>>getresult' in lowered[0:11] and allMessages:
        l =  []
        for k, v in allMessages.items():
            l.extend(v)
        allMsgString = ' '.join(l)
        print("[SYSTEM] asking the model...")
        return askQnA({"inputs": {"question": lowered[11:],"context": allMsgString}})
        
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
        if '[500]' in lowered:
            return "500 word response:\n" + ask_chatAI(lowered)[0:500]
        return ask_chatAI(lowered)[0:2000]
    
    return #choice(['Take it to a publisher bro', 'Ion know what u mean', 'Idk how to answer dat lfmao','code not implemented for yo bs yet'])
