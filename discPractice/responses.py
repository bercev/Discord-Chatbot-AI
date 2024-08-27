from random import choice, randint
from aiTest import ask_chatAI, askQnA
from collections import defaultdict

# responses based on input
def get_response(user_input: str=None, deleted: bool=False, allMessages: defaultdict=None) -> str:
    lowered: str = user_input.lower()

    if ('>>getresult' in lowered[0:11] and allMessages) or ('>>dump' in lowered[0:7] and allMessages):
        l =  [] # creates a list to be converted into a string
        for key, v in allMessages.items():
            l.append(key + " sent these messages:") # appends to list
            l.extend(v) # converts hashmap into an element of the array
            l.append("\n---") # appends a new line
        allMsgString = ' '.join(l) # converts list to string
        if '>>dump' in lowered[0:7]: # retrieve data
            print(allMsgString)
            return allMsgString
        print("[SYSTEM] asking the model...") # asking the model for an answer
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
        print("[SYSTEM] asking Llama AI...")
        if ('[' in lowered and ']' in lowered) and (lowered.index('[') < lowered.index(']')):
            try:
                num = int(lowered[lowered.index('[') +1: lowered.index(']')])
                return f"{num} word response:\n" + ask_chatAI(lowered)[0:num]
            except Exception as e:
                print(e)
        return ask_chatAI(lowered)[0:2000] # default max length
    
    return #choice(['Take it to a publisher bro', 'Ion know what u mean', 'Idk how to answer dat lfmao','code not implemented for yo bs yet'])
