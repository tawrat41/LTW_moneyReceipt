from num2words import num2words


def amount_to_words(amount):
    if amount == 0:
        return "Zero Taka Only"

    try:
        words = num2words(amount, lang='en')
        words = words.replace("-", " ")
        return words.title() + " Taka Only"
    except Exception:
        return "Amount Conversion Error"