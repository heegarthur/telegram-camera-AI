import random, re

# Functie om de training data te laden
def laad_training_data(bestandsnaam):
    training_data = []
    try:
        with open(bestandsnaam, 'r', encoding="utf-8", errors="replace") as bestand:
            for regel in bestand:
                vraag, antwoord = regel.strip().split(':')
                training_data.append((vraag, antwoord))
    except FileNotFoundError:
        print("file not found!")
        exit()
    except Exception as e:
        print(f"Error: {e}")
    return training_data

# Functie om de AI te trainen
def train_ai(training_data):
    ai = {}
    antwoord_frequentie = {}
    for vraag, antwoord in training_data:
        if vraag not in ai:
            ai[vraag] = []
        ai[vraag].append(antwoord)
        if antwoord not in antwoord_frequentie:
            antwoord_frequentie[antwoord] = 0
        antwoord_frequentie[antwoord] += 1
    return ai, antwoord_frequentie




# Functie om een antwoord te geven op een gebruikersvraag
def geef_antwoord(ai, vraag, antwoord_frequentie):
    beste_antwoord = None
    beste_score = 0
    for v in ai:
        score = 0
        # Kijk naar exacte overeenkomst
        if v.lower() == vraag.lower():
            score = 100
        else:
            # Kijk naar overeenkomende woorden
            vraag_woorden = re.findall(r'\b\w+\b', vraag.lower())
            v_woorden = re.findall(r'\b\w+\b', v.lower())
            for woord in vraag_woorden:
                if woord in v_woorden:
                    score += 1
            # Kijk naar overeenkomende cijfers
            vraag_cijfers = re.findall(r'\d+', vraag)
            v_cijfers = re.findall(r'\d+', v)
            for cijfer in vraag_cijfers:
                if cijfer in v_cijfers:
                    score += 1
        if score > beste_score:
            beste_score = score
            beste_antwoord = random.choice(ai[v])
    if beste_antwoord is None:
        # Kies de meestgekozen antwoord
        meestgekozen_antwoord = max(antwoord_frequentie, key=antwoord_frequentie.get)
        return meestgekozen_antwoord
    return beste_antwoord

def add_train_data(data, path):
    with open(path, 'a') as f:
        f.write(data+"\n")

# Hoofdprogramma
def main(vraag=None, path="next_action.txt", memory=None):
    if path != "next_action.txt":
        bestandsnaam = path
    else:
        bestandsnaam = 'next_action.txt'
    training_data = laad_training_data(bestandsnaam)
    ai, antwoord_frequentie = train_ai(training_data)
    while True:
        if vraag == None:
            vraag = input("question: ")
        antwoord = geef_antwoord(ai, vraag, antwoord_frequentie)
        return antwoord

if __name__ == "__main__":
    main()