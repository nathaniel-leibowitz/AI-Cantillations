import requests
import json
import csv
from normalization import NormalizerComposer
from pprint import pprint
import requests_cache
requests_cache.install_cache('my_cache', expire_after=3600*24*14)


def bleach_text(text: str):
    dirt = ["&nbsp;", "{ס}", "{פ}", "thinsp", ";", "&"]
    for symbol in dirt:
        text = text.replace(symbol, "")
    text = text.replace("  ", " ")
    return text


def write_dicts_to_csv(data, filename):
    # Extracting field names from the first dictionary
    fieldnames = data[0].keys()

    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header
        writer.writeheader()

        # Write data
        for row in data:
            writer.writerow(row)
def pure_text_with_cantillation(book):
    url = "https://www.sefaria.org/api/v3/texts/" + book
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    normalizer_cantilized_full = NormalizerComposer(['unidecode', 'br-tag', 'html', 'maqaf', 'nikkud', 'double-space', "kri-ktiv"])
    normalizer_cantilized_medium = NormalizerComposer(['unidecode', 'br-tag', 'html', 'maqaf', 'nikkud', 'double-space', "kri-ktiv", 'cantillation-non-etnahta-sofpasuk-merhaptipha'])
    normalizer_cantilized_small = NormalizerComposer(['unidecode', 'br-tag', 'html', 'maqaf', 'nikkud', 'double-space', "kri-ktiv",'cantillation-non-etnahta-sofpasuk'])
    normalizer_pure = NormalizerComposer(['unidecode', 'br-tag', 'html', 'maqaf', 'nikkud', 'cantillation', 'double-space', "kri-ktiv"])
    res_dict = json.loads(response.text)
    psukim = []
    for perek_index, perek in enumerate(res_dict['versions'][0]['text']):
        for pasuk_index, pasuk in enumerate(perek):
            text_cantilized_full = (bleach_text(normalizer_cantilized_full.normalize(pasuk)))
            text_cantilized_medium = (bleach_text(normalizer_cantilized_medium.normalize(pasuk)))
            text_cantilized_small = (bleach_text(normalizer_cantilized_small.normalize(pasuk)))
            text_pure = (bleach_text(normalizer_pure.normalize(pasuk)))
            psukim += ([{"book": book, "perek": perek_index+1, "pasuk": pasuk_index+1,
                         "raw_text": text_pure,
                         "cantilized_full": text_cantilized_full,
                         "cantilized_medium": text_cantilized_medium,
                         "cantilized_small": text_cantilized_small,
                         "cantilized_ai": ""}])
    return psukim


def create_new_training_query(training_description, pasuk_raw, pasuk_cantillized):
    return (
    {"messages": [{"role": "system", "content": training_description},
                  {"role": "user", "content": pasuk_raw},
                  {"role": "assistant", "content": pasuk_cantillized}]}
    )


def choose_training_set(set):
    for s_index, s in enumerate(set):
        s["training"] = s_index % 2


def generate_training_description():
    cantillations = ('\u0591' + " " + '\u0592' + " " + '\u0593' + " " + '\u0594' + " " + '\u0595' + " " +
                     '\u0596' + " " + '\u0597' + " " + '\u0598' + " " + '\u0599' + " " + '\u059a' + " " +
                     '\u059b' + " " + '\u059c' + " " + '\u059d' + " " + '\u059e' + " " + '\u059f' + " " +
                     '\u05a0' + " " + '\u05a1' + " " + '\u05a2' + " " + '\u05a3' + " " + '\u05a4' + " " +
                     '\u05a5' + " " + '\u05a6' + " " + '\u05a7' + " " + '\u05a8' + " " + '\u05a9' + " " +
                     '\u05aa' + " " + '\u05ab' + " " + '\u05ac' + " " + '\u05ad' + " " + '\u05ae' + " " +
                     '\u05bd' + " " + '\u05be' + " " + '\u05c0' + " " + '\u05c3' + " " + '\u05c6')
    return "place the most fitting biblical cantillation marks in the appropriate letters of the verse. Use the following cantillations: " + cantillations



if __name__ == '__main__':
    hebrew_bible_books = [
        "Genesis",
        "Exodus",
        "Leviticus",
        "Numbers",
        "Deuteronomy",
        "Joshua",
        "Judges",
        "1 Samuel",
        "2 Samuel",
        "1 Kings",
        "2 Kings",
        "Isaiah",
        "Jeremiah",
        "Ezekiel",
        "Hosea",
        "Joel",
        "Amos",
        "Obadiah",
        "Jonah",
        "Micah",
        "Nahum",
        "Habakkuk",
        "Zephaniah",
        "Haggai",
        "Zechariah",
        "Malachi",
        "Song of Solomon",
        "Ruth",
        "Lamentations",
        "Ecclesiastes",
        "Esther",
        "Daniel",
        "Ezra",
        "Nehemiah",
        "1 Chronicles",
        "2 Chronicles"
    ]
    training_description = generate_training_description()
    cantillations = []


    for book in hebrew_bible_books:
        cantillations += pure_text_with_cantillation(book)
    choose_training_set(cantillations)
    for s in cantillations:
        if s["training"]:
            s["training_query"] = create_new_training_query(training_description, s["raw_text"], s["cantilized_full"])
        else:
            s["training_query"] = ""
    pprint(cantillations[0])
    pprint(cantillations[2741])
    pprint(cantillations[2742])
    write_dicts_to_csv(cantillations, 'data.csv')
    print("finished")