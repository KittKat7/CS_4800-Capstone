from types import ModuleType
from .langs import en_us

class LangMap:
    """
    Holds a map of the available languages and the current language being used.
    """
    langMap: dict[str, str]|None = None
    availableLangs: dict[str, ModuleType] = {
        "en_us": en_us,
    }

def setLangMap(language: str):
    """
    Sets the language map for use.
    """
    if language in LangMap.availableLangs.keys():
        LangMap.langMap = LangMap.availableLangs[language].language
    else:
        raise Exception("Language does not exist!")


def getString(key: str) -> str:
    """
    Gets a string from the current language. If the string does not exist,
    returns none.
    """
    if LangMap.langMap == None:
        raise Exception("Language Map not set!")
    
    if key in LangMap.langMap.keys():
        return LangMap.langMap[key]
        # return " ".join(LangMap.langMap[key].split())
    else:
        raise Exception("Failed to find string!")
